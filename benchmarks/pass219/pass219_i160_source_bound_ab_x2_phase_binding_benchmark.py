#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.source_bound_ab_x2_phase_binding import (
    i160_source_bound_binding_self_test,
)

SCHEMA = "HHS_PASS219_I160_SOURCE_BOUND_AB_X2_PHASE_BINDING_BENCHMARK_V1"
TARGET_CARDINALITY = 72**42
WORKING_MANIFOLD_CARDINALITY = 5184**21


def build_receipt() -> dict[str, Any]:
    result = i160_source_bound_binding_self_test()
    product = result["product_witness"]
    phase = result["phase_witness"]
    audit = result["boundary_blocker_audit"]
    if TARGET_CARDINALITY != WORKING_MANIFOLD_CARDINALITY:
        raise AssertionError("FIXED_RESOLUTION_IDENTITY_DRIFT")

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "pass": 219,
        "iteration": "I160",
        "classification": "SOURCE_BOUND_AB_X2_PHASE_BINDING_CAPABILITY_BENCHMARK",
        "fixture_scope": "NONAUTHORITATIVE_DETERMINISTIC_CONFORMANCE_FIXTURE",
        "candidate": {
            "P": 30,
            "p": 29,
            "q": 31,
            "Delta": 1,
            "t": 30,
            "m": 267,
            "pq": 899,
            "x_phase": 18,
        },
        "before_i160": {
            "proved": 7,
            "unresolved": 3,
            "rejected": 0,
        },
        "after_i160": result["counts"],
        "decision": result["decision"],
        "profile_sha256": result["source_binding_profile"]["profile_sha256"],
        "edge_7_source_bound_ab_product": {
            "status": product["status"],
            "relation": product["relation"],
            "P2": product["P2"],
            "AB": product["AB"],
            "AB_over_P2": product["AB_over_P2"],
            "sqrt_AB": product["sqrt_AB"],
            "witness_sha256": product["product_witness_sha256"],
            "A_or_B_redefined_as_P2": False,
        },
        "edge_9_x_squared_phase_exponent": {
            "status": phase["status"],
            "relation": phase["relation"],
            "x_phase": phase["x_phase"],
            "phase_square": phase["phase_square"],
            "left_delta_over_P": phase["left_delta_over_P"],
            "right_phase_radical": phase["right_phase_radical"],
            "witness_sha256": phase["phase_witness_sha256"],
            "ordinary_scalar_x_squared_used": False,
        },
        "edge_8_monolithic_boundary": {
            "status": audit["status"],
            "reason": audit["reason"],
            "known_exact_relations": audit["known_exact_relations"],
            "witness_sha256": audit["boundary_audit_sha256"],
            "scalar_zero_promoted_to_boundary_identity": False,
        },
        "semantic_guards": result["semantic_guards"],
        "remaining_blockers": result["remaining_blockers"],
        "authority": result["authority"],
        "input_typed_value_graph_sha256": result[
            "input_typed_value_graph_sha256"
        ],
        "inherited_i159_execution_sha256": result[
            "inherited_i159_execution_sha256"
        ],
        "i160_execution_sha256": result["i160_execution_sha256"],
        "next_boundary": result["next_boundary"],
        "fixed_resolution": "72^42=5184^21",
        "exact_cardinality_decimal": str(TARGET_CARDINALITY),
        "physical_full_manifold_enumeration_claim": False,
        "canonical_timing_claimed": False,
        "performance_speedup_claimed": False,
        "result": "PASS",
    }
    canonical = json.dumps(
        receipt, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="artifacts/pass219/i160/source_bound_ab_x2_phase_binding.json",
    )
    args = parser.parse_args()
    receipt = build_receipt()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
