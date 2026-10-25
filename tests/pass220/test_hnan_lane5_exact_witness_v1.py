"""Dependency-scoped regression for the read-only HNAN Lane 5 witness."""
import unittest
from hhs_runtime.pass220.hnan_lane5_exact_witness_v1 import (
    HNANExactWitnessError, EXPECTED_PI_B, OFFSETS,
    pi_b_from_phase_matrix, verify_matrix_factorization,
    verify_gradient_offsets, reciprocal_hash72,
    serialization_address, verify_read_only_candidate,
)

class TestHNANLane5ExactWitness(unittest.TestCase):
    def test_formal_matrix_coefficients(self):
        self.assertEqual(pi_b_from_phase_matrix(), EXPECTED_PI_B)
        self.assertTrue(verify_matrix_factorization())

    def test_matrix_negative(self):
        mutated = tuple(tuple(dict(entry) for entry in row) for row in EXPECTED_PI_B)
        changed = [list(row) for row in mutated]
        changed[0][0][9] += 1
        with self.assertRaisesRegex(HNANExactWitnessError, "FACTORIZATION_DRIFT"):
            verify_matrix_factorization(expected=tuple(tuple(row) for row in changed))

    def test_gradient_offset_constant_and_mutation(self):
        self.assertTrue(verify_gradient_offsets())
        bad = list(OFFSETS)
        bad[4] = 6
        with self.assertRaisesRegex(HNANExactWitnessError, "OFFSET_DRIFT"):
            verify_gradient_offsets(offsets=tuple(bad))

    def test_reciprocal_phase(self):
        self.assertEqual([reciprocal_hash72(k) for k in range(9)],
                         [0, 71, 70, 69, 68, 67, 66, 65, 64])
        self.assertEqual(len({reciprocal_hash72(k) for k in range(72)}), 72)
        with self.assertRaises(HNANExactWitnessError):
            reciprocal_hash72(72)

    def test_exact_5184_addressing(self):
        self.assertEqual(serialization_address(0, 0, 0), 0)
        self.assertEqual(serialization_address(71, 7, 8), 5183)
        with self.assertRaises(HNANExactWitnessError):
            serialization_address(72, 0, 0)

    def test_no_authority_escalation(self):
        receipt = verify_read_only_candidate()
        self.assertTrue(receipt["matrix_factorization_exact"])
        self.assertTrue(receipt["gradient_offsets_constant"])
        self.assertFalse(receipt["native_inverse_closure_certified"])
        self.assertFalse(receipt["genesis_equivalence_certified"])
        self.assertFalse(receipt["vm81_mutation_authority"])

if __name__ == "__main__":
    unittest.main()
