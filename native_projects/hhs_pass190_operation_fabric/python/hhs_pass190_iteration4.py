#!/usr/bin/env python3
"""Pass 190 Iteration 4: distributed singleton admission with durable fencing."""
from __future__ import annotations

import copy
import json
import os
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Mapping

from hhs_pass190 import (
    CLASSIFICATION,
    CONTRACT_ID,
    DEFAULT_REGISTRY,
    HHSAuthorityContext,
    InvocationResult,
    ReplayMismatchError,
    canonical_json,
    hash72,
    hash216,
)
from hhs_pass190_iteration2 import PersistentStoreError
from hhs_pass190_iteration3_hardening import (
    DEFAULT_DATABASE,
    HardenedAuthorityContext,
    HardenedSQLiteAuthorityStore,
)

ITERATION4_CLASSIFICATION = "HHS_PASS_190_ITERATION_4_DISTRIBUTED_SINGLETON_FENCED_AUTHORITY_VERIFIED"
DEFAULT_LEASE_TTL_NS = int(os.environ.get("HHS_PASS190_LEASE_TTL_NS", "30000000000"))
DEFAULT_LEASE_WAIT_NS = int(os.environ.get("HHS_PASS190_LEASE_WAIT_NS", "5000000000"))
ARBITRATION_KEY = "pass190.singleton.vm81"


class LeaseBusyError(PersistentStoreError):
    """Another process currently owns the singleton admission lease."""


class StaleFenceError(PersistentStoreError):
    """A candidate was produced under a superseded or expired fencing token."""


@dataclass(frozen=True)
class LeaseGrant:
    holder_id: str
    fencing_token: int
    acquired_ns: int
    expires_ns: int


class DistributedAuthorityStore(HardenedSQLiteAuthorityStore):
    """Hardened SQLite authority with a durable process lease and fence ledger."""

    def __init__(
        self,
        path: Path | str,
        *,
        clock_ns: Callable[[], int] = time.time_ns,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        self._clock_ns = clock_ns
        self._sleeper = sleeper
        super().__init__(path)
        self._connection.execute("PRAGMA busy_timeout=1000")

    def _initialize(self) -> None:
        super()._initialize()
        with self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS authority_lease (
                    singleton_key TEXT PRIMARY KEY,
                    holder_id TEXT NOT NULL,
                    fencing_token INTEGER NOT NULL,
                    acquired_ns INTEGER NOT NULL,
                    expires_ns INTEGER NOT NULL,
                    released_ns INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS authority_fences (
                    receipt_hash72 TEXT PRIMARY KEY,
                    receipt_index INTEGER NOT NULL UNIQUE,
                    holder_id TEXT NOT NULL,
                    fencing_token INTEGER NOT NULL UNIQUE,
                    acquired_ns INTEGER NOT NULL,
                    committed_ns INTEGER NOT NULL,
                    expires_ns INTEGER NOT NULL,
                    predecessor_hash72 TEXT NOT NULL,
                    state_before TEXT NOT NULL,
                    state_after TEXT NOT NULL,
                    legacy_migration INTEGER NOT NULL CHECK(legacy_migration IN (0,1)),
                    fence_hash72 TEXT NOT NULL UNIQUE,
                    FOREIGN KEY(receipt_hash72) REFERENCES receipts(hash72)
                );
                """
            )
            rows = self._connection.execute(
                "SELECT receipt_index,hash72,predecessor_hash72,payload_json FROM receipts ORDER BY receipt_index"
            ).fetchall()
            for row in rows:
                if self._connection.execute(
                    "SELECT 1 FROM authority_fences WHERE receipt_hash72=?", (row["hash72"],)
                ).fetchone():
                    continue
                receipt = json.loads(row["payload_json"])
                payload = {
                    "schema": "HHS_PASS_190_FENCE_V1",
                    "receipt_hash72": row["hash72"],
                    "receipt_index": int(row["receipt_index"]),
                    "holder_id": "iteration3-migration",
                    "fencing_token": int(row["receipt_index"]),
                    "acquired_ns": 0,
                    "committed_ns": 0,
                    "expires_ns": 0,
                    "predecessor_hash72": row["predecessor_hash72"],
                    "state_before": receipt["state_before"],
                    "state_after": receipt["state_after"],
                    "legacy_migration": True,
                }
                self._connection.execute(
                    "INSERT INTO authority_fences(receipt_hash72,receipt_index,holder_id,fencing_token,"
                    "acquired_ns,committed_ns,expires_ns,predecessor_hash72,state_before,state_after,"
                    "legacy_migration,fence_hash72) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        payload["receipt_hash72"], payload["receipt_index"], payload["holder_id"],
                        payload["fencing_token"], payload["acquired_ns"], payload["committed_ns"],
                        payload["expires_ns"], payload["predecessor_hash72"], payload["state_before"],
                        payload["state_after"], 1, hash72("pass190.fence", payload),
                    ),
                )

    def reset(self) -> None:
        with self._condition, self._connection:
            self._connection.executescript(
                "DELETE FROM authority_fences; DELETE FROM authority_lease; DELETE FROM idempotency; "
                "DELETE FROM receipts; DELETE FROM authority_meta; DELETE FROM events; "
                "DELETE FROM sqlite_sequence WHERE name='events';"
            )
            self._condition.notify_all()

    def _begin_immediate(self) -> None:
        self._connection.execute("BEGIN IMMEDIATE")

    def acquire_lease(
        self,
        holder_id: str,
        *,
        ttl_ns: int = DEFAULT_LEASE_TTL_NS,
        wait_ns: int = DEFAULT_LEASE_WAIT_NS,
    ) -> LeaseGrant:
        if not holder_id or len(holder_id) > 256:
            raise PersistentStoreError("invalid authority holder identity")
        if ttl_ns < 1 or wait_ns < 0:
            raise PersistentStoreError("invalid lease timing")
        deadline = time.monotonic_ns() + wait_ns
        while True:
            now = self._clock_ns()
            with self._lock:
                try:
                    self._begin_immediate()
                    row = self._connection.execute(
                        "SELECT holder_id,fencing_token,expires_ns FROM authority_lease WHERE singleton_key=?",
                        (ARBITRATION_KEY,),
                    ).fetchone()
                    highest = int(self._connection.execute(
                        "SELECT COALESCE(MAX(fencing_token),0) FROM authority_fences"
                    ).fetchone()[0])
                    available = row is None or int(row["expires_ns"]) <= now
                    if available:
                        previous = 0 if row is None else int(row["fencing_token"])
                        token = max(previous, highest) + 1
                        expires = now + ttl_ns
                        self._connection.execute(
                            "INSERT INTO authority_lease(singleton_key,holder_id,fencing_token,acquired_ns,"
                            "expires_ns,released_ns) VALUES(?,?,?,?,?,0) ON CONFLICT(singleton_key) DO UPDATE SET "
                            "holder_id=excluded.holder_id,fencing_token=excluded.fencing_token,"
                            "acquired_ns=excluded.acquired_ns,expires_ns=excluded.expires_ns,released_ns=0",
                            (ARBITRATION_KEY, holder_id, token, now, expires),
                        )
                        self._connection.commit()
                        return LeaseGrant(holder_id, token, now, expires)
                    self._connection.rollback()
                except sqlite3.Error:
                    self._connection.rollback()
                    raise
            if time.monotonic_ns() >= deadline:
                raise LeaseBusyError("singleton VM81 authority lease is currently held")
            self._sleeper(0.01)

    def _verify_grant(self, grant: LeaseGrant, *, require_live: bool = True) -> sqlite3.Row:
        row = self._connection.execute(
            "SELECT holder_id,fencing_token,acquired_ns,expires_ns,released_ns FROM authority_lease "
            "WHERE singleton_key=?",
            (ARBITRATION_KEY,),
        ).fetchone()
        if row is None:
            raise StaleFenceError("authority lease is absent")
        if row["holder_id"] != grant.holder_id or int(row["fencing_token"]) != grant.fencing_token:
            raise StaleFenceError("authority fencing token has been superseded")
        if require_live and (int(row["expires_ns"]) <= self._clock_ns() or int(row["released_ns"]) != 0):
            raise StaleFenceError("authority lease expired before commit")
        return row

    @contextmanager
    def admission(self, grant: LeaseGrant) -> Iterator[None]:
        with self._lock:
            try:
                self._begin_immediate()
                self._verify_grant(grant)
                yield
                self._verify_grant(grant)
                released = self._clock_ns()
                self._connection.execute(
                    "UPDATE authority_lease SET expires_ns=0,released_ns=? WHERE singleton_key=? "
                    "AND holder_id=? AND fencing_token=?",
                    (released, ARBITRATION_KEY, grant.holder_id, grant.fencing_token),
                )
                self._connection.commit()
                self._condition.notify_all()
            except Exception:
                self._connection.rollback()
                self._release_after_failure(grant)
                raise

    def _release_after_failure(self, grant: LeaseGrant) -> None:
        try:
            self._begin_immediate()
            row = self._connection.execute(
                "SELECT holder_id,fencing_token FROM authority_lease WHERE singleton_key=?",
                (ARBITRATION_KEY,),
            ).fetchone()
            if row and row["holder_id"] == grant.holder_id and int(row["fencing_token"]) == grant.fencing_token:
                self._connection.execute(
                    "UPDATE authority_lease SET expires_ns=0,released_ns=? WHERE singleton_key=?",
                    (self._clock_ns(), ARBITRATION_KEY),
                )
            self._connection.commit()
        except sqlite3.Error:
            self._connection.rollback()

    def persist_fenced_invocation(
        self,
        context: HHSAuthorityContext,
        invocation: InvocationResult,
        idempotency_key: str | None,
        grant: LeaseGrant,
    ) -> int:
        self._verify_grant(grant)
        receipt = dict(invocation.receipt)
        persisted_head = self._connection.execute(
            "SELECT value_json FROM authority_meta WHERE key='last_hash72'"
        ).fetchone()
        current_head = "0" * 72 if persisted_head is None else json.loads(persisted_head[0])
        persisted_index = self._connection.execute("SELECT COUNT(*) FROM receipts").fetchone()[0]
        if receipt["predecessor_hash72"] != current_head:
            raise StaleFenceError("candidate predecessor no longer matches durable chain head")
        if int(receipt["receipt_index"]) != int(persisted_index) + 1:
            raise StaleFenceError("candidate receipt index no longer follows durable authority")
        self._connection.execute(
            "INSERT INTO receipts(receipt_index,hash72,predecessor_hash72,payload_json) VALUES(?,?,?,?)",
            (
                receipt["receipt_index"], receipt["hash72"], receipt["predecessor_hash72"],
                canonical_json(receipt),
            ),
        )
        if idempotency_key:
            self._connection.execute(
                "INSERT INTO idempotency(key,request_identity,receipt_hash72) VALUES(?,?,?)",
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
        committed = self._clock_ns()
        fence_payload = {
            "schema": "HHS_PASS_190_FENCE_V1",
            "receipt_hash72": receipt["hash72"],
            "receipt_index": receipt["receipt_index"],
            "holder_id": grant.holder_id,
            "fencing_token": grant.fencing_token,
            "acquired_ns": grant.acquired_ns,
            "committed_ns": committed,
            "expires_ns": grant.expires_ns,
            "predecessor_hash72": receipt["predecessor_hash72"],
            "state_before": receipt["state_before"],
            "state_after": receipt["state_after"],
            "legacy_migration": False,
        }
        fence_hash = hash72("pass190.fence", fence_payload)
        self._connection.execute(
            "INSERT INTO authority_fences(receipt_hash72,receipt_index,holder_id,fencing_token,"
            "acquired_ns,committed_ns,expires_ns,predecessor_hash72,state_before,state_after,"
            "legacy_migration,fence_hash72) VALUES(?,?,?,?,?,?,?,?,?,?,0,?)",
            (
                receipt["hash72"], receipt["receipt_index"], grant.holder_id, grant.fencing_token,
                grant.acquired_ns, committed, grant.expires_ns, receipt["predecessor_hash72"],
                receipt["state_before"], receipt["state_after"], fence_hash,
            ),
        )
        event = {
            "schema": "HHS_PASS_190_EVENT_V1",
            "event_type": "operation.admitted",
            "operation_id": invocation.operation_id,
            "receipt_index": receipt["receipt_index"],
            "hash72": receipt["hash72"],
            "hash216": receipt["hash216"],
            "state_after": receipt["state_after"],
            "fencing_token": grant.fencing_token,
            "fence_hash72": fence_hash,
        }
        cursor = self._connection.execute(
            "INSERT INTO events(event_type,payload_json,event_hash72) VALUES(?,?,NULL)",
            (event["event_type"], canonical_json(event)),
        )
        sequence = int(cursor.lastrowid)
        self._connection.execute(
            "UPDATE events SET event_hash72=? WHERE sequence=?",
            (hash72("pass190.event", {"sequence": sequence, "event_type": event["event_type"], "payload": event}), sequence),
        )
        return sequence

    def append_fenced_event(self, event_type: str, payload: Mapping[str, Any], grant: LeaseGrant) -> int:
        self._verify_grant(grant)
        event = {
            "schema": "HHS_PASS_190_EVENT_V1",
            "event_type": event_type,
            **dict(payload),
            "fencing_token": grant.fencing_token,
        }
        cursor = self._connection.execute(
            "INSERT INTO events(event_type,payload_json,event_hash72) VALUES(?,?,NULL)",
            (event_type, canonical_json(event)),
        )
        sequence = int(cursor.lastrowid)
        self._connection.execute(
            "UPDATE events SET event_hash72=? WHERE sequence=?",
            (hash72("pass190.event", {"sequence": sequence, "event_type": event_type, "payload": event}), sequence),
        )
        return sequence

    def restore_into(self, context: HHSAuthorityContext) -> None:
        super().restore_into(context)
        self._validate_fences(context._receipts)

    def _validate_fences(self, receipts: Mapping[str, Mapping[str, Any]]) -> None:
        rows = self._connection.execute(
            "SELECT * FROM authority_fences ORDER BY receipt_index"
        ).fetchall()
        if len(rows) != len(receipts):
            raise PersistentStoreError("receipt and fencing witness counts disagree")
        previous_token = 0
        for row in rows:
            receipt = receipts.get(row["receipt_hash72"])
            if receipt is None:
                raise PersistentStoreError("fencing witness references unknown receipt")
            token = int(row["fencing_token"])
            if token <= previous_token:
                raise PersistentStoreError("fencing tokens are not strictly increasing")
            previous_token = token
            payload = {
                "schema": "HHS_PASS_190_FENCE_V1",
                "receipt_hash72": row["receipt_hash72"],
                "receipt_index": int(row["receipt_index"]),
                "holder_id": row["holder_id"],
                "fencing_token": token,
                "acquired_ns": int(row["acquired_ns"]),
                "committed_ns": int(row["committed_ns"]),
                "expires_ns": int(row["expires_ns"]),
                "predecessor_hash72": row["predecessor_hash72"],
                "state_before": row["state_before"],
                "state_after": row["state_after"],
                "legacy_migration": bool(row["legacy_migration"]),
            }
            if row["fence_hash72"] != hash72("pass190.fence", payload):
                raise PersistentStoreError("fencing witness Hash72 mismatch")
            if int(row["receipt_index"]) != receipt["receipt_index"]:
                raise PersistentStoreError("fencing receipt index mismatch")
            if row["predecessor_hash72"] != receipt["predecessor_hash72"]:
                raise PersistentStoreError("fencing predecessor mismatch")
            if row["state_before"] != receipt["state_before"] or row["state_after"] != receipt["state_after"]:
                raise PersistentStoreError("fencing state topology mismatch")

    def arbitration_report(self) -> dict[str, Any]:
        with self._lock:
            row = self._connection.execute(
                "SELECT holder_id,fencing_token,acquired_ns,expires_ns,released_ns FROM authority_lease "
                "WHERE singleton_key=?",
                (ARBITRATION_KEY,),
            ).fetchone()
            fence_count = int(self._connection.execute("SELECT COUNT(*) FROM authority_fences").fetchone()[0])
            highest = int(self._connection.execute(
                "SELECT COALESCE(MAX(fencing_token),0) FROM authority_fences"
            ).fetchone()[0])
            now = self._clock_ns()
            active = bool(row and int(row["released_ns"]) == 0 and int(row["expires_ns"]) > now)
            return {
                "schema": "HHS_PASS_190_ARBITRATION_STATUS_V1",
                "classification": ITERATION4_CLASSIFICATION,
                "singleton_key": ARBITRATION_KEY,
                "active": active,
                "holder_id": row["holder_id"] if active else None,
                "fencing_token": int(row["fencing_token"]) if row else highest,
                "lease_expires_ns": int(row["expires_ns"]) if active else 0,
                "fence_count": fence_count,
                "highest_committed_fence": highest,
            }

    def integrity_report(self) -> dict[str, Any]:
        report = super().integrity_report()
        arbitration = self.arbitration_report()
        return {
            **report,
            "classification": ITERATION4_CLASSIFICATION,
            "distributed_singleton_verified": True,
            "fence_count": arbitration["fence_count"],
            "highest_committed_fence": arbitration["highest_committed_fence"],
            "lease_active": arbitration["active"],
        }


class DistributedAuthorityContext(HardenedAuthorityContext):
    """One durable VM81 admission authority shared safely by multiple processes."""

    def __init__(
        self,
        database_path: Path | str = DEFAULT_DATABASE,
        registry_path: Path = DEFAULT_REGISTRY,
        *,
        holder_id: str | None = None,
        lease_ttl_ns: int = DEFAULT_LEASE_TTL_NS,
        lease_wait_ns: int = DEFAULT_LEASE_WAIT_NS,
        clock_ns: Callable[[], int] = time.time_ns,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        self.holder_id = holder_id or f"{os.getpid()}:{uuid.uuid4().hex}"
        self.lease_ttl_ns = lease_ttl_ns
        self.lease_wait_ns = lease_wait_ns
        self.store = DistributedAuthorityStore(database_path, clock_ns=clock_ns, sleeper=sleeper)
        HHSAuthorityContext.__init__(self, registry_path)
        self.store.restore_into(self)

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
            grant = self.store.acquire_lease(
                self.holder_id, ttl_ns=self.lease_ttl_ns, wait_ns=self.lease_wait_ns
            )
            try:
                with self.store.admission(grant):
                    self.store.restore_into(self)
                    before_index = self._receipt_index
                    result = HHSAuthorityContext.invoke(
                        self,
                        operation_id,
                        arguments,
                        surface=surface,
                        capabilities=capabilities,
                        idempotency_key=idempotency_key,
                        expected_state=expected_state,
                    )
                    if self._receipt_index > before_index:
                        self.store.persist_fenced_invocation(self, result, idempotency_key, grant)
                    return result
            except Exception:
                self.store.restore_into(self)
                raise

    def replay(self, receipt_hash72: str) -> InvocationResult:
        with self._lock:
            grant = self.store.acquire_lease(
                self.holder_id, ttl_ns=self.lease_ttl_ns, wait_ns=self.lease_wait_ns
            )
            try:
                with self.store.admission(grant):
                    self.store.restore_into(self)
                    receipt = self._receipts.get(receipt_hash72)
                    if receipt is None:
                        raise ReplayMismatchError("unknown receipt")
                    if receipt["operation_id"] == "system.status":
                        expected = copy.deepcopy(receipt["result"])
                        recomputed = {
                            "status": "ok",
                            "classification": CLASSIFICATION,
                            "contract": CONTRACT_ID,
                            "operations": len(self.registry.records),
                            "state_root": receipt["state_before"],
                            "receipt_index": receipt["receipt_index"] - 1,
                        }
                        if recomputed != expected:
                            raise ReplayMismatchError("semantic replay mismatch")
                        payload = {key: value for key, value in receipt.items() if key not in {"hash72", "hash216"}}
                        if hash72("pass190.receipt", payload) != receipt["hash72"]:
                            raise ReplayMismatchError("Hash72 replay mismatch")
                        if hash216("pass190.receipt.topology", payload) != receipt["hash216"]:
                            raise ReplayMismatchError("Hash216 replay mismatch")
                        result = InvocationResult("system.status", expected, receipt, "replay", True)
                    else:
                        result = HHSAuthorityContext.replay(self, receipt_hash72)
                    self.store.append_fenced_event(
                        "operation.replayed",
                        {"operation_id": result.operation_id, "hash72": receipt_hash72, "replay_verified": True},
                        grant,
                    )
                    return result
            except Exception:
                self.store.restore_into(self)
                raise

    def arbitration_report(self) -> dict[str, Any]:
        return self.store.arbitration_report()


_CONTEXT: DistributedAuthorityContext | None = None
_CONTEXT_LOCK = threading.Lock()
_CONTEXT_PATH: Path | None = None


def get_iteration4_context(database_path: Path | str | None = None) -> DistributedAuthorityContext:
    global _CONTEXT, _CONTEXT_PATH
    requested = Path(database_path or DEFAULT_DATABASE)
    if _CONTEXT is None:
        with _CONTEXT_LOCK:
            if _CONTEXT is None:
                _CONTEXT = DistributedAuthorityContext(requested)
                _CONTEXT_PATH = requested
    elif _CONTEXT_PATH != requested:
        raise PersistentStoreError("process authority context already bound to another database")
    return _CONTEXT
