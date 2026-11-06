import unittest
from hhs_runtime.pass220.lane5_lean_equivalence_congruence_v1 import (
    THEOREMS, instantiate_equivalence, ExactRatEquivalenceError,
)
def p(n,d): return {"numerator":n,"denominator":d}
class TestLeanExactRatEquivalence(unittest.TestCase):
    def test_all_six(self):
        cases={
            "eqv_refl":[p(2,3)],
            "eqv_symm":[p(2,3),p(4,6)],
            "eqv_trans":[p(2,3),p(4,6),p(6,9)],
            "eqv_neg_congr":[p(2,3),p(4,6)],
            "eqv_add_congr":[p(2,3),p(4,6),p(-5,7),p(-10,14)],
            "eqv_mul_congr":[p(2,3),p(4,6),p(-5,7),p(-10,14)],
        }
        self.assertEqual(set(cases),set(THEOREMS))
        for name,inputs in cases.items():
            receipt=instantiate_equivalence(name,inputs)
            self.assertTrue(receipt["proof_premises_and_conclusion_exact"])
            self.assertEqual(receipt["original_operands"],inputs)
            self.assertFalse(receipt["canonical_representative_rewrite"])
            self.assertFalse(receipt["canonical_vm81_admission"])
    def test_mismatched_premise_rejected(self):
        with self.assertRaisesRegex(ExactRatEquivalenceError,"PREMISE_OR_CONCLUSION"):
            instantiate_equivalence("eqv_trans",[p(2,3),p(4,7),p(6,9)])
    def test_float_rejected(self):
        with self.assertRaisesRegex(ExactRatEquivalenceError,"POSITIVE_DENOMINATOR"):
            instantiate_equivalence("eqv_refl",[p(2.0,3)])
    def test_unknown_rejected(self):
        with self.assertRaisesRegex(ExactRatEquivalenceError,"UNREGISTERED"):
            instantiate_equivalence("eqv_hnan_comm",[p(2,3)])
if __name__=="__main__": unittest.main()
