from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import COORDINATES, SNAPSHOT_BYTES
from hhs_runtime.pass218 import (
    ClosedTransactionVectorVM5184Adapter,
    PASS218_PROMOTION_MEMBRANE_VERSION,
    PROMOTION_SCOPE,
    Pass218PromotionValidationError,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
)

ROOT = Path(__file__).resolve().parents[2]


def _source() -> str:
    return (
        "A synthetic narrative exists only to exercise the promotion proof membrane. "
        "It must never become external truth or action authority. "
        "A second sentence creates deterministic structural succession."
    )


def _beat(ordinal: int, label: str) -> dict[str, object]:
    span = f"iteration5-span-{ordinal}-{label}".encode("utf-8")
    payload = {
        "ordinal": ordinal,
        "source_span_sha256": sha256(span).hexdigest(),
        "paragraph_count": 1,
        "token_count": 9 + ordinal,
        "sentence_count": 1,
        "dialogue_turn_count": ordinal % 2,
        "perspective_counts": {
            "first_person": 0,
            "second_person": 0,
            "third_person": 1,
        },
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
    source = _source()
    genesis = hash72_digest({"domain": "P218-I5-TEST-GENESIS"}, label.encode())
    hydration = hash72_digest({"domain": "P218-I5-TEST-HYDRATION"}, label.encode())
    validation = hash72_digest({"domain": "P218-I5-TEST-VALIDATION"}, label.encode())
    return {
        "schema": "HHS-P218-NARRATIVE-HYDRATION-CANDIDATE-I2-V1",
        "hydrator_version": "HHS-P218-NARRATIVE-HYDRATOR-I2-V1",
        "source_id": f"iteration5-{label}",
        "source_sha256": sha256(source.encode("utf-8")).hexdigest(),
        "source_epistemic_class": "FICTIONAL_COUNTERFACTUAL",
        "genesis_seed_hash72": genesis,
        "grammar_rule_set_hash72": hash72_digest(
            {"domain": "P218-I5-TEST-GRAMMAR"}, label.encode()
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


def _snapshot_and_stage(label: str = "A") -> tuple[dict[str, object], dict[str, object]]:
    transaction = SourceTransaction.begin(_hydration(label), _source())
    transaction.commit_and_purge()
    snapshot = transaction.snapshot()
    staged = ClosedTransactionVectorVM5184Adapter().stage(snapshot)
    return snapshot, staged


def _proof(label: str = "A"):
    snapshot, staged = _snapshot_and_stage(label)
    proof = PromotionProofMembrane().prove(
        closed_transaction_snapshot=snapshot,
        staged_candidate=staged,
    )
    return snapshot, staged, proof


def _grant(proof, *, sequence: int = 1):
    return PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=hash72_digest(
            {"domain": "P218-I5-TEST-GRANTOR"}, b"explicit-authority"
        ),
        grant_sequence=sequence,
    )


def test_proof_replays_exact_iteration4_candidate() -> None:
    _, staged, proof = _proof()
    record = proof.to_record()
    assert record["promotable"] is True
    assert record["entry_id_sha256"] == staged["vector_entry"]["entry_id_sha256"]
    assert record["projection_sha256"] == staged["vm5184_projection_sha256"]
    assert record["explicit_authority_grant_present"] is False
    assert record["canonical_mutation_permitted"] is False


def test_proof_hash216_is_valid_and_ordered() -> None:
    _, _, proof = _proof()
    record = proof.to_record()
    value = record["proof_hash216"]
    assert len(value) == 216
    assert all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))
    assert record["hash216_semantics"] == [
        "VECTOR_VM5184_STAGE_CANDIDATE",
        "PROMOTABILITY_PROOF",
        "PROOF_VALIDATION_RECEIPT",
    ]


def test_proof_binds_pass217_vector_identity() -> None:
    _, staged, proof = _proof()
    entry = staged["vector_entry"]
    body = {key: value for key, value in entry.items() if key != "entry_id_sha256"}
    expected = sha256(
        b"HHS-P218-I4-P217-VECTOR-ENTRY\0"
        + json.dumps(
            body,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    assert expected == proof.entry_id_sha256


def test_proof_binds_exact_vm5184_projection_and_support_partition() -> None:
    _, staged, proof = _proof()
    entry = staged["vector_entry"]
    assert staged["vm5184_projection_bytes"] == SNAPSHOT_BYTES == 648
    assert len(entry["forward_support"]) + len(entry["inverse_support"]) == COORDINATES
    assert set(entry["forward_support"]).isdisjoint(entry["inverse_support"])
    assert proof.projection_sha256 == staged["vm5184_projection_sha256"]


def test_tampered_stage_is_rejected_by_exact_replay() -> None:
    snapshot, staged = _snapshot_and_stage()
    tampered = json.loads(json.dumps(staged))
    tampered["vector_entry"]["collision_bucket"] += 1
    with pytest.raises(
        Pass218PromotionValidationError, match="P218_I5_EXACT_STAGE_REPLAY_MISMATCH"
    ):
        PromotionProofMembrane().prove(
            closed_transaction_snapshot=snapshot,
            staged_candidate=tampered,
        )


def test_mismatched_closed_transaction_is_rejected() -> None:
    snapshot_a, staged_a = _snapshot_and_stage("A")
    snapshot_b, _ = _snapshot_and_stage("B")
    assert snapshot_a != snapshot_b
    with pytest.raises(
        Pass218PromotionValidationError, match="P218_I5_EXACT_STAGE_REPLAY_MISMATCH"
    ):
        PromotionProofMembrane().prove(
            closed_transaction_snapshot=snapshot_b,
            staged_candidate=staged_a,
        )


def test_proof_alone_cannot_authorize_mutation() -> None:
    _, _, proof = _proof()
    journal = PromotionAuthorizationJournal()
    with pytest.raises(
        Pass218PromotionValidationError, match="P218_I5_GRANT_SCHEMA_INVALID"
    ):
        journal.authorize(proof, {})


def test_grant_requires_explicit_valid_grantor_authority_root() -> None:
    _, _, proof = _proof()
    with pytest.raises(
        Pass218PromotionValidationError,
        match="P218_I5_GRANTOR_AUTHORITY_HASH72_INVALID",
    ):
        PromotionAuthorityGrant.bind(
            proof,
            grantor_authority_hash72="invalid",
            grant_sequence=1,
        )


def test_grant_is_exactly_scoped_to_candidate_and_promotion_surface() -> None:
    _, _, proof = _proof()
    grant = _grant(proof)
    record = grant.to_record()
    assert record["target_scope"] == PROMOTION_SCOPE
    assert record["entry_id_sha256"] == proof.entry_id_sha256
    assert record["proof_hash72"] == proof.proof_hash72
    assert record["learning_authority_granted"] is False
    assert record["truth_promotion"] is False
    assert record["action_authority_minted"] is False


def test_mismatched_grant_cannot_authorize_different_candidate() -> None:
    _, _, proof_a = _proof("A")
    _, _, proof_b = _proof("B")
    grant_a = _grant(proof_a).to_record()
    with pytest.raises(
        Pass218PromotionValidationError,
        match="P218_I5_GRANT_CANDIDATE_BINDING_MISMATCH",
    ):
        PromotionAuthorizationJournal().authorize(proof_b, grant_a)


def test_exact_proof_and_grant_create_precommit_authorization() -> None:
    _, _, proof = _proof()
    grant = _grant(proof)
    authorization = PromotionAuthorizationJournal().authorize(proof, grant)
    assert authorization["state"] == "AUTHORIZED_PENDING_CANONICAL_COMMIT"
    assert authorization["proof_required"] is True
    assert authorization["grant_required"] is True
    assert authorization["canonical_mutation_permitted"] is True
    assert authorization["canonical_vector_store_mutation_invoked"] is False
    assert authorization["canonical_vm81_commit_invoked"] is False
    assert authorization["canonical_learning_commit_invoked"] is False


def test_authorization_hash216_is_valid() -> None:
    _, _, proof = _proof()
    authorization = PromotionAuthorizationJournal().authorize(proof, _grant(proof))
    value = authorization["authorization_hash216"]
    assert len(value) == 216
    assert all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))


def test_authorization_replay_is_deterministic_and_content_addressed() -> None:
    _, _, proof = _proof()
    grant = _grant(proof)
    journal = PromotionAuthorizationJournal()
    first = journal.authorize(proof, grant)
    second = journal.authorize(proof, grant)
    assert first == second
    assert journal.record()["authorization_count"] == 1


def test_mutation_precondition_requires_exact_authorized_identity() -> None:
    _, _, proof = _proof()
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, _grant(proof))
    assert journal.mutation_precondition(
        authorization["authorization_hash72"],
        entry_id_sha256=proof.entry_id_sha256,
        projection_sha256=proof.projection_sha256,
    )
    assert not journal.mutation_precondition(
        authorization["authorization_hash72"],
        entry_id_sha256="0" * 64,
        projection_sha256=proof.projection_sha256,
    )


def test_precommit_rollback_revokes_mutation_permission_deterministically() -> None:
    _, _, proof = _proof()
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, _grant(proof, sequence=7))
    rolled = journal.rollback(
        authorization["authorization_hash72"],
        reason_code="DEPENDENCY_SCOPE_RECHECK_REQUESTED",
    )
    replay = journal.rollback(
        authorization["authorization_hash72"],
        reason_code="DEPENDENCY_SCOPE_RECHECK_REQUESTED",
    )
    assert rolled == replay
    assert rolled["state"] == "ROLLED_BACK_BEFORE_CANONICAL_COMMIT"
    assert rolled["canonical_mutation_permitted"] is False
    assert validate_hash72(rolled["rollback_hash72"])
    assert not journal.mutation_precondition(
        authorization["authorization_hash72"],
        entry_id_sha256=proof.entry_id_sha256,
        projection_sha256=proof.projection_sha256,
    )


def test_iteration5_retains_nonverbatim_nontruth_nonaction_boundary() -> None:
    _, _, proof = _proof()
    proof_record = proof.to_record()
    grant_record = _grant(proof).to_record()
    authorization = PromotionAuthorizationJournal().authorize(proof, grant_record)
    serialized = json.dumps(
        {
            "proof": proof_record,
            "grant": grant_record,
            "authorization": authorization,
        },
        sort_keys=True,
    )
    assert _source() not in serialized
    assert proof_record["verbatim_source_retained"] is False
    assert proof_record["truth_promotion"] is False
    assert proof_record["action_authority_minted"] is False
    assert authorization["truth_promotion"] is False
    assert authorization["action_authority_minted"] is False


def test_version_and_scope_are_frozen() -> None:
    assert PASS218_PROMOTION_MEMBRANE_VERSION == "HHS-P218-PROMOTION-ADMISSION-I5-V1"
    assert PROMOTION_SCOPE == "PASS217_VECTOR_VM5184_PROMOTION"


def test_no_float_literals_in_pass218_runtime_package() -> None:
    paths = sorted((ROOT / "hhs_runtime" / "pass218").glob("*.py"))
    assert paths
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path
