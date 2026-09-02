from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from hhs_runtime.pass163.vmrc import VMRCRuntime
from hhs_runtime.pass179.backends import project_backend
from hhs_runtime.pass179.golden import golden_scene_manifest, lattice_run_scene, motion_5184_scene
from hhs_runtime.pass179.runtime import GraphicsAuthority, command_stream
from hhs_runtime.pass179.shader_ir import compile_shader_ir
from hhs_runtime.pass179.software import render_command_stream

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ID = "HHS-P179-NEGAS-MRL"
VALIDATED_NUCLEUS_HEAD = "ff149faeadf3e31764138a2316052a013b28599c"
NUCLEUS_RECEIPT_BLOB = "b6c7c9b42d3892de6ddaff354514ceafaa695b8e"
INHERITED_I146_HEAD = "f03491cd6744e56e2e81a689416b94a6fb0ae9a4"
PRE_CUMULATIVE_GREEN_RUN = 33621928309
REMAINING_TERMINAL_CATEGORIES = (
    "FULL_NATIVE_2D_3D_LIBRARY",
    "FULL_SHADER_IR_GRAPH_AND_BACKEND_COMPILERS",
    "FULL_WEBGPU_WEBGL2_DEVICE_EXECUTION",
    "THREEJS_PASS178_PARITY",
    "PLAYABLE_NATIVE_LATTICE_RUN",
    "FULL_5184_MOTION_PARITY",
    "IDE_EDITOR_TIMELINE_SHADER_GRAPH",
    "FULL_CAPTURE_VIDEO_PIPELINE",
    "BROWSER_E2E_PERFORMANCE_ACCESSIBILITY_SECURITY",
    "AUTHORITATIVE_MAIN_INTEGRATION",
)


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _text(path: str) -> str:
    return (ROOT / path).read_text("utf-8")


def validate_pass179_frozen_nucleus() -> dict[str, Any]:
    _git("merge-base", "--is-ancestor", INHERITED_I146_HEAD, "HEAD")
    _git("merge-base", "--is-ancestor", VALIDATED_NUCLEUS_HEAD, "HEAD")
    receipt_path = ROOT / "evidence/pass179/i147/PASS_219_I147_PASS179_NATIVE_GRAPHICS_NUCLEUS_RECEIPT_INDEX.json"
    blob = _git("hash-object", str(receipt_path.relative_to(ROOT)))
    if blob != NUCLEUS_RECEIPT_BLOB:
        raise RuntimeError(f"PASS179_NUCLEUS_RECEIPT_BLOB_DRIFT:{blob}")
    receipt = json.loads(receipt_path.read_text("utf-8"))
    validated = receipt["validated_nucleus"]
    if validated["workflow_run_id"] != PRE_CUMULATIVE_GREEN_RUN or validated["conclusion"] != "success":
        raise RuntimeError("PASS179_PRE_CUMULATIVE_RECEIPT_NOT_GREEN")
    return {
        "ok": True,
        "validated_nucleus_head": VALIDATED_NUCLEUS_HEAD,
        "nucleus_receipt_blob": NUCLEUS_RECEIPT_BLOB,
        "pre_cumulative_green_run": PRE_CUMULATIVE_GREEN_RUN,
    }


def validate_pass179_runtime_projection() -> dict[str, Any]:
    vm81 = VMRCRuntime()
    authority = GraphicsAuthority(vm81=vm81)
    scene = lattice_run_scene()
    before = vm81.epoch
    record = authority.commit_scene(scene)
    if vm81.epoch != before + 1:
        raise RuntimeError("PASS179_VM81_COMMIT_DID_NOT_ADVANCE")
    admission = record["vm81_admission"]
    if admission["classification"] != "HHS_PASS179_VM81_SCENE_ADMISSION_VERIFIED":
        raise RuntimeError("PASS179_VM81_ADMISSION_CLASSIFICATION")
    if admission["independent_vm81_authority"] is not False:
        raise RuntimeError("PASS179_PEER_VM81_AUTHORITY")
    if admission["validation_mutation_authority"] is not False:
        raise RuntimeError("PASS179_VALIDATION_MUTATION_AUTHORITY")
    if len(record["post_vm81_hash72_evidence"]) != 72 or len(record["scene_hash216"]) != 216:
        raise RuntimeError("PASS179_HASH_IDENTITY_LENGTH")
    frame = render_command_stream(record["command_stream"])
    if not frame["frame_sha256"] or frame["canonical_mutation_authority"] is not False:
        raise RuntimeError("PASS179_SOFTWARE_RENDERER_AUTHORITY")
    packets = [
        project_backend(record["command_stream"], backend)
        for backend in ("WEBGPU", "WEBGL2", "THREEJS")
    ]
    if any(packet["canonical_mutation_authority"] for packet in packets):
        raise RuntimeError("PASS179_BACKEND_MUTATION_AUTHORITY")
    return {
        "ok": True,
        "vm81_scene_admission": True,
        "post_vm81_hash72_evidence": True,
        "archival_hash216_identity": True,
        "software_renderer_projection_only": True,
        "backend_packets_projection_only": True,
    }


def validate_pass179_shader_and_golden_nuclei() -> dict[str, Any]:
    ir = {
        "schema": "HHS_PASS_179_SHADER_IR_V1",
        "nodes": [
            {"id": "color", "op": "CONST_RGBA16", "rgba16": [65535, 32768, 0, 65535]},
            {"id": "out", "op": "OUTPUT_COLOR", "inputs": ["color"]},
        ],
        "output": "out",
    }
    wgsl = compile_shader_ir(ir, "WGSL")
    glsl = compile_shader_ir(ir, "GLSL")
    if wgsl["shader_ir_sha256"] != glsl["shader_ir_sha256"]:
        raise RuntimeError("PASS179_SHADER_IR_PROJECTION_IDENTITY_DRIFT")
    motion = motion_5184_scene()
    if len(motion.nodes) != 5184 or len({node.node_id for node in motion.nodes}) != 5184:
        raise RuntimeError("PASS179_MOTION_5184_CARDINALITY_DRIFT")
    manifest = golden_scene_manifest()
    if manifest["terminal_golden_scene_parity"] is not False:
        raise RuntimeError("PASS179_FALSE_GOLDEN_TERMINAL_CLAIM")
    return {
        "ok": True,
        "typed_shader_ir": True,
        "wgsl_projection": True,
        "glsl_projection": True,
        "motion_5184_node_count": 5184,
        "terminal_golden_scene_parity": False,
    }


def validate_pass179_global_census() -> dict[str, Any]:
    contract = json.loads(_text("contracts/pass219/PASS_219_GLOBAL_CANONICAL_DEFAULTS_1_0.json"))
    census = contract["current_cumulative_binding_census"]
    if census["wired_floor_pass"] != 179 or census["binding_count"] != 42:
        raise RuntimeError(f"PASS179_GLOBAL_CENSUS_DRIFT:{census}")
    if census["ordered_bindings"][-5:] != ["183", "182", "181", "180", "179"]:
        raise RuntimeError("PASS179_GLOBAL_CENSUS_TAIL_DRIFT")
    debt = next((item for item in contract["known_repair_forward_debt"] if item["pass"] == 179), None)
    if debt is None:
        raise RuntimeError("PASS179_REPAIR_FORWARD_DEBT_MISSING")
    if debt["classification"] != "WIRED_NONTERMINAL_REPAIR_FORWARD":
        raise RuntimeError("PASS179_DEBT_CLASSIFICATION_DRIFT")
    if debt["terminal_completion_claimed"] is not False:
        raise RuntimeError("PASS179_FALSE_TERMINAL_DEBT_CLAIM")
    if tuple(debt["remaining_terminal_categories"]) != REMAINING_TERMINAL_CATEGORIES:
        raise RuntimeError("PASS179_TERMINAL_CATEGORY_DRIFT")
    return {
        "ok": True,
        "wired_floor": 179,
        "binding_count": 42,
        "terminal_completion_claimed": False,
        "repair_forward_required": True,
        "remaining_terminal_category_count": len(REMAINING_TERMINAL_CATEGORIES),
    }


def validate_pass179_exact_binding_surface() -> dict[str, Any]:
    h = _text("hhs_runtime/include/hhs_pass219_inherited_pass179_1_47.h")
    hpp = _text("hhs_runtime/include/hhs_pass219_inherited_pass179_1_47.hpp")
    c = _text("hhs_runtime/c/hhs_pass219_inherited_pass179_1_47.inc")
    exact_h = _text("hhs_runtime/include/hhs_runtime_exact_abi.h")
    exact_c = _text("hhs_runtime/c/hhs_runtime_exact_abi.c")
    for token in (
        "hhs_exact_pass219_bind_pass179_native_graphics",
        "terminal_pass179_completion",
        "repair_forward_required",
        "remaining_terminal_category_count",
    ):
        if token not in h + c:
            raise RuntimeError(f"PASS179_EXACT_BINDING_TOKEN_MISSING:{token}")
    for token in (
        "terminal_pass179_completion_claimed() noexcept { return false; }",
        "repair_forward_required() noexcept { return true; }",
        "independent_hash72_commit_authority() noexcept { return false; }",
        "gpu_mutation_authority() noexcept { return false; }",
    ):
        if token not in hpp:
            raise RuntimeError(f"PASS179_CPP_AUTHORITY_TOKEN_MISSING:{token}")
    if "hhs_pass219_inherited_pass179_1_47.h" not in exact_h:
        raise RuntimeError("PASS179_AGGREGATE_HEADER_MISSING")
    if "hhs_pass219_inherited_pass179_1_47.inc" not in exact_c:
        raise RuntimeError("PASS179_AGGREGATE_SOURCE_MISSING")
    return {
        "ok": True,
        "exact_c_binding": True,
        "exact_cpp_membrane": True,
        "terminal_completion_claimed": False,
        "repair_forward_required": True,
    }


def pass179_membrane_manifest() -> dict[str, Any]:
    return {
        "pass_number": 179,
        "iteration": 147,
        "contract_id": CONTRACT_ID,
        "classification": "WIRED_NONTERMINAL_PENDING_I147_POST_BINDING_VALIDATION",
        "validated_nucleus_head": VALIDATED_NUCLEUS_HEAD,
        "nucleus_receipt_blob": NUCLEUS_RECEIPT_BLOB,
        "aggregate_order_tail": [183, 182, 181, 180, 179],
        "terminal_completion_claimed": False,
        "repair_forward_required": True,
        "remaining_terminal_categories": list(REMAINING_TERMINAL_CATEGORIES),
        "merge_status": "UNMERGED",
        "authoritative_main_verification": False,
    }


def execute_pass179_membrane_preflight() -> dict[str, Any]:
    checks = {
        "frozen_nucleus": validate_pass179_frozen_nucleus(),
        "runtime_projection": validate_pass179_runtime_projection(),
        "shader_and_golden_nuclei": validate_pass179_shader_and_golden_nuclei(),
        "global_census": validate_pass179_global_census(),
        "exact_binding_surface": validate_pass179_exact_binding_surface(),
    }
    return {
        "ok": all(item["ok"] is True for item in checks.values()),
        "classification": "HHS_PASS179_I147_CUMULATIVE_NONTERMINAL_PREFLIGHT_VERIFIED",
        "manifest": pass179_membrane_manifest(),
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(execute_pass179_membrane_preflight(), sort_keys=True, indent=2))
