from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deployment" / "digitalocean" / "guarded_auto_update"


def read(name: str) -> str:
    return (DEPLOY / name).read_text(encoding="utf-8")


def _run(
    *args: str,
    cwd: Path,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=check)


def _git_commit(repo: Path, message: str, *paths: str) -> str:
    _run("git", "add", "-f", *paths, cwd=repo)
    _run("git", "commit", "-qm", message, cwd=repo)
    return _run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()


def _write_runtime_os_dist(root: Path, label: str) -> Path:
    dist = root / "dist"
    assets = dist / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (dist / "index.html").write_text(
        "<!doctype html><title>HHS Visual Runtime OS Workspace</title>"
        f"<main>{label}</main><script src='/assets/index-{label}.js'></script>\n",
        encoding="utf-8",
    )
    (assets / f"index-{label}.js").write_text(f"console.log({label!r});\n", encoding="utf-8")
    return dist


def _bundle_create_stage(tool: Path, root: Path, sha: str, label: str) -> Path:
    source = root / f"source-{label}"
    dist = _write_runtime_os_dist(source, label)
    incoming = root / "incoming" / sha
    incoming.mkdir(parents=True, exist_ok=True)
    archive = incoming / "runtime-os.tar.gz"
    manifest = incoming / "manifest.json"
    _run(
        sys.executable,
        str(tool),
        "create",
        "--dist",
        str(dist),
        "--repository-sha",
        sha,
        "--archive",
        str(archive),
        "--manifest",
        str(manifest),
        cwd=ROOT,
    )
    staged = _run(
        sys.executable,
        str(tool),
        "stage",
        "--root",
        str(root),
        "--archive",
        str(archive),
        "--manifest",
        str(manifest),
        "--expected-sha",
        sha,
        cwd=ROOT,
    ).stdout.strip()
    return Path(staged)


def test_guarded_updater_is_fail_closed_and_serialized() -> None:
    source = read("hhs-guarded-update.sh")
    assert "set -Eeuo pipefail" in source
    assert "flock" in source
    assert "EXPECTED_REPOSITORY" in source
    assert "origin/main" in source
    assert "git merge-base --is-ancestor" in source
    assert "validate-candidate.sh" in source
    assert "ROLLBACK" in source
    assert "PROMOTED" in source
    assert "HHS_RUNTIME_OS_BUNDLE_MODE" in source
    assert "runtime-os-bundle.py" in source


def test_installer_uses_exact_one_shot_promotion_before_periodic_timer() -> None:
    source = read("install.sh")
    stop = source.index("systemctl stop hhs-guarded-update.timer")
    synchronous = source.index("systemctl start hhs-guarded-update.service")
    enable = source.index("systemctl enable hhs-guarded-update.timer")
    start = source.index("systemctl start hhs-guarded-update.timer", enable)
    assert stop < synchronous < enable < start
    assert "HHS_INSTALL_ENABLE_PROMOTION" in source
    assert "HHS_RUNTIME_OS_BUNDLE_SHA" in source
    assert "existing guarded updater owner" in source or "existing guarded updater" in source
    assert "timer remains stopped" in source


def test_candidate_gate_uses_prebuilt_bundle_in_production_and_retains_source_mode() -> None:
    source = read("validate-candidate.sh")
    assert 'case "$BUNDLE_MODE" in' in source
    assert "prebuilt)" in source
    assert "auto|source)" in source
    assert "runtime-os-bundle.py" in source
    assert "Runtime OS bundle SHA does not match candidate" in source
    assert 'HHS_RUNTIME_OS_ASSET_ROOT="$RUNTIME_OS_ROOT"' in source
    assert 'env -u HHS_RUNTIME_OS_ROOT' in source
    assert 'HHS_RUNTIME_OS_ROOT="$RUNTIME_OS_ROOT"' not in source
    assert "candidate Runtime OS asset authority mismatch" in source


def test_bundle_tool_rejects_wrong_sha_corruption_and_legacy_identity() -> None:
    tool = DEPLOY / "runtime-os-bundle.py"
    with tempfile.TemporaryDirectory(prefix="hhs-runtime-os-bundle-test-") as temp:
        root = Path(temp)
        sha = "a" * 40
        dist = _write_runtime_os_dist(root / "source", "alpha")
        archive = root / "runtime-os.tar.gz"
        manifest = root / "manifest.json"
        _run(
            sys.executable,
            str(tool),
            "create",
            "--dist",
            str(dist),
            "--repository-sha",
            sha,
            "--archive",
            str(archive),
            "--manifest",
            str(manifest),
            cwd=ROOT,
        )

        wrong = _run(
            sys.executable,
            str(tool),
            "stage",
            "--root",
            str(root / "wrong"),
            "--archive",
            str(archive),
            "--manifest",
            str(manifest),
            "--expected-sha",
            "b" * 40,
            cwd=ROOT,
            check=False,
        )
        assert wrong.returncode != 0

        damaged = root / "damaged.tar.gz"
        damaged.write_bytes(archive.read_bytes() + b"corruption")
        corrupted = _run(
            sys.executable,
            str(tool),
            "stage",
            "--root",
            str(root / "damaged-root"),
            "--archive",
            str(damaged),
            "--manifest",
            str(manifest),
            "--expected-sha",
            sha,
            cwd=ROOT,
            check=False,
        )
        assert corrupted.returncode != 0

        legacy_source = root / "legacy-source"
        legacy_dist = legacy_source / "dist"
        legacy_assets = legacy_dist / "assets"
        legacy_assets.mkdir(parents=True)
        (legacy_dist / "index.html").write_text(
            "<!doctype html><title>Holofractal Harmonizer</title><script src='/assets/index-old.js'></script>\n",
            encoding="utf-8",
        )
        (legacy_assets / "index-old.js").write_text("console.log('legacy');\n", encoding="utf-8")
        legacy_archive = root / "legacy.tar.gz"
        legacy_manifest = root / "legacy.json"
        legacy = _run(
            sys.executable,
            str(tool),
            "create",
            "--dist",
            str(legacy_dist),
            "--repository-sha",
            sha,
            "--archive",
            str(legacy_archive),
            "--manifest",
            str(legacy_manifest),
            cwd=ROOT,
            check=False,
        )
        assert legacy.returncode != 0


def test_bundle_activation_and_rollback_are_versioned_and_atomic() -> None:
    tool = DEPLOY / "runtime-os-bundle.py"
    with tempfile.TemporaryDirectory(prefix="hhs-runtime-os-release-test-") as temp:
        root = Path(temp)
        first_sha = "1" * 40
        second_sha = "2" * 40
        first = _bundle_create_stage(tool, root, first_sha, "first")
        second = _bundle_create_stage(tool, root, second_sha, "second")

        _run(sys.executable, str(tool), "activate", "--root", str(root), "--release", str(first), cwd=ROOT)
        assert (root / "current").resolve() == first.resolve()
        _run(sys.executable, str(tool), "activate", "--root", str(root), "--release", str(second), cwd=ROOT)
        assert (root / "current").resolve() == second.resolve()
        _run(sys.executable, str(tool), "activate", "--root", str(root), "--release", str(first), cwd=ROOT)
        assert (root / "current").resolve() == first.resolve()


def test_preserve_host_drift_archives_tracked_source_and_migrates_runtime_journal() -> None:
    script = DEPLOY / "preserve-host-drift.sh"
    with tempfile.TemporaryDirectory(prefix="hhs-host-drift-test-") as temp:
        base = Path(temp)
        repo = base / "repo"
        state = base / "state"
        runtime = base / "runtime"
        repo.mkdir()
        _run("git", "init", "-q", cwd=repo)
        _run("git", "config", "user.name", "HHS Deployment Test", cwd=repo)
        _run("git", "config", "user.email", "hhs-deploy-test@example.invalid", cwd=repo)
        source = repo / "hhs_backend" / "runtime" / "live_fastapi_workflow_v1.py"
        source.parent.mkdir(parents=True)
        source.write_text("VALUE = 1\n", encoding="utf-8")
        journal = repo / "data" / "runtime" / "hhs_hash72_runtime_journal.jsonl"
        journal.parent.mkdir(parents=True)
        journal.write_text('{"event":"legacy"}\n', encoding="utf-8")
        _git_commit(
            repo,
            "baseline",
            "hhs_backend/runtime/live_fastapi_workflow_v1.py",
            "data/runtime/hhs_hash72_runtime_journal.jsonl",
        )
        source.write_text("VALUE = 2\n", encoding="utf-8")
        journal.write_text('{"event":"legacy"}\n{"event":"runtime"}\n', encoding="utf-8")
        untracked = repo / "data" / "runtime" / "runtime.tmp"
        untracked.write_text("temporary\n", encoding="utf-8")

        env = dict(os.environ)
        env.update(
            HHS_UPDATE_STATE_ROOT=str(state),
            HHS_RUNTIME_OUTPUT_DIR=str(runtime),
            HHS_HOST_DRIFT_MODE="source",
        )
        first = _run("bash", str(script), str(repo), cwd=ROOT, env=env)
        assert "HHS_HOST_DRIFT_RECONCILED=1" in first.stdout
        assert source.read_text(encoding="utf-8") == "VALUE = 1\n"
        assert journal.exists(), "source phase must leave runtime files untouched while service remains online"
        manifests = sorted((state / "host-drift").glob("*/manifest.json"))
        assert manifests
        manifest = json.loads(manifests[-1].read_text(encoding="utf-8"))
        assert "hhs_backend/runtime/live_fastapi_workflow_v1.py" in manifest["tracked_paths"]

        env["HHS_HOST_DRIFT_MODE"] = "final"
        second = _run("bash", str(script), str(repo), cwd=ROOT, env=env)
        assert "HHS_HOST_DRIFT_FINALIZED=1" in second.stdout
        assert not journal.exists()
        assert not untracked.exists()
        migrated = runtime / "hhs_hash72_runtime_journal.jsonl"
        assert migrated.read_text(encoding="utf-8").endswith('{"event":"runtime"}\n')
        assert _run("git", "status", "--porcelain=v1", cwd=repo).stdout.strip() == ""


def test_post_compile_uses_guarded_python_interpreter_contract() -> None:
    source = (ROOT / "bin" / "post_compile").read_text(encoding="utf-8")
    assert 'HHS_POST_COMPILE_PYTHON' in source
    assert 'HHS_VALIDATE_PYTHON' in source
    assert 'command -v "$PYTHON_BIN"' in source
    assert '"$PYTHON_BIN" tools/install_production_language_assets.py' in source


def test_timer_and_service_are_bounded() -> None:
    timer = read("hhs-guarded-update.timer")
    service = read("hhs-guarded-update.service")
    assert "OnUnitActiveSec=5min" in timer
    assert "RandomizedDelaySec=30s" in timer
    assert "TimeoutStartSec=90min" in service
    assert "Type=oneshot" in service
    assert "NoNewPrivileges=true" in service


def test_github_merge_gate_is_label_and_trust_scoped() -> None:
    workflow = (ROOT / ".github" / "workflows" / "guarded-continuous-integration.yml").read_text(encoding="utf-8")
    assert "hhs-automerge" in workflow
    assert "head.repo.full_name == github.repository" in workflow
    assert '"OWNER","MEMBER","COLLABORATOR"' in workflow
    assert "gh pr merge" in workflow


def test_digitalocean_workflow_builds_frontend_in_github_and_transfers_exact_bundle() -> None:
    workflow = (ROOT / ".github" / "workflows" / "digitalocean-production-main.yml").read_text(encoding="utf-8")
    required = [
        "actions/setup-node@v4",
        "node-version: '22'",
        "npm install --no-audit --no-fund",
        "runtime-os-bundle.py create",
        "runtime-os-bundle.py stage",
        "scp -i",
        "/var/lib/hhs/runtime-os/incoming/${TARGET_SHA}",
        "HHS_RUNTIME_OS_BUNDLE_SHA=\"$TARGET_SHA\"",
        "git rev-parse origin/main",
        "last-success.json",
        "runtime_os_bundle_sha",
        "production checkout is dirty after promotion",
        "HHS_RUNTIME_OUTPUT_DIR=/var/lib/hhs/data/runtime",
        "HHS_RUNTIME_OS_ASSET_ROOT=/var/lib/hhs/runtime-os/current",
        "readlink -f \"$BUNDLE_ROOT/current\"",
        "ServerAliveInterval=30",
        "ServerAliveCountMax=20",
        "hhs_backend.production_visual_server:app",
        "expected exactly one production listener on 8080",
        "EXPECTED_RUNTIME_OS_RELEASE",
        "Runtime OS asset authority mismatch",
        "/api/interface/status",
        "HHS Visual Runtime OS Workspace",
        "legacy_harmonizer_is_public_root",
        "/var/lib/hhs/runtime-os/releases/",
        "HHS_DIGITALOCEAN_PUBLIC_RUNTIME_OS_VERIFIED",
    ]
    for token in required:
        assert token in workflow
    assert "HHS_RUNTIME_OS_ROOT=/var/lib/hhs/runtime-os/current" not in workflow
    assert "npm ci --no-audit --no-fund" not in workflow
