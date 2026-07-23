from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root, stable

SCHEMA = "HHS_HASH216_IMMUTABLE_VECTOR_RESOLVER_MANIFEST_V1"
CONTRACT_ID = "HHS-VM81-H216-NATIVE-DEV-ELASTIC-MEMORY"
ABI_VERSION = 1

SOURCE_PATHS = (
    "native_projects/hhs_vm81_native_development/c/hhs_hash216_vector_resolver_v1.h",
    "native_projects/hhs_vm81_native_development/c/hhs_hash216_vector_resolver_v1.c",
    "native_projects/hhs_vm81_native_development/c/hhs_hash216_vector_resolver_smoke.c",
)

DOMAINS = (
    "PROGRAM",
    "TILE",
    "MAP",
    "SPRITE",
    "ENTITY",
    "PHYSICS",
    "INPUT",
    "FRAME",
    "HISTORY",
    "RECEIPT",
    "METADATA",
)

ROLES = (
    "PRIMARY",
    "GRAPHICS",
    "COLLISION",
    "METADATA",
    "FRAMEBUFFER",
    "PALETTE",
    "INPUT_SEQUENCE",
    "RECEIPT_CHAIN",
)

STATUSES = (
    "OK",
    "INVALID_ARGUMENT",
    "ABI_VERSION_MISMATCH",
    "INVALID_DOMAIN",
    "INVALID_ROLE",
    "POSITION_OUT_OF_RANGE",
    "LANE_OUT_OF_RANGE",
    "PHASE_OUT_OF_RANGE",
    "VERSION_INVALID",
    "GENERATION_INVALID",
    "SIZE_OVERFLOW",
    "CAPACITY_VIOLATION",
    "DESCRIPTOR_INVALID",
    "DUPLICATE_ADDRESS",
    "RESOLVER_UNSEALED",
    "NONCANONICAL_ADDRESS",
    "NOT_FOUND",
    "STALE_VERSION",
    "STALE_GENERATION",
    "CONTENT_COMMITMENT_MISMATCH",
    "READ_OUT_OF_BOUNDS",
    "OUTPUT_TOO_SMALL",
    "MUTATION_NOT_SUPPORTED",
    "INTERNAL_INVARIANT_FAILURE",
)

OPERATIONS = (
    "ADDRESS_BUILD",
    "ADDRESS_VALIDATE",
    "IMMUTABLE_RESOLVER_INITIALIZE",
    "VRESOLVE",
    "VREAD",
)


def _source_record(repo: Path, relative: str) -> dict[str, Any]:
    path = repo / relative
    return {
        "path": relative,
        "present": path.is_file(),
        "size": path.stat().st_size if path.is_file() else None,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
    }


def build_manifest(repo: Path) -> dict[str, Any]:
    result = stable(
        {
            "schema": SCHEMA,
            "contract_id": CONTRACT_ID,
            "abi_version": ABI_VERSION,
            "implementation_slice": "HASH216_CANONICAL_LOGICAL_ADDRESS_AND_IMMUTABLE_BOUNDED_VECTOR_RESOLUTION",
            "sources": [_source_record(repo, relative) for relative in SOURCE_PATHS],
            "address_tuple": [
                "domain",
                "role",
                "position",
                "lane",
                "phase",
                "version",
                "generation",
                "content_commitment",
            ],
            "canonical_serialization": {
                "native_struct_bytes_used": False,
                "integer_encoding": "FIXED_WIDTH_BIG_ENDIAN",
                "content_commitment_positions": 216,
                "logical_address_positions": 216,
                "domain_separator": "HHS-HASH216-LOGICAL-ADDRESS-V1",
                "physical_pointer_included": False,
            },
            "limits": {
                "position_min": 0,
                "position_max": 215,
                "vm81_lane_min": 0,
                "vm81_lane_max": 80,
                "phase_min": 0,
                "phase_max": 71,
                "maximum_objects_per_snapshot": 8,
                "maximum_bytes_per_object": 4096,
                "minimum_version": 1,
                "minimum_generation": 1,
            },
            "domains": list(DOMAINS),
            "roles": list(ROLES),
            "statuses": list(STATUSES),
            "operations": list(OPERATIONS),
            "descriptor": {
                "fields": [
                    "canonical_address",
                    "element_count",
                    "byte_length",
                    "capacity_bytes",
                    "element_size",
                    "element_format",
                    "immutable",
                    "descriptor_commitment",
                ],
                "raw_pointer_exposed": False,
                "content_commitment_checked_before_read": True,
                "bounds_checked_before_copy": True,
            },
            "resolver": {
                "construction": "BUILD_COMPLETE_CANDIDATE_VALIDATE_SORT_COMMIT_ROOT_THEN_SEAL",
                "candidate_snapshot_only": True,
                "sealed_candidate_mutable": False,
                "authoritative_publication_performed": False,
                "vm81_authorized_publication_required": True,
                "order_independent_root": True,
                "duplicate_logical_address_rejected": True,
                "partial_candidate_exposure_on_failure": False,
                "stale_version_typed_rejection": True,
                "stale_generation_typed_rejection": True,
                "noncanonical_address_typed_rejection": True,
                "content_tamper_typed_rejection": True,
            },
            "authority": {
                "hash216_role": "LOGICAL_IDENTITY_INTEGRITY_AND_ADDRESSING",
                "vm81_execution_authority_transferred": False,
                "host_physical_address_authority": False,
                "sealed_candidate_is_authoritative": False,
                "vm81_authorized_resolver_publication_implemented": False,
                "runtime_mutation_surface_exposed": False,
                "single_use_mutation_capability_implemented": False,
            },
            "closure": {
                "canonical_hash216_address_implemented": True,
                "bounded_immutable_vector_descriptor_implemented": True,
                "immutable_resolver_candidate_snapshot_implemented": True,
                "bounded_vresolve_implemented": True,
                "bounded_vread_implemented": True,
                "stale_address_rejection_implemented": True,
                "content_integrity_revalidation_implemented": True,
                "no_partial_candidate_exposure_implemented": True,
                "vm81_authorized_resolver_publication_implemented": False,
                "vector_mutation_implemented": False,
                "terminal_classification_emitted": False,
            },
            "implementation_status": "HASH216_IMMUTABLE_VECTOR_RESOLVER_IMPLEMENTED_TERMINAL_VERIFICATION_NOT_YET_CLAIMED",
        }
    )
    result["resolver_manifest_root_hash72"] = product_root(
        "hhs_hash216_immutable_vector_resolver_manifest_v1", result
    )
    return stable(result)
