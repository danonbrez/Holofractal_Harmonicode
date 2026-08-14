#!/usr/bin/env python3
"""Real-etcd validation for Pass 218 Iteration 18 terminal closure."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.distributed_closure_i18 import Pass218EtcdDistributedClosureLedger
from hhs_runtime.pass218.distributed_consumption_i16 import Pass218EtcdDistributedConsumptionLedger
from hhs_runtime.pass218.distributed_execution_i17 import Pass218EtcdDistributedExecutionLedger
from hhs_runtime.pass218.distributed_ownership import Pass218EtcdDistributedAuthority
from hhs_runtime.pass218.execution_i15 import seal_execution_attestation, seal_execution_reconciliation, seal_release_claim
from hhs_runtime.pass218.observability_i13 import seal_maintenance_run_receipt, seal_operator_action

NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I18-REAL-ETCD"}, {"label": label})


def make_action() -> dict:
    return seal_operator_action(
        request_id="i18-real-etcd-request",
        operator_id="prep",
        action=ACTION,
        status_hash72=h72("before-status"),
        prepared_epoch_seconds=NOW - 10,
        requires_external_executor=True,
    )


def make_release(action_hash: str) -> dict:
    body = {
        "schema": "HHS-P218-I14-MAINTENANCE-RELEASE-V1",
        "version": "HHS-P218-MULTI-PARTY-MAINTENANCE-APPROVAL-I14-V1",
        "policy_hash72": h72("policy"),
        "action_record_hash72": action_hash,
        "action": ACTION,
        "prepared_by_operator_id": "prep",
        "preparer_message_hash72": h72("prep"),
        "approver_operator_ids": ["alice", "bob"],
        "approval_message_hash72s": [h72("alice"), h72("bob")],
        "executor_operator_id": "exec",
        "executor_message_hash72": h72("exec"),
        "required_distinct_approvers": 2,
        "valid_distinct_approvers": 2,
        "distributed_fence_epoch": 1,
        "current_status_hash72": h72("release-status"),
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
        "distributed_fence_epoch": 1,
        "current_status_hash72": h72("preflight"),
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "recorded_revocations_rechecked": True,
        "maintenance_remains_external": True,
    }
    return seal_release_claim(release=release, preflight=preflight, claimed_epoch_ns=NOW * 1_000_000_000)


def main() -> int:
    endpoint = os.environ.get("HHS_PASS218_I10_ETCD_TEST_ENDPOINT", "").strip()
    if not endpoint:
        raise RuntimeError("P218_I18_REAL_ETCD_ENDPOINT_REQUIRED")
    base_namespace = os.environ.get("HHS_PASS218_I10_ETCD_TEST_NAMESPACE", "/hhs/pass218/i18-real-etcd").strip().rstrip("/")
    namespace = base_namespace + "/i18-closure-proof"

    first = Pass218EtcdDistributedAuthority(
        endpoint,
        namespace=namespace,
        owner_id="i18-real-etcd-owner-a",
        host_id="i18-real-etcd-host-a",
        lease_ttl_seconds=9,
    )
    first_record = first.acquire()
    if first_record is None or first_record["fence_epoch"] != 1:
        raise RuntimeError("P218_I18_REAL_ETCD_FIRST_FENCE_REQUIRED")

    action = make_action()
    release = make_release(action["record_hash72"])
    claim = make_claim(release)
    consumption_a = Pass218EtcdDistributedConsumptionLedger(first)
    consumption_a.consume_claim(claim)
    execution_a = Pass218EtcdDistributedExecutionLedger(first, consumption_a)
    closure_a = Pass218EtcdDistributedClosureLedger(first, execution_a)
    source = closure_a.ensure_action_source(action)
    if source["source_fence_epoch"] != 1:
        raise RuntimeError("P218_I18_REAL_ETCD_SOURCE_FENCE_INVALID")
    dispatch = execution_a.reserve_dispatch(claim, executor_id="i18-real-etcd-executor", dispatched_epoch_ns=NOW * 1_000_000_000 + 1)
    result = execution_a.record_result(
        dispatch,
        {"outcome": "FAILED", "external_operation_executed": False, "external_result_hash72": h72("terminal-result")},
        completed_epoch_ns=NOW * 1_000_000_000 + 2,
    )
    if closure_a.closure_for_claim(claim["record_hash72"]) is not None:
        raise RuntimeError("P218_I18_REAL_ETCD_PREFAILOVER_CLOSURE_MUST_BE_ABSENT")
    first.release()

    second = Pass218EtcdDistributedAuthority(
        endpoint,
        namespace=namespace,
        owner_id="i18-real-etcd-owner-b",
        host_id="i18-real-etcd-host-b",
        lease_ttl_seconds=9,
    )
    second_record = second.acquire()
    if second_record is None or second_record["fence_epoch"] != 2:
        raise RuntimeError("P218_I18_REAL_ETCD_SECOND_FENCE_REQUIRED")

    consumption_b = Pass218EtcdDistributedConsumptionLedger(second)
    execution_b = Pass218EtcdDistributedExecutionLedger(second, consumption_b)
    closure_b = Pass218EtcdDistributedClosureLedger(second, execution_b)
    restored_source = closure_b.source_for_action(action["record_hash72"])
    restored_result = execution_b.result_for_claim(claim["record_hash72"])
    if restored_source is None or restored_source["record_hash72"] != source["record_hash72"]:
        raise RuntimeError("P218_I18_REAL_ETCD_ACTION_SOURCE_MISSING")
    if restored_result is None or restored_result["record_hash72"] != result["record_hash72"]:
        raise RuntimeError("P218_I18_REAL_ETCD_RESULT_MISSING")

    attestation = seal_execution_attestation(
        claim=claim,
        outcome="FAILED",
        completed_epoch_ns=result["completed_epoch_ns"],
        external_result_hash72=result["external_result_hash72"],
        external_operation_executed=False,
    )
    run = seal_maintenance_run_receipt(
        run_id="i18-real-etcd-run",
        action_record_hash72=action["record_hash72"],
        operator_id=action["operator_id"],
        action=ACTION,
        outcome="FAILED",
        started_epoch_seconds=NOW,
        completed_epoch_seconds=NOW + 1,
        before_status_hash72=action["status_hash72"],
        after_status_hash72=h72("after-status"),
        external_operation_executed=False,
        canonical_target_changed=False,
        authority_minted=False,
    )
    reconciliation = seal_execution_reconciliation(claim=claim, attestation=attestation, i13_run_receipt=run)
    closure = closure_b.record_closure(
        claim=claim,
        result=restored_result,
        attestation=attestation,
        i13_run_receipt=run,
        reconciliation=reconciliation,
    )
    persisted = closure_b.closure_for_claim(claim["record_hash72"])
    if persisted is None or persisted["record_hash72"] != closure["record_hash72"]:
        raise RuntimeError("P218_I18_REAL_ETCD_CLOSURE_NOT_PERSISTED")
    status = closure_b.status()
    if status["distributed_terminal_closure_count"] != 1 or status["terminal_result_pending_closure_count"] != 0:
        raise RuntimeError("P218_I18_REAL_ETCD_CLOSURE_STATUS_INVALID")
    second.release()

    summary = {
        "schema": "HHS-P218-I18-REAL-ETCD-DISTRIBUTED-TERMINAL-CLOSURE-VALIDATION-V1",
        "first_fence_epoch": first_record["fence_epoch"],
        "replacement_fence_epoch": second_record["fence_epoch"],
        "action_source_hash72": source["record_hash72"],
        "dispatch_record_hash72": dispatch["record_hash72"],
        "i17_terminal_result_hash72": result["record_hash72"],
        "terminal_closure_hash72": closure["record_hash72"],
        "action_source_survived_machine_loss": True,
        "i17_result_survived_machine_loss": True,
        "successor_created_terminal_closure_without_redispatch": True,
        "distributed_closure_single_write": True,
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "action_authority_minted": False,
    }
    out = ROOT / ".i18-evidence"
    out.mkdir(parents=True, exist_ok=True)
    (out / "real-etcd-summary.json").write_text(json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print("PASS218_I18_REAL_ETCD_TERMINAL_CLOSURE=1")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
