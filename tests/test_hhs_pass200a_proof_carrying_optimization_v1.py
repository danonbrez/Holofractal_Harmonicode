from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from hhs_backend.runtime import hhs_pass200a_proof_carrying_optimization_v1 as legacy
from hhs_backend.runtime import hhs_pass200a_proof_carrying_optimization_v2 as repaired
from hhs_backend.runtime.hhs_pass200a_proof_carrying_optimization import (
    NONPRODUCTION_CLASSIFICATION,
    PASS200A_OPTIMIZATION_AUTHORITY,
    Pass200AError,
    Pass200AProofCarryingOptimizationAuthority,
)
from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController

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


class Pass200ARepairTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self._old_runtime_output = os.environ.get("HHS_RUNTIME_OUTPUT_DIR")
        self._old_pass200a_root = os.environ.get("HHS_PASS200A_STATE_ROOT")
        os.environ["HHS_RUNTIME_OUTPUT_DIR"] = str(self.root / "runtime")
        os.environ["HHS_PASS200A_STATE_ROOT"] = str(self.root / "default-pass200a")
        self.controller = HHSRuntimeController()
        self.authority = Pass200AProofCarryingOptimizationAuthority(
            state_root=self.root / "pass200a",
            holdouts=TINY_HOLDOUTS,
        )

    def tearDown(self) -> None:
        try:
            self.authority.close()
        finally:
            if self._old_runtime_output is None:
                os.environ.pop("HHS_RUNTIME_OUTPUT_DIR", None)
            else:
                os.environ["HHS_RUNTIME_OUTPUT_DIR"] = self._old_runtime_output
            if self._old_pass200a_root is None:
                os.environ.pop("HHS_PASS200A_STATE_ROOT", None)
            else:
                os.environ["HHS_PASS200A_STATE_ROOT"] = self._old_pass200a_root
            self.temp.cleanup()

    def receipt(self, source: str) -> str:
        tick = self.controller.authorized_tick(source=source)
        return tick["receipt"]["receipt_hash72"]

    def qualify(self) -> dict:
        return self.authority.run_holdouts(
            worker_count=2,
            vm81_receipt_hash72=self.receipt("pass200a.test.holdouts"),
        )

    def shadow(self) -> dict:
        self.qualify()
        return self.authority.execute_all_shadows(
            worker_count=2,
            vm81_receipt_hash72=self.receipt("pass200a.test.shadows"),
            config_payload=SHADOW_CONFIG,
        )

    def test_canonical_singleton_is_upgraded_in_place_not_duplicated(self) -> None:
        self.assertIs(PASS200A_OPTIMIZATION_AUTHORITY, legacy.PASS200A_OPTIMIZATION_AUTHORITY)
        self.assertIs(PASS200A_OPTIMIZATION_AUTHORITY, repaired.PASS200A_LEGACY_SINGLETON)
        self.assertIsInstance(PASS200A_OPTIMIZATION_AUTHORITY, Pass200AProofCarryingOptimizationAuthority)

    def test_arbitrary_72_glyph_receipt_is_rejected_before_mutation(self) -> None:
        with self.assertRaises(ValueError):
            self.authority.run_holdouts(
                worker_count=2,
                vm81_receipt_hash72="7" * 72,
            )
        self.assertEqual(self.authority.list_envelopes(), [])

    def test_verified_vm81_receipt_chain_allows_bounded_holdout_work(self) -> None:
        result = self.qualify()
        self.assertTrue(result["profile_closed"])
        self.assertFalse(result["closed"])
        self.assertFalse(result["production_closed"])
        self.assertEqual(result["classification"], NONPRODUCTION_CLASSIFICATION)
        self.assertEqual(result["independent_envelope_count"], 4)
        self.assertEqual(result["bundle_count"], 4)
        self.assertTrue(result["vm81_receipt_provenance"]["ok"])
        self.assertTrue(all(item["compiler_mode"] == "SHADOW" for item in result["bundles"]))

    def test_custom_four_state_profile_cannot_claim_production_closure(self) -> None:
        result = self.qualify()
        acceptance = result["production_acceptance"]
        self.assertFalse(acceptance["production_profile"])
        self.assertFalse(acceptance["totals_match"])
        status = self.authority.status()
        self.assertFalse(status["closed"])
        self.assertFalse(status["production_closed"])
        self.assertEqual(status["classification"], "HHS_PASS_200A_IN_PROGRESS")

    def test_compiler_shadow_executes_both_lanes_and_returns_reference(self) -> None:
        result = self.shadow()
        self.assertTrue(result["profile_closed"])
        self.assertFalse(result["production_closed"])
        self.assertEqual(result["shadow_match_count"], 4)
        self.assertEqual(result["candidate_execution_count"], 4)
        self.assertEqual(result["reference_return_count"], 4)
        self.assertEqual(result["candidate_activation_count"], 0)
        for item in result["records"]:
            self.assertTrue(item["candidate_lane_executed"])
            self.assertTrue(item["reference_lane_executed"])
            self.assertTrue(item["exact_match"])
            self.assertTrue(item["witness_match"])
            self.assertTrue(item["replay_match"])
            self.assertEqual(item["returned_path"], "REFERENCE")
            self.assertEqual(
                item["reference_semantic_root_hash72"],
                item["candidate_semantic_root_hash72"],
            )

    def test_broken_candidate_lane_cannot_be_hardcoded_to_match(self) -> None:
        self.qualify()
        original = repaired.evaluate_branch_candidate

        def corrupted(arguments):
            result = original(arguments)
            if arguments.get("branch") == "B" and result.get("cell_value_hashes"):
                result = json.loads(json.dumps(result))
                result["cell_value_hashes"][0] = "X" * 72
                result["cell_root_hash72"] = "Y" * 72
                result["address_witness_root_hash72"] = "Z" * 72
                result["equivalence_root_hash72"] = "Q" * 72
            return result

        with mock.patch.object(repaired, "evaluate_branch_candidate", side_effect=corrupted):
            result = self.authority.execute_all_shadows(
                worker_count=2,
                vm81_receipt_hash72=self.receipt("pass200a.test.corrupt-candidate"),
                config_payload=SHADOW_CONFIG,
            )
        self.assertFalse(result["profile_closed"])
        self.assertEqual(result["shadow_match_count"], 0)
        self.assertTrue(all(item["status"] == "MISMATCH" for item in result["records"]))
        self.assertTrue(all(item["returned_path"] == "REFERENCE" for item in result["records"]))
        self.assertEqual(result["candidate_activation_count"], 0)

    def test_persisted_shadow_payload_tamper_is_detected(self) -> None:
        result = self.shadow()
        shadow = result["records"][0]
        row = self.authority._db.execute(
            "SELECT payload_json FROM shadow_runs WHERE shadow_run_id=?",
            (shadow["shadow_run_id"],),
        ).fetchone()
        document = json.loads(row[0])
        document["exact_match"] = False
        self.authority._db.execute(
            "UPDATE shadow_runs SET payload_json=? WHERE shadow_run_id=?",
            (json.dumps(document, sort_keys=True, separators=(",", ":")), shadow["shadow_run_id"]),
        )
        self.authority._db.commit()
        with self.assertRaises(Pass200AError):
            self.authority.verify()

    def test_rehashed_shadow_payload_without_event_binding_cannot_qualify(self) -> None:
        result = self.shadow()
        shadow = result["records"][0]
        row = self.authority._db.execute(
            "SELECT payload_json FROM shadow_runs WHERE shadow_run_id=?",
            (shadow["shadow_run_id"],),
        ).fetchone()
        document = json.loads(row[0])
        document["candidate_semantic_root_hash72"] = "T" * 72
        document["exact_match"] = False
        document["status"] = "MISMATCH"
        identity = {
            key: value
            for key, value in document.items()
            if key not in {"shadow_hash72", "event_hash72"}
        }
        from hhs_backend.runtime.pass197_exact_v1 import hash72
        document["shadow_hash72"] = hash72("pass200a.shadow.run", identity)
        self.authority._db.execute(
            "UPDATE shadow_runs SET status=?,payload_json=? WHERE shadow_run_id=?",
            ("MISMATCH", json.dumps(document, sort_keys=True, separators=(",", ":")), shadow["shadow_run_id"]),
        )
        self.authority._db.commit()
        verification = self.authority.verify()
        self.assertGreaterEqual(verification["legacy_unbound_shadow_run_count"], 1)
        self.assertLess(verification["qualifying_shadow_run_count"], 4)
        self.assertFalse(self.authority.status()["profile_closed"])

    def test_revoked_current_pass198_proof_invalidates_bundle(self) -> None:
        qualification = self.qualify()
        bundle = qualification["bundles"][0]
        receipt = self.receipt("pass200a.test.revoke")
        self.authority.distributed.pass198.revoke_simplification(
            bundle["simplification_id"],
            {"reason": "test revocation"},
            vm81_receipt_hash72=receipt,
        )
        with self.assertRaises(Pass200AError):
            self.authority.get_bundle(bundle["bundle_id"])
        with self.assertRaises(Pass200AError):
            self.authority.list_bundles()

    def test_partial_holdout_state_is_recoverable_in_progress(self) -> None:
        envelope = TINY_HOLDOUTS[0]
        config = self.authority._config(envelope)
        receipt = self.receipt("pass200a.test.partial")
        report = self.authority.distributed.run(
            "pass197.reciprocal_matrix_gate",
            config,
            worker_count=2,
            vm81_receipt_hash72=receipt,
            resume=True,
            full_replay=True,
        )
        self.authority._validate_closed_report(report)
        tree = self.authority.distributed.pass198.parameter_tree(
            "pass197.reciprocal_matrix_gate", config
        )
        self.authority._record_envelope(envelope, tree, report)
        status = self.authority.status()
        self.assertFalse(status["closed"])
        self.assertEqual(status["classification"], "HHS_PASS_200A_IN_PROGRESS")
        self.assertEqual(status["independent_envelope_count"], 1)

    def test_restart_revalidates_bound_shadows_and_event_chain(self) -> None:
        self.shadow()
        before = self.authority.status()
        self.authority.close()
        self.authority = Pass200AProofCarryingOptimizationAuthority(
            state_root=self.root / "pass200a",
            holdouts=TINY_HOLDOUTS,
        )
        after = self.authority.status()
        self.assertTrue(after["event_chain"]["ok"])
        self.assertEqual(after["event_chain"]["tip_hash72"], before["event_chain"]["tip_hash72"])
        self.assertEqual(after["qualifying_shadow_run_count"], 4)
        self.assertEqual(after["candidate_activation_count"], 0)


if __name__ == "__main__":
    unittest.main()
