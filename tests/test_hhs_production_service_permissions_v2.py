from __future__ import annotations

import grp
import importlib.util
import os
from pathlib import Path
import pwd
import stat
import subprocess
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


def test_updater_normalizes_before_every_service_start() -> None:
    source = (ROOT / "deployment" / "digitalocean" / "guarded_auto_update" / "hhs-guarded-update.sh").read_text(encoding="utf-8")
    start = source.index("start_units()")
    normalize = source.index("normalize_service_permissions", start)
    systemctl_start = source.index('systemctl start "$unit"', start)
    assert normalize < systemctl_start
    assert "rollback_live_checkout" in source


def test_installer_requires_healthy_rollback_boundary_before_promotion() -> None:
    source = (ROOT / "deployment" / "digitalocean" / "guarded_auto_update" / "install.sh").read_text(encoding="utf-8")
    receipt_gate = source.index('ROLLBACK_HEALTH_FAILED')
    normalize = source.index("normalize_production_checkout")
    rollback_healthy = source.index("HHS_ROLLBACK_BOUNDARY_HEALTHY=1")
    updater_start = source.index("systemctl start hhs-guarded-update.service")
    assert normalize < rollback_healthy < updater_start
    assert receipt_gate < rollback_healthy
    assert "Existing production service is active but unhealthy; refusing promotion." in source
