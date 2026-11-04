"""Source-identity regression for the nucleus-5 HARMONICODE ingress payload.

No host numeric evaluation; native Pass159/VM81 admission is a separate gate.
"""
import unittest

from hhs_runtime.hhs_pass220_nucleus5_matrixtimes_abp_source_v1 import (
    ABP_ORDERED_EDGES,
    Nucleus5Source,
    RECIPROCAL_SOURCE,
    VERBATIM_SOURCE,
    structural_source_checks,
)


class Nucleus5SourceTests(unittest.TestCase):
    def test_verbatim_source_structure(self):
        self.assertTrue(all(structural_source_checks().values()))
        self.assertEqual(VERBATIM_SOURCE.count("=="), 3)
        self.assertEqual(VERBATIM_SOURCE.count("MatrixTimes("), 2)
        self.assertEqual(Nucleus5Source().native_source_bytes(), VERBATIM_SOURCE.encode("utf-8"))

    def test_nucleus_and_reciprocal_retained(self):
        self.assertEqual(Nucleus5Source().nucleus_cell, 5)
        self.assertTrue(VERBATIM_SOURCE.endswith("/(" + RECIPROCAL_SOURCE + ")"))

    def test_input_orientations_not_conjoined(self):
        witness = Nucleus5Source()
        first = witness.parameter_edges("ONE_INPUT")
        second = witness.parameter_edges("EQUATION_INPUT")
        self.assertIn("A==P^2", first)
        self.assertIn("A!=B", first)
        self.assertNotIn("A==B", first)
        self.assertIn("A==B", second)
        self.assertIn("A!=P^2", second)
        self.assertNotIn("A==P^2", second)
        self.assertNotIn("A==B", ABP_ORDERED_EDGES)

    def test_ordered_phase_channels_are_distinct(self):
        self.assertIn("AB==P^4", ABP_ORDERED_EDGES)
        self.assertIn("BA==-P^4", ABP_ORDERED_EDGES)


if __name__ == "__main__":
    unittest.main()
