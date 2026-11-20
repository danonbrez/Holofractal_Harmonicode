"""Exact source grammar regression tests: ordered syntax, not Ncalc values."""
from __future__ import annotations
import unittest
from hhs_runtime.pass220.pass220_ptm_ordered_expression_lowering_v1 import (
    SourceSyntaxError, Node, tokenize, lower, receipt, canonical_receipts,
)
from hhs_runtime.pass220.pass220_ptm_exact_generator_witness_v1 import (
    GENERATOR_SOURCE, CONSTRAINED_SOURCE,
)


class TestPtmExpressionLowering(unittest.TestCase):
    def test_complete_source_lowering(self):
        for source in (GENERATOR_SOURCE, CONSTRAINED_SOURCE):
            with self.subTest(source=source[:24]):
                r=receipt(source)
                self.assertEqual(r["operator_counts"]["NcalcMatrixPower"],3)
                self.assertEqual(r["operator_counts"]["NcalcEuclideanMod"],1)
                self.assertEqual(r["operator_counts"]["MatrixTimes"],3)
                self.assertEqual(r["root_op"],"-")
                self.assertEqual(r["node_count"],len(r["ordered_postorder"]))
                self.assertEqual(r["native_value_execution"],"NOT_EXECUTED")

    def test_preserves_comparison_objects(self):
        raw=receipt(GENERATOR_SOURCE)
        constrained=receipt(CONSTRAINED_SOURCE)
        self.assertNotIn("==",raw["operator_counts"])
        self.assertGreaterEqual(constrained["operator_counts"]["=="],4)
        self.assertIn(("symbol","t",0),constrained["ordered_postorder"])
        self.assertIn(("literal","25",0),constrained["ordered_postorder"])
        self.assertIn(("literal","248",0),constrained["ordered_postorder"])
        self.assertIn(("literal","30",0),constrained["ordered_postorder"])

    def test_euclidean_mod_argument_order(self):
        root=lower(GENERATOR_SOURCE)
        def nodes(node):
            yield node
            for child in node.args:
                yield from nodes(child)
        matches=[n for n in nodes(root) if n.op=="NcalcEuclideanMod"]
        self.assertEqual(len(matches),1)
        self.assertEqual(len(matches[0].args),3)
        self.assertEqual(matches[0].args[1],Node("symbol",text="m"))
        self.assertEqual(matches[0].args[2],Node("literal",text="30"))

    def test_list_and_ordered_tensor_power(self):
        root=lower(GENERATOR_SOURCE)
        def nodes(node):
            yield node
            for child in node.args:
                yield from nodes(child)
        lists=[n for n in nodes(root) if n.op=="List"]
        self.assertGreaterEqual(len(lists),5)
        self.assertTrue(all(len(n.args)>0 for n in lists))
        self.assertGreater(sum(n.op=="^" for n in nodes(root)),4)

    def test_exact_decimal_lexemes(self):
        values=[t for t in tokenize(GENERATOR_SOURCE) if "." in t]
        self.assertEqual(values,["0.01","0.001","0.2","0.209"])
        self.assertEqual(lower("-2^2").op,"unary-")
        self.assertEqual(lower("(-2)^2").op,"^")

    def test_invalid_source_rejected(self):
        for bad in ("", "List(1,,2)", "NcalcMatrixPower(", "OtherCall(3)", "x@2", "x+y)"):
            with self.subTest(source=bad):
                with self.assertRaises(SourceSyntaxError):
                    lower(bad)

    def test_replay_determinism(self):
        self.assertEqual(canonical_receipts(),canonical_receipts())


if __name__=="__main__":
    unittest.main()
