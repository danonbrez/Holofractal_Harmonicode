from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deployment" / "digitalocean" / "guarded_auto_update"


def read(name: str) -> str:
    return (DEPLOY / name).read_text(encoding="utf-8")


def test_shell_assets_parse() -> None:
    scripts = [
        DEPLOY / "hhs-guarded-update.sh",
        DEPLOY / "build-runtime-os.sh",
        DEPLOY / "preserve-host-drift.sh",
        DEPLOY / "validate-candidate.sh",
        DEPLOY / "install.sh",
        ROOT / "bin" / "post_compile",
    ]
    subprocess.run(["bash", "-n", *map(str, scripts)], check=True)


def test_updater_is_fail_closed_fast_forward_only_and_drift_preserving() -> None:
    source = read("hhs-guarded-update.sh")
    required = [
        "flock -n",
        "merge-base --is-ancestor",
        "merge --ff-only",
        "rollback_live_checkout",
        "wait_for_health",
        "receipts.jsonl",
        "HHS_EXPECTED_REPOSITORY",
        "sync_installed_assets",
        "ROLLBACK_COMMAND",
        "build-runtime-os.sh",
        "preserve-host-drift.sh",
        "reconcile_host_drift source",
        "reconcile_host_drift final",
        "Stopping live units for final host-state reconciliation",
        "Tracked live checkout drift remains after reconciliation",
        "hhs-pass196-integrated-environment.service",
    ]
    for token in required:
        assert token in source


def test_host_drift_reconciler_preserves_source_and_migrates_runtime_journal() -> None:
    script = DEPLOY / "preserve-host-drift.sh"
    with tempfile.TemporaryDirectory(prefix="hhs-drift-test-") as tmp:
        root = Path(tmp)
        repo = root / "repo"
        state = root / "state"
        runtime = root / "runtime"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "hhs-test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "HHS Test"], check=True)

        (repo / "data" / "runtime").mkdir(parents=True)
        snapshot = repo / "data" / "runtime" / "hhs_unified_hash72_ledger.json"
        journal = repo / "data" / "runtime" / "hhs_unified_hash72_ledger.json.journal.jsonl"
        tracked = repo / "tracked.txt"
        snapshot.write_text('{"schema":"TEST_LEDGER","entries":[]}\n', encoding="utf-8")
        tracked.write_text("committed\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "baseline"], check=True)

        tracked.write_text("host-local-edit\n", encoding="utf-8")
        journal.write_text('{"schema":"TEST_JOURNAL","entry_count":1}\n', encoding="utf-8")

        env = dict(os.environ)
        env.update(
            HHS_UPDATE_STATE_ROOT=str(state),
            HHS_RUNTIME_OUTPUT_DIR=str(runtime),
            HHS_HOST_DRIFT_MODE="source",
        )
        source_run = subprocess.run(
            ["bash", str(script), str(repo)],
            check=True,
            text=True,
            capture_output=True,
            env=env,
        )
        assert "HHS_HOST_DRIFT_MODE=source" in source_run.stdout
        assert tracked.read_text(encoding="utf-8") == "committed\n"
        assert journal.is_file(), "live runtime journal must remain while service may still be active"
        assert subprocess.run(
            ["git", "-C", str(repo), "diff-index", "--quiet", "HEAD", "--"],
            check=False,
        ).returncode == 0

        source_manifests = sorted((state / "host-drift").glob("*-source-*/manifest.json"))
        assert len(source_manifests) == 1
        source_manifest = json.loads(source_manifests[0].read_text(encoding="utf-8"))
        assert source_manifest["host_edits_preserved_before_reset"] is True
        assert any("tracked.txt" in line for line in source_manifest["status"])
        assert (source_manifests[0].parent / "tracked.patch").stat().st_size > 0
        assert (source_manifests[0].parent / "untracked-files.tar.gz").stat().st_size > 0

        env["HHS_HOST_DRIFT_MODE"] = "final"
        final_run = subprocess.run(
            ["bash", str(script), str(repo)],
            check=True,
            text=True,
            capture_output=True,
            env=env,
        )
        assert "HHS_HOST_DRIFT_MODE=final" in final_run.stdout
        assert "committed-snapshot-and-repository-journal-migrated" in final_run.stdout
        assert not journal.exists()
        assert (runtime / "hhs_unified_hash72_ledger.json").read_text(encoding="utf-8") == snapshot.read_text(encoding="utf-8")
        assert (runtime / "hhs_unified_hash72_ledger.json.journal.jsonl").read_text(encoding="utf-8") == '{"schema":"TEST_JOURNAL","entry_count":1}\n'
        assert subprocess.check_output(
            ["git", "-C", str(repo), "status", "--porcelain=v1", "--untracked-files=normal"],
            text=True,
        ) == ""

        final_manifests = sorted((state / "host-drift").glob("*-final-*/manifest.json"))
        assert len(final_manifests) == 1
        final_manifest = json.loads(final_manifests[0].read_text(encoding="utf-8"))
        assert final_manifest["ledger_migration"] == "committed-snapshot-and-repository-journal-migrated"


def test_candidate_gate_covers_runtime_os_and_integrated_runtime() -> None:
    source = read("validate-candidate.sh")
    required = [
        "bin/post_compile",
        "build-runtime-os.sh",
        "test_hhs_full_application_ide_root_v1.py",
        "application.studio.test.mjs",
        "hhs_backend.runtime_os_application_server:app",
        "/api/system/status",
        "/api/interface/status",
        "HHS Visual Runtime OS Workspace",
        "/api/runtime/repository/status",
        "/api/runtime/workspace/session",
    ]
    for token in required:
        assert token in source


def test_runtime_os_builder_is_source_driven_and_fail_closed() -> None:
    source = read("build-runtime-os.sh")
    required = [
        "command -v node",
        "command -v npm",
        "package-lock.json",
        "npm ci --no-audit --no-fund",
        "npm run typecheck",
        'npm run build -- --outDir "$OUTPUT_ROOT" --emptyOutDir',
        "OUTPUT_ROOT=/var/lib/hhs/runtime-os/dist",
        '$OUTPUT_ROOT/index.html',
        '$OUTPUT_ROOT/assets',
        "HHS Visual Runtime OS Workspace",
        '/etc/systemd/system/hhs.service',
    ]
    for token in required:
        assert token in source


def test_post_compile_uses_guarded_python_interpreter_contract() -> None:
    source = (ROOT / "bin" / "post_compile").read_text(encoding="utf-8")
    assert 'HHS_POST_COMPILE_PYTHON' in source
    assert 'HHS_VALIDATE_PYTHON' in source
    assert 'python3' in source
    assert 'command -v "$PYTHON_BIN"' in source
    assert '"$PYTHON_BIN" tools/install_production_language_assets.py' in source
    assert '\npython tools/install_production_language_assets.py' not in source


def test_timer_and_service_are_bounded() -> None:
    timer = read("hhs-guarded-update.timer")
    service = read("hhs-guarded-update.service")
    assert "OnUnitActiveSec=5min" in timer
    assert "RandomizedDelaySec=30s" in timer
    assert "TimeoutStartSec=90min" in service
    assert "Type=oneshot" in service
    assert "NoNewPrivileges=true" in service


def test_installer_supports_safe_external_bootstrap_runtime_os_and_drift_migration() -> None:
    installer = read("install.sh")
    example = read("hhs-guarded-update.env.example")
    assert "SOURCE_ROOT=${SOURCE_ROOT:-$REPO_ROOT}" in installer
    assert "HHS_INSTALL_ENABLE_PROMOTION" in installer
    assert "HHS_UPDATE_DRY_RUN=0" in installer
    assert "HHS_UPDATE_DRY_RUN=1" in installer
    assert "HHS_UPDATE_DRY_RUN=1" in example
    assert "CANONICAL_HHS_SERVICE" in installer
    assert "RUNTIME_OS_BUILD" in installer
    assert "HHS_POST_MERGE_COMMAND=bash bin/post_compile" in installer
    assert "HHS_ROLLBACK_COMMAND=bash bin/post_compile" in installer
    assert "build-runtime-os.sh" in installer
    assert "preserve-host-drift.sh" in installer
    assert "host-drift" in installer
    assert "build-runtime-os.sh" in example


def test_github_merge_gate_is_label_and_trust_scoped() -> None:
    workflow = (ROOT / ".github" / "workflows" / "guarded-continuous-integration.yml").read_text(
        encoding="utf-8"
    )
    assert "hhs-automerge" in workflow
    assert "head.repo.full_name == github.repository" in workflow
    assert '"OWNER","MEMBER","COLLABORATOR"' in workflow
    assert "gh pr merge" in workflow
    assert "--merge --delete-branch" in workflow


def test_digitalocean_push_deployment_requires_exact_main_identity_runtime_os_and_clean_checkout() -> None:
    workflow = (ROOT / ".github" / "workflows" / "digitalocean-production-main.yml").read_text(
        encoding="utf-8"
    )
    required = [
        "branches: [main]",
        "HHS_DIGITALOCEAN_SSH_PRIVATE_KEY",
        "TARGET_SHA: ${{ github.sha }}",
        "git rev-parse origin/main",
        "HHS_INSTALL_ENABLE_PROMOTION=1",
        "preserve-host-drift.sh",
        "HHS_HOST_DRIFT_MODE=source",
        "last-success.json",
        'payload.get("candidate_sha") != expected',
        "hhs-guarded-update.timer",
        "HHS_DIGITALOCEAN_EXACT_MAIN_PROMOTED",
        "production checkout is dirty after promotion",
        "HHS_RUNTIME_OUTPUT_DIR=/var/lib/hhs/data/runtime",
        "HHS_RUNTIME_OS_ROOT=/var/lib/hhs/runtime-os/current",
        "/api/interface/status",
        "HHS Visual Runtime OS Workspace",
        "legacy_harmonizer_is_public_root",
        "HHS_DIGITALOCEAN_HOST_DRIFT_MANIFEST",
    ]
    for token in required:
        assert token in workflow
