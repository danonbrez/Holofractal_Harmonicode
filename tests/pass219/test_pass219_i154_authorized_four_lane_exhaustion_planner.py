from __future__ import annotations

import pytest

from hhs_runtime.pass219.authorized_four_lane_exhaustion_planner import (
    AUTHORITY_SCHEMA,
    LANES,
    PRODUCTION_AUTHORITY_ORIGIN,
    TEST_FIXTURE_AUTHORITY_ORIGIN,
    WORKLOAD_SCHEMA,
    AuthorizedPlannerError,
    normalize_authority_packet,
    plan_authorized_four_lane_exhaustion,
)
from hhs_runtime.pass219.fixed_cardinality_optimization import (
    ROUTE_MULTIPLICITY_PER_TARGET,
)
from hhs_runtime.pass219.local_global_equation_search_filter import (
    HASH216_FORMAT_GENOME_ROOT,
    make_snapshot,
)


def _authority(snapshot: dict[str, object], *, propagate: bool = True) -> dict[str, object]:
    gates = [True, True, True, True, True] if propagate else [True, False, True, True, True]
    return {
        "schema": AUTHORITY_SCHEMA,
        "authority_origin": TEST_FIXTURE_AUTHORITY_ORIGIN,
        "runtime_provider_available": True,
        "pass169_authority_verified": True,
        "boolean_gate_results_available": True,
        "membrane_input_ready": True,
        "canonical_monolithic_proof": True,
        "local_snapshot_binding_verified": True,
        "decision": "PROPAGATE" if propagate else "REJECT",
        "P": snapshot["P"],
        "local_snapshot_binding_sha256": snapshot["snapshot_binding_sha256"],
        "canonical_global_symbol_environment_root": "b" * 64,
        "gate_results": gates,
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


def _workload(
    lane: str,
    *,
    index: int,
    propagate: bool = True,
    baseline: int = 1024,
    downstream: int = 32,
) -> dict[str, object]:
    snapshot = make_snapshot(
        snapshot_hash216=f"{index + 1:064x}",
        snapshot_hash216_format=HASH216_FORMAT_GENOME_ROOT,
        P=157 + index,
    )
    route = 100 + index
    return {
        "schema": WORKLOAD_SCHEMA,
        "workload_id": f"fixture-{index}-{lane}",
        "lane": lane,
        "snapshot": snapshot,
        "authority_packet": _authority(snapshot, propagate=propagate),
        "target_block_index": index,
        "route_index": route,
        "working_index": index * ROUTE_MULTIPLICITY_PER_TARGET + route,
        "baseline_work_units": baseline,
        "downstream_work_units_if_survives": downstream,
    }


def test_test_fixture_authority_is_rejected_by_default() -> None:
    snapshot = make_snapshot(
        snapshot_hash216="1" * 64,
        snapshot_hash216_format=HASH216_FORMAT_GENOME_ROOT,
        P=157,
    )
    with pytest.raises(AuthorizedPlannerError, match="TEST_FIXTURE_AUTHORITY_FORBIDDEN"):
        normalize_authority_packet(_authority(snapshot))


def test_test_only_four_lane_plumbing_requires_explicit_override() -> None:
    workloads = [
        _workload(lane, index=index)
        for index, lane in enumerate(LANES)
    ]
    result = plan_authorized_four_lane_exhaustion(
        workloads,
        allow_test_authority=True,
    )
    assert result["lanes"] == list(LANES)
    assert result["baseline_work_units"] == 4096
    assert result["effective_downstream_work_units"] == 128
    assert result["work_units_avoided"] == 3968
    assert result["within_81_over_7_representative_work_budget"] is True
    assert result["classification"] == "TEST_ONLY_FOUR_LANE_PLUMBING_WITHIN_81_OVER_7"
    assert result["canonical_evidence_eligible"] is False
    assert result["test_authority_override_used"] is True
    assert result["physical_full_target_exhaustion_claim"] is False
    assert result["physical_full_working_manifold_enumeration_claim"] is False
    assert result["global_exhaustion_bound_proven_from_sample"] is False


def test_authoritative_rejection_avoids_downstream_work_in_test_plumbing() -> None:
    workloads = [
        _workload(lane, index=index, propagate=(index != 2))
        for index, lane in enumerate(LANES)
    ]
    result = plan_authorized_four_lane_exhaustion(
        workloads,
        allow_test_authority=True,
    )
    assert result["baseline_work_units"] == 4096
    assert result["effective_downstream_work_units"] == 96
    rejected = [row for row in result["workloads"] if row["provider_decision"] == "REJECT"]
    assert len(rejected) == 1
    assert rejected[0]["i153_survives"] is False
    assert rejected[0]["effective_downstream_work_units"] == 0
    assert rejected[0]["work_avoided"] == 1024


def test_all_four_lanes_are_mandatory() -> None:
    workloads = [
        _workload(lane, index=index)
        for index, lane in enumerate(LANES[:-1])
    ]
    with pytest.raises(AuthorizedPlannerError, match="EXACTLY_FOUR_REPRESENTATIVE_WORKLOADS_REQUIRED"):
        plan_authorized_four_lane_exhaustion(
            workloads,
            allow_test_authority=True,
        )


def test_snapshot_binding_and_P_are_not_transferable() -> None:
    workload = _workload(LANES[0], index=0)
    workload["authority_packet"]["P"] = 999
    workloads = [workload] + [
        _workload(lane, index=index)
        for index, lane in enumerate(LANES[1:], start=1)
    ]
    with pytest.raises(AuthorizedPlannerError, match="AUTHORITY_P_SNAPSHOT_DRIFT"):
        plan_authorized_four_lane_exhaustion(
            workloads,
            allow_test_authority=True,
        )


def test_propagate_requires_all_five_true_gates() -> None:
    snapshot = make_snapshot(
        snapshot_hash216="2" * 64,
        snapshot_hash216_format=HASH216_FORMAT_GENOME_ROOT,
        P=158,
    )
    packet = _authority(snapshot, propagate=True)
    packet["gate_results"][3] = False
    with pytest.raises(AuthorizedPlannerError, match="PROPAGATE_REQUIRES_ALL_GATES_TRUE"):
        normalize_authority_packet(packet, allow_test_authority=True)


def test_real_origin_does_not_bypass_required_authority_fields() -> None:
    snapshot = make_snapshot(
        snapshot_hash216="3" * 64,
        snapshot_hash216_format=HASH216_FORMAT_GENOME_ROOT,
        P=159,
    )
    packet = _authority(snapshot)
    packet["authority_origin"] = PRODUCTION_AUTHORITY_ORIGIN
    packet["local_snapshot_binding_verified"] = False
    with pytest.raises(AuthorizedPlannerError, match="AUTHORITY_PACKET_INCOMPLETE"):
        normalize_authority_packet(packet)


def test_duplicate_working_routes_fail_closed() -> None:
    workloads = [
        _workload(lane, index=index)
        for index, lane in enumerate(LANES)
    ]
    workloads[1]["target_block_index"] = workloads[0]["target_block_index"]
    workloads[1]["route_index"] = workloads[0]["route_index"]
    workloads[1]["working_index"] = workloads[0]["working_index"]
    with pytest.raises(AuthorizedPlannerError, match="DUPLICATE_WORKING_INDEX"):
        plan_authorized_four_lane_exhaustion(
            workloads,
            allow_test_authority=True,
        )
