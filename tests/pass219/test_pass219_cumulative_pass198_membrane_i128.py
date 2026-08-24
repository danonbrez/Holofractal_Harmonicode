from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i128_pass198 import (
    PASS198_CENSUS_CLASSIFICATION,
    REQUIRED_OPERATIONS,
    execute_pass198_membrane_preflight,
    invoke,
    pass198_membrane_manifest,
)


def main() -> None:
    manifest = pass198_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert PASS198_CENSUS_CLASSIFICATION == "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
    assert manifest["accepted_merge"] == "122d21565fd7f3f9bbe9fb73ad2182d1d468ba5e"
    assert manifest["frozen_predecessor"] == "fa89488d84f845fa372551b5324e0ddd37e49daf"
    assert manifest["validated_repair_head"] == "97faba2ec59c54d1cd17be5bb88ade370841f65f"
    assert manifest["review_finding_ids"] == [
        3700385770, 3700385771, 3700385772, 3700385773,
        3700385776, 3700385777, 3700385778, 3700385779,
        3700385780, 3700385781, 3700385783, 3700385785,
        3700385787,
    ]
    assert tuple(manifest["declared_operations"]) == REQUIRED_OPERATIONS
    assert manifest["validated_runs"] == {
        "pass198_i128": 32770921677,
        "pass198_production": 32770921723,
        "pass199_production": 32770921637,
        "pass200a_production": 32770921758,
        "pass200b_production": 32770921660,
        "frozen_i127": 32770921681,
        "vm81_exact_abi": 32770921615,
        "uqcel": 32770921651,
    }

    preflight = execute_pass198_membrane_preflight()
    assert preflight["ok"] is True

    identity = invoke("validate_pass198_squash_identity")
    assert identity["ok"] is True
    assert identity["pull_request"] == 136
    assert identity["squash_aware"] is True
    assert identity["accepted_provenance_preserved"] is True

    repair = invoke("validate_pass198_review_repair")
    assert repair["ok"] is True
    assert repair["finding_count"] == 13
    assert repair["repair_schema"] == "HHS_PASS_198_I128_REPAIR_V1"

    exact = invoke("validate_pass198_exact_execution_boundary")
    assert exact["full_replay_required"] is True
    assert exact["nonzero_admitted_coverage_required"] is True
    assert exact["exact_builtin_adapter_spec_binding_required"] is True
    assert exact["registration_vm81_receipt_persisted"] is True
    assert exact["recursive_float_identity_rejection"] is True
    assert exact["checkpoint_receipt_independent"] is True
    assert exact["distinct_workload_promotion_required"] is True
    assert exact["per_simplification_cost_claim"] == "NO_PER_SIMPLIFICATION_COST_MEASURED"

    mutations = invoke("validate_pass198_negative_mutation_execution")
    assert mutations["schema"] == "HHS_PASS_198_EXECUTED_NEGATIVE_MUTATION_EVIDENCE_V1"
    assert mutations["required_mutation_count"] == 6
    assert mutations["executed_mutation_count"] == 6
    assert mutations["all_required_negative_mutations_executed_and_detected"] is True
    assert mutations["required_before_envelope_verified"] is True

    acceptance = invoke("validate_pass198_production_acceptance")
    assert acceptance["parameter_states"] == 405
    assert acceptance["admitted_states"] == 320
    assert acceptance["domain_rejections"] == 85
    assert acceptance["vm5184_address_comparisons"] == 1_658_880
    assert acceptance["simplification_count"] == 4
    assert acceptance["negative_mutation_count"] == 6

    successor = invoke("validate_pass199_successor_binding")
    assert successor["successor_pass"] == 199
    assert successor["successor_preserved"] is True
    assert successor["successor_accepted_merge"] == "426fe7786abff2e1e4688222a600f5ab39d14a5a"

    authority = invoke("validate_pass198_no_new_authority")
    assert authority["api_mutation_authority"] is False
    assert authority["i128_new_candidate_authority"] is False
    assert authority["i128_new_canonical_mutation_authority"] is False
    assert authority["i128_new_persistence_authority"] is False
    assert authority["i128_new_hash72_clock"] is False
    assert authority["cxx_mutation_authority"] is False
    assert authority["vm81_mutation_authority"] is False
    assert authority["compiler_auto_promotion"] is False
    assert authority["runtime_auto_admission"] is False
    assert authority["singleton_vm81_authority_remains_inherited"] is True


if __name__ == "__main__":
    main()
