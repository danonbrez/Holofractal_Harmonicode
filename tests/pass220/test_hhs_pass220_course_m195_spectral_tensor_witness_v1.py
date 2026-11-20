"""Regression checks for Module 195 exact spectral witness and non-admission."""
import unittest
from hhs_runtime.hhs_pass220_course_m195_spectral_tensor_witness_v1 import (
    D, I, M, ZERO, EXPECTED_K, SOURCE, add, evaluate, mm, pmat_mul, scale,
)


class TestM195(unittest.TestCase):
    def test_exact_spectral_closure(self):
        r = evaluate()
        self.assertEqual(r["module"], 195)
        self.assertEqual(r["ordered_operator_K"], [list(row) for row in EXPECTED_K])
        self.assertEqual(r["denominator_coefficients_ascending"], [0,25,6,1])
        self.assertEqual(r["cayley_hamilton_residual"], [list(row) for row in ZERO])
        self.assertEqual(r["adjugate_residual_coefficients"],
                         [[list(row) for row in ZERO] for _ in range(4)])
        self.assertEqual(r["nonzero_spectral_magnitudes"], [5,5])
        self.assertEqual(tuple(sum(row[j] * v for j,v in enumerate((1,2,1)))
                               for row in EXPECTED_K), (0,0,0))

    def test_order_and_source_retained(self):
        self.assertEqual(mm(M, scale(M,-1)), EXPECTED_K)
        self.assertEqual(mm(scale(M,-1), M), EXPECTED_K)  # observed only for this M
        self.assertIn("MatrixTimes(MatrixTimes(", SOURCE)
        self.assertIn("==1/m", SOURCE)
        self.assertNotEqual(EXPECTED_K, I)

    def test_guarded_native_boundaries_fail_closed(self):
        r=evaluate()
        for key in ("canonical_vm81_admission","hash72_minted",
                    "hash216_minted","native_hnan_executed",
                    "lane5_producer_provenance_verified",
                    "scalar_coercion_refutes_native_gate"):
            self.assertIs(r[key], False)
        self.assertEqual(r["ordered_typed_equality"],
                         "OUTSTANDING_NATIVE_PROOF_OBLIGATION")
        self.assertEqual(r["module194_v160_source_address_contract"],
                         "DISTINCT_UNCHANGED")
        self.assertEqual(r["denominator_zero_guard"],
                         "HNAN_NATIVE_RUNTIME_GATE_REQUIRED")

    def test_deterministic_candidate(self):
        self.assertEqual(evaluate(),evaluate())
        self.assertEqual(len(evaluate()["candidate_sha256"]),64)


if __name__=="__main__":
    unittest.main()
