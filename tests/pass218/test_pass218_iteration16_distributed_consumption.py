from __future__ import annotations

import ast
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.distributed_consumption_i16 import (
    PASS218_DISTRIBUTED_CONSUMPTION_VERSION,
    Pass218DistributedConsumptionReplayRejected,
    Pass218DistributedConsumptionValidationError,
    Pass218InMemoryDistributedConsumptionLedger,
    migrate_current_fence_local_claims,
    synchronize_distributed_claims_to_local,
    validate_distributed_consumption_entry,
)
from hhs_runtime.pass218.distributed_ownership import (
    Pass218InMemoryConsensusHarness,
    Pass218InMemoryDistributedAuthority,
)
from hhs_runtime.pass218.execution_i15 import (
    Pass218ReleaseConsumptionJournal,
    seal_release_claim,
)

NOW = 1_800_000_000
ACTION = "PREPARE_CREDENTIAL_ROTATION"


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I16-TEST"}, {"label": label})


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


def claim(value: dict, *, ordinal: int = 0) -> dict:
    return seal_release_claim(
        release=value,
        preflight=preflight(value),
        claimed_epoch_ns=NOW * 1_000_000_000 + ordinal,
    )


def authority(
    harness: Pass218InMemoryConsensusHarness,
    owner: str,
    host: str,
) -> Pass218InMemoryDistributedAuthority:
    return Pass218InMemoryDistributedAuthority(
        harness,
        owner_id=owner,
        host_id=host,
        lease_ttl_seconds=9,
    )


def test_i16_declares_distributed_consumption_contract() -> None:
    assert PASS218_DISTRIBUTED_CONSUMPTION_VERSION == "HHS-P218-DISTRIBUTED-CONSUMPTION-I16-V1"


def test_i16_same_fence_migrates_existing_i15_claim_once(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "owner-a", "host-a")
    assert first.acquire()["fence_epoch"] == 1
    ledger = Pass218InMemoryDistributedConsumptionLedger(first)
    journal = Pass218ReleaseConsumptionJournal(tmp_path / "journal")
    action_hash = h72("same-fence-action")
    value = release(fence=1, action_hash=action_hash, suffix="same-fence")
    local_claim = journal.claim_release(
        release=value,
        preflight=preflight(value),
        claimed_epoch_ns=NOW * 1_000_000_000,
    )

    result = migrate_current_fence_local_claims(journal, ledger)
    assert result["migrated_local_claim_count"] == 1
    assert result["stale_unreplicated_local_claim_count"] == 0
    entry = ledger.entry_for_release(value["record_hash72"])
    assert entry is not None
    assert entry["claim_record_hash72"] == local_claim["record_hash72"]
    assert entry["distributed_first"] is True
    assert entry["canonical_authority_minted"] is False


def test_i16_machine_loss_reconstructs_claim_on_replacement_host(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "owner-a", "host-a")
    assert first.acquire()["fence_epoch"] == 1
    action_hash = h72("failover-action")
    value = release(fence=1, action_hash=action_hash, suffix="primary")
    first_claim = claim(value)
    first_ledger = Pass218InMemoryDistributedConsumptionLedger(first)
    entry = first_ledger.consume_claim(first_claim)
    assert entry["ledger_sequence"] == 1

    harness.expire_owner()
    replacement = authority(harness, "owner-b", "host-b")
    assert replacement.acquire()["fence_epoch"] == 2
    replacement_ledger = Pass218InMemoryDistributedConsumptionLedger(replacement)
    empty_local = Pass218ReleaseConsumptionJournal(tmp_path / "replacement")
    assert empty_local.claim_for_release(value["record_hash72"]) is None

    mirrored = synchronize_distributed_claims_to_local(empty_local, replacement_ledger)
    assert mirrored == 1
    restored = empty_local.claim_for_release(value["record_hash72"])
    assert restored is not None
    assert restored["record_hash72"] == first_claim["record_hash72"]

    second_release = release(fence=2, action_hash=action_hash, suffix="replacement-release")
    second_claim = claim(second_release, ordinal=1)
    with pytest.raises(
        Pass218DistributedConsumptionReplayRejected,
        match="ACTION_ALREADY_CONSUMED_DISTRIBUTED",
    ):
        replacement_ledger.consume_claim(second_claim)


def test_i16_same_release_and_action_markers_are_independently_enforced() -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "owner-a", "host-a")
    first.acquire()
    ledger = Pass218InMemoryDistributedConsumptionLedger(first)
    action_hash = h72("marker-action")
    value = release(fence=1, action_hash=action_hash, suffix="marker")
    first_claim = claim(value)
    ledger.consume_claim(first_claim)

    with pytest.raises(
        Pass218DistributedConsumptionReplayRejected,
        match="RELEASE_ALREADY_CONSUMED_DISTRIBUTED",
    ):
        ledger.consume_claim(first_claim)

    alternate = release(fence=1, action_hash=action_hash, suffix="alternate")
    with pytest.raises(
        Pass218DistributedConsumptionReplayRejected,
        match="ACTION_ALREADY_CONSUMED_DISTRIBUTED",
    ):
        ledger.consume_claim(claim(alternate, ordinal=2))


def test_i16_stale_unreplicated_local_claim_is_not_reauthored(tmp_path: Path) -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "owner-a", "host-a")
    first.acquire()
    journal = Pass218ReleaseConsumptionJournal(tmp_path / "stale")
    value = release(fence=1, action_hash=h72("stale-action"), suffix="stale")
    journal.claim_release(
        release=value,
        preflight=preflight(value),
        claimed_epoch_ns=NOW * 1_000_000_000,
    )

    harness.expire_owner()
    replacement = authority(harness, "owner-b", "host-b")
    assert replacement.acquire()["fence_epoch"] == 2
    ledger = Pass218InMemoryDistributedConsumptionLedger(replacement)
    result = migrate_current_fence_local_claims(journal, ledger)
    assert result["migrated_local_claim_count"] == 0
    assert result["stale_unreplicated_local_claim_count"] == 1
    assert ledger.entry_for_release(value["record_hash72"]) is None


def test_i16_entry_tamper_is_rejected() -> None:
    harness = Pass218InMemoryConsensusHarness()
    first = authority(harness, "owner-a", "host-a")
    first.acquire()
    ledger = Pass218InMemoryDistributedConsumptionLedger(first)
    value = release(fence=1, action_hash=h72("tamper-action"), suffix="tamper")
    entry = ledger.consume_claim(claim(value))
    tampered = dict(entry)
    tampered["action_permanently_consumed"] = False
    with pytest.raises(Pass218DistributedConsumptionValidationError):
        validate_distributed_consumption_entry(tampered)


def test_i16_authoritative_modules_contain_no_float_literals() -> None:
    root = Path(__file__).resolve().parents[2]
    for rel in (
        "hhs_runtime/pass218/distributed_consumption_i16.py",
        "hhs_backend/pass218_execution_i16_control.py",
        "hhs_backend/runtime_os_pass218_consumption_i16.py",
    ):
        tree = ast.parse((root / rel).read_text(encoding="utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, rel
