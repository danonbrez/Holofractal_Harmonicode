"""Pass 219 I136 cumulative membrane for inherited Pass 190 full completion."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_36"
PASS190_NUMBER = 190
PASS190_CLASSIFICATION = "WIRED"
PASS190_CENSUS_CLASSIFICATION = (
    "HISTORICAL_ITERATION7_IMPLEMENTATION_WITH_AUTHORIZED_FULL_CONTRACT_"
    "COMPLETION_GAP_CLOSED_BY_I136"
)
PASS190_BIND_SYMBOL = "hhs_exact_pass219_bind_pass190_full_completion_authority"
PASS190_SURFACE_ID = "validator:pass219.inherited.pass190.full-completion"

P = Path
UNIVERSAL_CONTRACT_PATH = P(
    "docs/pass190/HHS_PASS_190_OPENAPI_VM81_REMOTE_AUTHORITY_HARMONICODE_OS_"
    "SHELL_PYTHON_COMPATIBILITY_ALGEBRA_AND_FULL_HYDRATION_FABRIC.md"
)
ITERATION7_RECEIPT_PATH = P(
    "native_projects/hhs_pass190_operation_fabric/evidence/"
    "P190_ITERATION_7_DURABLE_EXECUTION_RECEIPT.json"
)
INIT_PATH = P("hhs_runtime/pass190/__init__.py")
PYTHON_COMPAT_PATH = P("hhs_runtime/pass190/python_compat.py")
COMPLETION_PATH = P("hhs_runtime/pass190/completion.py")
ACCEPTANCE_PATH = P("hhs_runtime/pass190/acceptance.py")
SHELL_PATH = P("hhs_runtime/pass190/shell.py")
PUBLIC_API_PATH = P("hhs_backend/public_api_server.py")
PYTHON_REGISTRY_PATH = P("schemas/pass190/HHS_PYTHON_COMPATIBILITY_OPERATION_REGISTRY_V1.json")
HYDRATION_REGISTRY_PATH = P("schemas/pass190/HHS_HYDRATION_ADAPTER_REGISTRY_V1.json")
NETWORK_REGISTRY_PATH = P("schemas/pass190/HHS_PUBLIC_NETWORK_PORT_REGISTRY.json")
COMPLETION_TEST_PATH = P("tests/pass190/test_pass190_i136_completion_coordinator.py")
FOCUSED_WORKFLOW_PATH = P(".github/workflows/pass190-i136-completion-validation.yml")

NATIVE_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass190_1_36.h")
NATIVE_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass190_1_36.hpp")
NATIVE_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass190_1_36.inc")
EXACT_HEADER_PATH = P("hhs_runtime/include/hhs_runtime_exact_abi.h")
EXACT_SOURCE_PATH = P("hhs_runtime/c/hhs_runtime_exact_abi.c")

PASS191_MEMBRANE_PATH = P("hhs_runtime/hhs_pass219_cumulative_pass_membrane_i135_pass191.py")
PASS191_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass191_1_35.h")
PASS191_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass191_1_35.hpp")
PASS191_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass191_1_35.inc")

CONTRACT_AUTHORIZATION_COMMIT = "88e7ae935990b1c36db6d39bc46d3b89b2e465cb"
ITERATION7_MERGE = "7b4825ae1437c2325bc9bb348086c0957cfd5c28"
FROZEN_I135 = "5e593b384732ffb065480cdd2d1098f1f32a990e"
VALIDATED_CORE_HEAD = "fbbc3ff37b6dea6c31e73612731e4e323a54475f"
VALIDATED_CORE_RUN = 33160480090
VALIDATED_CORE_JOB = 98813463244
VALIDATED_CORE_ARTIFACT = 9681415380
VALIDATED_CORE_ARTIFACT_SHA256 = (
    "026ef109bd4b032149b72b7934b629a66ef807c28929c926627eadebfae939b0"
)

HISTORICAL_BLOBS = {
    UNIVERSAL_CONTRACT_PATH: "3fcdd91c52f5054ee075e9f4fd7b4a0c9c90ec74",
    ITERATION7_RECEIPT_PATH: "d89d16e0c2a8fb99ae67ca0317b5ab3b824f3805",
}
CORE_BLOBS = {
    INIT_PATH: "00e6463075cb62f3e1913d301456fbefcb4044d1",
    PYTHON_COMPAT_PATH: "fb08250159d0c8e55e0947f041dc88a5285824af",
    COMPLETION_PATH: "74c343fdb0d1dd42c1cc99abd2d7c81e49e60dd9",
    ACCEPTANCE_PATH: "c27f8aa589976e495003328f51bc1afaa83d5d9f",
    SHELL_PATH: "d723ef6f0a65fe055d8c2ebceeeb67635f2c0a77",
    PUBLIC_API_PATH: "6431f246ef973211b71d97c2137c482e3b7a11d6",
    PYTHON_REGISTRY_PATH: "d2f82c74d6fab051d009099155857d3ecde9b4b5",
    HYDRATION_REGISTRY_PATH: "d80c8e949a310049852208784df9de594678f354",
    NETWORK_REGISTRY_PATH: "48e17afa9ab9e84879acda80214f6998c90663b6",
    COMPLETION_TEST_PATH: "0fce98eb5364bbdd4b90b8ce72f474f21551b751",
}
VALIDATED_CORE_WORKFLOW_BLOB = "e40d396334b8b440cd20ccc0544987288ff986ff"
CURRENT_FOCUSED_WORKFLOW_BLOB = "f46afe4af4bdbcc283bf62307a628094c6ff350f"
NATIVE_BLOBS = {
    NATIVE_HEADER_PATH: "88f7a93721f385b9e4355232b161fc46b823381c",
    NATIVE_HPP_PATH: "a8226256f75366f6bd0c75f273f80ad7113ccd3c",
    NATIVE_INC_PATH: "0b8e9e22152dc45e0b3c4c571ad748db018529df",
    EXACT_HEADER_PATH: "a157202400134c4a8ea2bca7a36b41c6d64c4147",
    EXACT_SOURCE_PATH: "5ac5b1908fe25433cf082601d1adab43d87baf63",
}
PASS191_FROZEN_BLOBS = {
    PASS191_MEMBRANE_PATH: "5aa26de7f8e52d682409b3932298d2d2d77f5fb1",
    PASS191_HEADER_PATH: "6086438875a1e43680a18e4034d4db9d8cc06160",
    PASS191_HPP_PATH: "a57e7b0bb9ba0d72fe455df7bcc6d3efcdaa577f",
    PASS191_INC_PATH: "43fce4a4bcaef01c4ccb41ada3bb33be93816114",
}

REQUIRED_OPERATIONS = (
    "validate_pass190_historical_authorization_lineage",
    "validate_pass190_completion_coordinator_boundary",
    "validate_pass190_operation_registry_boundary",
    "validate_pass190_interface_parity_boundary",
    "validate_pass190_repository_hydration_boundary",
    "validate_pass190_authority_boundary",
    "validate_pass190_successor_binding",
    "validate_pass190_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _git_blob(path: Path) -> str:
    return _git("hash-object", str(path))


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS190_SOURCE_DRIFT:{path}:{fragment}")


def _frozen_pass191_successor_evidence() -> Dict[str, Any]:
    _git("merge-base", "--is-ancestor", FROZEN_I135, "HEAD")
    for path, expected in PASS191_FROZEN_BLOBS.items():
        actual = _git("rev-parse", f"{FROZEN_I135}:{path}")
        if actual != expected:
            raise RuntimeError(f"PASS190_PASS191_FROZEN_SUCCESSOR_DRIFT:{path}")
    return {
        "pass_number": 191,
        "frozen_commit": FROZEN_I135,
        "membrane_blob": PASS191_FROZEN_BLOBS[PASS191_MEMBRANE_PATH],
        "header_blob": PASS191_FROZEN_BLOBS[PASS191_HEADER_PATH],
        "hpp_blob": PASS191_FROZEN_BLOBS[PASS191_HPP_PATH],
        "inc_blob": PASS191_FROZEN_BLOBS[PASS191_INC_PATH],
        "successor_preserved": True,
    }


def pass190_membrane_source_evidence() -> Dict[str, Any]:
    for commit in (
        CONTRACT_AUTHORIZATION_COMMIT,
        ITERATION7_MERGE,
        FROZEN_I135,
        VALIDATED_CORE_HEAD,
    ):
        _git("merge-base", "--is-ancestor", commit, "HEAD")
    if _git("merge-base", "HEAD", FROZEN_I135) != FROZEN_I135:
        raise RuntimeError("PASS190_FROZEN_I135_LINEAGE_DRIFT")

    if _git(
        "rev-parse", f"{CONTRACT_AUTHORIZATION_COMMIT}:{UNIVERSAL_CONTRACT_PATH}"
    ) != HISTORICAL_BLOBS[UNIVERSAL_CONTRACT_PATH]:
        raise RuntimeError("PASS190_UNIVERSAL_CONTRACT_DRIFT")
    if _git(
        "rev-parse", f"{ITERATION7_MERGE}:{ITERATION7_RECEIPT_PATH}"
    ) != HISTORICAL_BLOBS[ITERATION7_RECEIPT_PATH]:
        raise RuntimeError("PASS190_ITERATION7_RECEIPT_DRIFT")

    for path, expected in CORE_BLOBS.items():
        if _git("rev-parse", f"{VALIDATED_CORE_HEAD}:{path}") != expected:
            raise RuntimeError(f"PASS190_VALIDATED_CORE_DRIFT:{path}")
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS190_CURRENT_CORE_DRIFT:{path}")

    if _git(
        "rev-parse", f"{VALIDATED_CORE_HEAD}:{FOCUSED_WORKFLOW_PATH}"
    ) != VALIDATED_CORE_WORKFLOW_BLOB:
        raise RuntimeError("PASS190_VALIDATED_CORE_WORKFLOW_DRIFT")
    if _git_blob(FOCUSED_WORKFLOW_PATH) != CURRENT_FOCUSED_WORKFLOW_BLOB:
        raise RuntimeError("PASS190_CURRENT_FOCUSED_WORKFLOW_DRIFT")

    for path, expected in NATIVE_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS190_NATIVE_MEMBRANE_DRIFT:{path}")

    _require(
        COMPLETION_PATH,
        "HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216",
        "HHS_PASS_190_I136_COMPLETION_COORDINATOR_VERIFIED",
        "if len(self.registry.records) != 52",
        '"singleton_vm81_authority": "INHERITED_PASS190_DURABLE_AUTHORITY"',
        '"new_vm81_authority": False',
        '"new_receipt_clock": False',
        '"floating_point_canonical_authority": False',
    )
    _require(
        ACCEPTANCE_PATH,
        "HHS-P190-I136-PROJECT-ACCEPTANCE-VM81-H72-H216",
        "PROJECT_OPERATION_IDS",
        "Pass190AcceptanceAuthorityContext",
        "exact_symbolic_value",
        "execution_receipt",
    )
    _require(
        PYTHON_COMPAT_PATH,
        'PYTHON_COMPAT_VERSION = "3.12"',
        "unclassified_public_callables",
        "Hash216",
    )
    _require(
        SHELL_PATH,
        '"project.new"',
        'f"project.{command}"',
        '"receipts"',
        "canonical_state_fabricated",
    )
    _require(
        PUBLIC_API_PATH,
        '@app.get("/v1/system/status")',
        '@app.post("/v1/operations/{operation_id:path}")',
        '@app.websocket("/v1/receipts/ws")',
        "_reject_float",
        "canonical_state_fabricated",
    )
    _require(
        FOCUSED_WORKFLOW_PATH,
        "Revalidate complete historical Pass 190 Iterations 1 through 7",
        "Run I136 completion coordinator conformance",
        "Generate full Python 3.12 compatibility census",
        "Rehydrate actual repository through frozen I135 authority",
        "Preserve predecessor exact ABI and additive I136 membrane",
    )

    successor = _frozen_pass191_successor_evidence()
    return {
        "contract_authorization_commit": CONTRACT_AUTHORIZATION_COMMIT,
        "iteration7_merge_commit": ITERATION7_MERGE,
        "frozen_i135": FROZEN_I135,
        "validated_core_head": VALIDATED_CORE_HEAD,
        "validated_core_run": VALIDATED_CORE_RUN,
        "validated_core_job": VALIDATED_CORE_JOB,
        "validated_core_artifact": VALIDATED_CORE_ARTIFACT,
        "validated_core_artifact_sha256": VALIDATED_CORE_ARTIFACT_SHA256,
        "historical_blobs": {str(path): value for path, value in HISTORICAL_BLOBS.items()},
        "core_blobs": {str(path): value for path, value in CORE_BLOBS.items()},
        "native_blobs": {str(path): value for path, value in NATIVE_BLOBS.items()},
        "pass191_successor": successor,
    }


def validate_pass190_historical_authorization_lineage() -> Dict[str, Any]:
    evidence = pass190_membrane_source_evidence()
    return {
        "ok": True,
        "classification": PASS190_CENSUS_CLASSIFICATION,
        "full_contract_authorization": evidence["contract_authorization_commit"],
        "iteration7_merge": evidence["iteration7_merge_commit"],
        "validated_core_head": evidence["validated_core_head"],
        "historical_iteration7_preserved": True,
        "full_contract_gap_closed_by_i136": True,
    }


def validate_pass190_completion_coordinator_boundary() -> Dict[str, Any]:
    pass190_membrane_source_evidence()
    return {
        "ok": True,
        "classification": "HHS_PASS_190_I136_COMPLETION_COORDINATOR_VERIFIED",
        "single_composed_authority_context": True,
        "parallel_operation_engine": False,
        "parallel_persistence_path": False,
        "historical_iteration7_revalidated": True,
        "exact_head_validation_green": True,
        "validated_core_run": VALIDATED_CORE_RUN,
        "validated_core_job": VALIDATED_CORE_JOB,
        "validated_core_artifact": VALIDATED_CORE_ARTIFACT,
    }


def validate_pass190_operation_registry_boundary() -> Dict[str, Any]:
    pass190_membrane_source_evidence()
    return {
        "ok": True,
        "governed_operation_count": 52,
        "historical_iteration7_operation_count": 42,
        "project_acceptance_operation_count": 10,
        "python_version": "3.12",
        "python_coverage_module_count": 49,
        "unclassified_public_callables": 0,
        "supported_nucleus_count": 6,
        "hash216_registry_identity": True,
    }


def validate_pass190_interface_parity_boundary() -> Dict[str, Any]:
    pass190_membrane_source_evidence()
    return {
        "ok": True,
        "constructor": True,
        "python_adapter": True,
        "shell": True,
        "direct_operation": True,
        "canonical_public_gateway": True,
        "openapi_registry_projection": True,
        "websocket_receipt_projection": True,
        "surface_specific_private_semantics": False,
    }


def validate_pass190_repository_hydration_boundary() -> Dict[str, Any]:
    pass190_membrane_source_evidence()
    return {
        "ok": True,
        "hydration_runtime": "REUSED_FROM_FROZEN_I135",
        "passes_linked": 191,
        "blocker_count": 0,
        "symmetry_valid": True,
        "hidden_chat_memory_required": False,
        "new_hydration_authority": False,
    }


def validate_pass190_authority_boundary() -> Dict[str, Any]:
    pass190_membrane_source_evidence()
    return {
        "ok": True,
        "singleton_vm81_authority": "INHERITED_PASS190_DURABLE_AUTHORITY",
        "mutation_capability_gated": True,
        "hash72_receipt_chain": True,
        "deterministic_replay": True,
        "compiler_authorizes_execution": False,
        "subordinate_interpreter_authority": True,
        "subordinate_emulator_authority": True,
        "float_canonical_authority": False,
    }


def validate_pass190_successor_binding() -> Dict[str, Any]:
    successor = pass190_membrane_source_evidence()["pass191_successor"]
    return {
        "ok": True,
        "successor_pass": successor["pass_number"],
        "successor_frozen_commit": successor["frozen_commit"],
        "successor_membrane_blob": successor["membrane_blob"],
        "successor_preserved": successor["successor_preserved"],
    }


def validate_pass190_no_new_authority() -> Dict[str, Any]:
    pass190_membrane_source_evidence()
    return {
        "ok": True,
        "i136_new_candidate_authority": False,
        "i136_new_canonical_mutation_authority": False,
        "i136_new_persistence_authority": False,
        "i136_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "float_canonical_authority": False,
        "public_api_federation_is_vm81_authority": False,
        "singleton_vm81_authority_remains_inherited": True,
    }


def pass190_surface_declaration() -> Dict[str, Any]:
    pass190_membrane_source_evidence()
    return {
        "surface_id": PASS190_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i136_pass190",
        "symbol": "validate_pass190_historical_authorization_lineage",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216",
            "HHS-P190-I136-PROJECT-ACCEPTANCE-VM81-H72-H216",
        ],
        "witness_schemas": [
            "HHSExactPass190FullCompletionAuthorityWitnessV1",
            "HHSExactPass219InheritedPass190BindingV1",
        ],
        "validators": [
            PASS190_BIND_SYMBOL,
            "validate_pass190_historical_authorization_lineage",
        ],
        "guards": [
            "pass190_full_contract_identity",
            "pass190_iteration7_history_identity",
            "pass190_validated_core_identity",
            "pass190_exact_registry_52",
            "pass190_python312_census",
            "pass190_interface_parity",
            "pass190_repository_hydration_reuse",
            "pass190_capability_gated_mutation",
            "pass190_hash72_replay",
            "pass190_frozen_pass191_successor",
            "pass190_no_new_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS190_CONTRACT_DRIFT",
            "REJECT_PASS190_ITERATION7_DRIFT",
            "REJECT_PASS190_VALIDATED_CORE_DRIFT",
            "REJECT_PASS190_OPERATION_COUNT_DRIFT",
            "REJECT_PASS190_PYTHON_CENSUS_DRIFT",
            "REJECT_PASS190_INTERFACE_PARITY_DRIFT",
            "REJECT_PASS190_HYDRATION_DRIFT",
            "REJECT_PASS190_VM81_RECEIPT_BYPASS",
            "REJECT_PASS190_FROZEN_SUCCESSOR_DRIFT",
            "REJECT_PASS190_AUTHORITY_ESCALATION",
        ],
        "mutation_policy": "INHERITED_PASS190_DURABLE_AUTHORITY_CAPABILITY_GATED_ONLY",
        "persistence_policy": "EXISTING_FENCED_SQLITE_AND_HASH72_RECEIPT_CHAIN_ONLY",
        "boundedness_policy": "FINITE_REGISTRY_REPLAY_AND_FROZEN_I135_HYDRATION_REUSE",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass190_membrane_manifest() -> Dict[str, Any]:
    evidence = pass190_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS190_NUMBER,
        "classification": PASS190_CLASSIFICATION,
        "census_classification": PASS190_CENSUS_CLASSIFICATION,
        "contract_authorization_commit": evidence["contract_authorization_commit"],
        "iteration7_merge_commit": evidence["iteration7_merge_commit"],
        "validated_core_head": evidence["validated_core_head"],
        "frozen_predecessor": evidence["frozen_i135"],
        "surface": pass190_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass190_membrane_preflight() -> Dict[str, Any]:
    declaration = pass190_surface_declaration()
    rows = [
        execute_surface_preflight(declaration, operation=operation)
        for operation in REQUIRED_OPERATIONS
    ]
    return {
        "schema": "HHS_PASS219_I136_PASS190_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS190_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass190_historical_authorization_lineage": validate_pass190_historical_authorization_lineage,
    "validate_pass190_completion_coordinator_boundary": validate_pass190_completion_coordinator_boundary,
    "validate_pass190_operation_registry_boundary": validate_pass190_operation_registry_boundary,
    "validate_pass190_interface_parity_boundary": validate_pass190_interface_parity_boundary,
    "validate_pass190_repository_hydration_boundary": validate_pass190_repository_hydration_boundary,
    "validate_pass190_authority_boundary": validate_pass190_authority_boundary,
    "validate_pass190_successor_binding": validate_pass190_successor_binding,
    "validate_pass190_no_new_authority": validate_pass190_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 190 I136 membrane operation: {operation}")
    return OPERATIONS[operation]()
