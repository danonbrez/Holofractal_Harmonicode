"""Pass 219 RML14 native route-bound receipt successor bridge.

RML14 closes the receipt-side witness gap left intentionally by frozen UQCEL v1.
It delegates all Hash72/Hash216 computation to the canonical native runtime and
leaves the existing RML13/UQCEL VM81 commit path unchanged. Python only builds
the validated RML13 route witness packet and transports the native result.
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
from hhs_runtime.pass219.native_route_witness_binding import (
    HHSExactPass219RML13RouteWitnessV1,
    build_route_witness,
)

PASS = 219
ITERATION = "RML14_ROUTE_BOUND_RECEIPT_SUCCESSOR"
RML14_VERSION = (1 << 16) | (27 << 8)
RML14_VERIFIED = 1
RML14_RECORD_SCHEMA = "HHS_PASS219_RML14_ROUTE_BOUND_RECEIPT_SUCCESSOR_RECORD_V1"


class RouteBoundReceiptSuccessorError(RuntimeError):
    pass


class HHSExactPass219RML14BindingV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("decision", c_uint32),
        ("reason", c_uint32),
        ("rml13_binding_verified", c_uint32),
        ("receipt_material_exact", c_uint32),
        ("receipt_material_contains_route_witness_root", c_uint32),
        ("receipt_material_contains_route_bound_change_hash72", c_uint32),
        ("successor_receipt_hash72_route_bound", c_uint32),
        ("successor_hash216_triplet_route_bound", c_uint32),
        ("successor_hash216_identity_route_bound", c_uint32),
        ("frozen_uqcel_receipt_preserved", c_uint32),
        ("frozen_rml13_transition_preserved", c_uint32),
        ("canonical_hash72_delegate_used", c_uint32),
        ("canonical_hash216_delegate_used", c_uint32),
        ("canonical_hash216_parity_with_frozen_uqcel_verified", c_uint32),
        ("independent_hash_implementation_used", c_uint32),
        ("second_vm81_commit_primitive_added", c_uint32),
        ("single_vm81_commit_authority_preserved", c_uint32),
        ("optimizer_transition_authority", c_uint32),
        ("floating_point_authority", c_uint32),
        ("hash216_persistence_authority", c_uint32),
        ("scalar_projection_substitution_authority", c_uint32),
        ("receipt_material_length", c_uint32),
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
        ("receipt_material_sha256", c_uint8 * 32),
        ("witness_root_sha256", c_uint8 * 32),
        ("route_environment_root_sha256", c_uint8 * 32),
        ("candidate_frame_sha256", c_uint8 * 32),
        ("previous_hash72", c_char * 73),
        ("change_hash72", c_char * 73),
        ("frozen_uqcel_receipt_hash72", c_char * 73),
        ("successor_receipt_hash72", c_char * 73),
        ("frozen_rml13_transition_hash216", c_char * 217),
        ("successor_hash216_triplet", c_char * 217),
        ("successor_transition_hash216", c_char * 217),
    ]


def _load_extension(repository_root: Path) -> ctypes.CDLL:
    library = repository_root / "hhs_runtime" / "builds" / "libhhs_pass219_rml14.so"
    if not library.is_file():
        raise RouteBoundReceiptSuccessorError(f"RML14_NATIVE_EXTENSION_MISSING:{library}")
    native = ctypes.CDLL(str(library))
    native.hhs_exact_pass219_rml14_version.argtypes = []
    native.hhs_exact_pass219_rml14_version.restype = c_uint32
    native.hhs_exact_pass219_rml14_bind_route_receipt_successor.argtypes = [
        POINTER(c_uint8),
        c_size_t,
        POINTER(HHSExactPass219RML13RouteWitnessV1),
        POINTER(HHSExactPass219RML14BindingV1),
    ]
    native.hhs_exact_pass219_rml14_bind_route_receipt_successor.restype = ctypes.c_int
    return native


def invoke_native_route_bound_receipt(
    witness: HHSExactPass219RML13RouteWitnessV1,
    *,
    repository_root: str | Path,
) -> HHSExactPass219RML14BindingV1:
    root = Path(repository_root).resolve()
    source = (root / CANONICAL_SOURCE_PATH).read_bytes()
    if len(source) != CANONICAL_SOURCE_BYTES:
        raise RouteBoundReceiptSuccessorError("PASS169_CANONICAL_SOURCE_LENGTH_MISMATCH")
    import hashlib

    if hashlib.sha256(source).hexdigest() != CANONICAL_SOURCE_SHA256:
        raise RouteBoundReceiptSuccessorError("PASS169_CANONICAL_SOURCE_IDENTITY_MISMATCH")

    native = _load_extension(root)
    if int(native.hhs_exact_pass219_rml14_version()) != RML14_VERSION:
        raise RouteBoundReceiptSuccessorError("RML14_NATIVE_VERSION_MISMATCH")

    raw = (c_uint8 * len(source)).from_buffer_copy(source)
    binding = HHSExactPass219RML14BindingV1()
    status = int(
        native.hhs_exact_pass219_rml14_bind_route_receipt_successor(
            raw,
            len(source),
            ctypes.byref(witness),
            ctypes.byref(binding),
        )
    )
    if status != 0:
        raise RouteBoundReceiptSuccessorError(
            f"RML14_NATIVE_BINDING_STATUS_{status}_REASON_{int(binding.reason)}"
        )
    if binding.decision != RML14_VERIFIED:
        raise RouteBoundReceiptSuccessorError(
            f"RML14_NATIVE_BINDING_REJECTED_REASON_{int(binding.reason)}"
        )
    return binding


def _ascii(value: bytes) -> str:
    return value.decode("ascii")


def bind_selected_route_receipt_successor(
    bundle: Mapping[str, Any],
    *,
    repository_root: str | Path,
) -> dict[str, Any]:
    witness, summary = build_route_witness(bundle)
    binding = invoke_native_route_bound_receipt(witness, repository_root=repository_root)

    required_true = (
        "rml13_binding_verified",
        "receipt_material_exact",
        "receipt_material_contains_route_witness_root",
        "receipt_material_contains_route_bound_change_hash72",
        "successor_receipt_hash72_route_bound",
        "successor_hash216_triplet_route_bound",
        "successor_hash216_identity_route_bound",
        "frozen_uqcel_receipt_preserved",
        "frozen_rml13_transition_preserved",
        "canonical_hash72_delegate_used",
        "canonical_hash216_delegate_used",
        "canonical_hash216_parity_with_frozen_uqcel_verified",
        "single_vm81_commit_authority_preserved",
    )
    for field in required_true:
        if getattr(binding, field) != 1:
            raise RouteBoundReceiptSuccessorError(f"RML14_REQUIRED_NATIVE_EVIDENCE_MISSING:{field}")

    required_zero = (
        "independent_hash_implementation_used",
        "second_vm81_commit_primitive_added",
        "optimizer_transition_authority",
        "floating_point_authority",
        "hash216_persistence_authority",
        "scalar_projection_substitution_authority",
    )
    for field in required_zero:
        if getattr(binding, field) != 0:
            raise RouteBoundReceiptSuccessorError(f"RML14_AUTHORITY_BOUNDARY_VIOLATION:{field}")

    record = {
        "schema": RML14_RECORD_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "native_abi_version": int(binding.version),
        "decision": int(binding.decision),
        **summary,
        "receipt_material_length": int(binding.receipt_material_length),
        "receipt_material_sha256": bytes(binding.receipt_material_sha256).hex(),
        "witness_root_sha256": bytes(binding.witness_root_sha256).hex(),
        "route_environment_root_sha256": bytes(binding.route_environment_root_sha256).hex(),
        "candidate_frame_sha256": bytes(binding.candidate_frame_sha256).hex(),
        "vm5184_address": int(binding.vm5184_address),
        "previous_hash72": _ascii(binding.previous_hash72),
        "change_hash72": _ascii(binding.change_hash72),
        "frozen_uqcel_receipt_hash72": _ascii(binding.frozen_uqcel_receipt_hash72),
        "successor_receipt_hash72": _ascii(binding.successor_receipt_hash72),
        "frozen_rml13_transition_hash216": _ascii(binding.frozen_rml13_transition_hash216),
        "successor_hash216_triplet": _ascii(binding.successor_hash216_triplet),
        "successor_transition_hash216": _ascii(binding.successor_transition_hash216),
        "rml13_binding_verified": True,
        "receipt_material_exact": True,
        "receipt_material_contains_route_witness_root": True,
        "receipt_material_contains_route_bound_change_hash72": True,
        "successor_receipt_hash72_route_bound": True,
        "successor_hash216_triplet_route_bound": True,
        "successor_hash216_identity_route_bound": True,
        "frozen_uqcel_receipt_preserved": True,
        "frozen_rml13_transition_preserved": True,
        "canonical_hash72_delegate_used": True,
        "canonical_hash216_delegate_used": True,
        "canonical_hash216_parity_with_frozen_uqcel_verified": True,
        "independent_hash_implementation_used": False,
        "second_vm81_commit_primitive_added": False,
        "single_vm81_commit_authority_preserved": True,
        "optimizer_transition_authority": False,
        "floating_point_authority": False,
        "hash216_persistence_authority": False,
        "scalar_projection_substitution_authority": False,
        "historical_uqcel_v1_receipt_rewritten": False,
        "historical_rml13_transition_rewritten": False,
    }
    return record


__all__ = [
    "HHSExactPass219RML14BindingV1",
    "RML14_RECORD_SCHEMA",
    "RML14_VERSION",
    "RouteBoundReceiptSuccessorError",
    "bind_selected_route_receipt_successor",
    "invoke_native_route_bound_receipt",
]
