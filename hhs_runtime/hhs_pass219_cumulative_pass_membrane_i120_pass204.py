"""Pass 219 I120 inherited Pass 204 open-cloud mainframe membrane.

This layer exposes the accepted Pass 204 universal executable-declaration and
safe open-cloud boundary without redefining its execution, durable session/job
persistence, sandbox policy, snapshot, recall, or inherited VM81 authority.
I120 is a read-only evidence/ABI binding over the already-merged Pass 204
production implementation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i119_pass205 import pass205_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_20"
PASS204_NUMBER = 204
PASS204_CLASSIFICATION = "WIRED"
PASS204_CENSUS_CLASSIFICATION = "MISSING_MEMBRANE_EXPOSURE"
PASS204_BIND_SYMBOL = "hhs_exact_pass219_bind_pass204_open_cloud_mainframe"
PASS204_SURFACE_ID = "validator:pass219.inherited.pass204.open-cloud-mainframe"

PASS204_CONTRACT_PATH = Path("HHS_PASS_204_UNIVERSAL_EXECUTABLE_DECLARATIONS_OPEN_CLOUD_COMPUTER.md")
PASS204_RESTART_PATH = Path("docs/pass204/RESTART_RECORD.md")
PASS204_RECEIPT_PATH = Path("evidence/pass204/PASS204_OPEN_CLOUD_VALIDATION_RECEIPT.json")
PASS203_RECEIPT_PATH = Path("evidence/pass204/PASS203_INHERITED_VALIDATION_RECEIPT.json")
PASS204_RUNTIME_V1_PATH = Path("hhs_backend/runtime/hhs_pass204_open_cloud_mainframe_v1.py")
PASS204_RUNTIME_PATH = Path("hhs_backend/runtime/hhs_pass204_open_cloud_mainframe.py")
PASS204_WORKER_V1_PATH = Path("hhs_backend/runtime/hhs_pass204_sandbox_worker_v1.py")
PASS204_WORKER_PATH = Path("hhs_backend/runtime/hhs_pass204_sandbox_worker.py")
PASS204_NATIVE_PATH = Path("hhs_backend/runtime/hhs_pass204_native_abi_executor_v1.py")
PASS204_ROUTES_PATH = Path("hhs_backend/api/pass204_open_cloud_routes.py")
PASS204_TEST_PATH = Path("tests/test_hhs_pass204_open_cloud_mainframe_v1.py")
PASS204_WORKFLOW_PATH = Path(".github/workflows/pass204-open-cloud-mainframe.yml")

BASE_COMMIT = "fe5cb897ce5ca97a0c6c7439f26743dcefb83d4f"
VALIDATED_HEAD = "6b26fbf6f4b767d4eb5f2a790c552b03fd39d352"
MERGE_COMMIT = "deb34287ee155d9538005bbbfd6519794d999ac9"
FINAL_VALIDATION_WORKFLOW_RUN = 30810922316
FINAL_VALIDATION_ARTIFACT_ID = 8854791111
FINAL_VALIDATION_ARTIFACT_DIGEST = "sha256:1ab7b1307fd9bff930d8f11405a9e2d1cddeb7772a55a4fa80fce55d65669150"
VALIDATION_RECEIPT_BLOB = "2b2a3baa87ea41577b4b4397da03b1b790c5cfae"
STATUS_HASH72 = "LH0bm1Oh2BoGuenUhhwB/KIc!cUG/3XON6wm+Y)pcyuZXv8x0Y2LKQyubd8g4JD)FAtnxz)0"
SNAPSHOT_ROOT = "JCR<sW/pI9rz*w5svIUaOIs/1(Rkfo050NYBfXRSDhY+i/maOouphah7vgrK(UuIXOv)v-hm"
CORE_NATIVE_RECEIPT_HASH72 = "KLW)NAj5T9kF6JT6ZA0kok!uVFLe!*gAYYK(><uwvpf52hlwgCXoTKkSuZHNG8Iy364Tw3VY"
PROJECT_NATIVE_RECEIPT_HASH72 = "Np78ojOERbOo2pB0+Bvp47*KhGqdS1EtpcSX(Kuex(Uuf<!s2wn!<wtxqNWCYQg)lFpKlJRi"

EXPECTED_BLOBS = {
    PASS204_RECEIPT_PATH: VALIDATION_RECEIPT_BLOB,
    PASS204_RUNTIME_V1_PATH: "409e30b3abe4d53f319d0ba83bdc60cc44946198",
    PASS204_RUNTIME_PATH: "2dcaed59d5ce457650987f9dc9aeb89ac6cfe60b",
    PASS204_WORKER_V1_PATH: "18ba30c2cd9c68713b18b847d7fd8a15d1fa0af2",
    PASS204_WORKER_PATH: "1a95bc76a3bcd6219b22f483badcb073bcbf44a6",
    PASS204_NATIVE_PATH: "963ba904e04484a835743295fc935443ec0a0e27",
    PASS204_ROUTES_PATH: "f950f86c88ac56bbf2d94addb339a50cd3ea4489",
    PASS204_TEST_PATH: "807be51dd9be3c3bbb80c3ca06f74ed8081cc584",
    PASS204_WORKFLOW_PATH: "174ff0397529c13ad13f591b6bc2243bb2ce64cb",
}

REQUIRED_OPERATIONS = (
    "validate_pass204_production_identity",
    "validate_pass204_declaration_closure",
    "validate_pass204_fixed_sandbox_policy",
    "validate_pass204_immutable_history_boundary",
    "validate_pass204_persistence_and_recall",
    "validate_pass204_native_execution_boundary",
    "validate_pass203_inherited_replay",
    "validate_pass205_successor_binding",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _load(path: Path) -> Dict[str, Any]:
    value = json.loads(_text(path))
    if not isinstance(value, dict):
        raise RuntimeError("PASS204_OBJECT_REQUIRED:" + str(path))
    return value


def _git_blob(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def pass204_membrane_source_evidence() -> Dict[str, Any]:
    receipt = _load(PASS204_RECEIPT_PATH)
    inherited = _load(PASS203_RECEIPT_PATH)
    contract = _text(PASS204_CONTRACT_PATH)
    restart = _text(PASS204_RESTART_PATH)
    runtime_v1 = _text(PASS204_RUNTIME_V1_PATH)
    runtime = _text(PASS204_RUNTIME_PATH)
    worker = _text(PASS204_WORKER_PATH)
    native = _text(PASS204_NATIVE_PATH)
    routes = _text(PASS204_ROUTES_PATH)
    successor = pass205_membrane_source_evidence()

    for path, expected in EXPECTED_BLOBS.items():
        actual = _git_blob(path)
        if actual != expected:
            raise RuntimeError(f"PASS204_FROZEN_BLOB_DRIFT:{path}:{actual}")

    if receipt.get("schema") != "HHS_PASS_204_OPEN_CLOUD_VALIDATION_RECEIPT_V1":
        raise RuntimeError("PASS204_RECEIPT_SCHEMA_DRIFT")
    if receipt.get("classification") != "HHS_PASS_204_UNIVERSAL_EXECUTABLE_DECLARATIONS_OPEN_CLOUD_VERIFIED":
        raise RuntimeError("PASS204_RECEIPT_CLASSIFICATION_DRIFT")
    if receipt.get("contract") != "HHS-P204-UNIVERSAL-EXECUTABLE-DECLARATIONS-OPEN-CLOUD-SANDBOX-VM81-H72-H216":
        raise RuntimeError("PASS204_CONTRACT_IDENTITY_DRIFT")
    if receipt.get("closed") is not True or receipt.get("recall_verified") is not True:
        raise RuntimeError("PASS204_CLOSURE_DRIFT")

    summary = receipt.get("summary") or {}
    expected_summary = {
        "catalog_count": 2939,
        "hydrated_count": 2939,
        "callable_count": 2939,
        "binding_gap_count": 0,
        "public_route_count": 470,
        "openapi_path_count": 441,
        "core_native_execution_status": "COMPLETED",
        "project_native_execution_status": "ACCEPTED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise RuntimeError("PASS204_SUMMARY_DRIFT:" + key)

    policy = receipt.get("sandbox_policy") or {}
    required_policy = {
        "remote_users_automatically_sandboxed": True,
        "ephemeral_compute": True,
        "persistent_capabilities": False,
        "direct_host_kernel_access": False,
        "caller_adjustable_internal_policy": False,
        "internal_behavior_parameters_exposed": False,
        "repo_source_read_only": True,
        "sandbox_writes_discarded_after_snapshot": True,
        "session_recall_restores_capabilities": False,
    }
    for key, expected in required_policy.items():
        if policy.get(key) is not expected:
            raise RuntimeError("PASS204_SANDBOX_POLICY_DRIFT:" + key)
    if policy.get("durable_outputs") != ["artifacts", "jobs", "receipts", "layered_snapshots"]:
        raise RuntimeError("PASS204_DURABLE_OUTPUT_SET_DRIFT")

    kernel = receipt.get("kernel_constraint_manifest") or {}
    if kernel.get("admitted_history_mutable") is not False:
        raise RuntimeError("PASS204_ADMITTED_HISTORY_MUTABILITY_DRIFT")
    if kernel.get("constraint_authority_mutable") is not False:
        raise RuntimeError("PASS204_CONSTRAINT_AUTHORITY_MUTABILITY_DRIFT")
    if kernel.get("caller_adjustable_internal_parameters") is not False:
        raise RuntimeError("PASS204_INTERNAL_PARAMETER_AUTHORITY_DRIFT")

    host = receipt.get("host_trust_boundary") or {}
    if host.get("weakest_external_operational_layer") != "CLOUD_SERVER_HARDWARE_ENVIRONMENT":
        raise RuntimeError("PASS204_HOST_TRUST_BOUNDARY_DRIFT")
    if host.get("host_fault_can_rewrite_admitted_hash_history") is not False:
        raise RuntimeError("PASS204_HOST_HISTORY_REWRITE_DRIFT")
    if host.get("host_fault_can_mutate_constraint_contract") is not False:
        raise RuntimeError("PASS204_HOST_CONSTRAINT_MUTATION_DRIFT")
    if host.get("capability_state_recovered") is not False:
        raise RuntimeError("PASS204_HOST_CAPABILITY_RECOVERY_DRIFT")

    if receipt.get("status_hash72") != STATUS_HASH72 or len(STATUS_HASH72) != 72:
        raise RuntimeError("PASS204_STATUS_HASH72_DRIFT")
    if receipt.get("snapshot_root") != SNAPSHOT_ROOT or len(SNAPSHOT_ROOT) != 72:
        raise RuntimeError("PASS204_SNAPSHOT_ROOT_DRIFT")
    if receipt.get("core_native_receipt_hash72") != CORE_NATIVE_RECEIPT_HASH72:
        raise RuntimeError("PASS204_CORE_NATIVE_RECEIPT_DRIFT")
    if receipt.get("project_native_receipt_hash72") != PROJECT_NATIVE_RECEIPT_HASH72:
        raise RuntimeError("PASS204_PROJECT_NATIVE_RECEIPT_DRIFT")

    if inherited.get("schema") != "HHS_PASS_204_INHERITED_PASS_203_REPLAY_RECEIPT_V1":
        raise RuntimeError("PASS204_PASS203_RECEIPT_SCHEMA_DRIFT")
    if inherited.get("classification") != "HHS_PASS_203_UNIVERSAL_HYDRATED_FUNCTION_MAINFRAME_VERIFIED":
        raise RuntimeError("PASS204_PASS203_CLASSIFICATION_DRIFT")
    if inherited.get("closed") is not True or inherited.get("standalone_replay") is not True:
        raise RuntimeError("PASS204_PASS203_REPLAY_DRIFT")

    required_source_fragments = {
        "runtime_v1": (
            "PASS_204_INHERITS_ALL_PRIOR_PASSES_AS_ONE_INTEGRATED_SYSTEM",
            "persistent_capabilities",
            "session_recall_restores_capabilities",
        ),
        "runtime": (
            "history_rewrite_permitted",
            "capability_state_persisted",
            "CLOUD_SERVER_HARDWARE_ENVIRONMENT",
        ),
        "worker": (
            "network operation requires a mediated durable job",
            "host process creation is not exposed to remote sessions",
            "writes are restricted to the ephemeral sandbox",
        ),
        "native": (
            "raw host pointers are not accepted",
            "CANONICAL_CTYPES_ABI_EXECUTED",
            "raw_pointer_exposed",
        ),
        "routes": (
            "policy_mutation_endpoint",
            "mainframe_upgrade_unconditional",
            "capabilities_restored_on_recall",
        ),
    }
    source_texts = {
        "runtime_v1": runtime_v1,
        "runtime": runtime,
        "worker": worker,
        "native": native,
        "routes": routes,
    }
    for group, fragments in required_source_fragments.items():
        for fragment in fragments:
            if fragment not in source_texts[group]:
                raise RuntimeError(f"PASS204_SOURCE_BOUNDARY_DRIFT:{group}:{fragment}")

    if "Every declaration indexed by the cumulative mainframe catalog shall be hydrated and executable." not in contract:
        raise RuntimeError("PASS204_CONTRACT_CLOSURE_TEXT_DRIFT")
    if "Fixed read-only sandbox policy with no remote or internal mutation selector." not in restart:
        raise RuntimeError("PASS204_RESTART_SANDBOX_BOUNDARY_DRIFT")
    if "Pull request: `#147`" not in restart:
        raise RuntimeError("PASS204_RESTART_PR_IDENTITY_DRIFT")

    successor_receipt = successor.get("receipt") or {}
    if successor_receipt.get("contract") != "HHS-P205-VM5184-G243-DETERMINISTIC-MULTIMODAL-CONTINUATION-GAMING-ML-H72-H216":
        raise RuntimeError("PASS204_PASS205_SUCCESSOR_DRIFT")

    return {
        "receipt": receipt,
        "pass203_receipt": inherited,
        "pass205_successor": successor,
        "base_commit": BASE_COMMIT,
        "validated_head": VALIDATED_HEAD,
        "merge_commit": MERGE_COMMIT,
        "final_validation_workflow_run": FINAL_VALIDATION_WORKFLOW_RUN,
        "final_validation_artifact_id": FINAL_VALIDATION_ARTIFACT_ID,
        "final_validation_artifact_digest": FINAL_VALIDATION_ARTIFACT_DIGEST,
        "validation_receipt_blob": VALIDATION_RECEIPT_BLOB,
        "source_blobs": {str(path): value for path, value in EXPECTED_BLOBS.items()},
    }


def validate_pass204_production_identity() -> Dict[str, Any]:
    source = pass204_membrane_source_evidence()
    return {
        "ok": True,
        "classification": source["receipt"]["classification"],
        "validated_head": source["validated_head"],
        "merge_commit": source["merge_commit"],
    }


def validate_pass204_declaration_closure() -> Dict[str, Any]:
    summary = pass204_membrane_source_evidence()["receipt"]["summary"]
    return {
        "ok": True,
        "catalog_count": summary["catalog_count"],
        "hydrated_count": summary["hydrated_count"],
        "callable_count": summary["callable_count"],
        "binding_gap_count": summary["binding_gap_count"],
        "all_declarations_executable": True,
    }


def validate_pass204_fixed_sandbox_policy() -> Dict[str, Any]:
    policy = pass204_membrane_source_evidence()["receipt"]["sandbox_policy"]
    return {
        "ok": True,
        "remote_users_automatically_sandboxed": policy["remote_users_automatically_sandboxed"],
        "persistent_capabilities": policy["persistent_capabilities"],
        "direct_host_kernel_access": policy["direct_host_kernel_access"],
        "caller_adjustable_internal_policy": policy["caller_adjustable_internal_policy"],
    }


def validate_pass204_immutable_history_boundary() -> Dict[str, Any]:
    source = pass204_membrane_source_evidence()["receipt"]
    kernel = source["kernel_constraint_manifest"]
    host = source["host_trust_boundary"]
    return {
        "ok": True,
        "admitted_history_mutable": kernel["admitted_history_mutable"],
        "constraint_authority_mutable": kernel["constraint_authority_mutable"],
        "host_fault_can_rewrite_admitted_hash_history": host["host_fault_can_rewrite_admitted_hash_history"],
        "host_fault_can_mutate_constraint_contract": host["host_fault_can_mutate_constraint_contract"],
    }


def validate_pass204_persistence_and_recall() -> Dict[str, Any]:
    receipt = pass204_membrane_source_evidence()["receipt"]
    return {
        "ok": True,
        "inherited_durable_outputs": receipt["sandbox_policy"]["durable_outputs"],
        "recall_verified": receipt["recall_verified"],
        "capabilities_restored_on_recall": receipt["sandbox_policy"]["session_recall_restores_capabilities"],
        "i120_new_persistence_authority": False,
    }


def validate_pass204_native_execution_boundary() -> Dict[str, Any]:
    summary = pass204_membrane_source_evidence()["receipt"]["summary"]
    return {
        "ok": True,
        "core_native_execution_status": summary["core_native_execution_status"],
        "project_native_execution_status": summary["project_native_execution_status"],
        "raw_pointer_exposed": False,
        "direct_host_kernel_access": False,
    }


def validate_pass203_inherited_replay() -> Dict[str, Any]:
    inherited = pass204_membrane_source_evidence()["pass203_receipt"]
    return {
        "ok": True,
        "inherited_pass": 203,
        "classification": inherited["classification"],
        "standalone_replay": inherited["standalone_replay"],
    }


def validate_pass205_successor_binding() -> Dict[str, Any]:
    source = pass204_membrane_source_evidence()["pass205_successor"]
    return {
        "ok": True,
        "successor_pass": 205,
        "successor_contract": source["receipt"]["contract"],
        "successor_classification": source["receipt"]["classification"],
    }


def pass204_surface_declaration() -> Dict[str, Any]:
    pass204_membrane_source_evidence()
    return {
        "surface_id": PASS204_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i120_pass204",
        "symbol": "validate_pass204_production_identity",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS_PASS_204_OPEN_CLOUD_VALIDATION_RECEIPT_V1",
            "HHS_PASS_204_INHERITED_PASS_203_REPLAY_RECEIPT_V1",
        ],
        "witness_schemas": [
            "HHSExactPass204OpenCloudWitnessV1",
            "HHSExactPass219InheritedPass204BindingV1",
        ],
        "validators": [PASS204_BIND_SYMBOL, "validate_pass204_production_identity"],
        "guards": [
            "pass204_zero_binding_gaps",
            "pass204_fixed_remote_sandbox",
            "pass204_no_persistent_capabilities",
            "pass204_capability_free_recall",
            "pass204_immutable_admitted_history",
            "pass204_no_host_pointer_exposure",
            "pass204_pass203_replay_preserved",
            "pass204_pass205_successor_preserved",
        ],
        "rejection_codes": [
            "REJECT_PASS204_PRODUCTION_IDENTITY_DRIFT",
            "REJECT_PASS204_BINDING_GAP_REINTRODUCTION",
            "REJECT_PASS204_SANDBOX_POLICY_MUTATION",
            "REJECT_PASS204_PERSISTENT_CAPABILITY_ESCALATION",
            "REJECT_PASS204_HISTORY_REWRITE_AUTHORITY",
            "REJECT_PASS204_HOST_POINTER_EXPOSURE",
            "REJECT_PASS204_PASS203_REPLAY_DRIFT",
            "REJECT_PASS204_PASS205_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_PASS204_DURABLE_STATE_READ_ONLY_BINDING",
        "boundedness_policy": "PASS_204_VERIFIED_OPEN_CLOUD_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass204_membrane_manifest() -> Dict[str, Any]:
    source = pass204_membrane_source_evidence()
    receipt = source["receipt"]
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS204_NUMBER,
        "classification": PASS204_CLASSIFICATION,
        "census_classification": PASS204_CENSUS_CLASSIFICATION,
        "pass219_c_abi_surface": PASS204_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass204OpenCloudMainframe",
        "declaration_count": receipt["summary"]["catalog_count"],
        "binding_gap_count": receipt["summary"]["binding_gap_count"],
        "public_route_count": receipt["summary"]["public_route_count"],
        "openapi_path_count": receipt["summary"]["openapi_path_count"],
        "fixed_sandbox_policy_bound": True,
        "persistent_capabilities": False,
        "capability_free_recall_bound": True,
        "immutable_history_boundary_bound": True,
        "canonical_core_abi_bound": True,
        "project_native_durable_job_bound": True,
        "inherited_pass204_persistence_bound": True,
        "pass203_inheritance_bound": True,
        "pass205_successor_bound": True,
        "pass219_new_canonical_mutation_authority": False,
        "pass219_new_persistence_authority": False,
        "pass219_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "validated_head": source["validated_head"],
        "merge_commit": source["merge_commit"],
        "validation_receipt_blob": source["validation_receipt_blob"],
        "source_blobs": source["source_blobs"],
        "surface": pass204_surface_declaration(),
    }


def preflight_pass204_membrane() -> Dict[str, Any]:
    declaration = pass204_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    ok = all(row.get("ok") is True for row in rows)
    return {
        "schema": "HHS_PASS219_I120_PASS204_MEMBRANE_PREFLIGHT_V1",
        "ok": ok,
        "surface_id": PASS204_SURFACE_ID,
        "operations": rows,
        "manifest": pass204_membrane_manifest(),
    }


if __name__ == "__main__":
    print(json.dumps(preflight_pass204_membrane(), indent=2, sort_keys=True))
