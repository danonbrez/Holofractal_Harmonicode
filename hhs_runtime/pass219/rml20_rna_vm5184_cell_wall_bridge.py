"""Pass 219 RML20 RNA/VM5184 bridge over the current sealed RML17 geometry.

RML20 is additive. It lowers one current RML17 directed address
(operation64, phase72, cell81, direction4) into the public exact 648-byte
VM5184 candidate ABI and C++ RNA cell wall, then proves parity back to RML17.

The native path remains candidate-only. It has no VM81 mutation, Hash72 mint,
Hash216 persistence, canonical persistence, or floating-point authority.
"""
from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.discrete_transport_conservation import (
    ADDRESS_COUNT,
    CELL_COUNT,
    DIRECTIONS,
    DIRECTION_COUNT,
    INDEX_DIRECTION,
    OPERATIONS_PER_CELL,
    PHASE_COUNT,
    decode_transport_address,
    discrete_divergence,
    reciprocal_direction_index,
    signed_address_flux,
    transport_neighbor,
)

PASS = 219
ITERATION = "RML20_RNA_VM5184_CELL_WALL_BRIDGE"
SCHEMA = "HHS_PASS219_RML20_RNA_VM5184_CELL_WALL_BRIDGE_V2"
LIBRARY_ENV = "HHS_PASS219_RML20_NATIVE_LIB"
VM5184_BYTES = 648
HASH72_STRLEN = 73
HASH216_STRLEN = 217
HASH216_OCCURRENCES = 216
SHA256_BYTES = 32
HHS_EXACT_STATUS_OK = 0
INTEGER_SYMMETRIC_PROFILE = 1

NATIVE_DIRECTION = {name: index for index, name in enumerate(DIRECTIONS)}


class RML20NativeBridgeError(RuntimeError):
    pass


class _BigUIntView(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("byte_length", ctypes.c_uint32),
        ("bytes_be", ctypes.POINTER(ctypes.c_uint8)),
    ]


class _UQCELInput(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("uqcel_version", ctypes.c_uint32),
        ("profile", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("P", _BigUIntView),
        ("p", _BigUIntView),
        ("q", _BigUIntView),
        ("delta", _BigUIntView),
        ("A", _BigUIntView),
        ("B", _BigUIntView),
        ("cell81", ctypes.c_uint8),
        ("left_basis8", ctypes.c_uint8),
        ("right_basis8", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8),
        ("source_envelope_sha256", ctypes.c_uint8 * SHA256_BYTES),
        ("previous_hash72", ctypes.c_char * HASH72_STRLEN),
    ]


class _Hash72Occurrence(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("absolute_position216", ctypes.c_uint16),
        ("lane_role", ctypes.c_uint8),
        ("lane_position72", ctypes.c_uint8),
        ("glyph", ctypes.c_uint8),
        ("sha256_index_present", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8 * 2),
        ("sha256_index_record", ctypes.c_uint8 * SHA256_BYTES),
    ]


class _Hash216Transition(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("previous_hash72", ctypes.c_char * HASH72_STRLEN),
        ("change_hash72", ctypes.c_char * HASH72_STRLEN),
        ("receipt_hash72", ctypes.c_char * HASH72_STRLEN),
        ("transition_word216", ctypes.c_char * HASH216_STRLEN),
        ("transition_identity216", ctypes.c_char * HASH216_STRLEN),
        ("occurrences", _Hash72Occurrence * HASH216_OCCURRENCES),
        ("resolved_index_count", ctypes.c_uint16),
        ("reserved0", ctypes.c_uint16),
    ]


class _Descriptor(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("lane_count", ctypes.c_uint32),
        ("operations_per_cell", ctypes.c_uint32),
        ("phase_count", ctypes.c_uint32),
        ("cell_count", ctypes.c_uint32),
        ("address_count", ctypes.c_uint32),
        ("direction_count", ctypes.c_uint32),
        ("vm5184_bytes", ctypes.c_uint32),
        ("cpp_rna_cell_wall", ctypes.c_uint8),
        ("current_rml17_parity_surface", ctypes.c_uint8),
        ("direction_embedded_address", ctypes.c_uint8),
        ("reciprocal_flux_transport", ctypes.c_uint8),
        ("candidate_only", ctypes.c_uint8),
        ("exact_integer_only", ctypes.c_uint8),
        ("canonical_mutation_authority", ctypes.c_uint8),
        ("canonical_hash72_authority", ctypes.c_uint8),
        ("canonical_hash216_authority", ctypes.c_uint8),
        ("canonical_persistence_authority", ctypes.c_uint8),
        ("floating_point_authority", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8 * 5),
    ]


class _Receipt(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("source_address", ctypes.c_uint32),
        ("target_address", ctypes.c_uint32),
        ("source_operation", ctypes.c_uint8),
        ("source_phase", ctypes.c_uint8),
        ("source_cell", ctypes.c_uint8),
        ("source_direction", ctypes.c_uint8),
        ("target_operation", ctypes.c_uint8),
        ("target_phase", ctypes.c_uint8),
        ("target_cell", ctypes.c_uint8),
        ("target_direction", ctypes.c_uint8),
        ("requested_direction", ctypes.c_uint8),
        ("inverse_direction", ctypes.c_uint8),
        ("forward_flux", ctypes.c_int8),
        ("reverse_flux", ctypes.c_int8),
        ("discrete_divergence", ctypes.c_int8),
        ("encode_decode_bijective", ctypes.c_uint8),
        ("reciprocal_neighbor_restores_source", ctypes.c_uint8),
        ("reciprocal_flux_balanced", ctypes.c_uint8),
        ("operation_cell_preserved", ctypes.c_uint8),
        ("zero_discrete_divergence", ctypes.c_uint8),
        ("zero_diffusion_classification", ctypes.c_uint8),
        ("feedback_lane_bound", ctypes.c_uint8),
        ("feedback_trinary_bound", ctypes.c_uint8),
        ("rna_cell_wall_routed", ctypes.c_uint8),
        ("selected_lane", ctypes.c_uint8),
        ("candidate_only", ctypes.c_uint8),
        ("exact_integer_only", ctypes.c_uint8),
        ("canonical_mutation_authority", ctypes.c_uint8),
        ("canonical_hash72_authority", ctypes.c_uint8),
        ("canonical_hash216_authority", ctypes.c_uint8),
        ("canonical_persistence_authority", ctypes.c_uint8),
        ("floating_point_authority", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8 * 4),
        ("graph_signature64", ctypes.c_uint64),
        ("tensor_signature64", ctypes.c_uint64),
        ("decision_signature64", ctypes.c_uint64),
        ("transition_identity216", ctypes.c_char * HASH216_STRLEN),
    ]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_library_path() -> Path:
    explicit = os.environ.get(LIBRARY_ENV)
    if explicit:
        return Path(explicit).expanduser().resolve()
    build_root = _repo_root() / "hhs_runtime" / "builds"
    if sys.platform.startswith("win"):
        name = "hhs_runtime.dll"
    elif sys.platform == "darwin":
        name = "libhhs_runtime.dylib"
    else:
        name = "libhhs_runtime.so"
    return build_root / name


def _load_library(path: str | Path | None = None) -> tuple[ctypes.CDLL, Path, _Descriptor]:
    selected = Path(path).expanduser().resolve() if path is not None else _default_library_path()
    if not selected.is_file():
        raise RML20NativeBridgeError(f"RML20_NATIVE_LIBRARY_REQUIRED:{selected}")
    try:
        library = ctypes.CDLL(str(selected))
    except OSError as exc:
        raise RML20NativeBridgeError(
            f"RML20_NATIVE_LIBRARY_LOAD_FAILED:{selected}:{exc}"
        ) from exc

    required = (
        "hhs_exact_uqcel_version",
        "hhs_exact_pass219_vm81_pqc_hash216_genesis_reference",
        "hhs_exact_pass219_rml20_rna_vm5184_version",
        "hhs_exact_pass219_rml20_rna_vm5184_descriptor",
        "hhs_exact_pass219_rml20_rna_vm5184_route",
    )
    for symbol in required:
        if not hasattr(library, symbol):
            raise RML20NativeBridgeError(f"RML20_NATIVE_SYMBOL_MISSING:{symbol}")

    library.hhs_exact_uqcel_version.argtypes = []
    library.hhs_exact_uqcel_version.restype = ctypes.c_uint32

    genesis = library.hhs_exact_pass219_vm81_pqc_hash216_genesis_reference
    genesis.argtypes = [ctypes.POINTER(_Hash216Transition)]
    genesis.restype = ctypes.c_int

    descriptor_fn = library.hhs_exact_pass219_rml20_rna_vm5184_descriptor
    descriptor_fn.argtypes = [ctypes.POINTER(_Descriptor)]
    descriptor_fn.restype = ctypes.c_int

    route_fn = library.hhs_exact_pass219_rml20_rna_vm5184_route
    route_fn.argtypes = [
        ctypes.POINTER(_UQCELInput),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(_Hash216Transition),
        ctypes.c_uint32,
        ctypes.c_uint8,
        ctypes.POINTER(_Receipt),
    ]
    route_fn.restype = ctypes.c_int

    descriptor = _Descriptor()
    status = int(descriptor_fn(ctypes.byref(descriptor)))
    if status != HHS_EXACT_STATUS_OK:
        raise RML20NativeBridgeError(f"RML20_DESCRIPTOR_REJECTED:status={status}")

    expected = (
        int(descriptor.lane_count) == DIRECTION_COUNT,
        int(descriptor.operations_per_cell) == OPERATIONS_PER_CELL,
        int(descriptor.phase_count) == PHASE_COUNT,
        int(descriptor.cell_count) == CELL_COUNT,
        int(descriptor.address_count) == ADDRESS_COUNT,
        int(descriptor.direction_count) == DIRECTION_COUNT,
        int(descriptor.vm5184_bytes) == VM5184_BYTES,
        bool(descriptor.cpp_rna_cell_wall),
        bool(descriptor.current_rml17_parity_surface),
        bool(descriptor.direction_embedded_address),
        bool(descriptor.reciprocal_flux_transport),
        bool(descriptor.candidate_only),
        bool(descriptor.exact_integer_only),
        not bool(descriptor.canonical_mutation_authority),
        not bool(descriptor.canonical_hash72_authority),
        not bool(descriptor.canonical_hash216_authority),
        not bool(descriptor.canonical_persistence_authority),
        not bool(descriptor.floating_point_authority),
    )
    if not all(expected):
        raise RML20NativeBridgeError("RML20_NATIVE_DESCRIPTOR_PARITY_FAILURE")
    return library, selected, descriptor


def _minimal_exact_input(library: ctypes.CDLL) -> tuple[_UQCELInput, ctypes.Array[ctypes.c_uint8]]:
    delta_bytes = (ctypes.c_uint8 * 1)(1)
    value = _UQCELInput()
    value.struct_size = ctypes.sizeof(_UQCELInput)
    value.uqcel_version = int(library.hhs_exact_uqcel_version())
    value.profile = INTEGER_SYMMETRIC_PROFILE
    value.delta.struct_size = ctypes.sizeof(_BigUIntView)
    value.delta.byte_length = 1
    value.delta.bytes_be = ctypes.cast(
        delta_bytes, ctypes.POINTER(ctypes.c_uint8)
    )
    return value, delta_bytes


def _genesis_transition(library: ctypes.CDLL) -> _Hash216Transition:
    transition = _Hash216Transition()
    status = int(
        library.hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(
            ctypes.byref(transition)
        )
    )
    if status != HHS_EXACT_STATUS_OK:
        raise RML20NativeBridgeError(
            f"RML20_GENESIS_HASH216_REFERENCE_REJECTED:status={status}"
        )
    return transition


def route_rml17_candidate_through_rna_vm5184(
    raw_frame_le: bytes | bytearray | memoryview,
    source_address: int,
    direction: str,
    *,
    library_path: str | Path | None = None,
) -> dict[str, Any]:
    """Lower one current RML17 directed address through RNA/VM5184."""
    raw = bytes(raw_frame_le)
    if len(raw) != VM5184_BYTES:
        raise RML20NativeBridgeError(
            f"RML20_VM5184_EXACT_648_BYTES_REQUIRED:{len(raw)}"
        )
    if isinstance(source_address, bool) or not isinstance(source_address, int):
        raise RML20NativeBridgeError("RML20_SOURCE_ADDRESS_EXACT_INTEGER_REQUIRED")
    if source_address < 0 or source_address >= ADDRESS_COUNT:
        raise RML20NativeBridgeError("RML20_SOURCE_ADDRESS_OUT_OF_RANGE")
    if direction not in NATIVE_DIRECTION:
        raise RML20NativeBridgeError("RML20_TRANSPORT_DIRECTION_UNSUPPORTED")

    python_source = decode_transport_address(source_address)
    source_direction = python_source[3]
    requested_direction = NATIVE_DIRECTION[direction]
    if requested_direction != source_direction:
        raise RML20NativeBridgeError(
            "RML20_DIRECTION_MUST_MATCH_EMBEDDED_RML17_ADDRESS"
        )

    library, selected, descriptor = _load_library(library_path)
    input_value, delta_keepalive = _minimal_exact_input(library)
    transition = _genesis_transition(library)
    frame = (ctypes.c_uint8 * VM5184_BYTES).from_buffer_copy(raw)
    receipt = _Receipt()

    status = int(
        library.hhs_exact_pass219_rml20_rna_vm5184_route(
            ctypes.byref(input_value),
            frame,
            len(raw),
            ctypes.byref(transition),
            source_address,
            requested_direction,
            ctypes.byref(receipt),
        )
    )
    _ = delta_keepalive
    if status != HHS_EXACT_STATUS_OK:
        raise RML20NativeBridgeError(
            f"RML20_NATIVE_ROUTE_REJECTED:status={status}"
        )

    python_target = transport_neighbor(source_address)
    python_target_coordinates = decode_transport_address(python_target)
    python_forward_flux = signed_address_flux(source_address)
    python_reverse_flux = signed_address_flux(python_target)
    python_divergence = discrete_divergence(source_address)
    inverse_index = reciprocal_direction_index(source_direction)
    inverse_name = INDEX_DIRECTION[inverse_index]

    native_source = (
        int(receipt.source_operation),
        int(receipt.source_phase),
        int(receipt.source_cell),
        int(receipt.source_direction),
    )
    native_target = (
        int(receipt.target_operation),
        int(receipt.target_phase),
        int(receipt.target_cell),
        int(receipt.target_direction),
    )

    parity = {
        "address_encoding_identical": native_source == python_source,
        "neighbor_address_identical": int(receipt.target_address) == python_target,
        "neighbor_coordinates_identical": native_target == python_target_coordinates,
        "embedded_direction_guard_identical": (
            int(receipt.requested_direction) == source_direction
            and int(receipt.source_direction) == source_direction
        ),
        "reciprocal_direction_identical": (
            int(receipt.inverse_direction) == inverse_index
            and int(receipt.target_direction) == inverse_index
        ),
        "flux_orientation_identical": (
            int(receipt.forward_flux) == python_forward_flux
        ),
        "reciprocal_flux_identical": (
            int(receipt.reverse_flux) == python_reverse_flux
        ),
        "zero_divergence_identical": (
            int(receipt.discrete_divergence) == python_divergence == 0
        ),
        "reciprocal_edge_alignment": bool(
            receipt.reciprocal_neighbor_restores_source
        ),
        "zero_diffusion_classification": bool(
            receipt.zero_diffusion_classification
        ),
        "operation_cell_preserved": bool(receipt.operation_cell_preserved),
        "feedback_lane_bound": bool(receipt.feedback_lane_bound),
        "feedback_trinary_bound": bool(receipt.feedback_trinary_bound),
        "rna_cell_wall_routed": bool(receipt.rna_cell_wall_routed),
    }
    if not all(parity.values()):
        failed = sorted(key for key, value in parity.items() if not value)
        raise RML20NativeBridgeError(
            "RML20_PYTHON_NATIVE_TRANSPORT_PARITY_FAILURE:" + ",".join(failed)
        )

    authority = {
        "candidate_only": bool(receipt.candidate_only),
        "exact_integer_only": bool(receipt.exact_integer_only),
        "canonical_vm81_mutation_authority": bool(
            receipt.canonical_mutation_authority
        ),
        "canonical_hash72_mint_authority": bool(
            receipt.canonical_hash72_authority
        ),
        "canonical_hash216_persistence_authority": bool(
            receipt.canonical_hash216_authority
        ),
        "canonical_persistence_authority": bool(
            receipt.canonical_persistence_authority
        ),
        "floating_point_authority": bool(receipt.floating_point_authority),
    }
    if not (
        authority["candidate_only"]
        and authority["exact_integer_only"]
        and not authority["canonical_vm81_mutation_authority"]
        and not authority["canonical_hash72_mint_authority"]
        and not authority["canonical_hash216_persistence_authority"]
        and not authority["canonical_persistence_authority"]
        and not authority["floating_point_authority"]
    ):
        raise RML20NativeBridgeError("RML20_NATIVE_AUTHORITY_BOUNDARY_FAILURE")

    transition_identity = bytes(receipt.transition_identity216).split(
        b"\0", 1
    )[0].decode("ascii")
    return {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "result": "PASS",
        "native_library": str(selected),
        "native_version": int(receipt.version),
        "native_lane_count": int(descriptor.lane_count),
        "current_rml17_direction_count": DIRECTION_COUNT,
        "vm5184_bytes": VM5184_BYTES,
        "source_address": source_address,
        "target_address": int(receipt.target_address),
        "source_coordinates": list(native_source),
        "target_coordinates": list(native_target),
        "direction": direction,
        "inverse_direction": inverse_name,
        "forward_flux": int(receipt.forward_flux),
        "reverse_flux": int(receipt.reverse_flux),
        "discrete_divergence": int(receipt.discrete_divergence),
        "selected_lane": int(receipt.selected_lane),
        "graph_signature64": int(receipt.graph_signature64),
        "tensor_signature64": int(receipt.tensor_signature64),
        "decision_signature64": int(receipt.decision_signature64),
        "transition_identity216": transition_identity,
        "parity": parity,
        "authority": authority,
    }
