from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.pass218_execution_i15_control import Pass218ExecutionControlPlane
from hhs_backend.runtime_os_pass218_consumption_i15 import (
    PASS218_I15_ATTEST_PATH,
    PASS218_I15_CLAIM_PATH,
    PASS218_I15_RECONCILE_PATH,
    PASS218_I15_STATUS_PATH,
    install_pass218_i15_consumption_control_plane,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.authority_maintenance_i12 import seal_credential_rotation_plan
from hhs_runtime.pass218.execution_i15 import Pass218ExecutionReplayRejected
from hhs_runtime.pass218.observability_i13 import Pass218OperatorJournal, seal_maintenance_run_receipt

ACTION = "PREPARE_CREDENTIAL_ROTATION"
FENCE = 9
NOW = 1_800_000_000


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I15-CONTROL-TEST"}, {"label": label})


def release() -> dict:
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
        "distributed_fence_epoch": FENCE,
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


def i12_rotation() -> dict:
    return seal_credential_rotation_plan(
        rotation_id="i15-control-rotation",
        old_ca_sha256="a" * 64,
        new_ca_sha256="b" * 64,
        old_client_cert_sha256="c" * 64,
        new_client_cert_sha256="d" * 64,
        old_client_key_sha256="e" * 64,
        new_client_key_sha256="f" * 64,
        preflight_probe_hash72=h72("probe"),
        current_global_fence=FENCE,
    )


class FakeI14:
    def preflight(self, payload):
        value = payload["release"]
        return {
            "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
            "ok": True,
            "release_record_hash72": value["record_hash72"],
            "action_record_hash72": value["action_record_hash72"],
            "distributed_fence_epoch": value["distributed_fence_epoch"],
            "current_status_hash72": h72("current-status"),
            "approval_quorum_satisfied": True,
            "separation_of_duties_satisfied": True,
            "current_quorum_satisfied": True,
            "current_writer_fence_satisfied": True,
            "recorded_revocations_rechecked": True,
            "maintenance_remains_external": True,
        }


class FakeI13:
    def __init__(self, root: Path) -> None:
        self.journal = Pass218OperatorJournal(root / "i13-journal.jsonl")

    def record_run(self, payload):
        receipt = seal_maintenance_run_receipt(
            run_id=payload["run_id"],
            action_record_hash72=payload["action_record_hash72"],
            operator_id="prep",
            action=ACTION,
            outcome=payload["outcome"],
            started_epoch_seconds=payload["started_epoch_seconds"],
            completed_epoch_seconds=max(payload["started_epoch_seconds"], NOW + 1),
            before_status_hash72=h72("before"),
            after_status_hash72=h72("after"),
            external_operation_executed=payload["external_operation_executed"],
            canonical_target_changed=False,
            authority_minted=False,
        )
        self.journal.append_run_receipt(receipt)
        return receipt


def test_i15_control_claim_attest_and_reconcile_are_durable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("hhs_backend.pass218_execution_i15_control.time.time_ns", lambda: NOW * 1_000_000_000)
    i13 = FakeI13(tmp_path)
    control = Pass218ExecutionControlPlane(i13, FakeI14(), state_root=tmp_path)
    value = release()
    claim = control.claim({"release": value})
    assert claim["release_consumed"] is True
    with pytest.raises(Pass218ExecutionReplayRejected):
        control.claim({"release": value})

    result = control.attest({
        "release_record_hash72": value["record_hash72"],
        "outcome": "SUCCEEDED",
        "external_result_hash72": h72("result"),
        "external_operation_executed": True,
        "i12_maintenance_record": i12_rotation(),
    })
    reconciliation = result["reconciliation"]
    assert reconciliation["reconciled_into_i13"] is True
    assert reconciliation["reconciled_into_i14_namespace"] is True
    assert len(i13.journal.records()) == 1
    assert control.reconcile({"release_record_hash72": value["record_hash72"]})["record_hash72"] == reconciliation["record_hash72"]

    restarted = Pass218ExecutionControlPlane(i13, FakeI14(), state_root=tmp_path)
    status = restarted.status()
    assert status["claimed_release_count"] == 1
    assert status["terminal_attestation_count"] == 1
    assert status["reconciled_release_count"] == 1
    assert status["terminal_pending_reconciliation_count"] == 0


def test_i15_status_is_read_only_and_routes_install(tmp_path: Path) -> None:
    app = FastAPI()
    control = install_pass218_i15_consumption_control_plane(app, FakeI13(tmp_path), FakeI14(), state_root=tmp_path)
    paths = {route.path for route in app.router.routes}
    assert {PASS218_I15_STATUS_PATH, PASS218_I15_CLAIM_PATH, PASS218_I15_ATTEST_PATH, PASS218_I15_RECONCILE_PATH}.issubset(paths)
    with TestClient(app) as client:
        response = client.get(PASS218_I15_STATUS_PATH)
        assert response.status_code == 200
        body = response.json()
        assert body["single_use_release_enforced"] is True
        assert body["single_execution_per_action_enforced"] is True
        assert body["maintenance_execution_remains_external"] is True
        assert body["canonical_authority_minted"] is False
        assert body["action_authority_minted"] is False
    assert control.status()["claimed_release_count"] == 0
