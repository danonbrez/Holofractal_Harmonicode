"""Exercise actual compiled Pass219 Lane5 shared library, not a bridge stub.

The native result is a candidate only; no signed VM81 admission or Hash216
persistence may be claimed from this test.
"""
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_backend.runtime.hhs_admin_sql_lane5_continuation_v1 import continue_staged_to_lane5
from hhs_python.runtime.hhs_pass219_lane5_unbounded_workload_scaling_bridge import (
    Pass219Lane5UnboundedWorkloadBridge,
)

class TestNativeAdminStagedSource(unittest.TestCase):
    def test_real_native_bridge_exact_binary_candidate(self):
        with tempfile.TemporaryDirectory() as root:
            staging = AdminStreamStaging(root)
            try:
                source = bytes(range(256)) * 17 + b"\0unknown-binary-source\xff"
                upload_id = staging.create("verified-admin", "source.unknown-format")["upload_id"]
                for offset in range(0, len(source), 503):
                    staging.append(upload_id, "verified-admin", offset, source[offset:offset + 503])
                staged = staging.finalize(upload_id, "verified-admin", sha256(source).hexdigest())
                self.assertEqual(staged["received_bytes"], len(source))

                native = Pass219Lane5UnboundedWorkloadBridge()
                result = continue_staged_to_lane5(staging, upload_id, "verified-admin", bridge_factory=lambda: native)
                receipt = result["native_candidate_receipt"]
                self.assertEqual(result["source_sha256"], sha256(source).hexdigest())
                self.assertEqual(receipt["workload_byte_count"], len(source))
                self.assertEqual(receipt["workload_sha256"], staged["source_sha256"])
                self.assertGreaterEqual(receipt["admitted_candidates"], 1)
                self.assertTrue(receipt["candidate_only"])
                self.assertFalse(receipt["canonical_vm81_mutation_authority"])
                self.assertFalse(receipt["canonical_hash216_authority"])
                self.assertTrue(receipt["requires_signed_environmental_vm81_admission"])
                self.assertFalse(result["canonical_hash216_admitted"])
                self.assertTrue(result["signed_vm81_admission_required"])
                self.assertEqual(staging.read_staged(upload_id, "verified-admin").read_bytes(), source)
            finally:
                staging.close()

if __name__ == "__main__":
    unittest.main()
