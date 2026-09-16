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
SCHEMA = "HHS_TIME_BOUNDED_MATH_SUPREMACY_V2_EVIDENCE"


def _cpu_model() -> str:
    p = Path("/proc/cpuinfo")
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def _cc_version() -> str:
    try:
        return subprocess.run(["cc", "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
    except Exception:
        return "unknown"


def parse(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    meta = None
    cases: list[dict[str, Any]] = []
    witness = None
    terminal = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        rec = json.loads(raw)
        if rec.get("type") == "meta":
            meta = rec
        elif rec.get("type") == "case":
            cases.append(rec)
        elif rec.get("type") == "witness":
            witness = rec
        elif rec.get("type") == "result":
            terminal = rec.get("result") == "PASS"
    if meta is None or witness is None or not terminal:
        raise ValueError("v2 evidence is incomplete")
    return meta, cases, witness


def analyze(meta: dict[str, Any], cases: list[dict[str, Any]], witness: dict[str, Any]) -> dict[str, Any]:
    if meta.get("schema") != "HHS_TIME_BOUNDED_MATH_SUPREMACY_V2":
        raise ValueError("unexpected benchmark schema")
    deadline = int(meta["deadline_ns"])
    if deadline != 120_000_000:
        raise ValueError("v2 requires the 120ms common deadline")
    if int(meta.get("active_threads", 0)) != 1:
        raise ValueError("v2 must be single-threaded")
    if meta.get("legacy_class") != "L_step_state_materializing":
        raise ValueError("unexpected legacy comparator class")
    if len(cases) < 2:
        raise ValueError("at least one calibration and one witness case are required")

    last_k = 0
    calibrations: list[dict[str, Any]] = []
    witness_case = None
    for rec in cases:
        k = int(rec["k"])
        if last_k and k != last_k * 10:
            raise ValueError("gradient must scale k by exactly 10")
        last_k = k
        if int(rec["hhs_endpoint"]) != int(rec["independent_endpoint"]):
            raise ValueError("HHS and independent verifier disagree")
        if int(rec["hhs_total_ns"]) > deadline:
            raise ValueError("HHS exceeded deadline")
        if bool(rec["legacy_solved"]):
            if int(rec["legacy_endpoint"]) != int(rec["hhs_endpoint"]):
                raise ValueError("calibration endpoint mismatch")
            if int(rec["legacy_steps"]) != k:
                raise ValueError("solved legacy case did not execute k transitions")
            calibrations.append(rec)
        else:
            if witness_case is not None:
                raise ValueError("more than one incomplete case after stop")
            if int(rec["legacy_steps"]) <= 0 or int(rec["legacy_steps"]) >= k:
                raise ValueError("invalid incomplete legacy work count")
            witness_case = rec

    if not calibrations or witness_case is None:
        raise ValueError("missing calibration or bounded witness case")
    k_star = int(witness["k_star"])
    if witness.get("result") != "BOUNDED_SUPREMACY_WITNESS":
        raise ValueError("witness marker missing")
    if k_star != int(witness_case["k"]):
        raise ValueError("witness k does not match first incomplete case")
    if int(witness["last_both_complete_k"]) != int(calibrations[-1]["k"]):
        raise ValueError("last calibration k mismatch")
    if int(witness["deadline_ns"]) != deadline:
        raise ValueError("witness deadline mismatch")
    if int(witness["materialized_intermediate_states"]) != 0:
        raise ValueError("HHS materialized intermediate states")

    hhs_ns = Decimal(int(witness_case["hhs_total_ns"]))
    hhs_s = hhs_ns / Decimal(1_000_000_000)
    comps = Decimal(int(witness_case["hhs_compositions"]))
    steps = Decimal(int(witness_case["legacy_steps"]))
    k_dec = Decimal(k_star)
    completion_fraction = steps / k_dec
    work_ratio = k_dec / comps
    time_lb = Decimal(deadline) / hhs_ns
    info_bits = Decimal(str(math.log2(k_star)))
    info_density = info_bits / hhs_s

    return {
        "schema": SCHEMA,
        "result": "PASS",
        "claim": "BOUNDED_SUPREMACY_WITNESS",
        "legacy_class": "L_step_state_materializing",
        "deadline_ns_each_architecture": deadline,
        "gradient_factor": 10,
        "calibration_case_count": len(calibrations),
        "last_both_complete_k": int(calibrations[-1]["k"]),
        "k_star": k_star,
        "hhs": {
            "endpoint": int(witness_case["hhs_endpoint"]),
            "total_ns": int(witness_case["hhs_total_ns"]),
            "composition_count": int(witness_case["hhs_compositions"]),
            "independent_verifier_equal": True,
            "materialized_intermediate_states": 0,
            "lane5_candidate_only": True,
        },
        "legacy": {
            "complete": False,
            "executed_steps": int(witness_case["legacy_steps"]),
            "elapsed_ns": int(witness_case["legacy_elapsed_ns"]),
            "completion_fraction": str(completion_fraction),
            "unresolved_fraction": str(Decimal(1) - completion_fraction),
        },
        "normalization": {
            "declared_work_lower_bound": k_star,
            "problem_information_bits_equivalent": str(info_bits),
            "hhs_problem_information_bits_equivalent_per_second": str(info_density),
            "exact_work_ratio_k_over_hhs_compositions": str(work_ratio),
            "time_advantage_lower_bound": str(time_lb),
        },
        "runner": {
            "cpu_model": _cpu_model(),
            "logical_cpu_count": os.cpu_count(),
            "platform": platform.platform(),
            "kernel_release": platform.release(),
            "runner_os_env": os.getenv("RUNNER_OS"),
            "runner_arch_env": os.getenv("RUNNER_ARCH"),
            "image_os_env": os.getenv("ImageOS"),
            "image_version_env": os.getenv("ImageVersion"),
            "cc_version": _cc_version(),
        },
        "falsifiability": {
            "legacy_completion_at_k_star_would_falsify": True,
            "hhs_deadline_failure_would_falsify": True,
            "independent_verifier_disagreement_would_falsify": True,
            "lane5_admission_failure_would_falsify": True,
        },
        "claim_scope": "Existence result against the explicitly defined linear state-materializing comparator class; not a universal lower bound for all classical algorithms.",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    meta, cases, witness = parse(args.input)
    evidence = analyze(meta, cases, witness)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("HHS_TIME_BOUNDED_MATH_SUPREMACY_V2_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
