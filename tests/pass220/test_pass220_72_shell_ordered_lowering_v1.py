"""Dependency-scoped Pass 220 source preservation and negative tests."""
import unittest
from hhs_runtime.pass220_72_shell_ordered_lowering_v1 import (
    SOURCE, SOURCE_SHA256, SOURCE_GATE_OFFSETS, INNER_GRAMMAR,
    SourceBindingError, lower_exact_source, admission_disposition,
)

class Test72ShellLowering(unittest.TestCase):
    def test_exact_source_and_structure(self):
        result = lower_exact_source(SOURCE)
        self.assertEqual(result.source_sha256, SOURCE_SHA256)
        self.assertEqual(result.gate_offsets, SOURCE_GATE_OFFSETS)
        self.assertEqual(result.source_length, 121)
        root = result.root
        self.assertEqual(root.kind, "HHS_ORDERED_OUTER_EQUALITY")
        chain = root.children[0].children[0]
        self.assertEqual(chain.kind, "HHS_ORDERED_CHAIN_3_GATES")
        self.assertEqual(tuple(node.source for node in chain.children), INNER_GRAMMAR)
        self.assertEqual([(node.byte_start,node.byte_end) for node in chain.children],
                         [(1,74),(76,89),(91,92),(94,99)])
        self.assertFalse(result.native_proof_admitted)
        self.assertFalse(result.vm81_admitted)
        self.assertEqual(admission_disposition(result), "UNSUPPORTED_DOMAIN_NATIVE_PROOF_REQUIRED")

    def test_exact_modulus(self):
        result = lower_exact_source(SOURCE)
        self.assertEqual(result.rational_residue.numerator,
                         775710873160901421359061468620360862729920180854006643986760192036)
        self.assertEqual(result.rational_residue.denominator,
                         3110094060648844770831880556173301180945943326884396380767822265625)

    def test_mutations_fail_closed(self):
        mutations = [
            SOURCE.replace("==b==", "==b="),
            SOURCE.replace("b==1/b^3", "b==1/b^2"),
            SOURCE.replace("c^2-a^2", "a^2-c^2"),
            SOURCE.replace("0.2752680919", "0.2752680918"),
            SOURCE.replace("72^72", "72^71", 1),
            SOURCE.replace("==b==", "==b =="),
            SOURCE.replace("x^4", "X^4"),
        ]
        for candidate in mutations:
            with self.subTest(candidate=candidate), self.assertRaises(SourceBindingError):
                lower_exact_source(candidate)

if __name__ == "__main__":
    unittest.main()
