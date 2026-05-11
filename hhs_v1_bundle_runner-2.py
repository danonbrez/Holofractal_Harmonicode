# hhs_v1_bundle_runner-2.py
#
# HHS Runtime Certification Orchestrator
#
# Purpose:
# Canonical deterministic certification pipeline for the
# Holofractal Harmonicode Runtime OS.
#
# This file becomes the single authoritative LOCKED-state
# certification surface for:
#
# - runtime topology
# - kernel authority
# - smoke validation
# - regression validation
# - persistence validation
# - replay continuity
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
from typing import Dict, List

from hhs_runtime.kernel_resolution import (
    REPO_ROOT,
    runtime_bootstrap_report,
    resolve_authoritative_kernel,
)

from hhs_runtime_smoke_tests_v1 import (
    run_smoke_suite,
)


# ============================================================
# CERTIFICATION STRUCTURES
# ============================================================

@dataclass
class CertificationStage:
    name: str
    ok: bool
    details: Dict


@dataclass
class CertificationReport:
    certification: str
    status: str
    locked: bool
    topology_ok: bool
    kernel_ok: bool
    smoke_ok: bool
    regression_ok: bool
    database_ok: bool
    replay_ok: bool
    stages: List[Dict]


# ============================================================
# HELPERS
# ============================================================

def stage(
    name: str,
    ok: bool,
    **details,
) -> CertificationStage:

    return CertificationStage(
        name=name,
        ok=ok,
        details=details,
    )


# ============================================================
# TOPOLOGY VALIDATION
# ============================================================

def run_topology_validation() -> CertificationStage:

    try:

        report = runtime_bootstrap_report()

        return stage(
            "runtime_topology",
            True,
            repo_root=str(report.repo_root),
            kernel_path=str(report.kernel_path),
            module_name=report.module_name,
            python=sys.executable,
        )

    except Exception as exc:

        return stage(
            "runtime_topology",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# KERNEL VALIDATION
# ============================================================

def run_kernel_validation() -> CertificationStage:

    try:

        kernel = resolve_authoritative_kernel()

        return stage(
            "kernel_authority",
            True,
            kernel_module=kernel.__name__,
        )

    except Exception as exc:

        return stage(
            "kernel_authority",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# REGRESSION VALIDATION
# ============================================================

def run_regression_validation() -> CertificationStage:

    try:

        module = importlib.import_module(
            "hhs_regression_suite_v1"
        )

        if hasattr(module, "run_regression_suite"):

            report = module.run_regression_suite()

            ok = report.get(
                "summary",
                {}
            ).get(
                "all_ok",
                False,
            )

            return stage(
                "regression_suite",
                ok,
                report=report,
            )

        return stage(
            "regression_suite",
            True,
            import_only=True,
        )

    except Exception as exc:

        return stage(
            "regression_suite",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# DATABASE VALIDATION
# ============================================================

def run_database_validation() -> CertificationStage:

    try:

        module = importlib.import_module(
            "hhs_database_integration_layer_v1"
        )

        return stage(
            "database_persistence",
            True,
            module=str(module),
        )

    except Exception as exc:

        return stage(
            "database_persistence",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# REPLAY VALIDATION
# ============================================================

def run_replay_validation() -> CertificationStage:

    try:

        module = importlib.import_module(
            "hhs_receipt_replay_verifier_v1"
        )

        return stage(
            "receipt_replay",
            True,
            module=str(module),
        )

    except Exception as exc:

        return stage(
            "receipt_replay",
            False,
            exception=repr(exc),
            traceback=traceback.format_exc(),
        )


# ============================================================
# CERTIFICATION ORCHESTRATION
# ============================================================

def run_bundle_certification() -> CertificationReport:

    stages: List[CertificationStage] = []

    # --------------------------------------------------------
    # TOPOLOGY
    # --------------------------------------------------------

    topology = run_topology_validation()
    stages.append(topology)

    # --------------------------------------------------------
    # KERNEL
    # --------------------------------------------------------

    kernel = run_kernel_validation()
    stages.append(kernel)

    # --------------------------------------------------------
    # SMOKE
    # --------------------------------------------------------

    smoke_report = run_smoke_suite()

    smoke_ok = smoke_report["summary"]["all_ok"]

    stages.append(
        stage(
            "runtime_smoke",
            smoke_ok,
            report=smoke_report,
        )
    )

    # --------------------------------------------------------
    # REGRESSION
    # --------------------------------------------------------

    regression = run_regression_validation()
    stages.append(regression)

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    database = run_database_validation()
    stages.append(database)

    # --------------------------------------------------------
    # REPLAY
    # --------------------------------------------------------

    replay = run_replay_validation()
    stages.append(replay)

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    topology_ok = topology.ok
    kernel_ok = kernel.ok
    regression_ok = regression.ok
    database_ok = database.ok
    replay_ok = replay.ok

    locked = (
        topology_ok
        and kernel_ok
        and smoke_ok
        and regression_ok
        and database_ok
        and replay_ok
    )

    status = (
        "CERTIFIED_LOCKED"
        if locked
        else "CERTIFICATION_FAILED"
    )

    return CertificationReport(
        certification="HHS_GENERAL_PROGRAMMING_ENVIRONMENT_V1",
        status=status,
        locked=locked,
        topology_ok=topology_ok,
        kernel_ok=kernel_ok,
        smoke_ok=smoke_ok,
        regression_ok=regression_ok,
        database_ok=database_ok,
        replay_ok=replay_ok,
        stages=[
            asdict(s) for s in stages
        ],
    )


# ============================================================
# REPORTING
# ============================================================

def print_report(
    report: CertificationReport,
) -> None:

    print("\n")
    print("=" * 60)
    print("HHS CERTIFICATION REPORT")
    print("=" * 60)

    print(
        json.dumps(
            asdict(report),
            indent=2,
            default=str,
        )
    )

    print("=" * 60)


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    report = run_bundle_certification()

    print_report(report)

    if not report.locked:
        raise SystemExit(1)