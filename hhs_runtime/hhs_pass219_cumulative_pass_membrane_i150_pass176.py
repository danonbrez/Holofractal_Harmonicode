from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALIDATED_TERMINAL_HEAD = "c2cb9ca92e21721581d896fdd53f226d6d055f57"
TERMINAL_RECEIPT_INDEX_BLOB = "963b50533389114e2b270aff52184396b9e8178e"
TERMINAL_WORKFLOW_RUN = 33766747861
TERMINAL_RECEIPT_SHA256 = "f43d26f4932074d8de5e001a4de4dee2435ce216c4112c4612547f63ef771173"
TERMINAL_ARTIFACT_SHA256 = "b20edde645e16c13eb7629778e3bce3a5f4293684abb605c722a8254cdc86282"


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def validate_pass176_frozen_terminal_evidence() -> dict[str, Any]:
    _git("merge-base", "--is-ancestor", VALIDATED_TERMINAL_HEAD, "HEAD")
    path = ROOT / "evidence/pass176/i150/PASS_219_I150_PASS176_TERMINAL_RECEIPT_INDEX.json"
    blob = _git("hash-object", str(path.relative_to(ROOT)))
    if blob != TERMINAL_RECEIPT_INDEX_BLOB:
        raise RuntimeError(f"PASS176_TERMINAL_RECEIPT_INDEX_BLOB_DRIFT:{blob}")
    receipt = json.loads(path.read_text("utf-8"))
    exact = receipt["exact_validation"]
    terminal = receipt["terminal_receipt"]
    artifact = receipt["artifact"]
    if receipt["terminal_pass176_completion"] is not True:
        raise RuntimeError("PASS176_TERMINAL_COMPLETION_NOT_FROZEN")
    if exact["workflow_run_id"] != TERMINAL_WORKFLOW_RUN or exact["conclusion"] != "success" or exact["all_workflow_steps_green"] is not True:
        raise RuntimeError("PASS176_EXACT_TERMINAL_RUN_NOT_GREEN")
    if terminal["receipt_sha256"] != TERMINAL_RECEIPT_SHA256 or terminal["terminal_pass176_completion"] is not True or terminal["all_checks_green"] is not True:
        raise RuntimeError("PASS176_TERMINAL_RECEIPT_DRIFT")
    if artifact["sha256"] != TERMINAL_ARTIFACT_SHA256:
        raise RuntimeError("PASS176_TERMINAL_ARTIFACT_DRIFT")
    authority = receipt["authority"]
    if authority["frontend_is_canonical_authority"] is not False:
        raise RuntimeError("PASS176_FRONTEND_AUTHORITY_WIDENED")
    if authority["singleton_vm81_admission_preserved"] is not True or authority["hash72_commit_streams"] != 1:
        raise RuntimeError("PASS176_CANONICAL_AUTHORITY_DRIFT")
    if authority["independent_vm81_authority"] or authority["independent_hash72_commit_authority"] or authority["hash216_mutation_authority"]:
        raise RuntimeError("PASS176_INDEPENDENT_AUTHORITY_CREATED")
    return {
        "ok": True,
        "validated_terminal_head": VALIDATED_TERMINAL_HEAD,
        "terminal_workflow_run": TERMINAL_WORKFLOW_RUN,
        "terminal_receipt_sha256": TERMINAL_RECEIPT_SHA256,
        "terminal_artifact_sha256": TERMINAL_ARTIFACT_SHA256,
    }


def validate_pass176_preservation_surface() -> dict[str, Any]:
    server = (ROOT / "hhs_backend/runtime_os_application_server_full.py").read_text("utf-8")
    production = (ROOT / "hhs_backend/public_ide_bootstrap.py").read_text("utf-8")
    visual = (ROOT / "applications/holofractal_harmonizer/src/visual-ide.mjs").read_text("utf-8")
    for token in (
        'PASS176_FROZEN_IDE_PATH = "/pass176-ide"',
        'PASS176_FROZEN_IDE_PATH + "/"',
        "app.mount(",
    ):
        if token not in server:
            raise RuntimeError(f"PASS176_ADDITIVE_ROUTE_DRIFT:{token}")
    if "HHS Visual Runtime OS Workspace" not in server + production:
        raise RuntimeError("PASS176_RUNTIME_OS_PUBLIC_ROOT_DRIFT")
    for token in ("window.HHSVisualIDEBoot", "window.HHSVisualIDE", "INTERACTIVE"):
        if token not in visual:
            raise RuntimeError(f"PASS176_VISUAL_IDE_SURFACE_DRIFT:{token}")
    return {"ok": True, "runtime_os_public_root": True, "pass176_additive_route": "/pass176-ide/"}


def validate_pass176_global_census() -> dict[str, Any]:
    contract = json.loads((ROOT / "contracts/pass219/PASS_219_GLOBAL_CANONICAL_DEFAULTS_1_0.json").read_text("utf-8"))
    census = contract["current_cumulative_binding_census"]
    if census["wired_floor_pass"] != 176 or census["binding_count"] != 45:
        raise RuntimeError(f"PASS176_GLOBAL_CENSUS_DRIFT:{census}")
    if census["ordered_bindings"][-5:] != ["180", "179", "178", "177", "176"]:
        raise RuntimeError("PASS176_GLOBAL_CENSUS_TAIL_DRIFT")
    i150 = census.get("i150_reconciliation")
    if not i150 or i150.get("pass176") != "FROZEN_IDE_CUMULATIVELY_WIRED_TERMINAL":
        raise RuntimeError("PASS176_I150_GLOBAL_RECONCILIATION_MISSING")
    return {"ok": True, "wired_floor": 176, "binding_count": 45, "terminal_completion_claimed": True}


def validate_pass176_exact_binding_surface() -> dict[str, Any]:
    h = (ROOT / "hhs_runtime/include/hhs_pass219_inherited_pass176_1_50.h").read_text("utf-8")
    hpp = (ROOT / "hhs_runtime/include/hhs_pass219_inherited_pass176_1_50.hpp").read_text("utf-8")
    c = (ROOT / "hhs_runtime/c/hhs_pass219_inherited_pass176_1_50.inc").read_text("utf-8")
    ah = (ROOT / "hhs_runtime/include/hhs_runtime_exact_abi.h").read_text("utf-8")
    ac = (ROOT / "hhs_runtime/c/hhs_runtime_exact_abi.c").read_text("utf-8")
    for token in ("hhs_exact_pass219_bind_pass176", "terminal_pass176_completion", TERMINAL_RECEIPT_SHA256, TERMINAL_ARTIFACT_SHA256):
        if token not in h + c:
            raise RuntimeError(f"PASS176_BINDING_TOKEN_MISSING:{token}")
    if "terminal_pass176_completion_claimed() noexcept { return true; }" not in hpp:
        raise RuntimeError("PASS176_CPP_TERMINAL_DRIFT")
    if "independent_vm81_authority() noexcept { return false; }" not in hpp:
        raise RuntimeError("PASS176_CPP_VM81_AUTHORITY_DRIFT")
    if "independent_hash72_commit_authority() noexcept { return false; }" not in hpp:
        raise RuntimeError("PASS176_CPP_HASH72_AUTHORITY_DRIFT")
    if "hash216_mutation_authority() noexcept { return false; }" not in hpp:
        raise RuntimeError("PASS176_CPP_HASH216_AUTHORITY_DRIFT")
    if "hhs_pass219_inherited_pass176_1_50.h" not in ah or "hhs_pass219_inherited_pass176_1_50.inc" not in ac:
        raise RuntimeError("PASS176_AGGREGATE_EXPOSURE_MISSING")
    return {"ok": True, "terminal_completion_claimed": True, "independent_authority_created": False}


def execute_pass176_membrane_preflight() -> dict[str, Any]:
    return {
        "ok": True,
        "classification": "HHS_PASS176_I150_CUMULATIVE_TERMINAL_PREFLIGHT",
        "frozen_terminal": validate_pass176_frozen_terminal_evidence(),
        "preservation": validate_pass176_preservation_surface(),
        "census": validate_pass176_global_census(),
        "exact_binding": validate_pass176_exact_binding_surface(),
        "manifest": {
            "schema": "HHS_PASS219_I150_PASS176_CUMULATIVE_MEMBRANE_V1",
            "aggregate_order_tail": [180, 179, 178, 177, 176],
            "terminal_pass176_completion": True,
            "authority": {
                "frontend_canonical_authority": False,
                "singleton_vm81_inherited": True,
                "hash72_commit_streams": 1,
                "independent_vm81_authority": False,
                "independent_hash72_commit_authority": False,
                "hash216_mutation_authority": False,
            },
        },
    }
