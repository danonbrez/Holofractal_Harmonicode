"""Run the complete Pass 200A -> 200B -> 200C production validation chain."""
from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

from hhs_backend.runtime.hhs_pass200a_proof_carrying_optimization import (
    Pass200AProofCarryingOptimizationAuthority,
)
from hhs_backend.runtime.hhs_pass200b_governed_canary_admission import (
    Pass200BGovernedCanaryAuthority,
)
from hhs_backend.runtime.hhs_pass200c_guarded_active_admission import (
    CLASSIFICATION,
    Pass200CGuardedActiveAuthority,
)


def run(state_root: Path, evidence_path: Path) -> dict:
    shutil.rmtree(state_root, ignore_errors=True)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    pass200a = Pass200AProofCarryingOptimizationAuthority(state_root=state_root / "pass200a")
    pass200b = None
    pass200c = None
    reopened = None
    try:
        qualification = pass200a.run_holdouts(
            worker_count=8,
            vm81_receipt_hash72="7" * 72,
        )
        shadows = pass200a.execute_all_shadows(
            worker_count=8,
            vm81_receipt_hash72="8" * 72,
        )
        assert qualification["closed"] is True
        assert qualification["independent_envelope_count"] == 4
        assert qualification["bundle_count"] == 4
        assert shadows["closed"] is True
        assert shadows["shadow_match_count"] == 4
        assert shadows["candidate_activation_count"] == 0

        pass200b = Pass200BGovernedCanaryAuthority(
            state_root=state_root / "pass200b",
            pass200a=pass200a,
        )
        bundle = pass200a.list_bundles()[0]

        def canary_approvals(now_ns: int, compiler_receipt: str, runtime_receipt: str):
            current = pass200b.current_frontier()
            expiry = now_ns + 900_000_000_000
            return [
                pass200b.build_approval(
                    principal_id="vm81:compiler-promotion-authority",
                    capability="COMPILER_PROMOTION_APPROVE",
                    receipt_hash72=compiler_receipt,
                    bundle_hash72=bundle["bundle_hash72"],
                    expected_frontier_hash72=current["frontier_hash72"],
                    expires_at_ns=expiry,
                ),
                pass200b.build_approval(
                    principal_id="vm81:runtime-promotion-authority",
                    capability="RUNTIME_PROMOTION_APPROVE",
                    receipt_hash72=runtime_receipt,
                    bundle_hash72=bundle["bundle_hash72"],
                    expected_frontier_hash72=current["frontier_hash72"],
                    expires_at_ns=expiry,
                ),
            ], expiry

        now = time.time_ns()
        approvals1, expiry1 = canary_approvals(now, "C" * 72, "D" * 72)
        canary1 = pass200b.admit_canary(
            bundle["bundle_id"],
            invocation_limit=8,
            canary_numerator=1,
            canary_denominator=4,
            approvals=approvals1,
            vm81_activation_receipt_hash72="A" * 72,
            expires_at_ns=expiry1,
            now_ns=now,
        )
        canary_paths1 = [
            pass200b.execute_verified_probe(
                canary1["frontier_id"],
                invocation_receipt_hash72="I" * 72,
                now_ns=now + ordinal + 1,
            )["returned_path"]
            for ordinal in range(8)
        ]
        assert canary_paths1 == [
            "CANDIDATE",
            "REFERENCE",
            "REFERENCE",
            "REFERENCE",
            "CANDIDATE",
            "REFERENCE",
            "REFERENCE",
            "REFERENCE",
        ]
        assert pass200b.current_frontier()["mode"] == "EXHAUSTED"

        now2 = now + 10_000
        approvals2, expiry2 = canary_approvals(now2, "E" * 72, "F" * 72)
        canary2 = pass200b.admit_canary(
            bundle["bundle_id"],
            invocation_limit=8,
            canary_numerator=1,
            canary_denominator=2,
            approvals=approvals2,
            vm81_activation_receipt_hash72="B" * 72,
            expires_at_ns=expiry2,
            now_ns=now2,
        )
        canary_paths2 = [
            pass200b.execute_verified_probe(
                canary2["frontier_id"],
                invocation_receipt_hash72="J" * 72,
                now_ns=now2 + ordinal + 1,
            )["returned_path"]
            for ordinal in range(8)
        ]
        assert canary_paths2 == [
            "CANDIDATE",
            "REFERENCE",
            "CANDIDATE",
            "REFERENCE",
            "CANDIDATE",
            "REFERENCE",
            "CANDIDATE",
            "REFERENCE",
        ]
        assert pass200b.current_frontier()["mode"] == "EXHAUSTED"

        pass200c = Pass200CGuardedActiveAuthority(
            state_root=state_root / "pass200c",
            pass200b=pass200b,
        )
        evidence = pass200c.aggregate_canary_evidence(bundle["bundle_id"])
        assert evidence["successful_canary_count"] == 2
        assert evidence["total_canary_invocations"] == 16
        assert evidence["total_candidate_returns"] == 6
        assert evidence["total_reference_returns"] == 10

        def active_approvals(now_ns: int, receipts: tuple[str, str, str]):
            current = pass200c.current_frontier()
            expiry = now_ns + 1_800_000_000_000
            specs = [
                ("vm81:compiler-active-authority", "COMPILER_ACTIVE_APPROVE", receipts[0]),
                ("vm81:runtime-active-authority", "RUNTIME_ACTIVE_APPROVE", receipts[1]),
                ("vm81:operations-active-authority", "OPERATIONS_ACTIVE_APPROVE", receipts[2]),
            ]
            return [
                pass200c.build_approval(
                    principal_id=principal,
                    capability=capability,
                    receipt_hash72=receipt,
                    bundle_hash72=bundle["bundle_hash72"],
                    evidence_hash72=evidence["evidence_hash72"],
                    expected_frontier_hash72=current["frontier_hash72"],
                    expires_at_ns=expiry,
                )
                for principal, capability, receipt in specs
            ], expiry

        now3 = now + 20_000
        active_approvals1, active_expiry1 = active_approvals(
            now3,
            ("K" * 72, "L" * 72, "M" * 72),
        )
        active1 = pass200c.admit_active(
            bundle["bundle_id"],
            lease_invocation_limit=6,
            approvals=active_approvals1,
            vm81_activation_receipt_hash72="N" * 72,
            expires_at_ns=active_expiry1,
            now_ns=now3,
        )
        active_paths = [
            pass200c.execute_verified_probe(
                active1["frontier_id"],
                invocation_receipt_hash72="P" * 72,
                now_ns=now3 + ordinal + 1,
            )["returned_path"]
            for ordinal in range(6)
        ]
        assert active_paths == ["CANDIDATE"] * 6
        assert pass200c.current_frontier()["mode"] == "LEASE_EXHAUSTED"

        now4 = now + 30_000
        active_approvals2, active_expiry2 = active_approvals(
            now4,
            ("Q" * 72, "R" * 72, "S" * 72),
        )
        active2 = pass200c.admit_active(
            bundle["bundle_id"],
            lease_invocation_limit=4,
            approvals=active_approvals2,
            vm81_activation_receipt_hash72="U" * 72,
            expires_at_ns=active_expiry2,
            now_ns=now4,
        )
        mismatch = pass200c.execute_active(
            active2["frontier_id"],
            reference_result={"value": 1},
            candidate_result={"value": 2},
            reference_witness_hash72="W" * 72,
            candidate_witness_hash72="X" * 72,
            reference_replay_hash72="Y" * 72,
            candidate_replay_hash72="Z" * 72,
            invocation_receipt_hash72="V" * 72,
            now_ns=now4 + 1,
        )
        assert mismatch["status"] == "ROLLED_BACK"
        assert mismatch["returned_path"] == "REFERENCE"
        assert pass200c.current_frontier()["mode"] == "ROLLED_BACK"

        status = pass200c.status()
        verification = pass200c.verify()
        assert status["classification"] == CLASSIFICATION
        assert status["closed"] is True
        assert status["total_invocations"] == 7
        assert status["candidate_returns"] == 6
        assert status["reference_returns"] == 1
        assert status["current_mode"] == "ROLLED_BACK"
        assert status["guard_every_active_invocation"] is True
        assert status["frozen_constraint_enabled"] is False
        assert verification["frontier_count"] == 5
        assert verification["active_frontier_count"] == 2
        assert verification["lease_exhausted_frontier_count"] == 1
        assert verification["rollback_frontier_count"] == 1
        assert verification["singleton_activation_commit_count"] == 2
        assert verification["evidence_count"] == 1
        assert verification["invocation_count"] == 7
        assert verification["event_chain"]["ok"] is True
        assert verification["event_chain"]["event_count"] == 13

        current = pass200c.current_frontier()
        tip = verification["event_chain"]["tip_hash72"]
        receipt = {
            "schema": "HHS_PASS_200C_VALIDATION_RECEIPT_V1",
            "contract": status["contract"],
            "classification": status["classification"],
            "closed": True,
            "summary": {
                "pass200a_independent_envelopes": qualification["independent_envelope_count"],
                "pass200a_compiler_candidate_bundles": qualification["bundle_count"],
                "pass200a_shadow_matches": shadows["shadow_match_count"],
                "successful_canary_frontiers": evidence["successful_canary_count"],
                "canary_invocations": evidence["total_canary_invocations"],
                "canary_candidate_returns": evidence["total_candidate_returns"],
                "canary_reference_returns": evidence["total_reference_returns"],
                "active_frontiers": verification["active_frontier_count"],
                "singleton_activation_commits": verification["singleton_activation_commit_count"],
                "active_invocations": status["total_invocations"],
                "active_candidate_returns": status["candidate_returns"],
                "active_reference_returns": status["reference_returns"],
                "lease_exhausted_frontiers": verification["lease_exhausted_frontier_count"],
                "rollback_frontiers": verification["rollback_frontier_count"],
                "event_count": verification["event_chain"]["event_count"],
            },
            "evidence_hash72": evidence["evidence_hash72"],
            "first_active_frontier_hash72": active1["frontier_hash72"],
            "second_active_frontier_hash72": active2["frontier_hash72"],
            "current_frontier_hash72": current["frontier_hash72"],
            "status_hash72": status["status_hash72"],
            "event_chain": verification["event_chain"],
            "claim_boundary": {
                "three_active_approvals_required": True,
                "guard_every_active_invocation": True,
                "candidate_self_authorization": False,
                "mismatch_returns_reference": True,
                "lease_exhaustion_restores_reference": True,
                "automatic_frozen_constraint_promotion": False,
            },
        }
        evidence_path.write_text(
            json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        pass200c.close()
        pass200c = None
        reopened = Pass200CGuardedActiveAuthority(
            state_root=state_root / "pass200c",
            pass200b=pass200b,
        )
        restarted = reopened.status()
        assert restarted["current_frontier"]["frontier_hash72"] == current["frontier_hash72"]
        assert restarted["total_invocations"] == 7
        assert restarted["candidate_returns"] == 6
        assert restarted["reference_returns"] == 1
        assert restarted["event_chain"]["tip_hash72"] == tip
        return receipt
    finally:
        if reopened is not None:
            reopened.close()
        if pass200c is not None:
            pass200c.close()
        if pass200b is not None:
            pass200b.close()
        pass200a.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-root", default=".hhs/pass200c-ci")
    parser.add_argument(
        "--evidence",
        default="evidence/pass200c-ci/PASS200C_VALIDATION_RECEIPT.json",
    )
    args = parser.parse_args()
    receipt = run(Path(args.state_root), Path(args.evidence))
    print(json.dumps(receipt["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
