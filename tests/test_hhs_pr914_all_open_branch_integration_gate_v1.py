"""Source-level release gate for cumulative PR #914 branch reconciliation."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "contracts/architecture/HHS_PR914_CUMULATIVE_OPEN_BRANCH_INTEGRATION_GATE_V1.json"


class TestAllOpenBranchReconciliationGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(C.read_text(encoding="utf-8"))
        inventory = ROOT / cls.contract["snapshot"]
        cls.inventory = json.loads(inventory.read_text(encoding="utf-8"))

    def test_inventory_is_distinct_and_complete_for_snapshot(self):
        i = self.inventory
        self.assertEqual(i["schema"], "HHS_PR914_OPEN_BRANCH_CONSOLIDATION_INVENTORY_V1")
        self.assertEqual(len(i["entries"]), i["open_pull_request_count"])
        self.assertEqual(len({x["number"] for x in i["entries"]}), len(i["entries"]))
        self.assertIn(914, {x["number"] for x in i["entries"]})
        self.assertEqual(i["open_pull_request_count"], self.contract["observed_open_pr_count"])
        self.assertTrue(i["requires_refresh_before_any_merge"])

    def test_no_unsupported_merge_or_identity_claim(self):
        c = self.contract
        self.assertEqual(c["status"], "INTEGRATION_REQUIRED_NOT_COMPLETED")
        self.assertEqual(c["mergability"], "BLOCKED_UNTIL_ALL_RELEASE_GATES_PASS")
        self.assertFalse(c["automatic_mass_merge_authorized"])
        self.assertFalse(c["snapshot_is_promotion_evidence"])
        self.assertEqual(c["progress"]["main_merge"], "NOT_PERFORMED")
        self.assertEqual(c["progress"]["production_deploy"], "NOT_PERFORMED")
        self.assertFalse(self.inventory["integrated"])
        self.assertFalse(self.inventory["head_refs_verified"])

    def test_every_open_pr_requires_nonloss_disposition(self):
        c = self.contract
        self.assertEqual(list(c["release_gates"]), [f"G{x}" for x in range(8)])
        self.assertIn("UNASSESSED", c["prohibited_terminal_dispositions"])
        self.assertIn("BLOCKED_SECURITY_OR_AUTHORITY", c["required_dispositions"])
        self.assertIn("integration_commit", c["entry_receipt_fields"])
        self.assertTrue(all(x["resolution"] == "UNASSESSED" for x in self.inventory["entries"]))
        self.assertTrue(all(x["head_sha"] is None for x in self.inventory["entries"]))


if __name__ == "__main__":
    unittest.main()
