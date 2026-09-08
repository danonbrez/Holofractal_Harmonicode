#include "../include/hhs_pass219_hhcq_reciprocal_economy_1_29.h"

#include <limits.h>
#include <string.h>

static uint64_t hhs_p219_hhcq_economy_mix64(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static int hhs_p219_hhcq_economy_add_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL || UINT64_MAX - a < b)
        return 0;
    *out = a + b;
    return 1;
}

static int hhs_p219_hhcq_economy_phase5_divisor_value(uint8_t index, uint16_t *out_value) {
    return hhs_exact_pass219_hhcq_resolution_divisor(index, out_value) == HHS_EXACT_STATUS_OK;
}

static int hhs_p219_hhcq_economy_is_phase5_divisor(uint16_t value) {
    uint8_t i;
    uint16_t divisor;
    for (i = 0U; i < (uint8_t)HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT; ++i) {
        if (!hhs_p219_hhcq_economy_phase5_divisor_value(i, &divisor))
            return 0;
        if (divisor == value)
            return 1;
    }
    return 0;
}

static int hhs_p219_hhcq_economy_flag(uint8_t value) {
    return value == 0U || value == 1U;
}

static void hhs_p219_hhcq_economy_axis(
    uint64_t units,
    uint64_t *out_credit,
    uint64_t *out_debt
) {
    if (units <= HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS) {
        *out_credit = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS - units;
        *out_debt = 0U;
    } else {
        *out_credit = 0U;
        *out_debt = units - HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    }
}

uint32_t hhs_exact_pass219_hhcq_reciprocal_economy_version(void) {
    return HHS_EXACT_PASS219_HHCQ_RECIPROCAL_ECONOMY_VERSION;
}

HHSExactStatus hhs_exact_pass219_hhcq_reciprocal_economy_descriptor(
    HHSExactPass219HHCQReciprocalEconomyDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_HHCQ_RECIPROCAL_ECONOMY_VERSION;
    out_descriptor->inherited_policy_state_bytes =
        (uint32_t)sizeof(HHSExactPass219HHCQJointStateV1);
    out_descriptor->max_candidates = HHS_EXACT_PASS219_HHCQ_ECONOMY_MAX_CANDIDATES;
    out_descriptor->parity_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    out_descriptor->reciprocal_1_over_n_to_n_boundary = 1U;
    out_descriptor->n_must_be_phase5_divisor = 1U;
    out_descriptor->separate_axis_ledgers = 1U;
    out_descriptor->exact_one_to_one_information_closure = 1U;
    out_descriptor->lower_resolution_recovery_allowed = 1U;
    out_descriptor->spendable_savings_budget = 1U;
    out_descriptor->one_step_translation_required = 1U;
    out_descriptor->all_native_modalities_required = 1U;
    out_descriptor->phase5_resolution_locked = 1U;
    out_descriptor->fixed_size_policy_state = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->exact_integer_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(
    const HHSExactPass219HHCQEconomyCandidateV1 *candidate,
    HHSExactPass219HHCQEconomyResultV1 *out_result
) {
    uint64_t upper;
    uint64_t total_savings = 0U;
    uint64_t total_debt = 0U;
    uint64_t total_spend = 0U;
    uint64_t total_cost;
    uint16_t intrinsic_parameters;
    uint16_t effective_parameters;
    uint16_t required_parameters;
    uint64_t signature;
    int admitted;

    if (candidate == NULL || out_result == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate->struct_size != sizeof(*candidate) ||
        candidate->version != HHS_EXACT_PASS219_HHCQ_RECIPROCAL_ECONOMY_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (candidate->reciprocal_n == 0U ||
        !hhs_p219_hhcq_economy_is_phase5_divisor(candidate->reciprocal_n) ||
        candidate->intrinsic_resolution_index >= HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT ||
        candidate->effective_resolution_index >= HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT ||
        candidate->required_resolution_index >= HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT ||
        candidate->latency_units == 0U || candidate->memory_units == 0U ||
        candidate->compression_units == 0U || candidate->translation_units == 0U ||
        candidate->lossy_information_units > HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS ||
        candidate->recovered_information_units > HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS ||
        !hhs_p219_hhcq_economy_flag(candidate->exact_semantic_closure) ||
        !hhs_p219_hhcq_economy_flag(candidate->exact_reconstruction) ||
        !hhs_p219_hhcq_economy_flag(candidate->all_native_modalities_translatable) ||
        !hhs_p219_hhcq_economy_flag(candidate->one_step_translation) ||
        !hhs_p219_hhcq_economy_flag(candidate->phase5_resolution_locked) ||
        !hhs_p219_hhcq_economy_flag(candidate->candidate_only) ||
        !hhs_p219_hhcq_economy_flag(candidate->canonical_authority_requested) ||
        !hhs_p219_hhcq_economy_flag(candidate->floating_point_authority_requested))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    if (!hhs_p219_hhcq_economy_phase5_divisor_value(
            candidate->intrinsic_resolution_index, &intrinsic_parameters) ||
        !hhs_p219_hhcq_economy_phase5_divisor_value(
            candidate->effective_resolution_index, &effective_parameters) ||
        !hhs_p219_hhcq_economy_phase5_divisor_value(
            candidate->required_resolution_index, &required_parameters))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (candidate->effective_resolution_index < candidate->intrinsic_resolution_index)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    upper = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS * (uint64_t)candidate->reciprocal_n;

    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (uint32_t)sizeof(*out_result);
    out_result->version = HHS_EXACT_PASS219_HHCQ_RECIPROCAL_ECONOMY_VERSION;
    out_result->route_id = candidate->route_id;
    out_result->decision = HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_REJECTED;
    out_result->reciprocal_n = candidate->reciprocal_n;
    out_result->intrinsic_resolution_parameters = intrinsic_parameters;
    out_result->effective_resolution_parameters = effective_parameters;
    out_result->required_resolution_parameters = required_parameters;
    out_result->reciprocal_lower_bound_units =
        HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS / (uint64_t)candidate->reciprocal_n;
    out_result->reciprocal_upper_bound_units = upper;

    out_result->reciprocal_bounds_met =
        candidate->latency_units >= out_result->reciprocal_lower_bound_units &&
        candidate->latency_units <= upper &&
        candidate->memory_units >= out_result->reciprocal_lower_bound_units &&
        candidate->memory_units <= upper &&
        candidate->compression_units >= out_result->reciprocal_lower_bound_units &&
        candidate->compression_units <= upper &&
        candidate->translation_units >= out_result->reciprocal_lower_bound_units &&
        candidate->translation_units <= upper &&
        candidate->redundancy_spend_units <= upper &&
        candidate->ecc_spend_units <= upper &&
        candidate->precision_spend_units <= upper &&
        candidate->learning_spend_units <= upper;

    hhs_p219_hhcq_economy_axis(candidate->latency_units,
                               &out_result->latency_credit_units,
                               &out_result->latency_debt_units);
    hhs_p219_hhcq_economy_axis(candidate->memory_units,
                               &out_result->memory_credit_units,
                               &out_result->memory_debt_units);
    hhs_p219_hhcq_economy_axis(candidate->compression_units,
                               &out_result->compression_credit_units,
                               &out_result->compression_debt_units);
    hhs_p219_hhcq_economy_axis(candidate->translation_units,
                               &out_result->translation_credit_units,
                               &out_result->translation_debt_units);

    if (!hhs_p219_hhcq_economy_add_u64(out_result->latency_credit_units,
                                        out_result->memory_credit_units,
                                        &total_savings) ||
        !hhs_p219_hhcq_economy_add_u64(total_savings,
                                        out_result->compression_credit_units,
                                        &total_savings) ||
        !hhs_p219_hhcq_economy_add_u64(total_savings,
                                        out_result->translation_credit_units,
                                        &total_savings) ||
        !hhs_p219_hhcq_economy_add_u64(out_result->latency_debt_units,
                                        out_result->memory_debt_units,
                                        &total_debt) ||
        !hhs_p219_hhcq_economy_add_u64(total_debt,
                                        out_result->compression_debt_units,
                                        &total_debt) ||
        !hhs_p219_hhcq_economy_add_u64(total_debt,
                                        out_result->translation_debt_units,
                                        &total_debt) ||
        !hhs_p219_hhcq_economy_add_u64(candidate->redundancy_spend_units,
                                        candidate->ecc_spend_units,
                                        &total_spend) ||
        !hhs_p219_hhcq_economy_add_u64(total_spend,
                                        candidate->precision_spend_units,
                                        &total_spend) ||
        !hhs_p219_hhcq_economy_add_u64(total_spend,
                                        candidate->learning_spend_units,
                                        &total_spend) ||
        !hhs_p219_hhcq_economy_add_u64(total_debt, total_spend, &total_cost) ||
        total_savings > (uint64_t)INT64_MAX || total_cost > (uint64_t)INT64_MAX)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    out_result->total_savings_units = total_savings;
    out_result->total_axis_debt_units = total_debt;
    out_result->total_spend_units = total_spend;
    if (total_savings >= total_cost)
        out_result->net_budget_units = (int64_t)(total_savings - total_cost);
    else
        out_result->net_budget_units = -(int64_t)(total_cost - total_savings);

    out_result->lossy_information_units = candidate->lossy_information_units;
    out_result->recovered_information_units = candidate->recovered_information_units;
    out_result->information_one_to_one =
        candidate->lossy_information_units == candidate->recovered_information_units;
    out_result->effective_resolution_met =
        candidate->effective_resolution_index >= candidate->required_resolution_index;
    out_result->lower_resolution_recovered =
        candidate->intrinsic_resolution_index < candidate->required_resolution_index &&
        out_result->effective_resolution_met != 0U &&
        out_result->information_one_to_one != 0U &&
        candidate->lossy_information_units != 0U;
    out_result->exact_semantic_closure = candidate->exact_semantic_closure;
    out_result->exact_reconstruction = candidate->exact_reconstruction;
    out_result->all_native_modalities_translatable =
        candidate->all_native_modalities_translatable;
    out_result->one_step_translation = candidate->one_step_translation;
    out_result->phase5_resolution_locked = candidate->phase5_resolution_locked;
    out_result->budget_nonnegative = out_result->net_budget_units >= 0 ? 1U : 0U;
    out_result->candidate_only = 1U;
    out_result->exact_integer_only = 1U;

    admitted =
        out_result->reciprocal_bounds_met != 0U &&
        out_result->information_one_to_one != 0U &&
        out_result->effective_resolution_met != 0U &&
        candidate->exact_semantic_closure != 0U &&
        candidate->exact_reconstruction != 0U &&
        candidate->all_native_modalities_translatable != 0U &&
        candidate->one_step_translation != 0U &&
        candidate->phase5_resolution_locked != 0U &&
        candidate->candidate_only != 0U &&
        candidate->canonical_authority_requested == 0U &&
        candidate->floating_point_authority_requested == 0U &&
        out_result->budget_nonnegative != 0U;

    if (candidate->intrinsic_resolution_index < candidate->required_resolution_index &&
        out_result->lower_resolution_recovered == 0U)
        admitted = 0;

    if (admitted)
        out_result->decision = HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_ADMITTED;

    signature = UINT64_C(0x219ec0a0b1e00129) ^
        ((uint64_t)candidate->route_id << 32U) ^
        ((uint64_t)candidate->reciprocal_n << 16U) ^
        ((uint64_t)candidate->intrinsic_resolution_index << 8U) ^
        (uint64_t)candidate->effective_resolution_index;
    signature = hhs_p219_hhcq_economy_mix64(
        signature ^ candidate->latency_units ^
        (candidate->memory_units << 1U) ^
        (candidate->compression_units << 2U) ^
        (candidate->translation_units << 3U));
    signature = hhs_p219_hhcq_economy_mix64(
        signature ^ total_savings ^ (total_debt << 1U) ^
        (total_spend << 2U) ^ (uint64_t)out_result->net_budget_units ^
        ((uint64_t)candidate->lossy_information_units << 32U) ^
        (uint64_t)candidate->recovered_information_units ^
        ((uint64_t)out_result->decision << 60U));
    out_result->result_signature64 = signature;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_reciprocal_economy_select(
    const HHSExactPass219HHCQEconomyCandidateV1 *candidates,
    size_t candidate_count,
    HHSExactPass219HHCQEconomySelectionV1 *out_selection
) {
    size_t i;
    size_t best_index = 0U;
    int have_best = 0;
    HHSExactPass219HHCQEconomyResultV1 best_result;
    uint64_t signature = UINT64_C(0x2195e1ec7e001029);

    if (candidates == NULL || out_selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate_count == 0U || candidate_count > HHS_EXACT_PASS219_HHCQ_ECONOMY_MAX_CANDIDATES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_selection, 0, sizeof(*out_selection));
    memset(&best_result, 0, sizeof(best_result));
    out_selection->struct_size = (uint32_t)sizeof(*out_selection);
    out_selection->version = HHS_EXACT_PASS219_HHCQ_RECIPROCAL_ECONOMY_VERSION;
    out_selection->candidate_count = (uint32_t)candidate_count;
    out_selection->selected_route_id = UINT32_MAX;
    out_selection->selected_candidate_index = UINT32_MAX;
    out_selection->exact_integer_only = 1U;
    out_selection->candidate_only = 1U;

    for (i = 0U; i < candidate_count; ++i) {
        HHSExactPass219HHCQEconomyResultV1 result;
        HHSExactStatus status = hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(
            &candidates[i], &result);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        signature = hhs_p219_hhcq_economy_mix64(
            signature ^ result.result_signature64 ^ (uint64_t)i);
        if (result.decision != HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_ADMITTED)
            continue;
        ++out_selection->admitted_count;
        if (!have_best ||
            candidates[i].effective_resolution_index >
                candidates[best_index].effective_resolution_index ||
            (candidates[i].effective_resolution_index ==
                 candidates[best_index].effective_resolution_index &&
             result.net_budget_units > best_result.net_budget_units) ||
            (candidates[i].effective_resolution_index ==
                 candidates[best_index].effective_resolution_index &&
             result.net_budget_units == best_result.net_budget_units &&
             candidates[i].latency_units < candidates[best_index].latency_units) ||
            (candidates[i].effective_resolution_index ==
                 candidates[best_index].effective_resolution_index &&
             result.net_budget_units == best_result.net_budget_units &&
             candidates[i].latency_units == candidates[best_index].latency_units &&
             candidates[i].memory_units < candidates[best_index].memory_units) ||
            (candidates[i].effective_resolution_index ==
                 candidates[best_index].effective_resolution_index &&
             result.net_budget_units == best_result.net_budget_units &&
             candidates[i].latency_units == candidates[best_index].latency_units &&
             candidates[i].memory_units == candidates[best_index].memory_units &&
             candidates[i].compression_units < candidates[best_index].compression_units) ||
            (candidates[i].effective_resolution_index ==
                 candidates[best_index].effective_resolution_index &&
             result.net_budget_units == best_result.net_budget_units &&
             candidates[i].latency_units == candidates[best_index].latency_units &&
             candidates[i].memory_units == candidates[best_index].memory_units &&
             candidates[i].compression_units == candidates[best_index].compression_units &&
             candidates[i].translation_units < candidates[best_index].translation_units) ||
            (candidates[i].effective_resolution_index ==
                 candidates[best_index].effective_resolution_index &&
             result.net_budget_units == best_result.net_budget_units &&
             candidates[i].latency_units == candidates[best_index].latency_units &&
             candidates[i].memory_units == candidates[best_index].memory_units &&
             candidates[i].compression_units == candidates[best_index].compression_units &&
             candidates[i].translation_units == candidates[best_index].translation_units &&
             candidates[i].route_id < candidates[best_index].route_id)) {
            have_best = 1;
            best_index = i;
            best_result = result;
        }
    }

    if (have_best) {
        uint16_t parameters = 0U;
        if (!hhs_p219_hhcq_economy_phase5_divisor_value(
                candidates[best_index].effective_resolution_index, &parameters))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out_selection->selected_route_id = candidates[best_index].route_id;
        out_selection->selected_candidate_index = (uint32_t)best_index;
        out_selection->selected_effective_resolution_index =
            candidates[best_index].effective_resolution_index;
        out_selection->selected_intrinsic_resolution_index =
            candidates[best_index].intrinsic_resolution_index;
        out_selection->selected_effective_resolution_parameters = parameters;
        out_selection->selected_net_budget_units = best_result.net_budget_units;
    }
    out_selection->selection_signature64 = hhs_p219_hhcq_economy_mix64(
        signature ^ ((uint64_t)out_selection->admitted_count << 48U) ^
        ((uint64_t)out_selection->selected_route_id << 16U) ^
        (uint64_t)out_selection->selected_candidate_index);
    return HHS_EXACT_STATUS_OK;
}
