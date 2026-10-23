"""Dependency-scoped tests for Pass 220 rectangular dimension closure."""
import unittest
from fractions import Fraction
from hhs_runtime.pass220.exact_rectangular_dimension_closure_v1 import rectangular_dimension_closure


class RectangularClosureTests(unittest.TestCase):
    def test_six_cell_transpose_and_hash72_quantization(self):
        a = [[1, 2, 3], [4, 5, 6]]
        b = [[1, 4], [2, 5], [3, 6]]
        w = rectangular_dimension_closure(a, b)
        self.assertEqual(w.product_capacity, 36)
        self.assertEqual(w.exact_square_root, 6)
        self.assertEqual(w.copies_per_ring, 12)
        self.assertEqual(len(w.ring_a), 72)
        self.assertEqual(len(w.ring_b), 72)
        self.assertEqual(w.ring_a[:6], tuple(map(Fraction, (1, 2, 3, 4, 5, 6))))
        self.assertEqual(w.ring_b[:6], tuple(map(Fraction, (1, 4, 2, 5, 3, 6))))
        self.assertEqual(w.admission_status, "CANDIDATE_ONLY")
        self.assertEqual(w.phase_status, "HNAN_NOT_EVALUATED")

    def test_twelve_cell_transpose_quantizes_six_times(self):
        a = [[3, 3, "9/4", "55/8", "50/7", "37/5"],
             ["1/3", "1/3", "4/9", "8/55", "7/50", "5/37"]]
        b = [list(row) for row in zip(*a)]
        w = rectangular_dimension_closure(a, b)
        self.assertEqual((w.product_capacity, w.exact_square_root), (144, 12))
        self.assertEqual(w.copies_per_ring, 6)
        self.assertEqual(w.cells_a[2], Fraction(9, 4))

    def test_fails_closed_on_mismatch_and_non_exact_ring(self):
        with self.assertRaises(ValueError):
            rectangular_dimension_closure([[1, 2, 3]], [[1], [2], [4]])
        with self.assertRaises(ValueError):
            rectangular_dimension_closure([[1, 2, 3, 4, 5]], [[1], [2], [3], [4], [5]])
        with self.assertRaises(ValueError):
            rectangular_dimension_closure([[1, 2]], [[1], [2]], ring_width=0)
        with self.assertRaises(TypeError):
            rectangular_dimension_closure([[1.0, 2]], [[1.0], [2]])


if __name__ == "__main__":
    unittest.main()
