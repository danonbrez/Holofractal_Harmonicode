from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess

import pytest

from deployment.digitalocean import warm_boot_manifest as warm


ROOT = Path(__file__).resolve().parents[2]
SHA = "a" * 40


def _fixture(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    paths = {
        "HHS_DATA_DIR": tmp_path / "data",
        "HHS_PASS174_STATE_DIR": tmp_path / "pass174",
        "HHS_PASS194_STATE_ROOT": tmp_path / "pass194",
        "HHS_PASS205_DB": tmp_path / "pass205" / "continuation.sqlite3",
        "HHS_PASS213_SURFACE_STATE_DIR": tmp_path / "pass213" / "surface",
        "HHS_PASS218_STATE_ROOT": tmp_path / "pass218",
        "HHS_PASS219_LANE5_STATE_ROOT": tmp_path / "pass219" / "lane5",
        "HHS_RUNTIME_BOOTSTRAP_ROOT": tmp_path / "runtime-bootstrap",
    }
    for key, path in paths.items():
        monkeypatch.setenv(key, str(path))
        (path.parent if key == "HHS_PASS205_DB" else path).mkdir(
            parents=True, exist_ok=True
        )
    monkeypatch.setenv("HHS_DISABLE_C_AUTOBUILD", "1")
    monkeypatch.setattr(warm, "_head", lambda _root: SHA)
    repo = tmp_path / "repo"
    native = repo / "hhs_runtime" / "builds" / "libhhs_runtime.so"
    native.parent.mkdir(parents=True)
    native.write_bytes(b"prebuilt-native-binary")
    release = tmp_path / "runtime-os" / "release"
    (release / "assets").mkdir(parents=True)
    (release / "index.html").write_text("<title>HHS</title>", encoding="utf-8")
    return paths, repo, release, tmp_path / "manifests"


def _seal(repo: Path, release: Path, manifest_root: Path) -> Path:
    return warm.create_manifest(
        repo_root=repo, runtime_os_root=release, manifest_root=manifest_root
    )


def test_partial_state_cannot_be_misreported_as_hydrated(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    paths, repo, release, root = _fixture(monkeypatch, tmp_path)
    manifest = json.loads(_seal(repo, release, root).read_text())
    assert manifest["persistence_inventory"]["hydration_classification"] == (
        "PERSISTENCE_PARTIAL"
    )
    observed = warm.verify_manifest(repo_root=repo, manifest_root=root)
    assert observed["persistent_roots_adopted"] is True
    assert observed["persistent_state_adopted"] is False
    assert observed["protected_compiled_rom_recovery_verified"] is False


def test_existing_store_or_key_cannot_disappear_after_seal(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    paths, repo, release, root = _fixture(monkeypatch, tmp_path)
    db = paths["HHS_PASS174_STATE_DIR"] / "hash216_vectors.sqlite3"
    key = paths["HHS_PASS174_STATE_DIR"] / "hash216_vectors.key"
    db.write_bytes(b"sqlite-placeholder")
    key.write_bytes(b"fixed-private-key-material")
    _seal(repo, release, root)

    verified = warm.verify_manifest(repo_root=repo, manifest_root=root)
    assert verified["hydration_classification"] == "PERSISTENCE_PARTIAL"

    key.write_bytes(b"unexpected-rotation")
    with pytest.raises(warm.WarmBootError, match="PERSISTENT_KEY_CHANGED"):
        warm.verify_manifest(repo_root=repo, manifest_root=root)

    key.write_bytes(b"fixed-private-key-material")
    db.unlink()
    with pytest.raises(warm.WarmBootError, match="PERSISTENT_ARTIFACT_LOST"):
        warm.verify_manifest(repo_root=repo, manifest_root=root)


def test_all_inventory_files_mark_persistence_present_without_claiming_rom(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, repo, release, root = _fixture(monkeypatch, tmp_path)
    state = warm._state_roots()
    for namespace, names in warm.PERSISTENT_COMPONENTS.items():
        base = warm._root_directory(namespace, state[namespace])
        for name in names:
            (base / name).write_bytes(b"present-" + name.encode())
    _seal(repo, release, root)
    observed = warm.verify_manifest(repo_root=repo, manifest_root=root)
    assert observed["persistent_state_adopted"] is True
    assert observed["hydration_classification"] == "PERSISTENCE_PRESENT"
    assert observed["protected_compiled_rom_recovery_verified"] is False


def test_service_environment_has_one_directive_per_physical_line() -> None:
    service = (
        ROOT / "deploy/digitalocean/hhs-pass196-integrated-environment.service"
    ).read_text()
    lines = service.splitlines()
    env = [line for line in lines if line.startswith("Environment=")]
    assert len(env) == len(set(env))
    assert all("\\n" not in line and line.count("Environment=") == 1 for line in env)
    assert "Environment=HHS_RUNTIME_STATUS_PROBE_TIMEOUT_SECONDS=180" in env
    assert "Environment=HHS_RUNTIME_STATUS_PROBE_CONCURRENCY=2" in env
    assert "Environment=HHS_DISABLE_C_AUTOBUILD=1" in env


def test_installer_assignment_values_are_real_shell_lines() -> None:
    installer = (
        ROOT / "deployment/digitalocean/guarded_auto_update/install.sh"
    ).read_text()
    lines = installer.splitlines()
    for variable in (
        "RECOVERY_VERIFIER",
        "STATIC_FIRST_CONFIGURATOR",
        "NATIVE_BUILD",
    ):
        matching = [line for line in lines if line.startswith(variable + "=")]
        assert len(matching) == 1, variable
        assert "\\n" not in matching[0]
    preamble = installer.split("[[ $EUID -eq 0 ]]", 1)[0]
    completed = subprocess.run(
        ["bash", "-c", preamble + "\nprintf '%s\\n' \"$NATIVE_BUILD\""],
        capture_output=True, text=True, check=True,
    )
    assert "make c-abi" in completed.stdout


def test_seal_failure_rolls_back_before_start() -> None:
    updater = (
        ROOT / "deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh"
    ).read_text()
    start = updater.index('log "Sealing warm hydrated VM boot identity"')
    rollback = updater.index(
        'rollback_live_checkout "warm-boot seal or durable-root initialization failed"'
    )
    service_start = updater.index("if ! start_units; then")
    assert start < rollback < service_start
    assert "if ! (" in updater[:start][-60:]
