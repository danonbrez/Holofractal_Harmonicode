#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

from hhs_runtime.pass219.fixed_cardinality_optimization import (
    MAX_EFFECTIVE_EXHAUSTION_WORK,
    ROUTE_MULTIPLICITY_PER_TARGET,
    TARGET_CARDINALITY,
    WORKING_MANIFOLD_CARDINALITY,
    decode_working_route,
    encode_working_route,
    evaluate_exhaustion_work,
    local_reduction_meets_exhaustion_ratio,
    validate_fixed_cardinalities,
)

I151_RAW_BASELINE = 11_466_081
I151_RAW_SELECTED = 5_645_376
I151_CROSS_BASELINE = 1_384_512
I151_CROSS_SELECTED = 32_228


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "artifacts/pass219/i152/fixed_manifold_exhaustion_benchmark.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    cardinalities = validate_fixed_cardinalities()

    route_cases = []
    samples = (
        (0, 0),
        (0, ROUTE_MULTIPLICITY_PER_TARGET - 1),
        (TARGET_CARDINALITY // 2, ROUTE_MULTIPLICITY_PER_TARGET // 2),
        (TARGET_CARDINALITY - 1, 0),
        (TARGET_CARDINALITY - 1, ROUTE_MULTIPLICITY_PER_TARGET - 1),
    )
    for block, route in samples:
        working = encode_working_route(block, route)
        decoded_block, decoded_route = decode_working_route(working)
        assert decoded_block == block
        assert decoded_route == route
        route_cases.append(
            {
                "target_block_index": str(block),
                "route_index": str(route),
                "working_index": str(working),
                "roundtrip_equal": True,
            }
        )

    assert encode_working_route(
        TARGET_CARDINALITY - 1,
        ROUTE_MULTIPLICITY_PER_TARGET - 1,
    ) == WORKING_MANIFOLD_CARDINALITY - 1

    boundary = evaluate_exhaustion_work(MAX_EFFECTIVE_EXHAUSTION_WORK)
    over = evaluate_exhaustion_work(MAX_EFFECTIVE_EXHAUSTION_WORK + 1)
    zero = evaluate_exhaustion_work(0)
    assert boundary["within_81_over_7_exhaustion_budget"] is True
    assert over["within_81_over_7_exhaustion_budget"] is False
    assert zero["within_81_over_7_exhaustion_budget"] is True

    raw_local = local_reduction_meets_exhaustion_ratio(
        I151_RAW_BASELINE, I151_RAW_SELECTED
    )
    cross_local = local_reduction_meets_exhaustion_ratio(
        I151_CROSS_BASELINE, I151_CROSS_SELECTED
    )
    assert raw_local is False
    assert cross_local is True

    receipt = {
        "schema": "HHS_PASS219_I152_FIXED_MANIFOLD_EXHAUSTION_BENCHMARK_V1",
        "pass": 219,
        "iteration": "I152",
        "metric_class": "EXACT_INTEGER_CARDINALITY_AND_LOGICAL_WORK_GATE",
        "fixed_cardinalities": cardinalities,
        "factorization": {
            "working_equals_target_times_route_multiplicity": (
                WORKING_MANIFOLD_CARDINALITY
                == TARGET_CARDINALITY * ROUTE_MULTIPLICITY_PER_TARGET
            ),
            "route_roundtrip_cases": route_cases,
            "last_working_index_exact": str(WORKING_MANIFOLD_CARDINALITY - 1),
        },
        "exhaustion_gate": {
            "boundary": boundary,
            "one_unit_over": over,
            "zero_work": zero,
        },
        "inherited_local_observations": {
            "raw5184_audio": {
                "baseline_work_units": I151_RAW_BASELINE,
                "selected_work_units": I151_RAW_SELECTED,
                "reduction_x1000_floor": (
                    I151_RAW_BASELINE * 1000 // I151_RAW_SELECTED
                ),
                "locally_meets_81_over_7": raw_local,
            },
            "cross_modal_reversible_state": {
                "baseline_work_units": I151_CROSS_BASELINE,
                "selected_work_units": I151_CROSS_SELECTED,
                "reduction_x1000_floor": (
                    I151_CROSS_BASELINE * 1000 // I151_CROSS_SELECTED
                ),
                "locally_meets_81_over_7": cross_local,
            },
        },
        "full_four_lane_exhaustion": {
            "status": "VALIDATION_REQUIRED",
            "physical_enumeration_executed": False,
            "reason": (
                "Fixed cardinalities and exact budget are proven; inherited local "
                "benchmarks do not constitute an integrated four-lane full-space run."
            ),
        },
        "authority": {
            "canonical_vm81_mutation": False,
            "canonical_hash72_mint": False,
            "canonical_hash216_persistence": False,
        },
        "result": "PASS",
    }
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
