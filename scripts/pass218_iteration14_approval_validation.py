#!/usr/bin/env python3
"""Validate I14 with real inherited Pass 146 signed statements."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime_os_pass218_authority_i13 import Pass218AuthorityControlPlane
from hhs_backend.runtime_os_pass218_approval_i14 import Pass218ApprovalControlPlane
from hhs_runtime.pass146.service import HHS146Service
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

I12_EVIDENCE = ROOT / ".i12-evidence"
I14_EVIDENCE = ROOT / ".i14-evidence"


class EvidenceLifecycle:
    def __init__(self, i12: dict) -> None:
        self.fence = int(i12["bounded_recovery"]["recovered_fence"])
        self.member_ids = list(i12["member_replacement"]["member_ids"])
        self.reachable = int(i12["member_replacement"]["reachable_member_count"])
        self.probe = i12["member_replacement"]["post_probe_hash72"]

    def status(self) -> dict:
        return {
            "startup_complete": True,
            "ingestion_enabled": True,
            "local_authority_held": True,
            "distributed_authority_held": True,
            "distributed_fence_epoch": self.fence,
            "cluster_quorum_ready": True,
            "cluster_identity_consistent": True,
            "cluster_linearizable_read_ready": True,
            "cluster_expected_member_count": 3,
            "cluster_quorum_size": 2,
            "cluster_reachable_member_count": self.reachable,
            "cluster_unavailable_member_count": 0,
            "cluster_id": None,
            "cluster_member_ids": self.member_ids,
            "cluster_leader_ids": [],
            "cluster_probe_hash72": self.probe,
            "quorum_loss_count": 1,
            "quorum_recovery_count": 1,
        }


def statement_data(*, kind: str, operator_id: str, action: dict, fence: int, now: int, revoked_message_hash72: str | None = None) -> dict:
    value = {
        "schema": OPERATOR_STATEMENT_SCHEMA,
        "kind": kind,
        "operator_id": operator_id,
        "action_record_hash72": action["record_hash72"],
        "action": action["action"],
        "prepared_by_operator_id": action["operator_id"],
        "distributed_fence_epoch": fence,
        "statement_epoch_seconds": now,
        "expires_epoch_seconds": now + 300,
        "nonce": f"i14-{kind.lower()}-{operator_id}-{now}",
    }
    if revoked_message_hash72 is not None:
        value["revoked_message_hash72"] = revoked_message_hash72
    return value


def signed_statement(service: HHS146Service, actor: dict, alias: str, data: dict) -> dict:
    contract = service.security.construct_path(
        actor["identity_id"],
        actor["grant_id"],
        actor["token"],
        "PROPAGATE",
        {
            "data": data,
            "source_peer": alias,
            "destination_peer": STATEMENT_DESTINATION,
            "classification": "INTERNAL",
            "provenance": {"pass": 218, "iteration": 14},
        },
        destination={"kind": "PEER", "id": STATEMENT_DESTINATION},
    )
    executed = service.security.execute_path(
        contract["result"]["contract_id"],
        actor["identity_id"],
        actor["token"],
    )
    message_id = executed["result"]["result"]["message_id"]
    inspected = service.security.inspect_message(message_id)
    if inspected["integrity_valid"] is not True:
        raise RuntimeError("P218_I14_PASS146_STATEMENT_NOT_VALID")
    return inspected["envelope"]


def create_actor(service: HHS146Service, root: dict, alias: str, role: str) -> tuple[dict, dict]:
    created = service.security.create_identity(
        root["identity_id"], root["grant_id"], root["token"], f"Pass218 I14 {alias}"
    )
    identity_id = created["result"]["identity_id"]
    token = created["authentication_token"]
    grant = service.security.create_grant(
        root["identity_id"],
        root["grant_id"],
        root["token"],
        identity_id,
        capabilities=["NETWORK", "NETWORK_SEND", "PATH_EXECUTION"],
        operations=["PROPAGATE"],
        sources=["*"],
        destinations=[STATEMENT_DESTINATION],
        disclosure_policy={"classifications": ["INTERNAL"], "allow_remote": False},
    )
    actor = {
        "identity_id": identity_id,
        "grant_id": grant["result"]["grant_id"],
        "token": token,
    }
    public = service.security.identity_public_record(identity_id)
    record = seal_operator_record(
        operator_id=alias,
        identity_id=identity_id,
        identity_hash72=public["identity_hash72"],
        public_key_b64=public["public_key_b64"],
        public_key_fingerprint=public["public_key_fingerprint"],
        roles=[role],
    )
    return actor, record


def main() -> int:
    i12_path = I12_EVIDENCE / "operational-summary.json"
    if not i12_path.is_file():
        raise RuntimeError("P218_I14_REAL_I12_EVIDENCE_REQUIRED")
    i12 = json.loads(i12_path.read_text(encoding="utf-8"))
    now = time.time_ns() // 1_000_000_000
    os.environ["HHS_PASS218_CLIENT_CERT_NOT_AFTER_EPOCH_SECONDS"] = str(now + 31_536_000)
    os.environ["HHS_PASS218_LATEST_SNAPSHOT_EPOCH_SECONDS"] = str(now)
    os.environ["HHS_PASS218_LATEST_REHEARSAL_EPOCH_SECONDS"] = str(now)

    I14_EVIDENCE.mkdir(parents=True, exist_ok=True)
    lifecycle = EvidenceLifecycle(i12)
    i13 = Pass218AuthorityControlPlane(lifecycle, state_root=I14_EVIDENCE / "runtime-state")
    action = i13.prepare_action({
        "request_id": "i14-real-credential-rotation-preparation",
        "operator_id": "prep",
        "action": "PREPARE_CREDENTIAL_ROTATION",
    })
    current_status = i13.status()
    if current_status["health"] != "READY":
        raise RuntimeError("P218_I14_I13_STATUS_NOT_READY")

    db_path = I14_EVIDENCE / "pass146-operators.sqlite3"
    if db_path.exists():
        db_path.unlink()
    with HHS146Service(db_path) as service:
        boot = service.security.bootstrap_local_owner("Pass218 I14 Root")
        root = {
            "identity_id": boot["result"]["identity_id"],
            "grant_id": boot["result"]["grant_id"],
            "token": boot["authentication_token"],
        }
        actors: dict[str, dict] = {}
        records: list[dict] = []
        for alias, role in (
            ("prep", "PREPARER"),
            ("alice", "APPROVER"),
            ("bob", "APPROVER"),
            ("carol", "APPROVER"),
            ("exec", "EXECUTOR"),
        ):
            actors[alias], record = create_actor(service, root, alias, role)
            records.append(record)
        registry = Pass218OperatorRegistry(records)
        (I14_EVIDENCE / "operator-registry.json").write_text(
            json.dumps({"schema": "HHS-P218-I14-OPERATOR-REGISTRY-V1", "operators": records}, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        fence = int(current_status["distributed_fence_epoch"])
        prep = signed_statement(service, actors["prep"], "prep", statement_data(kind="PREPARE", operator_id="prep", action=action, fence=fence, now=now))
        alice = signed_statement(service, actors["alice"], "alice", statement_data(kind="APPROVE", operator_id="alice", action=action, fence=fence, now=now))
        bob = signed_statement(service, actors["bob"], "bob", statement_data(kind="APPROVE", operator_id="bob", action=action, fence=fence, now=now))
        executor = signed_statement(service, actors["exec"], "exec", statement_data(kind="EXECUTE", operator_id="exec", action=action, fence=fence, now=now))

        policy = Pass218ApprovalPolicy(required_distinct_approvers=2, approval_ttl_seconds=1800, release_ttl_seconds=600)
        release = evaluate_maintenance_release(
            action_record=action,
            current_status=current_status,
            preparer_statement=prep,
            approval_statements=[alice, bob],
            executor_statement=executor,
            revocation_statements=[],
            registry=registry,
            policy=policy,
            now_epoch_seconds=now,
        )
        validate_maintenance_release(release, now_epoch_seconds=now)

        one_approval_rejected = False
        try:
            evaluate_maintenance_release(
                action_record=action,
                current_status=current_status,
                preparer_statement=prep,
                approval_statements=[alice],
                executor_statement=executor,
                revocation_statements=[],
                registry=registry,
                policy=policy,
                now_epoch_seconds=now,
            )
        except Pass218ApprovalRejected:
            one_approval_rejected = True
        if not one_approval_rejected:
            raise RuntimeError("P218_I14_ONE_APPROVAL_NOT_REJECTED")

        revoke_alice = signed_statement(
            service,
            actors["carol"],
            "carol",
            statement_data(
                kind="REVOKE",
                operator_id="carol",
                action=action,
                fence=fence,
                now=now,
                revoked_message_hash72=alice["message_hash72"],
            ),
        )
        revocation_rejected = False
        try:
            evaluate_maintenance_release(
                action_record=action,
                current_status=current_status,
                preparer_statement=prep,
                approval_statements=[alice, bob],
                executor_statement=executor,
                revocation_statements=[revoke_alice],
                registry=registry,
                policy=policy,
                now_epoch_seconds=now,
            )
        except Pass218ApprovalRejected:
            revocation_rejected = True
        if not revocation_rejected:
            raise RuntimeError("P218_I14_REVOCATION_NOT_ENFORCED")

        tampered = copy.deepcopy(alice)
        tampered["message_hash72"] = bob["message_hash72"]
        tamper_rejected = False
        try:
            evaluate_maintenance_release(
                action_record=action,
                current_status=current_status,
                preparer_statement=prep,
                approval_statements=[tampered, bob],
                executor_statement=executor,
                revocation_statements=[],
                registry=registry,
                policy=policy,
                now_epoch_seconds=now,
            )
        except Pass218ApprovalRejected:
            tamper_rejected = True
        if not tamper_rejected:
            raise RuntimeError("P218_I14_TAMPER_NOT_REJECTED")

    i14_control = Pass218ApprovalControlPlane(
        i13,
        state_root=I14_EVIDENCE / "runtime-state",
        registry=registry,
        policy=policy,
    )
    preflight = i14_control.preflight({"release": release})
    if preflight["ok"] is not True:
        raise RuntimeError("P218_I14_PREFLIGHT_NOT_READY")
    lifecycle.fence += 1
    fence_change_rejected = False
    try:
        i14_control.preflight({"release": release})
    except Pass218ApprovalRejected:
        fence_change_rejected = True
    if not fence_change_rejected:
        raise RuntimeError("P218_I14_FENCE_CHANGE_NOT_REJECTED")
    lifecycle.fence -= 1

    summary = {
        "schema": "HHS-P218-I14-REAL-APPROVAL-VALIDATION-V1",
        "i12_recovered_fence": i12["bounded_recovery"]["recovered_fence"],
        "i14_action_record_hash72": action["record_hash72"],
        "i14_release_record_hash72": release["record_hash72"],
        "i14_preflight_status_hash72": preflight["current_status_hash72"],
        "i14_required_distinct_approvers": release["required_distinct_approvers"],
        "i14_approver_operator_ids": release["approver_operator_ids"],
        "i14_executor_operator_id": release["executor_operator_id"],
        "real_pass146_statements": True,
        "one_approval_rejected": one_approval_rejected,
        "revocation_enforced": revocation_rejected,
        "tamper_rejected": tamper_rejected,
        "fence_change_rejected": fence_change_rejected,
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
    (I14_EVIDENCE / "real-approval-summary.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("PASS218_I14_REAL_MULTI_PARTY_APPROVAL=1")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
