"""ctypes bridge for the subordinate Pass 219 RML17 transport ABI.

This module exposes native conservation geometry to the Python RML17 witness.
It has no transition, VM81 mutation, Hash72 mint, or Hash216 persistence API.
"""
from __future__ import annotations

import ctypes
from pathlib import Path
from typing import Iterator


class NativeTransportConservationError(RuntimeError):
    pass


class NativeTransportAddress(ctypes.Structure):
    _fields_ = [
        ("operation64", ctypes.c_uint8),
        ("phase72", ctypes.c_uint8),
        ("cell81", ctypes.c_uint8),
        ("direction4", ctypes.c_uint8),
    ]


class NativeTransportParityRow(ctypes.Structure):
    _fields_ = [
        ("source_index", ctypes.c_uint64),
        ("target_index", ctypes.c_uint64),
        ("source", NativeTransportAddress),
        ("target", NativeTransportAddress),
        ("source_flux", ctypes.c_int8),
        ("reciprocal_direction4", ctypes.c_uint8),
        ("zero_canonical_diffusion", ctypes.c_uint8),
        ("exact_reverse_restores_source", ctypes.c_uint8),
    ]


class NativeTransportReport(ctypes.Structure):
    _fields_ = [
        ("node_count", ctypes.c_uint64),
        ("address_count", ctypes.c_uint64),
        ("discrete_divergence_nodes_checked", ctypes.c_uint64),
        ("reciprocal_edge_addresses_checked", ctypes.c_uint64),
        ("admission_preservation_addresses_checked", ctypes.c_uint64),
        ("zero_diffusion_addresses_checked", ctypes.c_uint64),
        ("composed_reverse_addresses_checked", ctypes.c_uint64),
        ("unique_target_addresses", ctypes.c_uint64),
        ("failure_count", ctypes.c_uint64),
        ("discrete_divergence_gate", ctypes.c_uint8),
        ("reciprocal_edge_balance_gate", ctypes.c_uint8),
        ("admission_preservation_gate", ctypes.c_uint8),
        ("zero_canonical_diffusion_gate", ctypes.c_uint8),
        ("composed_reverse_closure_gate", ctypes.c_uint8),
        ("exhaustive_address_coverage", ctypes.c_uint8),
        ("target_map_bijective", ctypes.c_uint8),
        ("exact_integer_phase_arithmetic", ctypes.c_uint8),
        ("canonical_transition_authority", ctypes.c_uint8),
        ("canonical_vm81_mutation_authority", ctypes.c_uint8),
        ("canonical_hash72_mint_authority", ctypes.c_uint8),
        ("canonical_hash216_persistence_authority", ctypes.c_uint8),
        ("pass_", ctypes.c_uint8),
    ]


def default_library_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    return (
        root
        / "native_projects"
        / "hhs_pass219_discrete_transport_conservation"
        / "build"
        / "libhhs_pass219_rml17_transport_abi.so"
    )


def _bind(library_path: str | Path | None = None) -> ctypes.CDLL:
    path = Path(library_path) if library_path is not None else default_library_path()
    if not path.is_file():
        raise NativeTransportConservationError(
            f"RML17_NATIVE_TRANSPORT_ABI_NOT_FOUND:{path}"
        )
    library = ctypes.CDLL(str(path))

    library.hhs_pass219_rml17_transport_abi_version.argtypes = []
    library.hhs_pass219_rml17_transport_abi_version.restype = ctypes.c_uint32
    library.hhs_pass219_rml17_transport_node_count.argtypes = []
    library.hhs_pass219_rml17_transport_node_count.restype = ctypes.c_uint64
    library.hhs_pass219_rml17_transport_address_count.argtypes = []
    library.hhs_pass219_rml17_transport_address_count.restype = ctypes.c_uint64

    library.hhs_pass219_rml17_transport_flatten.argtypes = [
        ctypes.POINTER(NativeTransportAddress),
        ctypes.POINTER(ctypes.c_uint64),
    ]
    library.hhs_pass219_rml17_transport_flatten.restype = ctypes.c_int
    library.hhs_pass219_rml17_transport_unflatten.argtypes = [
        ctypes.c_uint64,
        ctypes.POINTER(NativeTransportAddress),
    ]
    library.hhs_pass219_rml17_transport_unflatten.restype = ctypes.c_int
    library.hhs_pass219_rml17_transport_signed_flux.argtypes = [
        ctypes.c_uint8,
        ctypes.POINTER(ctypes.c_int8),
    ]
    library.hhs_pass219_rml17_transport_signed_flux.restype = ctypes.c_int
    library.hhs_pass219_rml17_transport_reciprocal.argtypes = [
        ctypes.c_uint8,
        ctypes.POINTER(ctypes.c_uint8),
    ]
    library.hhs_pass219_rml17_transport_reciprocal.restype = ctypes.c_int
    library.hhs_pass219_rml17_transport_successor.argtypes = [
        ctypes.POINTER(NativeTransportAddress),
        ctypes.POINTER(NativeTransportAddress),
    ]
    library.hhs_pass219_rml17_transport_successor.restype = ctypes.c_int
    library.hhs_pass219_rml17_transport_zero_diffusion.argtypes = [
        ctypes.POINTER(NativeTransportAddress),
        ctypes.POINTER(ctypes.c_uint8),
    ]
    library.hhs_pass219_rml17_transport_zero_diffusion.restype = ctypes.c_int
    library.hhs_pass219_rml17_transport_export_parity_rows.argtypes = [
        ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.POINTER(NativeTransportParityRow),
    ]
    library.hhs_pass219_rml17_transport_export_parity_rows.restype = ctypes.c_int
    library.hhs_pass219_rml17_transport_audit.argtypes = [
        ctypes.POINTER(NativeTransportReport)
    ]
    library.hhs_pass219_rml17_transport_audit.restype = ctypes.c_int
    library.hhs_pass219_rml17_transport_has_transition_authority.argtypes = []
    library.hhs_pass219_rml17_transport_has_transition_authority.restype = ctypes.c_int
    return library


def native_contract_report(library_path: str | Path | None = None) -> dict[str, int | bool]:
    library = _bind(library_path)
    report = NativeTransportReport()
    if library.hhs_pass219_rml17_transport_audit(ctypes.byref(report)) != 1:
        raise NativeTransportConservationError("RML17_NATIVE_TRANSPORT_AUDIT_FAILED")
    return {
        "abi_version": int(library.hhs_pass219_rml17_transport_abi_version()),
        "node_count": int(report.node_count),
        "address_count": int(report.address_count),
        "discrete_divergence_nodes_checked": int(report.discrete_divergence_nodes_checked),
        "reciprocal_edge_addresses_checked": int(report.reciprocal_edge_addresses_checked),
        "admission_preservation_addresses_checked": int(report.admission_preservation_addresses_checked),
        "zero_diffusion_addresses_checked": int(report.zero_diffusion_addresses_checked),
        "composed_reverse_addresses_checked": int(report.composed_reverse_addresses_checked),
        "unique_target_addresses": int(report.unique_target_addresses),
        "failure_count": int(report.failure_count),
        "discrete_divergence_gate": bool(report.discrete_divergence_gate),
        "reciprocal_edge_balance_gate": bool(report.reciprocal_edge_balance_gate),
        "admission_preservation_gate": bool(report.admission_preservation_gate),
        "zero_canonical_diffusion_gate": bool(report.zero_canonical_diffusion_gate),
        "composed_reverse_closure_gate": bool(report.composed_reverse_closure_gate),
        "exhaustive_address_coverage": bool(report.exhaustive_address_coverage),
        "target_map_bijective": bool(report.target_map_bijective),
        "exact_integer_phase_arithmetic": bool(report.exact_integer_phase_arithmetic),
        "canonical_transition_authority": bool(report.canonical_transition_authority),
        "canonical_vm81_mutation_authority": bool(report.canonical_vm81_mutation_authority),
        "canonical_hash72_mint_authority": bool(report.canonical_hash72_mint_authority),
        "canonical_hash216_persistence_authority": bool(report.canonical_hash216_persistence_authority),
        "pass": bool(report.pass_),
        "abi_has_transition_authority": bool(
            library.hhs_pass219_rml17_transport_has_transition_authority()
        ),
    }


def iter_native_parity_rows(
    *,
    library_path: str | Path | None = None,
    chunk_size: int = 4096,
) -> Iterator[NativeTransportParityRow]:
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size <= 0:
        raise NativeTransportConservationError("RML17_NATIVE_PARITY_CHUNK_SIZE_INVALID")
    library = _bind(library_path)
    address_count = int(library.hhs_pass219_rml17_transport_address_count())
    row_array_type = NativeTransportParityRow * chunk_size
    for start in range(0, address_count, chunk_size):
        count = min(chunk_size, address_count - start)
        rows = row_array_type()
        if library.hhs_pass219_rml17_transport_export_parity_rows(
            start, count, rows
        ) != 1:
            raise NativeTransportConservationError(
                f"RML17_NATIVE_PARITY_EXPORT_FAILED:{start}:{count}"
            )
        for offset in range(count):
            yield rows[offset]


__all__ = [
    "NativeTransportAddress",
    "NativeTransportConservationError",
    "NativeTransportParityRow",
    "NativeTransportReport",
    "default_library_path",
    "iter_native_parity_rows",
    "native_contract_report",
]
