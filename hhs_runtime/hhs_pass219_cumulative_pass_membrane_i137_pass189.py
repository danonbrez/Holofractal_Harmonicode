"""Pass 219 I137 cumulative membrane for inherited Pass 189 authority."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_37"
PASS189_NUMBER = 189
PASS189_CLASSIFICATION = "WIRED"
PASS189_CENSUS_CLASSIFICATION = (
    "MULTI_ITERATION_EXECUTABLE_HQLH_AUTHORITY_WITH_"
    "CALIBRATION_IN_PROGRESS_AND_HARDWARE_EXECUTION_UNAUTHORIZED"
)
PASS189_BIND_SYMBOL = "hhs_exact_pass219_bind_pass189_cumulative_authority"
PASS189_SURFACE_ID = "validator:pass219.inherited.pass189.cumulative-authority"

P = Path
TEMPLATE_CONTRACT_PATH = P(
    "docs/pass189/"
    "HHS_PASS_189_REPOSITORY_WIDE_TEMPLATE_OBJECT_REGISTRY_SEARCH_AND_MODALITY_MENU_TREE.md"
)
HQLH_CONTRACT_PATH = P(
    "HHS_PASS_189_HARMONICODE_QUANTUM_LOGIC_HYDRATION_UNIFIED_PHYSICS_AUTHORITY_ADDITION.md"
)
RUNTIME_DOC_PATH = P("HHS_PASS_189_HQLH_RUNTIME_IMPLEMENTATION_AND_DIGITALOCEAN_AUTHORITY.md")
ITERATION2_DOC_PATH = P("HHS_PASS_189_ITERATION_2_CALIBRATION_CAUSAL_PERSISTENCE_AUTHORITY.md")
ITERATION3_DOC_PATH = P("HHS_PASS_189_ITERATION_3_DEVICE_ADAPTER_LEASE_WATCHDOG_AUTHORITY.md")
ITERATION4_DOC_PATH = P("HHS_PASS_189_ITERATION_4_DRIVER_PROVENANCE_QUARANTINE_PROMOTION_AUTHORITY.md")

MAKEFILE_PATH = P("native_projects/hhs_pass189_hqlh_runtime/Makefile")
NATIVE_HQLH_HEADER_PATH = P("native_projects/hhs_pass189_hqlh_runtime/include/hhs_pass189_hqlh.h")
NATIVE_HQLH_SOURCE_PATH = P("native_projects/hhs_pass189_hqlh_runtime/src/hhs_pass189_hqlh.c")
PYTHON_RUNTIME_PATH = P("native_projects/hhs_pass189_hqlh_runtime/python/hhs_pass189.py")
ITERATION2_PYTHON_PATH = P("native_projects/hhs_pass189_hqlh_runtime/python/hhs_pass189_iteration2.py")
ITERATION3_PYTHON_PATH = P("native_projects/hhs_pass189_hqlh_runtime/python/hhs_pass189_iteration3.py")
ITERATION4_PYTHON_PATH = P("native_projects/hhs_pass189_hqlh_runtime/python/hhs_pass189_iteration4.py")
TOKEN_LIFECYCLE_PATH = P(
    "native_projects/hhs_pass189_hqlh_runtime/python/hhs_pass189_iteration4_token_lifecycle.py"
)
TEMPLATE_REGISTRY_PATH = P(
    "native_projects/hhs_pass189_hqlh_runtime/registry/hhs_pass189_hqlh.template.json"
)
FOCUSED_WORKFLOW_PATH = P(".github/workflows/pass189-hqlh-runtime.yml")
BASE_RECEIPT_PATH = P("native_projects/hhs_pass189_hqlh_runtime/evidence/P189_VALIDATION_RECEIPT.json")
ITERATION2_RECEIPT_PATH = P(
    "native_projects/hhs_pass189_hqlh_runtime/evidence/P189_ITERATION_2_VALIDATION_RECEIPT.json"
)
ITERATION3_RECEIPT_PATH = P(
    "native_projects/hhs_pass189_hqlh_runtime/evidence/P189_ITERATION_3_VALIDATION_RECEIPT.json"
)
ITERATION4_RECEIPT_PATH = P(
    "native_projects/hhs_pass189_hqlh_runtime/evidence/P189_ITERATION_4_VALIDATION_RECEIPT.json"
)
DNS_REGISTRY_PATH = P("native_projects/hhs_native_dns_gate/config/service_registry.json")
DEPLOY_INSTALL_PATH = P(
    "native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/install.sh"
)
DEPLOY_NGINX_PATH = P(
    "native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/nginx-hhs-pass189.conf"
)
DEPLOY_VERIFY_PATH = P(
    "native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh"
)

NATIVE_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass189_1_37.h")
NATIVE_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass189_1_37.hpp")
NATIVE_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass189_1_37.inc")
EXACT_HEADER_PATH = P("hhs_runtime/include/hhs_runtime_exact_abi.h")
EXACT_SOURCE_PATH = P("hhs_runtime/c/hhs_runtime_exact_abi.c")

PASS190_MEMBRANE_PATH = P("hhs_runtime/hhs_pass219_cumulative_pass_membrane_i136_pass190.py")
PASS190_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass190_1_36.h")
PASS190_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass190_1_36.hpp")
PASS190_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass190_1_36.inc")

TEMPLATE_CONTRACT_COMMIT = "9dfd373d5ccd66b9172313b750c8439435d90f49"
HQLH_CONTRACT_MERGE = "54ffe9d89d1aa928a6be75a3663ad51f709b7b9d"
RUNTIME_IMPLEMENTATION_COMMIT = "a1a55a4f621ff3678f5af81119439e9558cf9db4"
ITERATION2_COMMIT = "c3cc477cd1b573eb5a318c7f38a1197e428d7014"
ITERATION3_COMMIT = "f3ceba745ce5b478ca850c14a543a18189cc7d6c"
ITERATION4_COMMIT = "7a99674997974262b171a0aee05665cbeab42ab9"
TOKEN_LIFECYCLE_COMMIT = "0ee579aa574fa8f8b4c827518ae4249bbad4e8be"
DNS_INTEGRATION_COMMIT = "8ac51f5de0be323513577863fcbde71578ef4e14"
FROZEN_I136 = "3a76667eb463f8027e2bfaea4a2f76cff470c564"

SOURCE_BLOBS = {
    TEMPLATE_CONTRACT_PATH: "daae3c4cb368d42fd9f83c22abd9a81380ba0f2a",
    HQLH_CONTRACT_PATH: "0bc9f1a3ee9d2252002310e5c5cab88ad98553a5",
    RUNTIME_DOC_PATH: "3d9a4f7869b23d2655c1027fac353c841a8b7a2e",
    ITERATION2_DOC_PATH: "492c28b6368d7f36649e377cb052097a6fa60703",
    ITERATION3_DOC_PATH: "492e5434c4319b28a9f8838606cfd8dc00b0ae65",
    ITERATION4_DOC_PATH: "5c7e8391a28c14ae0bbdae15592d3889c85f53c0",
    MAKEFILE_PATH: "35f9ed59c26994247a2fa209afe0280329cef106",
    NATIVE_HQLH_HEADER_PATH: "b558c7f090913a70bf3691f6fb413fd5a7bdebff",
    NATIVE_HQLH_SOURCE_PATH: "651a2a2f4be6d802c88182c016657be1698f83b2",
    PYTHON_RUNTIME_PATH: "5d98e213ce80f793b0d3761efbe88dff33bb7f14",
    ITERATION2_PYTHON_PATH: "88f50add4b71c9c57877f96f61854aade405c0b3",
    ITERATION3_PYTHON_PATH: "eea7c2f825583d4013395c472d62cf9dd81e5923",
    ITERATION4_PYTHON_PATH: "aeec45db0b773364fdc155be62499cbb5ec4e221",
    TOKEN_LIFECYCLE_PATH: "b427718ba16e143797c0856587ec83556314df19",
    TEMPLATE_REGISTRY_PATH: "8583c4e2e3621072d414448968cbdbfe81e311ad",
    FOCUSED_WORKFLOW_PATH: "f184f462b5eb1a93fd3c41d2b622ee4ac0bcc35c",
    BASE_RECEIPT_PATH: "23d61fa5cc157fcb44967e33956bbc97d50dba36",
    ITERATION2_RECEIPT_PATH: "2e99a7a11e1adca6168ba10ad51cb6bf9d96b487",
    ITERATION3_RECEIPT_PATH: "c0ef0202fda59f93581da4cad3f6ec163b7feb0a",
    ITERATION4_RECEIPT_PATH: "c383e5232d1d16ba2b9f66cbe9a7bda09e432d9d",
    DNS_REGISTRY_PATH: "16a264268f91301ba499c8beb253b18677873390",
    DEPLOY_INSTALL_PATH: "0812c2b856d0ee566a85406bf985e43ddc36bd82",
    DEPLOY_NGINX_PATH: "7ff10ade19f06fe344572e223ee04ef8beaa9a63",
    DEPLOY_VERIFY_PATH: "af3888769a913ee0bd72c002a854a77672ca3353",
}

NATIVE_BLOBS = {
    NATIVE_HEADER_PATH: "f487d7e67402cce3b97124dea531347e10b4be07",
    NATIVE_HPP_PATH: "610bcb4c9b823c457d3a049c45426ff57d5c992c",
    NATIVE_INC_PATH: "a3c054c8b4592a3a22944e5418a8847958156556",
    EXACT_HEADER_PATH: "80b3480b96ec897804f44ca561b3f575f070c9bb",
    EXACT_SOURCE_PATH: "e22eba55fcd054984ca1c2d883d093130e4ab974",
}

PASS190_FROZEN_BLOBS = {
    PASS190_MEMBRANE_PATH: "7dd6b98e7603ebed21c272bd1341961619984444",
    PASS190_HEADER_PATH: "88f7a93721f385b9e4355232b161fc46b823381c",
    PASS190_HPP_PATH: "a8226256f75366f6bd0c75f273f80ad7113ccd3c",
    PASS190_INC_PATH: "0b8e9e22152dc45e0b3c4c571ad748db018529df",
}

REQUIRED_OPERATIONS = (
    "validate_pass189_historical_lineage",
    "validate_pass189_template_registry_boundary",
    "validate_pass189_hqlh_exact_topology_boundary",
    "validate_pass189_calibration_causal_boundary",
    "validate_pass189_device_adapter_boundary",
    "validate_pass189_driver_provenance_boundary",
    "validate_pass189_deployment_dns_boundary",
    "validate_pass189_successor_binding",
    "validate_pass189_no_new_authority",
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
            raise RuntimeError(f"PASS189_SOURCE_DRIFT:{path}:{fragment}")


def _frozen_pass190_successor_evidence() -> Dict[str, Any]:
    _git("merge-base", "--is-ancestor", FROZEN_I136, "HEAD")
    for path, expected in PASS190_FROZEN_BLOBS.items():
        actual = _git("rev-parse", f"{FROZEN_I136}:{path}")
        if actual != expected:
            raise RuntimeError(f"PASS189_PASS190_FROZEN_SUCCESSOR_DRIFT:{path}")
    return {
        "pass_number": 190,
        "frozen_commit": FROZEN_I136,
        "membrane_blob": PASS190_FROZEN_BLOBS[PASS190_MEMBRANE_PATH],
        "header_blob": PASS190_FROZEN_BLOBS[PASS190_HEADER_PATH],
        "hpp_blob": PASS190_FROZEN_BLOBS[PASS190_HPP_PATH],
        "inc_blob": PASS190_FROZEN_BLOBS[PASS190_INC_PATH],
        "successor_preserved": True,
    }


def pass189_membrane_source_evidence() -> Dict[str, Any]:
    for commit in (
        TEMPLATE_CONTRACT_COMMIT,
        HQLH_CONTRACT_MERGE,
        RUNTIME_IMPLEMENTATION_COMMIT,
        ITERATION2_COMMIT,
        ITERATION3_COMMIT,
        ITERATION4_COMMIT,
        TOKEN_LIFECYCLE_COMMIT,
        DNS_INTEGRATION_COMMIT,
        FROZEN_I136,
    ):
        _git("merge-base", "--is-ancestor", commit, "HEAD")
    if _git("merge-base", "HEAD", FROZEN_I136) != FROZEN_I136:
        raise RuntimeError("PASS189_FROZEN_I136_LINEAGE_DRIFT")

    historical = {
        TEMPLATE_CONTRACT_COMMIT: TEMPLATE_CONTRACT_PATH,
        HQLH_CONTRACT_MERGE: HQLH_CONTRACT_PATH,
        RUNTIME_IMPLEMENTATION_COMMIT: RUNTIME_DOC_PATH,
        ITERATION2_COMMIT: ITERATION2_DOC_PATH,
        ITERATION3_COMMIT: ITERATION3_DOC_PATH,
        TOKEN_LIFECYCLE_COMMIT: ITERATION4_DOC_PATH,
    }
    for commit, path in historical.items():
        if _git("rev-parse", f"{commit}:{path}") != SOURCE_BLOBS[path]:
            raise RuntimeError(f"PASS189_HISTORICAL_SOURCE_DRIFT:{commit}:{path}")

    for path, expected in SOURCE_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS189_IMPLEMENTED_SOURCE_DRIFT:{path}")
    for path, expected in NATIVE_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS189_NATIVE_MEMBRANE_DRIFT:{path}")

    _require(
        HQLH_CONTRACT_PATH,
        "HHS-P189-HQLH-LS41-XNOR-P1-H72-H216-UPA",
        "HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS",
        "no floating-point canonical authority",
        "one VM81 admission membrane",
        "one Hash72 commit chain",
    )
    _require(
        ITERATION2_DOC_PATH,
        "HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS",
        "CANDIDATE_ONLY_NO_DEVICE_DRIVER",
        "BEGIN IMMEDIATE",
        "one global Hash72",
        "Non-authoritative and excluded from acceptance",
    )
    _require(
        ITERATION3_DOC_PATH,
        "HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS",
        "LOOPBACK",
        "FILE_SINK",
        "anti-replay",
    )
    _require(
        ITERATION4_DOC_PATH,
        "HARDWARE_CANDIDATE_NONEXECUTABLE",
        "promotion",
        "rollback",
        "issue witness",
    )
    _require(
        TEMPLATE_REGISTRY_PATH,
        '"maturity": "DRIVER_PROVENANCE_QUARANTINE_AND_TOKEN_LIFECYCLE_IMPLEMENTED_REAL_DRIVER_EXECUTION_PENDING"',
        '"runtime_authority": "VM81_SINGLETON_HASH72_CHAIN_WITH_SQLITE_CALIBRATION_DEVICE_AND_PROVENANCE_PERSISTENCE"',
        '"floating_point_canonical_authority"',
        '"hardware_candidate_execution"',
        '"vercel_authority": false',
    )
    _require(
        MAKEFILE_PATH,
        "validate: clean all test disassemble",
        "$(MAKE) iteration2-test",
        "$(MAKE) iteration3-test",
        "$(MAKE) iteration4-test",
        "$(MAKE) iteration4-token-test",
        "$(MAKE) iteration4-token-surface-test",
    )
    _require(
        FOCUSED_WORKFLOW_PATH,
        "Validate exact Pass 189 authority through Iteration 4",
        "make validate",
    )

    successor = _frozen_pass190_successor_evidence()
    return {
        "template_contract_commit": TEMPLATE_CONTRACT_COMMIT,
        "hqlh_contract_merge": HQLH_CONTRACT_MERGE,
        "runtime_implementation_commit": RUNTIME_IMPLEMENTATION_COMMIT,
        "iteration2_commit": ITERATION2_COMMIT,
        "iteration3_commit": ITERATION3_COMMIT,
        "iteration4_commit": ITERATION4_COMMIT,
        "token_lifecycle_commit": TOKEN_LIFECYCLE_COMMIT,
        "dns_integration_commit": DNS_INTEGRATION_COMMIT,
        "frozen_i136": FROZEN_I136,
        "source_blobs": {str(path): value for path, value in SOURCE_BLOBS.items()},
        "native_blobs": {str(path): value for path, value in NATIVE_BLOBS.items()},
        "pass190_successor": successor,
    }


def validate_pass189_historical_lineage() -> Dict[str, Any]:
    evidence = pass189_membrane_source_evidence()
    return {
        "ok": True,
        "classification": PASS189_CENSUS_CLASSIFICATION,
        "template_contract_commit": evidence["template_contract_commit"],
        "hqlh_contract_merge": evidence["hqlh_contract_merge"],
        "runtime_implementation_commit": evidence["runtime_implementation_commit"],
        "token_lifecycle_commit": evidence["token_lifecycle_commit"],
        "all_historical_layers_preserved": True,
    }


def validate_pass189_template_registry_boundary() -> Dict[str, Any]:
    pass189_membrane_source_evidence()
    return {
        "ok": True,
        "template_registered": True,
        "template_version": "1.3.1",
        "modality_tree_preserved": True,
        "runtime_authority": (
            "VM81_SINGLETON_HASH72_CHAIN_WITH_SQLITE_"
            "CALIBRATION_DEVICE_AND_PROVENANCE_PERSISTENCE"
        ),
        "real_driver_execution_pending": True,
    }


def validate_pass189_hqlh_exact_topology_boundary() -> Dict[str, Any]:
    pass189_membrane_source_evidence()
    return {
        "ok": True,
        "contextual_addresses": 51648192,
        "lo_shu_41_group": True,
        "xnor_truth_table": True,
        "signed_xnor_ternary": True,
        "hash72_glyphs": 72,
        "hash216_glyphs": 216,
        "deterministic_replay": True,
        "canonical_float_authority": False,
    }


def validate_pass189_calibration_causal_boundary() -> Dict[str, Any]:
    pass189_membrane_source_evidence()
    return {
        "ok": True,
        "classification": "HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS",
        "exact_rational_calibration": True,
        "persistent_sqlite_authority": True,
        "atomic_receipt_locked_worldlines": True,
        "checkpoint_recovery": True,
        "physical_candidates_require_measured_evidence_attestation_and_arm": True,
        "device_driver_dispatch_in_iteration2": False,
    }


def validate_pass189_device_adapter_boundary() -> Dict[str, Any]:
    pass189_membrane_source_evidence()
    return {
        "ok": True,
        "software_adapters": ["LOOPBACK", "FILE_SINK"],
        "bounded_operator_leases": True,
        "anti_replay_sequence": True,
        "watchdog_expiry": True,
        "revoke_disable_authority": True,
        "software_traces_are_hardware_measurements": False,
        "real_hardware_dispatch_authorized": False,
    }


def validate_pass189_driver_provenance_boundary() -> Dict[str, Any]:
    pass189_membrane_source_evidence()
    return {
        "ok": True,
        "payload_bound_quarantine": True,
        "conformance_evidence_separated": True,
        "dual_approval_promotion": True,
        "promotion_token_validation": True,
        "persistent_promotion_expiry": True,
        "trust_root_and_promotion_revocation": True,
        "deterministic_rollback": True,
        "hardware_promotion_class": "HARDWARE_CANDIDATE_NONEXECUTABLE",
        "hardware_candidate_execution": False,
    }


def validate_pass189_deployment_dns_boundary() -> Dict[str, Any]:
    pass189_membrane_source_evidence()
    return {
        "ok": True,
        "deployment_authority": "DIGITALOCEAN_SELF_HOSTED",
        "external_digitalocean_mutation_claimed": False,
        "vercel_authority": False,
        "ports": [8189, 8190, 8191, 8192],
        "pass189_pass190_8190_conflict_resolved_by_host_local_dns_identity": True,
        "dns_registry_hash72_witnessed": True,
    }


def validate_pass189_successor_binding() -> Dict[str, Any]:
    successor = pass189_membrane_source_evidence()["pass190_successor"]
    return {
        "ok": True,
        "successor_pass": successor["pass_number"],
        "successor_frozen_commit": successor["frozen_commit"],
        "successor_membrane_blob": successor["membrane_blob"],
        "successor_preserved": successor["successor_preserved"],
    }


def validate_pass189_no_new_authority() -> Dict[str, Any]:
    pass189_membrane_source_evidence()
    return {
        "ok": True,
        "i137_new_candidate_authority": False,
        "i137_new_canonical_mutation_authority": False,
        "i137_new_persistence_authority": False,
        "i137_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "float_canonical_authority": False,
        "real_hardware_execution_authorized": False,
        "external_digitalocean_mutation_claimed": False,
        "vercel_authority": False,
        "singleton_vm81_authority_remains_inherited": True,
    }


def pass189_surface_declaration() -> Dict[str, Any]:
    pass189_membrane_source_evidence()
    return {
        "surface_id": PASS189_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i137_pass189",
        "symbol": "validate_pass189_historical_lineage",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS-P189-HQLH-LS41-XNOR-P1-H72-H216-UPA",
            "HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS",
        ],
        "witness_schemas": [
            "HHSExactPass189CumulativeAuthorityWitnessV1",
            "HHSExactPass219InheritedPass189BindingV1",
        ],
        "validators": [
            PASS189_BIND_SYMBOL,
            "validate_pass189_historical_lineage",
        ],
        "guards": [
            "pass189_dual_contract_preservation",
            "pass189_hqlh_runtime_identity",
            "pass189_exact_topology",
            "pass189_calibration_in_progress",
            "pass189_hardware_nonexecution",
            "pass189_software_adapter_bounds",
            "pass189_driver_provenance_token_lifecycle",
            "pass189_deterministic_replay",
            "pass189_dns_port_separation",
            "pass189_frozen_pass190_successor",
            "pass189_no_new_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS189_CONTRACT_DRIFT",
            "REJECT_PASS189_RUNTIME_DRIFT",
            "REJECT_PASS189_TOPOLOGY_DRIFT",
            "REJECT_PASS189_CALIBRATION_STATUS_ESCALATION",
            "REJECT_PASS189_HARDWARE_EXECUTION_ESCALATION",
            "REJECT_PASS189_ADAPTER_BOUNDARY_DRIFT",
            "REJECT_PASS189_PROVENANCE_DRIFT",
            "REJECT_PASS189_REPLAY_DRIFT",
            "REJECT_PASS189_DEPLOYMENT_IDENTITY_DRIFT",
            "REJECT_PASS189_FROZEN_SUCCESSOR_DRIFT",
            "REJECT_PASS189_AUTHORITY_ESCALATION",
        ],
        "mutation_policy": "INHERITED_VM81_SINGLETON_HASH72_CHAIN_ONLY",
        "persistence_policy": "INHERITED_SQLITE_CALIBRATION_DEVICE_AND_PROVENANCE_STATE_ONLY",
        "boundedness_policy": "SOFTWARE_ADAPTER_EXECUTION_ONLY_REAL_HARDWARE_NONEXECUTABLE",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass189_membrane_manifest() -> Dict[str, Any]:
    evidence = pass189_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS189_NUMBER,
        "classification": PASS189_CLASSIFICATION,
        "census_classification": PASS189_CENSUS_CLASSIFICATION,
        "frozen_predecessor": evidence["frozen_i136"],
        "surface": pass189_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass189_membrane_preflight() -> Dict[str, Any]:
    declaration = pass189_surface_declaration()
    rows = [
        execute_surface_preflight(declaration, operation=operation)
        for operation in REQUIRED_OPERATIONS
    ]
    return {
        "schema": "HHS_PASS219_I137_PASS189_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS189_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass189_historical_lineage": validate_pass189_historical_lineage,
    "validate_pass189_template_registry_boundary": validate_pass189_template_registry_boundary,
    "validate_pass189_hqlh_exact_topology_boundary": validate_pass189_hqlh_exact_topology_boundary,
    "validate_pass189_calibration_causal_boundary": validate_pass189_calibration_causal_boundary,
    "validate_pass189_device_adapter_boundary": validate_pass189_device_adapter_boundary,
    "validate_pass189_driver_provenance_boundary": validate_pass189_driver_provenance_boundary,
    "validate_pass189_deployment_dns_boundary": validate_pass189_deployment_dns_boundary,
    "validate_pass189_successor_binding": validate_pass189_successor_binding,
    "validate_pass189_no_new_authority": validate_pass189_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 189 I137 membrane operation: {operation}")
    return OPERATIONS[operation]()
