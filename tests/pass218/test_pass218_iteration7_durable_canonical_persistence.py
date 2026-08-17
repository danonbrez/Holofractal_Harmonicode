from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218 import (
    CHECKPOINT_SCHEMA,
    MANIFEST_SCHEMA,
    PASS218_PERSISTENCE_VERSION,
    RESTORE_SCHEMA,
    ClosedTransactionVectorVM5184Adapter,
    Pass217VM81CanonicalTarget,
    Pass218CanonicalCommitBoundary,
    Pass218DurableCanonicalStore,
    Pass218PersistenceStateError,
    Pass218PersistenceValidationError,
    PromotionAuthorityGrant,
    PromotionAuthorizationJournal,
    PromotionProofMembrane,
    SourceTransaction,
    validate_checkpoint,
    validate_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


def _source(label: str = "A") -> str:
    return (
        "A synthetic narrative exists only to test the Iteration 7 durable "
        f"canonical restart boundary {label}. It must never be retained. "
        "A second sentence ensures a non-empty structural projection."
    )


def _beat(ordinal: int, label: str) -> dict[str, object]:
    payload = {
        "ordinal": ordinal,
        "source_span_sha256": sha256(
            f"iteration7-span-{ordinal}-{label}".encode("utf-8")
        ).hexdigest(),
        "paragraph_count": 1,
        "token_count": 13 + ordinal,
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
    genesis = hash72_digest({"domain": "P218-I7-TEST-GENESIS"}, label.encode())
    hydration = hash72_digest({"domain": "P218-I7-TEST-HYDRATION"}, label.encode())
    validation = hash72_digest({"domain": "P218-I7-TEST-VALIDATION"}, label.encode())
    return {
        "schema": "HHS-P218-NARRATIVE-HYDRATION-CANDIDATE-I2-V1",
        "hydrator_version": "HHS-P218-NARRATIVE-HYDRATOR-I2-V1",
        "source_id": f"iteration7-{label}",
        "source_sha256": sha256(source.encode("utf-8")).hexdigest(),
        "source_epistemic_class": "FICTIONAL_COUNTERFACTUAL",
        "genesis_seed_hash72": genesis,
        "grammar_rule_set_hash72": hash72_digest(
            {"domain": "P218-I7-TEST-GRAMMAR"}, label.encode()
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
            {"domain": "P218-I7-TEST-GRANTOR"},
            f"authority-{label}".encode("utf-8"),
        ),
        grant_sequence=sequence,
    )
    journal = PromotionAuthorizationJournal()
    authorization = journal.authorize(proof, grant)
    return staged, journal, authorization


def _commit_into(
    target: Pass217VM81CanonicalTarget | None = None,
    *,
    label: str = "A",
    sequence: int = 1,
):
    target = target or Pass217VM81CanonicalTarget()
    staged, journal, authorization = _authorized(label, sequence=sequence)
    boundary = Pass218CanonicalCommitBoundary(target=target)
    prepared = boundary.prepare(
        authorization=authorization,
        staged_candidate=staged,
        authorization_journal=journal,
    )
    receipt = boundary.commit(prepared, authorization_journal=journal)
    return target, receipt, staged


def _active_generation_path(store: Pass218DurableCanonicalStore, result) -> Path:
    return store.generations / result["manifest"]["active_generation"]


def test_iteration7_declares_durable_persistence_contract() -> None:
    assert PASS218_PERSISTENCE_VERSION == "HHS-P218-DURABLE-CANONICAL-PERSISTENCE-I7-V1"
    assert CHECKPOINT_SCHEMA == "HHS-P218-I7-DURABLE-CANONICAL-CHECKPOINT-V1"
    assert MANIFEST_SCHEMA == "HHS-P218-I7-DURABLE-CANONICAL-MANIFEST-V1"
    assert RESTORE_SCHEMA == "HHS-P218-I7-DURABLE-CANONICAL-RESTORE-RECEIPT-V1"


def test_empty_target_cannot_be_persisted(tmp_path: Path) -> None:
    with pytest.raises(
        Pass218PersistenceStateError,
        match="P218_I7_EMPTY_CANONICAL_TARGET_NOT_PERSISTABLE",
    ):
        Pass218DurableCanonicalStore(tmp_path).checkpoint(
            Pass217VM81CanonicalTarget()
        )


def test_checkpoint_writes_sealed_generation_and_atomic_manifest(tmp_path: Path) -> None:
    target, _, _ = _commit_into()
    store = Pass218DurableCanonicalStore(tmp_path)
    result = store.checkpoint(target)
    assert result["state"] == "DURABLE_CHECKPOINT_COMMITTED"
    assert result["idempotent_replay"] is False
    assert store.manifest_path.is_file()
    assert _active_generation_path(store, result).is_file()
    assert validate_manifest(result["manifest"]) == result["manifest"]
    assert validate_checkpoint(result["checkpoint"]) == result["checkpoint"]


def test_checkpoint_hash216_binds_canonical_target_checkpoint_and_validation(tmp_path: Path) -> None:
    target, _, _ = _commit_into()
    checkpoint = Pass218DurableCanonicalStore(tmp_path).checkpoint(target)["checkpoint"]
    assert len(checkpoint["checkpoint_hash216"]) == 216
    assert checkpoint["checkpoint_hash216"][:72] == target.root_hash72()
    assert checkpoint["checkpoint_hash216"][72:144] == checkpoint["checkpoint_hash72"]
    assert checkpoint["checkpoint_hash216"][144:] == checkpoint["validation_hash72"]
    assert all(
        validate_hash72(checkpoint["checkpoint_hash216"][start:start + 72])
        for start in (0, 72, 144)
    )


def test_restart_reconstructs_exact_canonical_root_snapshot_and_receipt(tmp_path: Path) -> None:
    target, receipt, _ = _commit_into()
    root_before = target.root_hash72()
    snapshot_before = target.snapshot_bytes()
    result = Pass218DurableCanonicalStore(tmp_path).checkpoint(target)

    restarted_store = Pass218DurableCanonicalStore(tmp_path)
    restored = restarted_store.restore()
    assert restored.state == "RESTORED_ACTIVE_GENERATION"
    assert restored.target.root_hash72() == root_before
    assert restored.target.snapshot_bytes() == snapshot_before
    assert restored.target.committed_receipt(receipt["authorization_hash72"]) == receipt
    assert restored.checkpoint["checkpoint_sha256"] == result["checkpoint"]["checkpoint_sha256"]


def test_restore_is_receipt_replay_not_new_authorization_or_mutation(tmp_path: Path) -> None:
    target, _, _ = _commit_into()
    store = Pass218DurableCanonicalStore(tmp_path)
    store.checkpoint(target)
    record = store.restore().to_record()
    assert record["new_canonical_mutation_invoked"] is False
    assert record["new_authorization_minted"] is False
    assert record["canonical_learning_commit_invoked"] is False
    assert record["truth_promotion"] is False
    assert record["action_authority_minted"] is False
    assert record["verbatim_source_retained"] is False
    assert record["pass165_source_retaining_path_invoked"] is False
    assert validate_hash72(record["restore_hash72"])


def test_checkpoint_replay_is_idempotent_and_does_not_advance_generation(tmp_path: Path) -> None:
    target, _, _ = _commit_into()
    store = Pass218DurableCanonicalStore(tmp_path)
    first = store.checkpoint(target)
    second = store.checkpoint(target)
    assert second["state"] == "DURABLE_CHECKPOINT_IDEMPOTENT_REPLAY"
    assert second["idempotent_replay"] is True
    assert second["manifest"] == first["manifest"]
    assert second["checkpoint"] == first["checkpoint"]
    assert len(list(store.generations.glob("checkpoint-*.json"))) == 1


def test_second_canonical_state_creates_next_generation_with_previous_pointer(tmp_path: Path) -> None:
    target, _, _ = _commit_into(label="A", sequence=1)
    store = Pass218DurableCanonicalStore(tmp_path)
    first = store.checkpoint(target)
    _commit_into(target, label="B", sequence=2)
    second = store.checkpoint(target)
    assert second["manifest"]["generation_sequence"] == 1
    assert second["manifest"]["previous_generation"] == first["manifest"]["active_generation"]
    assert second["manifest"]["previous_checkpoint_sha256"] == first["checkpoint"]["checkpoint_sha256"]
    assert second["checkpoint"]["previous_checkpoint_sha256"] == first["checkpoint"]["checkpoint_sha256"]
    assert len(list(store.generations.glob("checkpoint-*.json"))) == 2


def test_injected_failure_before_manifest_swap_preserves_previous_durable_state(tmp_path: Path) -> None:
    target, _, _ = _commit_into(label="A", sequence=1)
    store = Pass218DurableCanonicalStore(tmp_path)
    first = store.checkpoint(target)
    first_manifest_bytes = store.manifest_path.read_bytes()
    _commit_into(target, label="B", sequence=2)
    with pytest.raises(
        Pass218PersistenceStateError,
        match="P218_I7_INJECTED_FAILURE_BEFORE_MANIFEST_SWAP",
    ):
        store.checkpoint(target, fail_before_manifest_swap=True)
    assert store.manifest_path.read_bytes() == first_manifest_bytes
    restored = store.restore()
    assert restored.target.root_hash72() == first["manifest"]["canonical_root_hash72"]
    assert restored.state == "RESTORED_ACTIVE_GENERATION"


def test_corrupt_active_generation_recovers_previous_valid_generation(tmp_path: Path) -> None:
    target, _, _ = _commit_into(label="A", sequence=1)
    store = Pass218DurableCanonicalStore(tmp_path)
    first = store.checkpoint(target)
    _commit_into(target, label="B", sequence=2)
    second = store.checkpoint(target)
    _active_generation_path(store, second).write_bytes(b"{corrupt")
    restored = store.restore()
    assert restored.state == "RECOVERED_PREVIOUS_VALID_GENERATION"
    assert restored.recovered_previous_generation is True
    assert restored.target.root_hash72() == first["manifest"]["canonical_root_hash72"]
    assert restored.checkpoint["checkpoint_sha256"] == first["checkpoint"]["checkpoint_sha256"]


def test_corrupt_active_generation_is_rejected_when_fallback_disabled(tmp_path: Path) -> None:
    target, _, _ = _commit_into(label="A", sequence=1)
    store = Pass218DurableCanonicalStore(tmp_path)
    store.checkpoint(target)
    _commit_into(target, label="B", sequence=2)
    second = store.checkpoint(target)
    _active_generation_path(store, second).write_bytes(b"{corrupt")
    with pytest.raises(Pass218PersistenceValidationError):
        store.restore(allow_previous_generation=False)


def test_checkpoint_seal_tamper_is_rejected(tmp_path: Path) -> None:
    target, _, _ = _commit_into()
    checkpoint = Pass218DurableCanonicalStore(tmp_path).checkpoint(target)["checkpoint"]
    tampered = json.loads(json.dumps(checkpoint))
    tampered["generation_sequence"] += 1
    with pytest.raises(
        Pass218PersistenceValidationError,
        match="P218_I7_CHECKPOINT_SEAL_MISMATCH",
    ):
        validate_checkpoint(tampered)


def test_embedded_iteration6_receipt_tamper_is_rejected_even_with_resealed_checkpoint(tmp_path: Path) -> None:
    target, receipt, _ = _commit_into()
    store = Pass218DurableCanonicalStore(tmp_path)
    original = store.checkpoint(target)["checkpoint"]
    tampered = json.loads(json.dumps(original))
    tampered["commits_by_authorization_hash72"][receipt["authorization_hash72"]][
        "projection_sha256"
    ] = "0" * 64
    from hhs_runtime.pass218.persistence import seal_checkpoint

    payload = {
        key: value
        for key, value in tampered.items()
        if key not in {
            "checkpoint_sha256",
            "checkpoint_hash72",
            "validation_hash72",
            "checkpoint_hash216",
            "hash216_semantics",
        }
    }
    resealed = seal_checkpoint(payload)
    with pytest.raises(
        Pass218PersistenceValidationError,
        match="P218_I7_COMMIT_HASH72_MISMATCH",
    ):
        validate_checkpoint(resealed)


def test_vm81_snapshot_tamper_is_rejected_even_with_resealed_checkpoint(tmp_path: Path) -> None:
    target, _, _ = _commit_into()
    original = Pass218DurableCanonicalStore(tmp_path).checkpoint(target)["checkpoint"]
    tampered = json.loads(json.dumps(original))
    raw = bytearray(__import__("base64").b64decode(tampered["vm81_snapshot_b64"]))
    raw[0] ^= 1
    tampered["vm81_snapshot_b64"] = __import__("base64").b64encode(raw).decode("ascii")
    tampered["vm81_snapshot_sha256"] = sha256(raw).hexdigest()
    from hhs_runtime.pass218.persistence import seal_checkpoint

    payload = {
        key: value
        for key, value in tampered.items()
        if key not in {
            "checkpoint_sha256",
            "checkpoint_hash72",
            "validation_hash72",
            "checkpoint_hash216",
            "hash216_semantics",
        }
    }
    resealed = seal_checkpoint(payload)
    with pytest.raises(
        Pass218PersistenceValidationError,
        match="P218_I7_FINAL_PROJECTION_SHA256_MISMATCH",
    ):
        validate_checkpoint(resealed)


def test_noncanonical_persisted_json_is_rejected(tmp_path: Path) -> None:
    target, _, _ = _commit_into()
    store = Pass218DurableCanonicalStore(tmp_path)
    result = store.checkpoint(target)
    active = _active_generation_path(store, result)
    value = json.loads(active.read_text("utf-8"))
    active.write_text(json.dumps(value, indent=2), "utf-8")
    with pytest.raises(
        Pass218PersistenceValidationError,
        match="P218_I7_PERSISTED_JSON_NONCANONICAL",
    ):
        store.restore(allow_previous_generation=False)


def test_manifest_tamper_is_rejected_before_loading_generation(tmp_path: Path) -> None:
    target, _, _ = _commit_into()
    store = Pass218DurableCanonicalStore(tmp_path)
    result = store.checkpoint(target)
    manifest = json.loads(json.dumps(result["manifest"]))
    manifest["canonical_root_hash72"] = hash72_digest(
        {"domain": "P218-I7-TAMPER"}, b"tamper"
    )
    store.manifest_path.write_bytes(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    with pytest.raises(
        Pass218PersistenceValidationError,
        match="P218_I7_MANIFEST_HASH72_MISMATCH",
    ):
        store.restore()


def test_persistence_artifacts_do_not_retain_verbatim_source(tmp_path: Path) -> None:
    source = _source("NO_SOURCE")
    target, _, _ = _commit_into(label="NO_SOURCE", sequence=7)
    store = Pass218DurableCanonicalStore(tmp_path)
    result = store.checkpoint(target)
    assert source.encode("utf-8") not in store.manifest_path.read_bytes()
    assert source.encode("utf-8") not in _active_generation_path(store, result).read_bytes()
    serialized = json.dumps(
        {"manifest": result["manifest"], "checkpoint": result["checkpoint"]},
        sort_keys=True,
    )
    assert source not in serialized
    assert '"verbatim_source_retained": true' not in serialized.lower()


def test_restored_target_can_continue_only_through_a_new_iteration6_authorization(tmp_path: Path) -> None:
    target, _, _ = _commit_into(label="A", sequence=1)
    store = Pass218DurableCanonicalStore(tmp_path)
    store.checkpoint(target)
    restored = store.restore().target
    before = restored.root_hash72()
    _, receipt, _ = _commit_into(restored, label="B", sequence=2)
    assert restored.root_hash72() != before
    assert restored.record()["canonical_commit_count"] == 2
    assert restored.authorization_consumed(receipt["authorization_hash72"]) is True


def test_restored_target_can_be_checkpointed_as_next_generation(tmp_path: Path) -> None:
    target, _, _ = _commit_into(label="A", sequence=1)
    store = Pass218DurableCanonicalStore(tmp_path)
    first = store.checkpoint(target)
    restored = store.restore().target
    _commit_into(restored, label="B", sequence=2)
    second = store.checkpoint(restored)
    replayed = store.restore()
    assert second["manifest"]["generation_sequence"] == 1
    assert replayed.target.root_hash72() == restored.root_hash72()
    assert second["manifest"]["previous_checkpoint_sha256"] == first["checkpoint"]["checkpoint_sha256"]


def test_iteration7_persistence_module_does_not_import_pass165() -> None:
    source = (ROOT / "hhs_runtime" / "pass218" / "persistence.py").read_text("utf-8")
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert all("pass165" not in name.lower() for name in imported)


def test_iteration7_preserves_no_authoritative_float_literal_rule() -> None:
    for path in sorted((ROOT / "hhs_runtime" / "pass218").glob("*.py")):
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, f"{path}: authoritative float literal(s) found"
