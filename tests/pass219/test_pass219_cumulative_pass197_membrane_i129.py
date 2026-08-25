from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i129_pass197 import (
    PASS197_CENSUS_CLASSIFICATION,
    REQUIRED_OPERATIONS,
    execute_pass197_membrane_preflight,
    invoke,
    pass197_membrane_manifest,
)


def main() -> None:
    manifest = pass197_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert PASS197_CENSUS_CLASSIFICATION == "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
    assert manifest["accepted_merge"] == "2321a1f05a6da410034a31ca141e3919091bb09a"
    assert manifest["frozen_predecessor"] == "c85b2b29cdf26d21912eb06b7d50323526944cc2"
    assert manifest["review_finding_ids"] == [
        3699915198, 3699915199, 3699915201, 3699915203, 3699915204,
        3699915205, 3699915207, 3699915209, 3699915210, 3699915212,
    ]
    assert tuple(manifest["declared_operations"]) == REQUIRED_OPERATIONS

    preflight = execute_pass197_membrane_preflight()
    assert preflight["ok"] is True

    identity = invoke("validate_pass197_squash_identity")
    assert identity["ok"] is True
    assert identity["pull_request"] == 133
    assert identity["squash_aware"] is True

    repair = invoke("validate_pass197_ten_finding_repair")
    assert repair["ok"] is True
    assert repair["finding_count"] == 10
    assert repair["repair_schema"] == "HHS_PASS_197_I129_REPAIR_V1"

    exact = invoke("validate_pass197_exact_execution_boundary")
    assert exact["pre_persistence_kernel_audit_required"] is True
    assert exact["fail_closed_hash72_authority"] is True
    assert exact["full_replay_required_for_closure"] is True
    assert exact["strict_rational_object_components"] is True
    assert exact["state_root_run_serialization"] is True
    assert exact["persisted_report_integrity_status_gate"] is True
    assert exact["maximum_synchronous_parameter_states"] == 405
    assert exact["strict_exponent_ingress"] is True
    assert exact["duplicate_coordinate_rejection"] is True
    assert exact["closed_only_frontend_projection"] is True

    successor = invoke("validate_pass197_successor_binding")
    assert successor["successor_pass"] == 198
    assert successor["successor_preserved"] is True
    assert successor["successor_accepted_merge"] == "122d21565fd7f3f9bbe9fb73ad2182d1d468ba5e"

    authority = invoke("validate_pass197_no_new_authority")
    assert authority["i129_new_candidate_authority"] is False
    assert authority["i129_new_canonical_mutation_authority"] is False
    assert authority["i129_new_persistence_authority"] is False
    assert authority["i129_new_hash72_clock"] is False
    assert authority["cxx_mutation_authority"] is False
    assert authority["vm81_mutation_authority"] is False
    assert authority["singleton_vm81_authority_remains_inherited"] is True


if __name__ == "__main__":
    main()
