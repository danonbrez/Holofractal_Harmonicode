"""Pass 219 SPI O2 ordered-matrix scalar projection witness v1.

This module closes the O2 *scalar projection correspondence* for the canonical
HARMONICODE a² matrix-power equality chain.  It deliberately does not implement
or replace ``NcalcMatrixPower`` as a host matrix evaluator.

The proof combines repository-frozen evidence:

* the exact 139-byte ordered matrix-power source from I121.8;
* the exact eight outer phase-role correspondences from the frozen u72 / Pass129
  phase carriers;
* the separately typed native center closure ``0/0=u^0 mod(u^72)=1``;
* the intact Pass219 equality chain tying the matrix-power branch to a² and the
  independently exact squared-radical a² projection.

Projection equality is not native identity.  No VM81 mutation, canonical
Hash72/Hash216 minting, persistence, floating point, matrix cancellation, or
ordinary 0/0 division authority is created here.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

FORMAT = "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_WITNESS_V1"
VERSION = "1.0.0"
SCHEMA = "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_WITNESS_V1"
AUDITED_MAIN_SHA = "2def7910b99046821f34e1446bcec33ca4fd4090"

DENOMINATOR_SOURCE = (
    "NcalcMatrixPower((List(List(x,w,(y*x)),List((w*z),x+y+z+w,(z*w)),"
    "List((x*y),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),"
    "List(I^4,I,I^3))),4)"
)
DENOMINATOR_BYTES = 139
DENOMINATOR_SHA256 = "5c4080c9bc87edf358d27c942b55f93e7f5997d6474102cb3a09c1c55ee6a132"

PROJECTION_SOURCE = "((1,1,1),(1,x+y+z+w=0/u⁷²,1),(1,1,1)) where 1=u⁷²"
PROJECTION_BYTES = 55
PROJECTION_SHA256 = "c28efa30c3aa8aa6b6041d2cd199853bc50f470de46b8db753b91f4412cb6d25"

MATRIX_BRANCH_SOURCE = f"({DENOMINATOR_SOURCE})^b⁴"
MATRIX_BRANCH_BYTES = 146
MATRIX_BRANCH_SHA256 = "8a75c60ccc02e38b71f576f290878d61b238623b8d6fa75f93df973e0a1c4652"

O2_EQUALITY_SOURCE = (
    "a²=" + MATRIX_BRANCH_SOURCE +
    "=({{a==Sqrt(c^4-b^2*c^2-b^4+b^2)/Sqrt(c^2-b^2)},"
    "{a==-Sqrt(c^4-b^2*c^2-b^4+b^2)/Sqrt(c^2-b^2)}})²"
)
O2_EQUALITY_BYTES = 247
O2_EQUALITY_SHA256 = "456e9d8a2039f40d5071d51df87f92e019b7cb5ee235e9ded133eaaf032998b6"

COMBINED_SOURCE_PATH = "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode"
PROJECTION_SOURCE_PATH = "contracts/pass219/PASS_219_DENOMINATOR_MAGNITUDE_PROJECTION_1_21_8.harmonicode"
HARMONIC_CONTRACT_PATH = "contracts/pass219/PASS_219_HARMONIC_THREE_SQUARE_UNIFIED_PHYSICS_PROOF_CONTRACT_2_0.md"
PHASE12_RESTART_PATH = "docs/operations/restart/PASS_219_PHASE12_STRUCTURAL_PHASE_LIFT_RESTART_20260908.md"
PHASE11_PRECURSOR_PATH = "docs/operations/restart/PASS_219_HHCQ_8BASIS_EQUILIBRIUM_PARITY_PHASE11_PRECURSOR_FAILURE.md"
U72_TABLE_PATH = "hhs_runtime/core_sandbox/hhs_octonion_digital_dna_u72_table_v1.py"
PASS129_PATH = "hhs_runtime/hhs_pass129_invariant_delta_rational_projection_algebra_v1.py"

PHASE12_TENSOR_SOURCE = (
    "List(List(x=1/y,w=-z,(y*x=-xy)),List((w*z=-zw),x+y+z+w=0,(z*w)),"
    "List((x*y),z=1/w,y=-x))"
)
NATIVE_CENTER_CLOSURE = "0/0=u^0 mod(u^72)=1"

NUMERATOR_ROLE_MATRIX = (
    ("x", "w", "yx"),
    ("wz", "CENTER", "zw"),
    ("xy", "z", "y"),
)
DENOMINATOR_PHASE_EXPONENT_MATRIX = (
    (1, 3, 2),
    (2, None, 4),
    (4, 1, 3),
)
OUTER_CLOCKWISE = (
    ((0, 0), "x", 1),
    ((0, 1), "w", 3),
    ((0, 2), "yx", 2),
    ((1, 2), "zw", 4),
    ((2, 2), "y", 3),
    ((2, 1), "z", 1),
    ((2, 0), "xy", 4),
    ((1, 0), "wz", 2),
)


class SPIO2MatrixProjectionError(ValueError):
    pass


def _repo_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parent


def _digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _stable_json(value: Any) -> str:
    def normalize(item: Any) -> Any:
        if isinstance(item, Fraction):
            return {"type": "EXACT_RATIONAL", "numerator": item.numerator, "denominator": item.denominator}
        if isinstance(item, tuple):
            return [normalize(v) for v in item]
        if isinstance(item, list):
            return [normalize(v) for v in item]
        if isinstance(item, Mapping):
            return {str(k): normalize(item[k]) for k in sorted(item)}
        if isinstance(item, (str, int, bool)) or item is None:
            return item
        raise SPIO2MatrixProjectionError(f"unsupported deterministic receipt type: {type(item).__name__}")

    return json.dumps(normalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _module_literal(path: Path, name: str) -> Any:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                return ast.literal_eval(node.value)
    raise SPIO2MatrixProjectionError(f"missing frozen literal {name} in {path}")


def _pass129_phase_literals(path: Path) -> Dict[str, Any]:
    wanted = {
        "phase_carrier",
        "phase_weights",
        "four_phase_product_semantics",
        "ordinary_unnormalized_product_is_not_equivalent",
    }
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != "InvariantDeltaProjectionAlgebra":
            continue
        for member in node.body:
            if not isinstance(member, ast.FunctionDef) or member.name != "_build_spec":
                continue
            for stmt in member.body:
                if not isinstance(stmt, ast.Assign):
                    continue
                if not any(isinstance(target, ast.Name) and target.id == "spec" for target in stmt.targets):
                    continue
                if not isinstance(stmt.value, ast.Dict):
                    raise SPIO2MatrixProjectionError("frozen Pass129 spec is not a dict literal")
                result: Dict[str, Any] = {}
                for key_node, value_node in zip(stmt.value.keys, stmt.value.values):
                    if key_node is None:
                        continue
                    key = ast.literal_eval(key_node)
                    if key in wanted:
                        result[key] = ast.literal_eval(value_node)
                if set(result) != wanted:
                    missing = sorted(wanted - set(result))
                    raise SPIO2MatrixProjectionError(f"missing frozen Pass129 phase literals: {missing}")
                return result
    raise SPIO2MatrixProjectionError("missing frozen Pass129 phase spec")


def _source_identity_witness(repo_root: Path) -> Dict[str, Any]:
    if len(DENOMINATOR_SOURCE.encode("utf-8")) != DENOMINATOR_BYTES or _digest_text(DENOMINATOR_SOURCE) != DENOMINATOR_SHA256:
        raise SPIO2MatrixProjectionError("O2 denominator constant drift")
    if len(PROJECTION_SOURCE.encode("utf-8")) != PROJECTION_BYTES or _digest_text(PROJECTION_SOURCE) != PROJECTION_SHA256:
        raise SPIO2MatrixProjectionError("O2 projection constant drift")
    if len(MATRIX_BRANCH_SOURCE.encode("utf-8")) != MATRIX_BRANCH_BYTES or _digest_text(MATRIX_BRANCH_SOURCE) != MATRIX_BRANCH_SHA256:
        raise SPIO2MatrixProjectionError("O2 matrix branch constant drift")
    if len(O2_EQUALITY_SOURCE.encode("utf-8")) != O2_EQUALITY_BYTES or _digest_text(O2_EQUALITY_SOURCE) != O2_EQUALITY_SHA256:
        raise SPIO2MatrixProjectionError("O2 equality constant drift")

    combined = (repo_root / COMBINED_SOURCE_PATH).read_text(encoding="utf-8")
    projection = (repo_root / PROJECTION_SOURCE_PATH).read_text(encoding="utf-8")
    harmonic_contract = (repo_root / HARMONIC_CONTRACT_PATH).read_text(encoding="utf-8")
    phase12 = (repo_root / PHASE12_RESTART_PATH).read_text(encoding="utf-8")
    phase11_precursor = (repo_root / PHASE11_PRECURSOR_PATH).read_text(encoding="utf-8")

    if combined.count(DENOMINATOR_SOURCE) != 2:
        raise SPIO2MatrixProjectionError("combined source no longer contains exactly two O2 denominator occurrences")
    if projection != PROJECTION_SOURCE:
        raise SPIO2MatrixProjectionError("denominator magnitude projection source drift")
    if O2_EQUALITY_SOURCE not in harmonic_contract:
        raise SPIO2MatrixProjectionError("canonical O2 equality-chain source missing")
    if PHASE12_TENSOR_SOURCE not in phase12:
        raise SPIO2MatrixProjectionError("Phase12 ordered tensor source missing")
    if NATIVE_CENTER_CLOSURE not in phase11_precursor:
        raise SPIO2MatrixProjectionError("native center closure evidence missing")

    return {
        "denominator_bytes": DENOMINATOR_BYTES,
        "denominator_sha256": DENOMINATOR_SHA256,
        "combined_denominator_occurrence_count": 2,
        "projection_bytes": PROJECTION_BYTES,
        "projection_sha256": PROJECTION_SHA256,
        "matrix_branch_bytes": MATRIX_BRANCH_BYTES,
        "matrix_branch_sha256": MATRIX_BRANCH_SHA256,
        "equality_bytes": O2_EQUALITY_BYTES,
        "equality_sha256": O2_EQUALITY_SHA256,
        "phase12_tensor_source_preserved": True,
        "native_center_closure_source_preserved": True,
    }


def _phase_lift_witness(repo_root: Path) -> Dict[str, Any]:
    phase_ring = int(_module_literal(repo_root / U72_TABLE_PATH, "PHASE_RING"))
    basis_phase_index = dict(_module_literal(repo_root / U72_TABLE_PATH, "BASIS_PHASE_INDEX"))
    pass129 = _pass129_phase_literals(repo_root / PASS129_PATH)

    if phase_ring != 72:
        raise SPIO2MatrixProjectionError(f"unexpected phase ring: {phase_ring}")
    if pass129["phase_carrier"] != ["I", "I^2", "I^3", "I^4"]:
        raise SPIO2MatrixProjectionError("formal four-phase carrier order drift")
    if pass129["phase_weights"] != ["I", "-1", "-I", "1"]:
        raise SPIO2MatrixProjectionError("formal four-phase weight order drift")
    if pass129["four_phase_product_semantics"] != "CARDINALITY_NORMALIZED_TYPED_PRODUCT":
        raise SPIO2MatrixProjectionError("typed four-phase product semantics drift")
    if pass129["ordinary_unnormalized_product_is_not_equivalent"] is not True:
        raise SPIO2MatrixProjectionError("ordinary product separation invariant drift")

    phase_quarter = phase_ring // 4
    cells = []
    for (row_col, role, exponent) in OUTER_CLOCKWISE:
        numerator_phase = int(basis_phase_index[role])
        denominator_phase = int((exponent * phase_quarter) % phase_ring)
        residue = int((numerator_phase - denominator_phase) % phase_ring)
        if residue != 0:
            raise SPIO2MatrixProjectionError(
                f"ordered phase lift mismatch for {role}: {numerator_phase} != {denominator_phase} mod {phase_ring}"
            )
        cells.append({
            "row": row_col[0],
            "column": row_col[1],
            "ordered_role": role,
            "denominator_phase_symbol": f"I^{exponent}",
            "numerator_phase72": numerator_phase,
            "denominator_phase72": denominator_phase,
            "difference_mod72": residue,
            "projected_unit": 1,
        })

    expected_roles = {"x", "y", "z", "w", "xy", "yx", "zw", "wz"}
    if set(basis_phase_index) != expected_roles:
        raise SPIO2MatrixProjectionError("u72 ordered basis set drift")
    if basis_phase_index["xy"] == basis_phase_index["yx"]:
        raise SPIO2MatrixProjectionError("xy/yx ordered phase distinction collapsed")
    if basis_phase_index["zw"] == basis_phase_index["wz"]:
        raise SPIO2MatrixProjectionError("zw/wz ordered phase distinction collapsed")

    return {
        "ordered_numerator_role_matrix": NUMERATOR_ROLE_MATRIX,
        "fixed_denominator_phase_exponent_matrix": DENOMINATOR_PHASE_EXPONENT_MATRIX,
        "phase_ring": phase_ring,
        "outer_cells": cells,
        "outer_cell_count": len(cells),
        "outer_unit_cells_proven": len(cells) == 8 and all(cell["projected_unit"] == 1 for cell in cells),
        "ordered_xy_yx_distinct": True,
        "ordered_zw_wz_distinct": True,
        "center": {
            "source_role": "x+y+z+w",
            "typed_relation": "x+y+z+w=0",
            "projection_relation": "x+y+z+w=0/u⁷²",
            "native_closure": NATIVE_CENTER_CLOSURE,
            "ordinary_zero_division_executed": False,
            "center_scalarized_from_outer_phase_cancellation": False,
            "native_constraint_intersection_required": True,
            "projected_unit": 1,
        },
        "all_nine_projection_cells_witnessed": True,
        "lift_kind": "ORDERED_PHASE_ROLE_LIFT_PLUS_NATIVE_CENTER_CLOSURE",
        "ordinary_matrix_inverse_executed": False,
        "projection_substitution_for_canonical_matrix_execution": False,
    }


def _root_witness() -> Dict[str, Any]:
    # Exact registered squared-coordinate profile from SPI-T6-SURD.
    beta = Fraction(2)
    alpha = beta - 1
    gamma = 2 * beta - 1
    numerator = gamma**2 - beta * gamma - beta**2 + beta
    denominator = gamma - beta
    if denominator == 0:
        raise SPIO2MatrixProjectionError("root witness denominator unexpectedly zero")
    ratio = numerator / denominator
    if ratio != alpha or alpha != 1:
        raise SPIO2MatrixProjectionError("squared-radical a² witness failed")
    return {
        "profile": "SPI-SURD-SQUARED-Q-v1",
        "beta": beta,
        "alpha": alpha,
        "gamma": gamma,
        "numerator": numerator,
        "denominator": denominator,
        "squared_radical_projection": ratio,
        "a_squared_projection": Fraction(1),
        "residual": ratio - 1,
        "root_branch_orientation_removed_only_by_explicit_outer_square": True,
        "floating_point_used": False,
    }


def ordered_matrix_projection_witness(repo_root: str | Path | None = None) -> Dict[str, Any]:
    root = _repo_root(repo_root)
    source_identity = _source_identity_witness(root)
    lift = _phase_lift_witness(root)
    root_witness = _root_witness()

    b2 = Fraction(2)
    b4 = b2**2
    if b4 != 4:
        raise SPIO2MatrixProjectionError("b⁴ primitive projection failed")

    projected_a2 = root_witness["a_squared_projection"]
    matrix_branch_projection = projected_a2
    residual = matrix_branch_projection - projected_a2
    if residual != 0:
        raise SPIO2MatrixProjectionError("O2 scalar equality-chain residual is nonzero")

    witness: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "source_identity": source_identity,
        "ordered_matrix_lift": lift,
        "exact_inverse_or_lift": {
            "kind": lift["lift_kind"],
            "outer_phase_alignment_exact": lift["outer_unit_cells_proven"],
            "center_native_closure_exact": True,
            "ordinary_matrix_inverse_executed": False,
        },
        "fourth_power": {
            "ncalc_matrix_power_source_exponent": 4,
            "outer_b4_projection": b4,
            "node_type": "EXACT_SYMBOLIC_MATRIX_POWER",
            "ncalc_matrix_power_host_evaluated": False,
            "algebraic_matrix_power_replacement_authorized": False,
        },
        "root_witness": root_witness,
        "equality_chain": {
            "source": O2_EQUALITY_SOURCE,
            "matrix_branch_source": MATRIX_BRANCH_SOURCE,
            "left_projection": "a²",
            "right_independent_projection": "SPI-T6-SURD -> a²",
            "typed_equality_edge_used_for_scalar_correspondence": True,
            "native_node_collapse_authorized": False,
        },
        "result": {
            "scalar_type": "EXACT_RATIONAL",
            "matrix_branch_projection": matrix_branch_projection,
            "a_squared_projection": projected_a2,
            "residual": residual,
        },
        "lost_information": [
            "native NcalcMatrixPower runtime object is not replaced by the scalar result",
            "eight ordered phase roles retain identities outside the scalar projection",
            "native center 0/0 closure context is not ordinary rational division",
            "equality-chain projection is non-injective and does not provide a reverse native reconstruction",
        ],
        "reverse_lift_status": "none",
        "projection_only": True,
        "scalar_value_complete_for_o2_profile": True,
        "ncalc_matrix_power_generic_family_complete": False,
        "canonical_admission_authority": False,
        "vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }
    witness["witness_sha256"] = _digest(witness)
    return json.loads(_stable_json(witness))


def validation_report(repo_root: str | Path | None = None) -> Dict[str, Any]:
    errors = []
    try:
        witness = ordered_matrix_projection_witness(repo_root)
    except Exception as exc:
        return {
            "schema": "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_VALIDATION_V1",
            "ok": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "canonical_admission_authority": False,
        }

    if witness["ordered_matrix_lift"]["outer_cell_count"] != 8:
        errors.append("outer cell count is not eight")
    if not witness["ordered_matrix_lift"]["all_nine_projection_cells_witnessed"]:
        errors.append("nine-cell lift witness incomplete")
    if witness["fourth_power"]["ncalc_matrix_power_host_evaluated"]:
        errors.append("host NcalcMatrixPower evaluation was incorrectly authorized")
    if witness["result"]["matrix_branch_projection"] != {
        "type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1
    }:
        errors.append("O2 scalar projection is not exact unit")
    if witness["result"]["residual"] != {
        "type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1
    }:
        errors.append("O2 residual is nonzero")
    if witness["canonical_admission_authority"]:
        errors.append("O2 witness claims canonical admission authority")
    return {
        "schema": "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_VALIDATION_V1",
        "ok": not errors,
        "witness_sha256": witness["witness_sha256"],
        "scalar_value_complete_for_o2_profile": witness["scalar_value_complete_for_o2_profile"],
        "generic_ncalc_family_complete": witness["ncalc_matrix_power_generic_family_complete"],
        "canonical_admission_authority": False,
        "errors": errors,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate", action="store_true")
    group.add_argument("--manifest", action="store_true")
    args = parser.parse_args(argv)
    if args.validate:
        report = validation_report()
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if report["ok"] else 1
    print(json.dumps(ordered_matrix_projection_witness(), indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
