#include "hhs_pass219_inherited_pass198_1_28.h"

#include <assert.h>
#include <string.h>

static HHSExactPass198RepairedCalibrationRegistryWitnessV1 witness(void) {
    HHSExactPass198RepairedCalibrationRegistryWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass198_version();
    w.primary_pull_request = 136U;
    w.default_parameter_states = 405U;
    w.default_admitted_states = 320U;
    w.default_rejected_states = 85U;
    w.vm5184_address_comparisons = 1658880U;
    w.simplification_count = 4U;
    w.negative_mutation_count = 6U;
    w.review_finding_count = 13U;
    w.full_replay_required = 1U;
    w.full_replay_executed = 1U;
    w.nonzero_admitted_coverage_required = 1U;
    w.exact_builtin_adapter_spec_binding_required = 1U;
    w.registration_vm81_receipt_persisted = 1U;
    w.recursive_float_identity_rejection = 1U;
    w.atomic_builtin_registration = 1U;
    w.normalized_persistent_identifier_updates = 1U;
    w.transactional_promotion_state_recheck = 1U;
    w.checkpoint_receipt_independent = 1U;
    w.distinct_workload_promotion_required = 1U;
    w.per_simplification_cost_unmeasured = 1U;
    w.executed_negative_mutations_required = 1U;
    w.executed_negative_mutation_count = 6U;
    w.all_negative_mutations_detected = 1U;
    w.pass199_successor_preserved = 1U;
    strcpy(w.historical_base_commit, "b40e11315840781d1fd9c12932fad46eb32e383f");
    strcpy(w.historical_reviewed_head, "a383ab8ec6a55e04ab490477c7b8cfe5d107d098");
    strcpy(w.accepted_merge_commit, "122d21565fd7f3f9bbe9fb73ad2182d1d468ba5e");
    strcpy(w.frozen_i127_commit, "fa89488d84f845fa372551b5324e0ddd37e49daf");
    strcpy(w.validated_repair_head, "97faba2ec59c54d1cd17be5bb88ade370841f65f");
    strcpy(w.accepted_contract_blob, "c623794f920ebbefbb6cb21eaf20767a1fd78306");
    strcpy(w.accepted_runtime_blob, "3ec97b653344cbaf28eee89e6debbe1b6a89975d");
    strcpy(w.accepted_api_blob, "0e2581a3ecb0044eaf328617be1ae85e69e1e9a7");
    strcpy(w.accepted_test_blob, "2f4285b15644e88fb46d74bf06fa5c8d266e8859");
    strcpy(w.accepted_workflow_blob, "d9eb8b172d81ed2d9e07916c13b914bab8ec6654");
    strcpy(w.repaired_runtime_blob, "9be70fd34fad007001a830fc225792a9a56a24e7");
    strcpy(w.repaired_api_blob, "2b2663cab7f74a2e1c21b77c2d5317296d925911");
    strcpy(w.repaired_regression_blob, "b05a76b0cb694a51b66b147583c95520f2e54a9b");
    strcpy(w.repaired_workflow_blob, "879f6b10ed08f5be590f28510ba12b225da44d0b");
    return w;
}

int main(void) {
    HHSExactPass198RepairedCalibrationRegistryWitnessV1 w = witness();
    HHSExactPass219InheritedPass198BindingV1 b;
    assert(hhs_exact_pass219_bind_pass198_repaired_calibration_registry(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.pass_number == 198U);
    assert(b.inherited_defects_repaired == 1U);
    assert(b.production_totals_bound == 1U);
    assert(b.deterministic_replay_bound == 1U);
    assert(b.executed_negative_mutation_bound == 1U);
    assert(b.pass199_successor_bound == 1U);
    assert(b.pass219_new_candidate_authority == 0U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.pass219_new_persistence_authority == 0U);
    assert(b.pass219_new_hash72_clock == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);

    w.executed_negative_mutation_count = 5U;
    assert(hhs_exact_pass219_bind_pass198_repaired_calibration_registry(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.full_replay_executed = 0U;
    assert(hhs_exact_pass219_bind_pass198_repaired_calibration_registry(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.pass219_new_canonical_mutation_authority = 1U;
    assert(hhs_exact_pass219_bind_pass198_repaired_calibration_registry(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
