#!/usr/bin/env python3
"""Pass 190 Iteration 3 additive authenticated, fail-closed authority layer."""
from __future__ import annotations

import copy
import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any, Mapping

from hhs_pass190 import (
    DEFAULT_REGISTRY,
    HHSAuthorityContext,
    InvocationResult,
    canonical_json,
    hash72,
    hash216,
)
from hhs_pass190_iteration2 import (
    PersistentAuthorityContext,
    PersistentStoreError,
    SQLiteAuthorityStore,
)

HARDENING_CLASSIFICATION = "HHS_PASS_190_ITERATION_3_AUTHENTICATED_FAIL_CLOSED_AUTHORITY_VERIFIED"
DEFAULT_DATABASE = Path(os.environ.get("HHS_PASS190_DATABASE", "pass190-authority.sqlite3"))
GENESIS_STATE = {"counter": 0}
GENESIS_ROOT = hash72("pass190.state", GENESIS_STATE)
REQUIRED_META = {"state", "state_root", "receipt_index", "last_hash72"}


def event_hash72(sequence: int, event_type: str, payload: Mapping[str, Any]) -> str:
    return hash72(
        "pass190.event",
        {"sequence": sequence, "event_type": event_type, "payload": dict(payload)},
    )


class HardenedSQLiteAuthorityStore(SQLiteAuthorityStore):
    """SQLite authority that validates receipts, metadata, and event topology."""

    def _initialize(self) -> None:
        super()._initialize()
        with self._connection:
            columns = {row[1] for row in self._connection.execute("PRAGMA table_info(events)")}
            if "event_hash72" not in columns:
                self._connection.execute("ALTER TABLE events ADD COLUMN event_hash72 TEXT")
            rows = self._connection.execute(
                "SELECT sequence,event_type,payload_json,event_hash72 FROM events ORDER BY sequence"
            ).fetchall()
            for row in rows:
                if row["event_hash72"]:
                    continue
                try:
                    payload = json.loads(row["payload_json"])
                except json.JSONDecodeError as exc:
                    raise PersistentStoreError("cannot migrate invalid event payload") from exc
                self._connection.execute(
                    "UPDATE events SET event_hash72=? WHERE sequence=?",
                    (event_hash72(int(row["sequence"]), str(row["event_type"]), payload), int(row["sequence"])),
                )
            self._connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS events_hash72_unique ON events(event_hash72)"
            )

    def reset(self) -> None:
        with self._condition, self._connection:
            self._connection.executescript(
                "DELETE FROM idempotency; DELETE FROM receipts; DELETE FROM authority_meta; "
                "DELETE FROM events; DELETE FROM sqlite_sequence WHERE name='events';"
            )
            self._condition.notify_all()

    @staticmethod
    def _decode_receipt(
        row: sqlite3.Row,
        index: int,
        predecessor: str,
        state_root: str,
    ) -> tuple[dict[str, Any], str, str]:
        if int(row["receipt_index"]) != index:
            raise PersistentStoreError("receipt index discontinuity")
        try:
            receipt = json.loads(row["payload_json"])
        except json.JSONDecodeError as exc:
            raise PersistentStoreError("receipt payload is not valid JSON") from exc
        if not isinstance(receipt, dict) or receipt.get("receipt_index") != index:
            raise PersistentStoreError("receipt payload index mismatch")
        if row["predecessor_hash72"] != predecessor or receipt.get("predecessor_hash72") != predecessor:
            raise PersistentStoreError("receipt predecessor mismatch")
        if receipt.get("state_before") != state_root:
            raise PersistentStoreError("receipt state continuity mismatch")
        next_state = receipt.get("state_after")
        if not isinstance(next_state, str) or len(next_state) != 72:
            raise PersistentStoreError("receipt state root is invalid")
        payload = {key: value for key, value in receipt.items() if key not in {"hash72", "hash216"}}
        expected72 = hash72("pass190.receipt", payload)
        expected216 = hash216("pass190.receipt.topology", payload)
        if row["hash72"] != expected72 or receipt.get("hash72") != expected72:
            raise PersistentStoreError("receipt Hash72 mismatch")
        if receipt.get("hash216") != expected216:
            raise PersistentStoreError("receipt Hash216 mismatch")
        return receipt, expected72, next_state

    def _validated_receipts(self) -> tuple[dict[str, dict[str, Any]], str, str]:
        rows = self._connection.execute(
            "SELECT receipt_index,hash72,predecessor_hash72,payload_json FROM receipts ORDER BY receipt_index"
        ).fetchall()
        receipts: dict[str, dict[str, Any]] = {}
        predecessor = "0" * 72
        state_root = GENESIS_ROOT
        for index, row in enumerate(rows, 1):
            receipt, receipt_hash, state_root = self._decode_receipt(row, index, predecessor, state_root)
            receipts[receipt_hash] = receipt
            predecessor = receipt_hash
        return receipts, predecessor, state_root

    def _validated_meta(self, receipt_count: int, chain_head: str, final_state_root: str) -> dict[str, Any]:
        meta = self._meta()
        if not meta and receipt_count == 0:
            return {
                "state": copy.deepcopy(GENESIS_STATE),
                "state_root": GENESIS_ROOT,
                "receipt_index": 0,
                "last_hash72": "0" * 72,
            }
        missing = REQUIRED_META - set(meta)
        if missing:
            raise PersistentStoreError(f"incomplete authority metadata: {sorted(missing)}")
        state = meta["state"]
        if not isinstance(state, dict):
            raise PersistentStoreError("persisted state must be an object")
        if meta["state_root"] != hash72("pass190.state", state):
            raise PersistentStoreError("persisted state root mismatch")
        if meta["state_root"] != final_state_root:
            raise PersistentStoreError("persisted state does not match final receipt")
        if meta["receipt_index"] != receipt_count:
            raise PersistentStoreError("persisted receipt index mismatch")
        if meta["last_hash72"] != chain_head:
            raise PersistentStoreError("persisted chain head mismatch")
        return meta

    @staticmethod
    def _validated_event(
        sequence: int,
        event_type: str,
        payload: Any,
        supplied_hash: Any,
        receipts: Mapping[str, Mapping[str, Any]],
    ) -> dict[str, Any]:
        if not isinstance(payload, dict) or payload.get("schema") != "HHS_PASS_190_EVENT_V1":
            raise PersistentStoreError("event schema mismatch")
        if payload.get("event_type") != event_type:
            raise PersistentStoreError("event type mismatch")
        expected_hash = event_hash72(sequence, event_type, payload)
        if supplied_hash != expected_hash:
            raise PersistentStoreError("event Hash72 mismatch")
        receipt = receipts.get(payload.get("hash72"))
        if receipt is None:
            raise PersistentStoreError("event references an unknown receipt")
        if event_type == "operation.admitted":
            expected = {
                "operation_id": receipt["operation_id"],
                "receipt_index": receipt["receipt_index"],
                "hash216": receipt["hash216"],
                "state_after": receipt["state_after"],
            }
            for key, value in expected.items():
                if payload.get(key) != value:
                    raise PersistentStoreError(f"admitted event {key} mismatch")
        elif event_type == "operation.replayed":
            if payload.get("operation_id") != receipt["operation_id"] or payload.get("replay_verified") is not True:
                raise PersistentStoreError("replay event mismatch")
        else:
            raise PersistentStoreError("unsupported persisted event type")
        return {"sequence": sequence, "event_hash72": expected_hash, **payload}

    def _validated_events(self, receipts: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            "SELECT sequence,event_type,payload_json,event_hash72 FROM events ORDER BY sequence"
        ).fetchall()
        events: list[dict[str, Any]] = []
        admitted: set[str] = set()
        for expected_sequence, row in enumerate(rows, 1):
            sequence = int(row["sequence"])
            if sequence != expected_sequence:
                raise PersistentStoreError("event sequence discontinuity")
            try:
                payload = json.loads(row["payload_json"])
            except json.JSONDecodeError as exc:
                raise PersistentStoreError("event payload is not valid JSON") from exc
            event = self._validated_event(
                sequence, str(row["event_type"]), payload, row["event_hash72"], receipts
            )
            if event["event_type"] == "operation.admitted":
                receipt_hash = str(event["hash72"])
                if receipt_hash in admitted:
                    raise PersistentStoreError("duplicate admitted event")
                admitted.add(receipt_hash)
            events.append(event)
        if admitted != set(receipts):
            raise PersistentStoreError("receipt and admitted-event topology mismatch")
        return events

    def restore_into(self, context: HHSAuthorityContext) -> None:
        with self._lock:
            receipts, chain_head, final_state = self._validated_receipts()
            meta = self._validated_meta(len(receipts), chain_head, final_state)
            self._validated_events(receipts)
            context._receipts = receipts
            context._receipt_index = len(receipts)
            context._last_hash72 = chain_head
            context._state = copy.deepcopy(meta["state"])
            context._state_root = str(meta["state_root"])
            context._idempotency = {}
            for row in self._connection.execute(
                "SELECT key,request_identity,receipt_hash72 FROM idempotency ORDER BY key"
            ):
                receipt = receipts.get(row["receipt_hash72"])
                if receipt is None or receipt.get("request_identity") != row["request_identity"]:
                    raise PersistentStoreError("idempotency reference mismatch")
                context._idempotency[row["key"]] = InvocationResult(
                    receipt["operation_id"], copy.deepcopy(receipt["result"]), receipt, "persistent"
                )

    def _insert_event(self, event_type: str, payload: Mapping[str, Any]) -> int:
        event = {"schema": "HHS_PASS_190_EVENT_V1", "event_type": event_type, **dict(payload)}
        cursor = self._connection.execute(
            "INSERT INTO events(event_type,payload_json,event_hash72) VALUES(?,?,NULL)",
            (event_type, canonical_json(event)),
        )
        sequence = int(cursor.lastrowid)
        self._connection.execute(
            "UPDATE events SET event_hash72=? WHERE sequence=?",
            (event_hash72(sequence, event_type, event), sequence),
        )
        return sequence

    def persist_invocation(
        self,
        context: HHSAuthorityContext,
        invocation: InvocationResult,
        idempotency_key: str | None,
    ) -> int:
        receipt = dict(invocation.receipt)
        with self._condition, self._connection:
            existing = self._connection.execute(
                "SELECT receipt_index FROM receipts WHERE hash72=?", (receipt["hash72"],)
            ).fetchone()
            if existing:
                return int(existing["receipt_index"])
            self._connection.execute(
                "INSERT INTO receipts(receipt_index,hash72,predecessor_hash72,payload_json) VALUES(?,?,?,?)",
                (
                    receipt["receipt_index"], receipt["hash72"],
                    receipt["predecessor_hash72"], canonical_json(receipt),
                ),
            )
            if idempotency_key:
                self._connection.execute(
                    "INSERT OR REPLACE INTO idempotency(key,request_identity,receipt_hash72) VALUES(?,?,?)",
                    (idempotency_key, receipt["request_identity"], receipt["hash72"]),
                )
            for key, value in {
                "state": context._state,
                "state_root": context._state_root,
                "receipt_index": context._receipt_index,
                "last_hash72": context._last_hash72,
            }.items():
                self._connection.execute(
                    "INSERT OR REPLACE INTO authority_meta(key,value_json) VALUES(?,?)",
                    (key, canonical_json(value)),
                )
            sequence = self._insert_event(
                "operation.admitted",
                {
                    "operation_id": invocation.operation_id,
                    "receipt_index": receipt["receipt_index"],
                    "hash72": receipt["hash72"],
                    "hash216": receipt["hash216"],
                    "state_after": receipt["state_after"],
                },
            )
            self._condition.notify_all()
            return sequence

    def append_event(self, event_type: str, payload: Mapping[str, Any]) -> int:
        with self._condition, self._connection:
            sequence = self._insert_event(event_type, payload)
            self._condition.notify_all()
            return sequence

    def events_after(self, sequence: int, limit: int = 100) -> list[dict[str, Any]]:
        if sequence < 0 or limit < 1 or limit > 1000:
            raise PersistentStoreError("invalid event range")
        with self._lock:
            receipts, _head, _state = self._validated_receipts()
            rows = self._connection.execute(
                "SELECT sequence,event_type,payload_json,event_hash72 FROM events "
                "WHERE sequence>? ORDER BY sequence LIMIT ?",
                (sequence, limit),
            ).fetchall()
            events: list[dict[str, Any]] = []
            for row in rows:
                try:
                    payload = json.loads(row["payload_json"])
                except json.JSONDecodeError as exc:
                    raise PersistentStoreError("event payload is not valid JSON") from exc
                events.append(self._validated_event(
                    int(row["sequence"]), str(row["event_type"]), payload,
                    row["event_hash72"], receipts,
                ))
            return events

    def integrity_report(self) -> dict[str, Any]:
        probe = type("Probe", (), {})()
        probe._receipts, probe._idempotency = {}, {}
        probe._receipt_index, probe._last_hash72 = 0, "0" * 72
        probe._state, probe._state_root = copy.deepcopy(GENESIS_STATE), GENESIS_ROOT
        self.restore_into(probe)  # type: ignore[arg-type]
        return {
            "status": "ok",
            "classification": HARDENING_CLASSIFICATION,
            "receipt_count": probe._receipt_index,
            "chain_head": probe._last_hash72,
            "state_root": probe._state_root,
            "event_count": int(self._connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]),
            "idempotency_count": int(self._connection.execute("SELECT COUNT(*) FROM idempotency").fetchone()[0]),
            "metadata_complete": True,
            "events_verified": True,
        }


class HardenedAuthorityContext(PersistentAuthorityContext):
    """Iteration 2 semantics using the fail-closed Iteration 3 persistence layer."""

    def __init__(
        self,
        database_path: Path | str = DEFAULT_DATABASE,
        registry_path: Path = DEFAULT_REGISTRY,
    ):
        self.store = HardenedSQLiteAuthorityStore(database_path)
        HHSAuthorityContext.__init__(self, registry_path)
        self.store.restore_into(self)


_CONTEXT: HardenedAuthorityContext | None = None
_CONTEXT_LOCK = threading.Lock()
_CONTEXT_PATH: Path | None = None


def get_hardened_context(database_path: Path | str | None = None) -> HardenedAuthorityContext:
    global _CONTEXT, _CONTEXT_PATH
    requested = Path(database_path or DEFAULT_DATABASE)
    if _CONTEXT is None:
        with _CONTEXT_LOCK:
            if _CONTEXT is None:
                _CONTEXT = HardenedAuthorityContext(requested)
                _CONTEXT_PATH = requested
    elif _CONTEXT_PATH != requested:
        raise PersistentStoreError("process authority context already bound to another database")
    return _CONTEXT
