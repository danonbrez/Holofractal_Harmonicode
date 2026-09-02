from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from hhs_runtime.pass163.vmrc import VMRCRuntime
from hhs_runtime.pass177.runtime import Pass177WorkflowAuthority

ROOT = Path(__file__).resolve().parents[1]
VALIDATED_AUTHORITY_HEAD = "15fa5a458c6755eab4d1af4b405b83b3467d45d9"
AUTHORITY_RECEIPT_BLOB = "357365c6c55df87b1c199e64fb53d889c7315249"
PRE_CUMULATIVE_GREEN_RUN = 33632013615
HISTORICAL_MERGE = "2aeb16e736829ec9fe64b2a0d9779bbfa147f4ec"
REMAINING_TERMINAL_CATEGORIES = (
    "COMPLETE_REQUIRED_APPLICATION_TEMPLATE_FAMILIES",
    "COMPLETE_REQUIRED_CREATIVE_CONTENT_FAMILIES",
    "VERSIONED_ENVIRONMENT_ADAPTER_REGISTRY",
    "VERIFIED_TOOLCHAIN_PROVISIONING",
    "REAL_MULTI_TARGET_COMPILATION_TRANSFORMATION",
    "FORMAT_APPROPRIATE_MEDIA_OUTPUT_VALIDATION",
    "PROJECT_VISIBLE_DURABLE_CHECKPOINT_STORE",
    "ASSISTANT_TYPED_MUTATION_PARITY",
    "EXPLICIT_DEPLOYMENT_EXECUTION_AND_REVISION_EVIDENCE",
    "NOVICE_EXPERT_BROWSER_USABILITY",
    "PERFORMANCE_SCALE_AND_RESOURCE_EVIDENCE",
    "AUTHORITATIVE_MAIN_AND_DEPLOYED_REVISION_CLOSURE",
)


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _project() -> dict[str, Any]:
    return {
        "schema": "hhs.pass177.generated-project/v1",
        "manifest": {
            "schema": "hhs.pass177.project/v1",
            "id": "i149-project",
            "template": {"id": "offline-pwa", "version": "1.0.0"},
            "workflow": {"id": "pwa.application.source-zip", "version": "1.0.0"},
            "identity": {
                "algorithm": "HHS-P150-HASH216-CONSTRAINT-GENOME-V1",
                "root": "a" * 64,
                "payloadSha256": "b" * 64,
                "previousRoot": "0" * 64,
                "sequence": 0,
                "vm81EchoRequired": True,
                "browserProjectionOnly": True,
                "canonicalAdmissionRequired": True,
                "canonicalMutationAuthority": False,
            },
        },
        "identity": {
            "root": "a" * 64,
            "browserProjectionOnly": True,
            "canonicalAdmissionRequired": True,
            "canonicalMutationAuthority": False,
        },
        "files": [{"path": "index.html", "mediaType": "text/html", "content": "<!doctype html>\n"}],
    }


def _run() -> dict[str, Any]:
    return {
        "schema": "hhs.pass177.workflow-run/v1",
        "runId": "i149-run",
        "workflowId": "pwa.application.source-zip",
        "workflowVersion": "1.0.0",
        "status": "succeeded",
        "context": {"projectId": "i149-project"},
        "stageStates": {},
        "checkpoint": 6,
        "checkpointAuthority": "MEMORY_CANDIDATE_ONLY",
        "canonicalAdmissionRequired": True,
        "canonicalMutationAuthority": False,
    }


def validate_pass177_frozen_authority() -> dict[str, Any]:
    _git("merge-base", "--is-ancestor", HISTORICAL_MERGE, "HEAD")
    _git("merge-base", "--is-ancestor", VALIDATED_AUTHORITY_HEAD, "HEAD")
    path = ROOT / "evidence/pass177/i149/PASS_219_I149_PASS177_WORKFLOW_AUTHORITY_RECEIPT_INDEX.json"
    blob = _git("hash-object", str(path.relative_to(ROOT)))
    if blob != AUTHORITY_RECEIPT_BLOB:
        raise RuntimeError(f"PASS177_AUTHORITY_RECEIPT_BLOB_DRIFT:{blob}")
    receipt = json.loads(path.read_text("utf-8"))
    validated = receipt["validated_authority"]
    if validated["workflow_run_id"] != PRE_CUMULATIVE_GREEN_RUN or validated["conclusion"] != "success":
        raise RuntimeError("PASS177_PRE_CUMULATIVE_RECEIPT_NOT_GREEN")
    return {
        "ok": True,
        "historical_merge": HISTORICAL_MERGE,
        "validated_authority_head": VALIDATED_AUTHORITY_HEAD,
        "authority_receipt_blob": AUTHORITY_RECEIPT_BLOB,
        "pre_cumulative_green_run": PRE_CUMULATIVE_GREEN_RUN,
    }


def validate_pass177_runtime_authority() -> dict[str, Any]:
    vm81 = VMRCRuntime()
    authority = Pass177WorkflowAuthority(vm81=vm81)
    before = vm81.epoch
    project = authority.admit_project(_project())
    if vm81.epoch != before + 1:
        raise RuntimeError("PASS177_PROJECT_VM81_ADMISSION_DRIFT")
    checkpoint = authority.admit_workflow_checkpoint(project_id="i149-project", run=_run())
    if vm81.epoch != before + 2:
        raise RuntimeError("PASS177_CHECKPOINT_VM81_ADMISSION_DRIFT")
    if project["browser_identity_authoritative"] is not False:
        raise RuntimeError("PASS177_BROWSER_IDENTITY_AUTHORITY_DRIFT")
    if checkpoint["memory_checkpoint_authoritative"] is not False:
        raise RuntimeError("PASS177_MEMORY_CHECKPOINT_AUTHORITY_DRIFT")
    if len(project["post_vm81_hash72_evidence"]) != 72 or len(project["project_hash216"]) != 216:
        raise RuntimeError("PASS177_PROJECT_EVIDENCE_DRIFT")
    if len(checkpoint["post_vm81_hash72_evidence"]) != 72 or len(checkpoint["checkpoint_hash216"]) != 216:
        raise RuntimeError("PASS177_CHECKPOINT_EVIDENCE_DRIFT")
    return {
        "ok": True,
        "vm81_project_admission": True,
        "vm81_checkpoint_admission": True,
        "browser_identity_authoritative": False,
        "memory_checkpoint_authoritative": False,
    }


def validate_pass177_historical_truth() -> dict[str, Any]:
    source = (ROOT / "applications/holofractal_harmonizer/src/pass177/workflow-engine.mjs").read_text("utf-8")
    project = (ROOT / "applications/holofractal_harmonizer/src/pass177/project-factory.mjs").read_text("utf-8")
    required = (
        "status: 'source-validated'",
        "mode: 'source-preserving'",
        "independentOfCompilation: true",
        "checkpointAuthority: 'MEMORY_CANDIDATE_ONLY'",
    )
    for token in required:
        if token not in source:
            raise RuntimeError(f"PASS177_HISTORICAL_TRUTH_DRIFT:{token}")
    for token in ("browserProjectionOnly: true", "canonicalAdmissionRequired: true", "canonicalMutationAuthority: false"):
        if token not in project:
            raise RuntimeError(f"PASS177_BROWSER_AUTHORITY_MARKER_DRIFT:{token}")
    return {"ok": True, "historical_stage_truth_preserved": True}


def validate_pass177_global_census() -> dict[str, Any]:
    contract = json.loads((ROOT / "contracts/pass219/PASS_219_GLOBAL_CANONICAL_DEFAULTS_1_0.json").read_text("utf-8"))
    census = contract["current_cumulative_binding_census"]
    if census["wired_floor_pass"] != 177 or census["binding_count"] != 44:
        raise RuntimeError(f"PASS177_GLOBAL_CENSUS_DRIFT:{census}")
    if census["ordered_bindings"][-5:] != ["181", "180", "179", "178", "177"]:
        raise RuntimeError("PASS177_GLOBAL_CENSUS_TAIL_DRIFT")
    debt = next((x for x in contract["known_repair_forward_debt"] if x["pass"] == 177), None)
    if debt is None or debt["classification"] != "WIRED_NONTERMINAL_REPAIR_FORWARD":
        raise RuntimeError("PASS177_REPAIR_FORWARD_DEBT_MISSING")
    if debt["terminal_completion_claimed"] is not False or debt["historical_stage_truth_preserved"] is not True:
        raise RuntimeError("PASS177_REPAIR_FORWARD_DEBT_DRIFT")
    if tuple(debt["remaining_terminal_categories"]) != REMAINING_TERMINAL_CATEGORIES:
        raise RuntimeError("PASS177_TERMINAL_CATEGORY_DRIFT")
    return {
        "ok": True,
        "wired_floor": 177,
        "binding_count": 44,
        "terminal_completion_claimed": False,
        "repair_forward_required": True,
        "remaining_terminal_category_count": 12,
    }


def validate_pass177_exact_binding_surface() -> dict[str, Any]:
    h = (ROOT / "hhs_runtime/include/hhs_pass219_inherited_pass177_1_49.h").read_text("utf-8")
    hpp = (ROOT / "hhs_runtime/include/hhs_pass219_inherited_pass177_1_49.hpp").read_text("utf-8")
    c = (ROOT / "hhs_runtime/c/hhs_pass219_inherited_pass177_1_49.inc").read_text("utf-8")
    ah = (ROOT / "hhs_runtime/include/hhs_runtime_exact_abi.h").read_text("utf-8")
    ac = (ROOT / "hhs_runtime/c/hhs_runtime_exact_abi.c").read_text("utf-8")
    for token in ("hhs_exact_pass219_bind_pass177_creation_workflows", "terminal_pass177_completion", "historical_stage_truth_preserved"):
        if token not in h + c:
            raise RuntimeError(f"PASS177_BINDING_TOKEN_MISSING:{token}")
    if "terminal_pass177_completion_claimed() noexcept { return false; }" not in hpp:
        raise RuntimeError("PASS177_CPP_TERMINAL_DRIFT")
    if "repair_forward_required() noexcept { return true; }" not in hpp:
        raise RuntimeError("PASS177_CPP_REPAIR_FORWARD_DRIFT")
    if "hhs_pass219_inherited_pass177_1_49.h" not in ah or "hhs_pass219_inherited_pass177_1_49.inc" not in ac:
        raise RuntimeError("PASS177_AGGREGATE_EXPOSURE_MISSING")
    return {
        "ok": True,
        "terminal_completion_claimed": False,
        "repair_forward_required": True,
        "historical_stage_truth_preserved": True,
    }


def execute_pass177_membrane_preflight() -> dict[str, Any]:
    return {
        "ok": True,
        "classification": "HHS_PASS177_I149_CUMULATIVE_NONTERMINAL_PREFLIGHT",
        "frozen": validate_pass177_frozen_authority(),
        "runtime": validate_pass177_runtime_authority(),
        "historical_truth": validate_pass177_historical_truth(),
        "census": validate_pass177_global_census(),
        "exact_binding": validate_pass177_exact_binding_surface(),
        "manifest": {
            "schema": "HHS_PASS219_I149_PASS177_CUMULATIVE_MEMBRANE_V1",
            "aggregate_order_tail": [181, 180, 179, 178, 177],
            "terminal_pass177_completion": False,
            "repair_forward_required": True,
            "remaining_terminal_categories": list(REMAINING_TERMINAL_CATEGORIES),
            "authority": {
                "singleton_vm81_inherited": True,
                "independent_vm81_authority": False,
                "independent_hash72_commit_authority": False,
                "hash216_mutation_authority": False,
                "browser_identity_authoritative": False,
                "memory_checkpoint_authoritative": False,
            },
        },
    }
