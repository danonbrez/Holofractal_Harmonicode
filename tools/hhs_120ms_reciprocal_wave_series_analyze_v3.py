#!/usr/bin/env python3
from __future__ import annotations

import argparse
from decimal import Decimal, getcontext
import json
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


def _parse(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[int, dict[str, Any]], dict[str, Any]]:
    meta = None
    records: list[dict[str, Any]] = []
    refs: dict[int, dict[str, Any]] = {}
    batch_result = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        rec = json.loads(raw)
        kind = rec.get("type")
        if kind == "batch_meta":
            meta = rec
        elif kind == "benchmark":
            records.append(rec)
        elif kind == "sample_reference":
            refs[int(rec["sample"])] = rec
        elif kind == "batch_result":
            batch_result = rec
    if meta is None or batch_result is None or batch_result.get("result") != "PASS":
        raise ValueError("incomplete reciprocal-wave batch")
    return meta, records, refs, batch_result


def _state_tuple(rec: dict[str, Any]) -> tuple[int, int, int, int, int]:
    return (
        int(rec["completed_queries"]), int(rec["represented_transitions"]), int(rec["descriptor_bits"]),
        int(rec["endpoint_digest"]), int(rec["descriptor_digest"]),
    )


def _reference_tuple(ref: dict[str, Any]) -> tuple[int, int, int, int, int]:
    return (
        int(ref["completed_queries"]), int(ref["represented_transitions"]), int(ref["descriptor_bits"]),
        int(ref["endpoint_digest"]), int(ref["descriptor_digest"]),
    )


def _signed_residual(rec: dict[str, Any], ref: dict[str, Any]) -> Decimal:
    budget = Decimal(int(rec["leg_budget_ns"]))
    if bool(rec["dataset_complete"]):
        return (Decimal(int(rec["completion_elapsed_ns"])) - budget) / budget
    target = Decimal(int(ref["represented_transitions"]))
    done = Decimal(int(rec["represented_transitions"]))
    if target <= 0 or done < 0 or done > target:
        raise ValueError("invalid incomplete-work relation")
    return (target - done) / target


def analyze(meta: dict[str, Any], records: list[dict[str, Any]], refs: dict[int, dict[str, Any]], batch_result: dict[str, Any]) -> dict[str, Any]:
    if meta.get("schema") != SCHEMA or int(meta["global_budget_ns"]) != GLOBAL_BUDGET_NS:
        raise ValueError("unexpected schema/global budget")
    if int(meta.get("active_threads_per_benchmark", 0)) != 1 or not bool(meta.get("benchmarks_sequential")):
        raise ValueError("benchmark must be sequential and single-threaded")
    sample_count = int(batch_result["sample_count"])
    if sample_count <= 0 or len(records) != 4 * sample_count or set(refs) != set(range(sample_count)):
        raise ValueError("sample cardinality mismatch")
    batch_elapsed = int(batch_result["batch_elapsed_ns"])
    if batch_elapsed > GLOBAL_BUDGET_NS + 10_000_000:
        raise ValueError("measured batch exceeded global timing tolerance")

    grouped: dict[int, dict[str, dict[str, Any]]] = {}
    for rec in records:
        grouped.setdefault(int(rec["sample"]), {})[str(rec["id"])] = rec
    if set(grouped) != set(range(sample_count)):
        raise ValueError("sample indices are not contiguous")

    vectors: list[list[Decimal]] = []
    balances: list[Decimal] = []
    evidence_samples: list[dict[str, Any]] = []
    bounded_supremacy_samples: list[int] = []
    previous_scale = 0

    for i in range(sample_count):
        legs = grouped[i]
        ref = refs[i]
        if set(legs) != {"A", "B", "C", "D"}:
            raise ValueError(f"sample {i}: missing A/B/C/D")
        scale = int(ref["query_scale"])
        if scale <= previous_scale:
            raise ValueError("gradient query scale did not increase")
        if i > 0 and scale != previous_scale * 2:
            raise ValueError("gradient factor must be exactly 2")
        previous_scale = scale
        expected_arch = {"A": "hhs", "B": "conventional_matrix", "C": "conventional_matrix", "D": "hhs"}
        expected_axis = {"A": "x", "B": "y", "C": "z", "D": "w"}
        budgets = {int(v["leg_budget_ns"]) for v in legs.values()}
        thresholds = {int(v["predicted_threshold_ns"]) for v in legs.values()}
        if len(budgets) != 1 or len(thresholds) != 1:
            raise ValueError(f"sample {i}: unequal reciprocal leg budget/threshold")
        leg_budget = next(iter(budgets))
        threshold = next(iter(thresholds))
        subthreshold = bool(ref["subthreshold"])
        if subthreshold != (leg_budget < threshold):
            raise ValueError(f"sample {i}: subthreshold classification mismatch")

        for ident, rec in legs.items():
            if rec.get("architecture") != expected_arch[ident] or rec.get("axis") != expected_axis[ident] or rec.get("dataset") != "W":
                raise ValueError(f"sample {i} {ident}: route identity mismatch")
            if int(rec["dataset_limit_queries"]) != scale or int(rec["query_scale"]) != scale:
                raise ValueError(f"sample {i} {ident}: workload scale mismatch")
            if ident in ("A", "D"):
                if int(rec.get("lane5_admissions", -1)) != int(rec["completed_queries"]):
                    raise ValueError(f"sample {i} {ident}: Lane 5 admission mismatch")
                if int(rec.get("materialized_intermediate_states", -1)) != 0:
                    raise ValueError(f"sample {i} {ident}: intermediate materialization")

        completed = {k: bool(v["dataset_complete"]) for k, v in legs.items()}
        ref_state = _reference_tuple(ref)
        if not subthreshold and not all(completed.values()):
            raise ValueError(f"sample {i}: incomplete work above predicted reasonable threshold")
        if all(completed.values()):
            for ident, rec in legs.items():
                if _state_tuple(rec) != ref_state:
                    raise ValueError(f"sample {i} {ident}: completed state differs from State(W_n)")
        if completed["A"] and completed["D"] and (not completed["B"] or not completed["C"]):
            bounded_supremacy_samples.append(i)

        eps = [_signed_residual(legs[k], ref) for k in ("A", "B", "C", "D")]
        vectors.append(eps)
        hhs_balance = (eps[0] + eps[3]) / Decimal(2)
        conventional_balance = (eps[1] + eps[2]) / Decimal(2)
        balance = hhs_balance + conventional_balance
        balances.append(balance)
        evidence_samples.append({
            "sample": i,
            "query_scale": scale,
            "leg_budget_ns": leg_budget,
            "predicted_threshold_ns": threshold,
            "subthreshold": subthreshold,
            "xyzw_signed_residuals": [str(x) for x in eps],
            "hhs_mean_residual": str(hhs_balance),
            "conventional_mean_residual": str(conventional_balance),
            "architecture_balance": str(balance),
            "completion": completed,
            "same_state_if_complete": all((not completed[k]) or _state_tuple(legs[k]) == ref_state for k in legs),
            "target_represented_transitions": int(ref["represented_transitions"]),
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
        "batch_elapsed_ns": batch_elapsed,
        "remaining_budget_ns": int(batch_result["remaining_budget_ns"]),
        "sample_count": sample_count,
        "gradient_factor": int(meta["gradient_factor"]),
        "base_dataset_queries": int(meta["base_dataset_queries"]),
        "probabilistic_balance": {
            "mean": str(mean_balance), "sample_sd": str(sd),
            "confidence_95_low": str(ci_low), "confidence_95_high": str(ci_high),
            "zero_inside_95_percent_interval": ci_low <= 0 <= ci_high,
        },
        "discrete_reciprocal_wave_fit": _wave_fit(vectors),
        "bounded_supremacy_observation_samples": bounded_supremacy_samples,
        "runner": {
            "cpu_model": _cpu_model(), "logical_cpu_count": os.cpu_count(), "memory_kib": _memory_kib(),
            "platform": platform.platform(), "kernel_release": platform.release(),
            "runner_os_env": os.getenv("RUNNER_OS"), "runner_arch_env": os.getenv("RUNNER_ARCH"),
            "image_os_env": os.getenv("ImageOS"), "image_version_env": os.getenv("ImageVersion"),
            "cc_version": _cc_version(),
        },
        "samples": evidence_samples,
        "claim_scope": {
            "same_exact_state_required_above_threshold": True,
            "positive_global_time_drives_larger_gradient_workloads": True,
            "physical_negative_time_claim": False,
            "universal_classical_supremacy_claim": False,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("batch_ndjson", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    meta, records, refs, batch_result = _parse(args.batch_ndjson)
    evidence = analyze(meta, records, refs, batch_result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("HHS_120MS_GLOBAL_RECIPROCAL_WAVE_XYZW_V3_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
