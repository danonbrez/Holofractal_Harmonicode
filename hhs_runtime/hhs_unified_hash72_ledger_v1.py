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

from hhs_runtime.hhs_hash72_kernel_authority_v1 import hash72_kernel_digest, make_hash72_kernel_witness
from hhs_runtime.hhs_repo_paths_v1 import runtime_artifact_path


GENESIS_HASH72 = "H72-UNIFIED-GENESIS"


def _canonical_payload(value: Any) -> str:
    """Return a stable JSON projection for Hash72 ledger hashing."""

    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def _ledger_digest(label: str, value: Any, *, width: int = 24) -> str:
    # Kernel-backed Hash72: canonical payload is transported through the C u^72
    # Digital DNA ring before a receipt digest is projected.
    return hash72_kernel_digest(label, value, width=width)


def _ledger_witness(label: str, value: Any, *, width: int = 24) -> Dict[str, Any]:
    return make_hash72_kernel_witness(label, value, width=width).to_dict()


def _ledger_summary_payload(entries: List[Dict[str, Any]], tip_hash72: str) -> Dict[str, Any]:
    """Compact ledger projection for whole-ledger Hash72 authority.

    Entry hashes already bind full payloads and parent links. The ledger-level
    digest therefore hashes the ordered entry-hash chain rather than refeeding
    every nested payload repeatedly through the u^72 ring.
    """

    return {
        "entry_count": len(entries),
        "entry_hashes": [entry.get("entry_hash72", "") for entry in entries],
        "tip_hash72": tip_hash72,
    }


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
            "ledger_hash72": _ledger_digest("hhs_unified_hash72_ledger_v1", _ledger_summary_payload([], GENESIS_HASH72)),
        "hash72_authority": "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1",
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
    entry_hash72 = _ledger_digest("hhs_unified_ledger_entry_v1", core)
    return UnifiedLedgerEntry(kind=kind, source=source, payload=payload, parent_hash72=parent_hash72, entry_hash72=entry_hash72)


def append_unified_entry(ledger_path: str | Path, entry: UnifiedLedgerEntry) -> Dict[str, Any]:
    p = Path(ledger_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = _load(p)
    data.setdefault("entries", []).append(entry.to_dict())
    data["entry_count"] = len(data["entries"])
    data["tip_hash72"] = entry.entry_hash72
    data["ledger_hash72"] = _ledger_digest("hhs_unified_hash72_ledger_v1", _ledger_summary_payload(data["entries"], data["tip_hash72"]))
    data["hash72_authority"] = "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1"
    data["tip_hash72_kernel_witness"] = _ledger_witness("hhs_unified_hash72_ledger_v1", _ledger_summary_payload(data["entries"], data["tip_hash72"]))
    p.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return data


def append_payload(kind: str, source: str, payload: Dict[str, Any], *, ledger_path: str | Path | None = None) -> Dict[str, Any]:
    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    data = _load(path)
    # Pass 015 migration: any legacy/default ledger loaded before kernel-backed
    # u^72 authority is rebuilt before accepting new propagation. This prevents
    # mixed static-digest/kernel-ring chains from silently coexisting.
    if data.get("entries") and data.get("hash72_authority") != "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1":
        data = rebuild_unified_ledger(path)
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

    recomputed_ledger_hash72 = _ledger_digest("hhs_unified_hash72_ledger_v1", _ledger_summary_payload(entries, expected_parent))
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
        "hash72_authority": data.get("hash72_authority", "LEGACY_OR_UNDECLARED"),
        "recomputed_ledger_hash72": recomputed_ledger_hash72,
        "ledger_path": str(path),
    }



def rebuild_unified_ledger(ledger_path: str | Path | None = None) -> Dict[str, Any]:
    """Recompute parent, entry, tip, and ledger hashes for existing records.

    This is a repair-only migration helper for ledgers created before canonical
    payload hashing was enforced. It preserves kind/source/payload records while
    rebuilding the Hash72 chain deterministically.
    """

    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    data = _load(path)
    rebuilt_entries: List[Dict[str, Any]] = []
    parent = GENESIS_HASH72

    for raw in data.get("entries", []):
        entry = make_unified_entry(
            raw.get("kind", ""),
            raw.get("source", ""),
            raw.get("payload", {}),
            parent,
        )
        entry_dict = entry.to_dict()
        rebuilt_entries.append(entry_dict)
        parent = entry.entry_hash72

    path.parent.mkdir(parents=True, exist_ok=True)
    repaired = {
        "schema": "HHS_UNIFIED_HASH72_LEDGER_V1",
        "entries": rebuilt_entries,
        "entry_count": len(rebuilt_entries),
        "tip_hash72": parent,
        "ledger_hash72": _ledger_digest(
            "hhs_unified_hash72_ledger_v1",
            _ledger_summary_payload(rebuilt_entries, parent),
        ),
        "hash72_authority": "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1",
        "tip_hash72_kernel_witness": _ledger_witness(
            "hhs_unified_hash72_ledger_v1",
            _ledger_summary_payload(rebuilt_entries, parent),
        ),
    }
    path.write_text(json.dumps(repaired, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return repaired

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
