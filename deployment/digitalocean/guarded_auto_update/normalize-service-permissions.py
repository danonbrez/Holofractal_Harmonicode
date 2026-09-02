#!/usr/bin/env python3
"""Normalize HHS production checkout read/traverse permissions for hhs.service.

This is intentionally independent of native compilation and language-model
installation so it can repair both promotion and rollback service boundaries.
Only Git-tracked source plus the minimum /opt/hhs parent chain is modified.
Untracked host state, .git internals, runtime state, and secrets are untouched.
"""
from __future__ import annotations

import argparse
import grp
import json
import os
from pathlib import Path
import pwd
import stat
import subprocess
from typing import Any


def _tracked_paths(root: Path) -> tuple[Path, ...]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return tuple(
        root / Path(raw.decode("utf-8", errors="strict"))
        for raw in result.stdout.split(b"\0")
        if raw
    )


def _set_group_mode(path: Path, gid: int, *, directory: bool, allow_chown: bool) -> None:
    if not path.exists() or path.is_symlink():
        return
    current = path.stat()
    if allow_chown:
        os.chown(path, -1, gid)
    required = stat.S_IRGRP | (stat.S_IXGRP if directory else 0)
    desired = stat.S_IMODE(current.st_mode) | required
    if desired != stat.S_IMODE(current.st_mode):
        os.chmod(path, desired)


def _service_access(user: str, path: Path, flag: str) -> bool:
    if pwd.getpwuid(os.geteuid()).pw_name == user:
        return os.access(path, os.X_OK if flag == "-x" else os.R_OK)
    completed = subprocess.run(
        ["runuser", "-u", user, "--", "test", flag, str(path)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def normalize_checkout(
    root: Path,
    *,
    service_user: str,
    service_group: str,
    require_root: bool = True,
) -> dict[str, Any]:
    root = root.resolve()
    if require_root and os.geteuid() != 0:
        raise PermissionError("production permission normalization requires root")
    if not (root / ".git").exists():
        raise FileNotFoundError(f"repository missing at {root}")

    user = pwd.getpwnam(service_user)
    group = grp.getgrnam(service_group)
    gid = group.gr_gid
    allow_chown = os.geteuid() == 0

    tracked = _tracked_paths(root)
    tracked_files = 0
    tracked_dirs: set[Path] = {root, root.parent}

    for path in tracked:
        if not path.exists() or path.is_symlink():
            continue
        if path.is_dir():
            tracked_dirs.add(path)
            continue
        _set_group_mode(path, gid, directory=False, allow_chown=allow_chown)
        tracked_files += 1
        parent = path.parent
        while parent == root or root in parent.parents:
            tracked_dirs.add(parent)
            if parent == root:
                break
            parent = parent.parent

    # /opt/hhs and /opt/hhs/app are normalized to the service group.
    # /opt itself remains host/root-owned and is verified, not chowned.
    for directory in sorted(tracked_dirs, key=lambda value: len(value.parts)):
        _set_group_mode(directory, gid, directory=True, allow_chown=allow_chown)

    backend = root / "hhs_backend"
    init_file = backend / "__init__.py"
    required_dirs = (root.parent.parent, root.parent, root, backend)
    for directory in required_dirs:
        if not directory.is_dir():
            raise FileNotFoundError(f"required production directory missing: {directory}")
        if not _service_access(service_user, directory, "-x"):
            raise PermissionError(
                f"service user {service_user} cannot traverse {directory}"
            )
    if not init_file.is_file():
        raise FileNotFoundError(f"required backend package marker missing: {init_file}")
    if not _service_access(service_user, init_file, "-r"):
        raise PermissionError(
            f"service user {service_user} cannot read {init_file}"
        )

    return {
        "schema": "HHS_PRODUCTION_CHECKOUT_PERMISSION_RECEIPT_V2",
        "repository_root": str(root),
        "service_user": user.pw_name,
        "service_group": group.gr_name,
        "tracked_files_normalized": tracked_files,
        "tracked_directories_normalized": len(tracked_dirs),
        "backend_init_readable": True,
        "parent_traversal_verified": [str(path) for path in required_dirs],
        "untracked_state_modified": False,
        "result": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default="/opt/hhs/app")
    parser.add_argument("--service-user", default="hhs")
    parser.add_argument("--service-group", default="hhs")
    args = parser.parse_args()
    receipt = normalize_checkout(
        Path(args.repo_root),
        service_user=args.service_user,
        service_group=args.service_group,
        require_root=True,
    )
    print(json.dumps(receipt, sort_keys=True))
    print("HHS_PRODUCTION_CHECKOUT_PERMISSIONS_VERIFIED=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
