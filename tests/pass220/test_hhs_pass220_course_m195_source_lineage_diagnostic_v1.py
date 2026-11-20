"""Regression: preserve historical frozen course and identify changed source."""
import unittest
from pathlib import Path
from hhs_runtime.hhs_pass220_course_m195_source_lineage_diagnostic_v1 import (
    diagnose_course_lineage, SOURCE_PATH,
)


class TestM195SourceLineage(unittest.TestCase):
    def test_immutable_freeze_and_current_are_distinct(self):
        receipt = diagnose_course_lineage()
        self.assertEqual(receipt["module"], 195)
        self.assertEqual(receipt["source_path"], SOURCE_PATH)
        self.assertEqual(
            receipt["historical_blob_sha"],
            "2744e9ecf1f260ff9a5a02870320698ee2d7dcaf"
        )
        self.assertEqual(
            receipt["working_blob_sha"],
            "968735b21bb0fda42f9c944ae6987099e624e7a7"
        )
        self.assertTrue(receipt["legacy_source_still_recoverable"])
        self.assertFalse(receipt["blob_identity_matches"])
        self.assertEqual(receipt["source_graph_status"], "SOURCE_BLOB_CHANGED")
        self.assertEqual(
            receipt["resolution"], "AUTHORITATIVE_SOURCE_RECONCILIATION_REQUIRED"
        )
        self.assertFalse(receipt["source_graph_binding_eligible"])
        self.assertFalse(receipt["freeze_repin_performed"])
        self.assertFalse(receipt["course_contents_mutated"])
        self.assertFalse(receipt["native_proof_admitted"])
        self.assertFalse(receipt["canonical_vm81_admission"])
        self.assertFalse(receipt["hash72_minted"])
        self.assertFalse(receipt["hash216_minted"])
        self.assertGreater(
            receipt["working_byte_count"], receipt["historical_byte_count"]
        )

    def test_deterministic_read_only_lineage(self):
        first = diagnose_course_lineage()
        second = diagnose_course_lineage()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
