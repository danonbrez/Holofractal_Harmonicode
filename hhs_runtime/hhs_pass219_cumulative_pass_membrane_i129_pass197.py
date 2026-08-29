"""Pass 219 I129 membrane for repaired inherited Pass 197 A/B hydration calibration."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i128_pass198 import pass198_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_29"
PASS197_NUMBER = 197
PASS197_CLASSIFICATION = "WIRED"
PASS197_CENSUS_CLASSIFICATION = "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
PASS197_BIND_SYMBOL = "hhs_exact_pass219_bind_pass197_repaired_hydration_calibration"
PASS197_SURFACE_ID = "validator:pass219.inherited.pass197.repaired-hydration-calibration"

P = Path
CONTRACT_PATH = P("HHS_PASS_197_AB_HYDRATION_CALIBRATION.md")
EXACT_PATH = P("hhs_backend/runtime/pass197_exact_v1.py")
STATE_PATH = P("hhs_backend/runtime/pass197_state_v1.py")
RUNTIME_PATH = P("hhs_backend/runtime/hhs_pass197_ab_hydration_calibration_v1.py")
API_PATH = P("hhs_backend/api/pass197_calibration_routes.py")
FRONTEND_PATH = P("applications/holofractal_harmonizer/src/pass197-calibration.mjs")
HISTORICAL_TEST_PATH = P("tests/test_hhs_pass197_ab_hydration_calibration_v1.py")
REPAIR_TEST_PATH = P("tests/test_hhs_pass197_i129_repair_v1.py")
HISTORICAL_WORKFLOW_PATH = P(".github/workflows/pass197-ab-hydration-calibration.yml")
REPAIR_WORKFLOW_PATH = P(".github/workflows/pass197-i129-repair-validation.yml")

HISTORICAL_BASE = "77bf7ddfcfb09246a805a6e8f0919cfa18d0f3c0"
HISTORICAL_REVIEWED_HEAD = "aeadabcce0ea178ad5b6a27001e109f349808dde"
ACCEPTED_MERGE = "2321a1f05a6da410034a31ca141e3919091bb09a"
FROZEN_I128 = "c85b2b29cdf26d21912eb06b7d50323526944cc2"

HISTORICAL_BLOBS = {
    EXACT_PATH: "8f1674801005a0de400a13d61ac537b11d65e152",
    STATE_PATH: "4a60cae7139771feea0e1131fd6b40143f8e42fd",
    RUNTIME_PATH: "597afc78212df9460688d71fc262bbd3f9b881ba",
    API_PATH: "daa7a22d85f685b123292e10cc6b5e05bb5fe9ef",
    FRONTEND_PATH: "81161f6af73120c6d5fa2fd5e1a0eb4a5c579050",
    HISTORICAL_TEST_PATH: "a1a495bfd2deab466570d4a54b38af4f3060d4a5",
    HISTORICAL_WORKFLOW_PATH: "a4ec60a0c1e77869c2016766c8b994c259e05042",
}

REPAIRED_BLOBS = {
    EXACT_PATH: "96be2009ca46cbcab7633f6fae97a0bea7621abb",
    STATE_PATH: "10c986063d5fa2503d732e6725bb3b8665372666",
    RUNTIME_PATH: "6d86629bdf25bdb03890197475a12dbf9190c618",
    API_PATH: "0325974ff78c097b010b297971c2243d4132af43",
    FRONTEND_PATH: "f68cac28e29a29da99c4cb415778fb1c196a19f2",
    REPAIR_TEST_PATH: "1924e7c9eb3642087b6b2792ce75fded38dbee00",
    REPAIR_WORKFLOW_PATH: "76786543a6bac5f0884c19e8226369ae8f47ff0c",
}

REVIEW_FINDING_IDS = (
    3699915198,
    3699915199,
    3699915201,
    3699915203,
    3699915204,
    3699915205,
    3699915207,
    3699915209,
    3699915210,
    3699915212,
)

PRODUCTION_TOTALS = {
    "parameter_states": 405,
    "admitted_states": 320,
    "domain_rejections": 85,
    "vm5184_address_comparisons": 1_658_880,
}

REQUIRED_OPERATIONS = (
    "validate_pass197_squash_identity",
    "validate_pass197_ten_finding_repair",
    "validate_pass197_exact_execution_boundary",
    "validate_pass197_successor_binding",
    "validate_pass197_no_new_authority",
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
            raise RuntimeError(f"PASS197_REPAIR_SOURCE_DRIFT:{path}:{fragment}")


def pass197_membrane_source_evidence() -> Dict[str, Any]:
    if _git("merge-base", "--is-ancestor", ACCEPTED_MERGE, "HEAD") != "":
        raise RuntimeError("PASS197_ACCEPTED_MERGE_ANCESTRY_OUTPUT")
    if _git("merge-base", HISTORICAL_REVIEWED_HEAD, "HEAD") != HISTORICAL_BASE:
        raise RuntimeError("PASS197_SQUASH_LINEAGE_DRIFT")
    if _git("merge-base", "HEAD", FROZEN_I128) != FROZEN_I128:
        raise RuntimeError("PASS197_FROZEN_I128_LINEAGE_DRIFT")

    for path, expected in HISTORICAL_BLOBS.items():
        historical = _git("rev-parse", f"{ACCEPTED_MERGE}:{path}")
        if historical != expected:
            raise RuntimeError(f"PASS197_HISTORICAL_BLOB_DRIFT:{path}:{historical}")

    for path, expected in REPAIRED_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS197_REPAIRED_SOURCE_DRIFT:{path}")

    _require(
        EXACT_PATH,
        'HASH_AUTHORITY = "HHS_HASH72_KERNEL_AUTHORITY_UNAVAILABLE"',
        "Pass197 canonical Hash72 authority is unavailable",
        "rational object components must be exact integers",
    )
    _require(
        STATE_PATH,
        "MAX_SYNCHRONOUS_PARAMETER_STATES = 405",
        "must contain unique exact coordinates",
        "xy_symbol_values requires exact integers",
    )
    _require(
        RUNTIME_PATH,
        'REPAIR_SCHEMA = "HHS_PASS_197_I129_REPAIR_V1"',
        "inherited kernel audit evidence",
        "kernel_audit_receipt_hash72",
        "full_replay_verified = config.full_replay",
        "REPORT_INTEGRITY_VERIFICATION_FAILED",
        "self._root_locks.setdefault",
    )
    _require(
        API_PATH,
        "List[StrictInt]",
        "StrictBool",
        "VM81 authorized tick did not produce a Hash72 receipt",
    )
    _require(
        FRONTEND_PATH,
        "if (!value?.closed || !value?.report_hash72) return;",
        "lifecycle_state: 'ACTIVE'",
    )
    _require(
        REPAIR_TEST_PATH,
        "test_01_rational_object_components_are_strict_integers",
        "test_12_frontend_registers_only_verified_closed_projection",
    )

    successor = pass198_membrane_source_evidence()
    if successor.get("accepted_merge") != "122d21565fd7f3f9bbe9fb73ad2182d1d468ba5e":
        raise RuntimeError("PASS197_PASS198_SUCCESSOR_IDENTITY_DRIFT")

    return {
        "historical_base": HISTORICAL_BASE,
        "historical_reviewed_head": HISTORICAL_REVIEWED_HEAD,
        "accepted_merge": ACCEPTED_MERGE,
        "frozen_i128": FROZEN_I128,
        "historical_blobs": {str(path): value for path, value in HISTORICAL_BLOBS.items()},
        "repaired_blobs": {str(path): value for path, value in REPAIRED_BLOBS.items()},
        "review_finding_ids": list(REVIEW_FINDING_IDS),
        "production_totals": dict(PRODUCTION_TOTALS),
        "pass198_successor": successor,
    }


def validate_pass197_squash_identity() -> Dict[str, Any]:
    s = pass197_membrane_source_evidence()
    return {"ok": True, "pull_request": 133, "historical_base": s["historical_base"], "historical_reviewed_head": s["historical_reviewed_head"], "accepted_merge": s["accepted_merge"], "squash_aware": True}


def validate_pass197_ten_finding_repair() -> Dict[str, Any]:
    s = pass197_membrane_source_evidence()
    return {"ok": True, "repair_schema": "HHS_PASS_197_I129_REPAIR_V1", "review_finding_ids": s["review_finding_ids"], "finding_count": len(s["review_finding_ids"]), "historical_v1_preserved_as_provenance": True}


def validate_pass197_exact_execution_boundary() -> Dict[str, Any]:
    pass197_membrane_source_evidence()
    return {
        "ok": True,
        "pre_persistence_kernel_audit_required": True,
        "fail_closed_hash72_authority": True,
        "full_replay_required_for_closure": True,
        "strict_rational_object_components": True,
        "state_root_run_serialization": True,
        "persisted_report_integrity_status_gate": True,
        "maximum_synchronous_parameter_states": 405,
        "strict_exponent_ingress": True,
        "duplicate_coordinate_rejection": True,
        "closed_only_frontend_projection": True,
    }


def validate_pass197_successor_binding() -> Dict[str, Any]:
    successor = pass197_membrane_source_evidence()["pass198_successor"]
    return {"ok": True, "successor_pass": 198, "successor_accepted_merge": successor["accepted_merge"], "successor_preserved": True}


def validate_pass197_no_new_authority() -> Dict[str, Any]:
    pass197_membrane_source_evidence()
    return {
        "ok": True,
        "i129_new_candidate_authority": False,
        "i129_new_canonical_mutation_authority": False,
        "i129_new_persistence_authority": False,
        "i129_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "singleton_vm81_authority_remains_inherited": True,
    }


def pass197_surface_declaration() -> Dict[str, Any]:
    pass197_membrane_source_evidence()
    return {
        "surface_id": PASS197_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i129_pass197",
        "symbol": "validate_pass197_ten_finding_repair",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P197-ABTREE-VM81X64-EXACT-LOSSLESS-HYDRATION"],
        "witness_schemas": ["HHSExactPass197RepairedHydrationCalibrationWitnessV1", "HHSExactPass219InheritedPass197BindingV1"],
        "validators": [PASS197_BIND_SYMBOL, "validate_pass197_ten_finding_repair"],
        "guards": [
            "pass197_squash_identity",
            "pass197_ten_finding_repair",
            "pass197_kernel_audit_before_persistence",
            "pass197_fail_closed_hash72",
            "pass197_exact_ingress",
            "pass197_full_replay_closure",
            "pass197_state_root_serialization",
            "pass197_verified_status",
            "pass197_bounded_sync_envelope",
            "pass197_closed_only_projection",
            "pass197_pass198_successor",
        ],
        "rejection_codes": [
            "REJECT_PASS197_HISTORICAL_IDENTITY_DRIFT",
            "REJECT_PASS197_KERNEL_AUDIT_BYPASS",
            "REJECT_PASS197_HASH72_AUTHORITY_LOSS",
            "REJECT_PASS197_APPROXIMATE_INGRESS",
            "REJECT_PASS197_UNEXECUTED_REPLAY",
            "REJECT_PASS197_STATE_ROOT_CONCURRENCY",
            "REJECT_PASS197_REPORT_INTEGRITY_DRIFT",
            "REJECT_PASS197_UNBOUNDED_SYNC_WORKLOAD",
            "REJECT_PASS197_FRONTEND_PROJECTION_DRIFT",
            "REJECT_PASS197_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_PASS197_STATE_READ_ONLY_MEMBRANE",
        "boundedness_policy": "PASS_197_REPAIRED_CALIBRATION_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass197_membrane_manifest() -> Dict[str, Any]:
    s = pass197_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS197_NUMBER,
        "classification": PASS197_CLASSIFICATION,
        "census_classification": PASS197_CENSUS_CLASSIFICATION,
        "accepted_merge": s["accepted_merge"],
        "frozen_predecessor": s["frozen_i128"],
        "review_finding_ids": s["review_finding_ids"],
        "production_totals": s["production_totals"],
        "surface": pass197_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass197_membrane_preflight() -> Dict[str, Any]:
    declaration = pass197_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    return {
        "schema": "HHS_PASS219_I129_PASS197_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS197_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass197_squash_identity": validate_pass197_squash_identity,
    "validate_pass197_ten_finding_repair": validate_pass197_ten_finding_repair,
    "validate_pass197_exact_execution_boundary": validate_pass197_exact_execution_boundary,
    "validate_pass197_successor_binding": validate_pass197_successor_binding,
    "validate_pass197_no_new_authority": validate_pass197_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 197 I129 membrane operation: {operation}")
    return OPERATIONS[operation]()
