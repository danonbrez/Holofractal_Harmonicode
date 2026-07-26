from __future__ import annotations

import os
from pathlib import Path
import unittest

from hhs_pass157.executor import SOURCE, native_verify, verify
from hhs_pass157.model import (
    CENTERLINE_LABELS,
    construct_exact,
    fibonacci,
    phase_decompose,
    plastic_mul,
    plastic_power,
    polynomial_component,
    pythagorean,
)
from hhs_pass157.parser import compile_membrane, hash216, parse_source


class Pass157Positive(unittest.TestCase):
    def test_hash216_length(self): self.assertEqual(len(hash216(b"abc")), 216)
    def test_hash216_deterministic(self): self.assertEqual(hash216(b"abc"), hash216(b"abc"))
    def test_phase_positive(self): self.assertEqual(phase_decompose(137, 72), (1, 65))
    def test_phase_negative(self): self.assertEqual(phase_decompose(-137, 72), (-2, 7))
    def test_phase_large_bigint(self):
        n = -(10**200 + 179971)
        q, r = phase_decompose(n, 72)
        self.assertEqual(q * 72 + r, n)
        self.assertTrue(0 <= r < 72)
    def test_fibonacci(self): self.assertEqual(fibonacci(9), 34)
    def test_plastic_cubic_relation(self): self.assertEqual(plastic_power(3), (1, 1, 0))
    def test_plastic_fourth(self): self.assertEqual(plastic_power(4), (0, 1, 1))
    def test_plastic_multiply(self): self.assertEqual(plastic_mul((0, 1, 0), (0, 0, 1)), (1, 1, 0))
    def test_pythagorean(self): self.assertEqual(pythagorean(3, 2), (5, 12, 13))
    def test_digit_five(self): self.assertEqual(polynomial_component(5, 5, 12, 13), 313)
    def test_digit_nine(self): self.assertEqual(polynomial_component(9, 5, 12, 13), 28561)
    def test_construct_invariants(self):
        result = construct_exact(P=5,p=2,q=3,euclid_m=3,euclid_n=2,full_rotation=-137,local_modulus=72,centerline=tuple(range(1,12)))
        self.assertEqual(result.A * result.B, result.P4)
        self.assertEqual(result.Delta, result.P2 - result.pq)
    def test_orthogonal_lanes(self):
        result = construct_exact(P=5,p=2,q=3,euclid_m=3,euclid_n=2,full_rotation=-137,local_modulus=72,centerline=tuple(range(1,12)))
        self.assertEqual(tuple(lane.modulus for lane in result.orthogonal_phase), (100,175,275))
    def test_loshu_tensor(self):
        result = construct_exact(P=5,p=2,q=3,euclid_m=3,euclid_n=2,full_rotation=-137,local_modulus=72,centerline=tuple(range(1,12)))
        self.assertEqual(tuple(cell.lo_shu_digit for cell in result.tensor), (4,9,2,3,5,7,8,1,6))
    def test_vm81(self):
        result = construct_exact(P=5,p=2,q=3,euclid_m=3,euclid_n=2,full_rotation=-137,local_modulus=72,centerline=tuple(range(1,12)))
        self.assertEqual(len(result.vm81_cells), 81)
        self.assertTrue(all(0 <= cell < 72 for cell in result.vm81_cells))
    def test_centerline_labels(self): self.assertEqual(len(CENTERLINE_LABELS), 11)
    def test_source_preserved(self): self.assertEqual(parse_source(SOURCE).original_text, SOURCE)
    def test_unicode_view(self): self.assertIn("π", parse_source("O != π; Δ != ∆").normalized_unicode_view)
    def test_exact_decimal(self): self.assertIn("5/4", parse_source("x=1.25").exact_numbers)
    def test_exact_scientific(self): self.assertIn("1/1000", parse_source("x=1e-3").exact_numbers)
    def test_boundary_carrier(self): self.assertEqual(parse_source("x=ComplexInfinity").boundary_carriers, ("ComplexInfinity",))
    def test_symbolic_radical(self): self.assertEqual(parse_source("x=√(5)").symbolic_radicals, ("√",))
    def test_matrix_marker(self): self.assertEqual(parse_source("M=[[1,2],[3,4]]").matrix_tensor_markers.count("["), 3)
    def test_scope_graph(self): self.assertEqual(len(parse_source("f({x+[y]})").scope_edges), 3)
    def test_equality_membrane(self): self.assertEqual(compile_membrane("a=b==c")["lane_count"], 3)
    def test_global_membrane(self): self.assertTrue(compile_membrane("a=b=c")["global_simultaneous_constraint"])
    def test_typed_ast(self): self.assertTrue(compile_membrane("a=b")["typed_ast"])
    def test_no_arbitrary_target(self): self.assertFalse(compile_membrane("a=b")["arbitrary_solve_target"])
    def test_native_contract(self): self.assertEqual(native_verify()["contract"], "HHS-P157-PPF-MPTC")
    def test_cross_language_verify(self): self.assertEqual(verify()["replay"], "MATCH")


class Pass157Negative(unittest.TestCase):
    def test_zero_modulus(self):
        with self.assertRaises(ValueError): phase_decompose(1, 0)
    def test_negative_fibonacci(self):
        with self.assertRaises(ValueError): fibonacci(-1)
    def test_negative_plastic_exponent(self):
        with self.assertRaises(ValueError): plastic_power(-1)
    def test_bad_pythagorean_order(self):
        with self.assertRaises(ValueError): pythagorean(2, 2)
    def test_bad_digit(self):
        with self.assertRaises(KeyError): polynomial_component(10, 5, 12, 13)
    def test_zero_P(self):
        with self.assertRaises(ValueError): construct_exact(P=0,p=2,q=3,euclid_m=3,euclid_n=2,full_rotation=1,local_modulus=72,centerline=tuple(range(1,12)))
    def test_short_centerline(self):
        with self.assertRaises(ValueError): construct_exact(P=5,p=2,q=3,euclid_m=3,euclid_n=2,full_rotation=1,local_modulus=72,centerline=(1,2))
    def test_unsorted_centerline(self):
        with self.assertRaises(ValueError): construct_exact(P=5,p=2,q=3,euclid_m=3,euclid_n=2,full_rotation=1,local_modulus=72,centerline=(1,2,3,4,5,5,7,8,9,10,11))
    def test_zero_denominator_preserved(self): self.assertIn("ZERO_DENOMINATOR", parse_source("x=3/0").diagnostics[0])
    def test_unmatched_close(self): self.assertTrue(parse_source("x)").diagnostics)
    def test_unclosed_scope(self): self.assertTrue(parse_source("f(x").diagnostics)
    def test_unresolved_codepoint(self): self.assertEqual(parse_source("x=🙂").outcome, "PARSE_PARTIAL")
    def test_ambiguity_preserved(self): self.assertTrue(parse_source("72P").ambiguities)
    def test_invalid_mode(self):
        with self.assertRaises(ValueError): compile_membrane("a=b", "RANDOM_SOLVE")
    def test_non_string_source(self):
        with self.assertRaises(TypeError): parse_source(123)  # type: ignore[arg-type]
    def test_O_pi_distinct(self): self.assertTrue(compile_membrane("O!=π")["symbols_distinct"]["O_ne_pi"])
    def test_hash_input_changes(self): self.assertNotEqual(hash216(b"a"), hash216(b"b"))


if __name__ == "__main__":
    unittest.main()
