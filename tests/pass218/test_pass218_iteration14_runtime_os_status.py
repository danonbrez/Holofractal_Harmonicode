from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_approval_i14 import (
    PASS218_I14_EVALUATE_PATH,
    PASS218_I14_PREFLIGHT_PATH,
    PASS218_I14_STATUS_PATH,
    Pass218ApprovalControlPlane,
    install_pass218_i14_approval_control_plane,
)


class EmptyJournal:
    def records(self):
        return []


class I13Stub:
    journal = EmptyJournal()

    def status(self):
        return {
            "record_hash72": "A" * 72,
            "health": "READY",
            "cluster_quorum_ready": True,
            "distributed_authority_held": True,
            "distributed_fence_epoch": 1,
        }

    def _find_action(self, _value):
        return None


def test_i14_empty_configuration_is_closed(tmp_path: Path) -> None:
    control = Pass218ApprovalControlPlane(I13Stub(), state_root=tmp_path)
    status = control.status()
    assert status["configured_operator_count"] == 0
    assert status["release_possible_from_registry"] is False
    assert status["empty_registry_is_fail_closed"] is True
    assert status["maintenance_remains_external"] is True


def test_i14_routes_are_installed_once(tmp_path: Path) -> None:
    app = FastAPI()
    first = install_pass218_i14_approval_control_plane(app, I13Stub(), state_root=tmp_path)
    second = install_pass218_i14_approval_control_plane(app, first.i13_control, state_root=tmp_path)
    assert first is second
    paths = [str(getattr(route, "path", "")) for route in app.router.routes]
    assert paths.count(PASS218_I14_STATUS_PATH) == 1
    assert paths.count(PASS218_I14_EVALUATE_PATH) == 1
    assert paths.count(PASS218_I14_PREFLIGHT_PATH) == 1


def test_i14_status_endpoint_projects_policy(tmp_path: Path) -> None:
    app = FastAPI()
    install_pass218_i14_approval_control_plane(app, I13Stub(), state_root=tmp_path)
    response = TestClient(app).get(PASS218_I14_STATUS_PATH)
    assert response.status_code == 200
    body = response.json()
    assert body["approval_threshold"] == 2
    assert body["role_counts"] == {"PREPARER": 0, "APPROVER": 0, "EXECUTOR": 0}
    assert body["canonical_authority_minted"] is False
    assert body["canonical_mutation_permitted"] is False
