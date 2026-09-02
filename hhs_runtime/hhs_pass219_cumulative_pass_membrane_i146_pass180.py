from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from hhs_backend.runtime.hhs_application_factory_v1 import (
    ApplicationFactory,
    LIFECYCLE_STAGES,
    MODULE_LIBRARY,
    WORKFLOW_LIBRARY,
)
from hhs_runtime.pass163.vmrc import VMRCRuntime

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ID = "HHS-P180-IAF-VM81-H72-H216"
HISTORICAL_GREEN_HEAD = "9d0e8ef4a60d450f69ef5bf4dab3ad1c18b30dba"
HISTORICAL_GREEN_RUN = 30633469008
FROZEN_I145_CHECKPOINT = "4762e1b5428f09a957905cc59669b7c9aeb36f06"
I145_RECEIPT_BLOB = "331ca8095e5828dc8de0846f6c96c0336e260293"


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _text(path: str) -> str:
    return (ROOT / path).read_text("utf-8")


def validate_pass180_historical_lineage() -> dict[str, Any]:
    _git("merge-base", "--is-ancestor", HISTORICAL_GREEN_HEAD, "HEAD")
    _git("merge-base", "--is-ancestor", FROZEN_I145_CHECKPOINT, "HEAD")
    contract = _text("docs/pass180/HHS_PASS_180_INTEGRATED_APPLICATION_FACTORY.md")
    workflow = _text(".github/workflows/pass180-application-factory.yml")
    if CONTRACT_ID not in contract:
        raise RuntimeError("PASS180_CONTRACT_ID_DRIFT")
    for token in (
        "hhs_backend/runtime/hhs_application_factory_v1.py",
        "hhs_backend/api/application_factory_routes.py",
        "tests/test_pass180_application_factory.py",
    ):
        if token not in workflow:
            raise RuntimeError(f"PASS180_HISTORICAL_WORKFLOW_SURFACE_MISSING:{token}")
    return {
        "ok": True,
        "historical_green_head": HISTORICAL_GREEN_HEAD,
        "historical_green_run": HISTORICAL_GREEN_RUN,
        "frozen_i145_checkpoint": FROZEN_I145_CHECKPOINT,
        "i145_validation_receipt_blob": I145_RECEIPT_BLOB,
    }


def validate_pass180_runtime_reachability() -> dict[str, Any]:
    required = {
        "runtime": "hhs_backend/runtime/hhs_application_factory_v1.py",
        "api": "hhs_backend/api/application_factory_routes.py",
        "visual_server": "hhs_backend/visual_server.py",
        "contract": "docs/pass180/HHS_PASS_180_INTEGRATED_APPLICATION_FACTORY.md",
        "tests": "tests/test_pass180_application_factory.py",
    }
    missing = [name for name, path in required.items() if not (ROOT / path).is_file()]
    if missing:
        raise RuntimeError(f"PASS180_RUNTIME_REACHABILITY_MISSING:{missing}")
    if len(MODULE_LIBRARY) != 14 or len(WORKFLOW_LIBRARY) != 7:
        raise RuntimeError("PASS180_LIBRARY_CARDINALITY_DRIFT")
    routes = _text(required["api"])
    for token in (
        "/projects/{project_id}/lifecycle",
        "/projects/{project_id}/source.zip",
        "/projects/{project_id}/replay",
    ):
        if token not in routes:
            raise RuntimeError(f"PASS180_PUBLIC_ROUTE_MISSING:{token}")
    return {
        "ok": True,
        "surface_count": len(required),
        "module_count": len(MODULE_LIBRARY),
        "workflow_count": len(WORKFLOW_LIBRARY),
    }


def validate_pass180_vm81_authority_repair() -> dict[str, Any]:
    source = _text("hhs_backend/runtime/hhs_application_factory_v1.py")
    for token in (
        "def _vm81_commit_transition",
        'capability_scope="P180_APPLICATION_FACTORY_CANONICAL_MUTATION"',
        '"HHS_PASS180_APPLICATION_FACTORY_VM81_ADMISSION_VERIFIED"',
        '"P180_VM81_ADMISSION_AUTHORITY_REQUIRED"',
        '"vm81_receipt_hash72": admission["receipt_hash72"]',
    ):
        if token not in source:
            raise RuntimeError(f"PASS180_VM81_REPAIR_SURFACE_MISSING:{token}")

    missing = ApplicationFactory()
    rejected = missing.create_project(name="No VM81", workflow_id="web_application")
    if rejected.get("ok") is not False or rejected.get("status") != "REJECT_APPLICATION_VM81_AUTHORITY":
        raise RuntimeError("PASS180_MUTATION_WITHOUT_VM81_ACCEPTED")
    if missing.projects:
        raise RuntimeError("PASS180_REJECTED_MUTATION_CHANGED_PROJECT_STATE")

    vm81 = VMRCRuntime()
    factory = ApplicationFactory(vm81=vm81)
    start = vm81.epoch
    created = factory.create_project(name="I146", workflow_id="web_application")
    if created.get("ok") is not True or vm81.epoch != start + 1:
        raise RuntimeError("PASS180_CREATE_VM81_ADMISSION_FAILED")
    project_id = created["project"]["project_id"]
    changed = factory.upsert_file(project_id, "src/app.js", "const i146=true;\n")
    if changed.get("ok") is not True or vm81.epoch != start + 2:
        raise RuntimeError("PASS180_UPSERT_VM81_ADMISSION_FAILED")
    lifecycle = factory.run_lifecycle(project_id, ["src/app.js"])
    if lifecycle.get("ok") is not True or vm81.epoch != start + 3:
        raise RuntimeError("PASS180_LIFECYCLE_VM81_ADMISSION_FAILED")
    if [x["stage"] for x in lifecycle["job"]["checkpoints"]] != list(LIFECYCLE_STAGES):
        raise RuntimeError("PASS180_LIFECYCLE_CHECKPOINT_DRIFT")
    for result in (
        created["project"]["vm81_admission"],
        changed["project"]["vm81_admission"],
        lifecycle["job"]["result"]["vm81_admission"],
    ):
        if result.get("classification") != "HHS_PASS180_APPLICATION_FACTORY_VM81_ADMISSION_VERIFIED":
            raise RuntimeError("PASS180_VM81_ADMISSION_CLASSIFICATION_DRIFT")
        if result.get("singleton_authority") is not True:
            raise RuntimeError("PASS180_SINGLETON_VM81_NOT_PRESERVED")
        if result.get("independent_vm81_authority") is not False:
            raise RuntimeError("PASS180_PEER_VM81_AUTHORITY_CREATED")
        if result.get("validation_mutation_authority") is not False:
            raise RuntimeError("PASS180_VALIDATION_MUTATION_AUTHORITY_DRIFT")
        if not result.get("receipt_hash72") or not result.get("operation_hash216"):
            raise RuntimeError("PASS180_VM81_RECEIPT_INCOMPLETE")
    return {
        "ok": True,
        "create_upsert_lifecycle_vm81_admitted": True,
        "hash72_after_vm81": True,
        "missing_vm81_fails_closed": True,
        "independent_vm81_authority": False,
    }


def validate_pass180_terminal_contract() -> dict[str, Any]:
    vm81 = VMRCRuntime()
    factory = ApplicationFactory(vm81=vm81)
    project = factory.create_project(
        name="Terminal",
        workflow_id="document_studio",
    )["project"]
    plan = factory.plan_changes(project["project_id"], ["documents/main.md"])
    lifecycle = factory.run_lifecycle(project["project_id"], ["documents/main.md"])
    first = factory.export_source_zip(project["project_id"])
    second = factory.export_source_zip(project["project_id"])
    replay = factory.replay_project(project["project_id"])
    checks = {
        "module_catalog_callable": len(MODULE_LIBRARY) == 14,
        "workflow_catalog_callable": len(WORKFLOW_LIBRARY) == 7,
        "dependency_closure": "runtime.vm81" in project["modules"],
        "incremental_planning": plan.get("ok") is True,
        "candidate_groups": bool(plan["plan"]["parallel_candidate_groups"]),
        "eight_checkpoints": len(lifecycle["job"]["checkpoints"]) == 8,
        "lifecycle_terminal": lifecycle["job"]["state"] == "SUCCEEDED",
        "source_zip_without_compile": first["manifest"]["compile_required"] is False,
        "deterministic_zip": first["zip_bytes"] == second["zip_bytes"],
        "deterministic_replay": replay.get("deterministic_replay") is True,
        "external_success_nonfabrication": lifecycle["job"]["result"]["test_plan"]["status"] == "PLANNED",
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError("PASS180_TERMINAL_CONTRACT_FAILED:" + ",".join(failed))
    return {
        "ok": True,
        "checks": checks,
        "terminal_pass180_completion": True,
        "remaining_terminal_obligation_count": 0,
    }


def validate_pass180_global_default_reachability() -> dict[str, Any]:
    contract = json.loads(_text("contracts/pass219/PASS_219_GLOBAL_CANONICAL_DEFAULTS_1_0.json"))
    census = contract["current_cumulative_binding_census"]
    if census["wired_floor_pass"] != 180 or census["binding_count"] != 41:
        raise RuntimeError(f"PASS180_GLOBAL_CENSUS_DRIFT:{census}")
    if census["ordered_bindings"][-5:] != ["184", "183", "182", "181", "180"]:
        raise RuntimeError("PASS180_GLOBAL_CENSUS_TAIL_DRIFT")
    if any(x.get("pass") == 180 for x in contract.get("known_repair_forward_debt", [])):
        raise RuntimeError("PASS180_TERMINAL_DEBT_SHOULD_BE_CLOSED")
    return {
        "ok": True,
        "wired_floor": 180,
        "binding_count": 41,
        "terminal_completion_claimed": True,
    }


def validate_pass180_no_new_authority() -> dict[str, Any]:
    hpp = _text("hhs_runtime/include/hhs_pass219_inherited_pass180_1_46.hpp")
    required = (
        "independent_vm81_authority() noexcept { return false; }",
        "independent_hash72_authority() noexcept { return false; }",
        "hash216_mutation_authority() noexcept { return false; }",
        "floating_point_canonical_authority() noexcept { return false; }",
        "hash72_follows_vm81_mutation() noexcept { return true; }",
        "external_success_may_be_fabricated() noexcept { return false; }",
        "terminal_pass180_completion_claimed() noexcept { return true; }",
    )
    for token in required:
        if token not in hpp:
            raise RuntimeError(f"PASS180_AUTHORITY_DECLARATION_DRIFT:{token}")
    return {
        "ok": True,
        "singleton_vm81_authority_remains_inherited": True,
        "independent_vm81_authority": False,
        "independent_hash72_authority": False,
        "hash216_mutation_authority": False,
        "floating_point_canonical_authority": False,
    }


def pass180_membrane_manifest() -> dict[str, Any]:
    return {
        "pass_number": 180,
        "iteration": 146,
        "contract_id": CONTRACT_ID,
        "classification": "WIRED_TERMINAL_PENDING_I146_EXECUTED_VALIDATION",
        "historical_green_head": HISTORICAL_GREEN_HEAD,
        "historical_green_run": HISTORICAL_GREEN_RUN,
        "frozen_predecessor": FROZEN_I145_CHECKPOINT,
        "aggregate_order_tail": [184, 183, 182, 181, 180],
        "terminal_completion_claimed": True,
        "repair_forward_required": False,
        "remaining_terminal_obligation_count": 0,
        "merge_status": "UNMERGED",
        "authoritative_main_verification": False,
        "deployment_status": "NOT_PERFORMED",
    }


def execute_pass180_membrane_preflight() -> dict[str, Any]:
    checks = {
        "historical_lineage": validate_pass180_historical_lineage(),
        "runtime_reachability": validate_pass180_runtime_reachability(),
        "vm81_authority_repair": validate_pass180_vm81_authority_repair(),
        "terminal_contract": validate_pass180_terminal_contract(),
        "global_default_reachability": validate_pass180_global_default_reachability(),
        "no_new_authority": validate_pass180_no_new_authority(),
    }
    return {
        "ok": all(item.get("ok") is True for item in checks.values()),
        "classification": "HHS_PASS180_I146_DEPENDENCY_SCOPED_PREFLIGHT_VERIFIED",
        "manifest": pass180_membrane_manifest(),
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(execute_pass180_membrane_preflight(), sort_keys=True, indent=2))
