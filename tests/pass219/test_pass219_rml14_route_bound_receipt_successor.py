from __future__ import annotations

from pathlib import Path

import pytest

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.native_route_witness_binding import build_route_witness
from hhs_runtime.pass219.reciprocal_route_optimizer import build_and_select_reciprocal_route
from hhs_runtime.pass219.route_bound_receipt_successor import (
    RML14_RECORD_SCHEMA,
    RouteBoundReceiptSuccessorError,
    bind_selected_route_receipt_successor,
    invoke_native_route_bound_receipt,
)

ROOT = Path(__file__).resolve().parents[2]


def _state(*, state_id: str, x: int) -> dict[str, object]:
    primitives = {"x": x, "y": 19, "z": 31, "w": 43}
    signs = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
    phases = {
        "x": primitives["x"],
        "y": primitives["y"],
        "z": primitives["z"],
        "w": primitives["w"],
        "xy": expected_product_phase(primitives["x"], signs["xy"]),
        "yx": expected_product_phase(primitives["y"], signs["yx"]),
        "zw": expected_product_phase(primitives["z"], signs["zw"]),
        "wz": expected_product_phase(primitives["w"], signs["wz"]),
    }
    return build_gyroscope_state(phases, signs, state_id=state_id)


@pytest.fixture(scope="module")
def route_bundles() -> tuple[dict[str, object], dict[str, object]]:
    source = _state(state_id="rml14:source", x=7)
    target_a = _state(state_id="rml14:target:a", x=8)
    target_b = _state(state_id="rml14:target:b", x=9)
    first = build_and_select_reciprocal_route(source, target_a, route_id="rml14:a")
    second = build_and_select_reciprocal_route(source, target_b, route_id="rml14:b")
    return first, second


def test_rml14_route_bound_receipt_successor_is_native_and_authority_bounded(route_bundles) -> None:
    record = bind_selected_route_receipt_successor(route_bundles[0], repository_root=ROOT)
    assert record["schema"] == RML14_RECORD_SCHEMA
    assert record["decision"] == 1
    assert record["rml13_binding_verified"] is True
    assert record["receipt_material_exact"] is True
    assert record["receipt_material_contains_route_witness_root"] is True
    assert record["receipt_material_contains_route_bound_change_hash72"] is True
    assert record["successor_receipt_hash72_route_bound"] is True
    assert record["successor_hash216_triplet_route_bound"] is True
    assert record["successor_hash216_identity_route_bound"] is True
    assert record["canonical_hash72_delegate_used"] is True
    assert record["canonical_hash216_delegate_used"] is True
    assert record["canonical_hash216_parity_with_frozen_uqcel_verified"] is True
    assert record["independent_hash_implementation_used"] is False
    assert record["second_vm81_commit_primitive_added"] is False
    assert record["single_vm81_commit_authority_preserved"] is True
    assert record["optimizer_transition_authority"] is False
    assert record["floating_point_authority"] is False
    assert record["hash216_persistence_authority"] is False
    assert record["scalar_projection_substitution_authority"] is False


def test_successor_hash216_triplet_is_exact_previous_change_route_bound_receipt(route_bundles) -> None:
    record = bind_selected_route_receipt_successor(route_bundles[0], repository_root=ROOT)
    assert len(record["previous_hash72"]) == 72
    assert len(record["change_hash72"]) == 72
    assert len(record["frozen_uqcel_receipt_hash72"]) == 72
    assert len(record["successor_receipt_hash72"]) == 72
    assert len(record["frozen_rml13_transition_hash216"]) == 216
    assert len(record["successor_hash216_triplet"]) == 216
    assert len(record["successor_transition_hash216"]) == 216
    assert record["successor_hash216_triplet"] == (
        record["previous_hash72"]
        + record["change_hash72"]
        + record["successor_receipt_hash72"]
    )
    assert record["historical_uqcel_v1_receipt_rewritten"] is False
    assert record["historical_rml13_transition_rewritten"] is False


def test_different_valid_routes_bind_both_successor_receipt_and_successor_hash216(route_bundles) -> None:
    first = bind_selected_route_receipt_successor(route_bundles[0], repository_root=ROOT)
    second = bind_selected_route_receipt_successor(route_bundles[1], repository_root=ROOT)

    assert first["selected_route_sha256"] != second["selected_route_sha256"]
    assert first["witness_root_sha256"] != second["witness_root_sha256"]
    assert first["candidate_frame_sha256"] != second["candidate_frame_sha256"]
    assert first["change_hash72"] != second["change_hash72"]
    assert first["receipt_material_sha256"] != second["receipt_material_sha256"]
    assert first["successor_receipt_hash72"] != second["successor_receipt_hash72"]
    assert first["successor_hash216_triplet"] != second["successor_hash216_triplet"]
    assert first["successor_transition_hash216"] != second["successor_transition_hash216"]

    # Frozen historical receipt material remains unchanged by route choice.
    assert first["frozen_uqcel_receipt_hash72"] == second["frozen_uqcel_receipt_hash72"]
    assert first["frozen_uqcel_receipt_preserved"] is True
    assert second["frozen_uqcel_receipt_preserved"] is True


def test_rml14_repeated_invocation_is_deterministic(route_bundles) -> None:
    first = bind_selected_route_receipt_successor(route_bundles[0], repository_root=ROOT)
    second = bind_selected_route_receipt_successor(route_bundles[0], repository_root=ROOT)
    for key in (
        "receipt_material_sha256",
        "witness_root_sha256",
        "route_environment_root_sha256",
        "candidate_frame_sha256",
        "previous_hash72",
        "change_hash72",
        "frozen_uqcel_receipt_hash72",
        "successor_receipt_hash72",
        "frozen_rml13_transition_hash216",
        "successor_hash216_triplet",
        "successor_transition_hash216",
    ):
        assert first[key] == second[key]


def test_rml14_rejects_invalid_parent_route_witness(route_bundles) -> None:
    witness, _ = build_route_witness(route_bundles[0])
    witness.hopf_base_moving_edges += 1
    with pytest.raises(RouteBoundReceiptSuccessorError, match="RML14_NATIVE_BINDING_STATUS"):
        invoke_native_route_bound_receipt(witness, repository_root=ROOT)
