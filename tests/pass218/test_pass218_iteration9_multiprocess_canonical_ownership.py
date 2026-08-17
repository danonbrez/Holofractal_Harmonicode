from __future__ import annotations

import ast
from hashlib import sha256
import json
import multiprocessing
from pathlib import Path

import pytest
from fastapi import FastAPI

from hhs_backend.runtime_os_pass218_lifecycle import install_pass218_runtime_os_lifecycle
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218 import (
    ClosedTransactionVectorVM5184Adapter,
    MULTIPROCESS_LIFECYCLE_STATUS_SCHEMA,
    OWNERSHIP_LOCK_STRATEGY,
    OWNERSHIP_RECORD_SCHEMA,
    OWNERSHIP_SCOPE,
    PASS218_MULTIPROCESS_LIFECYCLE_VERSION,
    PASS218_OWNERSHIP_VERSION,
    Pass218CanonicalOwnershipLease,
    Pass218MultiprocessRuntimeLifecycle,
    Pass218OwnershipFenceLost,
    Pass218OwnershipValidationError,
    Pass218RuntimeLifecycleNotReady,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
    seal_ownership_record,
    validate_ownership_record,
)

ROOT = Path(__file__).resolve().parents[2]


def _source(label: str = "A") -> str:
    return (
        "A synthetic narrative exists only to test Iteration 9 process fencing "
        f"{label}. It must never be retained. A second sentence ensures a "
        "non-empty deterministic structural projection."
    )


def _beat(ordinal: int, label: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "ordinal": ordinal,
        "source_span_sha256": sha256(
            f"iteration9-span-{ordinal}-{label}".encode("utf-8")
        ).hexdigest(),
        "paragraph_count": 1,
        "token_count": 19 + ordinal,
        "sentence_count": 1,
        "dialogue_turn_count": ordinal % 2,
        "perspective_counts": {"first_person": 0, "second_person": 0, "third_person": 1},
        "negation_count": 1,
        "modal_count": 1,
        "authority_count": 1,
        "temporal_count": 1,
        "dominant_perspective": "THIRD_PERSON",
        "relation_types": ["TEMPORAL_SUCCESSION"],
        "distinction_mentions": [],
        "verbatim_source_retained": False,
    }
    payload["beat_hash72"] = hash72_digest(
        {"domain": "HHS-P218-NARRATIVE-BEAT-I2-V1"}, payload
    )
    return payload


def _hydration(label: str = "A") -> dict[str, object]:
    source = _source(label)
    genesis = hash72_digest({"domain": "P218-I9-TEST-GENESIS"}, label.encode())
    hydration = hash72_digest({"domain": "P218-I9-TEST-HYDRATION"}, label.encode())
    validation = hash72_digest({"domain": "P218-I9-TEST-VALIDATION"}, label.encode())
    return {
        "schema": "HHS-P218-NARRATIVE-HYDRATION-CANDIDATE-I2-V1",
        "hydrator_version": "HHS-P218-NARRATIVE-HYDRATOR-I2-V1",
        "source_id": f"iteration9-{label}",
        "source_sha256": sha256(source.encode("utf-8")).hexdigest(),
        "source_epistemic_class": "FICTIONAL_COUNTERFACTUAL",
        "genesis_seed_hash72": genesis,
        "grammar_rule_set_hash72": hash72_digest(
            {"domain": "P218-I9-TEST-GRAMMAR"}, label.encode()
        ),
        "beats": [_beat(index, label) for index in range(4)],
        "hydration_hash72": hydration,
        "validation_hash72": validation,
        "hash216": genesis + hydration + validation,
        "hash216_semantics": [
            "PREVIOUS_GENESIS_STATE",
            "NEXT_HYDRATION_CANDIDATE",
            "VALIDATION_RECEIPT",
        ],
        "verbatim_source_retained": False,
        "source_text_retained": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "authoritative_vector_store_promotion": False,
        "authoritative_float_weights": False,
    }


def _authorized(label: str = "A", *, sequence: int = 1):
    source = _source(label)
    transaction = SourceTransaction.begin(_hydration(label), source)
    transaction.commit_and_purge()
    staged = ClosedTransactionVectorVM5184Adapter().stage(transaction.snapshot())
    proof = PromotionProofMembrane().prove(
        closed_transaction_snapshot=transaction.snapshot(),
        staged_candidate=staged,
    )
    grant = PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=hash72_digest(
            {"domain": "P218-I9-TEST-GRANTOR"}, f"authority-{label}".encode()
        ),
        grant_sequence=sequence,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)
    return staged, journal, authorization


def _commit(lifecycle: Pass218MultiprocessRuntimeLifecycle, label: str = "A"):
    staged, journal, authorization = _authorized(label)
    boundary = lifecycle.canonical_boundary()
    prepared = boundary.prepare(
        authorization=authorization,
        staged_candidate=staged,
        authorization_journal=journal,
    )
    result = lifecycle.commit_prepared(prepared, authorization_journal=journal)
    return result, authorization


def _child_hold(root: str, ready, release) -> None:
    lease = Pass218CanonicalOwnershipLease(root, owner_id="child-owner")
    record = lease.acquire(blocking=False)
    ready.put(record["fence_epoch"] if record else -1)
    release.get()


def test_iteration9_declares_ownership_contract() -> None:
    assert PASS218_OWNERSHIP_VERSION == "HHS-P218-MULTIPROCESS-CANONICAL-OWNERSHIP-I9-V1"
    assert OWNERSHIP_RECORD_SCHEMA == "HHS-P218-I9-CANONICAL-OWNERSHIP-RECORD-V1"
    assert OWNERSHIP_LOCK_STRATEGY == "POSIX_FLOCK_EXCLUSIVE"
    assert OWNERSHIP_SCOPE == "LOCK_COHERENT_POSIX_FILESYSTEM"
    assert PASS218_MULTIPROCESS_LIFECYCLE_VERSION == "HHS-P218-MULTIPROCESS-RUNTIME-LIFECYCLE-I9-V1"
    assert MULTIPROCESS_LIFECYCLE_STATUS_SCHEMA == "HHS-P218-I9-MULTIPROCESS-LIFECYCLE-STATUS-V1"


def test_first_lease_acquires_fence_epoch_one(tmp_path: Path) -> None:
    lease = Pass218CanonicalOwnershipLease(tmp_path, owner_id="owner-a")
    record = lease.acquire()
    assert record is not None
    assert record["fence_epoch"] == 1
    assert record["previous_fence_epoch"] == 0
    assert record["previous_owner_id"] is None
    assert validate_ownership_record(record) == record
    lease.release()


def test_second_process_style_lease_is_busy_while_primary_holds(tmp_path: Path) -> None:
    first = Pass218CanonicalOwnershipLease(tmp_path, owner_id="owner-a")
    second = Pass218CanonicalOwnershipLease(tmp_path, owner_id="owner-b")
    assert first.acquire() is not None
    assert second.acquire() is None
    first.release()


def test_takeover_advances_fence_and_links_previous_owner(tmp_path: Path) -> None:
    first = Pass218CanonicalOwnershipLease(tmp_path, owner_id="owner-a")
    first_record = first.acquire()
    first.release()
    second = Pass218CanonicalOwnershipLease(tmp_path, owner_id="owner-b")
    second_record = second.acquire()
    assert first_record is not None and second_record is not None
    assert second_record["fence_epoch"] == 2
    assert second_record["previous_fence_epoch"] == 1
    assert second_record["previous_owner_id"] == "owner-a"
    second.release()


def test_stale_unlocked_record_is_recovered_by_new_fence(tmp_path: Path) -> None:
    payload = {
        "schema": OWNERSHIP_RECORD_SCHEMA,
        "ownership_version": PASS218_OWNERSHIP_VERSION,
        "fence_epoch": 1,
        "owner_id": "dead-owner",
        "previous_owner_id": None,
        "previous_fence_epoch": 0,
        "lock_strategy": OWNERSHIP_LOCK_STRATEGY,
        "ownership_scope": OWNERSHIP_SCOPE,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
    }
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "ownership.json").write_bytes(
        json.dumps(seal_ownership_record(payload), sort_keys=True, separators=(",", ":")).encode()
    )
    lease = Pass218CanonicalOwnershipLease(tmp_path, owner_id="replacement")
    record = lease.acquire()
    assert record is not None
    assert record["fence_epoch"] == 2
    assert record["previous_owner_id"] == "dead-owner"
    lease.release()


def test_tampered_ownership_record_fails_closed(tmp_path: Path) -> None:
    lease = Pass218CanonicalOwnershipLease(tmp_path, owner_id="owner-a")
    record = lease.acquire()
    assert record is not None
    lease.release()
    tampered = dict(record)
    tampered["owner_id"] = "forged"
    lease.record_path.write_bytes(
        json.dumps(tampered, sort_keys=True, separators=(",", ":")).encode()
    )
    contender = Pass218CanonicalOwnershipLease(tmp_path, owner_id="owner-b")
    with pytest.raises(Pass218OwnershipValidationError):
        contender.acquire()


def test_multiprocess_kernel_release_allows_takeover(tmp_path: Path) -> None:
    context = multiprocessing.get_context("spawn")
    ready = context.Queue()
    release = context.Queue()
    process = context.Process(target=_child_hold, args=(str(tmp_path), ready, release))
    process.start()
    assert ready.get(timeout=15) == 1
    contender = Pass218CanonicalOwnershipLease(tmp_path, owner_id="parent-owner")
    assert contender.acquire() is None
    process.terminate()
    process.join(timeout=15)
    acquired = contender.acquire()
    assert acquired is not None
    assert acquired["fence_epoch"] == 2
    contender.release()


def test_primary_lifecycle_opens_ingestion_and_standby_does_not(tmp_path: Path) -> None:
    primary = Pass218MultiprocessRuntimeLifecycle(tmp_path, owner_id="owner-a")
    standby = Pass218MultiprocessRuntimeLifecycle(tmp_path, owner_id="owner-b")
    primary_status = primary.startup()
    standby_status = standby.startup()
    assert primary_status["state"] == "EMPTY_READY"
    assert primary_status["ownership_state"] == "PRIMARY"
    assert primary_status["ownership_fence_epoch"] == 1
    assert primary_status["ingestion_enabled"] is True
    assert standby_status["state"] == "OWNERSHIP_STANDBY"
    assert standby_status["ownership_writer_authority"] is False
    assert standby_status["ingestion_enabled"] is False
    primary.shutdown()


def test_standby_cannot_construct_canonical_boundary(tmp_path: Path) -> None:
    primary = Pass218MultiprocessRuntimeLifecycle(tmp_path, owner_id="owner-a")
    standby = Pass218MultiprocessRuntimeLifecycle(tmp_path, owner_id="owner-b")
    primary.startup()
    standby.startup()
    with pytest.raises(Pass218RuntimeLifecycleNotReady, match="P218_I9_OWNERSHIP_FENCE_REQUIRED"):
        standby.canonical_boundary()
    primary.shutdown()


def test_takeover_restores_exact_committed_target_and_receipt(tmp_path: Path) -> None:
    primary = Pass218MultiprocessRuntimeLifecycle(tmp_path, owner_id="owner-a")
    primary.startup()
    result, authorization = _commit(primary)
    root = primary.target.root_hash72()
    snapshot = primary.target.snapshot_bytes()
    receipt = result["canonical_receipt"]
    primary.shutdown()

    replacement = Pass218MultiprocessRuntimeLifecycle(tmp_path, owner_id="owner-b")
    status = replacement.attempt_ownership_takeover()
    assert status["state"] == "RESTORED_READY"
    assert status["ownership_fence_epoch"] == 2
    assert replacement.target.root_hash72() == root
    assert replacement.target.snapshot_bytes() == snapshot
    assert replacement.target.committed_receipt(authorization["authorization_hash72"]) == receipt
    assert status["restart_new_authorization_minted"] is False
    assert status["restart_new_canonical_mutation_invoked"] is False
    replacement.shutdown()


def test_released_stale_lifecycle_cannot_resume_writes(tmp_path: Path) -> None:
    primary = Pass218MultiprocessRuntimeLifecycle(tmp_path, owner_id="owner-a")
    primary.startup()
    primary.shutdown()
    with pytest.raises(Pass218RuntimeLifecycleNotReady, match="P218_I9_OWNERSHIP_FENCE_REQUIRED"):
        primary.require_ingestion_ready()


def test_non_owner_checkpoint_is_rejected(tmp_path: Path) -> None:
    primary = Pass218MultiprocessRuntimeLifecycle(tmp_path, owner_id="owner-a")
    standby = Pass218MultiprocessRuntimeLifecycle(tmp_path, owner_id="owner-b")
    primary.startup()
    standby.startup()
    with pytest.raises(Exception, match="P218_I9_CHECKPOINT_OWNERSHIP_FENCE_REQUIRED"):
        standby.checkpoint_current()
    primary.shutdown()


def test_runtime_os_installer_uses_iteration9_owner(tmp_path: Path) -> None:
    app = FastAPI()
    first = install_pass218_runtime_os_lifecycle(app, state_root=tmp_path)
    second = install_pass218_runtime_os_lifecycle(app, state_root=tmp_path)
    assert isinstance(first, Pass218MultiprocessRuntimeLifecycle)
    assert second is first


def test_status_exposes_fence_without_new_authority(tmp_path: Path) -> None:
    lifecycle = Pass218MultiprocessRuntimeLifecycle(tmp_path, owner_id="owner-a")
    status = lifecycle.startup()
    assert status["ownership_writer_authority"] is True
    assert status["split_brain_writer_permitted"] is False
    assert status["canonical_learning_commit_invoked"] is False
    assert status["truth_promotion"] is False
    assert status["action_authority_minted"] is False
    assert status["verbatim_source_retained"] is False
    assert status["pass165_source_retaining_path_invoked"] is False
    lifecycle.shutdown()


def test_iteration9_authority_surfaces_contain_no_float_literals() -> None:
    for relative in (
        "hhs_runtime/pass218/ownership.py",
        "hhs_runtime/pass218/lifecycle_i9.py",
        "hhs_backend/runtime_os_pass218_lifecycle.py",
    ):
        tree = ast.parse((ROOT / relative).read_text("utf-8"))
        floats = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, relative
