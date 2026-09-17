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
    out_route->work_units = (uint64_t)candidate->rounds_per_sample;
    out_route->exact_semantic_equal = candidate->exact_result_equal;
    out_route->exact_selector_proven = 1U;
    out_route->complete_fallback = 1U;
    out_route->candidate_only = 1U;
    out_route->canonical_authority_requested = 0U;
}

static void h36_global_latency_route_from_selection(
    const HHSExactPass219H36StackSelectionV1 *selection,
    HHSExactPass219LatencyRouteV1 *out_route
) {
    memset(out_route, 0, sizeof(*out_route));
    out_route->struct_size = (uint32_t)sizeof(*out_route);
    out_route->version = hhs_exact_pass219_global_latency_policy_version();
    out_route->route_id = selection->selected_candidate_id;
    out_route->observed_ns = selection->selected_median_ns;
    /*
     * A prevalidated selection has already compared equal-work candidates.
     * The absolute work quantum is no longer needed for a one-route latency
     * classification, so one exact selected route is the complete work unit.
     */
    out_route->work_units = UINT64_C(1);
    out_route->exact_semantic_equal = 1U;
    out_route->exact_selector_proven = 1U;
    out_route->complete_fallback = 1U;
    out_route->candidate_only = 1U;
    out_route->canonical_authority_requested = 0U;
}

static HHSExactStatus h36_global_latency_finish(
    const HHSExactPass219H36StackSelectionV1 *stack_selection,
    const HHSExactPass219LatencySelectionV1 *latency_selection,
    uint32_t requested_tier,
    HHSExactPass219H36GlobalLatencySelectionV1 *out_selection
) {
    if (stack_selection == NULL || latency_selection == NULL || out_selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    if (latency_selection->selected_route_id !=
            stack_selection->selected_candidate_id ||
        latency_selection->selected_observed_ns !=
            stack_selection->selected_median_ns ||
        latency_selection->complete_fallback_present != 1U ||
        latency_selection->canonical_authority != 0U ||
        latency_selection->timing_is_noncanonical != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_selection, 0, sizeof(*out_selection));
    out_selection->struct_size = (uint32_t)sizeof(*out_selection);
    out_selection->version = HHS_EXACT_PASS219_H36_GLOBAL_LATENCY_VERSION;
    out_selection->requested_tier = requested_tier;
    out_selection->stack_selection = *stack_selection;
    out_selection->latency_selection = *latency_selection;
    out_selection->global_latency_policy_required = 1U;
    out_selection->exact_selector_parity = 1U;
    out_selection->complete_fallback_preserved = 1U;
    out_selection->budget_decision_explicit = 1U;
    out_selection->required_computation_preserved = 1U;
    out_selection->candidate_only = 1U;
    out_selection->canonical_authority = 0U;
    out_selection->timing_is_noncanonical = 1U;

    return hhs_exact_pass219_h36_global_latency_selection_validate(out_selection);
}

HHSExactStatus hhs_exact_pass219_h36_global_latency_select_prevalidated(
    const HHSExactPass219H36StackSelectionV1 *selection,
    uint32_t requested_tier,
    HHSExactPass219H36GlobalLatencySelectionV1 *out_selection
) {
    HHSExactPass219LatencyRouteV1 route;
    HHSExactPass219LatencySelectionV1 latency_selection;
    HHSExactStatus status;

    if (selection == NULL || out_selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_global_latency_policy_validate();
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_h36_stack_selection_validate(selection);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    h36_global_latency_route_from_selection(selection, &route);
    status = hhs_exact_pass219_global_latency_select_route(
        &route,
        1U,
        requested_tier,
        &latency_selection);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return h36_global_latency_finish(
        selection,
        &latency_selection,
        requested_tier,
        out_selection);
}

HHSExactStatus hhs_exact_pass219_h36_global_latency_select_cached(
    const HHSExactPass219H36StackCacheV1 *cache,
    uint64_t workload_signature36,
    uint64_t semantic_result_signature64,
    const char vector_key216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    uint32_t requested_tier,
    HHSExactPass219H36GlobalLatencySelectionV1 *out_selection,
    HHSExactPass219H36StackCacheReceiptV1 *out_cache_receipt
) {
    HHSExactPass219H36StackSelectionV1 cached;
    HHSExactStatus status;

    if (cache == NULL || vector_key216 == NULL || out_selection == NULL ||
        out_cache_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_h36_stack_cache_lookup(
        cache,
        workload_signature36,
        semantic_result_signature64,
        vector_key216,
        &cached,
        out_cache_receipt);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (out_cache_receipt->cache_hit != 1U ||
        out_cache_receipt->selection_integrity_validated != 1U ||
        out_cache_receipt->exact_replayable != 1U ||
        out_cache_receipt->canonical_mutation_authority != 0U ||
        out_cache_receipt->canonical_hash72_authority != 0U ||
        out_cache_receipt->canonical_hash216_authority != 0U ||
        out_cache_receipt->canonical_persistence_authority != 0U ||
        out_cache_receipt->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_h36_stack_cache_receipt_validate(
        cache, out_cache_receipt);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return hhs_exact_pass219_h36_global_latency_select_prevalidated(
        &cached,
        requested_tier,
        out_selection);
}

HHSExactStatus hhs_exact_pass219_h36_global_latency_select_branch_ref(
    HHSExactPass219H36BranchReferenceCacheV1 *branch_cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t branch_id,
    uint8_t target_lane_role,
    uint32_t requested_tier,
    HHSExactPass219H36GlobalLatencySelectionV1 *out_selection,
    HHSExactPass219H36BranchReceiptV1 *out_branch_receipt,
    HHSExactPass219H36CompositionReceiptMemoV1 *out_composition_receipt
) {
    const HHSExactPass219H36StackSelectionV1 *parent_selection = NULL;
    HHSExactStatus status;

    if (branch_cache == NULL || frozen_parent_cache == NULL ||
        out_selection == NULL || out_branch_receipt == NULL ||
        out_composition_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (target_lane_role >= HHS_EXACT_PASS219_H36_BRANCH_REF_LANES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    status = hhs_exact_pass219_h36_branch_ref_resolve(
        branch_cache,
        frozen_parent_cache,
        branch_id,
        &parent_selection,
        out_branch_receipt);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (parent_selection == NULL ||
        out_branch_receipt->frozen_parent_validated != 1U ||
        out_branch_receipt->exact_replayable != 1U ||
        out_branch_receipt->branch_reference_only != 1U ||
        out_branch_receipt->canonical_mutation_authority != 0U ||
        out_branch_receipt->canonical_hash72_authority != 0U ||
        out_branch_receipt->canonical_hash216_authority != 0U ||
        out_branch_receipt->canonical_persistence_authority != 0U ||
        out_branch_receipt->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_h36_branch_ref_receipt_validate(
        branch_cache,
        frozen_parent_cache,
        out_branch_receipt);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_h36_branch_ref_composition_receipt(
        branch_cache,
        frozen_parent_cache,
        branch_id,
        target_lane_role,
        out_composition_receipt);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_h36_branch_ref_composition_receipt_validate(
        branch_cache,
        frozen_parent_cache,
        out_composition_receipt);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (out_composition_receipt->exact_replayable != 1U ||
        out_composition_receipt->canonical_mutation_authority != 0U ||
        out_composition_receipt->canonical_hash72_authority != 0U ||
        out_composition_receipt->canonical_hash216_authority != 0U ||
        out_composition_receipt->canonical_persistence_authority != 0U ||
        out_composition_receipt->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return hhs_exact_pass219_h36_global_latency_select_prevalidated(
        parent_selection,
        requested_tier,
        out_selection);
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

    status = hhs_exact_pass219_h36_stack_select(first, second, &stack_selection);
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

    return h36_global_latency_finish(
        &stack_selection,
        &latency_selection,
        requested_tier,
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
