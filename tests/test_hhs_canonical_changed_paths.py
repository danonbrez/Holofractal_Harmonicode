"""Regression coverage for the canonical frozen-layer path evidence constructor."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from hhs_canonical_changed_paths import ChangedPathEvidenceError, decode_nul_paths, changed_paths


class CanonicalPathEvidenceTests(unittest.TestCase):
    def test_byte_delimiter_not_literal_backslash_zero(self):
        self.assertEqual(decode_nul_paths(b"policy\\0name\0other\0"),
                         frozenset({"policy\\0name", "other"}))

    def test_invalid_records_fail_closed(self):
        for data in (b"bad", b"bad\\0", b"one\0\0", b""):
            with self.subTest(data=data):
                with self.assertRaises(ChangedPathEvidenceError):
                    decode_nul_paths(data)

    def test_non_utf8_path_roundtrips(self):
        raw = b"policy-\xff\0"
        item = next(iter(decode_nul_paths(raw)))
        self.assertEqual(item.encode("utf-8", "surrogateescape") + b"\0", raw)

    def test_real_git_rename_exposes_both_endpoints(self):
        with tempfile.TemporaryDirectory() as temp:
            def git(*args):
                return subprocess.check_output(["git", "-C", temp, *args]).decode().strip()
            git("init", "-q")
            git("config", "user.email", "test@example.invalid")
            git("config", "user.name", "Test")
            original = pathlib.Path(temp) / "policy"
            original.write_text("same")
            git("add", ".")
            git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD")
            original.rename(pathlib.Path(temp) / "renamed")
            git("add", "-A")
            git("commit", "-qm", "rename")
            head = git("rev-parse", "HEAD")
            cwd = pathlib.Path.cwd()
            import os
            try:
                os.chdir(temp)
                self.assertEqual(changed_paths(base, head), frozenset({"policy", "renamed"}))
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
