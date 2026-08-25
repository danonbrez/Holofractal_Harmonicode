#include "hhs_pass219_inherited_pass198_1_28.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass198RepairedCalibrationRegistryWitnessV1 make_witness() {
    HHSExactPass198RepairedCalibrationRegistryWitnessV1 w{};
    w.struct_size = static_cast<uint32_t>(sizeof(w));
    w.version = hhs::rna::InheritedPass198RepairedCalibrationRegistry::version();
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
    std::strcpy(w.historical_base_commit, "b40e11315840781d1fd9c12932fad46eb32e383f");
    std::strcpy(w.historical_reviewed_head, "a383ab8ec6a55e04ab490477c7b8cfe5d107d098");
    std::strcpy(w.accepted_merge_commit, "122d21565fd7f3f9bbe9fb73ad2182d1d468ba5e");
    std::strcpy(w.frozen_i127_commit, "fa89488d84f845fa372551b5324e0ddd37e49daf");
    std::strcpy(w.validated_repair_head, "97faba2ec59c54d1cd17be5bb88ade370841f65f");
    std::strcpy(w.accepted_contract_blob, "c623794f920ebbefbb6cb21eaf20767a1fd78306");
    std::strcpy(w.accepted_runtime_blob, "3ec97b653344cbaf28eee89e6debbe1b6a89975d");
    std::strcpy(w.accepted_api_blob, "0e2581a3ecb0044eaf328617be1ae85e69e1e9a7");
    std::strcpy(w.accepted_test_blob, "2f4285b15644e88fb46d74bf06fa5c8d266e8859");
    std::strcpy(w.accepted_workflow_blob, "d9eb8b172d81ed2d9e07916c13b914bab8ec6654");
    std::strcpy(w.repaired_runtime_blob, "9be70fd34fad007001a830fc225792a9a56a24e7");
    std::strcpy(w.repaired_api_blob, "2b2663cab7f74a2e1c21b77c2d5317296d925911");
    std::strcpy(w.repaired_regression_blob, "b05a76b0cb694a51b66b147583c95520f2e54a9b");
    std::strcpy(w.repaired_workflow_blob, "879f6b10ed08f5be590f28510ba12b225da44d0b");
    return w;
}

int main() {
    using Surface = hhs::rna::InheritedPass198RepairedCalibrationRegistry;
    static_assert(!Surface::mutation_authority());
    static_assert(!Surface::persistence_authority());
    static_assert(!Surface::hash72_clock_authority());
    static_assert(!Surface::vm81_mutation_authority());
    static_assert(!Surface::candidate_authority());
    static_assert(!Surface::api_mutation_authority());
    static_assert(Surface::singleton_vm81_authority_remains_inherited());
    static_assert(Surface::full_replay_required_for_verified_proofs());
    static_assert(Surface::executed_negative_mutations_required_for_verified_proofs());
    static_assert(Surface::executed_negative_mutation_count() == 6U);

    auto w = make_witness();
    HHSExactPass219InheritedPass198BindingV1 b{};
    assert(Surface::bind(w, b) == HHS_EXACT_STATUS_OK);
    assert(b.inherited_defects_repaired == 1U);
    assert(b.executed_negative_mutation_bound == 1U);
    assert(b.pass199_successor_bound == 1U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);
    return 0;
}
