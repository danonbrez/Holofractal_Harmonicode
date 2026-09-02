#include "hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static int expect_tier(uint64_t ns, uint32_t expected) {
    uint32_t tier = 0U;
    if (hhs_exact_pass219_global_latency_classify_ns(ns, &tier) !=
        HHS_EXACT_STATUS_OK)
        return 0;
    return tier == expected;
}

static HHSExactPass219LatencyRouteV1 route(
    uint32_t id,
    uint64_t ns,
    uint64_t work,
    uint8_t equal,
    uint8_t selector,
    uint8_t fallback
) {
    HHSExactPass219LatencyRouteV1 r;
    memset(&r, 0, sizeof(r));
    r.struct_size = (uint32_t)sizeof(r);
    r.version = hhs_exact_pass219_global_latency_policy_version();
    r.route_id = id;
    r.observed_ns = ns;
    r.work_units = work;
    r.exact_semantic_equal = equal;
    r.exact_selector_proven = selector;
    r.complete_fallback = fallback;
    r.candidate_only = 1U;
    return r;
}

int main(void) {
    HHSExactPass219GlobalLatencyPolicyV1 policy;
    HHSExactPass219LatencyWindowInputV1 window;
    HHSExactPass219LatencyWindowResultV1 result;
    HHSExactPass219LatencySelectionV1 selection;
    HHSExactPass219LatencyRouteV1 routes[2];
    uint32_t i;

    if (hhs_exact_pass219_global_latency_policy_validate() != HHS_EXACT_STATUS_OK)
        return 1;
    if (hhs_exact_pass219_global_latency_policy(&policy) != HHS_EXACT_STATUS_OK)
        return 2;

    if (policy.a2 != 1U || policy.b2 != 2U || policy.c2 != 3U || policy.d2 != 5U)
        return 3;
    if (policy.mean_ratio_numerator_ms != 25U ||
        policy.mean_ratio_denominator_ms != 3U)
        return 4;
    if ((uint64_t)policy.d2 * policy.d2 * policy.mean_ratio_denominator_ms !=
        (uint64_t)policy.c2 * policy.mean_ratio_numerator_ms)
        return 5;
    if ((uint64_t)(policy.b2 + policy.c2) * (policy.b2 + policy.c2) *
            policy.mean_ratio_denominator_ms !=
        (uint64_t)(policy.a2 + policy.b2) * policy.mean_ratio_numerator_ms)
        return 6;

    if (!expect_tier(UINT64_C(8333333), HHS_EXACT_PASS219_LATENCY_TIER1_120FPS) ||
        !expect_tier(UINT64_C(8333334), HHS_EXACT_PASS219_LATENCY_TIER2_60FPS) ||
        !expect_tier(UINT64_C(16666666), HHS_EXACT_PASS219_LATENCY_TIER2_60FPS) ||
        !expect_tier(UINT64_C(16666667), HHS_EXACT_PASS219_LATENCY_TIER3_30FPS) ||
        !expect_tier(UINT64_C(33333333), HHS_EXACT_PASS219_LATENCY_TIER3_30FPS) ||
        !expect_tier(UINT64_C(33333334), HHS_EXACT_PASS219_LATENCY_TIER_OVER_BUDGET))
        return 7;

    memset(&window, 0, sizeof(window));
    window.struct_size = (uint32_t)sizeof(window);
    window.version = hhs_exact_pass219_global_latency_policy_version();
    window.sample_count = 20U;
    for (i = 0U; i < 19U; ++i)
        window.samples_ns[i] = UINT64_C(8000000);
    window.samples_ns[19] = UINT64_C(12000000);
    memset(&result, 0, sizeof(result));
    if (hhs_exact_pass219_global_latency_window_evaluate(&window, &result) !=
        HHS_EXACT_STATUS_OK)
        return 8;
    if (result.mean_within_tier1 != 1U ||
        result.p95_within_tier2 != 1U ||
        result.max_within_tier3 != 1U ||
        result.window_policy_met != 1U ||
        result.p95_nearest_rank != 19U ||
        result.p95_ns != UINT64_C(8000000) ||
        result.max_ns != UINT64_C(12000000))
        return 9;

    window.samples_ns[19] = UINT64_C(34000000);
    if (hhs_exact_pass219_global_latency_window_evaluate(&window, &result) !=
        HHS_EXACT_STATUS_OK)
        return 10;
    if (result.max_within_tier3 != 0U ||
        result.window_policy_met != 0U ||
        result.max_tier != HHS_EXACT_PASS219_LATENCY_TIER_OVER_BUDGET)
        return 11;

    /* Fold7 measured dense and M=729 routes. */
    routes[0] = route(
        0U,
        UINT64_C(13400000),
        UINT64_C(68024448),
        1U,
        0U,
        1U
    );
    routes[1] = route(
        729U,
        UINT64_C(1368750),
        UINT64_C(7558272),
        1U,
        1U,
        0U
    );

    memset(&selection, 0, sizeof(selection));
    if (hhs_exact_pass219_global_latency_select_route(
            routes,
            2U,
            HHS_EXACT_PASS219_LATENCY_TIER1_120FPS,
            &selection) != HHS_EXACT_STATUS_OK)
        return 12;
    if (selection.selected_route_id != 729U ||
        selection.selected_tier != HHS_EXACT_PASS219_LATENCY_TIER1_120FPS ||
        selection.decision != HHS_EXACT_PASS219_LATENCY_DECISION_BUDGET_MET ||
        selection.budget_met != 1U ||
        selection.canonical_authority != 0U ||
        selection.timing_is_noncanonical != 1U)
        return 13;

    /* Remove the exact selector proof: complete dense route must be preserved. */
    routes[1].exact_selector_proven = 0U;
    if (hhs_exact_pass219_global_latency_select_route(
            routes,
            2U,
            HHS_EXACT_PASS219_LATENCY_TIER1_120FPS,
            &selection) != HHS_EXACT_STATUS_OK)
        return 14;
    if (selection.selected_route_id != 0U ||
        selection.selected_tier != HHS_EXACT_PASS219_LATENCY_TIER2_60FPS ||
        selection.decision != HHS_EXACT_PASS219_LATENCY_DECISION_BUDGET_UNMET ||
        selection.budget_met != 0U ||
        selection.complete_fallback_present != 1U)
        return 15;

    routes[1].exact_selector_proven = 1U;
    routes[1].canonical_authority_requested = 1U;
    if (hhs_exact_pass219_global_latency_select_route(
            routes,
            2U,
            HHS_EXACT_PASS219_LATENCY_TIER1_120FPS,
            &selection) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        return 16;

    routes[1].canonical_authority_requested = 0U;
    routes[0].complete_fallback = 0U;
    if (hhs_exact_pass219_global_latency_select_route(
            routes,
            2U,
            HHS_EXACT_PASS219_LATENCY_TIER1_120FPS,
            &selection) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        return 17;

    puts("PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0_C_OK");
    return 0;
}
