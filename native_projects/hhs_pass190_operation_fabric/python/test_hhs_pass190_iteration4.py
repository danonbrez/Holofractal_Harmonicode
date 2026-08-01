from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "server"))

from hhs_pass190 import StateConflictError  # noqa: E402
from hhs_pass190_iteration3_hardening import HardenedAuthorityContext  # noqa: E402
from hhs_pass190_iteration4 import (  # noqa: E402
    DistributedAuthorityContext,
    DistributedAuthorityStore,
    LeaseBusyError,
    StaleFenceError,
)
from hhs_pass190_iteration4_server import build_server  # noqa: E402

SECRET = "pass190-iteration4-test-secret-" + ("w" * 48)


class MutableClock:
    def __init__(self, value: int):
        self.value = value

    def __call__(self) -> int:
        return self.value


class Iteration4Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "authority.sqlite3"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_independent_contexts_refresh_before_admission(self) -> None:
        first = DistributedAuthorityContext(self.db, holder_id="process-a")
        second = DistributedAuthorityContext(self.db, holder_id="process-b")
        try:
            one = first.invoke(
                "state.counter.advance",
                {"delta": 2},
                capabilities={"runtime.mutate"},
            )
            two = second.invoke(
                "state.counter.advance",
                {"delta": 3},
                capabilities={"runtime.mutate"},
            )
            self.assertEqual(one.result["before"], 0)
            self.assertEqual(two.result["before"], 2)
            self.assertEqual(two.result["after"], 5)
            self.assertEqual(two.receipt["receipt_index"], 2)
            report = second.integrity_report()
            self.assertEqual(report["fence_count"], 2)
            self.assertEqual(report["highest_committed_fence"], 2)
        finally:
            first.close()
            second.close()

    def test_lease_contention_fails_with_bounded_error(self) -> None:
        clock = MutableClock(1_000)
        first = DistributedAuthorityStore(self.db, clock_ns=clock, sleeper=lambda _seconds: None)
        second = DistributedAuthorityStore(self.db, clock_ns=clock, sleeper=lambda _seconds: None)
        try:
            grant = first.acquire_lease("holder-a", ttl_ns=100, wait_ns=0)
            with self.assertRaises(LeaseBusyError):
                second.acquire_lease("holder-b", ttl_ns=100, wait_ns=0)
            with first.admission(grant):
                pass
            recovered = second.acquire_lease("holder-b", ttl_ns=100, wait_ns=0)
            self.assertGreater(recovered.fencing_token, grant.fencing_token)
            with second.admission(recovered):
                pass
        finally:
            first.close()
            second.close()

    def test_expired_lease_takeover_rejects_stale_fence(self) -> None:
        clock = MutableClock(10_000)
        first = DistributedAuthorityStore(self.db, clock_ns=clock, sleeper=lambda _seconds: None)
        second = DistributedAuthorityStore(self.db, clock_ns=clock, sleeper=lambda _seconds: None)
        try:
            stale = first.acquire_lease("holder-a", ttl_ns=10, wait_ns=0)
            clock.value = 10_011
            current = second.acquire_lease("holder-b", ttl_ns=100, wait_ns=0)
            self.assertGreater(current.fencing_token, stale.fencing_token)
            with self.assertRaises(StaleFenceError):
                with first.admission(stale):
                    pass
            with second.admission(current):
                pass
        finally:
            first.close()
            second.close()

    def test_iteration3_receipts_receive_migration_fences(self) -> None:
        legacy = HardenedAuthorityContext(self.db)
        legacy.invoke("system.status", {})
        legacy.close()
        current = DistributedAuthorityContext(self.db, holder_id="migration-reader")
        try:
            arbitration = current.arbitration_report()
            self.assertEqual(arbitration["fence_count"], 1)
            connection = sqlite3.connect(self.db)
            migrated = connection.execute(
                "SELECT legacy_migration,holder_id FROM authority_fences WHERE receipt_index=1"
            ).fetchone()
            connection.close()
            self.assertEqual(migrated, (1, "iteration3-migration"))
        finally:
            current.close()

    def test_fence_tamper_is_rejected(self) -> None:
        context = DistributedAuthorityContext(self.db, holder_id="writer")
        context.invoke("system.status", {})
        context.close()
        connection = sqlite3.connect(self.db)
        connection.execute(
            "UPDATE authority_fences SET fence_hash72=? WHERE receipt_index=1",
            ("0" * 72,),
        )
        connection.commit()
        connection.close()
        with self.assertRaises(Exception) as captured:
            DistributedAuthorityContext(self.db, holder_id="reader")
        self.assertIn("fencing witness Hash72 mismatch", str(captured.exception))

    def test_expected_state_is_checked_after_distributed_refresh(self) -> None:
        first = DistributedAuthorityContext(self.db, holder_id="process-a")
        second = DistributedAuthorityContext(self.db, holder_id="process-b")
        stale_root = second.state_root
        try:
            first.invoke(
                "state.counter.advance",
                {"delta": 1},
                capabilities={"runtime.mutate"},
            )
            with self.assertRaises(StateConflictError):
                second.invoke(
                    "state.counter.advance",
                    {"delta": 1},
                    capabilities={"runtime.mutate"},
                    expected_state=stale_root,
                )
            report = first.integrity_report()
            self.assertEqual(report["receipt_count"], 1)
            self.assertEqual(report["fence_count"], 1)
        finally:
            first.close()
            second.close()

    def test_separate_python_processes_share_one_chain(self) -> None:
        script = """
import json, sys
from hhs_pass190_iteration4 import DistributedAuthorityContext
ctx = DistributedAuthorityContext(sys.argv[1], holder_id=sys.argv[2])
try:
    result = ctx.invoke('state.counter.advance', {'delta': int(sys.argv[3])}, capabilities={'runtime.mutate'})
    print(json.dumps({'before': result.result['before'], 'after': result.result['after'], 'index': result.receipt['receipt_index']}))
finally:
    ctx.close()
"""
        environment = dict(__import__("os").environ)
        environment["PYTHONPATH"] = str(ROOT / "python")
        first = json.loads(subprocess.check_output(
            [sys.executable, "-c", script, str(self.db), "external-a", "4"],
            text=True,
            env=environment,
        ))
        second = json.loads(subprocess.check_output(
            [sys.executable, "-c", script, str(self.db), "external-b", "6"],
            text=True,
            env=environment,
        ))
        self.assertEqual(first, {"before": 0, "after": 4, "index": 1})
        self.assertEqual(second, {"before": 4, "after": 10, "index": 2})
        reader = DistributedAuthorityContext(self.db, holder_id="reader")
        try:
            self.assertEqual(reader.integrity_report()["highest_committed_fence"], 2)
        finally:
            reader.close()

    def test_server_exposes_iteration4_arbitration(self) -> None:
        context = DistributedAuthorityContext(self.db, holder_id="server")
        server = build_server(port=0, context=context, capability_secret=SECRET)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            with urlopen(base + "/api/pass190/health", timeout=5) as response:
                health = json.load(response)
            self.assertEqual(health["result"]["status"], "ok")
            with urlopen(base + "/api/pass190/arbitration", timeout=5) as response:
                arbitration = json.load(response)
            self.assertFalse(arbitration["active"])
            self.assertEqual(arbitration["fence_count"], 1)
            with urlopen(base + "/openapi.json", timeout=5) as response:
                openapi = json.load(response)
            self.assertEqual(openapi["x-hhs-iteration"], 4)
            self.assertIn("/api/pass190/arbitration", openapi["paths"])
            self.assertIn("/api/pass190/compile-execute", openapi["paths"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
