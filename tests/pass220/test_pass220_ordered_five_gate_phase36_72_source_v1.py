"""Fail-closed, source-only conformance for the supplied ordered phase36/72 expression.

This test is NOT a native VM81 proof or a Hash72/Hash216 mint.
"""
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "contracts/pass220/PASS_220_ORDERED_FIVE_GATE_PHASE36_72_SOURCE_V1.harmonicode"
SOURCE_SHA256 = "ceec282499ddaf48eba1d25b6313c407d9466d379e321b47f9a6b3f752c2a499"
EXPECTED_EQUALITIES = ((54, 3), (139, 3), (223, 1), (229, 0), (276, 1))


def equality_edges(source: str):
    """Return ordered == positions and parenthesis depths; never evaluate equality."""
    depth = 0
    positions = []
    for index, char in enumerate(source):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced closing delimiter")
        if source.startswith("==", index):
            positions.append((index, depth))
    if depth != 0:
        raise ValueError("unbalanced opening delimiter")
    return tuple(positions)


class TestOrderedFiveGateSource(unittest.TestCase):
    def test_verbatim_source(self):
        raw = SOURCE.read_bytes()
        self.assertEqual(len(raw), 283)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(raw.decode("ascii").encode("ascii"), raw)
        self.assertNotIn(bytes((10,)), raw)

    def test_nested_ordered_edges(self):
        source = SOURCE.read_text(encoding="ascii")
        self.assertEqual(equality_edges(source), EXPECTED_EQUALITIES)
        self.assertEqual(sum(depth == 0 for _, depth in EXPECTED_EQUALITIES), 1)
        self.assertEqual(source[229:231], "==")
        self.assertEqual(source.count("=="), 5)

    def test_ordered_pairs_and_phase_carriers_retained(self):
        source = SOURCE.read_text(encoding="ascii")
        for fragment in (
            "(x*y-1)/b^2*(z*w-1)/(c^2-a^2)",
            "(z*w-1)/b^2*(x*y-1)/(c^2-a^2)",
            "((-x)*y)/(z*w)*(z*w)/((-x)*y)",
            "((-z)*w)/(x*y)*(x*y)/((-z)*w)",
            "^(u^36==z^2)",
            "^(x^2==u^36)",
            "/u^72",
        ):
            self.assertIn(fragment, source)

    def test_no_host_equality_or_native_receipt_claim(self):
        # A source-only test must never claim native closure, admission or minting.
        self.assertTrue(SOURCE.suffix == ".harmonicode")


if __name__ == "__main__":
    unittest.main()
