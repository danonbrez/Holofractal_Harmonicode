"""Pass 219 I118 inherited Pass 206 cumulative-enforcement membrane."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass206_cumulative_enforcement_v1 import validate_pass206_enforcement
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i117_pass207 import pass207_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_18"
PASS206_NUMBER = 206
PASS206_CLASSIFICATION = "WIRED"
PASS206_BIND_SYMBOL = "hhs_exact_pass219_bind_pass206_cumulative_enforcement"
PASS206_SURFACE_ID = "validator:pass219.inherited.pass206.cumulative-enforcement"

PASS206_CONTRACT_PATH = Path("contracts/pass206/PASS_206_CONTRACT.json")
PASS206_FREEZE_PATH = Path("artifacts/pass206/CORE_FUNCTION_FREEZE_MANIFEST.json")
PASS206_REPAIR_LINEAGE_PATH = Path("artifacts/pass206/CORE_SUCCESSOR_REPAIR_LINEAGE.json")
PASS206_MATRIX_PATH = Path("artifacts/pass206/VALIDATION_MATRIX.json")
PASS206_RECEIPT_PATH = Path("artifacts/pass206/PASS_206_COMPLETION_RECEIPT.json")
PASS206_COMPLETION_PATH = Path("docs/pass206/COMPLETION.md")

GROUNDING_BASELINE = "918121aeb6d1c55aa8fbd5d60b15f03c4eb22423"
SEALED_PREDECESSOR = "2fe770d68f6e1da172d2c7992a90e31d69577b90"
FREEZE_CHECKPOINT = "84e057047e6c3da8753ea500a88193f769e49cca"
DEVELOPMENT_COMPLETION_HEAD = "16d17c1db690116fdc5f5b63ef7a097548685885"
APPROVED_REPAIR_MERGE = "284bf652d9635cc0c940f79dfe6aff6f8b787c3c"
FREEZE_MANIFEST_SHA256 = "d60f6191c3fd77d8255e629dc73a7050d4093fe94845ff1bc63bd81d2dfa6da2"
REPAIR_LINEAGE_SHA256 = "29d0fa640d9a75b6520738826df3e17b769fc4129db4771c8720b7039b4f3440"
PRE_RECEIPT_MATRIX_SHA256 = "1f4da9ca815d99f76c30e26076435cc277c3912ce1658cb5ddb6876f5358406b"
COMPLETION_RECEIPT_SHA256 = "c25d3db3f6d20aef54092d4fda7663370ec855e8841df691b7ef1bf6d9db2c24"
POST_RECEIPT_MATRIX_SHA256 = "ec6aaaeb917abb0bc1f8c1c54e2c721b175e841b603094eb6e687751bb6b79df"

REQUIRED_OPERATIONS = (
    "validate_pass206_enforcement",
    "validate_pass206_core_freeze",
    "validate_pass206_repair_lineage",
    "validate_pass206_development_completion",
    "validate_pass207_successor_binding",
)


def _load(path: Path) -> Dict[str, Any]:
    value = json.loads((ROOT / path).read_text("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("PASS206_OBJECT_REQUIRED:" + str(path))
    return value


def _artifact_hash(value: Dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("artifact_sha256", None)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _require_artifact(value: Dict[str, Any], expected: str, label: str) -> None:
    if value.get("artifact_sha256") != expected or _artifact_hash(value) != expected:
        raise RuntimeError("PASS206_ARTIFACT_DRIFT:" + label)


def pass206_membrane_source_evidence() -> Dict[str, Any]:
    contract = _load(PASS206_CONTRACT_PATH)
    freeze = _load(PASS206_FREEZE_PATH)
    lineage = _load(PASS206_REPAIR_LINEAGE_PATH)
    matrix = _load(PASS206_MATRIX_PATH)
    receipt = _load(PASS206_RECEIPT_PATH)
    completion = (ROOT / PASS206_COMPLETION_PATH).read_text("utf-8")
    enforcement = validate_pass206_enforcement(ROOT)
    successor = pass207_membrane_source_evidence()

    if contract.get("schema") != "HHS_PASS_206_CONTRACT_V1" or contract.get("pass") != 206:
        raise RuntimeError("PASS206_CONTRACT_IDENTITY_DRIFT")
    if contract.get("classification") != "CONTRACT_AUTHORIZED_FULL_IMPLEMENTATION_REQUIRED":
        raise RuntimeError("PASS206_CONTRACT_CLASSIFICATION_DRIFT")
    if contract.get("grounding_baseline") != GROUNDING_BASELINE:
        raise RuntimeError("PASS206_GROUNDING_BASELINE_DRIFT")
    authority = contract.get("authority") or {}
    if authority.get("canonical_mutation_authority") != "VM81_KERNEL" or authority.get("canonical_mutation_authority_count") != 1:
        raise RuntimeError("PASS206_VM81_AUTHORITY_DRIFT")
    if authority.get("canonical_hash72_commit_stream_count") != 1:
        raise RuntimeError("PASS206_HASH72_STREAM_DRIFT")

    _require_artifact(freeze, FREEZE_MANIFEST_SHA256, "CORE_FUNCTION_FREEZE_MANIFEST")
    _require_artifact(lineage, REPAIR_LINEAGE_SHA256, "CORE_SUCCESSOR_REPAIR_LINEAGE")
    _require_artifact(matrix, POST_RECEIPT_MATRIX_SHA256, "VALIDATION_MATRIX")
    _require_artifact(receipt, COMPLETION_RECEIPT_SHA256, "PASS_206_COMPLETION_RECEIPT")

    if freeze.get("grounding_baseline") != GROUNDING_BASELINE or freeze.get("entry_count") != 10:
        raise RuntimeError("PASS206_CORE_FREEZE_DRIFT")
    if lineage.get("approved_successor_count") != 1 or lineage.get("unchanged_core_count") != 9:
        raise RuntimeError("PASS206_REPAIR_LINEAGE_CARDINALITY_DRIFT")
    approved = lineage.get("approved_successors") or []
    if len(approved) != 1 or approved[0].get("repair_merge_commit") != APPROVED_REPAIR_MERGE:
        raise RuntimeError("PASS206_APPROVED_REPAIR_DRIFT")

    if matrix.get("stage") != "DEVELOPMENT_COMPLETE_CANONICAL_MAIN_VERIFICATION_PENDING":
        raise RuntimeError("PASS206_MATRIX_STAGE_DRIFT")
    if matrix.get("completion_claimed") is not False or matrix.get("canonical_main_verified") is not False:
        raise RuntimeError("PASS206_MATRIX_MAIN_BOUNDARY_DRIFT")
    if matrix.get("development_completion_receipt_emitted") is not True:
        raise RuntimeError("PASS206_MATRIX_RECEIPT_BOUNDARY_DRIFT")

    if receipt.get("status") != "DEVELOPMENT_IMPLEMENTATION_AND_FINAL_REPLAY_COMPLETE_CANONICAL_MAIN_VERIFICATION_PENDING":
        raise RuntimeError("PASS206_RECEIPT_STATUS_DRIFT")
    canonical_main = receipt.get("canonical_main") or {}
    if canonical_main.get("promotion_authorized") is not False or canonical_main.get("verified") is not False or canonical_main.get("completion_claimed") is not False:
        raise RuntimeError("PASS206_RECEIPT_MAIN_BOUNDARY_DRIFT")
    closure = receipt.get("development_closure") or {}
    for key in (
        "discover_index_freeze_complete",
        "enforcement_complete",
        "dependency_scoped_validation_complete",
        "final_cumulative_replay_complete",
        "completion_evidence_emitted",
        "ready_for_pass219_inherited_membrane",
    ):
        if closure.get(key) is not True:
            raise RuntimeError("PASS206_DEVELOPMENT_CLOSURE_DRIFT:" + key)
    decision = receipt.get("enforcement_decision") or {}
    if decision.get("status") != "ADMIT_PASS206_CUMULATIVE_ENFORCEMENT":
        raise RuntimeError("PASS206_RECEIPT_ENFORCEMENT_DRIFT")
    if decision.get("frozen_core_count") != 10 or decision.get("approved_successor_count") != 1:
        raise RuntimeError("PASS206_RECEIPT_CORE_COUNT_DRIFT")
    if decision.get("canonical_mutation_authority") != "VM81_KERNEL" or decision.get("canonical_mutation_authority_count") != 1:
        raise RuntimeError("PASS206_RECEIPT_VM81_DRIFT")
    if decision.get("canonical_hash72_commit_stream_count") != 1:
        raise RuntimeError("PASS206_RECEIPT_HASH72_DRIFT")
    for key in ("pass206_new_mutation_authority", "pass206_new_persistence_authority", "pass206_new_hash72_clock"):
        if decision.get(key) is not False:
            raise RuntimeError("PASS206_RECEIPT_AUTHORITY_ESCALATION:" + key)

    if not enforcement.get("ok") or enforcement.get("status") != "ADMIT_PASS206_CUMULATIVE_ENFORCEMENT":
        raise RuntimeError("PASS206_LIVE_ENFORCEMENT_REPLAY_FAILED")
    if enforcement.get("pass206_changed_frozen_core_paths") != []:
        raise RuntimeError("PASS206_LIVE_CORE_DRIFT")

    successor_contract = successor.get("contract") or {}
    if successor_contract.get("pass") != 207 or successor_contract.get("parent") != "Complete cumulative HHS runtime through Pass 206":
        raise RuntimeError("PASS206_PASS207_SUCCESSOR_DRIFT")
    successor_core = successor_contract.get("core_preservation") or {}
    if successor_core.get("modifies_pass206_frozen_core") is not False:
        raise RuntimeError("PASS206_PASS207_CORE_DRIFT")

    if "CANONICAL MAIN VERIFICATION PENDING" not in completion:
        raise RuntimeError("PASS206_COMPLETION_DOCUMENT_MAIN_BOUNDARY_DRIFT")
    if "completion_claimed = false" not in completion:
        raise RuntimeError("PASS206_COMPLETION_DOCUMENT_CLAIM_DRIFT")

    return {
        "contract": contract,
        "freeze_manifest": freeze,
        "repair_lineage": lineage,
        "validation_matrix": matrix,
        "completion_receipt": receipt,
        "live_enforcement": enforcement,
        "successor_pass207": successor,
        "grounding_baseline": GROUNDING_BASELINE,
        "sealed_predecessor": SEALED_PREDECESSOR,
        "freeze_checkpoint": FREEZE_CHECKPOINT,
        "development_completion_head": DEVELOPMENT_COMPLETION_HEAD,
        "approved_repair_merge": APPROVED_REPAIR_MERGE,
        "freeze_manifest_sha256": FREEZE_MANIFEST_SHA256,
        "repair_lineage_sha256": REPAIR_LINEAGE_SHA256,
        "pre_receipt_matrix_sha256": PRE_RECEIPT_MATRIX_SHA256,
        "completion_receipt_sha256": COMPLETION_RECEIPT_SHA256,
        "post_receipt_matrix_sha256": POST_RECEIPT_MATRIX_SHA256,
    }


def validate_pass206_core_freeze() -> Dict[str, Any]:
    source = pass206_membrane_source_evidence()
    return {"ok": True, "frozen_core_count": source["freeze_manifest"]["entry_count"]}


def validate_pass206_repair_lineage() -> Dict[str, Any]:
    source = pass206_membrane_source_evidence()
    return {"ok": True, "approved_successor_count": source["repair_lineage"]["approved_successor_count"]}


def validate_pass206_development_completion() -> Dict[str, Any]:
    source = pass206_membrane_source_evidence()
    return {"ok": True, "canonical_main_verified": source["completion_receipt"]["canonical_main"]["verified"]}


def validate_pass207_successor_binding() -> Dict[str, Any]:
    source = pass206_membrane_source_evidence()
    return {"ok": True, "successor_pass": source["successor_pass207"]["contract"]["pass"]}


def pass206_surface_declaration() -> Dict[str, Any]:
    pass206_membrane_source_evidence()
    return {
        "surface_id": PASS206_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass206_cumulative_enforcement_v1",
        "symbol": "validate_pass206_enforcement",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS_PASS_206_CONTRACT_V1", "HHS_PASS_206_CUMULATIVE_ENFORCEMENT_DECISION_V1"],
        "witness_schemas": ["HHS_PASS206_CUMULATIVE_ENFORCEMENT_WITNESS_V1", "HHS_PASS_206_DEVELOPMENT_COMPLETION_RECEIPT_V1"],
        "validators": [PASS206_BIND_SYMBOL, "validate_pass206_enforcement"],
        "guards": [
            "pass206_exact_baseline_freeze",
            "pass206_approved_repair_lineage",
            "pass206_single_vm81_authority",
            "pass206_single_hash72_stream",
            "pass206_no_new_mutation_persistence_or_hash72_clock",
            "pass206_canonical_main_pending",
            "pass206_pass207_successor_preserved",
        ],
        "rejection_codes": [
            "REJECT_PASS206_CORE_DRIFT",
            "REJECT_PASS206_UNAPPROVED_REPAIR",
            "REJECT_PASS206_AUTHORITY_ESCALATION",
            "REJECT_PASS206_CANONICAL_MAIN_OVERCLAIM",
            "REJECT_PASS206_PASS207_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_EVIDENCE_IDENTITY_ONLY",
        "boundedness_policy": "PASS_206_FREEZE_ENFORCEMENT_DEVELOPMENT_COMPLETION_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass206_membrane_manifest() -> Dict[str, Any]:
    source = pass206_membrane_source_evidence()
    receipt = source["completion_receipt"]
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS206_NUMBER,
        "classification": PASS206_CLASSIFICATION,
        "pass219_c_abi_surface": PASS206_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass206CumulativeEnforcement",
        "frozen_core_count": 10,
        "approved_successor_count": 1,
        "canonical_mutation_authority": "VM81_KERNEL",
        "canonical_mutation_authority_count": 1,
        "canonical_hash72_commit_stream_count": 1,
        "enforcement_admitted": True,
        "development_implementation_complete": True,
        "development_final_replay_complete": True,
        "development_completion_receipt_emitted": True,
        "canonical_main_verified": False,
        "canonical_main_promotion_authorized": False,
        "canonical_completion_claimed": False,
        "pass207_successor_bound": True,
        "pass219_new_canonical_mutation_authority": False,
        "pass219_new_persistence_authority": False,
        "pass219_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "completion_receipt_sha256": receipt["artifact_sha256"],
        "next_pass_to_census": 205,
    }


def preflight_pass206_membrane() -> Dict[str, Any]:
    declaration = pass206_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    ok = all(row.get("ok") is True for row in rows)
    return {
        "schema": "HHS_PASS219_I118_PASS206_MEMBRANE_PREFLIGHT_V1",
        "ok": ok,
        "surface_id": PASS206_SURFACE_ID,
        "operations": rows,
        "manifest": pass206_membrane_manifest(),
    }


if __name__ == "__main__":
    print(json.dumps(preflight_pass206_membrane(), indent=2, sort_keys=True))
