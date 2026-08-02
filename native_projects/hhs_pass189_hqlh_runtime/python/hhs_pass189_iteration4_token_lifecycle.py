#!/usr/bin/env python3
"""Pass 189 Iteration 4 promotion-token lifecycle closure.

This authority extends the merged provenance/quarantine implementation with a
required issue witness, v2 token identity, explicit token validation, and
persistent promotion expiry. The DigitalOcean Iteration 4 service uses this
class; the original class remains a pre-lifecycle compatibility surface.
"""
from __future__ import annotations

from typing import Any, Mapping

from hhs_pass189_iteration3 import hash72, integer, now_ns, require_hash72
from hhs_pass189_iteration4 import (
    DriverProvenanceAuthority,
    SOFTWARE_TEST_KINDS,
)


class DriverProvenanceLifecycleAuthority(DriverProvenanceAuthority):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        columns = {row[1] for row in self._connection.execute("PRAGMA table_info(promotions)")}
        if "issue_witness_hash72" not in columns:
            self._connection.execute(
                "ALTER TABLE promotions ADD COLUMN issue_witness_hash72 TEXT NOT NULL DEFAULT '" + ("0" * 72) + "'"
            )

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
                "SELECT evidence_class,status FROM conformance_runs WHERE package_id=? ORDER BY created_ns",
                (package_id,),
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
        issue_witness = require_hash72(request.get("issue_witness_hash72", ""), "issue_witness_hash72")
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
            "schema": "HHS_PASS_189_ITERATION_4_ADMISSION_TOKEN_V2",
            "promotion_id": promotion_id,
            "package_id": package_id,
            "driver_id": package["manifest"]["driver_id"],
            "driver_kind": driver_kind,
            "promotion_class": promotion_class,
            "package_hash72": package["package_hash72"],
            "approver_a_hash72": approver_a,
            "approver_b_hash72": approver_b,
            "issue_witness_hash72": issue_witness,
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
                "INSERT INTO promotions(promotion_id,package_id,promotion_class,approver_a_hash72,approver_b_hash72,issued_ns,expires_ns,rollback_package_id,token_hash72,status,issue_witness_hash72) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
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
                    issue_witness,
                ),
            )
            connection.execute(
                "INSERT INTO active_drivers VALUES(?,?,?,?,?) ON CONFLICT(driver_id) DO UPDATE SET package_id=excluded.package_id,promotion_id=excluded.promotion_id,promotion_class=excluded.promotion_class,activated_ns=excluded.activated_ns",
                (package["manifest"]["driver_id"], package_id, promotion_id, promotion_class, issued_ns),
            )
            connection.execute("UPDATE packages SET status='PROMOTED' WHERE package_id=?", (package_id,))
            event = self._event(connection, "PACKAGE_PROMOTED_V2", {**token_payload, "token_hash72": token_hash}, issued_ns)
        return {**token_payload, "token_hash72": token_hash, "event": event}

    def sweep_expired_promotions(self, *, at_ns: int | None = None) -> dict[str, Any]:
        ns = now_ns() if at_ns is None else integer(at_ns, "at_ns")
        with self._tx() as connection:
            rows = connection.execute(
                "SELECT promotion_id,package_id FROM promotions WHERE status='ACTIVE' AND expires_ns<=? ORDER BY promotion_id",
                (ns,),
            ).fetchall()
            expired = [{"promotion_id": row[0], "package_id": row[1]} for row in rows]
            for item in expired:
                connection.execute("UPDATE promotions SET status='EXPIRED' WHERE promotion_id=?", (item["promotion_id"],))
                connection.execute("DELETE FROM active_drivers WHERE promotion_id=?", (item["promotion_id"],))
                connection.execute(
                    "UPDATE packages SET status='CONFORMANT' WHERE package_id=? AND status='PROMOTED'",
                    (item["package_id"],),
                )
            event = None
            if expired:
                event = self._event(connection, "PROMOTIONS_EXPIRED", {"expired": expired, "at_ns": ns}, ns)
        return {"expired": expired, "count": len(expired), "at_ns": ns, "event": event}

    def validate_promotion_token(self, token_hash72: str, *, at_ns: int | None = None) -> dict[str, Any]:
        token_hash = require_hash72(token_hash72, "token_hash72")
        ns = now_ns() if at_ns is None else integer(at_ns, "at_ns")
        self.sweep_expired_promotions(at_ns=ns)
        with self._lock:
            row = self._connection.execute(
                """SELECT p.*,k.driver_id,k.driver_kind,k.package_hash72,k.status AS package_status,
                          t.status AS trust_status,a.package_id AS active_package_id,a.promotion_id AS active_promotion_id
                   FROM promotions p
                   JOIN packages k ON k.package_id=p.package_id
                   JOIN trust_roots t ON t.signer_id=k.signer_id
                   LEFT JOIN active_drivers a ON a.driver_id=k.driver_id
                   WHERE p.token_hash72=?""",
                (token_hash,),
            ).fetchone()
        if not row:
            return {"valid": False, "reason": "UNKNOWN_TOKEN", "token_hash72": token_hash, "at_ns": ns}
        reasons: list[str] = []
        if row["status"] != "ACTIVE":
            reasons.append(f"PROMOTION_{row['status']}")
        if row["package_status"] != "PROMOTED":
            reasons.append(f"PACKAGE_{row['package_status']}")
        if row["trust_status"] != "ACTIVE":
            reasons.append("TRUST_ROOT_INACTIVE")
        if not (row["issued_ns"] <= ns < row["expires_ns"]):
            reasons.append("TOKEN_OUTSIDE_VALIDITY_WINDOW")
        if row["active_package_id"] != row["package_id"] or row["active_promotion_id"] != row["promotion_id"]:
            reasons.append("NOT_ACTIVE_DRIVER_DESIGNATION")
        executable = row["promotion_class"] == "SOFTWARE_TEST_EXECUTABLE" and row["driver_kind"] in SOFTWARE_TEST_KINDS
        return {
            "valid": not reasons,
            "reason": "VALID" if not reasons else reasons[0],
            "reasons": reasons,
            "token_hash72": token_hash,
            "promotion_id": row["promotion_id"],
            "package_id": row["package_id"],
            "driver_id": row["driver_id"],
            "driver_kind": row["driver_kind"],
            "promotion_class": row["promotion_class"],
            "issue_witness_hash72": row["issue_witness_hash72"],
            "issued_ns": row["issued_ns"],
            "expires_ns": row["expires_ns"],
            "executable": executable and not reasons,
            "real_hardware_dispatch_authorized": False,
            "at_ns": ns,
        }

    def status(self) -> dict[str, Any]:
        self.sweep_expired_promotions()
        return super().status()
