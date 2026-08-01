#!/usr/bin/env python3
"""Pass 190 Iteration 5: atomic lease receipts and kernel-authority fencing."""
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

from hhs_pass190 import DEFAULT_REGISTRY, HHSAuthorityContext, InvocationResult, canonical_json, hash72
from hhs_pass190_iteration2 import PersistentStoreError
from hhs_pass190_iteration3_hardening import DEFAULT_DATABASE, HardenedSQLiteAuthorityStore
from hhs_pass190_iteration4 import (
    ARBITRATION_KEY,
    DEFAULT_LEASE_TTL_NS,
    DEFAULT_LEASE_WAIT_NS,
    DistributedAuthorityContext,
    DistributedAuthorityStore,
    LeaseBusyError,
    LeaseGrant,
    StaleFenceError,
)

ITERATION5_CLASSIFICATION = "HHS_PASS_190_ITERATION_5_ATOMIC_KERNEL_AUTHORITY_CORRECTNESS_VERIFIED"
LEASE_RECEIPT_SCHEMA = "HHS_PASS_190_LEASE_TRANSITION_RECEIPT_V1"
KERNEL_AUTHORITY_SCHEMA = "HHS_PASS_190_KERNEL_AUTHORITY_V1"
LEASE_TRANSITIONS = {"MIGRATED", "ACQUIRED", "RELEASED", "FAILED_RELEASED", "EXPIRED"}


@dataclass(frozen=True)
class KernelLeaseGrant(LeaseGrant):
    acquire_receipt_hash72: str


class CorrectedAuthorityStore(DistributedAuthorityStore):
    """Iteration 4 authority with atomic snapshots and a lease-transition receipt chain."""

    def _initialize(self) -> None:
        # Do not invoke Iteration 4 migration: validate inherited receipts first.
        HardenedSQLiteAuthorityStore._initialize(self)
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
                CREATE TABLE IF NOT EXISTS authority_lease_receipts (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    singleton_key TEXT NOT NULL,
                    transition TEXT NOT NULL,
                    holder_id TEXT NOT NULL,
                    fencing_token INTEGER NOT NULL,
                    observed_ns INTEGER NOT NULL,
                    acquired_ns INTEGER NOT NULL,
                    expires_ns INTEGER NOT NULL,
                    released_ns INTEGER NOT NULL,
                    predecessor_hash72 TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    receipt_hash72 TEXT NOT NULL UNIQUE,
                    UNIQUE(fencing_token, transition)
                );
                """
            )
            columns = {row[1] for row in self._connection.execute("PRAGMA table_info(authority_fences)")}
            if "lease_acquire_hash72" not in columns:
                self._connection.execute("ALTER TABLE authority_fences ADD COLUMN lease_acquire_hash72 TEXT")
            if "kernel_authority_hash72" not in columns:
                self._connection.execute("ALTER TABLE authority_fences ADD COLUMN kernel_authority_hash72 TEXT")

            receipts, chain_head, final_state = self._validated_receipts()
            self._validated_meta(len(receipts), chain_head, final_state)
            self._validated_events(receipts)

            # Only validated inherited receipts may receive migration fences.
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

            # Validate inherited Iteration 4 witnesses before extending them.
            DistributedAuthorityStore._validate_fences(self, receipts)
            self._backfill_kernel_authority(receipts)
            self._validate_lease_receipts()
            self._validate_kernel_fences(receipts)
            self._validate_kernel_events()

    def reset(self) -> None:
        with self._condition, self._connection:
            self._connection.executescript(
                "DELETE FROM authority_lease_receipts; DELETE FROM authority_fences; "
                "DELETE FROM authority_lease; DELETE FROM idempotency; DELETE FROM receipts; "
                "DELETE FROM authority_meta; DELETE FROM events; "
                "DELETE FROM sqlite_sequence WHERE name IN ('events','authority_lease_receipts');"
            )
            self._condition.notify_all()

    @staticmethod
    def _is_lock_error(exc: sqlite3.OperationalError) -> bool:
        text = str(exc).lower()
        return "locked" in text or "busy" in text

    def _rollback_if_needed(self) -> None:
        if self._connection.in_transaction:
            self._connection.rollback()

    def _begin_immediate_until(self, deadline_ns: int) -> None:
        while True:
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                return
            except sqlite3.OperationalError as exc:
                self._rollback_if_needed()
                if not self._is_lock_error(exc) or time.monotonic_ns() >= deadline_ns:
                    if self._is_lock_error(exc):
                        raise LeaseBusyError("SQLite authority remained locked beyond bounded wait") from exc
                    raise
                self._sleeper(0.01)

    def _highest_token(self) -> int:
        values = [
            int(self._connection.execute("SELECT COALESCE(MAX(fencing_token),0) FROM authority_fences").fetchone()[0]),
            int(self._connection.execute("SELECT COALESCE(MAX(fencing_token),0) FROM authority_lease_receipts").fetchone()[0]),
        ]
        row = self._connection.execute(
            "SELECT fencing_token FROM authority_lease WHERE singleton_key=?", (ARBITRATION_KEY,)
        ).fetchone()
        if row:
            values.append(int(row[0]))
        return max(values)

    def _append_lease_receipt(
        self,
        transition: str,
        *,
        holder_id: str,
        fencing_token: int,
        observed_ns: int,
        acquired_ns: int,
        expires_ns: int,
        released_ns: int,
    ) -> str:
        if transition not in LEASE_TRANSITIONS:
            raise PersistentStoreError("unsupported lease transition")
        existing = self._connection.execute(
            "SELECT receipt_hash72 FROM authority_lease_receipts WHERE fencing_token=? AND transition=?",
            (fencing_token, transition),
        ).fetchone()
        if existing:
            return str(existing[0])
        previous = self._connection.execute(
            "SELECT receipt_hash72 FROM authority_lease_receipts ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        predecessor = "0" * 72 if previous is None else str(previous[0])
        payload = {
            "schema": LEASE_RECEIPT_SCHEMA,
            "singleton_key": ARBITRATION_KEY,
            "transition": transition,
            "holder_id": holder_id,
            "fencing_token": fencing_token,
            "observed_ns": observed_ns,
            "acquired_ns": acquired_ns,
            "expires_ns": expires_ns,
            "released_ns": released_ns,
            "predecessor_hash72": predecessor,
        }
        receipt_hash = hash72("pass190.lease.transition", payload)
        self._connection.execute(
            "INSERT INTO authority_lease_receipts(singleton_key,transition,holder_id,fencing_token,"
            "observed_ns,acquired_ns,expires_ns,released_ns,predecessor_hash72,payload_json,receipt_hash72) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                ARBITRATION_KEY, transition, holder_id, fencing_token, observed_ns, acquired_ns,
                expires_ns, released_ns, predecessor, canonical_json(payload), receipt_hash,
            ),
        )
        return receipt_hash

    def _settle_expired_locked(self, now: int) -> None:
        row = self._connection.execute(
            "SELECT holder_id,fencing_token,acquired_ns,expires_ns,released_ns FROM authority_lease "
            "WHERE singleton_key=?",
            (ARBITRATION_KEY,),
        ).fetchone()
        if row is None or int(row["released_ns"]) != 0 or int(row["expires_ns"]) > now:
            return
        self._append_lease_receipt(
            "EXPIRED",
            holder_id=str(row["holder_id"]),
            fencing_token=int(row["fencing_token"]),
            observed_ns=now,
            acquired_ns=int(row["acquired_ns"]),
            expires_ns=int(row["expires_ns"]),
            released_ns=now,
        )
        self._connection.execute(
            "UPDATE authority_lease SET expires_ns=0,released_ns=? WHERE singleton_key=?",
            (now, ARBITRATION_KEY),
        )

    def acquire_lease(
        self,
        holder_id: str,
        *,
        ttl_ns: int = DEFAULT_LEASE_TTL_NS,
        wait_ns: int = DEFAULT_LEASE_WAIT_NS,
    ) -> KernelLeaseGrant:
        if not holder_id or len(holder_id) > 256:
            raise PersistentStoreError("invalid authority holder identity")
        if ttl_ns < 1 or wait_ns < 0:
            raise PersistentStoreError("invalid lease timing")
        deadline = time.monotonic_ns() + wait_ns
        while True:
            now = self._clock_ns()
            with self._lock:
                try:
                    self._begin_immediate_until(deadline)
                    self._settle_expired_locked(now)
                    row = self._connection.execute(
                        "SELECT holder_id,fencing_token,expires_ns,released_ns FROM authority_lease "
                        "WHERE singleton_key=?",
                        (ARBITRATION_KEY,),
                    ).fetchone()
                    available = row is None or int(row["released_ns"]) != 0 or int(row["expires_ns"]) <= now
                    if available:
                        token = self._highest_token() + 1
                        expires = now + ttl_ns
                        self._connection.execute(
                            "INSERT INTO authority_lease(singleton_key,holder_id,fencing_token,acquired_ns,"
                            "expires_ns,released_ns) VALUES(?,?,?,?,?,0) ON CONFLICT(singleton_key) DO UPDATE SET "
                            "holder_id=excluded.holder_id,fencing_token=excluded.fencing_token,"
                            "acquired_ns=excluded.acquired_ns,expires_ns=excluded.expires_ns,released_ns=0",
                            (ARBITRATION_KEY, holder_id, token, now, expires),
                        )
                        acquire_hash = self._append_lease_receipt(
                            "ACQUIRED", holder_id=holder_id, fencing_token=token, observed_ns=now,
                            acquired_ns=now, expires_ns=expires, released_ns=0,
                        )
                        self._connection.commit()
                        return KernelLeaseGrant(holder_id, token, now, expires, acquire_hash)
                    self._connection.rollback()
                except LeaseBusyError:
                    self._rollback_if_needed()
                    raise
                except sqlite3.OperationalError as exc:
                    self._rollback_if_needed()
                    if not self._is_lock_error(exc):
                        raise
            if time.monotonic_ns() >= deadline:
                raise LeaseBusyError("singleton VM81 authority lease is currently held")
            self._sleeper(0.01)

    def _verify_kernel_grant(self, grant: KernelLeaseGrant) -> None:
        self._verify_grant(grant)
        row = self._connection.execute(
            "SELECT payload_json,receipt_hash72 FROM authority_lease_receipts "
            "WHERE fencing_token=? AND transition='ACQUIRED'",
            (grant.fencing_token,),
        ).fetchone()
        if row is None or row["receipt_hash72"] != grant.acquire_receipt_hash72:
            raise StaleFenceError("lease acquisition receipt is absent or superseded")
        payload = json.loads(row["payload_json"])
        if payload["holder_id"] != grant.holder_id or payload["expires_ns"] != grant.expires_ns:
            raise StaleFenceError("lease acquisition receipt does not match the grant")

    @contextmanager
    def admission(self, grant: KernelLeaseGrant) -> Iterator[None]:
        deadline = time.monotonic_ns() + DEFAULT_LEASE_WAIT_NS
        with self._lock:
            try:
                self._begin_immediate_until(deadline)
                self._verify_kernel_grant(grant)
                yield
                self._verify_kernel_grant(grant)
                released = self._clock_ns()
                self._append_lease_receipt(
                    "RELEASED", holder_id=grant.holder_id, fencing_token=grant.fencing_token,
                    observed_ns=released, acquired_ns=grant.acquired_ns, expires_ns=grant.expires_ns,
                    released_ns=released,
                )
                self._connection.execute(
                    "UPDATE authority_lease SET expires_ns=0,released_ns=? WHERE singleton_key=? "
                    "AND holder_id=? AND fencing_token=?",
                    (released, ARBITRATION_KEY, grant.holder_id, grant.fencing_token),
                )
                self._connection.commit()
                self._condition.notify_all()
            except Exception:
                self._rollback_if_needed()
                self._release_after_failure(grant)
                raise

    def _release_after_failure(self, grant: KernelLeaseGrant) -> None:
        deadline = time.monotonic_ns() + DEFAULT_LEASE_WAIT_NS
        try:
            self._begin_immediate_until(deadline)
            row = self._connection.execute(
                "SELECT holder_id,fencing_token,acquired_ns,expires_ns,released_ns FROM authority_lease "
                "WHERE singleton_key=?",
                (ARBITRATION_KEY,),
            ).fetchone()
            if row and row["holder_id"] == grant.holder_id and int(row["fencing_token"]) == grant.fencing_token:
                released = self._clock_ns()
                if int(row["released_ns"]) == 0:
                    self._append_lease_receipt(
                        "FAILED_RELEASED", holder_id=grant.holder_id, fencing_token=grant.fencing_token,
                        observed_ns=released, acquired_ns=grant.acquired_ns, expires_ns=grant.expires_ns,
                        released_ns=released,
                    )
                    self._connection.execute(
                        "UPDATE authority_lease SET expires_ns=0,released_ns=? WHERE singleton_key=?",
                        (released, ARBITRATION_KEY),
                    )
            self._connection.commit()
        except (sqlite3.Error, LeaseBusyError):
            self._rollback_if_needed()

    @staticmethod
    def _kernel_fence_payload(row: Mapping[str, Any], acquire_hash: str) -> dict[str, Any]:
        return {
            "schema": KERNEL_AUTHORITY_SCHEMA,
            "receipt_hash72": row["receipt_hash72"],
            "receipt_index": int(row["receipt_index"]),
            "fence_hash72": row["fence_hash72"],
            "lease_acquire_hash72": acquire_hash,
            "holder_id": row["holder_id"],
            "fencing_token": int(row["fencing_token"]),
            "predecessor_hash72": row["predecessor_hash72"],
            "state_before": row["state_before"],
            "state_after": row["state_after"],
        }

    def _kernel_event_payload(self, sequence: int, event: Mapping[str, Any], acquire_hash: str) -> dict[str, Any]:
        return {
            "schema": KERNEL_AUTHORITY_SCHEMA,
            "event_sequence": sequence,
            "event_type": event["event_type"],
            "operation_id": event.get("operation_id"),
            "receipt_hash72": event.get("hash72"),
            "fencing_token": int(event["fencing_token"]),
            "lease_acquire_hash72": acquire_hash,
        }

    def _migration_lease_receipt(self, row: Mapping[str, Any]) -> str:
        return self._append_lease_receipt(
            "MIGRATED", holder_id=str(row["holder_id"]), fencing_token=int(row["fencing_token"]),
            observed_ns=int(row["committed_ns"]), acquired_ns=int(row["acquired_ns"]),
            expires_ns=int(row["expires_ns"]), released_ns=int(row["committed_ns"]),
        )

    def _backfill_kernel_authority(self, receipts: Mapping[str, Mapping[str, Any]]) -> None:
        fences = self._connection.execute("SELECT * FROM authority_fences ORDER BY receipt_index").fetchall()
        for row in fences:
            acquire_hash = row["lease_acquire_hash72"] or self._migration_lease_receipt(row)
            kernel_hash = hash72("pass190.kernel.authority", self._kernel_fence_payload(row, acquire_hash))
            self._connection.execute(
                "UPDATE authority_fences SET lease_acquire_hash72=?,kernel_authority_hash72=? "
                "WHERE receipt_hash72=?",
                (acquire_hash, kernel_hash, row["receipt_hash72"]),
            )

        events = self._connection.execute(
            "SELECT sequence,event_type,payload_json FROM events ORDER BY sequence"
        ).fetchall()
        for row in events:
            event = json.loads(row["payload_json"])
            if event["event_type"] == "operation.admitted":
                fence = self._connection.execute(
                    "SELECT * FROM authority_fences WHERE receipt_hash72=?", (event["hash72"],)
                ).fetchone()
                if fence is None:
                    raise PersistentStoreError("admitted event has no kernel fence")
                acquire_hash = fence["lease_acquire_hash72"]
                event["fencing_token"] = int(fence["fencing_token"])
                event["fence_hash72"] = fence["fence_hash72"]
                event["kernel_authority_hash72"] = fence["kernel_authority_hash72"]
                event["lease_acquire_hash72"] = acquire_hash
            elif event["event_type"] == "operation.replayed":
                token = event.get("fencing_token")
                lease_row = None
                if isinstance(token, int):
                    lease_row = self._connection.execute(
                        "SELECT receipt_hash72 FROM authority_lease_receipts WHERE fencing_token=? "
                        "ORDER BY sequence LIMIT 1", (token,)
                    ).fetchone()
                if lease_row is None:
                    token = self._highest_token() + 1
                    acquire_hash = self._append_lease_receipt(
                        "MIGRATED", holder_id="iteration4-event-migration", fencing_token=token,
                        observed_ns=0, acquired_ns=0, expires_ns=0, released_ns=0,
                    )
                else:
                    acquire_hash = lease_row["receipt_hash72"]
                event["fencing_token"] = int(token)
                event["lease_acquire_hash72"] = acquire_hash
                event["kernel_authority_hash72"] = hash72(
                    "pass190.kernel.event.authority",
                    self._kernel_event_payload(int(row["sequence"]), event, acquire_hash),
                )
            self._connection.execute(
                "UPDATE events SET payload_json=?,event_hash72=? WHERE sequence=?",
                (
                    canonical_json(event),
                    hash72("pass190.event", {
                        "sequence": int(row["sequence"]), "event_type": event["event_type"], "payload": event,
                    }),
                    int(row["sequence"]),
                ),
            )

    def persist_fenced_invocation(
        self,
        context: HHSAuthorityContext,
        invocation: InvocationResult,
        idempotency_key: str | None,
        grant: KernelLeaseGrant,
    ) -> int:
        sequence = DistributedAuthorityStore.persist_fenced_invocation(
            self, context, invocation, idempotency_key, grant
        )
        row = self._connection.execute(
            "SELECT * FROM authority_fences WHERE receipt_hash72=?", (invocation.receipt["hash72"],)
        ).fetchone()
        if row is None:
            raise PersistentStoreError("new receipt is missing its fencing witness")
        kernel_hash = hash72(
            "pass190.kernel.authority",
            self._kernel_fence_payload(row, grant.acquire_receipt_hash72),
        )
        self._connection.execute(
            "UPDATE authority_fences SET lease_acquire_hash72=?,kernel_authority_hash72=? "
            "WHERE receipt_hash72=?",
            (grant.acquire_receipt_hash72, kernel_hash, invocation.receipt["hash72"]),
        )
        event_row = self._connection.execute(
            "SELECT payload_json FROM events WHERE sequence=?", (sequence,)
        ).fetchone()
        event = json.loads(event_row[0])
        event["lease_acquire_hash72"] = grant.acquire_receipt_hash72
        event["kernel_authority_hash72"] = kernel_hash
        self._connection.execute(
            "UPDATE events SET payload_json=?,event_hash72=? WHERE sequence=?",
            (
                canonical_json(event),
                hash72("pass190.event", {"sequence": sequence, "event_type": event["event_type"], "payload": event}),
                sequence,
            ),
        )
        return sequence

    def append_fenced_event(self, event_type: str, payload: Mapping[str, Any], grant: KernelLeaseGrant) -> int:
        sequence = DistributedAuthorityStore.append_fenced_event(self, event_type, payload, grant)
        row = self._connection.execute("SELECT payload_json FROM events WHERE sequence=?", (sequence,)).fetchone()
        event = json.loads(row[0])
        event["lease_acquire_hash72"] = grant.acquire_receipt_hash72
        event["kernel_authority_hash72"] = hash72(
            "pass190.kernel.event.authority",
            self._kernel_event_payload(sequence, event, grant.acquire_receipt_hash72),
        )
        self._connection.execute(
            "UPDATE events SET payload_json=?,event_hash72=? WHERE sequence=?",
            (
                canonical_json(event),
                hash72("pass190.event", {"sequence": sequence, "event_type": event_type, "payload": event}),
                sequence,
            ),
        )
        return sequence

    def _validate_lease_receipts(self) -> None:
        rows = self._connection.execute(
            "SELECT sequence,transition,holder_id,fencing_token,payload_json,receipt_hash72 "
            "FROM authority_lease_receipts ORDER BY sequence"
        ).fetchall()
        predecessor = "0" * 72
        states: dict[int, list[str]] = {}
        for expected_sequence, row in enumerate(rows, 1):
            if int(row["sequence"]) != expected_sequence:
                raise PersistentStoreError("lease receipt sequence discontinuity")
            payload = json.loads(row["payload_json"])
            if payload.get("schema") != LEASE_RECEIPT_SCHEMA or payload.get("transition") != row["transition"]:
                raise PersistentStoreError("lease receipt schema or transition mismatch")
            if payload.get("predecessor_hash72") != predecessor:
                raise PersistentStoreError("lease receipt predecessor mismatch")
            expected = hash72("pass190.lease.transition", payload)
            if row["receipt_hash72"] != expected:
                raise PersistentStoreError("lease transition receipt Hash72 mismatch")
            if payload["holder_id"] != row["holder_id"] or payload["fencing_token"] != row["fencing_token"]:
                raise PersistentStoreError("lease transition receipt identity mismatch")
            predecessor = expected
            states.setdefault(int(row["fencing_token"]), []).append(str(row["transition"]))
        for transitions in states.values():
            if transitions == ["MIGRATED"]:
                continue
            if not transitions or transitions[0] != "ACQUIRED":
                raise PersistentStoreError("lease token does not begin with ACQUIRED")
            terminals = [value for value in transitions[1:] if value in {"RELEASED", "FAILED_RELEASED", "EXPIRED"}]
            if len(terminals) > 1 or len(transitions) > 2:
                raise PersistentStoreError("lease token has multiple terminal transitions")

    def _validate_kernel_fences(self, receipts: Mapping[str, Mapping[str, Any]]) -> None:
        DistributedAuthorityStore._validate_fences(self, receipts)
        rows = self._connection.execute("SELECT * FROM authority_fences ORDER BY receipt_index").fetchall()
        for row in rows:
            acquire_hash = row["lease_acquire_hash72"]
            kernel_hash = row["kernel_authority_hash72"]
            if not acquire_hash or not kernel_hash:
                raise PersistentStoreError("kernel-authority fence fields are incomplete")
            lease = self._connection.execute(
                "SELECT payload_json FROM authority_lease_receipts WHERE receipt_hash72=?", (acquire_hash,)
            ).fetchone()
            if lease is None:
                raise PersistentStoreError("kernel fence references an unknown lease receipt")
            payload = json.loads(lease[0])
            if payload["holder_id"] != row["holder_id"] or payload["fencing_token"] != row["fencing_token"]:
                raise PersistentStoreError("kernel fence and lease receipt identities disagree")
            expected = hash72("pass190.kernel.authority", self._kernel_fence_payload(row, acquire_hash))
            if kernel_hash != expected:
                raise PersistentStoreError("kernel-authority Hash72 mismatch")

    def _validate_kernel_events(self) -> None:
        rows = self._connection.execute(
            "SELECT sequence,event_type,payload_json FROM events ORDER BY sequence"
        ).fetchall()
        for row in rows:
            event = json.loads(row["payload_json"])
            if event["event_type"] == "operation.admitted":
                fence = self._connection.execute(
                    "SELECT fencing_token,fence_hash72,lease_acquire_hash72,kernel_authority_hash72 "
                    "FROM authority_fences WHERE receipt_hash72=?", (event["hash72"],)
                ).fetchone()
                if fence is None:
                    raise PersistentStoreError("admitted event has no kernel fence")
                for key in ("fencing_token", "fence_hash72", "lease_acquire_hash72", "kernel_authority_hash72"):
                    if event.get(key) != fence[key]:
                        raise PersistentStoreError(f"admitted event {key} mismatch")
            elif event["event_type"] == "operation.replayed":
                acquire_hash = event.get("lease_acquire_hash72")
                if not acquire_hash or self._connection.execute(
                    "SELECT 1 FROM authority_lease_receipts WHERE receipt_hash72=?", (acquire_hash,)
                ).fetchone() is None:
                    raise PersistentStoreError("replay event references an unknown lease receipt")
                expected = hash72(
                    "pass190.kernel.event.authority",
                    self._kernel_event_payload(int(row["sequence"]), event, acquire_hash),
                )
                if event.get("kernel_authority_hash72") != expected:
                    raise PersistentStoreError("replay kernel-authority Hash72 mismatch")

    def restore_into(self, context: HHSAuthorityContext) -> None:
        with self._lock:
            started = not self._connection.in_transaction
            try:
                if started:
                    self._connection.execute("BEGIN")
                HardenedSQLiteAuthorityStore.restore_into(self, context)
                self._validate_lease_receipts()
                self._validate_kernel_fences(context._receipts)
                self._validate_kernel_events()
                if started:
                    self._connection.commit()
            except Exception:
                if started:
                    self._rollback_if_needed()
                raise

    def _refresh_expired_lease(self) -> None:
        deadline = time.monotonic_ns() + DEFAULT_LEASE_WAIT_NS
        with self._lock:
            try:
                self._begin_immediate_until(deadline)
                self._settle_expired_locked(self._clock_ns())
                self._connection.commit()
            except Exception:
                self._rollback_if_needed()
                raise

    def lease_receipts_after(self, sequence: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        if sequence < 0 or limit < 1 or limit > 1000:
            raise PersistentStoreError("invalid lease receipt range")
        with self._lock:
            self._validate_lease_receipts()
            rows = self._connection.execute(
                "SELECT sequence,payload_json,receipt_hash72 FROM authority_lease_receipts "
                "WHERE sequence>? ORDER BY sequence LIMIT ?", (sequence, limit)
            ).fetchall()
            return [
                {"sequence": int(row["sequence"]), **json.loads(row["payload_json"]),
                 "receipt_hash72": row["receipt_hash72"]}
                for row in rows
            ]

    def arbitration_report(self) -> dict[str, Any]:
        self._refresh_expired_lease()
        with self._lock:
            self._connection.execute("BEGIN")
            try:
                self._validate_lease_receipts()
                row = self._connection.execute(
                    "SELECT holder_id,fencing_token,acquired_ns,expires_ns,released_ns FROM authority_lease "
                    "WHERE singleton_key=?", (ARBITRATION_KEY,)
                ).fetchone()
                fence_count = int(self._connection.execute("SELECT COUNT(*) FROM authority_fences").fetchone()[0])
                highest = int(self._connection.execute(
                    "SELECT COALESCE(MAX(fencing_token),0) FROM authority_fences"
                ).fetchone()[0])
                transition_count = int(self._connection.execute(
                    "SELECT COUNT(*) FROM authority_lease_receipts"
                ).fetchone()[0])
                last = self._connection.execute(
                    "SELECT transition,receipt_hash72 FROM authority_lease_receipts ORDER BY sequence DESC LIMIT 1"
                ).fetchone()
                now = self._clock_ns()
                active = bool(row and int(row["released_ns"]) == 0 and int(row["expires_ns"]) > now)
                if row is None:
                    lease_state = "absent"
                elif active:
                    lease_state = "active"
                elif int(row["released_ns"]) != 0:
                    lease_state = "released"
                else:
                    lease_state = "expired"
                report = {
                    "schema": "HHS_PASS_190_ARBITRATION_STATUS_V2",
                    "classification": ITERATION5_CLASSIFICATION,
                    "singleton_key": ARBITRATION_KEY,
                    "active": active,
                    "lease_state": lease_state,
                    "holder_id": row["holder_id"] if active else None,
                    "fencing_token": int(row["fencing_token"]) if row else highest,
                    "lease_expires_ns": int(row["expires_ns"]) if active else 0,
                    "fence_count": fence_count,
                    "highest_committed_fence": highest,
                    "lease_transition_count": transition_count,
                    "last_transition": None if last is None else last["transition"],
                    "last_transition_hash72": None if last is None else last["receipt_hash72"],
                    "lease_receipt_chain_verified": True,
                }
                self._connection.commit()
                return report
            except Exception:
                self._rollback_if_needed()
                raise

    def integrity_report(self) -> dict[str, Any]:
        probe = type("Probe", (), {})()
        probe._receipts, probe._idempotency = {}, {}
        probe._receipt_index, probe._last_hash72 = 0, "0" * 72
        probe._state, probe._state_root = {"counter": 0}, hash72("pass190.state", {"counter": 0})
        self.restore_into(probe)  # type: ignore[arg-type]
        arbitration = self.arbitration_report()
        return {
            "status": "ok",
            "classification": ITERATION5_CLASSIFICATION,
            "receipt_count": probe._receipt_index,
            "chain_head": probe._last_hash72,
            "state_root": probe._state_root,
            "event_count": int(self._connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]),
            "idempotency_count": int(self._connection.execute("SELECT COUNT(*) FROM idempotency").fetchone()[0]),
            "metadata_complete": True,
            "events_verified": True,
            "distributed_singleton_verified": True,
            "atomic_snapshot_verified": True,
            "lease_receipts_verified": True,
            "kernel_authority_verified": True,
            "fence_count": arbitration["fence_count"],
            "highest_committed_fence": arbitration["highest_committed_fence"],
            "lease_transition_count": arbitration["lease_transition_count"],
            "lease_active": arbitration["active"],
            "lease_state": arbitration["lease_state"],
        }


class CorrectedAuthorityContext(DistributedAuthorityContext):
    """Iteration 5 authority preserving all inherited operation semantics."""

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
        self.store = CorrectedAuthorityStore(database_path, clock_ns=clock_ns, sleeper=sleeper)
        HHSAuthorityContext.__init__(self, registry_path)
        self.store.restore_into(self)

    def lease_receipts_after(self, sequence: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.lease_receipts_after(sequence, limit)


_CONTEXT: CorrectedAuthorityContext | None = None
_CONTEXT_LOCK = threading.Lock()
_CONTEXT_PATH: Path | None = None


def get_iteration5_context(database_path: Path | str | None = None) -> CorrectedAuthorityContext:
    global _CONTEXT, _CONTEXT_PATH
    requested = Path(database_path or DEFAULT_DATABASE)
    if _CONTEXT is None:
        with _CONTEXT_LOCK:
            if _CONTEXT is None:
                _CONTEXT = CorrectedAuthorityContext(requested)
                _CONTEXT_PATH = requested
    elif _CONTEXT_PATH != requested:
        raise PersistentStoreError("process authority context already bound to another database")
    return _CONTEXT
