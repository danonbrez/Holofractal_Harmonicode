import unittest
from hhs_runtime.pass220.lane5_lean_normalization_instance_v1 import (
    instantiate_existing_normalization, NormalizationInstantiationError,
)
from hhs_runtime.pass220.lane5_lean_normalization_lookup_v1 import NORMALIZATION_DECLARATIONS

def q(n,d=1):
    return {"numerator":n,"denominator":d}

class TestExactLeanInstantiation(unittest.TestCase):
    def test_all_registered_declarations(self):
        for name in NORMALIZATION_DECLARATIONS:
            receipt=instantiate_existing_normalization(name,[q(17,19),q(-3,7),q(11,13)])
            self.assertEqual(receipt["lhs_exact"],receipt["rhs_exact"])
            self.assertEqual(receipt["theorem"]["declaration"],name)
            self.assertFalse(receipt["canonical_vm81_admission"])
            self.assertFalse(receipt["runtime_lean_kernel_invoked"])

    def test_canonical_rational_results_and_source_operands(self):
        operands=[q(-7,11),q(5,13),q(3,17)]
        receipt=instantiate_existing_normalization("value_left_distrib",operands)
        self.assertEqual(receipt["operands"],operands)
        self.assertEqual(receipt["lhs_exact"],receipt["rhs_exact"])
        self.assertEqual(receipt["theorem"]["application_declaration"],"value_left_distrib_application")

    def test_denominator_zero_rejected(self):
        with self.assertRaisesRegex(NormalizationInstantiationError,"COMPONENT_REJECTED"):
            instantiate_existing_normalization("value_mul_assoc",[q(1,0),q(2),q(3)])

    def test_ieee_float_rejected(self):
        with self.assertRaisesRegex(NormalizationInstantiationError,"COMPONENT_REJECTED"):
            instantiate_existing_normalization("value_mul_assoc",[q(1.0),q(2),q(3)])

    def test_missing_theorem_rejected(self):
        with self.assertRaisesRegex(NormalizationInstantiationError,"UNKNOWN_THEOREM"):
            instantiate_existing_normalization("AB_equals_BA",[q(1),q(2),q(3)])

if __name__=="__main__":
    unittest.main()
