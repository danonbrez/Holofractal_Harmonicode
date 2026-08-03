"""Pass 205 production deterministic multimodal continuation runtime.

The service has one mutation authority, preserves parent-addressed Hash216
lineage, commits one ordered Hash72 receipt per admitted continuation, stores
all prior snapshots, and verifies sparse state/projection/learning hydration
against full deterministic recomputation before persistence.
"""
from __future__ import annotations

import json
import os
import pathlib
import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Any, Iterable, Mapping, Sequence

from hhs_python.runtime.hhs_pass205_continuation_bridge import (
    CELL_COUNT,
    CONTROL_COUNT,
    PROJECTION_CHANNELS,
    Q_COUNT,
    STATE_BITS,
    UINT64_MASK,
    Pass205NativeBridge,
)

CONTRACT = "HHS-P205-VM5184-G243-DETERMINISTIC-MULTIMODAL-CONTINUATION-GAMING-ML-H72-H216"
CLASSIFICATION = "HHS_PASS_205_PRODUCTION_CONTINUATION_RUNTIME_ACTIVE"
CLOSURE_CLASSIFICATION = "HHS_PASS_205_DETERMINISTIC_MULTIMODAL_CONTINUATION_RUNTIME_VERIFIED"
SCHEMA = "HHS_PASS_205_CONTINUATION_SNAPSHOT_V1"
API_PREFIX = "/api/runtime/continuation"
DEFAULT_SCHEMA_ROOT_LABEL = "HHS_PASS205_VM5184_G243_STATE_SCHEMA_V1"
DEFAULT_CONSTRAINT_ROOT_LABEL = "HHS_PASS205_INHERITED_VM81_HASH72_HASH216_CONSTRAINTS_V1"
ZERO_STATE = [0] * CELL_COUNT


class ContinuationError(RuntimeError):
    pass


class ContinuationNotFound(ContinuationError):
    pass


class ContinuationRejected(ContinuationError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")


def _json(value: Any) -> str:
    return _canonical_bytes(value).decode("utf-8")


def _parse_json(value: str) -> Any:
    return json.loads(value)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _default_db_path() -> pathlib.Path:
    configured = os.environ.get("HHS_PASS205_DB", "").strip()
    if configured:
        return pathlib.Path(configured).expanduser().resolve()
    root = pathlib.Path(__file__).resolve().parents[2]
    return root / "state" / "pass205" / "continuation.sqlite3"


def _validate_words(words: Sequence[int]) -> list[int]:
    if len(words) != CELL_COUNT:
        raise ContinuationRejected(f"state requires exactly {CELL_COUNT} uint64 words")
    result: list[int] = []
    for index, value in enumerate(words):
        integer = int(value)
        if integer < 0 or integer > UINT64_MASK:
            raise ContinuationRejected(f"state word {index} is outside uint64")
        result.append(integer)
    return result


def _normalize_events(events: Sequence[Mapping[str, Any]]) -> list[dict[str, int]]:
    normalized: list[dict[str, int]] = []
    seen: set[int] = set()
    if len(events) > CELL_COUNT:
        raise ContinuationRejected(f"delta supports at most {CELL_COUNT} cell events")
    for position, event in enumerate(events):
        try:
            cell = int(event["cell"])
            control_g = int(event["control_g"])
            xor_mask = int(event["xor_mask"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ContinuationRejected(f"invalid event at position {position}") from exc
        if cell < 0 or cell >= CELL_COUNT:
            raise ContinuationRejected(f"invalid cell index: {cell}")
        if cell in seen:
            raise ContinuationRejected(f"duplicate cell mutation in one continuation: {cell}")
        if control_g < 0 or control_g >= CONTROL_COUNT:
            raise ContinuationRejected(f"invalid control_g: {control_g}")
        if xor_mask <= 0 or xor_mask > UINT64_MASK:
            raise ContinuationRejected(f"invalid xor_mask: {xor_mask}")
        seen.add(cell)
        normalized.append({
            "position": position,
            "cell": cell,
            "control_g": control_g,
            "xor_mask": xor_mask,
        })
    if not normalized:
        raise ContinuationRejected("a continuation requires at least one state change")
    return normalized


def _learning_cell(state_word: int, projection: Sequence[Sequence[int]], cell: int) -> int:
    value = int(state_word) & UINT64_MASK
    for channel in range(PROJECTION_CHANNELS):
        shift = (channel * 7 + cell) & 63
        word = int(projection[channel][cell]) & 0xFFFFFFFF
        value ^= ((word << shift) | (word >> ((64 - shift) & 63))) & UINT64_MASK
        value = (value * 0x9E3779B97F4A7C15 + channel + cell + 1) & UINT64_MASK
    return value


def _learning_full(state: Sequence[int], projection: Sequence[Sequence[int]]) -> list[int]:
    return [_learning_cell(state[cell], projection, cell) for cell in range(CELL_COUNT)]


def _learning_sparse(
    parent_features: Sequence[int],
    child_state: Sequence[int],
    child_projection: Sequence[Sequence[int]],
    frontier: Iterable[int],
) -> list[int]:
    result = [int(value) for value in parent_features]
    for cell in frontier:
        result[int(cell)] = _learning_cell(child_state[int(cell)], child_projection, int(cell))
    return result


def _popcount_distance(a: Sequence[int], b: Sequence[int]) -> int:
    return sum((int(left) ^ int(right)).bit_count() for left, right in zip(a, b))


class Pass205ContinuationRuntime:
    """Single-authority continuation runtime and persistent snapshot graph."""

    def __init__(self, db_path: str | pathlib.Path | None = None) -> None:
        self.native = Pass205NativeBridge()
        self.db_path = pathlib.Path(db_path) if db_path is not None else _default_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._mutation_lock = threading.RLock()
        self._configure_database()
        self.schema_root216 = self.native.hash216_bytes(DEFAULT_SCHEMA_ROOT_LABEL.encode("utf-8"))
        self.constraint_root216 = self.native.hash216_bytes(DEFAULT_CONSTRAINT_ROOT_LABEL.encode("utf-8"))
        self.genesis_root216 = self._ensure_genesis()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.db_path), timeout=30.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    @contextmanager
    def _transaction(self):
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _configure_database(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    continuation_root216 TEXT PRIMARY KEY,
                    parent_root216 TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    content_root216 TEXT NOT NULL,
                    delta_root216 TEXT NOT NULL,
                    hydration_root216 TEXT NOT NULL,
                    dependency_root216 TEXT NOT NULL,
                    projection_root216 TEXT NOT NULL,
                    learning_root216 TEXT NOT NULL,
                    parent_receipt_hash72 TEXT NOT NULL,
                    receipt_hash72 TEXT NOT NULL UNIQUE,
                    schema_root216 TEXT NOT NULL,
                    constraint_root216 TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    projection_json TEXT NOT NULL,
                    learning_json TEXT NOT NULL,
                    frontier_json TEXT NOT NULL,
                    event_count INTEGER NOT NULL,
                    created_at_unix_ms INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS snapshots_parent_idx ON snapshots(parent_root216);
                CREATE INDEX IF NOT EXISTS snapshots_generation_idx ON snapshots(generation);
                CREATE TABLE IF NOT EXISTS deltas (
                    delta_root216 TEXT PRIMARY KEY,
                    events_json TEXT NOT NULL,
                    hydration_root216 TEXT NOT NULL,
                    dependency_root216 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS lineage (
                    parent_root216 TEXT NOT NULL,
                    child_root216 TEXT NOT NULL UNIQUE,
                    generation INTEGER NOT NULL,
                    PRIMARY KEY(parent_root216, child_root216)
                );
                CREATE INDEX IF NOT EXISTS lineage_parent_idx ON lineage(parent_root216);
                CREATE TABLE IF NOT EXISTS vectors (
                    continuation_root216 TEXT PRIMARY KEY,
                    schema_root216 TEXT NOT NULL,
                    constraint_root216 TEXT NOT NULL,
                    features_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS receipts (
                    receipt_hash72 TEXT PRIMARY KEY,
                    parent_receipt_hash72 TEXT NOT NULL,
                    continuation_root216 TEXT NOT NULL UNIQUE,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS retrievals (
                    retrieval_root216 TEXT PRIMARY KEY,
                    query_root216 TEXT NOT NULL,
                    selected_parent_root216 TEXT NOT NULL,
                    ranked_candidates_json TEXT NOT NULL,
                    rejected_candidates_json TEXT NOT NULL,
                    exact_delta_cost INTEGER NOT NULL,
                    created_at_unix_ms INTEGER NOT NULL
                );
                """
            )

    def _ensure_genesis(self) -> str:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT continuation_root216 FROM snapshots WHERE generation=0 ORDER BY created_at_unix_ms LIMIT 1"
            ).fetchone()
            if row is not None:
                return str(row["continuation_root216"])
        state = list(ZERO_STATE)
        projection = self.native.project_full(state)
        learning = _learning_full(state, projection)
        parent_root = self.native.hash216_bytes(b"HHS_PASS205_GENESIS_PARENT_V1")
        parent_receipt = self.native.hash216_bytes(b"HHS_PASS205_GENESIS_PARENT_RECEIPT_V1")[:72]
        empty_delta_root = self.native.hash216_bytes(b"HHS_PASS205_GENESIS_DELTA_V1")
        empty_hydration_root = self.native.hash216_bytes(b"HHS_PASS205_GENESIS_HYDRATION_V1")
        empty_dependency_root = self.native.frontier_root([])
        content_root = self.native.state_root(state)
        projection_root = self.native.projection_root(projection)
        learning_root = self.native.hash216_bytes(_canonical_bytes(learning))
        token = self.native.build_token(
            parent_root=parent_root,
            content_root=content_root,
            delta_root=empty_delta_root,
            hydration_root=empty_hydration_root,
            dependency_root=empty_dependency_root,
            projection_root=projection_root,
            learning_root=learning_root,
            parent_receipt=parent_receipt,
            generation=0,
        )
        now = _now_ms()
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO snapshots (
                    continuation_root216,parent_root216,generation,content_root216,delta_root216,
                    hydration_root216,dependency_root216,projection_root216,learning_root216,
                    parent_receipt_hash72,receipt_hash72,schema_root216,constraint_root216,
                    state_json,projection_json,learning_json,frontier_json,event_count,created_at_unix_ms
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    token["continuation_root216"], parent_root, 0, content_root, empty_delta_root,
                    empty_hydration_root, empty_dependency_root, projection_root, learning_root,
                    parent_receipt, token["receipt_hash72"], self.schema_root216,
                    self.constraint_root216, _json(state), _json(projection), _json(learning),
                    _json([]), 0, now,
                ),
            )
            connection.execute(
                "INSERT OR IGNORE INTO vectors VALUES (?,?,?,?)",
                (token["continuation_root216"], self.schema_root216, self.constraint_root216, _json(learning)),
            )
            connection.execute(
                "INSERT OR IGNORE INTO receipts VALUES (?,?,?,?)",
                (
                    token["receipt_hash72"], parent_receipt, token["continuation_root216"],
                    _json({"schema": SCHEMA, **token}),
                ),
            )
        return str(token["continuation_root216"])

    def _row(self, root216: str) -> sqlite3.Row:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM snapshots WHERE continuation_root216=?", (str(root216),)
            ).fetchone()
        if row is None:
            raise ContinuationNotFound(f"unknown continuation root: {root216}")
        return row

    @staticmethod
    def _decode_row(row: sqlite3.Row, *, include_payloads: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "schema": SCHEMA,
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "continuation_root216": str(row["continuation_root216"]),
            "parent_root216": str(row["parent_root216"]),
            "generation": int(row["generation"]),
            "content_root216": str(row["content_root216"]),
            "delta_root216": str(row["delta_root216"]),
            "ordered_event_control_root216": str(row["delta_root216"]),
            "hydration_root216": str(row["hydration_root216"]),
            "dependency_root216": str(row["dependency_root216"]),
            "projection_root216": str(row["projection_root216"]),
            "learning_root216": str(row["learning_root216"]),
            "parent_receipt_hash72": str(row["parent_receipt_hash72"]),
            "receipt_hash72": str(row["receipt_hash72"]),
            "schema_root216": str(row["schema_root216"]),
            "constraint_root216": str(row["constraint_root216"]),
            "event_count": int(row["event_count"]),
            "created_at_unix_ms": int(row["created_at_unix_ms"]),
        }
        if include_payloads:
            result.update({
                "state_words": _parse_json(str(row["state_json"])),
                "projection_channels": _parse_json(str(row["projection_json"])),
                "learning_features": _parse_json(str(row["learning_json"])),
                "frontier_cells": _parse_json(str(row["frontier_json"])),
            })
        return result

    def snapshot(self, root216: str, *, include_payloads: bool = True) -> dict[str, Any]:
        return self._decode_row(self._row(root216), include_payloads=include_payloads)

    def _delta_events(self, delta_root216: str) -> list[dict[str, int]]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT events_json FROM deltas WHERE delta_root216=?", (delta_root216,)
            ).fetchone()
        if row is None:
            raise ContinuationNotFound(f"delta unavailable: {delta_root216}")
        return [dict(event) for event in _parse_json(str(row["events_json"]))]

    def _persist(
        self,
        *,
        parent: Mapping[str, Any],
        state: Sequence[int],
        projection: Sequence[Sequence[int]],
        learning: Sequence[int],
        frontier_cells: Sequence[int],
        events: Sequence[Mapping[str, int]],
        token: Mapping[str, Any],
    ) -> dict[str, Any]:
        payload = {"schema": SCHEMA, "contract": CONTRACT, **dict(token)}
        now = _now_ms()
        with self._transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM snapshots WHERE continuation_root216=?",
                (token["continuation_root216"],),
            ).fetchone()
            if existing is not None:
                return self._decode_row(existing)
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
        return self.snapshot(str(token["continuation_root216"]))

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
            content_root = self.native.state_root(child_state)
            delta_root = self.native.delta_root(normalized)
            hydration_root = self.native.hydration_root(normalized)
            dependency_root = self.native.frontier_root(chosen_frontier)
            projection_root = self.native.projection_root(sparse_projection)
            learning_root = self.native.hash216_bytes(_canonical_bytes(sparse_learning))
            token = self.native.build_token(
                parent_root=parent["continuation_root216"],
                content_root=content_root,
                delta_root=delta_root,
                hydration_root=hydration_root,
                dependency_root=dependency_root,
                projection_root=projection_root,
                learning_root=learning_root,
                parent_receipt=parent["receipt_hash72"],
                generation=int(parent["generation"]) + 1,
            )
            return self._persist(
                parent=parent,
                state=child_state,
                projection=sparse_projection,
                learning=sparse_learning,
                frontier_cells=chosen_frontier,
                events=normalized,
                token=token,
            )

    def branch(self, **kwargs: Any) -> dict[str, Any]:
        return self.advance(**kwargs)

    def reverse(self, continuation_root216: str) -> dict[str, Any]:
        current = self.snapshot(continuation_root216)
        if int(current["generation"]) == 0:
            raise ContinuationRejected("genesis has no reversible delta")
        events = list(reversed(self._delta_events(str(current["delta_root216"]))))
        return self.advance(
            parent_root216=continuation_root216,
            events=events,
            expected_parent_receipt_hash72=str(current["receipt_hash72"]),
        )

    def retrieve(
        self,
        *,
        target_state_words: Sequence[int],
        schema_root216: str | None = None,
        constraint_root216: str | None = None,
        top_k: int = 32,
    ) -> dict[str, Any]:
        target = _validate_words(target_state_words)
        schema_root = schema_root216 or self.schema_root216
        constraint_root = constraint_root216 or self.constraint_root216
        target_projection = self.native.project_full(target)
        target_features = _learning_full(target, target_projection)
        query_root = self.native.hash216_bytes(_canonical_bytes({
            "state": target,
            "schema_root216": schema_root,
            "constraint_root216": constraint_root,
        }))
        compatible: list[tuple[int, str, list[int]]] = []
        rejected: list[dict[str, str]] = []
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT v.continuation_root216,v.schema_root216,v.constraint_root216,
                          v.features_json,s.state_json
                   FROM vectors v JOIN snapshots s USING(continuation_root216)"""
            ).fetchall()
        for row in rows:
            root = str(row["continuation_root216"])
            reasons: list[str] = []
            if str(row["schema_root216"]) != schema_root:
                reasons.append("SCHEMA_ROOT_MISMATCH")
            if str(row["constraint_root216"]) != constraint_root:
                reasons.append("CONSTRAINT_ROOT_MISMATCH")
            if reasons:
                rejected.append({"continuation_root216": root, "reason": ",".join(reasons)})
                continue
            features = [int(value) for value in _parse_json(str(row["features_json"]))]
            state = [int(value) for value in _parse_json(str(row["state_json"]))]
            compatible.append((_popcount_distance(features, target_features), root, state))
        if not compatible:
            raise ContinuationRejected("no continuation-compatible snapshot exists")
        shortlist_size = max(1, min(int(top_k), len(compatible)))
        shortlist = sorted(compatible, key=lambda item: (item[0], item[1]))[:shortlist_size]
        reranked = sorted(
            (
                _popcount_distance(state, target),
                vector_cost,
                root,
            )
            for vector_cost, root, state in shortlist
        )
        exact_cost, vector_cost, selected = reranked[0]
        ranked_payload = [
            {
                "continuation_root216": root,
                "vector_distance": int(vcost),
                "exact_delta_cost": int(ecost),
            }
            for ecost, vcost, root in reranked
        ]
        retrieval_root = self.native.hash216_bytes(_canonical_bytes({
            "query_root216": query_root,
            "selected_parent_root216": selected,
            "ranked_candidates": ranked_payload,
            "rejected_candidates": rejected,
        }))
        with self._transaction() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO retrievals VALUES (?,?,?,?,?,?,?)",
                (
                    retrieval_root, query_root, selected, _json(ranked_payload), _json(rejected),
                    int(exact_cost), _now_ms(),
                ),
            )
        return {
            "schema": "HHS_PASS_205_COMPATIBLE_SNAPSHOT_RETRIEVAL_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "ok": True,
            "retrieval_root216": retrieval_root,
            "query_root216": query_root,
            "selected_parent_root216": selected,
            "selected_parent_receipt_hash72": self.snapshot(selected, include_payloads=False)["receipt_hash72"],
            "vector_distance": int(vector_cost),
            "exact_delta_cost": int(exact_cost),
            "ranked_candidates": ranked_payload,
            "rejected_candidates": rejected,
            "approximate_similarity_is_authority": False,
            "exact_rerank_applied": True,
        }

    def hydrate_target(
        self,
        *,
        target_state_words: Sequence[int],
        controls_by_cell: Mapping[int | str, int] | None = None,
        schema_root216: str | None = None,
        constraint_root216: str | None = None,
        top_k: int = 32,
    ) -> dict[str, Any]:
        target = _validate_words(target_state_words)
        retrieval = self.retrieve(
            target_state_words=target,
            schema_root216=schema_root216,
            constraint_root216=constraint_root216,
            top_k=top_k,
        )
        parent = self.snapshot(str(retrieval["selected_parent_root216"]))
        controls = {int(key): int(value) for key, value in (controls_by_cell or {}).items()}
        events: list[dict[str, int]] = []
        for cell, (before, after) in enumerate(zip(parent["state_words"], target)):
            mask = int(before) ^ int(after)
            if mask == 0:
                continue
            control = controls.get(cell, 0)
            events.append({"cell": cell, "control_g": control, "xor_mask": mask})
        if not events:
            return {
                "schema": "HHS_PASS_205_TARGET_ALREADY_COMMITTED_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "ok": True,
                "retrieval": retrieval,
                "snapshot": parent,
                "new_continuation_created": False,
            }
        snapshot = self.advance(
            parent_root216=parent["continuation_root216"],
            expected_parent_receipt_hash72=parent["receipt_hash72"],
            events=events,
        )
        return {
            "schema": "HHS_PASS_205_RETRIEVAL_HYDRATED_CONTINUATION_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "ok": True,
            "retrieval": retrieval,
            "snapshot": snapshot,
            "new_continuation_created": True,
        }

    def verify(self, continuation_root216: str) -> dict[str, Any]:
        snapshot = self.snapshot(continuation_root216)
        reasons: list[str] = []
        state = _validate_words(snapshot["state_words"])
        projection = snapshot["projection_channels"]
        learning = snapshot["learning_features"]
        if self.native.state_root(state) != snapshot["content_root216"]:
            reasons.append("CONTENT_ROOT_MISMATCH")
        full_projection = self.native.project_full(state)
        if full_projection != projection:
            reasons.append("PROJECTION_PAYLOAD_MISMATCH")
        if self.native.projection_root(projection) != snapshot["projection_root216"]:
            reasons.append("PROJECTION_ROOT_MISMATCH")
        full_learning = _learning_full(state, projection)
        if full_learning != learning:
            reasons.append("LEARNING_PAYLOAD_MISMATCH")
        if self.native.hash216_bytes(_canonical_bytes(learning)) != snapshot["learning_root216"]:
            reasons.append("LEARNING_ROOT_MISMATCH")
        if int(snapshot["generation"]) == 0:
            events: list[dict[str, int]] = []
        else:
            events = self._delta_events(str(snapshot["delta_root216"]))
            if self.native.delta_root(events) != snapshot["delta_root216"]:
                reasons.append("DELTA_ROOT_MISMATCH")
            if self.native.hydration_root(events) != snapshot["hydration_root216"]:
                reasons.append("HYDRATION_ROOT_MISMATCH")
            if not self.native.validate_frontier(events, snapshot["frontier_cells"]):
                reasons.append("INCOMPLETE_DEPENDENCY_FRONTIER")
        if self.native.frontier_root(snapshot["frontier_cells"]) != snapshot["dependency_root216"]:
            reasons.append("DEPENDENCY_ROOT_MISMATCH")
        token = self.native.build_token(
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
        if token["continuation_root216"] != snapshot["continuation_root216"]:
            reasons.append("CONTINUATION_ROOT_MISMATCH")
        if token["receipt_hash72"] != snapshot["receipt_hash72"]:
            reasons.append("RECEIPT_HASH72_MISMATCH")
        if int(snapshot["generation"]) > 0:
            parent = self.snapshot(snapshot["parent_root216"], include_payloads=False)
            if parent["receipt_hash72"] != snapshot["parent_receipt_hash72"]:
                reasons.append("PARENT_RECEIPT_LINEAGE_MISMATCH")
            if int(parent["generation"]) + 1 != int(snapshot["generation"]):
                reasons.append("GENERATION_LINEAGE_MISMATCH")
        return {
            "schema": "HHS_PASS_205_CONTINUATION_VERIFICATION_V1",
            "contract": CONTRACT,
            "classification": CLOSURE_CLASSIFICATION if not reasons else "HHS_PASS_205_CONTINUATION_REJECTED",
            "ok": not reasons,
            "continuation_root216": continuation_root216,
            "reasons": reasons,
            "native_full_recomputation": True,
            "hash72_parent_bound": "PARENT_RECEIPT_LINEAGE_MISMATCH" not in reasons,
            "float_canonical_authority": False,
        }

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
        for snapshot in chain:
            verification = self.verify(str(snapshot["continuation_root216"]))
            if not verification["ok"]:
                failures.append(verification)
        return {
            "schema": "HHS_PASS_205_DETERMINISTIC_REPLAY_V1",
            "contract": CONTRACT,
            "classification": CLOSURE_CLASSIFICATION if not failures else "HHS_PASS_205_REPLAY_REJECTED",
            "ok": not failures,
            "target_root216": continuation_root216,
            "generation_count": len(chain),
            "ordered_roots216": [snapshot["continuation_root216"] for snapshot in chain],
            "ordered_receipts_hash72": [snapshot["receipt_hash72"] for snapshot in chain],
            "failures": failures,
        }

    def graph(self, continuation_root216: str) -> dict[str, Any]:
        target = self.snapshot(continuation_root216, include_payloads=False)
        ancestors: list[str] = []
        cursor = target
        while int(cursor["generation"]) > 0:
            ancestors.append(str(cursor["parent_root216"]))
            cursor = self.snapshot(str(cursor["parent_root216"]), include_payloads=False)
        with self._connect() as connection:
            children = [
                str(row["child_root216"])
                for row in connection.execute(
                    "SELECT child_root216 FROM lineage WHERE parent_root216=? ORDER BY generation,child_root216",
                    (continuation_root216,),
                ).fetchall()
            ]
        return {
            "schema": "HHS_PASS_205_CONTINUATION_GRAPH_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "ok": True,
            "target": target,
            "ancestors_root216": ancestors,
            "children_root216": children,
        }

    def projections(self, continuation_root216: str) -> dict[str, Any]:
        snapshot = self.snapshot(continuation_root216)
        return {
            "schema": "HHS_PASS_205_32_CHANNEL_PROJECTION_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "ok": True,
            "continuation_root216": continuation_root216,
            "projection_root216": snapshot["projection_root216"],
            "frontier_cells": snapshot["frontier_cells"],
            "channel_count": PROJECTION_CHANNELS,
            "channels": snapshot["projection_channels"],
        }

    def status(self) -> dict[str, Any]:
        with self._connect() as connection:
            snapshot_count = int(connection.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0])
            delta_count = int(connection.execute("SELECT COUNT(*) FROM deltas").fetchone()[0])
            branch_count = int(connection.execute("SELECT COUNT(*) FROM lineage").fetchone()[0])
            retrieval_count = int(connection.execute("SELECT COUNT(*) FROM retrievals").fetchone()[0])
            latest_generation = int(connection.execute("SELECT COALESCE(MAX(generation),0) FROM snapshots").fetchone()[0])
        return {
            "schema": "HHS_PASS_205_CONTINUATION_RUNTIME_STATUS_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "ok": True,
            "production_runtime_active": True,
            "closure_verified": False,
            "single_vm81_mutation_authority": True,
            "single_ordered_hash72_commit_stream": True,
            "cache_hit_bypasses_admission": False,
            "state_bits": STATE_BITS,
            "cell_count": CELL_COUNT,
            "control_count": CONTROL_COUNT,
            "hydration_projection_count": Q_COUNT,
            "projection_channel_count": PROJECTION_CHANNELS,
            "snapshot_count": snapshot_count,
            "delta_count": delta_count,
            "lineage_edge_count": branch_count,
            "retrieval_count": retrieval_count,
            "latest_generation": latest_generation,
            "genesis_root216": self.genesis_root216,
            "database": str(self.db_path),
            "sqlite_wal": True,
            "sqlite_synchronous": "FULL",
            "native_abi": self.native.abi_status(),
            "accelerator_translation": {
                "state_layout": "uint64 SoA[cell][batch]",
                "projection_layout": "uint32 SoA[channel][cell][batch]",
                "delta_layout": "CSR offsets + uint32 cell + uint64 XOR mask + uint8 control_g",
                "hydration_layout": "CSR offsets + uint32 q",
                "deterministic_integer_reduction": True,
                "physical_gpu_backend_active": False,
                "supported_backend_targets": ["CUDA", "HIP", "VULKAN_COMPUTE", "WEBGPU", "METAL"],
            },
            "external_vercel_quota_is_not_acceptance_gate": True,
        }


PASS205_CONTINUATION_RUNTIME = Pass205ContinuationRuntime()
