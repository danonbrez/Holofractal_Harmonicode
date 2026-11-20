"""Regression checks for exact rational Euclidean floor wrap."""
from __future__ import annotations

import importlib.util
from fractions import Fraction
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "hhs_runtime/pass220/pass220_ptm_exact_euclidean_mod_v1.py"
spec = importlib.util.spec_from_file_location("pass220_ptm_exact_euclidean_mod_v1", PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestPtmEuclideanMod(unittest.TestCase):
    def test_course_mod_one_fractional_part(self):
        self.assertEqual(mod.euclidean_mod_rational(Fraction(1001,1000),1), Fraction(1,1000))

    def test_course_mod_two_negative_wrap(self):
        self.assertEqual(mod.euclidean_mod_rational(-1,2), 1)

    def test_negative_fractional_wrap(self):
        self.assertEqual(mod.euclidean_mod_rational(Fraction(-1001,1000),1), Fraction(999,1000))

    def test_exact_large_moduli(self):
        for m in (247,248,249):
            for x in (Fraction(-3000003,3125),Fraction(0),Fraction(3000003,3125)):
                with self.subTest(m=m,x=x):
                    r=mod.euclidean_mod_rational(x,m)
                    self.assertGreaterEqual(r,0)
                    self.assertLess(r,m)
                    self.assertEqual((x-r)/m,(x-r)//m)

    def test_cellwise_payload(self):
        sample=((Fraction(1001,1000),-1),(0,Fraction(-1001,1000)))
        self.assertEqual(mod.map_exact_cells(sample,1),
                         ((Fraction(1,1000),Fraction(0)),(Fraction(0),Fraction(999,1000))))

    def test_modulus_guard(self):
        for m in (0,-1,Fraction(-1,2)):
            with self.subTest(m=m):
                with self.assertRaises(ValueError):
                    mod.euclidean_mod_rational(1,m)

    def test_does_not_claim_native_eval(self):
        receipt=mod.canonical_wrap_receipt()
        self.assertEqual(receipt["full_ptm_generator"],"NOT_EVALUATED")
        self.assertEqual(receipt["source_ncalc_third_argument_30"],"PRESERVED_UNINTERPRETED")


if __name__=="__main__":
    unittest.main()
