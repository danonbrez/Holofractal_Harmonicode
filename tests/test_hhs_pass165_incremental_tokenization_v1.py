from __future__ import annotations

import pytest

from hhs_runtime.pass165.incremental_tokenization import (
    derive_changed_line_spans,
    incremental_tokenize,
    validate_incremental_equivalence,
)
from hhs_runtime.pass165.ingestion import IngestionError, MultimodalLearningService


PROVENANCE = "pass217-incremental-tokenization"
SCOPE = "P217_INCREMENTAL_TOKENIZATION"


def _parent(service: MultimodalLearningService, text: str):
    raw = text.encode("utf-8")
    service.ingest_source(
        raw,
        declared_media_type="TEXT",
        provenance=PROVENANCE,
        authorization_scope=SCOPE,
    )
    return service.analyze(
        raw,
        declared_media_type="TEXT",
        provenance=PROVENANCE,
        authorization_scope=SCOPE,
    )


def _child_source(service: MultimodalLearningService, text: str):
    return service.capture_source(
        text.encode("utf-8"),
        declared_media_type="TEXT",
        provenance=PROVENANCE,
        authorization_scope=SCOPE,
    )


def test_changed_line_replacement_matches_full_pass165_tokenization() -> None:
    service = MultimodalLearningService()
    parent_text = "alpha one\nbeta two\ngamma three\n"
    child_text = "alpha one\nbeta changed words\ngamma three\n"
    parent = _parent(service, parent_text)
    child = _child_source(service, child_text)

    result = incremental_tokenize(parent.source, parent.tokens, child)
    equivalence = validate_incremental_equivalence(result, child)

    assert equivalence["equal"] is True
    assert result.common_prefix_line_count == 1
    assert result.common_suffix_line_count == 1
    assert result.reused_parent_observation_count > 0
    assert result.retokenized_child_token_count > 0
    assert 0 < result.lexically_scanned_child_bytes < result.child_total_bytes
    assert result.byte_shift_after_change == len(" changed words".encode()) - len(" two".encode())
    assert result.line_shift_after_change == 0


def test_inserted_line_rebases_suffix_spans_and_line_paths_exactly() -> None:
    service = MultimodalLearningService()
    parent_text = "first line\nsecond line\nthird line\n"
    child_text = "first line\ninserted exact line\nsecond line\nthird line\n"
    parent = _parent(service, parent_text)
    child = _child_source(service, child_text)

    result = incremental_tokenize(parent.source, parent.tokens, child)
    equivalence = validate_incremental_equivalence(result, child)

    assert equivalence["equal"] is True
    assert result.common_prefix_line_count == 1
    assert result.common_suffix_line_count == 2
    assert result.line_shift_after_change == 1
    assert result.byte_shift_after_change == len("inserted exact line\n".encode())
    assert any(token.structural_path == "line/3" for token in result.tokens)
    assert result.lexically_scanned_child_bytes == len("inserted exact line\n".encode())


def test_utf8_edit_uses_exact_byte_spans_and_matches_full_reference() -> None:
    service = MultimodalLearningService()
    parent_text = "header\ncafé λ\nfooter\n"
    child_text = "header\ncafé λ changed ✓\nfooter\n"
    parent = _parent(service, parent_text)
    child = _child_source(service, child_text)

    spans = derive_changed_line_spans(parent_text.encode(), child_text.encode())
    result = incremental_tokenize(parent.source, parent.tokens, child)
    equivalence = validate_incremental_equivalence(result, child)

    assert equivalence["equal"] is True
    assert list(result.parent_changed_span) == list(spans["parent_changed_span"])
    assert list(result.child_changed_span) == list(spans["child_changed_span"])
    assert result.common_prefix_line_count == 1
    assert result.common_suffix_line_count == 1
    assert result.lexically_scanned_child_bytes == len("café λ changed ✓\n".encode("utf-8"))


def test_no_change_is_not_a_valid_incremental_delta() -> None:
    service = MultimodalLearningService()
    text = "same source\n"
    parent = _parent(service, text)
    child = _child_source(service, text)
    with pytest.raises(IngestionError, match="P165_INCREMENTAL_NO_SOURCE_CHANGE"):
        incremental_tokenize(parent.source, parent.tokens, child)
