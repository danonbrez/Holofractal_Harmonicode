from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deployment" / "digitalocean" / "guarded_auto_update"
BUNDLE_TOOL = DEPLOY / "runtime-os-bundle.py"
UPDATER = DEPLOY / "hhs-guarded-update.sh"


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def _create_bundle(root: Path, sha: str) -> tuple[Path, Path]:
    dist = root / "dist"
    assets = dist / "assets"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text(
        '<!doctype html><title>HHS Visual Runtime OS Workspace</title>'
        '<script type="module" src="/assets/index-test.js"></script>\n',
        encoding="utf-8",
    )
    (assets / "index-test.js").write_text(
        "globalThis.HHS_RUNTIME_OS=true;\n", encoding="utf-8"
    )
    archive = root / "runtime-os.tar.gz"
    manifest = root / "manifest.json"
    subprocess.run(
        [
            "python3",
            str(BUNDLE_TOOL),
            "create",
            "--dist",
            str(dist),
            "--repository-sha",
            sha,
            "--archive",
            str(archive),
            "--manifest",
            str(manifest),
        ],
        check=True,
    )
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["repository_sha"] == sha
    return archive, manifest


def _stage(bundle_root: Path, archive: Path, manifest: Path, sha: str) -> Path:
    output = subprocess.check_output(
        [
            "python3",
            str(BUNDLE_TOOL),
            "stage",
            "--root",
            str(bundle_root),
            "--archive",
            str(archive),
            "--manifest",
            str(manifest),
            "--expected-sha",
            sha,
        ],
        text=True,
    )
    return Path(output.strip())


def test_stage_normalizes_release_root_and_descendants_for_unprivileged_service() -> None:
    with tempfile.TemporaryDirectory(prefix="hhs-runtime-os-permission-") as tmp:
        root = Path(tmp)
        sha = "d" * 40
        archive, manifest = _create_bundle(root, sha)
        bundle_root = root / "runtime-os"

        release = _stage(bundle_root, archive, manifest, sha)
        assert release == bundle_root / "releases" / sha
        assert _mode(bundle_root) == 0o755
        assert _mode(bundle_root / "releases") == 0o755
        assert _mode(release) == 0o755

        for path in release.rglob("*"):
            assert _mode(path) == (0o755 if path.is_dir() else 0o644)

        subprocess.run(
            [
                "python3",
                str(BUNDLE_TOOL),
                "verify",
                "--root",
                str(bundle_root),
                "--expected-sha",
                sha,
            ],
            check=True,
        )


def test_stage_repairs_existing_0700_release_before_activation() -> None:
    with tempfile.TemporaryDirectory(prefix="hhs-runtime-os-existing-") as tmp:
        root = Path(tmp)
        sha = "e" * 40
        archive, manifest = _create_bundle(root, sha)
        bundle_root = root / "runtime-os"
        release = _stage(bundle_root, archive, manifest, sha)

        release.chmod(0o700)
        assert _mode(release) == 0o700

        repaired = _stage(bundle_root, archive, manifest, sha)
        assert repaired == release
        assert _mode(repaired) == 0o755
        assert _mode(repaired / "index.html") == 0o644


def test_verify_rejects_release_root_that_service_cannot_traverse() -> None:
    with tempfile.TemporaryDirectory(prefix="hhs-runtime-os-reject-") as tmp:
        root = Path(tmp)
        sha = "f" * 40
        archive, manifest = _create_bundle(root, sha)
        bundle_root = root / "runtime-os"
        release = _stage(bundle_root, archive, manifest, sha)
        release.chmod(0o700)

        completed = subprocess.run(
            [
                "python3",
                str(BUNDLE_TOOL),
                "verify",
                "--root",
                str(bundle_root),
                "--expected-sha",
                sha,
            ],
            text=True,
            capture_output=True,
        )
        assert completed.returncode != 0
        assert "Runtime OS directory mode mismatch" in (completed.stdout + completed.stderr)


def test_rollback_keeps_validated_candidate_controller_while_restoring_previous_service() -> None:
    source = UPDATER.read_text(encoding="utf-8")
    assert "local controller_root=${1:-$REPO_ROOT}" in source
    assert "local service_root=${2:-$controller_root}" in source
    assert 'local rollback_controller_root="$CURRENT_CANDIDATE"' in source
    assert 'sync_installed_assets "$rollback_controller_root" "$REPO_ROOT"' in source
    assert "transaction controller must not downgrade itself" in source
    assert 'local hhs_service="$service_root/deploy/digitalocean/hhs-pass196-integrated-environment.service"' in source
