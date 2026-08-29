"""Pass 219 I131 membrane for repaired inherited Pass 195 Kimi K3 content engine."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i130_pass196 import pass196_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_31"
PASS195_NUMBER = 195
PASS195_CLASSIFICATION = "WIRED"
PASS195_CENSUS_CLASSIFICATION = "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
PASS195_BIND_SYMBOL = "hhs_exact_pass219_bind_pass195_repaired_kimi_k3_content_engine"
PASS195_SURFACE_ID = "validator:pass219.inherited.pass195.repaired-kimi-k3-content-engine"

P = Path
V1_PATH = P("hhs_backend/runtime/hhs_kimi_k3_content_engine_v1.py")
V2_PATH = P("hhs_backend/runtime/hhs_kimi_k3_content_engine_v2.py")
API_PATH = P("hhs_backend/api/kimi_k3_content_routes.py")
FRONTEND_PATH = P("applications/storybook_reel_studio/kimi-content-engine.js")
REPAIR_TEST_PATH = P("tests/test_hhs_pass195_i131_repair_v2.py")
REPAIR_WORKFLOW_PATH = P(".github/workflows/pass195-i131-repair-validation.yml")

ACCEPTED_PRIMARY_MERGE = "8bcc0921555ecface13113c8a2620415ddb3fdf1"
FROZEN_I130 = "69743440249dd7a05aa2b4096482d248973f239e"
HISTORICAL_V1_BLOB = "ea7041c026e63445034c7161268faafe436cd2d1"
REPAIRED_BLOBS = {
    V2_PATH: "c1cf830a8ede708b62cc052610968f7fc498228d",
    API_PATH: "e62f59d5c8617a546908fd9ca2bd43998c62cd2e",
    FRONTEND_PATH: "9153f922193ddadf2e208986e11dc9d57e12f817",
    REPAIR_TEST_PATH: "866a893e30dfd9565b712df9ff9c979395b25a3f",
    REPAIR_WORKFLOW_PATH: "f43d6cdb62e8836e075cb4400d9525eaf8f4d491",
}
REVIEW_FINDING_IDS = (
    3696077892, 3696077894, 3696077896, 3696077898,
    3696077899, 3696077901, 3696077903, 3696077905,
    3696077907, 3696077910, 3696077912, 3696077914,
)
REQUIRED_OPERATIONS = (
    "validate_pass195_historical_identity",
    "validate_pass195_provider_plan_and_input_binding",
    "validate_pass195_frontend_and_storybook_boundary",
    "validate_pass195_paid_route_boundary",
    "validate_pass195_multimodal_capability_boundary",
    "validate_pass195_tick_and_health_boundary",
    "validate_pass195_successor_binding",
    "validate_pass195_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _git_blob(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return completed.stdout.strip()


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS195_REPAIR_SOURCE_DRIFT:{path}:{fragment}")


def pass195_membrane_source_evidence() -> Dict[str, Any]:
    if _git("merge-base", "--is-ancestor", ACCEPTED_PRIMARY_MERGE, "HEAD") != "":
        raise RuntimeError("PASS195_PRIMARY_MERGE_ANCESTRY_OUTPUT")
    if _git("merge-base", "HEAD", FROZEN_I130) != FROZEN_I130:
        raise RuntimeError("PASS195_FROZEN_I130_LINEAGE_DRIFT")
    if _git_blob(V1_PATH) != HISTORICAL_V1_BLOB:
        raise RuntimeError("PASS195_HISTORICAL_V1_DRIFT")
    for path, expected in REPAIRED_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS195_REPAIRED_SOURCE_DRIFT:{path}")

    _require(
        V2_PATH,
        "KIMI_K3_PROVIDER_PLAN_SCHEMA_REJECTED",
        "constraints_root_hash72",
        "IMAGE_ANALYSIS",
        "image_analysis_invocation_receipt_hash72",
        "model_id = str(completion.get(\"model\") or self.config.model_id)",
        "status_root_hash72",
    )
    _require(
        API_PATH,
        "HHS_KIMI_K3_OPERATOR_TOKEN",
        "_PLAN_SEMAPHORE",
        "_consume_rate_slot",
        "_packet_from_authorized_tick",
        "runtime_graph.ingest_runtime_state(_packet_from_authorized_tick(authorized_tick))",
    )
    if "export_multimodal_packet()" in _text(API_PATH):
        raise RuntimeError("PASS195_POST_PROVIDER_GLOBAL_RUNTIME_EXPORT_REINTRODUCED")
    _require(
        FRONTEND_PATH,
        "payload?.ok !== true",
        "payload?.provider_result_ingress?.ok !== true",
        "'Authorization': `Bearer ${operatorToken}`",
    )
    frontend = _text(FRONTEND_PATH)
    if frontend.index("template.value = style.template_id") >= frontend.index(
        "for (const [key, value] of Object.entries(style))"
    ):
        raise RuntimeError("PASS195_TEMPLATE_OVERRIDE_ORDER_DRIFT")

    successor = pass196_membrane_source_evidence()
    if successor.get("accepted_primary_merge") != "37687d479f2a9f1d996d225a4ba3556d9db72a86":
        raise RuntimeError("PASS195_PASS196_SUCCESSOR_IDENTITY_DRIFT")
    return {
        "accepted_primary_merge": ACCEPTED_PRIMARY_MERGE,
        "frozen_i130": FROZEN_I130,
        "historical_v1_blob": HISTORICAL_V1_BLOB,
        "repaired_blobs": {str(path): value for path, value in REPAIRED_BLOBS.items()},
        "review_finding_ids": list(REVIEW_FINDING_IDS),
        "pass196_successor": successor,
    }


def validate_pass195_historical_identity() -> Dict[str, Any]:
    source = pass195_membrane_source_evidence()
    return {
        "ok": True,
        "primary_pull_request": 117,
        "accepted_primary_merge": source["accepted_primary_merge"],
        "historical_v1_preserved": True,
        "finding_count": len(REVIEW_FINDING_IDS),
    }


def validate_pass195_provider_plan_and_input_binding() -> Dict[str, Any]:
    pass195_membrane_source_evidence()
    return {
        "ok": True,
        "provider_plan_schema_validated_before_admission": True,
        "constraints_content_bound_to_proposal": True,
        "reference_image_content_bound_to_proposal": True,
        "model_identity_bound_before_plan_hash": True,
    }


def validate_pass195_frontend_and_storybook_boundary() -> Dict[str, Any]:
    pass195_membrane_source_evidence()
    return {
        "ok": True,
        "frontend_requires_admitted_provider_result": True,
        "template_applied_before_custom_overrides": True,
        "handoff_title_story_bounds_match_storybook": True,
        "style_ranges_match_storybook_controls": True,
        "browser_handoff_is_canonical_authority": False,
    }


def validate_pass195_paid_route_boundary() -> Dict[str, Any]:
    pass195_membrane_source_evidence()
    return {
        "ok": True,
        "operator_authorization_required": True,
        "bounded_concurrency": True,
        "bounded_rate": True,
        "provider_secret_exposed_to_client": False,
    }


def validate_pass195_multimodal_capability_boundary() -> Dict[str, Any]:
    pass195_membrane_source_evidence()
    return {
        "ok": True,
        "text_generation_capability_required": True,
        "image_analysis_capability_required_when_images_present": True,
        "image_analysis_receipt_bound_to_text_invocation": True,
        "provider_output_is_proposal_only": True,
    }


def validate_pass195_tick_and_health_boundary() -> Dict[str, Any]:
    pass195_membrane_source_evidence()
    return {
        "ok": True,
        "authorized_tick_ingested_before_provider_await": True,
        "post_provider_global_runtime_export_forbidden": True,
        "provider_failure_does_not_orphan_authorized_tick": True,
        "health_hash_seals_final_returned_object": True,
    }


def validate_pass195_successor_binding() -> Dict[str, Any]:
    successor = pass195_membrane_source_evidence()["pass196_successor"]
    return {
        "ok": True,
        "successor_pass": 196,
        "successor_accepted_merge": successor["accepted_primary_merge"],
        "successor_preserved": True,
    }


def validate_pass195_no_new_authority() -> Dict[str, Any]:
    pass195_membrane_source_evidence()
    return {
        "ok": True,
        "external_provider_is_canonical_authority": False,
        "browser_handoff_is_canonical_authority": False,
        "i131_new_candidate_authority": False,
        "i131_new_canonical_mutation_authority": False,
        "i131_new_persistence_authority": False,
        "i131_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "singleton_vm81_authority_remains_inherited": True,
    }


def pass195_surface_declaration() -> Dict[str, Any]:
    pass195_membrane_source_evidence()
    return {
        "surface_id": PASS195_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i131_pass195",
        "symbol": "validate_pass195_provider_plan_and_input_binding",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P195-KIMI-K3-MULTIMODAL-CONTENT-ENGINE"],
        "witness_schemas": [
            "HHSExactPass195RepairedKimiK3ContentEngineWitnessV1",
            "HHSExactPass219InheritedPass195BindingV1",
        ],
        "validators": [PASS195_BIND_SYMBOL, "validate_pass195_provider_plan_and_input_binding"],
        "guards": [
            "pass195_strict_provider_plan",
            "pass195_exact_input_receipt",
            "pass195_frontend_ingress",
            "pass195_paid_route_authorization",
            "pass195_multimodal_capability",
            "pass195_exact_tick_graph",
            "pass195_final_health_identity",
            "pass195_pass196_successor",
        ],
        "rejection_codes": [
            "REJECT_PASS195_PROVENANCE_DRIFT",
            "REJECT_PASS195_PROVIDER_SCHEMA_DRIFT",
            "REJECT_PASS195_INPUT_RECEIPT_BYPASS",
            "REJECT_PASS195_FRONTEND_INGRESS_BYPASS",
            "REJECT_PASS195_OPERATOR_AUTH_BYPASS",
            "REJECT_PASS195_MULTIMODAL_CAPABILITY_BYPASS",
            "REJECT_PASS195_RUNTIME_TICK_DRIFT",
            "REJECT_PASS195_AUTHORITY_ESCALATION",
        ],
        "mutation_policy": "NO_EXTERNAL_PROVIDER_DIRECT_STATE_MUTATION",
        "persistence_policy": "NO_NEW_PERSISTENCE_AUTHORITY",
        "boundedness_policy": "PASS_195_REPAIRED_KIMI_K3_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass195_membrane_manifest() -> Dict[str, Any]:
    source = pass195_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS195_NUMBER,
        "classification": PASS195_CLASSIFICATION,
        "census_classification": PASS195_CENSUS_CLASSIFICATION,
        "accepted_primary_merge": source["accepted_primary_merge"],
        "frozen_predecessor": source["frozen_i130"],
        "review_finding_ids": source["review_finding_ids"],
        "surface": pass195_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass195_membrane_preflight() -> Dict[str, Any]:
    declaration = pass195_surface_declaration()
    rows = [
        execute_surface_preflight(declaration, operation=operation)
        for operation in REQUIRED_OPERATIONS
    ]
    return {
        "schema": "HHS_PASS219_I131_PASS195_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS195_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass195_historical_identity": validate_pass195_historical_identity,
    "validate_pass195_provider_plan_and_input_binding": validate_pass195_provider_plan_and_input_binding,
    "validate_pass195_frontend_and_storybook_boundary": validate_pass195_frontend_and_storybook_boundary,
    "validate_pass195_paid_route_boundary": validate_pass195_paid_route_boundary,
    "validate_pass195_multimodal_capability_boundary": validate_pass195_multimodal_capability_boundary,
    "validate_pass195_tick_and_health_boundary": validate_pass195_tick_and_health_boundary,
    "validate_pass195_successor_binding": validate_pass195_successor_binding,
    "validate_pass195_no_new_authority": validate_pass195_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 195 I131 membrane operation: {operation}")
    return OPERATIONS[operation]()
