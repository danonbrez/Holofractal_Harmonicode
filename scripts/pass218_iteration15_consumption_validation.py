#!/usr/bin/env python3
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.authority_maintenance_i12 import seal_credential_rotation_plan
from hhs_runtime.pass218.execution_i15 import (
    Pass218ExecutionReplayRejected,
    Pass218ReleaseConsumptionJournal,
    seal_execution_attestation,
    seal_execution_reconciliation,
)
from hhs_runtime.pass218.observability_i13 import seal_maintenance_run_receipt

I12 = ROOT / ".i12-evidence" / "operational-summary.json"
OUT = ROOT / ".i15-evidence"
FENCE = 4
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str, value) -> str:
    return hash72_digest({"domain": "HHS-P218-I15-REAL", "label": label}, value)


def make_release(action_hash: str, now: int, suffix: str) -> dict:
    body = {
        "schema": "HHS-P218-I14-MAINTENANCE-RELEASE-V1",
        "version": "HHS-P218-MULTI-PARTY-MAINTENANCE-APPROVAL-I14-V1",
        "policy_hash72": h72("policy", suffix),
        "action_record_hash72": action_hash,
        "action": ACTION,
        "prepared_by_operator_id": "prep",
        "preparer_message_hash72": h72("prep", suffix),
        "approver_operator_ids": ["alice", "bob"],
        "approval_message_hash72s": [h72("alice", suffix), h72("bob", suffix)],
        "executor_operator_id": "exec",
        "executor_message_hash72": h72("exec", suffix),
        "required_distinct_approvers": 2,
        "valid_distinct_approvers": 2,
        "distributed_fence_epoch": FENCE,
        "current_status_hash72": h72("status", suffix),
        "released_epoch_seconds": now,
        "expires_epoch_seconds": now + 600,
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


def preflight(release: dict) -> dict:
    return {
        "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
        "ok": True,
        "release_record_hash72": release["record_hash72"],
        "action_record_hash72": release["action_record_hash72"],
        "distributed_fence_epoch": FENCE,
        "current_status_hash72": h72("preflight", release["record_hash72"]),
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "recorded_revocations_rechecked": True,
        "maintenance_remains_external": True,
    }


def contender(root: str, release: dict, gate: dict, epoch_ns: int) -> str:
    try:
        Pass218ReleaseConsumptionJournal(root).claim_release(release=release, preflight=gate, claimed_epoch_ns=epoch_ns)
        return "CLAIMED"
    except Pass218ExecutionReplayRejected:
        return "REJECTED"


def main() -> int:
    if not I12.is_file():
        raise RuntimeError("P218_I15_I12_EVIDENCE_REQUIRED")
    i12 = json.loads(I12.read_text(encoding="utf-8"))
    global FENCE
    FENCE = int(i12["bounded_recovery"]["recovered_fence"])
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)
    root = OUT / "journal"
    now = time.time_ns() // 1_000_000_000
    action_hash = h72("action", {"fence": FENCE})
    release = make_release(action_hash, now, "primary")
    gate = preflight(release)

    with ProcessPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(
            contender,
            [str(root)] * 8,
            [release] * 8,
            [gate] * 8,
            [time.time_ns() + index for index in range(8)],
        ))
    if results.count("CLAIMED") != 1 or results.count("REJECTED") != 7:
        raise RuntimeError("P218_I15_SINGLE_WINNER_REQUIRED")

    journal = Pass218ReleaseConsumptionJournal(root)
    claim = journal.claim_for_release(release["record_hash72"])
    if claim is None:
        raise RuntimeError("P218_I15_CLAIM_NOT_DURABLE")
    restarted = Pass218ReleaseConsumptionJournal(root)
    second = make_release(action_hash, now + 1, "second")
    try:
        restarted.claim_release(release=second, preflight=preflight(second), claimed_epoch_ns=time.time_ns())
    except Pass218ExecutionReplayRejected:
        same_action_rejected = True
    else:
        same_action_rejected = False
    if not same_action_rejected:
        raise RuntimeError("P218_I15_SECOND_ACTION_ATTEMPT_NOT_REJECTED")

    rotation = i12["credential_rotation"]
    i12_record = seal_credential_rotation_plan(
        rotation_id="i15-evidence",
        old_ca_sha256="a" * 64,
        new_ca_sha256="b" * 64,
        old_client_cert_sha256="c" * 64,
        new_client_cert_sha256="d" * 64,
        old_client_key_sha256="e" * 64,
        new_client_key_sha256="f" * 64,
        preflight_probe_hash72=rotation["new_probe_hash72"],
        current_global_fence=FENCE,
    )
    attestation = seal_execution_attestation(
        claim=claim,
        outcome="SUCCEEDED",
        completed_epoch_ns=time.time_ns(),
        external_result_hash72=h72("i12-operation", rotation),
        external_operation_executed=True,
        i12_maintenance_record=i12_record,
    )
    journal.record_attestation(release_hash=release["record_hash72"], attestation=attestation)
    run = seal_maintenance_run_receipt(
        run_id="i15-real-run",
        action_record_hash72=action_hash,
        operator_id="prep",
        action=ACTION,
        outcome="SUCCEEDED",
        started_epoch_seconds=now,
        completed_epoch_seconds=now + 1,
        before_status_hash72=h72("before", FENCE),
        after_status_hash72=h72("after", FENCE),
        external_operation_executed=True,
        canonical_target_changed=False,
        authority_minted=False,
    )
    reconciliation = seal_execution_reconciliation(claim=claim, attestation=attestation, i13_run_receipt=run)
    summary = {
        "schema": "HHS-P218-I15-REAL-CONSUMPTION-VALIDATION-V1",
        "recovered_fence": FENCE,
        "process_contenders": 8,
        "claim_winners": 1,
        "claim_rejections": 7,
        "same_action_second_release_rejected": same_action_rejected,
        "restart_preserved_claim": True,
        "claim_record_hash72": claim["record_hash72"],
        "attestation_record_hash72": attestation["record_hash72"],
        "reconciliation_record_hash72": reconciliation["record_hash72"],
        "i12_rotation_plan_hash72": rotation["rotation_plan_hash72"],
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "action_authority_minted": False,
    }
    for name, value in (("claim.json", claim), ("attestation.json", attestation), ("reconciliation.json", reconciliation), ("summary.json", summary)):
        (OUT / name).write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print("PASS218_I15_REAL_ONE_TIME_CONSUMPTION=1")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
