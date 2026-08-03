from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deployment" / "digitalocean" / "guarded_auto_update"


def read(name: str) -> str:
    return (DEPLOY / name).read_text(encoding="utf-8")


def test_shell_assets_parse() -> None:
    scripts = [
        DEPLOY / "hhs-guarded-update.sh",
        DEPLOY / "validate-candidate.sh",
        DEPLOY / "install.sh",
    ]
    subprocess.run(["bash", "-n", *map(str, scripts)], check=True)


def test_updater_is_fail_closed_and_fast_forward_only() -> None:
    source = read("hhs-guarded-update.sh")
    required = [
        "flock -n",
        "status --porcelain",
        "merge-base --is-ancestor",
        "merge --ff-only",
        "rollback_live_checkout",
        "wait_for_health",
        "receipts.jsonl",
        "HHS_EXPECTED_REPOSITORY",
        "sync_installed_assets",
        "ROLLBACK_COMMAND",
    ]
    for token in required:
        assert token in source


def test_candidate_gate_covers_integrated_runtime() -> None:
    source = read("validate-candidate.sh")
    required = [
        "bin/post_compile",
        "test_hhs_full_application_ide_root_v1.py",
        "application.studio.test.mjs",
        "hhs_backend.application_ide_server:app",
        "/api/system/status",
        "/api/runtime/repository/status",
        "/api/runtime/workspace/session",
    ]
    for token in required:
        assert token in source


def test_timer_and_service_are_bounded() -> None:
    timer = read("hhs-guarded-update.timer")
    service = read("hhs-guarded-update.service")
    assert "OnUnitActiveSec=5min" in timer
    assert "RandomizedDelaySec=30s" in timer
    assert "TimeoutStartSec=90min" in service
    assert "Type=oneshot" in service
    assert "NoNewPrivileges=true" in service


def test_installer_bootstraps_in_dry_run_mode() -> None:
    installer = read("install.sh")
    example = read("hhs-guarded-update.env.example")
    assert "HHS_UPDATE_DRY_RUN=1" in installer
    assert "HHS_UPDATE_DRY_RUN=1" in example
    assert "set HHS_UPDATE_DRY_RUN=0" in installer


def test_github_merge_gate_is_label_and_trust_scoped() -> None:
    workflow = (ROOT / ".github" / "workflows" / "guarded-continuous-integration.yml").read_text(
        encoding="utf-8"
    )
    assert "hhs-automerge" in workflow
    assert "head.repo.full_name == github.repository" in workflow
    assert '"OWNER","MEMBER","COLLABORATOR"' in workflow
    assert "gh pr merge" in workflow
    assert "--merge --delete-branch" in workflow
