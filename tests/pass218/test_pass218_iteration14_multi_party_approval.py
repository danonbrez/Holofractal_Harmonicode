from __future__ import annotations

import copy

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass146.engine import HHS146BoundaryEngine
from hhs_runtime.pass218.approval_i14 import (
    OPERATOR_STATEMENT_SCHEMA,
    STATEMENT_DESTINATION,
    Pass218ApprovalPolicy,
    Pass218ApprovalRejected,
    Pass218OperatorRegistry,
    evaluate_maintenance_release,
    seal_operator_record,
    validate_maintenance_release,
)

NOW = 1_800_000_000
FENCE = 9
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I14-TEST"}, {"label": label})


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
def registry() -> Pass218OperatorRegistry:
    return Pass218OperatorRegistry([
        operator("prep", ["PREPARER"]),
        operator("alice", ["APPROVER"]),
        operator("bob", ["APPROVER"]),
        operator("carol", ["APPROVER"]),
        operator("exec", ["EXECUTOR"]),
        operator("dual", ["APPROVER", "EXECUTOR"]),
    ])


@pytest.fixture(autouse=True)
def inherited_pass146_verifier(monkeypatch: pytest.MonkeyPatch) -> None:
    def verified(_envelope):
        return {
            "signature_valid": True,
            "envelope_hash_valid": True,
            "message_hash_valid": True,
            "data_hash_valid": True,
        }
    monkeypatch.setattr(HHS146BoundaryEngine, "_verify_signed_envelope", staticmethod(verified))


def statement(registry: Pass218OperatorRegistry, operator_id: str, kind: str, action_hash: str, *, preparer: str = "prep", fence: int = FENCE, epoch: int = NOW - 5, expires: int = NOW + 300, nonce: str | None = None, revoked_message_hash72: str | None = None, message_label: str | None = None) -> dict:
    record = registry.get(operator_id, role={"PREPARE": "PREPARER", "APPROVE": "APPROVER", "EXECUTE": "EXECUTOR", "REVOKE": "APPROVER"}[kind])
    data = {
        "schema": OPERATOR_STATEMENT_SCHEMA,
        "kind": kind,
        "operator_id": operator_id,
        "action_record_hash72": action_hash,
        "action": ACTION,
        "prepared_by_operator_id": preparer,
        "distributed_fence_epoch": fence,
        "statement_epoch_seconds": epoch,
        "expires_epoch_seconds": expires,
        "nonce": nonce or f"nonce-{operator_id}-{kind}",
    }
    if revoked_message_hash72 is not None:
        data["revoked_message_hash72"] = revoked_message_hash72
    return {
        "data": data,
        "authority": {
            "identity_id": record["identity_id"],
            "identity_hash72": record["identity_hash72"],
        },
        "source_peer": operator_id,
        "destination_peer": STATEMENT_DESTINATION,
        "sender_public_key_b64": record["public_key_b64"],
        "sender_public_key_fingerprint": record["public_key_fingerprint"],
        "message_hash72": h72(message_label or f"message-{operator_id}-{kind}-{nonce or 'default'}"),
    }


def action_record() -> dict:
    return {
        "record_hash72": h72("action"),
        "operator_id": "prep",
        "action": ACTION,
        "requires_external_executor": True,
        "prepared_not_executed": True,
    }


def status(*, fence: int = FENCE, quorum: bool = True, held: bool = True, health: str = "READY") -> dict:
    return {
        "record_hash72": h72(f"status-{fence}-{quorum}-{held}-{health}"),
        "health": health,
        "cluster_quorum_ready": quorum,
        "distributed_authority_held": held,
        "distributed_fence_epoch": fence,
    }


def valid_inputs(registry: Pass218OperatorRegistry) -> dict:
    action = action_record()
    return {
        "action_record": action,
        "current_status": status(),
        "preparer_statement": statement(registry, "prep", "PREPARE", action["record_hash72"]),
        "approval_statements": [
            statement(registry, "alice", "APPROVE", action["record_hash72"], message_label="alice-approval"),
            statement(registry, "bob", "APPROVE", action["record_hash72"], message_label="bob-approval"),
        ],
        "executor_statement": statement(registry, "exec", "EXECUTE", action["record_hash72"]),
        "revocation_statements": [],
        "registry": registry,
        "policy": Pass218ApprovalPolicy(),
        "now_epoch_seconds": NOW,
    }


def test_i14_valid_release_requires_two_distinct_approvers_and_distinct_executor(registry: Pass218OperatorRegistry) -> None:
    release = evaluate_maintenance_release(**valid_inputs(registry))
    assert release["approval_quorum_satisfied"] is True
    assert release["separation_of_duties_satisfied"] is True
    assert release["pass146_statement_integrity_satisfied"] is True
    assert release["current_quorum_satisfied"] is True
    assert release["current_writer_fence_satisfied"] is True
    assert release["external_maintenance_preconditions_satisfied"] is True
    assert release["maintenance_remains_external"] is True
    assert release["approver_operator_ids"] == ["alice", "bob"]
    assert release["executor_operator_id"] == "exec"
    assert release["canonical_authority_minted"] is False
    assert release["canonical_mutation_permitted"] is False
    validate_maintenance_release(release, now_epoch_seconds=NOW)


def test_i14_zero_or_one_approval_fails_closed(registry: Pass218OperatorRegistry) -> None:
    values = valid_inputs(registry)
    for approvals in ([], values["approval_statements"][:1]):
        candidate = dict(values)
        candidate["approval_statements"] = approvals
        with pytest.raises(Pass218ApprovalRejected, match="APPROVAL_QUORUM_NOT_MET"):
            evaluate_maintenance_release(**candidate)


def test_i14_duplicate_approver_does_not_satisfy_threshold(registry: Pass218OperatorRegistry) -> None:
    values = valid_inputs(registry)
    action_hash = values["action_record"]["record_hash72"]
    values["approval_statements"] = [
        statement(registry, "alice", "APPROVE", action_hash, nonce="a", message_label="alice-a"),
        statement(registry, "alice", "APPROVE", action_hash, nonce="b", message_label="alice-b"),
    ]
    with pytest.raises(Pass218ApprovalRejected, match="APPROVAL_QUORUM_NOT_MET"):
        evaluate_maintenance_release(**values)


def test_i14_preparer_self_approval_never_counts(registry: Pass218OperatorRegistry) -> None:
    records = registry.records() + [operator("prep-approver", ["PREPARER", "APPROVER"])]
    special = Pass218OperatorRegistry(records)
    action = action_record()
    action["operator_id"] = "prep-approver"
    action_hash = action["record_hash72"]
    values = {
        "action_record": action,
        "current_status": status(),
        "preparer_statement": statement(special, "prep-approver", "PREPARE", action_hash, preparer="prep-approver"),
        "approval_statements": [
            statement(special, "prep-approver", "APPROVE", action_hash, preparer="prep-approver"),
            statement(special, "alice", "APPROVE", action_hash, preparer="prep-approver"),
        ],
        "executor_statement": statement(special, "exec", "EXECUTE", action_hash, preparer="prep-approver"),
        "revocation_statements": [],
        "registry": special,
        "policy": Pass218ApprovalPolicy(),
        "now_epoch_seconds": NOW,
    }
    with pytest.raises(Pass218ApprovalRejected, match="APPROVAL_QUORUM_NOT_MET"):
        evaluate_maintenance_release(**values)


def test_i14_executor_cannot_overlap_counted_approver(registry: Pass218OperatorRegistry) -> None:
    values = valid_inputs(registry)
    action_hash = values["action_record"]["record_hash72"]
    values["approval_statements"] = [
        statement(registry, "alice", "APPROVE", action_hash),
        statement(registry, "dual", "APPROVE", action_hash),
    ]
    values["executor_statement"] = statement(registry, "dual", "EXECUTE", action_hash)
    with pytest.raises(Pass218ApprovalRejected, match="EXECUTOR_SEPARATION_VIOLATION"):
        evaluate_maintenance_release(**values)


def test_i14_expired_approval_fails_closed(registry: Pass218OperatorRegistry) -> None:
    values = valid_inputs(registry)
    action_hash = values["action_record"]["record_hash72"]
    values["approval_statements"][0] = statement(registry, "alice", "APPROVE", action_hash, epoch=NOW - 100, expires=NOW)
    with pytest.raises(Pass218ApprovalRejected, match="EXPIRED_OR_NOT_YET_VALID"):
        evaluate_maintenance_release(**values)


def test_i14_revocation_removes_approval_from_quorum(registry: Pass218OperatorRegistry) -> None:
    values = valid_inputs(registry)
    action_hash = values["action_record"]["record_hash72"]
    revoked_hash = values["approval_statements"][0]["message_hash72"]
    values["revocation_statements"] = [
        statement(registry, "carol", "REVOKE", action_hash, revoked_message_hash72=revoked_hash, message_label="revoke-alice")
    ]
    with pytest.raises(Pass218ApprovalRejected, match="APPROVAL_QUORUM_NOT_MET"):
        evaluate_maintenance_release(**values)


@pytest.mark.parametrize(
    "runtime_status",
    [
        status(quorum=False, health="BLOCKED"),
        status(held=False, health="DEGRADED"),
        status(fence=FENCE + 1),
    ],
)
def test_i14_runtime_or_fence_change_invalidates_release(registry: Pass218OperatorRegistry, runtime_status: dict) -> None:
    values = valid_inputs(registry)
    values["current_status"] = runtime_status
    with pytest.raises(Pass218ApprovalRejected):
        evaluate_maintenance_release(**values)


def test_i14_invalid_pass146_statement_is_rejected(registry: Pass218OperatorRegistry, monkeypatch: pytest.MonkeyPatch) -> None:
    def rejected(_envelope):
        raise ValueError("bad envelope")
    monkeypatch.setattr(HHS146BoundaryEngine, "_verify_signed_envelope", staticmethod(rejected))
    with pytest.raises(Pass218ApprovalRejected, match="PASS146_STATEMENT_INVALID"):
        evaluate_maintenance_release(**valid_inputs(registry))


def test_i14_release_expiry_is_enforced(registry: Pass218OperatorRegistry) -> None:
    release = evaluate_maintenance_release(**valid_inputs(registry))
    with pytest.raises(Pass218ApprovalRejected, match="RELEASE_EXPIRED"):
        validate_maintenance_release(release, now_epoch_seconds=release["expires_epoch_seconds"])


def test_i14_release_tamper_is_detected(registry: Pass218OperatorRegistry) -> None:
    release = evaluate_maintenance_release(**valid_inputs(registry))
    tampered = copy.deepcopy(release)
    tampered["executor_operator_id"] = "alice"
    with pytest.raises(Exception):
        validate_maintenance_release(tampered, now_epoch_seconds=NOW)
