"""Pass 220 I076 — ExactMatrixPower HIR hydration.

I076 lowers the two I075 typed 4x2 HARMONICODE rectangular tensor-power AST
records into the Pass169 canonical `ExactMatrixPower` HIR type. It preserves
source identity, ordered cell topology, and exponent tokens while explicitly
refusing host MatrixPower, square-matrix fallback, numeric exponent evaluation,
or unverified VM81 execution.

This is a source-preserving HIR lowering candidate. VM81 execution/admission is
still a downstream gate and is not claimed by this pass.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    hydrate_hash216_geometry,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import hash72
from hhs_runtime.hhs_pass220_i075_native_rectangular_tensor_power_hydration_v1 import (
    AUTHORITY_BOUNDARY as I075_AUTHORITY_BOUNDARY,
    build_candidate as build_i075_candidate,
    native_tensor_power_nodes,
    validate_candidate as validate_i075_candidate,
)

SCHEMA = "HHS_PASS_220_I076_EXACT_MATRIX_POWER_HIR_HYDRATION_V1"
PROFILE = "PASS220-I076-EXACT-MATRIX-POWER-HIR-HYDRATION-v1"
VERSION = "1.0.0"

PASS169_CONTRACT_ID = "HHS-P169-HSAE-VM81-ESCPR"
PASS169_CANONICAL_TYPE = "ExactMatrixPower"
HIR_NODE_KIND = "EXACT_SYMBOLIC_MATRIX_POWER"
SERIALIZED_CHARACTERS = 5184
HASH216_WIDTH = 216
FULL_HASH216_COMPONENTS = 15552

SOURCE_BUNDLE = (
    {
        "role": "I075_PARENT_RUNTIME",
        "path": "hhs_runtime/hhs_pass220_i075_native_rectangular_tensor_power_hydration_v1.py",
        "git_blob_sha": "4269eb0c6bec3805b8f108b77a77456a0a40c517",
    },
    {
        "role": "PASS169_TYPE_REGISTRY",
        "path": "HHS_PASS_169_TYPE_REGISTRY.json",
        "git_blob_sha": "70b7a0fe5b289a5ce15ea76e4bb4a9a80a5f9176",
    },
    {
        "role": "PASS169_NORMATIVE_CONTRACT",
        "path": "HHS_PASS_169_HARMONICODE_SYNTAX_ALGEBRA_ENFORCEMENT_AND_VM81_EXACT_SYMBOLIC_CONSTRAINT_PROOF_RUNTIME.md",
        "git_blob_sha": "a9b1a3eca87345214c13d85178fdf0b883b33e40",
    },
    {
        "role": "I075_LEAN_PARENT",
        "path": "formal/lean/HHS/Pass220/NativeRectangularTensorPowerHydration.lean",
        "git_blob_sha": "08f56f9ea83c89edcafa7d6ffa8b89682dc439e7",
    },
)

AUTHORITY_BOUNDARY = {
    "candidate_only": True,
    "pass169_type_registry_inherited": True,
    "exact_matrix_power_hir_typed": True,
    "source_identity_preserved": True,
    "ordered_cell_topology_preserved": True,
    "host_matrixpower_authority": False,
    "host_square_matrix_requirement_authority": False,
    "numeric_exponent_evaluation_authority": False,
    "matrix_power_value_derivation_authority": False,
    "vm81_execution_verified": False,
    "vm81_admission_verified": False,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_hash216_persistence_authority": False,
    "floating_point_authority": False,
    "projection_substitution_authorized": False,
    "external_egress_authority": False,
}


class Pass220I076Error(ValueError):
    pass


def _reject_float(value: Any, path: str = "root") -> None:
    if isinstance(value, float):
        raise Pass220I076Error(f"floating-point value forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


def source_bundle_witness() -> dict[str, Any]:
    body = {
        "schema": f"{SCHEMA}_SOURCE_BUNDLE_V1",
        "sources": [dict(row) for row in SOURCE_BUNDLE],
        "source_count": len(SOURCE_BUNDLE),
        "roles_unique": len({row["role"] for row in SOURCE_BUNDLE}) == len(SOURCE_BUNDLE),
        "paths_unique": len({row["path"] for row in SOURCE_BUNDLE}) == len(SOURCE_BUNDLE),
    }
    body["source_bundle_root_sha256"] = _sha256(body)
    return body


def exact_matrix_power_hir_nodes() -> tuple[dict[str, Any], ...]:
    native_nodes = native_tensor_power_nodes()
    lowered: list[dict[str, Any]] = []
    for index, node in enumerate(native_nodes):
        if (node.rows, node.columns) != (4, 2):
            raise Pass220I076Error("I075 rectangular shape drift")
        ordered_cells = tuple(tuple(row) for row in node.ordered_cells)
        cell_root = _sha256(ordered_cells)
        hir = {
            "schema": f"{SCHEMA}_HIR_NODE_V1",
            "node_index": index,
            "node_kind": HIR_NODE_KIND,
            "canonical_pass169_type": PASS169_CANONICAL_TYPE,
            "pass169_contract_id": PASS169_CONTRACT_ID,
            "source_operator": "MatrixPower",
            "source_node": node.source_node,
            "base_role": node.base_role,
            "base_shape": (node.rows, node.columns),
            "exponent_token": node.exponent_token,
            "ordered_cells": ordered_cells,
            "ordered_cells_root_sha256": cell_root,
            "source_identity_preserved": True,
            "ordered_cell_topology_preserved": True,
            "exact_symbolic_node": True,
            "host_matrixpower_evaluated": False,
            "host_square_matrix_requirement_imported": False,
            "numeric_exponent_evaluated": False,
            "matrix_power_value_derived": False,
            "vm81_execution_verified": False,
            "vm81_admission_required": True,
            "candidate_only": True,
        }
        hir["hir_node_root_sha256"] = _sha256(hir)
        lowered.append(hir)

    if len(lowered) != 2:
        raise Pass220I076Error("expected exactly two ExactMatrixPower HIR nodes")
    if tuple(row["source_node"] for row in lowered) != tuple(
        node.source_node for node in native_nodes
    ):
        raise Pass220I076Error("source-node identity drift")
    return tuple(lowered)


def hir_lowering_descriptor() -> dict[str, Any]:
    nodes = exact_matrix_power_hir_nodes()
    roots = tuple(row["hir_node_root_sha256"] for row in nodes)
    descriptor = {
        "schema": f"{SCHEMA}_HIR_DESCRIPTOR_V1",
        "pass169_contract_id": PASS169_CONTRACT_ID,
        "canonical_type": PASS169_CANONICAL_TYPE,
        "node_kind": HIR_NODE_KIND,
        "node_count": len(nodes),
        "nodes": nodes,
        "hir_node_roots_sha256": roots,
        "hir_forest_root_sha256": _sha256(roots),
        "rectangular_shapes": tuple(row["base_shape"] for row in nodes),
        "source_nodes": tuple(row["source_node"] for row in nodes),
        "exponent_tokens": tuple(row["exponent_token"] for row in nodes),
        "host_matrixpower_evaluations": 0,
        "numeric_exponent_evaluations": 0,
        "matrix_power_values_derived": 0,
        "vm81_executions_verified": 0,
        "source_identity_preserved": True,
        "ordered_topology_preserved": True,
        "vm81_admission_required": True,
    }
    descriptor["descriptor_root_sha256"] = _sha256(descriptor)
    return descriptor


def build_candidate() -> dict[str, Any]:
    parent = build_i075_candidate()
    if not validate_i075_candidate(parent):
        raise Pass220I076Error("I075 parent candidate invalid")

    sources = source_bundle_witness()
    descriptor = hir_lowering_descriptor()

    previous = hash72(
        {
            "schema": f"{SCHEMA}_PREVIOUS_V1",
            "parent_i075_root_sha256": parent["candidate_root_sha256"],
            "parent_i075_hash216": parent["candidate_hash216"],
            "source_bundle_root_sha256": sources["source_bundle_root_sha256"],
        }
    )
    change = hash72(
        {
            "schema": f"{SCHEMA}_CHANGE_V1",
            "descriptor_root_sha256": descriptor["descriptor_root_sha256"],
            "hir_forest_root_sha256": descriptor["hir_forest_root_sha256"],
            "canonical_type": PASS169_CANONICAL_TYPE,
        }
    )
    receipt = hash72(
        {
            "schema": f"{SCHEMA}_RECEIPT_V1",
            "node_count": descriptor["node_count"],
            "source_identity_preserved": descriptor["source_identity_preserved"],
            "ordered_topology_preserved": descriptor["ordered_topology_preserved"],
            "vm81_admission_required": descriptor["vm81_admission_required"],
            "authority": AUTHORITY_BOUNDARY,
        }
    )
    candidate_hash216 = previous + change + receipt
    if len(candidate_hash216) != HASH216_WIDTH:
        raise Pass220I076Error("Hash216 width drift")

    hydrated = hydrate_hash216_geometry(candidate_hash216)
    if hydrated.get("roundtrip_exact") is not True:
        raise Pass220I076Error("I076 Hash216 hydration roundtrip failed")
    if hydrated.get("full_attached_components") != FULL_HASH216_COMPONENTS:
        raise Pass220I076Error("I076 hydrated component count drift")

    plane_roots = tuple(
        {
            "role": plane["role"],
            "generator_hash72": plane["generator_hash72"],
            "expanded_vertices": plane["expanded_vertices"],
            "expanded_geometry_sha256": plane["expanded_geometry_sha256"],
            "roundtrip_exact": plane["roundtrip_exact"],
        }
        for plane in hydrated["planes"]
    )

    result = {
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "parent_i075": {
            "candidate_root_sha256": parent["candidate_root_sha256"],
            "binding_hash72": parent["binding_hash72"],
            "candidate_hash216": parent["candidate_hash216"],
            "authority": I075_AUTHORITY_BOUNDARY,
        },
        "source_bundle": sources,
        "hir_lowering": descriptor,
        "candidate_previous_hash72": previous,
        "candidate_change_hash72": change,
        "candidate_receipt_hash72": receipt,
        "candidate_hash216": candidate_hash216,
        "plane_roots": plane_roots,
        "hydration": {
            "roundtrip_exact": hydrated["roundtrip_exact"],
            "full_attached_components": hydrated["full_attached_components"],
            "expanded_geometry_persisted": False,
            "reconstructible_on_demand": True,
        },
        "authority": dict(AUTHORITY_BOUNDARY),
    }
    result["candidate_root_sha256"] = _sha256(result)
    result["binding_hash72"] = hash72(
        {
            "schema": SCHEMA,
            "candidate_root_sha256": result["candidate_root_sha256"],
            "candidate_hash216": candidate_hash216,
            "parent_binding_hash72": parent["binding_hash72"],
            "hir_forest_root_sha256": descriptor["hir_forest_root_sha256"],
            "plane_roots": plane_roots,
        }
    )
    return result


def validate_candidate(candidate: Mapping[str, Any]) -> bool:
    if not isinstance(candidate, Mapping) or candidate.get("schema") != SCHEMA:
        raise Pass220I076Error("candidate schema mismatch")
    _reject_float(candidate)
    canonical = build_candidate()
    for key in (
        "parent_i075",
        "source_bundle",
        "hir_lowering",
        "candidate_previous_hash72",
        "candidate_change_hash72",
        "candidate_receipt_hash72",
        "candidate_hash216",
        "plane_roots",
        "hydration",
        "authority",
        "candidate_root_sha256",
        "binding_hash72",
    ):
        if candidate.get(key) != canonical[key]:
            raise Pass220I076Error(f"candidate diverges at {key}")
    return True


def self_test() -> dict[str, Any]:
    candidate = build_candidate()
    hir = candidate["hir_lowering"]
    checks = {
        "candidate_valid": validate_candidate(candidate),
        "exact_matrix_power_type": hir["canonical_type"] == "ExactMatrixPower",
        "two_hir_nodes": hir["node_count"] == 2,
        "both_4x2": hir["rectangular_shapes"] == ((4, 2), (4, 2)),
        "source_identity_preserved": hir["source_identity_preserved"] is True,
        "ordered_topology_preserved": hir["ordered_topology_preserved"] is True,
        "no_host_matrixpower": hir["host_matrixpower_evaluations"] == 0,
        "no_numeric_exponent_eval": hir["numeric_exponent_evaluations"] == 0,
        "no_value_derivation": hir["matrix_power_values_derived"] == 0,
        "no_vm81_execution_claim": hir["vm81_executions_verified"] == 0,
        "vm81_admission_required": hir["vm81_admission_required"] is True,
        "hash216_width_216": len(candidate["candidate_hash216"]) == 216,
        "hydration_exact": candidate["hydration"]["roundtrip_exact"] is True,
        "hydration_15552": candidate["hydration"]["full_attached_components"] == 15552,
        "candidate_only": candidate["authority"]["candidate_only"] is True,
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(value) for value in checks.values()),
        "failed": [name for name, value in checks.items() if not value],
        "checks": checks,
        "candidate_root_sha256": candidate["candidate_root_sha256"],
        "binding_hash72": candidate["binding_hash72"],
        "candidate_hash216": candidate["candidate_hash216"],
    }


__all__ = [
    "AUTHORITY_BOUNDARY",
    "HIR_NODE_KIND",
    "PASS169_CANONICAL_TYPE",
    "PASS169_CONTRACT_ID",
    "Pass220I076Error",
    "SCHEMA",
    "SOURCE_BUNDLE",
    "build_candidate",
    "exact_matrix_power_hir_nodes",
    "hir_lowering_descriptor",
    "self_test",
    "source_bundle_witness",
    "validate_candidate",
]


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))
