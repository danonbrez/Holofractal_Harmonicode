"""ctypes bridge for Pass 219 Lane 5 automatic superedge routing 1.42."""
from __future__ import annotations

import ctypes
from ctypes import POINTER, Structure, c_uint8, c_uint32, c_uint64

from hhs_python.runtime.hhs_pass219_lane5_composition_jump_bridge import signature64_from_hash216
from hhs_python.runtime.hhs_pass219_lane5_persistent_composition_memory_bridge import (
    CYCLE,
    _load_runtime,
    signature64_from_text,
)

VERSION = 0x0001002A
QUARTER = 5_005
DEFAULT_PROMOTION_THRESHOLD = 2
HHS_EXACT_STATUS_OK = 0


class HHSExactPass219Lane5AutomaticRoutingAuthorityV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("full_cycle", c_uint32),
        ("quarter_cycle", c_uint32),
        ("default_promotion_threshold", c_uint32),
        ("cross_level_exact_routing", c_uint8),
        ("automatic_repeated_route_promotion", c_uint8),
        ("durable_exact_observation_ledger", c_uint8),
        ("integer_only_routing_cost", c_uint8),
        ("exact_hash216_adjacency_required", c_uint8),
        ("exact_target_closure_required", c_uint8),
        ("mixed_level_candidate_routing_allowed", c_uint8),
        ("mixed_level_recursive_promotion_allowed", c_uint8),
        ("inherited_gpu_vector_rank_non_authoritative", c_uint8),
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


class HHSExactPass219Lane5AutomaticRouteDescriptorV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("retrieval_count", c_uint32),
        ("base_hops", c_uint32),
        ("represented_span", c_uint32),
        ("max_hierarchy_level", c_uint32),
        ("phase_slot", c_uint32),
        ("layer_index", c_uint32),
        ("cycle_index", c_uint64),
        ("parent_signature64", c_uint64),
        ("goal_signature64", c_uint64),
        ("route_signature64", c_uint64),
        ("ordered_candidate_signature64", c_uint64),
        ("exact_hash216_adjacency", c_uint8),
        ("exact_target_closure", c_uint8),
        ("dependencies_live", c_uint8),
        ("selected_by_integer_cost", c_uint8),
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


class HHSExactPass219Lane5AutomaticRouteReceiptV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("retrieval_count", c_uint32),
        ("base_hops", c_uint32),
        ("represented_span", c_uint32),
        ("max_hierarchy_level", c_uint32),
        ("phase_slot", c_uint32),
        ("layer_index", c_uint32),
        ("cycle_index", c_uint64),
        ("descriptor_signature64", c_uint64),
        ("route_receipt_signature64", c_uint64),
        ("accepted", c_uint8),
        ("exact_hash216_adjacency", c_uint8),
        ("exact_target_closure", c_uint8),
        ("dependencies_live", c_uint8),
        ("selected_by_integer_cost", c_uint8),
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


class Pass219Lane5AutomaticSuperedgeRoutingBridge:
    def __init__(self) -> None:
        self.lib = _load_runtime()
        self.lib.hhs_exact_pass219_lane5_automatic_superedge_routing_version.argtypes = []
        self.lib.hhs_exact_pass219_lane5_automatic_superedge_routing_version.restype = c_uint32
        self.lib.hhs_exact_pass219_lane5_automatic_superedge_routing_authority.argtypes = [
            POINTER(HHSExactPass219Lane5AutomaticRoutingAuthorityV1)
        ]
        self.lib.hhs_exact_pass219_lane5_automatic_superedge_routing_authority.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_automatic_route_validate.argtypes = [
            POINTER(HHSExactPass219Lane5AutomaticRouteDescriptorV1),
            POINTER(HHSExactPass219Lane5AutomaticRouteReceiptV1),
        ]
        self.lib.hhs_exact_pass219_lane5_automatic_route_validate.restype = ctypes.c_int

    def version(self) -> int:
        return int(self.lib.hhs_exact_pass219_lane5_automatic_superedge_routing_version())

    def authority(self) -> dict[str, int]:
        value = HHSExactPass219Lane5AutomaticRoutingAuthorityV1()
        status = self.lib.hhs_exact_pass219_lane5_automatic_superedge_routing_authority(
            ctypes.byref(value)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Lane 5 automatic routing authority failed: {status}")
        return {name: int(getattr(value, name)) for name, _ in value._fields_}

    def validate_plan(
        self,
        *,
        retrieval_count: int,
        base_hops: int,
        represented_span: int,
        max_hierarchy_level: int,
        phase_slot: int,
        layer_index: int,
        cycle_index: int,
        parent_hash216: str,
        goal_hash216: str,
        route_hash216: str,
        ordered_candidate_identity: str,
    ) -> dict[str, int | bool]:
        for value in (
            retrieval_count,
            base_hops,
            represented_span,
            max_hierarchy_level,
            phase_slot,
            layer_index,
            cycle_index,
        ):
            if int(value) < 0:
                raise ValueError("automatic routing coordinates must be nonnegative")
        descriptor = HHSExactPass219Lane5AutomaticRouteDescriptorV1()
        descriptor.struct_size = ctypes.sizeof(descriptor)
        descriptor.version = VERSION
        descriptor.retrieval_count = int(retrieval_count)
        descriptor.base_hops = int(base_hops)
        descriptor.represented_span = int(represented_span)
        descriptor.max_hierarchy_level = int(max_hierarchy_level)
        descriptor.phase_slot = int(phase_slot)
        descriptor.layer_index = int(layer_index)
        descriptor.cycle_index = int(cycle_index)
        descriptor.parent_signature64 = signature64_from_hash216(parent_hash216)
        descriptor.goal_signature64 = signature64_from_hash216(goal_hash216)
        descriptor.route_signature64 = signature64_from_hash216(route_hash216)
        descriptor.ordered_candidate_signature64 = signature64_from_text(ordered_candidate_identity)
        descriptor.exact_hash216_adjacency = 1
        descriptor.exact_target_closure = 1
        descriptor.dependencies_live = 1
        descriptor.selected_by_integer_cost = 1
        descriptor.candidate_only = 1
        descriptor.requires_signed_environmental_vm81_admission = 1
        receipt = HHSExactPass219Lane5AutomaticRouteReceiptV1()
        status = self.lib.hhs_exact_pass219_lane5_automatic_route_validate(
            ctypes.byref(descriptor), ctypes.byref(receipt)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError(f"Lane 5 automatic routing rejected: status={status}")
        return {
            "retrieval_count": int(receipt.retrieval_count),
            "base_hops": int(receipt.base_hops),
            "represented_span": int(receipt.represented_span),
            "max_hierarchy_level": int(receipt.max_hierarchy_level),
            "phase_slot": int(receipt.phase_slot),
            "layer_index": int(receipt.layer_index),
            "cycle_index": int(receipt.cycle_index),
            "descriptor_signature64": int(receipt.descriptor_signature64),
            "route_receipt_signature64": int(receipt.route_receipt_signature64),
            "accepted": bool(receipt.accepted),
            "exact_hash216_adjacency": bool(receipt.exact_hash216_adjacency),
            "exact_target_closure": bool(receipt.exact_target_closure),
            "dependencies_live": bool(receipt.dependencies_live),
            "selected_by_integer_cost": bool(receipt.selected_by_integer_cost),
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
    "CYCLE",
    "QUARTER",
    "VERSION",
    "DEFAULT_PROMOTION_THRESHOLD",
    "Pass219Lane5AutomaticSuperedgeRoutingBridge",
]
