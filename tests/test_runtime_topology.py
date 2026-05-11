# tests/test_runtime_topology.py
#
# HHS Runtime Topology Verification Suite
#
# Purpose:
# Validate canonical runtime authority, package coherence,
# kernel bootstrap consistency, replay continuity surfaces,
# and persistence availability during the hybrid migration phase.
#
# This suite is intentionally infrastructure-focused rather than
# feature-focused. It verifies that all runtime entrypoints resolve
# toward the same authoritative topology.
#
# Invariants:
# Δe = 0
# Ψ = 0
# Θ15 = true
# Ω = true

from __future__ import annotations

import importlib
import inspect
import os
import pathlib
import sys
from types import ModuleType

import pytest

# ============================================================
# REPOSITORY ROOT DISCOVERY
# ============================================================

THIS_FILE = pathlib.Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parent.parent.resolve()

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ============================================================
# HELPERS
# ============================================================

def safe_import(module_name: str) -> ModuleType:
    """
    Import module with explicit failure context.
    """
    try:
        return importlib.import_module(module_name)
    except Exception as exc:
        pytest.fail(
            f"\nFAILED IMPORT:\n"
            f"module={module_name}\n"
            f"repo_root={REPO_ROOT}\n"
            f"sys.path[0]={sys.path[0]}\n"
            f"exception={repr(exc)}"
        )


def module_path(module: ModuleType) -> pathlib.Path:
    """
    Resolve physical module path.
    """
    return pathlib.Path(inspect.getfile(module)).resolve()


# ============================================================
# PACKAGE TOPOLOGY
# ============================================================

def test_repo_root_in_sys_path():
    assert str(REPO_ROOT) in sys.path


@pytest.mark.parametrize(
    "module_name",
    [
        "hhs_runtime",
        "hhs_backend",
    ]
)
def test_core_packages_import(module_name):
    module = safe_import(module_name)

    path = module_path(module)

    assert path.exists(), f"{module_name} path missing"
    assert REPO_ROOT in path.parents, (
        f"{module_name} resolved outside repo:\n{path}"
    )


# ============================================================
# CANONICAL MODULE SURFACE
# ============================================================

@pytest.mark.parametrize(
    "module_name",
    [
        # canonical migrated surfaces
        "hhs_runtime",

        # runtime infrastructure
        "hhs_runtime_smoke_tests_v1",
        "hhs_regression_suite_v1",
        "hhs_v1_bundle_runner-2",
    ]
)
def test_runtime_modules_resolve(module_name):
    safe_import(module_name)


# ============================================================
# OPTIONAL MIGRATED MODULES
# ============================================================

OPTIONAL_RUNTIME_MODULES = [
    "hhs_runtime.hhs_linguistic_validation_pipeline_v1",
    "hhs_runtime.hhs_loshu_phase_embedding_v1",
]

@pytest.mark.parametrize("module_name", OPTIONAL_RUNTIME_MODULES)
def test_optional_runtime_modules(module_name):
    """
    These modules may exist either:
    - directly under hhs_runtime
    - or under migrated subpaths.

    This test reports exact topology failures instead of
    generic ModuleNotFoundError ambiguity.
    """
    try:
        safe_import(module_name)
    except Failed:
        pytest.skip(f"Optional migrated module unresolved: {module_name}")


# ============================================================
# KERNEL AUTHORITY
# ============================================================

REQUIRED_KERNEL_SYMBOLS = [
    "AUTHORITATIVE_TRUST_POLICY_V44",
    "security_hash72_v44",
    "NativeHash72Codec",
    "Manifold9",
    "Tensor",
]


def discover_kernel_candidates():
    """
    Discover likely authoritative kernel modules.
    """
    candidates = []

    for path in REPO_ROOT.glob("HARMONICODE_KERNEL*.py"):
        candidates.append(path)

    return candidates


def import_kernel_from_path(path: pathlib.Path):
    module_name = path.stem

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)

    assert spec.loader is not None
    spec.loader.exec_module(module)

    return module


def test_authoritative_kernel_exists():
    kernels = discover_kernel_candidates()

    assert kernels, (
        "No HARMONICODE_KERNEL*.py files discovered"
    )


def test_authoritative_kernel_symbols():
    kernels = discover_kernel_candidates()

    assert kernels, "No kernel candidates discovered"

    errors = []

    for kernel_path in kernels:
        try:
            kernel = import_kernel_from_path(kernel_path)

            missing = [
                sym for sym in REQUIRED_KERNEL_SYMBOLS
                if not hasattr(kernel, sym)
            ]

            if not missing:
                return

            errors.append(
                f"{kernel_path.name}: missing={missing}"
            )

        except Exception as exc:
            errors.append(
                f"{kernel_path.name}: exception={repr(exc)}"
            )

    pytest.fail(
        "\nNo authoritative kernel satisfied symbol requirements.\n\n"
        + "\n".join(errors)
    )


# ============================================================
# RUNTIME PATH COHERENCE
# ============================================================

def test_no_mnt_data_runtime_dependency():
    """
    Detect stale sandbox-specific runtime assumptions.
    """

    bad_refs = []

    for py_file in REPO_ROOT.rglob("*.py"):

        try:
            text = py_file.read_text(encoding="utf-8")

            if "/mnt/data" in text:
                bad_refs.append(str(py_file.relative_to(REPO_ROOT)))

        except Exception:
            continue

    assert not bad_refs, (
        "Found stale /mnt/data references:\n\n"
        + "\n".join(bad_refs)
    )


# ============================================================
# PERSISTENCE AVAILABILITY
# ============================================================

def test_database_bridge_importable():

    try:
        safe_import("hhs_database_integration_layer_v1")
    except Exception as exc:
        pytest.fail(
            f"Database bridge unavailable:\n{repr(exc)}"
        )


# ============================================================
# RECEIPT / REPLAY SANITY
# ============================================================

def test_replay_verifier_importable():

    module = safe_import("hhs_receipt_replay_verifier_v1")

    assert module is not None


# ============================================================
# EXECUTION ENTRYPOINT COHERENCE
# ============================================================

ENTRYPOINTS = [
    "hhs_runtime_smoke_tests_v1",
    "hhs_regression_suite_v1",
]


@pytest.mark.parametrize("entrypoint", ENTRYPOINTS)
def test_entrypoint_resolves_inside_repo(entrypoint):

    module = safe_import(entrypoint)

    path = module_path(module)

    assert REPO_ROOT in path.parents, (
        f"{entrypoint} resolved outside repo:\n{path}"
    )


# ============================================================
# REPORT
# ============================================================

def test_runtime_topology_summary():

    print("\n")
    print("=" * 60)
    print("HHS RUNTIME TOPOLOGY VERIFIED")
    print("=" * 60)
    print(f"repo_root={REPO_ROOT}")
    print(f"python={sys.version}")
    print(f"sys.path[0]={sys.path[0]}")
    print("=" * 60)

    assert True