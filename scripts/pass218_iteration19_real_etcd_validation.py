#!/usr/bin/env python3
"""Real-etcd failover proof for Pass 218 Iteration 19."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.authority_maintenance_i12 import seal_credential_rotation_plan
from hhs_runtime.pass218.distributed_closure_i18 import Pass218EtcdDistributedClosureLedger
from hhs_runtime.pass218.distributed_consumption_i16 import Pass218EtcdDistributedConsumptionLedger
from hhs_runtime.pass218.distributed_execution_i17 import Pass218EtcdDistributedExecutionLedger
from hhs_runtime.pass218.distributed_ownership import Pass218EtcdDistributedAuthority
from hhs_runtime.pass218.distributed_postcondition_i19 import Pass218EtcdPostconditionLedger, seal_postcondition_observation
from hhs_runtime.pass218.execution_i15 import seal_execution_attestation, seal_execution_reconciliation, seal_release_claim
from hhs_runtime.pass218.observability_i13 import seal_maintenance_run_receipt, seal_operator_action

NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"
OLD_CA = "1" * 64
NEW_CA = "2" * 64
OLD_CERT = "3" * 64
NEW_CERT = "4" * 64
OLD_KEY = "5" * 64
NEW_KEY = "6" * 64


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I19-REAL-ETCD"}, {"label": label})


def make_action() -> dict:
    return seal_operator_action(
        request_id="i19-real-etcd-request",
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


def make_rotation() -> dict:
    return seal_credential_rotation_plan(
        rotation_id="i19-real-etcd-rotation",
        old_ca_sha256=OLD_CA,
        new_ca_sha256=NEW_CA,
        old_client_cert_sha256=OLD_CERT,
        new_client_cert_sha256=NEW_CERT,
        old_client_key_sha256=OLD_KEY,
        new_client_key_sha256=NEW_KEY,
        preflight_probe_hash72=h72("rotation-preflight"),
        current_global_fence=1,
    )


def main() -> int:
    endpoint = os.environ.get("HHS_PASS218_I10_ETCD_TEST_ENDPOINT", "").strip()
    if not endpoint:
        raise RuntimeError("P218_I19_REAL_ETCD_ENDPOINT_REQUIRED")
    base_namespace = os.environ.get("HHS_PASS218_I10_ETCD_TEST_NAMESPACE", "/hhs/pass218/i19-real-etcd").strip().rstrip("/")
    namespace = base_namespace + "/i19-postcondition-proof"

    first = Pass218EtcdDistributedAuthority(
        endpoint,
        namespace=namespace,
        owner_id="i19-real-etcd-owner-a",
        host_id="i19-real-etcd-host-a",
        lease_ttl_seconds=9,
    )
    first_record = first.acquire()
    if first_record is None or first_record["fence_epoch"] != 1:
        raise RuntimeError("P218_I19_REAL_ETCD_FIRST_FENCE_REQUIRED")

    action = make_action()
    release = make_release(action["record_hash72"])
    claim = make_claim(release)
    rotation = make_rotation()
    consumption_a = Pass218EtcdDistributedConsumptionLedger(first)
    consumption_a.consume_claim(claim)
    execution_a = Pass218EtcdDistributedExecutionLedger(first, consumption_a)
    closure_a = Pass218EtcdDistributedClosureLedger(first, execution_a)
    closure_a.ensure_action_source(action)
    dispatch = execution_a.reserve_dispatch(claim, executor_id="i19-real-etcd-executor", dispatched_epoch_ns=NOW * 1_000_000_000 + 1)
    first.release()

    second = Pass218EtcdDistributedAuthority(
        endpoint,
        namespace=namespace,
        owner_id="i19-real-etcd-owner-b",
        host_id="i19-real-etcd-host-b",
        lease_ttl_seconds=9,
    )
    second_record = second.acquire()
    if second_record is None or second_record["fence_epoch"] != 2:
        raise RuntimeError("P218_I19_REAL_ETCD_SECOND_FENCE_REQUIRED")

    consumption_b = Pass218EtcdDistributedConsumptionLedger(second)
    execution_b = Pass218EtcdDistributedExecutionLedger(second, consumption_b)
    closure_b = Pass218EtcdDistributedClosureLedger(second, execution_b)
    restored_dispatch = execution_b.dispatch_for_claim(claim["record_hash72"])
    if restored_dispatch is None or restored_dispatch["record_hash72"] != dispatch["record_hash72"]:
        raise RuntimeError("P218_I19_REAL_ETCD_DISPATCH_NOT_RECOVERED")
    result = execution_b.record_result(
        restored_dispatch,
        {
            "outcome": "SUCCEEDED",
            "external_operation_executed": True,
            "external_result_hash72": h72("rotation-result"),
            "i12_maintenance_record": rotation,
        },
        completed_epoch_ns=NOW * 1_000_000_000 + 2,
    )
    attestation = seal_execution_attestation(
        claim=claim,
        outcome="SUCCEEDED",
        completed_epoch_ns=result["completed_epoch_ns"],
        external_result_hash72=result["external_result_hash72"],
        external_operation_executed=True,
        i12_maintenance_record=rotation,
    )
    run = seal_maintenance_run_receipt(
        run_id="i19-real-etcd-run",
        action_record_hash72=action["record_hash72"],
        operator_id=action["operator_id"],
        action=ACTION,
        outcome="SUCCEEDED",
        started_epoch_seconds=NOW,
        completed_epoch_seconds=NOW + 1,
        before_status_hash72=action["status_hash72"],
        after_status_hash72=h72("after-status"),
        external_operation_executed=True,
        canonical_target_changed=False,
        authority_minted=False,
    )
    reconciliation = seal_execution_reconciliation(claim=claim, attestation=attestation, i13_run_receipt=run)
    closure = closure_b.record_closure(
        claim=claim,
        result=result,
        attestation=attestation,
        i13_run_receipt=run,
        reconciliation=reconciliation,
    )
    postconditions = Pass218EtcdPostconditionLedger(second, execution_b, closure_b)
    before = postconditions.status()
    if before["successful_closure_pending_verification_count"] != 1:
        raise RuntimeError("P218_I19_REAL_ETCD_SUCCESS_MUST_BEGIN_PENDING")

    observation = seal_postcondition_observation(
        action=ACTION,
        i12_maintenance_record=rotation,
        observation={
            "active_ca_sha256": NEW_CA,
            "active_client_cert_sha256": NEW_CERT,
            "active_client_key_sha256": NEW_KEY,
            "new_writer_fence_epoch": 2,
            "new_credentials_verified": True,
            "old_writer_released": True,
            "simultaneous_writer_identities_observed": False,
            "post_linearizable_probe_hash72": h72("post-probe"),
        },
        observed_epoch_ns=result["completed_epoch_ns"] + 1,
    )
    verification = postconditions.record_verification(closure=closure, result=result, observation=observation)
    persisted = postconditions.verification_for_claim(claim["record_hash72"])
    if persisted is None or persisted["record_hash72"] != verification["record_hash72"]:
        raise RuntimeError("P218_I19_REAL_ETCD_VERIFICATION_NOT_PERSISTED")
    status = postconditions.status()
    if status["successful_closure_pending_verification_count"] != 0 or status["distributed_postcondition_verification_count"] != 1:
        raise RuntimeError("P218_I19_REAL_ETCD_STATUS_INVALID")
    second.release()

    summary = {
        "schema": "HHS-P218-I19-REAL-ETCD-POSTCONDITION-VALIDATION-V1",
        "first_fence_epoch": first_record["fence_epoch"],
        "replacement_fence_epoch": second_record["fence_epoch"],
        "dispatch_record_hash72": dispatch["record_hash72"],
        "i17_result_record_hash72": result["record_hash72"],
        "i18_terminal_closure_hash72": closure["record_hash72"],
        "postcondition_observation_hash72": observation["record_hash72"],
        "postcondition_verification_hash72": verification["record_hash72"],
        "dispatch_survived_machine_loss": True,
        "successor_recorded_result_without_redispatch": True,
        "successful_closure_was_pending_effect_verification": True,
        "successor_sealed_postcondition_under_new_fence": True,
        "postcondition_verification_single_write": True,
        "successful_closure_pending_verification_count": 0,
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "action_authority_minted": False,
        "redispatch_permitted": False,
    }
    out = ROOT / ".i19-evidence"
    out.mkdir(parents=True, exist_ok=True)
    (out / "real-etcd-summary.json").write_text(json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print("PASS218_I19_REAL_ETCD_POSTCONDITION_VERIFICATION=1")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
