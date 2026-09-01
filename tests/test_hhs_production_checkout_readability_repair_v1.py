from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "tools" / "install_production_language_assets.py"
SERVICE = ROOT / "deploy" / "digitalocean" / "hhs-pass196-integrated-environment.service"


def test_root_guarded_update_normalizes_only_tracked_checkout_readability() -> None:
    source = INSTALLER.read_text(encoding="utf-8")
    assert "def _normalize_production_checkout_readability" in source
    assert 'if os.geteuid() != 0:' in source
    assert '["git", "-C", str(root), "ls-files", "-z"]' in source
    assert "stat.S_IRGRP" in source
    assert "stat.S_IXGRP" in source
    assert "os.chown(path, -1, gid)" in source
    assert "os.chown(directory, -1, gid)" in source
    assert "untracked host state and secrets" in source


def test_readability_repair_runs_before_fail_closed_language_authority_gate() -> None:
    source = INSTALLER.read_text(encoding="utf-8")
    normalize_call = source.index("        _normalize_production_checkout_readability()")
    execute_call = source.index("        report = execute(")
    assert normalize_call < execute_call
    assert "--require-assistant" in source
    assert "if require_assistant and not assistant_ready:" in source
    assert "fixture_substitution_allowed\": False" in source


def test_production_service_identity_matches_default_repair_group() -> None:
    source = SERVICE.read_text(encoding="utf-8")
    assert "User=hhs" in source
    assert "Group=hhs" in source
    installer = INSTALLER.read_text(encoding="utf-8")
    assert 'os.getenv("HHS_PRODUCTION_SERVICE_GROUP", "hhs")' in installer
