from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.execution_i15 import Pass218ExecutionReplayRejected, Pass218ReleaseConsumptionJournal


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I15-PARALLEL-RESERVATION"}, {"label": label})


def release() -> dict:
    body = {
        "schema": "HHS-P218-I14-MAINTENANCE-RELEASE-V1",
        "version": "HHS-P218-MULTI-PARTY-MAINTENANCE-APPROVAL-I14-V1",
        "policy_hash72": h72("policy"),
        "action_record_hash72": h72("action"),
        "action": "PREPARE_CREDENTIAL_ROTATION",
        "prepared_by_operator_id": "prep",
        "preparer_message_hash72": h72("prep"),
        "approver_operator_ids": ["alice", "bob"],
        "approval_message_hash72s": [h72("alice"), h72("bob")],
        "executor_operator_id": "exec",
        "executor_message_hash72": h72("exec"),
        "required_distinct_approvers": 2,
        "valid_distinct_approvers": 2,
        "distributed_fence_epoch": 4,
        "current_status_hash72": h72("status"),
        "released_epoch_seconds": 1_800_000_000,
        "expires_epoch_seconds": 1_800_000_600,
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "pass146_statement_integrity_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "external_maintenance_preconditions_satisfied": True,
        "maintenance_remains_external": True,
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
        "authoritative_float_weights": False,
    }
    body["record_hash72"] = hash72_digest({"domain": body["schema"]}, body)
    return body


def preflight(value: dict) -> dict:
    return {
        "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
        "ok": True,
        "release_record_hash72": value["record_hash72"],
        "action_record_hash72": value["action_record_hash72"],
        "distributed_fence_epoch": 4,
        "current_status_hash72": h72("preflight"),
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "recorded_revocations_rechecked": True,
        "maintenance_remains_external": True,
    }


def contender(root: str, value: dict, gate: dict, epoch_ns: int) -> str:
    try:
        Pass218ReleaseConsumptionJournal(root).claim_release(
            release=value,
            preflight=gate,
            claimed_epoch_ns=epoch_ns,
        )
        return "CLAIMED"
    except Pass218ExecutionReplayRejected:
        return "REJECTED"


def test_i15_parallel_reservation_has_exactly_one_winner(tmp_path: Path) -> None:
    value = release()
    gate = preflight(value)
    root = str(tmp_path / "journal")
    with ProcessPoolExecutor(max_workers=8) as pool:
        futures = [
            pool.submit(contender, root, value, gate, 1_800_000_000_000_000_000 + index)
            for index in range(8)
        ]
        outcomes = [future.result() for future in futures]
    assert outcomes.count("CLAIMED") == 1
    assert outcomes.count("REJECTED") == 7
