from __future__ import annotations

import grp
import importlib.util
import os
from pathlib import Path
import pwd
import stat
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "deployment" / "digitalocean" / "guarded_auto_update" / "normalize-service-permissions.py"


def _load_tool():
    spec = importlib.util.spec_from_file_location("hhs_permission_normalizer", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_permission_normalizer_repairs_tracked_read_and_parent_traversal_only() -> None:
    module = _load_tool()
    user = pwd.getpwuid(os.geteuid()).pw_name
    group = grp.getgrgid(os.getegid()).gr_name

    with tempfile.TemporaryDirectory(prefix="hhs-permissions-") as tmp:
        parent = Path(tmp)
        repo = parent / "app"
        backend = repo / "hhs_backend"
        backend.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "hhs-test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "HHS Test"], check=True)

        init_file = backend / "__init__.py"
        init_file.write_text("# tracked\n", encoding="utf-8")
        secret = repo / "host-secret.txt"
        secret.write_text("untracked\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "hhs_backend/__init__.py"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True)

        init_file.chmod(0o600)
        backend.chmod(0o700)
        repo.chmod(0o700)
        secret.chmod(0o600)
        secret_before = stat.S_IMODE(secret.stat().st_mode)

        receipt = module.normalize_checkout(
            repo,
            service_user=user,
            service_group=group,
            require_root=False,
        )

        assert receipt["result"] == "PASS"
        assert receipt["backend_init_readable"] is True
        assert receipt["untracked_state_modified"] is False
        assert stat.S_IMODE(init_file.stat().st_mode) & stat.S_IRGRP
        assert stat.S_IMODE(backend.stat().st_mode) & stat.S_IXGRP
        assert stat.S_IMODE(repo.stat().st_mode) & stat.S_IXGRP
        assert stat.S_IMODE(secret.stat().st_mode) == secret_before


def test_installed_normalizer_imports_recovery_from_explicit_repo_root() -> None:
    source = TOOL.read_text(encoding="utf-8")
    assert "repository_root = root.resolve()" in source
    assert "sys.path.insert(0, str(repository_root))" in source
    assert "Path(__file__).resolve().parents[3]" not in source

    with tempfile.TemporaryDirectory(prefix="hhs-installed-normalizer-") as tmp:
        workspace = Path(tmp)
        installed_dir = workspace / "usr" / "local" / "lib" / "hhs-guarded-update"
        installed_dir.mkdir(parents=True)
        installed_tool = installed_dir / "normalize-service-permissions.py"
        installed_tool.write_text(source, encoding="utf-8")

        repo = workspace / "opt" / "hhs" / "app"
        runtime = repo / "hhs_runtime"
        runtime.mkdir(parents=True)
        (runtime / "__init__.py").write_text("", encoding="utf-8")
        (runtime / "hhs_unified_hash72_ledger_recovery_v1.py").write_text(
            "def inspect_transition_metadata_recovery(path):\n"
            "    return {'status': 'VALID_NO_REPAIR_REQUIRED'}\n\n"
            "def repair_transition_metadata(*args, **kwargs):\n"
            "    raise AssertionError('repair must not run for a valid ledger')\n",
            encoding="utf-8",
        )

        runtime_output = workspace / "var" / "lib" / "hhs" / "data" / "runtime"
        runtime_output.mkdir(parents=True)
        ledger = runtime_output / "hhs_unified_hash72_ledger.json"
        ledger.write_text("{}\n", encoding="utf-8")

        spec = importlib.util.spec_from_file_location(
            "installed_hhs_permission_normalizer", installed_tool
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        old_package = sys.modules.pop("hhs_runtime", None)
        old_recovery = sys.modules.pop(
            "hhs_runtime.hhs_unified_hash72_ledger_recovery_v1", None
        )
        original_path = list(sys.path)
        old_repo_root = os.environ.get("HHS_REPO_ROOT")
        old_runtime_output = os.environ.get("HHS_RUNTIME_OUTPUT_DIR")
        try:
            receipt = module.recover_unified_ledger_rollback_boundary(
                repo,
                state_root=workspace / "state",
                runtime_output_dir=runtime_output,
            )
            assert receipt["status"] == "LEDGER_VALID"
            assert receipt["result"] == "PASS"
            assert os.environ["HHS_REPO_ROOT"] == str(repo.resolve())
        finally:
            sys.path[:] = original_path
            sys.modules.pop("hhs_runtime", None)
            sys.modules.pop(
                "hhs_runtime.hhs_unified_hash72_ledger_recovery_v1", None
            )
            if old_package is not None:
                sys.modules["hhs_runtime"] = old_package
            if old_recovery is not None:
                sys.modules[
                    "hhs_runtime.hhs_unified_hash72_ledger_recovery_v1"
                ] = old_recovery
            if old_repo_root is None:
                os.environ.pop("HHS_REPO_ROOT", None)
            else:
                os.environ["HHS_REPO_ROOT"] = old_repo_root
            if old_runtime_output is None:
                os.environ.pop("HHS_RUNTIME_OUTPUT_DIR", None)
            else:
                os.environ["HHS_RUNTIME_OUTPUT_DIR"] = old_runtime_output


def test_updater_normalizes_before_every_service_start() -> None:
    source = (ROOT / "deployment" / "digitalocean" / "guarded_auto_update" / "hhs-guarded-update.sh").read_text(encoding="utf-8")
    start = source.index("start_units()")
    normalize = source.index("normalize_service_permissions", start)
    systemctl_start = source.index('systemctl start "$unit"', start)
    assert normalize < systemctl_start
    assert "rollback_live_checkout" in source


def test_installer_requires_healthy_rollback_boundary_before_promotion() -> None:
    source = (ROOT / "deployment" / "digitalocean" / "guarded_auto_update" / "install.sh").read_text(encoding="utf-8")
    normalize = source.index("normalize_production_checkout")
    recovery_verifier = source.index('--receipt-log "$STATE_ROOT/receipts.jsonl"')
    receipt_verified = source.index("HHS_GUARDED_UPDATE_RECOVERY_RECEIPT_VERIFIED=1")
    rollback_restart = source.index("systemctl start hhs.service", receipt_verified)
    rollback_healthy = source.index("HHS_ROLLBACK_BOUNDARY_HEALTHY=1", rollback_restart)
    updater_start = source.index("systemctl start hhs-guarded-update.service", rollback_healthy)
    assert normalize < recovery_verifier < receipt_verified < rollback_restart < rollback_healthy < updater_start
    assert "Rollback boundary service failed health after permission normalization; refusing a new promotion." in source
    assert "Existing production service is active but unhealthy; refusing promotion." in source
