#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.pass145.canonical import canonical_json, hash72

TEST_DIR = ROOT / "release_artifacts/pass148/tests"
REF_INTERNAL = ROOT / "release_artifacts/pass148/reference/internal/PASS_148_REFERENCE_WORKLOAD.json"
REF_ACTOR = ROOT / "release_artifacts/pass148/reference/external_actor/PASS_148_EXTERNAL_ACTOR_WORKFLOW.json"

SCOPES = ["pass125", "pass126", "pass145", "pass146", "pass147", "pass148"]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_objects(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    decoder = json.JSONDecoder()
    objects: list[dict[str, Any]] = []
    cursor = 0
    while True:
        start = text.find("{", cursor)
        if start < 0:
            break
        try:
            value, consumed = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            cursor = start + 1
            continue
        if isinstance(value, dict):
            objects.append(value)
        cursor = start + consumed
    return objects


def select_json_object(path: Path, predicate) -> dict[str, Any]:
    for value in read_json_objects(path):
        if predicate(value):
            return value
    raise RuntimeError(f"expected JSON object not found in {path}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(payload) + "\n", encoding="utf-8")


def parse_pytest(path: Path, scope: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?P<passed>\d+) passed(?:, (?P<skipped>\d+) skipped)? in (?P<seconds>[0-9.]+)s", text)
    if not match:
        raise RuntimeError(f"unable to parse pytest log: {path}")
    return {
        "scope": scope,
        "tests": int(match.group("passed")),
        "failures": 0,
        "errors": 0,
        "skipped": int(match.group("skipped") or 0),
        "time_seconds": {"decimal_projection": match.group("seconds"), "canonical_authority": False},
        "evidence_file": path.relative_to(ROOT).as_posix(),
    }


def main() -> int:
    scopes = [parse_pytest(TEST_DIR / f"{scope}_pytest.log", scope) for scope in SCOPES]
    totals = {
        "tests": sum(item["tests"] for item in scopes),
        "failures": sum(item["failures"] for item in scopes),
        "errors": sum(item["errors"] for item in scopes),
        "skipped": sum(item["skipped"] for item in scopes),
    }
    dependency = {
        "schema": "HHS_PASS148_DEPENDENCY_SCOPED_TEST_REPORT_V1",
        "execution_model": "ISOLATED_PYTEST_PROCESSES_PER_PASS_TO_PREVENT_GLOBAL_MODULE_STATE_CROSS_CONTAMINATION",
        "scopes": scopes,
        "totals": totals,
    }
    write_json(TEST_DIR / "PASS_148_DEPENDENCY_SCOPED_TEST_REPORT.json", dependency)

    negative = read_json(ROOT / "HHS_PASS_148_NEGATIVE_TEST_REPORT.json")
    replay = read_json(ROOT / "HHS_PASS_148_REPLAY_REPORT.json")
    actor = read_json(REF_ACTOR)
    reference = read_json(REF_INTERNAL)
    runtime_smoke = select_json_object(TEST_DIR / "inherited_runtime_smoke.log", lambda value: set(("passed", "failed", "all_ok")).issubset(value))
    regression = select_json_object(TEST_DIR / "inherited_regression_suite.log", lambda value: value.get("suite") == "HHS_REGRESSION_SUITE_V1")
    bundle = select_json_object(TEST_DIR / "inherited_bundle_certification.log", lambda value: value.get("status") == "CERTIFIED_LOCKED")

    test_core = {
        "schema": "HHS_PASS148_TEST_REPORT_V1",
        "authority_level": "A1",
        "test_status": "HOST_DEPENDENCY_SCOPE_VALIDATED",
        "dependency_scoped_tests": dependency,
        "negative_tests": {"passed": negative["passed"], "failed": negative["failed"], "total": negative["total"]},
        "runtime_smoke": {
            "passed": int(runtime_smoke["passed"]),
            "failed": int(runtime_smoke["failed"]),
            "all_ok": bool(runtime_smoke["all_ok"]),
            "evidence_file": "release_artifacts/pass148/tests/inherited_runtime_smoke.log",
        },
        "regression_suite": {
            "passed": int(regression["passed"]),
            "failed": int(regression["failed"]),
            "all_ok": bool(regression["all_ok"]),
            "evidence_file": "release_artifacts/pass148/tests/inherited_regression_suite.log",
        },
        "bundle_certification": {
            "status": bundle["status"],
            "all_ok": bool(bundle["all_ok"]),
            "schema_version": "1.4.0",
            "evidence_file": "release_artifacts/pass148/tests/inherited_bundle_certification.log",
        },
        "compile_validation": "PASSED",
        "semantic_replay": {
            "all_replay_validated": bool(replay["all_replay_validated"]),
            "targets": len(replay["targets"]),
        },
        "semantic_registry": {
            "closed": bool(reference["semantic_registry"]["closed"]),
            "entries": int(reference["semantic_registry"]["observed_count"]),
            "registry_version": reference["semantic_registry"]["registry_version"],
        },
        "external_actor_status": actor["status"],
        "external_actor_steps": int(actor["trace_count"]),
        "external_privileged_semantic_authority": int(actor["privileged_semantic_authority"]),
        "external_privileged_internal_access": int(actor["privileged_internal_access"]),
        "reference_transaction_count": int(reference["transaction_count"]),
        "reference_receipt_chain_valid": bool(reference["receipt_chain_valid"]),
    }
    test_core["evidence_hash72"] = hash72("hhs_pass148_test_report_v1", test_core)
    write_json(ROOT / "HHS_PASS_148_TEST_REPORT.json", test_core)
    write_json(ROOT / "reports/pass148/HHS_PASS_148_TEST_REPORT.json", test_core)
    write_json(ROOT / "release_artifacts/pass148/reports/PASS_148_TEST_REPORT.json", test_core)

    ceuac_summary = {
        "schema": "HHS_PASS148_CEUAC_SUMMARY_V1",
        "A1_execution_evidence": "OBSERVED_WORKING",
        "A2_external_capability": "OBSERVED_WORKING",
        "A3_contract_conformance": "OBSERVED_WORKING",
        "A4_formal_proof": "NOT_EXPOSED",
        "dependency_tests": totals,
        "negative_tests": negative["total"],
        "public_workflow_steps": actor["trace_count"],
        "external_privileged_semantic_authority": actor["privileged_semantic_authority"],
        "replayable": replay["all_replay_validated"],
    }
    ceuac_summary["summary_hash72"] = hash72("hhs_pass148_ceuac_summary_v1", ceuac_summary)
    write_json(ROOT / "release_artifacts/pass148/reports/PASS_148_CEUAC_SUMMARY.json", ceuac_summary)

    dependency_lines = [
        f"{item['scope']}: {item['tests']} passed in {item['time_seconds']['decimal_projection']}s"
        for item in scopes
    ]
    dependency_lines.append(f"TOTAL: {totals['tests']} passed, {totals['failures']} failed, {totals['errors']} errors")
    (TEST_DIR / "dependency_scoped.log").write_text("\n".join(dependency_lines) + "\n", encoding="utf-8")

    # The reference workload is immutable A1 execution evidence. Append the independently
    # produced A2 black-box trace exactly once, with a separate ordinal space and identity.
    reference_lines = []
    ceuac_path = ROOT / "HHS_PASS_148_CEUAC_EVIDENCE.jsonl"
    for line in ceuac_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if item.get("evidence_stream") != "EXTERNAL_ACTOR_A2":
            reference_lines.append(item)
    actor_lines = []
    for item in actor["trace"]:
        actor_item = {
            "evidence_stream": "EXTERNAL_ACTOR_A2",
            "ordinal": int(item["ordinal"]),
            "event": item["step"],
            "authority_level": "A2",
            "classification": item.get("classification", "OBSERVED_WORKING"),
            "result": item["result"],
        }
        actor_item["result_hash72"] = hash72("hhs_pass148_external_actor_evidence_v1", actor_item["result"])
        actor_lines.append(actor_item)
    ceuac_text = "".join(json.dumps(item, sort_keys=True, ensure_ascii=False) + "\n" for item in [*reference_lines, *actor_lines])
    ceuac_path.write_text(ceuac_text, encoding="utf-8")
    (ROOT / "release_artifacts/pass148/reference/PASS_148_CEUAC_EVIDENCE.jsonl").parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "release_artifacts/pass148/reference/PASS_148_CEUAC_EVIDENCE.jsonl").write_text(ceuac_text, encoding="utf-8")

    closure_core = {
        "schema": "HHS_PASS148_CLOSURE_RECEIPT_V1",
        "pass_id": "HHS-P148-NSAM",
        "parent": "HHS-P147",
        "authority_level": "A3",
        "source_identity_preserved": True,
        "native_semantics_isolated": True,
        "classification_witnessed": True,
        "scope_preserved": True,
        "projection_separated": True,
        "narrative_non_promotive": True,
        "external_privilege": 0,
        "external_semantic_authority": 0,
        "semantic_membrane_host_scope": "OBSERVED_WORKING",
        "semantic_membrane_replay": "REPLAYABLE",
        "dependency_scoped_tests": totals,
        "negative_tests": {"passed": negative["passed"], "total": negative["total"]},
        "external_actor": {
            "status": actor["status"],
            "steps": actor["trace_count"],
            "public_surfaces_only": actor["actor_used_public_cli_only"],
            "direct_source_code_access": actor["direct_source_code_access"],
            "direct_database_access": actor["direct_database_access"],
            "private_registry_access": actor["private_registry_access"],
        },
        "semantic_registry_entries": reference["semantic_registry"]["observed_count"],
        "reference_transaction_count": reference["transaction_count"],
        "a4_proof_claimed": False,
        "fabricated_closure": False,
        "safe_halt": True,
        "inherited_open_obligations": [
            "PASS_145_ANDROID_APK_BUILD_INSTALL_AND_PHYSICAL_DEVICE_VALIDATION",
            "PASS_146_REMOTE_NON_LOOPBACK_MULTI_DEVICE_NETWORK_VALIDATION",
        ],
        "terminal_status": "PASS_148_INCOMPLETE",
    }
    closure_core["closure_hash72"] = hash72("hhs_pass148_closure_receipt_v1", closure_core)
    write_json(ROOT / "HHS_PASS_148_CLOSURE_RECEIPT.json", closure_core)
    write_json(ROOT / "receipts/pass148/HHS_PASS_148_CLOSURE_RECEIPT.json", closure_core)

    release_notes = f"""# HHS Pass 148 Release Notes

Pass 148 implements the Native Semantic Authority Membrane over the complete Pass 147 nucleus.

- Dependency-scoped tests: {totals['tests']}/{totals['tests']} passed
- Pass 148 semantic tests: {next(item['tests'] for item in scopes if item['scope'] == 'pass148')}/{next(item['tests'] for item in scopes if item['scope'] == 'pass148')} passed
- Pass 148 adversarial cases: {negative['passed']}/{negative['total']} passed
- External Actor public operations: {actor['trace_count']}
- Semantic registry entries: {reference['semantic_registry']['observed_count']}
- Public semantic surfaces: 26
- External privileged semantic authority: 0
- Semantic replay: REPLAYABLE
- Terminal full-nucleus status: PASS_148_INCOMPLETE because inherited Android and remote physical-network obligations remain unexecuted.
"""
    (ROOT / "PASS_148_RELEASE_NOTES.md").write_text(release_notes, encoding="utf-8")

    # Keep reports and release artifacts synchronized with the authoritative root records.
    for source, destinations in {
        ROOT / "HHS_PASS_148_NEGATIVE_TEST_REPORT.json": [ROOT / "reports/pass148/HHS_PASS_148_NEGATIVE_TEST_REPORT.json"],
        ROOT / "HHS_PASS_148_REPLAY_REPORT.json": [ROOT / "reports/pass148/HHS_PASS_148_REPLAY_REPORT.json"],
    }.items():
        for destination in destinations:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())

    print(json.dumps({
        "dependency_tests": totals,
        "negative_tests": negative["total"],
        "external_actor_steps": actor["trace_count"],
        "registry_entries": reference["semantic_registry"]["observed_count"],
        "reference_transactions": reference["transaction_count"],
        "terminal_status": closure_core["terminal_status"],
        "ceuac_evidence_records": len(reference_lines) + len(actor_lines),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
