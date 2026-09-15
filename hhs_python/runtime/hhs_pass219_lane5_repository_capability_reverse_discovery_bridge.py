"""ctypes bridge for Pass 219 Lane 5 repository capability reverse discovery 1.44."""
from __future__ import annotations

import ctypes
from ctypes import POINTER, Structure, c_uint8, c_uint32, c_uint64
from typing import Iterable

from hhs_python.runtime.hhs_pass219_lane5_persistent_composition_memory_bridge import (
    _load_runtime,
    signature64_from_text,
)

VERSION = 0x0001002C
NAMESPACE = 0x0002192C
MAX_ENTRIES = 4096
HHS_EXACT_STATUS_OK = 0

SOURCE_PUBLIC_REGISTRY = 1
SOURCE_NATIVE_EXACT_ABI = 2
SOURCE_PYTHON_OPERATION_REGISTRY = 3

AUTH_OBSERVATION = 1
AUTH_GOVERNED_TRANSFORM = 2
AUTH_CANONICAL_ADMISSION_BOUNDARY = 3
AUTH_RESTRICTED_OR_UNAVAILABLE = 4


class HHSExactPass219Lane5RepositoryCapabilityAuthorityV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("namespace_id", c_uint32),
        ("max_entries", c_uint32),
        ("global_capability_discovery", c_uint8),
        ("public_registry_snapshot", c_uint8),
        ("native_exact_abi_snapshot", c_uint8),
        ("python_operation_registry_snapshot", c_uint8),
        ("structural_registry_keys_only", c_uint8),
        ("ordered_identity", c_uint8),
        ("dependency_topology", c_uint8),
        ("authority_classification", c_uint8),
        ("deterministic_replay", c_uint8),
        ("canonical_boundary_singleton", c_uint8),
        ("candidate_only", c_uint8),
        ("exact_integer_only", c_uint8),
        ("auto_hash216_composition_promotion", c_uint8),
        ("auto_superedge_promotion", c_uint8),
        ("canonical_vm81_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("floating_point_canonical_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
        ("reserved0", c_uint8 * 2),
    ]


class HHSExactPass219Lane5RepositoryCapabilityDescriptorV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("namespace_id", c_uint32),
        ("total_entries", c_uint32),
        ("public_entries", c_uint32),
        ("native_entries", c_uint32),
        ("python_registry_entries", c_uint32),
        ("restricted_entries", c_uint32),
        ("canonical_boundary_entries", c_uint32),
        ("public_catalog_signature64", c_uint64),
        ("native_export_signature64", c_uint64),
        ("python_registry_signature64", c_uint64),
        ("dependency_signature64", c_uint64),
        ("model_signature64", c_uint64),
        ("canonical_boundary_signature64", c_uint64),
        ("entry_signature64", c_uint64 * MAX_ENTRIES),
        ("source_kind", c_uint8 * MAX_ENTRIES),
        ("authority_class", c_uint8 * MAX_ENTRIES),
        ("public_registry_complete", c_uint8),
        ("native_exact_abi_complete", c_uint8),
        ("python_operation_registry_complete", c_uint8),
        ("structural_registry_keys_only", c_uint8),
        ("ordered_unique_identity", c_uint8),
        ("candidate_only", c_uint8),
        ("auto_hash216_composition_promotion", c_uint8),
        ("auto_superedge_promotion", c_uint8),
        ("canonical_vm81_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("floating_point_canonical_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
    ]


class HHSExactPass219Lane5RepositoryCapabilityReceiptV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("namespace_id", c_uint32),
        ("total_entries", c_uint32),
        ("public_entries", c_uint32),
        ("native_entries", c_uint32),
        ("python_registry_entries", c_uint32),
        ("restricted_entries", c_uint32),
        ("canonical_boundary_entries", c_uint32),
        ("public_catalog_signature64", c_uint64),
        ("native_export_signature64", c_uint64),
        ("python_registry_signature64", c_uint64),
        ("dependency_signature64", c_uint64),
        ("model_signature64", c_uint64),
        ("canonical_boundary_signature64", c_uint64),
        ("descriptor_signature64", c_uint64),
        ("receipt_signature64", c_uint64),
        ("accepted", c_uint8),
        ("public_registry_complete", c_uint8),
        ("native_exact_abi_complete", c_uint8),
        ("python_operation_registry_complete", c_uint8),
        ("structural_registry_keys_only", c_uint8),
        ("ordered_unique_identity", c_uint8),
        ("candidate_only", c_uint8),
        ("auto_hash216_composition_promotion", c_uint8),
        ("auto_superedge_promotion", c_uint8),
        ("canonical_vm81_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("pqc_key_authority", c_uint8),
        ("receipt_clock_authority", c_uint8),
        ("requires_signed_environmental_vm81_admission", c_uint8),
    ]


class Pass219Lane5RepositoryCapabilityReverseDiscoveryBridge:
    def __init__(self) -> None:
        self.lib = _load_runtime()
        self.lib.hhs_exact_pass219_lane5_repository_capability_reverse_discovery_version.argtypes = []
        self.lib.hhs_exact_pass219_lane5_repository_capability_reverse_discovery_version.restype = c_uint32
        self.lib.hhs_exact_pass219_lane5_repository_capability_reverse_discovery_authority.argtypes = [
            POINTER(HHSExactPass219Lane5RepositoryCapabilityAuthorityV1)
        ]
        self.lib.hhs_exact_pass219_lane5_repository_capability_reverse_discovery_authority.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_repository_capability_reverse_discovery_validate.argtypes = [
            POINTER(HHSExactPass219Lane5RepositoryCapabilityDescriptorV1),
            POINTER(HHSExactPass219Lane5RepositoryCapabilityReceiptV1),
        ]
        self.lib.hhs_exact_pass219_lane5_repository_capability_reverse_discovery_validate.restype = ctypes.c_int

    def version(self) -> int:
        return int(self.lib.hhs_exact_pass219_lane5_repository_capability_reverse_discovery_version())

    def authority(self) -> dict[str, int]:
        value = HHSExactPass219Lane5RepositoryCapabilityAuthorityV1()
        status = self.lib.hhs_exact_pass219_lane5_repository_capability_reverse_discovery_authority(
            ctypes.byref(value)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Lane 5 repository capability authority failed: {status}")
        return {
            name: int(getattr(value, name))
            for name, _ in value._fields_
            if not name.startswith("reserved")
        }

    def validate_snapshot(
        self,
        *,
        entries: Iterable[tuple[int, int, int]],
        public_catalog_root: str,
        native_export_root: str,
        python_registry_root: str,
        dependency_root: str,
        model_root: str,
        canonical_boundary_signature64: int,
    ) -> dict[str, int | bool]:
        normalized = sorted(
            (int(sig), int(source), int(authority))
            for sig, source, authority in entries
        )
        if not normalized or len(normalized) > MAX_ENTRIES:
            raise ValueError("repository capability entry count is outside the native bound")
        if any(sig <= 0 for sig, _, _ in normalized):
            raise ValueError("repository capability entry signatures must be nonzero")
        signatures = [item[0] for item in normalized]
        if len(signatures) != len(set(signatures)):
            raise ValueError("repository capability entry signatures must be unique")

        descriptor = HHSExactPass219Lane5RepositoryCapabilityDescriptorV1()
        descriptor.struct_size = ctypes.sizeof(descriptor)
        descriptor.version = VERSION
        descriptor.namespace_id = NAMESPACE
        descriptor.total_entries = len(normalized)
        descriptor.public_entries = sum(
            1 for _, source, _ in normalized if source == SOURCE_PUBLIC_REGISTRY
        )
        descriptor.native_entries = sum(
            1 for _, source, _ in normalized if source == SOURCE_NATIVE_EXACT_ABI
        )
        descriptor.python_registry_entries = sum(
            1 for _, source, _ in normalized if source == SOURCE_PYTHON_OPERATION_REGISTRY
        )
        descriptor.restricted_entries = sum(
            1 for _, _, authority in normalized if authority == AUTH_RESTRICTED_OR_UNAVAILABLE
        )
        descriptor.canonical_boundary_entries = sum(
            1 for _, _, authority in normalized if authority == AUTH_CANONICAL_ADMISSION_BOUNDARY
        )
        descriptor.public_catalog_signature64 = signature64_from_text(public_catalog_root)
        descriptor.native_export_signature64 = signature64_from_text(native_export_root)
        descriptor.python_registry_signature64 = signature64_from_text(python_registry_root)
        descriptor.dependency_signature64 = signature64_from_text(dependency_root)
        descriptor.model_signature64 = signature64_from_text(model_root)
        descriptor.canonical_boundary_signature64 = int(canonical_boundary_signature64)
        for i, (signature, source, authority) in enumerate(normalized):
            descriptor.entry_signature64[i] = signature
            descriptor.source_kind[i] = source
            descriptor.authority_class[i] = authority
        descriptor.public_registry_complete = 1
        descriptor.native_exact_abi_complete = 1
        descriptor.python_operation_registry_complete = 1
        descriptor.structural_registry_keys_only = 1
        descriptor.ordered_unique_identity = 1
        descriptor.candidate_only = 1
        descriptor.requires_signed_environmental_vm81_admission = 1

        receipt = HHSExactPass219Lane5RepositoryCapabilityReceiptV1()
        status = self.lib.hhs_exact_pass219_lane5_repository_capability_reverse_discovery_validate(
            ctypes.byref(descriptor), ctypes.byref(receipt)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError(f"Lane 5 repository capability snapshot rejected: status={status}")
        return {
            "total_entries": int(receipt.total_entries),
            "public_entries": int(receipt.public_entries),
            "native_entries": int(receipt.native_entries),
            "python_registry_entries": int(receipt.python_registry_entries),
            "restricted_entries": int(receipt.restricted_entries),
            "canonical_boundary_entries": int(receipt.canonical_boundary_entries),
            "public_catalog_signature64": int(receipt.public_catalog_signature64),
            "native_export_signature64": int(receipt.native_export_signature64),
            "python_registry_signature64": int(receipt.python_registry_signature64),
            "dependency_signature64": int(receipt.dependency_signature64),
            "model_signature64": int(receipt.model_signature64),
            "canonical_boundary_signature64": int(receipt.canonical_boundary_signature64),
            "descriptor_signature64": int(receipt.descriptor_signature64),
            "receipt_signature64": int(receipt.receipt_signature64),
            "accepted": bool(receipt.accepted),
            "public_registry_complete": bool(receipt.public_registry_complete),
            "native_exact_abi_complete": bool(receipt.native_exact_abi_complete),
            "python_operation_registry_complete": bool(receipt.python_operation_registry_complete),
            "structural_registry_keys_only": bool(receipt.structural_registry_keys_only),
            "ordered_unique_identity": bool(receipt.ordered_unique_identity),
            "candidate_only": bool(receipt.candidate_only),
            "auto_hash216_composition_promotion": bool(receipt.auto_hash216_composition_promotion),
            "auto_superedge_promotion": bool(receipt.auto_superedge_promotion),
            "canonical_vm81_mutation_authority": bool(receipt.canonical_vm81_mutation_authority),
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
    "VERSION",
    "NAMESPACE",
    "MAX_ENTRIES",
    "SOURCE_PUBLIC_REGISTRY",
    "SOURCE_NATIVE_EXACT_ABI",
    "SOURCE_PYTHON_OPERATION_REGISTRY",
    "AUTH_OBSERVATION",
    "AUTH_GOVERNED_TRANSFORM",
    "AUTH_CANONICAL_ADMISSION_BOUNDARY",
    "AUTH_RESTRICTED_OR_UNAVAILABLE",
    "Pass219Lane5RepositoryCapabilityReverseDiscoveryBridge",
]
