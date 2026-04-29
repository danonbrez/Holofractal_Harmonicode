"""
HHS Unified Hash72 Ledger v1
===========================

Unifies independently produced runtime, filesystem, feedback, execution, and
validation receipts into one append-only Hash72 chain.

This module does not replace existing ledgers. It observes their receipts and
binds them together as a higher-level acceptance ledger.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_repo_paths_v1 import runtime_artifact_path


GENESIS_HASH72 = "H72-UNIFIED-GENESIS"


@dataclass(frozen=True)
class UnifiedLedgerEntry:
    kind: str
    source: str
    payload: Dict[str, Any]
    parent_hash72: str
    entry_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {
            "schema": "HHS_UNIFIED_HASH72_LEDGER_V1",
            "entries": [],
            "entry_count": 0,
            "tip_hash72": GENESIS_HASH72,
            "ledger_hash72": hash72_digest(("hhs_unified_hash72_ledger_v1", [], GENESIS_HASH72), width=24),
        }
    return json.loads(p.read_text(encoding="utf-8"))


def default_unified_ledger_path() -> Path:
    return runtime_artifact_path("hhs_unified_hash72_ledger.json")


def make_unified_entry(kind: str, source: str, payload: Dict[str, Any], parent_hash72: str) -> UnifiedLedgerEntry:
    core = {
        "kind": kind,
        "source": source,
        "payload": payload,
        "parent_hash72": parent_hash72,
    }
    entry_hash72 = hash72_digest(("hhs_unified_ledger_entry_v1", core), width=24)
    return UnifiedLedgerEntry(kind=kind, source=source, payload=payload, parent_hash72=parent_hash72, entry_hash72=entry_hash72)


def append_unified_entry(ledger_path: str | Path, entry: UnifiedLedgerEntry) -> Dict[str, Any]:
    p = Path(ledger_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = _load(p)
    data.setdefault("entries", []).append(entry.to_dict())
    data["entry_count"] = len(data["entries"])
    data["tip_hash72"] = entry.entry_hash72
    data["ledger_hash72"] = hash72_digest(("hhs_unified_hash72_ledger_v1", data["entries"], data["tip_hash72"]), width=24)
    p.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return data


def append_payload(kind: str, source: str, payload: Dict[str, Any], *, ledger_path: str | Path | None = None) -> Dict[str, Any]:
    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    data = _load(path)
    parent = data.get("tip_hash72", GENESIS_HASH72)
    entry = make_unified_entry(kind, source, payload, parent)
    return append_unified_entry(path, entry)


def verify_unified_ledger(ledger_path: str | Path | None = None) -> Dict[str, Any]:
    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    data = _load(path)
    entries: List[Dict[str, Any]] = data.get("entries", [])
    expected_parent = GENESIS_HASH72
    invalid: List[Dict[str, Any]] = []

    for idx, entry in enumerate(entries):
        if entry.get("parent_hash72") != expected_parent:
            invalid.append({
                "index": idx,
                "reason": "parent_hash72 mismatch",
                "expected": expected_parent,
                "actual": entry.get("parent_hash72"),
            })
        recomputed = make_unified_entry(
            entry.get("kind", ""),
            entry.get("source", ""),
            entry.get("payload", {}),
            entry.get("parent_hash72", ""),
        ).entry_hash72
        if entry.get("entry_hash72") != recomputed:
            invalid.append({
                "index": idx,
                "reason": "entry_hash72 mismatch",
                "expected": recomputed,
                "actual": entry.get("entry_hash72"),
            })
        expected_parent = entry.get("entry_hash72", "")

    recomputed_ledger_hash72 = hash72_digest(("hhs_unified_hash72_ledger_v1", entries, expected_parent), width=24)
    ledger_hash_ok = data.get("ledger_hash72") == recomputed_ledger_hash72
    if not ledger_hash_ok:
        invalid.append({
            "index": "ledger",
            "reason": "ledger_hash72 mismatch",
            "expected": recomputed_ledger_hash72,
            "actual": data.get("ledger_hash72"),
        })

    return {
        "ok": len(invalid) == 0,
        "invalid": invalid,
        "entry_count": len(entries),
        "tip_hash72": expected_parent,
        "ledger_hash72": data.get("ledger_hash72"),
        "recomputed_ledger_hash72": recomputed_ledger_hash72,
        "ledger_path": str(path),
    }


def absorb_json_artifacts(paths: Iterable[str | Path], *, ledger_path: str | Path | None = None) -> Dict[str, Any]:
    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    absorbed: List[Dict[str, Any]] = []
    for raw in paths:
        p = Path(raw)
        if not p.exists() or not p.is_file():
            absorbed.append({"path": str(p), "status": "MISSING"})
            continue
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            absorbed.append({"path": str(p), "status": "UNREADABLE", "error": f"{type(exc).__name__}: {exc}"})
            continue
        data = append_payload("JSON_ARTIFACT", str(p), payload, ledger_path=path)
        absorbed.append({"path": str(p), "status": "ABSORBED", "tip_hash72": data.get("tip_hash72")})
    verification = verify_unified_ledger(path)
    return {"absorbed": absorbed, "verification": verification}
