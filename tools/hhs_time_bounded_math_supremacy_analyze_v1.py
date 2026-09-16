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

H_ADDR = Decimal("444.23460010384649012933840792848557726141327470771727270562838225391814480238763")
SCHEMA = "HHS_TIME_BOUNDED_MATH_SUPREMACY_V1_EVIDENCE"


def _cpu_model() -> str:
    path = Path("/proc/cpuinfo")
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def _memory_kib() -> int | None:
    path = Path("/proc/meminfo")
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1])
    return None


def _cc_version() -> str:
    try:
        return subprocess.run(["cc", "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
    except Exception:
        return "unknown"


def load_native_cases(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    meta: dict[str, Any] | None = None
    cases: list[dict[str, Any]] = []
    terminal_pass = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        record = json.loads(raw)
        if record.get("type") == "meta":
            meta = record
        elif record.get("type") == "case":
            cases.append(record)
        elif record.get("type") == "result":
            terminal_pass = record.get("result") == "PASS"
    if meta is None or not cases or not terminal_pass:
        raise ValueError("native evidence is incomplete")
    return meta, cases


def analyze(native_control: dict[str, Any], meta: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, Any]:
    if native_control.get("result") != "PASS":
        raise ValueError("same-runner Lane 5 normalization control did not pass")
    if native_control.get("materialized_intermediate_states") != 0:
        raise ValueError("normalization control materialized intermediate states")

    time_bound_ns = int(meta["time_bound_ns"])
    if time_bound_ns <= 0:
        raise ValueError("invalid time bound")

    enriched: list[dict[str, Any]] = []
    crossovers: dict[str, dict[str, Any]] = {}
    solved_counts: dict[str, int] = {}
    timeout_counts: dict[str, int] = {}

    for case in cases:
        family = str(case["family"])
        omega = int(case["omega"])
        hhs_ns = int(case["hhs_total_ns"])
        work_lower = int(case["linear_work_lower_bound"])
        hhs_work = int(case["hhs_compositions"])
        linear_elapsed = int(case["linear_elapsed_ns"])
        status = str(case["linear_status"])

        if omega <= 1 or hhs_ns <= 0 or hhs_work <= 0 or work_lower <= 0:
            raise ValueError(f"invalid metrics for {family}:{case['size']}")
        if hhs_ns > time_bound_ns:
            raise ValueError(f"HHS exceeded time bound for {family}:{case['size']}")
        if not case.get("exact") or not case.get("lane5_admitted"):
            raise ValueError(f"exact/admission failure for {family}:{case['size']}")
        if int(case.get("materialized_intermediate_states", -1)) != 0:
            raise ValueError(f"intermediate materialization for {family}:{case['size']}")
        if int(case["hhs_result"]) != int(case["independent_result"]):
            raise ValueError(f"independent verifier disagreement for {family}:{case['size']}")

        h_bits = math.log2(omega)
        gamma_problem = h_bits * 1_000_000_000.0 / hhs_ns
        work_ratio = Decimal(work_lower) / Decimal(hhs_work)

        if status == "solved":
            solved_counts[family] = solved_counts.get(family, 0) + 1
            if int(case["linear_result"]) != int(case["hhs_result"]):
                raise ValueError(f"linear endpoint disagreement for {family}:{case['size']}")
            time_ratio_kind = "executed"
            time_ratio = Decimal(linear_elapsed) / Decimal(hhs_ns)
        elif status == "timeout":
            timeout_counts[family] = timeout_counts.get(family, 0) + 1
            time_ratio_kind = "lower_bound"
            time_ratio = Decimal(time_bound_ns) / Decimal(hhs_ns)
            crossovers.setdefault(
                family,
                {
                    "size": case["size"],
                    "omega": omega,
                    "hhs_total_ns": hhs_ns,
                    "linear_time_bound_ns": time_bound_ns,
                    "linear_steps_completed_before_timeout": int(case["linear_steps"]),
                    "linear_work_lower_bound": work_lower,
                    "hhs_compositions": hhs_work,
                },
            )
        else:
            raise ValueError(f"unknown comparator status {status!r}")

        item = dict(case)
        item["problem_information_bits_equivalent"] = repr(h_bits)
        item["problem_information_density_bits_equivalent_per_second"] = repr(gamma_problem)
        item["exact_work_ratio_linear_lower_bound_over_hhs"] = str(work_ratio)
        item["time_ratio_kind"] = time_ratio_kind
        item["time_ratio_linear_over_hhs"] = str(time_ratio)
        enriched.append(item)

    families = sorted({str(case["family"]) for case in cases})
    for family in families:
        if solved_counts.get(family, 0) == 0:
            raise ValueError(f"no exact completed linear control for {family}")
        if timeout_counts.get(family, 0) == 0:
            raise ValueError(f"no bounded crossover observed for {family}")
        if family not in crossovers:
            raise ValueError(f"missing crossover for {family}")

    candidate_rate = Decimal(int(native_control["candidates_per_second_floor"]))
    same_runner_basis_rate = candidate_rate * H_ADDR

    return {
        "schema": SCHEMA,
        "result": "PASS",
        "claim_scope": {
            "supremacy_class": "declared linear/materializing comparator classes only",
            "universal_classical_supremacy_claim": False,
            "stage": 1,
            "falsifiable": True,
        },
        "resource_envelope": {
            "runner_label": "ubuntu-24.04",
            "active_threads": int(meta.get("active_threads", 1)),
            "per_case_time_bound_ns": time_bound_ns,
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
        "same_runner_lane5_control": {
            "candidate_count": int(native_control["scale_candidates"]),
            "elapsed_ns": int(native_control["elapsed_ns"]),
            "candidate_rate_floor_per_second": int(native_control["candidates_per_second_floor"]),
            "basis_information_rate_bits_equivalent_per_second": str(same_runner_basis_rate),
            "stream_state_bytes": int(native_control["stream_state_bytes"]),
            "materialized_intermediate_states": int(native_control["materialized_intermediate_states"]),
        },
        "crossovers": crossovers,
        "cases": enriched,
        "interpretation": {
            "affine": "O(log k) exact affine-map composition versus C_step restricted to k sequential transition applications",
            "crt": "incremental exact CRT composition versus C_scan restricted to enumeration from 0 through the unique target M-1",
            "next_stage": "add optimized conventional algorithms as separate comparator classes; do not generalize this result beyond the declared linear classes",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("native_control", type=Path)
    parser.add_argument("math_ndjson", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    native_control = json.loads(args.native_control.read_text(encoding="utf-8"))
    meta, cases = load_native_cases(args.math_ndjson)
    evidence = analyze(native_control, meta, cases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("HHS_TIME_BOUNDED_MATH_SUPREMACY_V1_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
