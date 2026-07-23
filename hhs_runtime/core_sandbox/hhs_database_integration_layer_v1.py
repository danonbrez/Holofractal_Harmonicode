"""
Core Sandbox Database Integration V1
===================================

The original surface exposed ``HHSDatabase`` as deterministic JSON storage and
later callers declared a richer ``HHSRuntimeDatabaseBridgeV1`` contract.  Pass
145 preserves the legacy class and fulfils the declared runtime bridge through
the authoritative transactional knowledge database.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


class HHSDatabase:
    """Legacy deterministic JSON persistence surface."""

    def __init__(self, path: str):
        self.path = Path(path)

    def save(self, data: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class HHSRuntimeTraceRecordV1:
    trace_hash72: str
    source_id: str
    source_root_hash72: str
    program_name: str
    receipt_count: int
    database_root_hash72: str
    transaction_receipt_id: str
    transaction_receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": "HHS_RUNTIME_TRACE_RECORD_V1",
            "trace_hash72": self.trace_hash72,
            "source_id": self.source_id,
            "source_root_hash72": self.source_root_hash72,
            "program_name": self.program_name,
            "receipt_count": self.receipt_count,
            "database_root_hash72": self.database_root_hash72,
            "transaction_receipt_id": self.transaction_receipt_id,
            "transaction_receipt_hash72": self.transaction_receipt_hash72,
        }


class HHSRuntimeDatabaseBridgeV1:
    """Compatibility bridge backed by Pass 145 transactional storage.

    Runtime traces are admitted as immutable receipt documents.  The exact JSON
    bytes remain the evidence object; their parse and validation identities are
    separate, and retrieval is keyed by the canonical trace witness.
    """

    DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "runtime" / "hhs_runtime_bridge.sqlite3"

    def __init__(self, db_path: str | Path | None = None):
        from hhs_runtime.pass145.service import HHS145Service

        self.db_path = Path(db_path or self.DEFAULT_PATH).expanduser().resolve()
        self.service = HHS145Service(self.db_path)

    def close(self) -> None:
        self.service.close()

    def __enter__(self) -> "HHSRuntimeDatabaseBridgeV1":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    @staticmethod
    def _receipt_dict(receipt: Any) -> Dict[str, Any]:
        if hasattr(receipt, "to_dict"):
            value = receipt.to_dict()
        elif isinstance(receipt, Mapping):
            value = dict(receipt)
        else:
            raise TypeError(f"unsupported runtime receipt type: {type(receipt).__name__}")
        if not isinstance(value, dict):
            raise TypeError("runtime receipt serialization must be an object")
        return value

    def store_runner(self, runner: Any, *, program_name: str, metadata: Mapping[str, Any] | None = None) -> HHSRuntimeTraceRecordV1:
        receipts = getattr(getattr(runner, "commitments", None), "receipts", None)
        if receipts is None:
            raise TypeError("runner does not expose commitments.receipts")
        return self.store_trace(receipts, program_name=program_name, metadata=metadata)

    def store_trace(self, receipts: Iterable[Any], *, program_name: str, metadata: Mapping[str, Any] | None = None) -> HHSRuntimeTraceRecordV1:
        from hhs_runtime.pass145.canonical import canonical_json, hash72

        receipt_list = [self._receipt_dict(item) for item in receipts]
        payload = {
            "schema": "HHS_RUNTIME_TRACE_DOCUMENT_V1",
            "program_name": str(program_name),
            "metadata": dict(metadata or {}),
            "receipts": receipt_list,
        }
        trace_hash72 = hash72("hhs_runtime_trace_document_v1", payload)
        payload["trace_hash72"] = trace_hash72
        raw = (canonical_json(payload) + "\n").encode("utf-8")
        admitted = self.service.ingest_bytes(
            raw,
            name=f"runtime-trace-{trace_hash72}.json",
            mime_type="application/vnd.hhs.receipt+json",
            namespace="runtime-traces",
            source_kind="RUNTIME_DATABASE_BRIDGE",
            acquisition={"method": "RUNTIME_DATABASE_BRIDGE", "program_name": str(program_name)},
            analyze=False,
        )
        return HHSRuntimeTraceRecordV1(
            trace_hash72=trace_hash72,
            source_id=admitted["source_id"],
            source_root_hash72=admitted["source_root_hash72"],
            program_name=str(program_name),
            receipt_count=len(receipt_list),
            database_root_hash72=admitted["database_root_hash72"],
            transaction_receipt_id=admitted["receipt_id"],
            transaction_receipt_hash72=admitted["receipt_hash72"],
        )

    def load_trace(self, trace_hash72: str) -> Dict[str, Any] | None:
        rows = self.service.db.conn.execute(
            "SELECT source_id FROM sources WHERE namespace='runtime-traces' ORDER BY source_id"
        ).fetchall()
        for row in rows:
            source = self.service.db.get_source(row["source_id"], include_raw=True)
            if source is None:
                continue
            try:
                payload = json.loads(source["raw_bytes"])
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if payload.get("trace_hash72") == trace_hash72:
                return {
                    "schema": "HHS_RUNTIME_TRACE_LOAD_V1",
                    "trace_hash72": trace_hash72,
                    "source_id": source["source_id"],
                    "source_root_hash72": source["source_root_hash72"],
                    "program_name": payload.get("program_name"),
                    "metadata": payload.get("metadata", {}),
                    "receipts": payload.get("receipts", []),
                    "receipt_count": len(payload.get("receipts", [])),
                }
        return None

    def quarantine_report(self) -> Dict[str, Any]:
        db = self.service.db
        sources = int(db.conn.execute("SELECT COUNT(*) FROM sources WHERE quarantined=1").fetchone()[0])
        objects = int(db.conn.execute("SELECT COUNT(*) FROM objects WHERE quarantined=1").fetchone()[0])
        return {
            "schema": "HHS_RUNTIME_DATABASE_QUARANTINE_REPORT_V1",
            "quarantined_sources": sources,
            "quarantined_objects": objects,
            "database_integrity": db.integrity_check(),
        }


__all__ = ["HHSDatabase", "HHSRuntimeDatabaseBridgeV1", "HHSRuntimeTraceRecordV1"]
