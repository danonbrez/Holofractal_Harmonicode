"""Pass 219 I121.8 combined-equation test and optimization surface.

This module is deliberately read-only and candidate-only.  It does not replace
Pass169 whole-expression authority, evaluate NcalcMatrixPower independently, or
rewrite the supplied HARMONICODE equation algebraically.

The optimization proved here is structural common-subexpression reuse: the exact
same denominator MatrixPower source occurs twice in the combined equation, so a
future admitted runtime may compute that immutable exact subexpression once and
reuse its result for the LHS denominator and RHS comparison.  The user-supplied
3x3 denominator magnitude projection is bound as an expected projection witness,
not substituted for canonical evaluation.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight

VERSION = "PASS_219_I121_8_COMBINED_EQUATION_OPTIMIZER_V1"
SCHEMA = "HHS_PASS_219_I121_8_COMBINED_EQUATION_OPTIMIZER_V1"
CLASSIFICATION = "KERNEL_DERIVED_READ_ONLY_OPTIMIZATION_CANDIDATE"
DECISION = "PASS169_WHOLE_EXPRESSION_AUTHORITY_REQUIRED"

NUMERATOR_PATH = Path("contracts/pass219/PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode")
COMBINED_PATH = Path("contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode")
PROJECTION_PATH = Path("contracts/pass219/PASS_219_DENOMINATOR_MAGNITUDE_PROJECTION_1_21_8.harmonicode")

NUMERATOR_BYTES = 348
NUMERATOR_SHA256 = "ac143798146d89a3fe932f39ccb4d612e4fb3e45c471abc1a8bbbebb0f9c0a6a"
DENOMINATOR_BYTES = 139
DENOMINATOR_SHA256 = "5c4080c9bc87edf358d27c942b55f93e7f5997d6474102cb3a09c1c55ee6a132"
COMBINED_BYTES = 632
COMBINED_SHA256 = "3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53"
PROJECTION_BYTES = 55
PROJECTION_SHA256 = "c28efa30c3aa8aa6b6041d2cd199853bc50f470de46b8db753b91f4412cb6d25"

DENOMINATOR_SOURCE = (
    "NcalcMatrixPower((List(List(x,w,(y*x)),List((w*z),x+y+z+w,(z*w)),"
    "List((x*y),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),"
    "List(I^4,I,I^3))),4)"
)
NUMERATOR_MATRIX_SOURCE = (
    "List(List(x,w,(y*x)),List((w*z),x+y+z+w,(z*w)),List((x*y),z,y))"
)
PHASE_MATRIX_SOURCE = (
    "List(List(I,I^3,I^2),List(I^2,0,I^4),List(I^4,I,I^3))"
)
PROJECTION_SOURCE = "((1,1,1),(1,x+y+z+w=0/u⁷²,1),(1,1,1)) where 1=u⁷²"

PERIMETER_CLOCKWISE = ("x", "w", "y*x", "z*w", "y", "z", "x*y", "w*z")
XY_RING = ("x", "y*x", "y", "x*y")
ZW_RING = ("w", "z*w", "z", "w*z")
CENTER_RELATION = "x+y+z+w=0/u⁷²"

SURFACE_ID = "validator:pass219.i121.combined-equation-optimizer"
SURFACE_SYMBOL = "verify_combined_equation_optimizer"


def _repo_root(root: str | Path | None = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[2]


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _read_exact(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def combined_optimizer_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.core_sandbox.hhs_pass219_combined_equation_optimizer_1_21_8",
        "symbol": SURFACE_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            SCHEMA,
            "HHS_PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20",
            "PASS_219B_PHASE_QUANTIZED_SELECTIVE_HYDRATION_1_0",
            "HHS_PASS_169_HARMONICODE_SYNTAX_ALGEBRA_ENFORCEMENT_AND_VM81_EXACT_SYMBOLIC_CONSTRAINT_PROOF_RUNTIME",
        ],
        "witness_schemas": [
            "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
            "HHS_PASS_219_I121_8_REPEATED_DENOMINATOR_IDENTITY_V1",
            "HHS_PASS_219_I121_8_DENOMINATOR_MAGNITUDE_PROJECTION_V1",
        ],
        "validators": [
            SURFACE_SYMBOL,
            "exact_repeated_subexpression_identity",
            "ordered_perimeter_ring_identity",
            "denominator_projection_identity",
        ],
        "guards": [
            "runtime_constraint_enforcement",
            "zero_bypass_runtime_interposer",
            "kernel_runtime_autocomposer",
            "pass169_whole_expression_authority_gate",
            "no_algebraic_cancellation_gate",
            "no_projection_substitution_gate",
            "ordered_noncommutative_product_gate",
        ],
        "rejection_codes": [
            "REJECT_I1218_SOURCE_IDENTITY_DRIFT",
            "REJECT_I1218_DENOMINATOR_IDENTITY_DRIFT",
            "REJECT_I1218_ORDERED_PRODUCT_COLLAPSE",
            "REJECT_I1218_PROJECTION_DRIFT",
            "REJECT_I1218_AUTHORITY_PROMOTION",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "NO_PERSISTENCE_MUTATION",
        "boundedness_policy": "STRUCTURAL_CSE_AND_PROJECTION_WITNESS_ONLY",
        "declared_operations": [SURFACE_SYMBOL],
    }


def preflight_combined_optimizer(
    *, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    result = execute_surface_preflight(
        combined_optimizer_surface_declaration(),
        operation=SURFACE_SYMBOL,
        cache=cache if cache is not None else {},
    )
    if result.get("ok") is not True:
        raise RuntimeError("PASS219_I1218_KERNEL_PREFLIGHT_REJECTED")
    pipeline = result.get("composition_plan", {}).get("pipeline", {})
    required_path = [
        "kernel_conformance_decision",
        "runtime_constraint_enforcement",
        "zero_bypass_runtime_interposer",
    ]
    if pipeline.get("enforcement_path") != required_path:
        raise RuntimeError("PASS219_I1218_ENFORCEMENT_PATH_DRIFT")
    if result.get("expanded_metadata_persisted") is not False:
        raise RuntimeError("PASS219_I1218_PERSISTENCE_DRIFT")
    return result


def verify_combined_equation_optimizer(
    root: str | Path | None = None,
    *, combined_override: Optional[str] = None,
    projection_override: Optional[str] = None,
    cache: Optional[MutableMapping[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    preflight = preflight_combined_optimizer(cache=cache)
    repo = _repo_root(root)

    numerator = _read_exact(repo / NUMERATOR_PATH)
    combined = combined_override if combined_override is not None else _read_exact(repo / COMBINED_PATH)
    projection = projection_override if projection_override is not None else _read_exact(repo / PROJECTION_PATH)

    if len(numerator.encode("utf-8")) != NUMERATOR_BYTES or _sha256_text(numerator) != NUMERATOR_SHA256:
        raise ValueError("REJECT_I1218_NUMERATOR_IDENTITY_DRIFT")
    if len(DENOMINATOR_SOURCE.encode("utf-8")) != DENOMINATOR_BYTES or _sha256_text(DENOMINATOR_SOURCE) != DENOMINATOR_SHA256:
        raise ValueError("REJECT_I1218_DENOMINATOR_CONSTANT_DRIFT")

    expected_combined = f"({numerator})/({DENOMINATOR_SOURCE})={DENOMINATOR_SOURCE}"
    if combined != expected_combined:
        raise ValueError("REJECT_I1218_SOURCE_IDENTITY_DRIFT")
    if len(combined.encode("utf-8")) != COMBINED_BYTES or _sha256_text(combined) != COMBINED_SHA256:
        raise ValueError("REJECT_I1218_COMBINED_HASH_DRIFT")
    if combined.count(DENOMINATOR_SOURCE) != 2:
        raise ValueError("REJECT_I1218_DENOMINATOR_OCCURRENCE_DRIFT")

    if NUMERATOR_MATRIX_SOURCE not in DENOMINATOR_SOURCE or PHASE_MATRIX_SOURCE not in DENOMINATOR_SOURCE:
        raise ValueError("REJECT_I1218_MATRIX_SOURCE_DRIFT")
    if "(y*x)" not in NUMERATOR_MATRIX_SOURCE or "(x*y)" not in NUMERATOR_MATRIX_SOURCE:
        raise ValueError("REJECT_I1218_XY_ORDER_COLLAPSE")
    if "(w*z)" not in NUMERATOR_MATRIX_SOURCE or "(z*w)" not in NUMERATOR_MATRIX_SOURCE:
        raise ValueError("REJECT_I1218_ZW_ORDER_COLLAPSE")

    if projection != PROJECTION_SOURCE:
        raise ValueError("REJECT_I1218_PROJECTION_DRIFT")
    if len(projection.encode("utf-8")) != PROJECTION_BYTES or _sha256_text(projection) != PROJECTION_SHA256:
        raise ValueError("REJECT_I1218_PROJECTION_HASH_DRIFT")
    if projection.count("1") != 9 or CENTER_RELATION not in projection or "where 1=u⁷²" not in projection:
        raise ValueError("REJECT_I1218_PROJECTION_SHAPE_DRIFT")

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "classification": CLASSIFICATION,
        "decision": DECISION,
        "ok": True,
        "preflight_ok": True,
        "combined_source_bytes": COMBINED_BYTES,
        "combined_source_sha256": COMBINED_SHA256,
        "numerator_source_bytes": NUMERATOR_BYTES,
        "numerator_source_sha256": NUMERATOR_SHA256,
        "denominator_source_bytes": DENOMINATOR_BYTES,
        "denominator_source_sha256": DENOMINATOR_SHA256,
        "denominator_occurrences": 2,
        "common_subexpression_identity_verified": True,
        "perimeter_clockwise": list(PERIMETER_CLOCKWISE),
        "xy_ring": list(XY_RING),
        "zw_ring": list(ZW_RING),
        "center_relation": CENTER_RELATION,
        "ordered_xy_yx_distinct": True,
        "ordered_zw_wz_distinct": True,
        "denominator_magnitude_projection_source": PROJECTION_SOURCE,
        "projection_outer_unit_cells": 8,
        "projection_center_cells": 1,
        "projection_unit_definition": "1=u⁷²",
        "baseline_denominator_evaluations": 2,
        "planned_denominator_evaluations": 1,
        "duplicate_denominator_evaluations_eliminated": 1,
        "compute_denominator_once_candidate": True,
        "reuse_same_denominator_identity_on_lhs_and_rhs": True,
        "baseline_projection_cell_checks": 9,
        "candidate_projection_orbit_representatives": 3,
        "candidate_projection_checks_eliminated": 6,
        "projection_representatives": ["xy-ring", "zw-ring", "center"],
        "projection_fast_path_candidate_only": True,
        "projection_derivation_authority": False,
        "projection_substitution_authorized": False,
        "algebraic_cancellation_authorized": False,
        "ordinary_scalar_squaring_authorized": False,
        "ncalc_matrix_power_reimplemented": False,
        "floating_point_authority": False,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "persistence_mutation_authority": False,
        "canonical_monolithic_proof": False,
        "pass169_whole_expression_admission_required": True,
        "preflight": preflight,
    }


def main() -> int:
    result = verify_combined_equation_optimizer()
    import json
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
