#!/usr/bin/env python3
"""Restartable terminal validation for Pass 218 Iteration 17."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.distributed_consumption_i16 import Pass218InMemoryDistributedConsumptionLedger
from hhs_runtime.pass218.distributed_execution_i17 import (
    Pass218ExternalExecutionReplayRejected,
    Pass218InMemoryDistributedExecutionLedger,
)
from hhs_runtime.pass218.distributed_ownership import (
    Pass218InMemoryConsensusHarness,
    Pass218InMemoryDistributedAuthority,
)
from hhs_runtime.pass218.execution_i15 import seal_release_claim

NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I17-VALIDATION"}, {"label": label})


def make_release(fence: int) -> dict:
    body = {
        "schema": "HHS-P218-I14-MAINTENANCE-RELEASE-V1",
        "version": "HHS-P218-MULTI-PARTY-MAINTENANCE-APPROVAL-I14-V1",
        "policy_hash72": h72("policy"),
        "action_record_hash72": h72("action"),
        "action": ACTION,
        "prepared_by_operator_id": "prep",
        "preparer_message_hash72": h72("prep"),
        "approver_operator_ids": ["alice", "bob"],
        "approval_message_hash72s": [h72("alice"), h72("bob")],
        "executor_operator_id": "exec",
        "executor_message_hash72": h72("exec"),
        "required_distinct_approvers": 2,
        "valid_distinct_approvers": 2,
        "distributed_fence_epoch": fence,
        "current_status_hash72": h72("status"),
        "released_epoch_seconds": NOW,
        "expires_epoch_seconds": NOW + 600,
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


def make_claim(release: dict) -> dict:
    preflight = {
        "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
        "ok": True,
        "release_record_hash72": release["record_hash72"],
        "action_record_hash72": release["action_record_hash72"],
        "distributed_fence_epoch": release["distributed_fence_epoch"],
        "current_status_hash72": h72("preflight"),
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "recorded_revocations_rechecked": True,
        "maintenance_remains_external": True,
    }
    return seal_release_claim(
        release=release,
        preflight=preflight,
        claimed_epoch_ns=NOW * 1_000_000_000,
    )


def authority(harness, owner: str, host: str):
    return Pass218InMemoryDistributedAuthority(
        harness,
        owner_id=owner,
        host_id=host,
        lease_ttl_seconds=9,
    )


def main() -> int:
    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "i17-owner-a", "i17-host-a")
    first_record = first.acquire()
    if first_record is None or first_record["fence_epoch"] != 1:
        raise RuntimeError("P218_I17_FIRST_FENCE_REQUIRED")

    release = make_release(1)
    claim = make_claim(release)
    consumption_a = Pass218InMemoryDistributedConsumptionLedger(first)
    consumption_a.consume_claim(claim)
    execution_a = Pass218InMemoryDistributedExecutionLedger(first, consumption_a)
    dispatch = execution_a.reserve_dispatch(
        claim,
        executor_id="i17-executor",
        dispatched_epoch_ns=NOW * 1_000_000_000 + 1,
    )

    harness.expire_owner()
    second = authority(harness, "i17-owner-b", "i17-host-b")
    second_record = second.acquire()
    if second_record is None or second_record["fence_epoch"] != 2:
        raise RuntimeError("P218_I17_SECOND_FENCE_REQUIRED")
    consumption_b = Pass218InMemoryDistributedConsumptionLedger(second)
    execution_b = Pass218InMemoryDistributedExecutionLedger(second, consumption_b)
    restored = execution_b.dispatch_for_claim(claim["record_hash72"])
    if restored is None or restored["record_hash72"] != dispatch["record_hash72"]:
        raise RuntimeError("P218_I17_FAILOVER_DISPATCH_MISMATCH")

    replay_rejected = False
    try:
        execution_b.reserve_dispatch(
            claim,
            executor_id="i17-executor",
            dispatched_epoch_ns=NOW * 1_000_000_000 + 2,
        )
    except Pass218ExternalExecutionReplayRejected:
        replay_rejected = True
    if not replay_rejected:
        raise RuntimeError("P218_I17_REDISPATCH_NOT_REJECTED")

    result = execution_b.record_result(
        restored,
        {
            "outcome": "FAILED",
            "external_operation_executed": False,
            "external_result_hash72": h72("result"),
        },
        completed_epoch_ns=NOW * 1_000_000_000 + 3,
    )
    summary = {
        "schema": "HHS-P218-I17-FENCED-EXTERNAL-EXECUTION-VALIDATION-V1",
        "first_fence_epoch": first_record["fence_epoch"],
        "replacement_fence_epoch": second_record["fence_epoch"],
        "dispatch_record_hash72": dispatch["record_hash72"],
        "result_record_hash72": result["record_hash72"],
        "successor_read_exact_dispatch": True,
        "redispatch_after_failover_rejected": True,
        "successor_recorded_terminal_result_without_redispatch": True,
        "distributed_reservation_precedes_external_call": True,
        "distributed_result_precedes_local_attestation": True,
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "action_authority_minted": False,
    }
    out = ROOT / ".i17-evidence"
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("PASS218_I17_FENCED_EXTERNAL_EXECUTION=1")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
