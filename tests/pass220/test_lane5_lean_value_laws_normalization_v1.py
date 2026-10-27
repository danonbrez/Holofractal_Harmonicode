import unittest
from hhs_runtime.pass220.lane5_lean_value_laws_normalization_v1 import (
    DECLARATIONS, instantiate_existing_value_law, ValueLawNormalizationError,
)

class TestI056ValueLaws(unittest.TestCase):
    def test_all_twelve(self):
        for theorem in DECLARATIONS:
            record = instantiate_existing_value_law(theorem, {"numerator": -17, "denominator": 19})
            self.assertEqual(record["lhs_exact"],record["rhs_exact"])
            self.assertEqual(record["application_declaration"], theorem + "_application")
            self.assertFalse(record["ordered_hnan_rewrite_authorized"])
            self.assertFalse(record["canonical_vm81_admission"])
    def test_zero_denominator_rejected(self):
        with self.assertRaisesRegex(ValueLawNormalizationError,"POSITIVE_DENOMINATOR"):
            instantiate_existing_value_law("value_add_zero",{"numerator":1,"denominator":0})
    def test_float_rejected(self):
        with self.assertRaisesRegex(ValueLawNormalizationError,"POSITIVE_DENOMINATOR"):
            instantiate_existing_value_law("value_add_zero",{"numerator":1.0,"denominator":2})
    def test_unknown_rejected(self):
        with self.assertRaisesRegex(ValueLawNormalizationError,"UNKNOWN_DECLARATION"):
            instantiate_existing_value_law("AB_BA_commute",{"numerator":1,"denominator":2})

if __name__=="__main__":
    unittest.main()
