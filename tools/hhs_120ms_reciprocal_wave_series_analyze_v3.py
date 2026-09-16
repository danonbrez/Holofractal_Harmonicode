#!/usr/bin/env python3
from __future__ import annotations

import argparse
from decimal import Decimal, getcontext
import json
import math
import os
from pathlib import Path
import platform
import subprocess
from typing import Any

getcontext().prec = 90
SCHEMA = "HHS_120MS_GLOBAL_RECIPROCAL_WAVE_XYZW_V3"
EVIDENCE_SCHEMA = "HHS_120MS_GLOBAL_RECIPROCAL_WAVE_XYZW_V3_EVIDENCE"
GLOBAL_BUDGET_NS = 120_000_000
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
        return subprocess.run(["cc", "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
    except Exception:
        return "unknown"


def _mean(xs: list[Decimal]) -> Decimal:
    return sum(xs, Decimal(0)) / Decimal(len(xs))


def _sample_sd(xs: list[Decimal]) -> Decimal:
    if len(xs) < 2:
        return Decimal(0)
    mu = _mean(xs)
    return (sum((x - mu) ** 2 for x in xs) / Decimal(len(xs) - 1)).sqrt()


def _laplacian(v: list[Decimal]) -> list[Decimal]:
    x, y, z, w = v
    return [x - z, y - w, z - x, w - y]


def _dot(a: list[Decimal], b: list[Decimal]) -> Decimal:
    return sum((x * y for x, y in zip(a, b)), Decimal(0))


def _wave_fit(vectors: list[list[Decimal]]) -> dict[str, Any]:
    if len(vectors) < 3:
        return {"available": False, "reason": "at least three gradient samples are required"}
    d2s: list[list[Decimal]] = []
    laps: list[list[Decimal]] = []
    for i in range(1, len(vectors) - 1):
        d2 = [vectors[i + 1][j] - Decimal(2) * vectors[i][j] + vectors[i - 1][j] for j in range(4)]
        d2s.append(d2)
        laps.append(_laplacian(vectors[i]))
    denom = sum((_dot(l, l) for l in laps), Decimal(0))
    lam = Decimal(0) if denom == 0 else -sum((_dot(d2, l) for d2, l in zip(d2s, laps)), Decimal(0)) / denom
    residuals = [[d2[j] + lam * lap[j] for j in range(4)] for d2, lap in zip(d2s, laps)]
    residual_sq = sum((_dot(r, r) for r in residuals), Decimal(0))
    signal_sq = sum((_dot(d2, d2) for d2 in d2s), Decimal(0))
    nrms = Decimal(0) if signal_sq == 0 else (residual_sq / signal_sq).sqrt()
    return {
        "available": True,
        "equation": "D2 Psi_n + lambda * L_reciprocal(Psi_n) = eta_n",
        "lambda": str(lam),
        "normalized_residual_rms": str(nrms),
        "interior_sample_count": len(residuals),
        "reciprocal_graph_edges": ["x<->z", "y<->w"],
    }


def _parse(path: Path) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    meta = None
    target = None
    records: list[dict[str, Any]] = []
    batch_result = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        rec = json.loads(raw)
        kind = rec.get("type")
        if kind == "batch_meta":
            meta = rec
        elif kind == "target_state":
            target = rec
        elif kind == "benchmark":
            records.append(rec)
        elif kind == "batch_result":
            batch_result = rec
    if meta is None or target is None or batch_result is None or batch_result.get("result") != "PASS":
        raise ValueError("incomplete reciprocal-wave batch")
    return meta, target, records, batch_result


def _state_tuple(rec: dict[str, Any]) -> tuple[int, int, int, int, int]:
    return (
        int(rec["completed_queries"]),
        int(rec["represented_transitions"]),
        int(rec["descriptor_bits"]),
        int(rec["endpoint_digest"]),
        int(rec["descriptor_digest"]),
    )


def _target_tuple(target: dict[str, Any]) -> tuple[int, int, int, int, int]:
    return (
        int(target["completed_queries"]),
        int(target["represented_transitions"]),
        int(target["descriptor_bits"]),
        int(target["endpoint_digest"]),
        int(target["descriptor_digest"]),
    )


def _signed_residual(rec: dict[str, Any], target: dict[str, Any], leg_budget_ns: int) -> Decimal:
    if bool(rec["dataset_complete"]):
        return (Decimal(int(rec["completion_elapsed_ns"])) - Decimal(leg_budget_ns)) / Decimal(leg_budget_ns)
    target_work = Decimal(int(target["represented_transitions"]))
    done = Decimal(int(rec["represented_transitions"]))
    if target_work <= 0 or done < 0 or done > target_work:
        raise ValueError("invalid incomplete-work relation")
    return (target_work - done) / target_work


def analyze(meta: dict[str, Any], target: dict[str, Any], records: list[dict[str, Any]], batch_result: dict[str, Any]) -> dict[str, Any]:
    if meta.get("schema") != SCHEMA:
        raise ValueError("unexpected schema")
    if int(meta["global_budget_ns"]) != GLOBAL_BUDGET_NS:
        raise ValueError("global pass is not exactly 120ms")
    if int(meta.get("active_threads_per_benchmark", 0)) != 1 or not bool(meta.get("benchmarks_sequential")):
        raise ValueError("benchmark must be sequential and single-threaded")
    sample_count = int(meta["sample_count"])
    if sample_count <= 0:
        raise ValueError("sample_count must be positive")
    if len(records) != 4 * sample_count:
        raise ValueError("expected exactly four legs per sample")
    if int(meta["nominal_measured_budget_ns"]) > GLOBAL_BUDGET_NS:
        raise ValueError("nominal budget exceeds global 120ms")
    if int(batch_result["batch_elapsed_ns"]) > GLOBAL_BUDGET_NS + 10_000_000:
        raise ValueError("measured batch exceeded timing tolerance")

    leg_budget_ns = int(meta["leg_budget_ns"])
    threshold_ns = int(meta["reasonable_completion_threshold_ns"])
    subthreshold = bool(meta["subthreshold"])
    if subthreshold != (leg_budget_ns < threshold_ns):
        raise ValueError("subthreshold classification mismatch")

    target_state = _target_tuple(target)
    grouped: dict[int, dict[str, dict[str, Any]]] = {}
    for rec in records:
        sample = int(rec["sample"])
        ident = str(rec["id"])
        grouped.setdefault(sample, {})[ident] = rec
    if set(grouped) != set(range(sample_count)):
        raise ValueError("sample indices are not contiguous")

    vectors: list[list[Decimal]] = []
    balances: list[Decimal] = []
    sample_evidence: list[dict[str, Any]] = []
    supremacy_samples: list[int] = []
    for i in range(sample_count):
        legs = grouped[i]
        if set(legs) != {"A", "B", "C", "D"}:
            raise ValueError(f"sample {i} missing A/B/C/D")
        expected_arch = {"A": "hhs", "B": "conventional_matrix", "C": "conventional_matrix", "D": "hhs"}
        expected_axis = {"A": "x", "B": "y", "C": "z", "D": "w"}
        for ident, rec in legs.items():
            if rec.get("architecture") != expected_arch[ident] or rec.get("axis") != expected_axis[ident] or rec.get("dataset") != "W":
                raise ValueError(f"sample {i} {ident}: route identity mismatch")
            if int(rec["dataset_limit_queries"]) != int(target["completed_queries"]):
                raise ValueError(f"sample {i} {ident}: target size mismatch")
            if ident in ("A", "D"):
                if int(rec.get("lane5_admissions", -1)) != int(rec["completed_queries"]):
                    raise ValueError(f"sample {i} {ident}: Lane 5 admission mismatch")
                if int(rec.get("materialized_intermediate_states", -1)) != 0:
                    raise ValueError(f"sample {i} {ident}: intermediate materialization")

        completed = {k: bool(v["dataset_complete"]) for k, v in legs.items()}
        if not subthreshold and not all(completed.values()):
            raise ValueError(f"sample {i}: incomplete work above reasonable threshold")
        if all(completed.values()):
            for ident, rec in legs.items():
                if _state_tuple(rec) != target_state:
                    raise ValueError(f"sample {i} {ident}: completed state != State(W)")
        if completed["A"] and completed["D"] and (not completed["B"] or not completed["C"]):
            supremacy_samples.append(i)

        eps = [_signed_residual(legs[k], target, leg_budget_ns) for k in ("A", "B", "C", "D")]
        vectors.append(eps)
        balance = (eps[0] + eps[3]) / Decimal(2) + (eps[1] + eps[2]) / Decimal(2)
        balances.append(balance)
        sample_evidence.append({
            "sample": i,
            "query_scale": int(target["completed_queries"]),
            "xyzw_signed_residuals": [str(x) for x in eps],
            "architecture_balance": str(balance),
            "completion": completed,
            "completion_elapsed_ns": {k: int(v["completion_elapsed_ns"]) for k, v in legs.items()},
            "represented_transitions": {k: int(v["represented_transitions"]) for k, v in legs.items()},
        })

    mean_balance = _mean(balances)
    sd = _sample_sd(balances)
    se = Decimal(0) if sample_count < 2 else sd / Decimal(sample_count).sqrt()
    ci_low = mean_balance - Z95 * se
    ci_high = mean_balance + Z95 * se

    return {
        "schema": EVIDENCE_SCHEMA,
        "result": "PASS",
        "global_budget_ns": GLOBAL_BUDGET_NS,
        "batch_elapsed_ns": int(batch_result["batch_elapsed_ns"]),
        "sample_count": sample_count,
        "leg_budget_ns": leg_budget_ns,
        "reasonable_completion_threshold_ns": threshold_ns,
        "subthreshold": subthreshold,
        "target_state": {
            "queries": target_state[0],
            "represented_transitions": target_state[1],
            "descriptor_bits": target_state[2],
            "endpoint_digest": target_state[3],
            "descriptor_digest": target_state[4],
        },
        "probabilistic_balance": {
            "mean": str(mean_balance),
            "sample_sd": str(sd),
            "confidence_95_low": str(ci_low),
            "confidence_95_high": str(ci_high),
            "zero_inside_95_percent_interval": ci_low <= 0 <= ci_high,
        },
        "discrete_reciprocal_wave_fit": _wave_fit(vectors),
        "bounded_supremacy_observation_samples": supremacy_samples,
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
        "samples": sample_evidence,
        "claim_scope": {
            "same_exact_state_required_when_above_threshold": True,
            "physical_negative_time_claim": False,
            "universal_classical_supremacy_claim": False,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("batch_ndjson", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    meta, target, records, batch_result = _parse(args.batch_ndjson)
    evidence = analyze(meta, target, records, batch_result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("HHS_120MS_GLOBAL_RECIPROCAL_WAVE_XYZW_V3_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
