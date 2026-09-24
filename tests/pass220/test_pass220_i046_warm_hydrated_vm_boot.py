from __future__ import annotations

import json
from pathlib import Path

import pytest

from deployment.digitalocean import warm_boot_manifest


ROOT = Path(__file__).resolve().parents[2]
SHA_A = "1" * 40
SHA_B = "2" * 40


def _prepare_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> dict[str, Path]:
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
    for name, path in paths.items():
        monkeypatch.setenv(name, str(path))
        directory = path.parent if name == "HHS_PASS205_DB" else path
        directory.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HHS_DISABLE_C_AUTOBUILD", "1")
    return paths


def _prepare_artifacts(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    runtime = repo / "hhs_runtime" / "builds" / "libhhs_runtime.so"
    runtime.parent.mkdir(parents=True)
    runtime.write_bytes(b"compiled-rom-native-runtime")

    runtime_os = tmp_path / "runtime-os" / "release"
    (runtime_os / "assets").mkdir(parents=True)
    (runtime_os / "index.html").write_text(
        "<!doctype html><title>HHS Visual Runtime OS Workspace</title>",
        encoding="utf-8",
    )
    return repo, runtime_os


def test_manifest_create_then_restart_verify_adopts_without_build(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _prepare_state(monkeypatch, tmp_path)
    repo, runtime_os = _prepare_artifacts(tmp_path)
    manifest_root = tmp_path / "warm-boot" / "releases"
    monkeypatch.setattr(warm_boot_manifest, "_head", lambda _repo: SHA_A)

    manifest = warm_boot_manifest.create_manifest(
        repo_root=repo,
        runtime_os_root=runtime_os,
        manifest_root=manifest_root,
    )
    assert manifest.name == f"{SHA_A}.json"

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["repository_sha"] == SHA_A
    assert payload["boot_policy"]["autobuild_forbidden"] is True
    assert payload["boot_policy"]["compile_on_restart"] is False
    assert payload["boot_policy"]["rehydrate_from_empty_on_restart"] is False
    assert payload["boot_policy"]["adopt_persistent_state"] is True

    verified = warm_boot_manifest.verify_manifest(
        repo_root=repo,
        manifest_root=manifest_root,
    )
    assert verified["repository_sha"] == SHA_A
    assert verified["native_runtime_adopted"] is True
    assert verified["runtime_os_adopted"] is True
    assert verified["persistent_roots_adopted"] is True
    assert verified["persistent_state_adopted"] is False
    assert verified["hydration_classification"] == "PERSISTENCE_PARTIAL_OR_UNSEALED"
    assert verified["protected_compiled_rom_recovery_verified"] is False
    assert verified["compile_on_restart"] is False
    assert verified["rehydrate_from_empty_on_restart"] is False
    assert verified["canonical_state_authority"] is False


def test_restart_rejects_when_autobuild_is_not_disabled(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _prepare_state(monkeypatch, tmp_path)
    repo, runtime_os = _prepare_artifacts(tmp_path)
    manifest_root = tmp_path / "warm-boot" / "releases"
    monkeypatch.setattr(warm_boot_manifest, "_head", lambda _repo: SHA_A)
    warm_boot_manifest.create_manifest(
        repo_root=repo,
        runtime_os_root=runtime_os,
        manifest_root=manifest_root,
    )
    monkeypatch.delenv("HHS_DISABLE_C_AUTOBUILD", raising=False)

    with pytest.raises(
        warm_boot_manifest.WarmBootError,
        match="HHS_WARM_BOOT_AUTOBUILD_NOT_DISABLED",
    ):
        warm_boot_manifest.verify_manifest(
            repo_root=repo,
            manifest_root=manifest_root,
        )


def test_release_manifests_are_sha_scoped_for_rollback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _prepare_state(monkeypatch, tmp_path)
    repo, runtime_os = _prepare_artifacts(tmp_path)
    manifest_root = tmp_path / "warm-boot" / "releases"

    current = {"sha": SHA_A}
    monkeypatch.setattr(warm_boot_manifest, "_head", lambda _repo: current["sha"])
    first = warm_boot_manifest.create_manifest(
        repo_root=repo,
        runtime_os_root=runtime_os,
        manifest_root=manifest_root,
    )

    current["sha"] = SHA_B
    second = warm_boot_manifest.create_manifest(
        repo_root=repo,
        runtime_os_root=runtime_os,
        manifest_root=manifest_root,
    )

    assert first.name == f"{SHA_A}.json"
    assert second.name == f"{SHA_B}.json"
    assert first.is_file()
    assert second.is_file()


def test_production_service_binds_all_warm_durable_state_and_preflight() -> None:
    service = (
        ROOT / "deploy/digitalocean/hhs-pass196-integrated-environment.service"
    ).read_text(encoding="utf-8")
    required = (
        "HHS_DISABLE_C_AUTOBUILD=1",
        "HHS_PASS174_STATE_DIR=/var/lib/hhs/pass174",
        "HHS_PASS194_STATE_ROOT=/var/lib/hhs/pass194",
        "HHS_PASS205_DB=/var/lib/hhs/pass205/continuation.sqlite3",
        "HHS_PASS213_SURFACE_STATE_DIR=/var/lib/hhs/pass213/surface",
        "HHS_PASS218_STATE_ROOT=/var/lib/hhs/pass218",
        "HHS_PASS219_LANE5_STATE_ROOT=/var/lib/hhs/pass219/lane5",
        "HHS_RUNTIME_BOOTSTRAP_ROOT=/var/lib/hhs/runtime-bootstrap",
        "HHS_WARM_BOOT_MANIFEST_ROOT=/var/lib/hhs/warm-boot/releases",
        "ExecStartPre=/opt/hhs/venv/bin/python /opt/hhs/app/deployment/digitalocean/warm_boot_manifest.py verify",
    )
    for needle in required:
        assert needle in service


def test_promotion_builds_once_then_seals_before_service_start() -> None:
    updater = (
        ROOT / "deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh"
    ).read_text(encoding="utf-8")

    assert 'log "Running configured native post-merge command"' in updater
    assert 'log "Sealing warm hydrated VM boot identity"' in updater
    assert "warm_boot_manifest.py" in updater
    assert updater.index('log "Sealing warm hydrated VM boot identity"') < updater.index(
        "if ! start_units; then"
    )
    assert "/var/lib/hhs/pass174" in updater
    assert "/var/lib/hhs/pass194" in updater
    assert "/var/lib/hhs/pass213/surface" in updater
    assert "/var/lib/hhs/pass219/lane5" in updater


def test_restart_verifier_contains_no_build_or_hydration_commands() -> None:
    source = (
        ROOT / "deployment/digitalocean/warm_boot_manifest.py"
    ).read_text(encoding="utf-8").lower()
    forbidden = (
        "make c-abi",
        "gcc ",
        "clang ",
        "cmake ",
        "npm install",
        "pip install",
        "apt-get",
        "post_compile",
        "generate_affine_hydration",
    )
    for token in forbidden:
        assert token not in source
