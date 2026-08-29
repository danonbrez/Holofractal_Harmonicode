from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i139_pass187 import (
    PASS187_CENSUS_CLASSIFICATION,
    execute_pass187_membrane_preflight,
    pass187_membrane_manifest,
    pass187_membrane_source_evidence,
    validate_pass187_bott_lineage_boundary,
    validate_pass187_composition_authority_boundary,
    validate_pass187_composition_completion_boundary,
    validate_pass187_historical_lineage,
    validate_pass187_incremental_recomposition_boundary,
    validate_pass187_interaction_and_adapter_boundary,
    validate_pass187_no_new_authority,
    validate_pass187_successor_binding,
)


def main() -> None:
    evidence = pass187_membrane_source_evidence()
    assert evidence["composition_completion_head"] == "c36beacd8d6748f65c30ca3b02ac237eac38c34d"
    assert evidence["focused_run"] == 33186767175
    assert evidence["focused_job"] == 98901660703
    assert evidence["pass188_successor"]["successor_preserved"] is True

    manifest = pass187_membrane_manifest()
    assert manifest["pass_number"] == 187
    assert manifest["classification"] == "WIRED"
    assert "COMPOSITION_CONTRACT_IMPLEMENTATION_GAP_CLOSED_BY_I139" in PASS187_CENSUS_CLASSIFICATION

    lineage = validate_pass187_historical_lineage()
    assert lineage["historical_bott_baseline_preserved"] is True
    assert lineage["historical_bott_runtime_gap_record_preserved"] is True
    assert lineage["composition_gap_closed_by_i139"] is True

    completion = validate_pass187_composition_completion_boundary()
    assert completion["classification"] == "HHS_PASS_187_UNIVERSAL_COMPOSITION_AND_INCREMENTAL_RECOMPOSITION_VERIFIED"
    assert completion["acceptance_scenarios"] == 12
    assert completion["harmonicode_roundtrip"] is True
    assert completion["dependency_aware_incremental_recomposition"] is True
    assert completion["cold_restart_recovery"] is True

    authority = validate_pass187_composition_authority_boundary()
    assert authority["explicit_inherited_vm81_hash72_witness_required"] is True
    assert authority["local_graph_event_evidence_is_mutation_authority"] is False
    assert authority["independent_vm81_authority"] is False
    assert authority["independent_hash72_clock"] is False
    assert authority["browser_authority"] is False
    assert authority["cache_authority"] is False
    assert authority["compiled_artifact_authority"] is False
    assert authority["float_canonical_authority"] is False

    incremental = validate_pass187_incremental_recomposition_boundary()
    assert incremental["ten_node_chain_verified"] is True
    assert incremental["unaffected_nodes_not_reexecuted"] is True
    assert incremental["causal_runtime_value_dependency_fingerprint"] is True
    assert incremental["bounded_feedback"] is True
    assert incremental["planner_benchmark_nodes"] == 100
    assert incremental["planner_timing_authority"] is False

    interaction = validate_pass187_interaction_and_adapter_boundary()
    assert interaction["visual_mouse_drag_drop"] is True
    assert interaction["visual_keyboard"] is True
    assert interaction["visual_touch"] is True
    assert interaction["visual_pen_pointer"] is True
    assert interaction["visual_accessibility_navigation"] is True
    assert interaction["visual_cancellation"] is True
    assert interaction["projection_is_authority"] is False

    bott = validate_pass187_bott_lineage_boundary()
    assert bott["historical_runtime_complete_at_freeze"] is False
    assert bott["hydrated_addresses"] == 1_259_712
    assert bott["pass188_runtime_closure_preserved"] is True
    assert bott["bott_candidate_only"] is True
    assert bott["bott_canonical_mutation_authority"] is False

    successor = validate_pass187_successor_binding()
    assert successor["successor_pass"] == 188
    assert successor["successor_frozen_commit"] == "6f59481b48903759395dfbe94a4dc61097b306b1"
    assert successor["successor_preserved"] is True

    no_new = validate_pass187_no_new_authority()
    assert no_new["singleton_vm81_authority_remains_inherited"] is True
    for key, value in no_new.items():
        if key in {"ok", "singleton_vm81_authority_remains_inherited"}:
            continue
        assert value is False

    preflight = execute_pass187_membrane_preflight()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(manifest["declared_operations"])


if __name__ == "__main__":
    main()
