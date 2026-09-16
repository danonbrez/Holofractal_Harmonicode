"""Fail-closed recovery for derived unified Hash72 journal metadata.

This module repairs only journal transition metadata that can be recomputed from
an independently verified authoritative entry chain.  It never repairs entry
payloads, parent links, entry hashes, malformed JSON, or snapshot authority.

The recovery contract is deliberately narrower than ``rebuild_unified_ledger``:

* every snapshot and journal entry must already verify from genesis;
* every verifier error must be a journal transition-metadata error;
* the original snapshot and journal are backed up before mutation;
* the journal is replaced atomically while preserving each authoritative entry;
* the complete ledger must verify after replacement or the original journal is
  restored; and
* a standalone recovery receipt is emitted outside the ledger being repaired.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any

from hhs_runtime import hhs_unified_hash72_ledger_v1 as ledger


RECOVERY_SCHEMA = "HHS_UNIFIED_HASH72_TRANSITION_RECOVERY_V1"
RECOVERABLE_REASONS = frozenset(
    {
        "journal entry_count mismatch",
        "journal prior_ledger_hash72 mismatch",
        "journal ledger_hash72 mismatch",
        "journal transition payload mismatch",
        "journal Hash72 accumulator witness mismatch",
    }
)


class UnifiedLedgerRecoveryError(RuntimeError):
    """Raised when a ledger cannot be repaired without changing authority."""


@dataclass(frozen=True)
class _VerifiedEntryChain:
    snapshot: dict[str, Any]
    journal_records: tuple[dict[str, Any], ...]
    snapshot_entry_count: int
    initial_journal_ledger_hash72: str


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.recovery.tmp")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(ledger._canonical_payload(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_restore(source: Path, destination: Path) -> None:
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.restore.tmp")
    shutil.copy2(source, temporary)
    with temporary.open("rb") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, destination)


def _verify_authoritative_entry_chain(path: Path) -> _VerifiedEntryChain:
    snapshot = ledger._read_snapshot(path)
    snapshot_entries = [dict(entry) for entry in snapshot.get("entries", [])]
    journal_records, journal_parse_errors = ledger._read_journal(path)
    if journal_parse_errors:
        raise UnifiedLedgerRecoveryError(
            f"journal syntax is not recoverable: {journal_parse_errors[:3]}"
        )

    declared_count = int(snapshot.get("entry_count") or 0)
    if declared_count != len(snapshot_entries):
        raise UnifiedLedgerRecoveryError(
            "snapshot entry_count is authoritative state and does not match entries"
        )
    expected_snapshot_tip = (
        str(snapshot_entries[-1].get("entry_hash72", ""))
        if snapshot_entries
        else ledger.GENESIS_HASH72
    )
    if str(snapshot.get("tip_hash72") or ledger.GENESIS_HASH72) != expected_snapshot_tip:
        raise UnifiedLedgerRecoveryError("snapshot tip_hash72 does not match authoritative entries")

    expected_parent = ledger.GENESIS_HASH72
    logical_ledger_hash72 = ledger._empty_legacy_ledger_hash72()
    for index, entry in enumerate(snapshot_entries):
        actual_hash, invalid = ledger._validate_entry(
            entry,
            expected_parent=expected_parent,
            index=index,
        )
        if invalid:
            raise UnifiedLedgerRecoveryError(
                f"snapshot authoritative entry chain is invalid: {invalid[:3]}"
            )
        logical_ledger_hash72, _, _ = ledger._ledger_transition(
            logical_ledger_hash72,
            index + 1,
            actual_hash,
        )
        expected_parent = actual_hash

    if snapshot_entries:
        if snapshot.get("ledger_accumulator_version") == ledger.ACCUMULATOR_VERSION:
            expected_snapshot_hash = logical_ledger_hash72
        else:
            expected_snapshot_hash = ledger._ledger_digest(
                "hhs_unified_hash72_ledger_v1",
                ledger._ledger_summary_payload(snapshot_entries, expected_parent),
            )
        if snapshot.get("ledger_hash72") != expected_snapshot_hash:
            raise UnifiedLedgerRecoveryError(
                "snapshot ledger_hash72 is not derivable from authoritative entries"
            )

    for offset, record in enumerate(journal_records, start=1):
        if record.get("schema") != ledger.JOURNAL_SCHEMA:
            raise UnifiedLedgerRecoveryError(
                f"journal:{offset} schema mismatch is outside transition recovery"
            )
        entry_raw = record.get("entry")
        if not isinstance(entry_raw, dict):
            raise UnifiedLedgerRecoveryError(
                f"journal:{offset} does not contain an authoritative entry object"
            )
        entry = dict(entry_raw)
        actual_hash, invalid = ledger._validate_entry(
            entry,
            expected_parent=expected_parent,
            index=f"journal:{offset}",
        )
        if invalid:
            raise UnifiedLedgerRecoveryError(
                f"journal authoritative entry chain is invalid: {invalid[:3]}"
            )
        expected_parent = actual_hash

    return _VerifiedEntryChain(
        snapshot=dict(snapshot),
        journal_records=tuple(dict(record) for record in journal_records),
        snapshot_entry_count=len(snapshot_entries),
        initial_journal_ledger_hash72=logical_ledger_hash72,
    )


def _assert_transition_only_errors(invalid: list[dict[str, Any]]) -> None:
    forbidden = [
        item
        for item in invalid
        if not str(item.get("index", "")).startswith("journal:")
        or str(item.get("reason", "")) not in RECOVERABLE_REASONS
    ]
    if forbidden:
        raise UnifiedLedgerRecoveryError(
            f"ledger contains non-transition corruption: {forbidden[:3]}"
        )


def inspect_transition_metadata_recovery(
    ledger_path: str | Path,
) -> dict[str, Any]:
    """Return whether a ledger is valid or narrowly transition-repairable."""

    path = Path(ledger_path)
    with ledger._lock_for(path):
        chain = _verify_authoritative_entry_chain(path)
        verification = ledger.verify_unified_ledger(path)
        invalid = [dict(item) for item in verification.get("invalid", [])]
        if not invalid:
            return {
                "schema": RECOVERY_SCHEMA,
                "status": "VALID_NO_REPAIR_REQUIRED",
                "repairable": False,
                "entry_count": int(verification.get("entry_count") or 0),
                "ledger_path": str(path),
            }
        _assert_transition_only_errors(invalid)
        return {
            "schema": RECOVERY_SCHEMA,
            "status": "RECOVERABLE_TRANSITION_METADATA",
            "repairable": True,
            "entry_count": chain.snapshot_entry_count + len(chain.journal_records),
            "ledger_path": str(path),
            "invalid": invalid,
        }


def repair_transition_metadata(
    ledger_path: str | Path,
    *,
    backup_root: str | Path,
    receipt_path: str | Path | None = None,
    require_repair: bool = False,
) -> dict[str, Any]:
    """Repair only derivable journal transition metadata, with rollback evidence."""

    path = Path(ledger_path)
    journal_path = ledger._journal_path(path)
    backup_base = Path(backup_root)

    with ledger._lock_for(path):
        chain = _verify_authoritative_entry_chain(path)
        before = ledger.verify_unified_ledger(path)
        invalid = [dict(item) for item in before.get("invalid", [])]
        if not invalid:
            if require_repair:
                raise UnifiedLedgerRecoveryError("ledger is already valid; repair was required")
            receipt = {
                "schema": RECOVERY_SCHEMA,
                "status": "VALID_NO_REPAIR_REQUIRED",
                "ledger_path": str(path),
                "entry_count": int(before.get("entry_count") or 0),
                "ledger_hash72": before.get("ledger_hash72"),
                "tip_hash72": before.get("tip_hash72"),
            }
            if receipt_path is not None:
                destination = Path(receipt_path)
                destination.parent.mkdir(parents=True, exist_ok=True)
                ledger._atomic_write_json(destination, receipt)
            return receipt

        _assert_transition_only_errors(invalid)
        if not journal_path.is_file():
            raise UnifiedLedgerRecoveryError("transition errors exist but journal file is missing")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        incident_hash = hashlib.sha256(
            ledger._canonical_payload(invalid).encode("utf-8")
        ).hexdigest()[:16]
        backup_dir = backup_base / f"{timestamp}-{incident_hash}"
        backup_dir.mkdir(parents=True, exist_ok=False)
        snapshot_backup = backup_dir / path.name
        journal_backup = backup_dir / journal_path.name
        if path.is_file():
            shutil.copy2(path, snapshot_backup)
        shutil.copy2(journal_path, journal_backup)

        before_hashes = {
            "snapshot_sha256": _sha256(path),
            "journal_sha256": _sha256(journal_path),
        }

        repaired_records: list[dict[str, Any]] = []
        logical_ledger_hash72 = chain.initial_journal_ledger_hash72
        entry_count = chain.snapshot_entry_count
        for record in chain.journal_records:
            entry = dict(record["entry"])
            entry_count += 1
            entry_hash72 = str(entry.get("entry_hash72", ""))
            next_hash, witness, transition_payload = ledger._ledger_transition(
                logical_ledger_hash72,
                entry_count,
                entry_hash72,
            )
            repaired = dict(record)
            repaired.update(
                {
                    "schema": ledger.JOURNAL_SCHEMA,
                    "entry": entry,
                    "entry_count": entry_count,
                    "prior_ledger_hash72": logical_ledger_hash72,
                    "ledger_hash72": next_hash,
                    "transition_payload": transition_payload,
                    "tip_hash72_kernel_witness": witness,
                }
            )
            repaired_records.append(repaired)
            logical_ledger_hash72 = next_hash

        try:
            _atomic_write_jsonl(journal_path, repaired_records)
            after = ledger.verify_unified_ledger(path)
            if not after.get("ok"):
                raise UnifiedLedgerRecoveryError(
                    f"post-repair ledger verification failed: {after.get('invalid', [])[:3]}"
                )
        except Exception:
            _atomic_restore(journal_backup, journal_path)
            restored = ledger.verify_unified_ledger(path)
            if restored.get("ok"):
                raise UnifiedLedgerRecoveryError(
                    "repair failed and original journal was restored to a valid state"
                )
            raise

        receipt = {
            "schema": RECOVERY_SCHEMA,
            "status": "REPAIRED_TRANSITION_METADATA",
            "ledger_path": str(path),
            "journal_path": str(journal_path),
            "backup_directory": str(backup_dir),
            "snapshot_backup": str(snapshot_backup) if snapshot_backup.exists() else None,
            "journal_backup": str(journal_backup),
            "authoritative_entries_preserved": True,
            "entry_payloads_modified": False,
            "entry_hashes_modified": False,
            "repaired_journal_records": len(repaired_records),
            "invalid_before": invalid,
            "before_hashes": before_hashes,
            "after_hashes": {
                "snapshot_sha256": _sha256(path),
                "journal_sha256": _sha256(journal_path),
            },
            "entry_count": int(after.get("entry_count") or 0),
            "tip_hash72": after.get("tip_hash72"),
            "ledger_hash72": after.get("ledger_hash72"),
            "hash72_authority": after.get("hash72_authority"),
            "result": "PASS",
        }
        destination = Path(receipt_path) if receipt_path is not None else backup_dir / "recovery-receipt.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        ledger._atomic_write_json(destination, receipt)
        receipt["receipt_path"] = str(destination)
        return receipt
