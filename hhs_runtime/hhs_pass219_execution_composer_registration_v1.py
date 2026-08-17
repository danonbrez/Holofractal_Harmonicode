"""Pass 219 I114 canonical execution-composer registration.

This module registers the additive exact C ABI execution selector with the
inherited Pass 043/217 kernel runtime auto-composer.  It does not duplicate the
C routing policy and it does not grant mutation authority.
"""

from __future__ import annotations

from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight

VERSION = "PASS_219_RNA_EXECUTION_COMPOSER_REGISTRATION_1_14"
SURFACE_ID = "executor:pass219.rna.execution.compose"
EXECUTION_SYMBOL = "hhs_exact_pass219_rna_execution_compose"
PREPARE_SYMBOL = "hhs_exact_pass219_rna_execution_prepare_candidate"

BYPASS_REASONS = (
    "FIRST_PRINCIPLES_EXPORT",
    "DEPENDENCY_CHANGED",
    "CORRUPTION_RECOVERY",
    "MISSING_OR_INVALID_REFERENCE_EVIDENCE",
    "REFERENCE_ORACLE",
    "ABLATION_OR_BENCHMARK_CONTROL",
    "UNAVAILABLE_AUTHENTICATED_PREDECESSOR",
    "EXPLICITLY_AUTHORIZED_AUDIT",
)


def pass219_execution_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": SURFACE_ID,
        "surface_type": "EXECUTOR",
        "module": "hhs_runtime_exact_abi",
        "symbol": EXECUTION_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS_PASS219_RNA_EXECUTION_COMPOSER_ABI_1_14",
            "HHS_PASS219_POST_PASS218_INDEXED_REUSE_POLICY_1_5_0",
        ],
        "witness_schemas": [
            "HHS_KERNEL_DERIVATION_WITNESS_V1",
            "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
            "HHS_PASS219_RNA_EXECUTION_PLAN_V1",
        ],
        "validators": [
            EXECUTION_SYMBOL,
            PREPARE_SYMBOL,
        ],
        "guards": [
            "kernel_runtime_autocomposer",
            "authenticated_indexed_predecessor_gate",
            "dependency_frontier_gate",
            "single_c_vm81_mutation_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS219_EXECUTION_ROUTE_WITHOUT_TYPED_REASON",
            "REJECT_PASS219_INDEXED_CONTINUATION_WITHOUT_AUTHENTICATED_PREDECESSOR",
            "REJECT_PASS219_DEPENDENCY_CHANGE_AS_UNSCOPED_GENESIS_REPLAY",
            "REJECT_PASS219_CPP_MUTATION_AUTHORITY",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "EXECUTION_ROUTE_EVIDENCE_ONLY",
        "boundedness_policy": "PASS_219_FIXED_ABI_ROUTE_SELECTION_1_14",
        "declared_operations": [EXECUTION_SYMBOL],
    }


def pass219_execution_registration_manifest() -> Dict[str, Any]:
    return {
        "schema": "HHS_PASS219_EXECUTION_COMPOSER_REGISTRATION_V1",
        "version": VERSION,
        "surface_id": SURFACE_ID,
        "execution_symbol": EXECUTION_SYMBOL,
        "prepare_symbol": PREPARE_SYMBOL,
        "default_eligible_route": "INDEXED_CONTINUATION",
        "default_preconditions": [
            "AUTHENTICATED_INDEXED_PREDECESSOR",
            "CURRENT_DEPENDENCY_FRONTIER_MATCH",
            "NO_TYPED_BYPASS_REQUEST",
        ],
        "typed_bypass_reasons": list(BYPASS_REASONS),
        "genesis_replay_default": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": "INHERITED_C_ONLY",
    }


def preflight_pass219_execution_composer(
    *, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Traverse the inherited canonical kernel composer for the I114 ABI symbol."""

    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    return execute_surface_preflight(
        pass219_execution_surface_declaration(),
        operation=EXECUTION_SYMBOL,
        cache=decision_cache,
    )


__all__ = [
    "VERSION",
    "SURFACE_ID",
    "EXECUTION_SYMBOL",
    "PREPARE_SYMBOL",
    "BYPASS_REASONS",
    "pass219_execution_surface_declaration",
    "pass219_execution_registration_manifest",
    "preflight_pass219_execution_composer",
]
