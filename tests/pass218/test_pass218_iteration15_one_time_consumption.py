from __future__ import annotations

import ast
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass146.engine import HHS146BoundaryEngine
from hhs_runtime.pass218.approval_i14 import (
    OPERATOR_STATEMENT_SCHEMA,
    STATEMENT_DESTINATION,
    Pass218ApprovalPolicy,
    Pass218OperatorRegistry,
    evaluate_maintenance_release,
    seal_operator_record,
)
from hhs_runtime.pass218.authority_maintenance_i12 import seal_credential_rotation_plan
from hhs_runtime.pass218.execution_i15 import (
    PASS218_ONE_TIME_EXECUTION_VERSION,
    Pass218ExecutionReplayRejected,
    Pass218ReleaseConsumptionJournal,
    seal_execution_attestation,
    seal_execution_reconciliation,
    validate_execution_attestation,
    validate_execution_reconciliation,
    validate_release_claim,
)
from hhs_runtime.pass218.observability_i13 import seal_maintenance_run_receipt

NOW = 1_800_000_000
FENCE = 9
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I15-TEST"}, {"label": label})


def operator(operator_id: str, roles: list[str]) -> dict:
    return seal_operator_record(
        operator_id=operator_id,
        identity_id="IDN-" + operator_id,
        identity_hash72=h72("identity-" + operator_id),
        public_key_b64="pub-" + operator_id,
        public_key_fingerprint="fingerprint-" + operator_id,
        roles=roles,
    )


@pytest.fixture
def registry(monkeypatch: pytest.MonkeyPatch) -> Pass218OperatorRegistry:
    monkeypatch.setattr(HHS146BoundaryEngine, "_verify_signed_envelope", staticmethod(lambda _: {
        "signature_valid": True,
        "envelope_hash_valid": True,
        "message_hash_valid": True,
        "data_hash_valid": True,
    }))
    return Pass218OperatorRegistry([
        operator("prep", ["PREPARER"]),
        operator("alice", ["APPROVER"]),
        operator("bob", ["APPROVER"]),
        operator("exec", ["EXECUTOR"]),
    ])


def statement(registry: Pass218OperatorRegistry, operator_id: str, kind: str, action_hash: str, *, now: int = NOW, label: str | None = None) -> dict:
    role = {"PREPARE": "PREPARER", "APPROVE": "APPROVER", "EXECUTE": "EXECUTOR"}[kind]
    record = registry.get(operator_id, role=role)
    data = {
        "schema": OPERATOR_STATEMENT_SCHEMA,
        "kind": kind,
        "operator_id": operator_id,
        "action_record_hash72": action_hash,
        "action": ACTION,
        "prepared_by_operator_id": "prep",
        "distributed_fence_epoch": FENCE,
        "statement_epoch_seconds": now - 5,
        "expires_epoch_seconds": NOW + 900,
        "nonce": f"nonce-{operator_id}-{kind}-{now}",
    }
    return {
        "data": data,
        "authority": {"identity_id": record["identity_id"], "identity_hash72": record["identity_hash72"]},
        "source_peer": operator_id,
        "destination_peer": STATEMENT_DESTINATION,
        "sender_public_key_b64": record["public_key_b64"],
        "sender_public_key_fingerprint": record["public_key_fingerprint"],
        "message_hash72": h72(label or f"{operator_id}-{kind}-{now}"),
    }


def action_record() -> dict:
    return {
        "record_hash72": h72("action"),
        "operator_id": "prep",
        "action": ACTION,
        "requires_external_executor": True,
        "prepared_not_executed": True,
    }


def release(registry: Pass218OperatorRegistry, *, now: int = NOW) -> dict:
    action = action_record()
    status = {
        "record_hash72": h72("status"),
        "health": "READY",
        "cluster_quorum_ready": True,
        "distributed_authority_held": True,
        "distributed_fence_epoch": FENCE,
    }
    return evaluate_maintenance_release(
        action_record=action,
        current_status=status,
        preparer_statement=statement(registry, "prep", "PREPARE", action["record_hash72"], now=now),
        approval_statements=[
            statement(registry, "alice", "APPROVE", action["record_hash72"], now=now, label=f"alice-{now}"),
            statement(registry, "bob", "APPROVE", action["record_hash72"], now=now, label=f"bob-{now}"),
        ],
        executor_statement=statement(registry, "exec", "EXECUTE", action["record_hash72"], now=now),
        revocation_statements=[],
        registry=registry,
        policy=Pass218ApprovalPolicy(),
        now_epoch_seconds=now,
    )


def preflight(value: dict) -> dict:
    return {
        "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
        "ok": True,
        "release_record_hash72": value["record_hash72"],
        "action_record_hash72": value["action_record_hash72"],
        "distributed_fence_epoch": value["distributed_fence_epoch"],
        "current_status_hash72": h72("preflight-status"),
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "recorded_revocations_rechecked": True,
        "maintenance_remains_external": True,
    }


def i12_rotation() -> dict:
    return seal_credential_rotation_plan(
        rotation_id="i15-rotation",
        old_ca_sha256="a" * 64,
        new_ca_sha256="b" * 64,
        old_client_cert_sha256="c" * 64,
        new_client_cert_sha256="d" * 64,
        old_client_key_sha256="e" * 64,
        new_client_key_sha256="f" * 64,
        preflight_probe_hash72=h72("i12-preflight"),
        current_global_fence=FENCE,
    )


def test_i15_version_and_claim_invariants(tmp_path: Path, registry: Pass218OperatorRegistry) -> None:
    value = release(registry)
    journal = Pass218ReleaseConsumptionJournal(tmp_path)
    claim = journal.claim_release(release=value, preflight=preflight(value), claimed_epoch_ns=NOW * 1_000_000_000)
    assert claim["version"] == PASS218_ONE_TIME_EXECUTION_VERSION
    assert claim["release_consumed"] is True
    assert claim["single_use_release"] is True
    assert claim["single_execution_per_action"] is True
    assert claim["consume_before_execute"] is True
    assert claim["crash_does_not_reopen_release"] is True
    assert claim["canonical_authority_minted"] is False
    validate_release_claim(claim)


def test_i15_same_release_can_be_claimed_only_once(tmp_path: Path, registry: Pass218OperatorRegistry) -> None:
    value = release(registry)
    journal = Pass218ReleaseConsumptionJournal(tmp_path)
    journal.claim_release(release=value, preflight=preflight(value), claimed_epoch_ns=NOW * 1_000_000_000)
    with pytest.raises(Pass218ExecutionReplayRejected, match="RELEASE_ALREADY_CONSUMED"):
        journal.claim_release(release=value, preflight=preflight(value), claimed_epoch_ns=NOW * 1_000_000_000 + 1)


def test_i15_different_release_for_same_action_cannot_start_second_attempt(tmp_path: Path, registry: Pass218OperatorRegistry) -> None:
    first = release(registry, now=NOW)
    second = release(registry, now=NOW + 1)
    assert first["record_hash72"] != second["record_hash72"]
    journal = Pass218ReleaseConsumptionJournal(tmp_path)
    journal.claim_release(release=first, preflight=preflight(first), claimed_epoch_ns=NOW * 1_000_000_000)
    with pytest.raises(Pass218ExecutionReplayRejected, match="ACTION_ALREADY_CLAIMED"):
        journal.claim_release(release=second, preflight=preflight(second), claimed_epoch_ns=NOW * 1_000_000_000 + 1)


def test_i15_claim_survives_restart_and_remains_consumed(tmp_path: Path, registry: Pass218OperatorRegistry) -> None:
    value = release(registry)
    first = Pass218ReleaseConsumptionJournal(tmp_path)
    claim = first.claim_release(release=value, preflight=preflight(value), claimed_epoch_ns=NOW * 1_000_000_000)
    restarted = Pass218ReleaseConsumptionJournal(tmp_path)
    assert restarted.claim_for_release(value["record_hash72"])["record_hash72"] == claim["record_hash72"]
    with pytest.raises(Pass218ExecutionReplayRejected):
        restarted.claim_release(release=value, preflight=preflight(value), claimed_epoch_ns=NOW * 1_000_000_000 + 2)


def test_i15_success_attestation_requires_i12_evidence_and_is_terminal(tmp_path: Path, registry: Pass218OperatorRegistry) -> None:
    value = release(registry)
    journal = Pass218ReleaseConsumptionJournal(tmp_path)
    claim = journal.claim_release(release=value, preflight=preflight(value), claimed_epoch_ns=NOW * 1_000_000_000)
    with pytest.raises(Exception, match="SUCCESS_REQUIRES_I12_EVIDENCE"):
        seal_execution_attestation(
            claim=claim,
            outcome="SUCCEEDED",
            completed_epoch_ns=NOW * 1_000_000_000 + 10,
            external_result_hash72=h72("result"),
            external_operation_executed=True,
        )
    attestation = seal_execution_attestation(
        claim=claim,
        outcome="SUCCEEDED",
        completed_epoch_ns=NOW * 1_000_000_000 + 10,
        external_result_hash72=h72("result"),
        external_operation_executed=True,
        i12_maintenance_record=i12_rotation(),
    )
    stored = journal.record_attestation(release_hash=value["record_hash72"], attestation=attestation)
    assert stored["terminal_attempt"] is True
    assert stored["release_permanently_consumed"] is True
    validate_execution_attestation(stored)
    with pytest.raises(Pass218ExecutionReplayRejected, match="TERMINAL_ATTESTATION_ALREADY_RECORDED"):
        journal.record_attestation(release_hash=value["record_hash72"], attestation=attestation)


def test_i15_failed_or_aborted_attempt_does_not_reopen_release(tmp_path: Path, registry: Pass218OperatorRegistry) -> None:
    value = release(registry)
    journal = Pass218ReleaseConsumptionJournal(tmp_path)
    claim = journal.claim_release(release=value, preflight=preflight(value), claimed_epoch_ns=NOW * 1_000_000_000)
    failed = seal_execution_attestation(
        claim=claim,
        outcome="ABORTED",
        completed_epoch_ns=NOW * 1_000_000_000 + 5,
        external_result_hash72=h72("aborted"),
        external_operation_executed=False,
    )
    journal.record_attestation(release_hash=value["record_hash72"], attestation=failed)
    with pytest.raises(Pass218ExecutionReplayRejected):
        journal.claim_release(release=value, preflight=preflight(value), claimed_epoch_ns=NOW * 1_000_000_000 + 9)


def test_i15_reconciliation_binds_i13_and_i12_evidence(tmp_path: Path, registry: Pass218OperatorRegistry) -> None:
    value = release(registry)
    journal = Pass218ReleaseConsumptionJournal(tmp_path)
    claim = journal.claim_release(release=value, preflight=preflight(value), claimed_epoch_ns=NOW * 1_000_000_000)
    attestation = seal_execution_attestation(
        claim=claim,
        outcome="SUCCEEDED",
        completed_epoch_ns=NOW * 1_000_000_000 + 10,
        external_result_hash72=h72("external-result"),
        external_operation_executed=True,
        i12_maintenance_record=i12_rotation(),
    )
    run = seal_maintenance_run_receipt(
        run_id="i15-run",
        action_record_hash72=value["action_record_hash72"],
        operator_id="prep",
        action=ACTION,
        outcome="SUCCEEDED",
        started_epoch_seconds=NOW,
        completed_epoch_seconds=NOW + 1,
        before_status_hash72=h72("before"),
        after_status_hash72=h72("after"),
        external_operation_executed=True,
        canonical_target_changed=False,
        authority_minted=False,
    )
    reconciliation = seal_execution_reconciliation(claim=claim, attestation=attestation, i13_run_receipt=run)
    assert reconciliation["reconciled_into_i13"] is True
    assert reconciliation["reconciled_into_i14_namespace"] is True
    assert reconciliation["no_second_execution_permitted"] is True
    validate_execution_reconciliation(reconciliation)


def test_i15_authoritative_modules_contain_no_float_literals() -> None:
    root = Path(__file__).resolve().parents[2]
    for rel in (
        "hhs_runtime/pass218/execution_i15.py",
        "hhs_backend/pass218_execution_i15_control.py",
        "hhs_backend/runtime_os_pass218_consumption_i15.py",
    ):
        tree = ast.parse((root / rel).read_text(encoding="utf-8"))
        floats = [node for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, float)]
        assert not floats, rel
