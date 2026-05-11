# hhs_runtime_smoke_tests_v1.py
#
# HHS Runtime Smoke Certification Suite
#
# Canonical topology-aware runtime validation layer.
#
# Purpose:
# Validate:
#
# - runtime bootstrap coherence
# - authoritative kernel loading
# - receipt/replay continuity
# - runtime gate integrity
# - persistence availability
#
# This suite intentionally validates infrastructure coherence
# rather than deep feature correctness.
#
# Invariants:
# Δe = 0
# Ψ = 0
# Θ15 = true
# Ω = true

from __future__ import annotations

import importlib
import json
import pathlib
import sys
import traceback
from dataclasses import dataclass, asdict
from typing import Callable, Dict, List

from hhs_runtime.kernel_resolution import (
    REPO_ROOT,
    REQUIRED_KERNEL_SYMBOLS,
    resolve_authoritative_kernel,
    runtime_bootstrap_report,
)

# ============================================================
# RESULT STRUCTURES
# ============================================================

@dataclass
class SmokeResult:
    name: str
    ok: bool
    details: Dict


# ============================================================
# TEST REGISTRY
# ============================================================

SMOKE_TESTS: List[Callable[[], SmokeResult]] = []


def smoke_test(fn):
    SMOKE_TESTS.append(fn)
    return fn


# ============================================================
# HELPERS
# ============================================================

def result(
    name: str,
    ok: bool,
    **details,
) -> SmokeResult:
    return SmokeResult(
        name=name,
        ok=ok,
        details=details,
    )


# ============================================================
# TOPOLOGY
# ============================================================

@smoke_test
def test_runtime_bootstrap() -> SmokeResult:

    try:

        report = runtime_bootstrap_report()

        return result(
            "runtime_bootstrap",
            True,
            repo_root=str(report.repo_root),
            kernel_path=str(report.kernel_path),
            module_name=report.module_name,
            python=sys.executable,
        )

    except Exception as exc:

        return result(
            "runtime_bootstrap",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# KERNEL AUTHORITY
# ============================================================

@smoke_test
def test_kernel_authority_loaded() -> SmokeResult:

    try:

        kernel = resolve_authoritative_kernel()

        missing = []

        for symbol in REQUIRED_KERNEL_SYMBOLS:

            if not hasattr(kernel, symbol):
                missing.append(symbol)

        if missing:

            return result(
                "kernel_authority_loaded",
                False,
                missing_symbols=missing,
                kernel=str(kernel),
            )

        return result(
            "kernel_authority_loaded",
            True,
            verified_symbols=REQUIRED_KERNEL_SYMBOLS,
            kernel_module=kernel.__name__,
        )

    except Exception as exc:

        return result(
            "kernel_authority_loaded",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# REPLAY VERIFIER
# ============================================================

@smoke_test
def test_receipt_replay_verifier() -> SmokeResult:

    try:

        module = importlib.import_module(
            "hhs_receipt_replay_verifier_v1"
        )

        return result(
            "receipt_replay_verifier",
            True,
            module=str(module),
        )

    except Exception as exc:

        return result(
            "receipt_replay_verifier",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# DRIFT GATE / CONTROL FLOW
# ============================================================

@smoke_test
def test_runtime_gate_integrity() -> SmokeResult:

    try:

        module = importlib.import_module(
            "hhs_control_flow_gates_v1"
        )

        return result(
            "runtime_gate_integrity",
            True,
            module=str(module),
        )

    except Exception as exc:

        return result(
            "runtime_gate_integrity",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# DATABASE BRIDGE
# ============================================================

@smoke_test
def test_database_bridge_available() -> SmokeResult:

    try:

        module = importlib.import_module(
            "hhs_database_integration_layer_v1"
        )

        return result(
            "database_bridge_available",
            True,
            module=str(module),
        )

    except Exception as exc:

        return result(
            "database_bridge_available",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# REGRESSION SUITE IMPORT
# ============================================================

@smoke_test
def test_regression_suite_importable() -> SmokeResult:

    try:

        module = importlib.import_module(
            "hhs_regression_suite_v1"
        )

        return result(
            "regression_suite_importable",
            True,
            module=str(module),
        )

    except Exception as exc:

        return result(
            "regression_suite_importable",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# NO /mnt/data DRIFT
# ============================================================

@smoke_test
def test_no_mnt_data_dependency() -> SmokeResult:

    bad_refs = []

    for py_file in REPO_ROOT.rglob("*.py"):

        try:

            text = py_file.read_text(
                encoding="utf-8",
            )

            if "/mnt/data" in text:

                bad_refs.append(
                    str(py_file.relative_to(REPO_ROOT))
                )

        except Exception:
            continue

    if bad_refs:

        return result(
            "no_mnt_data_dependency",
            False,
            stale_refs=bad_refs,
        )

    return result(
        "no_mnt_data_dependency",
        True,
    )


# ============================================================
# PACKAGE TOPOLOGY
# ============================================================

@smoke_test
def test_runtime_package_topology() -> SmokeResult:

    try:

        runtime = importlib.import_module(
            "hhs_runtime"
        )

        path = pathlib.Path(
            runtime.__file__
        ).resolve()

        return result(
            "runtime_package_topology",
            True,
            runtime_path=str(path),
        )

    except Exception as exc:

        return result(
            "runtime_package_topology",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# EXECUTION
# ============================================================

def run_smoke_suite():

    results: List[SmokeResult] = []

    passed = 0
    failed = 0

    for test_fn in SMOKE_TESTS:

        r = test_fn()

        results.append(r)

        if r.ok:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(
            f"[{status}] {r.name}"
        )

        if not r.ok:

            details = json.dumps(
                r.details,
                indent=2,
                default=str,
            )

            print(details)

    summary = {
        "passed": passed,
        "failed": failed,
        "all_ok": failed == 0,
    }

    print("\n")
    print("=" * 60)
    print("HHS RUNTIME SMOKE SUMMARY")
    print("=" * 60)

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    return {
        "summary": summary,
        "results": [
            asdict(r) for r in results
        ],
    }


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    report = run_smoke_suite()

    if not report["summary"]["all_ok"]:
        raise SystemExit(1)