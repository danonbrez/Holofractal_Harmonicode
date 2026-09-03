#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

from hhs_runtime.pass219.authorized_four_lane_exhaustion_planner import (
    AUTHORITY_SCHEMA,
    LANES,
    TEST_FIXTURE_AUTHORITY_ORIGIN,
    WORKLOAD_SCHEMA,
    plan_authorized_four_lane_exhaustion,
)
from hhs_runtime.pass219.fixed_cardinality_optimization import (
    ROUTE_MULTIPLICITY_PER_TARGET,
    TARGET_CARDINALITY,
    WORKING_MANIFOLD_CARDINALITY,
)
from hhs_runtime.pass219.local_global_equation_search_filter import (
    HASH216_FORMAT_GENOME_ROOT,
    make_snapshot,
)


def _fixture_authority(snapshot: dict[str, object]) -> dict[str, object]:
    return {
        "schema": AUTHORITY_SCHEMA,
        "authority_origin": TEST_FIXTURE_AUTHORITY_ORIGIN,
        "runtime_provider_available": True,
        "pass169_authority_verified": True,
        "boolean_gate_results_available": True,
        "membrane_input_ready": True,
        "canonical_monolithic_proof": True,
        "local_snapshot_binding_verified": True,
        "decision": "PROPAGATE",
        "P": snapshot["P"],
        "local_snapshot_binding_sha256": snapshot["snapshot_binding_sha256"],
        "canonical_global_symbol_environment_root": "b" * 64,
        "gate_results": [True, True, True, True, True],
        "proof_hash216": "H" * 216,
        "transition_hash216": "T" * 216,
        "receipt_hash72": "R" * 72,
        "replay_hash72": "Y" * 72,
        "vm81_steps": 81,
        "replay_vm81_steps": 81,
        "i12111_binding_verified": True,
        "source_identity_exact": True,
        "pipeline_identity_exact": True,
        "deterministic_replay_verified": True,
        "floating_point_authority": False,
    }


def _fixture_workloads() -> list[dict[str, object]]:
    workloads: list[dict[str, object]] = []
    for index, lane in enumerate(LANES):
        snapshot = make_snapshot(
            snapshot_hash216=f"{index + 1:064x}",
            snapshot_hash216_format=HASH216_FORMAT_GENOME_ROOT,
            P=157 + index,
        )
        route = 100 + index
        workloads.append(
            {
                "schema": WORKLOAD_SCHEMA,
                "workload_id": f"i154-fixture-{index}-{lane}",
                "lane": lane,
                "snapshot": snapshot,
                "authority_packet": _fixture_authority(snapshot),
                "target_block_index": index,
                "route_index": route,
                "working_index": index * ROUTE_MULTIPLICITY_PER_TARGET + route,
                "baseline_work_units": 1024,
                "downstream_work_units_if_survives": 32,
            }
        )
    return workloads


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: pass219_i154_authorized_four_lane_exhaustion_benchmark.py "
            "<production-probe.json> <fixture-probe.json> <output.json>"
        )

    production = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    fixture = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    output = Path(sys.argv[3])
    output.parent.mkdir(parents=True, exist_ok=True)

    assert production["schema"] == "HHS_PASS219_I154_PASS169_PROVIDER_PROBE_V1"
    assert production["provider_origin"] == "REPOSITORY_PRODUCTION_PASS169_VM81_PROVIDER"
    assert production["runtime_provider_available"] is True
    assert production["classification"] == "BLOCKED_FULL_SYMBOLIC_RESIDUAL"
    assert production["binding_decision"] == "UNRESOLVED"
    assert production["binding_reason_mask"] == 512
    assert production["pass169_authority_verified"] is False
    assert production["boolean_gate_results_available"] is False
    assert production["membrane_input_ready"] is False
    assert production["canonical_monolithic_proof"] is False
    assert production["i154_planner_input_ready"] is False

    assert fixture["schema"] == "HHS_PASS219_I154_PASS169_PROVIDER_PROBE_V1"
    assert fixture["provider_origin"] == "TEST_FIXTURE_PASS169_VM81_PROVIDER"
    assert fixture["runtime_provider_available"] is True
    assert fixture["classification"] == "TEST_FIXTURE_PROVIDER_DIAGNOSTIC_ONLY"
    assert fixture["pass169_authority_verified"] is True
    assert fixture["canonical_monolithic_proof"] is True
    assert fixture["test_fixture_is_authority"] is False
    assert fixture["i154_planner_input_ready"] is False

    plumbing = plan_authorized_four_lane_exhaustion(
        _fixture_workloads(),
        allow_test_authority=True,
    )
    assert plumbing["baseline_work_units"] == 4096
    assert plumbing["effective_downstream_work_units"] == 128
    assert plumbing["work_units_avoided"] == 3968
    assert plumbing["within_81_over_7_representative_work_budget"] is True
    assert plumbing["canonical_evidence_eligible"] is False
    assert plumbing["test_authority_override_used"] is True

    receipt = {
        "schema": "HHS_PASS219_I154_AUTHORIZED_FOUR_LANE_EXHAUSTION_BENCHMARK_V1",
        "pass": 219,
        "iteration": "I154",
        "production_measurement": {
            "status": "BLOCKED_FULL_SYMBOLIC_RESIDUAL",
            "effective_exhaustion_work_measured": False,
            "authoritative_workload_count": 0,
            "runtime_provider_available": True,
            "pass169_authority_verified": False,
            "local_P_snapshot_binding_available": False,
            "gate_vector_environment_export_available": False,
            "planner_input_ready": False,
            "required_reduction_ratio": "81/7",
            "within_81_over_7_claim": None,
        },
        "test_only_plumbing": {
            "status": plumbing["classification"],
            "lanes": plumbing["lanes"],
            "baseline_work_units": plumbing["baseline_work_units"],
            "effective_downstream_work_units": plumbing[
                "effective_downstream_work_units"
            ],
            "work_units_avoided": plumbing["work_units_avoided"],
            "candidate_reduction_fraction": {"numerator": 4096, "denominator": 128},
            "candidate_reduction_x1000_floor": 32000,
            "within_81_over_7_representative_work_budget": plumbing[
                "within_81_over_7_representative_work_budget"
            ],
            "canonical_evidence_eligible": False,
            "test_fixture_authority": False,
            "receipt_sha256": plumbing["receipt_sha256"],
        },
        "unresolved_authority_requirements": [
            "FULL_SYMBOLIC_UQCEL_MONOLITHIC_EQUALITY_CHAIN",
            "I154_LOCAL_P_SNAPSHOT_BINDING_VERIFIED_BY_PROVIDER",
            "I154_CANONICAL_GATE_VECTOR_AND_GLOBAL_ENVIRONMENT_EXPORT",
        ],
        "fixed_search_space": {
            "target": "72^42=5184^21",
            "target_cardinality_decimal": str(TARGET_CARDINALITY),
            "working_manifold": "3*72^72",
            "working_manifold_cardinality_decimal": str(
                WORKING_MANIFOLD_CARDINALITY
            ),
            "route_multiplicity": "3*72^30",
            "route_multiplicity_decimal": str(ROUTE_MULTIPLICITY_PER_TARGET),
            "cardinality_changed": False,
        },
        "physical_full_target_exhaustion_claim": False,
        "physical_full_working_manifold_enumeration_claim": False,
        "global_exhaustion_bound_proven": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "timing_is_canonical": False,
        "result": "BLOCKED_REAL_AUTHORITY_INPUT",
    }

    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
