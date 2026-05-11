# hhs_runtime/__init__.py
#
# HHS Canonical Runtime Namespace Surface
#
# Purpose:
# Stabilize import topology during the hybrid migration phase.
#
# This package acts as:
#
# - canonical runtime namespace
# - compatibility forwarding layer
# - migration bridge
# - runtime authority surface
#
# All migrated runtime modules should eventually resolve through:
#
#     hhs_runtime.*
#
# Root-level legacy files remain compatibility shims only.
#
# Invariants:
# Δe = 0
# Ψ = 0
# Θ15 = true
# Ω = true

from __future__ import annotations


# ============================================================
# RUNTIME BOOTSTRAP
# ============================================================

from .kernel_resolution import (
    REPO_ROOT,
    resolve_repo_root,
    resolve_kernel_candidates,
    resolve_authoritative_kernel,
    runtime_bootstrap_report,
    assert_runtime_bootstrap_valid,
)


# ============================================================
# OPTIONAL MIGRATED MODULE FORWARDERS
# ============================================================
#
# These preserve historical import surfaces while canonical
# package migration continues.
#
# Example:
#
# old:
#     import hhs_runtime.foo
#
# migrated:
#     hhs_runtime.core_sandbox.foo
#
# This layer prevents topology collapse during transition.
#
# ============================================================

_OPTIONAL_FORWARDERS = [
    (
        "hhs_linguistic_validation_pipeline_v1",
        ".core_sandbox.hhs_linguistic_validation_pipeline_v1",
    ),
    (
        "hhs_loshu_phase_embedding_v1",
        ".core_sandbox.hhs_loshu_phase_embedding_v1",
    ),
]


def _install_forwarders():

    import importlib
    import sys

    runtime_pkg = __name__

    for public_name, target_path in _OPTIONAL_FORWARDERS:

        try:

            module = importlib.import_module(
                target_path,
                package=runtime_pkg,
            )

            sys.modules[
                f"{runtime_pkg}.{public_name}"
            ] = module

            globals()[public_name] = module

        except Exception:
            #
            # Forwarders are intentionally soft-fail during
            # migration so partially migrated repos remain
            # bootable.
            #
            pass


_install_forwarders()


# ============================================================
# PACKAGE METADATA
# ============================================================

__all__ = [
    "REPO_ROOT",
    "resolve_repo_root",
    "resolve_kernel_candidates",
    "resolve_authoritative_kernel",
    "runtime_bootstrap_report",
    "assert_runtime_bootstrap_valid",
]


# ============================================================
# PACKAGE VALIDATION
# ============================================================

def runtime_namespace_report():

    return {
        "package": __name__,
        "repo_root": str(REPO_ROOT),
        "forwarders": [
            name for name, _ in _OPTIONAL_FORWARDERS
        ],
    }