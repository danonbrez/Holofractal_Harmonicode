from __future__ import annotations

from hashlib import sha256

from hhs_runtime.hhs_pass217_checkpoint7_content_reuse_v1 import (
    CHECKPOINT7_AUTHORITIES,
    CHECKPOINT7_AUTHORITY_MAP,
    CONTENT_SOURCE_REQUEST_SCHEMA,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import compose_bound_route_ingress
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache
from hhs_runtime.pass165.ingestion import MultimodalLearningService


def _decisions(decision):
    reachability = decision["inherited_execution_authority_reachability"]
    return {row["authority_id"]: row for row in reachability["decisions"]}


def _request(source_text: str, **extra):
    return {
        "schema": CONTENT_SOURCE_REQUEST_SCHEMA,
        "source_text": source_text,
        "declared_media_type": "TEXT",
        "provenance": "pass217-checkpoint7",
        "authorization_scope": "P217_CHECKPOINT7",
        "expected_source_hash": sha256(source_text.encode("utf-8")).hexdigest(),
        **extra,
    }


def _seed(service: MultimodalLearningService, source_text: str):
    return service.ingest_source(
        source_text.encode("utf-8"),
        declared_media_type="TEXT",
        provenance="pass217-checkpoint7",
        authorization_scope="P217_CHECKPOINT7",
    )


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
    assert incremental["reference_symbol"] == "MultimodalTokenizer.tokenize"
    assert incremental["incremental_delta_callable_proven"] is False
    assert incremental["full_source_tokenizer_may_not_be_reclassified_as_incremental"] is True
    assert incremental["applicable_without_proven_callable"] == "FAIL_CLOSED"


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

    reachability = decision["inherited_execution_authority_reachability"]
    assert reachability["required_authority_count"] == 9
    assert tuple(reachability["checkpoint_scope"][-2:]) == CHECKPOINT7_AUTHORITIES


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
    assert witness["receipt_hash72"] == seed["receipt"]["receipt_hash72"]
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
    assert content["observed_facts"]["committed_source_receipt_present"] is False
    assert content["observed_facts"]["content_addressed_reuse_candidate_present"] is False
    assert before["ingestion_epoch"] == after["ingestion_epoch"] == 0
    assert before["sources"] == after["sources"] == 0
    assert before["vm81"]["state_hash72"] == after["vm81"]["state_hash72"]


def test_partial_content_reuse_context_is_applicable_and_fails_closed(tmp_path) -> None:
    service = MultimodalLearningService()
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "content_addressed_source_reuse": {
                "schema": CONTENT_SOURCE_REQUEST_SCHEMA,
                "declared_media_type": "TEXT",
                "provenance": "pass217-checkpoint7",
                "authorization_scope": "P217_CHECKPOINT7",
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
        {
            "service": "example",
            "content_addressed_source_reuse": request,
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        source_reuse_service=service,
    )

    assert decision is not None and decision["ok"] is False
    content = _decisions(decision)["content_addressed_source_reuse"]
    assert content["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in content["reasons"]
    assert "REJECT_PASS165_CONTENT_REUSE_SCOPE_OR_PROVENANCE_MISMATCH" in content[
        "traversal_witness"
    ]["reason"]


def test_incremental_tokenization_marker_fails_closed_without_proven_callable(tmp_path) -> None:
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
        {
            "service": "example",
            "content_addressed_source_reuse": request,
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        source_reuse_service=service,
    )

    assert decision is not None and decision["ok"] is False
    assert decision["propagation_allowed"] is False
    decisions = _decisions(decision)
    assert decisions["content_addressed_source_reuse"]["state"] == "ACTIVE_IN_PATH"
    incremental = decisions["incremental_tokenization"]
    assert incremental["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in incremental["reasons"]
    assert incremental["traversal_witness"]["reason"] == (
        "REJECT_INCREMENTAL_TOKENIZATION_INHERITED_CALLABLE_UNPROVEN"
    )
    facts = incremental["traversal_witness"]["applicability_facts"]
    assert facts["incremental_tokenization_domain_present"] is True
    assert facts["incremental_delta_callable_proven"] is False
    assert set(facts["incremental_tokenization_markers"]) == {
        "changed_source_spans",
        "parent_source_hash",
    }
