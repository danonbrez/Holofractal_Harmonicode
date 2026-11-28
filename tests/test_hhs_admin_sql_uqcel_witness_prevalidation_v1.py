"""Exact UQCEL mathematical validation at the read-only staged source boundary."""
from hashlib import sha256
import tempfile
import unittest

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_backend.runtime.hhs_admin_sql_uqcel_witness_prevalidation_v1 import (
    UQCELWitnessPrevalidationError,
    prevalidate_staged_uqcel_witness,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import build_execution_cases


VALID = {
    "P": 4, "p": 3, "q": 5, "delta": 1, "A": 16, "B": 16,
    "cell81": 41, "left_basis8": 0, "right_basis8": 1,
    "previous_hash72": "0" * 72,
}


class TestUQCELWitnessPrevalidation(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.stage = AdminStreamStaging(temp.name)
        self.addCleanup(self.stage.close)
        source = build_execution_cases()[0]["raw_bytes"]
        self.upload = self.stage.create("owner", "typed-vm81")["upload_id"]
        self.stage.append(self.upload, "owner", 0, source)
        self.stage.finalize(self.upload, "owner", sha256(source).hexdigest())

    def test_real_native_uqcel_validation_no_source_promotion(self):
        receipt = prevalidate_staged_uqcel_witness(
            self.stage, self.upload, "owner", witness=VALID
        )
        self.assertTrue(receipt["typed_frame_recognized"])
        self.assertIsInstance(receipt["uqcel_native_status"], int)
        self.assertIsInstance(receipt["uqcel_native_decision"], int)
        self.assertIsInstance(receipt["uqcel_native_validation_succeeded"], bool)
        self.assertFalse(receipt["source_to_witness_provenance_bound"])
        self.assertFalse(receipt["authorized_parent_hash216_bound"])
        self.assertFalse(receipt["signed_vm81_admission_performed"])
        self.assertFalse(receipt["canonical_hash216_admitted"])
        self.assertFalse(self.stage.status(self.upload, "owner")["canonical_hash216_admitted"])

    def test_invalid_witness_denied_before_native(self):
        calls = []
        def validator(**kwargs):
            calls.append(kwargs)
            return {"status": 0, "admission": {"decision": 1, "source_hash_match": True}}
        for invalid in (
            dict(VALID, P=4.0),
            dict(VALID, p=-1),
            dict(VALID, cell81=81),
            dict(VALID, left_basis8=8),
            dict(VALID, previous_hash72="not-a-hash"),
            {k:v for k,v in VALID.items() if k != "P"},
        ):
            with self.assertRaises(UQCELWitnessPrevalidationError):
                prevalidate_staged_uqcel_witness(
                    self.stage, self.upload, "owner", witness=invalid, native_validator=validator
                )
        self.assertEqual(calls, [])

    def test_native_failure_does_not_count_as_validation(self):
        def reject(**kwargs):
            return {"status": 7, "admission": {"decision": 2, "source_hash_match": False}}
        receipt = prevalidate_staged_uqcel_witness(
            self.stage, self.upload, "owner", witness=VALID, native_validator=reject
        )
        self.assertFalse(receipt["uqcel_native_validation_succeeded"])
        self.assertFalse(receipt["canonical_hash216_admitted"])

    def test_owner_guard_and_nonframe(self):
        with self.assertRaises(Exception):
            prevalidate_staged_uqcel_witness(
                self.stage, self.upload, "foreign", witness=VALID,
            )
        other = self.stage.create("owner", "opaque")["upload_id"]
        self.stage.append(other, "owner", 0, b"arbitrary original data")
        self.stage.finalize(other, "owner")
        with self.assertRaisesRegex(UQCELWitnessPrevalidationError, "EXISTING_TYPED_VM81"):
            prevalidate_staged_uqcel_witness(
                self.stage, other, "owner", witness=VALID,
            )


if __name__ == "__main__":
    unittest.main()
