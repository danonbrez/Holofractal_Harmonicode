"""Pass 219 I116 cumulative inherited-pass membrane.

The membrane exposes already-admitted inherited authorities without replacing
them. Pass 218 binds its terminal I48 completion seal. Pass 217 binds the
admitted cumulative utilization/reachability closure and authenticates frozen
Iteration 4 Hash72-manifold / immutable-nucleus evidence as historical
authority. Pass 216 binds its completed reserved-number contract and
inheritance-alignment policy while explicitly preserving that its optional
runtime-optimization roadmap was not claimed complete. No binding grants C++
or VM81 mutation authority.
"""

from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass217_cumulative_closure_v1 import (
    build_cumulative_utilization_reachability_closure,
)

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_16"
PASS_NUMBER = 218
CLASSIFICATION = "WIRED"
PASS217_NUMBER = 217
PASS217_CLASSIFICATION = "WIRED"
PASS216_NUMBER = 216
PASS216_CLASSIFICATION = "WIRED"
PASS218_SURFACE_ID = "validator:pass219.inherited.pass218.completion"
PASS218_BIND_SYMBOL = "hhs_exact_pass219_bind_pass218_completion"
PASS217_SURFACE_ID = "validator:pass219.inherited.pass217.cumulative-closure"
PASS217_BIND_SYMBOL = "hhs_exact_pass219_bind_pass217_cumulative_closure"
PASS216_SURFACE_ID = "validator:pass219.inherited.pass216.contract-alignment"
PASS216_BIND_SYMBOL = "hhs_exact_pass219_bind_pass216_alignment"
SURFACE_ID = PASS218_SURFACE_ID
BIND_SYMBOL = PASS218_BIND_SYMBOL
ROOT = Path(__file__).resolve().parents[1]

PASS217_I4_EVIDENCE_PATH = Path(
    "evidence/pass217/PASS_217_ITERATION_4_HASH72_MANIFOLD_NUCLEUS.json"
)
PASS217_I4_RECORD_ROOT = "5c996cda648db2074a144ab8b9b0834ef442ee8bc2b2c7ed91885bc38aa6d03f"
PASS217_I4_CANDIDATE_SHA256 = "97379c7ae7cdaebd8031a3a3fb58559c967b361b360c7db34ec096acabfc8fe8"
PASS217_I4_ADDRESS_MAP_SHA256 = "2f8d8a23114b87f2dbe91f3d302ef089b750f9d91f533d744a4524e907717f5f"
PASS217_I4_MATRIX_ROOT_SHA256 = "6c0b2e9e354e8d7eb17a746d01c157b19aa95b58296884126cdf5bef7998e286"
PASS217_I4_MANIFOLD_ROOT_SHA256 = "c757bae150d9ab94485c680ec3143e715b674d35f445a72c6fb4ea2def6f7884"
PASS217_I4_NUCLEUS_IDENTITY_SHA256 = "da7b33fa1a419e00ce81eeeeb5f1c435acd6ae7b95d355e3a1749a6a238e3164"
PASS217_I4_NUCLEUS_SUPPORT_SHA256 = "ac46211412784990e08e5cf0b80df5db381aad612a7ccd8aa816815a105b0294"
PASS217_I4_PROTECTED_RUNTIME_BLOB = "362cd6e892ae66024333b111aec83f12023fdce3"
PASS217_CHECKPOINT15_GIT_SHA = "be71da59c9b8b7c7e055c03da703ca301849cfff"
PASS217_INTEGRATION_GIT_SHA = "b0656a92ab29507f81eae760e070f74e49db83f4"

PASS216_CONTRACT_PATH = Path("contracts/pass216/PASS_216_CONTRACT.json")
PASS216_ADDENDUM_PATH = Path(
    "contracts/pass216/PASS_216_DETERMINISM_INHERITANCE_ADDENDUM.json"
)
PASS216_PASS215_FINAL_HEAD = "b85ea7c340976a20a78f9c7d8d89a688a1b4f8fc"
PASS216_PASS215_FINAL_TREE = "17127e80a3f4852aeaedd1b807971fb4b4fba229"
PASS216_PASS215_MAIN_MERGE = "cc7a0d67d7d9e4bd1e800f62d5ef577cb4ab1086"
PASS216_PASS215_ARTIFACT_SHA256 = "9e71ff3f48cd4da24c34854f8eadfa57f26d7c6ef5bddd1026c89e2ace63bf55"
PASS216_PUBLISHED_HEAD = "0ad2759a4379376244589aa3ee241e51d779df26"
PASS216_PUBLISHED_TREE = "b9ff48b17f1e3c8272cd8c5c7b4381df69d4c7e9"
PASS216_MERGE_COMMIT = "f10e453c5d7c7467cf5e57f6452958491fe763ad"
PASS216_CONTRACT_GIT_BLOB = "9e04e4aca8b127e009c0343ceb5e78092de40c43"
PASS216_ADDENDUM_GIT_BLOB = "3e4121afe2f5750283f5ef350c0afa416eb2addd"
PASS216_SELECTED_TOKEN_IDS = (450, 6575, 471, 528, 2827, 322, 278)

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

PASS216_CAPABILITIES = (
    "RESERVED_NUMBER_CONTRACT_ALIGNMENT_COMPLETE",
    "PASS215_TERMINAL_REFERENCE_BINDING",
    "GLOBAL_STRICT_MODE_SUNSET",
    "DETERMINISTIC_TRUTH_GATE_SCOPING",
    "DEPENDENCY_SCOPED_EXACT_VALIDATION",
    "UNCHANGED_AUTHORITY_IDENTITY_REUSE",
    "EXACT_REFERENCE_FIXTURE_POLICY",
    "LOSSLESS_NO_FLOAT_OPTIMIZATION_POLICY",
)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_float(item) for item in value)
    return False


def _verify_frozen_pass217_i4_evidence() -> Dict[str, Any]:
    path = ROOT / PASS217_I4_EVIDENCE_PATH
    record = json.loads(path.read_text("utf-8"))
    if record.get("schema") != "HHS_PASS_217_ITERATION_4_HASH72_MANIFOLD_NUCLEUS_V1":
        raise RuntimeError("PASS217_I4_EVIDENCE_SCHEMA_DRIFT")
    if record.get("classification") != "HHS_PASS_217_ITERATION_4_RECONCILED_HASH72_MANIFOLD_NUCLEUS_VERIFIED":
        raise RuntimeError("PASS217_I4_EVIDENCE_CLASSIFICATION_DRIFT")
    if record.get("pass") != 217 or record.get("iteration") != 4:
        raise RuntimeError("PASS217_I4_EVIDENCE_IDENTITY_DRIFT")
    observed_root = record.get("record_root_sha256")
    unsigned = dict(record)
    unsigned.pop("record_root_sha256", None)
    computed_root = sha256(_canonical_bytes(unsigned)).hexdigest()
    if observed_root != PASS217_I4_RECORD_ROOT or computed_root != PASS217_I4_RECORD_ROOT:
        raise RuntimeError("PASS217_I4_EVIDENCE_ROOT_DRIFT")

    frozen = record["frozen_inputs"]
    if frozen["logical_genesis_candidate"].get("sha256") != PASS217_I4_CANDIDATE_SHA256:
        raise RuntimeError("PASS217_I4_CANDIDATE_IDENTITY_DRIFT")
    if frozen["logical_genesis_candidate"].get("byte_count") != 648:
        raise RuntimeError("PASS217_I4_CANDIDATE_SIZE_DRIFT")
    if frozen["address_map"].get("sha256") != PASS217_I4_ADDRESS_MAP_SHA256:
        raise RuntimeError("PASS217_I4_ADDRESS_MAP_IDENTITY_DRIFT")
    protected = frozen["protected_vm81_runtime"]
    if protected.get("git_blob") != PASS217_I4_PROTECTED_RUNTIME_BLOB or protected.get("modified") is not False:
        raise RuntimeError("PASS217_I4_HISTORICAL_RUNTIME_WITNESS_DRIFT")

    manifold = record["hash72_manifold"]
    if manifold.get("symbol_count") != 72 or manifold.get("matrix_positions") != 5184:
        raise RuntimeError("PASS217_I4_HASH72_GEOMETRY_DRIFT")
    if manifold.get("matrix_root_sha256") != PASS217_I4_MATRIX_ROOT_SHA256:
        raise RuntimeError("PASS217_I4_MATRIX_ROOT_DRIFT")
    if manifold.get("manifold_root_sha256") != PASS217_I4_MANIFOLD_ROOT_SHA256:
        raise RuntimeError("PASS217_I4_MANIFOLD_ROOT_DRIFT")
    directions = manifold.get("wrapped_directions") or []
    if len(directions) != 4 or any(row.get("order") != 72 for row in directions):
        raise RuntimeError("PASS217_I4_ORBIT_ORDER_DRIFT")

    nucleus = record["immutable_nucleus"]
    if nucleus.get("identity_root_sha256") != PASS217_I4_NUCLEUS_IDENTITY_SHA256:
        raise RuntimeError("PASS217_I4_NUCLEUS_IDENTITY_DRIFT")
    if nucleus.get("support_root_sha256") != PASS217_I4_NUCLEUS_SUPPORT_SHA256:
        raise RuntimeError("PASS217_I4_NUCLEUS_SUPPORT_DRIFT")
    if nucleus.get("fixed_pointwise") is not True or nucleus.get("support_bits") != 576:
        raise RuntimeError("PASS217_I4_NUCLEUS_FIXED_POINT_DRIFT")

    gate = record["inheritance_gate"]
    if gate.get("predecessor_reconciliation_complete") is not True:
        raise RuntimeError("PASS217_I4_RECONCILIATION_DRIFT")
    if gate.get("iteration1_3_artifacts_regenerated") is not False:
        raise RuntimeError("PASS217_I4_FROZEN_ARTIFACT_REGEN_DRIFT")
    if gate.get("canonical_promotion_allowed_by_iteration4") is not False:
        raise RuntimeError("PASS217_I4_PROMOTION_GATE_DRIFT")

    claim = record["claim_boundary"]
    if claim.get("hash72_manifold_validated") is not True:
        raise RuntimeError("PASS217_I4_HASH72_MANIFOLD_UNVERIFIED")
    if claim.get("immutable_nucleus_validated") is not True:
        raise RuntimeError("PASS217_I4_NUCLEUS_UNVERIFIED")
    for field in (
        "canonical_authority_promoted",
        "canonical_genesis_selected",
        "logical_genesis_rom_generated",
        "runtime_mutation_performed",
        "authoritative_hash72_transition_receipt_minted",
        "authoritative_hash216_transition_minted",
        "pass219_runtime_implementation_started",
    ):
        if claim.get(field) is not False:
            raise RuntimeError("PASS217_I4_CLAIM_BOUNDARY_DRIFT:" + field)
    return record


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


@lru_cache(maxsize=1)
def pass217_membrane_source_evidence() -> Dict[str, Any]:
    closure = build_cumulative_utilization_reachability_closure()
    i4_record = _verify_frozen_pass217_i4_evidence()

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

    return {
        "closure": closure,
        "iteration4": i4_record,
        "checkpoint15_git_sha": PASS217_CHECKPOINT15_GIT_SHA,
        "integration_git_sha": PASS217_INTEGRATION_GIT_SHA,
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
            "verify_frozen_pass217_iteration4_evidence",
        ],
        "guards": [
            "pass217_required_authority_nonbypass_gate",
            "pass217_global_surface_publication_gate",
            "pass217_incremental_tokenization_active_path_gate",
            "pass217_i4_frozen_evidence_root_gate",
            "pass217_i4_hash72_manifold_gate",
            "pass217_i4_immutable_nucleus_gate",
            "pass217_i4_no_genesis_rom_promotion_gate",
            "single_c_vm81_mutation_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS217_CUMULATIVE_CLOSURE_BLOCKED",
            "REJECT_PASS217_REQUIRED_AUTHORITY_BYPASS",
            "REJECT_PASS217_INCREMENTAL_TOKENIZATION_GAP",
            "REJECT_PASS217_I4_FROZEN_EVIDENCE_DRIFT",
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
        "supporting_authority_surface": str(PASS217_I4_EVIDENCE_PATH),
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
        "i4_record_root_sha256": i4["record_root_sha256"],
        "i4_hash72_manifold_root_sha256": i4["hash72_manifold"]["manifold_root_sha256"],
        "i4_nucleus_identity_root_sha256": i4["immutable_nucleus"]["identity_root_sha256"],
        "i4_historical_runtime_blob": i4["frozen_inputs"]["protected_vm81_runtime"]["git_blob"],
        "i4_historical_runtime_blob_is_current_runtime_requirement": False,
        "i4_canonical_authority_promoted": i4["claim_boundary"]["canonical_authority_promoted"],
        "checkpoint15_git_sha": evidence["checkpoint15_git_sha"],
        "integration_git_sha": evidence["integration_git_sha"],
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": "NOT_GRANTED_BY_THIS_BINDING",
        "genesis_rom_promotion_claimed_by_membrane": False,
        "next_pass_to_census": 216,
    }


@lru_cache(maxsize=1)
def pass216_membrane_source_evidence() -> Dict[str, Any]:
    contract = json.loads((ROOT / PASS216_CONTRACT_PATH).read_text("utf-8"))
    addendum = json.loads((ROOT / PASS216_ADDENDUM_PATH).read_text("utf-8"))

    if _contains_float(contract) or _contains_float(addendum):
        raise RuntimeError("PASS216_ALIGNMENT_FLOAT_AUTHORITY_DRIFT")
    if contract.get("schema") != "HHS_PASS_216_CONTRACT_V3" or contract.get("pass") != 216:
        raise RuntimeError("PASS216_CONTRACT_IDENTITY_DRIFT")
    if contract.get("status") != "CONTRACT_COMPLETE_PARENT_TERMINAL_ALIGNED":
        raise RuntimeError("PASS216_CONTRACT_STATUS_DRIFT")
    boundary = contract["completion_boundary"]
    if boundary.get("contract_layer_complete") is not True or boundary.get("parent_alignment_complete") is not True:
        raise RuntimeError("PASS216_ALIGNMENT_INCOMPLETE")
    if boundary.get("runtime_optimization_implementation_claimed") is not False:
        raise RuntimeError("PASS216_RUNTIME_OPTIMIZATION_OVERCLAIM")
    if boundary.get("pass216_runtime_implementation_required_before_pass217_continuation") is not False:
        raise RuntimeError("PASS216_RUNTIME_PREDECESSOR_GATE_DRIFT")

    parent = contract["parent_binding"]
    expected_parent = {
        "final_closure_head": PASS216_PASS215_FINAL_HEAD,
        "final_closure_tree": PASS216_PASS215_FINAL_TREE,
        "main_merge_commit": PASS216_PASS215_MAIN_MERGE,
        "final_closure_artifact_sha256": PASS216_PASS215_ARTIFACT_SHA256,
    }
    for field, expected in expected_parent.items():
        if parent.get(field) != expected:
            raise RuntimeError("PASS216_PARENT_BINDING_DRIFT:" + field)
    if parent.get("final_closure_run") != 31325831364 or parent.get("final_closure_job") != 93275935886:
        raise RuntimeError("PASS216_PARENT_VALIDATION_IDENTITY_DRIFT")
    if parent.get("final_closure_cumulative_controls") != 240:
        raise RuntimeError("PASS216_PARENT_CONTROL_COUNT_DRIFT")

    strict = contract["strict_mode_lifecycle"]
    if strict.get("global_strict_mode_after_successful_pass215_terminal_closure") is not False:
        raise RuntimeError("PASS216_STRICT_MODE_SUNSET_DRIFT")
    validation = contract["validation_policy"]
    if validation.get("global_strict_mode_enabled") is not False:
        raise RuntimeError("PASS216_GLOBAL_STRICT_DEFAULT_DRIFT")
    if validation.get("cumulative_strict_workflow_replay_required") is not False:
        raise RuntimeError("PASS216_CUMULATIVE_REPLAY_DEFAULT_DRIFT")
    if validation.get("changed_surface_exactness_required") is not True:
        raise RuntimeError("PASS216_CHANGED_SURFACE_EXACTNESS_DRIFT")
    if validation.get("repair_forward") is not True:
        raise RuntimeError("PASS216_REPAIR_FORWARD_DRIFT")

    non_goals = contract["non_goals"]
    if non_goals.get("floating_point_canonical_authority") is not False:
        raise RuntimeError("PASS216_FLOAT_AUTHORITY_DRIFT")
    if contract["optimization_domains"]["exact_storage_compression"].get(
        "lossy_authoritative_methods_allowed"
    ) is not False:
        raise RuntimeError("PASS216_LOSSY_AUTHORITY_DRIFT")
    baseline = contract["pass215_terminal_frozen_baseline"]
    if tuple(baseline.get("selected_token_ids", ())) != PASS216_SELECTED_TOKEN_IDS:
        raise RuntimeError("PASS216_SELECTED_TOKEN_FIXTURE_DRIFT")
    if baseline.get("termination_reason") != "MAX_NEW_TOKENS":
        raise RuntimeError("PASS216_TERMINATION_FIXTURE_DRIFT")

    if addendum.get("schema") != "HHS_PASS_216_DETERMINISM_INHERITANCE_ADDENDUM_V3":
        raise RuntimeError("PASS216_ADDENDUM_IDENTITY_DRIFT")
    if addendum.get("status") != "AUTHORITATIVE_CONTRACT_ADDENDUM":
        raise RuntimeError("PASS216_ADDENDUM_STATUS_DRIFT")
    truth_gate = addendum["sha256_deterministic_truth_gate"]
    if truth_gate.get("default_state") != "CLOSED":
        raise RuntimeError("PASS216_TRUTH_GATE_DEFAULT_DRIFT")
    if truth_gate.get("full_system_reproof_required_by_default") is not False:
        raise RuntimeError("PASS216_FULL_REPROOF_DEFAULT_DRIFT")
    operating = addendum["pass216_operating_rule"]
    if operating.get("global_strict_mode_default") is not False:
        raise RuntimeError("PASS216_OPERATING_STRICT_DEFAULT_DRIFT")
    if operating.get("unchanged_authenticated_identity_requires_reexecution") is not False:
        raise RuntimeError("PASS216_UNCHANGED_REEXECUTION_DRIFT")
    if operating.get("unchanged_authenticated_identity_requires_only_identity_verification") is not True:
        raise RuntimeError("PASS216_IDENTITY_VERIFICATION_RULE_DRIFT")
    if operating.get("changed_transition_requires_dependency_scoped_exact_validation") is not True:
        raise RuntimeError("PASS216_DEPENDENCY_SCOPED_RULE_DRIFT")
    successor = addendum["successor_inheritance"]
    if successor.get("pass216_contract_alignment_is_complete") is not True:
        raise RuntimeError("PASS216_SUCCESSOR_ALIGNMENT_DRIFT")
    if successor.get("pass216_runtime_optimization_implementation_is_not_claimed") is not True:
        raise RuntimeError("PASS216_SUCCESSOR_RUNTIME_OVERCLAIM")
    if successor.get("pass219_must_inherit_unchanged_pass215_pass216_and_pass217_authority") is not True:
        raise RuntimeError("PASS216_PASS219_INHERITANCE_DRIFT")

    return {
        "contract": contract,
        "addendum": addendum,
        "pass216_published_head": PASS216_PUBLISHED_HEAD,
        "pass216_published_tree": PASS216_PUBLISHED_TREE,
        "pass216_merge_commit": PASS216_MERGE_COMMIT,
        "contract_git_blob": PASS216_CONTRACT_GIT_BLOB,
        "addendum_git_blob": PASS216_ADDENDUM_GIT_BLOB,
    }


def pass216_membrane_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": PASS216_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime_exact_abi",
        "symbol": PASS216_BIND_SYMBOL,
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS_PASS_216_CONTRACT_V3",
            "HHS_PASS_216_DETERMINISM_INHERITANCE_ADDENDUM_V3",
            "HHS_PASS219_INHERITED_PASS216_ALIGNMENT_BINDING_1_16",
        ],
        "witness_schemas": [
            "PASS_215_ITERATION_20_TERMINAL_CLOSURE",
            "HHS_PASS219_PASS216_ALIGNMENT_WITNESS_V1",
        ],
        "validators": [
            PASS216_BIND_SYMBOL,
            "pass216_contract_alignment_validation",
        ],
        "guards": [
            "pass216_parent_terminal_identity_gate",
            "pass216_contract_blob_identity_gate",
            "pass216_truth_gate_scope_gate",
            "pass216_dependency_scoped_validation_gate",
            "pass216_no_runtime_optimization_overclaim_gate",
            "pass216_no_global_strict_default_gate",
            "pass216_no_lossy_or_float_authority_gate",
            "single_c_vm81_mutation_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS216_PARENT_IDENTITY_DRIFT",
            "REJECT_PASS216_CONTRACT_OR_ADDENDUM_DRIFT",
            "REJECT_PASS216_GLOBAL_STRICT_DEFAULT_REINTRODUCTION",
            "REJECT_PASS216_UNCHANGED_IDENTITY_REEXECUTION_REQUIREMENT",
            "REJECT_PASS216_FULL_SYSTEM_REPROOF_DEFAULT",
            "REJECT_PASS216_RUNTIME_OPTIMIZATION_OVERCLAIM",
            "REJECT_PASS216_LOSSY_OR_FLOAT_AUTHORITY",
            "REJECT_PASS216_CPP_MUTATION_AUTHORITY",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_CONTRACT_ALIGNMENT_IDENTITY_ONLY",
        "boundedness_policy": "PASS_216_COMPLETED_CONTRACT_ALIGNMENT_NOT_OPTIONAL_RUNTIME_ROADMAP",
        "declared_operations": [PASS216_BIND_SYMBOL],
    }


def pass216_membrane_manifest() -> Dict[str, Any]:
    evidence = pass216_membrane_source_evidence()
    contract = evidence["contract"]
    addendum = evidence["addendum"]
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS216_NUMBER,
        "classification": PASS216_CLASSIFICATION,
        "authoritative_surface": str(PASS216_CONTRACT_PATH),
        "supporting_authority_surface": str(PASS216_ADDENDUM_PATH),
        "pass219_c_abi_surface": PASS216_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass216Alignment",
        "capabilities": list(PASS216_CAPABILITIES),
        "contract_alignment_complete": contract["completion_boundary"]["contract_layer_complete"],
        "parent_alignment_complete": contract["completion_boundary"]["parent_alignment_complete"],
        "pass215_final_head": contract["parent_binding"]["final_closure_head"],
        "pass215_artifact_sha256": contract["parent_binding"]["final_closure_artifact_sha256"],
        "pass216_published_head": evidence["pass216_published_head"],
        "pass216_published_tree": evidence["pass216_published_tree"],
        "pass216_merge_commit": evidence["pass216_merge_commit"],
        "contract_git_blob": evidence["contract_git_blob"],
        "addendum_git_blob": evidence["addendum_git_blob"],
        "truth_gate_default_state": addendum["sha256_deterministic_truth_gate"]["default_state"],
        "global_strict_mode_default": addendum["pass216_operating_rule"]["global_strict_mode_default"],
        "dependency_scoped_exact_validation": addendum["pass216_operating_rule"][
            "changed_transition_requires_dependency_scoped_exact_validation"
        ],
        "unchanged_identity_requires_reexecution": addendum["pass216_operating_rule"][
            "unchanged_authenticated_identity_requires_reexecution"
        ],
        "runtime_optimization_implementation_claimed": contract["completion_boundary"][
            "runtime_optimization_implementation_claimed"
        ],
        "runtime_optimization_roadmap_complete": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": "NOT_GRANTED_BY_THIS_BINDING",
        "next_pass_to_census": 215,
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


def preflight_pass216_membrane(
    *, cache: Optional[MutableMapping[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    pass216_membrane_source_evidence()
    decision_cache: MutableMapping[str, Dict[str, Any]] = cache if cache is not None else {}
    return execute_surface_preflight(
        pass216_membrane_surface_declaration(),
        operation=PASS216_BIND_SYMBOL,
        cache=decision_cache,
    )


__all__ = [
    "VERSION",
    "PASS_NUMBER",
    "CLASSIFICATION",
    "PASS217_NUMBER",
    "PASS217_CLASSIFICATION",
    "PASS216_NUMBER",
    "PASS216_CLASSIFICATION",
    "SURFACE_ID",
    "BIND_SYMBOL",
    "PASS218_SURFACE_ID",
    "PASS218_BIND_SYMBOL",
    "PASS217_SURFACE_ID",
    "PASS217_BIND_SYMBOL",
    "PASS216_SURFACE_ID",
    "PASS216_BIND_SYMBOL",
    "PASS218_CAPABILITIES",
    "PASS217_CAPABILITIES",
    "PASS216_CAPABILITIES",
    "pass218_membrane_surface_declaration",
    "pass218_membrane_manifest",
    "pass217_membrane_source_evidence",
    "pass217_membrane_surface_declaration",
    "pass217_membrane_manifest",
    "pass216_membrane_source_evidence",
    "pass216_membrane_surface_declaration",
    "pass216_membrane_manifest",
    "preflight_pass218_membrane",
    "preflight_pass217_membrane",
    "preflight_pass216_membrane",
]
