from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_authority_i13 import (
    PASS218_AUTHORITY_ACTION_PREPARE_PATH,
    PASS218_AUTHORITY_ALERTS_PATH,
    PASS218_AUTHORITY_RUN_RECORD_PATH,
    PASS218_AUTHORITY_STATUS_PATH,
    Pass218AuthorityControlPlane,
    install_pass218_authority_control_plane,
)


class DummyLifecycle:
    def __init__(self, *, quorum_ready: bool = True, reachable: int = 3) -> None:
        self.quorum_ready = quorum_ready
        self.reachable = reachable

    def status(self) -> dict:
        return {
            "startup_complete": True,
            "ingestion_enabled": self.quorum_ready,
            "local_authority_held": True,
            "distributed_authority_held": self.quorum_ready,
            "distributed_fence_epoch": 31 if self.quorum_ready else None,
            "cluster_quorum_ready": self.quorum_ready,
            "cluster_identity_consistent": self.quorum_ready,
            "cluster_linearizable_read_ready": self.quorum_ready,
            "cluster_expected_member_count": 3,
            "cluster_quorum_size": 2,
            "cluster_reachable_member_count": self.reachable,
            "cluster_unavailable_member_count": 3 - self.reachable,
            "cluster_id": 99,
            "cluster_member_ids": [10, 20, 30],
            "cluster_leader_ids": [20] if self.quorum_ready else [],
            "cluster_probe_hash72": None,
            "quorum_loss_count": 0,
            "quorum_recovery_count": 0,
        }


def test_control_plane_installs_exact_api_routes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HHS_PASS218_CLIENT_CERT_NOT_AFTER_EPOCH_SECONDS", "4102444800")
    monkeypatch.setenv("HHS_PASS218_LATEST_SNAPSHOT_EPOCH_SECONDS", "2000000000")
    monkeypatch.setenv("HHS_PASS218_LATEST_REHEARSAL_EPOCH_SECONDS", "2000000000")
    app = FastAPI()
    control = install_pass218_authority_control_plane(
        app,
        DummyLifecycle(),
        state_root=tmp_path,
    )
    assert isinstance(control, Pass218AuthorityControlPlane)
    paths = {str(route.path) for route in app.router.routes}
    assert PASS218_AUTHORITY_STATUS_PATH in paths
    assert PASS218_AUTHORITY_ALERTS_PATH in paths
    assert PASS218_AUTHORITY_ACTION_PREPARE_PATH in paths
    assert PASS218_AUTHORITY_RUN_RECORD_PATH in paths


def test_status_and_alert_routes_are_diagnostic_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HHS_PASS218_CLIENT_CERT_NOT_AFTER_EPOCH_SECONDS", "4102444800")
    monkeypatch.setenv("HHS_PASS218_LATEST_SNAPSHOT_EPOCH_SECONDS", "4102444700")
    monkeypatch.setenv("HHS_PASS218_LATEST_REHEARSAL_EPOCH_SECONDS", "4102444700")
    app = FastAPI()
    install_pass218_authority_control_plane(app, DummyLifecycle(), state_root=tmp_path)
    client = TestClient(app)
    status = client.get(PASS218_AUTHORITY_STATUS_PATH).json()
    assert status["schema"] == "HHS-P218-I13-AUTHORITY-OBSERVABILITY-STATUS-V1"
    assert status["canonical_authority_minted"] is False
    assert status["canonical_mutation_permitted"] is False
    alerts = client.get(PASS218_AUTHORITY_ALERTS_PATH).json()
    assert alerts["diagnostic_only"] is True
    assert alerts["canonical_authority_minted"] is False


def test_prepare_and_record_run_persist_sealed_receipts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HHS_PASS218_CLIENT_CERT_NOT_AFTER_EPOCH_SECONDS", "4102444800")
    monkeypatch.setenv("HHS_PASS218_LATEST_SNAPSHOT_EPOCH_SECONDS", "4102444700")
    monkeypatch.setenv("HHS_PASS218_LATEST_REHEARSAL_EPOCH_SECONDS", "4102444700")
    app = FastAPI()
    control = install_pass218_authority_control_plane(app, DummyLifecycle(), state_root=tmp_path)
    client = TestClient(app)
    prepared = client.post(
        PASS218_AUTHORITY_ACTION_PREPARE_PATH,
        json={
            "request_id": "operator-snapshot-1",
            "operator_id": "operator-test",
            "action": "REQUEST_SNAPSHOT_REHEARSAL",
        },
    )
    assert prepared.status_code == 200
    action = prepared.json()
    assert action["prepared_not_executed"] is True
    assert action["requires_external_executor"] is True
    assert control.journal.pending_action_count() == 1

    completed = client.post(
        PASS218_AUTHORITY_RUN_RECORD_PATH,
        json={
            "action_record_hash72": action["record_hash72"],
            "run_id": "operator-run-1",
            "outcome": "SUCCEEDED",
            "external_operation_executed": True,
            "canonical_target_changed": False,
            "authority_minted": False,
        },
    )
    assert completed.status_code == 200
    receipt = completed.json()
    assert receipt["diagnostic_receipt_only"] is True
    assert receipt["canonical_target_changed"] is False
    assert receipt["authority_minted"] is False
    assert control.journal.pending_action_count() == 0


def test_member_replacement_prepare_is_rejected_without_full_cluster(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HHS_PASS218_CLIENT_CERT_NOT_AFTER_EPOCH_SECONDS", "4102444800")
    monkeypatch.setenv("HHS_PASS218_LATEST_SNAPSHOT_EPOCH_SECONDS", "4102444700")
    monkeypatch.setenv("HHS_PASS218_LATEST_REHEARSAL_EPOCH_SECONDS", "4102444700")
    app = FastAPI()
    install_pass218_authority_control_plane(
        app,
        DummyLifecycle(quorum_ready=True, reachable=2),
        state_root=tmp_path,
    )
    client = TestClient(app)
    response = client.post(
        PASS218_AUTHORITY_ACTION_PREPARE_PATH,
        json={
            "request_id": "replace-no-full-cluster",
            "operator_id": "operator-test",
            "action": "PREPARE_MEMBER_REPLACEMENT",
        },
    )
    assert response.status_code == 409
    assert "P218_I13_FULL_CLUSTER_REQUIRED_BEFORE_MEMBER_REPLACEMENT" in response.json()["detail"]


def test_record_run_rejects_canonical_effect_claim(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HHS_PASS218_CLIENT_CERT_NOT_AFTER_EPOCH_SECONDS", "4102444800")
    monkeypatch.setenv("HHS_PASS218_LATEST_SNAPSHOT_EPOCH_SECONDS", "4102444700")
    monkeypatch.setenv("HHS_PASS218_LATEST_REHEARSAL_EPOCH_SECONDS", "4102444700")
    app = FastAPI()
    install_pass218_authority_control_plane(app, DummyLifecycle(), state_root=tmp_path)
    client = TestClient(app)
    action = client.post(
        PASS218_AUTHORITY_ACTION_PREPARE_PATH,
        json={
            "request_id": "probe-run",
            "operator_id": "operator-test",
            "action": "PROBE_CLUSTER",
        },
    ).json()
    response = client.post(
        PASS218_AUTHORITY_RUN_RECORD_PATH,
        json={
            "action_record_hash72": action["record_hash72"],
            "outcome": "SUCCEEDED",
            "external_operation_executed": False,
            "canonical_target_changed": True,
            "authority_minted": False,
        },
    )
    assert response.status_code == 409
    assert "P218_I13_RUN_CANONICAL_EFFECT_FORBIDDEN" in response.json()["detail"]
