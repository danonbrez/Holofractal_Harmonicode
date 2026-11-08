"""Dependency-scoped exact witness checks; no state mutation."""
import unittest
from fractions import Fraction

from hhs_runtime.hhs_pass220_ers_analog_qutrit_netlist_v2_audit import (
    CIRCUITS, STAGES, F_EXPECTED, POLYNOMIAL_CELLS, branch_audit,
    phase_root_address, primitive_phase_audit, qutrit_projection_witness,
    sum_polynomials, unit_orbit, unit_orbit_nonzero_guards, witness_packet,
)


class ERSAnalogQutritV2Test(unittest.TestCase):
    def test_ten_closed_circuits_and_six_stages(self):
        self.assertEqual(len(CIRCUITS), 10)
        self.assertEqual(len(STAGES), 6)
        self.assertEqual(len(POLYNOMIAL_CELLS), 11)

    def test_polynomial_sum_exact_not_assumed(self):
        self.assertEqual(sum_polynomials(), F_EXPECTED)
        self.assertEqual(F_EXPECTED[0], -11)

    def test_unit_orbit_and_guarded_singular_loci(self):
        for P in (Fraction(-3), Fraction(0), Fraction(1),
                  Fraction(2), Fraction(13, 7)):
            o = unit_orbit(P)
            self.assertEqual(o["Delta"], 1)
            self.assertEqual(o["q_minus_p"], 2)
            self.assertEqual(o["p_plus_q"], 2 * P)
        self.assertFalse(unit_orbit_nonzero_guards(0)["p_plus_q"])
        self.assertFalse(unit_orbit_nonzero_guards(1)["p"])
        self.assertFalse(unit_orbit_nonzero_guards(-1)["q"])

    def test_current_rational_grounding_is_open(self):
        w = branch_audit()
        self.assertEqual(w["a_squared"], Fraction(1004006004001, 1000000000000))
        self.assertEqual(w["pythagorean_tail"], Fraction(-4006004001, 500000000000))
        self.assertFalse(w["tail_closed"])

    def test_root_exact_sector_round_trip(self):
        for k in range(72):
            a = phase_root_address(k)
            self.assertEqual(a["chromatic"] + 12 * a["sector"], k)
            self.assertEqual(a["u72"], 0)
        with self.assertRaises(ValueError):
            phase_root_address(72)

    def test_primitive_root_reciprocal_gate_must_not_close(self):
        w = primitive_phase_audit()
        self.assertTrue(w["u36_is_minus_one"])
        self.assertFalse(w["u36_is_one"])
        self.assertFalse(w["u_minus_180_is_one"])
        self.assertTrue(w["u_minus_180_equals_u_minus_36"])

    def test_qutrit_projection_exact(self):
        self.assertTrue(all(qutrit_projection_witness().values()))

    def test_no_canonical_admission_from_probes(self):
        w = witness_packet()
        self.assertTrue(w["polynomial_bank_exact"])
        self.assertTrue(w["F_equals_G_minus_11"])
        for key in ("vm81_admitted", "hash72_minted", "hash216_committed",
                    "lane5_hydrated"):
            self.assertFalse(w[key])


if __name__ == "__main__":
    unittest.main()
