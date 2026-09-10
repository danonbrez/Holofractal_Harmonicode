"""Pass 219 RML15 deterministic route-aware reverse/replay closure.

RML15 preserves the RML13/UQCEL predecessor chain and the RML14 route-aware
successor chain, replays RML14 deterministically, and proves the selected RML12
route can be reversed from retained edge ancestry back to the exact predecessor
phase state. Hash216 is never treated as cryptographically invertible.
"""
from __future__ import annotations

import ctypes
from ctypes import (
    POINTER,
    Structure,
    c_char,
    c_int8,
    c_int32,
    c_size_t,
    c_uint8,
    c_uint32,
    c_uint64,
)
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.pass169.runtime_binding import (
    CANONICAL_SOURCE_BYTES,
    CANONICAL_SOURCE_PATH,
    CANONICAL_SOURCE_SHA256,
)
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    GYROSCOPE_SCHEMA,
    PRODUCTS,
    advance_gyroscope,
)
from hhs_runtime.pass219.gyroscope_admission_membrane import flip_chiral_pair_half_turn
from hhs_runtime.pass219.native_route_witness_binding import (
    HHSExactPass219RML13RouteWitnessV1,
    build_route_witness,
)
from hhs_runtime.pass219.reciprocal_route_optimizer import PLAN_SCHEMA

PASS = 219
ITERATION = "RML15_ROUTE_REVERSE_REPLAY"
RML15_VERSION = (1 << 16) | (28 << 8)
RML15_VERIFIED = 1
RML15_MAX_EDGES = 6
RML15_EDGE_COUPLED_MOVE = 1
RML15_EDGE_PAIR_FLIP = 2
RML15_RECORD_SCHEMA = "HHS_PASS219_RML15_ROUTE_REVERSE_REPLAY_RECORD_V1"
RML12_BUNDLE_SCHEMA = "HHS_PASS219_RML12_SELECTED_RECIPROCAL_ROUTE_BUNDLE_V1"
GENERATOR_INDEX = {"x": 0, "y": 1, "z": 2, "w": 3}


class RouteReverseReplayError(RuntimeError):
    pass


class HHSExactPass219RML15PhaseStateV1(Structure):
    _fields_ = [
        ("phases", c_uint8 * 8),
        ("quarter_turn_signs", c_int8 * 4),
        ("reserved0", c_uint8 * 4),
        ("ambient_state_index", c_uint64),
    ]


class HHSExactPass219RML15ReverseEdgeV1(Structure):
    _fields_ = [
        ("kind", c_uint32),
        ("selector", c_uint32),
        ("signed_steps", c_int32),
        ("reserved0", c_uint32),
    ]


class HHSExactPass219RML15ReverseWitnessV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("edge_count", c_uint32),
        ("retained_forward_ancestry_used", c_uint32),
        ("reverse_edges_are_exact_inverses", c_uint32),
        ("reverse_terminal_matches_retained_source", c_uint32),
        ("hash216_cryptographic_inversion_used", c_uint32),
        ("floating_point_authority", c_uint32),
        ("route_sha256", c_uint8 * 32),
        ("source_state_sha256", c_uint8 * 32),
        ("target_state_sha256", c_uint8 * 32),
        ("source_state", HHSExactPass219RML15PhaseStateV1),
        ("target_state", HHSExactPass219RML15PhaseStateV1),
        ("edges", HHSExactPass219RML15ReverseEdgeV1 * RML15_MAX_EDGES),
    ]


class HHSExactPass219RML15BindingV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("decision", c_uint32),
        ("reason", c_uint32),
        ("rml14_forward_verified", c_uint32),
        ("rml14_replay_verified", c_uint32),
        ("forward_replay_identity_equal", c_uint32),
        ("retained_ancestry_verified", c_uint32),
        ("reverse_instruction_sequence_verified", c_uint32),
        ("reverse_phase_state_restored", c_uint32),
        ("reverse_ambient_index_restored", c_uint32),
        ("reverse_product_geometry_preserved", c_uint32),
        ("reverse_chirality_preserved", c_uint32),
        ("reverse_receipt_is_ancestry_witness_not_hash_inverse", c_uint32),
        ("canonical_hash72_delegate_used", c_uint32),
        ("canonical_hash216_delegate_used", c_uint32),
        ("historical_uqcel_receipt_preserved", c_uint32),
        ("historical_rml13_transition_preserved", c_uint32),
        ("rml14_successor_chain_preserved", c_uint32),
        ("hash216_cryptographic_inversion_used", c_uint32),
        ("second_vm81_commit_primitive_added", c_uint32),
        ("optimizer_transition_authority", c_uint32),
        ("floating_point_authority", c_uint32),
        ("hash216_persistence_authority", c_uint32),
        ("scalar_projection_substitution_authority", c_uint32),
        ("edge_count", c_uint32),
        ("pair_flip_edges", c_uint32),
        ("coupled_move_edges", c_uint32),
        ("reverse_material_length", c_uint32),
        ("restored_ambient_state_index", c_uint64),
        ("reverse_instruction_root_sha256", c_uint8 * 32),
        ("reverse_material_sha256", c_uint8 * 32),
        ("previous_hash72", c_char * 73),
        ("route_bound_change_hash72", c_char * 73),
        ("frozen_uqcel_receipt_hash72", c_char * 73),
        ("rml14_successor_receipt_hash72", c_char * 73),
        ("reverse_receipt_hash72", c_char * 73),
        ("frozen_rml13_transition_hash216", c_char * 217),
        ("rml14_successor_transition_hash216", c_char * 217),
        ("reverse_witness_hash216", c_char * 217),
    ]


def _selected_plan(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    if bundle.get("schema") != RML12_BUNDLE_SCHEMA:
        raise RouteReverseReplayError("RML12_SELECTED_ROUTE_BUNDLE_REQUIRED")
    selection = bundle.get("selection")
    if not isinstance(selection, Mapping):
        raise RouteReverseReplayError("RML12_SELECTION_REQUIRED")
    selected = selection.get("selected_route_sha256")
    for candidate in (bundle.get("shortest_candidate"), bundle.get("complementary_candidate")):
        if isinstance(candidate, Mapping) and candidate.get("route_sha256") == selected:
            if candidate.get("schema") != PLAN_SCHEMA:
                raise RouteReverseReplayError("RML12_ROUTE_PLAN_SCHEMA_REQUIRED")
            return candidate
    raise RouteReverseReplayError("RML12_SELECTED_ROUTE_NOT_MATERIALIZED")


def _digest_into(target: Any, value: Any, label: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise RouteReverseReplayError(f"{label}_SHA256_REQUIRED")
    try:
        raw = bytes.fromhex(value)
    except ValueError as exc:
        raise RouteReverseReplayError(f"{label}_SHA256_REQUIRED") from exc
    if len(raw) != 32 or not any(raw):
        raise RouteReverseReplayError(f"{label}_SHA256_NONZERO_REQUIRED")
    for index, octet in enumerate(raw):
        target[index] = octet


def _phase_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return (
        left.get("phases") == right.get("phases")
        and left.get("quarter_turn_signs") == right.get("quarter_turn_signs")
        and left.get("ambient_state_index") == right.get("ambient_state_index")
    )


def _require_endpoint(state: Mapping[str, Any], plan: Mapping[str, Any], prefix: str) -> None:
    if state.get("schema") != GYROSCOPE_SCHEMA or state.get("admissible_product_geometry") is not True:
        raise RouteReverseReplayError(f"RML15_{prefix}_ADMISSIBLE_GYROSCOPE_STATE_REQUIRED")
    if tuple(state.get("phases", {}).keys()) != CHANNELS:
        raise RouteReverseReplayError(f"RML15_{prefix}_ORDERED_PHASES_REQUIRED")
    if tuple(state.get("quarter_turn_signs", {}).keys()) != PRODUCTS:
        raise RouteReverseReplayError(f"RML15_{prefix}_ORDERED_SIGNS_REQUIRED")
    if state.get("state_sha256") != plan.get(f"{prefix.lower()}_state_sha256"):
        raise RouteReverseReplayError(f"RML15_{prefix}_STATE_HASH_MISMATCH")
    if state.get("ambient_state_index") != plan.get(f"{prefix.lower()}_ambient_state_index"):
        raise RouteReverseReplayError(f"RML15_{prefix}_AMBIENT_INDEX_MISMATCH")


def _fill_phase_state(target: HHSExactPass219RML15PhaseStateV1, state: Mapping[str, Any]) -> None:
    for index, channel in enumerate(CHANNELS):
        phase = state["phases"][channel]
        if isinstance(phase, bool) or not isinstance(phase, int) or phase < 0 or phase >= 72:
            raise RouteReverseReplayError("RML15_PHASE72_EXACT_INTEGER_REQUIRED")
        target.phases[index] = phase
    for index, product in enumerate(PRODUCTS):
        sign = state["quarter_turn_signs"][product]
        if isinstance(sign, bool) or not isinstance(sign, int) or sign not in (-1, 1):
            raise RouteReverseReplayError("RML15_QUARTER_TURN_SIGN_REQUIRED")
        target.quarter_turn_signs[index] = sign
    target.ambient_state_index = int(state["ambient_state_index"])


def build_reverse_witness(
    bundle: Mapping[str, Any],
    source_state: Mapping[str, Any],
    target_state: Mapping[str, Any],
) -> tuple[HHSExactPass219RML15ReverseWitnessV1, dict[str, Any]]:
    """Construct exact reverse instructions from the retained selected RML12 edge ancestry."""
    plan = _selected_plan(bundle)
    _require_endpoint(source_state, plan, "SOURCE")
    _require_endpoint(target_state, plan, "TARGET")
    edges = plan.get("edges")
    if not isinstance(edges, list) or len(edges) > RML15_MAX_EDGES:
        raise RouteReverseReplayError("RML15_BOUNDED_RML12_EDGE_LIST_REQUIRED")
    if plan.get("all_edges_reversible") is not True or plan.get("reverse_edge_sequence_restores_source_exactly") is not True:
        raise RouteReverseReplayError("RML15_VALIDATED_RML12_REVERSE_PROOF_REQUIRED")

    witness = HHSExactPass219RML15ReverseWitnessV1()
    witness.struct_size = ctypes.sizeof(HHSExactPass219RML15ReverseWitnessV1)
    witness.version = RML15_VERSION
    witness.edge_count = len(edges)
    witness.retained_forward_ancestry_used = 1
    witness.reverse_edges_are_exact_inverses = 1
    witness.reverse_terminal_matches_retained_source = 1
    witness.hash216_cryptographic_inversion_used = 0
    witness.floating_point_authority = 0
    _digest_into(witness.route_sha256, plan.get("route_sha256"), "ROUTE")
    _digest_into(witness.source_state_sha256, plan.get("source_state_sha256"), "SOURCE_STATE")
    _digest_into(witness.target_state_sha256, plan.get("target_state_sha256"), "TARGET_STATE")
    _fill_phase_state(witness.source_state, source_state)
    _fill_phase_state(witness.target_state, target_state)

    current: Mapping[str, Any] = dict(target_state)
    reverse_trace: list[dict[str, Any]] = []
    pair_flips = 0
    coupled_moves = 0
    for reverse_index, edge in enumerate(reversed(edges)):
        native_edge = witness.edges[reverse_index]
        kind = edge.get("kind")
        before_index = int(current["ambient_state_index"])
        if kind == "COUPLED_GENERATOR_PRODUCT_PHASE_MOVE":
            generator = str(edge.get("generator"))
            if generator not in GENERATOR_INDEX:
                raise RouteReverseReplayError("RML15_REVERSE_GENERATOR_UNSUPPORTED")
            delta = edge.get("signed_steps")
            if isinstance(delta, bool) or not isinstance(delta, int):
                raise RouteReverseReplayError("RML15_FORWARD_SIGNED_STEPS_REQUIRED")
            inverse_delta = -delta
            native_edge.kind = RML15_EDGE_COUPLED_MOVE
            native_edge.selector = GENERATOR_INDEX[generator]
            native_edge.signed_steps = inverse_delta
            product = str(edge.get("dependent_product"))
            steps = {channel: 0 for channel in CHANNELS}
            steps[generator] = inverse_delta
            steps[product] = inverse_delta
            transition = advance_gyroscope(
                current,
                steps,
                transition_id=f"rml15:reverse:{reverse_index}:{generator}",
            )
            current = transition["next_state"]
            coupled_moves += 1
            reverse_trace.append(
                {
                    "kind": kind,
                    "generator": generator,
                    "dependent_product": product,
                    "signed_steps": inverse_delta,
                    "source_ambient_state_index": before_index,
                    "target_ambient_state_index": int(current["ambient_state_index"]),
                }
            )
        elif kind == "CHIRAL_PAIR_U36_FLIP":
            pair_index = edge.get("pair_index")
            if isinstance(pair_index, bool) or not isinstance(pair_index, int) or pair_index not in (0, 1):
                raise RouteReverseReplayError("RML15_PAIR_INDEX_REQUIRED")
            native_edge.kind = RML15_EDGE_PAIR_FLIP
            native_edge.selector = pair_index
            native_edge.signed_steps = 36
            transition = flip_chiral_pair_half_turn(
                current,
                pair_index=pair_index,
                transition_id=f"rml15:reverse:{reverse_index}:pair:{pair_index}",
            )
            current = transition["next_state"]
            pair_flips += 1
            reverse_trace.append(
                {
                    "kind": kind,
                    "pair_index": pair_index,
                    "signed_steps": 36,
                    "source_ambient_state_index": before_index,
                    "target_ambient_state_index": int(current["ambient_state_index"]),
                }
            )
        else:
            raise RouteReverseReplayError("RML15_ROUTE_EDGE_KIND_UNSUPPORTED")
        if current.get("admissible_product_geometry") is not True:
            raise AssertionError("RML15_REVERSE_LEFT_ADMISSIBLE_PRODUCT_GEOMETRY")

    if not _phase_equal(current, source_state):
        raise AssertionError("RML15_REVERSE_DID_NOT_RESTORE_RETAINED_SOURCE_PHASE_STATE")

    summary = {
        "selected_route_sha256": plan["route_sha256"],
        "source_state_sha256": plan["source_state_sha256"],
        "target_state_sha256": plan["target_state_sha256"],
        "source_ambient_state_index": int(source_state["ambient_state_index"]),
        "target_ambient_state_index": int(target_state["ambient_state_index"]),
        "edge_count": len(edges),
        "pair_flip_edges": pair_flips,
        "coupled_move_edges": coupled_moves,
        "reverse_trace": reverse_trace,
        "python_reverse_phase_state_restored": True,
        "python_reverse_uses_retained_edge_ancestry": True,
        "hash216_cryptographic_inversion_used": False,
    }
    return witness, summary


def _load_extension(repository_root: Path) -> ctypes.CDLL:
    library = repository_root / "hhs_runtime" / "builds" / "libhhs_pass219_rml15.so"
    if not library.is_file():
        raise RouteReverseReplayError(f"RML15_NATIVE_EXTENSION_MISSING:{library}")
    native = ctypes.CDLL(str(library))
    native.hhs_exact_pass219_rml15_version.argtypes = []
    native.hhs_exact_pass219_rml15_version.restype = c_uint32
    native.hhs_exact_pass219_rml15_verify_route_reverse_replay.argtypes = [
        POINTER(c_uint8),
        c_size_t,
        POINTER(HHSExactPass219RML13RouteWitnessV1),
        POINTER(HHSExactPass219RML15ReverseWitnessV1),
        POINTER(HHSExactPass219RML15BindingV1),
    ]
    native.hhs_exact_pass219_rml15_verify_route_reverse_replay.restype = ctypes.c_int
    return native


def _ascii(value: bytes) -> str:
    return value.decode("ascii")


def bind_route_reverse_replay(
    bundle: Mapping[str, Any],
    source_state: Mapping[str, Any],
    target_state: Mapping[str, Any],
    *,
    repository_root: str | Path,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    source_bytes = (root / CANONICAL_SOURCE_PATH).read_bytes()
    if len(source_bytes) != CANONICAL_SOURCE_BYTES:
        raise RouteReverseReplayError("PASS169_CANONICAL_SOURCE_LENGTH_MISMATCH")
    import hashlib

    if hashlib.sha256(source_bytes).hexdigest() != CANONICAL_SOURCE_SHA256:
        raise RouteReverseReplayError("PASS169_CANONICAL_SOURCE_IDENTITY_MISMATCH")

    route_witness, _ = build_route_witness(bundle)
    reverse_witness, summary = build_reverse_witness(bundle, source_state, target_state)
    native = _load_extension(root)
    if int(native.hhs_exact_pass219_rml15_version()) != RML15_VERSION:
        raise RouteReverseReplayError("RML15_NATIVE_VERSION_MISMATCH")

    raw = (c_uint8 * len(source_bytes)).from_buffer_copy(source_bytes)
    binding = HHSExactPass219RML15BindingV1()
    status = int(
        native.hhs_exact_pass219_rml15_verify_route_reverse_replay(
            raw,
            len(source_bytes),
            ctypes.byref(route_witness),
            ctypes.byref(reverse_witness),
            ctypes.byref(binding),
        )
    )
    if status != 0 or binding.decision != RML15_VERIFIED:
        raise RouteReverseReplayError(
            f"RML15_NATIVE_STATUS_{status}_DECISION_{int(binding.decision)}_REASON_{int(binding.reason)}"
        )

    required_true = (
        "rml14_forward_verified",
        "rml14_replay_verified",
        "forward_replay_identity_equal",
        "retained_ancestry_verified",
        "reverse_instruction_sequence_verified",
        "reverse_phase_state_restored",
        "reverse_ambient_index_restored",
        "reverse_product_geometry_preserved",
        "reverse_chirality_preserved",
        "reverse_receipt_is_ancestry_witness_not_hash_inverse",
        "canonical_hash72_delegate_used",
        "canonical_hash216_delegate_used",
        "historical_uqcel_receipt_preserved",
        "historical_rml13_transition_preserved",
        "rml14_successor_chain_preserved",
    )
    for field in required_true:
        if getattr(binding, field) != 1:
            raise RouteReverseReplayError(f"RML15_REQUIRED_NATIVE_EVIDENCE_MISSING:{field}")
    required_zero = (
        "hash216_cryptographic_inversion_used",
        "second_vm81_commit_primitive_added",
        "optimizer_transition_authority",
        "floating_point_authority",
        "hash216_persistence_authority",
        "scalar_projection_substitution_authority",
    )
    for field in required_zero:
        if getattr(binding, field) != 0:
            raise RouteReverseReplayError(f"RML15_AUTHORITY_BOUNDARY_VIOLATION:{field}")

    return {
        "schema": RML15_RECORD_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "native_abi_version": int(binding.version),
        "decision": int(binding.decision),
        **summary,
        "restored_ambient_state_index": int(binding.restored_ambient_state_index),
        "reverse_instruction_root_sha256": bytes(binding.reverse_instruction_root_sha256).hex(),
        "reverse_material_sha256": bytes(binding.reverse_material_sha256).hex(),
        "reverse_material_length": int(binding.reverse_material_length),
        "previous_hash72": _ascii(binding.previous_hash72),
        "route_bound_change_hash72": _ascii(binding.route_bound_change_hash72),
        "frozen_uqcel_receipt_hash72": _ascii(binding.frozen_uqcel_receipt_hash72),
        "rml14_successor_receipt_hash72": _ascii(binding.rml14_successor_receipt_hash72),
        "reverse_receipt_hash72": _ascii(binding.reverse_receipt_hash72),
        "frozen_rml13_transition_hash216": _ascii(binding.frozen_rml13_transition_hash216),
        "rml14_successor_transition_hash216": _ascii(binding.rml14_successor_transition_hash216),
        "reverse_witness_hash216": _ascii(binding.reverse_witness_hash216),
        "rml14_forward_verified": True,
        "rml14_replay_verified": True,
        "forward_replay_identity_equal": True,
        "retained_ancestry_verified": True,
        "reverse_instruction_sequence_verified": True,
        "reverse_phase_state_restored": True,
        "reverse_ambient_index_restored": True,
        "reverse_product_geometry_preserved": True,
        "reverse_chirality_preserved": True,
        "reverse_receipt_is_ancestry_witness_not_hash_inverse": True,
        "historical_uqcel_receipt_preserved": True,
        "historical_rml13_transition_preserved": True,
        "rml14_successor_chain_preserved": True,
        "canonical_hash72_delegate_used": True,
        "canonical_hash216_delegate_used": True,
        "hash216_cryptographic_inversion_used": False,
        "second_vm81_commit_primitive_added": False,
        "optimizer_transition_authority": False,
        "floating_point_authority": False,
        "hash216_persistence_authority": False,
        "scalar_projection_substitution_authority": False,
    }


__all__ = [
    "HHSExactPass219RML15BindingV1",
    "HHSExactPass219RML15PhaseStateV1",
    "HHSExactPass219RML15ReverseEdgeV1",
    "HHSExactPass219RML15ReverseWitnessV1",
    "RML15_RECORD_SCHEMA",
    "RML15_VERSION",
    "RouteReverseReplayError",
    "bind_route_reverse_replay",
    "build_reverse_witness",
]
