"""Pass 219 I116 cumulative inherited-pass membrane.

The membrane exposes already-admitted inherited authorities without replacing
them. Pass 218 binds its terminal I48 completion seal. Pass 217 binds the
admitted cumulative utilization/reachability closure and the frozen Iteration 4
Hash72-manifold / immutable-nucleus evidence. Neither binding grants C++ or
VM81 mutation authority or promotes a separate Genesis ROM.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_backend.runtime.hhs_pass217_hash72_manifold_nucleus_v1 import (
    EVIDENCE_PATH as PASS217_I4_EVIDENCE_PATH,
    validate_record as validate_pass217_i4_record,
)
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass217_cumulative_closure_v1 import (
    build_cumulative_utilization_reachability_closure,
)

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_16"
PASS_NUMBER = 218
CLASSIFICATION = "WIRED"
PASS217_NUMBER = 217
PASS217_CLASSIFICATION = "WIRED"
PASS218_SURFACE_ID = "validator:pass219.inherited.pass218.completion"
PASS218_BIND_SYMBOL = "hhs_exact_pass219_bind_pass218_completion"
PASS217_SURFACE_ID = "validator:pass219.inherited.pass217.cumulative-closure"
PASS217_BIND_SYMBOL = "hhs_exact_pass219_bind_pass217_cumulative_closure"
SURFACE_ID = PASS218_SURFACE_ID
BIND_SYMBOL = PASS218_BIND_SYMBOL
ROOT = Path(__file__).resolve().parents[1]

PASS218_CAPABILITIES = (
    "MANIFEST_BOUND_CURRICULUM_COMPLETION_SEAL",
    "DETERMINISTIC_ORDERED_CURRICULUM_IDENTITY",
    "AUTHORITATIVE_MANIFEST_EXHAUSTION",
    "HASH72_HASH216_CONTINUATION_IDENTITY",
    "EXACT_FINAL_CURSOR_IDENTITY",
    "UNCHANGED_I30_SEMANTIC_GENERATION_IDENTITY",
    "RESTART_SAFE_COMPLETION_SEAL",
)

PASS217_CAPABILITIES = (
    "CUMULATIVE_UTILIZATION_REACHABILITY_CLOSURE",
    "TWENTY_FIVE_REQUIRED_AUTHORITIES_NONBYPASSABLE",
    "PASS042_PRODUCTION_ROUTE_PUBLICATION",
    "EXACT_INCREMENTAL_TOKENIZATION_ACTIVE_PATH",
    "HASH72_ORDER72_MANIFOLD_I4",
    "IMMUTABLE_LO_SHU_PHASE_NUCLEUS_I4",
)


def pass218_membrane_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": PASS218_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime_exact_abi",
        "symbol": PASS218_BIND_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS-P218-I48-MANIFEST-BOUND-CURRICULUM-COMPLETION-RECEIPT-V1",
            "HHS_PASS219_INHERITED_PASS218_COMPLETION_BINDING_1_16",
        ],
        "witness_schemas": [
            "HHS-P218-I48-MANIFEST-BOUND-CURRICULUM-COMPLETION-PROOF-V1",
            "HHS_PASS219_PASS218_COMPLETION_WITNESS_V1",
        ],
        "validators": [PASS218_BIND_SYMBOL],
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
        "declared_operations": [PASS218_BIND_SYMBOL],
    }


def pass218_membrane_manifest() -> Dict[str, Any]:
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS_NUMBER,
        "classification": CLASSIFICATION,
        "authoritative_surface": "hhs_runtime.pass218.manifest_bound_curriculum_completion_seal_i48",
        "runtime_os_surface": "hhs_backend.runtime_os_pass218_manifest_curriculum_completion_i48",
        "pass219_c_abi_surface": PASS218_BIND_SYMBOL,
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


def pass217_membrane_source_evidence() -> Dict[str, Any]:
    closure = build_cumulative_utilization_reachability_closure()
    i4_summary = validate_pass217_i4_record(ROOT)
    i4_record = json.loads((ROOT / PASS217_I4_EVIDENCE_PATH).read_text("utf-8"))

    if closure.get("status") != "ADMIT_PASS217_CUMULATIVE_UTILIZATION_REACHABILITY_CLOSURE":
        raise RuntimeError("PASS217_CUMULATIVE_CLOSURE_NOT_ADMITTED")
    if closure.get("closure_ready") is not True or closure.get("blockers") != []:
        raise RuntimeError("PASS217_CUMULATIVE_CLOSURE_BLOCKED")
    if closure.get("required_authority_count") != 25:
        raise RuntimeError("PASS217_REQUIRED_AUTHORITY_COUNT_DRIFT")
    if closure["required_authority_bypass_negative_matrix"].get(
        "all_applicable_required_authority_omissions_blocked"
    ) is not True:
        raise RuntimeError("PASS217_REQUIRED_AUTHORITY_BYPASS_GATE_DRIFT")
    if closure["required_authority_profile_coverage"].get(
        "incremental_tokenization_applicable_active_path_proven"
    ) is not True:
        raise RuntimeError("PASS217_INCREMENTAL_TOKENIZATION_GAP")
    if i4_summary.get("canonical_authority_promoted") is not False:
        raise RuntimeError("PASS217_I4_PROMOTION_BOUNDARY_DRIFT")
    claim = i4_record["claim_boundary"]
    if claim.get("hash72_manifold_validated") is not True:
        raise RuntimeError("PASS217_I4_HASH72_MANIFOLD_UNVERIFIED")
    if claim.get("immutable_nucleus_validated") is not True:
        raise RuntimeError("PASS217_I4_NUCLEUS_UNVERIFIED")
    if claim.get("runtime_mutation_performed") is not False:
        raise RuntimeError("PASS217_I4_RUNTIME_MUTATION_DRIFT")

    return {
        "closure": closure,
        "iteration4": i4_record,
        "checkpoint15_git_sha": "be71da59c9b8b7c7e055c03da703ca301849cfff",
        "integration_git_sha": "b0656a92ab29507f81eae760e070f74e49db83f4",
    }


def pass217_membrane_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": PASS217_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime_exact_abi",
        "symbol": PASS217_BIND_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS_PASS217_CUMULATIVE_UTILIZATION_REACHABILITY_CLOSURE_V1",
            "HHS_PASS_217_ITERATION_4_HASH72_MANIFOLD_NUCLEUS_V1",
            "HHS_PASS219_INHERITED_PASS217_CUMULATIVE_CLOSURE_BINDING_1_16",
        ],
        "witness_schemas": [
            "HHS_CUMULATIVE_EXECUTION_AUTHORITY_REACHABILITY_V1",
            "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
            "HHS_PASS219_PASS217_CUMULATIVE_CLOSURE_WITNESS_V1",
        ],
        "validators": [
            PASS217_BIND_SYMBOL,
            "build_cumulative_utilization_reachability_closure",
            "validate_pass217_iteration4_record",
        ],
        "guards": [
            "pass217_required_authority_nonbypass_gate",
            "pass217_global_surface_publication_gate",
            "pass217_incremental_tokenization_active_path_gate",
            "pass217_i4_hash72_manifold_gate",
            "pass217_i4_immutable_nucleus_gate",
            "pass217_i4_no_genesis_rom_promotion_gate",
            "single_c_vm81_mutation_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS217_CUMULATIVE_CLOSURE_BLOCKED",
            "REJECT_PASS217_REQUIRED_AUTHORITY_BYPASS",
            "REJECT_PASS217_INCREMENTAL_TOKENIZATION_GAP",
            "REJECT_PASS217_I4_MANIFOLD_OR_NUCLEUS_DRIFT",
            "REJECT_PASS217_UNAUTHORIZED_GENESIS_ROM_PROMOTION",
            "REJECT_PASS217_CPP_MUTATION_AUTHORITY",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_CLOSURE_IDENTITY_ONLY",
        "boundedness_policy": "PASS_217_ADMITTED_CUMULATIVE_CLOSURE_PLUS_FROZEN_I4_IDENTITY",
        "declared_operations": [PASS217_BIND_SYMBOL],
    }


def pass217_membrane_manifest() -> Dict[str, Any]:
    evidence = pass217_membrane_source_evidence()
    closure = evidence["closure"]
    i4 = evidence["iteration4"]
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS217_NUMBER,
        "classification": PASS217_CLASSIFICATION,
        "authoritative_surface": "hhs_runtime.hhs_pass217_cumulative_closure_v1",
        "supporting_authority_surface": "hhs_backend.runtime.hhs_pass217_hash72_manifold_nucleus_v1",
        "pass219_c_abi_surface": PASS217_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass217Closure",
        "capabilities": list(PASS217_CAPABILITIES),
        "required_authority_count": closure["required_authority_count"],
        "closure_root_hash72": closure["closure_root_hash72"],
        "closure_blockers": list(closure["blockers"]),
        "global_surface_publication_complete": closure["global_surface_publication"]["ok"],
        "all_required_authority_omissions_blocked": closure[
            "required_authority_bypass_negative_matrix"
        ]["all_applicable_required_authority_omissions_blocked"],
        "incremental_tokenization_active_path_proven": closure[
            "required_authority_profile_coverage"
        ]["incremental_tokenization_applicable_active_path_proven"],
        "i4_hash72_manifold_root_sha256": i4["hash72_manifold"]["manifold_root_sha256"],
        "i4_nucleus_identity_root_sha256": i4["immutable_nucleus"]["identity_root_sha256"],
        "i4_canonical_authority_promoted": i4["claim_boundary"]["canonical_authority_promoted"],
        "checkpoint15_git_sha": evidence["checkpoint15_git_sha"],
        "integration_git_sha": evidence["integration_git_sha"],
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": "NOT_GRANTED_BY_THIS_BINDING",
        "genesis_rom_promotion_claimed_by_membrane": False,
        "next_pass_to_census": 216,
    }


def preflight_pass218_membrane(
    *, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    return execute_surface_preflight(
        pass218_membrane_surface_declaration(),
        operation=PASS218_BIND_SYMBOL,
        cache=decision_cache,
    )


def preflight_pass217_membrane(
    *, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    pass217_membrane_source_evidence()
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    return execute_surface_preflight(
        pass217_membrane_surface_declaration(),
        operation=PASS217_BIND_SYMBOL,
        cache=decision_cache,
    )


__all__ = [
    "VERSION",
    "PASS_NUMBER",
    "CLASSIFICATION",
    "PASS217_NUMBER",
    "PASS217_CLASSIFICATION",
    "SURFACE_ID",
    "BIND_SYMBOL",
    "PASS218_SURFACE_ID",
    "PASS218_BIND_SYMBOL",
    "PASS217_SURFACE_ID",
    "PASS217_BIND_SYMBOL",
    "PASS218_CAPABILITIES",
    "PASS217_CAPABILITIES",
    "pass218_membrane_surface_declaration",
    "pass218_membrane_manifest",
    "pass217_membrane_source_evidence",
    "pass217_membrane_surface_declaration",
    "pass217_membrane_manifest",
    "preflight_pass218_membrane",
    "preflight_pass217_membrane",
]
