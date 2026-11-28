"""Regression checks for arbitrary-length private SQL staging (no native admission)."""
import tempfile
import unittest
import io
import sqlite3
from unittest.mock import patch
from pathlib import Path
from hashlib import sha256

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging, StagingError


class TestStreamStaging(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = AdminStreamStaging(self.tmp.name)
        self.addCleanup(self.store.close)
        self.ident = self.store.create("root-admin", "arbitrary.unknown")["upload_id"]

    def test_arbitrary_binary_and_unknown_modality(self):
        data = bytes(range(256)) * 200
        self.store.append(self.ident, "root-admin", 0, data)
        result = self.store.finalize(self.ident, "root-admin", sha256(data).hexdigest())
        self.assertEqual(result["received_bytes"], len(data))
        self.assertFalse(result["canonical_hash216_admitted"])
        self.assertEqual(self.store.read_staged(self.ident, "root-admin").read_bytes(), data)

    def test_chunked_input_arbitrary_total_size(self):
        unit = b"z" * (1024 * 1024)
        for i in range(19):
            result = self.store.append(self.ident, "root-admin", i * len(unit), unit)
        self.assertEqual(result["received_bytes"], 19 * len(unit))
        self.assertEqual(self.store.finalize(self.ident, "root-admin")["state"], "STAGED")

    def test_resume_after_restart(self):
        self.store.append(self.ident, "root-admin", 0, b"abc")
        self.store.close()
        self.store = AdminStreamStaging(self.tmp.name)
        self.store.append(self.ident, "root-admin", 3, b"def")
        self.assertEqual(self.store.finalize(self.ident, "root-admin")["received_bytes"], 6)

    def test_uncommitted_spool_tail_discarded(self):
        self.store.append(self.ident, "root-admin", 0, b"abc")
        with (Path(self.tmp.name) / "spool" / self.ident).open("ab") as f:
            f.write(b"stale")
        self.store.append(self.ident, "root-admin", 3, b"def")
        self.store.finalize(self.ident, "root-admin")
        self.assertEqual(self.store.read_staged(self.ident, "root-admin").read_bytes(), b"abcdef")

    def test_idempotent_retry(self):
        self.store.append(self.ident, "root-admin", 0, b"abc")
        self.assertEqual(self.store.append(self.ident, "root-admin", 0, b"abc")["received_bytes"], 3)

    def test_replay_conflict(self):
        self.store.append(self.ident, "root-admin", 0, b"abc")
        with self.assertRaises(StagingError):
            self.store.append(self.ident, "root-admin", 0, b"xyz")

    def test_wrong_owner_denied(self):
        with self.assertRaises(StagingError):
            self.store.append(self.ident, "another", 0, b"x")
        with self.assertRaises(StagingError):
            self.store.status(self.ident, "another")

    def test_digest_mismatch_not_admitted(self):
        self.store.append(self.ident, "root-admin", 0, b"abc")
        with self.assertRaises(StagingError):
            self.store.finalize(self.ident, "root-admin", "0" * 64)
        self.assertEqual(self.store.status(self.ident, "root-admin")["state"], "UPLOADING")

    def test_no_append_after_staging(self):
        self.store.finalize(self.ident, "root-admin")
        with self.assertRaises(StagingError):
            self.store.append(self.ident, "root-admin", 0, b"new")

    def test_invalid_uuid(self):
        with self.assertRaises(StagingError):
            self.store.status("../../etc/passwd", "root-admin")

    def test_exact_writer_completes_repeated_partial_writes(self):
        class ShortWriter:
            def __init__(self):
                self.data = bytearray()
            def write(self, payload):
                n = min(len(payload), 2)
                self.data.extend(payload[:n])
                return n
        writer = ShortWriter()
        AdminStreamStaging._write_exact(writer, b"abcdefgh")
        self.assertEqual(bytes(writer.data), b"abcdefgh")

    def test_exact_writer_rejects_zero_progress(self):
        class Stalled:
            def write(self, payload):
                return 0
        with self.assertRaisesRegex(OSError, "STAGING_SHORT_WRITE"):
            AdminStreamStaging._write_exact(Stalled(), b"abc")

    def test_stale_upload_tmp_does_not_block_finalization_retry(self):
        data = b"recoverable source bytes"
        self.store.append(self.ident, "root-admin", 0, data)
        digest = sha256(data).hexdigest()
        directory = Path(self.tmp.name) / "source-sha256" / digest[:2]
        directory.mkdir(parents=True, exist_ok=True)
        stale = directory / (self.ident + ".tmp")
        stale.write_bytes(b"old incomplete output")
        status = self.store.finalize(self.ident, "root-admin", digest)
        self.assertEqual(status["state"], "STAGED")
        self.assertEqual(self.store.read_staged(self.ident, "root-admin").read_bytes(), data)

    def test_failed_create_commit_rolls_back_uncommitted_row(self):
        class FailOnce:
            def __init__(self, db):
                self.delegate = db
                self.fail = True
            def execute(self, *args):
                return self.delegate.execute(*args)
            def commit(self):
                if self.fail:
                    self.fail = False
                    raise sqlite3.OperationalError("injected failed commit")
                return self.delegate.commit()
            def rollback(self):
                return self.delegate.rollback()
        original = self.store.db
        proxy = FailOnce(original)
        self.store.db = proxy
        with self.assertRaises(sqlite3.OperationalError):
            self.store.create("root-admin", "failing.bin")
        self.store.create("root-admin", "valid.bin")
        rows = original.execute("SELECT source_name FROM intake").fetchall()
        self.assertNotIn("failing.bin", [row["source_name"] for row in rows])
        self.assertEqual(original.execute("SELECT count(*) FROM intake").fetchone()[0], 2)
        self.store.db = original

    def test_failed_append_commit_does_not_advance_acknowledged_offset(self):
        class FailOnce:
            def __init__(self, db):
                self.delegate = db
                self.fail = True
            def execute(self, *args):
                return self.delegate.execute(*args)
            def commit(self):
                if self.fail:
                    self.fail = False
                    raise sqlite3.OperationalError("injected failed commit")
                return self.delegate.commit()
            def rollback(self):
                return self.delegate.rollback()
        original = self.store.db
        self.store.db = FailOnce(original)
        with self.assertRaises(sqlite3.OperationalError):
            self.store.append(self.ident, "root-admin", 0, b"uncommitted")
        self.assertEqual(self.store.status(self.ident, "root-admin")["received_bytes"], 0)
        self.store.append(self.ident, "root-admin", 0, b"valid")
        self.store.finalize(self.ident, "root-admin")
        self.assertEqual(self.store.read_staged(self.ident, "root-admin").read_bytes(), b"valid")
        self.store.db = original

    def test_finalization_directory_synced_before_staged_sql_commit(self):
        data = b"durable bytes"
        self.store.append(self.ident, "root-admin", 0, data)
        digest = sha256(data).hexdigest()
        calls = []
        original_sync = AdminStreamStaging._fsync_directory
        def record(directory):
            calls.append(("fsync", Path(directory)))
            return original_sync(directory)
        with patch.object(AdminStreamStaging, "_fsync_directory", staticmethod(record)):
            self.store.finalize(self.ident, "root-admin", digest)
        target_dir = Path(self.tmp.name) / "source-sha256" / digest[:2]
        self.assertIn(("fsync", target_dir), calls)
        self.assertEqual(self.store.status(self.ident, "root-admin")["state"], "STAGED")

    def test_empty_source_allowed(self):
        result = self.store.finalize(self.ident, "root-admin")
        self.assertEqual(result["received_bytes"], 0)
        self.assertEqual(result["source_sha256"], sha256(b"").hexdigest())


def load_tests(loader, tests, pattern):
    """Retain staging coverage and run PR914 gates in the authorized PR workflow."""
    from test_hhs_pr914_all_open_branch_integration_gate_v1 import (
        TestAllOpenBranchReconciliationGate,
    )
    from test_hhs_pr914_git_reconciliation_evidence_v1 import GitReconciliationTests
    from test_hhs_pr914_open_branch_census_v1 import CensusTests

    tests.addTests(loader.loadTestsFromTestCase(TestAllOpenBranchReconciliationGate))
    tests.addTests(loader.loadTestsFromTestCase(CensusTests))
    tests.addTests(loader.loadTestsFromTestCase(GitReconciliationTests))
    return tests


if __name__ == "__main__":
    unittest.main()
