#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static HHSExactPass219HHCQEconomyCandidateV1 make_candidate(uint32_t route_id) {
    HHSExactPass219HHCQEconomyCandidateV1 c;
    memset(&c, 0, sizeof(c));
    c.struct_size = (uint32_t)sizeof(c);
    c.version = HHS_EXACT_PASS219_HHCQ_RECIPROCAL_ECONOMY_VERSION;
    c.route_id = route_id;
    c.reciprocal_n = 4U;
    c.intrinsic_resolution_index = 34U;
    c.effective_resolution_index = 34U;
    c.required_resolution_index = 34U;
    c.latency_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.memory_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.compression_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.translation_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.exact_semantic_closure = 1U;
    c.exact_reconstruction = 1U;
    c.all_native_modalities_translatable = 1U;
    c.one_step_translation = 1U;
    c.phase5_resolution_locked = 1U;
    c.candidate_only = 1U;
    return c;
}

int main(void) {
    HHSExactPass219HHCQReciprocalEconomyDescriptorV1 descriptor;
    HHSExactPass219HHCQEconomyCandidateV1 baseline;
    HHSExactPass219HHCQEconomyCandidateV1 recovered;
    HHSExactPass219HHCQEconomyCandidateV1 overspent;
    HHSExactPass219HHCQEconomyCandidateV1 mismatch;
    HHSExactPass219HHCQEconomyCandidateV1 outside;
    HHSExactPass219HHCQEconomyCandidateV1 no_translation;
    HHSExactPass219HHCQEconomyCandidateV1 authority;
    HHSExactPass219HHCQEconomyCandidateV1 coarse;
    HHSExactPass219HHCQEconomyCandidateV1 candidates[3];
    HHSExactPass219HHCQEconomyCandidateV1 invalid_n;
    HHSExactPass219HHCQEconomyResultV1 result;
    HHSExactPass219HHCQEconomySelectionV1 selection_a;
    HHSExactPass219HHCQEconomySelectionV1 selection_b;
    HHSExactPass219HHCQJointStateV1 state;

    assert(hhs_exact_pass219_hhcq_reciprocal_economy_version() ==
           HHS_EXACT_PASS219_HHCQ_RECIPROCAL_ECONOMY_VERSION);
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_descriptor(&descriptor) ==
           HHS_EXACT_STATUS_OK);
    assert(descriptor.parity_units == 5184U);
    assert(descriptor.inherited_policy_state_bytes == sizeof(HHSExactPass219HHCQJointStateV1));
    assert(descriptor.inherited_policy_state_bytes == 112U);
    assert(descriptor.reciprocal_1_over_n_to_n_boundary == 1U);
    assert(descriptor.n_must_be_phase5_divisor == 1U);
    assert(descriptor.separate_axis_ledgers == 1U);
    assert(descriptor.exact_one_to_one_information_closure == 1U);
    assert(descriptor.lower_resolution_recovery_allowed == 1U);
    assert(descriptor.spendable_savings_budget == 1U);
    assert(descriptor.one_step_translation_required == 1U);
    assert(descriptor.all_native_modalities_required == 1U);
    assert(descriptor.phase5_resolution_locked == 1U);
    assert(descriptor.fixed_size_policy_state == 1U);
    assert(descriptor.candidate_only == 1U);
    assert(descriptor.exact_integer_only == 1U);
    assert(descriptor.canonical_mutation_authority == 0U);
    assert(descriptor.canonical_hash72_authority == 0U);
    assert(descriptor.canonical_hash216_authority == 0U);
    assert(descriptor.canonical_persistence_authority == 0U);
    assert(descriptor.floating_point_authority == 0U);

    assert(hhs_exact_pass219_hhcq_joint_state_init(&state) == HHS_EXACT_STATUS_OK);
    assert(sizeof(state) == 112U);

    baseline = make_candidate(10U);
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(&baseline, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.decision == HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_ADMITTED);
    assert(result.reciprocal_lower_bound_units == 1296U);
    assert(result.reciprocal_upper_bound_units == 20736U);
    assert(result.total_savings_units == 0U);
    assert(result.total_axis_debt_units == 0U);
    assert(result.total_spend_units == 0U);
    assert(result.net_budget_units == 0);
    assert(result.information_one_to_one == 1U);
    assert(result.effective_resolution_met == 1U);
    assert(result.lower_resolution_recovered == 0U);
    assert(result.canonical_authority_changed == 0U);
    assert(result.floating_point_authority == 0U);

    recovered = make_candidate(20U);
    recovered.intrinsic_resolution_index = 30U; /* 6 parameters per intrinsic region. */
    recovered.effective_resolution_index = 34U; /* reconstructed to 1 parameter. */
    recovered.required_resolution_index = 34U;
    recovered.latency_units = 1296U;
    recovered.memory_units = 2592U;
    recovered.compression_units = 2592U;
    recovered.translation_units = 5184U;
    recovered.redundancy_spend_units = 1000U;
    recovered.ecc_spend_units = 1000U;
    recovered.precision_spend_units = 1000U;
    recovered.learning_spend_units = 1000U;
    recovered.lossy_information_units = 1000U;
    recovered.recovered_information_units = 1000U;
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(&recovered, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.decision == HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_ADMITTED);
    assert(result.intrinsic_resolution_parameters == 6U);
    assert(result.effective_resolution_parameters == 1U);
    assert(result.required_resolution_parameters == 1U);
    assert(result.latency_credit_units == 3888U);
    assert(result.memory_credit_units == 2592U);
    assert(result.compression_credit_units == 2592U);
    assert(result.translation_credit_units == 0U);
    assert(result.total_savings_units == 9072U);
    assert(result.total_spend_units == 4000U);
    assert(result.net_budget_units == 5072);
    assert(result.information_one_to_one == 1U);
    assert(result.lower_resolution_recovered == 1U);
    assert(result.budget_nonnegative == 1U);

    overspent = recovered;
    overspent.route_id = 21U;
    overspent.redundancy_spend_units = 5000U;
    overspent.ecc_spend_units = 5000U;
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(&overspent, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.net_budget_units == -928);
    assert(result.budget_nonnegative == 0U);
    assert(result.decision == HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_REJECTED);

    mismatch = recovered;
    mismatch.route_id = 22U;
    mismatch.recovered_information_units = 999U;
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(&mismatch, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.information_one_to_one == 0U);
    assert(result.decision == HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_REJECTED);

    outside = recovered;
    outside.route_id = 23U;
    outside.latency_units = 1295U;
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(&outside, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.reciprocal_bounds_met == 0U);
    assert(result.decision == HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_REJECTED);

    no_translation = recovered;
    no_translation.route_id = 24U;
    no_translation.one_step_translation = 0U;
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(&no_translation, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.decision == HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_REJECTED);

    authority = recovered;
    authority.route_id = 25U;
    authority.canonical_authority_requested = 1U;
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(&authority, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.decision == HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_REJECTED);

    invalid_n = recovered;
    invalid_n.reciprocal_n = 5U;
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(&invalid_n, &result) ==
           HHS_EXACT_STATUS_RANGE_ERROR);

    coarse = make_candidate(30U);
    coarse.intrinsic_resolution_index = 30U;
    coarse.effective_resolution_index = 30U;
    coarse.required_resolution_index = 30U;
    coarse.latency_units = 1296U;
    coarse.memory_units = 1296U;
    coarse.compression_units = 1296U;
    coarse.translation_units = 1296U;
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(&coarse, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.net_budget_units == 15552);
    assert(result.decision == HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_ADMITTED);

    candidates[0] = baseline;
    candidates[1] = recovered;
    candidates[2] = coarse;
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_select(
        candidates, 3U, &selection_a) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_hhcq_reciprocal_economy_select(
        candidates, 3U, &selection_b) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&selection_a, &selection_b, sizeof(selection_a)) == 0);
    assert(selection_a.candidate_count == 3U);
    assert(selection_a.admitted_count == 3U);
    assert(selection_a.selected_candidate_index == 1U);
    assert(selection_a.selected_route_id == 20U);
    assert(selection_a.selected_effective_resolution_index == 34U);
    assert(selection_a.selected_intrinsic_resolution_index == 30U);
    assert(selection_a.selected_effective_resolution_parameters == 1U);
    assert(selection_a.selected_net_budget_units == 5072);
    assert(selection_a.exact_integer_only == 1U);
    assert(selection_a.candidate_only == 1U);
    assert(selection_a.canonical_authority_changed == 0U);
    assert(selection_a.floating_point_authority == 0U);

    assert(hhs_exact_pass219_hhcq_joint_validate_state(&state) == HHS_EXACT_STATUS_OK);
    assert(sizeof(state) == 112U);
    return 0;
}
