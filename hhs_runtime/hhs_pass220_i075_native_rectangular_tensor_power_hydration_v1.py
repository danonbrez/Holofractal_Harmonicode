"""Pass 220 I075 — native rectangular tensor-power hydration.

I075 lowers the two held 4x2 MatrixPower source nodes from I074 into typed
HARMONICODE rectangular tensor-power AST records without assigning host matrix
power semantics. The operator remains native, ordered, source-bound, and
candidate-only. Hash216 hydration is exact and reconstructible on demand.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    hydrate_hash216_geometry,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import hash72
from hhs_runtime.hhs_pass220_i074_full_tensor_hnan_closure_hydration_v1 import (
    AUTHORITY_BOUNDARY as I074_AUTHORITY_BOUNDARY,
    M_WZ,
    M_XY,
    MATRIX_POWER_NODES,
    build_candidate as build_i074_candidate,
    validate_candidate as validate_i074_candidate,
)

SCHEMA = "HHS_PASS_220_I075_NATIVE_RECTANGULAR_TENSOR_POWER_HYDRATION_V1"
PROFILE = "PASS220-I075-NATIVE-RECTANGULAR-TENSOR-POWER-HYDRATION-v1"
VERSION = "1.0.0"
HASH72_WIDTH = 72
HASH216_WIDTH = 216
SERIALIZED_CHARACTERS = 5184
FULL_HASH216_COMPONENTS = 15552

SOURCE_BUNDLE = (
    {
        "role": "I074_PARENT_RUNTIME",
        "path": "hhs_runtime/hhs_pass220_i074_full_tensor_hnan_closure_hydration_v1.py",
        "git_blob_sha": "b6ffd011c9f2bc8ed3d957e9c95573f89be2b7c6",
    },
    {
        "role": "I074_LEAN_PARENT",
        "path": "formal/lean/HHS/Pass220/FullTensorHNANClosureHydration.lean",
        "git_blob_sha": "78f4611ffe020c15bda630f789a6b028b0c5ad15",
    },
    {
        "role": "I073_PARENT_RUNTIME",
        "path": "hhs_runtime/hhs_pass220_i073_palindromic_rna_fibonacci_symbolic_tensor_v1.py",
        "git_blob_sha": "26ed28b7a9d1b2c694fcb5bae52fd254d544f43c",
    },
    {
        "role": "HNAN_ORDERED_GATE",
        "path": "hhs_runtime/pass219/hnan_4x4_recursive_gate_v1.py",
        "git_blob_sha": "a0ccd47620301ef2cc864e9e86834c8608b7b200",
    },
)

AUTHORITY_BOUNDARY = {
    "candidate_only": True,
    "inherits_i074": True,
    "native_rectangular_tensor_power_typed": True,
    "host_matrixpower_authority": False,
    "host_rectangular_matrixpower_authority": False,
    "numeric_exponent_evaluation_authority": False,
    "ordered_cell_identity_preserved": True,
    "projection_substitution_authorized": False,
    "floating_point_authority": False,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_hash216_persistence_authority": False,
    "external_egress_authority": False,
}


class Pass220I075Error(ValueError):
    pass


def _reject_float(value: Any, path: str = "root") -> None:
    if isinstance(value, float):
        raise Pass220I075Error(f"floating-point value forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for i, child in enumerate(value):
            _reject_float(child, f"{path}[{i}]")


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


@dataclass(frozen=True)
class NativeRectangularTensorPower:
    operator: str
    base_role: str
    rows: int
    columns: int
    exponent_token: str
    ordered_cells: tuple[tuple[str, ...], ...]
    source_node: str
    host_evaluated: bool
    numeric_exponent_evaluated: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_matrix(matrix: Sequence[Sequence[str]], role: str) -> tuple[tuple[str, ...], ...]:
    rows = tuple(tuple(row) for row in matrix)
    if len(rows) != 4 or any(len(row) != 2 for row in rows):
        raise Pass220I075Error(f"{role} must remain exact 4x2")
    if any(not isinstance(cell, str) or not cell for row in rows for cell in row):
        raise Pass220I075Error(f"{role} cells must be non-empty symbolic strings")
    return rows


def native_tensor_power_nodes() -> tuple[NativeRectangularTensorPower, ...]:
    mwz = _validate_matrix(M_WZ, "M_WZ")
    mxy = _validate_matrix(M_XY, "M_XY")
    nodes = (
        NativeRectangularTensorPower(
            operator="HARMONICODE_RECTANGULAR_TENSOR_POWER",
            base_role="M_WZ",
            rows=4,
            columns=2,
            exponent_token="x^2",
            ordered_cells=mwz,
            source_node=MATRIX_POWER_NODES[0],
            host_evaluated=False,
            numeric_exponent_evaluated=False,
        ),
        NativeRectangularTensorPower(
            operator="HARMONICODE_RECTANGULAR_TENSOR_POWER",
            base_role="M_XY",
            rows=4,
            columns=2,
            exponent_token="x^4",
            ordered_cells=mxy,
            source_node=MATRIX_POWER_NODES[1],
            host_evaluated=False,
            numeric_exponent_evaluated=False,
        ),
    )
    if tuple(node.source_node for node in nodes) != MATRIX_POWER_NODES:
        raise Pass220I075Error("source MatrixPower identity drift")
    if any(node.host_evaluated or node.numeric_exponent_evaluated for node in nodes):
        raise Pass220I075Error("native tensor-power node escaped held semantics")
    return nodes


def tensor_power_hydration_descriptor() -> dict[str, Any]:
    nodes = native_tensor_power_nodes()
    records = tuple(node.to_dict() for node in nodes)
    unique_cells: list[str] = []
    cell_index: dict[str, int] = {}
    occurrence_ids: list[int] = []
    for node in nodes:
        for row in node.ordered_cells:
            for cell in row:
                if cell not in cell_index:
                    cell_index[cell] = len(unique_cells)
                    unique_cells.append(cell)
                occurrence_ids.append(cell_index[cell])
    reconstructed = tuple(unique_cells[i] for i in occurrence_ids)
    original = tuple(cell for node in nodes for row in node.ordered_cells for cell in row)
    if reconstructed != original:
        raise Pass220I075Error("typed node cell reconstruction failed")
    return {
        "schema": f"{SCHEMA}_TENSOR_POWER_DESCRIPTOR_V1",
        "node_count": len(nodes),
        "nodes": records,
        "rectangular_shapes": ((4, 2), (4, 2)),
        "cell_occurrences": len(original),
        "unique_cell_expressions": len(unique_cells),
        "unique_cells": tuple(unique_cells),
        "occurrence_ids": tuple(occurrence_ids),
        "all_occurrence_witnesses_retained": True,
        "host_matrixpower_evaluations": 0,
        "numeric_exponent_evaluations": 0,
        "source_nodes_reconstructible": tuple(n.source_node for n in nodes) == MATRIX_POWER_NODES,
    }


def source_bundle_witness() -> dict[str, Any]:
    body = {
        "schema": f"{SCHEMA}_SOURCE_BUNDLE_V1",
        "sources": [dict(row) for row in SOURCE_BUNDLE],
        "source_count": len(SOURCE_BUNDLE),
    }
    body["source_bundle_root_sha256"] = _sha256(body)
    return body


def build_candidate() -> dict[str, Any]:
    parent = build_i074_candidate()
    if not validate_i074_candidate(parent):
        raise Pass220I075Error("I074 parent candidate invalid")
    descriptor = tensor_power_hydration_descriptor()
    sources = source_bundle_witness()

    previous = hash72({
        "schema": f"{SCHEMA}_PREVIOUS_V1",
        "parent_i074_root_sha256": parent["candidate_root_sha256"],
        "parent_i074_hash216": parent["candidate_hash216"],
        "source_bundle_root_sha256": sources["source_bundle_root_sha256"],
    })
    change = hash72({
        "schema": f"{SCHEMA}_CHANGE_V1",
        "descriptor_root_sha256": _sha256(descriptor),
        "source_nodes": MATRIX_POWER_NODES,
        "host_matrixpower_evaluations": descriptor["host_matrixpower_evaluations"],
    })
    receipt = hash72({
        "schema": f"{SCHEMA}_RECEIPT_V1",
        "node_count": descriptor["node_count"],
        "rectangular_shapes": descriptor["rectangular_shapes"],
        "all_occurrence_witnesses_retained": descriptor["all_occurrence_witnesses_retained"],
        "source_nodes_reconstructible": descriptor["source_nodes_reconstructible"],
        "authority": AUTHORITY_BOUNDARY,
    })
    candidate_hash216 = previous + change + receipt
    if len(candidate_hash216) != HASH216_WIDTH:
        raise Pass220I075Error("Hash216 width drift")

    hydrated = hydrate_hash216_geometry(candidate_hash216)
    if hydrated.get("roundtrip_exact") is not True:
        raise Pass220I075Error("I075 hydration roundtrip failed")
    if hydrated.get("full_attached_components") != FULL_HASH216_COMPONENTS:
        raise Pass220I075Error("I075 attached-component count drift")

    plane_roots = tuple({
        "role": plane["role"],
        "generator_hash72": plane["generator_hash72"],
        "expanded_vertices": plane["expanded_vertices"],
        "expanded_geometry_sha256": plane["expanded_geometry_sha256"],
        "roundtrip_exact": plane["roundtrip_exact"],
    } for plane in hydrated["planes"])

    candidate = {
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "parent_i074": {
            "candidate_root_sha256": parent["candidate_root_sha256"],
            "binding_hash72": parent["binding_hash72"],
            "candidate_hash216": parent["candidate_hash216"],
            "authority": I074_AUTHORITY_BOUNDARY,
        },
        "source_bundle": sources,
        "tensor_power_descriptor": descriptor,
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
    candidate["candidate_root_sha256"] = _sha256(candidate)
    candidate["binding_hash72"] = hash72({
        "schema": SCHEMA,
        "candidate_root_sha256": candidate["candidate_root_sha256"],
        "candidate_hash216": candidate_hash216,
        "parent_binding_hash72": parent["binding_hash72"],
        "plane_roots": plane_roots,
    })
    return candidate


def validate_candidate(candidate: Mapping[str, Any]) -> bool:
    if not isinstance(candidate, Mapping) or candidate.get("schema") != SCHEMA:
        raise Pass220I075Error("candidate schema mismatch")
    _reject_float(candidate)
    canonical = build_candidate()
    for key in (
        "parent_i074", "source_bundle", "tensor_power_descriptor",
        "candidate_previous_hash72", "candidate_change_hash72",
        "candidate_receipt_hash72", "candidate_hash216", "plane_roots",
        "hydration", "authority", "candidate_root_sha256", "binding_hash72",
    ):
        if candidate.get(key) != canonical[key]:
            raise Pass220I075Error(f"candidate diverges at {key}")
    return True


def self_test() -> dict[str, Any]:
    candidate = build_candidate()
    d = candidate["tensor_power_descriptor"]
    checks = {
        "candidate_valid": validate_candidate(candidate),
        "two_native_nodes": d["node_count"] == 2,
        "both_4x2": d["rectangular_shapes"] == ((4, 2), (4, 2)),
        "source_nodes_reconstructible": d["source_nodes_reconstructible"] is True,
        "occurrences_retained": d["all_occurrence_witnesses_retained"] is True,
        "no_host_matrixpower": d["host_matrixpower_evaluations"] == 0,
        "no_numeric_exponent_eval": d["numeric_exponent_evaluations"] == 0,
        "hash216_width": len(candidate["candidate_hash216"]) == 216,
        "hydration_exact": candidate["hydration"]["roundtrip_exact"] is True,
        "hydration_15552": candidate["hydration"]["full_attached_components"] == 15552,
        "candidate_only": candidate["authority"]["candidate_only"] is True,
        "no_vm81_mutation": candidate["authority"]["canonical_vm81_mutation_authority"] is False,
        "no_hash216_commit": candidate["authority"]["canonical_hash216_commit_authority"] is False,
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(v) for v in checks.values()),
        "failed": [k for k, v in checks.items() if not v],
        "checks": checks,
        "candidate_root_sha256": candidate["candidate_root_sha256"],
        "binding_hash72": candidate["binding_hash72"],
        "candidate_hash216": candidate["candidate_hash216"],
    }


__all__ = [
    "AUTHORITY_BOUNDARY",
    "NativeRectangularTensorPower",
    "Pass220I075Error",
    "SCHEMA",
    "SOURCE_BUNDLE",
    "build_candidate",
    "native_tensor_power_nodes",
    "self_test",
    "source_bundle_witness",
    "tensor_power_hydration_descriptor",
    "validate_candidate",
]


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))
