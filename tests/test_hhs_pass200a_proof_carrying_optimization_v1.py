from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from hhs_backend.runtime.hhs_pass200a_proof_carrying_optimization_v1 import (
    CONTRACT,
    Pass200AError,
    Pass200AProofCarryingOptimizationAuthority,
)

TINY_HOLDOUTS = (
    {
        "envelope_id": "test.holdout.one",
        "x_values": ["1"],
        "y_values": ["1"],
        "xy_symbol_values": [0],
    },
    {
        "envelope_id": "test.holdout.two",
        "x_values": ["2"],
        "y_values": ["1"],
        "xy_symbol_values": [1],
    },
    {
        "envelope_id": "test.holdout.three",
        "x_values": ["1/2"],
        "y_values": ["3"],
        "xy_symbol_values": [-1],
    },
    {
        "envelope_id": "test.holdout.four",
        "x_values": ["-1"],
        "y_values": ["2"],
        "xy_symbol_values": [2],
    },
)

SHADOW_CONFIG = {
    "x_values": ["3/2"],
    "y_values": ["5/3"],
    "xy_symbol_values": [-3],
}


class Pass200AProofCarryingOptimizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "pass200a"
        self.authority = Pass200AProofCarryingOptimizationAuthority(
            state_root=self.root,
            holdouts=TINY_HOLDOUTS,
        )

    def tearDown(self) -> None:
        try:
            self.authority.close()
        finally:
            self.temp.cleanup()

    def qualify(self) -> dict:
        return self.authority.run_holdouts(
            worker_count=2,
            vm81_receipt_hash72="7" * 72,
        )

    def shadow(self) -> dict:
        self.qualify()
        return self.authority.execute_all_shadows(
            worker_count=2,
            vm81_receipt_hash72="8" * 72,
            config_payload=SHADOW_CONFIG,
        )

    def test_four_independent_envelopes_create_four_compiler_candidates(self) -> None:
        result = self.qualify()
        self.assertTrue(result["closed"])
        self.assertEqual(result["contract"], CONTRACT)
        self.assertEqual(result["independent_envelope_count"], 4)
        self.assertEqual(result["bundle_count"], 4)
        self.assertEqual(result["compiler_candidate_count"], 4)
        self.assertEqual(result["automatic_promotion_count"], 0)
        self.assertTrue(result["reference_result_remains_authoritative"])
        self.assertEqual(len({item["tree_hash72"] for item in result["envelopes"]}), 4)
        self.assertEqual(len({item["config_hash72"] for item in result["envelopes"]}), 4)
        self.assertEqual(len({item["report_hash72"] for item in result["envelopes"]}), 4)
        self.assertEqual(len({item["state_root_hash72"] for item in result["envelopes"]}), 4)
        self.assertTrue(all(item["status"] == "COMPILER_CANDIDATE" for item in result["bundles"]))
        self.assertTrue(all(item["compiler_mode"] == "SHADOW" for item in result["bundles"]))

    def test_receipt_only_or_duplicate_envelope_does_not_count_as_independent(self) -> None:
        result = self.qualify()
        duplicate = json.loads(json.dumps(result["envelopes"][0]))
        duplicate["envelope_id"] = "test.holdout.duplicate"
        with self.assertRaises(Pass200AError):
            self.authority._assert_independence([*result["envelopes"][:3], duplicate])

    def test_negative_mutations_are_executed_for_every_holdout(self) -> None:
        result = self.qualify()
        mutations = [
            mutation
            for envelope in result["envelopes"]
            for mutation in envelope["negative_mutations"]
        ]
        self.assertEqual(len(mutations), 24)
        self.assertTrue(all(item["detected"] for item in mutations))
        self.assertTrue(all(item["mutation_grants_authority"] is False for item in mutations))

    def test_compiler_shadow_plan_has_reference_and_candidate_lanes(self) -> None:
        result = self.qualify()
        bundle = result["bundles"][0]
        plan = self.authority.compile_shadow_plan(
            bundle["bundle_id"],
            {"x_values": ["3/2"], "y_values": ["5/3"], "xy_symbol_values": [-3]},
        )
        self.assertEqual(plan["vmir"]["mode"], "SHADOW")
        self.assertEqual(plan["vmir"]["reference_lane"], "AUTHORITATIVE_RETURN")
        self.assertEqual(plan["vmir"]["candidate_lane"], "NONAUTHORITATIVE_COMPARE_ONLY")
        self.assertFalse(plan["vmir"]["candidate_may_commit"])
        self.assertFalse(plan["vmir"]["candidate_may_activate"])
        self.assertEqual(plan["vmir"]["rollback_target"], "REFERENCE_PATH")
        self.assertEqual(len(plan["program_hash72"]), 72)

    def test_all_shadow_executions_match_and_return_reference(self) -> None:
        result = self.shadow()
        self.assertTrue(result["closed"])
        self.assertEqual(result["bundle_count"], 4)
        self.assertEqual(result["shadow_match_count"], 4)
        self.assertEqual(result["reference_return_count"], 4)
        self.assertEqual(result["candidate_activation_count"], 0)
        self.assertTrue(all(item["exact_match"] for item in result["records"]))
        self.assertTrue(all(item["witness_match"] for item in result["records"]))
        self.assertTrue(all(item["replay_match"] for item in result["records"]))
        self.assertTrue(all(item["returned_path"] == "REFERENCE" for item in result["records"]))

    def test_bundle_tampering_is_rejected(self) -> None:
        result = self.qualify()
        bundle = result["bundles"][0]
        row = self.authority._db.execute(
            "SELECT payload_json FROM bundles WHERE bundle_id=?",
            (bundle["bundle_id"],),
        ).fetchone()
        document = json.loads(row[0])
        document["compiler_mode"] = "ACTIVE"
        self.authority._db.execute(
            "UPDATE bundles SET payload_json=? WHERE bundle_id=?",
            (json.dumps(document, sort_keys=True, separators=(",", ":")), bundle["bundle_id"]),
        )
        self.authority._db.commit()
        with self.assertRaises(Pass200AError):
            self.authority.list_bundles()

    def test_restart_preserves_envelopes_bundles_shadows_and_event_chain(self) -> None:
        self.shadow()
        before = self.authority.status()
        self.authority.close()
        self.authority = Pass200AProofCarryingOptimizationAuthority(
            state_root=self.root,
            holdouts=TINY_HOLDOUTS,
        )
        after = self.authority.status()
        self.assertTrue(after["closed"])
        self.assertEqual(after["independent_envelope_count"], 4)
        self.assertEqual(after["bundle_count"], 4)
        self.assertEqual(after["shadow_match_count"], 4)
        self.assertEqual(after["candidate_activation_count"], 0)
        self.assertEqual(after["event_chain"]["tip_hash72"], before["event_chain"]["tip_hash72"])

    def test_pass200a_never_enables_canary_active_or_frozen_modes(self) -> None:
        self.shadow()
        status = self.authority.status()
        self.assertFalse(status["canary_enabled"])
        self.assertFalse(status["active_enabled"])
        self.assertFalse(status["frozen_constraint_enabled"])
        self.assertFalse(status["compiler_auto_activation"])
        self.assertFalse(status["runtime_auto_admission"])
        self.assertTrue(status["reference_result_remains_authoritative"])
        self.assertFalse(status["candidate_execution_is_authority"])


if __name__ == "__main__":
    unittest.main()
