from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))

from hhs_pass190_iteration3_hardening import HardenedAuthorityContext  # noqa: E402
from hhs_pass190_iteration4 import DistributedAuthorityContext, LeaseBusyError, StaleFenceError  # noqa: E402
from hhs_pass190_iteration5 import CorrectedAuthorityContext  # noqa: E402
from hhs_pass190_iteration5_server import build_server  # noqa: E402

SECRET = "pass190-iteration5-test-secret-" + ("r" * 48)


class Iteration5Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "authority.sqlite3"
        self.context = CorrectedAuthorityContext(self.db, holder_id="primary")

    def tearDown(self) -> None:
        try:
            self.context.close()
        except sqlite3.ProgrammingError:
            pass
        self.temp.cleanup()

    def _block_database(self) -> tuple[threading.Event, threading.Event, threading.Thread]:
        ready = threading.Event()
        release = threading.Event()

        def hold() -> None:
            connection = sqlite3.connect(self.db, timeout=5)
            connection.execute("BEGIN IMMEDIATE")
            ready.set()
            release.wait(5)
            connection.rollback()
            connection.close()

        thread = threading.Thread(target=hold, daemon=True)
        thread.start()
        self.assertTrue(ready.wait(2))
        return ready, release, thread

    def test_operation_has_lease_transition_and_kernel_witnesses(self) -> None:
        result = self.context.invoke("system.status", {})
        transitions = self.context.lease_receipts_after()
        self.assertEqual([item["transition"] for item in transitions], ["ACQUIRED", "RELEASED"])
        self.assertEqual(transitions[0]["fencing_token"], transitions[1]["fencing_token"])
        connection = sqlite3.connect(self.db)
        connection.row_factory = sqlite3.Row
        fence = connection.execute(
            "SELECT lease_acquire_hash72,kernel_authority_hash72 FROM authority_fences "
            "WHERE receipt_hash72=?", (result.receipt["hash72"],)
        ).fetchone()
        event = json.loads(connection.execute(
            "SELECT payload_json FROM events WHERE event_type='operation.admitted'"
        ).fetchone()[0])
        connection.close()
        self.assertEqual(fence["lease_acquire_hash72"], transitions[0]["receipt_hash72"])
        self.assertEqual(len(fence["kernel_authority_hash72"]), 72)
        self.assertEqual(event["kernel_authority_hash72"], fence["kernel_authority_hash72"])
        integrity = self.context.integrity_report()
        self.assertTrue(integrity["atomic_snapshot_verified"])
        self.assertTrue(integrity["lease_receipts_verified"])
        self.assertTrue(integrity["kernel_authority_verified"])

    def test_failed_candidate_gets_failed_release_receipt(self) -> None:
        with self.assertRaises(Exception):
            self.context.invoke("unknown.operation", {})
        transitions = self.context.lease_receipts_after()
        self.assertEqual([item["transition"] for item in transitions], ["ACQUIRED", "FAILED_RELEASED"])
        self.assertEqual(self.context.integrity_report()["receipt_count"], 0)

    def test_sqlite_lock_is_retried_then_succeeds(self) -> None:
        _ready, release, thread = self._block_database()
        timer = threading.Timer(0.08, release.set)
        timer.start()
        result = self.context.invoke("system.status", {})
        timer.join(2)
        thread.join(2)
        self.assertEqual(result.operation_id, "system.status")
        self.assertEqual(self.context.integrity_report()["receipt_count"], 1)

    def test_sqlite_lock_timeout_is_typed(self) -> None:
        self.context.close()
        self.context = CorrectedAuthorityContext(
            self.db, holder_id="bounded", lease_wait_ns=20_000_000
        )
        _ready, release, thread = self._block_database()
        try:
            with self.assertRaises(LeaseBusyError):
                self.context.invoke("system.status", {})
        finally:
            release.set()
            thread.join(2)

    def test_legacy_receipt_is_validated_before_fence_migration(self) -> None:
        legacy_path = Path(self.temp.name) / "legacy-tamper.sqlite3"
        legacy = HardenedAuthorityContext(legacy_path)
        legacy.invoke("system.status", {})
        legacy.close()
        connection = sqlite3.connect(legacy_path)
        payload = json.loads(connection.execute("SELECT payload_json FROM receipts").fetchone()[0])
        payload["result"]["status"] = "tampered"
        connection.execute("UPDATE receipts SET payload_json=?", (json.dumps(payload),))
        connection.commit()
        connection.close()
        with self.assertRaises(Exception):
            CorrectedAuthorityContext(legacy_path)
        connection = sqlite3.connect(legacy_path)
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='authority_fences'"
        ).fetchone()
        count = 0 if table is None else connection.execute("SELECT COUNT(*) FROM authority_fences").fetchone()[0]
        connection.close()
        self.assertEqual(count, 0)

    def test_iteration4_database_is_migrated_additively(self) -> None:
        legacy_path = Path(self.temp.name) / "iteration4.sqlite3"
        legacy = DistributedAuthorityContext(legacy_path, holder_id="iteration4")
        admitted = legacy.invoke("system.status", {})
        legacy.close()
        upgraded = CorrectedAuthorityContext(legacy_path, holder_id="iteration5")
        try:
            self.assertEqual(upgraded.integrity_report()["receipt_count"], 1)
            receipt = upgraded.lease_receipts_after()[0]
            self.assertEqual(receipt["transition"], "MIGRATED")
            connection = sqlite3.connect(legacy_path)
            row = connection.execute(
                "SELECT lease_acquire_hash72,kernel_authority_hash72 FROM authority_fences "
                "WHERE receipt_hash72=?", (admitted.receipt["hash72"],)
            ).fetchone()
            connection.close()
            self.assertEqual(row[0], receipt["receipt_hash72"])
            self.assertEqual(len(row[1]), 72)
        finally:
            upgraded.close()

    def test_expired_lease_is_receipted_and_old_grant_is_stale(self) -> None:
        now = [1_000]
        self.context.close()
        self.context = CorrectedAuthorityContext(
            self.db,
            holder_id="clocked",
            lease_ttl_ns=10,
            clock_ns=lambda: now[0],
            sleeper=lambda _seconds: None,
        )
        grant = self.context.store.acquire_lease("old", ttl_ns=10, wait_ns=0)
        now[0] = 1_020
        report = self.context.arbitration_report()
        self.assertFalse(report["active"])
        self.assertEqual(report["last_transition"], "EXPIRED")
        with self.assertRaises(StaleFenceError):
            self.context.store._verify_kernel_grant(grant)
        next_grant = self.context.store.acquire_lease("new", ttl_ns=10, wait_ns=0)
        self.assertGreater(next_grant.fencing_token, grant.fencing_token)
        with self.context.store.admission(next_grant):
            pass

    def test_restore_validation_executes_inside_one_transaction(self) -> None:
        self.context.invoke("system.status", {})
        statements: list[str] = []
        self.context.store._connection.set_trace_callback(statements.append)
        self.context.store.restore_into(self.context)
        self.context.store._connection.set_trace_callback(None)
        normalized = [statement.strip().upper() for statement in statements]
        begin = next(index for index, statement in enumerate(normalized) if statement == "BEGIN")
        receipt_read = next(index for index, statement in enumerate(normalized) if "FROM RECEIPTS" in statement)
        commit = max(index for index, statement in enumerate(normalized) if statement == "COMMIT")
        self.assertLess(begin, receipt_read)
        self.assertLess(receipt_read, commit)

    def test_active_lease_is_a_valid_arbitration_state(self) -> None:
        grant = self.context.store.acquire_lease("observer", wait_ns=0)
        report = self.context.arbitration_report()
        self.assertTrue(report["active"])
        self.assertEqual(report["lease_state"], "active")
        self.assertEqual(report["last_transition"], "ACQUIRED")
        with self.context.store.admission(grant):
            pass
        self.assertEqual(self.context.arbitration_report()["lease_state"], "released")

    def test_server_preserves_structured_503_for_custom_routes(self) -> None:
        class FailingContext(CorrectedAuthorityContext):
            def arbitration_report(self):
                raise sqlite3.OperationalError("simulated authority failure")

        failing = FailingContext(Path(self.temp.name) / "failing.sqlite3")
        server = build_server(port=0, context=failing, capability_secret=SECRET)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with self.assertRaises(HTTPError) as caught:
                urlopen(
                    f"http://127.0.0.1:{server.server_address[1]}/api/pass190/arbitration",
                    timeout=5,
                )
            self.assertEqual(caught.exception.code, 503)
            payload = json.loads(caught.exception.read())
            self.assertEqual(payload["error"], "persistent_authority_unavailable")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_live_server_projects_iteration5_receipts(self) -> None:
        server = build_server(port=0, context=self.context, capability_secret=SECRET)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            health = json.loads(urlopen(base + "/api/pass190/health", timeout=5).read())
            self.assertEqual(health["result"]["status"], "ok")
            arbitration = json.loads(urlopen(base + "/api/pass190/arbitration", timeout=5).read())
            self.assertTrue(arbitration["lease_receipt_chain_verified"])
            receipts = json.loads(urlopen(base + "/api/pass190/lease-receipts", timeout=5).read())
            self.assertEqual([item["transition"] for item in receipts["lease_receipts"][-2:]], ["ACQUIRED", "RELEASED"])
            openapi = json.loads(urlopen(base + "/openapi.json", timeout=5).read())
            self.assertEqual(openapi["x-hhs-iteration"], 5)
            self.assertIn("/api/pass190/lease-receipts", openapi["paths"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            self.context = CorrectedAuthorityContext(self.db, holder_id="restored")


if __name__ == "__main__":
    unittest.main(verbosity=2)
