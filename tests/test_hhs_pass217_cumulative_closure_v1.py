from __future__ import annotations

from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
from hhs_runtime.hhs_pass217_cumulative_closure_v1 import (
    build_cumulative_utilization_reachability_closure,
    build_global_surface_publication_evidence,
    build_required_authority_bypass_negative_matrix,
    build_required_authority_profile_coverage,
)
from hhs_runtime.hhs_pass217_checkpoint13_interruption_recovery_v1 import (
    CHECKPOINT13_REQUIRED_AUTHORITIES,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import build_bound_route_surface
from hhs_runtime.hhs_pass217_surface_bindings_v1 import (
    SERVICE_ROUTE_BINDINGS,
    service_route_surface_declaration,
)


def _surface_index():
    surface_map = build_surface_map()
    return surface_map, {
        surface["surface_id"]: surface for surface in surface_map["surfaces"]
    }


def test_pass217_service_routes_are_published_in_global_pass042_surface_map() -> None:
    surface_map, surfaces = _surface_index()
    assert surface_map["validation"]["ok"] is True
    assert len([s for s in surface_map["surfaces"] if s["surface_type"] == "API_ROUTE"]) == 24
    for source, binding in SERVICE_ROUTE_BINDINGS.items():
        declaration = service_route_surface_declaration(source)
        surface_id = declaration["surface_id"]
        assert surface_id in surfaces
        published = surfaces[surface_id]
        assert published["symbol"] == binding["symbol"]
        assert published["mutation_policy"] == binding["mutation_policy"]
        assert published["persistence_policy"] == binding["persistence_policy"]
        assert published["derivation_complete"] is True
        assert "HHS_PASS217_CUMULATIVE_EXECUTION_ROUTE_CONTRACT_V1" in published["contract_schemas"]
        assert "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1" in published["witness_schemas"]
        assert "HHS_CUMULATIVE_EXECUTION_AUTHORITY_REACHABILITY_V1" in published["witness_schemas"]
        assert "validate_pass217_cumulative_route_composition" in published["validators"]
        assert "validate_authority_reachability" in published["validators"]
        assert "kernel_runtime_autocomposer" in published["guards"]
        assert "cumulative_execution_authority_reachability" in published["guards"]
        assert "REJECT_INHERITED_EXECUTION_AUTHORITY_REACHABILITY" in published["rejection_codes"]


def test_runtime_composer_uses_same_canonical_surface_declarations() -> None:
    _, surfaces = _surface_index()
    for source in SERVICE_ROUTE_BINDINGS:
        runtime_surface = build_bound_route_surface(source)
        published = surfaces[runtime_surface["surface_id"]]
        for field in (
            "surface_id",
            "symbol",
            "invariant_ids",
            "contract_schemas",
            "witness_schemas",
            "validators",
            "guards",
            "rejection_codes",
            "mutation_policy",
            "persistence_policy",
            "boundedness_policy",
            "declared_operations",
            "derivation_complete",
        ):
            assert runtime_surface[field] == published[field]


def test_all_required_authority_omissions_fail_closed() -> None:
    matrix = build_required_authority_bypass_negative_matrix()
    assert matrix["required_authority_count"] == len(CHECKPOINT13_REQUIRED_AUTHORITIES) == 25
    assert matrix["baseline_all_active_gate_fixture_admitted"] is True
    assert matrix["synthetic_gate_fixtures_only"] is True
    assert matrix["synthetic_fixtures_count_as_runtime_traversal_evidence"] is False
    assert matrix["omission_case_count"] == 25
    assert matrix["all_applicable_required_authority_omissions_blocked"] is True
    seen = set()
    for row in matrix["cases"]:
        authority_id = row["omitted_authority_id"]
        seen.add(authority_id)
        assert row["admitted"] is False
        assert row["expected_blocker_present"] is True
        assert row["omitted_decision_state"] is None
        assert row["omitted_decision_accepted"] is False
        assert row["omitted_decision_reasons"] == [
            "REJECT_INHERITED_AUTHORITY_DISPOSITION_MISSING"
        ]
    assert seen == set(CHECKPOINT13_REQUIRED_AUTHORITIES)


def test_required_profile_inventory_exactly_matches_connected_checkpoint13_scope() -> None:
    profile = build_required_authority_profile_coverage()
    assert profile["profile_required_authority_count"] == 25
    assert profile["connected_required_authority_count"] == 25
    assert profile["authority_sets_equal"] is True
    assert profile["missing_connected_authority_ids"] == []
    assert profile["unexpected_connected_authority_ids"] == []
    assert profile["optional_profile_classes_promoted_to_core"] is False
    assert profile["experimental_profile_classes_promoted_to_core"] is False
    incremental = profile["incremental_tokenization"]
    assert incremental["incremental_delta_callable_proven"] is True
    assert incremental["module"] == "hhs_runtime.pass165.incremental_tokenization"
    assert incremental["symbol"] == "incremental_tokenize"
    assert incremental["parent_committed_receipt_required"] is True
    assert incremental["parent_token_stream_root_required"] is True
    assert incremental["declared_changed_spans_must_equal_derived_spans"] is True
    assert incremental["floating_point_authority"] is False
    assert profile["incremental_tokenization_applicable_active_path_proven"] is True
    assert profile["incremental_tokenization_full_reference_equivalence_required"] is True
    assert profile["incremental_tokenization_parent_commit_binding_required"] is True
    assert profile["incremental_tokenization_declared_span_verification_required"] is True


def test_surface_publication_evidence_is_complete() -> None:
    evidence = build_global_surface_publication_evidence()
    assert evidence["ok"] is True
    assert evidence["pass042_surface_map_validation_ok"] is True
    assert evidence["pass042_api_route_count"] == 24
    assert evidence["published_pass217_route_count"] == 3
    assert evidence["expected_pass217_route_count"] == 3
    assert all(row["ok"] for row in evidence["routes"])


def test_terminal_closure_artifact_is_admitted_after_incremental_authority_connection() -> None:
    closure = build_cumulative_utilization_reachability_closure()
    assert closure["required_authority_count"] == 25
    assert closure["structural_closure_hardening_complete"] is True
    assert closure["universal_applicable_utilization_reachability_complete"] is True
    assert closure["closure_ready"] is True
    assert closure["status"] == "ADMIT_PASS217_CUMULATIVE_UTILIZATION_REACHABILITY_CLOSURE"
    assert closure["blockers"] == []
    assert closure["current_known_applicable_active_gap_authority_ids"] == []
    assert closure["synthetic_bypass_fixtures_are_runtime_evidence"] is False
    assert closure["required_authority_profile_coverage"][
        "incremental_tokenization_applicable_active_path_proven"
    ] is True
    assert isinstance(closure["closure_root_hash72"], str)
    assert len(closure["closure_root_hash72"]) == 72
