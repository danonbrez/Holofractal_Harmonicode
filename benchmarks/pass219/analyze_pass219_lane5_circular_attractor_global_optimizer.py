#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "HHS_PASS219_LANE5_CIRCULAR_ATTRACTOR_GLOBAL_OPTIMIZER_BENCHMARK_V1":
        raise SystemExit("unexpected benchmark schema")
    if data.get("result") != "PASS":
        raise SystemExit("native benchmark did not pass")
    return data


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("timing_is_canonical") is not False:
        raise SystemExit("benchmark timing promoted to canonical authority")
    for field in (
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "floating_point_canonical_authority",
    ):
        if data.get(field) is not False:
            raise SystemExit(f"authority drift: {field}")
    if data.get("candidate_only") is not True:
        raise SystemExit("candidate-only boundary drift")
    if data.get("negative_invalid_best_fallback_passed") is not True:
        raise SystemExit("invalid-best fallback did not pass")
    if data.get("negative_authority_escalation_fallback_passed") is not True:
        raise SystemExit("authority-escalation fallback did not pass")

    cases = data.get("cases") or []
    if len(cases) != 16:
        raise SystemExit(f"expected 16 benchmark cases, got {len(cases)}")

    by_count: dict[int, list[dict[str, Any]]] = defaultdict(list)
    observed_speedups: list[int] = []
    for case in cases:
        count = int(case["candidate_count"])
        target = int(case["target_phase"])
        if target not in (0, 18, 36, 54):
            raise SystemExit("quarter-phase target coverage drift")
        if case.get("exact_selected_route_equal") is not True:
            raise SystemExit("exhaustive/attractor route mismatch")
        if int(case["phase_distance_squared"]) != 0:
            raise SystemExit("selected route is not at circular closure")
        if int(case["exhaustive_full_validations"]) != count:
            raise SystemExit("exhaustive validation accounting drift")
        if int(case["attractor_full_validations"]) != 1:
            raise SystemExit("attractor fast path did not close in one full validation")
        if int(case["validation_reduction_x1000"]) != count * 1000:
            raise SystemExit("exact validation reduction drift")
        if int(case["exhaustive_mean_ns_floor"]) <= 0 or int(case["attractor_mean_ns_floor"]) <= 0:
            raise SystemExit("non-positive timing sample")
        speedup = int(case["observed_speedup_x1000"])
        if speedup <= 0:
            raise SystemExit("invalid speedup observation")
        observed_speedups.append(speedup)
        by_count[count].append(case)

    if set(by_count) != {64, 256, 1024, 4096}:
        raise SystemExit(f"candidate-count coverage drift: {sorted(by_count)}")
    if any({int(x["target_phase"]) for x in rows} != {0, 18, 36, 54} for rows in by_count.values()):
        raise SystemExit("each candidate count must cover all four quarter phases")

    summaries: list[dict[str, Any]] = []
    for count in sorted(by_count):
        rows = by_count[count]
        speeds = sorted(int(x["observed_speedup_x1000"]) for x in rows)
        exhaustive = [int(x["exhaustive_mean_ns_floor"]) for x in rows]
        attractor = [int(x["attractor_mean_ns_floor"]) for x in rows]
        summaries.append(
            {
                "candidate_count": count,
                "phase_targets": [0, 18, 36, 54],
                "validation_reduction_exact_x": count,
                "observed_speedup_x1000_min": min(speeds),
                "observed_speedup_x1000_median": int(statistics.median(speeds)),
                "observed_speedup_x1000_max": max(speeds),
                "exhaustive_mean_ns_floor_median": int(statistics.median(exhaustive)),
                "attractor_mean_ns_floor_median": int(statistics.median(attractor)),
                "all_exact_selected_route_equal": True,
            }
        )

    all_wall_speedups = all(v > 1000 for v in observed_speedups)
    classification = (
        "CIRCULAR_ATTRACTOR_EXACT_WORK_AND_WALL_LATENCY_REDUCTION_OBSERVED"
        if all_wall_speedups
        else "CIRCULAR_ATTRACTOR_EXACT_WORK_REDUCTION_PROVEN_WALL_LATENCY_ENVIRONMENT_DEPENDENT"
    )

    return {
        "schema": "HHS_PASS219_LANE5_CIRCULAR_ATTRACTOR_GLOBAL_OPTIMIZER_ANALYSIS_V1",
        "classification": classification,
        "base_main": data["base_main"],
        "case_count": len(cases),
        "quarter_phase_coverage": True,
        "global_constraint_validation_reused_existing_native_validator": True,
        "exact_selected_route_equality": True,
        "exact_full_validation_reduction": True,
        "minimum_validation_reduction_exact_x": min(by_count),
        "maximum_validation_reduction_exact_x": max(by_count),
        "all_observed_wall_speedups_gt_1": all_wall_speedups,
        "global_observed_speedup_x1000_min": min(observed_speedups),
        "global_observed_speedup_x1000_median": int(statistics.median(observed_speedups)),
        "global_observed_speedup_x1000_max": max(observed_speedups),
        "negative_controls": {
            "invalid_best_falls_back_to_exhaustive": True,
            "authority_escalation_candidate_rejected": True,
        },
        "latency_policy": {
            "policy": "PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0",
            "classification_is_observational": True,
            "timing_changes_canonical_identity": False,
        },
        "authority": {
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "floating_point_canonical_authority": False,
        },
        "by_candidate_count": summaries,
        "result": "PASS",
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: analyze <benchmark.json> <analysis.json>")
    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    result = analyze(load(source))
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "classification": result["classification"],
        "case_count": result["case_count"],
        "global_observed_speedup_x1000_min": result["global_observed_speedup_x1000_min"],
        "global_observed_speedup_x1000_median": result["global_observed_speedup_x1000_median"],
        "global_observed_speedup_x1000_max": result["global_observed_speedup_x1000_max"],
        "minimum_validation_reduction_exact_x": result["minimum_validation_reduction_exact_x"],
        "maximum_validation_reduction_exact_x": result["maximum_validation_reduction_exact_x"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
