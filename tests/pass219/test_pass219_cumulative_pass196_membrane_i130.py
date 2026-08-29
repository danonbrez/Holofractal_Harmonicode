from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i130_pass196 import (
    PASS196_CENSUS_CLASSIFICATION,
    REQUIRED_OPERATIONS,
    execute_pass196_membrane_preflight,
    invoke,
    pass196_membrane_manifest,
)


def main() -> None:
    manifest = pass196_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert PASS196_CENSUS_CLASSIFICATION == "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
    assert manifest["accepted_primary_merge"] == "37687d479f2a9f1d996d225a4ba3556d9db72a86"
    assert manifest["accepted_topology_merge"] == "959729c9070399fcdf0015702cd8777079e05dcc"
    assert manifest["frozen_predecessor"] == "40e6e07d5f4a401541a6255339223e853846e713"
    assert manifest["review_finding_ids"] == [
        3699626177, 3699626180, 3699626182, 3699626186, 3699626190,
        3699626194, 3699626196, 3699626198, 3699626201, 3699626204,
    ]
    assert tuple(manifest["declared_operations"]) == REQUIRED_OPERATIONS

    preflight = execute_pass196_membrane_preflight()
    assert preflight["ok"] is True

    identity = invoke("validate_pass196_historical_identity")
    assert identity["ok"] is True
    assert identity["primary_pull_request"] == 128
    assert identity["topology_pull_request"] == 130
    assert identity["historical_v1_preserved"] is True

    repair = invoke("validate_pass196_ten_finding_repair")
    assert repair["ok"] is True
    assert repair["finding_count"] == 10
    assert repair["repair_schema"] == "HHS_PASS_196_I130_REPAIR_V1"
    assert repair["service_state_directory_previously_repaired_and_preserved"] is True

    observation = invoke("validate_pass196_observation_and_manifest_boundary")
    assert observation["same_bytes_hash_and_classification"] is True
    assert observation["host_independent_manifest_identity"] is True
    assert observation["distinct_executable_evidence_required"] is True
    assert observation["failed_scan_quarantines_current_success"] is True

    persistence = invoke("validate_pass196_persistence_and_restart_boundary")
    assert persistence["vm81_hash72_receipt_required_for_persistence"] is True
    assert persistence["persisted_restart_lineage_restored"] is True
    assert persistence["vector_store_is_source_authority"] is False

    api = invoke("validate_pass196_api_and_projection_boundary")
    assert api["strict_boolean_tool_ingress"] is True
    assert api["scan_error_mapping_parity"] is True
    assert api["validated_projection_refresh"] is True
    assert api["browser_projection_is_authority"] is False

    successor = invoke("validate_pass196_successor_binding")
    assert successor["successor_pass"] == 197
    assert successor["successor_preserved"] is True
    assert successor["successor_accepted_merge"] == "2321a1f05a6da410034a31ca141e3919091bb09a"

    authority = invoke("validate_pass196_no_new_authority")
    assert authority["i130_new_candidate_authority"] is False
    assert authority["i130_new_canonical_mutation_authority"] is False
    assert authority["i130_new_persistence_authority"] is False
    assert authority["i130_new_hash72_clock"] is False
    assert authority["cxx_mutation_authority"] is False
    assert authority["vm81_mutation_authority"] is False
    assert authority["singleton_vm81_authority_remains_inherited"] is True


if __name__ == "__main__":
    main()
