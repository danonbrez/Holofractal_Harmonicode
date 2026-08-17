from __future__ import annotations

import ast
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.authority_maintenance_i12 import seal_credential_rotation_plan
from hhs_runtime.pass218.distributed_consumption_i16 import Pass218InMemoryDistributedConsumptionLedger
from hhs_runtime.pass218.distributed_execution_i17 import (
    PASS218_DISTRIBUTED_EXECUTION_VERSION,
    Pass218ExternalExecutionReplayRejected,
    Pass218ExternalExecutionValidationError,
    Pass218InMemoryDistributedExecutionLedger,
    validate_external_dispatch,
    validate_external_result,
)
from hhs_runtime.pass218.distributed_ownership import (
    Pass218InMemoryConsensusHarness,
    Pass218InMemoryDistributedAuthority,
)
from hhs_runtime.pass218.execution_i15 import seal_release_claim

NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I17-TEST"}, {"label": label})


def release(*, fence: int, action_hash: str, suffix: str) -> dict:
    body = {
        "schema": "HHS-P218-I14-MAINTENANCE-RELEASE-V1",
        "version": "HHS-P218-MULTI-PARTY-MAINTENANCE-APPROVAL-I14-V1",
        "policy_hash72": h72("policy-" + suffix),
        "action_record_hash72": action_hash,
        "action": ACTION,
        "prepared_by_operator_id": "prep",
        "preparer_message_hash72": h72("prep-" + suffix),
        "approver_operator_ids": ["alice", "bob"],
        "approval_message_hash72s": [h72("alice-" + suffix), h72("bob-" + suffix)],
        "executor_operator_id": "exec",
        "executor_message_hash72": h72("exec-" + suffix),
        "required_distinct_approvers": 2,
        "valid_distinct_approvers": 2,
        "distributed_fence_epoch": fence,
        "current_status_hash72": h72("status-" + suffix),
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


def preflight(value: dict) -> dict:
    return {
        "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
        "ok": True,
        "release_record_hash72": value["record_hash72"],
        "action_record_hash72": value["action_record_hash72"],
        "distributed_fence_epoch": value["distributed_fence_epoch"],
        "current_status_hash72": h72("preflight-" + value["record_hash72"]),
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "recorded_revocations_rechecked": True,
        "maintenance_remains_external": True,
    }


def claim(value: dict) -> dict:
    return seal_release_claim(
        release=value,
        preflight=preflight(value),
        claimed_epoch_ns=NOW * 1_000_000_000,
    )


def authority(harness: Pass218InMemoryConsensusHarness, owner: str, host: str) -> Pass218InMemoryDistributedAuthority:
    return Pass218InMemoryDistributedAuthority(
        harness,
        owner_id=owner,
        host_id=host,
        lease_ttl_seconds=9,
    )


def rotation_evidence(*, fence: int) -> dict:
    return seal_credential_rotation_plan(
        rotation_id="i17-rotation",
        old_ca_sha256="1" * 64,
        new_ca_sha256="2" * 64,
        old_client_cert_sha256="3" * 64,
        new_client_cert_sha256="4" * 64,
        old_client_key_sha256="5" * 64,
        new_client_key_sha256="6" * 64,
        preflight_probe_hash72=h72("rotation-preflight"),
        current_global_fence=fence,
    )


def setup_primary():
    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "owner-a", "host-a")
    assert first.acquire()["fence_epoch"] == 1
    consumption = Pass218InMemoryDistributedConsumptionLedger(first)
    value = release(fence=1, action_hash=h72("action"), suffix="primary")
    first_claim = claim(value)
    consumption.consume_claim(first_claim)
    execution = Pass218InMemoryDistributedExecutionLedger(first, consumption)
    return harness, first, consumption, execution, value, first_claim


def test_i17_declares_fenced_external_execution_contract() -> None:
    assert PASS218_DISTRIBUTED_EXECUTION_VERSION == "HHS-P218-FENCED-EXTERNAL-EXECUTION-I17-V1"


def test_i17_distributed_reservation_precedes_external_call_and_is_single_use() -> None:
    _, _, _, execution, _, first_claim = setup_primary()
    dispatch = execution.reserve_dispatch(
        first_claim,
        executor_id="executor-service-a",
        dispatched_epoch_ns=NOW * 1_000_000_000 + 1,
    )
    assert dispatch["distributed_reservation_precedes_external_call"] is True
    assert dispatch["single_dispatch_per_claim"] is True
    assert dispatch["redispatch_after_unknown_forbidden"] is True
    assert dispatch["canonical_authority_minted"] is False
    with pytest.raises(Pass218ExternalExecutionReplayRejected, match="CLAIM_ALREADY_DISPATCHED"):
        execution.reserve_dispatch(
            first_claim,
            executor_id="executor-service-a",
            dispatched_epoch_ns=NOW * 1_000_000_000 + 2,
        )


def test_i17_machine_loss_preserves_dispatch_and_successor_records_result_without_redispatch() -> None:
    harness, _, _, execution, _, first_claim = setup_primary()
    dispatch = execution.reserve_dispatch(
        first_claim,
        executor_id="executor-service-a",
        dispatched_epoch_ns=NOW * 1_000_000_000 + 1,
    )

    harness.expire_owner()
    replacement = authority(harness, "owner-b", "host-b")
    assert replacement.acquire()["fence_epoch"] == 2
    replacement_consumption = Pass218InMemoryDistributedConsumptionLedger(replacement)
    replacement_execution = Pass218InMemoryDistributedExecutionLedger(replacement, replacement_consumption)

    restored = replacement_execution.dispatch_for_claim(first_claim["record_hash72"])
    assert restored is not None
    assert restored["record_hash72"] == dispatch["record_hash72"]
    with pytest.raises(Pass218ExternalExecutionReplayRejected, match="CLAIM_ALREADY_DISPATCHED"):
        replacement_execution.reserve_dispatch(
            first_claim,
            executor_id="executor-service-a",
            dispatched_epoch_ns=NOW * 1_000_000_000 + 2,
        )

    result = replacement_execution.record_result(
        restored,
        {
            "outcome": "SUCCEEDED",
            "external_operation_executed": True,
            "external_result_hash72": h72("external-result"),
            "i12_maintenance_record": rotation_evidence(fence=2),
        },
        completed_epoch_ns=NOW * 1_000_000_000 + 3,
    )
    assert result["result_recorded_fence_epoch"] == 2
    assert result["dispatch_fence_epoch"] == 1
    assert result["distributed_result_precedes_local_attestation"] is True
    assert result["i12_evidence_present"] is True
    assert result["canonical_mutation_permitted"] is False


def test_i17_success_requires_i12_evidence() -> None:
    _, _, _, execution, _, first_claim = setup_primary()
    dispatch = execution.reserve_dispatch(
        first_claim,
        executor_id="executor-service-a",
        dispatched_epoch_ns=NOW * 1_000_000_000 + 1,
    )
    with pytest.raises(Pass218ExternalExecutionValidationError, match="SUCCESS_REQUIRES_EXECUTION_AND_I12_EVIDENCE"):
        execution.record_result(
            dispatch,
            {
                "outcome": "SUCCEEDED",
                "external_operation_executed": True,
                "external_result_hash72": h72("missing-i12"),
            },
            completed_epoch_ns=NOW * 1_000_000_000 + 2,
        )


def test_i17_terminal_result_is_single_write() -> None:
    _, _, _, execution, _, first_claim = setup_primary()
    dispatch = execution.reserve_dispatch(
        first_claim,
        executor_id="executor-service-a",
        dispatched_epoch_ns=NOW * 1_000_000_000 + 1,
    )
    first = execution.record_result(
        dispatch,
        {
            "outcome": "FAILED",
            "external_operation_executed": False,
            "external_result_hash72": h72("failed-result"),
        },
        completed_epoch_ns=NOW * 1_000_000_000 + 2,
    )
    assert first["outcome"] == "FAILED"
    with pytest.raises(Pass218ExternalExecutionReplayRejected, match="TERMINAL_RESULT_ALREADY_RECORDED"):
        execution.record_result(
            dispatch,
            {
                "outcome": "ABORTED",
                "external_operation_executed": False,
                "external_result_hash72": h72("different-result"),
            },
            completed_epoch_ns=NOW * 1_000_000_000 + 3,
        )


def test_i17_dispatch_and_result_tamper_are_rejected() -> None:
    _, _, _, execution, _, first_claim = setup_primary()
    dispatch = execution.reserve_dispatch(
        first_claim,
        executor_id="executor-service-a",
        dispatched_epoch_ns=NOW * 1_000_000_000 + 1,
    )
    tampered_dispatch = dict(dispatch)
    tampered_dispatch["redispatch_after_unknown_forbidden"] = False
    with pytest.raises(Pass218ExternalExecutionValidationError):
        validate_external_dispatch(tampered_dispatch)

    result = execution.record_result(
        dispatch,
        {
            "outcome": "FAILED",
            "external_operation_executed": False,
            "external_result_hash72": h72("tamper-result"),
        },
        completed_epoch_ns=NOW * 1_000_000_000 + 2,
    )
    tampered_result = dict(result)
    tampered_result["distributed_result_precedes_local_attestation"] = False
    with pytest.raises(Pass218ExternalExecutionValidationError):
        validate_external_result(tampered_result)


def test_i17_status_reports_unresolved_then_terminal() -> None:
    _, _, _, execution, _, first_claim = setup_primary()
    dispatch = execution.reserve_dispatch(
        first_claim,
        executor_id="executor-service-a",
        dispatched_epoch_ns=NOW * 1_000_000_000 + 1,
    )
    status = execution.status()
    assert status["dispatch_count"] == 1
    assert status["unresolved_dispatch_count"] == 1
    execution.record_result(
        dispatch,
        {
            "outcome": "FAILED",
            "external_operation_executed": False,
            "external_result_hash72": h72("status-result"),
        },
        completed_epoch_ns=NOW * 1_000_000_000 + 2,
    )
    status = execution.status()
    assert status["terminal_result_count"] == 1
    assert status["unresolved_dispatch_count"] == 0


def test_i17_authoritative_modules_contain_no_float_literals() -> None:
    root = Path(__file__).resolve().parents[2]
    for rel in (
        "hhs_runtime/pass218/distributed_execution_i17.py",
        "hhs_backend/pass218_execution_i17_control.py",
        "hhs_backend/runtime_os_pass218_execution_i17.py",
    ):
        tree = ast.parse((root / rel).read_text(encoding="utf-8"))
        floats = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, rel
