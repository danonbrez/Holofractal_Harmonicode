"""Exact candidate-only Lane 5 dyadic register checks."""
import unittest
from fractions import Fraction
from hhs_runtime.pass220.lane5_dyadic_virtual_register import (
    VirtualRegister, decode_address, dyadic, encode_address,
    hydration_address, prime_center_witness, reciprocal_witness,
    shell, symmetric_witness, symbolic_reciprocal_pair, prepare_lane5_hydration_candidate,
)

class DyadicVirtualRegisterTests(unittest.TestCase):
    def test_reciprocal_shells(self):
        for n in range(17):
            self.assertEqual(len(shell(n)), 2*n + 1)
            self.assertTrue(reciprocal_witness(n))
            self.assertTrue(reciprocal_witness(-n))
        self.assertEqual(dyadic(-6), Fraction(1, 64))
        with self.assertRaises(TypeError):
            dyadic(1.5)

    def test_radix72_round_trip(self):
        for index in [0, 1, 71, 72, 5183, 5184, 72**72-1]:
            self.assertEqual(encode_address(decode_address(index)), index)
        with self.assertRaises(ValueError):
            decode_address(72**72)
        with self.assertRaises(ValueError):
            encode_address((0,)*71 + (72,))

    def test_5184_address(self):
        self.assertEqual(hydration_address(71, 71), 5183)
        self.assertEqual(hydration_address(0, 0), 0)

    def test_register_preserves_metadata(self):
        r = VirtualRegister(decode_address(5184), -8, "u72", "ordered-cell", "OP_11", "source:1")
        self.assertEqual(r.index, 5184)
        self.assertEqual(r.quantization, Fraction(1, 256))
        self.assertEqual(r.provenance, "source:1")

    def test_constructor_projection_and_symbolic_guard(self):
        a = symmetric_witness(Fraction(3), 2)
        self.assertEqual((a["p"], a["q"], a["delta"]), (Fraction(1), Fraction(5), Fraction(4)))
        odd = symmetric_witness(Fraction(3), 1)
        self.assertEqual(odd["status"], "SYMBOLIC_UNADMITTED")
        self.assertIsNone(odd["p"])
        self.assertEqual(odd["pq"], Fraction(7))

    def test_prime_unit_defect(self):
        self.assertEqual(prime_center_witness(19)["modulus"], 360)
        self.assertEqual(prime_center_witness(3)["modulus"], 8)
        with self.assertRaises(ValueError):
            prime_center_witness(9)

    def test_exact_symbolic_reciprocal_pair(self):
        for n in range(-10, 11):
            w = symbolic_reciprocal_pair(n)
            self.assertEqual(w["delta"], dyadic(n))
            self.assertEqual(w["difference_of_squares"], Fraction(1))
            self.assertEqual(w["p_times_q"], Fraction(1))
            self.assertEqual(w["admission"], "CANDIDATE_ONLY")
        self.assertEqual(symbolic_reciprocal_pair(0)["P"], ("POSITIVE_SQRT", Fraction(2)))
        self.assertEqual(symbolic_reciprocal_pair(1)["P"], ("POSITIVE_SQRT", Fraction(3)))

    def test_inherited_typed_gate_proposal(self):
        r = VirtualRegister(decode_address(5183), -3, "u72", "ordered-cell", "P_pq", "source:191")
        proposal = prepare_lane5_hydration_candidate(r)
        self.assertEqual(proposal["virtual_address"], 5183)
        self.assertEqual(proposal["quantization"], Fraction(1, 8))
        self.assertEqual(proposal["inherited_gate_id"], "HHS_GATE_EQ")
        self.assertTrue(proposal["candidate_only"])
        self.assertIsNone(proposal["canonical_hash_mutation"])
        with self.assertRaises(ValueError):
            prepare_lane5_hydration_candidate(r, witness=symbolic_reciprocal_pair(2))
        with self.assertRaises(ValueError):
            bad = symbolic_reciprocal_pair(-3)
            bad["admission"] = "ADMITTED"
            prepare_lane5_hydration_candidate(r, witness=bad)

if __name__ == "__main__":
    unittest.main()
