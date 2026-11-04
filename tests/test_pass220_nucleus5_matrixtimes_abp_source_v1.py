"""Source-identity regression for the nucleus-5 HARMONICODE ingress payload.

No host numeric evaluation; native Pass159/VM81 admission is a separate gate.
"""
import unittest
from unittest.mock import patch
from hashlib import sha256

from hhs_runtime.hhs_pass220_nucleus5_matrixtimes_abp_source_v1 import (
    ABP_ORDERED_EDGES,
    Nucleus5Source,
    RECIPROCAL_SOURCE,
    VERBATIM_SOURCE,
    structural_source_checks,
    bind_inherited_hnan_ingress,
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

    def test_native_hnan_qgu_ingress_binding(self):
        for mode in ("ONE_INPUT", "EQUATION_INPUT"):
            ingress = bind_inherited_hnan_ingress(mode)
            self.assertEqual(ingress.nucleus_cell, 5)
            self.assertEqual(ingress.source_bytes, VERBATIM_SOURCE.encode("utf-8"))
            self.assertEqual(ingress.source_sha256, sha256(ingress.source_bytes).hexdigest())
            self.assertEqual(ingress.parameter_edge_bytes,
                             tuple(e.encode("utf-8") for e in Nucleus5Source().parameter_edges(mode)))
            self.assertEqual(ingress.inherited_hnan_terminal_source, "xy+epsilon")
            self.assertEqual(len(ingress.inherited_hnan_receipt_sha256), 64)
            self.assertEqual(len(ingress.inherited_qgu_receipt_sha256), 64)

    def test_reject_unadmitted_hnan_gate(self):
        with patch("hhs_runtime.pass219.hnan_4x4_recursive_gate_v1.hnan_loshu_resolution_receipt",
                   return_value={"status": "FAIL"}):
            with self.assertRaisesRegex(ValueError, "INHERITED_HNAN_QGU_GATE_REJECTED"):
                bind_inherited_hnan_ingress("ONE_INPUT")

    def test_reject_unknown_parameter_orientation(self):
        with self.assertRaisesRegex(ValueError, "UNKNOWN_ABP_CONFIGURATION"):
            bind_inherited_hnan_ingress("UNREGISTERED")

    def test_ordered_phase_channels_are_distinct(self):
        self.assertIn("AB==P^4", ABP_ORDERED_EDGES)
        self.assertIn("BA==-P^4", ABP_ORDERED_EDGES)


if __name__ == "__main__":
    unittest.main()
