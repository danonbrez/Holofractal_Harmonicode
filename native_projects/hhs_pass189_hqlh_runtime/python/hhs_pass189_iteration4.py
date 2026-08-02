#!/usr/bin/env python3
"""Pass 189 Iteration 4 driver provenance, quarantine, promotion, and rollback authority.

This module authenticates package manifests with operator-provided HMAC keys,
binds exact package bytes by SHA-256, records conformance evidence, and issues
bounded admission tokens. It never loads or executes real hardware drivers.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import shutil
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Mapping, Sequence

from hhs_pass189_iteration3 import (
    CLASSIFICATION,
    CONTRACT,
    HEX72,
    ZERO_HASH72,
    canonical_json,
    exact_fraction,
    fraction_json,
    hash72,
    integer,
    now_ns,
    require_hash72,
)

ITERATION = "HHS-P189-HQLH-ITERATION-4-DRIVER-PROVENANCE-QUARANTINE-PROMOTION"
DRIVER_KINDS = ("LOOPBACK", "FILE_SINK", "GPIO", "SERIAL", "USB", "NETWORK_DEVICE", "ACTUATOR")
SOFTWARE_TEST_KINDS = ("LOOPBACK", "FILE_SINK")
REAL_HARDWARE_KINDS = ("GPIO", "SERIAL", "USB", "NETWORK_DEVICE", "ACTUATOR")
EVIDENCE_CLASSES = ("SOFTWARE_FIXTURE", "HARDWARE_IN_LOOP")
PROMOTION_CLASSES = ("SOFTWARE_TEST_EXECUTABLE", "HARDWARE_CANDIDATE_NONEXECUTABLE")
REQUIRED_SOFTWARE_TESTS = (
    "manifest_identity",
    "payload_digest",
    "path_confinement",
    "capability_scope",
    "range_enforcement",
    "watchdog_fail_closed",
    "anti_replay",
    "rollback_ready",
)
REQUIRED_HIL_TESTS = REQUIRED_SOFTWARE_TESTS + (
    "physical_interlock",
    "measured_return_trace",
    "emergency_stop",
)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_sha256(value: Any, name: str) -> str:
    text = str(value).lower()
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise ValueError(f"{name} must be 64 lowercase hexadecimal glyphs")
    return text


def _canonical_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    driver_id = str(manifest.get("driver_id", "")).strip()
    version = str(manifest.get("version", "")).strip()
    driver_kind = str(manifest.get("driver_kind", "")).strip().upper()
    entrypoint = str(manifest.get("entrypoint", "")).strip()
    signer_id = str(manifest.get("signer_id", "")).strip()
    if not all((driver_id, version, entrypoint, signer_id)):
        raise ValueError("driver_id, version, entrypoint, and signer_id are required")
    if driver_kind not in DRIVER_KINDS:
        raise ValueError(f"driver_kind must be one of {DRIVER_KINDS}")
    path = PurePosixPath(entrypoint)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("entrypoint must be a confined relative POSIX path")
    operations = sorted({str(item).strip().upper() for item in manifest.get("operations", []) if str(item).strip()})
    capabilities = sorted({str(item).strip().lower() for item in manifest.get("capabilities", []) if str(item).strip()})
    units = sorted({str(item).strip() for item in manifest.get("units", []) if str(item).strip()})
    device_ids = sorted({str(item).strip() for item in manifest.get("device_ids", []) if str(item).strip()})
    interlocks = sorted({str(item).strip().upper() for item in manifest.get("required_interlocks", []) if str(item).strip()})
    if not operations or not capabilities or not units:
        raise ValueError("operations, capabilities, and units must be non-empty")
    minimum = exact_fraction(manifest.get("minimum", 0), "minimum")
    maximum = exact_fraction(manifest.get("maximum", 0), "maximum")
    if minimum > maximum:
        raise ValueError("minimum cannot exceed maximum")
    watchdog_timeout_ms = integer(manifest.get("watchdog_timeout_ms", 1000), "watchdog_timeout_ms", True)
    if watchdog_timeout_ms > 60_000:
        raise ValueError("watchdog_timeout_ms exceeds 60000")
    return {
        "schema": "HHS_PASS_189_ITERATION_4_DRIVER_MANIFEST_V1",
        "driver_id": driver_id,
        "version": version,
        "driver_kind": driver_kind,
        "entrypoint": str(path),
        "signer_id": signer_id,
        "payload_sha256": require_sha256(manifest.get("payload_sha256", ""), "payload_sha256"),
        "operations": operations,
        "capabilities": capabilities,
        "units": units,
        "device_ids": device_ids,
        "minimum": fraction_json(minimum),
        "maximum": fraction_json(maximum),
        "watchdog_timeout_ms": watchdog_timeout_ms,
        "required_interlocks": interlocks,
        "created_ns": integer(manifest.get("created_ns", now_ns()), "created_ns"),
    }


def sign_manifest(manifest: Mapping[str, Any], key: bytes) -> str:
    if not key:
        raise ValueError("signing key cannot be empty")
    canonical = _canonical_manifest(manifest)
    return hmac.new(key, canonical_json(canonical).encode("utf-8"), hashlib.sha256).hexdigest()


class DriverProvenanceAuthority:
    def __init__(
        self,
        database: str | os.PathLike[str],
        *,
        quarantine_directory: str | os.PathLike[str] | None = None,
        busy_timeout_ms: int = 1500,
        retry_count: int = 4,
    ) -> None:
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self.quarantine_directory = Path(quarantine_directory or self.database.parent / "iteration4-quarantine").resolve()
        self.quarantine_directory.mkdir(parents=True, exist_ok=True)
        self.busy_timeout_ms = integer(busy_timeout_ms, "busy_timeout_ms", True)
        self.retry_count = integer(retry_count, "retry_count", True)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(
            str(self.database), timeout=self.busy_timeout_ms / 1000, check_same_thread=False, isolation_level=None
        )
        self._connection.row_factory = sqlite3.Row
        for query in (
            "PRAGMA journal_mode=WAL",
            "PRAGMA synchronous=FULL",
            "PRAGMA foreign_keys=ON",
            f"PRAGMA busy_timeout={self.busy_timeout_ms}",
        ):
            self._connection.execute(query)
        self._connection.executescript(
            """
CREATE TABLE IF NOT EXISTS events(
 sequence INTEGER PRIMARY KEY,event_type TEXT NOT NULL,predecessor_hash72 TEXT NOT NULL,
 successor_hash72 TEXT NOT NULL UNIQUE,payload_json TEXT NOT NULL,created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS trust_roots(
 signer_id TEXT PRIMARY KEY,key_sha256 TEXT NOT NULL,algorithm TEXT NOT NULL,status TEXT NOT NULL,
 payload_json TEXT NOT NULL,created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS packages(
 package_id TEXT PRIMARY KEY,driver_id TEXT NOT NULL,version TEXT NOT NULL,driver_kind TEXT NOT NULL,
 signer_id TEXT NOT NULL REFERENCES trust_roots(signer_id),manifest_json TEXT NOT NULL,payload_sha256 TEXT NOT NULL,
 signature_hex TEXT NOT NULL,package_hash72 TEXT NOT NULL UNIQUE,status TEXT NOT NULL,quarantine_path TEXT NOT NULL,
 created_ns INTEGER NOT NULL,UNIQUE(driver_id,version));
CREATE TABLE IF NOT EXISTS conformance_runs(
 run_id TEXT PRIMARY KEY,package_id TEXT NOT NULL REFERENCES packages(package_id),evidence_class TEXT NOT NULL,
 report_json TEXT NOT NULL,report_hash72 TEXT NOT NULL UNIQUE,status TEXT NOT NULL,created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS promotions(
 promotion_id TEXT PRIMARY KEY,package_id TEXT NOT NULL REFERENCES packages(package_id),promotion_class TEXT NOT NULL,
 approver_a_hash72 TEXT NOT NULL,approver_b_hash72 TEXT NOT NULL,issued_ns INTEGER NOT NULL,expires_ns INTEGER NOT NULL,
 rollback_package_id TEXT,token_hash72 TEXT NOT NULL UNIQUE,status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS active_drivers(
 driver_id TEXT PRIMARY KEY,package_id TEXT NOT NULL REFERENCES packages(package_id),promotion_id TEXT NOT NULL REFERENCES promotions(promotion_id),
 promotion_class TEXT NOT NULL,activated_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS checkpoints(
 checkpoint_id TEXT PRIMARY KEY,captured_sequence INTEGER NOT NULL,captured_root_hash72 TEXT NOT NULL,
 digest_sha256 TEXT NOT NULL,path TEXT NOT NULL,created_ns INTEGER NOT NULL);
"""
        )

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            for attempt in range(self.retry_count):
                try:
                    self._connection.execute("BEGIN IMMEDIATE")
                    break
                except sqlite3.OperationalError as exc:
                    if "locked" not in str(exc).lower() or attempt + 1 >= self.retry_count:
                        raise
                    time.sleep((attempt + 1) * 0.01)
            try:
                yield self._connection
                self._connection.execute("COMMIT")
            except Exception:
                self._connection.execute("ROLLBACK")
                raise

    def _root(self, connection: sqlite3.Connection) -> tuple[int, str]:
        row = connection.execute("SELECT sequence,successor_hash72 FROM events ORDER BY sequence DESC LIMIT 1").fetchone()
        return (int(row[0]), str(row[1])) if row else (0, ZERO_HASH72)

    def _event(self, connection: sqlite3.Connection, event_type: str, payload: Mapping[str, Any], created_ns: int) -> dict[str, Any]:
        sequence, predecessor = self._root(connection)
        body = {
            "schema": "HHS_PASS_189_ITERATION_4_EVENT_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "classification": CLASSIFICATION,
            "sequence": sequence + 1,
            "event_type": event_type,
            "predecessor_hash72": predecessor,
            "payload": dict(payload),
            "created_ns": created_ns,
        }
        successor = hash72(body)
        connection.execute(
            "INSERT INTO events VALUES(?,?,?,?,?,?)",
            (sequence + 1, event_type, predecessor, successor, canonical_json(body), created_ns),
        )
        return {**body, "successor_hash72": successor}

    def register_trust_root(self, signer_id: str, key: bytes, *, created_ns: int | None = None) -> dict[str, Any]:
        signer_id = str(signer_id).strip()
        if not signer_id or not key:
            raise ValueError("signer_id and non-empty key are required")
        ns = now_ns() if created_ns is None else integer(created_ns, "created_ns")
        payload = {
            "schema": "HHS_PASS_189_ITERATION_4_TRUST_ROOT_V1",
            "signer_id": signer_id,
            "key_sha256": sha256_hex(key),
            "algorithm": "HMAC-SHA256-OPERATOR-KEY",
            "status": "ACTIVE",
            "created_ns": ns,
        }
        with self._tx() as connection:
            row = connection.execute("SELECT payload_json FROM trust_roots WHERE signer_id=?", (signer_id,)).fetchone()
            if row:
                current = json.loads(row[0])
                if canonical_json(current) != canonical_json(payload):
                    raise ValueError("signer_id already exists with different canonical payload")
                return current
            connection.execute(
                "INSERT INTO trust_roots VALUES(?,?,?,?,?,?)",
                (signer_id, payload["key_sha256"], payload["algorithm"], "ACTIVE", canonical_json(payload), ns),
            )
            event = self._event(connection, "TRUST_ROOT_REGISTERED", payload, ns)
        return {**payload, "event": event}

    def revoke_trust_root(self, signer_id: str, *, created_ns: int | None = None) -> dict[str, Any]:
        ns = now_ns() if created_ns is None else integer(created_ns, "created_ns")
        with self._tx() as connection:
            if not connection.execute("SELECT 1 FROM trust_roots WHERE signer_id=?", (signer_id,)).fetchone():
                raise ValueError("unknown signer_id")
            connection.execute("UPDATE trust_roots SET status='REVOKED' WHERE signer_id=?", (signer_id,))
            package_ids = [row[0] for row in connection.execute("SELECT package_id FROM packages WHERE signer_id=?", (signer_id,))]
            connection.execute("UPDATE packages SET status='REVOKED' WHERE signer_id=?", (signer_id,))
            for package_id in package_ids:
                connection.execute("UPDATE promotions SET status='REVOKED' WHERE package_id=?", (package_id,))
                connection.execute("DELETE FROM active_drivers WHERE package_id=?", (package_id,))
            event = self._event(connection, "TRUST_ROOT_REVOKED", {"signer_id": signer_id, "packages_revoked": package_ids}, ns)
        return {"signer_id": signer_id, "status": "REVOKED", "packages_revoked": package_ids, "event": event}

    def ingest_package(
        self,
        package_id: str,
        manifest: Mapping[str, Any],
        payload: bytes,
        signature_hex: str,
        verification_key: bytes,
    ) -> dict[str, Any]:
        package_id = str(package_id).strip()
        if not package_id:
            raise ValueError("package_id is required")
        canonical_manifest = _canonical_manifest(manifest)
        actual_digest = sha256_hex(payload)
        if actual_digest != canonical_manifest["payload_sha256"]:
            raise ValueError("payload digest does not match manifest")
        signature_hex = require_sha256(signature_hex, "signature_hex")
        expected_signature = hmac.new(
            verification_key, canonical_json(canonical_manifest).encode("utf-8"), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature_hex, expected_signature):
            raise ValueError("manifest authentication failed")
        signer_id = canonical_manifest["signer_id"]
        with self._lock:
            root = self._connection.execute(
                "SELECT key_sha256,status FROM trust_roots WHERE signer_id=?", (signer_id,)
            ).fetchone()
        if not root or root[1] != "ACTIVE" or root[0] != sha256_hex(verification_key):
            raise ValueError("signer trust root is missing, revoked, or key-mismatched")
        package_hash = hash72({"package_id": package_id, "manifest": canonical_manifest, "signature_hex": signature_hex})
        quarantine_path = (self.quarantine_directory / f"{package_id}-{actual_digest}.bin").resolve()
        try:
            quarantine_path.relative_to(self.quarantine_directory)
        except ValueError as exc:
            raise ValueError("quarantine path escaped authority directory") from exc
        temporary_path = quarantine_path.with_name(f".{quarantine_path.name}.{threading.get_ident()}.{now_ns()}.tmp")
        temporary_path.write_bytes(payload)
        os.replace(temporary_path, quarantine_path)
        ns = int(canonical_manifest["created_ns"])
        with self._tx() as connection:
            row = connection.execute("SELECT manifest_json,payload_sha256,signature_hex FROM packages WHERE package_id=?", (package_id,)).fetchone()
            if row:
                if (row[0], row[1], row[2]) != (canonical_json(canonical_manifest), actual_digest, signature_hex):
                    raise ValueError("package_id already exists with different canonical identity")
                return self.get_package(package_id)
            try:
                connection.execute(
                    "INSERT INTO packages VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        package_id,
                        canonical_manifest["driver_id"],
                        canonical_manifest["version"],
                        canonical_manifest["driver_kind"],
                        signer_id,
                        canonical_json(canonical_manifest),
                        actual_digest,
                        signature_hex,
                        package_hash,
                        "QUARANTINED",
                        str(quarantine_path),
                        ns,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("driver version already exists") from exc
            event = self._event(
                connection,
                "PACKAGE_QUARANTINED",
                {"package_id": package_id, "package_hash72": package_hash, "manifest": canonical_manifest},
                ns,
            )
        return {**self.get_package(package_id), "event": event}

    def get_package(self, package_id: str) -> dict[str, Any]:
        with self._lock:
            row = self._connection.execute("SELECT * FROM packages WHERE package_id=?", (package_id,)).fetchone()
        if not row:
            raise ValueError("unknown package_id")
        return {
            "package_id": row["package_id"],
            "manifest": json.loads(row["manifest_json"]),
            "payload_sha256": row["payload_sha256"],
            "signature_hex": row["signature_hex"],
            "package_hash72": row["package_hash72"],
            "status": row["status"],
            "quarantine_path": row["quarantine_path"],
        }

    def record_conformance(self, report: Mapping[str, Any]) -> dict[str, Any]:
        run_id = str(report.get("run_id", "")).strip()
        package_id = str(report.get("package_id", "")).strip()
        evidence_class = str(report.get("evidence_class", "")).strip().upper()
        if not run_id or not package_id:
            raise ValueError("run_id and package_id are required")
        if evidence_class not in EVIDENCE_CLASSES:
            raise ValueError(f"evidence_class must be one of {EVIDENCE_CLASSES}")
        package = self.get_package(package_id)
        if package["status"] == "REVOKED":
            raise ValueError("revoked package cannot receive conformance evidence")
        tests = {str(key): bool(value) for key, value in dict(report.get("tests", {})).items()}
        required = REQUIRED_HIL_TESTS if evidence_class == "HARDWARE_IN_LOOP" else REQUIRED_SOFTWARE_TESTS
        missing = [name for name in required if tests.get(name) is not True]
        trace_hash72 = require_hash72(report.get("trace_hash72", ""), "trace_hash72")
        physical_measurement = bool(report.get("physical_measurement", False))
        if evidence_class == "SOFTWARE_FIXTURE" and physical_measurement:
            raise ValueError("software fixture cannot claim physical measurement")
        if evidence_class == "HARDWARE_IN_LOOP" and not physical_measurement:
            raise ValueError("hardware-in-loop evidence requires physical_measurement=true")
        status = "PASS" if not missing else "FAIL"
        ns = integer(report.get("created_ns", now_ns()), "created_ns")
        payload = {
            "schema": "HHS_PASS_189_ITERATION_4_CONFORMANCE_V1",
            "run_id": run_id,
            "package_id": package_id,
            "evidence_class": evidence_class,
            "tests": tests,
            "required_tests": list(required),
            "missing_or_failed": missing,
            "trace_hash72": trace_hash72,
            "physical_measurement": physical_measurement,
            "status": status,
            "created_ns": ns,
        }
        payload["report_hash72"] = hash72(payload)
        with self._tx() as connection:
            if connection.execute("SELECT 1 FROM conformance_runs WHERE run_id=?", (run_id,)).fetchone():
                raise ValueError("run_id already exists")
            connection.execute(
                "INSERT INTO conformance_runs VALUES(?,?,?,?,?,?,?)",
                (run_id, package_id, evidence_class, canonical_json(payload), payload["report_hash72"], status, ns),
            )
            if status == "PASS":
                connection.execute("UPDATE packages SET status='CONFORMANT' WHERE package_id=?", (package_id,))
            event = self._event(connection, "CONFORMANCE_RECORDED", payload, ns)
        return {**payload, "event": event}

    def promote(self, request: Mapping[str, Any]) -> dict[str, Any]:
        promotion_id = str(request.get("promotion_id", "")).strip()
        package_id = str(request.get("package_id", "")).strip()
        if not promotion_id or not package_id:
            raise ValueError("promotion_id and package_id are required")
        package = self.get_package(package_id)
        if package["status"] != "CONFORMANT":
            raise ValueError("package must be conformant and non-revoked")
        driver_kind = package["manifest"]["driver_kind"]
        with self._lock:
            runs = self._connection.execute(
                "SELECT evidence_class,status FROM conformance_runs WHERE package_id=? ORDER BY created_ns", (package_id,)
            ).fetchall()
        passed_classes = {row[0] for row in runs if row[1] == "PASS"}
        if driver_kind in SOFTWARE_TEST_KINDS:
            promotion_class = "SOFTWARE_TEST_EXECUTABLE"
            if "SOFTWARE_FIXTURE" not in passed_classes:
                raise ValueError("software test driver requires passing software conformance")
        else:
            promotion_class = "HARDWARE_CANDIDATE_NONEXECUTABLE"
            if "HARDWARE_IN_LOOP" not in passed_classes:
                raise ValueError("real hardware driver requires passing hardware-in-loop evidence")
        approver_a = require_hash72(request.get("approver_a_hash72", ""), "approver_a_hash72")
        approver_b = require_hash72(request.get("approver_b_hash72", ""), "approver_b_hash72")
        if approver_a == approver_b:
            raise ValueError("dual approval requires distinct approvers")
        issued_ns = integer(request.get("issued_ns", now_ns()), "issued_ns")
        expires_ns = integer(request.get("expires_ns", 0), "expires_ns")
        if expires_ns <= issued_ns or expires_ns - issued_ns > 7 * 24 * 60 * 60 * 1_000_000_000:
            raise ValueError("promotion expiry must be within seven days")
        rollback_package_id = str(request.get("rollback_package_id", "")).strip() or None
        if rollback_package_id:
            rollback = self.get_package(rollback_package_id)
            if rollback["manifest"]["driver_id"] != package["manifest"]["driver_id"]:
                raise ValueError("rollback package must belong to the same driver_id")
            if rollback["status"] == "REVOKED":
                raise ValueError("rollback package cannot be revoked")
        token_payload = {
            "schema": "HHS_PASS_189_ITERATION_4_ADMISSION_TOKEN_V1",
            "promotion_id": promotion_id,
            "package_id": package_id,
            "driver_id": package["manifest"]["driver_id"],
            "driver_kind": driver_kind,
            "promotion_class": promotion_class,
            "package_hash72": package["package_hash72"],
            "approver_a_hash72": approver_a,
            "approver_b_hash72": approver_b,
            "issued_ns": issued_ns,
            "expires_ns": expires_ns,
            "rollback_package_id": rollback_package_id,
            "executable": promotion_class == "SOFTWARE_TEST_EXECUTABLE",
            "real_hardware_dispatch_authorized": False,
        }
        token_hash = hash72(token_payload)
        with self._tx() as connection:
            if connection.execute("SELECT 1 FROM promotions WHERE promotion_id=?", (promotion_id,)).fetchone():
                raise ValueError("promotion_id already exists")
            connection.execute(
                "INSERT INTO promotions VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    promotion_id,
                    package_id,
                    promotion_class,
                    approver_a,
                    approver_b,
                    issued_ns,
                    expires_ns,
                    rollback_package_id,
                    token_hash,
                    "ACTIVE",
                ),
            )
            connection.execute(
                "INSERT INTO active_drivers VALUES(?,?,?,?,?) ON CONFLICT(driver_id) DO UPDATE SET package_id=excluded.package_id,promotion_id=excluded.promotion_id,promotion_class=excluded.promotion_class,activated_ns=excluded.activated_ns",
                (package["manifest"]["driver_id"], package_id, promotion_id, promotion_class, issued_ns),
            )
            connection.execute("UPDATE packages SET status='PROMOTED' WHERE package_id=?", (package_id,))
            event = self._event(connection, "PACKAGE_PROMOTED", {**token_payload, "token_hash72": token_hash}, issued_ns)
        return {**token_payload, "token_hash72": token_hash, "event": event}

    def revoke_promotion(self, promotion_id: str, *, created_ns: int | None = None) -> dict[str, Any]:
        ns = now_ns() if created_ns is None else integer(created_ns, "created_ns")
        with self._tx() as connection:
            row = connection.execute("SELECT package_id FROM promotions WHERE promotion_id=?", (promotion_id,)).fetchone()
            if not row:
                raise ValueError("unknown promotion_id")
            connection.execute("UPDATE promotions SET status='REVOKED' WHERE promotion_id=?", (promotion_id,))
            connection.execute("DELETE FROM active_drivers WHERE promotion_id=?", (promotion_id,))
            connection.execute("UPDATE packages SET status='CONFORMANT' WHERE package_id=? AND status='PROMOTED'", (row[0],))
            event = self._event(connection, "PROMOTION_REVOKED", {"promotion_id": promotion_id, "package_id": row[0]}, ns)
        return {"promotion_id": promotion_id, "package_id": row[0], "status": "REVOKED", "event": event}

    def rollback(self, promotion_id: str, *, created_ns: int | None = None) -> dict[str, Any]:
        ns = now_ns() if created_ns is None else integer(created_ns, "created_ns")
        with self._tx() as connection:
            row = connection.execute(
                "SELECT p.package_id,p.rollback_package_id,p.status,k.driver_id FROM promotions p JOIN packages k ON k.package_id=p.package_id WHERE p.promotion_id=?",
                (promotion_id,),
            ).fetchone()
            if not row:
                raise ValueError("unknown promotion_id")
            if row[2] != "ACTIVE" or not row[1]:
                raise ValueError("active promotion has no rollback package")
            rollback = connection.execute("SELECT status FROM packages WHERE package_id=?", (row[1],)).fetchone()
            if not rollback or rollback[0] == "REVOKED":
                raise ValueError("rollback package unavailable")
            connection.execute("UPDATE promotions SET status='ROLLED_BACK' WHERE promotion_id=?", (promotion_id,))
            connection.execute("UPDATE packages SET status='CONFORMANT' WHERE package_id=?", (row[0],))
            connection.execute(
                "UPDATE active_drivers SET package_id=?,promotion_id=?,promotion_class='ROLLBACK_REFERENCE',activated_ns=? WHERE driver_id=?",
                (row[1], promotion_id, ns, row[3]),
            )
            event = self._event(
                connection,
                "PROMOTION_ROLLED_BACK",
                {"promotion_id": promotion_id, "from_package_id": row[0], "to_package_id": row[1], "driver_id": row[3]},
                ns,
            )
        return {"promotion_id": promotion_id, "from_package_id": row[0], "to_package_id": row[1], "status": "ROLLED_BACK", "event": event}

    def verify_chain(self) -> dict[str, Any]:
        with self._lock:
            rows = self._connection.execute("SELECT * FROM events ORDER BY sequence").fetchall()
        predecessor = ZERO_HASH72
        for expected_sequence, row in enumerate(rows, 1):
            payload = json.loads(row["payload_json"])
            if row["sequence"] != expected_sequence or row["predecessor_hash72"] != predecessor:
                return {"valid": False, "failure_sequence": expected_sequence}
            if hash72(payload) != row["successor_hash72"]:
                return {"valid": False, "failure_sequence": expected_sequence}
            predecessor = row["successor_hash72"]
        return {"valid": True, "events": len(rows), "root_hash72": predecessor}

    def status(self) -> dict[str, Any]:
        with self._lock:
            counts = {
                "events": self._connection.execute("SELECT COUNT(*) FROM events").fetchone()[0],
                "trust_roots": self._connection.execute("SELECT COUNT(*) FROM trust_roots WHERE status='ACTIVE'").fetchone()[0],
                "packages": self._connection.execute("SELECT COUNT(*) FROM packages").fetchone()[0],
                "quarantined": self._connection.execute("SELECT COUNT(*) FROM packages WHERE status='QUARANTINED'").fetchone()[0],
                "conformant": self._connection.execute("SELECT COUNT(*) FROM packages WHERE status='CONFORMANT'").fetchone()[0],
                "promoted": self._connection.execute("SELECT COUNT(*) FROM packages WHERE status='PROMOTED'").fetchone()[0],
                "active_drivers": self._connection.execute("SELECT COUNT(*) FROM active_drivers").fetchone()[0],
                "hardware_candidates": self._connection.execute("SELECT COUNT(*) FROM promotions WHERE promotion_class='HARDWARE_CANDIDATE_NONEXECUTABLE' AND status='ACTIVE'").fetchone()[0],
            }
            sequence, root = self._root(self._connection)
        return {
            "status": "ok",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "classification": CLASSIFICATION,
            "deployment_authority": "DIGITALOCEAN_SELF_HOSTED",
            "vercel_required": False,
            "real_hardware_dispatch_authorized": False,
            "sequence": sequence,
            "root_hash72": root,
            **counts,
        }

    def checkpoint(self, path: str | os.PathLike[str], checkpoint_id: str, *, created_ns: int | None = None) -> dict[str, Any]:
        target = Path(path).resolve()
        if target.exists():
            raise ValueError("checkpoint destination already exists")
        target.parent.mkdir(parents=True, exist_ok=True)
        ns = now_ns() if created_ns is None else integer(created_ns, "created_ns")
        with self._lock:
            sequence, root = self._root(self._connection)
            destination = sqlite3.connect(str(target))
            try:
                self._connection.backup(destination)
            finally:
                destination.close()
        digest = sha256_hex(target.read_bytes())
        with self._tx() as connection:
            connection.execute(
                "INSERT INTO checkpoints VALUES(?,?,?,?,?,?)",
                (checkpoint_id, sequence, root, digest, str(target), ns),
            )
            event = self._event(
                connection,
                "CHECKPOINT_CREATED",
                {"checkpoint_id": checkpoint_id, "captured_sequence": sequence, "captured_root_hash72": root, "digest_sha256": digest},
                ns,
            )
        return {
            "checkpoint_id": checkpoint_id,
            "captured_sequence": sequence,
            "captured_root_hash72": root,
            "digest_sha256": digest,
            "path": str(target),
            "event": event,
        }

    @staticmethod
    def verify_checkpoint(path: str | os.PathLike[str], digest_sha256: str, sequence: int, root_hash72: str) -> dict[str, Any]:
        checkpoint = Path(path)
        if not checkpoint.is_file() or sha256_hex(checkpoint.read_bytes()) != require_sha256(digest_sha256, "digest_sha256"):
            return {"valid": False, "reason": "DIGEST_MISMATCH"}
        connection = sqlite3.connect(str(checkpoint))
        try:
            row = connection.execute("SELECT sequence,successor_hash72 FROM events ORDER BY sequence DESC LIMIT 1").fetchone()
            actual = (int(row[0]), str(row[1])) if row else (0, ZERO_HASH72)
        finally:
            connection.close()
        valid = actual == (integer(sequence, "sequence"), require_hash72(root_hash72, "root_hash72"))
        return {"valid": valid, "captured_sequence": actual[0], "captured_root_hash72": actual[1]}

    @classmethod
    def recover(cls, checkpoint: str | os.PathLike[str], destination: str | os.PathLike[str], digest_sha256: str, sequence: int, root_hash72: str) -> "DriverProvenanceAuthority":
        verification = cls.verify_checkpoint(checkpoint, digest_sha256, sequence, root_hash72)
        if not verification["valid"]:
            raise ValueError("checkpoint verification failed")
        destination_path = Path(destination)
        if destination_path.exists():
            raise ValueError("recovery destination already exists")
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(checkpoint, destination_path)
        authority = cls(destination_path)
        chain = authority.verify_chain()
        if not chain["valid"] or chain["events"] != integer(sequence, "sequence") or chain["root_hash72"] != root_hash72:
            authority.close()
            raise ValueError("recovered authority does not match captured root")
        return authority


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HHS Pass 189 Iteration 4 driver provenance authority")
    parser.add_argument("--database", default=os.environ.get("HHS189_I4_DB", "/tmp/pass189-i4.sqlite3"))
    parser.add_argument("--quarantine", default=os.environ.get("HHS189_I4_QUARANTINE", "/tmp/pass189-i4-quarantine"))
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    subparsers.add_parser("verify-chain")
    sign = subparsers.add_parser("sign-manifest")
    sign.add_argument("manifest_file")
    sign.add_argument("key_base64")
    args = parser.parse_args(argv)
    if args.command == "sign-manifest":
        manifest = json.loads(Path(args.manifest_file).read_text(encoding="utf-8"))
        print(sign_manifest(manifest, base64.b64decode(args.key_base64)))
        return 0
    authority = DriverProvenanceAuthority(args.database, quarantine_directory=args.quarantine)
    try:
        result = authority.status() if args.command == "status" else authority.verify_chain()
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        authority.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
