from __future__ import annotations

from hashlib import sha256
import json

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218 import (
    DeterministicStructuralStore,
    Pass218TransactionValidationError,
    SourceTransaction,
    TransactionPhase,
)


def _source() -> str:
    return (
        "A bounded narrative source is consumed transiently for structural hydration. "
        "The transaction must preserve only exact structural relations and receipts. "
        "No source sentence is allowed to become authoritative memory."
    )


def _candidate(source_text: str | None = None) -> dict:
    source = _source() if source_text is None else source_text
    source_sha = sha256(source.encode("utf-8")).hexdigest()
    genesis = hash72_digest({"domain": "P218-I3-TEST-GENESIS"}, "genesis")
    hydration = hash72_digest({"domain": "P218-I3-TEST-HYDRATION"}, source_sha)
    validation = hash72_digest({"domain": "P218-I3-TEST-VALIDATION"}, hydration)
    beat = {
        "ordinal": 0,
        "source_span_sha256": source_sha,
        "paragraph_count": 1,
        "token_count": 28,
        "sentence_count": 3,
        "dialogue_turn_count": 0,
        "perspective_counts": {"first_person": 0, "second_person": 0, "third_person": 0},
        "negation_count": 1,
        "modal_count": 1,
        "authority_count": 1,
        "temporal_count": 0,
        "dominant_perspective": "UNSPECIFIED",
        "relation_types": ["AUTHORITY_SCOPE", "MODAL_CONSTRAINT", "NEGATION_PRESSURE"],
        "distinction_mentions": [],
        "beat_hash72": hash72_digest({"domain": "P218-I3-TEST-BEAT"}, source_sha),
        "verbatim_source_retained": False,
    }
    return {
        "schema": "HHS-P218-NARRATIVE-HYDRATION-CANDIDATE-I2-V1",
        "source_id": "iteration3-fixture",
        "source_sha256": source_sha,
        "source_epistemic_class": "REPOSITORY_NATIVE_TEST",
        "genesis_seed_hash72": genesis,
        "grammar_rule_set_hash72": hash72_digest({"domain": "P218-I3-TEST-GRAMMAR"}, "grammar"),
        "beats": [beat],
        "hydration_hash72": hydration,
        "validation_hash72": validation,
        "hash216": genesis + hydration + validation,
        "verbatim_source_retained": False,
        "source_text_retained": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "authoritative_vector_store_promotion": False,
        "authoritative_float_weights": False,
    }


def test_successful_transaction_requires_purge_before_admission() -> None:
    store = DeterministicStructuralStore()
    tx = SourceTransaction.begin(_candidate(), _source(), store=store)
    tx.validate()
    tx.commit_structural()
    assert tx.phase == TransactionPhase.STRUCTURAL_COMMITTED
    assert store.is_pending(tx.transaction_id_hash72)
    assert not store.is_admitted(tx.transaction_id_hash72)
    assert tx.managed_source_bytes == len(_source().encode("utf-8"))

    closure = tx.purge_and_close()
    assert tx.phase == TransactionPhase.CLOSED
    assert tx.managed_source_bytes == 0
    assert store.is_admitted(tx.transaction_id_hash72)
    assert closure["managed_buffer_zeroized"] is True
    assert closure["managed_buffer_cleared"] is True
    assert closure["authoritative_vector_store_promotion"] is False
    assert len(closure["transaction_hash216"]) == 216
    assert all(validate_hash72(closure["transaction_hash216"][start:start + 72]) for start in (0, 72, 144))


def test_admitted_structural_record_contains_no_verbatim_source() -> None:
    store = DeterministicStructuralStore()
    tx = SourceTransaction.begin(_candidate(), _source(), store=store)
    tx.commit_and_purge()
    record = store.admitted_record(tx.transaction_id_hash72)
    assert record is not None
    serialized = json.dumps(record, sort_keys=True)
    assert _source() not in serialized
    assert record["verbatim_source_retained"] is False
    assert record["source_text_retained"] is False
    assert record["admission_status"] == "PENDING_PURGE_PROOF"


def test_snapshot_never_serializes_source_buffer_or_source_text() -> None:
    tx = SourceTransaction.begin(_candidate(), _source())
    tx.validate()
    snapshot = tx.snapshot()
    serialized = json.dumps(snapshot, sort_keys=True)
    assert snapshot["source_buffer_serialized"] is False
    assert snapshot["verbatim_source_retained"] is False
    assert _source() not in serialized
    assert validate_hash72(snapshot["snapshot_hash72"])


def test_validated_restart_requires_exact_source_reingress_then_closes_identically() -> None:
    original = SourceTransaction.begin(_candidate(), _source())
    original.validate()
    snapshot = original.snapshot()
    restored = SourceTransaction.restore(snapshot)
    assert restored.phase == TransactionPhase.VALIDATED
    assert restored.managed_source_bytes == 0
    restored.resume_source(_source())
    closure = restored.commit_and_purge()
    assert restored.phase == TransactionPhase.CLOSED
    assert closure["managed_buffer_cleared"] is True


def test_closed_snapshot_replays_exact_admitted_structural_record() -> None:
    tx = SourceTransaction.begin(_candidate(), _source())
    first_closure = tx.commit_and_purge()
    snapshot = tx.snapshot()
    replay_store = DeterministicStructuralStore()
    replay = SourceTransaction.restore(snapshot, store=replay_store)
    assert replay.phase == TransactionPhase.CLOSED
    assert replay.verify_journal() is True
    assert replay_store.is_admitted(replay.transaction_id_hash72)
    assert replay.closure_receipt == first_closure


def test_interrupted_commit_without_purge_proof_is_quarantined_on_recovery() -> None:
    tx = SourceTransaction.begin(_candidate(), _source())
    tx.validate()
    tx.commit_structural()
    snapshot = tx.snapshot()
    restart_store = DeterministicStructuralStore()
    restored = SourceTransaction.restore(snapshot, store=restart_store)
    assert restart_store.is_pending(restored.transaction_id_hash72)
    restored.recover_interrupted_commit()
    assert restored.phase == TransactionPhase.QUARANTINED
    assert not restart_store.is_pending(restored.transaction_id_hash72)
    assert not restart_store.is_admitted(restored.transaction_id_hash72)
    assert restored.managed_source_bytes == 0


def test_source_checksum_mismatch_is_rejected_and_buffer_is_purged() -> None:
    candidate = _candidate()
    tx = SourceTransaction.begin(candidate, _source() + " tampered")
    assert tx.phase == TransactionPhase.REJECTED
    assert tx.managed_source_bytes == 0
    assert tx.purge_receipt["managed_buffer_cleared"] is True
    with pytest.raises(Pass218TransactionValidationError, match="P218_TRANSACTION_REJECTED"):
        tx.validate()


def test_tampered_hash216_quarantines_source_and_never_commits() -> None:
    candidate = _candidate()
    candidate["hash216"] = candidate["hash216"][:-1] + " "
    store = DeterministicStructuralStore()
    tx = SourceTransaction.begin(candidate, _source(), store=store)
    with pytest.raises(Pass218TransactionValidationError, match="P218_CANDIDATE_HASH216_INVALID"):
        tx.validate()
    assert tx.phase == TransactionPhase.QUARANTINED
    assert tx.managed_source_bytes == 0
    assert not store.is_admitted(tx.transaction_id_hash72)


def test_truth_or_vector_authority_request_is_quarantined() -> None:
    candidate = _candidate()
    candidate["truth_promotion"] = True
    candidate["authoritative_vector_store_promotion"] = True
    tx = SourceTransaction.begin(candidate, _source())
    with pytest.raises(Pass218TransactionValidationError, match="P218_FORBIDDEN_AUTHORITY_FLAG"):
        tx.validate()
    assert tx.phase == TransactionPhase.QUARANTINED
    assert tx.managed_source_bytes == 0


def test_verbatim_field_is_quarantined_even_when_top_level_retained_flag_is_false() -> None:
    candidate = _candidate()
    candidate["beats"][0]["raw_text"] = "forbidden source fragment"
    tx = SourceTransaction.begin(candidate, _source())
    with pytest.raises(Pass218TransactionValidationError, match="P218_VERBATIM_FIELD"):
        tx.validate()
    assert tx.phase == TransactionPhase.QUARANTINED
    assert tx.managed_source_bytes == 0


def test_transaction_closure_is_deterministic_for_identical_inputs() -> None:
    first = SourceTransaction.begin(_candidate(), _source())
    second = SourceTransaction.begin(_candidate(), _source())
    first_closure = first.commit_and_purge()
    second_closure = second.commit_and_purge()
    assert first.transaction_id_hash72 == second.transaction_id_hash72
    assert first_closure == second_closure
    assert first.snapshot() == second.snapshot()


def test_snapshot_tamper_is_detected_before_replay() -> None:
    tx = SourceTransaction.begin(_candidate(), _source())
    tx.validate()
    snapshot = tx.snapshot()
    snapshot["phase"] = int(TransactionPhase.CLOSED)
    with pytest.raises(Pass218TransactionValidationError, match="P218_TRANSACTION_SNAPSHOT_HASH_MISMATCH"):
        SourceTransaction.restore(snapshot)
