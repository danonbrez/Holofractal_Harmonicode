from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i138_pass188 import (
    PASS188_CENSUS_CLASSIFICATION,
    execute_pass188_membrane_preflight,
    pass188_membrane_manifest,
    pass188_membrane_source_evidence,
    validate_pass188_bott_runtime_boundary,
    validate_pass188_exact_arithmetic_boundary,
    validate_pass188_historical_lineage,
    validate_pass188_license_authority_boundary,
    validate_pass188_license_completion_boundary,
    validate_pass188_license_legacy_evidence_boundary,
    validate_pass188_no_new_authority,
    validate_pass188_successor_binding,
)


def main() -> None:
    evidence = pass188_membrane_source_evidence()
    assert evidence["license_completion_head"] == "8e6f209aa8974da30d0b1dcb85a7ca2dc10060c6"
    assert evidence["focused_license_run"] == 33177282910
    assert evidence["focused_license_job"] == 98869073632
    assert evidence["pass189_successor"]["successor_preserved"] is True

    manifest = pass188_membrane_manifest()
    assert manifest["pass_number"] == 188
    assert manifest["classification"] == "WIRED"
    assert "LICENSE_CONTRACT_IMPLEMENTATION_GAP_CLOSED_BY_I138" in PASS188_CENSUS_CLASSIFICATION

    lineage = validate_pass188_historical_lineage()
    assert lineage["historical_bott_preserved"] is True
    assert lineage["license_gap_closed_by_i138"] is True

    completion = validate_pass188_license_completion_boundary()
    assert completion["classification"] == "HHS_PASS_188_VERSIONED_CONTENT_LICENSE_AND_LEGACY_STATE_VERIFIED"
    assert completion["acceptance_scenarios"] == 16
    assert completion["immutable_content_versions"] is True
    assert completion["immutable_license_versions"] is True
    assert completion["exact_royalties"] is True
    assert completion["pass187_graph_impact"] is True
    assert completion["cold_restart_recovery"] is True

    authority = validate_pass188_license_authority_boundary()
    assert authority["explicit_inherited_vm81_hash72_witness_required"] is True
    assert authority["deterministic_replay"] is True
    assert authority["materialized_state_integrity"] is True
    assert authority["external_chain_required"] is False
    assert authority["wallet_authority"] is False
    assert authority["browser_local_authority"] is False
    assert authority["marketplace_authority"] is False
    assert authority["independent_vm81_authority"] is False
    assert authority["independent_hash72_clock"] is False

    legacy = validate_pass188_license_legacy_evidence_boundary()
    assert len(legacy["legacy_policies"]) == 7
    assert legacy["prior_receipts_immutable"] is True
    assert legacy["explicit_upgrade_required"] is True
    assert legacy["tampered_materialization_detected"] is True
    assert legacy["forged_binding_detected"] is True

    bott = validate_pass188_bott_runtime_boundary()
    assert bott["projected_addresses"] == 1_259_712
    assert bott["deterministic_replay_addresses"] == 1_259_712
    assert bott["projected_transition_is_candidate_only"] is True
    assert bott["canonical_mutation_authority"] is False

    exact = validate_pass188_exact_arithmetic_boundary()
    assert exact["license_float_canonical_authority"] is False
    assert exact["bott_float_canonical_authority"] is False
    assert exact["aggregate_float_canonical_authority"] is False

    successor = validate_pass188_successor_binding()
    assert successor["successor_pass"] == 189
    assert successor["successor_frozen_commit"] == "ef27a1caf0d977e0f767b13126dba8fe49b09dab"
    assert successor["successor_preserved"] is True

    no_new = validate_pass188_no_new_authority()
    assert no_new["singleton_vm81_authority_remains_inherited"] is True
    for key, value in no_new.items():
        if key in {"ok", "singleton_vm81_authority_remains_inherited"}:
            continue
        assert value is False

    preflight = execute_pass188_membrane_preflight()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == len(manifest["declared_operations"])


if __name__ == "__main__":
    main()
