"""Preserve visible Pass 220–222 obligation lineage without inventing Pass 222."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "contracts/architecture/HHS_PASS220_221_222_CUMULATIVE_OBLIGATION_REGISTER_V1.json"


class TestCumulativePassObligations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(REGISTER.read_text(encoding="utf-8"))

    def test_passes_are_distinct_and_unclosed(self):
        s = self.manifest
        self.assertEqual(s["schema"], "HHS_PASS220_221_222_CUMULATIVE_OBLIGATION_REGISTER_V1")
        self.assertEqual([p["pass"] for p in s["passes"]], [220, 221, 222])
        self.assertFalse(any(s["completion_claims"].values()))

    def test_original_sources_and_scope_are_preserved(self):
        p220, p221, p222 = self.manifest["passes"]
        self.assertTrue((ROOT / p220["canonical_source"]).is_file())
        self.assertTrue((ROOT / p221["canonical_source"]).is_file())
        self.assertIn("native Linux", " ".join(p220["known_normative_obligations"]))
        self.assertIn("Instagram", " ".join(p221["known_normative_obligations"]))
        self.assertIsNone(p222["canonical_source"])
        self.assertEqual(p222["known_normative_obligations"], [])

    def test_thread_spec_is_additive_not_superseding(self):
        relation = self.manifest["pr914_relation"]
        self.assertTrue((ROOT / relation["source"]).is_file())
        self.assertIn("NOT_A_REPLACEMENT", relation["role"])
        self.assertTrue(self.manifest["implementation_order"])


if __name__ == "__main__":
    unittest.main()
