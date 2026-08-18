"""Pass 219 I116 cumulative membrane registration, beginning with Pass 218.

This module does not reimplement Pass 218. It registers the exact C ABI binding
for an already-verified I48 terminal completion witness. The active reconciled
I116 development lineage contains both the canonical merged Pass 218 I1-I48
history and the exact frozen Pass 219 I115/I116 ancestry without rewriting
either history. Dependency-scoped exact/synthetic validation has proven the
Pass 218 terminal membrane compositionally reachable through Pass 219.
"""

from __future__ import annotations

from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_16"
PASS_NUMBER = 218
CLASSIFICATION = "WIRED"
SURFACE_ID = "validator:pass219.inherited.pass218.completion"
BIND_SYMBOL = "hhs_exact_pass219_bind_pass218_completion"

PASS218_CAPABILITIES = (
    "MANIFEST_BOUND_CURRICULUM_COMPLETION_SEAL",
    "DETERMINISTIC_ORDERED_CURRICULUM_IDENTITY",
    "AUTHORITATIVE_MANIFEST_EXHAUSTION",
    "HASH72_HASH216_CONTINUATION_IDENTITY",
    "EXACT_FINAL_CURSOR_IDENTITY",
    "UNCHANGED_I30_SEMANTIC_GENERATION_IDENTITY",
    "RESTART_SAFE_COMPLETION_SEAL",
)


def pass218_membrane_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime_exact_abi",
        "symbol": BIND_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS-P218-I48-MANIFEST-BOUND-CURRICULUM-COMPLETION-RECEIPT-V1",
            "HHS_PASS219_INHERITED_PASS218_COMPLETION_BINDING_1_16",
        ],
        "witness_schemas": [
            "HHS-P218-I48-MANIFEST-BOUND-CURRICULUM-COMPLETION-PROOF-V1",
            "HHS_PASS219_PASS218_COMPLETION_WITNESS_V1",
        ],
        "validators": [BIND_SYMBOL],
        "guards": [
            "pass218_i48_terminal_completion_verified_upstream",
            "pass218_hash216_triplet_continuity",
            "pass218_manifest_exhaustion_gate",
            "pass218_no_handoff_authority_gate",
            "single_c_vm81_mutation_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS218_UNSEALED_COMPLETION",
            "REJECT_PASS218_SOURCE_COUNT_MISMATCH",
            "REJECT_PASS218_HASH216_CONTINUITY_MISMATCH",
            "REJECT_PASS218_HANDOFF_AUTHORITY_ESCALATION",
            "REJECT_PASS218_VM81_AUTHORITY_ESCALATION",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_COMPLETION_IDENTITY_ONLY",
        "boundedness_policy": "PASS_218_TERMINAL_I48_BINDING_ONLY",
        "declared_operations": [BIND_SYMBOL],
    }


def pass218_membrane_manifest() -> Dict[str, Any]:
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS_NUMBER,
        "classification": CLASSIFICATION,
        "authoritative_surface": "hhs_runtime.pass218.manifest_bound_curriculum_completion_seal_i48",
        "runtime_os_surface": "hhs_backend.runtime_os_pass218_manifest_curriculum_completion_i48",
        "pass219_c_abi_surface": BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass218Completion",
        "capabilities": list(PASS218_CAPABILITIES),
        "receipt_semantics_preserved": True,
        "pass219_handoff_authority_minted": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": "NOT_GRANTED_BY_THIS_BINDING",
        "canonical_pass218_i48_present_on_active_branch": True,
        "canonical_main_with_pass218_i48": "d4b893521782d7f7590c74034c4634bfdba83874",
        "frozen_pass219_i115_parent": "f0e8fd3a871bd0e8ac0668d3d210f74c22061676",
        "frozen_pass219_i116_checkpoint": "c34956f2982020d7b16513e31cae3f40d91e9326",
        "reconciliation_merge_commit": "b65cb3748abfb2558ef6f481dfede7c1da799344",
        "required_repair": None,
        "next_pass_to_census": 217,
    }


def preflight_pass218_membrane(
    *, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    return execute_surface_preflight(
        pass218_membrane_surface_declaration(),
        operation=BIND_SYMBOL,
        cache=decision_cache,
    )


__all__ = [
    "VERSION",
    "PASS_NUMBER",
    "CLASSIFICATION",
    "SURFACE_ID",
    "BIND_SYMBOL",
    "PASS218_CAPABILITIES",
    "pass218_membrane_surface_declaration",
    "pass218_membrane_manifest",
    "preflight_pass218_membrane",
]
