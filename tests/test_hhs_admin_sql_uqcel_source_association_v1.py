"""Untrusted, replayable UQCEL/source association; no new admission authority."""
from hashlib import sha256
import tempfile
import unittest

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_backend.runtime.hhs_admin_sql_uqcel_source_association_v1 import (
    UQCELSourceAssociationError,
    build_candidate_source_witness_association,
    replay_candidate_source_witness_association,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import build_execution_cases

WITNESS = {
    "P": 4, "p": 3, "q": 5, "delta": 1, "A": 16, "B": 16,
    "cell81": 41, "left_basis8": 0, "right_basis8": 1,
    "previous_hash72": "0" * 72,
}


class TestSourceWitnessAssociation(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.stage = AdminStreamStaging(temp.name)
        self.addCleanup(self.stage.close)
        raw = build_execution_cases()[0]["raw_bytes"]
        self.upload_id = self.stage.create("owner", "exact-vm81")["upload_id"]
        self.stage.append(self.upload_id, "owner", 0, raw)
        self.stage.finalize(self.upload_id, "owner", sha256(raw).hexdigest())

    def test_native_association_build_and_replay(self):
        record = build_candidate_source_witness_association(
            self.stage, self.upload_id, "owner", witness=WITNESS,
        )
        self.assertEqual(record["source_bytes"], 648)
        self.assertTrue(record["native_uqcel_validated"])
        self.assertTrue(record["source_to_witness_candidate_association"])
        self.assertFalse(record["source_to_witness_authorized_provenance"])
        self.assertFalse(record["authorized_parent_hash216_bound"])
        self.assertFalse(record["signed_vm81_admission_performed"])
        self.assertFalse(record["canonical_hash216_admitted"])
        replay = replay_candidate_source_witness_association(self.stage, "owner", record)
        self.assertTrue(replay["exact_source_witness_association_replayed"])
        self.assertTrue(replay["native_uqcel_revalidated"])
        self.assertFalse(replay["canonical_hash216_admitted"])

    def test_tampered_witness_or_metadata_rejected(self):
        record = build_candidate_source_witness_association(
            self.stage, self.upload_id, "owner", witness=WITNESS,
        )
        edits = [
            dict(record, candidate_association_sha256="0" * 64),
            dict(record, source_sha256="0" * 64),
            dict(record, canonical_hash216_admitted=True),
            dict(record, source_to_witness_authorized_provenance=True),
            dict(record, authorized_parent_hash216_bound=True),
            dict(record, unexpected=True),
            dict(record, witness=dict(WITNESS, q=6)),
        ]
        for tampered in edits:
            with self.subTest(tampered=tampered):
                with self.assertRaises((UQCELSourceAssociationError, ValueError)):
                    replay_candidate_source_witness_association(
                        self.stage, "owner", tampered,
                    )
        with self.assertRaises(Exception):
            replay_candidate_source_witness_association(self.stage, "foreign", record)

    def test_source_tamper_and_native_reject(self):
        record = build_candidate_source_witness_association(
            self.stage, self.upload_id, "owner", witness=WITNESS,
        )
        path = self.stage.read_staged(self.upload_id, "owner")
        path.chmod(0o600)
        try:
            path.write_bytes(b"Z" * 648)
            with self.assertRaises(ValueError):
                replay_candidate_source_witness_association(self.stage, "owner", record)
        finally:
            # Restore the exact staged bytes so the next negative case reaches
            # the *native validator* rather than repeating source drift.
            from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import build_execution_cases
            path.write_bytes(build_execution_cases()[0]["raw_bytes"])
            path.chmod(0o400)

        def failed_native(**kwargs):
            return {"status": 7, "admission": {"decision": 2, "source_hash_match": False}}
        with self.assertRaisesRegex(UQCELSourceAssociationError, "MATHEMATICAL_VALIDATION_REQUIRED"):
            build_candidate_source_witness_association(
                self.stage, self.upload_id, "owner", witness=WITNESS,
                native_validator=failed_native,
            )

    def test_arbitrary_data_remains_regular_staging(self):
        other = self.stage.create("owner", "arbitrary.source")["upload_id"]
        self.stage.append(other, "owner", 0, b"opaque\0native\nsource")
        self.stage.finalize(other, "owner")
        with self.assertRaises(ValueError):
            build_candidate_source_witness_association(
                self.stage, other, "owner", witness=WITNESS,
            )
        self.assertEqual(self.stage.read_staged(other, "owner").read_bytes(), b"opaque\0native\nsource")


if __name__ == "__main__":
    unittest.main()
