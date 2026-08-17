from __future__ import annotations

from typing import Any

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.commit_boundary import _canonical_bytes
from hhs_runtime.pass218.distributed_consumption_i16 import (
    Pass218DistributedConsumptionReplayRejected,
    Pass218EtcdDistributedConsumptionLedger,
)
from hhs_runtime.pass218.distributed_ownership import (
    Pass218InMemoryConsensusHarness,
    Pass218InMemoryDistributedAuthority,
)
from hhs_runtime.pass218.execution_i15 import seal_release_claim

NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I16-ETCD-CAS-TEST"}, {"label": label})


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


def claim(value: dict, ordinal: int = 0) -> dict:
    preflight = {
        "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
        "ok": True,
        "release_record_hash72": value["record_hash72"],
        "action_record_hash72": value["action_record_hash72"],
        "distributed_fence_epoch": value["distributed_fence_epoch"],
        "current_status_hash72": h72("preflight-" + value["record_hash72"]),
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "recorded_revocations_rechecked": True,
        "maintenance_remains_external": True,
    }
    return seal_release_claim(
        release=value,
        preflight=preflight,
        claimed_epoch_ns=NOW * 1_000_000_000 + ordinal,
    )


class FakeEtcdClient:
    def __init__(self) -> None:
        self.storage: dict[bytes, bytes] = {}
        self.txn_call_count = 0

    def range_value(self, key: bytes):
        value = self.storage.get(key)
        return value, None if value is None else {"version": "1"}

    def compare_version(self, key: bytes, version: int) -> dict[str, Any]:
        return {"kind": "version", "key": key, "expected": version}

    def compare_value(self, key: bytes, value: bytes) -> dict[str, Any]:
        return {"kind": "value", "key": key, "expected": value}

    def put_operation(self, key: bytes, value: bytes, *, lease_id=None) -> dict[str, Any]:
        return {"kind": "put", "key": key, "value": value}

    def txn(self, *, compare, success, failure=None):
        self.txn_call_count += 1
        ok = True
        for item in compare:
            current = self.storage.get(item["key"])
            if item["kind"] == "version":
                version = 0 if current is None else 1
                ok = ok and version == item["expected"]
            elif item["kind"] == "value":
                ok = ok and current == item["expected"]
            else:
                raise AssertionError(item)
        if ok:
            for operation in success:
                assert operation["kind"] == "put"
                self.storage[operation["key"]] = operation["value"]
        return {"succeeded": ok}


class FakeAuthority:
    def __init__(self, client: FakeEtcdClient, record: dict, namespace: str) -> None:
        self.client = client
        self._record = record
        self.namespace = namespace
        self.owner_key = (namespace + "/owner").encode()
        self.fence_key = (namespace + "/fence").encode()
        client.storage[self.owner_key] = _canonical_bytes(record)
        client.storage[self.fence_key] = str(record["fence_epoch"]).encode("ascii")

    def assert_current(self) -> dict:
        assert self.client.storage.get(self.owner_key) == _canonical_bytes(self._record)
        assert self.client.storage.get(self.fence_key) == str(self._record["fence_epoch"]).encode("ascii")
        return self._record


def ownership_records() -> tuple[dict, dict]:
    harness = Pass218InMemoryConsensusHarness()
    first = Pass218InMemoryDistributedAuthority(
        harness, owner_id="owner-a", host_id="host-a", lease_ttl_seconds=9
    )
    first_record = first.acquire()
    harness.expire_owner()
    second = Pass218InMemoryDistributedAuthority(
        harness, owner_id="owner-b", host_id="host-b", lease_ttl_seconds=9
    )
    second_record = second.acquire()
    return first_record, second_record


def test_i16_production_etcd_ledger_commits_markers_in_one_fenced_txn() -> None:
    first_record, _ = ownership_records()
    client = FakeEtcdClient()
    authority = FakeAuthority(client, first_record, "/hhs/pass218/i16-test")
    ledger = Pass218EtcdDistributedConsumptionLedger(authority)
    action_hash = h72("action")
    value = release(fence=1, action_hash=action_hash, suffix="first")
    entry = ledger.consume_claim(claim(value))

    assert client.txn_call_count == 1
    assert entry["ledger_sequence"] == 1
    assert ledger.entry_for_release(value["record_hash72"])["record_hash72"] == entry["record_hash72"]
    assert ledger.entry_for_action(action_hash)["record_hash72"] == entry["record_hash72"]
    assert ledger.entries() == [entry]


def test_i16_production_etcd_markers_survive_owner_fence_failover() -> None:
    first_record, second_record = ownership_records()
    client = FakeEtcdClient()
    namespace = "/hhs/pass218/i16-failover-test"
    first_authority = FakeAuthority(client, first_record, namespace)
    first_ledger = Pass218EtcdDistributedConsumptionLedger(first_authority)
    action_hash = h72("failover-action")
    first_release = release(fence=1, action_hash=action_hash, suffix="first")
    first_ledger.consume_claim(claim(first_release))

    second_authority = FakeAuthority(client, second_record, namespace)
    second_ledger = Pass218EtcdDistributedConsumptionLedger(second_authority)
    assert second_ledger.entries()[0]["release_record_hash72"] == first_release["record_hash72"]
    second_release = release(fence=2, action_hash=action_hash, suffix="second")
    with pytest.raises(
        Pass218DistributedConsumptionReplayRejected,
        match="ACTION_ALREADY_CONSUMED_DISTRIBUTED",
    ):
        second_ledger.consume_claim(claim(second_release, 1))
