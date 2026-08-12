from __future__ import annotations

from hashlib import sha256

from hhs_runtime.hhs_pass217_checkpoint7_content_reuse_v1 import (
    CHECKPOINT7_AUTHORITIES,
    CHECKPOINT7_AUTHORITY_MAP,
    CONTENT_SOURCE_REQUEST_SCHEMA,
    INCREMENTAL_TOKENIZATION_REQUEST_SCHEMA,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import compose_bound_route_ingress
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache
from hhs_runtime.pass165.incremental_tokenization import derive_changed_line_spans
from hhs_runtime.pass165.ingestion import MultimodalLearningService


PROVENANCE = "pass217-checkpoint7"
SCOPE = "P217_CHECKPOINT7"


def _decisions(decision):
    reachability = decision["inherited_execution_authority_reachability"]
    return {row["authority_id"]: row for row in reachability["decisions"]}


def _request(source_text: str, **extra):
    return {
        "schema": CONTENT_SOURCE_REQUEST_SCHEMA,
        "source_text": source_text,
        "declared_media_type": "TEXT",
        "provenance": PROVENANCE,
        "authorization_scope": SCOPE,
        "expected_source_hash": sha256(source_text.encode("utf-8")).hexdigest(),
        **extra,
    }


def _seed(service: MultimodalLearningService, source_text: str):
    return service.ingest_source(
        source_text.encode("utf-8"),
        declared_media_type="TEXT",
        provenance=PROVENANCE,
        authorization_scope=SCOPE,
    )


def _incremental_request(
    service: MultimodalLearningService,
    parent_text: str,
    child_text: str,
    **extra,
):
    parent_raw = parent_text.encode("utf-8")
    child_raw = child_text.encode("utf-8")
    parent = service.analyze(
        parent_raw,
        declared_media_type="TEXT",
        provenance=PROVENANCE,
        authorization_scope=SCOPE,
    )
    spans = derive_changed_line_spans(parent_raw, child_raw)
    return {
        "schema": INCREMENTAL_TOKENIZATION_REQUEST_SCHEMA,
        "parent_source_text": parent_text,
        "child_source_text": child_text,
        "parent_source_hash": parent.source.source_hash,
        "parent_token_stream_root": parent.token_stream_root,
        "expected_child_source_hash": sha256(child_raw).hexdigest(),
        "declared_media_type": "TEXT",
        "provenance": PROVENANCE,
        "authorization_scope": SCOPE,
        "changed_source_spans": {
            "parent": list(spans["parent_changed_span"]),
            "child": list(spans["child_changed_span"]),
        },
        **extra,
    }


def test_checkpoint7_preserves_exact_authority_boundary() -> None:
    assert CHECKPOINT7_AUTHORITIES == (
        "content_addressed_source_reuse",
        "incremental_tokenization",
    )
    content = CHECKPOINT7_AUTHORITY_MAP["content_addressed_source_reuse"]
    assert content["origin_pass"] == 165
    assert content["module"] == "hhs_runtime.pass165.ingestion"
    assert content["symbol"] == "MultimodalLearningService.ingest_source"
    assert content["reuse_branch_required"] is True
    assert content["mutation_permitted_in_preflight"] is False

    incremental = CHECKPOINT7_AUTHORITY_MAP["incremental_tokenization"]
    assert incremental["origin_pass"] == 165
    assert incremental["repair_extension_pass"] == 217
    assert incremental["module"] == "hhs_runtime.pass165.incremental_tokenization"
    assert incremental["symbol"] == "incremental_tokenize"
    assert incremental["reference_symbol"] == "MultimodalTokenizer.tokenize"
    assert incremental["incremental_delta_callable_proven"] is True
    assert incremental["changed_region_granularity"] == "WHOLE_UTF8_TEXT_LINES"
    assert incremental["parent_committed_receipt_required"] is True
    assert incremental["parent_token_stream_root_required"] is True
    assert incremental["declared_changed_spans_must_equal_derived_spans"] is True
    assert incremental["floating_point_authority"] is False


def test_no_source_or_incremental_domain_is_mechanically_not_applicable(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
    )
    assert decision is not None and decision["ok"] is True
    decisions = _decisions(decision)

    content = decisions["content_addressed_source_reuse"]
    assert content["state"] == "NOT_APPLICABLE"
    assert content["mechanically_proven"] is True
    assert content["predicate"] == "content_source_domain_present == false"
    assert content["observed_facts"]["content_source_domain_present"] is False

    incremental = decisions["incremental_tokenization"]
    assert incremental["state"] == "NOT_APPLICABLE"
    assert incremental["mechanically_proven"] is True
    assert incremental["predicate"] == "incremental_tokenization_domain_present == false"
    assert incremental["observed_facts"]["incremental_tokenization_domain_present"] is False
    assert incremental["observed_facts"]["incremental_delta_callable_proven"] is True


def test_committed_source_reuse_traverses_pass165_without_preflight_mutation(tmp_path) -> None:
    service = MultimodalLearningService()
    source_text = "alpha alpha beta beta"
    seed = _seed(service, source_text)
    before = service.status()

    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "content_addressed_source_reuse": _request(source_text),
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        source_reuse_service=service,
    )
    after = service.status()

    assert decision is not None and decision["ok"] is True
    assert decision["propagation_allowed"] is True
    decisions = _decisions(decision)
    content = decisions["content_addressed_source_reuse"]
    assert content["state"] == "ACTIVE_IN_PATH"
    assert content["witness_root"] == seed["receipt"]["receipt_hash72"]
    witness = content["traversal_witness"]
    assert witness["status"] == "ADMIT_CONTENT_ADDRESSED_SOURCE_REUSE_TRAVERSAL"
    assert witness["content_addressed_source_reused"] is True
    assert witness["preflight_mutation_performed"] is False
    assert witness["ingestion_epoch_unchanged"] is True
    assert witness["vm81_state_unchanged"] is True

    incremental = decisions["incremental_tokenization"]
    assert incremental["state"] == "NOT_APPLICABLE"
    assert incremental["predicate"] == "incremental_tokenization_domain_present == false"
    assert before["ingestion_epoch"] == after["ingestion_epoch"]
    assert before["vm81"]["state_hash72"] == after["vm81"]["state_hash72"]
    assert before["sources"] == after["sources"] == 1
    assert before["weights"] == after["weights"]


def test_uncommitted_source_is_mechanically_outside_reuse_domain(tmp_path) -> None:
    service = MultimodalLearningService()
    before = service.status()
    source_text = "novel source not yet committed"
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "content_addressed_source_reuse": _request(source_text),
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        source_reuse_service=service,
    )
    after = service.status()

    assert decision is not None and decision["ok"] is True
    content = _decisions(decision)["content_addressed_source_reuse"]
    assert content["state"] == "NOT_APPLICABLE"
    assert content["mechanically_proven"] is True
    assert content["predicate"] == "committed_source_receipt_present == false"
    assert before["ingestion_epoch"] == after["ingestion_epoch"] == 0
    assert before["sources"] == after["sources"] == 0


def test_partial_content_reuse_context_is_applicable_and_fails_closed(tmp_path) -> None:
    service = MultimodalLearningService()
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "content_addressed_source_reuse": {
                "schema": CONTENT_SOURCE_REQUEST_SCHEMA,
                "declared_media_type": "TEXT",
                "provenance": PROVENANCE,
                "authorization_scope": SCOPE,
            },
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        source_reuse_service=service,
    )

    assert decision is not None and decision["ok"] is False
    content = _decisions(decision)["content_addressed_source_reuse"]
    assert content["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in content["reasons"]
    assert "REJECT_PASS165_SOURCE_ENCODING_AMBIGUOUS_OR_MISSING" in content[
        "traversal_witness"
    ]["reason"]


def test_content_reuse_rejects_cross_authorization_scope(tmp_path) -> None:
    service = MultimodalLearningService()
    source_text = "scope-bound repeated source"
    _seed(service, source_text)
    request = _request(source_text, authorization_scope="DIFFERENT_SCOPE")
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "content_addressed_source_reuse": request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        source_reuse_service=service,
    )

    assert decision is not None and decision["ok"] is False
    content = _decisions(decision)["content_addressed_source_reuse"]
    assert content["state"] is None
    assert "REJECT_PASS165_CONTENT_REUSE_SCOPE_OR_PROVENANCE_MISMATCH" in content[
        "traversal_witness"
    ]["reason"]


def test_incremental_tokenization_traverses_real_pass165_delta_and_equals_full(tmp_path) -> None:
    service = MultimodalLearningService()
    parent_text = "alpha one\nbeta two\ngamma three\n"
    child_text = "alpha one\nbeta changed words\ngamma three\n"
    _seed(service, parent_text)
    request = _incremental_request(service, parent_text, child_text)
    before = service.status()

    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "incremental_tokenization": request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        source_reuse_service=service,
    )
    after = service.status()

    assert decision is not None and decision["ok"] is True
    assert decision["propagation_allowed"] is True
    decisions = _decisions(decision)
    assert decisions["content_addressed_source_reuse"]["state"] == "NOT_APPLICABLE"
    incremental = decisions["incremental_tokenization"]
    assert incremental["state"] == "ACTIVE_IN_PATH"
    assert incremental["accepted"] is True
    witness = incremental["traversal_witness"]
    assert witness["status"] == "ADMIT_INCREMENTAL_TOKENIZATION_TRAVERSAL"
    assert witness["incremental_equals_full_tokenization"] is True
    assert witness["unchanged_regions_lexically_rescanned_by_incremental_callable"] is False
    assert witness["full_reference_used_for_equality_validation"] is True
    assert witness["reused_parent_observation_count"] > 0
    assert 0 < witness["lexically_scanned_child_bytes"] < witness["child_total_bytes"]
    assert witness["parent_changed_span"] == request["changed_source_spans"]["parent"]
    assert witness["child_changed_span"] == request["changed_source_spans"]["child"]
    assert witness["child_token_stream_root"] == witness["full_reference_token_stream_root"]
    assert before["ingestion_epoch"] == after["ingestion_epoch"] == 1
    assert before["sources"] == after["sources"] == 1
    assert before["vm81"]["state_hash72"] == after["vm81"]["state_hash72"]


def test_incremental_tokenization_rejects_stale_parent_token_root(tmp_path) -> None:
    service = MultimodalLearningService()
    parent_text = "first\nsecond\nthird\n"
    child_text = "first\nchanged\nthird\n"
    _seed(service, parent_text)
    request = _incremental_request(
        service,
        parent_text,
        child_text,
        parent_token_stream_root="0" * 64,
    )
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "incremental_tokenization": request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        source_reuse_service=service,
    )

    assert decision is not None and decision["ok"] is False
    incremental = _decisions(decision)["incremental_tokenization"]
    assert incremental["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in incremental["reasons"]
    assert "REJECT_INCREMENTAL_TOKENIZATION_PARENT_RECEIPT_TOKEN_ROOT_MISMATCH" in incremental[
        "traversal_witness"
    ]["reason"]


def test_incremental_tokenization_rejects_malformed_changed_span(tmp_path) -> None:
    service = MultimodalLearningService()
    parent_text = "first\nsecond\nthird\n"
    child_text = "first\nchanged\nthird\n"
    _seed(service, parent_text)
    request = _incremental_request(service, parent_text, child_text)
    request["changed_source_spans"] = {"parent": [0], "child": [0, 1]}
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "incremental_tokenization": request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        source_reuse_service=service,
    )

    assert decision is not None and decision["ok"] is False
    incremental = _decisions(decision)["incremental_tokenization"]
    assert incremental["state"] is None
    assert "REJECT_INCREMENTAL_TOKENIZATION_CHANGED_SPAN_INVALID" in incremental[
        "traversal_witness"
    ]["reason"]


def test_incremental_tokenization_rejects_lied_about_changed_span(tmp_path) -> None:
    service = MultimodalLearningService()
    parent_text = "first\nsecond\nthird\n"
    child_text = "first\nchanged longer\nthird\n"
    _seed(service, parent_text)
    request = _incremental_request(service, parent_text, child_text)
    request["changed_source_spans"]["parent"][0] += 1
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "incremental_tokenization": request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        source_reuse_service=service,
    )

    assert decision is not None and decision["ok"] is False
    incremental = _decisions(decision)["incremental_tokenization"]
    assert incremental["state"] is None
    assert "REJECT_INCREMENTAL_TOKENIZATION_PARENT_CHANGED_SPAN_MISMATCH" in incremental[
        "traversal_witness"
    ]["reason"]


def test_incremental_marker_without_exact_request_still_fails_closed(tmp_path) -> None:
    service = MultimodalLearningService()
    source_text = "alpha alpha beta beta"
    _seed(service, source_text)
    request = _request(
        source_text,
        parent_source_hash="parent-source-root",
        changed_source_spans=[[0, 5]],
    )
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "content_addressed_source_reuse": request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        source_reuse_service=service,
    )

    assert decision is not None and decision["ok"] is False
    decisions = _decisions(decision)
    assert decisions["content_addressed_source_reuse"]["state"] == "ACTIVE_IN_PATH"
    incremental = decisions["incremental_tokenization"]
    assert incremental["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in incremental["reasons"]
    assert incremental["traversal_witness"]["reason"] == (
        "REJECT_INCREMENTAL_TOKENIZATION_REQUEST_BUNDLE_COUNT"
    )
    facts = incremental["traversal_witness"]["applicability_facts"]
    assert facts["incremental_tokenization_domain_present"] is True
    assert facts["incremental_delta_callable_proven"] is True
