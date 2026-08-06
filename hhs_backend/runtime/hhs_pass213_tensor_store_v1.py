"""Persistent keyed moving-tensor chain for Pass 213 Iteration 8."""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    FULL_HYDRATION_DOMAIN, ZERO_HASH216, canonical_bytes,
)
from hhs_backend.runtime.hhs_pass213_moving_tensor_v1 import (
    MovingTensorState, Pass213TensorError,
)
from hhs_backend.runtime.hhs_pass213_trusted_timestamp_v1 import TrustedTimestampAnchorRecord


class MovingTensorStore:
    """SQLite WAL append-only tensor chain with keyed replay on every reopen."""

    def __init__(self, *, database_path: str | Path, root_key: bytes) -> None:
        if not isinstance(root_key, bytes) or len(root_key) < 32:
            raise Pass213TensorError("PASS213_TENSOR_ROOT_KEY_TOO_SHORT")
        self._root_key = root_key
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS moving_tensor_states(
              tensor_sequence INTEGER PRIMARY KEY,
              tensor_root_hash216 TEXT UNIQUE NOT NULL,
              prior_tensor_root_hash216 TEXT NOT NULL,
              anchor_sequence INTEGER UNIQUE NOT NULL,
              anchor_root_hash216 TEXT UNIQUE NOT NULL,
              requested_timestamp_ns INTEGER NOT NULL,
              state_json TEXT NOT NULL,
              trusted_anchor_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS moving_tensor_meta(
              key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)
        if self._meta("tensor_head_hash216") is None:
            with self._connection:
                self._set_meta("tensor_head_hash216", ZERO_HASH216)
        try:
            self.verify_chain()
        except Exception:
            self._root_key = b"\0" * len(self._root_key)
            self._connection.close()
            raise

    def _meta(self, key: str) -> str | None:
        row = self._connection.execute("SELECT value FROM moving_tensor_meta WHERE key=?", (key,)).fetchone()
        return None if row is None else str(row["value"])

    def _set_meta(self, key: str, value: str) -> None:
        self._connection.execute(
            "INSERT INTO moving_tensor_meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )

    def append(self, *, trusted_anchor: TrustedTimestampAnchorRecord, genesis_epoch: int, domain_size: int = FULL_HYDRATION_DOMAIN) -> MovingTensorState:
        sequence = int(self._connection.execute(
            "SELECT COALESCE(MAX(tensor_sequence),0) AS n FROM moving_tensor_states"
        ).fetchone()["n"]) + 1
        state = MovingTensorState.derive(
            root_key=self._root_key, trusted_anchor=trusted_anchor,
            tensor_sequence=sequence, genesis_epoch=genesis_epoch,
            prior_tensor_root_hash216=str(self._meta("tensor_head_hash216")),
            domain_size=domain_size,
        )
        previous = self._connection.execute(
            "SELECT anchor_sequence,requested_timestamp_ns FROM moving_tensor_states ORDER BY tensor_sequence DESC LIMIT 1"
        ).fetchone()
        if previous is not None:
            if state.anchor.anchor_sequence <= int(previous["anchor_sequence"]):
                raise Pass213TensorError("PASS213_TENSOR_ANCHOR_SEQUENCE_REGRESSION")
            if state.anchor.requested_timestamp_ns < int(previous["requested_timestamp_ns"]):
                raise Pass213TensorError("PASS213_TENSOR_TIMESTAMP_REGRESSION")
        with self._connection:
            self._connection.execute("INSERT INTO moving_tensor_states VALUES(?,?,?,?,?,?,?,?)", (
                state.tensor_sequence, state.tensor_root_hash216, state.prior_tensor_root_hash216,
                state.anchor.anchor_sequence, state.anchor.anchor_root_hash216,
                state.anchor.requested_timestamp_ns,
                canonical_bytes(state.to_mapping()).decode("utf-8"),
                canonical_bytes(trusted_anchor.to_mapping()).decode("utf-8"),
            ))
            self._set_meta("tensor_head_hash216", state.tensor_root_hash216)
        return state

    def get(self, tensor_sequence: int) -> MovingTensorState:
        row = self._connection.execute(
            "SELECT state_json FROM moving_tensor_states WHERE tensor_sequence=?", (int(tensor_sequence),)
        ).fetchone()
        if row is None:
            raise Pass213TensorError("PASS213_TENSOR_STATE_NOT_FOUND")
        return MovingTensorState.from_mapping(json.loads(str(row["state_json"])))

    def verify_chain(self) -> bool:
        prior, prior_anchor, prior_timestamp = ZERO_HASH216, 0, -1
        rows = self._connection.execute("SELECT * FROM moving_tensor_states ORDER BY tensor_sequence").fetchall()
        for expected_sequence, row in enumerate(rows, 1):
            if int(row["tensor_sequence"]) != expected_sequence:
                raise Pass213TensorError("PASS213_TENSOR_SEQUENCE_DISCONTINUITY")
            state = MovingTensorState.from_mapping(json.loads(str(row["state_json"])))
            anchor = TrustedTimestampAnchorRecord.from_mapping(json.loads(str(row["trusted_anchor_json"])))
            state.validate_with_key(root_key=self._root_key, trusted_anchor=anchor)
            if (
                state.prior_tensor_root_hash216 != prior
                or state.tensor_root_hash216 != str(row["tensor_root_hash216"])
                or state.anchor.anchor_root_hash216 != str(row["anchor_root_hash216"])
            ):
                raise Pass213TensorError("PASS213_TENSOR_CHAIN_DISCONTINUITY")
            if state.anchor.anchor_sequence <= prior_anchor or state.anchor.requested_timestamp_ns < prior_timestamp:
                raise Pass213TensorError("PASS213_TENSOR_BOUNDARY_REGRESSION")
            prior, prior_anchor, prior_timestamp = (
                state.tensor_root_hash216, state.anchor.anchor_sequence, state.anchor.requested_timestamp_ns
            )
        if str(self._meta("tensor_head_hash216")) != prior:
            raise Pass213TensorError("PASS213_TENSOR_HEAD_MISMATCH")
        return True

    def current_head(self) -> str:
        return str(self._meta("tensor_head_hash216"))

    def close(self) -> None:
        self._root_key = b"\0" * len(self._root_key)
        self._connection.close()

    def __enter__(self) -> "MovingTensorStore":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()
