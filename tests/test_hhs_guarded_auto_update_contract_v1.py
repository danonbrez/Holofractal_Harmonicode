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


def test_production_service_routes_live_semantic_cache_to_writable_runtime_state() -> None:
    production_service = (
        ROOT / "deploy" / "digitalocean" / "hhs-pass196-integrated-environment.service"
    ).read_text(encoding="utf-8")

    assert "Environment=HHS_RUNTIME_OUTPUT_DIR=/var/lib/hhs/data/runtime" in production_service
    assert (
        "Environment=HHS_LIVE_SEMANTIC_COMPOSITION_CACHE_PATH="
        "/var/lib/hhs/data/runtime/hhs_live_semantic_composition_cache_pass217.json"
    ) in production_service
    assert "Environment=HHS_COGNITION_AUTO_TICK=0" in production_service
    assert "ProtectSystem=full" in production_service
    assert "ReadWritePaths=/var/lib/hhs" in production_service


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


def test_production_candidate_validation_uses_explicit_hhs_venv_python() -> None:
    installer = read("install.sh")
    example = read("hhs-guarded-update.env.example")
    validator = read("validate-candidate.sh")

    binding = (
        'VALIDATE_PYTHON=${HHS_VALIDATE_PYTHON:-/opt/hhs/venv/bin/python}'
    )
    assert binding in installer
    assert '[[ -x "$VALIDATE_PYTHON" ]]' in installer
    assert '"$VALIDATE_PYTHON" -c \'import pytest\'' in installer
    assert "HHS_PRODUCTION_VALIDATE_PYTHON_VERIFIED=$VALIDATE_PYTHON" in installer

    assert "HHS_VALIDATE_PYTHON=$VALIDATE_PYTHON" in installer
    assert 'VALIDATE_PYTHON_VALUE="$VALIDATE_PYTHON"' in installer
    assert 'values["HHS_VALIDATE_PYTHON"] = validate_python' in installer
    assert '"HHS_VALIDATE_PYTHON",' in installer
    assert "HHS_VALIDATE_PYTHON=/opt/hhs/venv/bin/python\n" in example

    # Generic CI/development validation remains overridable and does not require
    # a production filesystem layout. The production installer supplies the
    # explicit venv path through its EnvironmentFile.
    assert 'PYTHON=${HHS_VALIDATE_PYTHON:-python3}' in validator


def test_installer_binds_lane5_socket_before_strict_unbound_use() -> None:
    installer = read("install.sh")
    binding = (
        'LANE5_INGRESS_SOCKET=${HHS_LANE5_INGRESS_SOCKET:-'
        '$SOURCE_ROOT/deploy/digitalocean/hhs-lane5-ingress.socket}'
    )
    assert binding in installer
    assert installer.index(binding) < installer.index('[[ -f "$LANE5_INGRESS_SOCKET" ]]')
    assert installer.index(binding) < installer.index(
        'install -m 0644 "$LANE5_INGRESS_SOCKET"'
    )


def test_exact_main_uses_transient_candidate_pin_without_freezing_periodic_updates() -> None:
    installer = read("install.sh")
    updater = read("hhs-guarded-update.sh")

    assert 'EXACT_CANDIDATE_SHA=${HHS_EXACT_CANDIDATE_SHA:-}' in updater
    assert 'REMOTE_TIP_SHA=$(git -C "$REPO_ROOT" rev-parse "$REMOTE/$BRANCH")' in updater
    assert 'CANDIDATE_SHA="$EXACT_CANDIDATE_SHA"' in updater
    assert (
        'merge-base --is-ancestor "$EXACT_CANDIDATE_SHA" "$REMOTE_TIP_SHA"'
        in updater
    )
    assert "Pinned exact candidate is not on current" in updater
    assert '[[ "$BUNDLE_SHA" == "$CANDIDATE_SHA" ]]' in updater
    assert "prebuilt Runtime OS bundle is not pinned to selected candidate" in updater

    set_pin = installer.index(
        'systemctl set-environment HHS_EXACT_CANDIDATE_SHA="$BUNDLE_SHA"'
    )
    start = installer.index("systemctl start hhs-guarded-update.service", set_pin)
    clear_after = installer.index("clear_exact_candidate_pin", start)
    timer_enable = installer.index("systemctl enable hhs-guarded-update.timer", clear_after)
    assert set_pin < start < clear_after < timer_enable

    # The candidate pin is deliberately transient. It must never be serialized
    # into the persistent guarded-update environment file used by the timer.
    persistent_env_block = installer[
        installer.index('if [[ ! -f "$ENV_FILE" ]]'):
        installer.index("chown root:root", installer.index('if [[ ! -f "$ENV_FILE" ]]'))
    ]
    assert "HHS_EXACT_CANDIDATE_SHA" not in persistent_env_block


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
    recovery = workflow.index("HHS_EXACT_MAIN_RECOVERY_MODE=1", git_fetch)
    drift = workflow.index("HHS_HOST_DRIFT_MODE=source", recovery)
    handoff = workflow.index("PROMOTION_HANDOFF=1", drift)
    installer_call = workflow.index("HHS_INSTALL_ENABLE_PROMOTION=1", handoff)
    assert claim < workflow_stop < ownership_witness < git_fetch < recovery < drift < handoff < installer_call
    for token in [
        "verify-recovery-state.py",
        "SERVICE_INACTIVE=1",
        'HHS_INSTALL_RECOVERY_MODE="$RECOVERY_MODE"',
        "HHS_PRODUCTION_HEALTH_TIMEOUT_SECONDS=600",
        "EXACT-MAIN PRODUCTION RECOVERY DIAGNOSTICS",
        "flock -w 10 8",
        '$PROMOTION_HANDOFF" == "0"',
        "systemctl start hhs-guarded-update.timer",
        "PRODUCTION_LOCK_FILE=/run/lock/hhs-production-mutation.lock",
        "HHS_PRODUCTION_MUTATION_OWNERSHIP_CLAIMED=1",
        "flock -w 30 7",
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

    # Push-triggered exact-main delivery owns prompt promotion. The periodic
    # timer is only a bounded watchdog and must leave startup/network headroom.
    assert "OnBootSec=15min" in timer
    assert "OnUnitActiveSec=30min" in timer
    assert "RandomizedDelaySec=2min" in timer
    assert "AccuracySec=30s" in timer

    # Candidate validation/build work must never be able to consume the full
    # 2-vCPU/4-GiB production host and starve sshd/nginx.
    for token in [
        "TimeoutStartSec=90min",
        "Type=oneshot",
        "Nice=15",
        "CPUAccounting=true",
        "CPUQuota=100%",
        "CPUWeight=10",
        "MemoryAccounting=true",
        "MemoryHigh=2G",
        "MemoryMax=3G",
        "MemorySwapMax=1G",
        "IOAccounting=true",
        "IOWeight=10",
        "IOSchedulingClass=idle",
        "OOMScoreAdjust=500",
        "TasksMax=512",
        "NoNewPrivileges=true",
    ]:
        assert token in service
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
        "/api/runtime/services",
        "HHS Visual Runtime OS Workspace",
        "legacy_harmonizer_is_public_root",
        "/var/lib/hhs/runtime-os/releases/",
        "HHS_DIGITALOCEAN_LOCAL_SERVICE_REGISTRY_VERIFIED",
        "HHS_DIGITALOCEAN_PUBLIC_RUNTIME_OS_VERIFIED",
        "HHS_DIGITALOCEAN_PUBLIC_SERVICE_REGISTRY_VERIFIED",
        "HHS_PRODUCTION_SERVICE_PERMISSIONS_VERIFIED=1",
        'runuser -u hhs -- test -r "$APP_ROOT/hhs_backend/__init__.py"',
    ]
    for token in required:
        assert token in workflow
    assert workflow.count("/api/runtime/services") >= 2
    assert "HHS_RUNTIME_OS_ROOT=/var/lib/hhs/runtime-os/current" not in workflow
    assert "npm ci --no-audit --no-fund" not in workflow



def test_promotion_normalizes_stale_candidate_validation_timeout() -> None:
    source = read("install.sh")
    assert "minimum_validate_timeout = 3600" in source
    assert 'values["HHS_VALIDATE_TIMEOUT_SECONDS"] = str(' in source
    assert "max(minimum_validate_timeout, current_validate_timeout)" in source
    assert '"HHS_VALIDATE_TIMEOUT_SECONDS",' in source


def test_repair_sources_reject_literal_escaped_newline_artifacts() -> None:
    # Reject the patch-corruption shape that previously wrote a literal "\\n"
    # followed by YAML/shell indentation on one physical source line. Normal
    # shell escapes such as printf '%s\\n' remain valid.
    escaped_newline = chr(92) + "n"
    targets = (
        ROOT / ".github" / "workflows" / "pass220-i045-startup-first-paint-parallel.yml",
        ROOT / ".github" / "workflows" / "pass220-ubuntu-application-vm.yml",
        ROOT / ".github" / "workflows" / "pass220-lane5-host-ingress-membrane.yml",
        ROOT / ".github" / "workflows" / "digitalocean-production-main.yml",
        ROOT / "tests" / "pass220" / "test_pass220_i045_startup_first_paint_parallel.py",
    )
    for path in targets:
        for line in path.read_text(encoding="utf-8").splitlines():
            assert escaped_newline + "          " not in line


def test_application_vm_production_shell_continuations_are_comment_free() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "pass220-ubuntu-application-vm-production.yml"
    ).read_text(encoding="utf-8")

    comment = "# Production deployment must not mutate the host network/desktop stack."
    env_block = (
        'REPO_ROOT="$RELEASE" \\\n'
        '          HHS_APPLICATION_VM_REQUIRE_GUI=1 \\\n'
        '          HHS_APPLICATION_VM_INSTALL_GUI=0 \\\n'
        '            bash "$RELEASE/deployment/ubuntu/application_vm/install.sh"'
    )
    assert comment in workflow
    assert env_block in workflow
    assert workflow.index(comment) < workflow.index(env_block)


def test_application_vm_production_is_manual_and_cannot_reprovision_host_network_stack() -> None:
    application_vm = (
        ROOT / ".github" / "workflows" / "pass220-ubuntu-application-vm-production.yml"
    ).read_text(encoding="utf-8")

    assert "push:" not in application_vm
    assert "workflow_dispatch:" in application_vm
    assert "LOCK_FILE=/run/lock/hhs-production-mutation.lock" in application_vm
    assert "HHS_APPLICATION_VM_INSTALL_GUI=1" not in application_vm
    assert "HHS_APPLICATION_VM_INSTALL_GUI=0" in application_vm
    assert 'chown -R root:hhs "$RELEASE"' in application_vm
    assert 'runuser -u hhs -- test -x "$RELEASE"' in application_vm


def test_all_production_host_mutators_share_one_lock_and_avoid_implicit_host_provisioning() -> None:
    exact_main = (
        ROOT / ".github" / "workflows" / "digitalocean-production-main.yml"
    ).read_text(encoding="utf-8")
    application_vm = (
        ROOT / ".github" / "workflows" / "pass220-ubuntu-application-vm-production.yml"
    ).read_text(encoding="utf-8")
    real_guest = (
        ROOT / ".github" / "workflows" / "pass220-i044-real-ubuntu-guest.yml"
    ).read_text(encoding="utf-8")

    shared_lock = "/run/lock/hhs-production-mutation.lock"
    for workflow in (exact_main, application_vm, real_guest):
        assert shared_lock in workflow
        assert "flock -w 30" in workflow

    assert "workflow_dispatch:" in application_vm
    assert "push:" not in application_vm
    assert "github.event_name == 'workflow_dispatch'" in real_guest
    assert "inputs.run_real_guest == true" in real_guest
    assert "HHS_GUEST_INSTALL_PACKAGES=0" in real_guest
    assert "HHS_APPLICATION_VM_INSTALL_GUI=0" in application_vm


def test_delivery_workflows_pin_active_production_target_and_skip_stale_index_without_failure() -> None:
    production = (
        ROOT / ".github" / "workflows" / "digitalocean-production-main.yml"
    ).read_text(encoding="utf-8")
    application_vm = (
        ROOT / ".github" / "workflows" / "pass220-ubuntu-application-vm-production.yml"
    ).read_text(encoding="utf-8")
    real_guest = (
        ROOT / ".github" / "workflows" / "pass220-i044-real-ubuntu-guest.yml"
    ).read_text(encoding="utf-8")
    mobile_gate = (
        ROOT / ".github" / "workflows" / "digitalocean-mobile-control-ingress.yml"
    ).read_text(encoding="utf-8")
    index_workflow = (
        ROOT / ".github" / "workflows" / "repository-hash216-dependency-index.yml"
    ).read_text(encoding="utf-8")

    active_host = "159.65.178.254"
    retired_host = "165.227.220.193"

    for workflow in (production, application_vm, real_guest):
        assert f"HHS_PRODUCTION_HOST: '{active_host}'" in workflow
        assert "vars.HHS_DIGITALOCEAN_HOST" not in workflow

    assert active_host in mobile_gate
    assert f'! grep -Fq "{retired_host}"' in mobile_gate
    assert retired_host not in production

    stale_guard = (
        'if [ "$remote_head" != "$EXPECTED_HEAD" ]; then',
        "Stale Hash216 projection skipped",
        "exit 0",
    )
    stale_start = index_workflow.index(stale_guard[0])
    stale_end = index_workflow.index("fi", stale_start)
    stale_block = index_workflow[stale_start:stale_end]
    assert stale_guard[1] in stale_block
    assert stale_guard[2] in stale_block
    assert "exit 1" not in stale_block
