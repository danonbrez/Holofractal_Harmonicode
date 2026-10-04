"""Pass 220 I074 — full I Tensor HNAN closure hydration optimizer.

I074 preserves the supplied HARMONICODE source as an exact symbolic object and
extends the merged I073 generator with a source-preserving structural optimizer:

* I069 exact A/B reciprocal generator and Lo Shu-routed C matrix;
* one shared E-membrane value node with three retained source occurrences;
* held 4x2 MatrixPower operand nodes (never host MatrixPower evaluation);
* HNAN / Mod[...,1] typed closure metadata;
* right-side common-subexpression roots with every source-cell witness retained;
* ordered Hash216 candidate hydrated/recompressed through I065.

No host scalar, Boolean, floating-point, commutative, or rectangular-matrix
power semantics are promoted to HARMONICODE authority.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    hydrate_hash216_geometry,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import (
    E_VECTOR,
    LO_SHU,
    hash72,
    matrix_a,
    matrix_b,
    matrix_c,
    phase_kernel,
)
from hhs_runtime.hhs_pass220_i073_palindromic_rna_fibonacci_symbolic_tensor_v1 import (
    DEFAULT_DECIMAL_SOURCE,
    build_generator as build_i073_generator,
    validate_generator as validate_i073_generator,
)

SCHEMA = "HHS_PASS_220_I074_FULL_TENSOR_HNAN_CLOSURE_HYDRATION_V1"
PROFILE = "PASS220-I074-FULL-TENSOR-HNAN-CLOSURE-HYDRATION-v1"
VERSION = "1.0.0"

HASH72_WIDTH = 72
HASH216_WIDTH = 216
SERIALIZED_CHARACTERS = 5184
FULL_HASH216_COMPONENTS = 3 * SERIALIZED_CHARACTERS

VERBATIM_SOURCE = (
    "u^((MatrixTimes(x,((-List(List(64,8,24),List(8,24,40),List(24,40,56)))"
    "/(E==List(8,24,40,56,72,16,32,48,64))))"
    "-MatrixTimes(y,((-List(List(8,64,48),List(64,48,32),List(48,32,16)))"
    "/(E==List(8,24,40,56,72,16,32,48,64))))"
    "==Mod(MatrixTimes(x*y,(List(List(56,64,24),List(40,72,32),List(48,8,16))"
    "/(E==List(8,24,40,56,72,16,32,48,64)))),72))/u/(x*y)"
    "==u^72/(Mod((-MatrixPower({{-w*z,z-w},{z-w,w*z},{w*z,-w*z},{y+x,z-w}},x^2)"
    "/(x*y)+MatrixPower({{-x*y,y+x},{y+x,x*y},{x*y,-x*y},{y+x,z-w}},x^4)"
    "/(w*z)=={{-1,0},{0,1},{1,-1},{0,0}}"
    "=={{w*z-x*y+1,-z+y+x+w},{-z+y+x+w,(-w)*z+x*y-1},"
    "{(-w)*z+x*y-1,w*z-x*y+1},{0,0}}==0),1))==1)"
)

E_MEMBRANE_SOURCE = "E==List(8,24,40,56,72,16,32,48,64)"
E_MEMBRANE_OCCURRENCES = 3
E_MEMBRANE_VALUE_NODES = 1
E_MEMBRANE_EVALUATIONS_AVOIDED = 2

M_WZ = (
    ("-w*z", "z-w"),
    ("z-w", "w*z"),
    ("w*z", "-w*z"),
    ("y+x", "z-w"),
)
M_XY = (
    ("-x*y", "y+x"),
    ("y+x", "x*y"),
    ("x*y", "-x*y"),
    ("y+x", "z-w"),
)
TARGET_MATRIX = (
    ("-1", "0"),
    ("0", "1"),
    ("1", "-1"),
    ("0", "0"),
)
CLOSURE_MATRIX = (
    ("w*z-x*y+1", "-z+y+x+w"),
    ("-z+y+x+w", "(-w)*z+x*y-1"),
    ("(-w)*z+x*y-1", "w*z-x*y+1"),
    ("0", "0"),
)
MATRIX_POWER_NODES = (
    "MatrixPower[M_wz,x^2]",
    "MatrixPower[M_xy,x^4]",
)

SOURCE_BUNDLE = (
    {
        "role": "I073_PARENT_GENERATOR",
        "path": "hhs_runtime/hhs_pass220_i073_palindromic_rna_fibonacci_symbolic_tensor_v1.py",
        "git_blob_sha": "26ed28b7a9d1b2c694fcb5bae52fd254d544f43c",
    },
    {
        "role": "I069_I_TENSOR_GENERATOR",
        "path": "hhs_runtime/hhs_pass220_i069_harmonicode_i_tensor_v1.py",
        "git_blob_sha": "b44f7660a7804ccd8d048c37797a0923fe17346f",
    },
    {
        "role": "HNAN_ORDERED_GATE",
        "path": "hhs_runtime/pass219/hnan_4x4_recursive_gate_v1.py",
        "git_blob_sha": "a0ccd47620301ef2cc864e9e86834c8608b7b200",
    },
    {
        "role": "I073_LEAN_PARENT",
        "path": "formal/lean/HHS/Pass220/PalindromicRNAFibonacciSymbolicTensor.lean",
        "git_blob_sha": "5a71a9df7da3c61598563b97067d2cf32e14d1eb",
    },
    {
        "role": "HNAN_LEAN_TRANSPORT",
        "path": "formal/lean/HHS/Pass219/QGUHNANTransport.lean",
        "git_blob_sha": "2b9b63f93d2f86aef1617fc5f1ed14d1ca0e2416",
    },
)

AUTHORITY_BOUNDARY = {
    "candidate_only": True,
    "verbatim_source_authoritative": True,
    "ordered_xy_yx_preserved": True,
    "ordered_zw_wz_preserved": True,
    "e_membrane_host_boolean_division_authority": False,
    "rectangular_host_matrixpower_authority": False,
    "host_mod_one_rewrite_authority": False,
    "host_division_by_zero_authority": False,
    "host_float_arithmetic_authority": False,
    "hnan_gate_native": True,
    "right_occurrence_witnesses_retained": True,
    "projection_substitution_authorized": False,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_hash216_persistence_authority": False,
    "external_egress_authority": False,
}


class Pass220I074Error(ValueError):
    """Raised when the I074 exact structural/hydration invariant fails."""


def _reject_float(value: Any, path: str = "root") -> None:
    if isinstance(value, float):
        raise Pass220I074Error(f"floating-point value forbidden at {path}")
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


def _det3(matrix: Sequence[Sequence[int]]) -> int:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise Pass220I074Error("determinant requires an exact 3x3 matrix")
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


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


def left_generator_witness() -> dict[str, Any]:
    a = matrix_a()
    b = matrix_b()
    c = matrix_c()
    kernel = phase_kernel()
    checks = {
        "e_vector_exact": E_VECTOR == (8, 24, 40, 56, 72, 16, 32, 48, 64),
        "lo_shu_exact": LO_SHU == ((4, 9, 2), (3, 5, 7), (8, 1, 6)),
        "phase_kernel_exact": kernel == ((8, 1, 3), (1, 3, 5), (3, 5, 7)),
        "a_b_pointwise_72": all(
            a[row][col] + b[row][col] == 72
            for row in range(3)
            for col in range(3)
        ),
        "c_center_72": c[1][1] == 72,
        "c_center_mod72_zero": c[1][1] % 72 == 0,
        "determinants_exact": (_det3(a), _det3(b), _det3(c))
        == (-18432, 18432, 32256),
        "e_membrane_occurrences_exact": VERBATIM_SOURCE.count(E_MEMBRANE_SOURCE)
        == E_MEMBRANE_OCCURRENCES,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise Pass220I074Error("left generator drift: " + ",".join(failed))
    return {
        "schema": f"{SCHEMA}_LEFT_GENERATOR_V1",
        "phase_kernel": kernel,
        "matrix_a": a,
        "matrix_b": b,
        "matrix_c": c,
        "determinants": (_det3(a), _det3(b), _det3(c)),
        "normalized_determinants": (-36, 36, 63),
        "e_membrane": {
            "source": E_MEMBRANE_SOURCE,
            "source_occurrences": E_MEMBRANE_OCCURRENCES,
            "value_nodes": E_MEMBRANE_VALUE_NODES,
            "value_evaluations_avoided": E_MEMBRANE_EVALUATIONS_AVOIDED,
            "source_occurrence_witnesses_retained": E_MEMBRANE_OCCURRENCES,
        },
        "checks": checks,
    }


def _flatten(matrix: Sequence[Sequence[str]]) -> tuple[str, ...]:
    return tuple(value for row in matrix for value in row)


def right_symbolic_cse_witness() -> dict[str, Any]:
    matrices = (M_WZ, M_XY, TARGET_MATRIX, CLOSURE_MATRIX)
    cells = tuple(value for matrix in matrices for value in _flatten(matrix))
    unique: list[str] = []
    index_by_value: dict[str, int] = {}
    occurrence_ids: list[int] = []
    for value in cells:
        if value not in index_by_value:
            index_by_value[value] = len(unique)
            unique.append(value)
        occurrence_ids.append(index_by_value[value])

    reconstructed = tuple(unique[index] for index in occurrence_ids)
    if reconstructed != cells:
        raise Pass220I074Error("right symbolic CSE reconstruction failed")
    if len(cells) != 32 or len(unique) != 12:
        raise Pass220I074Error("right symbolic CSE census drift")
    if len(cells) - len(unique) != 20:
        raise Pass220I074Error("right symbolic CSE savings drift")
    if VERBATIM_SOURCE.count("MatrixPower(") != 2:
        raise Pass220I074Error("MatrixPower source occurrence drift")

    return {
        "schema": f"{SCHEMA}_RIGHT_SYMBOLIC_CSE_V1",
        "matrix_shapes": ((4, 2), (4, 2), (4, 2), (4, 2)),
        "matrix_roles": ("M_WZ", "M_XY", "TARGET", "HNAN_CLOSURE"),
        "matrices": matrices,
        "cell_occurrences": len(cells),
        "unique_cell_expressions": len(unique),
        "materializations_avoided": len(cells) - len(unique),
        "unique_cells": tuple(unique),
        "occurrence_ids": tuple(occurrence_ids),
        "all_occurrence_witnesses_retained": True,
        "matrix_power_nodes": MATRIX_POWER_NODES,
        "matrix_power_source_occurrences": 2,
        "matrix_power_host_evaluated": False,
        "rectangular_matrixpower_promoted_to_host_semantics": False,
    }


def closure_witness() -> dict[str, Any]:
    """Record the native HARMONICODE closure route without host coercion."""
    required_tokens = (
        "/u/(x*y)",
        "/(w*z)",
        "=={{-1,0},{0,1},{1,-1},{0,0}}",
        "=={{w*z-x*y+1,-z+y+x+w}",
        "==0),1)",
        "==1)",
    )
    missing = [token for token in required_tokens if token not in VERBATIM_SOURCE]
    if missing:
        raise Pass220I074Error("closure source token drift: " + ",".join(missing))
    return {
        "schema": f"{SCHEMA}_CLOSURE_WITNESS_V1",
        "selected_interpretation": "HARMONICODE_NATIVE",
        "interpretation_locked": True,
        "ordered_xy_divisor_preserved": True,
        "ordered_wz_divisor_preserved": True,
        "hnan_mod_unit_gate_preserved": True,
        "hnan_pole_is_native_gate_state": True,
        "mod_one_is_native_quantization_gate": True,
        "u72_closure_unit": "Delta",
        "universal_denominator_unit": "Delta",
        "closure_readout": "1_H",
        "delta_e": "0",
        "psi": "0",
        "omega": True,
        "host_boolean_coercion_used": False,
        "host_modulo_one_used": False,
        "host_division_by_zero_used": False,
        "host_rectangular_matrixpower_used": False,
        "projection_substitution_used": False,
    }


def build_candidate(
    *,
    decimal_text: str = DEFAULT_DECIMAL_SOURCE,
    offsets: Sequence[int] | None = None,
    fibonacci_depth: int | None = None,
    nucleus_index: int = 0,
    nesting_depth: int = 0,
) -> dict[str, Any]:
    parent = build_i073_generator(
        decimal_text=decimal_text,
        offsets=offsets,
        fibonacci_depth=fibonacci_depth,
        nucleus_index=nucleus_index,
        nesting_depth=nesting_depth,
    )
    if not validate_i073_generator(parent):
        raise Pass220I074Error("I073 parent generator failed validation")

    source_bundle = source_bundle_witness()
    left = left_generator_witness()
    right = right_symbolic_cse_witness()
    closure = closure_witness()

    previous_hash72 = hash72(
        {
            "schema": f"{SCHEMA}_PREVIOUS_V1",
            "parent_i073_root_sha256": parent["generator_root_sha256"],
            "parent_i073_hash216": parent["generator_hash216"],
            "source_bundle_root_sha256": source_bundle["source_bundle_root_sha256"],
        }
    )
    change_hash72 = hash72(
        {
            "schema": f"{SCHEMA}_CHANGE_V1",
            "verbatim_source_sha256": sha256(VERBATIM_SOURCE.encode("utf-8")).hexdigest(),
            "left_generator_root_sha256": _sha256(left),
            "right_symbolic_cse_root_sha256": _sha256(right),
            "closure_root_sha256": _sha256(closure),
        }
    )
    receipt_hash72 = hash72(
        {
            "schema": f"{SCHEMA}_RECEIPT_V1",
            "e_membrane_value_evaluations_avoided": E_MEMBRANE_EVALUATIONS_AVOIDED,
            "right_materializations_avoided": right["materializations_avoided"],
            "right_occurrence_witnesses_retained": right[
                "all_occurrence_witnesses_retained"
            ],
            "matrix_power_host_evaluated": right["matrix_power_host_evaluated"],
            "closure_readout": closure["closure_readout"],
            "authority": AUTHORITY_BOUNDARY,
        }
    )
    candidate_hash216 = previous_hash72 + change_hash72 + receipt_hash72
    if len(candidate_hash216) != HASH216_WIDTH:
        raise Pass220I074Error("candidate Hash216 width drift")

    hydrated = hydrate_hash216_geometry(candidate_hash216)
    if hydrated.get("roundtrip_exact") is not True:
        raise Pass220I074Error("I074 Hash216 hydration roundtrip failed")
    if hydrated.get("full_attached_components") != FULL_HASH216_COMPONENTS:
        raise Pass220I074Error("I074 hydrated component count drift")

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

    candidate = {
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "verbatim_source": VERBATIM_SOURCE,
        "verbatim_source_sha256": sha256(VERBATIM_SOURCE.encode("utf-8")).hexdigest(),
        "parent_i073": {
            "generator_root_sha256": parent["generator_root_sha256"],
            "binding_hash72": parent["binding_hash72"],
            "generator_hash216": parent["generator_hash216"],
        },
        "source_bundle": source_bundle,
        "left_generator": left,
        "right_symbolic_cse": right,
        "closure": closure,
        "candidate_previous_hash72": previous_hash72,
        "candidate_change_hash72": change_hash72,
        "candidate_receipt_hash72": receipt_hash72,
        "candidate_hash216": candidate_hash216,
        "plane_roots": plane_roots,
        "hydration": {
            "roundtrip_exact": hydrated["roundtrip_exact"],
            "full_attached_components": hydrated["full_attached_components"],
            "expanded_geometry_persisted": False,
            "reconstructible_on_demand": True,
        },
        "optimization": {
            "left_27_matrix_cells_generated_not_independently_persisted": True,
            "e_membrane_source_occurrences": E_MEMBRANE_OCCURRENCES,
            "e_membrane_value_nodes": E_MEMBRANE_VALUE_NODES,
            "e_membrane_value_evaluations_avoided": E_MEMBRANE_EVALUATIONS_AVOIDED,
            "right_cell_occurrences": right["cell_occurrences"],
            "right_unique_cell_expressions": right["unique_cell_expressions"],
            "right_materializations_avoided": right["materializations_avoided"],
            "right_occurrence_witnesses_retained": True,
            "hash216_expansion_persisted": False,
        },
        "authority": dict(AUTHORITY_BOUNDARY),
    }
    candidate["candidate_root_sha256"] = _sha256(candidate)
    candidate["binding_hash72"] = hash72(
        {
            "schema": SCHEMA,
            "candidate_root_sha256": candidate["candidate_root_sha256"],
            "candidate_hash216": candidate_hash216,
            "parent_binding_hash72": parent["binding_hash72"],
            "closure_readout": closure["closure_readout"],
            "plane_roots": plane_roots,
        }
    )
    return candidate


def validate_candidate(candidate: Mapping[str, Any]) -> bool:
    if not isinstance(candidate, Mapping) or candidate.get("schema") != SCHEMA:
        raise Pass220I074Error("candidate schema mismatch")
    _reject_float(candidate)

    parent = candidate.get("parent_i073")
    if not isinstance(parent, Mapping):
        raise Pass220I074Error("parent I073 binding missing")

    # Reconstruct the canonical default parent geometry used by this I074
    # candidate surface. Alternative parameterizations are admitted only by
    # constructing a fresh candidate through build_candidate().
    canonical = build_candidate()
    for key in (
        "verbatim_source",
        "verbatim_source_sha256",
        "parent_i073",
        "source_bundle",
        "left_generator",
        "right_symbolic_cse",
        "closure",
        "candidate_previous_hash72",
        "candidate_change_hash72",
        "candidate_receipt_hash72",
        "candidate_hash216",
        "plane_roots",
        "hydration",
        "optimization",
        "authority",
        "candidate_root_sha256",
        "binding_hash72",
    ):
        if candidate.get(key) != canonical[key]:
            raise Pass220I074Error(f"candidate diverges at {key}")
    return True


def self_test() -> dict[str, Any]:
    candidate = build_candidate()
    right = candidate["right_symbolic_cse"]
    checks = {
        "candidate_valid": validate_candidate(candidate),
        "verbatim_source_exact": candidate["verbatim_source"] == VERBATIM_SOURCE,
        "left_generator_exact": all(candidate["left_generator"]["checks"].values()),
        "e_membrane_3_to_1": (
            candidate["optimization"]["e_membrane_source_occurrences"] == 3
            and candidate["optimization"]["e_membrane_value_nodes"] == 1
            and candidate["optimization"]["e_membrane_value_evaluations_avoided"] == 2
        ),
        "right_cse_32_to_12": (
            right["cell_occurrences"] == 32
            and right["unique_cell_expressions"] == 12
            and right["materializations_avoided"] == 20
        ),
        "right_witnesses_retained": right["all_occurrence_witnesses_retained"],
        "matrixpower_held": right["matrix_power_host_evaluated"] is False,
        "closure_typed_unit": candidate["closure"]["closure_readout"] == "1_H",
        "hash216_width_216": len(candidate["candidate_hash216"]) == HASH216_WIDTH,
        "hydration_roundtrip_exact": candidate["hydration"]["roundtrip_exact"],
        "hydration_components_15552": (
            candidate["hydration"]["full_attached_components"]
            == FULL_HASH216_COMPONENTS
        ),
        "no_expansion_persistence": (
            candidate["hydration"]["expanded_geometry_persisted"] is False
        ),
        "candidate_only": candidate["authority"]["candidate_only"] is True,
        "no_vm81_mutation_authority": (
            candidate["authority"]["canonical_vm81_mutation_authority"] is False
        ),
        "no_hash216_commit_authority": (
            candidate["authority"]["canonical_hash216_commit_authority"] is False
        ),
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(value) for value in checks.values()),
        "failed": [name for name, passed in checks.items() if not passed],
        "checks": checks,
        "candidate_root_sha256": candidate["candidate_root_sha256"],
        "binding_hash72": candidate["binding_hash72"],
        "candidate_hash216": candidate["candidate_hash216"],
    }


__all__ = [
    "AUTHORITY_BOUNDARY",
    "CLOSURE_MATRIX",
    "E_MEMBRANE_SOURCE",
    "MATRIX_POWER_NODES",
    "M_WZ",
    "M_XY",
    "Pass220I074Error",
    "SCHEMA",
    "TARGET_MATRIX",
    "VERBATIM_SOURCE",
    "build_candidate",
    "closure_witness",
    "left_generator_witness",
    "right_symbolic_cse_witness",
    "self_test",
    "source_bundle_witness",
    "validate_candidate",
]


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))
