from __future__ import annotations

import tempfile
from pathlib import Path

from hhs_backend.runtime.hhs_pass203_catalog_identity_guard_v1 import (
    install_pass203_catalog_identity_guard,
)
from hhs_backend.runtime.hhs_pass203_hydrated_mainframe_v1 import HydratedMainframe


def test_catalog_callers_receive_isolated_descriptor_snapshots(monkeypatch):
    with tempfile.TemporaryDirectory() as directory:
        monkeypatch.setenv("HHS_PASS203_STATE_ROOT", directory)
        runtime = HydratedMainframe(Path(__file__).resolve().parents[1])
        guard = install_pass203_catalog_identity_guard(runtime)

        before = runtime.status()
        first = runtime.catalog()
        original_name = first[0]["name"]
        first[0]["name"] = "CALLER_MUTATION_MUST_NOT_ESCAPE"

        second = runtime.catalog()
        after = runtime.status()
        assert second[0]["name"] == original_name
        assert after["catalog_sha256"] == before["catalog_sha256"]
        assert guard.status()["catalog_sha256"] == after["catalog_sha256"]
        assert guard.status()["caller_mutation_isolated"] is True


def test_explicit_refresh_atomically_replaces_catalog_identity(monkeypatch):
    with tempfile.TemporaryDirectory() as directory:
        monkeypatch.setenv("HHS_PASS203_STATE_ROOT", directory)
        runtime = HydratedMainframe(Path(__file__).resolve().parents[1])
        guard = install_pass203_catalog_identity_guard(runtime)

        initial_generation = guard.status()["generation"]
        report = runtime.refresh()
        status = runtime.status()
        guarded = guard.status()

        assert report["catalog_identity_guard"] == "HHS_PASS_203_CATALOG_IDENTITY_GUARD_V1"
        assert guarded["generation"] > initial_generation
        assert report["catalog_sha256"] == status["catalog_sha256"] == guarded["catalog_sha256"]
        assert report["catalog_count"] == status["catalog_count"] == guarded["catalog_count"]


def test_hosted_bootstrap_installs_guard_on_canonical_singleton():
    from hhs_backend.api.a_pass203_catalog_identity_bootstrap import (
        PASS203_CATALOG_IDENTITY_GUARD,
        PASS203_CATALOG_IDENTITY_STATUS,
    )
    from hhs_backend.runtime.hhs_pass203_hydrated_mainframe_v1 import PASS203_MAINFRAME

    assert PASS203_MAINFRAME._pass203_catalog_identity_guard is PASS203_CATALOG_IDENTITY_GUARD
    assert PASS203_CATALOG_IDENTITY_STATUS["installed"] is True
    assert PASS203_MAINFRAME.status()["catalog_sha256"] == PASS203_CATALOG_IDENTITY_GUARD.status()["catalog_sha256"]
