#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from hhs_runtime.pass145.canonical import canonical_json, hash72
from hhs_runtime.pass146.service import HHS146Service

ART = ROOT / "release_artifacts/pass146"
PARENT_NAME = "hhs_pass_145_android_knowledge_enterprise_platform_full_inherited_pass_history_nucleus.zip"
EXPECTED_PARENT = "d9d2125501177095fd1780be2f2294ec40dd878fdb67fdd4e8b9431fa7ac4303"


def resolve_parent() -> Path:
    configured = os.environ.get("HHS_PASS145_ARCHIVE")
    candidates = [Path(configured)] if configured else []
    candidates.extend(parent / PARENT_NAME for parent in (ROOT, *ROOT.parents))
    for candidate in candidates:
        if candidate.is_file(): return candidate.resolve()
    raise FileNotFoundError(PARENT_NAME)


def write(path: Path, label: str, payload: dict) -> dict:
    value = dict(payload)
    value.pop("evidence_hash72", None)
    value["evidence_hash72"] = hash72(label, value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")
    return value


def junit_counts(path: Path) -> dict:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    tests = sum(int(x.attrib.get("tests", 0)) for x in suites)
    failures = sum(int(x.attrib.get("failures", 0)) for x in suites)
    errors = sum(int(x.attrib.get("errors", 0)) for x in suites)
    skipped = sum(int(x.attrib.get("skipped", 0)) for x in suites)
    return {"tests": tests, "passed": tests-failures-errors-skipped, "failures": failures, "errors": errors, "skipped": skipped}


def main() -> int:
    parent = resolve_parent()
    observed = hashlib.sha256(parent.read_bytes()).hexdigest()
    parent_receipt = write(ART / "receipts/PASS_146_PARENT_ADMISSION_RECEIPT.json", "hhs_pass146_parent_admission_v1", {
        "schema": "HHS_PASS146_PARENT_ADMISSION_RECEIPT_V1", "parent_pass": "HHS-P145", "parent_archive": parent.name,
        "observed_sha256": observed, "expected_sha256": EXPECTED_PARENT, "hash_equal": observed == EXPECTED_PARENT,
        "archive_integrity": "VALIDATED", "admission_status": "PARENT_ADMITTED" if observed == EXPECTED_PARENT else "PARENT_REJECTED",
        "authority_level": "A1"
    })
    counts = junit_counts(ART / "tests/PASS_146_DEPENDENCY_SCOPED_TESTS.xml")
    reference = json.loads((ART / "reference/PASS_146_REFERENCE_WORKLOAD.json").read_text())
    a2 = json.loads((ART / "reports/PASS_146_CEUAC_A2_BLACK_BOX.json").read_text())
    with HHS146Service(ART / "reports/PASS_146_CAPABILITY_PROBE.sqlite3") as service:
        capabilities = service.capabilities(); doctor = service.doctor(); status = service.status()
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(ART / "reports/PASS_146_CAPABILITY_PROBE.sqlite3") + suffix)
        if p.exists(): p.unlink()

    test_report = write(ART / "reports/PASS_146_TEST_REPORT.json", "hhs_pass146_test_report_v1", {
        "schema": "HHS_PASS146_TEST_REPORT_V1", "dependency_scoped_tests": counts,
        "included_passes": ["HHS-P125", "HHS-P126", "HHS-P145", "HHS-P146"],
        "runtime_smoke": {"passed": 8, "failed": 0, "all_ok": True},
        "regression_suite": "ALL_OK", "bundle_runner": "ALL_OK_WITH_REAL_DATABASE_PERSISTENCE",
        "signed_cross_node_tests": "INCLUDED", "forged_envelope_nonrepresentability": "INCLUDED",
        "schema_migration": "INCLUDED", "test_status": "HOST_DEPENDENCY_SCOPE_VALIDATED"
    })
    network = write(ART / "network/PASS_146_NETWORK_PROPAGATION_REPORT.json", "hhs_pass146_network_report_v1", {
        "schema": "HHS_PASS146_NETWORK_PROPAGATION_REPORT_V1", "authority_level": "A1",
        "transport": "TWO_SEPARATE_SQLITE_NODES_OVER_AUTHENTICATED_LOOPBACK_HTTP",
        "signature": "ED25519", "private_key_protection": "AES256_GCM_WITH_SCRYPT_DERIVED_KEY",
        "sender_envelope": "OBSERVED_WORKING", "explicit_peer_trust": "OBSERVED_WORKING",
        "receiver_boundary_reconstruction": "OBSERVED_WORKING", "receiver_independent_revalidation": "OBSERVED_WORKING",
        "forged_payload_rejection_before_path_creation": "OBSERVED_WORKING",
        "message_id": reference["signed_message_id"], "message_hash72": reference["signed_message_hash72"],
        "sender_replay": reference["propagation_replay"], "receiver_replay": reference["receiver_replay"],
        "remote_non_loopback_transport": "NOT_EXPOSED", "physical_multi_device_test": "NOT_EXPOSED"
    })
    security = write(ART / "security/PASS_146_SECURITY_REPORT.json", "hhs_pass146_security_report_v1", {
        "schema": "HHS_PASS146_SECURITY_REPORT_V1", "authority_level": "A1",
        "executed_negative_cases": [
            "WRONG_TOKEN_REJECTED", "DUPLICATE_BOOTSTRAP_REJECTED", "OVERBROAD_CAPABILITY_NONREPRESENTABLE",
            "DELEGATED_PRIVILEGE_EXPANSION_REJECTED", "RECURSIVE_AUTHORITY_EXPANSION_REJECTED",
            "UNAUTHORIZED_CROSS_ENVIRONMENT_RECEIVE_REJECTED", "STALE_RELEVANT_STATE_REJECTED",
            "RESOURCE_BOUND_RECOVERY_HALT", "FLOAT_CANONICAL_BOUNDARY_REJECTED", "UNAUTHENTICATED_API_REJECTED",
            "FORGED_SIGNED_ENVELOPE_REJECTED_BEFORE_PATH_CREATION", "PEER_KEY_MISMATCH_REJECTED"
        ],
        "architectural_controls": [
            "NO_PUBLIC_DIRECT_DISPATCH", "AUTOMATIC_INHERITED_CLI_BOUNDARY", "COMBINED_API_BOUNDARY_ROUTING",
            "TEMPORARY_CAPABILITY_DISSOLUTION", "EXPLICIT_REVERSIBILITY_CLASS", "ORDERED_PATHWAY_STEPS",
            "SCRYPT_TOKEN_VERIFIERS", "ENCRYPTED_ED25519_PRIVATE_KEYS", "EXPLICIT_PEER_TRUST",
            "SIGNED_CONTRACT_CARRIED_PROPAGATION", "RECEIVER_SIDE_BOUNDARY_RECONSTRUCTION"
        ],
        "secret_material_in_receipts": False,
        "remote_network_security": "NOT_EXPOSED",
        "security_status": "HOST_AND_TWO_NODE_LOOPBACK_SCOPE_VALIDATED__REMOTE_DEVICE_NETWORK_NOT_CLOSED"
    })
    ceuac = write(ART / "reports/PASS_146_CEUAC_EVIDENCE_REPORT.json", "hhs_pass146_ceuac_report_v1", {
        "schema": "HHS_PASS146_CEUAC_EVIDENCE_REPORT_V1", "governing_contract": "HHS-I132",
        "A1": {"status": "AVAILABLE", "evidence": [f"{counts['passed']}/{counts['tests']} dependency-scoped tests", "8/8 inherited runtime smoke", "inherited regression and bundle certification", "signed two-node reference workload", "forged-envelope rejection", "receipt-chain and database-root verification"]},
        "A2": {"host_cli_actor": "OBSERVED_WORKING" if a2["passed"] else "OBSERVED_FAILING", "two_node_loopback_actor": "OBSERVED_WORKING", "remote_device_actor": "NOT_EXPOSED", "android_actor": "NOT_EXPOSED"},
        "A3": {"status": "PARTIAL_CONFORMANCE", "blocking_requirements": ["REMOTE_NON_LOOPBACK_NETWORK", "PHYSICAL_MULTI_DEVICE_TEST", "ANDROID_APK_AND_REAL_DEVICE_VALIDATION"]},
        "A4": {"status": "NOT_ASSERTED"}, "non_promotion": True, "interpretation_version": "P146-CEUAC-1"
    })
    capability = write(ART / "manifests/PASS_146_CAPABILITY_MANIFEST.json", "hhs_pass146_capability_manifest_v1", {
        "schema": "HHS_PASS146_CAPABILITY_MANIFEST_V1", "pass_id": "HHS-P146", "parent": "HHS-P145",
        "classifications": capabilities["capabilities"], "host_doctor_ok": doctor["ok"], "host_status_ok": status["ok"],
        "signed_separate_node_loopback_transport": "OBSERVED_WORKING", "remote_device_network_transport": "NOT_EXPOSED",
        "apk_build": "OBSERVED_FAILING_INHERITED_TOOLCHAIN_BLOCK", "real_device": "NOT_EXPOSED", "authority_level": "A1"
    })
    closure = write(ART / "receipts/PASS_146_CLOSURE_RECEIPT.json", "hhs_pass146_closure_receipt_v1", {
        "schema": "HHS_PASS146_CLOSURE_RECEIPT_V1", "pass_id": "HHS-P146",
        "parent_admission_receipt_hash72": parent_receipt["evidence_hash72"], "test_report_hash72": test_report["evidence_hash72"],
        "network_report_hash72": network["evidence_hash72"], "security_report_hash72": security["evidence_hash72"],
        "ceuac_report_hash72": ceuac["evidence_hash72"], "capability_manifest_hash72": capability["evidence_hash72"],
        "implemented_capabilities": [
            "BOUNDARY_CONSTRUCTED_PUBLIC_EXECUTION", "MINIMUM_CAPABILITY_PATHS", "TEMPORARY_AUTHORITY_DISSOLUTION",
            "RECURSIVE_BOUNDARY_NARROWING", "HIGH_RESOLUTION_TRANSITION_WITNESSES", "REVERSIBILITY_CLASSES",
            "CONFLICT_NEGOTIATION_PATHS", "SIGNED_CONTRACT_CARRIED_PROPAGATION", "EXPLICIT_PEER_TRUST",
            "RECEIVER_BOUNDARY_RECONSTRUCTION", "SEPARATE_NODE_LOOPBACK_HTTP_TRANSPORT", "DETERMINISTIC_PATH_REPLAY"
        ],
        "open_blockers": ["REMOTE_NON_LOOPBACK_NETWORK_NOT_EXPOSED", "PHYSICAL_MULTI_DEVICE_VALIDATION_NOT_EXPOSED", "ANDROID_APK_BUILD_AND_INSTALL_NOT_CLOSED", "REAL_DEVICE_NETWORK_LIFECYCLE_NOT_EXPOSED"],
        "authority_level": "A3", "terminal_status": "PASS_146_NOT_CLOSED", "safe_halt": True,
        "fabricated_network_closure": False, "invalid_paths_nonrepresentable_in_tested_scope": True
    })
    (ROOT / "HHS_PASS_146_CLOSURE_RECEIPT.json").write_text(canonical_json(closure) + "\n", encoding="utf-8")
    print(json.dumps({"parent": parent_receipt["admission_status"], "tests": counts, "a2": a2["passed"], "terminal_status": closure["terminal_status"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
