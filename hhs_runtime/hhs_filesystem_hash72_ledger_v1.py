"""
HHS Filesystem Hash72 Ledger v1
===============================

Binds repository-relative filesystem artifacts to Hash72 receipts.

This module does not perform filesystem operations on behalf of callers. It
records path-resolution and artifact-observation facts as deterministic ledger
entries so runtime storage becomes auditable without changing business logic.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List
import json
import time

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


@dataclass(frozen=True)
class FilesystemLedgerEntry:
    event: str
    path: str
    relative_path: str
    exists: bool
    is_file: bool
    is_dir: bool
    size_bytes: int | None
    content_hash72: str | None
    parent_hash72: str
    entry_hash72: str
    recorded_at_ns: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def file_content_hash72(path: str | Path, *, width: int = 24) -> str | None:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    # Read bytes deterministically and convert through a latin-1 carrier so every
    # byte value round-trips into a string without lossy decoding.
    payload = p.read_bytes().decode("latin-1")
    return hash72_digest(("hhs_filesystem_content_v1", str(p), payload), width=width)


def make_filesystem_ledger_entry(
    path: str | Path,
    *,
    repo_root: str | Path,
    event: str = "PATH_RESOLVED",
    parent_hash72: str = "H72-FS-GENESIS",
    hash_existing_content: bool = False,
) -> FilesystemLedgerEntry:
    p = Path(path)
    root = Path(repo_root)
    exists = p.exists()
    is_file = p.is_file() if exists else False
    is_dir = p.is_dir() if exists else False
    size_bytes = p.stat().st_size if is_file else None
    content_hash72 = file_content_hash72(p) if hash_existing_content and is_file else None
    recorded_at_ns = time.time_ns()
    rel = _relative(p, root)
    core = {
        "event": event,
        "path": str(p),
        "relative_path": rel,
        "exists": exists,
        "is_file": is_file,
        "is_dir": is_dir,
        "size_bytes": size_bytes,
        "content_hash72": content_hash72,
        "parent_hash72": parent_hash72,
    }
    entry_hash72 = hash72_digest(("hhs_filesystem_ledger_entry_v1", core), width=24)
    return FilesystemLedgerEntry(
        event=event,
        path=str(p),
        relative_path=rel,
        exists=exists,
        is_file=is_file,
        is_dir=is_dir,
        size_bytes=size_bytes,
        content_hash72=content_hash72,
        parent_hash72=parent_hash72,
        entry_hash72=entry_hash72,
        recorded_at_ns=recorded_at_ns,
    )


def append_filesystem_ledger_entry(ledger_path: str | Path, entry: FilesystemLedgerEntry) -> Dict[str, Any]:
    ledger = Path(ledger_path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    if ledger.exists():
        data = json.loads(ledger.read_text(encoding="utf-8"))
    else:
        data = {"schema": "HHS_FILESYSTEM_HASH72_LEDGER_V1", "entries": []}
    data.setdefault("entries", []).append(entry.to_dict())
    data["tip_hash72"] = entry.entry_hash72
    data["entry_count"] = len(data["entries"])
    data["ledger_hash72"] = hash72_digest(("hhs_filesystem_ledger_v1", data["entries"], data["tip_hash72"]), width=24)
    ledger.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return data


def read_filesystem_ledger(ledger_path: str | Path) -> Dict[str, Any]:
    ledger = Path(ledger_path)
    if not ledger.exists():
        return {"schema": "HHS_FILESYSTEM_HASH72_LEDGER_V1", "entries": [], "entry_count": 0, "tip_hash72": "H72-FS-GENESIS"}
    return json.loads(ledger.read_text(encoding="utf-8"))


def verify_filesystem_ledger(ledger_path: str | Path) -> Dict[str, Any]:
    data = read_filesystem_ledger(ledger_path)
    entries: List[Dict[str, Any]] = data.get("entries", [])
    expected_parent = "H72-FS-GENESIS"
    invalid: List[Dict[str, Any]] = []
    for idx, entry in enumerate(entries):
        if entry.get("parent_hash72") != expected_parent:
            invalid.append({"index": idx, "reason": "parent_hash72 mismatch", "expected": expected_parent, "actual": entry.get("parent_hash72")})
        expected_parent = entry.get("entry_hash72", "")
    recomputed = hash72_digest(("hhs_filesystem_ledger_v1", entries, expected_parent), width=24)
    ledger_hash_ok = data.get("ledger_hash72") in {None, recomputed} if not entries else data.get("ledger_hash72") == recomputed
    return {
        "ok": not invalid and ledger_hash_ok,
        "invalid": invalid,
        "entry_count": len(entries),
        "tip_hash72": expected_parent,
        "ledger_hash72": data.get("ledger_hash72"),
        "recomputed_ledger_hash72": recomputed,
    }
