from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from hhs_backend.runtime.hhs_pass200b_governed_canary_admission_v1 import (
    Pass200BError,
    Pass200BGovernedCanaryAuthority,
)
from hhs_backend.runtime.pass197_exact_v1 import hash72


class FakePass200A:
    def __init__(self) -> None:
        self.bundle = {
            "bundle_id": "bundle-001",
            "bundle_hash72": "B" * 72,
            "proof_hash72": "P" * 72,
            "status": "COMPILER_CANDIDATE",
            "compiler_mode": "SHADOW",
        }
        self.shadow = {
            "bundle_id": "bundle-001",
            "status": "MATCH",
            "candidate_activated": False,
            "reference_semantic_root_hash72": "S" * 72,
            "candidate_semantic_root_hash72": "S" * 72,
            "reference_replay_root_hash72": "R" * 72,
            "candidate_replay_root_hash72": "R" * 72,
        }

    def status(self):
        return {"closed": True, "candidate_activation_count": 0}

    def get_bundle(self, bundle_id: str):
        if bundle_id != self.bundle["bundle_id"]:
            raise RuntimeError("unknown bundle")
        return dict(self.bundle)

    def list_shadow_runs(self):
        return [dict(self.shadow)]


class Pass200BGovernedCanaryTests(unittest.TestCase):
    NOW = 10_000

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pass200a = FakePass200A()
        self.authority = Pass200BGovernedCanaryAuthority(
            state_root=self.root,
            pass200a=self.pass200a,
        )

    def tearDown(self) -> None:
        self.authority.close()
        self.temp.cleanup()

    def approvals(self, *, expires_at_ns: int | None = None, frontier_hash72: str | None = None):
        current = self.authority.current_frontier()
        frontier_hash = frontier_hash72 or current["frontier_hash72"]
        expiry = expires_at_ns if expires_at_ns is not None else self.NOW + 10_000
        return [
            self.authority.build_approval(
                principal_id="compiler-authority",
                capability="COMPILER_PROMOTION_APPROVE",
                receipt_hash72="C" * 72,
                bundle_hash72=self.pass200a.bundle["bundle_hash72"],
                expected_frontier_hash72=frontier_hash,
                expires_at_ns=expiry,
            ),
            self.authority.build_approval(
                principal_id="runtime-authority",
                capability="RUNTIME_PROMOTION_APPROVE",
                receipt_hash72="D" * 72,
                bundle_hash72=self.pass200a.bundle["bundle_hash72"],
                expected_frontier_hash72=frontier_hash,
                expires_at_ns=expiry,
            ),
        ]

    def admit(self, *, limit: int = 4, numerator: int = 1, denominator: int = 2):
        return self.authority.admit_canary(
            self.pass200a.bundle["bundle_id"],
            invocation_limit=limit,
            canary_numerator=numerator,
            canary_denominator=denominator,
            approvals=self.approvals(),
            vm81_activation_receipt_hash72="A" * 72,
            expires_at_ns=self.NOW + 20_000,
            now_ns=self.NOW,
        )

    def exact_invoke(self, frontier_id: str, ordinal: int):
        result = {"value": "exact", "ordinal": ordinal}
        return self.authority.execute_canary(
            frontier_id,
            reference_result=result,
            candidate_result=result,
            reference_witness_hash72="W" * 72,
            candidate_witness_hash72="W" * 72,
            reference_replay_hash72="R" * 72,
            candidate_replay_hash72="R" * 72,
            invocation_receipt_hash72=str(ordinal % 10) * 72,
            now_ns=self.NOW + ordinal + 1,
        )

    def test_dual_approval_and_singleton_activation_commit(self) -> None:
        frontier = self.admit()
        self.assertEqual(frontier["mode"], "CANARY")
        self.assertEqual(frontier["singleton_activation_commit_count"], 1)
        self.assertEqual(len(frontier["approvals"]), 2)
        self.assertFalse(frontier["candidate_self_authorization"])

    def test_duplicate_principal_and_expired_approval_are_rejected(self) -> None:
        approvals = self.approvals()
        approvals[1]["principal_id"] = approvals[0]["principal_id"]
        body = {key: value for key, value in approvals[1].items() if key != "approval_hash72"}
        approvals[1]["approval_hash72"] = hash72("pass200b.approval", body)
        with self.assertRaises(Pass200BError):
            self.authority.admit_canary(
                "bundle-001",
                invocation_limit=4,
                canary_numerator=1,
                canary_denominator=2,
                approvals=approvals,
                vm81_activation_receipt_hash72="A" * 72,
                expires_at_ns=self.NOW + 20_000,
                now_ns=self.NOW,
            )
        with self.assertRaises(Pass200BError):
            self.authority.admit_canary(
                "bundle-001",
                invocation_limit=4,
                canary_numerator=1,
                canary_denominator=2,
                approvals=self.approvals(expires_at_ns=self.NOW),
                vm81_activation_receipt_hash72="A" * 72,
                expires_at_ns=self.NOW + 20_000,
                now_ns=self.NOW,
            )

    def test_bounded_canary_returns_and_exhaustion_restore_reference(self) -> None:
        frontier = self.admit(limit=4, numerator=1, denominator=2)
        paths = [self.exact_invoke(frontier["frontier_id"], index)["returned_path"] for index in range(4)]
        self.assertEqual(paths, ["CANDIDATE", "REFERENCE", "CANDIDATE", "REFERENCE"])
        current = self.authority.current_frontier()
        self.assertEqual(current["mode"], "EXHAUSTED")
        status = self.authority.status()
        self.assertEqual(status["total_invocations"], 4)
        self.assertEqual(status["candidate_returns"], 2)
        self.assertEqual(status["reference_returns"], 2)
        self.assertFalse(status["active_mode_enabled"])
        self.assertFalse(status["frozen_constraint_enabled"])

    def test_exact_mismatch_rolls_back_before_candidate_return(self) -> None:
        frontier = self.admit()
        result = self.authority.execute_canary(
            frontier["frontier_id"],
            reference_result={"value": 1},
            candidate_result={"value": 2},
            reference_witness_hash72="W" * 72,
            candidate_witness_hash72="X" * 72,
            reference_replay_hash72="R" * 72,
            candidate_replay_hash72="Q" * 72,
            invocation_receipt_hash72="I" * 72,
            now_ns=self.NOW + 1,
        )
        self.assertEqual(result["status"], "ROLLED_BACK")
        self.assertEqual(result["returned_path"], "REFERENCE")
        self.assertEqual(self.authority.current_frontier()["mode"], "ROLLED_BACK")

    def test_manual_rollback_and_stale_frontier_rejection(self) -> None:
        frontier = self.admit()
        restored = self.authority.rollback(
            frontier["frontier_id"],
            reason="OPERATOR_ABORT",
            vm81_rollback_receipt_hash72="Z" * 72,
            now_ns=self.NOW + 1,
        )
        self.assertEqual(restored["mode"], "ROLLED_BACK")
        with self.assertRaises(Pass200BError):
            self.exact_invoke(frontier["frontier_id"], 0)

    def test_restart_preserves_frontier_counters_and_event_chain(self) -> None:
        frontier = self.admit(limit=3, numerator=1, denominator=3)
        self.exact_invoke(frontier["frontier_id"], 0)
        tip = self.authority.verify_event_chain()["tip_hash72"]
        self.authority.close()
        self.authority = Pass200BGovernedCanaryAuthority(
            state_root=self.root,
            pass200a=self.pass200a,
        )
        current = self.authority.current_frontier()
        self.assertEqual(current["frontier_id"], frontier["frontier_id"])
        self.assertEqual(current["counter"]["invocations_used"], 1)
        self.assertEqual(self.authority.verify_event_chain()["tip_hash72"], tip)

    def test_persisted_frontier_tampering_is_rejected(self) -> None:
        frontier = self.admit()
        row = self.authority._db.execute(
            "SELECT payload_json FROM frontiers WHERE frontier_id=?",
            (frontier["frontier_id"],),
        ).fetchone()
        document = json.loads(row[0])
        document["invocation_limit"] = 63
        self.authority._db.execute(
            "UPDATE frontiers SET payload_json=? WHERE frontier_id=?",
            (json.dumps(document, sort_keys=True, separators=(",", ":")), frontier["frontier_id"]),
        )
        self.authority._db.commit()
        with self.assertRaises(Pass200BError):
            self.authority.current_frontier()

    def test_verified_probe_uses_pass200a_shadow_observation(self) -> None:
        frontier = self.admit(limit=1, numerator=1, denominator=1)
        result = self.authority.execute_verified_probe(
            frontier["frontier_id"],
            invocation_receipt_hash72="V" * 72,
            now_ns=self.NOW + 1,
        )
        self.assertEqual(result["status"], "MATCH")
        self.assertEqual(result["returned_path"], "CANDIDATE")
        self.assertEqual(self.authority.current_frontier()["mode"], "EXHAUSTED")


if __name__ == "__main__":
    unittest.main()
