#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static void prepare_pair(
    uint64_t h36_ns,
    uint64_t linux_ns,
    HHSExactPass219H36StackCandidateEvidenceV1 *h36,
    HHSExactPass219H36StackCandidateEvidenceV1 *linux
) {
    const uint64_t workload36 = UINT64_C(012345670123);
    const uint64_t result64 = UINT64_C(0xA55A123456789ABC);

    assert(hhs_exact_pass219_h36_stack_candidate_prepare(
        1U,
        HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
        workload36,
        result64,
        h36_ns,
        9U,
        32U,
        4096U,
        14U,
        1U,
        h36
    ) == HHS_EXACT_STATUS_OK);

    assert(hhs_exact_pass219_h36_stack_candidate_prepare(
        2U,
        HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
        workload36,
        result64,
        linux_ns,
        9U,
        32U,
        2048U,
        20U,
        1U,
        linux
    ) == HHS_EXACT_STATUS_OK);
}

int main(void) {
    HHSExactPass219H36StackCandidateEvidenceV1 h36;
    HHSExactPass219H36StackCandidateEvidenceV1 linux;
    HHSExactPass219H36StackCandidateEvidenceV1 bad;
    HHSExactPass219H36GlobalLatencySelectionV1 selected;

    assert(hhs_exact_pass219_h36_global_latency_policy_version() ==
           HHS_EXACT_PASS219_H36_GLOBAL_LATENCY_VERSION);

    prepare_pair(UINT64_C(1000000), UINT64_C(2000000), &h36, &linux);

    assert(hhs_exact_pass219_h36_global_latency_select(
        &h36,
        &linux,
        HHS_EXACT_PASS219_LATENCY_TIER1_120FPS,
        &selected
    ) == HHS_EXACT_STATUS_OK);

    assert(selected.stack_selection.selected_candidate_id == 1U);
    assert(selected.latency_selection.selected_route_id == 1U);
    assert(selected.latency_selection.selected_tier ==
           HHS_EXACT_PASS219_LATENCY_TIER1_120FPS);
    assert(selected.latency_selection.decision ==
           HHS_EXACT_PASS219_LATENCY_DECISION_BUDGET_MET);
    assert(selected.latency_selection.budget_met == 1U);
    assert(selected.exact_selector_parity == 1U);
    assert(selected.complete_fallback_preserved == 1U);
    assert(selected.required_computation_preserved == 1U);
    assert(selected.canonical_authority == 0U);

    /*
     * 10 ms and 12 ms are both outside Tier 1 but within Tier 2.
     * The exact H36 winner is preserved and the budget failure is explicit;
     * required computation is not discarded.
     */
    prepare_pair(UINT64_C(10000000), UINT64_C(12000000), &h36, &linux);

    assert(hhs_exact_pass219_h36_global_latency_select(
        &h36,
        &linux,
        HHS_EXACT_PASS219_LATENCY_TIER1_120FPS,
        &selected
    ) == HHS_EXACT_STATUS_OK);

    assert(selected.stack_selection.selected_candidate_id == 1U);
    assert(selected.latency_selection.selected_route_id == 1U);
    assert(selected.latency_selection.selected_tier ==
           HHS_EXACT_PASS219_LATENCY_TIER2_60FPS);
    assert(selected.latency_selection.decision ==
           HHS_EXACT_PASS219_LATENCY_DECISION_BUDGET_UNMET);
    assert(selected.latency_selection.budget_met == 0U);
    assert(selected.complete_fallback_preserved == 1U);
    assert(selected.required_computation_preserved == 1U);
    assert(selected.canonical_authority == 0U);

    bad = linux;
    bad.semantic_result_signature64 ^= UINT64_C(1);
    assert(hhs_exact_pass219_h36_global_latency_select(
        &h36,
        &bad,
        HHS_EXACT_PASS219_LATENCY_TIER1_120FPS,
        &selected
    ) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad = linux;
    bad.exact_result_equal = 0U;
    assert(hhs_exact_pass219_h36_global_latency_select(
        &h36,
        &bad,
        HHS_EXACT_PASS219_LATENCY_TIER1_120FPS,
        &selected
    ) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(hhs_exact_pass219_h36_global_latency_select(
        &h36,
        &linux,
        HHS_EXACT_PASS219_LATENCY_TIER_INVALID,
        &selected
    ) == HHS_EXACT_STATUS_RANGE_ERROR);

    return 0;
}
