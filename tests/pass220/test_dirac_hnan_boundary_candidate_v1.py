"""Dependency-scoped exact reference tests for Pass 220 Dirac/HNAN candidate boundaries."""
import unittest
from fractions import Fraction as F
from hhs_runtime.pass220.dirac_hnan_boundary_candidate_v1 import (
    ROLES, ZERO, reference_projector, normal_flux, evaluate,
)

class TestDiracHNAN(unittest.TestCase):
    def setUp(self):
        seed=((F(1),F(0)),(F(0),F(0)),(F(0),F(0)),(F(0),F(0)))
        self.psi=reference_projector(seed)
        self.sectors=[{"address":a,"role":r,"spinor":self.psi} for a,r in ROLES]

    def test_eight_reference_boundaries(self):
        out=evaluate(self.sectors)
        self.assertTrue(out["reference_pass"])
        self.assertEqual(len(out["sectors"]),8)
        self.assertFalse(out["native_admission"])
        self.assertFalse(out["particle_physics_mutated"])

    def test_exact_projector_and_zero_flux(self):
        self.assertEqual(reference_projector(self.psi),self.psi)
        self.assertEqual(normal_flux(self.psi),ZERO)

    def test_order_required(self):
        reversed_sectors=list(reversed(self.sectors))
        with self.assertRaisesRegex(ValueError,"HNAN_ORDER_ADDRESS_MISMATCH"):
            evaluate(reversed_sectors)

    def test_float_rejected(self):
        self.sectors[0]["spinor"]=((1.0,0),)*4
        with self.assertRaisesRegex(ValueError,"EXACT_RATIONAL_REQUIRED"):
            evaluate(self.sectors)

    def test_unprojected_spinor_not_admitted(self):
        self.sectors[0]["spinor"]=((F(1),F(0)),ZERO,ZERO,ZERO)
        self.assertFalse(evaluate(self.sectors)["reference_pass"])

    def test_zero_spinor_rejected(self):
        self.sectors[0]["spinor"]=(ZERO,)*4
        self.assertFalse(evaluate(self.sectors)["reference_pass"])

    def test_witness_flags_cannot_mint_native_state(self):
        out=evaluate(self.sectors,center_gate_witness=True,
                     conservation_witness=True,native_mapping_witness=True)
        self.assertFalse(out["native_admission"])

if __name__=="__main__":
    unittest.main()
