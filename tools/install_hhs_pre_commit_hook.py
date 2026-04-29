"""
Install HHS pre-commit hook
===========================

Installs a local Git pre-commit hook that runs the HHS commit acceptance gate
before allowing a commit.

Usage:
    python tools/install_hhs_pre_commit_hook.py

The hook is local to the checkout and is not automatically active until this
installer is run once in the repository.
"""

from __future__ import annotations

from pathlib import Path
import os
import stat


def find_repo_root() -> Path:
    cursor = Path(__file__).resolve()
    for candidate in [cursor.parent, *cursor.parents]:
        if (candidate / ".git").exists() and (candidate / "HHS_SYSTEM_ANCHOR_v1.md").exists():
            return candidate
    raise RuntimeError("Could not locate repository root")


def install() -> Path:
    root = find_repo_root()
    hooks_dir = root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_dir / "pre-commit"
    hook_body = """#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "[HHS] Running commit acceptance gate..."
python hhs_runtime/hhs_commit_acceptance_gate_v1.py
"""
    hook_path.write_text(hook_body, encoding="utf-8")
    mode = hook_path.stat().st_mode
    hook_path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return hook_path


if __name__ == "__main__":
    path = install()
    print(f"Installed HHS pre-commit hook: {path}")
