from __future__ import annotations

import importlib
from pathlib import Path

from hhs_runtime import hhs_repo_paths_v1 as repo_paths


def test_established_repo_path_interface_and_environment_overrides(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "HHS_SYSTEM_ANCHOR_v1.md").write_text("anchor\n", encoding="utf-8")

    data = tmp_path / "data"
    runtime = tmp_path / "runtime"
    kernels = tmp_path / "kernels"
    ledger = tmp_path / "filesystem-ledger.json"

    monkeypatch.setenv(repo_paths.REPO_ROOT_ENV, str(repo))
    monkeypatch.setenv(repo_paths.DATA_DIR_ENV, str(data))
    monkeypatch.setenv(repo_paths.RUNTIME_OUTPUT_DIR_ENV, str(runtime))
    monkeypatch.setenv(repo_paths.KERNEL_DIR_ENV, str(kernels))
    monkeypatch.setenv(repo_paths.FILESYSTEM_LEDGER_ENV, str(ledger))

    assert repo_paths.repo_root() == repo.resolve()
    assert repo_paths.data_dir("nested", create=True) == data / "nested"
    assert (data / "nested").is_dir()
    assert repo_paths.runtime_output_dir("receipts", create=True) == runtime / "receipts"
    assert (runtime / "receipts").is_dir()
    assert repo_paths.kernel_dir("exact", create=True) == kernels / "exact"
    assert (kernels / "exact").is_dir()

    artifact = repo_paths.runtime_artifact_path("consensus.json")
    assert artifact == runtime / "consensus.json"
    assert artifact.parent.is_dir()

    relative = repo_paths.resolve_repo_path("hhs_runtime/example.py")
    assert relative == repo / "hhs_runtime/example.py"

    fallback = repo_paths.resolve_repo_path(None, "data", "runtime", "fallback.json", create_parent=True)
    assert fallback == repo / "data/runtime/fallback.json"
    assert fallback.parent.is_dir()

    present = repo / "present.txt"
    present.write_text("present\n", encoding="utf-8")
    assert repo_paths.first_existing(("missing.txt", "present.txt")) == present
    assert repo_paths.first_existing(("missing-a.txt", "missing-b.txt")) is None


def test_existing_callers_import_against_restored_interface(tmp_path, monkeypatch):
    monkeypatch.setenv(repo_paths.REPO_ROOT_ENV, str(tmp_path))
    monkeypatch.setenv(repo_paths.RUNTIME_OUTPUT_DIR_ENV, str(tmp_path / "runtime"))
    monkeypatch.setenv(repo_paths.FILESYSTEM_LEDGER_ENV, str(tmp_path / "filesystem-ledger.json"))

    dependency_audit = importlib.import_module("hhs_runtime.hhs_dependency_audit_v1")
    atomic_write = importlib.import_module("hhs_runtime.hhs_atomic_write_layer_v1")
    unified_ledger = importlib.import_module("hhs_runtime.hhs_unified_hash72_ledger_v1")

    assert dependency_audit.repo_root() == tmp_path.resolve()
    target = atomic_write.runtime_artifact_path("caller-compatibility.json")
    assert target == tmp_path / "runtime/caller-compatibility.json"
    assert callable(unified_ledger.runtime_artifact_path)
