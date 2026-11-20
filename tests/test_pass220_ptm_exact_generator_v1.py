"""Regression checks for the source-bound P/t/m exact-rational witness.

Run: python -m unittest discover -s tests -p 'test_pass220_ptm_exact_generator_v1.py'
No Ncalc numerical evaluation is performed here.
"""
from __future__ import annotations

import importlib.util
from fractions import Fraction
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "hhs_runtime/pass220/pass220_ptm_exact_generator_witness_v1.py"
spec = importlib.util.spec_from_file_location("pass220_ptm_exact_generator_witness_v1", SOURCE)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestPtmExactGenerator(unittest.TestCase):
    def test_exact_reference_receipt(self):
        receipt = mod.witness()
        self.assertTrue(receipt["exact_reference_reconstruction"])
        self.assertEqual(receipt["native_evaluation"], "NOT_EXECUTED")
        self.assertEqual(receipt["scale"], "1000001/6250")
        self.assertEqual(receipt["reference"], {"P": "Sqrt(3)", "t": 25, "m": 248})

    def test_all_nine_exact_cells(self):
        for i in range(3):
            for j in range(3):
                with self.subTest(row=i, col=j):
                    self.assertEqual(
                        mod.REFERENCE[i][j],
                        mod.SCALE * mod.FACTOR[i][j] - 2 * mod.CORRECTION[i][j],
                    )

    def test_exact_integer_fraction_channels(self):
        integer_component = tuple(
            tuple(160 * mod.FACTOR[i][j] - 2 * mod.CORRECTION[i][j] for j in range(3))
            for i in range(3)
        )
        fractional_component = tuple(
            tuple(Fraction(mod.FACTOR[i][j], 6250) for j in range(3))
            for i in range(3)
        )
        self.assertEqual(integer_component, (
            (-162, -482, -1442),
            (4640, 0, 960),
            (-642, -962, -4802),
        ))
        self.assertEqual(
            tuple(tuple(integer_component[i][j] + fractional_component[i][j] for j in range(3)) for i in range(3)),
            mod.REFERENCE,
        )

    def test_operator_and_order_preservation(self):
        for source in (mod.GENERATOR_SOURCE, mod.CONSTRAINED_SOURCE):
            self.assertEqual(source.count("NcalcMatrixPower"), 3)
            self.assertEqual(source.count("NcalcEuclideanMod"), 1)
            self.assertEqual(source.count("MatrixTimes"), 3)
            self.assertIn("List((-1),1,(-1))", source)
            self.assertIn("0.01-0.001+0.2", source)
        self.assertIn("MatrixTimes(t,", mod.GENERATOR_SOURCE)
        self.assertIn("MatrixTimes((t==25),", mod.CONSTRAINED_SOURCE)
        self.assertIn("(m==248),30", mod.CONSTRAINED_SOURCE)
        self.assertIn("((x*y==Sqrt(3))", mod.CONSTRAINED_SOURCE)
        self.assertIn("((z*w==Sqrt(3))", mod.CONSTRAINED_SOURCE)

    def test_sweep_is_only_a_schedule(self):
        receipt = mod.witness()
        self.assertEqual(len(receipt["sweep"]), 9)
        self.assertEqual(len(set(receipt["sweep"])), 9)
        self.assertIn((25, 248), receipt["sweep"])
        self.assertEqual(receipt["required_next_binding"], "SOURCE_BOUND_NCALC_MATRIX_POWER_AND_EUCLIDEAN_MOD")
        self.assertNotIn("sweep_outputs", receipt)

    def test_reference_ratios_without_dividing_zero(self):
        f = mod.FACTOR
        self.assertEqual(Fraction(f[0][1], f[0][0]), 3)
        self.assertEqual(Fraction(f[0][2], f[0][1]), 3)
        self.assertEqual(Fraction(f[1][0], f[1][2]), Fraction(29, 6))
        self.assertEqual(Fraction(f[2][1], f[2][0]), Fraction(3, 2))


if __name__ == "__main__":
    unittest.main()
