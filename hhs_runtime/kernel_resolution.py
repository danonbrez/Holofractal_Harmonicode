# hhs_runtime/kernel_resolution.py
#
# HHS Canonical Runtime Bootstrap Resolver
#
# Purpose:
# Establish a single authoritative runtime bootstrap surface
# for:
#
# - repo root discovery
# - kernel discovery
# - authority verification
# - runtime topology normalization
# - compatibility fallback routing
#
# This module MUST become the only kernel/bootstrap authority
# surface used by:
#
# - smoke tests
# - bundle runner
# - certification pipeline
# - backend runtime
# - websocket runtime
# - pytest runtime fixtures
#
# Invariants:
# Δe = 0
# Ψ = 0
# Θ15 = true
# Ω = true

from __future__ import annotations

import importlib.util
import inspect
import os
import pathlib
import sys
from dataclasses import dataclass
from types import ModuleType
from typing import List, Optional


# ============================================================
# REQUIRED AUTHORITATIVE SYMBOLS
# ============================================================

REQUIRED_KERNEL_SYMBOLS = [
    "AUTHORITATIVE_TRUST_POLICY_V44",
    "security_hash72_v44",
    "NativeHash72Codec",
    "Manifold9",
    "Tensor",
]


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class KernelCandidate:
    path: pathlib.Path
    module_name: str


@dataclass
class BootstrapReport:
    repo_root: pathlib.Path
    kernel_path: pathlib.Path
    module_name: str
    verified_symbols: List[str]
    missing_symbols: List[str]
    python_executable: str
    sys_path_0: str


# ============================================================
# REPO ROOT DISCOVERY
# ============================================================

def resolve_repo_root() -> pathlib.Path:
    """
    Resolve canonical repository root.

    Priority:
    1. HHS_REPO_ROOT env override
    2. walk upward from current file
    """

    env_override = os.environ.get("HHS_REPO_ROOT")

    if env_override:
        path = pathlib.Path(env_override).resolve()

        if path.exists():
            return path

    current = pathlib.Path(__file__).resolve()

    for parent in current.parents:

        readme = parent / "README.md"

        if readme.exists():
            return parent

    raise RuntimeError(
        "Unable to resolve HHS repository root"
    )


REPO_ROOT = resolve_repo_root()


# ============================================================
# SYS.PATH NORMALIZATION
# ============================================================

def normalize_runtime_sys_path() -> None:
    """
    Ensure repo root is authoritative sys.path[0].
    """

    repo_root_str = str(REPO_ROOT)

    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)


normalize_runtime_sys_path()


# ============================================================
# KERNEL DISCOVERY
# ============================================================

def resolve_kernel_candidates() -> List[KernelCandidate]:
    """
    Discover possible authoritative kernels.
    """

    candidates: List[KernelCandidate] = []

    # --------------------------------------------------------
    # ENV OVERRIDE
    # --------------------------------------------------------

    env_kernel = os.environ.get("HHS_KERNEL_PATH")

    if env_kernel:

        path = pathlib.Path(env_kernel).resolve()

        if path.exists():
            candidates.append(
                KernelCandidate(
                    path=path,
                    module_name=path.stem,
                )
            )

    # --------------------------------------------------------
    # REPO ROOT DISCOVERY
    # --------------------------------------------------------

    for path in sorted(
        REPO_ROOT.glob("HARMONICODE_KERNEL*.py")
    ):
        candidates.append(
            KernelCandidate(
                path=path.resolve(),
                module_name=path.stem,
            )
        )

    return candidates


# ============================================================
# MODULE IMPORT
# ============================================================

def import_module_from_path(
    path: pathlib.Path,
    module_name: str,
) -> ModuleType:
    """
    Import module directly from file path.
    """

    spec = importlib.util.spec_from_file_location(
        module_name,
        str(path),
    )

    if spec is None:
        raise RuntimeError(
            f"Failed to create spec for: {path}"
        )

    if spec.loader is None:
        raise RuntimeError(
            f"Spec loader missing for: {path}"
        )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


# ============================================================
# SYMBOL VERIFICATION
# ============================================================

def verify_kernel_symbols(
    module: ModuleType,
) -> List[str]:
    """
    Return list of missing symbols.
    """

    missing = []

    for symbol in REQUIRED_KERNEL_SYMBOLS:

        if not hasattr(module, symbol):
            missing.append(symbol)

    return missing


# ============================================================
# AUTHORITATIVE KERNEL RESOLUTION
# ============================================================

def resolve_authoritative_kernel() -> ModuleType:
    """
    Resolve and verify canonical authoritative kernel.
    """

    candidates = resolve_kernel_candidates()

    if not candidates:
        raise RuntimeError(
            "No HARMONICODE_KERNEL candidates discovered"
        )

    errors = []

    for candidate in candidates:

        try:

            module = import_module_from_path(
                candidate.path,
                candidate.module_name,
            )

            missing = verify_kernel_symbols(module)

            if not missing:
                return module

            errors.append(
                f"{candidate.path.name}: "
                f"missing symbols={missing}"
            )

        except Exception as exc:

            errors.append(
                f"{candidate.path.name}: "
                f"exception={repr(exc)}"
            )

    raise RuntimeError(
        "No authoritative kernel satisfied requirements.\n\n"
        + "\n".join(errors)
    )


# ============================================================
# REPORTING
# ============================================================

def runtime_bootstrap_report() -> BootstrapReport:
    """
    Generate runtime bootstrap topology report.
    """

    kernel = resolve_authoritative_kernel()

    kernel_path = pathlib.Path(
        inspect.getfile(kernel)
    ).resolve()

    missing = verify_kernel_symbols(kernel)

    return BootstrapReport(
        repo_root=REPO_ROOT,
        kernel_path=kernel_path,
        module_name=kernel.__name__,
        verified_symbols=[
            s for s in REQUIRED_KERNEL_SYMBOLS
            if hasattr(kernel, s)
        ],
        missing_symbols=missing,
        python_executable=sys.executable,
        sys_path_0=sys.path[0],
    )


# ============================================================
# VALIDATION
# ============================================================

def assert_runtime_bootstrap_valid() -> None:
    """
    Hard fail if runtime bootstrap is inconsistent.
    """

    report = runtime_bootstrap_report()

    if report.missing_symbols:

        raise RuntimeError(
            "Authoritative kernel missing symbols:\n"
            + "\n".join(report.missing_symbols)
        )

    if "/mnt/data" in str(report.kernel_path):

        raise RuntimeError(
            "Stale sandbox kernel path detected:\n"
            f"{report.kernel_path}"
        )


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    report = runtime_bootstrap_report()

    print("\n")
    print("=" * 60)
    print("HHS RUNTIME BOOTSTRAP REPORT")
    print("=" * 60)

    print(f"repo_root      : {report.repo_root}")
    print(f"kernel_path    : {report.kernel_path}")
    print(f"module_name    : {report.module_name}")
    print(f"python_exec    : {report.python_executable}")
    print(f"sys.path[0]    : {report.sys_path_0}")

    print("\nVerified Symbols:")
    for symbol in report.verified_symbols:
        print(f"  PASS  {symbol}")

    if report.missing_symbols:

        print("\nMissing Symbols:")
        for symbol in report.missing_symbols:
            print(f"  FAIL  {symbol}")

    else:
        print("\nAll required symbols verified.")

    print("=" * 60)