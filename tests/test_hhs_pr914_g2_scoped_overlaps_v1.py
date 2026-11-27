"""Execute G2 conflict receipt generation on the sourced PR overlap slice."""
import json
from pathlib import Path
import unittest

from tools.hhs_pr914_g2_conflict_receipts import evaluate_conflicts, validate_receipt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "contracts/architecture/HHS_PR914_G2_SCOPED_MECHANICAL_OVERLAPS_20261127.json"
CONTRACT = ROOT / "contracts/architecture/HHS_PR914_G2_DEPENDENCY_CONFLICT_AND_CANDIDATE_COMPOSITION_CONTRACT_V1.json"


class TestG2ScopedEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.result = evaluate_conflicts(cls.source["events"], cls.contract)

    def test_source_scope_and_overlap_paths(self):
        self.assertEqual(self.source["scope"], "7_PR_FOCUSED_NOT_FULL_G0_G1_CENSUS")
        self.assertEqual(self.source["observed_overlap_pairs"], 3)
        self.assertEqual(len(self.source["source_prs"]), 7)
        expected = {
            ("PR:000914", "PR:000917"): {"applications/holofractal_harmonizer/src/project-lifecycle.mjs"},
            ("PR:000900", "PR:000901"): {"examples/ParticleSimulation.html"},
            ("PR:000908", "PR:000921"): {
                "hhs_runtime/hhs_pass220_remote_ref_tree_reconciliation_v1.py",
                "tests/pass220/test_hhs_pass220_v162_module194_ordered_hnan_native_boundary_v1.py",
            },
        }
        observed = {
            tuple(e["entry_ids"]): set(e["paths_or_requirement_ids"])
            for e in self.source["events"]
        }
        self.assertEqual(observed, expected)

    def test_receipts_are_all_unresolved_and_evidence_bound(self):
        self.assertEqual(self.result["event_count"], 3)
        self.assertEqual(len(self.result["unresolved_conflicts"]), 3)
        for receipt in self.result["conflict_receipts"]:
            self.assertEqual(receipt["status"], "UNRESOLVED")
            self.assertEqual(receipt["semantic_assessment"], "UNASSESSED")
            self.assertIsNone(receipt["integration_commit"])
            self.assertTrue(all(len(sha) == 40 for sha in receipt["exact_source_heads"].values()))
            self.assertIn("G2_BLOCKED_UNRESOLVED_SEMANTIC_CONFLICT",
                          validate_receipt(receipt, self.contract))

    def test_candidate_never_promoted_by_scoped_evidence(self):
        self.assertFalse(self.result["candidate_composed"])
        self.assertFalse(self.result["g2_complete"])
        self.assertFalse(self.source["all_entries_reconciled"])
        self.assertFalse(self.source["candidate_composed"])


if __name__ == "__main__":
    unittest.main()
