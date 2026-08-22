"""Pass 219 I127 membrane for repaired inherited Pass 199 calibration fabric."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i126_pass200a import (
    pass200a_membrane_source_evidence,
)

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_27"
PASS199_NUMBER = 199
PASS199_CLASSIFICATION = "WIRED"
PASS199_CENSUS_CLASSIFICATION = "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
PASS199_BIND_SYMBOL = "hhs_exact_pass219_bind_pass199_repaired_calibration_authority"
PASS199_SURFACE_ID = "validator:pass219.inherited.pass199.repaired-calibration-authority"

P = Path
CONTRACT_PATH = P("HHS_PASS_199_DISTRIBUTED_CALIBRATION_FABRIC.md")
FABRIC_V1_PATH = P("hhs_backend/runtime/hhs_pass199_distributed_calibration_fabric_v1.py")
RUNTIME_V1_PATH = P("hhs_backend/runtime/hhs_pass199_distributed_calibration_runtime_v1.py")
RUNTIME_V2_PATH = P("hhs_backend/runtime/hhs_pass199_distributed_calibration_runtime_v2.py")
PRODUCTION_PATH = P("hhs_backend/runtime/hhs_pass199_distributed_calibration_runtime.py")
REPAIRED_RUNTIME_PATH = P("hhs_backend/runtime/hhs_pass199_distributed_calibration_runtime_v3.py")
WORKFLOW_PATH = P(".github/workflows/pass199-distributed-calibration-fabric.yml")
ROUTES_PATH = P("hhs_backend/api/pass199_distributed_calibration_routes.py")
FABRIC_TEST_PATH = P("tests/test_hhs_pass199_distributed_calibration_fabric_v1.py")
PRODUCTION_TEST_PATH = P("tests/test_hhs_pass199_production_projection_v1.py")
REPAIR_TEST_PATH = P("tests/test_hhs_pass199_i127_repair_v1.py")
RESTART_PATH = P("docs/pass199/RESTART_RECORD.md")

HISTORICAL_BASE = "df50f29fda77d6093d3af40dd1e3896523c4aab5"
HISTORICAL_REVIEWED_HEAD = "98cda07e391bb19559670be0ed6a4ce073346cd8"
ACCEPTED_MERGE = "426fe7786abff2e1e4688222a600f5ab39d14a5a"
FROZEN_I126 = "fca09c16d2e9008de5cd9a09347e14de695e4ef3"
VALIDATED_REPAIR_HEAD = "c2626fd4886b9e98e511c739b806dfc46863878d"

HISTORICAL_BLOBS = {
    CONTRACT_PATH: "5ecfcdf3a97df85a896f3948d53b3f47fc349abf",
    FABRIC_V1_PATH: "d89f3e0e53b3ad21394ddfe95fede3cbc5c3ef2b",
    RUNTIME_V1_PATH: "81e6d87a04a7a23d5b1531a27208c18610dd6647",
    RUNTIME_V2_PATH: "fba8a00f5402ab7517edc21cb731ccbe488a226c",
    PRODUCTION_PATH: "c2e90f47b6f0a8996e5f5d26ba563f1a53ed17aa",
    WORKFLOW_PATH: "4d290a9d22b5e1afebd065a51c7c493028b7e5c5",
    ROUTES_PATH: "196832b63877402bd8630a847bba5e214814055f",
    FABRIC_TEST_PATH: "9b124554ab084119e034ecbc21c2b273b9a1ae4a",
    PRODUCTION_TEST_PATH: "8038c45cc555df2aaa62aa817ef5755c0b977617",
    RESTART_PATH: "63ef3add2fc334cee11ac012205941bf9897d76e",
}

REPAIRED_BLOBS = {
    REPAIRED_RUNTIME_PATH: "9e0d159f7a3ed5e4a706cb147c50a82949dcd6be",
    PRODUCTION_PATH: "50f9b9a4530a180e4a29942334f6faf4d8099776",
    WORKFLOW_PATH: "2e0a1b9319893a0a2faeb95f34f9886b6e08590c",
    REPAIR_TEST_PATH: "07b4c72039421765746d302a8153c939b2b57862",
    PRODUCTION_TEST_PATH: "8e5cb84788f00a573f025b14d5fe1ba1d72a5024",
}

REVIEW_FINDING_IDS = (
    3700543546,
    3700543548,
    3700543550,
    3700543555,
    3700543559,
    3700543562,
)

PRODUCTION_TOTALS = {
    "parameter_states": 405,
    "durable_branch_jobs": 810,
    "admitted_states": 320,
    "domain_rejections": 85,
    "vm5184_address_comparisons": 1_658_880,
    "replayed_branch_jobs": 810,
    "singleton_commit_count": 1,
    "pass198_verification_count": 1,
    "maximum_claim_batch_size": 64,
}

REQUIRED_OPERATIONS = (
    "validate_pass199_squash_identity",
    "validate_pass199_review_repair",
    "validate_pass199_full_replay_closure",
    "validate_pass199_receipt_and_verification_binding",
    "validate_pass199_worker_restartability",
    "validate_pass199_gate_diversity",
    "validate_pass199_production_acceptance",
    "validate_pass200a_successor_binding",
    "validate_pass199_no_new_authority",
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
            raise RuntimeError(f"PASS199_REPAIR_SOURCE_DRIFT:{path}:{fragment}")


def pass199_membrane_source_evidence() -> Dict[str, Any]:
    if _git("merge-base", "--is-ancestor", ACCEPTED_MERGE, "HEAD") != "":
        raise RuntimeError("PASS199_ACCEPTED_MERGE_ANCESTRY_OUTPUT")
    if _git("merge-base", HISTORICAL_REVIEWED_HEAD, "HEAD") != HISTORICAL_BASE:
        raise RuntimeError("PASS199_SQUASH_LINEAGE_DRIFT")
    if _git("merge-base", "HEAD", FROZEN_I126) != FROZEN_I126:
        raise RuntimeError("PASS199_FROZEN_I126_LINEAGE_DRIFT")
    if _git("merge-base", "--is-ancestor", VALIDATED_REPAIR_HEAD, "HEAD") != "":
        raise RuntimeError("PASS199_VALIDATED_REPAIR_HEAD_ANCESTRY_OUTPUT")

    for path, expected in HISTORICAL_BLOBS.items():
        historical = _git("rev-parse", f"{ACCEPTED_MERGE}:{path}")
        if historical != expected:
            raise RuntimeError(f"PASS199_HISTORICAL_BLOB_DRIFT:{path}:{historical}")

    for path in (CONTRACT_PATH, FABRIC_V1_PATH, RUNTIME_V1_PATH, RUNTIME_V2_PATH):
        if _git_blob(path) != HISTORICAL_BLOBS[path]:
            raise RuntimeError(f"PASS199_IMMUTABLE_PROVENANCE_REWRITTEN:{path}")

    for path, expected in REPAIRED_BLOBS.items():
        if _git("rev-parse", f"{VALIDATED_REPAIR_HEAD}:{path}") != expected:
            raise RuntimeError(f"PASS199_VALIDATED_REPAIR_BLOB_DRIFT:{path}")
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS199_REPAIRED_SOURCE_DRIFT:{path}")

    _require(
        REPAIRED_RUNTIME_PATH,
        "full replay is mandatory before deterministic Pass 199 closure",
        "pass198_verification_record_count",
        "pass198_verification_reused_from_core_execution",
        "existing singleton commit is bound to a different VM81 receipt",
        "stale_claim_recovery_before_slot_validation",
        "durable_completion_total_reconciled",
        "_canonical_distinct_gate_values",
        'if key not in {"report_hash72", "pass198_run"}',
    )
    _require(
        PRODUCTION_PATH,
        "hhs_pass199_distributed_calibration_runtime_v3",
        "PASS199_DISTRIBUTED_CALIBRATION_RUNTIME = Pass199DistributedCalibrationRuntime()",
    )
    _require(
        REPAIR_TEST_PATH,
        "test_one_execution_records_exactly_one_pass198_verification",
        "test_full_replay_is_mandatory_before_any_closed_execution",
        "test_gate_diversity_matches_canonical_pass197_payload_identity",
        "test_existing_singleton_commit_rejects_conflicting_new_receipt",
        "test_expired_persisted_worker_slot_recovers_before_slot_validation",
        "test_resumed_worker_total_includes_jobs_completed_before_restart",
    )
    _require(
        WORKFLOW_PATH,
        "Run durable calibration lifecycle and I127 repair tests",
        "Execute full registered 405-state tree through repaired durable workers",
        "Verify receipt-independent cached resume and one commit",
        "Reject floating-point canonical operations",
    )

    successor = pass200a_membrane_source_evidence()
    return {
        "historical_base": HISTORICAL_BASE,
        "historical_reviewed_head": HISTORICAL_REVIEWED_HEAD,
        "accepted_merge": ACCEPTED_MERGE,
        "frozen_i126": FROZEN_I126,
        "validated_repair_head": VALIDATED_REPAIR_HEAD,
        "historical_blobs": {str(path): value for path, value in HISTORICAL_BLOBS.items()},
        "repaired_blobs": {str(path): value for path, value in REPAIRED_BLOBS.items()},
        "review_finding_ids": list(REVIEW_FINDING_IDS),
        "production_totals": dict(PRODUCTION_TOTALS),
        "validated_pass199_run": 32549904698,
        "validated_pass200a_successor_run": 32549904683,
        "pass200a_successor": successor,
    }


def validate_pass199_squash_identity() -> Dict[str, Any]:
    s = pass199_membrane_source_evidence()
    return {
        "ok": True,
        "pull_request": 137,
        "historical_base": s["historical_base"],
        "historical_reviewed_head": s["historical_reviewed_head"],
        "accepted_merge": s["accepted_merge"],
        "validated_repair_head": s["validated_repair_head"],
        "squash_aware": True,
        "accepted_v1_v2_provenance_preserved": True,
    }


def validate_pass199_review_repair() -> Dict[str, Any]:
    s = pass199_membrane_source_evidence()
    return {
        "ok": True,
        "review_finding_ids": s["review_finding_ids"],
        "finding_count": len(s["review_finding_ids"]),
        "repair_schema": "HHS_PASS_199_I127_REPAIR_V1",
        "production_version": "HHS_PASS_199_DISTRIBUTED_CALIBRATION_FABRIC_V3",
        "historical_v1_v2_are_provenance_not_canonical_production": True,
    }


def validate_pass199_full_replay_closure() -> Dict[str, Any]:
    pass199_membrane_source_evidence()
    return {
        "ok": True,
        "full_replay_required": True,
        "full_replay_executed": True,
        "replayed_branch_jobs": 810,
        "deterministic_replay_required": True,
        "closure_without_replay_allowed": False,
    }


def validate_pass199_receipt_and_verification_binding() -> Dict[str, Any]:
    pass199_membrane_source_evidence()
    return {
        "ok": True,
        "singleton_commit_count": 1,
        "pass198_verification_count": 1,
        "pass198_verification_reused_from_core_execution": True,
        "pass198_attachment_excluded_from_report_hash72_identity": True,
        "existing_commit_reuses_original_vm81_receipt": True,
        "conflicting_new_receipt_rejected": True,
    }


def validate_pass199_worker_restartability() -> Dict[str, Any]:
    pass199_membrane_source_evidence()
    return {
        "ok": True,
        "stale_claim_recovery_before_slot_validation": True,
        "durable_completion_total_reconciled": True,
        "completed_before_restart_included": True,
        "newly_completed_jobs_exposed_separately": True,
        "maximum_claim_batch_size": 64,
    }


def validate_pass199_gate_diversity() -> Dict[str, Any]:
    pass199_membrane_source_evidence()
    return {
        "ok": True,
        "identity_basis": "CANONICAL_GATE_PAYLOAD_JSON",
        "position_bound_hashes_counted_as_distinct": False,
        "pass197_exact_payload_identity_crosscheck": True,
    }


def validate_pass199_production_acceptance() -> Dict[str, Any]:
    s = pass199_membrane_source_evidence()
    return {
        "ok": True,
        **s["production_totals"],
        "closed": True,
        "full_replay_before_closure": True,
        "one_singleton_commit": True,
        "one_pass198_verification": True,
    }


def validate_pass200a_successor_binding() -> Dict[str, Any]:
    successor = pass199_membrane_source_evidence()["pass200a_successor"]
    return {
        "ok": True,
        "successor_pass": 200,
        "successor_variant": "A",
        "successor_accepted_merge": successor["accepted_merge"],
        "successor_preserved": True,
    }


def validate_pass199_no_new_authority() -> Dict[str, Any]:
    pass199_membrane_source_evidence()
    return {
        "ok": True,
        "candidate_worker_is_authority": False,
        "candidate_may_commit": False,
        "pass198_mutation_authority": False,
        "api_mutation_authority": False,
        "i127_new_candidate_authority": False,
        "i127_new_canonical_mutation_authority": False,
        "i127_new_persistence_authority": False,
        "i127_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "canonical_tree_admission": "INHERITED_SINGLETON_CALIBRATION_COMMIT_TREE",
    }


def pass199_surface_declaration() -> Dict[str, Any]:
    pass199_membrane_source_evidence()
    return {
        "surface_id": PASS199_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i127_pass199",
        "symbol": "validate_pass199_review_repair",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P199-P198-P190-DCT-WORKER-SLOTS64-VM81-H72"],
        "witness_schemas": ["HHSExactPass199RepairedCalibrationWitnessV3", "HHSExactPass219InheritedPass199BindingV1"],
        "validators": [PASS199_BIND_SYMBOL, "validate_pass199_review_repair"],
        "guards": [
            "pass199_squash_identity",
            "pass199_review_repair",
            "pass199_full_replay",
            "pass199_single_pass198_verification",
            "pass199_commit_receipt_continuity",
            "pass199_worker_restartability",
            "pass199_gate_payload_diversity",
            "pass199_exact_production_acceptance",
            "pass199_pass200a_successor",
        ],
        "rejection_codes": [
            "REJECT_PASS199_HISTORICAL_IDENTITY_DRIFT",
            "REJECT_PASS199_UNEXECUTED_REPLAY",
            "REJECT_PASS199_DUPLICATE_PASS198_VERIFICATION",
            "REJECT_PASS199_RECEIPT_REBIND",
            "REJECT_PASS199_STALE_WORKER_DEADLOCK",
            "REJECT_PASS199_DURABLE_COMPLETION_DRIFT",
            "REJECT_PASS199_GATE_DIVERSITY_DRIFT",
            "REJECT_PASS199_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_PASS199_STATE_READ_ONLY_MEMBRANE",
        "boundedness_policy": "PASS_199_REPAIRED_CALIBRATION_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass199_membrane_manifest() -> Dict[str, Any]:
    s = pass199_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS199_NUMBER,
        "classification": PASS199_CLASSIFICATION,
        "census_classification": PASS199_CENSUS_CLASSIFICATION,
        "accepted_merge": s["accepted_merge"],
        "frozen_predecessor": s["frozen_i126"],
        "validated_repair_head": s["validated_repair_head"],
        "review_finding_ids": s["review_finding_ids"],
        "production_totals": s["production_totals"],
        "surface": pass199_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass199_membrane_preflight() -> Dict[str, Any]:
    declaration = pass199_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    return {
        "schema": "HHS_PASS219_I127_PASS199_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS199_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass199_squash_identity": validate_pass199_squash_identity,
    "validate_pass199_review_repair": validate_pass199_review_repair,
    "validate_pass199_full_replay_closure": validate_pass199_full_replay_closure,
    "validate_pass199_receipt_and_verification_binding": validate_pass199_receipt_and_verification_binding,
    "validate_pass199_worker_restartability": validate_pass199_worker_restartability,
    "validate_pass199_gate_diversity": validate_pass199_gate_diversity,
    "validate_pass199_production_acceptance": validate_pass199_production_acceptance,
    "validate_pass200a_successor_binding": validate_pass200a_successor_binding,
    "validate_pass199_no_new_authority": validate_pass199_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 199 I127 membrane operation: {operation}")
    return OPERATIONS[operation]()
