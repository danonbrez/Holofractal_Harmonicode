#include "../include/hhs_pass219_global_latency_policy_25_3_1_0.h"

#include <limits.h>
#include <string.h>

static uint32_t hhs219_latency_version_word(void) {
    return (HHS_EXACT_PASS219_GLOBAL_LATENCY_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_GLOBAL_LATENCY_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_GLOBAL_LATENCY_VERSION_PATCH;
}

static int hhs219_latency_bool(uint8_t value) {
    return value <= 1U;
}

static uint64_t hhs219_latency_budget_numerator_ns(uint32_t tier) {
    switch (tier) {
        case HHS_EXACT_PASS219_LATENCY_TIER1_120FPS:
            return HHS_EXACT_PASS219_LATENCY_BASE_NUMERATOR_NS *
                   HHS_EXACT_PASS219_LATENCY_TIER1_MULTIPLIER;
        case HHS_EXACT_PASS219_LATENCY_TIER2_60FPS:
            return HHS_EXACT_PASS219_LATENCY_BASE_NUMERATOR_NS *
                   HHS_EXACT_PASS219_LATENCY_TIER2_MULTIPLIER;
        case HHS_EXACT_PASS219_LATENCY_TIER3_30FPS:
            return HHS_EXACT_PASS219_LATENCY_BASE_NUMERATOR_NS *
                   HHS_EXACT_PASS219_LATENCY_TIER3_MULTIPLIER;
        default:
            return 0U;
    }
}

static int hhs219_latency_fraction_within_tier(
    uint64_t numerator_ns,
    uint64_t denominator,
    uint32_t tier
) {
    const uint64_t budget_numerator = hhs219_latency_budget_numerator_ns(tier);
    uint64_t left;
    uint64_t right;

    if (denominator == 0U || budget_numerator == 0U)
        return 0;

    if (numerator_ns > UINT64_MAX / HHS_EXACT_PASS219_LATENCY_BASE_DENOMINATOR_NS)
        return 0;
    left = numerator_ns * HHS_EXACT_PASS219_LATENCY_BASE_DENOMINATOR_NS;

    if (denominator > UINT64_MAX / budget_numerator)
        return 1;
    right = denominator * budget_numerator;

    return left <= right;
}

static uint32_t hhs219_latency_fraction_tier(
    uint64_t numerator_ns,
    uint64_t denominator
) {
    if (hhs219_latency_fraction_within_tier(
            numerator_ns,
            denominator,
            HHS_EXACT_PASS219_LATENCY_TIER1_120FPS))
        return HHS_EXACT_PASS219_LATENCY_TIER1_120FPS;

    if (hhs219_latency_fraction_within_tier(
            numerator_ns,
            denominator,
            HHS_EXACT_PASS219_LATENCY_TIER2_60FPS))
        return HHS_EXACT_PASS219_LATENCY_TIER2_60FPS;

    if (hhs219_latency_fraction_within_tier(
            numerator_ns,
            denominator,
            HHS_EXACT_PASS219_LATENCY_TIER3_30FPS))
        return HHS_EXACT_PASS219_LATENCY_TIER3_30FPS;

    return HHS_EXACT_PASS219_LATENCY_TIER_OVER_BUDGET;
}

uint32_t hhs_exact_pass219_global_latency_policy_version(void) {
    return hhs219_latency_version_word();
}

HHSExactStatus hhs_exact_pass219_global_latency_policy(
    HHSExactPass219GlobalLatencyPolicyV1 *out_policy
) {
    if (out_policy == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_policy, 0, sizeof(*out_policy));
    out_policy->struct_size = (uint32_t)sizeof(*out_policy);
    out_policy->version = hhs219_latency_version_word();

    out_policy->a2 = HHS_EXACT_PASS219_LATENCY_A2;
    out_policy->b2 = HHS_EXACT_PASS219_LATENCY_B2;
    out_policy->c2 = HHS_EXACT_PASS219_LATENCY_C2;
    out_policy->d2 = HHS_EXACT_PASS219_LATENCY_D2;

    out_policy->mean_ratio_numerator_ms =
        HHS_EXACT_PASS219_LATENCY_MEAN_RATIO_NUMERATOR_MS;
    out_policy->mean_ratio_denominator_ms =
        HHS_EXACT_PASS219_LATENCY_MEAN_RATIO_DENOMINATOR_MS;

    out_policy->base_numerator_ns =
        HHS_EXACT_PASS219_LATENCY_BASE_NUMERATOR_NS;
    out_policy->base_denominator_ns =
        HHS_EXACT_PASS219_LATENCY_BASE_DENOMINATOR_NS;

    out_policy->tier1_multiplier =
        HHS_EXACT_PASS219_LATENCY_TIER1_MULTIPLIER;
    out_policy->tier2_multiplier =
        HHS_EXACT_PASS219_LATENCY_TIER2_MULTIPLIER;
    out_policy->tier3_multiplier =
        HHS_EXACT_PASS219_LATENCY_TIER3_MULTIPLIER;

    out_policy->tier1_fps = HHS_EXACT_PASS219_LATENCY_TIER1_FPS;
    out_policy->tier2_fps = HHS_EXACT_PASS219_LATENCY_TIER2_FPS;
    out_policy->tier3_fps = HHS_EXACT_PASS219_LATENCY_TIER3_FPS;

    out_policy->exact_integer_classification_required = 1U;
    out_policy->timing_is_noncanonical = 1U;
    out_policy->semantic_equality_required_before_route_selection = 1U;
    out_policy->complete_path_preserved_if_budget_unmet = 1U;
    out_policy->singleton_vm81_authority_preserved = 1U;
    out_policy->hash72_hash216_authority_preserved = 1U;
    out_policy->candidate_acceleration_only = 1U;
    out_policy->global_promotion_requires_measured_benefit = 1U;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_global_latency_policy_validate(void) {
    HHSExactPass219GlobalLatencyPolicyV1 p;
    uint64_t lhs;
    uint64_t rhs;

    if (hhs_exact_pass219_global_latency_policy(&p) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (p.struct_size != sizeof(p) ||
        p.version != hhs219_latency_version_word() ||
        p.a2 != 1U ||
        p.b2 != 2U ||
        p.c2 != 3U ||
        p.d2 != 5U ||
        p.mean_ratio_numerator_ms != 25U ||
        p.mean_ratio_denominator_ms != 3U ||
        p.base_numerator_ns != UINT64_C(25000000) ||
        p.base_denominator_ns != UINT64_C(3) ||
        p.tier1_multiplier != 1U ||
        p.tier2_multiplier != 2U ||
        p.tier3_multiplier != 4U ||
        p.tier1_fps != 120U ||
        p.tier2_fps != 60U ||
        p.tier3_fps != 30U ||
        p.exact_integer_classification_required != 1U ||
        p.timing_is_noncanonical != 1U ||
        p.semantic_equality_required_before_route_selection != 1U ||
        p.complete_path_preserved_if_budget_unmet != 1U ||
        p.singleton_vm81_authority_preserved != 1U ||
        p.hash72_hash216_authority_preserved != 1U ||
        p.candidate_acceleration_only != 1U ||
        p.global_promotion_requires_measured_benefit != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    /* d^4/c^2 = 25/3, using d^2 = 5 and c^2 = 3. */
    lhs = (uint64_t)p.d2 * (uint64_t)p.d2 *
          (uint64_t)p.mean_ratio_denominator_ms;
    rhs = (uint64_t)p.c2 * (uint64_t)p.mean_ratio_numerator_ms;
    if (lhs != rhs)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    /* (b^2+c^2)^2/(a^2+b^2) = 25/3. */
    lhs = (uint64_t)(p.b2 + p.c2) * (uint64_t)(p.b2 + p.c2) *
          (uint64_t)p.mean_ratio_denominator_ms;
    rhs = (uint64_t)(p.a2 + p.b2) *
          (uint64_t)p.mean_ratio_numerator_ms;
    if (lhs != rhs)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    /*
     * Holographic recursive-window closure under the inherited exact
     * projection residues T=(t^3-t)=1 and M=(m^2-m)=1:
     *
     * d^4/c^2 =
     * [b^2*T + (a^2+b^2)*M]^2 / (d^2-b^2).
     */
    {
        const uint64_t t_residue = 1U;
        const uint64_t m_residue = 1U;
        const uint64_t combined =
            (uint64_t)p.b2 * t_residue +
            (uint64_t)(p.a2 + p.b2) * m_residue;

        lhs = (uint64_t)p.d2 * (uint64_t)p.d2 *
              (uint64_t)(p.d2 - p.b2);
        rhs = (uint64_t)p.c2 * combined * combined;
        if (lhs != rhs || combined != 5U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    /* Exact millisecond/fps closure for 120/60/30. */
    if ((uint64_t)25U * 120U != (uint64_t)1000U * 3U ||
        (uint64_t)50U * 60U != (uint64_t)1000U * 3U ||
        (uint64_t)100U * 30U != (uint64_t)1000U * 3U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_global_latency_classify_ns(
    uint64_t observed_ns,
    uint32_t *out_tier
) {
    if (out_tier == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    *out_tier = hhs219_latency_fraction_tier(observed_ns, 1U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_global_latency_window_evaluate(
    const HHSExactPass219LatencyWindowInputV1 *input,
    HHSExactPass219LatencyWindowResultV1 *out_result
) {
    uint64_t sorted[HHS_EXACT_PASS219_LATENCY_WINDOW_MAX_SAMPLES];
    uint64_t sum = 0U;
    uint64_t max_value = 0U;
    uint32_t count;
    uint32_t i;
    uint32_t rank1;
    uint64_t p95;

    if (input == NULL || out_result == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (input->struct_size != sizeof(*input) ||
        input->version != hhs219_latency_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    count = input->sample_count;
    if (count == 0U || count > HHS_EXACT_PASS219_LATENCY_WINDOW_MAX_SAMPLES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    for (i = 0U; i < count; ++i) {
        const uint64_t value = input->samples_ns[i];
        uint32_t j = i;

        if (UINT64_MAX - sum < value)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        sum += value;
        if (value > max_value)
            max_value = value;

        while (j > 0U && sorted[j - 1U] > value) {
            sorted[j] = sorted[j - 1U];
            --j;
        }
        sorted[j] = value;
    }

    rank1 = (95U * count + 99U) / 100U;
    if (rank1 == 0U || rank1 > count)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    p95 = sorted[rank1 - 1U];

    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (uint32_t)sizeof(*out_result);
    out_result->version = hhs219_latency_version_word();
    out_result->sample_count = count;
    out_result->p95_nearest_rank = rank1;
    out_result->sum_ns = sum;
    out_result->mean_numerator_ns = sum;
    out_result->mean_denominator = count;
    out_result->p95_ns = p95;
    out_result->max_ns = max_value;

    out_result->mean_tier = hhs219_latency_fraction_tier(sum, count);
    out_result->p95_tier = hhs219_latency_fraction_tier(p95, 1U);
    out_result->max_tier = hhs219_latency_fraction_tier(max_value, 1U);

    out_result->mean_within_tier1 =
        (uint8_t)(hhs219_latency_fraction_within_tier(
            sum, count, HHS_EXACT_PASS219_LATENCY_TIER1_120FPS) ? 1U : 0U);
    out_result->p95_within_tier2 =
        (uint8_t)(hhs219_latency_fraction_within_tier(
            p95, 1U, HHS_EXACT_PASS219_LATENCY_TIER2_60FPS) ? 1U : 0U);
    out_result->max_within_tier3 =
        (uint8_t)(hhs219_latency_fraction_within_tier(
            max_value, 1U, HHS_EXACT_PASS219_LATENCY_TIER3_30FPS) ? 1U : 0U);
    out_result->window_policy_met =
        (uint8_t)(out_result->mean_within_tier1 != 0U &&
                  out_result->p95_within_tier2 != 0U &&
                  out_result->max_within_tier3 != 0U ? 1U : 0U);
    out_result->timing_is_noncanonical = 1U;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_global_latency_select_route(
    const HHSExactPass219LatencyRouteV1 *routes,
    size_t route_count,
    uint32_t requested_tier,
    HHSExactPass219LatencySelectionV1 *out_selection
) {
    size_t i;
    size_t best_meeting = SIZE_MAX;
    size_t best_any = SIZE_MAX;
    uint8_t complete_fallback_present = 0U;

    if (routes == NULL || out_selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (route_count == 0U || route_count > HHS_EXACT_PASS219_LATENCY_MAX_ROUTES)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (requested_tier < HHS_EXACT_PASS219_LATENCY_TIER1_120FPS ||
        requested_tier > HHS_EXACT_PASS219_LATENCY_TIER3_30FPS)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    for (i = 0U; i < route_count; ++i) {
        const HHSExactPass219LatencyRouteV1 *r = &routes[i];
        uint32_t tier = HHS_EXACT_PASS219_LATENCY_TIER_INVALID;
        int eligible;

        if (r->struct_size != sizeof(*r) ||
            r->version != hhs219_latency_version_word())
            return HHS_EXACT_STATUS_VERSION_MISMATCH;
        if (!hhs219_latency_bool(r->exact_semantic_equal) ||
            !hhs219_latency_bool(r->exact_selector_proven) ||
            !hhs219_latency_bool(r->complete_fallback) ||
            !hhs219_latency_bool(r->candidate_only) ||
            !hhs219_latency_bool(r->canonical_authority_requested))
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        if (r->canonical_authority_requested != 0U ||
            r->candidate_only != 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        if (r->complete_fallback != 0U && r->exact_semantic_equal != 0U)
            complete_fallback_present = 1U;

        eligible =
            r->exact_semantic_equal != 0U &&
            (r->exact_selector_proven != 0U || r->complete_fallback != 0U);

        if (!eligible)
            continue;

        if (hhs_exact_pass219_global_latency_classify_ns(
                r->observed_ns, &tier) != HHS_EXACT_STATUS_OK)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        if (best_any == SIZE_MAX ||
            r->observed_ns < routes[best_any].observed_ns ||
            (r->observed_ns == routes[best_any].observed_ns &&
             r->work_units < routes[best_any].work_units) ||
            (r->observed_ns == routes[best_any].observed_ns &&
             r->work_units == routes[best_any].work_units &&
             r->route_id < routes[best_any].route_id))
            best_any = i;

        if (tier <= requested_tier &&
            (best_meeting == SIZE_MAX ||
             r->observed_ns < routes[best_meeting].observed_ns ||
             (r->observed_ns == routes[best_meeting].observed_ns &&
              r->work_units < routes[best_meeting].work_units) ||
             (r->observed_ns == routes[best_meeting].observed_ns &&
              r->work_units == routes[best_meeting].work_units &&
              r->route_id < routes[best_meeting].route_id)))
            best_meeting = i;
    }

    if (complete_fallback_present == 0U || best_any == SIZE_MAX)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    {
        const size_t chosen = best_meeting != SIZE_MAX ? best_meeting : best_any;
        const HHSExactPass219LatencyRouteV1 *r = &routes[chosen];
        uint32_t tier = HHS_EXACT_PASS219_LATENCY_TIER_INVALID;

        if (hhs_exact_pass219_global_latency_classify_ns(
                r->observed_ns, &tier) != HHS_EXACT_STATUS_OK)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        memset(out_selection, 0, sizeof(*out_selection));
        out_selection->struct_size = (uint32_t)sizeof(*out_selection);
        out_selection->version = hhs219_latency_version_word();
        out_selection->requested_tier = requested_tier;
        out_selection->selected_route_id = r->route_id;
        out_selection->selected_tier = tier;
        out_selection->decision =
            best_meeting != SIZE_MAX
                ? HHS_EXACT_PASS219_LATENCY_DECISION_BUDGET_MET
                : HHS_EXACT_PASS219_LATENCY_DECISION_BUDGET_UNMET;
        out_selection->selected_observed_ns = r->observed_ns;
        out_selection->selected_work_units = r->work_units;
        out_selection->exact_semantic_equal_required = 1U;
        out_selection->complete_fallback_present = complete_fallback_present;
        out_selection->budget_met = (uint8_t)(best_meeting != SIZE_MAX ? 1U : 0U);
        out_selection->canonical_authority = 0U;
        out_selection->timing_is_noncanonical = 1U;
    }

    return HHS_EXACT_STATUS_OK;
}
