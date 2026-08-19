"""Pass 219 I121 inherited Pass 203 integrated-mainframe membrane.

This layer exposes the accepted Pass 203 hydrated-function mainframe and
high-fidelity native renderer through the cumulative Pass 219 membrane without
redefining their execution, renderer, UI, persistence, VM81, Hash72, or Hash216
authority. Historical Pass 203 catalog counts remain historical closure evidence;
Pass 204's standalone replay proves that later repository growth remains
compatible without pretending the historical catalog cardinality is timeless.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i120_pass204 import pass204_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_21"
PASS203_NUMBER = 203
PASS203_CLASSIFICATION = "WIRED"
PASS203_CENSUS_CLASSIFICATION = "MISSING_MEMBRANE_EXPOSURE"
PASS203_BIND_SYMBOL = "hhs_exact_pass219_bind_pass203_integrated_mainframe"
PASS203_SURFACE_ID = "validator:pass219.inherited.pass203.integrated-mainframe"

PASS203_CONTRACT_PATH = Path("HHS_PASS_203_UNIVERSAL_HYDRATED_FUNCTION_MAINFRAME.md")
PASS203_RESTART_PATH = Path("docs/pass203/RESTART_RECORD.md")
PASS203_MAINFRAME_RECEIPT_PATH = Path("evidence/pass203/PASS203_MAINFRAME_VALIDATION_RECEIPT.json")
PASS203_RENDER_RECEIPT_PATH = Path("evidence/pass203/PASS203_HIGH_FIDELITY_RENDER_VALIDATION_RECEIPT.json")
PASS203_PASS204_REPLAY_PATH = Path("evidence/pass204/PASS203_INHERITED_VALIDATION_RECEIPT.json")
PASS203_RUNTIME_PATH = Path("hhs_backend/runtime/hhs_pass203_hydrated_mainframe_v1.py")
PASS203_WORKER_PATH = Path("hhs_backend/runtime/hhs_pass203_function_worker_v1.py")
PASS203_STORYBOOK_FUNCTIONS_PATH = Path("hhs_backend/runtime/hhs_pass203_storybook_functions_v1.py")
PASS203_ROUTES_PATH = Path("hhs_backend/api/pass203_mainframe_routes.py")
PASS203_RENDERER_PATH = Path("hhs_backend/runtime/hhs_storybook_reel_v3.py")
PASS203_RENDERER_ROUTES_PATH = Path("hhs_backend/api/storybook_reel_routes.py")
PASS203_MAINFRAME_UI_PATH = Path("applications/holofractal_harmonizer/src/pass203-mainframe.mjs")
PASS203_RENDERER_UI_PATH = Path("applications/storybook_reel_studio/pass203-high-fidelity-controls.js")
PASS203_MAINFRAME_TEST_PATH = Path("tests/test_hhs_pass203_hydrated_mainframe_v1.py")
PASS203_RENDERER_TEST_PATH = Path("tests/test_hhs_pass203_high_fidelity_render_v1.py")
PASS203_MAINFRAME_WORKFLOW_PATH = Path(".github/workflows/pass203-hydrated-mainframe.yml")
PASS203_RENDERER_WORKFLOW_PATH = Path(".github/workflows/storybook-reel-studio.yml")

BASE_COMMIT = "8bd57b5843648efb52092568fae3501eeeefeda0"
VALIDATED_HEAD = "b1bb5ca1908b6e02a037ea412801286867be74b3"
MERGE_COMMIT = "b5209f0dad3fade8bacede8cf1dd10c3fdc12e34"
FINAL_MAINFRAME_WORKFLOW_RUN = 30791006119
FINAL_MAINFRAME_ARTIFACT_ID = 8847098572
FINAL_MAINFRAME_ARTIFACT_DIGEST = "sha256:a1dfa5f26ec84f2bef9b7dc35e67dc8b8150a6da5091e14a0330efe3be50ed26"
FINAL_STORYBOOK_WORKFLOW_RUN = 30791006060
FINAL_STORYBOOK_ARTIFACT_ID = 8847186479
FINAL_STORYBOOK_ARTIFACT_DIGEST = "sha256:be75626243fe1b5cdfcb0ea9eaba7dcc83b2042432352ed1f7a2f0738d1dd3dc"
MAINFRAME_RECEIPT_BLOB = "96ba032149343cffbde17ee9833e47c79395ac14"
RENDERER_RECEIPT_BLOB = "100a97fc47477d2f633626c33e89dfd6ccb44d21"
PASS204_REPLAY_RECEIPT_BLOB = "69e5e3f8db578fee2dfc07573fcce5423add6376"
MAINFRAME_STATUS_HASH72 = "J*pPaI2yHf3zQj6UDE9v*MNVOsw9/uQ-9ZF6Y!?ZaqjSF-(rMK*0R-wQFRt((-ZNc*CU55Ra"
RENDERER_CATALOG_HASH72 = "iN/zFXtXYMQKEf*xUis0(/wqZrCuIh2-5QDiHC8BE<kH!n<xyNubi<0ZPfxA(COAqV9bKmkX"
MAINFRAME_CATALOG_SHA256 = "aefc0c4997ec6ac798d2c1934242719b3176596296b45921032ba31edbc859fe"
RENDERER_FILTER_GRAPH_SHA256 = "d5602d04b1184888cb65ca5ef8384dd251a273374a96011d3d2c60e5dbc69545"

EXPECTED_BLOBS = {
    PASS203_MAINFRAME_RECEIPT_PATH: MAINFRAME_RECEIPT_BLOB,
    PASS203_RENDER_RECEIPT_PATH: RENDERER_RECEIPT_BLOB,
    PASS203_PASS204_REPLAY_PATH: PASS204_REPLAY_RECEIPT_BLOB,
    PASS203_RUNTIME_PATH: "3e4002bc6115f3e6f8d2b33eaf486b37dfa18685",
    PASS203_WORKER_PATH: "5f587460c9c6e51d386eaacd072b0fde787808d1",
    PASS203_STORYBOOK_FUNCTIONS_PATH: "8c39eef09d1e909c19f574e39cb77652bafdaf2e",
    PASS203_ROUTES_PATH: "25cf656a41bd72b3967f0d748ea6cf8b7479e78a",
    PASS203_RENDERER_PATH: "940fbc1d8e0bf071c35d3a8524e676e85a853e16",
    PASS203_RENDERER_ROUTES_PATH: "cb5fda6a1d3074f9bf825362f3a02ef686e088b8",
    PASS203_MAINFRAME_UI_PATH: "59743753aaaf7bed9bafbef3fb015de52deac421",
    PASS203_RENDERER_UI_PATH: "0ed08747993a81385b439bcf2665c6bb45e08c18",
    PASS203_MAINFRAME_TEST_PATH: "26c685c65d006f41adceac7750983e84e8a6e33e",
    PASS203_RENDERER_TEST_PATH: "945e687e1d1ffdb7398a645e86d23ee1c1a5a926",
    PASS203_MAINFRAME_WORKFLOW_PATH: "d69ff55f10e79ff760e03c820f212575f8f46d72",
    PASS203_RENDERER_WORKFLOW_PATH: "77e82a2d8f06c50e68a40babe2df081cc461b313",
}

REQUIRED_OPERATIONS = (
    "validate_pass203_historical_mainframe_identity",
    "validate_pass203_fail_closed_execution_boundary",
    "validate_pass203_renderer_subauthority",
    "validate_pass203_public_projection",
    "validate_pass203_dynamic_replay_compatibility",
    "validate_pass202_inheritance",
    "validate_pass204_successor_binding",
    "validate_pass203_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _load(path: Path) -> Dict[str, Any]:
    value = json.loads(_text(path))
    if not isinstance(value, dict):
        raise RuntimeError("PASS203_OBJECT_REQUIRED:" + str(path))
    return value


def _git_blob(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def pass203_membrane_source_evidence() -> Dict[str, Any]:
    mainframe = _load(PASS203_MAINFRAME_RECEIPT_PATH)
    renderer = _load(PASS203_RENDER_RECEIPT_PATH)
    replay = _load(PASS203_PASS204_REPLAY_PATH)
    contract = _text(PASS203_CONTRACT_PATH)
    restart = _text(PASS203_RESTART_PATH)
    runtime = _text(PASS203_RUNTIME_PATH)
    worker = _text(PASS203_WORKER_PATH)
    renderer_source = _text(PASS203_RENDERER_PATH)
    routes = _text(PASS203_ROUTES_PATH)
    renderer_routes = _text(PASS203_RENDERER_ROUTES_PATH)
    mainframe_ui = _text(PASS203_MAINFRAME_UI_PATH)
    renderer_ui = _text(PASS203_RENDERER_UI_PATH)
    mainframe_workflow = _text(PASS203_MAINFRAME_WORKFLOW_PATH)
    successor = pass204_membrane_source_evidence()

    for path, expected in EXPECTED_BLOBS.items():
        actual = _git_blob(path)
        if actual != expected:
            raise RuntimeError(f"PASS203_FROZEN_BLOB_DRIFT:{path}:{actual}")

    if mainframe.get("schema") != "HHS_PASS_203_VALIDATION_RECEIPT_V1":
        raise RuntimeError("PASS203_MAINFRAME_RECEIPT_SCHEMA_DRIFT")
    if mainframe.get("classification") != "HHS_PASS_203_UNIVERSAL_HYDRATED_FUNCTION_MAINFRAME_VERIFIED":
        raise RuntimeError("PASS203_MAINFRAME_CLASSIFICATION_DRIFT")
    if mainframe.get("contract") != "HHS-P203-UNIVERSAL-HYDRATED-FUNCTION-MAINFRAME-VM81-H72-H216":
        raise RuntimeError("PASS203_MAINFRAME_CONTRACT_DRIFT")
    if mainframe.get("closed") is not True:
        raise RuntimeError("PASS203_MAINFRAME_CLOSURE_DRIFT")
    if mainframe.get("catalog_sha256") != MAINFRAME_CATALOG_SHA256:
        raise RuntimeError("PASS203_MAINFRAME_CATALOG_DIGEST_DRIFT")
    if mainframe.get("status_hash72") != MAINFRAME_STATUS_HASH72 or len(MAINFRAME_STATUS_HASH72) != 72:
        raise RuntimeError("PASS203_MAINFRAME_STATUS_HASH72_DRIFT")

    summary = mainframe.get("summary") or {}
    expected_summary = {
        "catalog_count": 2902,
        "hydrated_count": 688,
        "callable_count": 688,
        "unbound_internal_count": 2214,
        "governed_operation_count": 42,
        "public_route_count": 464,
        "openapi_path_count": 435,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise RuntimeError("PASS203_HISTORICAL_SUMMARY_DRIFT:" + key)
    kinds = summary.get("kind_counts") or {}
    expected_kinds = {
        "PYTHON_FUNCTION": 2644,
        "NATIVE_ABI": 211,
        "GOVERNED_OPERATION": 42,
        "MAINFRAME_ADAPTER": 5,
    }
    for key, expected in expected_kinds.items():
        if kinds.get(key) != expected:
            raise RuntimeError("PASS203_KIND_COUNT_DRIFT:" + key)

    claim = mainframe.get("claim_boundary") or {}
    required_claim = {
        "all_discovered_functions_indexed": True,
        "all_hydrated_functions_callable": True,
        "unbound_functions_fail_closed": True,
        "arbitrary_host_eval_available": False,
        "unrestricted_subprocess_available": False,
        "assistant_plan_is_execution_authority": False,
        "bounded_pagination_preserved": True,
    }
    for key, expected in required_claim.items():
        if claim.get(key) is not expected:
            raise RuntimeError("PASS203_CLAIM_BOUNDARY_DRIFT:" + key)

    if renderer.get("schema") != "HHS_PASS_203_HIGH_FIDELITY_RENDER_VALIDATION_RECEIPT_V1":
        raise RuntimeError("PASS203_RENDERER_RECEIPT_SCHEMA_DRIFT")
    if renderer.get("classification") != "HHS_PASS_203_HIGH_FIDELITY_NATIVE_RENDER_SUBAUTHORITY_VERIFIED":
        raise RuntimeError("PASS203_RENDERER_CLASSIFICATION_DRIFT")
    if renderer.get("contract") != "HHS-P203-HIGH-FIDELITY-NATIVE-RENDER-PARAMETER-AUTHORITY-VM81-H72-H216":
        raise RuntimeError("PASS203_RENDERER_CONTRACT_DRIFT")
    if renderer.get("closed") is not True or renderer.get("all_prior_passes_inherited") is not True:
        raise RuntimeError("PASS203_RENDERER_CLOSURE_DRIFT")
    if renderer.get("catalog_hash72") != RENDERER_CATALOG_HASH72 or len(RENDERER_CATALOG_HASH72) != 72:
        raise RuntimeError("PASS203_RENDERER_CATALOG_HASH72_DRIFT")
    if renderer.get("filter_graph_sha256") != RENDERER_FILTER_GRAPH_SHA256:
        raise RuntimeError("PASS203_RENDERER_FILTER_GRAPH_DRIFT")

    render_summary = renderer.get("summary") or {}
    expected_render = {
        "parameter_count": 415,
        "style_parameter_count": 30,
        "native_layer_parameter_count": 10,
        "render_parameter_count": 21,
        "compiled_native_constant_record_count": 346,
        "quality_profile_count": 5,
        "validated_output_width": 1440,
        "validated_output_height": 2560,
        "texture_flags": 31,
        "sprite_overlay_flags": 31,
    }
    for key, expected in expected_render.items():
        if render_summary.get(key) != expected:
            raise RuntimeError("PASS203_RENDERER_SUMMARY_DRIFT:" + key)

    renderer_claim = renderer.get("claim_boundary") or {}
    required_renderer_claim = {
        "all_mutable_parameters_publicly_enumerated": True,
        "compiled_constants_public_and_read_only": True,
        "frontend_is_authority": False,
        "logical_frame_is_output_quality_ceiling": False,
        "native_frame_identity_preserved": True,
        "native_layers_publicly_selectable": True,
    }
    for key, expected in required_renderer_claim.items():
        if renderer_claim.get(key) is not expected:
            raise RuntimeError("PASS203_RENDERER_CLAIM_DRIFT:" + key)

    if replay.get("schema") != "HHS_PASS_204_INHERITED_PASS_203_REPLAY_RECEIPT_V1":
        raise RuntimeError("PASS203_PASS204_REPLAY_SCHEMA_DRIFT")
    if replay.get("classification") != mainframe.get("classification"):
        raise RuntimeError("PASS203_PASS204_REPLAY_CLASSIFICATION_DRIFT")
    if replay.get("contract") != mainframe.get("contract"):
        raise RuntimeError("PASS203_PASS204_REPLAY_CONTRACT_DRIFT")
    if replay.get("closed") is not True or replay.get("standalone_replay") is not True:
        raise RuntimeError("PASS203_PASS204_STANDALONE_REPLAY_DRIFT")
    replay_summary = replay.get("summary") or {}
    replay_catalog = replay_summary.get("catalog_count")
    replay_callable = replay_summary.get("callable_count")
    replay_hydrated = replay_summary.get("hydrated_count")
    replay_unbound = replay_summary.get("unbound_internal_count")
    if not isinstance(replay_catalog, int) or replay_catalog < 2902:
        raise RuntimeError("PASS203_DYNAMIC_CATALOG_REGRESSION")
    if replay_callable != 688 or replay_hydrated != 688:
        raise RuntimeError("PASS203_DYNAMIC_CALLABLE_SET_DRIFT")
    if replay_unbound != replay_catalog - replay_callable:
        raise RuntimeError("PASS203_DYNAMIC_FAIL_CLOSED_PARTITION_DRIFT")

    required_source_fragments = {
        "runtime": (
            "raw host-language eval and unrestricted",
            "ABI_BINDING_REQUIRED",
            "requires_vm81_authority",
        ),
        "worker": (
            "Isolated bounded Python function worker for Pass 203",
        ),
        "renderer": (
            "Pass 203 cumulative high-fidelity native storybook render authority",
        ),
        "routes": (
            "/api/runtime/mainframe",
        ),
        "renderer_routes": (
            "cumulative Pass 203 native storybook and game renderer",
        ),
        "mainframe_ui": (
            "/api/runtime/mainframe",
        ),
        "renderer_ui": (
            "/api/runtime/storybook-reel",
        ),
    }
    source_texts = {
        "runtime": runtime,
        "worker": worker,
        "renderer": renderer_source,
        "routes": routes,
        "renderer_routes": renderer_routes,
        "mainframe_ui": mainframe_ui,
        "renderer_ui": renderer_ui,
    }
    for group, fragments in required_source_fragments.items():
        for fragment in fragments:
            if fragment not in source_texts[group]:
                raise RuntimeError(f"PASS203_SOURCE_BOUNDARY_DRIFT:{group}:{fragment}")

    if "Pass 203 is the complete HHS version through this pass" not in restart:
        raise RuntimeError("PASS203_RESTART_CUMULATIVE_RULE_DRIFT")
    if "Parent version: Pass 202 guarded continuous integration and DigitalOcean deployment" not in restart:
        raise RuntimeError("PASS203_PASS202_RESTART_INHERITANCE_DRIFT")
    if "Pass 201 public federation regression" not in mainframe_workflow:
        raise RuntimeError("PASS203_PASS201_WORKFLOW_INHERITANCE_DRIFT")
    if "Pass 202 guarded deployment" not in mainframe_workflow:
        raise RuntimeError("PASS203_PASS202_WORKFLOW_INHERITANCE_DRIFT")
    if "arbitrary host-language evaluation" not in contract:
        raise RuntimeError("PASS203_CONTRACT_EXECUTION_BOUNDARY_DRIFT")

    successor_receipt = successor.get("receipt") or {}
    if successor_receipt.get("contract") != "HHS-P204-UNIVERSAL-EXECUTABLE-DECLARATIONS-OPEN-CLOUD-SANDBOX-VM81-H72-H216":
        raise RuntimeError("PASS203_PASS204_SUCCESSOR_DRIFT")

    return {
        "mainframe_receipt": mainframe,
        "renderer_receipt": renderer,
        "pass204_replay_receipt": replay,
        "pass204_successor": successor,
        "base_commit": BASE_COMMIT,
        "validated_head": VALIDATED_HEAD,
        "merge_commit": MERGE_COMMIT,
        "final_mainframe_workflow_run": FINAL_MAINFRAME_WORKFLOW_RUN,
        "final_mainframe_artifact_id": FINAL_MAINFRAME_ARTIFACT_ID,
        "final_mainframe_artifact_digest": FINAL_MAINFRAME_ARTIFACT_DIGEST,
        "final_storybook_workflow_run": FINAL_STORYBOOK_WORKFLOW_RUN,
        "final_storybook_artifact_id": FINAL_STORYBOOK_ARTIFACT_ID,
        "final_storybook_artifact_digest": FINAL_STORYBOOK_ARTIFACT_DIGEST,
        "mainframe_receipt_blob": MAINFRAME_RECEIPT_BLOB,
        "renderer_receipt_blob": RENDERER_RECEIPT_BLOB,
        "pass204_replay_receipt_blob": PASS204_REPLAY_RECEIPT_BLOB,
        "source_blobs": {str(path): value for path, value in EXPECTED_BLOBS.items()},
    }


def validate_pass203_historical_mainframe_identity() -> Dict[str, Any]:
    source = pass203_membrane_source_evidence()
    summary = source["mainframe_receipt"]["summary"]
    return {
        "ok": True,
        "classification": source["mainframe_receipt"]["classification"],
        "validated_head": source["validated_head"],
        "merge_commit": source["merge_commit"],
        "historical_catalog_count": summary["catalog_count"],
        "historical_callable_count": summary["callable_count"],
    }


def validate_pass203_fail_closed_execution_boundary() -> Dict[str, Any]:
    receipt = pass203_membrane_source_evidence()["mainframe_receipt"]
    claim = receipt["claim_boundary"]
    summary = receipt["summary"]
    return {
        "ok": True,
        "historical_unbound_count": summary["unbound_internal_count"],
        "unbound_functions_fail_closed": claim["unbound_functions_fail_closed"],
        "arbitrary_host_eval_available": claim["arbitrary_host_eval_available"],
        "unrestricted_subprocess_available": claim["unrestricted_subprocess_available"],
        "assistant_plan_is_execution_authority": claim["assistant_plan_is_execution_authority"],
    }


def validate_pass203_renderer_subauthority() -> Dict[str, Any]:
    receipt = pass203_membrane_source_evidence()["renderer_receipt"]
    return {
        "ok": True,
        "classification": receipt["classification"],
        "summary": receipt["summary"],
        "claim_boundary": receipt["claim_boundary"],
    }


def validate_pass203_public_projection() -> Dict[str, Any]:
    pass203_membrane_source_evidence()
    return {
        "ok": True,
        "mainframe_api": "/api/runtime/mainframe",
        "renderer_api": "/api/runtime/storybook-reel",
        "mainframe_ui_bound": True,
        "renderer_ui_bound": True,
        "frontend_is_authority": False,
    }


def validate_pass203_dynamic_replay_compatibility() -> Dict[str, Any]:
    source = pass203_membrane_source_evidence()
    historical = source["mainframe_receipt"]["summary"]
    replay = source["pass204_replay_receipt"]["summary"]
    return {
        "ok": True,
        "historical_catalog_count": historical["catalog_count"],
        "replay_catalog_count": replay["catalog_count"],
        "historical_callable_count": historical["callable_count"],
        "replay_callable_count": replay["callable_count"],
        "standalone_replay": source["pass204_replay_receipt"]["standalone_replay"],
        "dynamic_catalog_growth_compatible": True,
    }


def validate_pass202_inheritance() -> Dict[str, Any]:
    pass203_membrane_source_evidence()
    return {
        "ok": True,
        "parent_pass": 202,
        "parent_boundary": "guarded continuous integration and DigitalOcean deployment",
        "workflow_regression_bound": True,
    }


def validate_pass204_successor_binding() -> Dict[str, Any]:
    successor = pass203_membrane_source_evidence()["pass204_successor"]
    return {
        "ok": True,
        "successor_pass": 204,
        "successor_contract": successor["receipt"]["contract"],
        "successor_classification": successor["receipt"]["classification"],
    }


def validate_pass203_no_new_authority() -> Dict[str, Any]:
    pass203_membrane_source_evidence()
    return {
        "ok": True,
        "i121_new_execution_authority": False,
        "i121_new_canonical_mutation_authority": False,
        "i121_new_persistence_authority": False,
        "i121_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
    }


def pass203_surface_declaration() -> Dict[str, Any]:
    pass203_membrane_source_evidence()
    return {
        "surface_id": PASS203_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i121_pass203",
        "symbol": "validate_pass203_historical_mainframe_identity",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS_PASS_203_VALIDATION_RECEIPT_V1",
            "HHS_PASS_203_HIGH_FIDELITY_RENDER_VALIDATION_RECEIPT_V1",
            "HHS_PASS_204_INHERITED_PASS_203_REPLAY_RECEIPT_V1",
        ],
        "witness_schemas": [
            "HHSExactPass203IntegratedMainframeWitnessV1",
            "HHSExactPass219InheritedPass203BindingV1",
        ],
        "validators": [PASS203_BIND_SYMBOL, "validate_pass203_historical_mainframe_identity"],
        "guards": [
            "pass203_historical_receipts_exact",
            "pass203_unbound_functions_fail_closed",
            "pass203_no_arbitrary_host_eval",
            "pass203_no_unrestricted_subprocess",
            "pass203_renderer_frontend_not_authority",
            "pass203_compiled_constants_read_only",
            "pass203_dynamic_catalog_replay_preserved",
            "pass203_pass202_inheritance_preserved",
            "pass203_pass204_successor_preserved",
        ],
        "rejection_codes": [
            "REJECT_PASS203_HISTORICAL_IDENTITY_DRIFT",
            "REJECT_PASS203_FAIL_CLOSED_BOUNDARY_DRIFT",
            "REJECT_PASS203_HOST_EXECUTION_ESCAPE",
            "REJECT_PASS203_RENDERER_AUTHORITY_ESCALATION",
            "REJECT_PASS203_PUBLIC_PROJECTION_DRIFT",
            "REJECT_PASS203_DYNAMIC_REPLAY_REGRESSION",
            "REJECT_PASS203_PASS202_INHERITANCE_DRIFT",
            "REJECT_PASS203_PASS204_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_PASS203_RUNTIME_STATE_READ_ONLY_BINDING",
        "boundedness_policy": "PASS_203_VERIFIED_MAINFRAME_AND_RENDERER_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass203_membrane_manifest() -> Dict[str, Any]:
    source = pass203_membrane_source_evidence()
    mainframe = source["mainframe_receipt"]
    renderer = source["renderer_receipt"]
    replay = source["pass204_replay_receipt"]
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS203_NUMBER,
        "classification": PASS203_CLASSIFICATION,
        "census_classification": PASS203_CENSUS_CLASSIFICATION,
        "pass219_c_abi_surface": PASS203_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass203IntegratedMainframe",
        "historical_catalog_count": mainframe["summary"]["catalog_count"],
        "historical_callable_count": mainframe["summary"]["callable_count"],
        "historical_unbound_count": mainframe["summary"]["unbound_internal_count"],
        "renderer_record_count": renderer["summary"]["parameter_count"],
        "pass204_replay_catalog_count": replay["summary"]["catalog_count"],
        "pass204_standalone_replay_bound": replay["standalone_replay"],
        "fail_closed_binding_gaps_bound": True,
        "renderer_subauthority_bound": True,
        "renderer_frontend_is_authority": False,
        "pass202_inheritance_bound": True,
        "pass204_successor_bound": True,
        "pass219_new_execution_authority": False,
        "pass219_new_canonical_mutation_authority": False,
        "pass219_new_persistence_authority": False,
        "pass219_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "validated_head": source["validated_head"],
        "merge_commit": source["merge_commit"],
        "mainframe_receipt_blob": source["mainframe_receipt_blob"],
        "renderer_receipt_blob": source["renderer_receipt_blob"],
        "pass204_replay_receipt_blob": source["pass204_replay_receipt_blob"],
        "source_blobs": source["source_blobs"],
        "surface": pass203_surface_declaration(),
    }


def preflight_pass203_membrane() -> Dict[str, Any]:
    declaration = pass203_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    ok = all(row.get("ok") is True for row in rows)
    return {
        "schema": "HHS_PASS219_I121_PASS203_MEMBRANE_PREFLIGHT_V1",
        "ok": ok,
        "surface_id": PASS203_SURFACE_ID,
        "operations": rows,
        "manifest": pass203_membrane_manifest(),
    }


if __name__ == "__main__":
    print(json.dumps(preflight_pass203_membrane(), indent=2, sort_keys=True))
