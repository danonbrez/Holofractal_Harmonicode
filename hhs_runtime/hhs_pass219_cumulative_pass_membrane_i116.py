"""Pass 219 I116 cumulative inherited-pass membrane.

The membrane exposes already-admitted inherited authorities without replacing
them. Pass 218 binds its terminal I48 completion seal. Pass 217 binds the
admitted cumulative utilization/reachability closure and authenticates the
frozen Iteration 4 Hash72-manifold / immutable-nucleus evidence as historical
authority. It deliberately does not rerun I4's historical current-runtime-blob
guard against later accepted runtime revisions. Neither binding grants C++ or
VM81 mutation authority or promotes a separate Genesis ROM.
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
PASS218_SURFACE_ID = "validator:pass219.inherited.pass218.completion"
PASS218_BIND_SYMBOL = "hhs_exact_pass219_bind_pass218_completion"
PASS217_SURFACE_ID = "validator:pass219.inherited.pass217.cumulative-closure"
PASS217_BIND_SYMBOL = "hhs_exact_pass219_bind_pass217_cumulative_closure"
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


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


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
