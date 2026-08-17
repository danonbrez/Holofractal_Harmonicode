from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI

from hhs_backend.pass218_execution_i16_control import Pass218DistributedExecutionControlPlane
from hhs_backend.runtime_os_pass218_consumption_i15 import (
    PASS218_I15_ATTEST_PATH,
    PASS218_I15_CLAIM_PATH,
    PASS218_I15_RECONCILE_PATH,
    PASS218_I15_STATUS_PATH,
)
from hhs_backend.runtime_os_pass218_consumption_i16 import (
    PASS218_I16_STATUS_PATH,
    PASS218_I16_SYNCHRONIZE_PATH,
    install_pass218_i16_consumption_control_plane,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.distributed_consumption_i16 import (
    Pass218DistributedConsumptionReplayRejected,
    Pass218DistributedConsumptionValidationError,
    Pass218InMemoryDistributedConsumptionLedger,
)
from hhs_runtime.pass218.distributed_ownership import (
    Pass218InMemoryConsensusHarness,
    Pass218InMemoryDistributedAuthority,
)
from hhs_runtime.pass218.execution_i15 import Pass218ReleaseConsumptionJournal
from hhs_runtime.pass218.lifecycle_i10 import Pass218DistributedRuntimeLifecycle
from hhs_runtime.pass218.lifecycle_i9 import Pass218MultiprocessRuntimeLifecycle
from hhs_runtime.pass218.observability_i13 import Pass218OperatorJournal

NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I16-CONTROL-TEST"}, {"label": label})


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


class FakeI14:
    def preflight(self, payload):
        value = payload["release"]
        return {
            "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
            "ok": True,
            "release_record_hash72": value["record_hash72"],
            "action_record_hash72": value["action_record_hash72"],
            "distributed_fence_epoch": value["distributed_fence_epoch"],
            "current_status_hash72": h72("current-" + value["record_hash72"]),
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


def authority(harness, owner: str, host: str):
    return Pass218InMemoryDistributedAuthority(
        harness,
        owner_id=owner,
        host_id=host,
        lease_ttl_seconds=9,
    )


def test_i16_distributed_receipt_survives_local_mirror_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = Pass218InMemoryConsensusHarness()
    owner = authority(harness, "owner-a", "host-a")
    owner.acquire()
    ledger = Pass218InMemoryDistributedConsumptionLedger(owner)
    control = Pass218DistributedExecutionControlPlane(
        FakeI13(tmp_path),
        FakeI14(),
        state_root=str(tmp_path),
        distributed_ledger=ledger,
    )
    value = release(fence=1, action_hash=h72("action"), suffix="primary")

    with monkeypatch.context() as patch:
        patch.setattr(
            "hhs_backend.pass218_execution_i16_control.mirror_distributed_claim_to_local",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("injected local mirror loss")),
        )
        with pytest.raises(OSError, match="local mirror loss"):
            control.claim({"release": value})

    remote = ledger.entry_for_release(value["record_hash72"])
    assert remote is not None
    assert control.journal.claim_for_release(value["record_hash72"]) is None

    result = control.synchronize()
    assert result["mirrored"] == 1
    restored = control.journal.claim_for_release(value["record_hash72"])
    assert restored is not None
    assert restored["record_hash72"] == remote["claim_record_hash72"]
    with pytest.raises(Pass218DistributedConsumptionReplayRejected):
        control.claim({"release": value})


def test_i16_stale_local_only_claim_blocks_new_distributed_claims(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "owner-a", "host-a")
    first.acquire()
    journal = Pass218ReleaseConsumptionJournal(tmp_path / "i15" / "consumption")
    stale = release(fence=1, action_hash=h72("stale-action"), suffix="stale")
    journal.claim_release(
        release=stale,
        preflight=FakeI14().preflight({"release": stale}),
        claimed_epoch_ns=NOW * 1_000_000_000,
    )

    harness.expire_owner()
    replacement = authority(harness, "owner-b", "host-b")
    replacement.acquire()
    control = Pass218DistributedExecutionControlPlane(
        FakeI13(tmp_path),
        FakeI14(),
        state_root=str(tmp_path),
        distributed_ledger=Pass218InMemoryDistributedConsumptionLedger(replacement),
    )
    with pytest.raises(
        Pass218DistributedConsumptionValidationError,
        match="STALE_UNREPLICATED_LOCAL_CLAIM",
    ):
        control.synchronize()
    fresh = release(fence=2, action_hash=h72("fresh-action"), suffix="fresh")
    with pytest.raises(
        Pass218DistributedConsumptionValidationError,
        match="STALE_UNREPLICATED_LOCAL_CLAIM",
    ):
        control.claim({"release": fresh})


def test_i16_runtime_installer_preserves_i15_paths_and_adds_i16_paths(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    distributed = Pass218DistributedRuntimeLifecycle(
        tmp_path / "lifecycle",
        distributed_authority=authority(harness, "owner-a", "host-a"),
        owner_id="local-a",
    )
    app = FastAPI()
    control = install_pass218_i16_consumption_control_plane(
        app,
        distributed,
        FakeI13(tmp_path),
        FakeI14(),
        state_root=tmp_path,
    )
    paths = {route.path for route in app.router.routes}
    assert {
        PASS218_I15_STATUS_PATH,
        PASS218_I15_CLAIM_PATH,
        PASS218_I15_ATTEST_PATH,
        PASS218_I15_RECONCILE_PATH,
        PASS218_I16_STATUS_PATH,
        PASS218_I16_SYNCHRONIZE_PATH,
    }.issubset(paths)
    assert control.distributed_ledger is not None


def test_i16_local_i9_installation_retains_i15_local_semantics(tmp_path: Path) -> None:
    local = Pass218MultiprocessRuntimeLifecycle(tmp_path / "local")
    app = FastAPI()
    control = install_pass218_i16_consumption_control_plane(
        app,
        local,
        FakeI13(tmp_path),
        FakeI14(),
        state_root=tmp_path,
    )
    assert control.distributed_ledger is None
    status = control.distributed_status()
    assert status["distributed_consumption_configured"] is False
    assert status["canonical_authority_minted"] is False
