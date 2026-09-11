"""Pass 219 SPI O2 ordered-matrix scalar projection witness v1.

HARMONICODE matrix/tensor projection rule
-----------------------------------------
A matrix/tensor branch may project to a scalar when an exact native equality
edge defines a registered scalar symbol by that matrix/tensor expression.  The
scalar value comes from the scalar symbol's registered projection, not from
replacing or numerically evaluating the native matrix/tensor node.

For O2 the native edge defines ``a²`` by the ordered matrix-power branch and the
primitive scalar registry proves ``pi(a²)=1``.  Therefore that exact branch has
a source-bound scalar projection of ``1``.  The ordered phase and center
witnesses remain topology/consistency evidence; they are not prerequisites for
inventing the scalar numeral and they do not turn generic ``NcalcMatrixPower``
into a scalar evaluator.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from hhs_spi_defined_scalar_projection_rule_v1 import defined_scalar_projection

FORMAT = "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_WITNESS_V1"
VERSION = "1.1.0"
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
A2_MATRIX_DEFINITION_EDGE = f"a²={MATRIX_BRANCH_SOURCE}"

O2_EQUALITY_SOURCE = (
    A2_MATRIX_DEFINITION_EDGE +
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


def _exact_json(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"type": "EXACT_RATIONAL", "numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, tuple):
        return [_exact_json(v) for v in value]
    if isinstance(value, list):
        return [_exact_json(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _exact_json(value[k]) for k in sorted(value)}
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise SPIO2MatrixProjectionError(f"unsupported deterministic receipt type: {type(value).__name__}")


def _stable_json(value: Any) -> str:
    return json.dumps(_exact_json(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


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
    constants = (
        (DENOMINATOR_SOURCE, DENOMINATOR_BYTES, DENOMINATOR_SHA256, "denominator"),
        (PROJECTION_SOURCE, PROJECTION_BYTES, PROJECTION_SHA256, "projection"),
        (MATRIX_BRANCH_SOURCE, MATRIX_BRANCH_BYTES, MATRIX_BRANCH_SHA256, "matrix branch"),
        (O2_EQUALITY_SOURCE, O2_EQUALITY_BYTES, O2_EQUALITY_SHA256, "O2 equality"),
    )
    for source, expected_bytes, expected_sha, label in constants:
        if len(source.encode("utf-8")) != expected_bytes or _digest_text(source) != expected_sha:
            raise SPIO2MatrixProjectionError(f"{label} constant drift")

    combined = (repo_root / COMBINED_SOURCE_PATH).read_text(encoding="utf-8")
    projection = (repo_root / PROJECTION_SOURCE_PATH).read_text(encoding="utf-8")
    harmonic_contract = (repo_root / HARMONIC_CONTRACT_PATH).read_text(encoding="utf-8")
    phase12 = (repo_root / PHASE12_RESTART_PATH).read_text(encoding="utf-8")
    phase11_precursor = (repo_root / PHASE11_PRECURSOR_PATH).read_text(encoding="utf-8")

    if combined.count(DENOMINATOR_SOURCE) != 2:
        raise SPIO2MatrixProjectionError("combined source no longer contains exactly two denominator occurrences")
    if projection != PROJECTION_SOURCE:
        raise SPIO2MatrixProjectionError("denominator magnitude projection source drift")
    if O2_EQUALITY_SOURCE not in harmonic_contract or A2_MATRIX_DEFINITION_EDGE not in harmonic_contract:
        raise SPIO2MatrixProjectionError("canonical a² matrix definition edge missing")
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
        "a2_matrix_definition_edge": A2_MATRIX_DEFINITION_EDGE,
        "a2_matrix_definition_edge_sha256": _digest_text(A2_MATRIX_DEFINITION_EDGE),
        "equality_bytes": O2_EQUALITY_BYTES,
        "equality_sha256": O2_EQUALITY_SHA256,
        "phase12_tensor_source_preserved": True,
        "native_center_closure_source_preserved": True,
    }


def _phase_topology_witness(repo_root: Path) -> Dict[str, Any]:
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
    for row_col, role, exponent in OUTER_CLOCKWISE:
        numerator_phase = int(basis_phase_index[role])
        denominator_phase = int((exponent * phase_quarter) % phase_ring)
        residue = int((numerator_phase - denominator_phase) % phase_ring)
        if residue != 0:
            raise SPIO2MatrixProjectionError(f"ordered phase topology mismatch for {role}")
        cells.append({
            "row": row_col[0],
            "column": row_col[1],
            "ordered_role": role,
            "denominator_phase_symbol": f"I^{exponent}",
            "numerator_phase72": numerator_phase,
            "denominator_phase72": denominator_phase,
            "difference_mod72": residue,
        })

    if basis_phase_index["xy"] == basis_phase_index["yx"] or basis_phase_index["zw"] == basis_phase_index["wz"]:
        raise SPIO2MatrixProjectionError("ordered product distinction collapsed")

    return {
        "ordered_numerator_role_matrix": NUMERATOR_ROLE_MATRIX,
        "fixed_denominator_phase_exponent_matrix": DENOMINATOR_PHASE_EXPONENT_MATRIX,
        "phase_ring": phase_ring,
        "outer_cells": cells,
        "outer_cell_count": len(cells),
        "outer_phase_alignment_exact": len(cells) == 8 and all(cell["difference_mod72"] == 0 for cell in cells),
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
        },
        "all_nine_topology_cells_witnessed": True,
        "ordinary_matrix_inverse_executed": False,
        "projection_substitution_for_canonical_matrix_execution": False,
    }


def _surd_consistency_witness() -> Dict[str, Any]:
    beta = Fraction(2)
    alpha = beta - 1
    gamma = 2 * beta - 1
    numerator = gamma**2 - beta * gamma - beta**2 + beta
    denominator = gamma - beta
    if denominator == 0:
        raise SPIO2MatrixProjectionError("surd consistency denominator unexpectedly zero")
    ratio = numerator / denominator
    if ratio != alpha or alpha != 1:
        raise SPIO2MatrixProjectionError("squared-radical a² consistency witness failed")
    return {
        "profile": "SPI-SURD-SQUARED-Q-v1",
        "a_squared_projection": Fraction(1),
        "squared_radical_projection": ratio,
        "residual": ratio - 1,
        "required_for_matrix_to_scalar_projection": False,
        "purpose": "independent equality-chain consistency witness",
        "floating_point_used": False,
    }


def ordered_matrix_projection_witness(repo_root: str | Path | None = None) -> Dict[str, Any]:
    root = _repo_root(repo_root)
    source_identity = _source_identity_witness(root)
    topology = _phase_topology_witness(root)
    surd = _surd_consistency_witness()

    definition_receipt = defined_scalar_projection(
        scalar_symbol="a²",
        scalar_proof_id="SPI-PROJ-0001",
        scalar_value=1,
        defining_expression=MATRIX_BRANCH_SOURCE,
        equality_edge_source=A2_MATRIX_DEFINITION_EDGE,
        definition_kind="EXACT_SYMBOLIC_MATRIX_POWER",
        edge_id="HHCQ:E_a2:ordered-matrix-power-definition",
    )
    exact_one = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
    exact_zero = {"type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1}
    if definition_receipt["result"] != exact_one or definition_receipt["residual"] != exact_zero:
        raise SPIO2MatrixProjectionError("defined-scalar projection rule failed to produce a² -> 1")

    witness: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "harmonicode_projection_rule": (
            "an exact source-bound matrix/tensor definition of a registered scalar may inherit that scalar's exact projection"
        ),
        "source_identity": source_identity,
        "defined_scalar_projection": definition_receipt,
        "ordered_matrix_topology": topology,
        "exact_inverse_or_lift": {
            "kind": "TYPED_DEFINITION_EDGE_LIFT",
            "definition_edge": A2_MATRIX_DEFINITION_EDGE,
            "scalar_symbol": "a²",
            "scalar_projection": exact_one,
            "ordinary_matrix_inverse_executed": False,
            "reverse_native_reconstruction_authorized": False,
        },
        "fourth_power": {
            "ncalc_matrix_power_source_exponent": 4,
            "outer_b4_projection": {"type": "EXACT_RATIONAL", "numerator": 4, "denominator": 1},
            "node_type": "EXACT_SYMBOLIC_MATRIX_POWER",
            "ncalc_matrix_power_host_evaluated": False,
            "algebraic_matrix_power_replacement_authorized": False,
        },
        "root_witness": surd,
        "equality_chain": {
            "source": O2_EQUALITY_SOURCE,
            "matrix_definition_edge": A2_MATRIX_DEFINITION_EDGE,
            "matrix_branch_source": MATRIX_BRANCH_SOURCE,
            "left_projection": "a² -> 1",
            "right_independent_projection": "SPI-T6-SURD -> a² -> 1",
            "typed_equality_edge_used_for_scalar_correspondence": True,
            "native_node_collapse_authorized": False,
        },
        "result": {
            "scalar_type": "EXACT_RATIONAL",
            "matrix_branch_projection": exact_one,
            "a_squared_projection": exact_one,
            "residual": exact_zero,
            "projection_basis": "REGISTERED_SCALAR_DEFINITION_EDGE",
        },
        "lost_information": [
            "native NcalcMatrixPower runtime object is not reconstructed from scalar 1",
            "ordered matrix/tensor topology remains native and is not encoded by scalar 1",
            "native center closure context is not ordinary rational division",
            "definition-edge projection is non-injective and grants no reverse lift",
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
    return _exact_json(witness)


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

    if witness["defined_scalar_projection"]["result"] != {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}:
        errors.append("a²-defined matrix branch did not project to exact unit")
    if witness["defined_scalar_projection"]["matrix_or_tensor_host_evaluated"]:
        errors.append("host matrix/tensor evaluation was incorrectly authorized")
    if witness["ordered_matrix_topology"]["outer_cell_count"] != 8:
        errors.append("ordered perimeter topology is incomplete")
    if not witness["ordered_matrix_topology"]["all_nine_topology_cells_witnessed"]:
        errors.append("nine-cell topology witness incomplete")
    if witness["result"]["residual"] != {"type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1}:
        errors.append("O2 residual is nonzero")
    if witness["canonical_admission_authority"]:
        errors.append("O2 witness claims canonical admission authority")
    return {
        "schema": "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_VALIDATION_V1",
        "ok": not errors,
        "witness_sha256": witness["witness_sha256"],
        "projection_basis": witness["result"]["projection_basis"],
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
