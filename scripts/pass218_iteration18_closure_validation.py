#!/usr/bin/env python3
"""Deterministic failover validation for Pass 218 Iteration 18."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.pass218_execution_i18_control import Pass218DistributedTerminalClosureControlPlane
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.distributed_closure_i18 import Pass218InMemoryDistributedClosureLedger
from hhs_runtime.pass218.distributed_consumption_i16 import Pass218InMemoryDistributedConsumptionLedger
from hhs_runtime.pass218.distributed_execution_i17 import Pass218InMemoryDistributedExecutionLedger
from hhs_runtime.pass218.distributed_ownership import Pass218InMemoryConsensusHarness, Pass218InMemoryDistributedAuthority
from hhs_runtime.pass218.execution_i15 import seal_execution_attestation, seal_execution_reconciliation, seal_release_claim
from hhs_runtime.pass218.observability_i13 import Pass218OperatorJournal, seal_maintenance_run_receipt, seal_operator_action

NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I18-VALIDATION"}, {"label": label})


def authority(harness, owner: str, host: str):
    return Pass218InMemoryDistributedAuthority(harness, owner_id=owner, host_id=host, lease_ttl_seconds=9)


def make_action() -> dict:
    return seal_operator_action(
        request_id="i18-validation-request",
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


class FakeI13:
    def __init__(self, path: Path) -> None:
        self.journal = Pass218OperatorJournal(path)

    def status(self) -> dict:
        raise AssertionError("I18 mirror must not synthesize a new I13 status")


class FakeI14:
    pass


def main() -> int:
    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "i18-owner-a", "i18-host-a")
    first_record = first.acquire()
    if first_record is None or first_record["fence_epoch"] != 1:
        raise RuntimeError("P218_I18_FIRST_FENCE_REQUIRED")

    action = make_action()
    release = make_release(action["record_hash72"])
    claim = make_claim(release)
    consumption_a = Pass218InMemoryDistributedConsumptionLedger(first)
    consumption_a.consume_claim(claim)
    execution_a = Pass218InMemoryDistributedExecutionLedger(first, consumption_a)
    closure_a = Pass218InMemoryDistributedClosureLedger(first, execution_a)
    source = closure_a.ensure_action_source(action)
    dispatch = execution_a.reserve_dispatch(claim, executor_id="i18-executor", dispatched_epoch_ns=NOW * 1_000_000_000 + 1)
    result = execution_a.record_result(
        dispatch,
        {"outcome": "FAILED", "external_operation_executed": False, "external_result_hash72": h72("result")},
        completed_epoch_ns=NOW * 1_000_000_000 + 2,
    )
    if closure_a.closure_for_claim(claim["record_hash72"]) is not None:
        raise RuntimeError("P218_I18_PREFAILOVER_CLOSURE_MUST_BE_ABSENT")

    harness.expire_owner()
    second = authority(harness, "i18-owner-b", "i18-host-b")
    second_record = second.acquire()
    if second_record is None or second_record["fence_epoch"] != 2:
        raise RuntimeError("P218_I18_SECOND_FENCE_REQUIRED")

    consumption_b = Pass218InMemoryDistributedConsumptionLedger(second)
    execution_b = Pass218InMemoryDistributedExecutionLedger(second, consumption_b)
    closure_b = Pass218InMemoryDistributedClosureLedger(second, execution_b)
    restored_source = closure_b.source_for_action(action["record_hash72"])
    restored_result = execution_b.result_for_claim(claim["record_hash72"])
    if restored_source is None or restored_source["record_hash72"] != source["record_hash72"]:
        raise RuntimeError("P218_I18_ACTION_SOURCE_NOT_RECOVERED")
    if restored_result is None or restored_result["record_hash72"] != result["record_hash72"]:
        raise RuntimeError("P218_I18_RESULT_NOT_RECOVERED")

    attestation = seal_execution_attestation(
        claim=claim,
        outcome=result["outcome"],
        completed_epoch_ns=result["completed_epoch_ns"],
        external_result_hash72=result["external_result_hash72"],
        external_operation_executed=False,
    )
    run = seal_maintenance_run_receipt(
        run_id="i18-validation-run",
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

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        fake_i13 = FakeI13(root / "operator-journal.jsonl")
        control = Pass218DistributedTerminalClosureControlPlane(
            fake_i13,
            FakeI14(),
            state_root=str(root),
            distributed_ledger=consumption_b,
            execution_ledger=execution_b,
            external_executor=None,
            external_executor_id=None,
            result_shared_secret=None,
            closure_ledger=closure_b,
        )
        control.synchronize()
        control._mirror_closure_local(closure)
        local_claim = control.journal.claim_for_release(release["record_hash72"])
        local_attestation = control.journal.attestation_for_release(release["record_hash72"])
        local_reconciliation = control._existing_reconciliation(release["record_hash72"])
        local_runs = [item for item in fake_i13.journal.records() if item.get("kind") == "MAINTENANCE_RUN"]
        if local_claim is None or local_claim["record_hash72"] != claim["record_hash72"]:
            raise RuntimeError("P218_I18_LOCAL_CLAIM_NOT_REPAIRED")
        if local_attestation is None or local_attestation["record_hash72"] != attestation["record_hash72"]:
            raise RuntimeError("P218_I18_LOCAL_ATTESTATION_NOT_REPAIRED")
        if local_reconciliation is None or local_reconciliation["record_hash72"] != reconciliation["record_hash72"]:
            raise RuntimeError("P218_I18_LOCAL_RECONCILIATION_NOT_REPAIRED")
        if len(local_runs) != 1 or local_runs[0]["record"]["record_hash72"] != run["record_hash72"]:
            raise RuntimeError("P218_I18_LOCAL_I13_RUN_NOT_REPAIRED")

    summary = {
        "schema": "HHS-P218-I18-DISTRIBUTED-TERMINAL-CLOSURE-VALIDATION-V1",
        "first_fence_epoch": first_record["fence_epoch"],
        "replacement_fence_epoch": second_record["fence_epoch"],
        "action_source_hash72": source["record_hash72"],
        "i17_result_hash72": result["record_hash72"],
        "terminal_closure_hash72": closure["record_hash72"],
        "action_source_persisted_before_external_dispatch": True,
        "successor_created_closure_without_redispatch": True,
        "distributed_closure_precedes_local_terminal_mirror": True,
        "successor_repaired_exact_local_attestation": True,
        "successor_repaired_exact_i13_run_receipt": True,
        "successor_repaired_exact_reconciliation": True,
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "action_authority_minted": False,
    }
    out = ROOT / ".i18-evidence"
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print("PASS218_I18_DISTRIBUTED_TERMINAL_CLOSURE=1")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
