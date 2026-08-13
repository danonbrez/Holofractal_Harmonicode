from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.runtime_os_pass218_approval_i14 import (
    PASS218_I14_EVALUATE_PATH,
    PASS218_I14_PREFLIGHT_PATH,
    PASS218_I14_STATUS_PATH,
    Pass218ApprovalControlPlane,
    install_pass218_i14_approval_control_plane,
)
from hhs_backend.runtime_os_pass218_consumption_i15 import (
    PASS218_I15_ATTEST_PATH,
    PASS218_I15_CLAIM_PATH,
    PASS218_I15_RECONCILE_PATH,
    PASS218_I15_STATUS_PATH,
    install_pass218_i15_consumption_control_plane,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.consumption_recovery_i15 import repair_consumption_indexes
from hhs_runtime.pass218.execution_i15 import (
    Pass218ExecutionReplayRejected,
    Pass218ReleaseConsumptionJournal,
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


def _h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I15-RUNTIME-INTEGRATION"}, {"label": label})


def _release(suffix: str) -> dict:
    body = {
        "schema": "HHS-P218-I14-MAINTENANCE-RELEASE-V1",
        "version": "HHS-P218-MULTI-PARTY-MAINTENANCE-APPROVAL-I14-V1",
        "policy_hash72": _h72("policy-" + suffix),
        "action_record_hash72": _h72("shared-action"),
        "action": "PREPARE_CREDENTIAL_ROTATION",
        "prepared_by_operator_id": "prep",
        "preparer_message_hash72": _h72("prep-" + suffix),
        "approver_operator_ids": ["alice", "bob"],
        "approval_message_hash72s": [_h72("alice-" + suffix), _h72("bob-" + suffix)],
        "executor_operator_id": "exec",
        "executor_message_hash72": _h72("exec-" + suffix),
        "required_distinct_approvers": 2,
        "valid_distinct_approvers": 2,
        "distributed_fence_epoch": 1,
        "current_status_hash72": _h72("status-" + suffix),
        "released_epoch_seconds": 1_800_000_000,
        "expires_epoch_seconds": 1_800_000_600,
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


def _preflight(value: dict, suffix: str) -> dict:
    return {
        "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
        "ok": True,
        "release_record_hash72": value["record_hash72"],
        "action_record_hash72": value["action_record_hash72"],
        "distributed_fence_epoch": 1,
        "current_status_hash72": _h72("preflight-" + suffix),
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "recorded_revocations_rechecked": True,
        "maintenance_remains_external": True,
    }


def test_i15_runtime_routes_and_read_only_status_are_installed(tmp_path: Path) -> None:
    app = FastAPI()
    i14 = install_pass218_i14_approval_control_plane(app, I13Stub(), state_root=tmp_path)
    i15 = install_pass218_i15_consumption_control_plane(app, I13Stub(), i14, state_root=tmp_path)
    paths = {str(getattr(route, "path", "")) for route in app.router.routes}
    assert {PASS218_I15_STATUS_PATH, PASS218_I15_CLAIM_PATH, PASS218_I15_ATTEST_PATH, PASS218_I15_RECONCILE_PATH}.issubset(paths)
    response = TestClient(app).get(PASS218_I15_STATUS_PATH)
    assert response.status_code == 200
    status = response.json()
    assert status["claimed_release_count"] == 0
    assert status["single_use_release_enforced"] is True
    assert status["maintenance_execution_remains_external"] is True
    assert i15.status()["canonical_authority_minted"] is False


def test_i15_restart_repairs_missing_action_index_before_second_release(tmp_path: Path) -> None:
    root = tmp_path / "i15-consumption"
    first = _release("first")
    journal = Pass218ReleaseConsumptionJournal(root)
    journal.claim_release(
        release=first,
        preflight=_preflight(first, "first"),
        claimed_epoch_ns=1_800_000_000_000_000_000,
    )
    index_path = journal._action_path(first["action_record_hash72"])
    index_path.unlink()
    restarted = Pass218ReleaseConsumptionJournal(root)
    assert repair_consumption_indexes(restarted) == 1
    assert index_path.is_file()

    second = _release("second")
    assert second["record_hash72"] != first["record_hash72"]
    with pytest.raises(Pass218ExecutionReplayRejected, match="ACTION_ALREADY_CLAIMED"):
        restarted.claim_release(
            release=second,
            preflight=_preflight(second, "second"),
            claimed_epoch_ns=1_800_000_000_000_000_001,
        )


def test_i15_dedicated_suites_run_from_cumulative_gate() -> None:
    result = pytest.main([
        "-q",
        "tests/pass218/test_pass218_iteration15_one_time_consumption.py",
        "tests/pass218/test_pass218_iteration15_runtime_control.py",
        "tests/pass218/test_pass218_iteration15_parallel_reservation.py",
    ])
    assert result == pytest.ExitCode.OK
