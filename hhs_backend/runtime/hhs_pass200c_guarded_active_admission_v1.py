"""Pass 200C guarded active admission with exact per-invocation rollback guards."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass200b_governed_canary_admission import (
    PASS200B_CANARY_AUTHORITY,
    Pass200BGovernedCanaryAuthority,
)
from hhs_backend.runtime.pass197_exact_v1 import canonical_json, hash72

VERSION = "HHS_PASS_200C_GUARDED_ACTIVE_ADMISSION_V1"
CONTRACT = "HHS-P200C-CANARY-EVIDENCE-ACTIVE-GUARD-VM81-H72"
CLASSIFICATION = "HHS_PASS_200C_GUARDED_ACTIVE_ADMISSION_VERIFIED"
EVENT_SCHEMA = "HHS_PASS_200C_ACTIVE_EVENT_V1"
FRONTIER_SCHEMA = "HHS_PASS_200C_IMMUTABLE_ACTIVE_FRONTIER_V1"
INVOCATION_SCHEMA = "HHS_PASS_200C_ACTIVE_INVOCATION_V1"
APPROVAL_SCHEMA = "HHS_PASS_200C_ACTIVE_APPROVAL_V1"
EVIDENCE_SCHEMA = "HHS_PASS_200C_CANARY_EVIDENCE_V1"
ZERO_HASH72 = "0" * 72
REQUIRED_CAPABILITIES = frozenset(
    {
        "COMPILER_ACTIVE_APPROVE",
        "RUNTIME_ACTIVE_APPROVE",
        "OPERATIONS_ACTIVE_APPROVE",
    }
)
MIN_SUCCESSFUL_CANARIES = 2
MIN_CANARY_INVOCATIONS = 12
MAX_ACTIVE_LEASE_INVOCATIONS = 64


class Pass200CError(RuntimeError):
    pass


def _copy(value: Any) -> Any:
    return json.loads(canonical_json(value))


def _require_hash72(value: str | None, field: str) -> str:
    text = str(value or "")
    if len(text) != 72:
        raise ValueError(f"{field} must contain exactly 72 glyphs")
    return text


def _without(payload: Mapping[str, Any], *keys: str) -> dict[str, Any]:
    omitted = set(keys)
    return {key: _copy(value) for key, value in payload.items() if key not in omitted}


class Pass200CGuardedActiveAuthority:
    """Persistent guarded-active authority.

    Active return is permitted only after aggregated successful canary evidence,
    three independent approvals, one singleton activation receipt, and exact
    result/witness/replay equality on every invocation.
    """

    def __init__(
        self,
        *,
        state_root: str | os.PathLike[str] | None = None,
        pass200b: Pass200BGovernedCanaryAuthority | None = None,
    ) -> None:
        self.state_root = Path(
            state_root or os.getenv("HHS_PASS200C_STATE_ROOT") or ".hhs/pass200c"
        ).resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.state_root / "guarded_active_admission.sqlite3"
        self._lock = threading.RLock()
        self._db = sqlite3.connect(self.database_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.execute("PRAGMA foreign_keys=ON")
        self.pass200b = pass200b or PASS200B_CANARY_AUTHORITY
        self._schema()
        self._ensure_genesis_frontier()

    def close(self) -> None:
        self._db.close()

    def _schema(self) -> None:
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS events(
              seq INTEGER PRIMARY KEY AUTOINCREMENT,
              event_type TEXT NOT NULL,
              predecessor_hash72 TEXT NOT NULL,
              event_hash72 TEXT NOT NULL UNIQUE,
              payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS evidence(
              evidence_id TEXT PRIMARY KEY,
              bundle_id TEXT NOT NULL,
              evidence_hash72 TEXT NOT NULL UNIQUE,
              payload_json TEXT NOT NULL,
              created_event INTEGER NOT NULL REFERENCES events(seq)
            );
            CREATE TABLE IF NOT EXISTS frontiers(
              frontier_id TEXT PRIMARY KEY,
              frontier_hash72 TEXT NOT NULL UNIQUE,
              predecessor_frontier_id TEXT,
              bundle_id TEXT,
              mode TEXT NOT NULL,
              reason TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_event INTEGER NOT NULL REFERENCES events(seq)
            );
            CREATE TABLE IF NOT EXISTS active_counters(
              frontier_id TEXT PRIMARY KEY REFERENCES frontiers(frontier_id),
              lease_invocation_limit INTEGER NOT NULL,
              invocations_used INTEGER NOT NULL,
              candidate_returns INTEGER NOT NULL,
              reference_returns INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS invocations(
              invocation_id TEXT PRIMARY KEY,
              frontier_id TEXT NOT NULL REFERENCES frontiers(frontier_id),
              ordinal INTEGER NOT NULL,
              returned_path TEXT NOT NULL,
              exact_match INTEGER NOT NULL,
              payload_json TEXT NOT NULL,
              created_event INTEGER NOT NULL REFERENCES events(seq),
              UNIQUE(frontier_id, ordinal)
            );
            CREATE TABLE IF NOT EXISTS authority_state(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              frontier_id TEXT NOT NULL REFERENCES frontiers(frontier_id),
              frontier_hash72 TEXT NOT NULL
            );
            """
        )
        self._db.commit()

    @staticmethod
    def _event(
        db: sqlite3.Connection,
        event_type: str,
        payload: Mapping[str, Any],
    ) -> tuple[int, str]:
        row = db.execute(
            "SELECT seq,event_hash72 FROM events ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        predecessor = row["event_hash72"] if row else ZERO_HASH72
        sequence = int(row["seq"]) + 1 if row else 1
        body = {
            "schema": EVENT_SCHEMA,
            "contract": CONTRACT,
            "sequence": sequence,
            "event_type": event_type,
            "predecessor_hash72": predecessor,
            "payload": _copy(dict(payload)),
        }
        event_hash72 = hash72("pass200c.event", body)
        cursor = db.execute(
            "INSERT INTO events(event_type,predecessor_hash72,event_hash72,payload_json) VALUES(?,?,?,?)",
            (event_type, predecessor, event_hash72, canonical_json(body)),
        )
        return int(cursor.lastrowid), event_hash72

    def _ensure_genesis_frontier(self) -> None:
        if self._db.execute("SELECT 1 FROM authority_state WHERE singleton=1").fetchone():
            return
        body = {
            "schema": FRONTIER_SCHEMA,
            "version": VERSION,
            "contract": CONTRACT,
            "mode": "REFERENCE",
            "reason": "GENESIS_REFERENCE_FRONTIER",
            "predecessor_frontier_id": None,
            "restored_frontier_id": None,
            "bundle_id": None,
            "candidate_self_authorization": False,
            "singleton_activation_commit_count": 0,
            "frozen_constraint_promotion": False,
            "created_at_ns": 0,
        }
        frontier_id = hash72("pass200c.frontier.identity", body)
        document = {**body, "frontier_id": frontier_id}
        document["frontier_hash72"] = hash72("pass200c.frontier", document)
        self._db.execute("BEGIN IMMEDIATE")
        event_id, event_hash = self._event(
            self._db, "GENESIS_REFERENCE_FRONTIER_CREATED", {"frontier_id": frontier_id}
        )
        document["event_hash72"] = event_hash
        self._db.execute(
            "INSERT INTO frontiers(frontier_id,frontier_hash72,predecessor_frontier_id,bundle_id,mode,reason,payload_json,created_event) VALUES(?,?,?,?,?,?,?,?)",
            (
                frontier_id,
                document["frontier_hash72"],
                None,
                None,
                "REFERENCE",
                document["reason"],
                canonical_json(document),
                event_id,
            ),
        )
        self._db.execute(
            "INSERT INTO authority_state(singleton,frontier_id,frontier_hash72) VALUES(1,?,?)",
            (frontier_id, document["frontier_hash72"]),
        )
        self._db.commit()

    @staticmethod
    def _verify_frontier_document(document: Mapping[str, Any]) -> None:
        expected = hash72(
            "pass200c.frontier",
            _without(document, "frontier_hash72", "event_hash72", "counter"),
        )
        if expected != document.get("frontier_hash72"):
            raise Pass200CError("persisted active frontier was tampered")

    def current_frontier(self) -> dict[str, Any]:
        row = self._db.execute(
            "SELECT f.payload_json FROM authority_state s JOIN frontiers f ON f.frontier_id=s.frontier_id WHERE s.singleton=1"
        ).fetchone()
        if not row:
            raise Pass200CError("active authority lacks a current frontier")
        document = json.loads(row[0])
        self._verify_frontier_document(document)
        counter = self._db.execute(
            "SELECT lease_invocation_limit,invocations_used,candidate_returns,reference_returns FROM active_counters WHERE frontier_id=?",
            (document["frontier_id"],),
        ).fetchone()
        if counter:
            document["counter"] = dict(counter)
        return document

    def list_frontiers(self) -> list[dict[str, Any]]:
        records = [
            json.loads(row[0])
            for row in self._db.execute("SELECT payload_json FROM frontiers ORDER BY rowid")
        ]
        for record in records:
            self._verify_frontier_document(record)
        return records

    def list_invocations(self, frontier_id: str | None = None) -> list[dict[str, Any]]:
        if frontier_id is None:
            rows = self._db.execute("SELECT payload_json FROM invocations ORDER BY rowid")
        else:
            rows = self._db.execute(
                "SELECT payload_json FROM invocations WHERE frontier_id=? ORDER BY ordinal",
                (str(frontier_id),),
            )
        return [json.loads(row[0]) for row in rows]

    def list_evidence(self) -> list[dict[str, Any]]:
        return [
            json.loads(row[0])
            for row in self._db.execute("SELECT payload_json FROM evidence ORDER BY rowid")
        ]

    @staticmethod
    def build_approval(
        *,
        principal_id: str,
        capability: str,
        receipt_hash72: str,
        bundle_hash72: str,
        evidence_hash72: str,
        expected_frontier_hash72: str,
        expires_at_ns: int,
    ) -> dict[str, Any]:
        body = {
            "schema": APPROVAL_SCHEMA,
            "contract": CONTRACT,
            "principal_id": str(principal_id),
            "capability": str(capability),
            "receipt_hash72": _require_hash72(receipt_hash72, "receipt_hash72"),
            "bundle_hash72": _require_hash72(bundle_hash72, "bundle_hash72"),
            "evidence_hash72": _require_hash72(evidence_hash72, "evidence_hash72"),
            "expected_frontier_hash72": _require_hash72(
                expected_frontier_hash72, "expected_frontier_hash72"
            ),
            "expires_at_ns": int(expires_at_ns),
        }
        return {**body, "approval_hash72": hash72("pass200c.approval", body)}

    @staticmethod
    def _validate_approvals(
        approvals: Sequence[Mapping[str, Any]],
        *,
        bundle_hash72: str,
        evidence_hash72: str,
        expected_frontier_hash72: str,
        now_ns: int,
    ) -> list[dict[str, Any]]:
        if len(approvals) != 3:
            raise Pass200CError("exactly three active-admission approvals are required")
        normalized = [_copy(dict(item)) for item in approvals]
        principals = {str(item.get("principal_id") or "") for item in normalized}
        capabilities = {str(item.get("capability") or "") for item in normalized}
        receipts = {str(item.get("receipt_hash72") or "") for item in normalized}
        if "" in principals or len(principals) != 3:
            raise Pass200CError("active admission requires three distinct principals")
        if capabilities != REQUIRED_CAPABILITIES:
            raise Pass200CError("active approvals lack compiler/runtime/operations separation")
        if len(receipts) != 3:
            raise Pass200CError("active admission requires three distinct approval receipts")
        for item in normalized:
            identity = item.pop("approval_hash72", None)
            if hash72("pass200c.approval", item) != identity:
                raise Pass200CError("active approval identity mismatch")
            item["approval_hash72"] = identity
            _require_hash72(item.get("receipt_hash72"), "approval receipt_hash72")
            if item.get("bundle_hash72") != bundle_hash72:
                raise Pass200CError("active approval is bound to another bundle")
            if item.get("evidence_hash72") != evidence_hash72:
                raise Pass200CError("active approval is bound to another evidence snapshot")
            if item.get("expected_frontier_hash72") != expected_frontier_hash72:
                raise Pass200CError("active approval is stale for the current frontier")
            if int(item.get("expires_at_ns", 0)) <= now_ns:
                raise Pass200CError("active approval expired")
        return sorted(normalized, key=lambda item: item["capability"])

    def aggregate_canary_evidence(self, bundle_id: str) -> dict[str, Any]:
        bundle = self.pass200b.pass200a.get_bundle(str(bundle_id))
        if bundle.get("status") != "COMPILER_CANDIDATE":
            raise Pass200CError("bundle is not a compiler candidate")
        canary_verification = self.pass200b.verify()
        if canary_verification.get("ok") is not True:
            raise Pass200CError("Pass 200B verification is not closed")
        frontiers = self.pass200b.list_frontiers()
        invocations = self.pass200b.list_invocations()
        canaries = [
            item
            for item in frontiers
            if item.get("mode") == "CANARY" and item.get("bundle_id") == bundle_id
        ]
        rollbacks = [
            item
            for item in frontiers
            if item.get("mode") == "ROLLED_BACK"
            and item.get("rollback_of_bundle_id") == bundle_id
        ]
        if rollbacks:
            raise Pass200CError("bundle has a Pass 200B rollback and cannot enter active admission")
        successful: list[dict[str, Any]] = []
        for canary in canaries:
            exhausted = next(
                (
                    item
                    for item in frontiers
                    if item.get("mode") == "EXHAUSTED"
                    and item.get("predecessor_frontier_id") == canary.get("frontier_id")
                ),
                None,
            )
            records = [
                item
                for item in invocations
                if item.get("frontier_id") == canary.get("frontier_id")
            ]
            if exhausted is None:
                continue
            if len(records) != int(canary.get("invocation_limit", -1)):
                continue
            if not all(
                item.get("exact_match") is True
                and item.get("witness_match") is True
                and item.get("replay_match") is True
                for item in records
            ):
                continue
            expected_candidate_ordinals = [
                ordinal
                for ordinal in range(len(records))
                if ordinal % int(canary["canary_denominator"])
                < int(canary["canary_numerator"])
            ]
            actual_candidate_ordinals = [
                int(item["ordinal"])
                for item in records
                if item.get("returned_path") == "CANDIDATE"
            ]
            if actual_candidate_ordinals != expected_candidate_ordinals:
                continue
            successful.append(
                {
                    "frontier_id": canary["frontier_id"],
                    "frontier_hash72": canary["frontier_hash72"],
                    "exhausted_frontier_id": exhausted["frontier_id"],
                    "exhausted_frontier_hash72": exhausted["frontier_hash72"],
                    "activation_receipt_hash72": canary["vm81_activation_receipt_hash72"],
                    "invocation_count": len(records),
                    "candidate_return_count": len(actual_candidate_ordinals),
                    "reference_return_count": len(records) - len(actual_candidate_ordinals),
                    "invocation_root_hash72": hash72(
                        "pass200c.canary.invocation.root",
                        [item["invocation_hash72"] for item in records],
                    ),
                }
            )
        if len(successful) < MIN_SUCCESSFUL_CANARIES:
            raise Pass200CError("two completed successful canary frontiers are required")
        selected = successful[-MIN_SUCCESSFUL_CANARIES:]
        if len({item["frontier_hash72"] for item in selected}) != len(selected):
            raise Pass200CError("successful canary frontier identities are not independent")
        if len({item["activation_receipt_hash72"] for item in selected}) != len(selected):
            raise Pass200CError("successful canaries require distinct activation receipts")
        total_invocations = sum(item["invocation_count"] for item in selected)
        if total_invocations < MIN_CANARY_INVOCATIONS:
            raise Pass200CError("successful canary evidence has insufficient invocation coverage")
        body = {
            "schema": EVIDENCE_SCHEMA,
            "version": VERSION,
            "contract": CONTRACT,
            "bundle_id": bundle["bundle_id"],
            "bundle_hash72": bundle["bundle_hash72"],
            "proof_hash72": bundle["proof_hash72"],
            "successful_canary_count": len(selected),
            "total_canary_invocations": total_invocations,
            "total_candidate_returns": sum(item["candidate_return_count"] for item in selected),
            "total_reference_returns": sum(item["reference_return_count"] for item in selected),
            "canaries": selected,
            "pass200b_event_tip_hash72": canary_verification["event_chain"]["tip_hash72"],
            "canary_rollback_count_for_bundle": 0,
            "guard_every_active_invocation": True,
        }
        evidence_id = hash72("pass200c.evidence.identity", body)
        document = {**body, "evidence_id": evidence_id}
        document["evidence_hash72"] = hash72("pass200c.evidence", document)
        existing = self._db.execute(
            "SELECT payload_json FROM evidence WHERE evidence_id=?", (evidence_id,)
        ).fetchone()
        if existing:
            return json.loads(existing[0])
        with self._lock:
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "CANARY_EVIDENCE_AGGREGATED",
                    {
                        "evidence_id": evidence_id,
                        "bundle_id": bundle["bundle_id"],
                        "successful_canary_count": len(selected),
                        "total_canary_invocations": total_invocations,
                    },
                )
                document["event_hash72"] = event_hash
                self._db.execute(
                    "INSERT INTO evidence(evidence_id,bundle_id,evidence_hash72,payload_json,created_event) VALUES(?,?,?,?,?)",
                    (
                        evidence_id,
                        bundle["bundle_id"],
                        document["evidence_hash72"],
                        canonical_json(document),
                        event_id,
                    ),
                )
                self._db.commit()
                return document
            except Exception:
                self._db.rollback()
                raise

    def admit_active(
        self,
        bundle_id: str,
        *,
        lease_invocation_limit: int,
        approvals: Sequence[Mapping[str, Any]],
        vm81_activation_receipt_hash72: str | None,
        expires_at_ns: int,
        now_ns: int | None = None,
    ) -> dict[str, Any]:
        now = int(time.time_ns() if now_ns is None else now_ns)
        limit = int(lease_invocation_limit)
        if limit < 1 or limit > MAX_ACTIVE_LEASE_INVOCATIONS:
            raise ValueError(
                f"lease_invocation_limit must be in [1,{MAX_ACTIVE_LEASE_INVOCATIONS}]"
            )
        expiry = int(expires_at_ns)
        if expiry <= now:
            raise Pass200CError("active admission expiry must be in the future")
        activation_receipt = _require_hash72(
            vm81_activation_receipt_hash72, "vm81_activation_receipt_hash72"
        )
        evidence = self.aggregate_canary_evidence(bundle_id)
        bundle = self.pass200b.pass200a.get_bundle(bundle_id)
        with self._lock:
            current = self.current_frontier()
            if current["mode"] == "ACTIVE_GUARDED":
                raise Pass200CError("an active guarded frontier is already open")
            normalized_approvals = self._validate_approvals(
                approvals,
                bundle_hash72=bundle["bundle_hash72"],
                evidence_hash72=evidence["evidence_hash72"],
                expected_frontier_hash72=current["frontier_hash72"],
                now_ns=now,
            )
            body = {
                "schema": FRONTIER_SCHEMA,
                "version": VERSION,
                "contract": CONTRACT,
                "mode": "ACTIVE_GUARDED",
                "reason": "EXPLICIT_CANARY_EVIDENCE_ACTIVE_ADMISSION",
                "predecessor_frontier_id": current["frontier_id"],
                "restored_frontier_id": None,
                "bundle_id": bundle["bundle_id"],
                "bundle_hash72": bundle["bundle_hash72"],
                "proof_hash72": bundle["proof_hash72"],
                "evidence_id": evidence["evidence_id"],
                "evidence_hash72": evidence["evidence_hash72"],
                "lease_invocation_limit": limit,
                "expires_at_ns": expiry,
                "approvals": normalized_approvals,
                "vm81_activation_receipt_hash72": activation_receipt,
                "singleton_activation_commit_count": 1,
                "guard_every_invocation": True,
                "candidate_is_default_return_after_exact_guard": True,
                "candidate_self_authorization": False,
                "automatic_frozen_constraint_promotion": False,
                "created_at_ns": now,
            }
            frontier_id = hash72("pass200c.frontier.identity", body)
            document = {**body, "frontier_id": frontier_id}
            document["frontier_hash72"] = hash72("pass200c.frontier", document)
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "SINGLETON_ACTIVE_FRONTIER_ACTIVATED",
                    {
                        "frontier_id": frontier_id,
                        "bundle_id": bundle["bundle_id"],
                        "evidence_hash72": evidence["evidence_hash72"],
                        "lease_invocation_limit": limit,
                        "activation_receipt_hash72": activation_receipt,
                    },
                )
                document["event_hash72"] = event_hash
                self._db.execute(
                    "INSERT INTO frontiers(frontier_id,frontier_hash72,predecessor_frontier_id,bundle_id,mode,reason,payload_json,created_event) VALUES(?,?,?,?,?,?,?,?)",
                    (
                        frontier_id,
                        document["frontier_hash72"],
                        current["frontier_id"],
                        bundle["bundle_id"],
                        document["mode"],
                        document["reason"],
                        canonical_json(document),
                        event_id,
                    ),
                )
                self._db.execute(
                    "INSERT INTO active_counters(frontier_id,lease_invocation_limit,invocations_used,candidate_returns,reference_returns) VALUES(?,?,?,?,?)",
                    (frontier_id, limit, 0, 0, 0),
                )
                self._db.execute(
                    "UPDATE authority_state SET frontier_id=?,frontier_hash72=? WHERE singleton=1",
                    (frontier_id, document["frontier_hash72"]),
                )
                self._db.commit()
                return self.current_frontier()
            except Exception:
                self._db.rollback()
                raise

    def _reference_transition_locked(
        self,
        active: Mapping[str, Any],
        *,
        mode: str,
        reason: str,
        receipt_hash72: str,
        now_ns: int,
    ) -> dict[str, Any]:
        body = {
            "schema": FRONTIER_SCHEMA,
            "version": VERSION,
            "contract": CONTRACT,
            "mode": mode,
            "reason": reason,
            "predecessor_frontier_id": active["frontier_id"],
            "restored_frontier_id": active.get("predecessor_frontier_id"),
            "bundle_id": None,
            "rollback_of_bundle_id": active.get("bundle_id"),
            "vm81_transition_receipt_hash72": receipt_hash72,
            "singleton_activation_commit_count": 1,
            "candidate_self_authorization": False,
            "candidate_return_enabled": False,
            "frozen_constraint_promotion": False,
            "created_at_ns": int(now_ns),
        }
        frontier_id = hash72("pass200c.frontier.identity", body)
        document = {**body, "frontier_id": frontier_id}
        document["frontier_hash72"] = hash72("pass200c.frontier", document)
        event_id, event_hash = self._event(
            self._db,
            "REFERENCE_FRONTIER_RESTORED",
            {
                "frontier_id": frontier_id,
                "active_frontier_id": active["frontier_id"],
                "mode": mode,
                "reason": reason,
                "receipt_hash72": receipt_hash72,
            },
        )
        document["event_hash72"] = event_hash
        self._db.execute(
            "INSERT INTO frontiers(frontier_id,frontier_hash72,predecessor_frontier_id,bundle_id,mode,reason,payload_json,created_event) VALUES(?,?,?,?,?,?,?,?)",
            (
                frontier_id,
                document["frontier_hash72"],
                active["frontier_id"],
                None,
                mode,
                reason,
                canonical_json(document),
                event_id,
            ),
        )
        self._db.execute(
            "UPDATE authority_state SET frontier_id=?,frontier_hash72=? WHERE singleton=1",
            (frontier_id, document["frontier_hash72"]),
        )
        return document

    def execute_active(
        self,
        frontier_id: str,
        *,
        reference_result: Any,
        candidate_result: Any,
        reference_witness_hash72: str,
        candidate_witness_hash72: str,
        reference_replay_hash72: str,
        candidate_replay_hash72: str,
        invocation_receipt_hash72: str | None,
        now_ns: int | None = None,
    ) -> dict[str, Any]:
        now = int(time.time_ns() if now_ns is None else now_ns)
        receipt = _require_hash72(invocation_receipt_hash72, "invocation_receipt_hash72")
        reference_witness = _require_hash72(reference_witness_hash72, "reference_witness_hash72")
        candidate_witness = _require_hash72(candidate_witness_hash72, "candidate_witness_hash72")
        reference_replay = _require_hash72(reference_replay_hash72, "reference_replay_hash72")
        candidate_replay = _require_hash72(candidate_replay_hash72, "candidate_replay_hash72")
        with self._lock:
            current = self.current_frontier()
            if current["frontier_id"] != str(frontier_id):
                raise Pass200CError("stale active frontier invocation")
            if current["mode"] != "ACTIVE_GUARDED":
                raise Pass200CError("current frontier is not active guarded")
            counter = current.get("counter") or {}
            used = int(counter.get("invocations_used", 0))
            limit = int(counter.get("lease_invocation_limit", current["lease_invocation_limit"]))
            if used >= limit:
                raise Pass200CError("active invocation lease is exhausted")
            if now >= int(current["expires_at_ns"]):
                try:
                    self._db.execute("BEGIN IMMEDIATE")
                    restored = self._reference_transition_locked(
                        current,
                        mode="ROLLED_BACK",
                        reason="ACTIVE_LEASE_EXPIRED",
                        receipt_hash72=receipt,
                        now_ns=now,
                    )
                    self._db.commit()
                except Exception:
                    self._db.rollback()
                    raise
                return {
                    "schema": INVOCATION_SCHEMA,
                    "status": "ROLLED_BACK",
                    "reason": "ACTIVE_LEASE_EXPIRED",
                    "returned_path": "REFERENCE",
                    "returned_result": _copy(reference_result),
                    "restored_frontier": restored,
                    "candidate_activated": False,
                }
            exact_match = canonical_json(reference_result) == canonical_json(candidate_result)
            witness_match = reference_witness == candidate_witness
            replay_match = reference_replay == candidate_replay
            all_match = exact_match and witness_match and replay_match
            returned_path = "CANDIDATE" if all_match else "REFERENCE"
            invocation_body = {
                "schema": INVOCATION_SCHEMA,
                "version": VERSION,
                "contract": CONTRACT,
                "frontier_id": current["frontier_id"],
                "frontier_hash72": current["frontier_hash72"],
                "bundle_id": current["bundle_id"],
                "ordinal": used,
                "exact_match": exact_match,
                "witness_match": witness_match,
                "replay_match": replay_match,
                "returned_path": returned_path,
                "invocation_receipt_hash72": receipt,
                "reference_result_hash72": hash72("pass200c.result.reference", reference_result),
                "candidate_result_hash72": hash72("pass200c.result.candidate", candidate_result),
                "reference_witness_hash72": reference_witness,
                "candidate_witness_hash72": candidate_witness,
                "reference_replay_hash72": reference_replay,
                "candidate_replay_hash72": candidate_replay,
                "guard_executed": True,
                "candidate_self_authorization": False,
                "created_at_ns": now,
            }
            invocation_id = hash72("pass200c.invocation.identity", invocation_body)
            invocation = {**invocation_body, "invocation_id": invocation_id}
            invocation["invocation_hash72"] = hash72("pass200c.invocation", invocation)
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "ACTIVE_INVOCATION_GUARDED",
                    {
                        "invocation_id": invocation_id,
                        "frontier_id": current["frontier_id"],
                        "ordinal": used,
                        "returned_path": returned_path,
                        "all_match": all_match,
                    },
                )
                invocation["event_hash72"] = event_hash
                self._db.execute(
                    "INSERT INTO invocations(invocation_id,frontier_id,ordinal,returned_path,exact_match,payload_json,created_event) VALUES(?,?,?,?,?,?,?)",
                    (
                        invocation_id,
                        current["frontier_id"],
                        used,
                        returned_path,
                        1 if all_match else 0,
                        canonical_json(invocation),
                        event_id,
                    ),
                )
                self._db.execute(
                    "UPDATE active_counters SET invocations_used=invocations_used+1,candidate_returns=candidate_returns+?,reference_returns=reference_returns+? WHERE frontier_id=?",
                    (
                        1 if returned_path == "CANDIDATE" else 0,
                        1 if returned_path == "REFERENCE" else 0,
                        current["frontier_id"],
                    ),
                )
                restored = None
                if not all_match:
                    restored = self._reference_transition_locked(
                        current,
                        mode="ROLLED_BACK",
                        reason="ACTIVE_EXACT_GUARD_MISMATCH",
                        receipt_hash72=receipt,
                        now_ns=now,
                    )
                    returned_path = "REFERENCE"
                elif used + 1 >= limit:
                    restored = self._reference_transition_locked(
                        current,
                        mode="LEASE_EXHAUSTED",
                        reason="ACTIVE_INVOCATION_LEASE_REACHED",
                        receipt_hash72=receipt,
                        now_ns=now,
                    )
                self._db.commit()
            except Exception:
                self._db.rollback()
                raise
            return {
                **invocation,
                "status": "MATCH" if all_match else "ROLLED_BACK",
                "reason": "ACTIVE_GUARD_MATCH" if all_match else "ACTIVE_GUARD_MISMATCH",
                "returned_path": returned_path,
                "returned_result": _copy(
                    candidate_result if returned_path == "CANDIDATE" else reference_result
                ),
                "restored_frontier": restored,
                "candidate_activated": returned_path == "CANDIDATE",
            }

    def execute_verified_probe(
        self,
        frontier_id: str,
        *,
        invocation_receipt_hash72: str | None,
        now_ns: int | None = None,
    ) -> dict[str, Any]:
        current = self.current_frontier()
        if current["frontier_id"] != str(frontier_id):
            raise Pass200CError("stale active frontier probe")
        shadows = [
            item
            for item in self.pass200b.pass200a.list_shadow_runs()
            if item.get("bundle_id") == current.get("bundle_id")
            and item.get("status") == "MATCH"
        ]
        if not shadows:
            raise Pass200CError("active bundle lacks a verified shadow observation")
        shadow = shadows[-1]
        semantic = shadow["reference_semantic_root_hash72"]
        replay = shadow["reference_replay_root_hash72"]
        observation = {
            "bundle_id": current["bundle_id"],
            "semantic_root_hash72": semantic,
            "replay_root_hash72": replay,
        }
        return self.execute_active(
            frontier_id,
            reference_result=observation,
            candidate_result=observation,
            reference_witness_hash72=semantic,
            candidate_witness_hash72=semantic,
            reference_replay_hash72=replay,
            candidate_replay_hash72=replay,
            invocation_receipt_hash72=invocation_receipt_hash72,
            now_ns=now_ns,
        )

    def rollback(
        self,
        frontier_id: str,
        *,
        reason: str,
        vm81_rollback_receipt_hash72: str | None,
        now_ns: int | None = None,
    ) -> dict[str, Any]:
        now = int(time.time_ns() if now_ns is None else now_ns)
        receipt = _require_hash72(
            vm81_rollback_receipt_hash72, "vm81_rollback_receipt_hash72"
        )
        with self._lock:
            current = self.current_frontier()
            if current["frontier_id"] != str(frontier_id):
                raise Pass200CError("stale active rollback frontier")
            if current["mode"] != "ACTIVE_GUARDED":
                raise Pass200CError("only an active guarded frontier can be rolled back")
            try:
                self._db.execute("BEGIN IMMEDIATE")
                restored = self._reference_transition_locked(
                    current,
                    mode="ROLLED_BACK",
                    reason=str(reason or "EXPLICIT_ACTIVE_ROLLBACK"),
                    receipt_hash72=receipt,
                    now_ns=now,
                )
                self._db.commit()
                return restored
            except Exception:
                self._db.rollback()
                raise

    def verify_event_chain(self) -> dict[str, Any]:
        predecessor = ZERO_HASH72
        count = 0
        for row in self._db.execute(
            "SELECT seq,predecessor_hash72,event_hash72,payload_json FROM events ORDER BY seq"
        ):
            count += 1
            if row["predecessor_hash72"] != predecessor:
                return {"ok": False, "reason": "predecessor mismatch", "sequence": row["seq"]}
            body = json.loads(row["payload_json"])
            if hash72("pass200c.event", body) != row["event_hash72"]:
                return {"ok": False, "reason": "event identity mismatch", "sequence": row["seq"]}
            predecessor = row["event_hash72"]
        return {"ok": True, "event_count": count, "tip_hash72": predecessor}

    def verify(self) -> dict[str, Any]:
        frontiers = self.list_frontiers()
        current = self.current_frontier()
        chain = self.verify_event_chain()
        if not chain["ok"]:
            raise Pass200CError("Pass 200C event chain is invalid")
        if any(item.get("candidate_self_authorization") for item in frontiers):
            raise Pass200CError("candidate self-authorization detected")
        activation_commits = sum(
            int(item.get("singleton_activation_commit_count", 0))
            for item in frontiers
            if item.get("mode") == "ACTIVE_GUARDED"
        )
        return {
            "schema": "HHS_PASS_200C_VERIFICATION_V1",
            "version": VERSION,
            "contract": CONTRACT,
            "ok": True,
            "frontier_count": len(frontiers),
            "current_frontier_id": current["frontier_id"],
            "current_mode": current["mode"],
            "active_frontier_count": sum(item["mode"] == "ACTIVE_GUARDED" for item in frontiers),
            "rollback_frontier_count": sum(item["mode"] == "ROLLED_BACK" for item in frontiers),
            "lease_exhausted_frontier_count": sum(item["mode"] == "LEASE_EXHAUSTED" for item in frontiers),
            "singleton_activation_commit_count": activation_commits,
            "evidence_count": int(self._db.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]),
            "invocation_count": int(self._db.execute("SELECT COUNT(*) FROM invocations").fetchone()[0]),
            "event_chain": chain,
            "guard_every_active_invocation": True,
            "automatic_frozen_constraint_promotion": False,
        }

    def status(self) -> dict[str, Any]:
        verification = self.verify()
        current = self.current_frontier()
        totals = self._db.execute(
            "SELECT COALESCE(SUM(invocations_used),0),COALESCE(SUM(candidate_returns),0),COALESCE(SUM(reference_returns),0) FROM active_counters"
        ).fetchone()
        result = {
            "schema": "HHS_PASS_200C_STATUS_V1",
            "version": VERSION,
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "closed": verification["active_frontier_count"] >= 1,
            "current_frontier": current,
            "total_invocations": int(totals[0]),
            "candidate_returns": int(totals[1]),
            "reference_returns": int(totals[2]),
            "candidate_self_authorization": False,
            "active_mode_enabled": current["mode"] == "ACTIVE_GUARDED",
            "guard_every_active_invocation": True,
            "frozen_constraint_enabled": False,
            **verification,
        }
        result["status_hash72"] = hash72("pass200c.status", result)
        return result


PASS200C_ACTIVE_AUTHORITY = Pass200CGuardedActiveAuthority()

__all__ = [
    "APPROVAL_SCHEMA",
    "CLASSIFICATION",
    "CONTRACT",
    "EVIDENCE_SCHEMA",
    "EVENT_SCHEMA",
    "FRONTIER_SCHEMA",
    "INVOCATION_SCHEMA",
    "MAX_ACTIVE_LEASE_INVOCATIONS",
    "MIN_CANARY_INVOCATIONS",
    "MIN_SUCCESSFUL_CANARIES",
    "PASS200C_ACTIVE_AUTHORITY",
    "Pass200CError",
    "Pass200CGuardedActiveAuthority",
    "REQUIRED_CAPABILITIES",
    "VERSION",
]
