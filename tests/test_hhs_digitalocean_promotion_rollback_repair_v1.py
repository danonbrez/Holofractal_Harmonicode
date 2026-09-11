from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import pwd
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deployment" / "digitalocean" / "guarded_auto_update"
PERMISSION_TOOL = DEPLOY / "normalize-service-permissions.py"
LANGUAGE_INSTALLER = ROOT / "tools" / "install_production_language_assets.py"


def _load_permission_module():
    spec = importlib.util.spec_from_file_location(
        "hhs_normalize_service_permissions", PERMISSION_TOOL
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_guarded_updater_inherits_word2vec_optional_native_provider_contract() -> None:
    service = (DEPLOY / "hhs-guarded-update.service").read_text(encoding="utf-8")
    example = (DEPLOY / "hhs-guarded-update.env.example").read_text(encoding="utf-8")
    post_compile = (ROOT / "bin" / "post_compile").read_text(encoding="utf-8")

    assert "Environment=HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0" in service
    assert "HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0" in example
    assert 'export HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC="${HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC:-0}"' in post_compile
    assert "NoNewPrivileges=true" in service


def test_production_language_status_is_externalized_from_live_checkout() -> None:
    service = (DEPLOY / "hhs-guarded-update.service").read_text(encoding="utf-8")
    example = (DEPLOY / "hhs-guarded-update.env.example").read_text(encoding="utf-8")
    installer = LANGUAGE_INSTALLER.read_text(encoding="utf-8")
    status_path = "/var/lib/hhs/runtime-bootstrap/production_language_assets_status.json"

    assert f"Environment=HHS_PRODUCTION_LANGUAGE_STATUS_PATH={status_path}" in service
    assert f"HHS_PRODUCTION_LANGUAGE_STATUS_PATH={status_path}" in example
    assert 'os.getenv("HHS_PRODUCTION_LANGUAGE_STATUS_PATH", "").strip()' in installer
    assert '"status_path": str(STATUS_PATH)' in installer


def test_permission_verifier_does_not_spawn_runuser_under_no_new_privileges() -> None:
    source = PERMISSION_TOOL.read_text(encoding="utf-8")
    assert '"runuser"' not in source
    assert "def _identity_group_ids" in source
    assert "mode-bits-with-resolved-supplementary-groups" in source


def test_permission_verifier_uses_target_identity_mode_bits() -> None:
    module = _load_permission_module()
    current_user = pwd.getpwuid(os.geteuid()).pw_name

    with tempfile.TemporaryDirectory(prefix="hhs-permission-mode-") as tmp:
        root = Path(tmp)
        directory = root / "readable"
        directory.mkdir(mode=0o700)
        payload = directory / "payload.txt"
        payload.write_text("hhs\n", encoding="utf-8")
        payload.chmod(0o600)

        assert module._service_access(current_user, directory, "-x") is True
        assert module._service_access(current_user, payload, "-r") is True

        # Remove payload read authority while the parent is still traversable,
        # then independently remove directory traversal authority. Keeping the
        # two checks ordered avoids making the payload itself unreachable before
        # chmod can exercise its own read-bit boundary.
        payload.chmod(0o200)
        assert module._service_access(current_user, payload, "-r") is False

        directory.chmod(0o600)
        assert module._service_access(current_user, directory, "-x") is False
