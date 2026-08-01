#!/usr/bin/env python3
"""Pass 190 iteration 2: persistent receipts, event transport, and SDK authority."""
from __future__ import annotations

import copy
import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Iterable, Mapping

from hhs_pass190 import (
    DEFAULT_REGISTRY,
    HHSAuthorityContext,
    HHSOperationError,
    InvocationResult,
    canonical_json,
    hash72,
    hash216,
)

ITERATION2_CLASSIFICATION = "HHS_PASS_190_ITERATION_2_PERSISTENT_EVENT_SDK_GUI_FOUNDATION_VERIFIED"
DEFAULT_DATABASE = Path(os.environ.get("HHS_PASS190_DATABASE", "pass190-authority.sqlite3"))


class PersistentStoreError(HHSOperationError):
    pass


class SQLiteAuthorityStore:
    """Atomic SQLite state for receipts, idempotency, state, and resumable events."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        self._connection = sqlite3.connect(str(self.path), check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._initialize()

    def _initialize(self) -> None:
        with self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS receipts (
                    receipt_index INTEGER PRIMARY KEY,
                    hash72 TEXT NOT NULL UNIQUE,
                    predecessor_hash72 TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS idempotency (
                    key TEXT PRIMARY KEY,
                    request_identity TEXT NOT NULL,
                    receipt_hash72 TEXT NOT NULL,
                    FOREIGN KEY(receipt_hash72) REFERENCES receipts(hash72)
                );
                CREATE TABLE IF NOT EXISTS authority_meta (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                """
            )

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def reset(self) -> None:
        with self._condition, self._connection:
            self._connection.executescript(
                "DELETE FROM idempotency; DELETE FROM receipts; DELETE FROM authority_meta; DELETE FROM events;"
            )
            self._condition.notify_all()

    def _meta(self) -> dict[str, Any]:
        rows = self._connection.execute("SELECT key, value_json FROM authority_meta").fetchall()
        return {row["key"]: json.loads(row["value_json"]) for row in rows}

    def restore_into(self, context: HHSAuthorityContext) -> None:
        with self._lock:
            rows = self._connection.execute(
                "SELECT receipt_index, hash72, predecessor_hash72, payload_json FROM receipts ORDER BY receipt_index"
            ).fetchall()
            receipts: dict[str, dict[str, Any]] = {}
            predecessor = "0" * 72
            expected_index = 1
            for row in rows:
                if row["receipt_index"] != expected_index:
                    raise PersistentStoreError("receipt index discontinuity")
                receipt = json.loads(row["payload_json"])
                if receipt.get("receipt_index") != expected_index:
                    raise PersistentStoreError("receipt payload index mismatch")
                if row["predecessor_hash72"] != predecessor or receipt.get("predecessor_hash72") != predecessor:
                    raise PersistentStoreError("receipt predecessor mismatch")
                payload = {key: value for key, value in receipt.items() if key not in {"hash72", "hash216"}}
                expected_hash72 = hash72("pass190.receipt", payload)
                expected_hash216 = hash216("pass190.receipt.topology", payload)
                if row["hash72"] != expected_hash72 or receipt.get("hash72") != expected_hash72:
                    raise PersistentStoreError("receipt Hash72 mismatch")
                if receipt.get("hash216") != expected_hash216:
                    raise PersistentStoreError("receipt Hash216 mismatch")
                receipts[expected_hash72] = receipt
                predecessor = expected_hash72
                expected_index += 1

            meta = self._meta()
            context._receipts = receipts
            context._receipt_index = len(rows)
            context._last_hash72 = predecessor
            context._state = copy.deepcopy(meta.get("state", {"counter": 0}))
            context._state_root = meta.get("state_root", hash72("pass190.state", context._state))
            if context._state_root != hash72("pass190.state", context._state):
                raise PersistentStoreError("persisted state root mismatch")
            if meta.get("receipt_index", len(rows)) != len(rows):
                raise PersistentStoreError("persisted receipt index mismatch")
            if meta.get("last_hash72", predecessor) != predecessor:
                raise PersistentStoreError("persisted chain head mismatch")

            context._idempotency = {}
            for row in self._connection.execute(
                "SELECT key, request_identity, receipt_hash72 FROM idempotency ORDER BY key"
            ):
                receipt = receipts.get(row["receipt_hash72"])
                if receipt is None or receipt.get("request_identity") != row["request_identity"]:
                    raise PersistentStoreError("idempotency reference mismatch")
                context._idempotency[row["key"]] = InvocationResult(
                    receipt["operation_id"], copy.deepcopy(receipt["result"]), receipt, "persistent"
                )

    def persist_invocation(
        self,
        context: HHSAuthorityContext,
        invocation: InvocationResult,
        idempotency_key: str | None,
    ) -> int:
        receipt = dict(invocation.receipt)
        with self._condition, self._connection:
            existing = self._connection.execute(
                "SELECT receipt_index FROM receipts WHERE hash72 = ?", (receipt["hash72"],)
            ).fetchone()
            if existing:
                return int(existing["receipt_index"])
            self._connection.execute(
                "INSERT INTO receipts(receipt_index, hash72, predecessor_hash72, payload_json) VALUES(?,?,?,?)",
                (
                    receipt["receipt_index"],
                    receipt["hash72"],
                    receipt["predecessor_hash72"],
                    canonical_json(receipt),
                ),
            )
            if idempotency_key:
                self._connection.execute(
                    "INSERT OR REPLACE INTO idempotency(key, request_identity, receipt_hash72) VALUES(?,?,?)",
                    (idempotency_key, receipt["request_identity"], receipt["hash72"]),
                )
            meta = {
                "state": context._state,
                "state_root": context._state_root,
                "receipt_index": context._receipt_index,
                "last_hash72": context._last_hash72,
            }
            for key, value in meta.items():
                self._connection.execute(
                    "INSERT OR REPLACE INTO authority_meta(key, value_json) VALUES(?,?)",
                    (key, canonical_json(value)),
                )
            event = {
                "schema": "HHS_PASS_190_EVENT_V1",
                "event_type": "operation.admitted",
                "operation_id": invocation.operation_id,
                "receipt_index": receipt["receipt_index"],
                "hash72": receipt["hash72"],
                "hash216": receipt["hash216"],
                "state_after": receipt["state_after"],
            }
            cursor = self._connection.execute(
                "INSERT INTO events(event_type, payload_json) VALUES(?,?)",
                (event["event_type"], canonical_json(event)),
            )
            sequence = int(cursor.lastrowid)
            self._condition.notify_all()
            return sequence

    def append_event(self, event_type: str, payload: Mapping[str, Any]) -> int:
        event = {"schema": "HHS_PASS_190_EVENT_V1", "event_type": event_type, **dict(payload)}
        with self._condition, self._connection:
            cursor = self._connection.execute(
                "INSERT INTO events(event_type, payload_json) VALUES(?,?)",
                (event_type, canonical_json(event)),
            )
            sequence = int(cursor.lastrowid)
            self._condition.notify_all()
            return sequence

    def events_after(self, sequence: int, limit: int = 100) -> list[dict[str, Any]]:
        if sequence < 0 or limit < 1 or limit > 1000:
            raise PersistentStoreError("invalid event range")
        with self._lock:
            rows = self._connection.execute(
                "SELECT sequence, event_type, payload_json FROM events WHERE sequence > ? ORDER BY sequence LIMIT ?",
                (sequence, limit),
            ).fetchall()
            return [
                {"sequence": int(row["sequence"]), **json.loads(row["payload_json"])} for row in rows
            ]

    def wait_for_events(self, sequence: int, timeout: float = 15.0) -> list[dict[str, Any]]:
        deadline = time.monotonic() + timeout
        with self._condition:
            while True:
                events = self.events_after(sequence)
                if events:
                    return events
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return []
                self._condition.wait(min(remaining, 0.25))

    def receipts_after(self, receipt_index: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        if receipt_index < 0 or limit < 1 or limit > 1000:
            raise PersistentStoreError("invalid receipt range")
        with self._lock:
            rows = self._connection.execute(
                "SELECT payload_json FROM receipts WHERE receipt_index > ? ORDER BY receipt_index LIMIT ?",
                (receipt_index, limit),
            ).fetchall()
            return [json.loads(row["payload_json"]) for row in rows]

    def integrity_report(self) -> dict[str, Any]:
        probe = type("Probe", (), {})()
        probe._receipts = {}
        probe._receipt_index = 0
        probe._last_hash72 = "0" * 72
        probe._state = {"counter": 0}
        probe._state_root = hash72("pass190.state", probe._state)
        probe._idempotency = {}
        self.restore_into(probe)  # type: ignore[arg-type]
        return {
            "status": "ok",
            "classification": ITERATION2_CLASSIFICATION,
            "receipt_count": probe._receipt_index,
            "chain_head": probe._last_hash72,
            "state_root": probe._state_root,
            "event_count": self._connection.execute("SELECT COUNT(*) FROM events").fetchone()[0],
            "idempotency_count": self._connection.execute("SELECT COUNT(*) FROM idempotency").fetchone()[0],
        }


class PersistentAuthorityContext(HHSAuthorityContext):
    def __init__(self, database_path: Path | str = DEFAULT_DATABASE, registry_path: Path = DEFAULT_REGISTRY):
        self.store = SQLiteAuthorityStore(database_path)
        super().__init__(registry_path)
        self.store.restore_into(self)

    def close(self) -> None:
        self.store.close()

    def reset_for_tests(self) -> None:
        with self._lock:
            super().reset_for_tests()
            self.store.reset()

    def invoke(
        self,
        operation_id: str,
        arguments: Mapping[str, Any] | None = None,
        *,
        surface: str = "canonical",
        capabilities: Iterable[str] = (),
        idempotency_key: str | None = None,
        expected_state: str | None = None,
    ) -> InvocationResult:
        with self._lock:
            snapshot = {
                "receipt_index": self._receipt_index,
                "last_hash72": self._last_hash72,
                "receipts": copy.deepcopy(self._receipts),
                "idempotency": copy.deepcopy(self._idempotency),
                "state": copy.deepcopy(self._state),
                "state_root": self._state_root,
            }
            result = super().invoke(
                operation_id,
                arguments,
                surface=surface,
                capabilities=capabilities,
                idempotency_key=idempotency_key,
                expected_state=expected_state,
            )
            if self._receipt_index > snapshot["receipt_index"]:
                try:
                    self.store.persist_invocation(self, result, idempotency_key)
                except Exception:
                    self._receipt_index = snapshot["receipt_index"]
                    self._last_hash72 = snapshot["last_hash72"]
                    self._receipts = snapshot["receipts"]
                    self._idempotency = snapshot["idempotency"]
                    self._state = snapshot["state"]
                    self._state_root = snapshot["state_root"]
                    raise
            return result

    def replay(self, receipt_hash72: str) -> InvocationResult:
        with self._lock:
            result = super().replay(receipt_hash72)
            self.store.append_event(
                "operation.replayed",
                {"operation_id": result.operation_id, "hash72": receipt_hash72, "replay_verified": True},
            )
            return result

    def receipts_after(self, receipt_index: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.receipts_after(receipt_index, limit)

    def events_after(self, sequence: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.events_after(sequence, limit)

    def wait_for_events(self, sequence: int, timeout: float = 15.0) -> list[dict[str, Any]]:
        return self.store.wait_for_events(sequence, timeout)

    def integrity_report(self) -> dict[str, Any]:
        return self.store.integrity_report()


_CONTEXT: PersistentAuthorityContext | None = None
_CONTEXT_LOCK = threading.Lock()
_CONTEXT_PATH: Path | None = None


def get_iteration2_context(database_path: Path | str | None = None) -> PersistentAuthorityContext:
    global _CONTEXT, _CONTEXT_PATH
    requested = Path(database_path or DEFAULT_DATABASE)
    if _CONTEXT is None:
        with _CONTEXT_LOCK:
            if _CONTEXT is None:
                _CONTEXT = PersistentAuthorityContext(requested)
                _CONTEXT_PATH = requested
    elif _CONTEXT_PATH != requested:
        raise PersistentStoreError("process authority context already bound to another database")
    return _CONTEXT
