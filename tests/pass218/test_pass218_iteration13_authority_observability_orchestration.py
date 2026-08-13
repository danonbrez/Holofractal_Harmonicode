from __future__ import annotations

import ast
from pathlib import Path

import pytest

from hhs_runtime.pass218.observability_i13 import (
    AUTHORITY_STATUS_SCHEMA,
    MAINTENANCE_RUN_RECEIPT_SCHEMA,
    OBSERVABILITY_POLICY_SCHEMA,
    OPERATOR_ACTION_SCHEMA,
    PASS218_AUTHORITY_OBSERVABILITY_VERSION,
    Pass218AuthorityObservabilityValidationError,
    Pass218ObservabilityPolicy,
    Pass218OperatorActionRejected,
    Pass218OperatorJournal,
    Pass218OperatorOrchestrator,
    build_authority_observability_status,
    seal_maintenance_run_receipt,
    validate_authority_observability_status,
    validate_maintenance_run_receipt,
    validate_observability_policy,
    validate_operator_action,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = 2_000_000_000


def _ready_lifecycle() -> dict:
    return {
        "startup_complete": True,
        "ingestion_enabled": True,
        "local_authority_held": True,
        "distributed_authority_held": True,
        "distributed_fence_epoch": 17,
        "cluster_quorum_ready": True,
        "cluster_identity_consistent": True,
        "cluster_linearizable_read_ready": True,
        "cluster_expected_member_count": 3,
        "cluster_quorum_size": 2,
        "cluster_reachable_member_count": 3,
        "cluster_unavailable_member_count": 0,
        "cluster_id": 9001,
        "cluster_member_ids": [1, 2, 3],
        "cluster_leader_ids": [2],
        "cluster_probe_hash72": None,
        "quorum_loss_count": 0,
        "quorum_recovery_count": 0,
    }


def _ready_status(policy: Pass218ObservabilityPolicy | None = None) -> dict:
    resolved = policy or Pass218ObservabilityPolicy.build()
    return build_authority_observability_status(
        lifecycle_status=_ready_lifecycle(),
        policy=resolved,
        now_epoch_seconds=NOW,
        certificate_not_after_epoch_seconds=NOW + resolved.certificate_warning_seconds + 1,
        latest_snapshot_epoch_seconds=NOW - 10,
        latest_rehearsal_epoch_seconds=NOW - 10,
        pending_operator_actions=0,
    )


def test_i13_contract_identity() -> None:
    assert PASS218_AUTHORITY_OBSERVABILITY_VERSION == "HHS-P218-AUTHORITY-OBSERVABILITY-ORCHESTRATION-I13-V1"
    assert OBSERVABILITY_POLICY_SCHEMA == "HHS-P218-I13-OBSERVABILITY-POLICY-V1"
    assert AUTHORITY_STATUS_SCHEMA == "HHS-P218-I13-AUTHORITY-OBSERVABILITY-STATUS-V1"
    assert OPERATOR_ACTION_SCHEMA == "HHS-P218-I13-OPERATOR-ACTION-V1"
    assert MAINTENANCE_RUN_RECEIPT_SCHEMA == "HHS-P218-I13-MAINTENANCE-RUN-RECEIPT-V1"


def test_policy_is_integer_only_and_preparatory() -> None:
    policy = Pass218ObservabilityPolicy.build()
    record = policy.record()
    assert validate_observability_policy(record) == record
    assert record["operator_actions_are_preparatory_only"] is True
    assert record["external_executor_required_for_maintenance"] is True
    assert record["canonical_authority_minted"] is False
    assert record["canonical_mutation_permitted"] is False


def test_ready_status_has_no_alerts_when_all_maintenance_evidence_is_fresh() -> None:
    status = _ready_status()
    assert validate_authority_observability_status(status) == status
    assert status["health"] == "READY"
    assert status["alert_count"] == 0
    assert status["distributed_fence_epoch"] == 17
    assert status["cluster_quorum_ready"] is True


def test_quorum_loss_is_critical_and_fail_closed_projection() -> None:
    lifecycle = _ready_lifecycle()
    lifecycle.update({
        "ingestion_enabled": False,
        "distributed_authority_held": False,
        "cluster_quorum_ready": False,
        "cluster_reachable_member_count": 1,
        "cluster_unavailable_member_count": 2,
    })
    status = build_authority_observability_status(
        lifecycle_status=lifecycle,
        policy=Pass218ObservabilityPolicy.build(),
        now_epoch_seconds=NOW,
        certificate_not_after_epoch_seconds=NOW + 9_999_999,
        latest_snapshot_epoch_seconds=NOW,
        latest_rehearsal_epoch_seconds=NOW,
    )
    assert status["health"] == "BLOCKED"
    assert status["critical_alert_count"] >= 1
    assert any(alert["code"] == "P218_I13_QUORUM_BLOCKED" for alert in status["alerts"])
    assert status["canonical_authority_minted"] is False


def test_certificate_expiry_and_stale_evidence_generate_alerts() -> None:
    policy = Pass218ObservabilityPolicy.build(
        certificate_warning_seconds=100,
        snapshot_max_age_seconds=50,
        rehearsal_max_age_seconds=75,
    )
    status = build_authority_observability_status(
        lifecycle_status=_ready_lifecycle(),
        policy=policy,
        now_epoch_seconds=NOW,
        certificate_not_after_epoch_seconds=NOW + 25,
        latest_snapshot_epoch_seconds=NOW - 51,
        latest_rehearsal_epoch_seconds=NOW - 76,
    )
    codes = {item["code"] for item in status["alerts"]}
    assert status["health"] == "DEGRADED"
    assert "P218_I13_CERT_EXPIRY_NEAR" in codes
    assert "P218_I13_SNAPSHOT_STALE" in codes
    assert "P218_I13_REHEARSAL_DUE" in codes


def test_missing_maintenance_evidence_is_visible_not_fabricated() -> None:
    status = build_authority_observability_status(
        lifecycle_status=_ready_lifecycle(),
        policy=Pass218ObservabilityPolicy.build(),
        now_epoch_seconds=NOW,
        certificate_not_after_epoch_seconds=None,
        latest_snapshot_epoch_seconds=None,
        latest_rehearsal_epoch_seconds=None,
    )
    codes = {item["code"] for item in status["alerts"]}
    assert "P218_I13_CERT_EXPIRY_UNKNOWN" in codes
    assert "P218_I13_SNAPSHOT_MISSING" in codes
    assert "P218_I13_REHEARSAL_MISSING" in codes


def test_operator_probe_is_prepared_without_external_executor() -> None:
    orchestrator = Pass218OperatorOrchestrator()
    action = orchestrator.prepare(
        request_id="probe-1",
        operator_id="operator-a",
        action="PROBE_CLUSTER",
        status=_ready_status(),
        prepared_epoch_seconds=NOW,
    )
    assert validate_operator_action(action) == action
    assert action["requires_external_executor"] is False
    assert action["prepared_not_executed"] is True
    assert action["canonical_mutation_permitted"] is False


def test_maintenance_prepare_requires_quorum() -> None:
    lifecycle = _ready_lifecycle()
    lifecycle.update({
        "cluster_quorum_ready": False,
        "ingestion_enabled": False,
        "distributed_authority_held": False,
        "cluster_reachable_member_count": 1,
    })
    blocked = build_authority_observability_status(
        lifecycle_status=lifecycle,
        policy=Pass218ObservabilityPolicy.build(),
        now_epoch_seconds=NOW,
        certificate_not_after_epoch_seconds=NOW + 9_999_999,
        latest_snapshot_epoch_seconds=NOW,
        latest_rehearsal_epoch_seconds=NOW,
    )
    with pytest.raises(Pass218OperatorActionRejected):
        Pass218OperatorOrchestrator().prepare(
            request_id="replace-blocked",
            operator_id="operator-a",
            action="PREPARE_MEMBER_REPLACEMENT",
            status=blocked,
            prepared_epoch_seconds=NOW,
        )


def test_member_replacement_prepare_requires_full_cluster_not_just_majority() -> None:
    lifecycle = _ready_lifecycle()
    lifecycle["cluster_reachable_member_count"] = 2
    lifecycle["cluster_unavailable_member_count"] = 1
    status = build_authority_observability_status(
        lifecycle_status=lifecycle,
        policy=Pass218ObservabilityPolicy.build(),
        now_epoch_seconds=NOW,
        certificate_not_after_epoch_seconds=NOW + 9_999_999,
        latest_snapshot_epoch_seconds=NOW,
        latest_rehearsal_epoch_seconds=NOW,
    )
    with pytest.raises(Pass218OperatorActionRejected):
        Pass218OperatorOrchestrator().prepare(
            request_id="replace-majority-only",
            operator_id="operator-a",
            action="PREPARE_MEMBER_REPLACEMENT",
            status=status,
            prepared_epoch_seconds=NOW,
        )


def test_maintenance_run_receipt_cannot_claim_canonical_mutation() -> None:
    action = Pass218OperatorOrchestrator().prepare(
        request_id="snapshot-1",
        operator_id="operator-a",
        action="REQUEST_SNAPSHOT_REHEARSAL",
        status=_ready_status(),
        prepared_epoch_seconds=NOW,
    )
    with pytest.raises(Pass218AuthorityObservabilityValidationError):
        seal_maintenance_run_receipt(
            run_id="run-bad",
            action_record_hash72=action["record_hash72"],
            operator_id="operator-a",
            action="REQUEST_SNAPSHOT_REHEARSAL",
            outcome="SUCCEEDED",
            started_epoch_seconds=NOW,
            completed_epoch_seconds=NOW + 1,
            before_status_hash72=_ready_status()["record_hash72"],
            after_status_hash72=_ready_status()["record_hash72"],
            external_operation_executed=True,
            canonical_target_changed=True,
            authority_minted=False,
        )


def test_append_only_journal_tracks_pending_and_success_epochs(tmp_path: Path) -> None:
    journal = Pass218OperatorJournal(tmp_path / "operator.jsonl")
    orchestrator = Pass218OperatorOrchestrator(journal=journal)
    status = _ready_status()
    action = orchestrator.prepare(
        request_id="snapshot-2",
        operator_id="operator-b",
        action="REQUEST_SNAPSHOT_REHEARSAL",
        status=status,
        prepared_epoch_seconds=NOW,
    )
    assert journal.pending_action_count() == 1
    receipt = seal_maintenance_run_receipt(
        run_id="run-good",
        action_record_hash72=action["record_hash72"],
        operator_id="operator-b",
        action="REQUEST_SNAPSHOT_REHEARSAL",
        outcome="SUCCEEDED",
        started_epoch_seconds=NOW,
        completed_epoch_seconds=NOW + 5,
        before_status_hash72=status["record_hash72"],
        after_status_hash72=status["record_hash72"],
        external_operation_executed=True,
        canonical_target_changed=False,
        authority_minted=False,
    )
    assert validate_maintenance_run_receipt(receipt) == receipt
    journal.append_run_receipt(receipt)
    assert journal.pending_action_count() == 0
    assert journal.latest_success_epoch("REQUEST_SNAPSHOT_REHEARSAL") == NOW + 5


def test_tampered_status_seal_is_rejected() -> None:
    status = _ready_status()
    status["health"] = "BLOCKED"
    with pytest.raises(Pass218AuthorityObservabilityValidationError):
        validate_authority_observability_status(status)


def test_authoritative_i13_python_has_no_float_literals() -> None:
    path = ROOT / "hhs_runtime/pass218/observability_i13.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    floats = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, float)
    ]
    assert floats == []
