"""Governed Pass 205 continuation authority and reconstructive replay.

This additive projection preserves the validated V1 storage/compute engine while
placing the production mutation boundary behind the singleton VM81 runtime
controller. A new continuation is persisted only after an authorized runtime
step and Hash72 commit. Replay reconstructs each child from the ordered stored
delta rather than trusting stored child payloads.
"""
from __future__ import annotations

import sqlite3
from typing import Any, Callable, Mapping, Sequence

from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
    CLASSIFICATION,
    CLOSURE_CLASSIFICATION,
    CONTRACT,
    SCHEMA,
    ContinuationRejected,
    Pass205ContinuationRuntime,
    _canonical_bytes,
    _json,
    _learning_full,
    _learning_sparse,
    _normalize_events,
    _now_ms,
)

AuthorityProvider = Callable[[str], Mapping[str, Any]]
BLOCKED_AUTHORITY_STATES = {"LOCKED", "QUARANTINED", "REJECTED", "HALTED"}


def _default_authority_provider(source: str) -> Mapping[str, Any]:
    # Lazy import avoids creating a second controller and keeps one production
    # runtime/receipt owner across all API modules.
    from hhs_backend.api.runtime_routes import runtime_controller

    return runtime_controller.authorized_tick(source=source)


def _authority_state_labels(packet: Mapping[str, Any]) -> set[str]:
    labels: set[str] = set()
    stack: list[Any] = [packet]
    while stack:
        value = stack.pop()
        if isinstance(value, Mapping):
            for key, child in value.items():
                if str(key).lower() in {
                    "state", "status", "classification", "lifecycle_state",
                    "authority_state", "closure_state",
                } and isinstance(child, str):
                    labels.add(child.upper())
                elif isinstance(child, (Mapping, list, tuple)):
                    stack.append(child)
        elif isinstance(value, (list, tuple)):
            stack.extend(value)
    return labels


def _extract_authority_admission(packet: Mapping[str, Any]) -> dict[str, Any]:
    runtime = dict(packet.get("runtime") or {})
    receipt = dict(packet.get("receipt") or {})
    audit = dict(packet.get("authority_audit") or receipt.get("authority_audit") or {})
    receipt_hash72 = str(receipt.get("receipt_hash72") or runtime.get("receipt_hash72") or "")
    labels = _authority_state_labels(packet)
    blocked = sorted(labels & BLOCKED_AUTHORITY_STATES)
    if blocked:
        raise ContinuationRejected("VM81 authority blocked continuation: " + ",".join(blocked))
    if runtime.get("halted") is True:
        raise ContinuationRejected("VM81 authority is halted")
    if not audit or audit.get("ok") is not True:
        reasons = audit.get("reasons") if audit else ["authority audit missing"]
        raise ContinuationRejected("VM81 authority audit rejected continuation: " + "; ".join(map(str, reasons)))
    if len(receipt_hash72) != 72:
        raise ContinuationRejected("VM81 authority did not produce a canonical Hash72 receipt")
    return {
        "schema": "HHS_PASS_205_VM81_ADMISSION_V1",
        "ok": True,
        "receipt_hash72": receipt_hash72,
        "runtime_step": runtime.get("step"),
        "state_hash72": receipt.get("state_hash72") or runtime.get("state_hash72"),
        "authority_audit": audit,
        "authority_labels": sorted(labels),
    }


class GovernedPass205ContinuationRuntime(Pass205ContinuationRuntime):
    """Production Pass 205 runtime with singleton VM81 mutation admission."""

    def __init__(
        self,
        db_path=None,
        *,
        authority_provider: AuthorityProvider | None = None,
    ) -> None:
        self._authority_provider = authority_provider or _default_authority_provider
        super().__init__(db_path)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS vm81_admissions (
                    continuation_root216 TEXT PRIMARY KEY,
                    vm81_receipt_hash72 TEXT NOT NULL UNIQUE,
                    native_receipt_witness_hash72 TEXT NOT NULL,
                    runtime_step INTEGER,
                    state_hash72 TEXT,
                    authority_json TEXT NOT NULL,
                    created_at_unix_ms INTEGER NOT NULL,
                    FOREIGN KEY(continuation_root216) REFERENCES snapshots(continuation_root216)
                );
                """
            )

    def configure_authority(self, provider: AuthorityProvider) -> None:
        if not callable(provider):
            raise TypeError("Pass 205 authority provider must be callable")
        self._authority_provider = provider

    def _admission(self, root216: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM vm81_admissions WHERE continuation_root216=?",
                (str(root216),),
            ).fetchone()
        if row is None:
            return None
        payload = dict(__import__("json").loads(str(row["authority_json"])))
        payload.update(
            {
                "continuation_root216": str(row["continuation_root216"]),
                "vm81_receipt_hash72": str(row["vm81_receipt_hash72"]),
                "native_receipt_witness_hash72": str(row["native_receipt_witness_hash72"]),
                "runtime_step": row["runtime_step"],
                "state_hash72": row["state_hash72"],
                "created_at_unix_ms": int(row["created_at_unix_ms"]),
            }
        )
        return payload

    def _persist_governed(
        self,
        *,
        parent: Mapping[str, Any],
        state: Sequence[int],
        projection: Sequence[Sequence[int]],
        learning: Sequence[int],
        frontier_cells: Sequence[int],
        events: Sequence[Mapping[str, int]],
        token: Mapping[str, Any],
        native_receipt_witness_hash72: str,
        admission: Mapping[str, Any],
    ) -> dict[str, Any]:
        payload = {
            "schema": SCHEMA,
            "contract": CONTRACT,
            **dict(token),
            "vm81_admission": dict(admission),
            "native_receipt_witness_hash72": native_receipt_witness_hash72,
        }
        now = _now_ms()
        with self._transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM snapshots WHERE continuation_root216=?",
                (token["continuation_root216"],),
            ).fetchone()
            if existing is not None:
                result = self._decode_row(existing)
                prior = connection.execute(
                    "SELECT authority_json FROM vm81_admissions WHERE continuation_root216=?",
                    (token["continuation_root216"],),
                ).fetchone()
                if prior is None:
                    raise ContinuationRejected("existing continuation lacks VM81 admission witness")
                result["vm81_admission"] = __import__("json").loads(str(prior["authority_json"]))
                return result
            connection.execute(
                """
                INSERT INTO snapshots (
                    continuation_root216,parent_root216,generation,content_root216,delta_root216,
                    hydration_root216,dependency_root216,projection_root216,learning_root216,
                    parent_receipt_hash72,receipt_hash72,schema_root216,constraint_root216,
                    state_json,projection_json,learning_json,frontier_json,event_count,created_at_unix_ms
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    token["continuation_root216"], token["parent_root216"], token["generation"],
                    token["content_root216"], token["delta_root216"], token["hydration_root216"],
                    token["dependency_root216"], token["projection_root216"], token["learning_root216"],
                    token["parent_receipt_hash72"], token["receipt_hash72"],
                    parent["schema_root216"], parent["constraint_root216"],
                    _json(state), _json(projection), _json(learning), _json(list(frontier_cells)),
                    len(events), now,
                ),
            )
            connection.execute(
                "INSERT OR IGNORE INTO deltas VALUES (?,?,?,?)",
                (
                    token["delta_root216"], _json(list(events)), token["hydration_root216"],
                    token["dependency_root216"],
                ),
            )
            connection.execute(
                "INSERT INTO lineage VALUES (?,?,?)",
                (token["parent_root216"], token["continuation_root216"], token["generation"]),
            )
            connection.execute(
                "INSERT INTO vectors VALUES (?,?,?,?)",
                (
                    token["continuation_root216"], parent["schema_root216"],
                    parent["constraint_root216"], _json(learning),
                ),
            )
            connection.execute(
                "INSERT INTO receipts VALUES (?,?,?,?)",
                (
                    token["receipt_hash72"], token["parent_receipt_hash72"],
                    token["continuation_root216"], _json(payload),
                ),
            )
            connection.execute(
                "INSERT INTO vm81_admissions VALUES (?,?,?,?,?,?,?)",
                (
                    token["continuation_root216"], token["receipt_hash72"],
                    native_receipt_witness_hash72, admission.get("runtime_step"),
                    admission.get("state_hash72"), _json(dict(admission)), now,
                ),
            )
        result = self.snapshot(str(token["continuation_root216"]))
        result["vm81_admission"] = dict(admission)
        result["native_receipt_witness_hash72"] = native_receipt_witness_hash72
        return result

    def advance(
        self,
        *,
        parent_root216: str,
        events: Sequence[Mapping[str, Any]],
        expected_parent_receipt_hash72: str | None = None,
        frontier_cells: Sequence[int] | None = None,
    ) -> dict[str, Any]:
        normalized = _normalize_events(events)
        with self._mutation_lock:
            parent = self.snapshot(parent_root216)
            if expected_parent_receipt_hash72 is not None and (
                expected_parent_receipt_hash72 != parent["receipt_hash72"]
            ):
                raise ContinuationRejected("parent Hash72 receipt mismatch")
            child_state, required_bits, _, _ = self.native.apply_delta(parent["state_words"], normalized)
            required_frontier = [index for index, enabled in enumerate(required_bits) if enabled]
            chosen_frontier = required_frontier if frontier_cells is None else sorted({int(x) for x in frontier_cells})
            if chosen_frontier != required_frontier:
                raise ContinuationRejected(
                    "dependency frontier must exactly equal the native dependency-complete minimum"
                )
            if not self.native.validate_frontier(normalized, chosen_frontier):
                raise ContinuationRejected("incomplete dependency frontier")
            sparse_projection = self.native.project_sparse(
                child_state, parent["projection_channels"], chosen_frontier
            )
            full_projection = self.native.project_full(child_state)
            if sparse_projection != full_projection:
                raise ContinuationRejected("sparse projection differs from full deterministic recomputation")
            sparse_learning = _learning_sparse(
                parent["learning_features"], child_state, sparse_projection, chosen_frontier
            )
            full_learning = _learning_full(child_state, full_projection)
            if sparse_learning != full_learning:
                raise ContinuationRejected("sparse learning hydration differs from full recomputation")
            token = self.native.build_token(
                parent_root=parent["continuation_root216"],
                content_root=self.native.state_root(child_state),
                delta_root=self.native.delta_root(normalized),
                hydration_root=self.native.hydration_root(normalized),
                dependency_root=self.native.frontier_root(chosen_frontier),
                projection_root=self.native.projection_root(sparse_projection),
                learning_root=self.native.hash216_bytes(_canonical_bytes(sparse_learning)),
                parent_receipt=parent["receipt_hash72"],
                generation=int(parent["generation"]) + 1,
            )
            with self._connect() as connection:
                existing = connection.execute(
                    "SELECT continuation_root216 FROM snapshots WHERE continuation_root216=?",
                    (token["continuation_root216"],),
                ).fetchone()
            if existing is not None:
                admission = self._admission(str(token["continuation_root216"]))
                if admission is None:
                    raise ContinuationRejected("existing continuation lacks VM81 admission witness")
                result = self.snapshot(str(token["continuation_root216"]))
                result["vm81_admission"] = admission
                result["existing_committed_continuation"] = True
                return result

            native_receipt = str(token["receipt_hash72"])
            authority_packet = self._authority_provider(
                "GovernedPass205ContinuationRuntime.advance:"
                + str(token["continuation_root216"])[:24]
            )
            admission = _extract_authority_admission(authority_packet)
            token = dict(token)
            token["receipt_hash72"] = admission["receipt_hash72"]
            return self._persist_governed(
                parent=parent,
                state=child_state,
                projection=sparse_projection,
                learning=sparse_learning,
                frontier_cells=chosen_frontier,
                events=normalized,
                token=token,
                native_receipt_witness_hash72=native_receipt,
                admission=admission,
            )

    def verify(self, continuation_root216: str) -> dict[str, Any]:
        result = super().verify(continuation_root216)
        snapshot = self.snapshot(continuation_root216)
        if int(snapshot["generation"]) == 0:
            return result
        admission = self._admission(continuation_root216)
        reasons = [reason for reason in result["reasons"] if reason != "RECEIPT_HASH72_MISMATCH"]
        if admission is None:
            reasons.append("VM81_ADMISSION_MISSING")
        else:
            if admission["vm81_receipt_hash72"] != snapshot["receipt_hash72"]:
                reasons.append("VM81_RECEIPT_MISMATCH")
            if admission.get("authority_audit", {}).get("ok") is not True:
                reasons.append("VM81_AUTHORITY_AUDIT_REJECTED")
            native_token = self.native.build_token(
                parent_root=snapshot["parent_root216"],
                content_root=snapshot["content_root216"],
                delta_root=snapshot["delta_root216"],
                hydration_root=snapshot["hydration_root216"],
                dependency_root=snapshot["dependency_root216"],
                projection_root=snapshot["projection_root216"],
                learning_root=snapshot["learning_root216"],
                parent_receipt=snapshot["parent_receipt_hash72"],
                generation=int(snapshot["generation"]),
            )
            if native_token["receipt_hash72"] != admission["native_receipt_witness_hash72"]:
                reasons.append("NATIVE_RECEIPT_WITNESS_MISMATCH")
        result.update(
            {
                "ok": not reasons,
                "classification": CLOSURE_CLASSIFICATION if not reasons else "HHS_PASS_205_CONTINUATION_REJECTED",
                "reasons": reasons,
                "vm81_admission": admission,
                "single_vm81_mutation_authority": True,
            }
        )
        return result

    def replay(self, continuation_root216: str) -> dict[str, Any]:
        chain: list[dict[str, Any]] = []
        cursor = self.snapshot(continuation_root216)
        while True:
            chain.append(cursor)
            if int(cursor["generation"]) == 0:
                break
            cursor = self.snapshot(str(cursor["parent_root216"]))
        chain.reverse()

        failures: list[dict[str, Any]] = []
        boundary = chain[0]
        reconstructed_state = list(boundary["state_words"])
        reconstructed_projection = self.native.project_full(reconstructed_state)
        reconstructed_learning = _learning_full(reconstructed_state, reconstructed_projection)
        if self.native.state_root(reconstructed_state) != boundary["content_root216"]:
            failures.append({"generation": 0, "reason": "GENESIS_CONTENT_RECONSTRUCTION_MISMATCH"})

        parent = boundary
        for stored in chain[1:]:
            generation = int(stored["generation"])
            generation_reasons: list[str] = []
            events = self._delta_events(str(stored["delta_root216"]))
            child_state, frontier_bits, _, _ = self.native.apply_delta(reconstructed_state, events)
            frontier = [index for index, enabled in enumerate(frontier_bits) if enabled]
            if frontier != list(stored["frontier_cells"]):
                generation_reasons.append("FRONTIER_RECONSTRUCTION_MISMATCH")
            sparse_projection = self.native.project_sparse(child_state, reconstructed_projection, frontier)
            full_projection = self.native.project_full(child_state)
            if sparse_projection != full_projection:
                generation_reasons.append("SPARSE_FULL_PROJECTION_MISMATCH")
            child_learning = _learning_full(child_state, full_projection)
            roots = {
                "content_root216": self.native.state_root(child_state),
                "delta_root216": self.native.delta_root(events),
                "hydration_root216": self.native.hydration_root(events),
                "dependency_root216": self.native.frontier_root(frontier),
                "projection_root216": self.native.projection_root(full_projection),
                "learning_root216": self.native.hash216_bytes(_canonical_bytes(child_learning)),
            }
            for key, value in roots.items():
                if value != stored[key]:
                    generation_reasons.append(key.upper() + "_RECONSTRUCTION_MISMATCH")
            native_token = self.native.build_token(
                parent_root=parent["continuation_root216"],
                parent_receipt=parent["receipt_hash72"],
                generation=generation,
                **roots,
            )
            if native_token["continuation_root216"] != stored["continuation_root216"]:
                generation_reasons.append("CONTINUATION_ROOT_RECONSTRUCTION_MISMATCH")
            admission = self._admission(str(stored["continuation_root216"]))
            if admission is None:
                generation_reasons.append("VM81_ADMISSION_MISSING")
            else:
                if admission["vm81_receipt_hash72"] != stored["receipt_hash72"]:
                    generation_reasons.append("VM81_RECEIPT_RECONSTRUCTION_MISMATCH")
                if native_token["receipt_hash72"] != admission["native_receipt_witness_hash72"]:
                    generation_reasons.append("NATIVE_RECEIPT_WITNESS_RECONSTRUCTION_MISMATCH")
            if child_state != list(stored["state_words"]):
                generation_reasons.append("STATE_PAYLOAD_RECONSTRUCTION_MISMATCH")
            if full_projection != stored["projection_channels"]:
                generation_reasons.append("PROJECTION_PAYLOAD_RECONSTRUCTION_MISMATCH")
            if child_learning != stored["learning_features"]:
                generation_reasons.append("LEARNING_PAYLOAD_RECONSTRUCTION_MISMATCH")
            if generation_reasons:
                failures.append({
                    "generation": generation,
                    "continuation_root216": stored["continuation_root216"],
                    "reasons": generation_reasons,
                })
            reconstructed_state = child_state
            reconstructed_projection = full_projection
            reconstructed_learning = child_learning
            parent = stored

        return {
            "schema": "HHS_PASS_205_RECONSTRUCTIVE_REPLAY_V2",
            "contract": CONTRACT,
            "classification": CLOSURE_CLASSIFICATION if not failures else "HHS_PASS_205_REPLAY_REJECTED",
            "ok": not failures,
            "target_root216": continuation_root216,
            "generation_count": len(chain),
            "ordered_roots216": [snapshot["continuation_root216"] for snapshot in chain],
            "ordered_receipts_hash72": [snapshot["receipt_hash72"] for snapshot in chain],
            "reconstructed_from_ordered_deltas": True,
            "reconstructed_target_state_words": reconstructed_state,
            "reconstructed_target_learning_features": reconstructed_learning,
            "failures": failures,
        }

    def status(self) -> dict[str, Any]:
        result = super().status()
        with self._connect() as connection:
            admission_count = int(connection.execute("SELECT COUNT(*) FROM vm81_admissions").fetchone()[0])
        result.update(
            {
                "schema": "HHS_PASS_205_GOVERNED_CONTINUATION_RUNTIME_STATUS_V2",
                "production_runtime_active": True,
                "single_vm81_mutation_authority": True,
                "single_ordered_hash72_commit_stream": True,
                "vm81_admission_required_before_persistence": True,
                "vm81_admission_count": admission_count,
                "replay_reconstructs_ordered_deltas": True,
                "v1_engine_is_storage_compute_substrate": True,
            }
        )
        return result


GOVERNED_PASS205_CONTINUATION_RUNTIME = GovernedPass205ContinuationRuntime()


__all__ = [
    "GOVERNED_PASS205_CONTINUATION_RUNTIME",
    "GovernedPass205ContinuationRuntime",
]
