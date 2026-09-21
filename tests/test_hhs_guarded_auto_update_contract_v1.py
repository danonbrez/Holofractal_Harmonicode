from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deployment" / "digitalocean" / "guarded_auto_update"
BUNDLE_TOOL = DEPLOY / "runtime-os-bundle.py"


def read(name: str) -> str:
    return (DEPLOY / name).read_text(encoding="utf-8")


def test_shell_and_python_deployment_assets_parse() -> None:
    scripts = [
        DEPLOY / "hhs-guarded-update.sh",
        DEPLOY / "build-runtime-os.sh",
        DEPLOY / "preserve-host-drift.sh",
        DEPLOY / "validate-candidate.sh",
        DEPLOY / "install.sh",
        ROOT / "bin" / "post_compile",
    ]
    subprocess.run(["bash", "-n", *map(str, scripts)], check=True)
    subprocess.run(
        [
            "python3", "-m", "py_compile",
            str(BUNDLE_TOOL),
            str(DEPLOY / "normalize-service-permissions.py"),
            str(DEPLOY / "verify-recovery-state.py"),
        ],
        check=True,
    )


def test_runtime_os_bundle_is_sha_bound_hash_complete_and_rollback_safe() -> None:
    with tempfile.TemporaryDirectory(prefix="hhs-runtime-os-bundle-") as tmp:
        root = Path(tmp)
        dist = root / "dist"
        assets = dist / "assets"
        assets.mkdir(parents=True)
        (dist / "index.html").write_text(
            '<!doctype html><title>HHS Visual Runtime OS Workspace</title>'
            '<script type="module" src="/assets/index-test.js"></script>\n',
            encoding="utf-8",
        )
        (assets / "index-test.js").write_text("globalThis.HHS_RUNTIME_OS=true;\n", encoding="utf-8")

        bundle_root = root / "host-runtime-os"
        sha_a = "a" * 40
        archive_a = root / "a.tar.gz"
        manifest_a = root / "a.json"
        subprocess.run(
            ["python3", str(BUNDLE_TOOL), "create", "--dist", str(dist), "--repository-sha", sha_a,
             "--archive", str(archive_a), "--manifest", str(manifest_a)],
            check=True,
        )
        manifest = json.loads(manifest_a.read_text(encoding="utf-8"))
        assert manifest["schema"] == "HHS_RUNTIME_OS_DEPLOY_BUNDLE_V1"
        assert manifest["repository_sha"] == sha_a
        assert manifest["interface"] == "HHS_VISUAL_RUNTIME_OS_WORKSPACE"
        assert manifest["legacy_harmonizer_is_public_root"] is False
        assert {item["path"] for item in manifest["files"]} == {"index.html", "assets/index-test.js"}

        release_a = subprocess.check_output(
            ["python3", str(BUNDLE_TOOL), "stage", "--root", str(bundle_root), "--archive", str(archive_a),
             "--manifest", str(manifest_a), "--expected-sha", sha_a],
            text=True,
        ).strip()
        assert Path(release_a).is_dir()
        subprocess.run(
            ["python3", str(BUNDLE_TOOL), "verify", "--root", str(bundle_root), "--expected-sha", sha_a],
            check=True,
        )
        subprocess.run(
            ["python3", str(BUNDLE_TOOL), "activate", "--root", str(bundle_root), "--expected-sha", sha_a],
            check=True,
        )
        assert (bundle_root / "current").resolve() == Path(release_a).resolve()

        wrong = subprocess.run(
            ["python3", str(BUNDLE_TOOL), "stage", "--root", str(root / "wrong"), "--archive", str(archive_a),
             "--manifest", str(manifest_a), "--expected-sha", "c" * 40],
            text=True,
            capture_output=True,
        )
        assert wrong.returncode != 0
        assert "repository SHA mismatch" in (wrong.stderr + wrong.stdout)

        corrupted = root / "corrupted.tar.gz"
        corrupted.write_bytes(archive_a.read_bytes() + b"corruption")
        corrupt = subprocess.run(
            ["python3", str(BUNDLE_TOOL), "stage", "--root", str(root / "corrupt"), "--archive", str(corrupted),
             "--manifest", str(manifest_a), "--expected-sha", sha_a],
            text=True,
            capture_output=True,
        )
        assert corrupt.returncode != 0
        assert "archive length mismatch" in (corrupt.stderr + corrupt.stdout)

        sha_b = "b" * 40
        (assets / "index-test.js").write_text("globalThis.HHS_RUNTIME_OS='second';\n", encoding="utf-8")
        archive_b = root / "b.tar.gz"
        manifest_b = root / "b.json"
        subprocess.run(
            ["python3", str(BUNDLE_TOOL), "create", "--dist", str(dist), "--repository-sha", sha_b,
             "--archive", str(archive_b), "--manifest", str(manifest_b)],
            check=True,
        )
        release_b = subprocess.check_output(
            ["python3", str(BUNDLE_TOOL), "stage", "--root", str(bundle_root), "--archive", str(archive_b),
             "--manifest", str(manifest_b), "--expected-sha", sha_b],
            text=True,
        ).strip()
        subprocess.run(
            ["python3", str(BUNDLE_TOOL), "activate", "--root", str(bundle_root), "--expected-sha", sha_b],
            check=True,
        )
        assert (bundle_root / "current").resolve() == Path(release_b).resolve()
        subprocess.run(
            ["python3", str(BUNDLE_TOOL), "restore", "--root", str(bundle_root), "--release", release_a],
            check=True,
        )
        assert (bundle_root / "current").resolve() == Path(release_a).resolve()

        legacy = root / "legacy"
        (legacy / "assets").mkdir(parents=True)
        (legacy / "index.html").write_text("<title>Legacy Harmonizer</title>\n", encoding="utf-8")
        (legacy / "assets" / "index-old.js").write_text("// old\n", encoding="utf-8")
        rejected = subprocess.run(
            ["python3", str(BUNDLE_TOOL), "create", "--dist", str(legacy), "--repository-sha", sha_a,
             "--archive", str(root / "legacy.tar.gz"), "--manifest", str(root / "legacy.json")],
            text=True,
            capture_output=True,
        )
        assert rejected.returncode != 0
        assert "index identity missing" in (rejected.stderr + rejected.stdout)


def test_updater_is_fail_closed_fast_forward_only_drift_preserving_and_bundle_atomic() -> None:
    source = read("hhs-guarded-update.sh")
    required = [
        "flock -n",
        "merge-base --is-ancestor",
        "merge --ff-only",
        "rollback_live_checkout",
        "wait_for_health",
        "receipts.jsonl",
        "HHS_EXPECTED_REPOSITORY",
        "preserve-host-drift.sh",
        "reconcile_host_drift source",
        "reconcile_host_drift final",
        "runtime-os-bundle.py",
        "require_candidate_bundle",
        "capture_current_runtime_os",
        "activate_candidate_runtime_os",
        "restore_previous_runtime_os",
        'POST_MERGE_COMMAND=${HHS_POST_MERGE_COMMAND:-bash bin/post_compile}',
        'ROLLBACK_COMMAND=${HHS_ROLLBACK_COMMAND:-bash bin/post_compile}',
        "runtime_os_bundle_sha",
        "normalize_service_permissions",
        "normalize-service-permissions.py",
        "verify-recovery-state.py",
    ]
    for token in required:
        assert token in source
    assert "npm " not in source


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

        env = dict(os.environ, HHS_UPDATE_STATE_ROOT=str(state), HHS_RUNTIME_OUTPUT_DIR=str(runtime), HHS_HOST_DRIFT_MODE="source")
        source_run = subprocess.run(["bash", str(script), str(repo)], check=True, text=True, capture_output=True, env=env)
        assert "HHS_HOST_DRIFT_MODE=source" in source_run.stdout
        assert tracked.read_text(encoding="utf-8") == "committed\n"
        assert journal.is_file()
        assert subprocess.run(["git", "-C", str(repo), "diff-index", "--quiet", "HEAD", "--"], check=False).returncode == 0
        source_manifests = sorted((state / "host-drift").glob("*-source-*/manifest.json"))
        assert len(source_manifests) == 1
        source_manifest = json.loads(source_manifests[0].read_text(encoding="utf-8"))
        assert source_manifest["host_edits_preserved_before_reset"] is True
        assert (source_manifests[0].parent / "tracked.patch").stat().st_size > 0
        assert (source_manifests[0].parent / "untracked-files.tar.gz").stat().st_size > 0

        env["HHS_HOST_DRIFT_MODE"] = "final"
        final_run = subprocess.run(["bash", str(script), str(repo)], check=True, text=True, capture_output=True, env=env)
        assert "committed-snapshot-and-repository-journal-migrated" in final_run.stdout
        assert not journal.exists()
        assert (runtime / "hhs_unified_hash72_ledger.json").read_text(encoding="utf-8") == snapshot.read_text(encoding="utf-8")
        assert subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain=v1", "--untracked-files=normal"], text=True) == ""


def test_candidate_gate_uses_prebuilt_bundle_in_production_and_retains_source_mode() -> None:
    source = read("validate-candidate.sh")
    for token in [
        "HHS_RUNTIME_OS_BUNDLE_MODE",
        "HHS_RUNTIME_OS_BUNDLE_SHA",
        "runtime-os-bundle.py",
        '"$PYTHON" "$BUNDLE_TOOL" stage',
        '"$PYTHON" "$BUNDLE_TOOL" verify',
        "canonical Runtime OS source build",
        "hhs_backend.runtime_os_application_server:app",
        'HHS_RUNTIME_OS_ASSET_ROOT="$RUNTIME_OS_ROOT"',
        'env -u HHS_RUNTIME_OS_ROOT',
        "candidate Runtime OS asset authority mismatch",
        "/api/system/status",
        "/api/interface/status",
        "/api/runtime/repository/health",
        "HHS Visual Runtime OS Workspace",
        "/api/runtime/workspace/session",
    ]:
        assert token in source
    assert 'HHS_RUNTIME_OS_ROOT="$RUNTIME_OS_ROOT"' not in source


def test_source_builder_remains_available_for_ci_and_development_without_fake_lockfile_authority() -> None:
    source = read("build-runtime-os.sh")
    for token in [
        "command -v node",
        "command -v npm",
        "npm install --no-audit --no-fund",
        "npm run typecheck",
        "HHS Visual Runtime OS Workspace",
    ]:
        assert token in source
    assert "package-lock.json missing" not in source
    assert "npm ci --no-audit --no-fund" not in source


def test_installer_pins_prebuilt_bundle_and_repairs_failed_service_only_by_receipt() -> None:
    installer = read("install.sh")
    example = read("hhs-guarded-update.env.example")
    stable_build = "make c-abi && test -s hhs_runtime/builds/libhhs_runtime.so && /opt/hhs/venv/bin/python tools/install_production_language_assets.py --install-if-configured --require-assistant"
    for token in [
        "HHS_RUNTIME_OS_BUNDLE_SHA",
        "HHS_RUNTIME_OS_BUNDLE_MODE=prebuilt",
        "runtime-os-bundle.py",
        "promotion requires exact HHS_RUNTIME_OS_BUNDLE_SHA",
        "HHS_INSTALL_RECOVERY_MODE",
        "verify-recovery-state.py",
        "Recovery mode refused because another listener already owns port 8080",
        "HHS_GUARDED_UPDATE_RECOVERY_RECEIPT_VERIFIED=1",
        "HHS_ROLLBACK_BOUNDARY_HEALTHY=1",
        "normalize_production_checkout",
        "HHS PRODUCTION SERVICE DIAGNOSTICS",
        "HHS_POST_MERGE_COMMAND=$NATIVE_BUILD",
        "HHS_ROLLBACK_COMMAND=$NATIVE_BUILD",
        "HHS_HEALTH_TIMEOUT_SECONDS=$PRODUCTION_HEALTH_TIMEOUT",
    ]:
        assert token in installer
    assert "HHS_RUNTIME_OS_BUNDLE_MODE=prebuilt" in example
    assert "HHS_HEALTH_TIMEOUT_SECONDS=600\n" in example
    assert f"HHS_POST_MERGE_COMMAND={stable_build}\n" in example
    assert f"HHS_ROLLBACK_COMMAND={stable_build}\n" in example
    assert "bash bin/post_compile\n" not in example


def test_exact_main_promotion_has_one_updater_owner_timer_follower_and_receipt_gated_recovery() -> None:
    installer = read("install.sh")
    workflow = (ROOT / ".github" / "workflows" / "digitalocean-production-main.yml").read_text(encoding="utf-8")

    installer_stop = installer.index("systemctl stop hhs-guarded-update.timer")
    installer_wait = installer.index("while :; do", installer_stop)
    installer_start = installer.index("systemctl start hhs-guarded-update.service")
    installer_enable_timer = installer.index("systemctl enable hhs-guarded-update.timer")
    installer_start_timer = installer.index("systemctl start hhs-guarded-update.timer", installer_enable_timer)
    assert installer_stop < installer_wait < installer_start < installer_enable_timer < installer_start_timer
    assert "systemctl enable --now hhs-guarded-update.timer" not in installer
    assert "timer remains stopped" in installer
    assert "systemctl reset-failed hhs-guarded-update.service" in installer
    assert "hhs.service is not active after prior guarded updater ownership ended" in installer

    claim = workflow.index("=== CLAIM EXACT-MAIN UPDATER OWNERSHIP ===")
    workflow_stop = workflow.index("systemctl stop hhs-guarded-update.timer", claim)
    ownership_witness = workflow.index("HHS_EXACT_MAIN_UPDATER_OWNERSHIP_CLAIMED=1", claim)
    git_fetch = workflow.index("git fetch --prune origin main", claim)
    drift = workflow.index("HHS_HOST_DRIFT_MODE=source", claim)
    recovery = workflow.index("HHS_EXACT_MAIN_RECOVERY_MODE=1", drift)
    handoff = workflow.index("PROMOTION_HANDOFF=1", recovery)
    installer_call = workflow.index("HHS_INSTALL_ENABLE_PROMOTION=1", handoff)
    assert claim < workflow_stop < ownership_witness < git_fetch < drift < recovery < handoff < installer_call
    for token in [
        "verify-recovery-state.py",
        "SERVICE_INACTIVE=1",
        'HHS_INSTALL_RECOVERY_MODE="$RECOVERY_MODE"',
        "HHS_PRODUCTION_HEALTH_TIMEOUT_SECONDS=600",
        "EXACT-MAIN PRODUCTION RECOVERY DIAGNOSTICS",
        "flock -w 10 8",
        '$PROMOTION_HANDOFF" == "0"',
        "systemctl start hhs-guarded-update.timer",
    ]:
        assert token in workflow


def test_recovery_verifier_accepts_only_proven_safe_boundaries() -> None:
    verifier = DEPLOY / "verify-recovery-state.py"
    root = "/opt/hhs/app"
    branch = "main"
    promoted = "a" * 40
    interrupted = "b" * 40
    earlier = "c" * 40

    def receipt(*, phase: str, outcome: str, previous: str, candidate: str, bundle: str) -> dict:
        return {
            "schema": "HHS_GUARDED_UPDATE_RECEIPT_V2",
            "timestamp": "2026-09-21T00:00:00+00:00",
            "phase": phase,
            "outcome": outcome,
            "detail": "test",
            "repository_root": root,
            "branch": branch,
            "previous_sha": previous,
            "candidate_sha": candidate,
            "runtime_os_bundle_sha": bundle,
        }

    def run(rows: list[dict], head: str):
        with tempfile.TemporaryDirectory(prefix="hhs-recovery-verifier-") as tmp:
            path = Path(tmp) / "receipts.jsonl"
            path.write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
                encoding="utf-8",
            )
            return subprocess.run(
                [
                    "python3",
                    str(verifier),
                    "--receipt-log",
                    str(path),
                    "--current-head",
                    head,
                    "--repository-root",
                    root,
                    "--branch",
                    branch,
                ],
                text=True,
                capture_output=True,
            )

    promoted_row = receipt(
        phase="promotion",
        outcome="PROMOTED",
        previous=earlier,
        candidate=promoted,
        bundle=promoted,
    )
    validated_row = receipt(
        phase="validation",
        outcome="VALIDATED",
        previous=promoted,
        candidate=interrupted,
        bundle=interrupted,
    )

    safe = run([promoted_row, validated_row], promoted)
    assert safe.returncode == 0, safe.stdout + safe.stderr
    report = json.loads(safe.stdout)
    assert report["classification"] == "VALIDATED_PREPROMOTION_INTERRUPTION"
    assert report["rollback_boundary_sha"] == promoted
    assert report["prior_promoted_boundary_verified"] is True
    assert report["service_restart_before_new_promotion_required"] is True

    no_prior_promotion = run([validated_row], promoted)
    assert no_prior_promotion.returncode != 0
    assert "HHS_RECOVERY_VALIDATED_PREVIOUS_SHA_NOT_PROVEN_PROMOTED" in no_prior_promotion.stdout

    partially_advanced = run([promoted_row, validated_row], interrupted)
    assert partially_advanced.returncode != 0
    assert "HHS_RECOVERY_LIVE_HEAD_NOT_ROLLBACK_BOUNDARY" in partially_advanced.stdout

    mismatch = dict(validated_row)
    mismatch["runtime_os_bundle_sha"] = "d" * 40
    bad_bundle = run([promoted_row, mismatch], promoted)
    assert bad_bundle.returncode != 0
    assert "HHS_RECOVERY_VALIDATED_CANDIDATE_BUNDLE_IDENTITY_MISMATCH" in bad_bundle.stdout

    rollback_failed = receipt(
        phase="rollback",
        outcome="ROLLBACK_HEALTH_FAILED",
        previous=promoted,
        candidate=interrupted,
        bundle=interrupted,
    )
    legacy_safe = run([rollback_failed], promoted)
    assert legacy_safe.returncode == 0
    legacy_report = json.loads(legacy_safe.stdout)
    assert legacy_report["classification"] == "ROLLBACK_HEALTH_FAILED"


def test_post_compile_uses_guarded_python_interpreter_contract() -> None:
    source = (ROOT / "bin" / "post_compile").read_text(encoding="utf-8")
    assert 'HHS_POST_COMPILE_PYTHON' in source
    assert 'HHS_VALIDATE_PYTHON' in source
    assert 'command -v "$PYTHON_BIN"' in source
    assert '"$PYTHON_BIN" tools/install_production_language_assets.py' in source


def test_timer_and_service_are_bounded() -> None:
    timer = read("hhs-guarded-update.timer")
    service = read("hhs-guarded-update.service")
    production_service = (ROOT / "deploy" / "digitalocean" / "hhs-pass196-integrated-environment.service").read_text(encoding="utf-8")
    assert "OnUnitActiveSec=5min" in timer
    assert "RandomizedDelaySec=30s" in timer
    assert "TimeoutStartSec=90min" in service
    assert "Type=oneshot" in service
    assert "NoNewPrivileges=true" in service
    assert "Environment=HHS_COGNITION_AUTO_TICK=0" in production_service


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
        "HHS_COGNITION_AUTO_TICK=0",
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
        "HHS_PRODUCTION_SERVICE_PERMISSIONS_VERIFIED=1",
        'runuser -u hhs -- test -r "$APP_ROOT/hhs_backend/__init__.py"',
    ]
    for token in required:
        assert token in workflow
    assert "HHS_RUNTIME_OS_ROOT=/var/lib/hhs/runtime-os/current" not in workflow
    assert "npm ci --no-audit --no-fund" not in workflow



def test_promotion_normalizes_stale_candidate_validation_timeout() -> None:
    source = read("install.sh")
    assert "minimum_validate_timeout = 3600" in source
    assert 'values["HHS_VALIDATE_TIMEOUT_SECONDS"] = str(' in source
    assert "max(minimum_validate_timeout, current_validate_timeout)" in source
    assert '"HHS_VALIDATE_TIMEOUT_SECONDS",' in source
