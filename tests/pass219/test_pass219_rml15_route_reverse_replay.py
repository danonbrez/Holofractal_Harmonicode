from __future__ import annotations

import ctypes
from pathlib import Path

import pytest

from hhs_runtime.pass169.runtime_binding import CANONICAL_SOURCE_PATH
from hhs_runtime.pass219.dynamic_octonion_gyroscope import build_gyroscope_state, expected_product_phase
from hhs_runtime.pass219.native_route_witness_binding import build_route_witness
from hhs_runtime.pass219.reciprocal_route_optimizer import build_and_select_reciprocal_route
from hhs_runtime.pass219.route_bound_receipt_successor import bind_selected_route_receipt_successor
from hhs_runtime.pass219.route_reverse_replay import (
    HHSExactPass219RML15BindingV1,
    HHSExactPass219RML15ReverseWitnessV1,
    RML15_RECORD_SCHEMA,
    RouteReverseReplayError,
    bind_route_reverse_replay,
    build_reverse_witness,
)

ROOT = Path(__file__).resolve().parents[2]


def _state(*, state_id: str, primitives: tuple[int, int, int, int], signs: tuple[int, int, int, int]) -> dict[str, object]:
    x, y, z, w = primitives
    sx, sy, sz, sw = signs
    phases = {
        "x": x,
        "y": y,
        "z": z,
        "w": w,
        "xy": expected_product_phase(x, sx),
        "yx": expected_product_phase(y, sy),
        "zw": expected_product_phase(z, sz),
        "wz": expected_product_phase(w, sw),
    }
    return build_gyroscope_state(
        phases,
        {"xy": sx, "yx": sy, "zw": sz, "wz": sw},
        state_id=state_id,
    )


@pytest.fixture(scope="module")
def route_case() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    source = _state(
        state_id="rml15:source",
        primitives=(7, 19, 31, 43),
        signs=(1, -1, 1, -1),
    )
    target = _state(
        state_id="rml15:target",
        primitives=(10, 19, 35, 43),
        signs=(-1, 1, -1, 1),
    )
    bundle = build_and_select_reciprocal_route(source, target, route_id="rml15:multi")
    return source, target, bundle


def test_reverse_witness_is_exact_inverse_of_retained_selected_route(route_case) -> None:
    source, target, bundle = route_case
    witness, summary = build_reverse_witness(bundle, source, target)
    assert witness.edge_count == 4
    assert summary["pair_flip_edges"] == 2
    assert summary["coupled_move_edges"] == 2
    assert summary["python_reverse_phase_state_restored"] is True
    assert summary["python_reverse_uses_retained_edge_ancestry"] is True
    assert summary["hash216_cryptographic_inversion_used"] is False
    assert [witness.edges[i].kind for i in range(witness.edge_count)] == [1, 1, 2, 2]
    assert [witness.edges[i].signed_steps for i in range(witness.edge_count)] == [-4, -3, 36, 36]
    assert witness.source_state.ambient_state_index == source["ambient_state_index"]
    assert witness.target_state.ambient_state_index == target["ambient_state_index"]


def test_native_rml15_closes_forward_replay_and_reverse_ancestry(route_case) -> None:
    source, target, bundle = route_case
    record = bind_route_reverse_replay(bundle, source, target, repository_root=ROOT)
    assert record["schema"] == RML15_RECORD_SCHEMA
    assert record["decision"] == 1
    assert record["rml14_forward_verified"] is True
    assert record["rml14_replay_verified"] is True
    assert record["forward_replay_identity_equal"] is True
    assert record["retained_ancestry_verified"] is True
    assert record["reverse_instruction_sequence_verified"] is True
    assert record["reverse_phase_state_restored"] is True
    assert record["reverse_ambient_index_restored"] is True
    assert record["reverse_product_geometry_preserved"] is True
    assert record["reverse_chirality_preserved"] is True
    assert record["restored_ambient_state_index"] == source["ambient_state_index"]
    assert record["reverse_receipt_is_ancestry_witness_not_hash_inverse"] is True
    assert record["hash216_cryptographic_inversion_used"] is False
    assert record["second_vm81_commit_primitive_added"] is False
    assert len(record["reverse_receipt_hash72"]) == 72
    assert len(record["reverse_witness_hash216"]) == 216


def test_rml15_preserves_both_predecessor_and_rml14_successor_chains(route_case) -> None:
    source, target, bundle = route_case
    rml14 = bind_selected_route_receipt_successor(bundle, repository_root=ROOT)
    rml15 = bind_route_reverse_replay(bundle, source, target, repository_root=ROOT)
    assert rml15["historical_uqcel_receipt_preserved"] is True
    assert rml15["historical_rml13_transition_preserved"] is True
    assert rml15["rml14_successor_chain_preserved"] is True
    assert rml15["previous_hash72"] == rml14["previous_hash72"]
    assert rml15["route_bound_change_hash72"] == rml14["change_hash72"]
    assert rml15["frozen_uqcel_receipt_hash72"] == rml14["frozen_uqcel_receipt_hash72"]
    assert rml15["rml14_successor_receipt_hash72"] == rml14["successor_receipt_hash72"]
    assert rml15["frozen_rml13_transition_hash216"] == rml14["frozen_rml13_transition_hash216"]
    assert rml15["rml14_successor_transition_hash216"] == rml14["successor_transition_hash216"]


def test_native_rml15_replay_is_deterministic(route_case) -> None:
    source, target, bundle = route_case
    first = bind_route_reverse_replay(bundle, source, target, repository_root=ROOT)
    second = bind_route_reverse_replay(bundle, source, target, repository_root=ROOT)
    for key in (
        "reverse_instruction_root_sha256",
        "reverse_material_sha256",
        "reverse_receipt_hash72",
        "reverse_witness_hash216",
        "rml14_successor_transition_hash216",
    ):
        assert first[key] == second[key]


def test_different_route_endpoint_changes_reverse_witness_without_hash_inversion() -> None:
    source = _state(
        state_id="rml15:sensitivity:source",
        primitives=(7, 19, 31, 43),
        signs=(1, -1, 1, -1),
    )
    target_a = _state(
        state_id="rml15:sensitivity:a",
        primitives=(8, 19, 31, 43),
        signs=(1, -1, 1, -1),
    )
    target_b = _state(
        state_id="rml15:sensitivity:b",
        primitives=(9, 19, 31, 43),
        signs=(1, -1, 1, -1),
    )
    bundle_a = build_and_select_reciprocal_route(source, target_a, route_id="rml15:sensitivity:a")
    bundle_b = build_and_select_reciprocal_route(source, target_b, route_id="rml15:sensitivity:b")
    first = bind_route_reverse_replay(bundle_a, source, target_a, repository_root=ROOT)
    second = bind_route_reverse_replay(bundle_b, source, target_b, repository_root=ROOT)
    assert first["selected_route_sha256"] != second["selected_route_sha256"]
    assert first["rml14_successor_transition_hash216"] != second["rml14_successor_transition_hash216"]
    assert first["reverse_instruction_root_sha256"] != second["reverse_instruction_root_sha256"]
    assert first["reverse_receipt_hash72"] != second["reverse_receipt_hash72"]
    assert first["reverse_witness_hash216"] != second["reverse_witness_hash216"]
    assert first["hash216_cryptographic_inversion_used"] is False
    assert second["hash216_cryptographic_inversion_used"] is False


def test_python_rejects_endpoint_not_retained_by_selected_route(route_case) -> None:
    source, _, bundle = route_case
    wrong_target = _state(
        state_id="rml15:wrong-target",
        primitives=(11, 19, 35, 43),
        signs=(-1, 1, -1, 1),
    )
    with pytest.raises(RouteReverseReplayError, match="TARGET_STATE_HASH_MISMATCH"):
        build_reverse_witness(bundle, source, wrong_target)


def test_native_rejects_corrupted_reverse_instruction(route_case) -> None:
    source, target, bundle = route_case
    route_witness, _ = build_route_witness(bundle)
    reverse_witness, _ = build_reverse_witness(bundle, source, target)
    assert reverse_witness.edge_count > 0
    reverse_witness.edges[0].signed_steps += 1

    library = ROOT / "hhs_runtime" / "builds" / "libhhs_pass219_rml15.so"
    native = ctypes.CDLL(str(library))
    native.hhs_exact_pass219_rml15_verify_route_reverse_replay.argtypes = [
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(type(route_witness)),
        ctypes.POINTER(HHSExactPass219RML15ReverseWitnessV1),
        ctypes.POINTER(HHSExactPass219RML15BindingV1),
    ]
    native.hhs_exact_pass219_rml15_verify_route_reverse_replay.restype = ctypes.c_int
    raw_source = (ROOT / CANONICAL_SOURCE_PATH).read_bytes()
    raw = (ctypes.c_uint8 * len(raw_source)).from_buffer_copy(raw_source)
    binding = HHSExactPass219RML15BindingV1()
    status = native.hhs_exact_pass219_rml15_verify_route_reverse_replay(
        raw,
        len(raw_source),
        ctypes.byref(route_witness),
        ctypes.byref(reverse_witness),
        ctypes.byref(binding),
    )
    assert status != 0
    assert binding.decision == 2
    assert binding.reason == 4
