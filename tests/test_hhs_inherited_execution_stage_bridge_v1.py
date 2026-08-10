from __future__ import annotations

from dataclasses import asdict

from hhs_runtime.hhs_inherited_execution_stage_bridge_v1 import (
    build_initial_inherited_authority_reachability,
    continuation_context_facts,
)
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import (
    ContinuationLease,
    Hash72ReceiptChainWorkload,
    PredictiveContinuationEngine,
    ResourceContract,
    _hash,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import build_bound_route_surface
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache


def _decisions(record):
    return {row["authority_id"]: row for row in record["decisions"]}


def _pass111_bundle():
    dependency = _hash("pass217_bridge_dependency", {"version": 1})
    capability = _hash("pass217_bridge_capability", {"status": "CANONICAL_EXECUTABLE"})
    workload = Hash72ReceiptChainWorkload(
        "pass217:test:continuation",
        dependency,
        capability,
    )
    contract = ResourceContract(6, 0)
    engine = PredictiveContinuationEngine(workload, 10, contract)
    genesis = workload.genesis("pass217-bridge")
    state, receipts, states = workload.execute_range(genesis, 1, 6)
    cache = engine.create_cache(
        genesis_state=genesis,
        suspension_state=state,
        states_by_step=states,
        receipts=receipts,
        prediction=engine.predict(6),
    )
    lease = ContinuationLease(
        workload.operation_id,
        dependency,
        capability,
        cache["tail_length"],
        4,
    )
    return {
        "continuation_cache": cache,
        "continuation_lease": asdict(lease),
        "continuation_lease_root_hash72": lease.root_hash72,
        "resource_contract": asdict(contract),
    }


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


def test_complete_pass111_contract_replays_tail_and_activates_predictive_cache(tmp_path) -> None:
    surface = build_bound_route_surface("api.runtime.services.dispatch")
    preflight = execute_surface_preflight(
        surface,
        operation=surface["symbol"],
        cache={},
    )
    bundle = _pass111_bundle()
    record = build_initial_inherited_authority_reachability(
        preflight,
        surface,
        {"service": "example", "payload": {"continuation": bundle}},
        semantic_cache=SemanticCompositionCache(tmp_path / "composition-cache.json"),
    )
    decision = _decisions(record)["predictive_continuation_cache"]
    witness = decision["proof"]["traversal_witness"]

    assert record["admitted"] is True
    assert decision["state"] == "ACTIVE_IN_PATH"
    assert witness["status"] == "ADMIT_PREDICTIVE_CONTINUATION_TRAVERSAL"
    assert witness["resume_status"] == "ADMITTED_FOR_CONTINUATION"
    assert witness["production_path"] == "Hash72ReceiptChainWorkload.execute_step"
    assert witness["replay_work_steps"] == bundle["continuation_cache"]["tail_length"]
    assert witness["useful_progress_steps_added"] == 0
    assert all(witness["continuity_vector"].values())
    assert witness["cached_suspension_state_root_hash72"] == witness[
        "replayed_suspension_state_root_hash72"
    ]
    assert decision["proof"]["witness_root"] == witness["resume_admission_root_hash72"]
    assert record["continuation_applicability_facts"]["complete_contract_bundle_count"] == 1


def test_partial_continuation_context_is_applicable_but_fails_closed(tmp_path) -> None:
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
    decision = _decisions(record)["predictive_continuation_cache"]

    assert record["admitted"] is False
    assert record["continuation_applicability_facts"]["continuation_context_present"] is True
    assert record["continuation_applicability_facts"]["complete_contract_bundle_count"] == 0
    assert decision["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in decision["reasons"]
    assert decision["proof"]["traversal_witness"]["reason"] == (
        "REJECT_PASS111_CONTINUATION_CONTRACT_BUNDLE_COUNT"
    )


def test_corrupted_pass111_cache_fails_closed(tmp_path) -> None:
    surface = build_bound_route_surface("api.runtime.services.dispatch")
    preflight = execute_surface_preflight(
        surface,
        operation=surface["symbol"],
        cache={},
    )
    bundle = _pass111_bundle()
    bundle["continuation_cache"]["validated_current_state"]["accumulator"] += 1
    record = build_initial_inherited_authority_reachability(
        preflight,
        surface,
        {"service": "example", "payload": {"continuation": bundle}},
        semantic_cache=SemanticCompositionCache(tmp_path / "composition-cache.json"),
    )
    decision = _decisions(record)["predictive_continuation_cache"]

    assert record["admitted"] is False
    assert decision["state"] is None
    assert decision["proof"]["traversal_witness"]["reason"] == (
        "REJECT_CORRUPTED_CONTINUATION_CACHE"
    )


def test_stale_pass111_resource_contract_root_fails_closed(tmp_path) -> None:
    surface = build_bound_route_surface("api.runtime.services.dispatch")
    preflight = execute_surface_preflight(
        surface,
        operation=surface["symbol"],
        cache={},
    )
    bundle = _pass111_bundle()
    bundle["resource_contract"]["maximum_useful_steps_per_cycle"] += 1
    record = build_initial_inherited_authority_reachability(
        preflight,
        surface,
        {"service": "example", "payload": {"continuation": bundle}},
        semantic_cache=SemanticCompositionCache(tmp_path / "composition-cache.json"),
    )
    decision = _decisions(record)["predictive_continuation_cache"]

    assert record["admitted"] is False
    assert decision["state"] is None
    assert decision["proof"]["traversal_witness"]["reason"] == (
        "REJECT_PASS111_RESOURCE_CONTRACT_ROOT_MISMATCH"
    )


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
    assert facts["complete_contract_bundle_count"] == 0
