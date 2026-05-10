# ============================================================================
# hhs_runtime/runtime_lock_certifier_v1.py
# HARMONICODE / HHS
# LOCKED STATE CERTIFICATION AUTHORITY
#
# PURPOSE
# -------
# Canonical deterministic runtime certification layer for:
#
#   - runtime integrity verification
#   - receipt-chain verification
#   - replay continuity verification
#   - gate-route integrity
#   - authority-mode validation
#   - AGENTS compliance verification
#   - LOCKED certification generation
#
# This file is the authoritative operational integrity verifier.
#
# ============================================================================

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any

# ============================================================================
# CONSTANTS
# ============================================================================

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

CERT_DIR = (
    REPO_ROOT
    / "runtime_certification"
)

CERT_DIR.mkdir(
    exist_ok=True,
    parents=True
)

# ============================================================================
# RUNTIME MODES
# ============================================================================

MODE_SANDBOX = "sandbox"

MODE_EXTERNAL_KERNEL = "external-kernel"

MODE_MIXED = "mixed"

# ============================================================================
# CERTIFICATION STRUCTURES
# ============================================================================

@dataclass
class CertificationResult:

    passed: bool

    category: str

    message: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

# ----------------------------------------------------------------------------

@dataclass
class LockCertificationReport:

    timestamp: float

    runtime_mode: str

    locked: bool

    results: List[CertificationResult]

    totals: Dict[str, int]

# ============================================================================
# CERTIFIER
# ============================================================================

class HHSRuntimeLockCertifier:

    """
    Canonical LOCKED-state certification authority.
    """

    def __init__(self):

        self.results: List[
            CertificationResult
        ] = []

        self.runtime_mode = MODE_SANDBOX

    # =====================================================================
    # UTILITIES
    # =====================================================================

    def add_result(
        self,
        passed: bool,
        category: str,
        message: str,
        metadata: Optional[Dict] = None
    ):

        self.results.append(

            CertificationResult(

                passed=passed,

                category=category,

                message=message,

                metadata=metadata or {}
            )
        )

    # ---------------------------------------------------------------------

    def result_totals(self):

        passed = 0
        failed = 0

        for result in self.results:

            if result.passed:
                passed += 1
            else:
                failed += 1

        return {

            "passed": passed,

            "failed": failed,

            "total": passed + failed
        }

    # =====================================================================
    # FILE VALIDATION
    # =====================================================================

    def verify_required_files(self):

        required = [

            "hhs_backend/server.py",

            "hhs_backend/runtime/runtime_event_bus.py",

            "hhs_backend/websocket/runtime_stream_manager.py",

            "hhs_python/runtime/hhs_runtime_controller.py",

            "hhs_python/runtime/hhs_ctypes_bridge.py",

            "hhs_graph/hhs_multimodal_receipt_graph_v1.py",

            "hhs_runtime/c/hhs_runtime_abi.h",

            "hhs_runtime/c/hhs_runtime_abi.c",
        ]

        for relpath in required:

            path = REPO_ROOT / relpath

            if path.exists():

                self.add_result(

                    True,

                    "required_files",

                    f"Found: {relpath}"
                )

            else:

                self.add_result(

                    False,

                    "required_files",

                    f"Missing: {relpath}"
                )

    # =====================================================================
    # AGENTS COMPLIANCE
    # =====================================================================

    def verify_agents_contracts(self):

        agents_path = REPO_ROOT / "AGENTS.md"

        if not agents_path.exists():

            self.add_result(

                False,

                "agents",

                "AGENTS.md missing"
            )

            return

        text = agents_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        required_refs = [

            "hhs_v1_bundle_runner.py",

            "hhs_runtime_smoke_tests_v1.py",

            "hhs_regression_suite_v1.py",
        ]

        for ref in required_refs:

            if ref in text:

                self.add_result(

                    True,

                    "agents",

                    f"AGENTS reference present: {ref}"
                )

            else:

                self.add_result(

                    False,

                    "agents",

                    f"AGENTS reference missing: {ref}"
                )

    # =====================================================================
    # BUNDLE RUNNER
    # =====================================================================

    def verify_bundle_runner(self):

        runner = (
            REPO_ROOT
            / "hhs_v1_bundle_runner.py"
        )

        if not runner.exists():

            self.add_result(

                False,

                "bundle_runner",

                "Bundle runner missing"
            )

            return

        self.add_result(

            True,

            "bundle_runner",

            "Bundle runner present"
        )

    # =====================================================================
    # RUNTIME MODE
    # =====================================================================

    def detect_runtime_mode(self):

        runtime_core = (
            REPO_ROOT
            / "hhs_runtime"
            / "core_sandbox"
        )

        if runtime_core.exists():

            self.runtime_mode = MODE_SANDBOX

            self.add_result(

                True,

                "runtime_mode",

                "Sandbox runtime detected"
            )

        else:

            self.runtime_mode = MODE_MIXED

            self.add_result(

                False,

                "runtime_mode",

                "Sandbox runtime missing"
            )

    # =====================================================================
    # RECEIPT CHAIN
    # =====================================================================

    def verify_receipt_chain_integrity(self):

        graph_path = (
            REPO_ROOT
            / "hhs_graph"
            / "hhs_multimodal_receipt_graph_v1.py"
        )

        if not graph_path.exists():

            self.add_result(

                False,

                "receipt_chain",

                "Graph memory layer missing"
            )

            return

        text = graph_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        required_terms = [

            "receipt_hash72",

            "parent_id",

            "replay_chain",

            "ingest_runtime_state",
        ]

        ok = True

        missing = []

        for term in required_terms:

            if term not in text:

                ok = False

                missing.append(term)

        if ok:

            self.add_result(

                True,

                "receipt_chain",

                "Receipt continuity structures verified"
            )

        else:

            self.add_result(

                False,

                "receipt_chain",

                "Receipt continuity structures incomplete",

                metadata={
                    "missing": missing
                }
            )

    # =====================================================================
    # GATE ROUTE VERIFICATION
    # =====================================================================

    def verify_gate_route_integrity(self):

        runtime_controller = (
            REPO_ROOT
            / "hhs_python"
            / "runtime"
            / "hhs_runtime_controller.py"
        )

        if not runtime_controller.exists():

            self.add_result(

                False,

                "gate_routes",

                "Runtime controller missing"
            )

            return

        text = runtime_controller.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        required = [

            "receipt_commit",

            "runtime_step",

            "runtime_halt",
        ]

        ok = True

        missing = []

        for term in required:

            if term not in text:

                ok = False

                missing.append(term)

        if ok:

            self.add_result(

                True,

                "gate_routes",

                "Audited runtime routes verified"
            )

        else:

            self.add_result(

                False,

                "gate_routes",

                "Runtime gate routes incomplete",

                metadata={
                    "missing": missing
                }
            )

    # =====================================================================
    # STATIC BYPASS SCAN
    # =====================================================================

    def scan_for_bypass_patterns(self):

        suspicious = [

            "bypass",

            "skip_receipt",

            "unsafe_commit",

            "force_commit",
        ]

        hits = []

        for path in REPO_ROOT.rglob("*.py"):

            try:

                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                for token in suspicious:

                    if token in text:

                        hits.append({

                            "file": str(path),

                            "token": token
                        })

            except Exception:
                pass

        if hits:

            self.add_result(

                False,

                "bypass_scan",

                "Potential bypass patterns detected",

                metadata={
                    "hits": hits
                }
            )

        else:

            self.add_result(

                True,

                "bypass_scan",

                "No bypass patterns detected"
            )

    # =====================================================================
    # TEST EXECUTION
    # =====================================================================

    def execute_test_script(
        self,
        script_name: str
    ):

        script = REPO_ROOT / script_name

        if not script.exists():

            self.add_result(

                False,

                "tests",

                f"Missing test script: {script_name}"
            )

            return

        try:

            result = subprocess.run(

                [sys.executable, str(script)],

                cwd=str(REPO_ROOT),

                capture_output=True,

                text=True,

                timeout=120
            )

            passed = result.returncode == 0

            self.add_result(

                passed,

                "tests",

                f"{script_name} exit={result.returncode}",

                metadata={

                    "stdout":
                        result.stdout[-4000:],

                    "stderr":
                        result.stderr[-4000:]
                }
            )

        except Exception as e:

            self.add_result(

                False,

                "tests",

                f"{script_name} execution error",

                metadata={
                    "error": str(e)
                }
            )

    # =====================================================================
    # HASH SNAPSHOT
    # =====================================================================

    def generate_repo_snapshot(self):

        hashes = {}

        for path in REPO_ROOT.rglob("*.py"):

            try:

                data = path.read_bytes()

                digest = hashlib.sha256(
                    data
                ).hexdigest()

                hashes[str(path.relative_to(REPO_ROOT))] = digest

            except Exception:
                pass

        snapshot_path = (
            CERT_DIR
            / "topology_report.json"
        )

        snapshot_path.write_text(

            json.dumps(
                hashes,
                indent=2
            ),

            encoding="utf-8"
        )

        self.add_result(

            True,

            "snapshot",

            "Repository topology snapshot generated"
        )

    # =====================================================================
    # CERTIFICATION
    # =====================================================================

    def certify(self):

        self.detect_runtime_mode()

        self.verify_required_files()

        self.verify_agents_contracts()

        self.verify_bundle_runner()

        self.verify_receipt_chain_integrity()

        self.verify_gate_route_integrity()

        self.scan_for_bypass_patterns()

        self.execute_test_script(
            "hhs_runtime_smoke_tests_v1.py"
        )

        self.execute_test_script(
            "hhs_regression_suite_v1.py"
        )

        self.generate_repo_snapshot()

        totals = self.result_totals()

        locked = totals["failed"] == 0

        report = LockCertificationReport(

            timestamp=time.time(),

            runtime_mode=self.runtime_mode,

            locked=locked,

            results=self.results,

            totals=totals
        )

        self.write_reports(report)

        return report

    # =====================================================================
    # REPORT WRITING
    # =====================================================================

    def write_reports(
        self,
        report: LockCertificationReport
    ):

        # --------------------------------------------------------------
        # LOCK REPORT
        # --------------------------------------------------------------

        lock_report = {

            "timestamp":
                report.timestamp,

            "runtime_mode":
                report.runtime_mode,

            "locked":
                report.locked,

            "totals":
                report.totals,

            "results": [

                {
                    "passed":
                        r.passed,

                    "category":
                        r.category,

                    "message":
                        r.message,

                    "metadata":
                        r.metadata
                }

                for r in report.results
            ]
        }

        (
            CERT_DIR
            / "lock_report.json"
        ).write_text(

            json.dumps(
                lock_report,
                indent=2
            ),

            encoding="utf-8"
        )

        # --------------------------------------------------------------
        # REPLAY REPORT
        # --------------------------------------------------------------

        replay_report = {

            "receipt_chain_verified":
                any(
                    r.category == "receipt_chain"
                    and r.passed

                    for r in report.results
                ),

            "gate_routes_verified":
                any(
                    r.category == "gate_routes"
                    and r.passed

                    for r in report.results
                )
        }

        (
            CERT_DIR
            / "replay_report.json"
        ).write_text(

            json.dumps(
                replay_report,
                indent=2
            ),

            encoding="utf-8"
        )

        # --------------------------------------------------------------
        # INVARIANT REPORT
        # --------------------------------------------------------------

        invariant_report = {

            "runtime_mode":
                report.runtime_mode,

            "bypass_scan_passed":
                any(
                    r.category == "bypass_scan"
                    and r.passed

                    for r in report.results
                ),

            "tests": [

                r.message

                for r in report.results

                if r.category == "tests"
            ]
        }

        (
            CERT_DIR
            / "invariant_report.json"
        ).write_text(

            json.dumps(
                invariant_report,
                indent=2
            ),

            encoding="utf-8"
        )

    # =====================================================================
    # SUMMARY
    # =====================================================================

    def print_summary(
        self,
        report: LockCertificationReport
    ):

        print()

        print("=" * 72)

        print("HHS LOCK CERTIFICATION REPORT")

        print("=" * 72)

        print()

        print("Runtime Mode:", report.runtime_mode)

        print("LOCKED:", report.locked)

        print()

        print("Totals:")

        print(report.totals)

        print()

        for result in report.results:

            status = "PASS" if result.passed else "FAIL"

            print(
                f"[{status}] "
                f"{result.category}: "
                f"{result.message}"
            )

# ============================================================================
# SELF TEST
# ============================================================================

def certifier_self_test():

    certifier = HHSRuntimeLockCertifier()

    report = certifier.certify()

    certifier.print_summary(report)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    certifier_self_test()