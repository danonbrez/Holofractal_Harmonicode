from __future__ import annotations

from hhs_runtime.hhs_inherited_execution_stage_bridge_v1 import (
    build_initial_inherited_authority_reachability,
    continuation_context_facts,
)
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import build_bound_route_surface
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache


def _decisions(record):
    return {row["authority_id"]: row for row in record["decisions"]}


def test_first_real_stage_slice_traverses_pass43_and_pass44(tmp_path) -> None:
    surface = build_bound_route_surface("api.runtime.services")
    conformance_cache = {}
    semantic_cache = SemanticCompositionCache(tmp_path / "composition-cache.json")

    preflight = execute_surface_preflight(
        surface,
        operation=surface["symbol"],
        cache=conformance_cache,
    )
    record = build_initial_inherited_authority_reachability(
        preflight,
        surface,
        {"method": "GET"},
        semantic_cache=semantic_cache,
    )
    decisions = _decisions(record)

    assert record["admitted"] is True
    assert decisions["conformance_decision_cache"]["state"] == "ACTIVE_IN_PATH"
    assert decisions["semantic_composition_cache"]["state"] == "ACTIVE_IN_PATH"
    assert decisions["predictive_continuation_cache"]["state"] == "NOT_APPLICABLE"
    semantic = decisions["semantic_composition_cache"]["proof"]["traversal_witness"]
    assert semantic["cache_hit"] is False
    assert semantic["validation_status"] == "ADMIT_SEMANTIC_COMPOSITION_CACHE_ENTRY"
    assert semantic["expanded_payload_persisted"] is False
    assert semantic["reconstruction_recipe_hash72"]
    assert record["continuation_applicability_facts"]["continuation_context_present"] is False


def test_repeated_operation_reuses_both_inherited_cache_layers(tmp_path) -> None:
    surface = build_bound_route_surface("api.runtime.services")
    conformance_cache = {}
    semantic_cache = SemanticCompositionCache(tmp_path / "composition-cache.json")

    first_preflight = execute_surface_preflight(
        surface,
        operation=surface["symbol"],
        cache=conformance_cache,
    )
    first = build_initial_inherited_authority_reachability(
        first_preflight,
        surface,
        {"method": "GET"},
        semantic_cache=semantic_cache,
    )
    second_preflight = execute_surface_preflight(
        surface,
        operation=surface["symbol"],
        cache=conformance_cache,
    )
    second = build_initial_inherited_authority_reachability(
        second_preflight,
        surface,
        {"method": "GET"},
        semantic_cache=semantic_cache,
    )

    assert first["admitted"] is True
    assert second["admitted"] is True
    second_decisions = _decisions(second)
    assert second_decisions["conformance_decision_cache"]["proof"]["traversal_witness"]["cache_hit"] is True
    assert second_decisions["semantic_composition_cache"]["proof"]["traversal_witness"]["cache_hit"] is True


def test_continuation_markers_make_predictive_cache_applicable_and_unresolved(tmp_path) -> None:
    surface = build_bound_route_surface("api.runtime.services.dispatch")
    preflight = execute_surface_preflight(
        surface,
        operation=surface["symbol"],
        cache={},
    )
    record = build_initial_inherited_authority_reachability(
        preflight,
        surface,
        {
            "service": "example",
            "payload": {"continuation_cache_root_hash72": "root:continuation"},
        },
        semantic_cache=SemanticCompositionCache(tmp_path / "composition-cache.json"),
    )
    decisions = _decisions(record)

    assert record["admitted"] is False
    assert record["continuation_applicability_facts"]["continuation_context_present"] is True
    assert record["continuation_applicability_facts"]["observed_markers"] == [
        "continuation_cache_root_hash72"
    ]
    assert decisions["predictive_continuation_cache"]["state"] is None
    assert "REJECT_INHERITED_AUTHORITY_DISPOSITION_MISSING" in decisions[
        "predictive_continuation_cache"
    ]["reasons"]


def test_generic_cache_words_do_not_fake_continuation_applicability() -> None:
    facts = continuation_context_facts(
        {
            "cache": "generic",
            "cache_key": "not-a-pass111-contract",
            "resume": False,
            "nested": {"continuation": "word-only"},
        }
    )

    assert facts["continuation_context_present"] is False
    assert facts["observed_markers"] == []
    assert facts["marker_count"] == 0
