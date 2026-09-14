"""ctypes bridge for Pass 219 Lane 5 superedge hierarchy 1.41."""
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

VERSION = 0x00010029
QUARTER = 5_005
HHS_EXACT_STATUS_OK = 0


class HHSExactPass219Lane5SuperedgeHierarchyAuthorityV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("full_cycle", c_uint32),
        ("quarter_cycle", c_uint32),
        ("recursive_superedge_hierarchy", c_uint8),
        ("restart_rehydratable_superedges", c_uint8),
        ("one_snapshot_direct_reuse", c_uint8),
        ("transitive_flattened_provenance_required", c_uint8),
        ("hash216_hierarchy_seal_required", c_uint8),
        ("exact_component_adjacency_required", c_uint8),
        ("leaf_quarantine_propagation_required", c_uint8),
        ("inherited_gpu_vector_rank_allowed", c_uint8),
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


class HHSExactPass219Lane5SuperedgeDescriptorV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("hierarchy_level", c_uint32),
        ("direct_component_count", c_uint32),
        ("base_hops", c_uint32),
        ("total_span", c_uint32),
        ("phase_slot", c_uint32),
        ("layer_index", c_uint32),
        ("cycle_index", c_uint64),
        ("parent_signature64", c_uint64),
        ("child_signature64", c_uint64),
        ("route_signature64", c_uint64),
        ("hierarchy_signature64", c_uint64),
        ("metadata_signature64", c_uint64),
        ("component_lineage_signature64", c_uint64),
        ("flattened_leaf_signature64", c_uint64),
        ("exact_component_adjacency", c_uint8),
        ("lower_level_replay_authenticated", c_uint8),
        ("terminal_snapshot_encrypted", c_uint8),
        ("hierarchy_sealed", c_uint8),
        ("leaf_dependencies_live", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved0", c_uint8 * 3),
    ]


class HHSExactPass219Lane5SuperedgeReceiptV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("hierarchy_level", c_uint32),
        ("direct_component_count", c_uint32),
        ("base_hops", c_uint32),
        ("total_span", c_uint32),
        ("phase_slot", c_uint32),
        ("layer_index", c_uint32),
        ("cycle_index", c_uint64),
        ("descriptor_signature64", c_uint64),
        ("hierarchy_receipt_signature64", c_uint64),
        ("accepted", c_uint8),
        ("exact_component_adjacency", c_uint8),
        ("lower_level_replay_authenticated", c_uint8),
        ("terminal_snapshot_encrypted", c_uint8),
        ("hierarchy_sealed", c_uint8),
        ("leaf_dependencies_live", c_uint8),
        ("one_snapshot_direct_reuse", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved0", c_uint8),
    ]


class Pass219Lane5SuperedgeHierarchyBridge:
    def __init__(self) -> None:
        self.lib = _load_runtime()
        self.lib.hhs_exact_pass219_lane5_superedge_hierarchy_version.argtypes = []
        self.lib.hhs_exact_pass219_lane5_superedge_hierarchy_version.restype = c_uint32
        self.lib.hhs_exact_pass219_lane5_superedge_hierarchy_authority.argtypes = [
            POINTER(HHSExactPass219Lane5SuperedgeHierarchyAuthorityV1)
        ]
        self.lib.hhs_exact_pass219_lane5_superedge_hierarchy_authority.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_superedge_validate.argtypes = [
            POINTER(HHSExactPass219Lane5SuperedgeDescriptorV1),
            POINTER(HHSExactPass219Lane5SuperedgeReceiptV1),
        ]
        self.lib.hhs_exact_pass219_lane5_superedge_validate.restype = ctypes.c_int

    def version(self) -> int:
        return int(self.lib.hhs_exact_pass219_lane5_superedge_hierarchy_version())

    def authority(self) -> dict[str, int]:
        value = HHSExactPass219Lane5SuperedgeHierarchyAuthorityV1()
        status = self.lib.hhs_exact_pass219_lane5_superedge_hierarchy_authority(
            ctypes.byref(value)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Lane 5 superedge hierarchy authority failed: {status}")
        return {name: int(getattr(value, name)) for name, _ in value._fields_}

    def validate(
        self,
        *,
        hierarchy_level: int,
        direct_component_count: int,
        base_hops: int,
        total_span: int,
        phase_slot: int,
        layer_index: int,
        cycle_index: int,
        parent_hash216: str,
        child_hash216: str,
        route_hash216: str,
        hierarchy_hash216: str,
        metadata_hash216: str,
        component_lineage_identity: str,
        flattened_leaf_identity: str,
    ) -> dict[str, int | bool]:
        for value in (
            hierarchy_level,
            direct_component_count,
            base_hops,
            total_span,
            phase_slot,
            layer_index,
            cycle_index,
        ):
            if int(value) < 0:
                raise ValueError("superedge coordinates must be nonnegative")
        descriptor = HHSExactPass219Lane5SuperedgeDescriptorV1()
        descriptor.struct_size = ctypes.sizeof(descriptor)
        descriptor.version = VERSION
        descriptor.hierarchy_level = int(hierarchy_level)
        descriptor.direct_component_count = int(direct_component_count)
        descriptor.base_hops = int(base_hops)
        descriptor.total_span = int(total_span)
        descriptor.phase_slot = int(phase_slot)
        descriptor.layer_index = int(layer_index)
        descriptor.cycle_index = int(cycle_index)
        descriptor.parent_signature64 = signature64_from_hash216(parent_hash216)
        descriptor.child_signature64 = signature64_from_hash216(child_hash216)
        descriptor.route_signature64 = signature64_from_hash216(route_hash216)
        descriptor.hierarchy_signature64 = signature64_from_hash216(hierarchy_hash216)
        descriptor.metadata_signature64 = signature64_from_hash216(metadata_hash216)
        descriptor.component_lineage_signature64 = signature64_from_text(component_lineage_identity)
        descriptor.flattened_leaf_signature64 = signature64_from_text(flattened_leaf_identity)
        descriptor.exact_component_adjacency = 1
        descriptor.lower_level_replay_authenticated = 1
        descriptor.terminal_snapshot_encrypted = 1
        descriptor.hierarchy_sealed = 1
        descriptor.leaf_dependencies_live = 1
        descriptor.candidate_only = 1
        descriptor.requires_signed_environmental_vm81_admission = 1
        receipt = HHSExactPass219Lane5SuperedgeReceiptV1()
        status = self.lib.hhs_exact_pass219_lane5_superedge_validate(
            ctypes.byref(descriptor), ctypes.byref(receipt)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError(f"Lane 5 superedge hierarchy rejected: status={status}")
        return {
            "hierarchy_level": int(receipt.hierarchy_level),
            "direct_component_count": int(receipt.direct_component_count),
            "base_hops": int(receipt.base_hops),
            "total_span": int(receipt.total_span),
            "phase_slot": int(receipt.phase_slot),
            "layer_index": int(receipt.layer_index),
            "cycle_index": int(receipt.cycle_index),
            "descriptor_signature64": int(receipt.descriptor_signature64),
            "hierarchy_receipt_signature64": int(receipt.hierarchy_receipt_signature64),
            "accepted": bool(receipt.accepted),
            "exact_component_adjacency": bool(receipt.exact_component_adjacency),
            "lower_level_replay_authenticated": bool(receipt.lower_level_replay_authenticated),
            "terminal_snapshot_encrypted": bool(receipt.terminal_snapshot_encrypted),
            "hierarchy_sealed": bool(receipt.hierarchy_sealed),
            "leaf_dependencies_live": bool(receipt.leaf_dependencies_live),
            "one_snapshot_direct_reuse": bool(receipt.one_snapshot_direct_reuse),
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


__all__ = ["CYCLE", "QUARTER", "VERSION", "Pass219Lane5SuperedgeHierarchyBridge"]
