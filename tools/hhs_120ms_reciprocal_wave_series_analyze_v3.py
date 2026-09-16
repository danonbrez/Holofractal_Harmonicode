#!/usr/bin/env python3
from __future__ import annotations

import argparse
from decimal import Decimal, getcontext
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
from typing import Any

getcontext().prec = 90
BENCH_SCHEMA = "HHS_120MS_RECIPROCAL_WAVE_XYZW_V3"
EVIDENCE_SCHEMA = "HHS_120MS_RECIPROCAL_WAVE_XYZW_V3_SERIES_EVIDENCE"
WINDOW_NS = 120_000_000
Z95 = Decimal("1.959963984540054")


def _cpu_model() -> str:
    p = Path("/proc/cpuinfo")
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def _memory_kib() -> int | None:
    p = Path("/proc/meminfo")
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1])
    return None


def _cc_version() -> str:
    try:
        return subprocess.run(
            ["cc", "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
    except Exception:
        return "unknown"


def _rate(value: int, window_ns: int = WINDOW_NS) -> Decimal:
    return Decimal(value) * Decimal(1_000_000_000) / Decimal(window_ns)


def _seconds(ns: int) -> Decimal:
    return Decimal(ns) / Decimal(1_000_000_000)


def _mean(xs: list[Decimal]) -> Decimal:
    return sum(xs, Decimal(0)) / Decimal(len(xs))


def _sample_sd(xs: list[Decimal]) -> Decimal:
    if len(xs) < 2:
        return Decimal(0)
    mu = _mean(xs)
    variance = sum((x - mu) * (x - mu) for x in xs) / Decimal(len(xs) - 1)
    return variance.sqrt()


def _dot(a: list[Decimal], b: list[Decimal]) -> Decimal:
    return sum((x * y for x, y in zip(a, b)), Decimal(0))


def _sub(a: list[Decimal], b: list[Decimal]) -> list[Decimal]:
    return [x - y for x, y in zip(a, b)]


def _add(a: list[Decimal], b: list[Decimal]) -> list[Decimal]:
    return [x + y for x, y in zip(a, b)]


def _scale(s: Decimal, a: list[Decimal]) -> list[Decimal]:
    return [s * x for x in a]


def _laplacian(v: list[Decimal]) -> list[Decimal]:
    # Reciprocal graph edges: x <-> z and y <-> w.
    x, y, z, w = v
    return [x - z, y - w, z - x, w - y]


def _tensor(v: list[Decimal]) -> list[list[str]]:
    x, y, z, w = v
    xy, yx, zw, wz = x * y, y * x, z * w, w * z
    return [
        [str(xy), str(x + y), str(yx)],
        [str(xy - zw), str(x + y - z - w + xy + yx - zw - wz), str(wz - yx)],
        [str(wz), str(z + w), str(zw)],
    ]


def _boundary_residual(consumer: dict[str, Any], producer: dict[str, Any]) -> Decimal:
    """Signed reciprocal boundary residual.

    completed early -> negative normalized time slack
    incomplete at boundary -> positive remaining represented-work fraction
    exact boundary completion -> zero
    """
    if bool(consumer["dataset_complete"]):
        completion_ns = int(consumer["completion_elapsed_ns"])
        return (Decimal(completion_ns) - Decimal(WINDOW_NS)) / Decimal(WINDOW_NS)
    target = Decimal(int(producer["represented_transitions"]))
    done = Decimal(int(consumer["represented_transitions"]))
    if target <= 0 or done < 0 or done > target:
        raise ValueError("invalid producer/consumer represented-work relation")
    return (target - done) / target


def _parse_samples(path: Path) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        rec = json.loads(raw)
        kind = rec.get("type")
        if kind == "meta":
            if current is not None:
                raise ValueError("new sample began before previous result")
            current = {"meta": rec, "benchmarks": {}, "verifications": {}}
        elif current is None:
            raise ValueError("record appeared outside a sample")
        elif kind == "benchmark":
            current["benchmarks"][str(rec["id"])] = rec
        elif kind == "verification":
            current["verifications"][str(rec["dataset"])] = rec
        elif kind == "result":
            if rec.get("result") != "PASS":
                raise ValueError("sample terminal result was not PASS")
            samples.append(current)
            current = None
    if current is not None:
        raise ValueError("unterminated sample")
    if not samples:
        raise ValueError("no reciprocal samples found")
    return samples


def _validate_sample(sample: dict[str, Any], index: int) -> dict[str, Any]:
    meta = sample["meta"]
    benches = sample["benchmarks"]
    verifications = sample["verifications"]
    if meta.get("schema") != BENCH_SCHEMA:
        raise ValueError(f"sample {index}: wrong schema")
    if int(meta["window_ns"]) != WINDOW_NS:
        raise ValueError(f"sample {index}: window is not exactly 120ms")
    if int(meta.get("active_threads_per_benchmark", 0)) != 1:
        raise ValueError(f"sample {index}: benchmark is not single-threaded")
    if not bool(meta.get("benchmarks_sequential")):
        raise ValueError(f"sample {index}: A/B/C/D are not sequential")
    if int(meta["seed_X"]) == int(meta["seed_Y"]):
        raise ValueError(f"sample {index}: X/Y streams are not domain-separated")
    if set(benches) != {"A", "B", "C", "D"}:
        raise ValueError(f"sample {index}: A/B/C/D records missing")
    if set(verifications) != {"X", "Y"}:
        raise ValueError(f"sample {index}: X/Y verification records missing")

    expected = {
        "A": ("x", "hhs", "X", "capacity_120ms"),
        "B": ("y", "conventional_matrix", "Y", "capacity_120ms"),
        "C": ("z", "conventional_matrix", "X", "reciprocal_120ms"),
        "D": ("w", "hhs", "Y", "reciprocal_120ms"),
    }
    tolerance = 10_000_000
    for ident, rec in benches.items():
        axis, arch, dataset, mode = expected[ident]
        if (rec.get("axis"), rec.get("architecture"), rec.get("dataset"), rec.get("mode")) != (
            axis, arch, dataset, mode
        ):
            raise ValueError(f"sample {index}: {ident} identity mismatch")
        if int(rec["completed_queries"]) <= 0:
            raise ValueError(f"sample {index}: {ident} completed no work")
        elapsed = int(rec["elapsed_ns"])
        if ident in ("A", "B"):
            if elapsed < WINDOW_NS or elapsed > WINDOW_NS + tolerance:
                raise ValueError(f"sample {index}: {ident} violated 120ms producer bound")
        else:
            complete = bool(rec["dataset_complete"])
            if elapsed > WINDOW_NS + tolerance:
                raise ValueError(f"sample {index}: {ident} exceeded 120ms reciprocal bound")
            if not complete and elapsed < WINDOW_NS:
                raise ValueError(f"sample {index}: {ident} stopped early without completing dataset")
            if complete:
                completion = int(rec["completion_elapsed_ns"])
                if completion <= 0 or completion > WINDOW_NS + tolerance:
                    raise ValueError(f"sample {index}: {ident} invalid completion time")

    a, b, c, d = (benches[k] for k in ("A", "B", "C", "D"))
    if int(c["dataset_limit_queries"]) != int(a["completed_queries"]):
        raise ValueError(f"sample {index}: C target != A dataset")
    if int(d["dataset_limit_queries"]) != int(b["completed_queries"]):
        raise ValueError(f"sample {index}: D target != B dataset")
    if int(c["completed_queries"]) > int(a["completed_queries"]):
        raise ValueError(f"sample {index}: C exceeded X")
    if int(d["completed_queries"]) > int(b["completed_queries"]):
        raise ValueError(f"sample {index}: D exceeded Y")

    for consumer_id, producer_id, dataset in (("C", "A", "X"), ("D", "B", "Y")):
        consumer, producer = benches[consumer_id], benches[producer_id]
        v = verifications[dataset]
        if not bool(v.get("exact")):
            raise ValueError(f"sample {index}: {dataset} prefix did not verify")
        if str(v.get("producer")) != producer_id or str(v.get("consumer")) != consumer_id:
            raise ValueError(f"sample {index}: {dataset} producer/consumer mismatch")
        if int(v["verified_prefix_queries"]) != int(consumer["completed_queries"]):
            raise ValueError(f"sample {index}: {dataset} prefix count mismatch")
        for field in ("represented_transitions", "descriptor_bits", "endpoint_digest", "descriptor_digest"):
            if int(v[field]) != int(consumer[field]):
                raise ValueError(f"sample {index}: {dataset} prefix mismatch at {field}")
        if bool(consumer["dataset_complete"]):
            for field in ("completed_queries", "represented_transitions", "descriptor_bits", "endpoint_digest", "descriptor_digest"):
                if int(consumer[field]) != int(producer[field]):
                    raise ValueError(f"sample {index}: completed {dataset} != producer at {field}")

    for ident in ("A", "D"):
        rec = benches[ident]
        if int(rec.get("lane5_admissions", -1)) != int(rec["completed_queries"]):
            raise ValueError(f"sample {index}: {ident} missing Lane 5 admissions")
        if int(rec.get("materialized_intermediate_states", -1)) != 0:
            raise ValueError(f"sample {index}: {ident} materialized intermediates")

    rates = [_rate(int(benches[k]["represented_transitions"])) for k in ("A", "B", "C", "D")]
    epsilon_c = _boundary_residual(c, a)
    epsilon_d = _boundary_residual(d, b)
    balance = epsilon_c + epsilon_d
    state_bits = Decimal(str(math.log2(int(meta["modulus"]))))

    return {
        "index": index,
        "rates": rates,
        "tensor": _tensor(rates),
        "delta_xyzw": rates[0] * rates[1] - rates[2] * rates[3],
        "rho_X": rates[0] / rates[2] if rates[2] != 0 else None,
        "rho_Y": rates[3] / rates[1] if rates[1] != 0 else None,
        "epsilon_C": epsilon_c,
        "epsilon_D": epsilon_d,
        "balance": balance,
        "endpoint_bits_rates": [
            state_bits * _rate(int(benches[k]["completed_queries"])) for k in ("A", "B", "C", "D")
        ],
        "dataset_complete_C": bool(c["dataset_complete"]),
        "dataset_complete_D": bool(d["dataset_complete"]),
        "raw": {k: benches[k] for k in ("A", "B", "C", "D")},
    }


def _wave_fit(vectors: list[list[Decimal]]) -> dict[str, Any]:
    if len(vectors) < 3:
        return {
            "available": False,
            "reason": "at least three samples are required",
        }
    dt = Decimal(WINDOW_NS) / Decimal(1_000_000_000)
    dt2 = dt * dt
    d2s: list[list[Decimal]] = []
    laps: list[list[Decimal]] = []
    for i in range(1, len(vectors) - 1):
        d2 = _scale(Decimal(1) / dt2, _add(_sub(vectors[i + 1], _scale(Decimal(2), vectors[i])), vectors[i - 1]))
        lap = _laplacian(vectors[i])
        d2s.append(d2)
        laps.append(lap)
    denom = sum((_dot(l, l) for l in laps), Decimal(0))
    lam = Decimal(0) if denom == 0 else -sum((_dot(d2, l) for d2, l in zip(d2s, laps)), Decimal(0)) / denom
    residuals = [_add(d2, _scale(lam, lap)) for d2, lap in zip(d2s, laps)]
    residual_norm_sq = sum((_dot(r, r) for r in residuals), Decimal(0))
    d2_norm_sq = sum((_dot(d2, d2) for d2 in d2s), Decimal(0))
    normalized_rms = Decimal(0)
    if d2_norm_sq > 0:
        normalized_rms = (residual_norm_sq / d2_norm_sq).sqrt()
    mean_residual = [
        sum((r[j] for r in residuals), Decimal(0)) / Decimal(len(residuals)) for j in range(4)
    ]
    return {
        "available": True,
        "equation": "D2_t Psi_n + lambda * L_reciprocal * Psi_n = eta_n",
        "reciprocal_graph_edges": ["x<->z", "y<->w"],
        "lambda_s_inverse_2": str(lam),
        "lambda_positive_restoring": lam > 0,
        "normalized_residual_rms": str(normalized_rms),
        "mean_residual_vector": [str(x) for x in mean_residual],
        "interior_sample_count": len(residuals),
    }


def analyze(samples: list[dict[str, Any]]) -> dict[str, Any]:
    validated = [_validate_sample(sample, i) for i, sample in enumerate(samples)]
    vectors = [s["rates"] for s in validated]
    balances = [s["balance"] for s in validated]
    eps_c = [s["epsilon_C"] for s in validated]
    eps_d = [s["epsilon_D"] for s in validated]
    mean_balance = _mean(balances)
    sd_balance = _sample_sd(balances)
    se_balance = sd_balance / Decimal(len(balances)).sqrt() if len(balances) > 1 else Decimal(0)
    ci_low = mean_balance - Z95 * se_balance
    ci_high = mean_balance + Z95 * se_balance
    cancellation_supported = ci_low <= 0 <= ci_high

    means = [_mean([v[j] for v in vectors]) for j in range(4)]
    sds = [_sample_sd([v[j] for v in vectors]) for j in range(4)]
    wave = _wave_fit(vectors)

    sample_out: list[dict[str, Any]] = []
    for s in validated:
        sample_out.append({
            "index": s["index"],
            "xyzw_transition_rates_per_second": [str(v) for v in s["rates"]],
            "xyzw_endpoint_bits_equivalent_per_second": [str(v) for v in s["endpoint_bits_rates"]],
            "delta_xyzw": str(s["delta_xyzw"]),
            "rho_X": None if s["rho_X"] is None else str(s["rho_X"]),
            "rho_Y": None if s["rho_Y"] is None else str(s["rho_Y"]),
            "epsilon_C": str(s["epsilon_C"]),
            "epsilon_D": str(s["epsilon_D"]),
            "reciprocal_boundary_balance": str(s["balance"]),
            "C_dataset_complete": s["dataset_complete_C"],
            "D_dataset_complete": s["dataset_complete_D"],
            "tensor": s["tensor"],
        })

    return {
        "schema": EVIDENCE_SCHEMA,
        "result": "PASS",
        "sample_count": len(validated),
        "window_ns_each_leg": WINDOW_NS,
        "window_seconds_each_leg": "0.12",
        "measurement_definition": {
            "x": "HHS represented-transition rate on producer Dataset X",
            "y": "optimized conventional represented-transition rate on producer Dataset Y",
            "z": "optimized conventional represented-transition progress rate on frozen Dataset X",
            "w": "HHS represented-transition progress rate on frozen Dataset Y",
            "signed_boundary_residual": {
                "completed_early": "(completion_elapsed_ns - Delta_t) / Delta_t; negative",
                "incomplete": "(target_represented_work - completed_represented_work) / target_represented_work; positive",
                "boundary": "0",
            },
            "cancellation_hypothesis": "E[epsilon_C + epsilon_D] = 0",
        },
        "runner": {
            "cpu_model": _cpu_model(),
            "logical_cpu_count": os.cpu_count(),
            "memory_kib": _memory_kib(),
            "platform": platform.platform(),
            "kernel_release": platform.release(),
            "runner_os_env": os.getenv("RUNNER_OS"),
            "runner_arch_env": os.getenv("RUNNER_ARCH"),
            "image_os_env": os.getenv("ImageOS"),
            "image_version_env": os.getenv("ImageVersion"),
            "cc_version": _cc_version(),
        },
        "xyzw_rate_statistics": {
            "mean": [str(x) for x in means],
            "sample_sd": [str(x) for x in sds],
            "reference_unit": "1 represented transition / second",
        },
        "probabilistic_cancellation": {
            "mean_epsilon_C": str(_mean(eps_c)),
            "mean_epsilon_D": str(_mean(eps_d)),
            "mean_balance": str(mean_balance),
            "sample_sd_balance": str(sd_balance),
            "standard_error": str(se_balance),
            "confidence_95_low": str(ci_low),
            "confidence_95_high": str(ci_high),
            "zero_inside_95_percent_interval": cancellation_supported,
            "status": "SUPPORTED_AT_95_PERCENT" if cancellation_supported else "NOT_SUPPORTED_AT_95_PERCENT",
            "note": "This statistic tests the cancellation hypothesis; benchmark integrity PASS does not depend on the hypothesis being true.",
        },
        "discrete_reciprocal_wave_fit": wave,
        "samples": sample_out,
        "claim_scope": {
            "physical_negative_time_claim": False,
            "negative_time_semantics": "negative signed slack relative to the fixed 120ms normalization boundary",
            "physical_wavefunction_claim": False,
            "wave_equation_semantics": "discrete benchmark-space wave equation on the reciprocal x<->z, y<->w graph",
            "universal_computing_supremacy_claim": False,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("stream_ndjson", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--min-samples", type=int, default=16)
    args = p.parse_args()
    samples = _parse_samples(args.stream_ndjson)
    if len(samples) < args.min_samples:
        raise SystemExit(f"need at least {args.min_samples} samples, found {len(samples)}")
    evidence = analyze(samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("HHS_120MS_RECIPROCAL_WAVE_XYZW_V3_SERIES_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
