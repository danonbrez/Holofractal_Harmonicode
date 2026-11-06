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

    def test_canonical_abp_and_successor(self):
        witness = Nucleus5Source()
        first = witness.parameter_edges("ONE_INPUT")
        successor = witness.parameter_edges("SUCCESSOR_INPUT")
        self.assertEqual(first, ABP_ORDERED_EDGES)
        self.assertEqual(successor[:len(first)], first)
        self.assertIn("A==P^2", first)
        self.assertIn("B==P^2", first)
        self.assertIn("A==B", first)
        self.assertIn("P^2-pq==1", first)
        self.assertIn("P_next==P+3", successor)
        self.assertIn("A_next==P_next^2", successor)
        self.assertIn("B_next==P_next^2", successor)
        self.assertFalse(any("!=" in edge for edge in successor))

    def test_native_hnan_qgu_ingress_binding(self):
        for mode in ("ONE_INPUT", "SUCCESSOR_INPUT"):
            ingress = bind_inherited_hnan_ingress(mode)
            self.assertEqual(ingress.nucleus_cell, 5)
            self.assertEqual(ingress.source_bytes, VERBATIM_SOURCE.encode("utf-8"))
            self.assertEqual(ingress.compilation_source_bytes, Nucleus5Source().native_compilation_source_bytes(mode))
            self.assertEqual(ingress.compilation_source_sha256, sha256(ingress.compilation_source_bytes).hexdigest())
            self.assertTrue(ingress.compilation_source_bytes.startswith(b"List(" + ingress.source_bytes + b","))
            self.assertEqual(ingress.compilation_source_bytes.count(b"=="), 3 + sum(e.count(b"==") for e in ingress.parameter_edge_bytes))
            self.assertEqual(ingress.compilation_source_bytes.count(b"MatrixTimes("), 2)
            self.assertEqual(ingress.source_sha256, sha256(ingress.source_bytes).hexdigest())
            self.assertEqual(ingress.parameter_edge_bytes,
                             tuple(e.encode("utf-8") for e in Nucleus5Source().parameter_edges(mode)))
            self.assertEqual(ingress.inherited_hnan_terminal_source, "xy+epsilon")
            self.assertEqual(len(ingress.inherited_hnan_receipt_sha256), 64)
            self.assertEqual(len(ingress.inherited_qgu_receipt_sha256), 64)

    def test_ordered_circuit_preserves_canonical_base(self):
        source = Nucleus5Source()
        a = source.native_compilation_source_bytes("ONE_INPUT")
        b = source.native_compilation_source_bytes("SUCCESSOR_INPUT")
        self.assertNotEqual(a, b)
        self.assertTrue(b.startswith(a[:-1] + b","))
        self.assertIn(b"A==P^2,B==P^2,A==B", a)
        self.assertIn(b"P_next==P+3", b)
        self.assertNotIn(b"P_next==P+3", a)
        self.assertIn(VERBATIM_SOURCE.encode("utf-8"), a)
        self.assertIn(VERBATIM_SOURCE.encode("utf-8"), b)

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
