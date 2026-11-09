"""Regression tests for narrowly scoped production Python import permission repair."""
import importlib.util
import os
from pathlib import Path
import grp
import pwd
import stat
import tempfile
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1] / "deployment/digitalocean/guarded_auto_update/normalize-service-permissions.py"
spec = importlib.util.spec_from_file_location("hhs_venv_access_normalizer", TOOL)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def _boundary(root):
    site = root / "lib" / "python3.12" / "site-packages"
    site.mkdir(parents=True)
    target = site / "typing_extensions.py"
    target.write_text("Sentinel = object()\n")
    return target


def test_repairs_only_exact_import_boundary():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "venv"
        target = _boundary(root)
        unrelated = target.parent / "other.py"
        unrelated.write_text("secret\n")
        unrelated.chmod(0o600)
        target.chmod(0o600)
        user = pwd.getpwuid(os.geteuid()).pw_name
        group = grp.getgrgid(os.getegid()).gr_name
        # The production target is root-owned and hhs is a group reader.
        # Simulate that service group access independently of test UID ownership.
        with patch.object(module, "_service_access", side_effect=lambda u, p, flag: bool(
            stat.S_IMODE(p.stat().st_mode) & (
                stat.S_IRGRP if flag == "-r" else stat.S_IXGRP))):
            receipt = module.normalize_python_typing_extensions_access(
                root, service_user=user, service_group=group, require_root=False)
        assert receipt["result"] == "PASS"
        assert target.stat().st_mode & stat.S_IRGRP
        assert unrelated.stat().st_mode & stat.S_IRGRP == 0


def test_symlink_refusal_has_zero_writes():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "venv"
        target = _boundary(root)
        target.chmod(0o600)
        before = stat.S_IMODE(target.stat().st_mode)
        target.rename(target.with_suffix(".real"))
        target.symlink_to(target.with_suffix(".real"))
        user = pwd.getpwuid(os.geteuid()).pw_name
        group = grp.getgrgid(os.getegid()).gr_name
        try:
            module.normalize_python_typing_extensions_access(
                root, service_user=user, service_group=group, require_root=False)
        except RuntimeError as exc:
            assert "symlink" in str(exc)
        else:
            raise AssertionError("symlink boundary accepted")
        assert stat.S_IMODE(target.with_suffix(".real").stat().st_mode) == before
