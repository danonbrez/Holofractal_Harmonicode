#!/usr/bin/env python3
"""Restartable terminal validator for Pass 218 Iteration 16."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.distributed_consumption_i16 import (
    Pass218DistributedConsumptionReplayRejected,
    Pass218InMemoryDistributedConsumptionLedger,
    migrate_current_fence_local_claims,
    synchronize_distributed_claims_to_local,
)
from hhs_runtime.pass218.distributed_ownership import (
    Pass218InMemoryConsensusHarness,
    Pass218InMemoryDistributedAuthority,
)
from hhs_runtime.pass218.execution_i15 import (
    Pass218ReleaseConsumptionJournal,
    seal_release_claim,
)

OUT = ROOT / ".i16-evidence"
NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I16-VALIDATION"}, {"label": label})


def authority(harness, owner: str, host: str):
    return Pass218InMemoryDistributedAuthority(
        harness,
        owner_id=owner,
        host_id=host,
        lease_ttl_seconds=9,
    )


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


def preflight(value: dict) -> dict:
    return {
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


def claim(value: dict, ordinal: int) -> dict:
    return seal_release_claim(
        release=value,
        preflight=preflight(value),
        claimed_epoch_ns=NOW * 1_000_000_000 + ordinal,
    )


def main() -> int:
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)

    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "i16-owner-a", "i16-host-a")
    first_owner = first.acquire()
    if first_owner is None or first_owner["fence_epoch"] != 1:
        raise RuntimeError("P218_I16_FIRST_FENCE_REQUIRED")
    first_ledger = Pass218InMemoryDistributedConsumptionLedger(first)
    action_hash = h72("failover-action")
    first_release = release(fence=1, action_hash=action_hash, suffix="first")
    first_claim = claim(first_release, 1)
    distributed_entry = first_ledger.consume_claim(first_claim)

    # Deliberately model loss of the first host before its local I15 mirror is useful.
    harness.expire_owner()
    replacement = authority(harness, "i16-owner-b", "i16-host-b")
    replacement_owner = replacement.acquire()
    if replacement_owner is None or replacement_owner["fence_epoch"] != 2:
        raise RuntimeError("P218_I16_REPLACEMENT_FENCE_REQUIRED")
    replacement_ledger = Pass218InMemoryDistributedConsumptionLedger(replacement)
    replacement_journal = Pass218ReleaseConsumptionJournal(OUT / "replacement-journal")
    mirrored = synchronize_distributed_claims_to_local(
        replacement_journal, replacement_ledger
    )
    restored = replacement_journal.claim_for_release(first_release["record_hash72"])
    if mirrored != 1 or restored is None or restored["record_hash72"] != first_claim["record_hash72"]:
        raise RuntimeError("P218_I16_FAILOVER_RECONSTRUCTION_FAILED")

    second_release = release(fence=2, action_hash=action_hash, suffix="second")
    second_action_rejected = False
    try:
        replacement_ledger.consume_claim(claim(second_release, 2))
    except Pass218DistributedConsumptionReplayRejected:
        second_action_rejected = True
    if not second_action_rejected:
        raise RuntimeError("P218_I16_SECOND_ACTION_ATTEMPT_NOT_REJECTED")

    # Separate proof: a pre-I16 local claim that never reached the distributed
    # substrate may not be silently re-authored after a successor fence exists.
    stale_harness = Pass218InMemoryConsensusHarness()
    stale_first = authority(stale_harness, "stale-owner-a", "stale-host-a")
    stale_first.acquire()
    stale_journal = Pass218ReleaseConsumptionJournal(OUT / "stale-journal")
    stale_release = release(
        fence=1,
        action_hash=h72("stale-action"),
        suffix="stale",
    )
    stale_journal.claim_release(
        release=stale_release,
        preflight=preflight(stale_release),
        claimed_epoch_ns=NOW * 1_000_000_000 + 3,
    )
    stale_harness.expire_owner()
    stale_replacement = authority(
        stale_harness, "stale-owner-b", "stale-host-b"
    )
    stale_replacement.acquire()
    stale_result = migrate_current_fence_local_claims(
        stale_journal,
        Pass218InMemoryDistributedConsumptionLedger(stale_replacement),
    )
    if stale_result["stale_unreplicated_local_claim_count"] != 1:
        raise RuntimeError("P218_I16_STALE_LOCAL_CLAIM_NOT_DETECTED")
    if stale_result["migrated_local_claim_count"] != 0:
        raise RuntimeError("P218_I16_STALE_LOCAL_CLAIM_MIGRATED")

    summary = {
        "schema": "HHS-P218-I16-DISTRIBUTED-CONSUMPTION-VALIDATION-V1",
        "first_fence_epoch": first_owner["fence_epoch"],
        "replacement_fence_epoch": replacement_owner["fence_epoch"],
        "distributed_ledger_sequence": distributed_entry["ledger_sequence"],
        "distributed_entry_hash72": distributed_entry["record_hash72"],
        "claim_record_hash72": first_claim["record_hash72"],
        "replacement_reconstructed_exact_claim": True,
        "same_action_second_release_rejected": second_action_rejected,
        "stale_unreplicated_local_claim_rejected": True,
        "distributed_claim_precedes_local_mirror": True,
        "machine_loss_reopens_release": False,
        "machine_loss_reopens_prepared_action": False,
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "action_authority_minted": False,
    }
    for name, value in (
        ("distributed-entry.json", distributed_entry),
        ("restored-claim.json", restored),
        ("summary.json", summary),
    ):
        (OUT / name).write_text(
            json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
    print("PASS218_I16_DISTRIBUTED_CONSUMPTION_FAILOVER=1")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
