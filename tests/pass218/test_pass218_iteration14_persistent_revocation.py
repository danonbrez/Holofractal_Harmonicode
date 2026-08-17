from __future__ import annotations

from pathlib import Path

import pytest

from hhs_backend import runtime_os_pass218_approval_i14 as api
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass146.engine import HHS146BoundaryEngine
from hhs_runtime.pass218.approval_i14 import (
    OPERATOR_STATEMENT_SCHEMA,
    STATEMENT_DESTINATION,
    Pass218ApprovalPolicy,
    Pass218ApprovalRejected,
    Pass218OperatorRegistry,
    seal_operator_record,
)

NOW = 1_800_000_000
FENCE = 11
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I14-PERSISTENT-REVOCATION-TEST"}, {"label": label})


def operator(operator_id: str, roles: list[str]) -> dict:
    return seal_operator_record(
        operator_id=operator_id,
        identity_id="IDN-" + operator_id,
        identity_hash72=h72("identity-" + operator_id),
        public_key_b64="pub-" + operator_id,
        public_key_fingerprint="fingerprint-" + operator_id,
        roles=roles,
    )


def registry() -> Pass218OperatorRegistry:
    return Pass218OperatorRegistry([
        operator("prep", ["PREPARER"]),
        operator("alice", ["APPROVER"]),
        operator("bob", ["APPROVER"]),
        operator("exec", ["EXECUTOR"]),
    ])


class Journal:
    def records(self):
        return []


class I13:
    journal = Journal()

    def __init__(self) -> None:
        self.action = {
            "record_hash72": h72("action"),
            "operator_id": "prep",
            "action": ACTION,
            "requires_external_executor": True,
            "prepared_not_executed": True,
        }

    def _find_action(self, action_hash: str):
        return self.action if action_hash == self.action["record_hash72"] else None

    def status(self):
        return {
            "record_hash72": h72("status"),
            "health": "READY",
            "cluster_quorum_ready": True,
            "distributed_authority_held": True,
            "distributed_fence_epoch": FENCE,
        }


def statement(reg: Pass218OperatorRegistry, operator_id: str, kind: str, action_hash: str, *, revoked: str | None = None) -> dict:
    role = {"PREPARE": "PREPARER", "APPROVE": "APPROVER", "EXECUTE": "EXECUTOR", "REVOKE": "APPROVER"}[kind]
    record = reg.get(operator_id, role=role)
    data = {
        "schema": OPERATOR_STATEMENT_SCHEMA,
        "kind": kind,
        "operator_id": operator_id,
        "action_record_hash72": action_hash,
        "action": ACTION,
        "prepared_by_operator_id": "prep",
        "distributed_fence_epoch": FENCE,
        "statement_epoch_seconds": NOW - 5,
        "expires_epoch_seconds": NOW + 300,
        "nonce": f"{operator_id}-{kind}",
    }
    if revoked is not None:
        data["revoked_message_hash72"] = revoked
    return {
        "data": data,
        "authority": {"identity_id": record["identity_id"], "identity_hash72": record["identity_hash72"]},
        "source_peer": operator_id,
        "destination_peer": STATEMENT_DESTINATION,
        "sender_public_key_b64": record["public_key_b64"],
        "sender_public_key_fingerprint": record["public_key_fingerprint"],
        "message_hash72": h72(f"message-{operator_id}-{kind}"),
    }


def test_i14_recorded_self_revocation_invalidates_later_preflight(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(HHS146BoundaryEngine, "_verify_signed_envelope", staticmethod(lambda _value: {
        "signature_valid": True,
        "envelope_hash_valid": True,
        "message_hash_valid": True,
        "data_hash_valid": True,
    }))
    monkeypatch.setattr(api, "_now", lambda: NOW)
    reg = registry()
    i13 = I13()
    control = api.Pass218ApprovalControlPlane(
        i13,
        state_root=tmp_path,
        registry=reg,
        policy=Pass218ApprovalPolicy(),
    )
    action_hash = i13.action["record_hash72"]
    alice = statement(reg, "alice", "APPROVE", action_hash)
    release = control.evaluate({
        "action_record_hash72": action_hash,
        "preparer_statement": statement(reg, "prep", "PREPARE", action_hash),
        "approval_statements": [alice, statement(reg, "bob", "APPROVE", action_hash)],
        "executor_statement": statement(reg, "exec", "EXECUTE", action_hash),
        "revocation_statements": [],
    })
    assert control.preflight({"release": release})["ok"] is True

    receipt = control.record_revocation({
        "release": release,
        "revocation_statement": statement(reg, "alice", "REVOKE", action_hash, revoked=alice["message_hash72"]),
    })
    assert receipt["preflight_invalidation_required"] is True
    assert control.revocation_journal.is_file()
    assert control.status()["recorded_revocation_count"] == 1

    with pytest.raises(Pass218ApprovalRejected, match="PREFLIGHT_APPROVAL_REVOKED"):
        control.preflight({"release": release})
