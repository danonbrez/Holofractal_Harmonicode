from __future__ import annotations

import ast
from hashlib import sha256
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.authority_maintenance_i12 import (
    CREDENTIAL_ROTATION_PLAN_SCHEMA,
    MAINTENANCE_POLICY_SCHEMA,
    MEMBER_REPLACEMENT_PLAN_SCHEMA,
    OPERATIONAL_ALERT_RECEIPT_SCHEMA,
    PASS218_AUTHORITY_MAINTENANCE_VERSION,
    RECOVERY_STATUS_SCHEMA,
    SNAPSHOT_RETENTION_RECEIPT_SCHEMA,
    Pass218AuthorityMaintenanceStateError,
    Pass218AuthorityMaintenanceValidationError,
    Pass218BoundedRecoveryController,
    Pass218MaintenancePolicy,
    seal_credential_rotation_plan,
    seal_member_replacement_plan,
    seal_operational_alert_receipt,
    seal_snapshot_retention_receipt,
    validate_credential_rotation_plan,
    validate_maintenance_policy,
    validate_member_replacement_plan,
    validate_operational_alert_receipt,
    validate_recovery_status,
    validate_snapshot_retention_receipt,
)

ROOT = Path(__file__).resolve().parents[2]


def _sha(label: str) -> str:
    return sha256(label.encode("utf-8")).hexdigest()


def _h72(label: str) -> str:
    return hash72_digest({"domain": "P218-I12-TEST"}, label.encode("utf-8"))


def _policy() -> Pass218MaintenancePolicy:
    return Pass218MaintenancePolicy.build(expected_member_count=3)


def test_iteration12_declares_exact_operational_contract() -> None:
    assert PASS218_AUTHORITY_MAINTENANCE_VERSION == "HHS-P218-PRODUCTION-AUTHORITY-MAINTENANCE-I12-V1"
    assert MAINTENANCE_POLICY_SCHEMA == "HHS-P218-I12-MAINTENANCE-POLICY-V1"
    assert CREDENTIAL_ROTATION_PLAN_SCHEMA == "HHS-P218-I12-CREDENTIAL-ROTATION-PLAN-V1"
    assert MEMBER_REPLACEMENT_PLAN_SCHEMA == "HHS-P218-I12-MEMBER-REPLACEMENT-PLAN-V1"
    assert SNAPSHOT_RETENTION_RECEIPT_SCHEMA == "HHS-P218-I12-SNAPSHOT-RETENTION-RECEIPT-V1"
    assert OPERATIONAL_ALERT_RECEIPT_SCHEMA == "HHS-P218-I12-OPERATIONAL-ALERT-RECEIPT-V1"
    assert RECOVERY_STATUS_SCHEMA == "HHS-P218-I12-BOUNDED-RECOVERY-STATUS-V1"


def test_policy_requires_odd_cluster_and_preserves_quorum() -> None:
    with pytest.raises(Pass218AuthorityMaintenanceValidationError):
        Pass218MaintenancePolicy.build(expected_member_count=2)
    with pytest.raises(Pass218AuthorityMaintenanceValidationError):
        Pass218MaintenancePolicy.build(expected_member_count=4)
    with pytest.raises(Pass218AuthorityMaintenanceValidationError):
        Pass218MaintenancePolicy.build(
            expected_member_count=3,
            max_simultaneously_unavailable_members=2,
        )
    policy = _policy()
    assert policy.quorum_size == 2
    assert policy.max_simultaneously_unavailable_members == 1
    assert validate_maintenance_policy(policy.record()) == policy.record()


def test_policy_is_diagnostic_and_cannot_create_authority() -> None:
    record = _policy().record()
    assert record["client_writer_identity_hot_swap_permitted"] is False
    assert record["fresh_global_fence_after_authority_loss_required"] is True
    assert record["canonical_learning_commit_invoked"] is False
    assert record["truth_promotion"] is False
    assert record["action_authority_minted"] is False
    assert record["verbatim_source_retained"] is False
    assert record["pass165_source_retaining_path_invoked"] is False
    assert record["authoritative_float_weights"] is False


def test_credential_rotation_requires_explicit_writer_handoff() -> None:
    plan = seal_credential_rotation_plan(
        rotation_id="rotation-1",
        old_ca_sha256=_sha("old-ca"),
        new_ca_sha256=_sha("new-ca"),
        old_client_cert_sha256=_sha("old-cert"),
        new_client_cert_sha256=_sha("new-cert"),
        old_client_key_sha256=_sha("old-key"),
        new_client_key_sha256=_sha("new-key"),
        preflight_probe_hash72=_h72("probe-a"),
        current_global_fence=7,
    )
    assert validate_credential_rotation_plan(plan) == plan
    assert plan["old_writer_must_release_before_new_writer_acquires"] is True
    assert plan["new_writer_requires_strictly_newer_global_fence"] is True
    assert plan["simultaneous_writer_identities_permitted"] is False


def test_credential_rotation_rejects_identity_noop_and_tamper() -> None:
    with pytest.raises(Pass218AuthorityMaintenanceValidationError):
        seal_credential_rotation_plan(
            rotation_id="rotation-noop",
            old_ca_sha256=_sha("ca"),
            new_ca_sha256=_sha("ca"),
            old_client_cert_sha256=_sha("cert"),
            new_client_cert_sha256=_sha("cert"),
            old_client_key_sha256=_sha("key"),
            new_client_key_sha256=_sha("key"),
            preflight_probe_hash72=_h72("probe"),
            current_global_fence=1,
        )
    plan = seal_credential_rotation_plan(
        rotation_id="rotation-tamper",
        old_ca_sha256=_sha("old-ca"),
        new_ca_sha256=_sha("new-ca"),
        old_client_cert_sha256=_sha("old-cert"),
        new_client_cert_sha256=_sha("new-cert"),
        old_client_key_sha256=_sha("old-key"),
        new_client_key_sha256=_sha("new-key"),
        preflight_probe_hash72=_h72("probe"),
        current_global_fence=2,
    )
    plan["simultaneous_writer_identities_permitted"] = True
    with pytest.raises(Pass218AuthorityMaintenanceValidationError):
        validate_credential_rotation_plan(plan)


def test_member_replacement_is_serial_and_preserves_quorum() -> None:
    plan = seal_member_replacement_plan(
        replacement_id="replace-3",
        old_member_id=3,
        replacement_member_name="etcd3-new",
        replacement_peer_url="https://etcd3-new:2380",
        replacement_client_url="https://etcd3-new:2379",
        preflight_probe_hash72=_h72("full-quorum"),
        expected_member_count=3,
        quorum_size=2,
    )
    assert validate_member_replacement_plan(plan) == plan
    assert plan["maximum_members_replaced_concurrently"] == 1
    assert plan["pre_and_post_linearizable_probe_required"] is True
    assert plan["replacement_must_preserve_quorum"] is True
    assert plan["canonical_writer_identity_unchanged_by_member_identity"] is True


def test_member_replacement_rejects_invalid_cluster_shape() -> None:
    with pytest.raises(Pass218AuthorityMaintenanceValidationError):
        seal_member_replacement_plan(
            replacement_id="bad",
            old_member_id=1,
            replacement_member_name="replacement",
            replacement_peer_url="https://replacement:2380",
            replacement_client_url="https://replacement:2379",
            preflight_probe_hash72=_h72("probe"),
            expected_member_count=4,
            quorum_size=3,
        )


def test_snapshot_retention_receipt_requires_destructive_exactness_without_restart_mutation() -> None:
    policy = _policy()
    snapshots = [_sha("snapshot-1"), _sha("snapshot-2"), _sha("snapshot-3")]
    receipt = seal_snapshot_retention_receipt(
        policy=policy,
        snapshot_sha256_values=snapshots,
        rehearsal_snapshot_sha256=snapshots[-1],
        rehearsal_manifest_hash72=_h72("dr-manifest"),
        rehearsal_canonical_root_exact=True,
        rehearsal_vm81_snapshot_exact=True,
        rehearsal_consumed_receipt_exact=True,
        rehearsal_distributed_checkpoint_exact=True,
        restart_authorization_minted=False,
        restart_canonical_mutation_invoked=False,
    )
    assert validate_snapshot_retention_receipt(receipt) == receipt
    assert receipt["retained_snapshot_count"] == 3
    assert receipt["restart_authorization_minted"] is False
    assert receipt["restart_canonical_mutation_invoked"] is False


def test_snapshot_retention_rejects_nonexact_rehearsal() -> None:
    policy = _policy()
    snapshot = _sha("snapshot")
    with pytest.raises(Pass218AuthorityMaintenanceValidationError):
        seal_snapshot_retention_receipt(
            policy=policy,
            snapshot_sha256_values=[snapshot],
            rehearsal_snapshot_sha256=snapshot,
            rehearsal_manifest_hash72=_h72("manifest"),
            rehearsal_canonical_root_exact=True,
            rehearsal_vm81_snapshot_exact=False,
            rehearsal_consumed_receipt_exact=True,
            rehearsal_distributed_checkpoint_exact=True,
            restart_authorization_minted=False,
            restart_canonical_mutation_invoked=False,
        )


def test_operational_alert_receipt_is_diagnostic_only() -> None:
    alert = seal_operational_alert_receipt(
        alert_sequence=1,
        severity="critical",
        event_code="P218_I12_QUORUM_LOST",
        cluster_probe_hash72=_h72("lost"),
        global_fence=11,
        writer_authority_held=False,
        writer_authority_revoked=True,
        requires_new_global_fence=True,
    )
    assert validate_operational_alert_receipt(alert) == alert
    assert alert["severity"] == "CRITICAL"
    assert alert["diagnostic_only"] is True
    assert alert["action_authority_minted"] is False


def test_alert_rejects_revocation_without_new_fence_requirement() -> None:
    with pytest.raises(Pass218AuthorityMaintenanceValidationError):
        seal_operational_alert_receipt(
            alert_sequence=1,
            severity="WARNING",
            event_code="P218_I12_BAD_ALERT",
            cluster_probe_hash72=_h72("probe"),
            global_fence=3,
            writer_authority_held=False,
            writer_authority_revoked=True,
            requires_new_global_fence=False,
        )


def test_bounded_recovery_fails_closed_and_requires_strictly_newer_fence() -> None:
    controller = Pass218BoundedRecoveryController(_policy())
    lost = controller.record_authority_loss(
        predecessor_global_fence=19,
        cluster_probe_hash72=_h72("quorum-loss"),
    )
    assert lost["requires_new_global_fence"] is True
    with pytest.raises(Pass218AuthorityMaintenanceStateError):
        controller.begin_attempt(writer_authority_held=True)
    attempt = controller.begin_attempt(writer_authority_held=False)
    assert attempt["attempt_count"] == 1
    with pytest.raises(Pass218AuthorityMaintenanceStateError):
        controller.record_recovered_fence(
            recovered_global_fence=19,
            cluster_probe_hash72=_h72("same-fence"),
        )
    recovered = controller.record_recovered_fence(
        recovered_global_fence=20,
        cluster_probe_hash72=_h72("recovered"),
    )
    assert recovered["state"] == "RECOVERED_WITH_NEW_FENCE"
    assert recovered["requires_new_global_fence"] is False
    assert recovered["recovery_can_mint_authority"] is False
    assert recovered["recovery_can_mutate_canonical_target"] is False
    assert validate_recovery_status(recovered) == recovered


def test_bounded_recovery_stops_at_attempt_budget() -> None:
    policy = Pass218MaintenancePolicy.build(
        expected_member_count=3,
        max_automated_recovery_attempts=2,
    )
    controller = Pass218BoundedRecoveryController(policy)
    controller.record_authority_loss(
        predecessor_global_fence=3,
        cluster_probe_hash72=_h72("lost"),
    )
    controller.begin_attempt(writer_authority_held=False)
    controller.record_failed_attempt(cluster_probe_hash72=_h72("failed-1"))
    controller.begin_attempt(writer_authority_held=False)
    status = controller.record_failed_attempt(cluster_probe_hash72=_h72("failed-2"))
    assert status["state"] == "MANUAL_INTERVENTION_REQUIRED"
    with pytest.raises(Pass218AuthorityMaintenanceStateError):
        controller.begin_attempt(writer_authority_held=False)


def test_iteration12_authoritative_python_has_no_float_literals() -> None:
    path = ROOT / "hhs_runtime/pass218/authority_maintenance_i12.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    floats = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, float)
    ]
    assert floats == []
