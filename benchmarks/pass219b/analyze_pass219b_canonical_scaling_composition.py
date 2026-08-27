#!/usr/bin/env python3
"""Analyze the exact Pass 219B scaling-composition benchmark.

This analyzer does not assign semantic authority from wall-clock timing. It admits a
composition only when the exact reference/equality gates pass, then reports
portable work/capacity reductions and environment-specific timing separately.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

INVARIANT_FAILURE = 5
ROUTE_DENSE_REQUIRED = 2

CANONICAL_ORDER = [
    "EXACT_SELECTOR_AND_PRECONDITION_GATE",
    "PHASE_LOCALITY_BEFORE_CANDIDATE_EXPANSION",
    "PASS207_DETERMINISTIC_BATCHING_AND_CONTENT_KEYED_CACHE",
    "PASS208_CANDIDATE_BRANCH_EXPANSION",
    "EXACT_CPU_VM_ORACLE_EQUALITY",
    "INHERITED_SINGLETON_VM81_CANONICAL_ADMISSION",
    "I7_EXACT_SELECTIVE_PROJECTION_OF_AUTHORITATIVE_STATE",
    "I8_COMPLETE_WITNESS_SPARSE_DIRTY_DERIVED_UPDATE",
    "HASH72_HASH216_EXISTING_RECEIPT_AND_INDEX_PATHS",
]


def load(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ANALYSIS FAIL: {message}")


def ratio_key(p: int, q: int) -> str:
    return f"{p}/{q}"


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "usage: analyze_pass219b_canonical_scaling_composition.py "
            "COMPOSITION.json PHASE_LOCALITY.json PASS208.json OUTPUT.json",
            file=sys.stderr,
        )
        return 2

    composition = load(sys.argv[1])
    locality = load(sys.argv[2])
    pass208 = load(sys.argv[3])

    require(
        composition.get("schema")
        == "HHS_PASS219B_CANONICAL_SCALING_COMPOSITION_BENCHMARK_V1",
        "unexpected composition schema",
    )
    require(composition["authoritative_state_changed"] is False, "benchmark changed authority")
    require(composition["physical_gpu_claimed"] is False, "unexpected physical GPU claim")
    require(composition["wall_clock_is_observational"] is True, "wall timing boundary missing")

    depths = composition["phase_depth"]
    require(len(depths) == composition["phase_max_depth"] == 9, "phase depth sweep incomplete")
    for item in depths:
        depth = item["depth"]
        require(item["potential_phase_volume"] == 81**depth, f"bad phase volume depth {depth}")
        require(item["materialized_phase_volume"] == 1, f"bad selected volume depth {depth}")
        require(item["reduction_numerator"] == 81**depth, f"bad reduction depth {depth}")
        require(item["reduction_denominator"] == 1, f"bad reduction denominator depth {depth}")
        require(item["abstract_required_units"] == 1, f"bad abstract realization depth {depth}")
        require(item["pass208_lane_status"] == 0, f"Pass208 local lane planner failed depth {depth}")
        require(
            item["pass208_required_lane_units"] == 2 * 5184,
            f"selected Pass208 lane units changed at depth {depth}",
        )

    no_selector = composition["no_exact_selector"]
    require(no_selector["route"] == ROUTE_DENSE_REQUIRED, "selector absence did not fail to dense path")
    require(no_selector["dense_realization_forbidden"] == 0, "dense fallback unexpectedly forbidden")
    require(no_selector["required_realized_units"] == 81 * 2 * 5184, "dense fallback work mismatch")

    negative = composition["negative_gates"]
    require(
        negative["locality_authority_request_status"] == INVARIANT_FAILURE,
        "phase locality authority request not rejected",
    )
    require(
        negative["dirty_incomplete_status"] == INVARIANT_FAILURE,
        "incomplete dirty witness not rejected",
    )
    require(
        negative["sparse_authority_request_status"] == INVARIANT_FAILURE,
        "sparse authority request not rejected",
    )

    ratios = {
        ratio_key(item["p"], item["q"]): item for item in composition["projection_ratios"]
    }
    expected_counts = {
        "1/3": 5_875_200,
        "7/20": 6_168_960,
        "5/14": 6_294_860,
        "4/11": 6_409_311,
        "3/8": 6_609_600,
        "2/5": 7_050_240,
        "5/12": 7_344_000,
    }
    require(set(ratios) == set(expected_counts), "projection ratio sweep incomplete")
    for key, count in expected_counts.items():
        require(ratios[key]["selected_count"] == count, f"selected count mismatch {key}")
        require(
            ratios[key]["selected_count"] + ratios[key]["avoided_count"]
            == composition["source_count"],
            f"projection accounting mismatch {key}",
        )

    sparse_cases = composition["sparse_cases"]
    require(len(sparse_cases) == 7 * 5, "sparse composition matrix incomplete")
    for item in sparse_cases:
        require(item["exact_equal"] is True, "sparse/full result inequality")
        require(
            item["update_count"] + item["avoided_count"] == item["selected_count"],
            "sparse accounting mismatch",
        )
        require(
            item["full_work_units"] == item["selected_count"],
            "full work accounting mismatch",
        )
        require(
            item["sparse_work_units"] == item["update_count"],
            "sparse work accounting mismatch",
        )
        require(item["span_count"] <= item["dirty_cells"], "span coalescing bound violated")

    # Fresh execution of the inherited I2 locality benchmark.
    require(locality["surface_phase_cells"] == 419_904, "I2 phase surface mismatch")
    require(locality["vector_shortlist"]["work_reduction_x1000"] == 81_000, "I2 shortlist reduction")
    require(locality["vector_shortlist"]["exact_result_equal"] is True, "I2 shortlist inequality")
    require(locality["cache_exact_lookup"]["exact_result_equal"] is True, "I2 cache inequality")
    require(locality["materialization"]["capacity_reduction_x1000"] == 81_000, "I2 materialization reduction")
    require(locality["materialization"]["exact_selected_equal"] is True, "I2 materialization inequality")
    require(locality["authoritative_state_changed"] is False, "I2 authority changed")

    # Fresh actual Pass 208 CPU_REFERENCE execution through inherited Pass 205/207 paths.
    require(pass208["backend"] == "CPU_REFERENCE", "Pass208 control is not CPU_REFERENCE")
    require(pass208["physical_gpu"] is False, "CPU control unexpectedly claims physical GPU")
    require(pass208["baseline_branch_count"] == 162, "Pass208 baseline branch count mismatch")
    require(pass208["phase_selected_branch_count"] == 2, "Pass208 phase branch count mismatch")
    require(pass208["baseline_logical_lane_dispatches"] == 839_808, "Pass208 baseline lanes mismatch")
    require(pass208["phase_logical_lane_dispatches"] == 10_368, "Pass208 selected lanes mismatch")
    require(pass208["work_reduction_x1000"] == 81_000, "Pass208 deterministic work reduction mismatch")
    require(pass208["child_state_projection_equal"] is True, "Pass208 child-state inequality")
    require(pass208["authoritative_state_changed"] is False, "Pass208 benchmark changed authority")

    representative = next(
        item
        for item in sparse_cases
        if item["p"] == 1 and item["q"] == 3 and item["dirty_cells"] == 7
    )

    # Determine the admissible Pareto set by portable work only. Wall timing is
    # intentionally excluded from canonical selection.
    by_ratio: dict[str, dict[str, int]] = {}
    for item in sparse_cases:
        key = ratio_key(item["p"], item["q"])
        if item["dirty_cells"] != 7:
            continue
        by_ratio[key] = {
            "selected_count": item["selected_count"],
            "sparse_update_count": item["update_count"],
            "sparse_work_reduction_x1000": item["work_reduction_x1000"],
        }

    # At equal exact-authoritative semantics and equal complete dirty witness,
    # lower projection/update counts dominate only presentation/derived work.
    # They cannot choose a universal projection density because workload quality
    # requirements are external to this benchmark.
    smallest_ratio = min(
        by_ratio.items(),
        key=lambda kv: (kv[1]["selected_count"], kv[0]),
    )[0]

    result = {
        "schema": "HHS_PASS219B_CANONICAL_SCALING_COMPOSITION_DECISION_V1",
        "classification": "PASS_COMPOSITION_ORDER_PROVEN_PARAMETERS_REMAIN_WORKLOAD_BOUND",
        "semantic_equality": "PASS",
        "canonical_authority_changed": False,
        "decision": {
            "composition_order": CANONICAL_ORDER,
            "why": [
                "exact phase locality removes impossible phase work before Pass208 candidate expansion",
                "Pass207 batching/cache remains deterministic acceleration over candidate work",
                "Pass208 remains candidate-only and is checked against the exact CPU/VM oracle",
                "singleton VM81 remains the only canonical transition/admission step",
                "I7 reduces projection of an already-authoritative state without changing that state",
                "I8 reduces derived updates only when the dirty witness is complete",
                "every optimization falls back to the inherited complete path when its proof precondition is absent",
            ],
            "fixed_global_parameter_selected": False,
            "parameter_policy": "EXACT_WORKLOAD_BOUND_SELECTORS_WITH_FAIL_CLOSED_COMPLETE_PATH",
            "reason_no_fixed_parameter": (
                "The benchmark proves ordering and exact work reductions, but it does not prove "
                "one universal projection ratio, dirty density, phase depth, or device timing threshold."
            ),
        },
        "portable_deterministic_evidence": {
            "phase_locality_work_reduction_x1000": pass208["work_reduction_x1000"],
            "phase_locality_baseline_lanes": pass208["baseline_logical_lane_dispatches"],
            "phase_locality_selected_lanes": pass208["phase_logical_lane_dispatches"],
            "vector_shortlist_work_reduction_x1000": locality["vector_shortlist"][
                "work_reduction_x1000"
            ],
            "materialization_capacity_reduction_x1000": locality["materialization"][
                "capacity_reduction_x1000"
            ],
            "phase_recursive_max_current_depth": composition["phase_max_depth"],
            "phase_recursive_reduction_at_max_depth": depths[-1]["reduction_numerator"],
            "representative_one_third_dirty7": {
                "authoritative_source_entities": composition["source_count"],
                "selected_projection_entities": representative["selected_count"],
                "dirty_update_entities": representative["update_count"],
                "projection_avoided_entities": composition["source_count"]
                - representative["selected_count"],
                "sparse_avoided_selected_entities": representative["avoided_count"],
                "sparse_work_reduction_x1000": representative["work_reduction_x1000"],
                "exact_equal": representative["exact_equal"],
            },
            "ratio_sweep_dirty7": by_ratio,
            "lowest_derived_work_ratio_in_tested_set": smallest_ratio,
        },
        "observational_timing": {
            "canonical_selection_uses_wall_timing": False,
            "fresh_i2_vector_wall_speedup_x1000": locality["vector_shortlist"][
                "wall_speedup_x1000"
            ],
            "fresh_i2_cache_wall_speedup_x1000": locality["cache_exact_lookup"][
                "wall_speedup_x1000"
            ],
            "fresh_i2_materialization_wall_speedup_x1000": locality["materialization"][
                "wall_speedup_x1000"
            ],
            "fresh_pass208_cpu_wall_speedup_x1000": pass208["wall_speedup_x1000"],
            "representative_sparse_wall_speedup_x1000": representative[
                "wall_speedup_x1000"
            ],
            "physical_gpu_measured_in_this_run": False,
        },
        "fail_closed_proofs": {
            "missing_exact_phase_selector_routes_dense": True,
            "incomplete_dirty_witness_rejected": True,
            "canonical_authority_request_rejected": True,
            "all_sparse_full_equal": True,
            "pass208_cpu_reference_equal": True,
        },
    }

    Path(sys.argv[4]).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
