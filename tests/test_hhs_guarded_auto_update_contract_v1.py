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
        DEPLOY / "build-runtime-os.sh",
        DEPLOY / "validate-candidate.sh",
        DEPLOY / "install.sh",
        ROOT / "bin" / "post_compile",
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
        "build-runtime-os.sh",
    ]
    for token in required:
        assert token in source


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
        "npm run build",
        "dist/index.html",
        "dist/assets",
        "HHS Visual Runtime OS Workspace",
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


def test_installer_supports_safe_external_bootstrap_and_explicit_promotion() -> None:
    installer = read("install.sh")
    example = read("hhs-guarded-update.env.example")
    assert "SOURCE_ROOT=${SOURCE_ROOT:-$REPO_ROOT}" in installer
    assert "HHS_INSTALL_ENABLE_PROMOTION" in installer
    assert "HHS_UPDATE_DRY_RUN=0" in installer
    assert "HHS_UPDATE_DRY_RUN=1" in installer
    assert "HHS_UPDATE_DRY_RUN=1" in example


def test_github_merge_gate_is_label_and_trust_scoped() -> None:
    workflow = (ROOT / ".github" / "workflows" / "guarded-continuous-integration.yml").read_text(
        encoding="utf-8"
    )
    assert "hhs-automerge" in workflow
    assert "head.repo.full_name == github.repository" in workflow
    assert '"OWNER","MEMBER","COLLABORATOR"' in workflow
    assert "gh pr merge" in workflow
    assert "--merge --delete-branch" in workflow


def test_digitalocean_push_deployment_requires_exact_main_identity_and_runtime_os() -> None:
    workflow = (ROOT / ".github" / "workflows" / "digitalocean-production-main.yml").read_text(
        encoding="utf-8"
    )
    required = [
        "branches: [main]",
        "HHS_DIGITALOCEAN_SSH_PRIVATE_KEY",
        "TARGET_SHA: ${{ github.sha }}",
        "git rev-parse origin/main",
        "HHS_INSTALL_ENABLE_PROMOTION=1",
        "last-success.json",
        'payload.get("candidate_sha") != expected',
        "hhs-guarded-update.timer",
        "HHS_DIGITALOCEAN_EXACT_MAIN_PROMOTED",
        "/api/interface/status",
        "HHS Visual Runtime OS Workspace",
        "legacy_harmonizer_is_public_root",
    ]
    for token in required:
        assert token in workflow
