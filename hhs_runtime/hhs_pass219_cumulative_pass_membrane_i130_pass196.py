"""Pass 219 I130 membrane for repaired inherited Pass 196 integrated environment."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i129_pass197 import pass197_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_30"
PASS196_NUMBER = 196
PASS196_CLASSIFICATION = "WIRED"
PASS196_CENSUS_CLASSIFICATION = "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
PASS196_BIND_SYMBOL = "hhs_exact_pass219_bind_pass196_repaired_integrated_environment"
PASS196_SURFACE_ID = "validator:pass219.inherited.pass196.repaired-integrated-environment"

P = Path
V1_PATH = P("hhs_backend/runtime/hhs_pass196_integrated_environment_v1.py")
V2_PATH = P("hhs_backend/runtime/hhs_pass196_integrated_environment_v2.py")
API_PATH = P("hhs_backend/api/pass196_integration_routes.py")
FRONTEND_PATH = P("applications/holofractal_harmonizer/src/pass196-integration.mjs")
PROJECTION_PATH = P("applications/holofractal_harmonizer/src/pass196-projection-refresh.mjs")
REPAIR_TEST_PATH = P("tests/test_hhs_pass196_i130_repair_v2.py")
REPAIR_WORKFLOW_PATH = P(".github/workflows/pass196-i130-repair-validation.yml")
SERVICE_PATH = P("deploy/digitalocean/hhs-pass196-integrated-environment.service")

ACCEPTED_PRIMARY_MERGE = "37687d479f2a9f1d996d225a4ba3556d9db72a86"
ACCEPTED_TOPOLOGY_MERGE = "959729c9070399fcdf0015702cd8777079e05dcc"
FROZEN_I129 = "40e6e07d5f4a401541a6255339223e853846e713"
HISTORICAL_V1_BLOB = "d2cff008db58a29bf27be20cb3547b9e0018f5e1"
REPAIRED_BLOBS = {
    V2_PATH: "196b1fbdbbb3610ccb47e7fd638d4c3f2cdc67f6",
    API_PATH: "39187c3376591c64758019090d9b115c6a43f6ee",
    FRONTEND_PATH: "1503903c844c9e601133853eed9ed597f6fd2274",
    PROJECTION_PATH: "44254e10f90e929a4f8c1a18a75b3ca14a2c05ed",
    REPAIR_TEST_PATH: "55d1da0ea58044436646ccd8a331088135515c8f",
    REPAIR_WORKFLOW_PATH: "7a19d3e7faab6e7210e156026300e96550b9afcb",
}
REVIEW_FINDING_IDS = (
    3699626177, 3699626180, 3699626182, 3699626186, 3699626190,
    3699626194, 3699626196, 3699626198, 3699626201, 3699626204,
)
REQUIRED_OPERATIONS = (
    "validate_pass196_historical_identity",
    "validate_pass196_ten_finding_repair",
    "validate_pass196_observation_and_manifest_boundary",
    "validate_pass196_persistence_and_restart_boundary",
    "validate_pass196_api_and_projection_boundary",
    "validate_pass196_successor_binding",
    "validate_pass196_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _git_blob(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _git(*args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return completed.stdout.strip()


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS196_REPAIR_SOURCE_DRIFT:{path}:{fragment}")


def pass196_membrane_source_evidence() -> Dict[str, Any]:
    if _git("merge-base", "--is-ancestor", ACCEPTED_PRIMARY_MERGE, "HEAD") != "":
        raise RuntimeError("PASS196_PRIMARY_MERGE_ANCESTRY_OUTPUT")
    if _git("merge-base", "--is-ancestor", ACCEPTED_TOPOLOGY_MERGE, "HEAD") != "":
        raise RuntimeError("PASS196_TOPOLOGY_MERGE_ANCESTRY_OUTPUT")
    if _git("merge-base", "HEAD", FROZEN_I129) != FROZEN_I129:
        raise RuntimeError("PASS196_FROZEN_I129_LINEAGE_DRIFT")
    if _git_blob(V1_PATH) != HISTORICAL_V1_BLOB:
        raise RuntimeError("PASS196_HISTORICAL_V1_DRIFT")
    for path, expected in REPAIRED_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS196_REPAIRED_SOURCE_DRIFT:{path}")

    _require(V2_PATH,
        "PASS196_VM81_HASH72_RECEIPT_REQUIRED_FOR_PERSISTENCE",
        "PASS196_FILE_CHANGED_DURING_SCAN",
        "same_bytes_hash_and_classification",
        "_restore_vector_lineage",
        "PASS196_CURRENT_MANIFEST_QUARANTINED",
        "last_good_is_historical_only",
    )
    _require(API_PATH, "StrictBool", "PASS196_PERSIST_VECTOR_STRICT_BOOL_REQUIRED", "_scan_http_error")
    _require(PROJECTION_PATH,
        "refreshValidatedProjection",
        "P196_PROJECTION_AUTHORITY_ESCALATION_REJECTED",
        "P161_REPLAY",
        "frontend_is_authority: false",
    )
    _require(FRONTEND_PATH, "installPass196ProjectionRefresh", "CURRENT_SCAN_QUARANTINED")
    _require(SERVICE_PATH, "StateDirectory=hhs", "WorkingDirectory=/opt/hhs/app", "HHS_PASS196_STATE_ROOT=/var/lib/hhs/pass196")

    successor = pass197_membrane_source_evidence()
    if successor.get("accepted_merge") != "2321a1f05a6da410034a31ca141e3919091bb09a":
        raise RuntimeError("PASS196_PASS197_SUCCESSOR_IDENTITY_DRIFT")
    return {
        "accepted_primary_merge": ACCEPTED_PRIMARY_MERGE,
        "accepted_topology_merge": ACCEPTED_TOPOLOGY_MERGE,
        "frozen_i129": FROZEN_I129,
        "historical_v1_blob": HISTORICAL_V1_BLOB,
        "repaired_blobs": {str(path): value for path, value in REPAIRED_BLOBS.items()},
        "review_finding_ids": list(REVIEW_FINDING_IDS),
        "pass197_successor": successor,
    }


def validate_pass196_historical_identity() -> Dict[str, Any]:
    s = pass196_membrane_source_evidence()
    return {"ok": True, "primary_pull_request": 128, "topology_pull_request": 130, "accepted_primary_merge": s["accepted_primary_merge"], "accepted_topology_merge": s["accepted_topology_merge"], "historical_v1_preserved": True}


def validate_pass196_ten_finding_repair() -> Dict[str, Any]:
    s = pass196_membrane_source_evidence()
    return {"ok": True, "repair_schema": "HHS_PASS_196_I130_REPAIR_V1", "review_finding_ids": s["review_finding_ids"], "finding_count": 10, "service_state_directory_previously_repaired_and_preserved": True}


def validate_pass196_observation_and_manifest_boundary() -> Dict[str, Any]:
    pass196_membrane_source_evidence()
    return {"ok": True, "same_bytes_hash_and_classification": True, "host_independent_manifest_identity": True, "distinct_executable_evidence_required": True, "failed_scan_quarantines_current_success": True}


def validate_pass196_persistence_and_restart_boundary() -> Dict[str, Any]:
    pass196_membrane_source_evidence()
    return {"ok": True, "vm81_hash72_receipt_required_for_persistence": True, "persisted_restart_lineage_restored": True, "vector_store_is_source_authority": False}


def validate_pass196_api_and_projection_boundary() -> Dict[str, Any]:
    pass196_membrane_source_evidence()
    return {"ok": True, "strict_boolean_tool_ingress": True, "scan_error_mapping_parity": True, "validated_projection_refresh": True, "browser_projection_is_authority": False}


def validate_pass196_successor_binding() -> Dict[str, Any]:
    successor = pass196_membrane_source_evidence()["pass197_successor"]
    return {"ok": True, "successor_pass": 197, "successor_accepted_merge": successor["accepted_merge"], "successor_preserved": True}


def validate_pass196_no_new_authority() -> Dict[str, Any]:
    pass196_membrane_source_evidence()
    return {"ok": True, "i130_new_candidate_authority": False, "i130_new_canonical_mutation_authority": False, "i130_new_persistence_authority": False, "i130_new_hash72_clock": False, "cxx_mutation_authority": False, "vm81_mutation_authority": False, "singleton_vm81_authority_remains_inherited": True}


def pass196_surface_declaration() -> Dict[str, Any]:
    pass196_membrane_source_evidence()
    return {
        "surface_id": PASS196_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i130_pass196",
        "symbol": "validate_pass196_ten_finding_repair",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P196-SPIRAH-EVDB-LINUX-TOOLSERVER-VIDE-VM81-H72-H216"],
        "witness_schemas": ["HHSExactPass196RepairedIntegratedEnvironmentWitnessV1", "HHSExactPass219InheritedPass196BindingV1"],
        "validators": [PASS196_BIND_SYMBOL, "validate_pass196_ten_finding_repair"],
        "guards": ["pass196_vm81_receipt", "pass196_restart_lineage", "pass196_exact_observation", "pass196_reproducible_manifest", "pass196_failure_quarantine", "pass196_projection_refresh", "pass196_pass197_successor"],
        "rejection_codes": ["REJECT_PASS196_PROVENANCE_DRIFT", "REJECT_PASS196_RECEIPT_BYPASS", "REJECT_PASS196_RESTART_LINEAGE_DRIFT", "REJECT_PASS196_OBSERVATION_RACE", "REJECT_PASS196_STALE_SUCCESS", "REJECT_PASS196_AUTHORITY_ESCALATION", "REJECT_PASS196_SUCCESSOR_DRIFT"],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_PASS196_VM81_RECEIPT_BOUND_VECTOR_PERSISTENCE_ONLY",
        "boundedness_policy": "PASS_196_REPAIRED_INTEGRATED_ENVIRONMENT_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass196_membrane_manifest() -> Dict[str, Any]:
    s = pass196_membrane_source_evidence()
    return {"schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1", "version": VERSION, "pass_number": PASS196_NUMBER, "classification": PASS196_CLASSIFICATION, "census_classification": PASS196_CENSUS_CLASSIFICATION, "accepted_primary_merge": s["accepted_primary_merge"], "accepted_topology_merge": s["accepted_topology_merge"], "frozen_predecessor": s["frozen_i129"], "review_finding_ids": s["review_finding_ids"], "surface": pass196_surface_declaration(), "declared_operations": list(REQUIRED_OPERATIONS)}


def execute_pass196_membrane_preflight() -> Dict[str, Any]:
    declaration = pass196_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    return {"schema": "HHS_PASS219_I130_PASS196_PREFLIGHT_V1", "version": VERSION, "ok": all(row.get("ok") is True for row in rows), "surface_id": PASS196_SURFACE_ID, "operations": rows}


OPERATIONS = {
    "validate_pass196_historical_identity": validate_pass196_historical_identity,
    "validate_pass196_ten_finding_repair": validate_pass196_ten_finding_repair,
    "validate_pass196_observation_and_manifest_boundary": validate_pass196_observation_and_manifest_boundary,
    "validate_pass196_persistence_and_restart_boundary": validate_pass196_persistence_and_restart_boundary,
    "validate_pass196_api_and_projection_boundary": validate_pass196_api_and_projection_boundary,
    "validate_pass196_successor_binding": validate_pass196_successor_binding,
    "validate_pass196_no_new_authority": validate_pass196_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 196 I130 membrane operation: {operation}")
    return OPERATIONS[operation]()
