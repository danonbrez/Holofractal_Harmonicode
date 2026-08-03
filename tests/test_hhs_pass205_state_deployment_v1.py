from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "deployment" / "digitalocean" / "pass205_state" / "install.sh"
POST_COMPILE = ROOT / "bin" / "post_compile"


def test_pass205_state_installer_uses_system_state_boundary() -> None:
    source = INSTALLER.read_text(encoding="utf-8")
    assert "STATE_ROOT=${HHS_PASS205_STATE_ROOT:-/var/lib/hhs/pass205}" in source
    assert "DATABASE_PATH=${HHS_PASS205_DB:-$STATE_ROOT/continuation.sqlite3}" in source
    assert "Environment=HHS_PASS205_DB=$DATABASE_PATH" in source
    assert "ReadWritePaths=$STATE_ROOT" in source
    assert "systemctl show \"$SERVICE_NAME\" --property=User --value" in source
    assert "install -d -m 0750 -o \"$service_user\" -g \"$service_group\" \"$STATE_ROOT\"" in source
    assert "systemctl daemon-reload" in source


def test_post_compile_installs_state_boundary_only_as_root() -> None:
    source = POST_COMPILE.read_text(encoding="utf-8")
    assert "[[ $EUID -eq 0 && -x deployment/digitalocean/pass205_state/install.sh ]]" in source
    assert "bash deployment/digitalocean/pass205_state/install.sh" in source
    assert "Skipping system Pass 205 state installation outside a root deployment context." in source
