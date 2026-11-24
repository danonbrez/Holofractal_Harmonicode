"""G2 conflict-receipt evidence integrity and authority boundary tests."""
import copy
import json
from pathlib import Path
import unittest

from tools.hhs_pr914_g2_conflict_receipts import (
    evaluate_conflicts, unresolved_receipt, validate_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts/architecture/HHS_PR914_G2_DEPENDENCY_CONFLICT_AND_CANDIDATE_COMPOSITION_CONTRACT_V1.json"


class TestG2ConflictReceipts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def sample(self):
        return {
            "conflict_class": "TEXTUAL_OVERLAP",
            "entry_ids": ["PR:000918", "PR:000917"],
            "paths_or_requirement_ids": ["applications/ide/export.mjs"],
            "exact_source_heads": {
                "PR:000917": "a" * 40, "PR:000918": "b" * 40,
            },
            "mechanical_evidence": {
                "source": "G2_TEST_FIXTURE_NOT_LIVE_EVIDENCE",
                "shared_path": "applications/ide/export.mjs",
            },
        }

    def test_receipt_has_all_contract_fields_and_stays_unresolved(self):
        receipt = unresolved_receipt(self.sample(), self.contract)
        self.assertEqual(set(receipt), set(self.contract["conflict_receipt_schema"]["required_fields"]))
        self.assertEqual(receipt["status"], "UNRESOLVED")
        self.assertEqual(receipt["semantic_assessment"], "UNASSESSED")
        self.assertIsNone(receipt["integration_commit"])
        self.assertEqual(receipt["entry_ids"], ["PR:000917", "PR:000918"])
        self.assertIn("G2_BLOCKED_UNRESOLVED_SEMANTIC_CONFLICT",
                      validate_receipt(receipt, self.contract))

    def test_deterministic_conflict_receipts(self):
        event = self.sample()
        first = evaluate_conflicts([event], self.contract)
        second = evaluate_conflicts([event], self.contract)
        self.assertEqual(first, second)
        self.assertFalse(first["candidate_composed"])
        self.assertEqual(len(first["unresolved_conflicts"]), 1)

    def test_stale_head_and_forged_resolved_receipts_do_not_pass(self):
        receipt = unresolved_receipt(self.sample(), self.contract)
        receipt["status"] = "RESOLVED_FOCUSED_VALIDATION_PASSED"
        receipt["resolution_operation"] = "MANUAL_REQUIREMENT_PRESERVING_RESOLUTION"
        blockers = validate_receipt(receipt, self.contract)
        self.assertIn("G2_BLOCKED_CANDIDATE_IDENTITY_MISMATCH", blockers)
        self.assertIn("G2_BLOCKED_FOCUSED_VALIDATION_FAILED", blockers)
        receipt["exact_source_heads"]["PR:000917"] = None
        self.assertIn("G2_BLOCKED_STALE_REFS",
                      validate_receipt(receipt, self.contract))

    def test_authority_conflict_requires_explicit_authorized_reviews(self):
        event = self.sample()
        event["conflict_class"] = "SECURITY_OR_AUTHORITY_CONFLICT"
        receipt = unresolved_receipt(event, self.contract)
        receipt["status"] = "RESOLVED_VALIDATION_PENDING"
        receipt["resolution_operation"] = "MANUAL_REQUIREMENT_PRESERVING_RESOLUTION"
        receipt["integration_commit"] = "c" * 40
        receipt["before_blob_or_tree_identities"] = {"path": "d" * 40}
        receipt["after_blob_or_tree_identities"] = {"path": "e" * 40}
        receipt["preserved_requirement_ids"] = ["REQ1"]
        receipt["preserved_capability_ids"] = ["CAP1"]
        receipt["semantic_assessment"] = "EXACT_MANUAL_REVIEW_REQUIRED"
        receipt["nonoverlapping_behavior_disposition"] = "PRESERVED"
        receipt["frozen_and_canonical_review"] = {"authorized": False}
        receipt["security_and_authority_review"] = {"authorized": False}
        receipt["review_authority"] = "SYNTHETIC_TEST_ONLY"
        self.assertIn("G2_BLOCKED_FROZEN_OR_CANONICAL_AUTHORITY",
                      validate_receipt(receipt, self.contract))

    def test_exact_head_set_and_conflict_identity(self):
        event = self.sample()
        del event["exact_source_heads"]["PR:000918"]
        with self.assertRaisesRegex(ValueError, "HEAD_SET"):
            unresolved_receipt(event, self.contract)
        event = self.sample()
        event["exact_source_heads"]["PR:000918"] = "short"
        with self.assertRaisesRegex(ValueError, "SOURCE_HEAD_INVALID"):
            unresolved_receipt(event, self.contract)

    def test_duplicate_events_and_no_evidence_are_rejected(self):
        event = self.sample()
        with self.assertRaisesRegex(ValueError, "DUPLICATE_MECHANICAL"):
            evaluate_conflicts([event, copy.deepcopy(event)], self.contract)
        event["mechanical_evidence"] = {}
        with self.assertRaisesRegex(ValueError, "EVIDENCE_REQUIRED"):
            unresolved_receipt(event, self.contract)


if __name__ == "__main__":
    unittest.main()
