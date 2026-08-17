#!/usr/bin/env python3
"""Real-etcd validation for Pass 218 Iteration 16 distributed consumption."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.distributed_consumption_i16 import (
    Pass218DistributedConsumptionReplayRejected,
    Pass218EtcdDistributedConsumptionLedger,
)
from hhs_runtime.pass218.distributed_ownership import Pass218EtcdDistributedAuthority
from hhs_runtime.pass218.execution_i15 import seal_release_claim

NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I16-REAL-ETCD"}, {"label": label})


def make_release(*, fence: int, action_hash: str, suffix: str) -> dict:
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


def make_claim(value: dict, *, ordinal: int) -> dict:
    preflight = {
        "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
        "ok": True,
        "release_record_hash72": value["record_hash72"],
        "action_record_hash72": value["action_record_hash72"],
        "distributed_fence_epoch": value["distributed_fence_epoch"],
        "current_status_hash72": h72("preflight-" + str(ordinal)),
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


def main() -> int:
    endpoint = os.environ.get("HHS_PASS218_I10_ETCD_TEST_ENDPOINT", "").strip()
    if not endpoint:
        raise RuntimeError("P218_I16_REAL_ETCD_ENDPOINT_REQUIRED")
    base_namespace = os.environ.get(
        "HHS_PASS218_I10_ETCD_TEST_NAMESPACE", "/hhs/pass218/i16-real-etcd"
    ).strip().rstrip("/")
    namespace = base_namespace + "/i16-consumption-proof"

    first = Pass218EtcdDistributedAuthority(
        endpoint,
        namespace=namespace,
        owner_id="i16-real-etcd-owner-a",
        host_id="i16-real-etcd-host-a",
        lease_ttl_seconds=9,
    )
    first_record = first.acquire()
    if first_record is None or first_record["fence_epoch"] != 1:
        raise RuntimeError("P218_I16_REAL_ETCD_FIRST_FENCE_REQUIRED")
    ledger_a = Pass218EtcdDistributedConsumptionLedger(first)
    action_hash = h72("action")
    release_a = make_release(fence=1, action_hash=action_hash, suffix="a")
    claim_a = make_claim(release_a, ordinal=1)
    entry = ledger_a.consume_claim(claim_a)
    if entry["ledger_sequence"] != 1:
        raise RuntimeError("P218_I16_REAL_ETCD_LEDGER_SEQUENCE_INVALID")
    if ledger_a.entry_for_release(release_a["record_hash72"])["record_hash72"] != entry["record_hash72"]:
        raise RuntimeError("P218_I16_REAL_ETCD_RELEASE_MARKER_MISSING")
    if ledger_a.entry_for_action(action_hash)["record_hash72"] != entry["record_hash72"]:
        raise RuntimeError("P218_I16_REAL_ETCD_ACTION_MARKER_MISSING")
    first.release()

    second = Pass218EtcdDistributedAuthority(
        endpoint,
        namespace=namespace,
        owner_id="i16-real-etcd-owner-b",
        host_id="i16-real-etcd-host-b",
        lease_ttl_seconds=9,
    )
    second_record = second.acquire()
    if second_record is None or second_record["fence_epoch"] != 2:
        raise RuntimeError("P218_I16_REAL_ETCD_SECOND_FENCE_REQUIRED")
    ledger_b = Pass218EtcdDistributedConsumptionLedger(second)
    entries = ledger_b.entries()
    if len(entries) != 1 or entries[0]["record_hash72"] != entry["record_hash72"]:
        raise RuntimeError("P218_I16_REAL_ETCD_FAILOVER_LEDGER_MISMATCH")

    release_b = make_release(fence=2, action_hash=action_hash, suffix="b")
    replay_rejected = False
    try:
        ledger_b.consume_claim(make_claim(release_b, ordinal=2))
    except Pass218DistributedConsumptionReplayRejected:
        replay_rejected = True
    finally:
        second.release()
    if not replay_rejected:
        raise RuntimeError("P218_I16_REAL_ETCD_ACTION_REPLAY_NOT_REJECTED")

    summary = {
        "schema": "HHS-P218-I16-REAL-ETCD-CONSUMPTION-VALIDATION-V1",
        "first_fence_epoch": first_record["fence_epoch"],
        "replacement_fence_epoch": second_record["fence_epoch"],
        "ledger_sequence": entry["ledger_sequence"],
        "entry_hash72": entry["record_hash72"],
        "release_marker_persisted": True,
        "action_marker_persisted": True,
        "successor_read_exact_entry": True,
        "same_action_second_release_rejected": True,
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "action_authority_minted": False,
    }
    out = ROOT / ".i16-evidence"
    out.mkdir(parents=True, exist_ok=True)
    (out / "real-etcd-summary.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("PASS218_I16_REAL_ETCD_FAILOVER=1")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
