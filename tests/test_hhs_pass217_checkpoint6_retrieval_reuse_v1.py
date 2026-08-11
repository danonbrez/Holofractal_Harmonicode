from __future__ import annotations

from pathlib import Path

from hhs_runtime.hhs_pass217_checkpoint6_retrieval_reuse_v1 import (
    CHECKPOINT6_AUTHORITIES,
    CHECKPOINT6_NATIVE_CALLABLES,
    RETRIEVAL_REQUEST_SCHEMA,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import compose_bound_route_ingress
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache


def _decisions(decision):
    reachability = decision["inherited_execution_authority_reachability"]
    return {row["authority_id"]: row for row in reachability["decisions"]}


def test_checkpoint6_maps_exact_repository_native_callables() -> None:
    assert tuple(CHECKPOINT6_NATIVE_CALLABLES) == CHECKPOINT6_AUTHORITIES
    assert CHECKPOINT6_NATIVE_CALLABLES["reusable_pattern_cache"] == {
        "origin_pass": 86,
        "module": (
            "native_projects.hhs_bifurcation_calibration."
            "hhs_pass086_deterministic_multimodal_pattern_admission_v1"
        ),
        "symbol": "run",
        "callable_role": "deterministic reusable multimodal pattern cache admission",
    }
    for authority_id in (
        "vector_shortlist",
        "exact_compatibility_filtering",
        "exact_delta_cost_reranking",
    ):
        assert CHECKPOINT6_NATIVE_CALLABLES[authority_id]["origin_pass"] == 205
        assert CHECKPOINT6_NATIVE_CALLABLES[authority_id]["symbol"] == (
            "Pass205ContinuationRuntime.retrieve"
        )


def test_no_candidate_domain_is_mechanically_not_applicable(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
    )
    assert decision is not None and decision["ok"] is True
    decisions = _decisions(decision)

    pattern = decisions["reusable_pattern_cache"]
    assert pattern["state"] == "NOT_APPLICABLE"
    assert pattern["mechanically_proven"] is True
    assert pattern["predicate"] == "pattern_candidate_domain_present == false"
    assert pattern["observed_facts"]["pattern_candidate_domain_present"] is False

    for authority_id in (
        "vector_shortlist",
        "exact_compatibility_filtering",
        "exact_delta_cost_reranking",
    ):
        row = decisions[authority_id]
        assert row["state"] == "NOT_APPLICABLE"
        assert row["mechanically_proven"] is True
        assert row["predicate"] == "retrieval_candidate_domain_present == false"
        assert row["observed_facts"]["retrieval_candidate_domain_present"] is False

    reachability = decision["inherited_execution_authority_reachability"]
    assert reachability["required_authority_count"] == 7
    assert tuple(reachability["checkpoint_scope"][-4:]) == CHECKPOINT6_AUTHORITIES


def test_real_route_slice_traverses_pattern_cache_and_pass205_retrieval_chain(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("HHS_PASS205_DB", str(tmp_path / "module-default.sqlite3"))
    from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
        Pass205ContinuationRuntime,
    )
    from native_projects.hhs_bifurcation_calibration.hhs_pass086_deterministic_multimodal_pattern_admission_v1 import (
        default_workload,
    )

    runtime = Pass205ContinuationRuntime(tmp_path / "checkpoint6.sqlite3")
    genesis = runtime.snapshot(runtime.genesis_root216)
    child = runtime.advance(
        parent_root216=genesis["continuation_root216"],
        expected_parent_receipt_hash72=genesis["receipt_hash72"],
        events=[{"cell": 0, "control_g": 0, "xor_mask": 1}],
    )
    incompatible = runtime.advance(
        parent_root216=child["continuation_root216"],
        expected_parent_receipt_hash72=child["receipt_hash72"],
        events=[{"cell": 1, "control_g": 0, "xor_mask": 2}],
    )
    with runtime._transaction() as connection:
        connection.execute(
            "UPDATE vectors SET schema_root216=? WHERE continuation_root216=?",
            ("checkpoint6-incompatible-schema", incompatible["continuation_root216"]),
        )

    repo_root = Path(__file__).resolve().parents[1]
    pattern_workload = default_workload(
        repo_root,
        workload_id="pass217-checkpoint6-real-route-slice",
        instance_count=4,
        modalities=("VIDEO", "AUDIO"),
        roles_per_instance=2,
        pattern_family_count=1,
    )
    payload = {
        "service": "example",
        "reusable_pattern_workload": pattern_workload,
        "retrieval_reuse": {
            "schema": RETRIEVAL_REQUEST_SCHEMA,
            "target_state_words": child["state_words"],
            "schema_root216": runtime.schema_root216,
            "constraint_root216": runtime.constraint_root216,
            "top_k": 2,
        },
    }
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        payload,
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
        retrieval_runtime=runtime,
        pattern_repo_root=repo_root,
    )

    assert decision is not None and decision["ok"] is True
    assert decision["propagation_allowed"] is True
    decisions = _decisions(decision)
    for authority_id in CHECKPOINT6_AUTHORITIES:
        assert decisions[authority_id]["state"] == "ACTIVE_IN_PATH"
        assert decisions[authority_id]["witness_root"]

    pattern = decisions["reusable_pattern_cache"]["traversal_witness"]
    assert pattern["status"] == "ADMIT_REUSABLE_PATTERN_CACHE_TRAVERSAL"
    assert pattern["cache_entry_count"] >= 1
    assert pattern["cache_is_authority"] is False
    assert pattern["replay_verified"] is True

    shortlist = decisions["vector_shortlist"]["traversal_witness"]
    compatibility = decisions["exact_compatibility_filtering"]["traversal_witness"]
    rerank = decisions["exact_delta_cost_reranking"]["traversal_witness"]
    assert shortlist["status"] == "ADMIT_VECTOR_SHORTLIST_TRAVERSAL"
    assert shortlist["shortlist_candidate_count"] == 2
    assert shortlist["approximate_similarity_is_authority"] is False
    assert compatibility["status"] == "ADMIT_EXACT_COMPATIBILITY_FILTER_TRAVERSAL"
    assert compatibility["rejected_candidate_count"] == 1
    assert compatibility["rejected_candidates"][0]["reason"] == "SCHEMA_ROOT_MISMATCH"
    assert rerank["status"] == "ADMIT_EXACT_DELTA_COST_RERANK_TRAVERSAL"
    assert rerank["exact_rerank_applied"] is True
    assert rerank["selected_parent_root216"] == child["continuation_root216"]
    assert rerank["selected_exact_delta_cost"] == 0
    assert (
        decisions["vector_shortlist"]["witness_root"]
        == decisions["exact_compatibility_filtering"]["witness_root"]
        == decisions["exact_delta_cost_reranking"]["witness_root"]
    )


def test_partial_retrieval_marker_is_applicable_and_fails_closed(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "retrieval_reuse": {
                "schema": RETRIEVAL_REQUEST_SCHEMA,
                "top_k": 2,
            },
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
    )
    assert decision is not None and decision["ok"] is False
    assert decision["propagation_allowed"] is False
    decisions = _decisions(decision)
    assert decisions["reusable_pattern_cache"]["state"] == "NOT_APPLICABLE"
    for authority_id in (
        "vector_shortlist",
        "exact_compatibility_filtering",
        "exact_delta_cost_reranking",
    ):
        assert decisions[authority_id]["state"] is None
        assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in decisions[authority_id]["reasons"]
        assert decisions[authority_id]["traversal_witness"]["reason"] == (
            "REJECT_PASS205_RETRIEVAL_TARGET_STATE_MISSING"
        )


def test_partial_pattern_marker_is_applicable_and_fails_closed(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "reusable_pattern_workload": {"workload_id": "partial"},
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
    )
    assert decision is not None and decision["ok"] is False
    decisions = _decisions(decision)
    pattern = decisions["reusable_pattern_cache"]
    assert pattern["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in pattern["reasons"]
    assert pattern["traversal_witness"]["reason"] == "REJECT_PASS086_PATTERN_WORKLOAD_SCHEMA"
    for authority_id in (
        "vector_shortlist",
        "exact_compatibility_filtering",
        "exact_delta_cost_reranking",
    ):
        assert decisions[authority_id]["state"] == "NOT_APPLICABLE"
