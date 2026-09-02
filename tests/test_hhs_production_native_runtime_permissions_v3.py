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
    spec = importlib.util.spec_from_file_location("hhs_permission_normalizer_native_runtime", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_permission_normalizer_repairs_exact_generated_native_runtime_boundary() -> None:
    module = _load_tool()
    user = pwd.getpwuid(os.geteuid()).pw_name
    group = grp.getgrgid(os.getegid()).gr_name

    with tempfile.TemporaryDirectory(prefix="hhs-native-runtime-permissions-") as tmp:
        parent = Path(tmp)
        repo = parent / "app"
        backend = repo / "hhs_backend"
        runtime = repo / "hhs_runtime"
        builds = runtime / "builds"
        backend.mkdir(parents=True)
        builds.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "hhs-test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "HHS Test"], check=True)

        init_file = backend / "__init__.py"
        tracked_runtime = runtime / "tracked.py"
        init_file.write_text("# tracked backend\n", encoding="utf-8")
        tracked_runtime.write_text("# tracked runtime\n", encoding="utf-8")
        library = builds / "libhhs_runtime.so"
        library.write_bytes(b"native-runtime-fixture")
        unrelated = repo / "host-secret.txt"
        unrelated.write_text("untracked\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(repo), "add", "hhs_backend/__init__.py", "hhs_runtime/tracked.py"],
            check=True,
        )
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True)

        init_file.chmod(0o600)
        backend.chmod(0o700)
        runtime.chmod(0o700)
        builds.chmod(0o700)
        library.chmod(0o600)
        unrelated.chmod(0o600)
        unrelated_before = stat.S_IMODE(unrelated.stat().st_mode)

        receipt = module.normalize_checkout(
            repo,
            service_user=user,
            service_group=group,
            require_root=False,
        )

        assert receipt["schema"] == "HHS_PRODUCTION_CHECKOUT_PERMISSION_RECEIPT_V2"
        assert receipt["result"] == "PASS"
        assert receipt["runtime_library_present"] is True
        assert receipt["runtime_library_readable"] is True
        assert receipt["untracked_runtime_permissions_normalized"] is True
        assert receipt["untracked_runtime_permission_boundary"] == [str(builds), str(library)]
        assert receipt["untracked_state_modified"] is False
        assert stat.S_IMODE(builds.stat().st_mode) & stat.S_IXGRP
        assert stat.S_IMODE(library.stat().st_mode) & stat.S_IRGRP
        assert stat.S_IMODE(unrelated.stat().st_mode) == unrelated_before


def test_permission_normalizer_does_not_require_native_library_before_first_build() -> None:
    module = _load_tool()
    user = pwd.getpwuid(os.geteuid()).pw_name
    group = grp.getgrgid(os.getegid()).gr_name

    with tempfile.TemporaryDirectory(prefix="hhs-native-runtime-absent-") as tmp:
        repo = Path(tmp) / "app"
        backend = repo / "hhs_backend"
        backend.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "hhs-test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "HHS Test"], check=True)
        (backend / "__init__.py").write_text("# tracked\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "hhs_backend/__init__.py"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True)

        receipt = module.normalize_checkout(
            repo,
            service_user=user,
            service_group=group,
            require_root=False,
        )

        assert receipt["result"] == "PASS"
        assert receipt["runtime_library_present"] is False
        assert receipt["runtime_library_readable"] is None
        assert receipt["untracked_runtime_permissions_normalized"] is False
        assert receipt["untracked_runtime_permission_boundary"] == []
