#!/usr/bin/env python3
"""Real-etcd validation for Pass 218 Iteration 17 fenced external execution."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.distributed_consumption_i16 import (
    Pass218EtcdDistributedConsumptionLedger,
)
from hhs_runtime.pass218.distributed_execution_i17 import (
    Pass218EtcdDistributedExecutionLedger,
    Pass218ExternalExecutionReplayRejected,
)
from hhs_runtime.pass218.distributed_ownership import Pass218EtcdDistributedAuthority
from hhs_runtime.pass218.execution_i15 import seal_release_claim

NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I17-REAL-ETCD"}, {"label": label})


def make_release(*, fence: int) -> dict:
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


def main() -> int:
    endpoint = os.environ.get("HHS_PASS218_I10_ETCD_TEST_ENDPOINT", "").strip()
    if not endpoint:
        raise RuntimeError("P218_I17_REAL_ETCD_ENDPOINT_REQUIRED")
    base_namespace = os.environ.get(
        "HHS_PASS218_I10_ETCD_TEST_NAMESPACE", "/hhs/pass218/i17-real-etcd"
    ).strip().rstrip("/")
    namespace = base_namespace + "/i17-execution-proof"

    first = Pass218EtcdDistributedAuthority(
        endpoint,
        namespace=namespace,
        owner_id="i17-real-etcd-owner-a",
        host_id="i17-real-etcd-host-a",
        lease_ttl_seconds=9,
    )
    first_record = first.acquire()
    if first_record is None or first_record["fence_epoch"] != 1:
        raise RuntimeError("P218_I17_REAL_ETCD_FIRST_FENCE_REQUIRED")

    release = make_release(fence=1)
    claim = make_claim(release)
    consumption_a = Pass218EtcdDistributedConsumptionLedger(first)
    consumption_entry = consumption_a.consume_claim(claim)
    execution_a = Pass218EtcdDistributedExecutionLedger(first, consumption_a)
    dispatch = execution_a.reserve_dispatch(
        claim,
        executor_id="i17-real-etcd-executor",
        dispatched_epoch_ns=NOW * 1_000_000_000 + 1,
    )
    if dispatch["claim_record_hash72"] != claim["record_hash72"]:
        raise RuntimeError("P218_I17_REAL_ETCD_DISPATCH_CLAIM_MISMATCH")
    if execution_a.status()["unresolved_dispatch_count"] != 1:
        raise RuntimeError("P218_I17_REAL_ETCD_UNRESOLVED_DISPATCH_REQUIRED")
    first.release()

    second = Pass218EtcdDistributedAuthority(
        endpoint,
        namespace=namespace,
        owner_id="i17-real-etcd-owner-b",
        host_id="i17-real-etcd-host-b",
        lease_ttl_seconds=9,
    )
    second_record = second.acquire()
    if second_record is None or second_record["fence_epoch"] != 2:
        raise RuntimeError("P218_I17_REAL_ETCD_SECOND_FENCE_REQUIRED")

    consumption_b = Pass218EtcdDistributedConsumptionLedger(second)
    execution_b = Pass218EtcdDistributedExecutionLedger(second, consumption_b)
    restored = execution_b.dispatch_for_claim(claim["record_hash72"])
    if restored is None or restored["record_hash72"] != dispatch["record_hash72"]:
        raise RuntimeError("P218_I17_REAL_ETCD_FAILOVER_DISPATCH_MISMATCH")

    replay_rejected = False
    try:
        execution_b.reserve_dispatch(
            claim,
            executor_id="i17-real-etcd-executor",
            dispatched_epoch_ns=NOW * 1_000_000_000 + 2,
        )
    except Pass218ExternalExecutionReplayRejected:
        replay_rejected = True
    if not replay_rejected:
        raise RuntimeError("P218_I17_REAL_ETCD_REDISPATCH_NOT_REJECTED")

    result = execution_b.record_result(
        restored,
        {
            "outcome": "FAILED",
            "external_operation_executed": False,
            "external_result_hash72": h72("terminal-result"),
        },
        completed_epoch_ns=NOW * 1_000_000_000 + 3,
    )
    persisted = execution_b.result_for_claim(claim["record_hash72"])
    if persisted is None or persisted["record_hash72"] != result["record_hash72"]:
        raise RuntimeError("P218_I17_REAL_ETCD_TERMINAL_RESULT_MISSING")
    status = execution_b.status()
    if status["dispatch_count"] != 1 or status["terminal_result_count"] != 1:
        raise RuntimeError("P218_I17_REAL_ETCD_TERMINAL_STATUS_INVALID")
    if status["unresolved_dispatch_count"] != 0:
        raise RuntimeError("P218_I17_REAL_ETCD_DISPATCH_STILL_UNRESOLVED")
    second.release()

    summary = {
        "schema": "HHS-P218-I17-REAL-ETCD-EXTERNAL-EXECUTION-VALIDATION-V1",
        "first_fence_epoch": first_record["fence_epoch"],
        "replacement_fence_epoch": second_record["fence_epoch"],
        "consumption_entry_hash72": consumption_entry["record_hash72"],
        "dispatch_record_hash72": dispatch["record_hash72"],
        "terminal_result_hash72": result["record_hash72"],
        "distributed_dispatch_persisted_before_failover": True,
        "successor_read_exact_dispatch": True,
        "redispatch_after_failover_rejected": True,
        "successor_recorded_terminal_result_without_redispatch": True,
        "distributed_result_persisted": True,
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "action_authority_minted": False,
    }
    out = ROOT / ".i17-evidence"
    out.mkdir(parents=True, exist_ok=True)
    (out / "real-etcd-summary.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("PASS218_I17_REAL_ETCD_FAILOVER=1")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
