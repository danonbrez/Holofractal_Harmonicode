#include "../include/hhs_pass219_harmonic36_global_latency_policy_1_16.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

uint32_t hhs_exact_pass219_h36_global_latency_policy_version(void) {
    return HHS_EXACT_PASS219_H36_GLOBAL_LATENCY_VERSION;
}

static void h36_global_latency_route_from_candidate(
    const HHSExactPass219H36StackCandidateEvidenceV1 *candidate,
    HHSExactPass219LatencyRouteV1 *out_route
) {
    memset(out_route, 0, sizeof(*out_route));
    out_route->struct_size = (uint32_t)sizeof(*out_route);
    out_route->version = hhs_exact_pass219_global_latency_policy_version();
    out_route->route_id = candidate->candidate_id;
    out_route->observed_ns = candidate->median_ns;

    /*
     * H36 stack selection requires rounds_per_sample equality across candidates.
     * Using that exact shared work quantum preserves the existing stable
     * candidate-id tie break in the global planner.
     */
    out_route->work_units = (uint64_t)candidate->rounds_per_sample;
    out_route->exact_semantic_equal = candidate->exact_result_equal;
    out_route->exact_selector_proven = 1U;

    /*
     * Both H36 stack candidates are complete independently executable paths
     * whose semantic result equality is proven before timing. Either therefore
     * remains an exact complete fallback; timing never authorizes omission.
     */
    out_route->complete_fallback = 1U;
    out_route->candidate_only = 1U;
    out_route->canonical_authority_requested = 0U;
}

HHSExactStatus hhs_exact_pass219_h36_global_latency_select(
    const HHSExactPass219H36StackCandidateEvidenceV1 *first,
    const HHSExactPass219H36StackCandidateEvidenceV1 *second,
    uint32_t requested_tier,
    HHSExactPass219H36GlobalLatencySelectionV1 *out_selection
) {
    HHSExactPass219LatencyRouteV1 routes[2];
    HHSExactPass219H36StackSelectionV1 stack_selection;
    HHSExactPass219LatencySelectionV1 latency_selection;
    HHSExactStatus status;

    if (out_selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_global_latency_policy_validate();
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_h36_stack_select(
        first, second, &stack_selection);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    h36_global_latency_route_from_candidate(first, &routes[0]);
    h36_global_latency_route_from_candidate(second, &routes[1]);

    status = hhs_exact_pass219_global_latency_select_route(
        routes,
        sizeof(routes) / sizeof(routes[0]),
        requested_tier,
        &latency_selection);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (latency_selection.selected_route_id !=
            stack_selection.selected_candidate_id ||
        latency_selection.selected_observed_ns !=
            stack_selection.selected_median_ns ||
        latency_selection.complete_fallback_present != 1U ||
        latency_selection.canonical_authority != 0U ||
        latency_selection.timing_is_noncanonical != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_selection, 0, sizeof(*out_selection));
    out_selection->struct_size = (uint32_t)sizeof(*out_selection);
    out_selection->version = HHS_EXACT_PASS219_H36_GLOBAL_LATENCY_VERSION;
    out_selection->requested_tier = requested_tier;
    out_selection->stack_selection = stack_selection;
    out_selection->latency_selection = latency_selection;
    out_selection->global_latency_policy_required = 1U;
    out_selection->exact_selector_parity = 1U;
    out_selection->complete_fallback_preserved = 1U;
    out_selection->budget_decision_explicit = 1U;
    out_selection->required_computation_preserved = 1U;
    out_selection->candidate_only = 1U;
    out_selection->canonical_authority = 0U;
    out_selection->timing_is_noncanonical = 1U;

    return hhs_exact_pass219_h36_global_latency_selection_validate(
        out_selection);
}

HHSExactStatus hhs_exact_pass219_h36_global_latency_selection_validate(
    const HHSExactPass219H36GlobalLatencySelectionV1 *selection
) {
    uint32_t classified_tier = HHS_EXACT_PASS219_LATENCY_TIER_INVALID;
    HHSExactStatus status;

    if (selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (selection->struct_size != sizeof(*selection) ||
        selection->version != HHS_EXACT_PASS219_H36_GLOBAL_LATENCY_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = hhs_exact_pass219_h36_stack_selection_validate(
        &selection->stack_selection);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (selection->requested_tier <
            HHS_EXACT_PASS219_LATENCY_TIER1_120FPS ||
        selection->requested_tier >
            HHS_EXACT_PASS219_LATENCY_TIER3_30FPS ||
        selection->latency_selection.struct_size !=
            sizeof(selection->latency_selection) ||
        selection->latency_selection.version !=
            hhs_exact_pass219_global_latency_policy_version() ||
        selection->latency_selection.requested_tier !=
            selection->requested_tier ||
        selection->latency_selection.selected_route_id !=
            selection->stack_selection.selected_candidate_id ||
        selection->latency_selection.selected_observed_ns !=
            selection->stack_selection.selected_median_ns ||
        selection->latency_selection.exact_semantic_equal_required != 1U ||
        selection->latency_selection.complete_fallback_present != 1U ||
        selection->latency_selection.canonical_authority != 0U ||
        selection->latency_selection.timing_is_noncanonical != 1U ||
        selection->global_latency_policy_required != 1U ||
        selection->exact_selector_parity != 1U ||
        selection->complete_fallback_preserved != 1U ||
        selection->budget_decision_explicit != 1U ||
        selection->required_computation_preserved != 1U ||
        selection->candidate_only != 1U ||
        selection->canonical_authority != 0U ||
        selection->timing_is_noncanonical != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (selection->latency_selection.decision ==
            HHS_EXACT_PASS219_LATENCY_DECISION_BUDGET_MET) {
        if (selection->latency_selection.budget_met != 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    } else if (selection->latency_selection.decision ==
                   HHS_EXACT_PASS219_LATENCY_DECISION_BUDGET_UNMET) {
        if (selection->latency_selection.budget_met != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    } else {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    status = hhs_exact_pass219_global_latency_classify_ns(
        selection->latency_selection.selected_observed_ns,
        &classified_tier);
    if (status != HHS_EXACT_STATUS_OK ||
        classified_tier != selection->latency_selection.selected_tier)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}
