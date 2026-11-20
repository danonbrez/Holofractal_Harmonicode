"""Exact integer tests for P/t/m Delta boundary, without assigning native quotient semantics."""
from __future__ import annotations

import importlib.util
from fractions import Fraction
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "hhs_runtime/pass220/pass220_ptm_dyadic_shell_v1.py"
spec = importlib.util.spec_from_file_location("ptm_dyadic_shell", PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestPtmDyadicShell(unittest.TestCase):
    def test_source_preserved(self):
        self.assertEqual(mod.DELTA_SOURCE, "∆=2^n+(-2⁰,+2⁰,2ⁿ)/2^m+(-2⁰,+2⁰,2^m)")

    def test_exact_shift_components(self):
        for k in (0, 1, 25, 247, 248, 249):
            a, b, c = mod.shell(k)
            self.assertEqual(b-a, 2)
            self.assertEqual(a+b, c)
            self.assertEqual(c, 2*(1 << k))

    def test_identity_coordinate_probe(self):
        self.assertEqual(mod.exact_componentwise_probe(248,248),
                         (Fraction(1), Fraction(1), Fraction(1)))

    def test_adjacent_modulus_boundaries(self):
        rows = mod.witness()["rows"]
        self.assertEqual([row["m"] for row in rows], [247,248,249])
        self.assertEqual(len({tuple(row["denominator_components"]) for row in rows}),3)
        self.assertTrue(all(row["ncalc_matrix_output"]=="NOT_EVALUATED" for row in rows))
        self.assertTrue(all(row["native_tensor_quotient"]=="NOT_EVALUATED" for row in rows))

    def test_no_negative_or_noninteger_exponent(self):
        for invalid in (-1, Fraction(1,2), 1.0, True):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    mod.shell(invalid)


if __name__ == "__main__":
    unittest.main()
