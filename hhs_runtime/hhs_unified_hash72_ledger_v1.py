"""
HHS Unified Hash72 Ledger v1
===========================

Unifies independently produced runtime, filesystem, feedback, execution, and
validation receipts into one append-only Hash72 chain.

The authoritative entry chain is preserved exactly. Runtime appends use a
constant-size Hash72 accumulator transition and an append-only JSONL journal,
so request latency does not grow with the number or size of prior entries.
Full-chain verification remains available as an explicit audit operation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Iterable, List, Tuple
import json
import os

from hhs_runtime.hhs_hash72_kernel_authority_v1 import (
    hash72_kernel_digest,
    make_hash72_kernel_witness,
)
from hhs_runtime.hhs_repo_paths_v1 import runtime_artifact_path


GENESIS_HASH72 = "H72-UNIFIED-GENESIS"
LEDGER_SCHEMA = "HHS_UNIFIED_HASH72_LEDGER_V1"
HASH72_AUTHORITY = "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1"
ACCUMULATOR_VERSION = "HHS_UNIFIED_HASH72_INCREMENTAL_TIP_V1"
JOURNAL_SCHEMA = "HHS_UNIFIED_HASH72_LEDGER_JOURNAL_ENTRY_V1"
STORAGE_MODE = "COMPACTED_SNAPSHOT_PLUS_APPEND_JOURNAL"

_CACHE_GUARD = RLock()
_LEDGER_LOCKS: Dict[str, RLock] = {}
_LEDGER_CACHE: Dict[str, Dict[str, Any]] = {}
_LEDGER_CACHE_ERRORS: Dict[str, List[Dict[str, Any]]] = {}
_LEDGER_CACHE_SIGNATURES: Dict[str, Tuple[Tuple[bool, int, int], Tuple[bool, int, int]]] = {}


def _canonical_payload(value: Any) -> str:
    """Return a stable JSON projection for Hash72 ledger hashing."""

    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def _ledger_digest(label: str, value: Any, *, width: int = 24) -> str:
    return hash72_kernel_digest(label, value, width=width)


def _ledger_witness(label: str, value: Any, *, width: int = 24) -> Dict[str, Any]:
    return make_hash72_kernel_witness(label, value, width=width).to_dict()


def _ledger_summary_payload(entries: List[Dict[str, Any]], tip_hash72: str) -> Dict[str, Any]:
    """Legacy whole-ledger summary retained for backward verification."""

    return {
        "entry_count": len(entries),
        "entry_hashes": [entry.get("entry_hash72", "") for entry in entries],
        "tip_hash72": tip_hash72,
    }


def _empty_legacy_ledger_hash72() -> str:
    return _ledger_digest(
        "hhs_unified_hash72_ledger_v1",
        _ledger_summary_payload([], GENESIS_HASH72),
    )


def _ledger_transition_payload(
    prior_ledger_hash72: str,
    entry_count: int,
    entry_hash72: str,
) -> Dict[str, Any]:
    return {
        "accumulator_version": ACCUMULATOR_VERSION,
        "prior_ledger_hash72": prior_ledger_hash72,
        "entry_count": int(entry_count),
        "entry_hash72": entry_hash72,
        "tip_hash72": entry_hash72,
    }


def _ledger_transition(
    prior_ledger_hash72: str,
    entry_count: int,
    entry_hash72: str,
) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    payload = _ledger_transition_payload(prior_ledger_hash72, entry_count, entry_hash72)
    witness = _ledger_witness("hhs_unified_hash72_ledger_incremental_v1", payload)
    return str(witness["digest"]), witness, payload


def _path_key(path: str | Path) -> str:
    return str(Path(path).expanduser().resolve())


def _journal_path(path: str | Path) -> Path:
    p = Path(path)
    return p.with_name(f"{p.name}.journal.jsonl")


def _file_signature(path: Path) -> Tuple[bool, int, int]:
    try:
        stat = path.stat()
    except FileNotFoundError:
        return (False, 0, 0)
    return (True, int(stat.st_mtime_ns), int(stat.st_size))


def _signatures(path: Path) -> Tuple[Tuple[bool, int, int], Tuple[bool, int, int]]:
    return (_file_signature(path), _file_signature(_journal_path(path)))


def _lock_for(path: str | Path) -> RLock:
    key = _path_key(path)
    with _CACHE_GUARD:
        return _LEDGER_LOCKS.setdefault(key, RLock())


def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _append_journal_record(path: Path, payload: Dict[str, Any]) -> None:
    journal = _journal_path(path)
    journal.parent.mkdir(parents=True, exist_ok=True)
    encoded = _canonical_payload(payload) + "\n"
    with journal.open("a", encoding="utf-8") as handle:
        handle.write(encoded)
        handle.flush()
        if os.environ.get("HHS_LEDGER_FSYNC", "1").strip().lower() not in {"0", "false", "no"}:
            os.fsync(handle.fileno())


def _empty_snapshot() -> Dict[str, Any]:
    empty_hash = _empty_legacy_ledger_hash72()
    empty_payload = {
        "accumulator_version": ACCUMULATOR_VERSION,
        "prior_ledger_hash72": empty_hash,
        "entry_count": 0,
        "entry_hash72": GENESIS_HASH72,
        "tip_hash72": GENESIS_HASH72,
    }
    return {
        "schema": LEDGER_SCHEMA,
        "entries": [],
        "entry_count": 0,
        "tip_hash72": GENESIS_HASH72,
        "ledger_hash72": empty_hash,
        "hash72_authority": HASH72_AUTHORITY,
        "ledger_accumulator_version": ACCUMULATOR_VERSION,
        "ledger_storage_mode": STORAGE_MODE,
        "tip_hash72_kernel_witness": _ledger_witness(
            "hhs_unified_hash72_ledger_incremental_v1",
            empty_payload,
        ),
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


def default_unified_ledger_path() -> Path:
    return runtime_artifact_path("hhs_unified_hash72_ledger.json")


def make_unified_entry(
    kind: str,
    source: str,
    payload: Dict[str, Any],
    parent_hash72: str,
) -> UnifiedLedgerEntry:
    core = {
        "kind": kind,
        "source": source,
        "payload": payload,
        "parent_hash72": parent_hash72,
    }
    entry_hash72 = _ledger_digest("hhs_unified_ledger_entry_v1", core)
    return UnifiedLedgerEntry(
        kind=kind,
        source=source,
        payload=payload,
        parent_hash72=parent_hash72,
        entry_hash72=entry_hash72,
    )


def _read_snapshot(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return _empty_snapshot()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"unified ledger snapshot must be a JSON object: {path}")
    payload.setdefault("schema", LEDGER_SCHEMA)
    payload.setdefault("entries", [])
    return payload


def _read_journal(path: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    journal = _journal_path(path)
    if not journal.exists():
        return [], []

    records: List[Dict[str, Any]] = []
    invalid: List[Dict[str, Any]] = []
    with journal.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                record = json.loads(raw)
            except json.JSONDecodeError as exc:
                invalid.append({
                    "index": f"journal:{line_number}",
                    "reason": "invalid JSON journal record",
                    "error": str(exc),
                })
                continue
            if not isinstance(record, dict):
                invalid.append({
                    "index": f"journal:{line_number}",
                    "reason": "journal record must be a JSON object",
                })
                continue
            records.append(record)
    return records, invalid


def _validate_entry(
    entry: Dict[str, Any],
    *,
    expected_parent: str,
    index: Any,
) -> Tuple[str, List[Dict[str, Any]]]:
    invalid: List[Dict[str, Any]] = []
    actual_parent = str(entry.get("parent_hash72", ""))
    if actual_parent != expected_parent:
        invalid.append({
            "index": index,
            "reason": "parent_hash72 mismatch",
            "expected": expected_parent,
            "actual": actual_parent,
        })

    recomputed = make_unified_entry(
        str(entry.get("kind", "")),
        str(entry.get("source", "")),
        dict(entry.get("payload", {}) or {}),
        actual_parent,
    ).entry_hash72
    actual_hash = str(entry.get("entry_hash72", ""))
    if actual_hash != recomputed:
        invalid.append({
            "index": index,
            "reason": "entry_hash72 mismatch",
            "expected": recomputed,
            "actual": actual_hash,
        })
    return actual_hash, invalid


def _materialize(path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    snapshot = _read_snapshot(path)
    snapshot_entries = [dict(entry) for entry in snapshot.get("entries", [])]
    journal_records, invalid = _read_journal(path)

    if int(snapshot.get("entry_count") or 0) != len(snapshot_entries):
        invalid.append({
            "index": "snapshot",
            "reason": "snapshot entry_count mismatch",
            "expected": len(snapshot_entries),
            "actual": snapshot.get("entry_count"),
        })
    expected_snapshot_tip = (
        str(snapshot_entries[-1].get("entry_hash72", ""))
        if snapshot_entries
        else GENESIS_HASH72
    )
    if str(snapshot.get("tip_hash72") or GENESIS_HASH72) != expected_snapshot_tip:
        invalid.append({
            "index": "snapshot",
            "reason": "snapshot tip_hash72 mismatch",
            "expected": expected_snapshot_tip,
            "actual": snapshot.get("tip_hash72"),
        })

    expected_parent = GENESIS_HASH72
    logical_ledger_hash72 = _empty_legacy_ledger_hash72()
    last_witness = snapshot.get("tip_hash72_kernel_witness")

    for index, entry in enumerate(snapshot_entries):
        actual_hash, entry_invalid = _validate_entry(
            entry,
            expected_parent=expected_parent,
            index=index,
        )
        invalid.extend(entry_invalid)
        logical_ledger_hash72, last_witness, _ = _ledger_transition(
            logical_ledger_hash72,
            index + 1,
            actual_hash,
        )
        expected_parent = actual_hash

    snapshot_accumulator = snapshot.get("ledger_accumulator_version")
    if snapshot_entries:
        if snapshot_accumulator == ACCUMULATOR_VERSION:
            expected_snapshot_hash = logical_ledger_hash72
        else:
            expected_snapshot_hash = _ledger_digest(
                "hhs_unified_hash72_ledger_v1",
                _ledger_summary_payload(snapshot_entries, expected_parent),
            )
        if snapshot.get("ledger_hash72") != expected_snapshot_hash:
            invalid.append({
                "index": "snapshot-ledger",
                "reason": "snapshot ledger_hash72 mismatch",
                "expected": expected_snapshot_hash,
                "actual": snapshot.get("ledger_hash72"),
            })

    entries = list(snapshot_entries)
    for offset, record in enumerate(journal_records, start=1):
        journal_index = f"journal:{offset}"
        if record.get("schema") != JOURNAL_SCHEMA:
            invalid.append({
                "index": journal_index,
                "reason": "journal schema mismatch",
                "expected": JOURNAL_SCHEMA,
                "actual": record.get("schema"),
            })
        entry = dict(record.get("entry") or {})
        actual_hash, entry_invalid = _validate_entry(
            entry,
            expected_parent=expected_parent,
            index=journal_index,
        )
        invalid.extend(entry_invalid)

        expected_count = len(entries) + 1
        expected_hash, expected_witness, transition_payload = _ledger_transition(
            logical_ledger_hash72,
            expected_count,
            actual_hash,
        )
        try:
            actual_count = int(record.get("entry_count"))
        except (TypeError, ValueError):
            actual_count = -1
        if actual_count != expected_count:
            invalid.append({
                "index": journal_index,
                "reason": "journal entry_count mismatch",
                "expected": expected_count,
                "actual": record.get("entry_count"),
            })
        if record.get("prior_ledger_hash72") != logical_ledger_hash72:
            invalid.append({
                "index": journal_index,
                "reason": "journal prior_ledger_hash72 mismatch",
                "expected": logical_ledger_hash72,
                "actual": record.get("prior_ledger_hash72"),
            })
        if record.get("ledger_hash72") != expected_hash:
            invalid.append({
                "index": journal_index,
                "reason": "journal ledger_hash72 mismatch",
                "expected": expected_hash,
                "actual": record.get("ledger_hash72"),
            })
        if record.get("transition_payload") != transition_payload:
            invalid.append({
                "index": journal_index,
                "reason": "journal transition payload mismatch",
                "expected": transition_payload,
                "actual": record.get("transition_payload"),
            })
        if record.get("tip_hash72_kernel_witness") != expected_witness:
            invalid.append({
                "index": journal_index,
                "reason": "journal Hash72 accumulator witness mismatch",
            })

        entries.append(entry)
        expected_parent = actual_hash
        logical_ledger_hash72 = expected_hash
        last_witness = expected_witness

    if not entries:
        expected_parent = GENESIS_HASH72
        logical_ledger_hash72 = _empty_legacy_ledger_hash72()

    materialized = dict(snapshot)
    materialized.update({
        "schema": LEDGER_SCHEMA,
        "snapshot_hash72_authority": snapshot.get("hash72_authority", "LEGACY_OR_UNDECLARED"),
        "entries": entries,
        "entry_count": len(entries),
        "tip_hash72": expected_parent,
        "ledger_hash72": logical_ledger_hash72,
        "hash72_authority": HASH72_AUTHORITY,
        "ledger_accumulator_version": ACCUMULATOR_VERSION,
        "ledger_storage_mode": STORAGE_MODE,
        "snapshot_entry_count": len(snapshot_entries),
        "journal_entry_count": len(journal_records),
        "journal_path": str(_journal_path(path)),
        "tip_hash72_kernel_witness": last_witness,
    })
    return materialized, invalid


def _load_with_errors(
    path: str | Path,
    *,
    force_reload: bool = False,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    p = Path(path)
    key = _path_key(p)
    current_signatures = _signatures(p)
    with _CACHE_GUARD:
        if (
            not force_reload
            and key in _LEDGER_CACHE
            and _LEDGER_CACHE_SIGNATURES.get(key) == current_signatures
        ):
            return _LEDGER_CACHE[key], list(_LEDGER_CACHE_ERRORS.get(key, []))

    data, invalid = _materialize(p)
    with _CACHE_GUARD:
        _LEDGER_CACHE[key] = data
        _LEDGER_CACHE_ERRORS[key] = list(invalid)
        _LEDGER_CACHE_SIGNATURES[key] = current_signatures
    return data, invalid


def _load(path: str | Path) -> Dict[str, Any]:
    data, _ = _load_with_errors(path)
    return data


def warm_unified_ledger_cache(
    ledger_path: str | Path | None = None,
) -> Dict[str, Any]:
    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    with _lock_for(path):
        snapshot = _read_snapshot(path)
        if snapshot.get("entries") and snapshot.get("hash72_authority") != HASH72_AUTHORITY:
            rebuild_unified_ledger(path)
        data, invalid = _load_with_errors(path, force_reload=True)
        if invalid:
            raise RuntimeError(f"unified ledger failed warm validation: {invalid[:3]}")
        return _summary(data, path, ok=True)


def _summary(data: Dict[str, Any], path: Path, *, ok: bool) -> Dict[str, Any]:
    return {
        "schema": data.get("schema", LEDGER_SCHEMA),
        "ok": bool(ok),
        "entry_count": int(data.get("entry_count") or 0),
        "tip_hash72": str(data.get("tip_hash72") or GENESIS_HASH72),
        "ledger_hash72": str(data.get("ledger_hash72") or ""),
        "hash72_authority": data.get("hash72_authority", HASH72_AUTHORITY),
        "ledger_accumulator_version": data.get("ledger_accumulator_version", ACCUMULATOR_VERSION),
        "ledger_storage_mode": data.get("ledger_storage_mode", STORAGE_MODE),
        "snapshot_entry_count": int(data.get("snapshot_entry_count") or 0),
        "journal_entry_count": int(data.get("journal_entry_count") or 0),
        "ledger_path": str(path),
        "journal_path": str(_journal_path(path)),
    }


def unified_ledger_summary(
    ledger_path: str | Path | None = None,
) -> Dict[str, Any]:
    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    with _lock_for(path):
        data, invalid = _load_with_errors(path)
        return _summary(data, path, ok=not invalid)


def append_unified_entry(
    ledger_path: str | Path,
    entry: UnifiedLedgerEntry,
) -> Dict[str, Any]:
    path = Path(ledger_path)
    with _lock_for(path):
        data, invalid = _load_with_errors(path)
        if invalid:
            raise RuntimeError(f"refusing append to invalid unified ledger: {invalid[:3]}")

        expected_parent = str(data.get("tip_hash72") or GENESIS_HASH72)
        if entry.parent_hash72 != expected_parent:
            raise ValueError(
                "unified ledger entry parent mismatch: "
                f"expected {expected_parent}, got {entry.parent_hash72}"
            )

        if not path.exists():
            _atomic_write_json(path, _empty_snapshot())

        prior_ledger_hash72 = str(data.get("ledger_hash72") or _empty_legacy_ledger_hash72())
        entry_count = int(data.get("entry_count") or 0) + 1
        ledger_hash72, witness, transition_payload = _ledger_transition(
            prior_ledger_hash72,
            entry_count,
            entry.entry_hash72,
        )
        journal_record = {
            "schema": JOURNAL_SCHEMA,
            "entry": entry.to_dict(),
            "entry_count": entry_count,
            "prior_ledger_hash72": prior_ledger_hash72,
            "ledger_hash72": ledger_hash72,
            "transition_payload": transition_payload,
            "tip_hash72_kernel_witness": witness,
        }
        _append_journal_record(path, journal_record)

        data.setdefault("entries", []).append(entry.to_dict())
        data.update({
            "schema": LEDGER_SCHEMA,
            "entry_count": entry_count,
            "tip_hash72": entry.entry_hash72,
            "ledger_hash72": ledger_hash72,
            "hash72_authority": HASH72_AUTHORITY,
            "ledger_accumulator_version": ACCUMULATOR_VERSION,
            "ledger_storage_mode": STORAGE_MODE,
            "snapshot_entry_count": int(data.get("snapshot_entry_count") or 0),
            "journal_entry_count": int(data.get("journal_entry_count") or 0) + 1,
            "journal_path": str(_journal_path(path)),
            "tip_hash72_kernel_witness": witness,
        })

        key = _path_key(path)
        with _CACHE_GUARD:
            _LEDGER_CACHE[key] = data
            _LEDGER_CACHE_ERRORS[key] = []
            _LEDGER_CACHE_SIGNATURES[key] = _signatures(path)
        return data


def append_payload(
    kind: str,
    source: str,
    payload: Dict[str, Any],
    *,
    ledger_path: str | Path | None = None,
) -> Dict[str, Any]:
    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    with _lock_for(path):
        data, invalid = _load_with_errors(path)
        if data.get("entries") and data.get("snapshot_hash72_authority") != HASH72_AUTHORITY:
            data = rebuild_unified_ledger(path)
            invalid = []
        if invalid:
            raise RuntimeError(f"refusing append to invalid unified ledger: {invalid[:3]}")
        parent = str(data.get("tip_hash72") or GENESIS_HASH72)
        entry = make_unified_entry(kind, source, payload, parent)
        return append_unified_entry(path, entry)


def verify_unified_ledger(
    ledger_path: str | Path | None = None,
) -> Dict[str, Any]:
    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    with _lock_for(path):
        data, invalid = _load_with_errors(path, force_reload=True)
        return {
            "ok": len(invalid) == 0,
            "invalid": invalid,
            "entry_count": int(data.get("entry_count") or 0),
            "tip_hash72": data.get("tip_hash72"),
            "ledger_hash72": data.get("ledger_hash72"),
            "hash72_authority": data.get("hash72_authority", "LEGACY_OR_UNDECLARED"),
            "ledger_accumulator_version": data.get("ledger_accumulator_version"),
            "ledger_storage_mode": data.get("ledger_storage_mode"),
            "snapshot_entry_count": data.get("snapshot_entry_count", 0),
            "journal_entry_count": data.get("journal_entry_count", 0),
            "ledger_path": str(path),
            "journal_path": str(_journal_path(path)),
        }


def _raw_entries(path: Path) -> List[Dict[str, Any]]:
    snapshot = _read_snapshot(path)
    entries = [dict(entry) for entry in snapshot.get("entries", [])]
    journal_records, _ = _read_journal(path)
    entries.extend(dict(record.get("entry") or {}) for record in journal_records)
    return entries


def rebuild_unified_ledger(
    ledger_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Repair and compact the complete snapshot + journal into one snapshot."""

    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    with _lock_for(path):
        rebuilt_entries: List[Dict[str, Any]] = []
        parent = GENESIS_HASH72
        ledger_hash72 = _empty_legacy_ledger_hash72()
        witness: Dict[str, Any] | None = None

        for raw in _raw_entries(path):
            entry = make_unified_entry(
                str(raw.get("kind", "")),
                str(raw.get("source", "")),
                dict(raw.get("payload", {}) or {}),
                parent,
            )
            rebuilt_entries.append(entry.to_dict())
            parent = entry.entry_hash72
            ledger_hash72, witness, _ = _ledger_transition(
                ledger_hash72,
                len(rebuilt_entries),
                parent,
            )

        if witness is None:
            witness = _empty_snapshot()["tip_hash72_kernel_witness"]

        repaired = {
            "schema": LEDGER_SCHEMA,
            "entries": rebuilt_entries,
            "entry_count": len(rebuilt_entries),
            "tip_hash72": parent,
            "ledger_hash72": ledger_hash72,
            "hash72_authority": HASH72_AUTHORITY,
            "ledger_accumulator_version": ACCUMULATOR_VERSION,
            "ledger_storage_mode": STORAGE_MODE,
            "tip_hash72_kernel_witness": witness,
        }
        _atomic_write_json(path, repaired)
        journal = _journal_path(path)
        if journal.exists():
            journal.unlink()

        materialized = dict(repaired)
        materialized.update({
            "snapshot_entry_count": len(rebuilt_entries),
            "journal_entry_count": 0,
            "journal_path": str(journal),
        })
        key = _path_key(path)
        with _CACHE_GUARD:
            _LEDGER_CACHE[key] = materialized
            _LEDGER_CACHE_ERRORS[key] = []
            _LEDGER_CACHE_SIGNATURES[key] = _signatures(path)
        return materialized


def compact_unified_ledger(
    ledger_path: str | Path | None = None,
) -> Dict[str, Any]:
    return rebuild_unified_ledger(ledger_path)


def absorb_json_artifacts(
    paths: Iterable[str | Path],
    *,
    ledger_path: str | Path | None = None,
) -> Dict[str, Any]:
    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    absorbed: List[Dict[str, Any]] = []
    for raw in paths:
        artifact_path = Path(raw)
        if not artifact_path.exists() or not artifact_path.is_file():
            absorbed.append({"path": str(artifact_path), "status": "MISSING"})
            continue
        try:
            payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        except Exception as exc:
            absorbed.append({
                "path": str(artifact_path),
                "status": "UNREADABLE",
                "error": f"{type(exc).__name__}: {exc}",
            })
            continue
        data = append_payload("JSON_ARTIFACT", str(artifact_path), payload, ledger_path=path)
        absorbed.append({
            "path": str(artifact_path),
            "status": "ABSORBED",
            "tip_hash72": data.get("tip_hash72"),
        })
    verification = verify_unified_ledger(path)
    return {"absorbed": absorbed, "verification": verification}
