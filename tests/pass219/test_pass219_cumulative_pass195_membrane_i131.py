from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i131_pass195 import (
    PASS195_CENSUS_CLASSIFICATION,
    REQUIRED_OPERATIONS,
    execute_pass195_membrane_preflight,
    invoke,
    pass195_membrane_manifest,
)


def main() -> None:
    manifest = pass195_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert PASS195_CENSUS_CLASSIFICATION == "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
    assert manifest["accepted_primary_merge"] == "8bcc0921555ecface13113c8a2620415ddb3fdf1"
    assert manifest["frozen_predecessor"] == "69743440249dd7a05aa2b4096482d248973f239e"
    assert manifest["review_finding_ids"] == [
        3696077892, 3696077894, 3696077896, 3696077898,
        3696077899, 3696077901, 3696077903, 3696077905,
        3696077907, 3696077910, 3696077912, 3696077914,
    ]
    assert tuple(manifest["declared_operations"]) == REQUIRED_OPERATIONS

    preflight = execute_pass195_membrane_preflight()
    assert preflight["ok"] is True

    identity = invoke("validate_pass195_historical_identity")
    assert identity["ok"] is True
    assert identity["primary_pull_request"] == 117
    assert identity["historical_v1_preserved"] is True
    assert identity["finding_count"] == 12

    provider = invoke("validate_pass195_provider_plan_and_input_binding")
    assert provider["provider_plan_schema_validated_before_admission"] is True
    assert provider["constraints_content_bound_to_proposal"] is True
    assert provider["reference_image_content_bound_to_proposal"] is True
    assert provider["model_identity_bound_before_plan_hash"] is True

    frontend = invoke("validate_pass195_frontend_and_storybook_boundary")
    assert frontend["frontend_requires_admitted_provider_result"] is True
    assert frontend["template_applied_before_custom_overrides"] is True
    assert frontend["browser_handoff_is_canonical_authority"] is False

    paid = invoke("validate_pass195_paid_route_boundary")
    assert paid["operator_authorization_required"] is True
    assert paid["bounded_concurrency"] is True
    assert paid["bounded_rate"] is True
    assert paid["provider_secret_exposed_to_client"] is False

    multimodal = invoke("validate_pass195_multimodal_capability_boundary")
    assert multimodal["image_analysis_capability_required_when_images_present"] is True
    assert multimodal["image_analysis_receipt_bound_to_text_invocation"] is True
    assert multimodal["provider_output_is_proposal_only"] is True

    tick = invoke("validate_pass195_tick_and_health_boundary")
    assert tick["authorized_tick_ingested_before_provider_await"] is True
    assert tick["post_provider_global_runtime_export_forbidden"] is True
    assert tick["health_hash_seals_final_returned_object"] is True

    successor = invoke("validate_pass195_successor_binding")
    assert successor["successor_pass"] == 196
    assert successor["successor_preserved"] is True
    assert successor["successor_accepted_merge"] == "37687d479f2a9f1d996d225a4ba3556d9db72a86"

    authority = invoke("validate_pass195_no_new_authority")
    assert authority["external_provider_is_canonical_authority"] is False
    assert authority["browser_handoff_is_canonical_authority"] is False
    assert authority["i131_new_candidate_authority"] is False
    assert authority["i131_new_canonical_mutation_authority"] is False
    assert authority["i131_new_persistence_authority"] is False
    assert authority["i131_new_hash72_clock"] is False
    assert authority["cxx_mutation_authority"] is False
    assert authority["vm81_mutation_authority"] is False
    assert authority["singleton_vm81_authority_remains_inherited"] is True


if __name__ == "__main__":
    main()
