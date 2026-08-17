from __future__ import annotations

import ast
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.distributed_closure_i18 import (
    PASS218_DISTRIBUTED_CLOSURE_VERSION,
    Pass218DistributedClosureValidationError,
    Pass218InMemoryDistributedClosureLedger,
    validate_distributed_action_source,
    validate_distributed_terminal_closure,
)
from hhs_runtime.pass218.distributed_consumption_i16 import Pass218InMemoryDistributedConsumptionLedger
from hhs_runtime.pass218.distributed_execution_i17 import Pass218InMemoryDistributedExecutionLedger
from hhs_runtime.pass218.distributed_ownership import (
    Pass218InMemoryConsensusHarness,
    Pass218InMemoryDistributedAuthority,
)
from hhs_runtime.pass218.execution_i15 import (
    seal_execution_attestation,
    seal_execution_reconciliation,
    seal_release_claim,
)
from hhs_runtime.pass218.observability_i13 import (
    seal_maintenance_run_receipt,
    seal_operator_action,
)

NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I18-TEST"}, {"label": label})


def authority(harness: Pass218InMemoryConsensusHarness, owner: str, host: str) -> Pass218InMemoryDistributedAuthority:
    return Pass218InMemoryDistributedAuthority(harness, owner_id=owner, host_id=host, lease_ttl_seconds=9)


def action_record() -> dict:
    return seal_operator_action(
        request_id="i18-request",
        operator_id="prep",
        action=ACTION,
        status_hash72=h72("before-status"),
        prepared_epoch_seconds=NOW - 10,
        requires_external_executor=True,
    )


def release(*, fence: int, action_hash: str) -> dict:
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
        "distributed_fence_epoch": fence,
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


def claim(value: dict) -> dict:
    preflight = {
        "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
        "ok": True,
        "release_record_hash72": value["record_hash72"],
        "action_record_hash72": value["action_record_hash72"],
        "distributed_fence_epoch": value["distributed_fence_epoch"],
        "current_status_hash72": h72("preflight"),
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "recorded_revocations_rechecked": True,
        "maintenance_remains_external": True,
    }
    return seal_release_claim(release=value, preflight=preflight, claimed_epoch_ns=NOW * 1_000_000_000)


def terminal_records(first_claim: dict, result: dict, action: dict) -> tuple[dict, dict, dict]:
    attestation = seal_execution_attestation(
        claim=first_claim,
        outcome=result["outcome"],
        completed_epoch_ns=result["completed_epoch_ns"],
        external_result_hash72=result["external_result_hash72"],
        external_operation_executed=bool(result["external_operation_executed"]),
    )
    run = seal_maintenance_run_receipt(
        run_id="i18-run",
        action_record_hash72=first_claim["action_record_hash72"],
        operator_id=action["operator_id"],
        action=first_claim["action"],
        outcome=result["outcome"],
        started_epoch_seconds=NOW,
        completed_epoch_seconds=NOW + 1,
        before_status_hash72=action["status_hash72"],
        after_status_hash72=h72("after-status"),
        external_operation_executed=bool(result["external_operation_executed"]),
        canonical_target_changed=False,
        authority_minted=False,
    )
    reconciliation = seal_execution_reconciliation(
        claim=first_claim,
        attestation=attestation,
        i13_run_receipt=run,
    )
    return attestation, run, reconciliation


def setup_result():
    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "owner-a", "host-a")
    assert first.acquire()["fence_epoch"] == 1
    action = action_record()
    value = release(fence=1, action_hash=action["record_hash72"])
    first_claim = claim(value)
    consumption = Pass218InMemoryDistributedConsumptionLedger(first)
    consumption.consume_claim(first_claim)
    execution = Pass218InMemoryDistributedExecutionLedger(first, consumption)
    closure = Pass218InMemoryDistributedClosureLedger(first, execution)
    source = closure.ensure_action_source(action)
    dispatch = execution.reserve_dispatch(
        first_claim,
        executor_id="executor-service-a",
        dispatched_epoch_ns=NOW * 1_000_000_000 + 1,
    )
    result = execution.record_result(
        dispatch,
        {
            "outcome": "FAILED",
            "external_operation_executed": False,
            "external_result_hash72": h72("external-result"),
        },
        completed_epoch_ns=NOW * 1_000_000_000 + 2,
    )
    return harness, first, action, first_claim, source, dispatch, result


def test_i18_declares_distributed_terminal_closure_contract() -> None:
    assert PASS218_DISTRIBUTED_CLOSURE_VERSION == "HHS-P218-DISTRIBUTED-TERMINAL-CLOSURE-I18-V1"


def test_i18_action_source_is_metadata_only_and_grants_no_authority() -> None:
    _, _, action, _, source, _, _ = setup_result()
    validated = validate_distributed_action_source(source)
    assert validated["action_record_hash72"] == action["record_hash72"]
    assert validated["metadata_only"] is True
    assert validated["grants_execution_authority"] is False
    assert validated["grants_retry_authority"] is False
    assert validated["canonical_authority_minted"] is False


def test_i18_successor_closes_terminal_result_after_machine_loss_without_redispatch() -> None:
    harness, _, action, first_claim, source, dispatch, result = setup_result()
    assert source["source_fence_epoch"] == 1
    harness.expire_owner()
    replacement = authority(harness, "owner-b", "host-b")
    assert replacement.acquire()["fence_epoch"] == 2
    consumption_b = Pass218InMemoryDistributedConsumptionLedger(replacement)
    execution_b = Pass218InMemoryDistributedExecutionLedger(replacement, consumption_b)
    closure_b = Pass218InMemoryDistributedClosureLedger(replacement, execution_b)

    restored_dispatch = execution_b.dispatch_for_claim(first_claim["record_hash72"])
    restored_result = execution_b.result_for_claim(first_claim["record_hash72"])
    assert restored_dispatch is not None and restored_dispatch["record_hash72"] == dispatch["record_hash72"]
    assert restored_result is not None and restored_result["record_hash72"] == result["record_hash72"]
    restored_source = closure_b.source_for_action(action["record_hash72"])
    assert restored_source is not None and restored_source["record_hash72"] == source["record_hash72"]

    attestation, run, reconciliation = terminal_records(first_claim, restored_result, action)
    terminal = closure_b.record_closure(
        claim=first_claim,
        result=restored_result,
        attestation=attestation,
        i13_run_receipt=run,
        reconciliation=reconciliation,
    )
    assert terminal["closure_fence_epoch"] == 2
    assert terminal["i17_result_record_hash72"] == result["record_hash72"]
    assert terminal["successor_may_repair_local_evidence"] is True
    assert terminal["successor_may_redispatch"] is False
    assert terminal["canonical_mutation_permitted"] is False
    status = closure_b.status()
    assert status["distributed_terminal_closure_count"] == 1
    assert status["terminal_result_pending_closure_count"] == 0


def test_i18_terminal_closure_is_idempotent_for_exact_result() -> None:
    harness, _, action, first_claim, _, _, result = setup_result()
    attestation, run, reconciliation = terminal_records(first_claim, result, action)
    first_authority = authority(harness, "owner-shadow", "host-shadow")
    # Existing owner still holds the fence, so use the original state owner via a fresh
    # ledger only after failover.
    harness.expire_owner()
    assert first_authority.acquire()["fence_epoch"] == 2
    execution = Pass218InMemoryDistributedExecutionLedger(
        first_authority,
        Pass218InMemoryDistributedConsumptionLedger(first_authority),
    )
    ledger = Pass218InMemoryDistributedClosureLedger(first_authority, execution)
    first = ledger.record_closure(
        claim=first_claim,
        result=result,
        attestation=attestation,
        i13_run_receipt=run,
        reconciliation=reconciliation,
    )
    second = ledger.record_closure(
        claim=first_claim,
        result=result,
        attestation=attestation,
        i13_run_receipt=run,
        reconciliation=reconciliation,
    )
    assert first["record_hash72"] == second["record_hash72"]


def test_i18_rejects_tampered_terminal_closure() -> None:
    harness, _, action, first_claim, _, _, result = setup_result()
    harness.expire_owner()
    replacement = authority(harness, "owner-b", "host-b")
    assert replacement.acquire()["fence_epoch"] == 2
    execution = Pass218InMemoryDistributedExecutionLedger(
        replacement,
        Pass218InMemoryDistributedConsumptionLedger(replacement),
    )
    ledger = Pass218InMemoryDistributedClosureLedger(replacement, execution)
    attestation, run, reconciliation = terminal_records(first_claim, result, action)
    terminal = ledger.record_closure(
        claim=first_claim,
        result=result,
        attestation=attestation,
        i13_run_receipt=run,
        reconciliation=reconciliation,
    )
    tampered = dict(terminal)
    tampered["successor_may_redispatch"] = True
    with pytest.raises(Pass218DistributedClosureValidationError):
        validate_distributed_terminal_closure(tampered)


def test_i18_requires_distributed_action_source_before_closure() -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "owner-a", "host-a")
    assert first.acquire()["fence_epoch"] == 1
    action = action_record()
    value = release(fence=1, action_hash=action["record_hash72"])
    first_claim = claim(value)
    consumption = Pass218InMemoryDistributedConsumptionLedger(first)
    consumption.consume_claim(first_claim)
    execution = Pass218InMemoryDistributedExecutionLedger(first, consumption)
    dispatch = execution.reserve_dispatch(first_claim, executor_id="exec", dispatched_epoch_ns=NOW * 1_000_000_000 + 1)
    result = execution.record_result(
        dispatch,
        {"outcome": "FAILED", "external_operation_executed": False, "external_result_hash72": h72("no-source")},
        completed_epoch_ns=NOW * 1_000_000_000 + 2,
    )
    ledger = Pass218InMemoryDistributedClosureLedger(first, execution)
    attestation, run, reconciliation = terminal_records(first_claim, result, action)
    with pytest.raises(Pass218DistributedClosureValidationError, match="DISTRIBUTED_ACTION_SOURCE_REQUIRED"):
        ledger.record_closure(
            claim=first_claim,
            result=result,
            attestation=attestation,
            i13_run_receipt=run,
            reconciliation=reconciliation,
        )


def test_i18_authoritative_modules_contain_no_float_literals() -> None:
    root = Path(__file__).resolve().parents[2]
    for rel in (
        "hhs_runtime/pass218/distributed_closure_i18.py",
        "hhs_backend/pass218_execution_i18_control.py",
        "hhs_backend/runtime_os_pass218_closure_i18.py",
    ):
        tree = ast.parse((root / rel).read_text(encoding="utf-8"))
        floats = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, rel
