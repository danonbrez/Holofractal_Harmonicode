#!/usr/bin/env python3
"""Dependency-scoped validation for the Pass 216 contract alignment."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
PASS215_CONTRACT = ROOT / "contracts/pass215/PASS_215_ITERATION_20_CONTRACT.json"
PASS216_CONTRACT = ROOT / "contracts/pass216/PASS_216_CONTRACT.json"
PASS216_ADDENDUM = (
    ROOT / "contracts/pass216/PASS_216_DETERMINISM_INHERITANCE_ADDENDUM.json"
)

FINAL_HEAD = "b85ea7c340976a20a78f9c7d8d89a688a1b4f8fc"
FINAL_TREE = "17127e80a3f4852aeaedd1b807971fb4b4fba229"
MAIN_MERGE = "cc7a0d67d7d9e4bd1e800f62d5ef577cb4ab1086"
ALIGNED_MAIN = "07fd48d7919f2406585ab682ca901c945c5f99d0"
ARTIFACT_SHA256 = "9e71ff3f48cd4da24c34854f8eadfa57f26d7c6ef5bddd1026c89e2ace63bf55"
PASS217_HEAD = "947be39fd67700f307ff80d96c3a10c3acaa29cc"
PASS217_TREE = "f8d0af49e3574ea77657a79507601ae96f75918c"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.run(
        ("git", *args),
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_float(item) for item in value)
    return False


class Pass216ContractAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pass215 = load_json(PASS215_CONTRACT)
        cls.contract = load_json(PASS216_CONTRACT)
        cls.addendum = load_json(PASS216_ADDENDUM)

    def test_contract_layer_is_complete_without_runtime_overclaim(self) -> None:
        self.assertEqual(self.contract["schema"], "HHS_PASS_216_CONTRACT_V3")
        self.assertEqual(
            self.contract["status"], "CONTRACT_COMPLETE_PARENT_TERMINAL_ALIGNED"
        )
        boundary = self.contract["completion_boundary"]
        self.assertTrue(boundary["contract_layer_complete"])
        self.assertTrue(boundary["parent_alignment_complete"])
        self.assertFalse(boundary["runtime_optimization_implementation_claimed"])
        self.assertFalse(
            boundary["pass216_runtime_implementation_required_before_pass217_continuation"]
        )
        self.assertTrue(boundary["pass217_continuation_requires_this_contract_on_main"])

    def test_pass215_exact_head_and_main_lineage_are_bound(self) -> None:
        parent = self.contract["parent_binding"]
        self.assertEqual(parent["final_closure_head"], FINAL_HEAD)
        self.assertEqual(parent["final_closure_tree"], FINAL_TREE)
        self.assertEqual(parent["main_merge_commit"], MAIN_MERGE)
        self.assertEqual(parent["main_head_at_alignment"], ALIGNED_MAIN)
        self.assertEqual(git("show", "-s", "--format=%T", FINAL_HEAD), FINAL_TREE)
        for ancestor in (FINAL_HEAD, MAIN_MERGE, ALIGNED_MAIN):
            subprocess.run(
                ("git", "merge-base", "--is-ancestor", ancestor, "HEAD"),
                cwd=ROOT,
                check=True,
            )

    def test_exact_head_workflow_and_artifact_are_frozen(self) -> None:
        parent = self.contract["parent_binding"]
        self.assertEqual(parent["final_closure_run"], 31325831364)
        self.assertEqual(parent["final_closure_job"], 93275935886)
        self.assertEqual(parent["final_closure_cumulative_controls"], 240)
        self.assertEqual(parent["final_closure_artifact_id"], 9041918679)
        self.assertEqual(parent["final_closure_artifact_bytes"], 260003642)
        self.assertEqual(parent["final_closure_artifact_sha256"], ARTIFACT_SHA256)
        self.assertEqual(
            parent["binding_status"],
            "SUCCESSFUL_EXACT_HEAD_REPLAY_BOUND_AND_MAIN_LINEAGE_VERIFIED",
        )

    def test_frozen_baseline_matches_pass215_source_evidence(self) -> None:
        source = self.pass215["source_execution"]
        baseline = self.contract["pass215_terminal_frozen_baseline"]
        keys = (
            "selected_token_ids",
            "termination_reason",
            "earlier_checkpoint_canonical_bytes",
            "later_checkpoint_canonical_bytes",
            "earlier_checkpoint_root_hash216",
            "later_checkpoint_root_hash216",
            "earlier_standalone_compressed_blob_bytes",
            "later_standalone_compressed_blob_bytes",
            "reused_compressed_blob_bytes",
            "incremental_later_compressed_blob_bytes",
            "separate_stores_compressed_blob_bytes",
            "shared_store_compressed_blob_bytes",
            "shared_store_savings_bytes",
            "reused_unique_chunk_count",
            "incremental_new_unique_chunk_count",
            "shared_store_unique_chunk_count",
        )
        for key in keys:
            self.assertEqual(baseline[key], source[key], key)
        self.assertEqual(
            baseline["incremental_later_compressed_blob_bytes"]
            + baseline["reused_compressed_blob_bytes"],
            baseline["later_standalone_compressed_blob_bytes"],
        )
        self.assertEqual(
            baseline["separate_stores_compressed_blob_bytes"]
            - baseline["shared_store_compressed_blob_bytes"],
            baseline["shared_store_savings_bytes"],
        )

    def test_historical_pass215_reservation_is_superseded_not_rewritten(self) -> None:
        transition = self.pass215["downstream_transition"]
        authorization = self.contract["authorization"]
        self.assertEqual(transition["pass216_status"], "RESERVED_NUMBER_NO_PASS")
        self.assertEqual(authorization["supersession_scope"], "DOWNSTREAM_PASS_NUMBERING_ONLY")
        self.assertFalse(authorization["pass215_semantics_modified"])
        self.assertFalse(authorization["pass215_frozen_identities_modified"])

    def test_pass217_candidate_is_reused_but_not_promoted_by_alignment(self) -> None:
        downstream = self.contract["downstream_alignment"]
        self.assertEqual(downstream["pass217_candidate_head_at_alignment"], PASS217_HEAD)
        self.assertEqual(downstream["pass217_candidate_tree_at_alignment"], PASS217_TREE)
        self.assertEqual(
            downstream["pass217_candidate_validation_status"],
            "SUCCESSFUL_NON_PROMOTIONAL_REUSE_INPUT",
        )
        self.assertTrue(
            downstream["reuse_existing_pass217_iteration1_3_code_and_candidate_surfaces"]
        )
        self.assertFalse(downstream["redevelop_unchanged_pass217_iteration1_3_surfaces"])
        self.assertFalse(
            downstream["promote_stale_predecessor_bindings_without_reconciliation"]
        )
        self.assertFalse(downstream["repeat_pass215_terminal_workflow_by_default"])
        self.assertFalse(downstream["repeat_pass216_contract_development"])
        self.assertFalse(downstream["repeat_unchanged_pass217_preparation_in_pass219"])

    def test_addendum_carries_scoped_truth_and_successor_inheritance(self) -> None:
        self.assertEqual(
            self.addendum["schema"],
            "HHS_PASS_216_DETERMINISM_INHERITANCE_ADDENDUM_V3",
        )
        gate = self.addendum["sha256_deterministic_truth_gate"]
        successor = self.addendum["successor_inheritance"]
        self.assertEqual(gate["default_state"], "CLOSED")
        self.assertFalse(gate["full_system_reproof_required_by_default"])
        self.assertTrue(successor["pass216_contract_alignment_is_complete"])
        self.assertTrue(
            successor["pass216_runtime_optimization_implementation_is_not_claimed"]
        )
        self.assertTrue(successor["pass217_must_reuse_unchanged_validated_iteration1_through_3_work"])
        self.assertTrue(successor["pass219_must_inherit_unchanged_pass215_pass216_and_pass217_authority"])
        self.assertFalse(successor["later_pass_number_alone_reopens_prior_truth_gates"])

    def test_alignment_json_has_no_float_authority(self) -> None:
        self.assertFalse(contains_float(self.contract))
        self.assertFalse(contains_float(self.addendum))


if __name__ == "__main__":
    unittest.main(verbosity=2)
