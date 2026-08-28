from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i136_pass190 import (
    PASS190_CLASSIFICATION,
    PASS190_CENSUS_CLASSIFICATION,
    execute_pass190_membrane_preflight,
    pass190_membrane_manifest,
    pass190_membrane_source_evidence,
    validate_pass190_authority_boundary,
    validate_pass190_completion_coordinator_boundary,
    validate_pass190_historical_authorization_lineage,
    validate_pass190_interface_parity_boundary,
    validate_pass190_no_new_authority,
    validate_pass190_operation_registry_boundary,
    validate_pass190_repository_hydration_boundary,
    validate_pass190_successor_binding,
)


def main() -> None:
    evidence = pass190_membrane_source_evidence()
    assert evidence["frozen_i135"] == "5e593b384732ffb065480cdd2d1098f1f32a990e"
    assert evidence["validated_core_head"] == "fbbc3ff37b6dea6c31e73612731e4e323a54475f"
    assert evidence["validated_core_run"] == 33160480090
    assert evidence["pass191_successor"]["successor_preserved"] is True

    manifest = pass190_membrane_manifest()
    assert manifest["pass_number"] == 190
    assert manifest["classification"] == PASS190_CLASSIFICATION == "WIRED"
    assert "COMPLETION_GAP_CLOSED_BY_I136" in PASS190_CENSUS_CLASSIFICATION

    lineage = validate_pass190_historical_authorization_lineage()
    assert lineage["historical_iteration7_preserved"] is True
    assert lineage["full_contract_gap_closed_by_i136"] is True

    completion = validate_pass190_completion_coordinator_boundary()
    assert completion["classification"] == "HHS_PASS_190_I136_COMPLETION_COORDINATOR_VERIFIED"
    assert completion["single_composed_authority_context"] is True
    assert completion["parallel_operation_engine"] is False
    assert completion["parallel_persistence_path"] is False

    registry = validate_pass190_operation_registry_boundary()
    assert registry["governed_operation_count"] == 52
    assert registry["historical_iteration7_operation_count"] == 42
    assert registry["project_acceptance_operation_count"] == 10
    assert registry["python_version"] == "3.12"
    assert registry["unclassified_public_callables"] == 0

    parity = validate_pass190_interface_parity_boundary()
    assert parity["constructor"] is True
    assert parity["python_adapter"] is True
    assert parity["shell"] is True
    assert parity["direct_operation"] is True
    assert parity["canonical_public_gateway"] is True
    assert parity["surface_specific_private_semantics"] is False

    hydration = validate_pass190_repository_hydration_boundary()
    assert hydration["passes_linked"] == 191
    assert hydration["blocker_count"] == 0
    assert hydration["symmetry_valid"] is True
    assert hydration["new_hydration_authority"] is False

    authority = validate_pass190_authority_boundary()
    assert authority["singleton_vm81_authority"] == "INHERITED_PASS190_DURABLE_AUTHORITY"
    assert authority["mutation_capability_gated"] is True
    assert authority["hash72_receipt_chain"] is True
    assert authority["deterministic_replay"] is True
    assert authority["float_canonical_authority"] is False

    successor = validate_pass190_successor_binding()
    assert successor["successor_pass"] == 191
    assert successor["successor_preserved"] is True

    no_new = validate_pass190_no_new_authority()
    assert no_new["singleton_vm81_authority_remains_inherited"] is True
    for key, value in no_new.items():
        if key in {"ok", "singleton_vm81_authority_remains_inherited"}:
            continue
        assert value is False

    preflight = execute_pass190_membrane_preflight()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(manifest["declared_operations"])


if __name__ == "__main__":
    main()
