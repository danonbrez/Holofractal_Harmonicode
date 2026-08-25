"""Pass 219 I121.7 kernel-derived validation membrane.

This module repairs the validation path for I121.3/I121.5/I121.6 without
modifying or replacing frozen Pass 035, Pass 036, Pass 043, Pass 169, or
Pass 191 logic.

The membrane is deliberately read-only against canonical state. It exposes
validator surfaces through the inherited Pass 043 ``execute_surface_preflight``
path before candidate diagnostics or frozen Pass191 evidence are exercised.
Host compilers and unit tests remain diagnostics only; they cannot mint VM81
mutation authority, Hash72 commit authority, or canonical whole-expression
proof.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.core_sandbox.hhs_pass219_inherited_manifold_authority_1_21_5 import (
    verify_inherited_manifold_authority,
)

VERSION = "PASS_219_I121_7_KERNEL_DERIVED_VALIDATION_MEMBRANE_V1"
SCHEMA = "HHS_PASS219_I121_VALIDATION_MEMBRANE_V1"
CLASSIFICATION = "KERNEL_DERIVED_READ_ONLY_VALIDATION"
DECISION = "PASS169_WHOLE_EXPRESSION_AUTHORITY_REQUIRED"

I1213_VALIDATOR_SURFACE_ID = "validator:pass219.i121.exact-vm81-candidate"
I1213_VALIDATOR_SYMBOL = "hhs_exact_pass219_vm81_execute_candidate"
I1215_VALIDATOR_SURFACE_ID = "validator:pass219.i121.inherited-manifold-authority"
I1215_VALIDATOR_SYMBOL = "verify_inherited_manifold_authority"
I1216_VALIDATOR_SURFACE_ID = "validator:pass219.i121.authority-router"
I1216_VALIDATOR_SYMBOL = "hhs_exact_pass219_authority_route_evidence"

_REQUIRED_GUARDS = (
    "runtime_constraint_enforcement",
    "zero_bypass_runtime_interposer",
    "kernel_runtime_autocomposer",
    "pass169_whole_expression_authority_gate",
)
_REQUIRED_ENFORCEMENT_PATH = (
    "kernel_conformance_decision",
    "runtime_constraint_enforcement",
    "zero_bypass_runtime_interposer",
)


def exact_vm81_candidate_validator_surface_declaration() -> Dict[str, Any]:
    """Declare I121.3 candidate execution as diagnostic validation only."""
    return {
        "surface_id": I1213_VALIDATOR_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_pass219_exact_vm81_candidate_adapter_1_21_3",
        "symbol": I1213_VALIDATOR_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS_PASS219_EXACT_VM81_CANDIDATE_ADAPTER_1_21_3",
            "HHS_PASS219_MONOLITHIC_CONSTRAINT_ABI_1_20",
            "HHS_PASS_169_HARMONICODE_SYNTAX_ALGEBRA_ENFORCEMENT_AND_VM81_EXACT_SYMBOLIC_CONSTRAINT_PROOF_RUNTIME",
        ],
        "witness_schemas": [
            "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
            "HHS_EXACT_PASS219_VM81_EXECUTION_V1",
            "HHS_EXACT_PASS219_VM81_REPLAY_V1",
        ],
        "validators": [
            "hhs_exact_pass219_vm81_candidate_adapter_descriptor",
            I1213_VALIDATOR_SYMBOL,
            "hhs_exact_pass219_vm81_replay_candidate",
        ],
        "guards": [
            *_REQUIRED_GUARDS,
            "candidate_only_execution_gate",
            "source_semantics_unresolved_gate",
            "canonical_proof_absence_gate",
        ],
        "rejection_codes": [
            "REJECT_I1213_SOURCE_IDENTITY_DRIFT",
            "REJECT_I1213_CANDIDATE_REPLAY_MISMATCH",
            "REJECT_I1213_SOURCE_SEMANTICS_PROMOTION",
            "REJECT_I1213_CANONICAL_AUTHORITY_PROMOTION",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "NO_PERSISTENCE_MUTATION",
        "boundedness_policy": "ISOLATED_CANDIDATE_FRAME_DIAGNOSTIC_ONLY",
        "declared_operations": [I1213_VALIDATOR_SYMBOL],
    }


def inherited_manifold_validator_surface_declaration() -> Dict[str, Any]:
    """Declare I121.5 as a read-only validator surface, never an authority."""
    return {
        "surface_id": I1215_VALIDATOR_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.core_sandbox.hhs_pass219_inherited_manifold_authority_1_21_5",
        "symbol": I1215_VALIDATOR_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS_PASS_219_I121_5_INHERITED_MANIFOLD_AUTHORITY_V1",
            "HHS_PASS_191_UNIFIED_MANIFOLD_VM81_PROOF_SEARCH_EXECUTED",
            "HHS_PASS_169_HARMONICODE_SYNTAX_ALGEBRA_ENFORCEMENT_AND_VM81_EXACT_SYMBOLIC_CONSTRAINT_PROOF_RUNTIME",
        ],
        "witness_schemas": [
            "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
            "HHS_PASS_219_I121_5_INHERITED_MANIFOLD_AUTHORITY_V1",
            "PASS_191_INTEGRATED_PROOF_SEARCH",
            "PASS_191_INTEGRATED_COMPLETION_RECEIPT",
        ],
        "validators": [
            I1215_VALIDATOR_SYMBOL,
            "verify_integrated_manifold_search",
            "pass191_exact_context_scope_preservation",
        ],
        "guards": [
            *_REQUIRED_GUARDS,
            "pass191_exact_context_scope_gate",
            "pass191_obstructed_theorem_scope_gate",
        ],
        "rejection_codes": [
            "REJECT_I1215_SOURCE_IDENTITY_DRIFT",
            "REJECT_I1215_PASS191_EVIDENCE_DRIFT",
            "REJECT_I1215_SCOPE_PROMOTION",
            "REJECT_I1215_PARALLEL_AUTHORITY",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "NO_PERSISTENCE_MUTATION",
        "boundedness_policy": "FROZEN_PASS191_EVIDENCE_READ_ONLY",
        "declared_operations": [I1215_VALIDATOR_SYMBOL],
    }


def authority_router_validator_surface_declaration() -> Dict[str, Any]:
    """Declare I121.6 routing as a pure evidence-role validator surface."""
    return {
        "surface_id": I1216_VALIDATOR_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime_exact_abi",
        "symbol": I1216_VALIDATOR_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS_PASS219_AUTHORITY_ROUTER_1_21_6",
            "HHS_PASS_219_I121_5_INHERITED_MANIFOLD_AUTHORITY_V1",
            "HHS_PASS_169_HARMONICODE_SYNTAX_ALGEBRA_ENFORCEMENT_AND_VM81_EXACT_SYMBOLIC_CONSTRAINT_PROOF_RUNTIME",
        ],
        "witness_schemas": [
            "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
            "HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_V1",
            "HHS_EXACT_PASS219_AUTHORITY_ROUTE_V1",
        ],
        "validators": [
            I1216_VALIDATOR_SYMBOL,
            "hhs_exact_pass219_authority_router_descriptor",
            "pass169_whole_expression_authority_preservation",
        ],
        "guards": [
            *_REQUIRED_GUARDS,
            "pass191_evidence_nonpromotion_gate",
            "canonical_proof_decision_absence_gate",
        ],
        "rejection_codes": [
            "REJECT_I1216_MALFORMED_EVIDENCE",
            "REJECT_I1216_SCOPE_PROMOTION",
            "REJECT_I1216_PARALLEL_VM81_AUTHORITY",
            "REJECT_I1216_HASH72_COMMIT_AUTHORITY",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "NO_PERSISTENCE_MUTATION",
        "boundedness_policy": "EVIDENCE_ROLE_CLASSIFICATION_ONLY",
        "declared_operations": [I1216_VALIDATOR_SYMBOL],
    }


def _require_preflight_shape(result: Dict[str, Any], surface_id: str) -> None:
    if result.get("ok") is not True:
        raise RuntimeError(f"PASS219_I121_PREFLIGHT_REJECTED:{surface_id}")
    plan = result.get("composition_plan", {})
    pipeline = plan.get("pipeline", {}) if isinstance(plan, dict) else {}
    if tuple(pipeline.get("enforcement_path", ())) != _REQUIRED_ENFORCEMENT_PATH:
        raise RuntimeError(f"PASS219_I121_ENFORCEMENT_PATH_DRIFT:{surface_id}")
    guards = tuple(pipeline.get("guard_path", ()))
    for guard in _REQUIRED_GUARDS:
        if guard not in guards:
            raise RuntimeError(f"PASS219_I121_REQUIRED_GUARD_MISSING:{surface_id}:{guard}")
    if pipeline.get("mutation_policy") not in (None, "NO_EXTERNAL_STATE_MUTATION"):
        raise RuntimeError(f"PASS219_I121_MUTATION_POLICY_DRIFT:{surface_id}")
    if pipeline.get("persistence_policy") not in (None, "NO_PERSISTENCE_MUTATION"):
        raise RuntimeError(f"PASS219_I121_PERSISTENCE_POLICY_DRIFT:{surface_id}")
    if result.get("expanded_metadata_persisted") is not False:
        raise RuntimeError(f"PASS219_I121_METADATA_PERSISTENCE_DRIFT:{surface_id}")


def preflight_pass219_i121_validation_membrane(
    *, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Run inherited Pass043 preflight for all I121 diagnostic validator surfaces."""
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    candidate = execute_surface_preflight(
        exact_vm81_candidate_validator_surface_declaration(),
        operation=I1213_VALIDATOR_SYMBOL,
        cache=decision_cache,
    )
    manifold = execute_surface_preflight(
        inherited_manifold_validator_surface_declaration(),
        operation=I1215_VALIDATOR_SYMBOL,
        cache=decision_cache,
    )
    router = execute_surface_preflight(
        authority_router_validator_surface_declaration(),
        operation=I1216_VALIDATOR_SYMBOL,
        cache=decision_cache,
    )
    _require_preflight_shape(candidate, I1213_VALIDATOR_SURFACE_ID)
    _require_preflight_shape(manifold, I1215_VALIDATOR_SURFACE_ID)
    _require_preflight_shape(router, I1216_VALIDATOR_SURFACE_ID)
    return {
        "schema": "HHS_PASS219_I121_COMPOSED_VALIDATION_PREFLIGHT_V1",
        "version": VERSION,
        "ok": True,
        "classification": CLASSIFICATION,
        "candidate_validator": candidate,
        "manifold_validator": manifold,
        "authority_router_validator": router,
        "runtime_constraint_enforcement_required": True,
        "zero_bypass_interposer_required": True,
        "kernel_runtime_autocomposer_required": True,
        "host_diagnostic_authority": False,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "canonical_monolithic_proof": False,
    }


def verify_pass219_i121_through_membrane(
    root: str | Path | None = None,
    *,
    cache: Optional[MutableMapping[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Verify frozen I121.5 evidence only after all I121 validator surfaces admit."""
    preflight = preflight_pass219_i121_validation_membrane(cache=cache)
    evidence = verify_inherited_manifold_authority(root)

    if evidence.get("canonical_monolithic_proof") is not False:
        raise RuntimeError("PASS219_I121_CANONICAL_PROOF_PROMOTION_FORBIDDEN")
    if evidence.get("whole_expression_semantics_resolved") is not False:
        raise RuntimeError("PASS219_I121_WHOLE_EXPRESSION_SCOPE_PROMOTION_FORBIDDEN")
    if evidence.get("pass169_whole_expression_admission_required") is not True:
        raise RuntimeError("PASS219_I121_PASS169_AUTHORITY_BYPASS_FORBIDDEN")
    if evidence.get("vm81_mutation_authority") is not False:
        raise RuntimeError("PASS219_I121_VM81_MUTATION_AUTHORITY_FORBIDDEN")
    if evidence.get("hash72_commit_authority") is not False:
        raise RuntimeError("PASS219_I121_HASH72_COMMIT_AUTHORITY_FORBIDDEN")

    return {
        "schema": SCHEMA,
        "version": VERSION,
        "ok": True,
        "classification": CLASSIFICATION,
        "decision": DECISION,
        "preflight": preflight,
        "inherited_manifold_evidence": evidence,
        "i1213_candidate_execution_diagnostic_only": True,
        "frozen_pass191_evidence_verified": True,
        "host_compiler_tests_diagnostic_only": True,
        "host_diagnostic_authority": False,
        "whole_expression_semantics_resolved": False,
        "canonical_monolithic_proof": False,
        "pass169_whole_expression_admission_required": True,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "persistence_mutation_authority": False,
    }


def main() -> int:
    result = verify_pass219_i121_through_membrane()
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "VERSION",
    "SCHEMA",
    "CLASSIFICATION",
    "DECISION",
    "I1213_VALIDATOR_SURFACE_ID",
    "I1213_VALIDATOR_SYMBOL",
    "I1215_VALIDATOR_SURFACE_ID",
    "I1216_VALIDATOR_SURFACE_ID",
    "exact_vm81_candidate_validator_surface_declaration",
    "inherited_manifold_validator_surface_declaration",
    "authority_router_validator_surface_declaration",
    "preflight_pass219_i121_validation_membrane",
    "verify_pass219_i121_through_membrane",
]
