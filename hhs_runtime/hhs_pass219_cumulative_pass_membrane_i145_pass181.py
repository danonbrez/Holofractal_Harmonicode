from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from hhs_backend.runtime.hhs_graphics_constraint_registry_v1 import (
    AUTHORITY,
    PROMOTION_STAGES,
    GraphicsConstraintRegistry,
    GraphicsConstraintRegistryError,
)
from hhs_runtime.pass163.vmrc import VMRCRuntime

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ID = "HHS-P181-NCSR-GHIR-VM81-H72-H216"
HISTORICAL_GREEN_HEAD = "3ae56827b27500c2c8187126d5825a901d4feb40"
HISTORICAL_GREEN_RUN = 30660886113
FROZEN_I144_CHECKPOINT = "132694cee0af4a43113ddc4c50f867c084a22bae"
REMAINING_TERMINAL_OBLIGATIONS = (
    "DETERMINISTIC_COLD_START_NATIVE_RECONSTRUCTION_REPLAY",
    "THREEJS_EDITOR_PREVIEW_ENHANCEMENT_NO_FINAL_FRAME_AUTHORITY",
    "FULL_90_SECOND_INVERSE_RENDER_AND_ONE_CLICK_EVIDENCE_EXPORT",
)


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _text(path: str) -> str:
    return (ROOT / path).read_text("utf-8")


def _candidate() -> dict[str, Any]:
    return {
        "schema": "HHS_P181_GRAPHICS_INVARIANT_CANDIDATE_V1",
        "contract": CONTRACT_ID,
        "authority": AUTHORITY,
        "predicate_id": "I145_VM81_PROMOTION_PROOF",
        "candidate_class": "HARD_INVARIANT",
        "proposition": "runtime constraint activation requires inherited VM81 admission",
        "domain": "GRAPHICS_RUNTIME",
        "promotion_track": "RUNTIME_CONSTRAINT",
        "support_count": 2,
        "distinct_job_count": 2,
        "supporting_record_hash216": ["i145-record-a", "i145-record-b"],
        "supporting_job_ids": ["i145-job-a", "i145-job-b"],
        "counterexample_record_hash216": [],
        "minimum_support": 2,
        "minimum_distinct_jobs": 2,
        "eligible_for_promotion": True,
        "validation_state": "CANDIDATE",
        "runtime_constraint_authority": False,
        "frozen": False,
        "evidence_root_hash216": "i145-evidence-root",
        "candidate_hash216": "i145-candidate-root",
        "receipt_hash72": "i145-candidate-receipt",
    }


def _evidence() -> dict[str, Any]:
    return {
        "stages": {stage: True for stage in PROMOTION_STAGES},
        "stage_evidence": {
            stage: [f"i145-{stage}-evidence", f"i145-{stage}-receipt"]
            for stage in PROMOTION_STAGES
        },
        "contradiction_scan_result": "PASSED",
        "calibration_profile": {"profile": "i145", "sample_count": 72, "distinct_jobs": 2},
        "validator_versions": {
            "native_renderer": "HHS_NATIVE_ABI_V1",
            "canonical_decoder": "HHS_P181_CANONICAL_MP4_DECODE_MANIFEST_V1",
            "residual_analyzer": "HHS_P181_NATIVE_RECONSTRUCTION_RESIDUAL_REPORT_V1",
        },
        "operator": "HHS_VM81_PROMOTION_AUTHORITY",
    }


def validate_pass181_historical_lineage() -> dict[str, Any]:
    _git("merge-base", "--is-ancestor", HISTORICAL_GREEN_HEAD, "HEAD")
    _git("merge-base", "--is-ancestor", FROZEN_I144_CHECKPOINT, "HEAD")
    contract = _text("docs/pass181/HHS_PASS_181_NATIVE_CINEMATIC_STORY_REEL_GRAPHICS_HYDRATION_RUNTIME.md")
    workflow = _text(".github/workflows/pass181-graphics-hydration.yml")
    if CONTRACT_ID not in contract:
        raise RuntimeError("PASS181_CONTRACT_ID_DRIFT")
    for token in (
        "tests/test_pass181_graphics_hydration_runtime.py",
        "tests/test_pass181_graphics_constraint_registry.py",
        "hhs_backend/runtime/hhs_graphics_constraint_registry_v1.py",
    ):
        if token not in workflow:
            raise RuntimeError(f"PASS181_HISTORICAL_WORKFLOW_SURFACE_MISSING:{token}")
    return {
        "ok": True,
        "historical_green_head": HISTORICAL_GREEN_HEAD,
        "historical_green_run": HISTORICAL_GREEN_RUN,
        "frozen_i144_checkpoint": FROZEN_I144_CHECKPOINT,
        "historical_runtime_reachable": True,
    }


def validate_pass181_vm81_authority_repair() -> dict[str, Any]:
    registry_text = _text("hhs_backend/runtime/hhs_graphics_constraint_registry_v1.py")
    instance_text = _text("hhs_backend/runtime/hhs_graphics_constraint_registry_instance_v1.py")
    vector_text = _text("hhs_backend/runtime/hhs_graphics_vector_hydration_v1.py")
    legacy_text = _text("hhs_backend/runtime/hhs_graphics_hydration_v1.py")
    for token in (
        "def _vm81_commit_transition",
        'capability_scope="P181_GRAPHICS_CONSTRAINT_PROMOTION"',
        '"HHS_PASS181_GRAPHICS_CONSTRAINT_VM81_ADMISSION_VERIFIED"',
        '"P181_VM81_ADMISSION_AUTHORITY_REQUIRED"',
    ):
        if token not in registry_text:
            raise RuntimeError(f"PASS181_VM81_REPAIR_SURFACE_MISSING:{token}")
    if "GRAPHICS_VECTOR_HYDRATION.vm81_authority" not in instance_text:
        raise RuntimeError("PASS181_CONSTRAINT_REGISTRY_MINTS_PEER_VM81")
    if "def vm81_authority" not in vector_text:
        raise RuntimeError("PASS181_VECTOR_VM81_EXPOSURE_MISSING")
    if "P181_LEGACY_DIRECT_CONSTRAINT_PROMOTION_DISABLED_USE_REGISTRY_FREEZE" not in legacy_text:
        raise RuntimeError("PASS181_LEGACY_DIRECT_PROMOTION_STILL_EXPOSED")

    with tempfile.TemporaryDirectory(prefix="pass181-i145-") as tmp:
        root = Path(tmp) / "registry"
        missing = GraphicsConstraintRegistry(root)
        try:
            missing.freeze_candidate(_candidate(), _evidence())
        except GraphicsConstraintRegistryError as error:
            if "P181_VM81_ADMISSION_AUTHORITY_REQUIRED" not in str(error):
                raise
        else:
            raise RuntimeError("PASS181_FREEZE_WITHOUT_VM81_ACCEPTED")

        vm81 = VMRCRuntime()
        before = vm81.epoch
        registry = GraphicsConstraintRegistry(root, vm81=vm81)
        result = registry.freeze_candidate(_candidate(), _evidence())
        admission = result["record"]["vm81_admission"]
        if vm81.epoch != before + 1:
            raise RuntimeError("PASS181_VM81_EPOCH_NOT_ADVANCED")
        if admission.get("classification") != "HHS_PASS181_GRAPHICS_CONSTRAINT_VM81_ADMISSION_VERIFIED":
            raise RuntimeError("PASS181_VM81_ADMISSION_CLASSIFICATION_DRIFT")
        if admission.get("singleton_authority") is not True:
            raise RuntimeError("PASS181_SINGLETON_VM81_NOT_PRESERVED")
        if admission.get("independent_vm81_authority") is not False:
            raise RuntimeError("PASS181_PEER_VM81_AUTHORITY_CREATED")
        if admission.get("validation_mutation_authority") is not False:
            raise RuntimeError("PASS181_VM81_VALIDATION_MUTATION_AUTHORITY_DRIFT")
        replay = registry.verify_replay()
        if replay.get("ok") is not True:
            raise RuntimeError("PASS181_CONSTRAINT_REPLAY_FAILED")

    return {
        "ok": True,
        "freeze_without_vm81_rejected": True,
        "inherited_vm81_commit_required": True,
        "vm81_receipt_bound": True,
        "legacy_direct_promotion_disabled": True,
        "independent_vm81_authority": False,
    }


def validate_pass181_runtime_reachability() -> dict[str, Any]:
    required = {
        "reference_ingestion": "hhs_backend/runtime/hhs_graphics_hydration_v1.py",
        "canonical_mp4_timeline": "hhs_backend/runtime/hhs_graphics_mp4_decode_v1.py",
        "native_recipe_residual": "hhs_backend/runtime/hhs_graphics_recipe_v1.py",
        "bounded_optimization": "hhs_backend/runtime/hhs_graphics_optimization_v1.py",
        "vector_hydration": "hhs_backend/runtime/hhs_graphics_vector_hydration_v1.py",
        "constraint_registry": "hhs_backend/runtime/hhs_graphics_constraint_registry_v1.py",
        "public_hydration_routes": "hhs_backend/api/graphics_hydration_routes.py",
        "public_constraint_routes": "hhs_backend/api/graphics_constraint_routes.py",
    }
    missing = [name for name, path in required.items() if not (ROOT / path).is_file()]
    if missing:
        raise RuntimeError(f"PASS181_RUNTIME_REACHABILITY_MISSING:{missing}")
    routes = _text(required["public_constraint_routes"])
    for token in ("/registry/freeze", "/registry/rollback", "/registry/replay"):
        if token not in routes:
            raise RuntimeError(f"PASS181_PUBLIC_ROUTE_MISSING:{token}")
    return {"ok": True, "surface_count": len(required), "surfaces": required}


def validate_pass181_global_default_reachability() -> dict[str, Any]:
    contract = json.loads(_text("contracts/pass219/PASS_219_GLOBAL_CANONICAL_DEFAULTS_1_0.json"))
    census = contract["current_cumulative_binding_census"]
    if census["wired_floor_pass"] != 181 or census["binding_count"] != 40:
        raise RuntimeError(f"PASS181_GLOBAL_CENSUS_DRIFT:{census}")
    if census["ordered_bindings"][-5:] != ["185", "184", "183", "182", "181"]:
        raise RuntimeError("PASS181_GLOBAL_CENSUS_TAIL_DRIFT")
    debt = next((x for x in contract["known_repair_forward_debt"] if x.get("pass") == 181), None)
    if debt is None or debt.get("classification") != "WIRED_NONTERMINAL_REPAIR_FORWARD":
        raise RuntimeError("PASS181_NONTERMINAL_DEBT_MISSING")
    if debt.get("terminal_completion_claimed") is not False:
        raise RuntimeError("PASS181_FALSE_TERMINAL_CLAIM")
    if tuple(debt.get("remaining_terminal_obligations") or ()) != REMAINING_TERMINAL_OBLIGATIONS:
        raise RuntimeError("PASS181_TERMINAL_OBLIGATION_DRIFT")
    return {
        "ok": True,
        "wired_floor": 181,
        "binding_count": 40,
        "terminal_completion_claimed": False,
        "repair_forward_required": True,
        "remaining_terminal_obligations": list(REMAINING_TERMINAL_OBLIGATIONS),
    }


def validate_pass181_no_new_authority() -> dict[str, Any]:
    hpp = _text("hhs_runtime/include/hhs_pass219_inherited_pass181_1_45.hpp")
    required = (
        "independent_vm81_authority() noexcept { return false; }",
        "independent_hash72_authority() noexcept { return false; }",
        "hash216_mutation_authority() noexcept { return false; }",
        "floating_point_canonical_authority() noexcept { return false; }",
        "threejs_final_frame_authority() noexcept { return false; }",
        "terminal_pass181_completion_claimed() noexcept { return false; }",
    )
    for token in required:
        if token not in hpp:
            raise RuntimeError(f"PASS181_AUTHORITY_DECLARATION_DRIFT:{token}")
    return {
        "ok": True,
        "singleton_vm81_authority_remains_inherited": True,
        "independent_vm81_authority": False,
        "independent_hash72_authority": False,
        "hash216_mutation_authority": False,
        "floating_point_canonical_authority": False,
        "threejs_final_frame_authority": False,
    }


def pass181_membrane_manifest() -> dict[str, Any]:
    return {
        "pass_number": 181,
        "iteration": 145,
        "contract_id": CONTRACT_ID,
        "classification": "WIRED_NONTERMINAL_PENDING_I145_EXECUTED_VALIDATION",
        "historical_green_head": HISTORICAL_GREEN_HEAD,
        "historical_green_run": HISTORICAL_GREEN_RUN,
        "frozen_predecessor": FROZEN_I144_CHECKPOINT,
        "aggregate_order_tail": [185, 184, 183, 182, 181],
        "terminal_completion_claimed": False,
        "repair_forward_required": True,
        "remaining_terminal_obligations": list(REMAINING_TERMINAL_OBLIGATIONS),
        "merge_status": "UNMERGED",
        "authoritative_main_verification": False,
        "deployment_status": "NOT_PERFORMED",
    }


def execute_pass181_membrane_preflight() -> dict[str, Any]:
    checks = {
        "historical_lineage": validate_pass181_historical_lineage(),
        "runtime_reachability": validate_pass181_runtime_reachability(),
        "vm81_authority_repair": validate_pass181_vm81_authority_repair(),
        "global_default_reachability": validate_pass181_global_default_reachability(),
        "no_new_authority": validate_pass181_no_new_authority(),
    }
    return {
        "ok": all(item.get("ok") is True for item in checks.values()),
        "classification": "HHS_PASS181_I145_DEPENDENCY_SCOPED_PREFLIGHT_VERIFIED",
        "manifest": pass181_membrane_manifest(),
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(execute_pass181_membrane_preflight(), sort_keys=True, indent=2))
