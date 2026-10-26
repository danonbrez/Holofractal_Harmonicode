import unittest
from hhs_runtime.pass220.lane5_lean_normalization_lookup_v1 import (
    lookup_existing_normalization, LeanNormalizationLookupError,
    NORMALIZATION_DECLARATIONS,
)

class TestLane5ExistingLeanNormalization(unittest.TestCase):
    def test_all_eight_theorem_signatures(self):
        for name, (carrier, relation, operator) in NORMALIZATION_DECLARATIONS.items():
            item = lookup_existing_normalization(name, carrier=carrier,
                                                   relation=relation, operator=operator)
            self.assertEqual(item["application_declaration"], name + "_application")
            self.assertEqual(item["application_module"], "HHS.Pass220.Lane5NormalizationApplications")
            self.assertTrue(item["theorem_identity_hash72"])
            self.assertTrue(item["dependency_identity_hash72"])
            self.assertFalse(item["ordered_hnan_rewrite_authorized"])
            self.assertFalse(item["canonical_vm81_admission"])
            self.assertTrue(item["candidate_only"])

    def test_reject_hnan_type_substitution(self):
        with self.assertRaisesRegex(LeanNormalizationLookupError, "TYPE_MISMATCH"):
            lookup_existing_normalization("value_mul_assoc", carrier="HNAN",
                                           relation="Eq", operator="AB")

    def test_reject_missing_declaration(self):
        with self.assertRaisesRegex(LeanNormalizationLookupError, "NOT_REGISTERED"):
            lookup_existing_normalization("AB_equals_BA", carrier="ExactRatValue",
                                           relation="Eq", operator="ExactRatValue.mul")

if __name__ == "__main__":
    unittest.main()
