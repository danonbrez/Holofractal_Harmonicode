#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from hhs_runtime.pass219.fixed_cardinality_optimization import (
    local_reduction_meets_exhaustion_ratio,
)
from hhs_runtime.pass219.local_global_equation_search_filter import (
    HASH216_FORMAT_GENOME_ROOT,
    filter_search_space,
    make_candidate,
    make_snapshot,
)

CANDIDATE_COUNT = 4096
SYNTHETIC_GATE_COUNT = 5
EXPECTED_SURVIVORS = CANDIDATE_COUNT // (1 << SYNTHETIC_GATE_COUNT)


def _synthetic_gate_results(route_index: int, P: int) -> list[bool]:
    mixed = route_index ^ P
    return [((mixed >> bit) & 1) == 0 for bit in range(SYNTHETIC_GATE_COUNT)]


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "artifacts/pass219/i153/local_global_equation_search_filter_benchmark.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    P = 157
    snapshot = make_snapshot(
        snapshot_hash216=hashlib.sha256(b"PASS219-I153-BENCHMARK-SNAPSHOT").hexdigest(),
        snapshot_hash216_format=HASH216_FORMAT_GENOME_ROOT,
        P=P,
    )
    global_root = hashlib.sha256(b"PASS219-I153-BENCHMARK-GLOBAL-ENVIRONMENT").hexdigest()

    candidates = [
        make_candidate(
            snapshot=snapshot,
            target_block_index=0,
            route_index=route,
            global_symbol_environment_root=global_root,
            gate_results=_synthetic_gate_results(route, P),
        )
        for route in range(CANDIDATE_COUNT)
    ]
    filtered = filter_search_space(snapshot, candidates)

    assert filtered["candidate_count"] == CANDIDATE_COUNT
    assert filtered["survivor_count"] == EXPECTED_SURVIVORS
    assert filtered["rejected_count"] == CANDIDATE_COUNT - EXPECTED_SURVIVORS
    assert filtered["candidate_reduction_fraction"] == {
        "numerator": CANDIDATE_COUNT,
        "denominator": EXPECTED_SURVIVORS,
    }
    assert filtered["candidate_reduction_x1000_floor"] == 32000

    expected_residue = P & 31
    survivor_routes = [
        int(row["route_index"])
        for row in filtered["decisions"]
        if row["survives_equation_filter"]
    ]
    assert len(survivor_routes) == EXPECTED_SURVIVORS
    assert all(route % 32 == expected_residue for route in survivor_routes)

    meets_ratio = local_reduction_meets_exhaustion_ratio(
        CANDIDATE_COUNT,
        EXPECTED_SURVIVORS,
    )
    assert meets_ratio is True

    receipt = {
        "schema": "HHS_PASS219_I153_LOCAL_GLOBAL_EQUATION_SEARCH_FILTER_BENCHMARK_V1",
        "pass": 219,
        "iteration": "I153",
        "metric_class": "EXACT_BOUNDED_SYNTHETIC_CANDIDATE_COUNT",
        "synthetic_truth_authority": False,
        "snapshot_P": P,
        "snapshot_binding_sha256": snapshot["snapshot_binding_sha256"],
        "global_symbol_environment_root": global_root,
        "candidate_count": CANDIDATE_COUNT,
        "survivor_count": EXPECTED_SURVIVORS,
        "rejected_count": CANDIDATE_COUNT - EXPECTED_SURVIVORS,
        "synthetic_gate_count": SYNTHETIC_GATE_COUNT,
        "synthetic_survivor_residue_mod32": expected_residue,
        "candidate_reduction_fraction": {
            "numerator": CANDIDATE_COUNT,
            "denominator": EXPECTED_SURVIVORS,
        },
        "candidate_reduction_x1000_floor": 32000,
        "candidate_evaluations_avoided_before_downstream_optimizer": (
            CANDIDATE_COUNT - EXPECTED_SURVIVORS
        ),
        "bounded_synthetic_ratio_meets_81_over_7": meets_ratio,
        "rejection_reason_counts": filtered["rejection_reason_counts"],
        "equation_source": filtered["equation_source"],
        "fixed_search_space": filtered["fixed_search_space"],
        "proof_preserving_schedule_sha256": filtered[
            "proof_preserving_schedule_sha256"
        ],
        "filter_receipt_sha256": filtered["receipt_sha256"],
        "full_four_lane_exhaustion_claim": False,
        "physical_full_manifold_enumeration_claim": False,
        "canonical_vm81_mutation": False,
        "canonical_hash72_mint": False,
        "canonical_hash216_persistence": False,
        "timing_is_canonical": False,
        "result": "PASS",
    }
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
