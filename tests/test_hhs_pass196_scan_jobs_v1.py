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

    def test_submit_is_nonblocking_deduplicated_and_persists_summary(self) -> None:
        first = self.manager.submit(
            persist_vector=True,
            vm81_receipt_hash72="a" * 72,
            source="test",
        )
        self.assertIn(first["state"], {"QUEUED", "RUNNING"})
        self.assertTrue(self.started.wait(timeout=2))

        duplicate = self.manager.submit(
            persist_vector=False,
            vm81_receipt_hash72="b" * 72,
            source="duplicate",
        )
        self.assertEqual(duplicate["job_id"], first["job_id"])
        self.assertTrue(duplicate["deduplicated"])
        self.assertEqual(self.calls, 1)

        self.release.set()
        completed = self.manager.wait(first["job_id"], timeout_seconds=2)
        self.assertEqual(completed["state"], "SUCCEEDED")
        self.assertEqual(completed["result"]["file_count"], 4900)
        self.assertNotIn("manifest", completed["result"])

        persisted = json.loads(
            self.state_root.joinpath("scan-jobs", f"{first['job_id']}.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(persisted["state"], "SUCCEEDED")
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
