"""ctypes bridge for Pass 219 Lane 5 recursive Hash216 composition graph 1.40."""
from __future__ import annotations

import ctypes
from ctypes import POINTER, Structure, c_uint8, c_uint32, c_uint64

from hhs_python.runtime.hhs_pass219_lane5_composition_jump_bridge import (
    signature64_from_hash216,
)
from hhs_python.runtime.hhs_pass219_lane5_persistent_composition_memory_bridge import (
    CYCLE,
    _load_runtime,
    signature64_from_text,
)

VERSION = 0x00010028
QUARTER = 5_005
HHS_EXACT_STATUS_OK = 0


class HHSExactPass219Lane5RecursiveCompositionGraphAuthorityV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("full_cycle", c_uint32),
        ("quarter_cycle", c_uint32),
        ("persistent_composition_graph", c_uint8),
        ("recursive_multi_hop_search", c_uint8),
        ("hash216_path_seal_required", c_uint8),
        ("exact_hash216_adjacency_required", c_uint8),
        ("persistent_edge_authentication_required", c_uint8),
        ("inherited_gpu_vector_rank_required", c_uint8),
        ("prime_phase_cycle_bound", c_uint8),
        ("no_vertex_revisit_required", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_vm81_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("floating_point_canonical_authority", c_uint8),
    ]


class HHSExactPass219Lane5RecursiveCompositionGraphDescriptorV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("hop_count", c_uint32),
        ("total_span", c_uint32),
        ("phase_slot", c_uint32),
        ("reserved_phase", c_uint32),
        ("cycle_index", c_uint64),
        ("start_signature64", c_uint64),
        ("goal_signature64", c_uint64),
        ("terminal_signature64", c_uint64),
        ("path_signature64", c_uint64),
        ("ordered_lineage_signature64", c_uint64),
        ("exact_adjacency", c_uint8),
        ("persistent_edges_authenticated", c_uint8),
        ("path_sealed", c_uint8),
        ("no_vertex_revisit", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved0", c_uint8 * 4),
    ]


class HHSExactPass219Lane5RecursiveCompositionGraphReceiptV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("hop_count", c_uint32),
        ("total_span", c_uint32),
        ("phase_slot", c_uint32),
        ("reserved_phase", c_uint32),
        ("cycle_index", c_uint64),
        ("descriptor_signature64", c_uint64),
        ("graph_route_signature64", c_uint64),
        ("accepted", c_uint8),
        ("exact_adjacency", c_uint8),
        ("persistent_edges_authenticated", c_uint8),
        ("path_sealed", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved0", c_uint8 * 4),
    ]


class Pass219Lane5RecursiveCompositionGraphBridge:
    def __init__(self) -> None:
        self.lib = _load_runtime()
        self.lib.hhs_exact_pass219_lane5_recursive_composition_graph_version.argtypes = []
        self.lib.hhs_exact_pass219_lane5_recursive_composition_graph_version.restype = c_uint32
        self.lib.hhs_exact_pass219_lane5_recursive_composition_graph_authority.argtypes = [
            POINTER(HHSExactPass219Lane5RecursiveCompositionGraphAuthorityV1)
        ]
        self.lib.hhs_exact_pass219_lane5_recursive_composition_graph_authority.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_recursive_composition_graph_validate.argtypes = [
            POINTER(HHSExactPass219Lane5RecursiveCompositionGraphDescriptorV1),
            POINTER(HHSExactPass219Lane5RecursiveCompositionGraphReceiptV1),
        ]
        self.lib.hhs_exact_pass219_lane5_recursive_composition_graph_validate.restype = ctypes.c_int

    def version(self) -> int:
        return int(self.lib.hhs_exact_pass219_lane5_recursive_composition_graph_version())

    def authority(self) -> dict[str, int]:
        value = HHSExactPass219Lane5RecursiveCompositionGraphAuthorityV1()
        status = self.lib.hhs_exact_pass219_lane5_recursive_composition_graph_authority(
            ctypes.byref(value)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Lane 5 recursive composition graph authority failed: {status}")
        return {name: int(getattr(value, name)) for name, _ in value._fields_}

    def validate_path(
        self,
        *,
        start_hash216: str,
        goal_hash216: str,
        terminal_hash216: str,
        path_hash216: str,
        ordered_lineage_identity: str,
        hop_count: int,
        total_span: int,
        phase_slot: int,
        cycle_index: int,
    ) -> dict[str, int | bool]:
        for value in (hop_count, total_span, phase_slot, cycle_index):
            if int(value) < 0:
                raise ValueError("recursive composition graph coordinates must be nonnegative")
        descriptor = HHSExactPass219Lane5RecursiveCompositionGraphDescriptorV1()
        descriptor.struct_size = ctypes.sizeof(descriptor)
        descriptor.version = VERSION
        descriptor.hop_count = int(hop_count)
        descriptor.total_span = int(total_span)
        descriptor.phase_slot = int(phase_slot)
        descriptor.cycle_index = int(cycle_index)
        descriptor.start_signature64 = signature64_from_hash216(start_hash216)
        descriptor.goal_signature64 = signature64_from_hash216(goal_hash216)
        descriptor.terminal_signature64 = signature64_from_hash216(terminal_hash216)
        descriptor.path_signature64 = signature64_from_hash216(path_hash216)
        descriptor.ordered_lineage_signature64 = signature64_from_text(ordered_lineage_identity)
        descriptor.exact_adjacency = 1
        descriptor.persistent_edges_authenticated = 1
        descriptor.path_sealed = 1
        descriptor.no_vertex_revisit = 1
        descriptor.candidate_only = 1
        descriptor.requires_signed_environmental_vm81_admission = 1
        receipt = HHSExactPass219Lane5RecursiveCompositionGraphReceiptV1()
        status = self.lib.hhs_exact_pass219_lane5_recursive_composition_graph_validate(
            ctypes.byref(descriptor), ctypes.byref(receipt)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError(f"Lane 5 recursive composition graph rejected: status={status}")
        return {
            "hop_count": int(receipt.hop_count),
            "total_span": int(receipt.total_span),
            "phase_slot": int(receipt.phase_slot),
            "cycle_index": int(receipt.cycle_index),
            "descriptor_signature64": int(receipt.descriptor_signature64),
            "graph_route_signature64": int(receipt.graph_route_signature64),
            "accepted": bool(receipt.accepted),
            "exact_adjacency": bool(receipt.exact_adjacency),
            "persistent_edges_authenticated": bool(receipt.persistent_edges_authenticated),
            "path_sealed": bool(receipt.path_sealed),
            "candidate_only": bool(receipt.candidate_only),
            "canonical_mutation_authority": bool(receipt.canonical_mutation_authority),
            "canonical_hash72_authority": bool(receipt.canonical_hash72_authority),
            "canonical_hash216_authority": bool(receipt.canonical_hash216_authority),
            "canonical_persistence_authority": bool(receipt.canonical_persistence_authority),
            "pqc_key_authority": bool(receipt.pqc_key_authority),
            "receipt_clock_authority": bool(receipt.receipt_clock_authority),
            "requires_signed_environmental_vm81_admission": bool(
                receipt.requires_signed_environmental_vm81_admission
            ),
        }


__all__ = [
    "CYCLE", "QUARTER", "VERSION",
    "Pass219Lane5RecursiveCompositionGraphBridge",
]
