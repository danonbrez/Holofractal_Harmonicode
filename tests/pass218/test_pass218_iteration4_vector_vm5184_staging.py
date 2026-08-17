from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import COORDINATES, SNAPSHOT_BYTES
from hhs_runtime.pass165.ingestion import MultimodalLearningService
from hhs_runtime.pass175.runtime import InstructionAddress
from hhs_runtime.pass218 import (
    ClosedTransactionVectorVM5184Adapter,
    NonAuthoritativeVectorStageStore,
    Pass218VectorStageValidationError,
    SourceTransaction,
)

ROOT = Path(__file__).resolve().parents[2]


def _source() -> str:
    return (
        "A synthetic narrative reference exists only to exercise transient ingress. "
        "The runtime must preserve structural counts and hashes without retaining "
        "this sentence or granting truth, action, vector-store, or VM81 authority. "
        "A second paragraph gives deterministic succession and dialogue structure."
    )


def _beat(ordinal: int, label: str) -> dict[str, object]:
    span = f"synthetic-span-{ordinal}-{label}".encode("utf-8")
    relation_types = ["TEMPORAL_SUCCESSION"]
    if ordinal % 2:
        relation_types.append("DIALOGUE_RELATION")
    payload = {
        "ordinal": ordinal,
        "source_span_sha256": sha256(span).hexdigest(),
        "paragraph_count": 1,
        "token_count": 12 + ordinal,
        "sentence_count": 2,
        "dialogue_turn_count": ordinal % 2,
        "perspective_counts": {
            "first_person": ordinal,
            "second_person": 0,
            "third_person": 1,
        },
        "negation_count": ordinal % 2,
        "modal_count": 1,
        "authority_count": 1,
        "temporal_count": 1,
        "dominant_perspective": "THIRD_PERSON",
        "relation_types": sorted(relation_types),
        "distinction_mentions": [],
        "verbatim_source_retained": False,
    }
    payload["beat_hash72"] = hash72_digest(
        {"domain": "HHS-P218-NARRATIVE-BEAT-I2-V1"}, payload
    )
    return payload


def _candidate(source: str | None = None, *, label: str = "A") -> dict[str, object]:
    source = _source() if source is None else source
    genesis = hash72_digest({"domain": "P218-I4-TEST-GENESIS"}, label.encode())
    hydration = hash72_digest({"domain": "P218-I4-TEST-HYDRATION"}, label.encode())
    validation = hash72_digest({"domain": "P218-I4-TEST-VALIDATION"}, label.encode())
    return {
        "schema": "HHS-P218-NARRATIVE-HYDRATION-CANDIDATE-I2-V1",
        "hydrator_version": "HHS-P218-NARRATIVE-HYDRATOR-I2-V1",
        "source_id": f"iteration4-{label}",
        "source_sha256": sha256(source.encode("utf-8")).hexdigest(),
        "source_epistemic_class": "FICTIONAL_COUNTERFACTUAL",
        "genesis_seed_hash72": genesis,
        "grammar_rule_set_hash72": hash72_digest(
            {"domain": "P218-I4-TEST-GRAMMAR"}, label.encode()
        ),
        "beats": [_beat(index, label) for index in range(3)],
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


def _closed_snapshot(*, label: str = "A") -> dict[str, object]:
    source = _source()
    transaction = SourceTransaction.begin(_candidate(source, label=label), source)
    closure = transaction.commit_and_purge()
    assert closure["managed_buffer_cleared"] is True
    return transaction.snapshot()


def test_staging_requires_closed_transaction_and_purge_proof() -> None:
    source = _source()
    staged = SourceTransaction.begin(_candidate(source), source).snapshot()
    adapter = ClosedTransactionVectorVM5184Adapter()
    with pytest.raises(
        Pass218VectorStageValidationError, match="P218_I4_TRANSACTION_NOT_CLOSED"
    ):
        adapter.stage(staged)


def test_closed_transaction_stages_pass217_candidate_vector_entry() -> None:
    record = ClosedTransactionVectorVM5184Adapter().stage(_closed_snapshot())
    entry = record["vector_entry"]
    assert entry["schema"] == "HHS_PASS_217_VECTOR_STORE_ENTRY_V1"
    assert entry["admission_status"] == "CANDIDATE"
    assert record["authoritative_vector_store_promotion"] is False
    assert record["canonical_vm81_commit_invoked"] is False
    assert record["canonical_learning_commit_invoked"] is False


def test_projection_is_exact_inherited_5184_geometry() -> None:
    record = ClosedTransactionVectorVM5184Adapter().stage(_closed_snapshot())
    entry = record["vector_entry"]
    assert record["vm5184_projection_bytes"] == SNAPSHOT_BYTES == 648
    assert len(entry["forward_support"]) + len(entry["inverse_support"]) == COORDINATES
    assert set(entry["forward_support"]).isdisjoint(entry["inverse_support"])
    assert sorted(entry["forward_support"] + entry["inverse_support"]) == list(
        range(COORDINATES)
    )


def test_pass175_instruction_addressing_matches_ordered_path() -> None:
    record = ClosedTransactionVectorVM5184Adapter().stage(_closed_snapshot())
    for item in record["vector_entry"]["ordered_path"]:
        _, state, _, cell, _, operation = item.split("/")
        address = InstructionAddress.from_state(int(state))
        assert address.cell == int(cell)
        assert address.operation == int(operation)
        assert address.state == int(state)


def test_vector_entry_matches_inherited_pass217_required_shape() -> None:
    schema = json.loads(
        (ROOT / "contracts" / "pass217" / "vector_store.schema.json").read_text("utf-8")
    )
    record = ClosedTransactionVectorVM5184Adapter().stage(_closed_snapshot())
    entry = record["vector_entry"]
    assert set(entry) == set(schema["required"])
    assert schema["additionalProperties"] is False
    assert entry["schema"] == schema["properties"]["schema"]["const"]
    assert entry["admission_status"] in schema["properties"]["admission_status"]["enum"]


def test_staging_hash216_is_valid_and_semantically_ordered() -> None:
    record = ClosedTransactionVectorVM5184Adapter().stage(_closed_snapshot())
    value = record["staging_hash216"]
    assert len(value) == 216
    assert all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))
    assert record["hash216_semantics"] == [
        "CLOSED_SOURCE_TRANSACTION",
        "VECTOR_VM5184_STAGE_CANDIDATE",
        "STAGING_VALIDATION_RECEIPT",
    ]


def test_exact_replay_produces_identical_stage_record() -> None:
    snapshot = _closed_snapshot()
    first = ClosedTransactionVectorVM5184Adapter().stage(snapshot)
    second = ClosedTransactionVectorVM5184Adapter().stage(snapshot)
    assert first == second


def test_content_addressed_stage_store_reuses_identical_candidate() -> None:
    snapshot = _closed_snapshot()
    store = NonAuthoritativeVectorStageStore()
    adapter = ClosedTransactionVectorVM5184Adapter(stage_store=store)
    first = adapter.stage(snapshot)
    second = adapter.stage(snapshot)
    assert first == second
    assert store.record()["candidate_count"] == 1


def test_different_closed_structural_state_changes_vector_identity() -> None:
    first = ClosedTransactionVectorVM5184Adapter().stage(_closed_snapshot(label="A"))
    second = ClosedTransactionVectorVM5184Adapter().stage(_closed_snapshot(label="B"))
    assert first["vector_entry"]["entry_id_sha256"] != second["vector_entry"]["entry_id_sha256"]
    assert first["staging_hash72"] != second["staging_hash72"]


def test_verbatim_source_is_not_retained_in_stage_record() -> None:
    record = ClosedTransactionVectorVM5184Adapter().stage(_closed_snapshot())
    serialized = json.dumps(record, sort_keys=True)
    assert _source() not in serialized
    assert record["verbatim_source_retained"] is False
    assert record["truth_promotion"] is False
    assert record["action_authority_minted"] is False


def test_staging_does_not_call_pass165_learning_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("canonical learning commit must not be invoked")

    monkeypatch.setattr(MultimodalLearningService, "commit_learning_epoch", forbidden)
    record = ClosedTransactionVectorVM5184Adapter().stage(_closed_snapshot())
    assert record["canonical_learning_commit_invoked"] is False


def test_invalid_snapshot_is_rejected_before_vector_staging() -> None:
    snapshot = _closed_snapshot()
    snapshot["snapshot_hash72"] = "x" * 72
    with pytest.raises(
        Pass218VectorStageValidationError, match="P218_I4_TRANSACTION_RESTORE_INVALID"
    ):
        ClosedTransactionVectorVM5184Adapter().stage(snapshot)


def test_stage_store_rejects_authority_escalation() -> None:
    adapter = ClosedTransactionVectorVM5184Adapter()
    candidate = adapter.build(_closed_snapshot())
    entry = dict(candidate.vector_entry)
    entry["admission_status"] = "VM81_ADMITTED"
    escalated = type(candidate)(
        transaction_id_hash72=candidate.transaction_id_hash72,
        transaction_hash216=candidate.transaction_hash216,
        structural_record_hash72=candidate.structural_record_hash72,
        purge_receipt_hash72=candidate.purge_receipt_hash72,
        vector_entry=entry,
        projection_bytes=candidate.projection_bytes,
        projection_hash72=candidate.projection_hash72,
        projection_sha256=candidate.projection_sha256,
        staging_hash72=candidate.staging_hash72,
        validation_hash72=candidate.validation_hash72,
        staging_hash216=candidate.staging_hash216,
    )
    with pytest.raises(
        Pass218VectorStageValidationError, match="P218_I4_STAGE_NOT_CANDIDATE"
    ):
        NonAuthoritativeVectorStageStore().stage(escalated)


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
