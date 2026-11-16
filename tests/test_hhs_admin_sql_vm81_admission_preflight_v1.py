"""Read-only signed VM81 environmental preflight with actual native library."""
from hashlib import sha256
import tempfile
import unittest

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_backend.runtime.hhs_admin_sql_vm81_admission_preflight_v1 import (
    inspect_staged_admission_prerequisites,
)

class TestSignedAdmissionPreflight(unittest.TestCase):
    def test_real_native_read_only_availability(self):
        with tempfile.TemporaryDirectory() as root:
            stage = AdminStreamStaging(root)
            try:
                payload = bytes(range(256)) * 9 + b"\0"
                id_ = stage.create("admin", "opaque.unknown")["upload_id"]
                stage.append(id_, "admin", 0, payload)
                stage.finalize(id_, "admin", sha256(payload).hexdigest())
                report = inspect_staged_admission_prerequisites(stage, id_, "admin")
                self.assertEqual(report["source_sha256"], sha256(payload).hexdigest())
                self.assertEqual(report["received_bytes"], len(payload))
                self.assertGreater(report["environment_native_version"], 0)
                self.assertTrue(report["signed_environmental_entrypoint_exported"])
                self.assertIsInstance(report["ml_dsa_65_provider_available"], bool)
                self.assertIsInstance(report["slh_dsa_sha2_192s_provider_available"], bool)
                self.assertFalse(report["typed_source_constructor_bound"])
                self.assertFalse(report["authorized_parent_hash216_bound"])
                self.assertFalse(report["signed_vm81_admission_performed"])
                self.assertFalse(report["canonical_hash216_admitted"])
                with self.assertRaises(Exception):
                    inspect_staged_admission_prerequisites(stage, id_, "other")
            finally:
                stage.close()

    def test_unfinalized_source_denied(self):
        with tempfile.TemporaryDirectory() as root:
            stage = AdminStreamStaging(root)
            try:
                id_ = stage.create("admin", "unfinished")["upload_id"]
                with self.assertRaisesRegex(ValueError, "REQUIRES_STAGED_SOURCE"):
                    inspect_staged_admission_prerequisites(stage, id_, "admin")
            finally:
                stage.close()

    def test_unavailable_symbol_fails_closed(self):
        class IncompleteNative:
            pass
        with tempfile.TemporaryDirectory() as root:
            stage = AdminStreamStaging(root)
            try:
                id_ = stage.create("admin", "short")["upload_id"]
                stage.append(id_, "admin", 0, b"data")
                stage.finalize(id_, "admin")
                with self.assertRaisesRegex(RuntimeError, "SYMBOL_SET_INCOMPLETE"):
                    inspect_staged_admission_prerequisites(stage, id_, "admin", loader=IncompleteNative)
            finally:
                stage.close()
