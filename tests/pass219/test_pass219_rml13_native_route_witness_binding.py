from __future__ import annotations

from pathlib import Path

import pytest

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.native_route_witness_binding import (
    NativeRouteWitnessBindingError,
    RML13_RECORD_SCHEMA,
    bind_selected_route_pre_hash,
    build_route_witness,
    invoke_native_route_witness,
)
from hhs_runtime.pass219.reciprocal_route_optimizer import build_and_select_reciprocal_route

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
    source = _state(state_id="rml13:source", x=7)
    target_a = _state(state_id="rml13:target:a", x=8)
    target_b = _state(state_id="rml13:target:b", x=9)
    first = build_and_select_reciprocal_route(source, target_a, route_id="rml13:a")
    second = build_and_select_reciprocal_route(source, target_b, route_id="rml13:b")
    return first, second


def test_rml12_selected_route_serializes_to_exact_fixed_native_packet(route_bundles) -> None:
    witness, summary = build_route_witness(route_bundles[0])
    assert witness.edge_count == 1
    assert witness.pair_flip_edges == 0
    assert witness.coupled_move_edges == 1
    assert witness.hopf_same_base_edges + witness.hopf_base_moving_edges == 1
    assert (
        witness.clifford_full_intertwiner_edges
        + witness.clifford_chirality_swap_edges
        + witness.clifford_even_sector_preserving_edges
        + witness.residual_u72_edges
        == 1
    )
    assert witness.product_geometry_admissible == 1
    assert witness.all_edges_reversible == 1
    assert witness.target_reached_exactly == 1
    assert witness.reverse_restores_source_exactly == 1
    assert witness.optimizer_transition_authority == 0
    assert witness.floating_point_authority == 0
    assert summary["edge_count"] == 1


def test_native_rml13_binds_route_root_before_change_hash72_and_hash216(route_bundles) -> None:
    record = bind_selected_route_pre_hash(route_bundles[0], repository_root=ROOT)
    assert record["schema"] == RML13_RECORD_SCHEMA
    assert record["decision"] == 1
    assert record["source_provenance_verified"] is True
    assert record["route_witness_verified"] is True
    assert record["witness_serialization_exact"] is True
    assert record["witness_root_embedded_pre_hash"] is True
    assert record["candidate_frame_committed"] is True
    assert record["deterministic_replay_verified"] is True
    assert record["route_change_hash72_bound_to_witness"] is True
    assert record["route_hash216_identity_bound_to_witness"] is True
    assert record["single_vm81_commit_authority_preserved"] is True
    assert record["optimizer_transition_authority"] is False
    assert record["floating_point_authority"] is False
    assert record["hash216_persistence_authority"] is False
    assert record["scalar_projection_substitution_authority"] is False
    assert record["historical_i162_i168_hashes_modified"] is False
    assert len(record["change_hash72"]) == 72
    assert len(record["receipt_hash72"]) == 72
    assert len(record["hash216_triplet"]) == 216
    assert len(record["transition_hash216"]) == 216


def test_native_rml13_replay_is_deterministic(route_bundles) -> None:
    first = bind_selected_route_pre_hash(route_bundles[0], repository_root=ROOT)
    second = bind_selected_route_pre_hash(route_bundles[0], repository_root=ROOT)
    for key in (
        "witness_root_sha256",
        "route_environment_root_sha256",
        "candidate_frame_sha256",
        "change_hash72",
        "receipt_hash72",
        "replay_hash72",
        "hash216_triplet",
        "transition_hash216",
    ):
        assert first[key] == second[key]
    assert first["receipt_hash72"] == first["replay_hash72"]


def test_different_valid_route_witness_changes_prehash_transition_but_not_frozen_receipt(route_bundles) -> None:
    first = bind_selected_route_pre_hash(route_bundles[0], repository_root=ROOT)
    second = bind_selected_route_pre_hash(route_bundles[1], repository_root=ROOT)
    assert first["selected_route_sha256"] != second["selected_route_sha256"]
    assert first["witness_root_sha256"] != second["witness_root_sha256"]
    assert first["route_environment_root_sha256"] != second["route_environment_root_sha256"]
    assert first["candidate_frame_sha256"] != second["candidate_frame_sha256"]
    assert first["change_hash72"] != second["change_hash72"]
    assert first["hash216_triplet"] != second["hash216_triplet"]
    assert first["transition_hash216"] != second["transition_hash216"]

    # Honest frozen-v1 boundary: UQCEL receipt material excludes candidate frame.
    assert first["inherited_uqcel_receipt_material_frozen"] is True
    assert first["inherited_receipt_hash72_directly_bound_to_route_witness"] is False
    assert first["receipt_hash72"] == second["receipt_hash72"]


def test_native_rml13_rejects_inconsistent_route_partition(route_bundles) -> None:
    witness, _ = build_route_witness(route_bundles[0])
    witness.edge_count += 1
    with pytest.raises(NativeRouteWitnessBindingError, match="RML13_NATIVE_BINDING_STATUS"):
        invoke_native_route_witness(witness, repository_root=ROOT)
