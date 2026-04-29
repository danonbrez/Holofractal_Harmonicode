"""
HHS Repo Paths v1
=================

Single path authority for repository-relative runtime artifacts.

Rules:
- Never require /mnt/data or any host-specific absolute path.
- Prefer explicit caller paths when provided.
- Otherwise resolve paths relative to the repository root.
- Keep runtime outputs under data/runtime unless an explicit path is supplied.
- Keep optional kernel artifacts under data/kernels unless an explicit path is supplied.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
import os


REPO_ROOT_ENV = "HHS_REPO_ROOT"
DATA_DIR_ENV = "HHS_DATA_DIR"
RUNTIME_OUTPUT_DIR_ENV = "HHS_RUNTIME_OUTPUT_DIR"
KERNEL_DIR_ENV = "HHS_KERNEL_DIR"


def repo_root(start: str | Path | None = None) -> Path:
    """Return the repository root without depending on a fixed host path."""

    env_root = os.environ.get(REPO_ROOT_ENV)
    if env_root:
        return Path(env_root).expanduser().resolve()

    cursor = Path(start).expanduser().resolve() if start is not None else Path(__file__).resolve()
    if cursor.is_file():
        cursor = cursor.parent

    for candidate in [cursor, *cursor.parents]:
        if (candidate / "HHS_SYSTEM_ANCHOR_v1.md").exists() or (candidate / ".git").exists():
            return candidate

    # hhs_runtime/hhs_repo_paths_v1.py -> repo root is parent of hhs_runtime.
    return Path(__file__).resolve().parents[1]


def data_dir(*parts: str, create: bool = False) -> Path:
    base = Path(os.environ.get(DATA_DIR_ENV, repo_root() / "data")).expanduser()
    path = base.joinpath(*parts)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def runtime_output_dir(*parts: str, create: bool = False) -> Path:
    base = Path(os.environ.get(RUNTIME_OUTPUT_DIR_ENV, data_dir("runtime"))).expanduser()
    path = base.joinpath(*parts)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def kernel_dir(*parts: str, create: bool = False) -> Path:
    base = Path(os.environ.get(KERNEL_DIR_ENV, data_dir("kernels"))).expanduser()
    path = base.joinpath(*parts)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def runtime_artifact_path(filename: str, *, create_parent: bool = True) -> Path:
    path = runtime_output_dir(filename)
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def resolve_repo_path(path: str | Path | None, *fallback_parts: str, create_parent: bool = False) -> Path:
    """Resolve explicit path or repo-relative fallback.

    Absolute explicit paths are accepted only when explicitly supplied by caller.
    Relative explicit paths are resolved against repo root.
    """

    if path is None:
        resolved = repo_root().joinpath(*fallback_parts)
    else:
        candidate = Path(path).expanduser()
        resolved = candidate if candidate.is_absolute() else repo_root() / candidate
    if create_parent:
        resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def first_existing(paths: Iterable[str | Path]) -> Path | None:
    for p in paths:
        path = Path(p).expanduser()
        if not path.is_absolute():
            path = repo_root() / path
        if path.exists():
            return path
    return None
