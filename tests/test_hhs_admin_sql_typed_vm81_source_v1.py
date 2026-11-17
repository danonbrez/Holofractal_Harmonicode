"""Read-only inherited typed VM81 staged-source recognition tests."""
from hashlib import sha256
import tempfile
import unittest

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_backend.runtime.hhs_admin_sql_typed_vm81_source_v1 import inspect_exact_typed_vm81_source
from hhs_backend.runtime.hhs_admin_sql_signed_environment_fixture_handoff_v1 import verify_staged_signed_fixture, StagedSignedFixtureError
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import build_execution_cases


class TestStagedTypedVM81Recognition(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.stage = AdminStreamStaging(self.temp.name)
        self.addCleanup(self.stage.close)

    def staged(self, source):
        upload_id = self.stage.create("owner", "candidate")["upload_id"]
        for offset in range(0, len(source), 503):
            self.stage.append(upload_id, "owner", offset, source[offset:offset+503])
        self.stage.finalize(upload_id, "owner", sha256(source).hexdigest())
        return upload_id

    def test_existing_typed_frame_roundtrip_and_phase_metadata(self):
        for case in build_execution_cases():
            upload_id = self.staged(case["raw_bytes"])
            record = inspect_exact_typed_vm81_source(self.stage, upload_id, "owner")
            self.assertTrue(record["typed_frame_recognized"])
            self.assertTrue(record["frame_reencoded_exact"])
            self.assertEqual(record["source_sha256"], case["raw_sha256"])
            self.assertEqual(record["vm81_frame_bytes"], 648)
            self.assertEqual(record["glyph_count"], 72)
            self.assertEqual(record["metadata"]["opcode"], case["opcode"])
            self.assertEqual(record["metadata"]["direction"], case["direction"])
            self.assertEqual(record["bigint"], str(case["bigint"]))
            self.assertFalse(record["authorized_parent_hash216_bound"])
            self.assertFalse(record["uqcel_math_witness_bound"])
            self.assertFalse(record["signed_vm81_admission_performed"])
            self.assertFalse(record["canonical_hash216_admitted"])

    def test_opaque_and_malformed_sources_remain_staged_not_admitted(self):
        for payload in (b"arbitrary file", b"\0" * 648, bytes(range(256)) * 3):
            upload_id = self.staged(payload)
            result = inspect_exact_typed_vm81_source(self.stage, upload_id, "owner")
            self.assertFalse(result["typed_frame_recognized"])
            self.assertFalse(result["canonical_hash216_admitted"])
            self.assertEqual(self.stage.read_staged(upload_id, "owner").read_bytes(), payload)

    def test_fixture_handoff_rejects_opaque_and_wrong_owner_without_native_execution(self):
        opaque_id = self.staged(b"unrecognized native format")
        with self.assertRaisesRegex(StagedSignedFixtureError, "TYPED_VM81_SOURCE_REQUIRED"):
            verify_staged_signed_fixture(
                self.stage, opaque_id, "owner", native_probe=__file__,
            )
        exact = self.staged(build_execution_cases()[0]["raw_bytes"])
        with self.assertRaises(Exception):
            verify_staged_signed_fixture(
                self.stage, exact, "other", native_probe=__file__,
            )
        with self.assertRaisesRegex(StagedSignedFixtureError, "FIXTURE_POSITIVE_MODE_ONLY"):
            verify_staged_signed_fixture(
                self.stage, exact, "owner", native_probe=__file__, mode="bad-parent",
            )

    def test_identity_and_state_guards(self):
        upload_id = self.stage.create("owner", "incomplete")["upload_id"]
        with self.assertRaisesRegex(ValueError, "NOT_STAGED"):
            inspect_exact_typed_vm81_source(self.stage, upload_id, "owner")
        completed = self.staged(build_execution_cases()[0]["raw_bytes"])
        with self.assertRaises(Exception):
            inspect_exact_typed_vm81_source(self.stage, completed, "different-owner")
        source = self.stage.read_staged(completed, "owner")
        source.chmod(0o600)
        try:
            source.write_bytes(b"Z" * 648)
            with self.assertRaisesRegex(ValueError, "SOURCE_DRIFT"):
                inspect_exact_typed_vm81_source(self.stage, completed, "owner")
        finally:
            source.chmod(0o400)


if __name__ == "__main__":
    unittest.main()
