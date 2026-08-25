"""Pass 219 I119 inherited Pass 205 deterministic-continuation membrane.

This layer exposes the already-verified Pass 205 continuation nucleus without
changing its native transition, persistence, receipt, retrieval, or accelerator
semantics. Pass 205 remains the inherited singleton VM81 continuation authority
identified by the Pass 206 freeze; this module is read-only evidence binding.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i118_pass206 import pass206_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_19"
PASS205_NUMBER = 205
PASS205_CLASSIFICATION = "WIRED"
PASS205_CENSUS_CLASSIFICATION = "MISSING_MEMBRANE_EXPOSURE"
PASS205_BIND_SYMBOL = "hhs_exact_pass219_bind_pass205_deterministic_continuation"
PASS205_SURFACE_ID = "validator:pass219.inherited.pass205.deterministic-continuation"

PASS205_COMPLETION_PATH = Path("docs/pass205/PRODUCTION_COMPLETION.md")
PASS205_RECEIPT_PATH = Path("evidence/pass205/PASS205_PRODUCTION_COMPLETION_RECEIPT.json")
PASS206_FREEZE_PATH = Path("artifacts/pass206/CORE_FUNCTION_FREEZE_MANIFEST.json")

GROUNDING_BASELINE = "918121aeb6d1c55aa8fbd5d60b15f03c4eb22423"
IMPLEMENTATION_MERGE = "7be753b36d5b4c7a370b6435ddb027b6b05965d8"
CLOSURE_MERGE = "c717ab9e0437e1f407bbd3b22ed1fdd14bcd29b6"
COMPLETION_EVIDENCE_MERGE = "8e6cded890b86e36a2acd2162acf91d1cb4331ac"
COMPLETION_EVIDENCE_HEAD = "97f4e6a3828bd7fb85ad3cf9c2617c3ec99264e7"
CANDIDATE_MERGE_TREE = "73e3b87d162cfc73a9d6967a153a7cbb17b96e0d"
COMPLETION_RECEIPT_BLOB = "7884f6a2b00f1c2254fef5fdf87edca94ac5c6aa"
TERMINAL_RECEIPT_HASH72 = "87rndLmp6DJW!?V9S7ZZcP6xft4GX+(FCMTve!L(BNDEr4v>OoT/HV<RLeqQ4J9P64>HI8N4"
CLOSURE_WORKFLOW_RUN = 30837753796
CLOSURE_VALIDATION_JOB = 91766983285

PASS205_NATIVE_PATH = "hhs_runtime/c/hhs_pass205_continuation.c"
PASS205_BRIDGE_PATH = "hhs_python/runtime/hhs_pass205_continuation_bridge.py"

REQUIRED_OPERATIONS = (
    "validate_pass205_production_identity",
    "validate_pass205_vm81_authority",
    "validate_pass205_hash72_lineage",
    "validate_pass205_geometry",
    "validate_pass205_accelerator_boundary",
    "validate_pass206_successor_binding",
)


def _load(path: Path) -> Dict[str, Any]:
    value = json.loads((ROOT / path).read_text("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("PASS205_OBJECT_REQUIRED:" + str(path))
    return value


def _freeze_entry(freeze: Dict[str, Any], path: str) -> Dict[str, Any]:
    matches = [row for row in freeze.get("entries", []) if row.get("repository_path") == path]
    if len(matches) != 1:
        raise RuntimeError("PASS205_FREEZE_ENTRY_CARDINALITY_DRIFT:" + path)
    return dict(matches[0])


def pass205_membrane_source_evidence() -> Dict[str, Any]:
    receipt = _load(PASS205_RECEIPT_PATH)
    completion = (ROOT / PASS205_COMPLETION_PATH).read_text("utf-8")
    freeze = _load(PASS206_FREEZE_PATH)
    successor = pass206_membrane_source_evidence()

    if receipt.get("schema") != "HHS_PASS_205_PRODUCTION_COMPLETION_RECEIPT_V1":
        raise RuntimeError("PASS205_RECEIPT_SCHEMA_DRIFT")
    if receipt.get("classification") != "HHS_PASS_205_DETERMINISTIC_MULTIMODAL_CONTINUATION_RUNTIME_VERIFIED":
        raise RuntimeError("PASS205_RECEIPT_CLASSIFICATION_DRIFT")
    if receipt.get("closed") is not True:
        raise RuntimeError("PASS205_RECEIPT_CLOSURE_DRIFT")
    if receipt.get("contract") != "HHS-P205-VM5184-G243-DETERMINISTIC-MULTIMODAL-CONTINUATION-GAMING-ML-H72-H216":
        raise RuntimeError("PASS205_CONTRACT_IDENTITY_DRIFT")
    if receipt.get("implementation_merge_commit") != IMPLEMENTATION_MERGE:
        raise RuntimeError("PASS205_IMPLEMENTATION_LINEAGE_DRIFT")
    if receipt.get("authoritative_main_commit") != CLOSURE_MERGE:
        raise RuntimeError("PASS205_CLOSURE_LINEAGE_DRIFT")
    if receipt.get("closure_pull_request") != 150:
        raise RuntimeError("PASS205_CLOSURE_PR_DRIFT")

    workflow = receipt.get("closure_workflow") or {}
    if workflow.get("run_id") != CLOSURE_WORKFLOW_RUN or workflow.get("validate_job_id") != CLOSURE_VALIDATION_JOB:
        raise RuntimeError("PASS205_CLOSURE_WORKFLOW_DRIFT")
    if workflow.get("validation_conclusion") != "success" or workflow.get("merge_conclusion") != "success":
        raise RuntimeError("PASS205_CLOSURE_VALIDATION_DRIFT")
    if workflow.get("candidate_merge_commit") != CANDIDATE_MERGE_TREE:
        raise RuntimeError("PASS205_CANDIDATE_MERGE_IDENTITY_DRIFT")

    checks = receipt.get("checks") or {}
    required_true = (
        "native_library_built",
        "q_bijection_complete",
        "continuation_chain_verified",
        "replay_verified",
        "retrieval_exact_rerank",
        "retrieval_hydration_verified",
        "accelerator_cpu_oracle",
        "gpu_commit_forbidden",
        "single_hash72_commit_stream",
        "single_vm81_mutation_authority",
        "no_float_canonical_authority",
    )
    for key in required_true:
        if checks.get(key) is not True:
            raise RuntimeError("PASS205_REQUIRED_CHECK_DRIFT:" + key)

    runtime = receipt.get("runtime") or {}
    exact_runtime = {
        "cell_count": 81,
        "bits_per_cell": 64,
        "state_bits": 5184,
        "control_count": 243,
        "hydration_projection_count": 1259712,
        "projection_channel_count": 32,
        "canonical_float_fields": 0,
    }
    for key, expected in exact_runtime.items():
        if runtime.get(key) != expected:
            raise RuntimeError("PASS205_RUNTIME_GEOMETRY_DRIFT:" + key)

    measurements = receipt.get("measurements") or {}
    if measurements.get("q_addresses_verified") != 1259712:
        raise RuntimeError("PASS205_Q_VERIFICATION_DRIFT")
    if measurements.get("ordered_chain_generations") != 73:
        raise RuntimeError("PASS205_CHAIN_GENERATION_DRIFT")
    if measurements.get("stored_snapshots") != 77 or measurements.get("lineage_edges") != 76:
        raise RuntimeError("PASS205_PERSISTED_LINEAGE_DRIFT")

    terminal_receipt = str((receipt.get("roots") or {}).get("terminal_receipt_hash72") or "")
    if terminal_receipt != TERMINAL_RECEIPT_HASH72 or len(terminal_receipt) != 72:
        raise RuntimeError("PASS205_TERMINAL_HASH72_DRIFT")

    if freeze.get("grounding_baseline") != GROUNDING_BASELINE:
        raise RuntimeError("PASS205_PASS206_FREEZE_BASELINE_DRIFT")
    native = _freeze_entry(freeze, PASS205_NATIVE_PATH)
    bridge = _freeze_entry(freeze, PASS205_BRIDGE_PATH)
    if native.get("semantic_category") != "SINGLETON_VM81_CONTINUATION_IMPLEMENTATION":
        raise RuntimeError("PASS205_NATIVE_AUTHORITY_CLASSIFICATION_DRIFT")
    if native.get("git_blob") != "4eec6d600bf1dfc544132ec287b6c0968e5a08d3":
        raise RuntimeError("PASS205_NATIVE_FROZEN_BLOB_DRIFT")
    if bridge.get("semantic_category") != "PYTHON_NATIVE_AUTHORITY_BRIDGE":
        raise RuntimeError("PASS205_BRIDGE_AUTHORITY_CLASSIFICATION_DRIFT")
    if bridge.get("git_blob") != "d91e4a0905d450d28397a2ec02952c36624f69ac":
        raise RuntimeError("PASS205_BRIDGE_FROZEN_BLOB_DRIFT")
    if "singleton_vm81_admission" not in (bridge.get("receipt_replay_obligations") or []):
        raise RuntimeError("PASS205_BRIDGE_VM81_OBLIGATION_DRIFT")

    successor_contract = successor.get("contract") or {}
    if successor_contract.get("pass") != 206:
        raise RuntimeError("PASS205_PASS206_SUCCESSOR_DRIFT")
    if successor.get("grounding_baseline") != GROUNDING_BASELINE:
        raise RuntimeError("PASS205_PASS206_SUCCESSOR_BASELINE_DRIFT")

    if "Pass 205 production implementation is complete and verified." not in completion:
        raise RuntimeError("PASS205_COMPLETION_DOCUMENT_STATUS_DRIFT")
    if "single VM81 mutation/admission authority" not in completion:
        raise RuntimeError("PASS205_COMPLETION_DOCUMENT_AUTHORITY_DRIFT")

    return {
        "receipt": receipt,
        "completion_document": completion,
        "pass206_freeze_manifest": freeze,
        "pass206_successor": successor,
        "grounding_baseline": GROUNDING_BASELINE,
        "implementation_merge": IMPLEMENTATION_MERGE,
        "closure_merge": CLOSURE_MERGE,
        "completion_evidence_merge": COMPLETION_EVIDENCE_MERGE,
        "completion_evidence_head": COMPLETION_EVIDENCE_HEAD,
        "candidate_merge_tree": CANDIDATE_MERGE_TREE,
        "completion_receipt_blob": COMPLETION_RECEIPT_BLOB,
        "terminal_receipt_hash72": TERMINAL_RECEIPT_HASH72,
        "native_freeze_entry": native,
        "bridge_freeze_entry": bridge,
    }


def validate_pass205_production_identity() -> Dict[str, Any]:
    source = pass205_membrane_source_evidence()
    return {
        "ok": True,
        "classification": source["receipt"]["classification"],
        "closure_merge": source["closure_merge"],
    }


def validate_pass205_vm81_authority() -> Dict[str, Any]:
    source = pass205_membrane_source_evidence()
    return {
        "ok": True,
        "canonical_mutation_authority": "VM81_KERNEL",
        "canonical_mutation_authority_count": 1,
        "native_semantic_category": source["native_freeze_entry"]["semantic_category"],
        "bridge_semantic_category": source["bridge_freeze_entry"]["semantic_category"],
    }


def validate_pass205_hash72_lineage() -> Dict[str, Any]:
    source = pass205_membrane_source_evidence()
    return {
        "ok": True,
        "canonical_hash72_commit_stream_count": 1,
        "terminal_receipt_hash72": source["terminal_receipt_hash72"],
        "hash216_mutation_authority": False,
    }


def validate_pass205_geometry() -> Dict[str, Any]:
    runtime = pass205_membrane_source_evidence()["receipt"]["runtime"]
    return {
        "ok": True,
        "cell_count": runtime["cell_count"],
        "state_bits": runtime["state_bits"],
        "control_count": runtime["control_count"],
        "q_address_count": runtime["hydration_projection_count"],
        "projection_channel_count": runtime["projection_channel_count"],
    }


def validate_pass205_accelerator_boundary() -> Dict[str, Any]:
    source = pass205_membrane_source_evidence()
    return {
        "ok": True,
        "accelerator_candidate_only": True,
        "accelerator_may_commit_hash72": False,
        "physical_gpu_execution_claimed": source["receipt"]["accelerator_translation"]["physical_gpu_execution_claimed"],
    }


def validate_pass206_successor_binding() -> Dict[str, Any]:
    source = pass205_membrane_source_evidence()
    return {
        "ok": True,
        "successor_pass": source["pass206_successor"]["contract"]["pass"],
        "successor_preserves_single_vm81_authority": True,
    }


def pass205_surface_declaration() -> Dict[str, Any]:
    pass205_membrane_source_evidence()
    return {
        "surface_id": PASS205_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i119_pass205",
        "symbol": "validate_pass205_production_identity",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS_PASS_205_PRODUCTION_COMPLETION_RECEIPT_V1",
            "HHS_PASS_206_CORE_FUNCTION_FREEZE_MANIFEST_V1",
        ],
        "witness_schemas": [
            "HHSExactPass205DeterministicContinuationWitnessV1",
            "HHSExactPass219InheritedPass205BindingV1",
        ],
        "validators": [PASS205_BIND_SYMBOL, "validate_pass205_production_identity"],
        "guards": [
            "pass205_exact_production_identity",
            "pass205_single_vm81_authority",
            "pass205_single_hash72_stream",
            "pass205_exact_vm5184_g243_geometry",
            "pass205_exact_sparse_full_equivalence",
            "pass205_exact_retrieval_rerank",
            "pass205_accelerator_candidate_only",
            "pass205_pass206_successor_preserved",
        ],
        "rejection_codes": [
            "REJECT_PASS205_PRODUCTION_IDENTITY_DRIFT",
            "REJECT_PASS205_AUTHORITY_ESCALATION",
            "REJECT_PASS205_GEOMETRY_DRIFT",
            "REJECT_PASS205_APPROXIMATE_ADMISSION",
            "REJECT_PASS205_ACCELERATOR_MUTATION_AUTHORITY",
            "REJECT_PASS205_PASS206_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_EVIDENCE_IDENTITY_ONLY",
        "boundedness_policy": "PASS_205_VERIFIED_CONTINUATION_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass205_membrane_manifest() -> Dict[str, Any]:
    source = pass205_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS205_NUMBER,
        "classification": PASS205_CLASSIFICATION,
        "census_classification": PASS205_CENSUS_CLASSIFICATION,
        "pass219_c_abi_surface": PASS205_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass205DeterministicContinuation",
        "canonical_mutation_authority": "VM81_KERNEL",
        "canonical_mutation_authority_count": 1,
        "canonical_hash72_commit_stream_count": 1,
        "vm5184_state_bits": 5184,
        "g243_control_count": 243,
        "q_address_count": 1259712,
        "projection_channel_count": 32,
        "q_bijection_bound": True,
        "exact_sparse_full_equivalence_bound": True,
        "exact_retrieval_rerank_bound": True,
        "accelerator_candidate_only": True,
        "accelerator_may_commit_hash72": False,
        "physical_gpu_execution_claimed": False,
        "pass206_successor_bound": True,
        "pass219_new_canonical_mutation_authority": False,
        "pass219_new_persistence_authority": False,
        "pass219_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "completion_receipt_blob": source["completion_receipt_blob"],
        "next_pass_to_census": 204,
    }


def preflight_pass205_membrane() -> Dict[str, Any]:
    declaration = pass205_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    ok = all(row.get("ok") is True for row in rows)
    return {
        "schema": "HHS_PASS219_I119_PASS205_MEMBRANE_PREFLIGHT_V1",
        "ok": ok,
        "surface_id": PASS205_SURFACE_ID,
        "operations": rows,
        "manifest": pass205_membrane_manifest(),
    }


if __name__ == "__main__":
    print(json.dumps(preflight_pass205_membrane(), indent=2, sort_keys=True))
