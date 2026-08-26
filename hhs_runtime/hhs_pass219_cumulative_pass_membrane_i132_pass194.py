"""Pass 219 I132 membrane for inherited Pass 194 storage/training authority."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i131_pass195 import pass195_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_32"
PASS194_NUMBER = 194
PASS194_CLASSIFICATION = "WIRED"
PASS194_CENSUS_CLASSIFICATION = "MISSING_IMPLEMENTATION_AND_MEMBRANE_EXPOSURE"
PASS194_BIND_SYMBOL = "hhs_exact_pass219_bind_pass194_storage_training_snapshot_authority"
PASS194_SURFACE_ID = "validator:pass219.inherited.pass194.storage-training-snapshot-authority"

P = Path
CONTRACT_PATH = P("docs/pass194/HHS_PASS_194_USER_MULTIMODAL_FILE_FOLDER_HYDRATION_SNAPSHOT_SQL_CONTEXT_VECTOR_STORE_AGI_TRAINING_AUTHORITY.md")
RUNTIME_PATH = P("hhs_backend/runtime/hhs_pass194_multimodal_storage_training_v1.py")
API_PATH = P("hhs_backend/api/pass194_storage_training_routes.py")
VISUAL_SERVER_PATH = P("hhs_backend/visual_server.py")
RUNTIME_TEST_PATH = P("tests/test_hhs_pass194_multimodal_storage_training_v1.py")
API_TEST_PATH = P("tests/test_hhs_pass194_storage_training_routes.py")
FOCUSED_WORKFLOW_PATH = P(".github/workflows/pass194-i132-storage-training-validation.yml")

CONTRACT_AUTHORIZATION_COMMIT = "714f3f3c5c77eab9714be421811ce4fd650a8e99"
CONTRACT_BASELINE_COMMIT = "31aad2b8281c9a68c5f810948dac630dd5a387e0"
FROZEN_I131 = "b8202201bc92470afdd15d701d16ea102aeb3aab"
SOURCE_BLOBS = {
    CONTRACT_PATH: "f437461b4cb74b40ba8444c48319ad8f906359cf",
    RUNTIME_PATH: "37c7a7dd3ad246674111398c50ee94e580e72d58",
    API_PATH: "b414b77d2bf35e5fef3056e6e91da3d7146fc278",
    VISUAL_SERVER_PATH: "998852398931f2e3af2da57ec455211f938b2661",
    RUNTIME_TEST_PATH: "ee7044605fde90f5bd40813de18cdf5d30b6d560",
    API_TEST_PATH: "7954ea3d45184088ef7f4406a018316075388054",
    FOCUSED_WORKFLOW_PATH: "f5cb94c8ad9f92741dab81ec2b8cdf1661f6c979",
}
REQUIRED_OPERATIONS = (
    "validate_pass194_contract_and_lineage",
    "validate_pass194_content_and_sql_boundary",
    "validate_pass194_consent_dataset_boundary",
    "validate_pass194_vector_snapshot_boundary",
    "validate_pass194_training_checkpoint_boundary",
    "validate_pass194_revocation_replay_boundary",
    "validate_pass194_successor_binding",
    "validate_pass194_no_new_authority",
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
            raise RuntimeError(f"PASS194_SOURCE_DRIFT:{path}:{fragment}")


def pass194_membrane_source_evidence() -> Dict[str, Any]:
    if _git("merge-base", "--is-ancestor", CONTRACT_AUTHORIZATION_COMMIT, "HEAD") != "":
        raise RuntimeError("PASS194_AUTHORIZATION_ANCESTRY_OUTPUT")
    if _git("merge-base", "HEAD", FROZEN_I131) != FROZEN_I131:
        raise RuntimeError("PASS194_FROZEN_I131_LINEAGE_DRIFT")
    historical_contract = _git("rev-parse", f"{CONTRACT_AUTHORIZATION_COMMIT}:{CONTRACT_PATH}")
    if historical_contract != SOURCE_BLOBS[CONTRACT_PATH]:
        raise RuntimeError("PASS194_HISTORICAL_CONTRACT_DRIFT")
    for path, expected in SOURCE_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS194_IMPLEMENTED_SOURCE_DRIFT:{path}")

    _require(
        RUNTIME_PATH,
        "PRAGMA journal_mode=WAL",
        "PRAGMA synchronous=FULL",
        "default_training_allowed\": False",
        "HHS_P194_TRAINING_CONSENT_DENIED",
        "PersistentEncryptedVectorStore",
        "vector_store_is_source_authority\": False",
        "snapshot_is_training_authorization\": False",
        "training_provider_is_vm81_authority\": False",
        "HHS_P194_VM81_AUTHORITY_RECEIPT_REUSED",
        "deterministic_replay\": True",
    )
    _require(
        API_PATH,
        "/api/runtime/storage-training",
        "MAX_UPLOAD_BYTES",
        "Pass194Runtime",
        "authority_execution",
    )
    _require(
        VISUAL_SERVER_PATH,
        "pass194_storage_training_router",
        "/api/runtime/storage-training/status",
        "pass194_storage_training_api",
    )
    _require(
        RUNTIME_TEST_PATH,
        "SNAPSHOT_BYTES",
        "test_default_deny_requires_consent_and_fresh_snapshot",
        "test_dataset_training_checkpoint_and_delete_propagation",
        "test_restart_and_replay_validate_receipt_snapshot_dataset_identity",
    )

    successor = pass195_membrane_source_evidence()
    if successor.get("accepted_primary_merge") != "8bcc0921555ecface13113c8a2620415ddb3fdf1":
        raise RuntimeError("PASS194_PASS195_SUCCESSOR_IDENTITY_DRIFT")
    return {
        "contract_authorization_commit": CONTRACT_AUTHORIZATION_COMMIT,
        "contract_baseline_commit": CONTRACT_BASELINE_COMMIT,
        "frozen_i131": FROZEN_I131,
        "source_blobs": {str(path): value for path, value in SOURCE_BLOBS.items()},
        "pass195_successor": successor,
    }


def validate_pass194_contract_and_lineage() -> Dict[str, Any]:
    evidence = pass194_membrane_source_evidence()
    return {
        "ok": True,
        "contract_authorization_commit": evidence["contract_authorization_commit"],
        "contract_baseline_commit": evidence["contract_baseline_commit"],
        "frozen_i131": evidence["frozen_i131"],
        "historical_contract_preserved": True,
        "classification": PASS194_CENSUS_CLASSIFICATION,
    }


def validate_pass194_content_and_sql_boundary() -> Dict[str, Any]:
    pass194_membrane_source_evidence()
    return {
        "ok": True,
        "content_addressed_blob_store": True,
        "blob_identity_immutable": True,
        "versioned_sql_context_graph": True,
        "sqlite_wal": True,
        "sqlite_synchronous_full": True,
        "metadata_mutation_requires_inherited_vm81_receipt": True,
    }


def validate_pass194_consent_dataset_boundary() -> Dict[str, Any]:
    pass194_membrane_source_evidence()
    return {
        "ok": True,
        "training_default_deny": True,
        "sharing_default_deny": True,
        "public_default_deny": True,
        "training_requires_license": True,
        "dataset_requires_snapshot_consent_closure": True,
        "consent_drift_requires_new_snapshot": True,
    }


def validate_pass194_vector_snapshot_boundary() -> Dict[str, Any]:
    pass194_membrane_source_evidence()
    return {
        "ok": True,
        "encrypted_hash216_vector_projection": True,
        "vector_frame_uses_inherited_vmrc_snapshot_bytes": True,
        "vector_store_is_source_authority": False,
        "vector_store_is_consent_authority": False,
        "vector_store_is_vm81_authority": False,
        "hydration_snapshot_immutable": True,
        "snapshot_is_training_authorization": False,
    }


def validate_pass194_training_checkpoint_boundary() -> Dict[str, Any]:
    pass194_membrane_source_evidence()
    return {
        "ok": True,
        "training_run_kinds_bounded": True,
        "dataset_lineage_bound": True,
        "checkpoint_artifact_sha256_bound": True,
        "training_provider_is_vm81_authority": False,
        "checkpoint_is_vm81_authority": False,
    }


def validate_pass194_revocation_replay_boundary() -> Dict[str, Any]:
    pass194_membrane_source_evidence()
    return {
        "ok": True,
        "file_delete_tombstone": True,
        "dataset_revocation_propagates": True,
        "training_run_revocation_propagates": True,
        "orphan_blob_removal": True,
        "receipt_chain_replay": True,
        "snapshot_identity_replay": True,
        "dataset_identity_replay": True,
    }


def validate_pass194_successor_binding() -> Dict[str, Any]:
    successor = pass194_membrane_source_evidence()["pass195_successor"]
    return {
        "ok": True,
        "successor_pass": 195,
        "successor_accepted_merge": successor["accepted_primary_merge"],
        "successor_preserved": True,
    }


def validate_pass194_no_new_authority() -> Dict[str, Any]:
    pass194_membrane_source_evidence()
    return {
        "ok": True,
        "i132_new_candidate_authority": False,
        "i132_new_canonical_mutation_authority": False,
        "i132_new_persistence_authority": False,
        "i132_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "vector_store_is_source_authority": False,
        "vector_store_is_consent_authority": False,
        "browser_is_authority": False,
        "training_provider_is_vm81_authority": False,
        "singleton_vm81_authority_remains_inherited": True,
    }


def pass194_surface_declaration() -> Dict[str, Any]:
    pass194_membrane_source_evidence()
    return {
        "surface_id": PASS194_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i132_pass194",
        "symbol": "validate_pass194_contract_and_lineage",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P194-UMFFHS-SQLCG-EVS-AGITC-VM81-H72-H216"],
        "witness_schemas": [
            "HHSExactPass194StorageTrainingSnapshotAuthorityWitnessV1",
            "HHSExactPass219InheritedPass194BindingV1",
        ],
        "validators": [PASS194_BIND_SYMBOL, "validate_pass194_contract_and_lineage"],
        "guards": [
            "pass194_historical_contract_identity",
            "pass194_immutable_blob_identity",
            "pass194_sql_graph_authority",
            "pass194_default_deny_consent",
            "pass194_dataset_consent_license_closure",
            "pass194_vector_non_authority",
            "pass194_snapshot_identity",
            "pass194_training_checkpoint_lineage",
            "pass194_revocation_replay",
            "pass194_pass195_successor",
        ],
        "rejection_codes": [
            "REJECT_PASS194_CONTRACT_DRIFT",
            "REJECT_PASS194_SOURCE_IDENTITY_DRIFT",
            "REJECT_PASS194_VM81_RECEIPT_BYPASS",
            "REJECT_PASS194_CONSENT_BYPASS",
            "REJECT_PASS194_DATASET_CLOSURE_BYPASS",
            "REJECT_PASS194_VECTOR_AUTHORITY_ESCALATION",
            "REJECT_PASS194_SNAPSHOT_DRIFT",
            "REJECT_PASS194_TRAINING_LINEAGE_DRIFT",
            "REJECT_PASS194_REVOCATION_DRIFT",
            "REJECT_PASS194_AUTHORITY_ESCALATION",
        ],
        "mutation_policy": "INHERITED_VM81_AUTHORIZED_METADATA_MUTATIONS_ONLY",
        "persistence_policy": "PASS194_SQL_BLOB_VECTOR_SNAPSHOT_DATA_ONLY_NO_NEW_VM81_AUTHORITY",
        "boundedness_policy": "PASS_194_STORAGE_TRAINING_IMPLEMENTATION_AND_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass194_membrane_manifest() -> Dict[str, Any]:
    evidence = pass194_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS194_NUMBER,
        "classification": PASS194_CLASSIFICATION,
        "census_classification": PASS194_CENSUS_CLASSIFICATION,
        "contract_authorization_commit": evidence["contract_authorization_commit"],
        "frozen_predecessor": evidence["frozen_i131"],
        "surface": pass194_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass194_membrane_preflight() -> Dict[str, Any]:
    declaration = pass194_surface_declaration()
    rows = [
        execute_surface_preflight(declaration, operation=operation)
        for operation in REQUIRED_OPERATIONS
    ]
    return {
        "schema": "HHS_PASS219_I132_PASS194_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS194_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass194_contract_and_lineage": validate_pass194_contract_and_lineage,
    "validate_pass194_content_and_sql_boundary": validate_pass194_content_and_sql_boundary,
    "validate_pass194_consent_dataset_boundary": validate_pass194_consent_dataset_boundary,
    "validate_pass194_vector_snapshot_boundary": validate_pass194_vector_snapshot_boundary,
    "validate_pass194_training_checkpoint_boundary": validate_pass194_training_checkpoint_boundary,
    "validate_pass194_revocation_replay_boundary": validate_pass194_revocation_replay_boundary,
    "validate_pass194_successor_binding": validate_pass194_successor_binding,
    "validate_pass194_no_new_authority": validate_pass194_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 194 I132 membrane operation: {operation}")
    return OPERATIONS[operation]()
