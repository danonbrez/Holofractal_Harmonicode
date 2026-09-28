"""HHS Filesystem Hash72 Ledger v1.

Binds repository-relative filesystem observations into one append-only Hash72
parent chain.  Legacy ledgers written before chain authority was enforced are
deterministically rebound on their first subsequent append; observation payload,
ordering, paths, events, sizes, content commitments, and recorded timestamps are
preserved.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping
import json
import time

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


GENESIS_HASH72 = "H72-FS-GENESIS"
LEDGER_SCHEMA = "HHS_FILESYSTEM_HASH72_LEDGER_V1"
CHAIN_AUTHORITY = "HHS_FILESYSTEM_HASH72_APPEND_CHAIN_AUTHORITY_V1"


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
    payload = p.read_bytes().decode("latin-1")
    return hash72_digest(("hhs_filesystem_content_v1", str(p), payload), width=width)


def _entry_core(entry: Mapping[str, Any], *, parent_hash72: str | None = None) -> Dict[str, Any]:
    return {
        "event": entry.get("event"),
        "path": entry.get("path"),
        "relative_path": entry.get("relative_path"),
        "exists": bool(entry.get("exists")),
        "is_file": bool(entry.get("is_file")),
        "is_dir": bool(entry.get("is_dir")),
        "size_bytes": entry.get("size_bytes"),
        "content_hash72": entry.get("content_hash72"),
        "parent_hash72": entry.get("parent_hash72") if parent_hash72 is None else parent_hash72,
    }


def _entry_hash72(entry: Mapping[str, Any], *, parent_hash72: str | None = None) -> str:
    return hash72_digest(
        ("hhs_filesystem_ledger_entry_v1", _entry_core(entry, parent_hash72=parent_hash72)),
        width=24,
    )


def _rebind_entry(entry: Mapping[str, Any], parent_hash72: str) -> Dict[str, Any]:
    rebound = dict(entry)
    rebound["parent_hash72"] = parent_hash72
    rebound["entry_hash72"] = _entry_hash72(rebound, parent_hash72=parent_hash72)
    return rebound


def _ledger_hash72(entries: List[Dict[str, Any]], tip_hash72: str) -> str:
    # The aggregate commitment must survive JSON persistence. Hash a canonical
    # serialization rather than Python dict insertion order, because the ledger
    # is written with sort_keys=True and reloaded before distributed verification.
    canonical_entries = json.dumps(
        entries,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hash72_digest(
        ("hhs_filesystem_ledger_v1", canonical_entries, tip_hash72),
        width=24,
    )


def _migrate_legacy_flat_chain(data: Dict[str, Any]) -> Dict[str, Any]:
    if data.get("chain_authority") == CHAIN_AUTHORITY:
        return data

    original_entries = list(data.get("entries", []))
    prior_ledger_hash72 = data.get("ledger_hash72")
    parent = GENESIS_HASH72
    rebound: List[Dict[str, Any]] = []
    changed = 0
    for entry in original_entries:
        canonical = _rebind_entry(entry, parent)
        if (
            entry.get("parent_hash72") != canonical["parent_hash72"]
            or entry.get("entry_hash72") != canonical["entry_hash72"]
        ):
            changed += 1
        rebound.append(canonical)
        parent = canonical["entry_hash72"]

    data["schema"] = data.get("schema") or LEDGER_SCHEMA
    data["entries"] = rebound
    data["entry_count"] = len(rebound)
    data["tip_hash72"] = parent
    data["ledger_hash72"] = _ledger_hash72(rebound, parent)
    data["chain_authority"] = CHAIN_AUTHORITY
    migration_core = {
        "mode": "DETERMINISTIC_REBIND_LEGACY_FLAT_GENESIS_CHAIN",
        "rebound_entry_count": changed,
        "preserved_entry_count": len(rebound),
        "prior_ledger_hash72": prior_ledger_hash72,
        "tip_hash72": parent,
    }
    data["legacy_chain_repair"] = {
        **migration_core,
        "migration_receipt_hash72": hash72_digest(
            ("hhs_filesystem_ledger_legacy_chain_repair_v1", migration_core),
            width=24,
        ),
    }
    return data


def make_filesystem_ledger_entry(
    path: str | Path,
    *,
    repo_root: str | Path,
    event: str = "PATH_RESOLVED",
    parent_hash72: str = GENESIS_HASH72,
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


def append_filesystem_ledger_entry(
    ledger_path: str | Path,
    entry: FilesystemLedgerEntry,
) -> Dict[str, Any]:
    ledger = Path(ledger_path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    if ledger.exists():
        data = json.loads(ledger.read_text(encoding="utf-8"))
    else:
        data = {
            "schema": LEDGER_SCHEMA,
            "entries": [],
            "entry_count": 0,
            "tip_hash72": GENESIS_HASH72,
        }

    data = _migrate_legacy_flat_chain(data)
    parent = data.get("tip_hash72") or GENESIS_HASH72
    canonical_entry = _rebind_entry(entry.to_dict(), parent)
    entries = data.setdefault("entries", [])
    entries.append(canonical_entry)
    data["entry_count"] = len(entries)
    data["tip_hash72"] = canonical_entry["entry_hash72"]
    data["ledger_hash72"] = _ledger_hash72(entries, data["tip_hash72"])
    data["chain_authority"] = CHAIN_AUTHORITY
    ledger.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    return data


def read_filesystem_ledger(ledger_path: str | Path) -> Dict[str, Any]:
    ledger = Path(ledger_path)
    if not ledger.exists():
        return {
            "schema": LEDGER_SCHEMA,
            "entries": [],
            "entry_count": 0,
            "tip_hash72": GENESIS_HASH72,
            "chain_authority": CHAIN_AUTHORITY,
        }
    return json.loads(ledger.read_text(encoding="utf-8"))


def verify_filesystem_ledger(ledger_path: str | Path) -> Dict[str, Any]:
    data = read_filesystem_ledger(ledger_path)
    entries: List[Dict[str, Any]] = data.get("entries", [])
    expected_parent = GENESIS_HASH72
    invalid: List[Dict[str, Any]] = []

    if data.get("schema") != LEDGER_SCHEMA:
        invalid.append({
            "index": None,
            "reason": "schema mismatch",
            "expected": LEDGER_SCHEMA,
            "actual": data.get("schema"),
        })

    for idx, entry in enumerate(entries):
        actual_parent = entry.get("parent_hash72")
        if actual_parent != expected_parent:
            invalid.append({
                "index": idx,
                "reason": "parent_hash72 mismatch",
                "expected": expected_parent,
                "actual": actual_parent,
            })

        recomputed_entry_hash72 = _entry_hash72(entry, parent_hash72=actual_parent)
        stored_entry_hash72 = entry.get("entry_hash72")
        if stored_entry_hash72 != recomputed_entry_hash72:
            invalid.append({
                "index": idx,
                "reason": "entry_hash72 mismatch",
                "expected": recomputed_entry_hash72,
                "actual": stored_entry_hash72,
            })
        expected_parent = recomputed_entry_hash72

    recomputed = _ledger_hash72(entries, expected_parent)
    stored_ledger_hash72 = data.get("ledger_hash72")
    ledger_hash_ok = (
        stored_ledger_hash72 in {None, recomputed}
        if not entries
        else stored_ledger_hash72 == recomputed
    )
    if not ledger_hash_ok:
        invalid.append({
            "index": None,
            "reason": "ledger_hash72 mismatch",
            "expected": recomputed,
            "actual": stored_ledger_hash72,
        })

    stored_tip = data.get("tip_hash72", GENESIS_HASH72)
    if stored_tip != expected_parent:
        invalid.append({
            "index": None,
            "reason": "tip_hash72 mismatch",
            "expected": expected_parent,
            "actual": stored_tip,
        })

    return {
        "ok": not invalid,
        "invalid": invalid,
        "entry_count": len(entries),
        "tip_hash72": expected_parent,
        "ledger_hash72": stored_ledger_hash72,
        "recomputed_ledger_hash72": recomputed,
        "chain_authority": data.get("chain_authority"),
        "legacy_chain_repair": data.get("legacy_chain_repair"),
    }
