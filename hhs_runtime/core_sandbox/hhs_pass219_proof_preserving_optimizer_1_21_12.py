"""Pass 219 I121.12 proof-preserving read-only optimization activation.

This layer activates only the redundant-work reductions already proved by
I121.8-I121.11. It consumes the frozen I121.8 verifier and does not evaluate
the Harmonicode algebra, replace NcalcMatrixPower, or supply Pass169 truth.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.core_sandbox.hhs_pass219_combined_equation_optimizer_1_21_8 import (
    COMBINED_SHA256,
    DENOMINATOR_SHA256,
    PROJECTION_SHA256,
    verify_combined_equation_optimizer,
)

VERSION = "PASS_219_I121_12_PROOF_PRESERVING_OPTIMIZER_V1"
SCHEMA = "HHS_PASS_219_I121_12_PROOF_PRESERVING_OPTIMIZER_V1"
CLASSIFICATION = "PROOF_PRESERVING_READ_ONLY_OPTIMIZATION_ACTIVATED"
AUTHORITY_QUALIFIER = "READ_ONLY_OPTIMIZATION_ONLY_PASS169_RUNTIME_AUTHORITY_STILL_REQUIRED"

EXPECTED_PASS159_DISTINCTION = {
    "source_equal": 0,
    "tokens_equal": 0,
    "cst_equal": 0,
    "ast_equal": 0,
    "types_equal": 0,
    "graph_equal": 0,
    "hir_equal": 0,
    "vmir_equal": 0,
}
EXPECTED_GATE_OFFSETS = (96, 240, 266, 274, 285)


def _diagnostic_occurrence_id(offset: int) -> str:
    material = f"I121.12:{COMBINED_SHA256}:{DENOMINATOR_SHA256}:{offset}".encode("ascii")
    return hashlib.sha256(material).hexdigest()


def _stable_digest(value: Dict[str, Any]) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def activate_proof_preserving_optimization(
    root: str | Path | None = None,
    *,
    combined_override: Optional[str] = None,
    projection_override: Optional[str] = None,
    cache: Optional[MutableMapping[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Return the exact read-only optimization schedule permitted by proof.

    The function intentionally schedules work; it does not perform the missing
    Pass169 whole-expression evaluation. The denominator value remains opaque
    to this layer and may only be computed by a separately authorized evaluator.
    """

    inherited = verify_combined_equation_optimizer(
        root,
        combined_override=combined_override,
        projection_override=projection_override,
        cache=cache,
    )

    def require(condition: bool, code: str) -> None:
        if not condition:
            raise ValueError(code)

    require(inherited.get("ok") is True, "REJECT_I12112_INHERITED_PROOF_MISSING")
    require(
        inherited.get("combined_source_sha256") == COMBINED_SHA256,
        "REJECT_I12112_COMBINED_SOURCE_DRIFT",
    )
    require(
        inherited.get("denominator_source_sha256") == DENOMINATOR_SHA256,
        "REJECT_I12112_DENOMINATOR_IDENTITY_DRIFT",
    )
    require(
        inherited.get("denominator_occurrences") == 2,
        "REJECT_I12112_DENOMINATOR_OCCURRENCE_DRIFT",
    )
    require(
        inherited.get("denominator_source_occurrence_witnesses_required") == 2,
        "REJECT_I12112_DENOMINATOR_WITNESS_DRIFT",
    )
    require(
        inherited.get("denominator_memoized_value_nodes_candidate") == 1,
        "REJECT_I12112_CSE_VALUE_NODE_DRIFT",
    )
    require(
        inherited.get("source_occurrence_provenance_preserved") is True,
        "REJECT_I12112_SOURCE_PROVENANCE_DRIFT",
    )
    require(
        inherited.get("execution_receipt_count_reduction_authorized") is False,
        "REJECT_I12112_RECEIPT_REDUCTION_DRIFT",
    )
    require(
        inherited.get("candidate_projection_general_evaluations") == 3,
        "REJECT_I12112_PROJECTION_GENERAL_COUNT_DRIFT",
    )
    require(
        inherited.get("candidate_projection_exact_phase_witness_checks") == 6,
        "REJECT_I12112_PHASE_WITNESS_COUNT_DRIFT",
    )
    require(
        inherited.get("final_projection_cells_verified") == 9,
        "REJECT_I12112_FINAL_PROJECTION_COVERAGE_DRIFT",
    )
    require(
        inherited.get("projection_substitution_authorized") is False,
        "REJECT_I12112_PROJECTION_AUTHORITY_DRIFT",
    )
    require(
        inherited.get("algebraic_cancellation_authorized") is False,
        "REJECT_I12112_CANCELLATION_AUTHORITY_DRIFT",
    )
    require(
        inherited.get("canonical_monolithic_proof") is False,
        "REJECT_I12112_CANONICAL_PROOF_DRIFT",
    )
    require(
        inherited.get("pass169_whole_expression_admission_required") is True,
        "REJECT_I12112_PASS169_GATE_DRIFT",
    )

    offsets = list(inherited.get("denominator_occurrence_offsets", []))
    require(len(offsets) == 2 and offsets[0] < offsets[1], "REJECT_I12112_OCCURRENCE_OFFSET_DRIFT")

    occurrence_witnesses = [
        {
            "occurrence_index": index,
            "source_offset": offset,
            "diagnostic_occurrence_sha256": _diagnostic_occurrence_id(offset),
            "memoized_value_key_sha256": DENOMINATOR_SHA256,
        }
        for index, offset in enumerate(offsets)
    ]
    require(
        occurrence_witnesses[0]["diagnostic_occurrence_sha256"]
        != occurrence_witnesses[1]["diagnostic_occurrence_sha256"],
        "REJECT_I12112_OCCURRENCE_WITNESS_COLLAPSE",
    )
    require(
        occurrence_witnesses[0]["memoized_value_key_sha256"]
        == occurrence_witnesses[1]["memoized_value_key_sha256"],
        "REJECT_I12112_VALUE_KEY_DIVERGENCE",
    )

    baseline_general_work_units = (
        int(inherited["baseline_denominator_value_evaluations"])
        + int(inherited["baseline_projection_general_evaluations"])
    )
    optimized_general_work_units = (
        int(inherited["candidate_denominator_value_evaluations"])
        + int(inherited["candidate_projection_general_evaluations"])
    )

    schedule: Dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "classification": CLASSIFICATION,
        "authority_qualifier": AUTHORITY_QUALIFIER,
        "ok": True,
        "read_only_optimization_activated": True,
        "source_binding": {
            "combined_source_sha256": COMBINED_SHA256,
            "denominator_sha256": DENOMINATOR_SHA256,
            "projection_sha256": PROJECTION_SHA256,
            "expected_gate_offsets": list(EXPECTED_GATE_OFFSETS),
            "pass159_whole_expression_distinction_required": dict(EXPECTED_PASS159_DISTINCTION),
            "pass159_distinction_is_external_validation_evidence": True,
        },
        "denominator_cse": {
            "activation": "AUTHORIZED_READ_ONLY_VALUE_REUSE",
            "baseline_value_evaluations": 2,
            "memoized_value_evaluations": 1,
            "value_evaluations_avoided": 1,
            "memoized_value_nodes": 1,
            "source_occurrence_witness_count": 2,
            "occurrence_witnesses": occurrence_witnesses,
            "receipt_count_reduction_authorized": False,
            "source_occurrence_provenance_preserved": True,
            "algebraic_cancellation_authorized": False,
            "value_is_opaque_to_this_optimizer": True,
        },
        "projection_validation_fast_path": {
            "activation": "AUTHORIZED_READ_ONLY_VALIDATION_FAST_PATH",
            "baseline_general_evaluations": 9,
            "optimized_general_evaluations": 3,
            "general_representatives": list(inherited["projection_representatives"]),
            "exact_phase_witness_checks": 6,
            "final_verified_cells": 9,
            "final_cell_obligation_reduction": 0,
            "projection_substitution_authorized": False,
            "projection_derivation_authority": False,
            "center_relation_preserved": inherited["center_relation"],
            "ordered_xy_yx_distinct": inherited["ordered_xy_yx_distinct"],
            "ordered_zw_wz_distinct": inherited["ordered_zw_wz_distinct"],
        },
        "structural_work_accounting": {
            "baseline_general_work_units": baseline_general_work_units,
            "optimized_general_work_units": optimized_general_work_units,
            "general_work_units_avoided": baseline_general_work_units - optimized_general_work_units,
            "replacement_exact_phase_witness_checks": 6,
            "runtime_speedup_claimed": False,
            "proof_obligation_reduction_claimed": False,
        },
        "authority_boundary": {
            "pass169_whole_expression_admission_required": True,
            "boolean_gate_truth_produced": False,
            "canonical_monolithic_proof": False,
            "floating_point_authority": False,
            "vm81_mutation_authority": False,
            "hash72_commit_authority": False,
            "hash216_receipt_authority": False,
            "persistence_mutation_authority": False,
            "ncalc_matrix_power_reimplemented": False,
            "ordinary_scalar_squaring_authorized": False,
            "scalar_intermediate_required": False,
        },
    }
    schedule["optimization_schedule_sha256"] = _stable_digest(schedule)
    return schedule


def main() -> int:
    print(
        json.dumps(
            activate_proof_preserving_optimization(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
