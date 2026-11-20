"""Regression checks for arbitrary-length private SQL staging (no native admission)."""
import tempfile
import unittest
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

    def test_empty_source_allowed(self):
        result = self.store.finalize(self.ident, "root-admin")
        self.assertEqual(result["received_bytes"], 0)
        self.assertEqual(result["source_sha256"], sha256(b"").hexdigest())


if __name__ == "__main__":
    unittest.main()
