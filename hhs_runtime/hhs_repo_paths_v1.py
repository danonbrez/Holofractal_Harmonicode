"""
HHS Repo Paths v1
=================

Single path authority for repository-relative runtime artifacts.

Now bound to Hash72 filesystem ledger (non-invasive):
- Path resolution emits a ledger entry
- No change to caller logic or return values
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
import os

from hhs_runtime.hhs_filesystem_hash72_ledger_v1 import (
    append_filesystem_ledger_entry,
    make_filesystem_ledger_entry,
)


REPO_ROOT_ENV = "HHS_REPO_ROOT"
DATA_DIR_ENV = "HHS_DATA_DIR"
RUNTIME_OUTPUT_DIR_ENV = "HHS_RUNTIME_OUTPUT_DIR"
KERNEL_DIR_ENV = "HHS_KERNEL_DIR"
FILESYSTEM_LEDGER_ENV = "HHS_FILESYSTEM_LEDGER_PATH"


def repo_root(start: str | Path | None = None) -> Path:
    env_root = os.environ.get(REPO_ROOT_ENV)
    if env_root:
        return Path(env_root).expanduser().resolve()

    cursor = Path(start).expanduser().resolve() if start is not None else Path(__file__).resolve()
    if cursor.is_file():
        cursor = cursor.parent

    for candidate in [cursor, *cursor.parents]:
        if (candidate / "HHS_SYSTEM_ANCHOR_v1.md").exists() or (candidate / ".git").exists():
            return candidate

    return Path(__file__).resolve().parents[1]


def _filesystem_ledger_path() -> Path:
    env = os.environ.get(FILESYSTEM_LEDGER_ENV)
    if env:
        return Path(env)
    return repo_root() / "data" / "runtime" / "hhs_filesystem_ledger.json"


def _record(path: Path, event: str) -> None:
    try:
        entry = make_filesystem_ledger_entry(
            path,
            repo_root=repo_root(),
            event=event,
        )
        append_filesystem_ledger_entry(_filesystem_ledger_path(), entry)
    except Exception:
        # Ledger must never interfere with execution
        pass


def data_dir(*parts: str, create: bool = False) -> Path:
    base = Path(os.environ.get(DATA_DIR_ENV, repo_root() / "data")).expanduser()
    path = base.joinpath(*parts)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    _record(path, "DATA_DIR_RESOLVED")
    return path


def runtime_output_dir(*parts: str, create: bool = False) -> Path:
    base = Path(os.environ.get(RUNTIME_OUTPUT_DIR_ENV, data_dir("runtime"))).expanduser()
    path = base.joinpath(*parts)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    _record(path, "RUNTIME_OUTPUT_DIR_RESOLVED")
    return path


def kernel_dir(*parts: str, create: bool = False) -> Path:
    base = Path(os.environ.get(KERNEL_DIR_ENV, data_dir("kernels"))).expanduser()
    path = base.joinpath(*parts)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    _record(path, "KERNEL_DIR_RESOLVED")
    return path


def runtime_artifact_path(filename: str, *, create_parent: bool = True) -> Path:
    path = runtime_output_dir(filename)
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    _record(path, "RUNTIME_ARTIFACT_PATH")
    return path


def resolve_repo_path(path: str | Path | None, *fallback_parts: str, create_parent: bool = False) -> Path:
    if path is None:
        resolved = repo_root().joinpath(*fallback_parts)
    else:
        candidate = Path(path).expanduser()
        resolved = candidate if candidate.is_absolute() else repo_root() / candidate
    if create_parent:
        resolved.parent.mkdir(parents=True, exist_ok=True)
    _record(resolved, "RESOLVE_REPO_PATH")
    return resolved


def first_existing(paths: Iterable[str | Path]) -> Path | None:
    for p in paths:
        path = Path(p).expanduser()
        if not path.is_absolute():
            path = repo_root() / path
        if path.exists():
            _record(path, "FIRST_EXISTING_HIT")
            return path
    return None
