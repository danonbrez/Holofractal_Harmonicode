"""
hhs_v1_bundle_runner.py

Bundle certification runner for the HARMONICODE General Programming Environment V1.

Purpose
-------
Run the full local validation sequence and emit one certification report.

Sequence
--------
1. kernel authority / runtime smoke tests
2. regression suite
3. demo .hhsprog execution
4. .hhsrun replay verification
5. optional database persistence check
6. final bundle certification report

Run:
    python hhs_v1_bundle_runner.py

Outputs:
    /mnt/data/hhs_v1_bundle_certification_report.json
    /mnt/data/hhs_v1_demo_run.hhsrun
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import traceback

from hhs_runtime_smoke_tests_v1 import HHSSmokeTestSuiteV1
from hhs_regression_suite_v1 import HHSRegressionSuiteV1
from hhs_program_format_and_cli_v1 import (
    demo_program,
    execute_program,
    verify_run_file,
    write_json,
)
from hhs_receipt_replay_verifier_v1 import HHSReceiptReplayVerifierV1

try:
    from hhs_database_integration_layer_v1 import HHSRuntimeDatabaseBridgeV1
except Exception:
    HHSRuntimeDatabaseBridgeV1 = None


REPORT_PATH = Path("/mnt/data/hhs_v1_bundle_certification_report.json")
DEMO_PROGRAM_PATH = Path("/mnt/data/hhs_v1_demo_program.hhsprog")
DEMO_RUN_PATH = Path("/mnt/data/hhs_v1_demo_run.hhsrun")
DB_PATH = Path("/mnt/data/hhs_v1_bundle_certification.sqlite3")


def safe_run(name: str, fn):
    try:
        return {
            "name": name,
            "ok": True,
            "result": fn(),
        }
    except Exception as exc:
        return {
            "name": name,
            "ok": False,
            "error": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }


def run_smoke_tests() -> Dict[str, Any]:
    suite = HHSSmokeTestSuiteV1()
    return suite.run_all()


def run_regression_suite() -> Dict[str, Any]:
    suite = HHSRegressionSuiteV1()
    return suite.run_all()


def run_demo_program() -> Dict[str, Any]:
    program = demo_program()
    write_json(DEMO_PROGRAM_PATH, program)
    result = execute_program(program, persist=False)
    write_json(DEMO_RUN_PATH, result)
    return {
        "program_path": str(DEMO_PROGRAM_PATH),
        "run_path": str(DEMO_RUN_PATH),
        "run_result": result,
    }


def verify_demo_run() -> Dict[str, Any]:
    return verify_run_file(DEMO_RUN_PATH)


def run_database_persistence_check() -> Dict[str, Any]:
    if HHSRuntimeDatabaseBridgeV1 is None:
        return {
            "ok": False,
            "reason": "database bridge unavailable",
        }

    program = demo_program()
    result = execute_program(program, persist=False)

    # Store receipts from a temporary runner reconstruction is not possible
    # from only result payload, so use bridge tables directly through store_trace.
    bridge = HHSRuntimeDatabaseBridgeV1(db_path=DB_PATH)
    try:
        trace = bridge.store_trace(
            result["receipts"],
            program_name="HHS_V1_BUNDLE_CERTIFICATION_DEMO",
            metadata={
                "source": "hhs_v1_bundle_runner",
                "program_hash72": result["program_hash72"],
            },
        )
        quarantine = bridge.quarantine_report()
        loaded = bridge.load_trace(trace.trace_hash72)
        return {
            "ok": True,
            "db_path": str(DB_PATH),
            "trace": trace.to_dict(),
            "loaded_trace": loaded,
            "quarantine_report": quarantine,
        }
    finally:
        bridge.close()


def build_certification_report() -> Dict[str, Any]:
    smoke = safe_run("smoke_tests", run_smoke_tests)
    regression = safe_run("regression_suite", run_regression_suite)
    demo = safe_run("demo_program", run_demo_program)
    replay = safe_run("demo_replay_verify", verify_demo_run)
    database = safe_run("database_persistence_check", run_database_persistence_check)

    checks = [smoke, regression, demo, replay, database]

    all_ok = True
    reasons = []

    for check in checks:
        if not check["ok"]:
            all_ok = False
            reasons.append(f"{check['name']} raised {check.get('error')}: {check.get('message')}")
            continue

        result = check["result"]

        if check["name"] == "smoke_tests" and not result.get("all_ok"):
            all_ok = False
            reasons.append("smoke_tests reported failures")

        if check["name"] == "regression_suite" and not result.get("all_ok"):
            all_ok = False
            reasons.append("regression_suite reported failures")

        if check["name"] == "demo_program":
            run_result = result.get("run_result", {})
            if not run_result.get("all_ok"):
                all_ok = False
                reasons.append("demo program did not fully lock")

        if check["name"] == "demo_replay_verify":
            verification = result.get("verification", {})
            if not verification.get("ok"):
                all_ok = False
                reasons.append("demo replay verification failed")

        if check["name"] == "database_persistence_check":
            if not result.get("ok"):
                all_ok = False
                reasons.append("database persistence check failed")

    report = {
        "certification": "HHS_GENERAL_PROGRAMMING_ENVIRONMENT_V1",
        "all_ok": all_ok,
        "status": "CERTIFIED_LOCKED" if all_ok else "CERTIFICATION_FAILED",
        "failure_reasons": reasons,
        "artifacts": {
            "demo_program": str(DEMO_PROGRAM_PATH),
            "demo_run": str(DEMO_RUN_PATH),
            "database": str(DB_PATH),
            "report": str(REPORT_PATH),
        },
        "checks": checks,
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    report = build_certification_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["all_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
