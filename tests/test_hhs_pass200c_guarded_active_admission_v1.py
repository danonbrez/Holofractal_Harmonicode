from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from hhs_backend.runtime.hhs_pass200c_guarded_active_admission_v1 import (
    Pass200CError,
    Pass200CGuardedActiveAuthority,
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

    def get_bundle(self, bundle_id: str):
        if bundle_id != self.bundle["bundle_id"]:
            raise RuntimeError("unknown bundle")
        return dict(self.bundle)

    def list_shadow_runs(self):
        return [dict(self.shadow)]


class FakePass200B:
    def __init__(self, *, successful_canaries: int = 2, include_rollback: bool = False) -> None:
        self.pass200a = FakePass200A()
        self._frontiers = [
            {
                "frontier_id": "genesis",
                "frontier_hash72": "G" * 72,
                "mode": "REFERENCE",
                "bundle_id": None,
            }
        ]
        self._invocations = []
        for canary_index in range(successful_canaries):
            frontier_id = f"canary-{canary_index}"
            ratio_denominator = 4 if canary_index == 0 else 2
            canary = {
                "frontier_id": frontier_id,
                "frontier_hash72": hash72("test.canary.frontier", canary_index),
                "mode": "CANARY",
                "bundle_id": "bundle-001",
                "invocation_limit": 8,
                "canary_numerator": 1,
                "canary_denominator": ratio_denominator,
                "vm81_activation_receipt_hash72": str(canary_index + 1) * 72,
            }
            exhausted = {
                "frontier_id": f"exhausted-{canary_index}",
                "frontier_hash72": hash72("test.canary.exhausted", canary_index),
                "predecessor_frontier_id": frontier_id,
                "mode": "EXHAUSTED",
                "bundle_id": None,
            }
            self._frontiers.extend([canary, exhausted])
            for ordinal in range(8):
                returned_path = (
                    "CANDIDATE"
                    if ordinal % ratio_denominator < 1
                    else "REFERENCE"
                )
                body = {
                    "frontier_id": frontier_id,
                    "ordinal": ordinal,
                    "returned_path": returned_path,
                    "exact_match": True,
                    "witness_match": True,
                    "replay_match": True,
                }
                self._invocations.append(
                    {**body, "invocation_hash72": hash72("test.canary.invocation", body)}
                )
        if include_rollback:
            self._frontiers.append(
                {
                    "frontier_id": "rolled-back",
                    "frontier_hash72": "X" * 72,
                    "mode": "ROLLED_BACK",
                    "rollback_of_bundle_id": "bundle-001",
                    "predecessor_frontier_id": "canary-1",
                }
            )

    def verify(self):
        return {
            "ok": True,
            "event_chain": {"ok": True, "tip_hash72": "T" * 72},
        }

    def list_frontiers(self):
        return [dict(item) for item in self._frontiers]

    def list_invocations(self, frontier_id=None):
        records = self._invocations
        if frontier_id is not None:
            records = [item for item in records if item["frontier_id"] == frontier_id]
        return [dict(item) for item in records]


class Pass200CGuardedActiveTests(unittest.TestCase):
    NOW = 20_000

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pass200b = FakePass200B()
        self.authority = Pass200CGuardedActiveAuthority(
            state_root=self.root,
            pass200b=self.pass200b,
        )

    def tearDown(self) -> None:
        self.authority.close()
        self.temp.cleanup()

    def approvals(self, evidence, *, expires_at_ns=None, frontier_hash72=None):
        current = self.authority.current_frontier()
        frontier_hash = frontier_hash72 or current["frontier_hash72"]
        expiry = expires_at_ns if expires_at_ns is not None else self.NOW + 100_000
        specs = [
            ("compiler-authority", "COMPILER_ACTIVE_APPROVE", "C" * 72),
            ("runtime-authority", "RUNTIME_ACTIVE_APPROVE", "D" * 72),
            ("operations-authority", "OPERATIONS_ACTIVE_APPROVE", "O" * 72),
        ]
        return [
            self.authority.build_approval(
                principal_id=principal,
                capability=capability,
                receipt_hash72=receipt,
                bundle_hash72="B" * 72,
                evidence_hash72=evidence["evidence_hash72"],
                expected_frontier_hash72=frontier_hash,
                expires_at_ns=expiry,
            )
            for principal, capability, receipt in specs
        ]

    def admit(self, *, limit=4):
        evidence = self.authority.aggregate_canary_evidence("bundle-001")
        return self.authority.admit_active(
            "bundle-001",
            lease_invocation_limit=limit,
            approvals=self.approvals(evidence),
            vm81_activation_receipt_hash72="A" * 72,
            expires_at_ns=self.NOW + 200_000,
            now_ns=self.NOW,
        )

    def exact_invoke(self, frontier_id: str, ordinal: int):
        result = {"value": "exact", "ordinal": ordinal}
        return self.authority.execute_active(
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

    def test_canary_evidence_requires_two_successes_and_no_rollback(self) -> None:
        insufficient = Pass200CGuardedActiveAuthority(
            state_root=self.root / "insufficient",
            pass200b=FakePass200B(successful_canaries=1),
        )
        try:
            with self.assertRaises(Pass200CError):
                insufficient.aggregate_canary_evidence("bundle-001")
        finally:
            insufficient.close()
        rolled_back = Pass200CGuardedActiveAuthority(
            state_root=self.root / "rollback",
            pass200b=FakePass200B(include_rollback=True),
        )
        try:
            with self.assertRaises(Pass200CError):
                rolled_back.aggregate_canary_evidence("bundle-001")
        finally:
            rolled_back.close()

    def test_evidence_aggregates_independent_canary_coverage(self) -> None:
        evidence = self.authority.aggregate_canary_evidence("bundle-001")
        self.assertEqual(evidence["successful_canary_count"], 2)
        self.assertEqual(evidence["total_canary_invocations"], 16)
        self.assertEqual(evidence["total_candidate_returns"], 6)
        self.assertEqual(evidence["total_reference_returns"], 10)
        self.assertTrue(evidence["guard_every_active_invocation"])

    def test_three_distinct_approvals_and_singleton_activation(self) -> None:
        frontier = self.admit()
        self.assertEqual(frontier["mode"], "ACTIVE_GUARDED")
        self.assertEqual(len(frontier["approvals"]), 3)
        self.assertEqual(frontier["singleton_activation_commit_count"], 1)
        self.assertFalse(frontier["candidate_self_authorization"])

    def test_duplicate_principal_and_expired_approval_are_rejected(self) -> None:
        evidence = self.authority.aggregate_canary_evidence("bundle-001")
        approvals = self.approvals(evidence)
        approvals[2]["principal_id"] = approvals[0]["principal_id"]
        body = {key: value for key, value in approvals[2].items() if key != "approval_hash72"}
        approvals[2]["approval_hash72"] = hash72("pass200c.approval", body)
        with self.assertRaises(Pass200CError):
            self.authority.admit_active(
                "bundle-001",
                lease_invocation_limit=4,
                approvals=approvals,
                vm81_activation_receipt_hash72="A" * 72,
                expires_at_ns=self.NOW + 100_000,
                now_ns=self.NOW,
            )
        with self.assertRaises(Pass200CError):
            self.authority.admit_active(
                "bundle-001",
                lease_invocation_limit=4,
                approvals=self.approvals(evidence, expires_at_ns=self.NOW),
                vm81_activation_receipt_hash72="A" * 72,
                expires_at_ns=self.NOW + 100_000,
                now_ns=self.NOW,
            )

    def test_exact_active_returns_candidate_and_exhausts_lease(self) -> None:
        frontier = self.admit(limit=4)
        paths = [self.exact_invoke(frontier["frontier_id"], index)["returned_path"] for index in range(4)]
        self.assertEqual(paths, ["CANDIDATE"] * 4)
        self.assertEqual(self.authority.current_frontier()["mode"], "LEASE_EXHAUSTED")
        status = self.authority.status()
        self.assertEqual(status["total_invocations"], 4)
        self.assertEqual(status["candidate_returns"], 4)
        self.assertEqual(status["reference_returns"], 0)
        self.assertFalse(status["frozen_constraint_enabled"])

    def test_exact_guard_mismatch_returns_reference_and_rolls_back(self) -> None:
        frontier = self.admit()
        result = self.authority.execute_active(
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

    def test_expiry_restores_reference_before_candidate_return(self) -> None:
        evidence = self.authority.aggregate_canary_evidence("bundle-001")
        frontier = self.authority.admit_active(
            "bundle-001",
            lease_invocation_limit=4,
            approvals=self.approvals(evidence),
            vm81_activation_receipt_hash72="A" * 72,
            expires_at_ns=self.NOW + 10,
            now_ns=self.NOW,
        )
        result = self.authority.execute_active(
            frontier["frontier_id"],
            reference_result={"value": 1},
            candidate_result={"value": 1},
            reference_witness_hash72="W" * 72,
            candidate_witness_hash72="W" * 72,
            reference_replay_hash72="R" * 72,
            candidate_replay_hash72="R" * 72,
            invocation_receipt_hash72="I" * 72,
            now_ns=self.NOW + 10,
        )
        self.assertEqual(result["returned_path"], "REFERENCE")
        self.assertEqual(result["reason"], "ACTIVE_LEASE_EXPIRED")

    def test_restart_preserves_active_counter_and_event_chain(self) -> None:
        frontier = self.admit(limit=3)
        self.exact_invoke(frontier["frontier_id"], 0)
        tip = self.authority.verify_event_chain()["tip_hash72"]
        self.authority.close()
        self.authority = Pass200CGuardedActiveAuthority(
            state_root=self.root,
            pass200b=self.pass200b,
        )
        current = self.authority.current_frontier()
        self.assertEqual(current["frontier_id"], frontier["frontier_id"])
        self.assertEqual(current["counter"]["invocations_used"], 1)
        self.assertEqual(self.authority.verify_event_chain()["tip_hash72"], tip)

    def test_frontier_tampering_is_rejected(self) -> None:
        frontier = self.admit()
        row = self.authority._db.execute(
            "SELECT payload_json FROM frontiers WHERE frontier_id=?",
            (frontier["frontier_id"],),
        ).fetchone()
        document = json.loads(row[0])
        document["lease_invocation_limit"] = 63
        self.authority._db.execute(
            "UPDATE frontiers SET payload_json=? WHERE frontier_id=?",
            (json.dumps(document, sort_keys=True, separators=(",", ":")), frontier["frontier_id"]),
        )
        self.authority._db.commit()
        with self.assertRaises(Pass200CError):
            self.authority.current_frontier()

    def test_verified_probe_uses_pass200a_shadow_observation(self) -> None:
        frontier = self.admit(limit=1)
        result = self.authority.execute_verified_probe(
            frontier["frontier_id"],
            invocation_receipt_hash72="V" * 72,
            now_ns=self.NOW + 1,
        )
        self.assertEqual(result["returned_path"], "CANDIDATE")
        self.assertEqual(self.authority.current_frontier()["mode"], "LEASE_EXHAUSTED")


if __name__ == "__main__":
    unittest.main()
