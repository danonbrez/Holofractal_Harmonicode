"""Pass 219 RML13 bridge for native pre-hash RML12 route witness binding.

The Python layer only serializes already-validated RML12 route metadata into the
fixed-width RML13 ABI packet and invokes the native extension. It does not mint
Hash72/Hash216 values, mutate VM81 state, or recompute canonical algebra.
"""
from __future__ import annotations

import ctypes
from ctypes import POINTER, Structure, c_char, c_size_t, c_uint8, c_uint16, c_uint32
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.pass169.runtime_binding import (
    CANONICAL_SOURCE_BYTES,
    CANONICAL_SOURCE_PATH,
    CANONICAL_SOURCE_SHA256,
)
from hhs_runtime.pass219.reciprocal_route_optimizer import PLAN_SCHEMA

PASS = 219
ITERATION = "RML13_NATIVE_ROUTE_WITNESS_BINDING"
RML13_VERSION = (1 << 16) | (26 << 8)
RML13_VERIFIED = 1
RML12_BUNDLE_SCHEMA = "HHS_PASS219_RML12_SELECTED_RECIPROCAL_ROUTE_BUNDLE_V1"
RML13_RECORD_SCHEMA = "HHS_PASS219_RML13_NATIVE_PREHASH_ROUTE_BINDING_RECORD_V1"


class NativeRouteWitnessBindingError(RuntimeError):
    pass


class HHSExactPass219RML13RouteWitnessV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("edge_count", c_uint32),
        ("pair_flip_edges", c_uint32),
        ("coupled_move_edges", c_uint32),
        ("hopf_same_base_edges", c_uint32),
        ("hopf_base_moving_edges", c_uint32),
        ("clifford_full_intertwiner_edges", c_uint32),
        ("clifford_chirality_swap_edges", c_uint32),
        ("clifford_even_sector_preserving_edges", c_uint32),
        ("residual_u72_edges", c_uint32),
        ("product_geometry_admissible", c_uint32),
        ("all_edges_reversible", c_uint32),
        ("target_reached_exactly", c_uint32),
        ("reverse_restores_source_exactly", c_uint32),
        ("optimizer_transition_authority", c_uint32),
        ("floating_point_authority", c_uint32),
        ("route_sha256", c_uint8 * 32),
        ("selection_sha256", c_uint8 * 32),
        ("bundle_sha256", c_uint8 * 32),
        ("source_state_sha256", c_uint8 * 32),
        ("target_state_sha256", c_uint8 * 32),
    ]


class HHSExactPass219RML13BindingV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("decision", c_uint32),
        ("reason", c_uint32),
        ("source_provenance_verified", c_uint32),
        ("route_witness_verified", c_uint32),
        ("witness_serialization_exact", c_uint32),
        ("witness_root_embedded_pre_hash", c_uint32),
        ("candidate_frame_committed", c_uint32),
        ("deterministic_replay_verified", c_uint32),
        ("route_change_hash72_bound_to_witness", c_uint32),
        ("route_hash216_identity_bound_to_witness", c_uint32),
        ("inherited_uqcel_receipt_material_frozen", c_uint32),
        ("inherited_receipt_hash72_directly_bound_to_route_witness", c_uint32),
        ("single_vm81_commit_authority_preserved", c_uint32),
        ("optimizer_transition_authority", c_uint32),
        ("floating_point_authority", c_uint32),
        ("hash216_persistence_authority", c_uint32),
        ("scalar_projection_substitution_authority", c_uint32),
        ("edge_count", c_uint32),
        ("pair_flip_edges", c_uint32),
        ("coupled_move_edges", c_uint32),
        ("hopf_same_base_edges", c_uint32),
        ("hopf_base_moving_edges", c_uint32),
        ("clifford_full_intertwiner_edges", c_uint32),
        ("clifford_chirality_swap_edges", c_uint32),
        ("clifford_even_sector_preserving_edges", c_uint32),
        ("residual_u72_edges", c_uint32),
        ("vm5184_address", c_uint16),
        ("reserved0", c_uint16),
        ("witness_root_sha256", c_uint8 * 32),
        ("route_environment_root_sha256", c_uint8 * 32),
        ("candidate_frame_sha256", c_uint8 * 32),
        ("change_hash72", c_char * 73),
        ("receipt_hash72", c_char * 73),
        ("replay_hash72", c_char * 73),
        ("hash216_triplet", c_char * 217),
        ("transition_hash216", c_char * 217),
    ]


def _digest_bytes(value: Any, label: str) -> bytes:
    if not isinstance(value, str) or len(value) != 64:
        raise NativeRouteWitnessBindingError(f"{label}_SHA256_HEX_REQUIRED")
    try:
        raw = bytes.fromhex(value)
    except ValueError as exc:
        raise NativeRouteWitnessBindingError(f"{label}_SHA256_HEX_REQUIRED") from exc
    if len(raw) != 32 or not any(raw):
        raise NativeRouteWitnessBindingError(f"{label}_SHA256_NONZERO_REQUIRED")
    return raw


def _assign_digest(target: Any, raw: bytes) -> None:
    for index, value in enumerate(raw):
        target[index] = value


def _selected_plan(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    if bundle.get("schema") != RML12_BUNDLE_SCHEMA:
        raise NativeRouteWitnessBindingError("RML12_SELECTED_ROUTE_BUNDLE_REQUIRED")
    selection = bundle.get("selection")
    if not isinstance(selection, Mapping):
        raise NativeRouteWitnessBindingError("RML12_SELECTION_RECORD_REQUIRED")
    selected_sha = selection.get("selected_route_sha256")
    candidates = (bundle.get("shortest_candidate"), bundle.get("complementary_candidate"))
    for candidate in candidates:
        if isinstance(candidate, Mapping) and candidate.get("route_sha256") == selected_sha:
            if candidate.get("schema") != PLAN_SCHEMA:
                raise NativeRouteWitnessBindingError("RML12_ROUTE_PLAN_SCHEMA_REQUIRED")
            return candidate
    raise NativeRouteWitnessBindingError("RML12_SELECTED_ROUTE_NOT_MATERIALIZED")


def build_route_witness(bundle: Mapping[str, Any]) -> tuple[HHSExactPass219RML13RouteWitnessV1, dict[str, Any]]:
    """Serialize one selected RML12 route into the fixed native witness packet."""
    plan = _selected_plan(bundle)
    selection = bundle["selection"]
    edges = plan.get("edges")
    if not isinstance(edges, list):
        raise NativeRouteWitnessBindingError("RML12_EDGE_LIST_REQUIRED")

    pair_flip = sum(edge.get("kind") == "CHIRAL_PAIR_U36_FLIP" for edge in edges)
    coupled = sum(edge.get("kind") == "COUPLED_GENERATOR_PRODUCT_PHASE_MOVE" for edge in edges)
    hopf_same = sum(edge.get("same_hopf_base") is True for edge in edges)
    hopf_move = len(edges) - hopf_same
    full = sum(edge.get("full_cl08_module_intertwiner") is True for edge in edges)
    swap = sum(edge.get("clifford_chirality_sector_swapping") is True for edge in edges)
    residual = sum(edge.get("residual_u72_phase_preserved") is True for edge in edges)
    even = sum(
        edge.get("complete_clifford_lift") is True
        and edge.get("full_cl08_module_intertwiner") is not True
        and edge.get("clifford_chirality_sector_swapping") is not True
        for edge in edges
    )

    edge_count = len(edges)
    if pair_flip + coupled != edge_count:
        raise NativeRouteWitnessBindingError("RML12_EDGE_KIND_PARTITION_INCOMPLETE")
    if hopf_same + hopf_move != edge_count:
        raise NativeRouteWitnessBindingError("RML12_HOPF_PARTITION_INCOMPLETE")
    if full + swap + even + residual != edge_count:
        raise NativeRouteWitnessBindingError("RML12_CLIFFORD_PARTITION_INCOMPLETE")
    if plan.get("all_edges_remain_in_admissible_product_geometry") is not True:
        raise NativeRouteWitnessBindingError("RML12_PRODUCT_GEOMETRY_REQUIRED")
    if plan.get("all_edges_reversible") is not True:
        raise NativeRouteWitnessBindingError("RML12_EDGE_REVERSIBILITY_REQUIRED")
    if plan.get("target_reached_exactly") is not True:
        raise NativeRouteWitnessBindingError("RML12_EXACT_TARGET_REQUIRED")
    if plan.get("reverse_edge_sequence_restores_source_exactly") is not True:
        raise NativeRouteWitnessBindingError("RML12_REVERSE_RESTORATION_REQUIRED")
    if plan.get("route_selector_has_canonical_transition_authority") is not False:
        raise NativeRouteWitnessBindingError("RML12_OPTIMIZER_AUTHORITY_FORBIDDEN")
    if plan.get("floating_point_authority") is not False:
        raise NativeRouteWitnessBindingError("RML12_FLOAT_AUTHORITY_FORBIDDEN")

    witness = HHSExactPass219RML13RouteWitnessV1()
    witness.struct_size = ctypes.sizeof(HHSExactPass219RML13RouteWitnessV1)
    witness.version = RML13_VERSION
    witness.edge_count = edge_count
    witness.pair_flip_edges = pair_flip
    witness.coupled_move_edges = coupled
    witness.hopf_same_base_edges = hopf_same
    witness.hopf_base_moving_edges = hopf_move
    witness.clifford_full_intertwiner_edges = full
    witness.clifford_chirality_swap_edges = swap
    witness.clifford_even_sector_preserving_edges = even
    witness.residual_u72_edges = residual
    witness.product_geometry_admissible = 1
    witness.all_edges_reversible = 1
    witness.target_reached_exactly = 1
    witness.reverse_restores_source_exactly = 1
    witness.optimizer_transition_authority = 0
    witness.floating_point_authority = 0

    _assign_digest(witness.route_sha256, _digest_bytes(plan.get("route_sha256"), "ROUTE"))
    _assign_digest(witness.selection_sha256, _digest_bytes(selection.get("selection_sha256"), "SELECTION"))
    _assign_digest(witness.bundle_sha256, _digest_bytes(bundle.get("bundle_sha256"), "BUNDLE"))
    _assign_digest(witness.source_state_sha256, _digest_bytes(plan.get("source_state_sha256"), "SOURCE_STATE"))
    _assign_digest(witness.target_state_sha256, _digest_bytes(plan.get("target_state_sha256"), "TARGET_STATE"))

    summary = {
        "selected_route_sha256": plan["route_sha256"],
        "selection_sha256": selection["selection_sha256"],
        "bundle_sha256": bundle["bundle_sha256"],
        "source_state_sha256": plan["source_state_sha256"],
        "target_state_sha256": plan["target_state_sha256"],
        "edge_count": edge_count,
        "pair_flip_edges": pair_flip,
        "coupled_move_edges": coupled,
        "hopf_same_base_edges": hopf_same,
        "hopf_base_moving_edges": hopf_move,
        "clifford_full_intertwiner_edges": full,
        "clifford_chirality_swap_edges": swap,
        "clifford_even_sector_preserving_edges": even,
        "residual_u72_edges": residual,
    }
    return witness, summary


def _load_extension(repository_root: Path) -> ctypes.CDLL:
    library = repository_root / "hhs_runtime" / "builds" / "libhhs_pass219_rml13.so"
    if not library.is_file():
        raise NativeRouteWitnessBindingError(f"RML13_NATIVE_EXTENSION_MISSING:{library}")
    native = ctypes.CDLL(str(library))
    native.hhs_exact_pass219_rml13_version.argtypes = []
    native.hhs_exact_pass219_rml13_version.restype = c_uint32
    native.hhs_exact_pass219_rml13_bind_route_pre_hash.argtypes = [
        POINTER(c_uint8),
        c_size_t,
        POINTER(HHSExactPass219RML13RouteWitnessV1),
        POINTER(HHSExactPass219RML13BindingV1),
    ]
    native.hhs_exact_pass219_rml13_bind_route_pre_hash.restype = ctypes.c_int
    return native


def invoke_native_route_witness(
    witness: HHSExactPass219RML13RouteWitnessV1,
    *,
    repository_root: str | Path,
) -> HHSExactPass219RML13BindingV1:
    root = Path(repository_root).resolve()
    source = (root / CANONICAL_SOURCE_PATH).read_bytes()
    if len(source) != CANONICAL_SOURCE_BYTES:
        raise NativeRouteWitnessBindingError("PASS169_CANONICAL_SOURCE_LENGTH_MISMATCH")
    import hashlib

    if hashlib.sha256(source).hexdigest() != CANONICAL_SOURCE_SHA256:
        raise NativeRouteWitnessBindingError("PASS169_CANONICAL_SOURCE_IDENTITY_MISMATCH")

    native = _load_extension(root)
    if int(native.hhs_exact_pass219_rml13_version()) != RML13_VERSION:
        raise NativeRouteWitnessBindingError("RML13_NATIVE_VERSION_MISMATCH")
    raw = (c_uint8 * len(source)).from_buffer_copy(source)
    binding = HHSExactPass219RML13BindingV1()
    status = int(
        native.hhs_exact_pass219_rml13_bind_route_pre_hash(
            raw,
            len(source),
            ctypes.byref(witness),
            ctypes.byref(binding),
        )
    )
    if status != 0:
        raise NativeRouteWitnessBindingError(
            f"RML13_NATIVE_BINDING_STATUS_{status}_REASON_{int(binding.reason)}"
        )
    if binding.decision != RML13_VERIFIED:
        raise NativeRouteWitnessBindingError(
            f"RML13_NATIVE_BINDING_REJECTED_REASON_{int(binding.reason)}"
        )
    return binding


def _ascii(value: bytes) -> str:
    return value.decode("ascii")


def bind_selected_route_pre_hash(
    bundle: Mapping[str, Any],
    *,
    repository_root: str | Path,
) -> dict[str, Any]:
    witness, summary = build_route_witness(bundle)
    binding = invoke_native_route_witness(witness, repository_root=repository_root)

    required_true = (
        "source_provenance_verified",
        "route_witness_verified",
        "witness_serialization_exact",
        "witness_root_embedded_pre_hash",
        "candidate_frame_committed",
        "deterministic_replay_verified",
        "route_change_hash72_bound_to_witness",
        "route_hash216_identity_bound_to_witness",
        "inherited_uqcel_receipt_material_frozen",
        "single_vm81_commit_authority_preserved",
    )
    for field in required_true:
        if getattr(binding, field) != 1:
            raise NativeRouteWitnessBindingError(f"RML13_REQUIRED_NATIVE_EVIDENCE_MISSING:{field}")
    required_zero = (
        "inherited_receipt_hash72_directly_bound_to_route_witness",
        "optimizer_transition_authority",
        "floating_point_authority",
        "hash216_persistence_authority",
        "scalar_projection_substitution_authority",
    )
    for field in required_zero:
        if getattr(binding, field) != 0:
            raise NativeRouteWitnessBindingError(f"RML13_AUTHORITY_BOUNDARY_VIOLATION:{field}")

    record = {
        "schema": RML13_RECORD_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "native_abi_version": int(binding.version),
        "decision": int(binding.decision),
        **summary,
        "witness_root_sha256": bytes(binding.witness_root_sha256).hex(),
        "route_environment_root_sha256": bytes(binding.route_environment_root_sha256).hex(),
        "candidate_frame_sha256": bytes(binding.candidate_frame_sha256).hex(),
        "vm5184_address": int(binding.vm5184_address),
        "change_hash72": _ascii(binding.change_hash72),
        "receipt_hash72": _ascii(binding.receipt_hash72),
        "replay_hash72": _ascii(binding.replay_hash72),
        "hash216_triplet": _ascii(binding.hash216_triplet),
        "transition_hash216": _ascii(binding.transition_hash216),
        "source_provenance_verified": True,
        "route_witness_verified": True,
        "witness_serialization_exact": True,
        "witness_root_embedded_pre_hash": True,
        "candidate_frame_committed": True,
        "deterministic_replay_verified": True,
        "route_change_hash72_bound_to_witness": True,
        "route_hash216_identity_bound_to_witness": True,
        "inherited_uqcel_receipt_material_frozen": True,
        "inherited_receipt_hash72_directly_bound_to_route_witness": False,
        "single_vm81_commit_authority_preserved": True,
        "optimizer_transition_authority": False,
        "floating_point_authority": False,
        "hash216_persistence_authority": False,
        "scalar_projection_substitution_authority": False,
        "historical_i162_i168_hashes_modified": False,
    }
    if record["receipt_hash72"] != record["replay_hash72"]:
        raise NativeRouteWitnessBindingError("RML13_REPLAY_RECEIPT_DRIFT")
    return record


__all__ = [
    "HHSExactPass219RML13BindingV1",
    "HHSExactPass219RML13RouteWitnessV1",
    "NativeRouteWitnessBindingError",
    "RML13_RECORD_SCHEMA",
    "RML13_VERSION",
    "bind_selected_route_pre_hash",
    "build_route_witness",
    "invoke_native_route_witness",
]
