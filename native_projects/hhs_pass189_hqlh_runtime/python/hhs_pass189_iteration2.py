#!/usr/bin/env python3
"""Pass 189 Iteration 2 persistent calibration and joint-causal authority.

This module is additive to the Pass 189 hydration runtime. It supplies an exact
SQLite-backed calibration ledger, bounded physical-output admission, atomic
multi-object causal resolution, deterministic receipts, and checkpoint/recovery.
No floating-point value is accepted in canonical payloads.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

CONTRACT = "HHS-P189-HQLH-LS41-XNOR-P1-H72-H216-UPA"
ITERATION = "HHS-P189-HQLH-ITERATION-2-CALIBRATION-CAUSAL-PERSISTENCE"
CLASSIFICATION = "HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS"
SCHEMA_VERSION = 1
ZERO_HASH72 = "0" * 72


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def hash72(value: Any) -> str:
    return hashlib.sha512(canonical_json(value).encode("utf-8")).hexdigest()[:72]


def _fraction(value: Any, *, field: str = "value") -> Fraction:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an exact number")
    if isinstance(value, float):
        raise ValueError(f"{field} rejects floating-point canonical input")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"invalid exact rational for {field}") from exc
    if isinstance(value, Mapping):
        try:
            numerator = int(value["numerator"])
            denominator = int(value["denominator"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid exact rational object for {field}") from exc
        if denominator == 0:
            raise ValueError(f"{field} denominator must be nonzero")
        return Fraction(numerator, denominator)
    raise ValueError(f"unsupported exact rational for {field}")


def rational_json(value: Fraction | Any) -> dict[str, int]:
    item = value if isinstance(value, Fraction) else _fraction(value)
    return {"numerator": item.numerator, "denominator": item.denominator}


def _square(value: Fraction) -> Fraction:
    return value * value


def _require_hash72(value: str, field: str) -> str:
    text = str(value)
    if len(text) != 72 or any(ch not in "0123456789abcdef" for ch in text.lower()):
        raise ValueError(f"{field} must be a 72-glyph hexadecimal identity")
    return text.lower()


@dataclass(frozen=True)
class CalibrationProfile:
    profile_id: str
    device_id: str
    variable: str
    unit: str
    dimension: str
    scale: dict[str, int]
    offset: dict[str, int]
    raw_min: dict[str, int]
    raw_max: dict[str, int]
    canonical_min: dict[str, int]
    canonical_max: dict[str, int]
    resolution: dict[str, int]
    tolerance: dict[str, int]
    required_samples: int
    evidence_class: str
    calibration_source: str
    device_attested: bool
    operator_arm_hash72: str
    created_ns: int
    profile_hash72: str

    @classmethod
    def create(cls, payload: Mapping[str, Any]) -> "CalibrationProfile":
        device_id = str(payload.get("device_id", "")).strip()
        variable = str(payload.get("variable", "")).strip()
        unit = str(payload.get("unit", "")).strip()
        dimension = str(payload.get("dimension", "")).strip()
        calibration_source = str(payload.get("calibration_source", "")).strip()
        evidence_class = str(payload.get("evidence_class", "SYNTHETIC")).upper()
        if not all((device_id, variable, unit, dimension, calibration_source)):
            raise ValueError("profile requires device_id, variable, unit, dimension, and calibration_source")
        if evidence_class not in {"SYNTHETIC", "MEASURED_HARDWARE"}:
            raise ValueError("evidence_class must be SYNTHETIC or MEASURED_HARDWARE")
        scale = _fraction(payload.get("scale", 1), field="scale")
        offset = _fraction(payload.get("offset", 0), field="offset")
        raw_min = _fraction(payload.get("raw_min"), field="raw_min")
        raw_max = _fraction(payload.get("raw_max"), field="raw_max")
        canonical_min = _fraction(payload.get("canonical_min"), field="canonical_min")
        canonical_max = _fraction(payload.get("canonical_max"), field="canonical_max")
        resolution = _fraction(payload.get("resolution"), field="resolution")
        tolerance = _fraction(payload.get("tolerance"), field="tolerance")
        required_samples = int(payload.get("required_samples", 3))
        created_ns = int(payload.get("created_ns", 0))
        if raw_min >= raw_max or canonical_min >= canonical_max:
            raise ValueError("calibration ranges must be increasing")
        if resolution <= 0 or tolerance < 0:
            raise ValueError("resolution must be positive and tolerance nonnegative")
        if not 3 <= required_samples <= 10_000:
            raise ValueError("required_samples must be in [3,10000]")
        arm_hash = _require_hash72(str(payload.get("operator_arm_hash72", ZERO_HASH72)), "operator_arm_hash72")
        core = {
            "device_id": device_id,
            "variable": variable,
            "unit": unit,
            "dimension": dimension,
            "scale": rational_json(scale),
            "offset": rational_json(offset),
            "raw_min": rational_json(raw_min),
            "raw_max": rational_json(raw_max),
            "canonical_min": rational_json(canonical_min),
            "canonical_max": rational_json(canonical_max),
            "resolution": rational_json(resolution),
            "tolerance": rational_json(tolerance),
            "required_samples": required_samples,
            "evidence_class": evidence_class,
            "calibration_source": calibration_source,
            "device_attested": bool(payload.get("device_attested", False)),
            "operator_arm_hash72": arm_hash,
            "created_ns": created_ns,
        }
        profile_id = str(payload.get("profile_id", "")).strip() or hash72({"profile": core})
        core_with_id = {"profile_id": profile_id, **core}
        return cls(**core_with_id, profile_hash72=hash72(core_with_id))

    def convert(self, raw: Any) -> Fraction:
        raw_value = _fraction(raw, field="raw")
        return raw_value * _fraction(self.scale, field="scale") + _fraction(self.offset, field="offset")


class CalibrationLedger:
    """SQLite authority with bounded lock acquisition and append-only receipts."""

    def __init__(self, db_path: str | os.PathLike[str], *, busy_timeout_ms: int = 1500, retries: int = 4) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.busy_timeout_ms = max(1, min(int(busy_timeout_ms), 10_000))
        self.retries = max(1, min(int(retries), 20))
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.db_path, timeout=self.busy_timeout_ms / 1000, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute(f"PRAGMA busy_timeout={self.busy_timeout_ms}")
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._create_schema()

    def close(self) -> None:
        self._connection.close()

    def _create_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                predecessor_hash72 TEXT NOT NULL,
                event_hash72 TEXT NOT NULL UNIQUE,
                payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS profiles (
                profile_id TEXT PRIMARY KEY,
                profile_hash72 TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_event INTEGER NOT NULL REFERENCES events(seq)
            );
            CREATE TABLE IF NOT EXISTS samples (
                sample_id TEXT PRIMARY KEY,
                profile_id TEXT NOT NULL REFERENCES profiles(profile_id),
                accepted INTEGER NOT NULL,
                residual_num TEXT NOT NULL,
                residual_den TEXT NOT NULL,
                sample_hash72 TEXT NOT NULL UNIQUE,
                payload_json TEXT NOT NULL,
                created_event INTEGER NOT NULL REFERENCES events(seq)
            );
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                receipt_index INTEGER NOT NULL,
                root_hash72 TEXT NOT NULL,
                checkpoint_hash72 TEXT NOT NULL UNIQUE,
                snapshot_json TEXT NOT NULL,
                created_event INTEGER NOT NULL REFERENCES events(seq)
            );
            """
        )
        self._connection.execute(
            "INSERT OR IGNORE INTO metadata(key,value) VALUES('schema_version',?)", (str(SCHEMA_VERSION),)
        )
        self._connection.commit()

    def _execute_transaction(self, callback):
        last_error: Exception | None = None
        for attempt in range(self.retries):
            try:
                with self._lock:
                    self._connection.execute("BEGIN IMMEDIATE")
                    result = callback(self._connection)
                    self._connection.commit()
                    return result
            except sqlite3.OperationalError as exc:
                try:
                    self._connection.rollback()
                except sqlite3.Error:
                    pass
                last_error = exc
                if "locked" not in str(exc).lower() and "busy" not in str(exc).lower():
                    raise
                if attempt + 1 < self.retries:
                    time.sleep(min(0.02 * (attempt + 1), 0.1))
        raise RuntimeError("bounded SQLite authority acquisition failed") from last_error

    @staticmethod
    def _append_event(conn: sqlite3.Connection, event_type: str, payload: Mapping[str, Any]) -> tuple[int, str]:
        row = conn.execute("SELECT seq,event_hash72 FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        predecessor = row["event_hash72"] if row else ZERO_HASH72
        next_seq = (int(row["seq"]) + 1) if row else 1
        event_payload = {
            "schema": "HHS_PASS_189_ITERATION2_EVENT_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "seq": next_seq,
            "event_type": event_type,
            "predecessor_hash72": predecessor,
            "payload": dict(payload),
        }
        event_hash = hash72(event_payload)
        cursor = conn.execute(
            "INSERT INTO events(event_type,predecessor_hash72,event_hash72,payload_json) VALUES(?,?,?,?)",
            (event_type, predecessor, event_hash, canonical_json(event_payload)),
        )
        return int(cursor.lastrowid), event_hash

    def register_profile(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        profile = CalibrationProfile.create(payload)
        profile_data = asdict(profile)

        def operation(conn: sqlite3.Connection) -> dict[str, Any]:
            existing = conn.execute("SELECT payload_json,status,created_event FROM profiles WHERE profile_id=?", (profile.profile_id,)).fetchone()
            if existing:
                if canonical_json(profile_data) != canonical_json(json.loads(existing["payload_json"])):
                    raise ValueError("profile_id already exists with different payload")
                return {**json.loads(existing["payload_json"]), "status": existing["status"], "idempotent": True}
            event_seq, event_hash = self._append_event(conn, "CALIBRATION_PROFILE_REGISTERED", profile_data)
            conn.execute(
                "INSERT INTO profiles(profile_id,profile_hash72,status,payload_json,created_event) VALUES(?,?,?,?,?)",
                (profile.profile_id, profile.profile_hash72, "PENDING_SAMPLES", canonical_json(profile_data), event_seq),
            )
            return {**profile_data, "status": "PENDING_SAMPLES", "event_seq": event_seq, "event_hash72": event_hash, "idempotent": False}

        return self._execute_transaction(operation)

    def get_profile(self, profile_id: str) -> dict[str, Any]:
        with self._lock:
            row = self._connection.execute("SELECT payload_json,status FROM profiles WHERE profile_id=?", (profile_id,)).fetchone()
            if not row:
                raise KeyError("unknown calibration profile")
            payload = json.loads(row["payload_json"])
            counts = self._connection.execute(
                "SELECT COUNT(*) total, COALESCE(SUM(accepted),0) accepted FROM samples WHERE profile_id=?", (profile_id,)
            ).fetchone()
            return {**payload, "status": row["status"], "sample_count": int(counts["total"]), "accepted_samples": int(counts["accepted"])}

    def append_sample(self, profile_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        profile_data = self.get_profile(profile_id)
        profile = CalibrationProfile(**{key: profile_data[key] for key in CalibrationProfile.__dataclass_fields__})
        measurement_id = str(payload.get("measurement_id", "")).strip()
        source = str(payload.get("source", "")).strip()
        measurement_ns = int(payload.get("measurement_ns", 0))
        if not measurement_id or not source or measurement_ns <= 0:
            raise ValueError("sample requires measurement_id, source, and positive measurement_ns")
        raw = _fraction(payload.get("raw"), field="raw")
        expected = _fraction(payload.get("expected"), field="expected")
        raw_min, raw_max = _fraction(profile.raw_min), _fraction(profile.raw_max)
        canonical_min, canonical_max = _fraction(profile.canonical_min), _fraction(profile.canonical_max)
        computed = profile.convert(raw)
        residual = computed - expected
        accepted = (
            raw_min <= raw <= raw_max
            and canonical_min <= computed <= canonical_max
            and abs(residual) <= _fraction(profile.tolerance)
        )
        sample_core = {
            "profile_id": profile_id,
            "measurement_id": measurement_id,
            "measurement_ns": measurement_ns,
            "source": source,
            "raw": rational_json(raw),
            "expected": rational_json(expected),
            "computed": rational_json(computed),
            "residual": rational_json(residual),
            "accepted": accepted,
        }
        sample_id = str(payload.get("sample_id", "")).strip() or hash72({"sample": sample_core})
        sample_data = {"sample_id": sample_id, **sample_core}
        sample_hash = hash72(sample_data)

        def operation(conn: sqlite3.Connection) -> dict[str, Any]:
            existing = conn.execute("SELECT payload_json FROM samples WHERE sample_id=?", (sample_id,)).fetchone()
            if existing:
                if canonical_json(sample_data) != canonical_json(json.loads(existing["payload_json"])):
                    raise ValueError("sample_id already exists with different payload")
                return {**json.loads(existing["payload_json"]), "idempotent": True}
            event_seq, event_hash = self._append_event(conn, "CALIBRATION_SAMPLE_RECORDED", sample_data)
            conn.execute(
                "INSERT INTO samples(sample_id,profile_id,accepted,residual_num,residual_den,sample_hash72,payload_json,created_event) VALUES(?,?,?,?,?,?,?,?)",
                (
                    sample_id,
                    profile_id,
                    1 if accepted else 0,
                    str(residual.numerator),
                    str(residual.denominator),
                    sample_hash,
                    canonical_json(sample_data),
                    event_seq,
                ),
            )
            counts = conn.execute(
                "SELECT COUNT(*) total, COALESCE(SUM(accepted),0) accepted FROM samples WHERE profile_id=?", (profile_id,)
            ).fetchone()
            total, accepted_count = int(counts["total"]), int(counts["accepted"])
            status = "VALIDATED" if total >= profile.required_samples and accepted_count == total else "CALIBRATION_IN_PROGRESS"
            conn.execute("UPDATE profiles SET status=? WHERE profile_id=?", (status, profile_id))
            return {
                **sample_data,
                "sample_hash72": sample_hash,
                "profile_status": status,
                "sample_count": total,
                "accepted_samples": accepted_count,
                "event_seq": event_seq,
                "event_hash72": event_hash,
                "idempotent": False,
            }

        return self._execute_transaction(operation)

    def admit_output(
        self,
        profile_id: str,
        requested: Any,
        *,
        mode: str = "SIMULATION",
        operator_arm_token: str = "",
    ) -> dict[str, Any]:
        profile_data = self.get_profile(profile_id)
        requested_value = _fraction(requested, field="requested")
        mode_name = str(mode).upper()
        if mode_name not in {"SIMULATION", "PHYSICAL"}:
            raise ValueError("mode must be SIMULATION or PHYSICAL")
        within_range = _fraction(profile_data["canonical_min"]) <= requested_value <= _fraction(profile_data["canonical_max"])
        reasons: list[str] = []
        if not within_range:
            reasons.append("CANONICAL_RANGE_REJECTED")
        physical = mode_name == "PHYSICAL"
        if physical:
            if profile_data["status"] != "VALIDATED":
                reasons.append("CALIBRATION_NOT_VALIDATED")
            if profile_data["evidence_class"] != "MEASURED_HARDWARE":
                reasons.append("MEASURED_HARDWARE_EVIDENCE_REQUIRED")
            if not bool(profile_data["device_attested"]):
                reasons.append("DEVICE_ATTESTATION_REQUIRED")
            token_hash = hash72({"operator_arm_token": operator_arm_token})
            if token_hash != profile_data["operator_arm_hash72"]:
                reasons.append("OPERATOR_ARM_REJECTED")
        authorized = not reasons
        payload = {
            "profile_id": profile_id,
            "mode": mode_name,
            "requested": rational_json(requested_value),
            "authorized": authorized,
            "reasons": reasons or ["ADMITTED"],
            "dispatch_scope": "CANDIDATE_ONLY_NO_DEVICE_DRIVER" if physical else "SIMULATION_ONLY",
        }

        def operation(conn: sqlite3.Connection) -> dict[str, Any]:
            event_seq, event_hash = self._append_event(conn, "OUTPUT_ADMISSION", payload)
            return {**payload, "event_seq": event_seq, "event_hash72": event_hash}

        return self._execute_transaction(operation)

    def resolve_worldlines(
        self,
        candidates: Sequence[Mapping[str, Any]],
        *,
        causal_rate: Any = 1,
        collision_policy: str = "REJECT",
    ) -> dict[str, Any]:
        if not candidates:
            raise ValueError("at least one worldline candidate is required")
        if len(candidates) > 10_000:
            raise ValueError("worldline batch exceeds bounded candidate limit")
        rate = _fraction(causal_rate, field="causal_rate")
        if rate <= 0:
            raise ValueError("causal_rate must be positive")
        policy = str(collision_policy).upper()
        if policy not in {"REJECT", "ALLOW"}:
            raise ValueError("collision_policy must be REJECT or ALLOW")
        normalized: list[dict[str, Any]] = []
        object_ids: set[str] = set()
        current_receipt = self.receipt_index
        for candidate in candidates:
            object_id = str(candidate.get("object_id", "")).strip()
            if not object_id or object_id in object_ids:
                raise ValueError("worldline object_id values must be nonempty and unique")
            object_ids.add(object_id)
            input_receipt = int(candidate.get("input_receipt_index", current_receipt))
            if input_receipt != current_receipt:
                raise ValueError("worldline candidate receipt index drift")
            position = tuple(_fraction(value, field="position") for value in candidate.get("position4", ()))
            delta = tuple(_fraction(value, field="delta") for value in candidate.get("delta4", ()))
            if len(position) != 4 or len(delta) != 4:
                raise ValueError("position4 and delta4 must each contain four exact coordinates")
            dt = delta[0]
            spatial_sq = sum((_square(delta[index]) for index in range(1, 4)), Fraction(0, 1))
            causal_limit_sq = _square(rate * dt)
            if dt < 0 or spatial_sq > causal_limit_sq:
                raise ValueError(f"causal-rate violation for {object_id}")
            target = tuple(position[index] + delta[index] for index in range(4))
            interval = _square(dt) - spatial_sq
            normalized.append({
                "object_id": object_id,
                "input_receipt_index": input_receipt,
                "position4": [rational_json(value) for value in position],
                "delta4": [rational_json(value) for value in delta],
                "target4": [rational_json(value) for value in target],
                "proper_time_squared": rational_json(interval),
                "metadata": dict(candidate.get("metadata", {})),
            })
        normalized.sort(key=lambda item: item["object_id"])
        target_index: dict[str, list[str]] = {}
        for item in normalized:
            target_key = canonical_json(item["target4"])
            target_index.setdefault(target_key, []).append(item["object_id"])
        collisions = [ids for ids in target_index.values() if len(ids) > 1]
        if collisions and policy == "REJECT":
            raise ValueError(f"deterministic collision rejection: {canonical_json(collisions)}")
        payload = {
            "causal_rate": rational_json(rate),
            "collision_policy": policy,
            "collisions": collisions,
            "objects": normalized,
            "input_receipt_index": current_receipt,
        }

        def operation(conn: sqlite3.Connection) -> dict[str, Any]:
            row = conn.execute("SELECT COALESCE(MAX(seq),0) seq FROM events").fetchone()
            if int(row["seq"]) != current_receipt:
                raise RuntimeError("worldline authority changed before atomic admission")
            event_seq, event_hash = self._append_event(conn, "WORLDLINE_BATCH_ADMITTED", payload)
            return {
                "classification": CLASSIFICATION,
                "global_receipt_index": event_seq,
                "global_hash72": event_hash,
                "joint_admission": True,
                "objects": [{**item, "receipt_index": event_seq, "global_hash72": event_hash} for item in normalized],
                "collisions": collisions,
            }

        return self._execute_transaction(operation)

    @property
    def receipt_index(self) -> int:
        with self._lock:
            row = self._connection.execute("SELECT COALESCE(MAX(seq),0) seq FROM events").fetchone()
            return int(row["seq"])

    @property
    def root_hash72(self) -> str:
        with self._lock:
            row = self._connection.execute("SELECT event_hash72 FROM events ORDER BY seq DESC LIMIT 1").fetchone()
            return str(row["event_hash72"]) if row else ZERO_HASH72

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            counts = {
                "profiles": int(self._connection.execute("SELECT COUNT(*) n FROM profiles").fetchone()["n"]),
                "validated_profiles": int(self._connection.execute("SELECT COUNT(*) n FROM profiles WHERE status='VALIDATED'").fetchone()["n"]),
                "samples": int(self._connection.execute("SELECT COUNT(*) n FROM samples").fetchone()["n"]),
                "events": self.receipt_index,
                "checkpoints": int(self._connection.execute("SELECT COUNT(*) n FROM checkpoints").fetchone()["n"]),
            }
        return {
            "schema": "HHS_PASS_189_ITERATION2_STATUS_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "classification": CLASSIFICATION,
            "database": str(self.db_path),
            "root_hash72": self.root_hash72,
            "bounded_busy_timeout_ms": self.busy_timeout_ms,
            "vercel_required": False,
            "deployment_authority": "DIGITALOCEAN_SELF_HOSTED",
            **counts,
        }

    def _snapshot_payload(self) -> dict[str, Any]:
        def rows(table: str) -> list[dict[str, Any]]:
            return [dict(row) for row in self._connection.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()]

        return {
            "schema": "HHS_PASS_189_ITERATION2_CHECKPOINT_PAYLOAD_V1",
            "metadata": rows("metadata"),
            "events": rows("events"),
            "profiles": rows("profiles"),
            "samples": rows("samples"),
        }

    def create_checkpoint(self, label: str) -> dict[str, Any]:
        label_text = str(label).strip()
        if not label_text:
            raise ValueError("checkpoint label is required")
        with self._lock:
            snapshot = self._snapshot_payload()
            checkpoint_core = {
                "label": label_text,
                "receipt_index": self.receipt_index,
                "root_hash72": self.root_hash72,
                "snapshot": snapshot,
            }
            checkpoint_id = hash72({"checkpoint_id": checkpoint_core})
            checkpoint_hash = hash72(checkpoint_core)

            def operation(conn: sqlite3.Connection) -> dict[str, Any]:
                existing = conn.execute("SELECT checkpoint_hash72 FROM checkpoints WHERE checkpoint_id=?", (checkpoint_id,)).fetchone()
                if existing:
                    return {"checkpoint_id": checkpoint_id, "checkpoint_hash72": existing["checkpoint_hash72"], "idempotent": True}
                event_seq, event_hash = self._append_event(conn, "CHECKPOINT_CREATED", {"checkpoint_id": checkpoint_id, "checkpoint_hash72": checkpoint_hash, "label": label_text})
                conn.execute(
                    "INSERT INTO checkpoints(checkpoint_id,label,receipt_index,root_hash72,checkpoint_hash72,snapshot_json,created_event) VALUES(?,?,?,?,?,?,?)",
                    (checkpoint_id, label_text, checkpoint_core["receipt_index"], checkpoint_core["root_hash72"], checkpoint_hash, canonical_json(snapshot), event_seq),
                )
                return {
                    "checkpoint_id": checkpoint_id,
                    "checkpoint_hash72": checkpoint_hash,
                    "captured_receipt_index": checkpoint_core["receipt_index"],
                    "captured_root_hash72": checkpoint_core["root_hash72"],
                    "event_seq": event_seq,
                    "event_hash72": event_hash,
                    "idempotent": False,
                }

            return self._execute_transaction(operation)

    def verify_checkpoint(self, checkpoint_id: str) -> dict[str, Any]:
        row = self._connection.execute("SELECT * FROM checkpoints WHERE checkpoint_id=?", (checkpoint_id,)).fetchone()
        if not row:
            raise KeyError("unknown checkpoint")
        snapshot = json.loads(row["snapshot_json"])
        core = {
            "label": row["label"],
            "receipt_index": int(row["receipt_index"]),
            "root_hash72": row["root_hash72"],
            "snapshot": snapshot,
        }
        recomputed = hash72(core)
        valid_rows = all(
            len(str(item.get("event_hash72", ""))) == 72
            and len(str(item.get("predecessor_hash72", ""))) == 72
            for item in snapshot["events"]
        )
        return {
            "checkpoint_id": checkpoint_id,
            "checkpoint_hash72": row["checkpoint_hash72"],
            "snapshot_rows_valid": valid_rows,
            "captured_receipt_index": int(row["receipt_index"]),
            "captured_root_hash72": row["root_hash72"],
            "verified": valid_rows and recomputed == row["checkpoint_hash72"],
            "recomputed_hash72": recomputed,
        }

    def recover_checkpoint(self, checkpoint_id: str, target_db: str | os.PathLike[str]) -> dict[str, Any]:
        row = self._connection.execute("SELECT snapshot_json,root_hash72,receipt_index FROM checkpoints WHERE checkpoint_id=?", (checkpoint_id,)).fetchone()
        if not row:
            raise KeyError("unknown checkpoint")
        target = Path(target_db)
        if target.resolve() == self.db_path.resolve():
            raise ValueError("recovery target must differ from source database")
        if target.exists():
            raise ValueError("recovery target already exists")
        snapshot = json.loads(row["snapshot_json"])
        recovered = CalibrationLedger(target, busy_timeout_ms=self.busy_timeout_ms, retries=self.retries)
        try:
            with recovered._lock:
                conn = recovered._connection
                conn.execute("BEGIN IMMEDIATE")
                conn.execute("DELETE FROM metadata")
                conn.execute("DELETE FROM events")
                conn.execute("DELETE FROM profiles")
                conn.execute("DELETE FROM samples")
                for item in snapshot["metadata"]:
                    conn.execute("INSERT INTO metadata(key,value) VALUES(?,?)", (item["key"], item["value"]))
                for item in snapshot["events"]:
                    conn.execute(
                        "INSERT INTO events(seq,event_type,predecessor_hash72,event_hash72,payload_json) VALUES(?,?,?,?,?)",
                        (item["seq"], item["event_type"], item["predecessor_hash72"], item["event_hash72"], item["payload_json"]),
                    )
                for item in snapshot["profiles"]:
                    conn.execute(
                        "INSERT INTO profiles(profile_id,profile_hash72,status,payload_json,created_event) VALUES(?,?,?,?,?)",
                        (item["profile_id"], item["profile_hash72"], item["status"], item["payload_json"], item["created_event"]),
                    )
                for item in snapshot["samples"]:
                    conn.execute(
                        "INSERT INTO samples(sample_id,profile_id,accepted,residual_num,residual_den,sample_hash72,payload_json,created_event) VALUES(?,?,?,?,?,?,?,?)",
                        (item["sample_id"], item["profile_id"], item["accepted"], item["residual_num"], item["residual_den"], item["sample_hash72"], item["payload_json"], item["created_event"]),
                    )
                conn.commit()
            if recovered.receipt_index != int(row["receipt_index"]) or recovered.root_hash72 != row["root_hash72"]:
                raise RuntimeError("recovered checkpoint root mismatch")
            return {
                "checkpoint_id": checkpoint_id,
                "target_db": str(target),
                "receipt_index": recovered.receipt_index,
                "root_hash72": recovered.root_hash72,
                "recovered": True,
            }
        finally:
            recovered.close()


def verify_projection_lock(projections: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    if not projections:
        raise ValueError("projection set is empty")
    identities = {str(item.get("equation_hash72", "")) for item in projections.values()}
    receipts = {int(item.get("receipt_index", -1)) for item in projections.values()}
    if len(identities) != 1 or len(receipts) != 1:
        raise ValueError("projection identity or receipt drift")
    identity = next(iter(identities))
    _require_hash72(identity, "equation_hash72")
    receipt = next(iter(receipts))
    return {
        "locked": True,
        "equation_hash72": identity,
        "receipt_index": receipt,
        "projection_count": len(projections),
        "witness_hash72": hash72({"projections": sorted(projections), "equation_hash72": identity, "receipt_index": receipt}),
    }


def open_default_ledger() -> CalibrationLedger:
    path = os.environ.get("HHS189_I2_DB", "/var/lib/hhs-pass189/iteration2.sqlite3")
    try:
        return CalibrationLedger(path)
    except PermissionError:
        fallback = Path(os.environ.get("TMPDIR", "/tmp")) / "hhs-pass189-iteration2.sqlite3"
        return CalibrationLedger(fallback)
