from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path

from hhs_backend.runtime.hhs_pass196_scan_jobs_v1 import (
    Pass196ScanJobManager,
    Pass196ScanJobError,
)


class Pass196ScanJobManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.state_root = Path(self.temp.name)
        self.release = threading.Event()
        self.started = threading.Event()
        self.calls = 0
        self.authorization_calls = 0

        def runner(**kwargs):
            self.calls += 1
            self.started.set()
            self.release.wait(timeout=5)
            return {
                "schema": "HHS_PASS_196_INTEGRATED_ENVIRONMENT_STATUS_V1",
                "phase": "DEGRADED",
                "scanned": True,
                "operational": True,
                "integration_closed": False,
                "ok": False,
                "manifest_hash72": "h" * 72,
                "file_count": 4900,
                "pass_state_counts": {"INTEGRATED": 108, "PARTIAL": 70},
                "gap_scope": {
                    "schema": "HHS_PASS_196_INTEGRATION_GAP_PARTITION_V1",
                    "legacy_unresolved_count": 12,
                    "current_frontier_closed": True,
                },
                "manifest": {"must_not_be_persisted": True},
                "kwargs": kwargs,
            }

        self.manager = Pass196ScanJobManager(
            runner,
            state_root=self.state_root,
        )

    def tearDown(self) -> None:
        self.release.set()
        self.manager.shutdown()
        self.temp.cleanup()

    def _authorization(self, receipt: str) -> dict[str, object]:
        self.authorization_calls += 1
        return {
            "source": "test",
            "receipt_hash72": receipt,
            "runtime_step": self.authorization_calls,
            "background_worker_grants_mutation_authority": False,
        }

    def test_submit_is_nonblocking_deduplicated_and_persists_summary(self) -> None:
        first = self.manager.submit(
            persist_vector=True,
            source="test",
            authorization_factory=lambda: self._authorization("a" * 72),
        )
        self.assertIn(first["state"], {"QUEUED", "RUNNING"})
        self.assertTrue(self.started.wait(timeout=2))
        self.assertEqual(self.authorization_calls, 1)

        duplicate = self.manager.submit(
            persist_vector=False,
            source="duplicate",
            authorization_factory=lambda: self._authorization("b" * 72),
        )
        self.assertEqual(duplicate["job_id"], first["job_id"])
        self.assertTrue(duplicate["deduplicated"])
        self.assertEqual(self.calls, 1)
        self.assertEqual(
            self.authorization_calls,
            1,
            "deduplicated submission created an orphan canonical tick",
        )
        self.assertEqual(
            duplicate["vm81_authorized_tick"]["receipt_hash72"],
            "a" * 72,
        )

        self.release.set()
        completed = self.manager.wait(first["job_id"], timeout_seconds=2)
        self.assertEqual(completed["state"], "SUCCEEDED")
        self.assertEqual(completed["result"]["file_count"], 4900)
        self.assertTrue(completed["result"]["gap_scope"]["current_frontier_closed"])
        self.assertNotIn("manifest", completed["result"])

        persisted = json.loads(
            self.state_root.joinpath("scan-jobs", f"{first['job_id']}.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(persisted["state"], "SUCCEEDED")
        self.assertEqual(
            persisted["vm81_authorized_tick"]["receipt_hash72"],
            "a" * 72,
        )
        self.assertTrue(
            persisted["result"]["gap_scope"]["current_frontier_closed"]
        )
        self.assertNotIn("manifest", persisted["result"])

    def test_unknown_job_fails_explicitly(self) -> None:
        with self.assertRaises(Pass196ScanJobError):
            self.manager.get("pass196-scan:missing")

    def test_restart_marks_active_job_interrupted(self) -> None:
        jobs = self.state_root / "scan-jobs"
        jobs.mkdir(parents=True)
        path = jobs / "pass196-scan-stale.json"
        path.write_text(
            json.dumps(
                {
                    "schema": "HHS_PASS_196_INTEGRATION_SCAN_JOB_V1",
                    "job_id": "pass196-scan-stale",
                    "state": "RUNNING",
                    "created_at_unix_ms": 1,
                    "started_at_unix_ms": 2,
                    "finished_at_unix_ms": None,
                    "result": None,
                    "error": None,
                }
            ),
            encoding="utf-8",
        )
        other = Pass196ScanJobManager(lambda **_: {}, state_root=self.state_root)
        try:
            recovered = other.get("pass196-scan-stale")
            self.assertEqual(recovered["state"], "INTERRUPTED")
            self.assertEqual(recovered["error"]["type"], "ProcessRestart")
        finally:
            other.shutdown()

    def test_restart_restores_latest_by_creation_order_not_uuid_filename(self) -> None:
        jobs = self.state_root / "scan-jobs"
        jobs.mkdir(parents=True, exist_ok=True)
        older = {
            "schema": "HHS_PASS_196_INTEGRATION_SCAN_JOB_V1",
            "job_id": "pass196-scan:zzzz",
            "state": "SUCCEEDED",
            "created_at_unix_ms": 10,
            "started_at_unix_ms": 11,
            "finished_at_unix_ms": 12,
            "result": {"manifest_hash72": "o" * 72},
            "error": None,
        }
        newer = {
            "schema": "HHS_PASS_196_INTEGRATION_SCAN_JOB_V1",
            "job_id": "pass196-scan:aaaa",
            "state": "SUCCEEDED",
            "created_at_unix_ms": 20,
            "started_at_unix_ms": 21,
            "finished_at_unix_ms": 22,
            "result": {"manifest_hash72": "n" * 72},
            "error": None,
        }
        for job in (older, newer):
            jobs.joinpath(f"{job['job_id']}.json").write_text(
                json.dumps(job),
                encoding="utf-8",
            )

        other = Pass196ScanJobManager(lambda **_: {}, state_root=self.state_root)
        try:
            latest = other.latest()
            self.assertIsNotNone(latest)
            self.assertEqual(latest["job_id"], newer["job_id"])
        finally:
            other.shutdown()


if __name__ == "__main__":
    unittest.main(verbosity=2)
