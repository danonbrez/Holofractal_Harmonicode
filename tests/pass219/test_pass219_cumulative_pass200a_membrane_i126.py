from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i126_pass200a import (
    PASS200A_CENSUS_CLASSIFICATION,
    REQUIRED_OPERATIONS,
    execute_pass200a_membrane_preflight,
    invoke,
    pass200a_membrane_manifest,
)


def main() -> None:
    manifest = pass200a_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert PASS200A_CENSUS_CLASSIFICATION == "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
    assert manifest["review_finding_ids"] == [
        3700651637, 3700651638, 3700651639, 3700651640,
        3700651641, 3700651642, 3700651643, 3700651644,
    ]
    assert tuple(manifest["declared_operations"]) == REQUIRED_OPERATIONS

    preflight = execute_pass200a_membrane_preflight()
    assert preflight["ok"] is True

    squash = invoke("validate_pass200a_squash_identity")
    assert squash["ok"] is True
    assert squash["pull_request"] == 138
    assert squash["squash_aware"] is True
    assert squash["historical_v1_runtime_preserved"] is True

    repair = invoke("validate_pass200a_review_repair")
    assert repair["ok"] is True
    assert repair["finding_count"] == 8
    assert repair["historical_v1_is_provenance_not_canonical_production"] is True

    receipt = invoke("validate_pass200a_vm81_receipt_provenance")
    assert receipt["shape_only_hash72_acceptance"] is False
    assert receipt["verified_unified_hash72_chain_required"] is True
    assert receipt["pass219_new_hash72_clock"] is False

    shadows = invoke("validate_pass200a_independent_shadow_execution")
    assert shadows["both_lanes_independently_executed"] is True
    assert shadows["hardcoded_match_forbidden"] is True
    assert shadows["returned_path"] == "REFERENCE"
    assert shadows["candidate_execution_is_authority"] is False

    integrity = invoke("validate_pass200a_shadow_and_proof_integrity")
    assert integrity["shadow_hash72_recomputed"] is True
    assert integrity["shadow_event_payload_hash72_binding_required_for_qualification"] is True
    assert integrity["revoked_or_stale_source_rejected"] is True

    acceptance = invoke("validate_pass200a_production_acceptance")
    assert acceptance["parameter_states"] == 290
    assert acceptance["durable_branch_jobs"] == 580
    assert acceptance["admitted_states"] == 263
    assert acceptance["domain_rejections"] == 27
    assert acceptance["vm5184_address_comparisons"] == 1_363_392
    assert acceptance["custom_four_holdout_profile_can_claim_production_closed"] is False

    restart = invoke("validate_pass200a_singleton_and_restartability")
    assert restart["v1_singleton_upgraded_in_place"] is True
    assert restart["second_default_state_authority_constructed"] is False
    assert restart["canonical_bundle_order"] == "simplification_id"
    assert restart["partial_state_exception"] is False

    successor = invoke("validate_pass200b_successor_binding")
    assert successor["successor_variant"] == "B"
    assert successor["successor_preserved"] is True

    authority = invoke("validate_pass200a_no_new_authority")
    assert authority["candidate_may_commit"] is False
    assert authority["candidate_may_activate"] is False
    assert authority["i126_new_candidate_authority"] is False
    assert authority["i126_new_canonical_mutation_authority"] is False
    assert authority["i126_new_persistence_authority"] is False
    assert authority["i126_new_hash72_clock"] is False
    assert authority["cxx_mutation_authority"] is False
    assert authority["vm81_mutation_authority"] is False


if __name__ == "__main__":
    main()
