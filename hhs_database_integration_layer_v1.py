"""
hhs_database_integration_layer_v1.py

Database integration bridge for HARMONICODE general runtime.

Purpose
-------
Persist audited runtime execution into the verbatim semantic database layer.

Stores:
- Hash72 receipts
- transition traces
- witness payloads
- operation summaries
- replay tips
- quarantine reports

Design
------
This layer does not mutate the locked kernel or database module.
It imports the existing HarmonicodeVerbatimSemanticDatabaseV1 when available.
If the uploaded filename cannot be imported normally, it loads it by file path.

Default flow:
    AuditedRunner / ControlFlowGates
    -> receipt objects
    -> trace records
    -> database state records / transition traces
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import importlib.util
import json
import sqlite3
import sys
import time

from hhs_general_runtime_layer_v1 import (
    AuditedRunner,
    DEFAULT_KERNEL_PATH,
    GENESIS_RECEIPT_HASH72,
    Hash72Authority,
    canonical_json,
    canonicalize_for_hash72,
    load_authoritative_kernel,
)


DEFAULT_DB_MODULE_PATH = Path("/mnt/data/harmonicode_verbatim_semantic_database_v1.py")
DEFAULT_DB_PATH = Path("/mnt/data/hhs_runtime_receipts_v1.sqlite3")


class HHSDatabaseIntegrationError(RuntimeError):
    pass


def load_verbatim_database_module(path: str | Path = DEFAULT_DB_MODULE_PATH):
    path = Path(path)
    if not path.exists():
        raise HHSDatabaseIntegrationError(f"Database module not found: {path}")

    module_name = "harmonicode_verbatim_semantic_database_v1_loaded"
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise HHSDatabaseIntegrationError(f"Could not create import spec for database module: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class RuntimeTraceRecordV1:
    trace_hash72: str
    program_name: str
    operation_count: int
    genesis_hash72: str
    tip_hash72: str
    all_locked: bool
    quarantine_count: int
    receipt_hashes: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReceiptStorageReportV1:
    ok: bool
    db_path: str
    stored_receipts: int
    trace_hash72: str
    tip_hash72: str
    quarantine_count: int
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSRuntimeDatabaseBridgeV1:
    """
    Storage bridge for runtime receipts.

    It creates dedicated tables for receipts and runtime traces. It also attempts
    to mirror high-level records through HarmonicodeVerbatimSemanticDatabaseV1
    when the database module provides suitable APIs.
    """

    def __init__(
        self,
        db_path: str | Path = DEFAULT_DB_PATH,
        *,
        kernel_path: str | Path = DEFAULT_KERNEL_PATH,
        db_module_path: str | Path = DEFAULT_DB_MODULE_PATH,
    ):
        self.db_path = Path(db_path)
        self.kernel = load_authoritative_kernel(kernel_path)
        self.authority = Hash72Authority(self.kernel)

        self.db_module = load_verbatim_database_module(db_module_path)
        self.semantic_db = None
        db_cls = getattr(self.db_module, "HarmonicodeVerbatimSemanticDatabaseV1", None)
        if db_cls is not None:
            try:
                self.semantic_db = db_cls(self.db_path)
            except Exception:
                # Dedicated tables below remain authoritative for runtime receipts.
                self.semantic_db = None

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self._init_schema()

    def close(self) -> None:
        try:
            if self.semantic_db is not None and hasattr(self.semantic_db, "close"):
                self.semantic_db.close()
        finally:
            self.conn.close()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS hhs_runtime_receipts (
                receipt_hash72 TEXT PRIMARY KEY,
                parent_receipt_hash72 TEXT NOT NULL,
                phase INTEGER NOT NULL,
                operation TEXT NOT NULL,
                gate_status TEXT NOT NULL,
                locked INTEGER NOT NULL,
                quarantine INTEGER NOT NULL,
                integrity_hash72 TEXT NOT NULL,
                input_hash72 TEXT NOT NULL,
                pre_state_hash72 TEXT NOT NULL,
                operation_hash72 TEXT NOT NULL,
                post_state_hash72 TEXT NOT NULL,
                witness_hash72 TEXT NOT NULL,
                receipt_json TEXT NOT NULL,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS hhs_runtime_traces (
                trace_hash72 TEXT PRIMARY KEY,
                program_name TEXT NOT NULL,
                operation_count INTEGER NOT NULL,
                genesis_hash72 TEXT NOT NULL,
                tip_hash72 TEXT NOT NULL,
                all_locked INTEGER NOT NULL,
                quarantine_count INTEGER NOT NULL,
                receipt_hashes_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS hhs_runtime_witnesses (
                witness_hash72 TEXT PRIMARY KEY,
                receipt_hash72 TEXT NOT NULL,
                operation TEXT NOT NULL,
                witness_json TEXT NOT NULL,
                created_at REAL NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_hhs_receipt_parent ON hhs_runtime_receipts(parent_receipt_hash72);
            CREATE INDEX IF NOT EXISTS idx_hhs_receipt_operation ON hhs_runtime_receipts(operation);
            CREATE INDEX IF NOT EXISTS idx_hhs_receipt_locked ON hhs_runtime_receipts(locked);
            CREATE INDEX IF NOT EXISTS idx_hhs_trace_tip ON hhs_runtime_traces(tip_hash72);
            """
        )
        self.conn.commit()

    @staticmethod
    def _receipt_to_dict(receipt: Any) -> Dict[str, Any]:
        if hasattr(receipt, "to_dict") and callable(getattr(receipt, "to_dict")):
            return receipt.to_dict()
        if hasattr(receipt, "__dict__") and not isinstance(receipt, dict):
            return dict(receipt.__dict__)
        if isinstance(receipt, dict):
            return receipt
        raise TypeError(f"Unsupported receipt type: {type(receipt).__name__}")

    def store_receipt(self, receipt: Any, *, witness_payload: Optional[Any] = None) -> str:
        r = canonicalize_for_hash72(self._receipt_to_dict(receipt))
        receipt_hash = r["receipt_hash72"]
        now = time.time()

        self.conn.execute(
            """
            INSERT OR REPLACE INTO hhs_runtime_receipts (
                receipt_hash72,
                parent_receipt_hash72,
                phase,
                operation,
                gate_status,
                locked,
                quarantine,
                integrity_hash72,
                input_hash72,
                pre_state_hash72,
                operation_hash72,
                post_state_hash72,
                witness_hash72,
                receipt_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                receipt_hash,
                r["parent_receipt_hash72"],
                int(r["phase"]),
                r["operation"],
                r["gate_status"],
                1 if r["locked"] else 0,
                1 if r.get("quarantine") else 0,
                r["integrity_hash72"],
                r["input_hash72"],
                r["pre_state_hash72"],
                r["operation_hash72"],
                r["post_state_hash72"],
                r["witness_hash72"],
                canonical_json(r),
                now,
            ),
        )

        if witness_payload is not None:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO hhs_runtime_witnesses (
                    witness_hash72,
                    receipt_hash72,
                    operation,
                    witness_json,
                    created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    r["witness_hash72"],
                    receipt_hash,
                    r["operation"],
                    canonical_json(witness_payload),
                    now,
                ),
            )

        self.conn.commit()
        return receipt_hash

    def store_trace(
        self,
        receipts: Iterable[Any],
        *,
        program_name: str = "HHS_RUNTIME_PROGRAM",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RuntimeTraceRecordV1:
        normalized = [canonicalize_for_hash72(self._receipt_to_dict(r)) for r in receipts]
        receipt_hashes = [r["receipt_hash72"] for r in normalized]
        quarantine_count = sum(1 for r in normalized if r.get("quarantine") or not r.get("locked"))
        all_locked = quarantine_count == 0
        tip = receipt_hashes[-1] if receipt_hashes else GENESIS_RECEIPT_HASH72

        trace_core = {
            "program_name": program_name,
            "operation_count": len(normalized),
            "genesis_hash72": GENESIS_RECEIPT_HASH72,
            "tip_hash72": tip,
            "all_locked": all_locked,
            "quarantine_count": quarantine_count,
            "receipt_hashes": receipt_hashes,
            "metadata": metadata or {},
        }
        trace_hash = self.authority.commit(trace_core, domain="HHS_RUNTIME_TRACE")

        trace = RuntimeTraceRecordV1(
            trace_hash72=trace_hash,
            program_name=program_name,
            operation_count=len(normalized),
            genesis_hash72=GENESIS_RECEIPT_HASH72,
            tip_hash72=tip,
            all_locked=all_locked,
            quarantine_count=quarantine_count,
            receipt_hashes=receipt_hashes,
            metadata=metadata or {},
        )

        for receipt in normalized:
            self.store_receipt(receipt)

        self.conn.execute(
            """
            INSERT OR REPLACE INTO hhs_runtime_traces (
                trace_hash72,
                program_name,
                operation_count,
                genesis_hash72,
                tip_hash72,
                all_locked,
                quarantine_count,
                receipt_hashes_json,
                metadata_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace.trace_hash72,
                trace.program_name,
                trace.operation_count,
                trace.genesis_hash72,
                trace.tip_hash72,
                1 if trace.all_locked else 0,
                trace.quarantine_count,
                canonical_json(trace.receipt_hashes),
                canonical_json(trace.metadata),
                trace.created_at,
            ),
        )
        self.conn.commit()
        return trace

    def store_runner(
        self,
        runner: AuditedRunner,
        *,
        program_name: str = "HHS_AUDITED_RUNNER_PROGRAM",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ReceiptStorageReportV1:
        try:
            trace = self.store_trace(
                runner.commitments.receipts,
                program_name=program_name,
                metadata=metadata or {
                    "runner_tip_hash72": runner.commitments.tip_hash72,
                    "phase": runner.commitments.phase,
                    "registry": runner.registry.names(),
                },
            )
            return ReceiptStorageReportV1(
                ok=True,
                db_path=str(self.db_path),
                stored_receipts=trace.operation_count,
                trace_hash72=trace.trace_hash72,
                tip_hash72=trace.tip_hash72,
                quarantine_count=trace.quarantine_count,
            )
        except Exception as exc:
            return ReceiptStorageReportV1(
                ok=False,
                db_path=str(self.db_path),
                stored_receipts=0,
                trace_hash72="",
                tip_hash72="",
                quarantine_count=0,
                reason=f"{type(exc).__name__}: {exc}",
            )

    def load_trace(self, trace_hash72: str) -> Dict[str, Any]:
        row = self.conn.execute(
            "SELECT * FROM hhs_runtime_traces WHERE trace_hash72 = ?",
            (trace_hash72,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Trace not found: {trace_hash72}")

        columns = [d[0] for d in self.conn.execute("SELECT * FROM hhs_runtime_traces LIMIT 0").description]
        payload = dict(zip(columns, row))
        payload["receipt_hashes"] = json.loads(payload.pop("receipt_hashes_json"))
        payload["metadata"] = json.loads(payload.pop("metadata_json"))
        return payload

    def load_receipts_for_trace(self, trace_hash72: str) -> List[Dict[str, Any]]:
        trace = self.load_trace(trace_hash72)
        receipts = []
        for h in trace["receipt_hashes"]:
            row = self.conn.execute(
                "SELECT receipt_json FROM hhs_runtime_receipts WHERE receipt_hash72 = ?",
                (h,),
            ).fetchone()
            if row is None:
                raise KeyError(f"Receipt missing for trace {trace_hash72}: {h}")
            receipts.append(json.loads(row[0]))
        return receipts

    def quarantine_report(self) -> Dict[str, Any]:
        rows = self.conn.execute(
            """
            SELECT receipt_hash72, operation, gate_status, receipt_json
            FROM hhs_runtime_receipts
            WHERE quarantine = 1 OR locked = 0
            ORDER BY created_at ASC
            """
        ).fetchall()
        items = []
        for receipt_hash, operation, gate_status, receipt_json in rows:
            receipt = json.loads(receipt_json)
            items.append({
                "receipt_hash72": receipt_hash,
                "operation": operation,
                "gate_status": gate_status,
                "reason": receipt.get("reason", ""),
            })
        return {
            "quarantine_count": len(items),
            "items": items,
        }


def demo() -> Dict[str, Any]:
    runner = AuditedRunner()
    runner.execute("ADD", 2, 3)
    runner.execute("SORT", [9, 1, 4, 1])
    runner.execute("DIV", 1, 0)

    bridge = HHSRuntimeDatabaseBridgeV1()
    report = bridge.store_runner(
        runner,
        program_name="DATABASE_INTEGRATION_DEMO",
        metadata={"demo": True},
    )
    quarantine = bridge.quarantine_report()
    trace = bridge.load_trace(report.trace_hash72) if report.ok else {}
    bridge.close()

    return {
        "storage_report": report.to_dict(),
        "trace": trace,
        "quarantine_report": quarantine,
    }


def main() -> None:
    print(json.dumps(demo(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
