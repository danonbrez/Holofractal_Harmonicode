"""Test-only exact SQL-staged VM81 -> inherited signed environment verification.

The native probe owns a deterministic TEST ROOT and genesis parent; this
cannot be invoked as a production API or claim live parent Hash216 lineage.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import os
import tempfile
import unittest

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_backend.runtime.hhs_admin_sql_typed_vm81_source_v1 import inspect_exact_typed_vm81_source
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    build_execution_cases, raw_le_to_words, unpack_vm81_binding_words,
)
from hhs_runtime.pass219.vm81_rna_bigint_environment_admission_probe import (
    NEGATIVE_MODES, run_native_admission,
)


class TestSQLStagedSignedFixture(unittest.TestCase):
    def test_existing_native_signed_fixture_with_exact_staged_frames(self):
        native_probe = os.environ.get("HHS_PASS219_BIGINT_ENVIRONMENT_NATIVE_PROBE")
        if not native_probe:
            self.skipTest("OpenSSL3.5 ML-DSA provider / native signed fixture unavailable")
        self.assertTrue(Path(native_probe).is_file())
        with tempfile.TemporaryDirectory() as root:
            stage = AdminStreamStaging(root)
            try:
                cases = build_execution_cases()
                self.assertEqual(len(cases), 12)
                for case in cases:
                    source = case["raw_bytes"]
                    upload_id = stage.create("fixture-owner", "typed-vm81.bin")["upload_id"]
                    for offset in range(0, len(source), 127):
                        stage.append(upload_id, "fixture-owner", offset, source[offset:offset + 127])
                    staged = stage.finalize(upload_id, "fixture-owner", sha256(source).hexdigest())
                    decoded = inspect_exact_typed_vm81_source(stage, upload_id, "fixture-owner")
                    self.assertTrue(decoded["typed_frame_recognized"])
                    self.assertEqual(decoded["metadata"]["opcode"], case["opcode"])
                    self.assertFalse(decoded["authorized_parent_hash216_bound"])
                    self.assertFalse(decoded["signed_vm81_admission_performed"])
                    self.assertFalse(staged["canonical_hash216_admitted"])
                    from_sql = stage.read_staged(upload_id, "fixture-owner").read_bytes()
                    self.assertEqual(from_sql, source)
                    result = run_native_admission(from_sql, native_probe, "commit")
                    native = result["native"]
                    self.assertEqual(native["status"], 0)
                    self.assertEqual(native["provider_available"], 1)
                    self.assertEqual(native["parent_hash216_verified"], 1)
                    self.assertEqual(native["child_hash216_verified"], 1)
                    self.assertEqual(native["canonical_receipt_minted"], 1)
                    self.assertEqual(native["signature_verified"], 1)
                    self.assertEqual(native["environment_verified"], 1)
                    self.assertEqual(native["authority_handoff_exact"], 1)
                    self.assertEqual(result["committed_raw"], from_sql)
                    restored = unpack_vm81_binding_words(raw_le_to_words(result["committed_raw"]))
                    self.assertEqual(restored["bigint"], case["bigint"])
                    self.assertEqual(restored["metadata"]["opcode"], case["opcode"])
                    # The external test process owns fixture key+genesis ancestry.
                    # No canonical knowledge authority is passed back to SQL.
                    self.assertFalse(stage.status(upload_id, "fixture-owner")["canonical_hash216_admitted"])

                reference = cases[0]["raw_bytes"]
                for mode in NEGATIVE_MODES:
                    negative = run_native_admission(reference, native_probe, mode)
                    self.assertNotEqual(negative["native"]["status"], 0)
                    self.assertEqual(negative["committed_raw"], bytes(648))
                    self.assertEqual(negative["native"]["canonical_receipt_minted"], 0)
            finally:
                stage.close()


if __name__ == "__main__":
    unittest.main()
