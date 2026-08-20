"""Verified lookup of canonical VM81 runtime receipts in the unified Hash72 ledger."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_unified_hash72_ledger_v1 import (
    HASH72_AUTHORITY,
    _load_with_errors,
    _lock_for,
    default_unified_ledger_path,
)

VERSION = "HHS_VM81_RECEIPT_PROVENANCE_V1"
RUNTIME_RECEIPT_KIND = "RUNTIME_RECEIPT"
RUNTIME_RECEIPT_SOURCE = "HHSRuntimeController.commit_receipt"


def verify_runtime_receipt_hash72(
    receipt_hash72: str,
    *,
    ledger_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Verify that ``receipt_hash72`` is carried by the canonical validated ledger.

    A 72-glyph shape is necessary but never sufficient.  The receipt must occur
    in an intact unified Hash72 chain as a runtime-controller commit whose own
    authority audit was successful.
    """

    value = str(receipt_hash72 or "")
    if len(value) != 72:
        return {
            "schema": VERSION,
            "ok": False,
            "reason": "receipt_hash72 must contain exactly 72 glyphs",
            "receipt_hash72": value,
        }

    path = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    with _lock_for(path):
        data, invalid = _load_with_errors(path, force_reload=True)

    if invalid:
        return {
            "schema": VERSION,
            "ok": False,
            "reason": "unified Hash72 ledger failed validation",
            "receipt_hash72": value,
            "invalid_count": len(invalid),
            "ledger_path": str(path),
        }

    matches = []
    for index, entry in enumerate(data.get("entries") or []):
        if entry.get("kind") != RUNTIME_RECEIPT_KIND:
            continue
        if entry.get("source") != RUNTIME_RECEIPT_SOURCE:
            continue
        payload = entry.get("payload") or {}
        if payload.get("receipt_hash72") != value:
            continue
        audit = payload.get("authority_audit") or {}
        if audit.get("ok") is not True:
            continue
        if audit.get("receipt_hash72") != value:
            continue
        if audit.get("omega") is not True or audit.get("hash72_receipt_ok") is not True:
            continue
        matches.append(
            {
                "index": index,
                "entry_hash72": entry.get("entry_hash72"),
                "parent_hash72": entry.get("parent_hash72"),
                "runtime_step": payload.get("step"),
                "state_hash72": payload.get("state_hash72"),
            }
        )

    if not matches:
        return {
            "schema": VERSION,
            "ok": False,
            "reason": "receipt not found in canonical verified runtime receipt chain",
            "receipt_hash72": value,
            "entry_count": int(data.get("entry_count") or 0),
            "ledger_path": str(path),
        }

    return {
        "schema": VERSION,
        "ok": True,
        "receipt_hash72": value,
        "match_count": len(matches),
        "matches": matches,
        "entry_count": int(data.get("entry_count") or 0),
        "tip_hash72": data.get("tip_hash72"),
        "ledger_hash72": data.get("ledger_hash72"),
        "hash72_authority": data.get("hash72_authority", HASH72_AUTHORITY),
        "ledger_path": str(path),
    }


def require_runtime_receipt_hash72(
    receipt_hash72: str,
    *,
    ledger_path: str | Path | None = None,
) -> Dict[str, Any]:
    evidence = verify_runtime_receipt_hash72(receipt_hash72, ledger_path=ledger_path)
    if not evidence.get("ok"):
        raise ValueError(f"VM81_RECEIPT_PROVENANCE_REJECTED:{evidence.get('reason')}")
    return evidence
