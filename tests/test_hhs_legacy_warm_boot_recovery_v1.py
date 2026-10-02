from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
RECOVERY = ROOT / "deployment/digitalocean/guarded_auto_update/verify-recovery-state.py"
WARM_BOOT = ROOT / "deployment/digitalocean/warm_boot_manifest.py"
EXACT_MAIN = ROOT / ".github/workflows/digitalocean-production-main.yml"
INSTALLER = ROOT / "deployment/digitalocean/guarded_auto_update/install.sh"


def _run(command: list[str], *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def _fixture(root: Path) -> tuple[Path, Path, Path, dict[str, str], str]:
    repo = root / "repo"
    runtime = root / "runtime-os"
    manifests = root / "warm-boot" / "releases"
    (repo / "hhs_runtime" / "builds").mkdir(parents=True)
    (repo / "hhs_runtime" / "builds" / "libhhs_runtime.so").write_bytes(
        b"HHS-native-runtime-v1"
    )
    (runtime / "assets").mkdir(parents=True)
    (runtime / "index.html").write_text(
        "<!doctype html><title>HHS Visual Runtime OS Workspace</title>\n",
        encoding="utf-8",
    )
    (runtime / "assets" / "index.js").write_text(
        "window.HHS_RUNTIME_OS=true;\n",
        encoding="utf-8",
    )

    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "HHS Test"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "hhs-test@example.invalid"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "sealed rollback"], check=True)
    head = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        text=True,
    ).strip()

    state = root / "state"
    paths = {
        "HHS_DATA_DIR": state / "data",
        "HHS_PASS174_STATE_DIR": state / "pass174",
        "HHS_PASS194_STATE_ROOT": state / "pass194",
        "HHS_PASS205_DB": state / "pass205" / "continuation.sqlite3",
        "HHS_PASS213_SURFACE_STATE_DIR": state / "pass213" / "surface",
        "HHS_PASS218_STATE_ROOT": state / "pass218",
        "HHS_PASS219_LANE5_STATE_ROOT": state / "pass219" / "lane5",
        "HHS_RUNTIME_BOOTSTRAP_ROOT": state / "runtime-bootstrap",
    }
    for key, value in paths.items():
        directory = value.parent if key == "HHS_PASS205_DB" else value
        directory.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env.update({key: str(value) for key, value in paths.items()})
    env["HHS_DISABLE_C_AUTOBUILD"] = "1"
    return repo, runtime, manifests, env, head


def _seal(
    repo: Path,
    runtime: Path,
    manifests: Path,
    env: dict[str, str],
) -> None:
    result = _run(
        [
            "python3",
            str(WARM_BOOT),
            "create",
            "--repo-root",
            str(repo),
            "--runtime-os-root",
            str(runtime),
            "--manifest-root",
            str(manifests),
        ],
        env=env,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _receipt_log(path: Path, *, repo: Path, head: str) -> None:
    interrupted = "b" * 40
    row = {
        "schema": "HHS_GUARDED_UPDATE_RECEIPT_V2",
        "timestamp": "2026-10-02T00:00:00+00:00",
        "phase": "validation",
        "outcome": "VALIDATED",
        "detail": "candidate and bundle validated before first receipt-era promotion",
        "repository_root": str(repo.resolve()),
        "branch": "main",
        "previous_sha": head,
        "candidate_sha": interrupted,
        "runtime_os_bundle_sha": interrupted,
    }
    path.write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")


def _verify(
    *,
    receipts: Path,
    repo: Path,
    manifests: Path,
    env: dict[str, str],
    head: str,
    with_warm_proof: bool,
) -> subprocess.CompletedProcess[str]:
    command = [
        "python3",
        str(RECOVERY),
        "--receipt-log",
        str(receipts),
        "--current-head",
        head,
        "--repository-root",
        str(repo.resolve()),
        "--branch",
        "main",
    ]
    if with_warm_proof:
        command.extend(
            [
                "--warm-boot-verifier",
                str(WARM_BOOT),
                "--warm-boot-manifest-root",
                str(manifests),
            ]
        )
    return _run(command, env=env)


def test_legacy_recovery_requires_and_accepts_exact_i046_warm_boot_proof() -> None:
    with tempfile.TemporaryDirectory(prefix="hhs-legacy-recovery-") as tmp:
        root = Path(tmp)
        repo, runtime, manifests, env, head = _fixture(root)
        _seal(repo, runtime, manifests, env)
        receipts = root / "receipts.jsonl"
        _receipt_log(receipts, repo=repo, head=head)

        without_proof = _verify(
            receipts=receipts,
            repo=repo,
            manifests=manifests,
            env=env,
            head=head,
            with_warm_proof=False,
        )
        assert without_proof.returncode != 0
        assert (
            "HHS_RECOVERY_VALIDATED_PREVIOUS_SHA_NOT_PROVEN_PROMOTED"
            in without_proof.stdout
        )

        proven = _verify(
            receipts=receipts,
            repo=repo,
            manifests=manifests,
            env=env,
            head=head,
            with_warm_proof=True,
        )
        assert proven.returncode == 0, proven.stdout + proven.stderr
        report = json.loads(proven.stdout)
        assert (
            report["classification"]
            == "VALIDATED_PREPROMOTION_INTERRUPTION_LEGACY_WARM_BOOT"
        )
        assert report["rollback_boundary_sha"] == head
        assert report["prior_promoted_boundary_verified"] is False
        assert report["legacy_warm_boot_boundary_verified"] is True


def test_legacy_recovery_rejects_warm_boot_identity_tampering() -> None:
    with tempfile.TemporaryDirectory(prefix="hhs-legacy-recovery-negative-") as tmp:
        root = Path(tmp)
        repo, runtime, manifests, env, head = _fixture(root)
        receipts = root / "receipts.jsonl"
        _receipt_log(receipts, repo=repo, head=head)

        def verify_failure(expected: str) -> None:
            result = _verify(
                receipts=receipts,
                repo=repo,
                manifests=manifests,
                env=env,
                head=head,
                with_warm_proof=True,
            )
            assert result.returncode != 0
            combined = result.stdout + result.stderr
            assert "HHS_RECOVERY_LEGACY_WARM_BOOT_VERIFY_FAILED" in combined
            assert expected in combined

        _seal(repo, runtime, manifests, env)
        manifest = manifests / f"{head}.json"
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["manifest_sha256"] = "0" * 64
        manifest.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        verify_failure("HHS_WARM_BOOT_MANIFEST_DIGEST_MISMATCH")

        _seal(repo, runtime, manifests, env)
        native = repo / "hhs_runtime" / "builds" / "libhhs_runtime.so"
        native.write_bytes(b"HHS-native-runtime-tampered")
        verify_failure("HHS_WARM_BOOT_NATIVE_RUNTIME_IDENTITY_MISMATCH")
        native.write_bytes(b"HHS-native-runtime-v1")

        _seal(repo, runtime, manifests, env)
        index = runtime / "index.html"
        index.write_text("<title>tampered</title>\n", encoding="utf-8")
        verify_failure("HHS_WARM_BOOT_RUNTIME_OS_IDENTITY_MISMATCH")
        index.write_text(
            "<!doctype html><title>HHS Visual Runtime OS Workspace</title>\n",
            encoding="utf-8",
        )

        _seal(repo, runtime, manifests, env)
        state_root = Path(env["HHS_PASS218_STATE_ROOT"])
        shutil.rmtree(state_root)
        verify_failure("HHS_WARM_BOOT_STATE_ROOT_MISSING")


def test_production_recovery_call_sites_require_warm_boot_proof_inputs() -> None:
    workflow = EXACT_MAIN.read_text(encoding="utf-8")
    installer = INSTALLER.read_text(encoding="utf-8")
    for source in (workflow, installer):
        assert "--warm-boot-verifier" in source
        assert "--warm-boot-manifest-root /var/lib/hhs/warm-boot/releases" in source
    assert (
        '$bootstrap_root/deployment/digitalocean/warm_boot_manifest.py'
        in workflow
    )
    assert (
        '$SOURCE_ROOT/deployment/digitalocean/warm_boot_manifest.py'
        in installer
    )
