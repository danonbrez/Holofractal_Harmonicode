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

getcontext().prec = 80
SCHEMA = "HHS_120S_RECIPROCAL_XYZW_V2_EVIDENCE"


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


def load_records(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    meta: dict[str, Any] | None = None
    benches: dict[str, dict[str, Any]] = {}
    verifications: dict[str, dict[str, Any]] = {}
    terminal = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        rec = json.loads(raw)
        kind = rec.get("type")
        if kind == "meta":
            meta = rec
        elif kind == "benchmark":
            benches[str(rec["id"])] = rec
        elif kind == "verification":
            verifications[str(rec["dataset"])] = rec
        elif kind == "result":
            terminal = rec.get("result") == "PASS"
    if not terminal or meta is None:
        raise ValueError("reciprocal benchmark evidence is incomplete")
    if set(benches) != {"A", "B", "C", "D"}:
        raise ValueError("exactly A/B/C/D benchmark records are required")
    if set(verifications) != {"X", "Y"}:
        raise ValueError("dataset X/Y verification records are required")
    return meta, benches, verifications


def _rate(value: int, elapsed_ns: int) -> Decimal:
    return Decimal(value) * Decimal(1_000_000_000) / Decimal(elapsed_ns)


def _seconds(ns: int) -> Decimal:
    return Decimal(ns) / Decimal(1_000_000_000)


def analyze(
    meta: dict[str, Any],
    benches: dict[str, dict[str, Any]],
    verifications: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if meta.get("schema") != "HHS_120S_RECIPROCAL_XYZW_V2":
        raise ValueError("unexpected benchmark schema")
    window = int(meta["window_ns"])
    if window <= 0:
        raise ValueError("invalid capacity window")
    if int(meta.get("active_threads_per_benchmark", 0)) != 1:
        raise ValueError("benchmark must be single-thread per pass")
    if not bool(meta.get("benchmarks_sequential")):
        raise ValueError("A/B/C/D must execute sequentially")

    a, b, c, d = (benches[k] for k in ("A", "B", "C", "D"))
    expected = {
        "A": ("x", "hhs", "X", "capacity_120s"),
        "B": ("y", "conventional_matrix", "Y", "capacity_120s"),
        "C": ("z", "conventional_matrix", "X", "reciprocal_completion"),
        "D": ("w", "hhs", "Y", "reciprocal_completion"),
    }
    for ident, rec in benches.items():
        axis, arch, dataset, mode = expected[ident]
        if (rec.get("axis"), rec.get("architecture"), rec.get("dataset"), rec.get("mode")) != (
            axis, arch, dataset, mode
        ):
            raise ValueError(f"{ident} identity mismatch")
        if int(rec["completed_queries"]) <= 0 or int(rec["elapsed_ns"]) <= 0:
            raise ValueError(f"{ident} produced no measurable work")

    tolerance = max(1_000_000_000, window // 100)
    for ident in ("A", "B"):
        elapsed = int(benches[ident]["elapsed_ns"])
        if elapsed < window:
            raise ValueError(f"{ident} stopped before the capacity window")
        if elapsed > window + tolerance:
            raise ValueError(f"{ident} exceeded capacity-window tolerance")

    for producer_id, consumer_id, dataset in (("A", "C", "X"), ("B", "D", "Y")):
        producer = benches[producer_id]
        consumer = benches[consumer_id]
        for field in (
            "completed_queries",
            "represented_transitions",
            "descriptor_bits",
            "endpoint_digest",
            "descriptor_digest",
        ):
            if int(producer[field]) != int(consumer[field]):
                raise ValueError(f"dataset {dataset} differs at {field}")
        v = verifications[dataset]
        if not v.get("exact"):
            raise ValueError(f"dataset {dataset} did not verify exactly")
        if str(v.get("producer")) != producer_id or str(v.get("consumer")) != consumer_id:
            raise ValueError(f"dataset {dataset} producer/consumer mismatch")
        if int(v["queries"]) != int(producer["completed_queries"]):
            raise ValueError(f"dataset {dataset} query-count mismatch")
        if int(v["endpoint_digest"]) != int(producer["endpoint_digest"]):
            raise ValueError(f"dataset {dataset} endpoint digest mismatch")
        if int(v["descriptor_digest"]) != int(producer["descriptor_digest"]):
            raise ValueError(f"dataset {dataset} descriptor digest mismatch")

    for ident in ("A", "D"):
        rec = benches[ident]
        if int(rec.get("lane5_admissions", -1)) != int(rec["completed_queries"]):
            raise ValueError(f"{ident} missing Lane 5 admissions")
        if int(rec.get("materialized_intermediate_states", -1)) != 0:
            raise ValueError(f"{ident} materialized represented intermediates")
        if min(int(rec["affine_compositions"]), int(rec["matrix_multiplications"])) <= 0:
            raise ValueError(f"{ident} HHS work counters are invalid")

    for ident in ("B", "C"):
        if int(benches[ident]["matrix_multiplications"]) <= 0:
            raise ValueError(f"{ident} conventional matrix work counter is invalid")

    ae, be, ce, de = (int(benches[k]["elapsed_ns"]) for k in ("A", "B", "C", "D"))
    aq, bq = int(a["completed_queries"]), int(b["completed_queries"])
    at, bt = int(a["represented_transitions"]), int(b["represented_transitions"])

    modulus = int(meta["modulus"])
    state_space_bits = Decimal(str(math.log2(modulus)))
    a_qps, b_qps = _rate(aq, ae), _rate(bq, be)
    a_path_rate, b_path_rate = _rate(at, ae), _rate(bt, be)

    x_speed_hhs_over_conventional = Decimal(ce) / Decimal(ae)
    y_speed_hhs_over_conventional = Decimal(be) / Decimal(de)

    return {
        "schema": SCHEMA,
        "result": "PASS",
        "claim_scope": {
            "capacity_window_seconds": str(_seconds(window)),
            "benchmarks": "A/B are bounded capacity; C/D are unbounded exact reciprocal completion",
            "dataset_rule": "X is chosen only by A then replayed exactly by C; Y is chosen only by B then replayed exactly by D",
            "conventional_architecture": "optimized exact 2x2 homogeneous matrix exponentiation",
            "hhs_architecture": "exact affine composition + independent 2x2 verification + Lane 5 admission",
            "v1_linear_step_baseline_preserved_separately": True,
            "universal_computing_supremacy_claim": False,
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
        "workload": {
            "stream_seed": int(meta["stream_seed"]),
            "modulus": modulus,
            "endpoint_state_space_bits_equivalent": str(state_space_bits),
            "k_min": int(meta["k_min"]),
            "k_span": int(meta["k_span"]),
        },
        "xyzw": {
            "x_A_hhs_capacity_seconds": str(_seconds(ae)),
            "y_B_conventional_capacity_seconds": str(_seconds(be)),
            "z_C_conventional_completes_X_seconds": str(_seconds(ce)),
            "w_D_hhs_completes_Y_seconds": str(_seconds(de)),
        },
        "dataset_X": {
            "producer": "A",
            "consumer": "C",
            "queries": aq,
            "represented_transitions": at,
            "descriptor_bits": int(a["descriptor_bits"]),
            "endpoint_digest": int(a["endpoint_digest"]),
            "descriptor_digest": int(a["descriptor_digest"]),
            "A_hhs_elapsed_ns": ae,
            "C_conventional_elapsed_ns": ce,
            "same_work_speed_hhs_over_conventional": str(x_speed_hhs_over_conventional),
            "exact": True,
        },
        "dataset_Y": {
            "producer": "B",
            "consumer": "D",
            "queries": bq,
            "represented_transitions": bt,
            "descriptor_bits": int(b["descriptor_bits"]),
            "endpoint_digest": int(b["endpoint_digest"]),
            "descriptor_digest": int(b["descriptor_digest"]),
            "B_conventional_elapsed_ns": be,
            "D_hhs_elapsed_ns": de,
            "same_work_speed_hhs_over_conventional": str(y_speed_hhs_over_conventional),
            "exact": True,
        },
        "capacity": {
            "A_hhs_queries_per_second": str(a_qps),
            "B_conventional_queries_per_second": str(b_qps),
            "A_hhs_represented_transitions_per_second": str(a_path_rate),
            "B_conventional_represented_transitions_per_second": str(b_path_rate),
            "A_endpoint_bits_equivalent_per_second": str(state_space_bits * a_qps),
            "B_endpoint_bits_equivalent_per_second": str(state_space_bits * b_qps),
            "query_capacity_ratio_hhs_over_conventional": str(a_qps / b_qps),
            "represented_path_capacity_ratio_hhs_over_conventional": str(a_path_rate / b_path_rate),
        },
        "hhs_control_counts": {
            "A_affine_compositions": int(a["affine_compositions"]),
            "A_matrix_verifier_multiplications": int(a["matrix_multiplications"]),
            "A_lane5_admissions": int(a["lane5_admissions"]),
            "D_affine_compositions": int(d["affine_compositions"]),
            "D_matrix_verifier_multiplications": int(d["matrix_multiplications"]),
            "D_lane5_admissions": int(d["lane5_admissions"]),
        },
        "conventional_control_counts": {
            "B_matrix_multiplications": int(b["matrix_multiplications"]),
            "C_matrix_multiplications": int(c["matrix_multiplications"]),
        },
        "reciprocal_validation": {
            "X": verifications["X"],
            "Y": verifications["Y"],
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("stream_ndjson", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    meta, benches, verifications = load_records(args.stream_ndjson)
    evidence = analyze(meta, benches, verifications)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("HHS_120S_RECIPROCAL_XYZW_V2_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
