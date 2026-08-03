"""Pass 200B governed canary admission, metering, and fail-closed rollback."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass200a_proof_carrying_optimization import (
    PASS200A_OPTIMIZATION_AUTHORITY,
    Pass200AProofCarryingOptimizationAuthority,
)
from hhs_backend.runtime.pass197_exact_v1 import canonical_json, hash72

VERSION = "HHS_PASS_200B_GOVERNED_CANARY_ADMISSION_V1"
CONTRACT = "HHS-P200B-DUAL-APPROVAL-CANARY-ROLLBACK-VM81-H72"
CLASSIFICATION = "HHS_PASS_200B_GOVERNED_CANARY_ADMISSION_VERIFIED"
EVENT_SCHEMA = "HHS_PASS_200B_CANARY_EVENT_V1"
FRONTIER_SCHEMA = "HHS_PASS_200B_IMMUTABLE_FRONTIER_V1"
INVOCATION_SCHEMA = "HHS_PASS_200B_CANARY_INVOCATION_V1"
APPROVAL_SCHEMA = "HHS_PASS_200B_PROMOTION_APPROVAL_V1"
ZERO_HASH72 = "0" * 72
REQUIRED_CAPABILITIES = frozenset(
    {"COMPILER_PROMOTION_APPROVE", "RUNTIME_PROMOTION_APPROVE"}
)
MAX_INVOCATION_LIMIT = 64


class Pass200BError(RuntimeError):
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


class Pass200BGovernedCanaryAuthority:
    """Persistent canary authority with immutable frontiers and bounded counters."""

    def __init__(
        self,
        *,
        state_root: str | os.PathLike[str] | None = None,
        pass200a: Pass200AProofCarryingOptimizationAuthority | None = None,
    ) -> None:
        self.state_root = Path(
            state_root or os.getenv("HHS_PASS200B_STATE_ROOT") or ".hhs/pass200b"
        ).resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.state_root / "governed_canary_admission.sqlite3"
        self._lock = threading.RLock()
        self._db = sqlite3.connect(self.database_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.execute("PRAGMA foreign_keys=ON")
        self.pass200a = pass200a or PASS200A_OPTIMIZATION_AUTHORITY
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
            CREATE TABLE IF NOT EXISTS canary_counters(
              frontier_id TEXT PRIMARY KEY REFERENCES frontiers(frontier_id),
              invocation_limit INTEGER NOT NULL,
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
        event_hash72 = hash72("pass200b.event", body)
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
            "compiler_candidate_only": True,
            "candidate_self_authorization": False,
            "singleton_activation_commit_count": 0,
            "created_at_ns": 0,
        }
        frontier_id = hash72("pass200b.frontier.identity", body)
        document = {**body, "frontier_id": frontier_id}
        document["frontier_hash72"] = hash72("pass200b.frontier", document)
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
            "pass200b.frontier",
            _without(document, "frontier_hash72", "event_hash72", "counter"),
        )
        if expected != document.get("frontier_hash72"):
            raise Pass200BError("persisted canary frontier was tampered")

    def current_frontier(self) -> dict[str, Any]:
        row = self._db.execute(
            "SELECT f.payload_json FROM authority_state s JOIN frontiers f ON f.frontier_id=s.frontier_id WHERE s.singleton=1"
        ).fetchone()
        if not row:
            raise Pass200BError("canary authority lacks an active frontier")
        document = json.loads(row[0])
        self._verify_frontier_document(document)
        counter = self._db.execute(
            "SELECT invocation_limit,invocations_used,candidate_returns,reference_returns FROM canary_counters WHERE frontier_id=?",
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

    @staticmethod
    def build_approval(
        *,
        principal_id: str,
        capability: str,
        receipt_hash72: str,
        bundle_hash72: str,
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
            "expected_frontier_hash72": _require_hash72(
                expected_frontier_hash72, "expected_frontier_hash72"
            ),
            "expires_at_ns": int(expires_at_ns),
        }
        return {**body, "approval_hash72": hash72("pass200b.approval", body)}

    @staticmethod
    def _validate_approvals(
        approvals: Sequence[Mapping[str, Any]],
        *,
        bundle_hash72: str,
        expected_frontier_hash72: str,
        now_ns: int,
    ) -> list[dict[str, Any]]:
        if len(approvals) != 2:
            raise Pass200BError("exactly two promotion approvals are required")
        normalized = [_copy(dict(item)) for item in approvals]
        principals = {str(item.get("principal_id") or "") for item in normalized}
        capabilities = {str(item.get("capability") or "") for item in normalized}
        receipts = {str(item.get("receipt_hash72") or "") for item in normalized}
        if "" in principals or len(principals) != 2:
            raise Pass200BError("promotion approvals require two distinct principals")
        if capabilities != REQUIRED_CAPABILITIES:
            raise Pass200BError("promotion approvals lack compiler/runtime capability separation")
        if len(receipts) != 2:
            raise Pass200BError("promotion approvals require two distinct VM81 receipts")
        for item in normalized:
            approval_hash72 = item.pop("approval_hash72", None)
            if hash72("pass200b.approval", item) != approval_hash72:
                raise Pass200BError("promotion approval identity mismatch")
            item["approval_hash72"] = approval_hash72
            _require_hash72(item.get("receipt_hash72"), "approval receipt_hash72")
            if item.get("bundle_hash72") != bundle_hash72:
                raise Pass200BError("promotion approval is bound to another bundle")
            if item.get("expected_frontier_hash72") != expected_frontier_hash72:
                raise Pass200BError("promotion approval is stale for the current frontier")
            if int(item.get("expires_at_ns", 0)) <= now_ns:
                raise Pass200BError("promotion approval expired")
        return sorted(normalized, key=lambda item: item["capability"])

    def _qualified_bundle(self, bundle_id: str) -> dict[str, Any]:
        status = self.pass200a.status()
        if status.get("closed") is not True:
            raise Pass200BError("Pass 200A proof authority is not closed")
        if int(status.get("candidate_activation_count", -1)) != 0:
            raise Pass200BError("Pass 200A contains an unexpected candidate activation")
        bundle = self.pass200a.get_bundle(str(bundle_id))
        if bundle.get("status") != "COMPILER_CANDIDATE":
            raise Pass200BError("bundle is not a compiler candidate")
        if bundle.get("compiler_mode") != "SHADOW":
            raise Pass200BError("bundle did not complete the shadow membrane")
        shadows = [
            item
            for item in self.pass200a.list_shadow_runs()
            if item.get("bundle_id") == bundle.get("bundle_id")
            and item.get("status") == "MATCH"
            and item.get("candidate_activated") is False
        ]
        if not shadows:
            raise Pass200BError("bundle lacks a verified Pass 200A shadow match")
        return bundle

    def admit_canary(
        self,
        bundle_id: str,
        *,
        invocation_limit: int,
        canary_numerator: int,
        canary_denominator: int,
        approvals: Sequence[Mapping[str, Any]],
        vm81_activation_receipt_hash72: str | None,
        expires_at_ns: int,
        now_ns: int | None = None,
    ) -> dict[str, Any]:
        now = int(time.time_ns() if now_ns is None else now_ns)
        limit = int(invocation_limit)
        numerator = int(canary_numerator)
        denominator = int(canary_denominator)
        if limit < 1 or limit > MAX_INVOCATION_LIMIT:
            raise ValueError(f"invocation_limit must be in [1,{MAX_INVOCATION_LIMIT}]")
        if denominator < 1 or numerator < 1 or numerator > denominator:
            raise ValueError("canary ratio must satisfy 1 <= numerator <= denominator")
        expiry = int(expires_at_ns)
        if expiry <= now:
            raise Pass200BError("canary admission expiry must be in the future")
        activation_receipt = _require_hash72(
            vm81_activation_receipt_hash72, "vm81_activation_receipt_hash72"
        )
        bundle = self._qualified_bundle(bundle_id)
        with self._lock:
            current = self.current_frontier()
            if current["mode"] == "CANARY":
                raise Pass200BError("an unclosed canary frontier is already active")
            normalized_approvals = self._validate_approvals(
                approvals,
                bundle_hash72=bundle["bundle_hash72"],
                expected_frontier_hash72=current["frontier_hash72"],
                now_ns=now,
            )
            body = {
                "schema": FRONTIER_SCHEMA,
                "version": VERSION,
                "contract": CONTRACT,
                "mode": "CANARY",
                "reason": "EXPLICIT_DUAL_APPROVAL_CANARY_ADMISSION",
                "predecessor_frontier_id": current["frontier_id"],
                "restored_frontier_id": None,
                "bundle_id": bundle["bundle_id"],
                "bundle_hash72": bundle["bundle_hash72"],
                "proof_hash72": bundle["proof_hash72"],
                "invocation_limit": limit,
                "canary_numerator": numerator,
                "canary_denominator": denominator,
                "expires_at_ns": expiry,
                "approvals": normalized_approvals,
                "vm81_activation_receipt_hash72": activation_receipt,
                "singleton_activation_commit_count": 1,
                "candidate_self_authorization": False,
                "automatic_active_promotion": False,
                "automatic_frozen_constraint_promotion": False,
                "created_at_ns": now,
            }
            frontier_id = hash72("pass200b.frontier.identity", body)
            document = {**body, "frontier_id": frontier_id}
            document["frontier_hash72"] = hash72("pass200b.frontier", document)
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "SINGLETON_CANARY_FRONTIER_ACTIVATED",
                    {
                        "frontier_id": frontier_id,
                        "bundle_id": bundle["bundle_id"],
                        "invocation_limit": limit,
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
                        "CANARY",
                        document["reason"],
                        canonical_json(document),
                        event_id,
                    ),
                )
                self._db.execute(
                    "INSERT INTO canary_counters(frontier_id,invocation_limit,invocations_used,candidate_returns,reference_returns) VALUES(?,?,?,?,?)",
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
        canary: Mapping[str, Any],
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
            "predecessor_frontier_id": canary["frontier_id"],
            "restored_frontier_id": canary.get("predecessor_frontier_id"),
            "bundle_id": None,
            "rollback_of_bundle_id": canary.get("bundle_id"),
            "vm81_transition_receipt_hash72": receipt_hash72,
            "singleton_activation_commit_count": 1,
            "candidate_self_authorization": False,
            "candidate_return_enabled": False,
            "created_at_ns": int(now_ns),
        }
        frontier_id = hash72("pass200b.frontier.identity", body)
        document = {**body, "frontier_id": frontier_id}
        document["frontier_hash72"] = hash72("pass200b.frontier", document)
        event_id, event_hash = self._event(
            self._db,
            "REFERENCE_FRONTIER_RESTORED",
            {
                "frontier_id": frontier_id,
                "canary_frontier_id": canary["frontier_id"],
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
                canary["frontier_id"],
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

    def execute_canary(
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
                raise Pass200BError("stale canary frontier invocation")
            if current["mode"] != "CANARY":
                raise Pass200BError("current frontier is not a canary")
            counter = current.get("counter") or {}
            used = int(counter.get("invocations_used", 0))
            limit = int(counter.get("invocation_limit", current["invocation_limit"]))
            if used >= limit:
                raise Pass200BError("canary invocation budget is exhausted")
            if now >= int(current["expires_at_ns"]):
                try:
                    self._db.execute("BEGIN IMMEDIATE")
                    restored = self._reference_transition_locked(
                        current,
                        mode="ROLLED_BACK",
                        reason="CANARY_EXPIRED",
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
                    "reason": "CANARY_EXPIRED",
                    "returned_path": "REFERENCE",
                    "returned_result": _copy(reference_result),
                    "restored_frontier": restored,
                    "candidate_activated": False,
                }
            exact_match = canonical_json(reference_result) == canonical_json(candidate_result)
            witness_match = reference_witness == candidate_witness
            replay_match = reference_replay == candidate_replay
            all_match = exact_match and witness_match and replay_match
            ordinal = used
            selected = (ordinal % int(current["canary_denominator"])) < int(
                current["canary_numerator"]
            )
            returned_path = "CANDIDATE" if selected and all_match else "REFERENCE"
            invocation_body = {
                "schema": INVOCATION_SCHEMA,
                "version": VERSION,
                "contract": CONTRACT,
                "frontier_id": current["frontier_id"],
                "frontier_hash72": current["frontier_hash72"],
                "bundle_id": current["bundle_id"],
                "ordinal": ordinal,
                "selected_for_candidate_return": selected,
                "exact_match": exact_match,
                "witness_match": witness_match,
                "replay_match": replay_match,
                "returned_path": returned_path,
                "invocation_receipt_hash72": receipt,
                "reference_result_hash72": hash72("pass200b.result.reference", reference_result),
                "candidate_result_hash72": hash72("pass200b.result.candidate", candidate_result),
                "reference_witness_hash72": reference_witness,
                "candidate_witness_hash72": candidate_witness,
                "reference_replay_hash72": reference_replay,
                "candidate_replay_hash72": candidate_replay,
                "candidate_self_authorization": False,
                "created_at_ns": now,
            }
            invocation_id = hash72("pass200b.invocation.identity", invocation_body)
            invocation = {**invocation_body, "invocation_id": invocation_id}
            invocation["invocation_hash72"] = hash72("pass200b.invocation", invocation)
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "CANARY_INVOCATION_METERED",
                    {
                        "invocation_id": invocation_id,
                        "frontier_id": current["frontier_id"],
                        "ordinal": ordinal,
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
                        ordinal,
                        returned_path,
                        1 if all_match else 0,
                        canonical_json(invocation),
                        event_id,
                    ),
                )
                self._db.execute(
                    "UPDATE canary_counters SET invocations_used=invocations_used+1,candidate_returns=candidate_returns+?,reference_returns=reference_returns+? WHERE frontier_id=?",
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
                        reason="EXACT_CANARY_MISMATCH",
                        receipt_hash72=receipt,
                        now_ns=now,
                    )
                    returned_path = "REFERENCE"
                elif used + 1 >= limit:
                    restored = self._reference_transition_locked(
                        current,
                        mode="EXHAUSTED",
                        reason="CANARY_INVOCATION_LIMIT_REACHED",
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
                "reason": "CANARY_MATCH" if all_match else "CANARY_MISMATCH",
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
            raise Pass200BError("stale canary frontier probe")
        shadows = [
            item
            for item in self.pass200a.list_shadow_runs()
            if item.get("bundle_id") == current.get("bundle_id")
            and item.get("status") == "MATCH"
        ]
        if not shadows:
            raise Pass200BError("canary bundle lacks a verified shadow observation")
        shadow = shadows[-1]
        semantic = shadow["reference_semantic_root_hash72"]
        replay = shadow["reference_replay_root_hash72"]
        observation = {
            "bundle_id": current["bundle_id"],
            "semantic_root_hash72": semantic,
            "replay_root_hash72": replay,
        }
        return self.execute_canary(
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
                raise Pass200BError("stale rollback frontier")
            if current["mode"] != "CANARY":
                raise Pass200BError("only an active canary frontier can be rolled back")
            try:
                self._db.execute("BEGIN IMMEDIATE")
                restored = self._reference_transition_locked(
                    current,
                    mode="ROLLED_BACK",
                    reason=str(reason or "EXPLICIT_ROLLBACK"),
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
            if hash72("pass200b.event", body) != row["event_hash72"]:
                return {"ok": False, "reason": "event identity mismatch", "sequence": row["seq"]}
            predecessor = row["event_hash72"]
        return {"ok": True, "event_count": count, "tip_hash72": predecessor}

    def verify(self) -> dict[str, Any]:
        frontiers = self.list_frontiers()
        current = self.current_frontier()
        chain = self.verify_event_chain()
        if not chain["ok"]:
            raise Pass200BError("Pass 200B event chain is invalid")
        activation_commits = sum(
            int(item.get("singleton_activation_commit_count", 0))
            for item in frontiers
            if item.get("mode") == "CANARY"
        )
        if any(item.get("candidate_self_authorization") for item in frontiers):
            raise Pass200BError("candidate self-authorization detected")
        return {
            "schema": "HHS_PASS_200B_VERIFICATION_V1",
            "version": VERSION,
            "contract": CONTRACT,
            "ok": True,
            "frontier_count": len(frontiers),
            "current_frontier_id": current["frontier_id"],
            "current_mode": current["mode"],
            "canary_frontier_count": sum(item["mode"] == "CANARY" for item in frontiers),
            "rollback_frontier_count": sum(item["mode"] == "ROLLED_BACK" for item in frontiers),
            "exhausted_frontier_count": sum(item["mode"] == "EXHAUSTED" for item in frontiers),
            "singleton_activation_commit_count": activation_commits,
            "invocation_count": int(
                self._db.execute("SELECT COUNT(*) FROM invocations").fetchone()[0]
            ),
            "event_chain": chain,
            "automatic_active_promotion": False,
            "automatic_frozen_constraint_promotion": False,
        }

    def status(self) -> dict[str, Any]:
        verification = self.verify()
        current = self.current_frontier()
        totals = self._db.execute(
            "SELECT COALESCE(SUM(invocations_used),0),COALESCE(SUM(candidate_returns),0),COALESCE(SUM(reference_returns),0) FROM canary_counters"
        ).fetchone()
        result = {
            "schema": "HHS_PASS_200B_STATUS_V1",
            "version": VERSION,
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "closed": verification["canary_frontier_count"] >= 1,
            "current_frontier": current,
            "total_invocations": int(totals[0]),
            "candidate_returns": int(totals[1]),
            "reference_returns": int(totals[2]),
            "candidate_self_authorization": False,
            "active_mode_enabled": False,
            "frozen_constraint_enabled": False,
            **verification,
        }
        result["status_hash72"] = hash72("pass200b.status", result)
        return result


PASS200B_CANARY_AUTHORITY = Pass200BGovernedCanaryAuthority()

__all__ = [
    "APPROVAL_SCHEMA",
    "CLASSIFICATION",
    "CONTRACT",
    "EVENT_SCHEMA",
    "FRONTIER_SCHEMA",
    "INVOCATION_SCHEMA",
    "MAX_INVOCATION_LIMIT",
    "PASS200B_CANARY_AUTHORITY",
    "Pass200BError",
    "Pass200BGovernedCanaryAuthority",
    "REQUIRED_CAPABILITIES",
    "VERSION",
]
