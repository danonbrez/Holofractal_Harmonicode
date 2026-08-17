from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import SNAPSHOT_BYTES, THREADS
from hhs_runtime.pass218 import (
    CANONICAL_ADMISSION_STATUS,
    INHERITED_VM81_AUTHORITY,
    PASS217_VECTOR_ENTRY_SCHEMA,
    PASS217_VECTOR_SCHEMA_PATH,
    PASS218_CANONICAL_COMMIT_VERSION,
    ClosedTransactionVectorVM5184Adapter,
    Pass217VM81CanonicalTarget,
    Pass218CanonicalCommitBoundary,
    Pass218CanonicalCommitStateError,
    Pass218CanonicalCommitValidationError,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
)

ROOT = Path(__file__).resolve().parents[2]


def _source(label: str = "A") -> str:
    return (
        "A synthetic narrative exercises only the Iteration 6 canonical commit "
        f"boundary {label}. It must never become truth or action authority. "
        "A second sentence makes the structural projection non-empty."
    )


def _beat(ordinal: int, label: str) -> dict[str, object]:
    payload = {
        "ordinal": ordinal,
        "source_span_sha256": sha256(
            f"iteration6-span-{ordinal}-{label}".encode("utf-8")
        ).hexdigest(),
        "paragraph_count": 1,
        "token_count": 11 + ordinal,
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
    source = _source(label)
    genesis = hash72_digest({"domain": "P218-I6-TEST-GENESIS"}, label.encode())
    hydration = hash72_digest({"domain": "P218-I6-TEST-HYDRATION"}, label.encode())
    validation = hash72_digest({"domain": "P218-I6-TEST-VALIDATION"}, label.encode())
    return {
        "schema": "HHS-P218-NARRATIVE-HYDRATION-CANDIDATE-I2-V1",
        "hydrator_version": "HHS-P218-NARRATIVE-HYDRATOR-I2-V1",
        "source_id": f"iteration6-{label}",
        "source_sha256": sha256(source.encode("utf-8")).hexdigest(),
        "source_epistemic_class": "FICTIONAL_COUNTERFACTUAL",
        "genesis_seed_hash72": genesis,
        "grammar_rule_set_hash72": hash72_digest(
            {"domain": "P218-I6-TEST-GRAMMAR"}, label.encode()
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
    snapshot = transaction.snapshot()
    staged = ClosedTransactionVectorVM5184Adapter().stage(snapshot)
    proof = PromotionProofMembrane().prove(
        closed_transaction_snapshot=snapshot,
        staged_candidate=staged,
    )
    grant = PromotionAuthorityGrant.bind(
        proof,
        grantor_authority_hash72=hash72_digest(
            {"domain": "P218-I6-TEST-GRANTOR"},
            f"authority-{label}".encode("utf-8"),
        ),
        grant_sequence=sequence,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)
    return staged, proof, journal, authorization


def _prepared(label: str = "A", *, target=None, sequence: int = 1):
    staged, proof, journal, authorization = _authorized(label, sequence=sequence)
    boundary = Pass218CanonicalCommitBoundary(target=target)
    prepared = boundary.prepare(
        authorization=authorization,
        staged_candidate=staged,
        authorization_journal=journal,
    )
    return staged, proof, journal, authorization, boundary, prepared


def test_iteration6_binds_frozen_pass217_vector_and_vm81_authorities() -> None:
    assert PASS218_CANONICAL_COMMIT_VERSION == "HHS-P218-CANONICAL-COMMIT-I6-V1"
    assert PASS217_VECTOR_ENTRY_SCHEMA == "HHS_PASS_217_VECTOR_STORE_ENTRY_V1"
    assert PASS217_VECTOR_SCHEMA_PATH == "contracts/pass217/vector_store.schema.json"
    assert INHERITED_VM81_AUTHORITY == "hhs_runtime.pass163.vmrc.VMRCRuntime"
    assert CANONICAL_ADMISSION_STATUS == "VM81_ADMITTED"


def test_prepare_requires_exact_active_iteration5_authorization() -> None:
    staged, _, journal, authorization = _authorized()
    wrong = json.loads(json.dumps(authorization))
    wrong["entry_id_sha256"] = "0" * 64
    with pytest.raises(
        Pass218CanonicalCommitValidationError,
        match="P218_I6_AUTHORIZATION_NOT_ACTIVE_EXACT_JOURNAL_RECORD",
    ):
        Pass218CanonicalCommitBoundary().prepare(
            authorization=wrong,
            staged_candidate=staged,
            authorization_journal=journal,
        )


def test_rolled_back_iteration5_authorization_cannot_prepare() -> None:
    staged, _, journal, authorization = _authorized()
    journal.rollback(
        authorization["authorization_hash72"],
        reason_code="I6_TEST_PREPARE_REVOKED",
    )
    with pytest.raises(
        Pass218CanonicalCommitValidationError,
        match="P218_I6_AUTHORIZATION_NOT_ACTIVE_EXACT_JOURNAL_RECORD",
    ):
        Pass218CanonicalCommitBoundary().prepare(
            authorization=authorization,
            staged_candidate=staged,
            authorization_journal=journal,
        )


def test_prepare_binds_exact_candidate_and_promotes_only_admission_status() -> None:
    staged, _, _, authorization, _, prepared = _prepared()
    assert prepared.candidate_entry["entry_id_sha256"] == authorization["entry_id_sha256"]
    assert prepared.candidate_entry["admission_status"] == "CANDIDATE"
    assert prepared.admitted_entry["admission_status"] == "VM81_ADMITTED"
    assert prepared.admitted_entry["entry_id_sha256"] != prepared.candidate_entry["entry_id_sha256"]
    for key in (
        "parent_state_sha256",
        "candidate_state_sha256",
        "hash216_transition_sha256",
        "forward_support",
        "inverse_support",
        "ordered_path",
        "dependency_frontier",
        "collision_bucket",
    ):
        assert prepared.admitted_entry[key] == staged["vector_entry"][key]


def test_prepare_proves_full_5184_projection_through_inherited_vm81_runtime() -> None:
    staged, _, _, _, _, prepared = _prepared()
    assert len(prepared.projection_bytes) == SNAPSHOT_BYTES == 648
    assert prepared.shadow_runtime.snapshot().to_bytes() == prepared.projection_bytes
    assert prepared.shadow_runtime.epoch == THREADS == 64
    assert len(prepared.vm81_receipts) == THREADS
    assert prepared.shadow_runtime.snapshot_hash72 == staged["vm5184_projection_hash72"]
    assert all(validate_hash72(row["commit_receipt_hash72"]) for row in prepared.vm81_receipts)


def test_prepare_is_noncanonical_and_does_not_mutate_target() -> None:
    target = Pass217VM81CanonicalTarget()
    root_before = target.root_hash72()
    _, _, _, _, _, prepared = _prepared(target=target)
    record = prepared.to_record()
    assert target.root_hash72() == root_before == prepared.target_root_before_hash72
    assert target.record()["canonical_entry_count"] == 0
    assert record["canonical_vector_store_mutation_invoked"] is False
    assert record["canonical_vm81_commit_invoked"] is False
    assert record["canonical_learning_commit_invoked"] is False


def test_prepare_hash216_is_valid_and_ordered() -> None:
    _, _, _, authorization, _, prepared = _prepared()
    value = prepared.prepare_hash216
    assert len(value) == 216
    assert all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))
    assert value[:72] == authorization["authorization_hash72"]


def test_commit_atomically_admits_pass217_entry_and_vm81_image() -> None:
    _, _, journal, authorization, boundary, prepared = _prepared()
    receipt = boundary.commit(prepared, authorization_journal=journal)
    target = boundary.target
    assert receipt["state"] == "CANONICAL_COMMITTED"
    assert receipt["canonical_vector_store_mutation_invoked"] is True
    assert receipt["canonical_vm81_commit_invoked"] is True
    assert receipt["canonical_learning_commit_invoked"] is False
    assert receipt["authorization_consumed"] is True
    assert receipt["atomic_swap"] is True
    assert receipt["failed_partial_commit_possible"] is False
    assert target.snapshot_bytes() == prepared.projection_bytes
    assert target.authorization_consumed(authorization["authorization_hash72"])
    assert target.record()["canonical_entry_count"] == 1
    assert target.record()["canonical_commit_count"] == 1
    assert target.root_hash72() == receipt["target_root_after_hash72"]


def test_commit_receipt_hash216_is_valid() -> None:
    _, _, journal, _, boundary, prepared = _prepared()
    receipt = boundary.commit(prepared, authorization_journal=journal)
    value = receipt["commit_hash216"]
    assert len(value) == 216
    assert all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))
    assert receipt["hash216_semantics"] == [
        "CANONICAL_TARGET_PREPARE",
        "ATOMIC_CANONICAL_COMMIT",
        "CANONICAL_COMMIT_RECEIPT",
    ]


def test_commit_replay_is_idempotent_and_does_not_double_mutate() -> None:
    _, _, journal, _, boundary, prepared = _prepared()
    first = boundary.commit(prepared, authorization_journal=journal)
    root = boundary.target.root_hash72()
    second = boundary.commit(prepared, authorization_journal=journal)
    assert first == second
    assert boundary.target.root_hash72() == root
    assert boundary.target.record()["canonical_entry_count"] == 1
    assert boundary.target.record()["canonical_commit_count"] == 1


def test_injected_commit_failure_leaves_canonical_target_bit_exactly_unchanged() -> None:
    target = Pass217VM81CanonicalTarget()
    root_before = target.root_hash72()
    snapshot_before = target.snapshot_bytes()
    _, _, journal, _, boundary, prepared = _prepared(target=target)
    with pytest.raises(
        Pass218CanonicalCommitStateError,
        match="P218_I6_INJECTED_COMMIT_FAILURE_BEFORE_ATOMIC_SWAP",
    ):
        boundary.commit(
            prepared,
            authorization_journal=journal,
            fail_before_atomic_swap=True,
        )
    assert target.root_hash72() == root_before
    assert target.snapshot_bytes() == snapshot_before
    assert target.record()["canonical_entry_count"] == 0
    assert target.record()["canonical_commit_count"] == 0


def test_failed_commit_recovery_is_deterministic_and_retryable() -> None:
    _, _, journal, _, boundary, prepared = _prepared()
    with pytest.raises(Pass218CanonicalCommitStateError):
        boundary.commit(
            prepared,
            authorization_journal=journal,
            fail_before_atomic_swap=True,
        )
    first = boundary.recover_failed_commit(
        prepared,
        authorization_journal=journal,
        reason_code="I6_TEST_INJECTED_FAILURE",
    )
    second = boundary.recover_failed_commit(
        prepared,
        authorization_journal=journal,
        reason_code="I6_TEST_INJECTED_FAILURE",
    )
    assert first == second
    assert first["state"] == "RECOVERABLE_PREPARED_NOT_COMMITTED"
    assert first["retry_permitted"] is True
    assert first["canonical_vector_store_mutation_invoked"] is False
    assert first["canonical_vm81_commit_invoked"] is False
    receipt = boundary.commit(prepared, authorization_journal=journal)
    assert receipt["state"] == "CANONICAL_COMMITTED"


def test_authorization_revoked_after_prepare_cannot_commit() -> None:
    _, _, journal, authorization, boundary, prepared = _prepared()
    journal.rollback(
        authorization["authorization_hash72"],
        reason_code="I6_TEST_REVOKED_AFTER_PREPARE",
    )
    with pytest.raises(
        Pass218CanonicalCommitValidationError,
        match="P218_I6_COMMIT_AUTHORIZATION_NO_LONGER_ACTIVE",
    ):
        boundary.commit(prepared, authorization_journal=journal)
    assert boundary.target.record()["canonical_commit_count"] == 0


def test_target_change_after_prepare_rejects_stale_commit() -> None:
    target = Pass217VM81CanonicalTarget()
    _, _, journal_a, _, boundary_a, prepared_a = _prepared(
        "A", target=target, sequence=1
    )
    _, _, journal_b, _, boundary_b, prepared_b = _prepared(
        "B", target=target, sequence=2
    )
    boundary_a.commit(prepared_a, authorization_journal=journal_a)
    with pytest.raises(
        Pass218CanonicalCommitStateError,
        match="P218_I6_CANONICAL_TARGET_CHANGED_AFTER_PREPARE",
    ):
        boundary_b.commit(prepared_b, authorization_journal=journal_b)


def test_stage_candidate_with_source_text_is_rejected() -> None:
    staged, _, journal, authorization = _authorized()
    tampered = json.loads(json.dumps(staged))
    tampered["source_text"] = "verbatim content must never cross Iteration 6"
    with pytest.raises(
        Pass218CanonicalCommitValidationError,
        match="P218_I6_SOURCE_RETENTION_FIELD_FORBIDDEN",
    ):
        Pass218CanonicalCommitBoundary().prepare(
            authorization=authorization,
            staged_candidate=tampered,
            authorization_journal=journal,
        )


def test_stage_candidate_with_learning_commit_flag_is_rejected() -> None:
    staged, _, journal, authorization = _authorized()
    tampered = json.loads(json.dumps(staged))
    tampered["canonical_learning_commit_invoked"] = True
    with pytest.raises(
        Pass218CanonicalCommitValidationError,
        match="P218_I6_LEARNING_COMMIT_PATH_FORBIDDEN",
    ):
        Pass218CanonicalCommitBoundary().prepare(
            authorization=authorization,
            staged_candidate=tampered,
            authorization_journal=journal,
        )


def test_commit_receipt_never_promotes_truth_action_or_learning_authority() -> None:
    source = _source()
    _, _, journal, _, boundary, prepared = _prepared()
    receipt = boundary.commit(prepared, authorization_journal=journal)
    serialized = json.dumps(receipt, sort_keys=True)
    assert source not in serialized
    assert receipt["truth_promotion"] is False
    assert receipt["action_authority_minted"] is False
    assert receipt["verbatim_source_retained"] is False
    assert receipt["canonical_learning_commit_invoked"] is False
    assert receipt["pass165_source_retaining_path_invoked"] is False


def test_commit_boundary_has_no_pass165_import_dependency() -> None:
    path = ROOT / "hhs_runtime" / "pass218" / "commit_boundary.py"
    tree = ast.parse(path.read_text("utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert all("pass165" not in name.lower() for name in imported)


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
