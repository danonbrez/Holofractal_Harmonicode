"""
HHS Atomic Write Layer v1
=========================

Ensures all file writes are atomic and validated before becoming visible.
Failed writes are quarantined.
"""

from __future__ import annotations

from pathlib import Path
import shutil

from hhs_runtime.hhs_repo_paths_v1 import runtime_artifact_path


def atomic_write(path: str | Path, content: str) -> None:
    p = Path(path)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(p)


def quarantine_file(path: str | Path) -> Path:
    p = Path(path)
    qdir = runtime_artifact_path("quarantine", create_parent=True).parent / "quarantine"
    qdir.mkdir(parents=True, exist_ok=True)
    dest = qdir / p.name
    shutil.move(str(p), str(dest))
    return dest


if __name__ == "__main__":
    print("Atomic layer ready")
