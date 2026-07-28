from __future__ import annotations
from fractions import Fraction
import pytest

from hhs_runtime.pass165.ingestion import (
    COORDINATES,
    SNAPSHOT_BYTES,
    IngestionError,
    MultimodalLearningService,
    detect_modality,
)


def service():
    return MultimodalLearningService()


def request(modality=None):
    return dict(
        declared_media_type=modality,
        provenance="test-suite",
        authorization_scope="P165_TEST",
    )


def test_detects_text_json_csv_xml_code_and_binary():
    assert detect_modality(b"hello world") == "TEXT"
    assert detect_modality(b'{"a":1}') == "JSON"
    assert detect_modality(b"a,b\n1,2\n") == "CSV"
    assert detect_modality(b"<root><x/></root>") == "XML"
    assert detect_modality(b"def f():\n return 1\n") == "SOURCE_CODE"
    assert detect_modality(b"\x00\xff\x81") == "BINARY_OBJECT"


def test_detects_pdf_image_audio_video():
    assert detect_modality(b"%PDF-1.7\nobj") == "PDF"
    assert detect_modality(b"\x89PNG\r\n\x1a\n" + b"x" * 20) == "IMAGE"
    assert detect_modality(b"RIFF" + b"x" * 20) == "AUDIO"
    assert detect_modality(b"\x00\x00\x00\x18ftypisom" + b"x" * 20) == "VIDEO"


def test_media_spoofing_is_rejected():
    with pytest.raises(IngestionError, match="P165_MEDIA_TYPE_SPOOFING"):
        detect_modality(b"%PDF-1.7", "IMAGE")


def test_source_is_immutable_and_content_addressed():
    instance = service()
    raw = bytearray(b"alpha beta")
    first = instance.capture_source(raw, **request("TEXT"))
    raw[0] = ord("z")
    second = instance.capture_source(b"alpha beta", **request("TEXT"))
    assert first.source_bytes == b"alpha beta"
    assert first == second


def test_empty_compressed_and_unauthorized_sources_rejected():
    instance = service()
    with pytest.raises(IngestionError, match="P165_EMPTY_SOURCE"):
        instance.capture_source(b"", **request())
    with pytest.raises(IngestionError, match="P165_COMPRESSED_CONTAINER_QUARANTINED"):
        instance.capture_source(b"PK\x03\x04x", **request())
    with pytest.raises(IngestionError, match="P165_AUTHORIZATION_REQUIRED"):
        instance.capture_source(b"x", provenance="", authorization_scope="")


def test_text_tokenization_is_deterministic_and_source_spans_recover():
    instance = service()
    source = instance.capture_source("alpha β alpha".encode(), **request("TEXT"))
    first = instance._tokenizer.tokenize(source)
    second = instance._tokenizer.tokenize(source)
    assert first == second
    for token in first:
        recovered = source.source_bytes[token.source_span[0] : token.source_span[1]].decode()
        assert recovered == token.canonical_payload


def test_token_identity_binds_provenance():
    instance = service()
    source = instance.capture_source(b"alpha", **request("TEXT"))
    token = instance._tokenizer.tokenize(source)[0]
    assert len(token.token_id) == 64
    assert token.provenance_root == source.source_hash


def test_binary_tokenization_preserves_block_offsets():
    instance = service()
    raw = bytes(range(256)) * 3
    source = instance.capture_source(raw, **request("BINARY_OBJECT"))
    tokens = instance._tokenizer.tokenize(source)
    assert tokens[0].source_span == (0, 256)
    assert tokens[-1].source_span == (512, 768)


def test_chunk_graph_is_non_destructive_and_bounded():
    instance = service()
    source = instance.capture_source(b"one two three four five", **request("TEXT"))
    tokens = instance._tokenizer.tokenize(source)
    chunks, edges = instance.chunk_tokens(tokens, width=2)
    assert sum(len(chunk.token_ids) for chunk in chunks) == len(tokens)
    assert any(kind == "CONTAINS" for _, _, kind in edges)
    assert any(kind == "FOLLOWS" for _, _, kind in edges)


def test_projection_has_exact_5184_geometry_and_roundtrip():
    instance = service()
    result = instance.analyze(b"alpha beta alpha beta", **request("TEXT"))
    assert len(result.projection_bytes) == SNAPSHOT_BYTES
    assert COORDINATES == 5184
    assert instance.project_5184(result.tokens, result.graph_edges).to_bytes() == result.projection_bytes


def test_projection_determinism_and_tamper_difference():
    first = service().analyze(b"alpha beta", **request("TEXT"))
    second = service().analyze(b"alpha beta", **request("TEXT"))
    changed = service().analyze(b"alpha gamma", **request("TEXT"))
    assert first.projection_hash72 == second.projection_hash72
    assert first.projection_hash72 != changed.projection_hash72


def test_repetition_and_graph_invariants_are_candidates():
    result = service().analyze(b"alpha beta alpha beta", **request("TEXT"))
    classes = {item.candidate_class for item in result.invariant_candidates}
    assert "REPETITION" in classes
    assert "ORDER" in classes or "DEPENDENCY" in classes
    assert all(item.validation_state == "CANDIDATE" for item in result.invariant_candidates)


def test_repeated_source_does_not_amplify_learning():
    instance = service()
    first = instance.ingest_source(b"alpha alpha", **request("TEXT"))
    second = instance.ingest_source(b"alpha alpha", **request("TEXT"))
    assert first["receipt"]["reused"] is False
    assert second["receipt"]["reused"] is True
    assert instance.status()["sources"] == 1


def test_contradiction_is_separate_and_blocks_weight_commit():
    instance = service()
    instance.ingest_source(b"feature=true\nfeature=true\n", **request("TEXT"))
    result = instance.analyze(b"feature=false\nfeature=false\n", **request("TEXT"))
    assert result.contradictions
    assert result.weight_deltas == ()
    with pytest.raises(IngestionError, match="P165_CONTRADICTORY_INVARIANT_PROMOTION"):
        instance.commit_learning_epoch(result)


def test_weight_deltas_are_exact_bounded_and_source_scoped():
    result = service().analyze(b"alpha alpha alpha beta beta", **request("TEXT"))
    assert result.weight_deltas
    for delta in result.weight_deltas:
        exact = Fraction(delta.delta)
        assert 0 < exact <= Fraction(1, 16)
        assert delta.affected_dependencies


def test_vm81_governed_commit_advances_frontier_and_emits_receipt():
    instance = service()
    before = instance.status()["vm81"]["state_hash72"]
    output = instance.ingest_source(b"alpha alpha beta beta", **request("TEXT"))
    after = instance.status()["vm81"]["state_hash72"]
    assert before != after
    receipt = output["receipt"]
    assert len(receipt["receipt_hash72"]) == 72
    assert len(receipt["ingestion_operation_hash216"]) == 64
    assert receipt["incoming_vm81_hash72"] == before
    assert receipt["outgoing_vm81_hash72"] == after


def test_query_invariants_returns_validated_objects():
    instance = service()
    instance.ingest_source(b"a a b b", **request("TEXT"))
    values = instance.query_invariants(candidate_class="REPETITION")
    assert values
    assert all(item["validation_state"] == "VALIDATED" for item in values)


def test_receipt_lookup_and_missing_receipt():
    instance = service()
    output = instance.ingest_source(b"a a", **request("TEXT"))
    source_hash = output["source"]["source_hash"]
    assert instance.get_ingestion_receipt(source_hash)["receipt_hash72"] == output["receipt"]["receipt_hash72"]
    with pytest.raises(IngestionError, match="P165_RECEIPT_NOT_FOUND"):
        instance.get_ingestion_receipt("0" * 64)


def test_deterministic_replay_reconstructs_frontiers():
    instance = service()
    instance.ingest_source(b"a a b b", **request("TEXT"))
    instance.ingest_source(b"c c d d", **request("TEXT"))
    replay = instance.replay_ingestion()
    assert replay["deterministic_replay"] is True
    assert replay["records"] == 2
    assert replay["weight_root"] == instance.weight_root


def test_stale_weight_update_rejected():
    instance = service()
    result = instance.analyze(b"a a b b", **request("TEXT"))
    instance._weights[result.weight_deltas[0].parameter_id] = Fraction(1, 2)
    with pytest.raises(IngestionError, match="P165_STALE_PRIOR_WEIGHT_ROOT"):
        instance.validate_weight_update(result)


def test_operation_identity_binds_source_and_versions():
    first = service().analyze(b"a a", **request("TEXT"))
    second = service().analyze(b"a a", **request("TEXT"))
    changed = service().analyze(b"b b", **request("TEXT"))
    assert first.ingestion_operation_hash216 == second.ingestion_operation_hash216
    assert first.ingestion_operation_hash216 != changed.ingestion_operation_hash216
    assert len(first.ingestion_positions_hash216) == 216


def test_workers_have_no_direct_commit_authority():
    status = service().status()
    assert status["worker_commit_authority"] is False
    assert status["vm81_commit_authority"] is True
