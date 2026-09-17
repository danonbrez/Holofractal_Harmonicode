#ifndef HHS_PASS219_HARMONIC36_GLOBAL_LATENCY_POLICY_1_16_H
#define HHS_PASS219_HARMONIC36_GLOBAL_LATENCY_POLICY_1_16_H

#include "hhs_pass219_harmonic36_branch_reference_cache_1_17.h"
#include "hhs_pass219_global_latency_policy_25_3_1_0.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_GLOBAL_LATENCY_VERSION UINT32_C(0x00010010)

typedef struct HHSExactPass219H36GlobalLatencySelectionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t requested_tier;
    uint32_t reserved0;

    HHSExactPass219H36StackSelectionV1 stack_selection;
    HHSExactPass219LatencySelectionV1 latency_selection;

    uint8_t global_latency_policy_required;
    uint8_t exact_selector_parity;
    uint8_t complete_fallback_preserved;
    uint8_t budget_decision_explicit;
    uint8_t required_computation_preserved;
    uint8_t candidate_only;
    uint8_t canonical_authority;
    uint8_t timing_is_noncanonical;
} HHSExactPass219H36GlobalLatencySelectionV1;

HHS_EXACT_API uint32_t
hhs_exact_pass219_h36_global_latency_policy_version(void);

/* Existing fresh-selection compatibility surface. */
HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_global_latency_select(
    const HHSExactPass219H36StackCandidateEvidenceV1 *first,
    const HHSExactPass219H36StackCandidateEvidenceV1 *second,
    uint32_t requested_tier,
    HHSExactPass219H36GlobalLatencySelectionV1 *out_selection);

/*
 * Mandatory optimized surfaces. A selection that has already passed the exact
 * stack-selector membrane must not be recomputed merely to enter the latency
 * policy. Cached and branch-reference variants prove their own replay receipts
 * before delegating to the prevalidated selector below.
 */
HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_global_latency_select_prevalidated(
    const HHSExactPass219H36StackSelectionV1 *selection,
    uint32_t requested_tier,
    HHSExactPass219H36GlobalLatencySelectionV1 *out_selection);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_global_latency_select_cached(
    const HHSExactPass219H36StackCacheV1 *cache,
    uint64_t workload_signature36,
    uint64_t semantic_result_signature64,
    const char vector_key216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    uint32_t requested_tier,
    HHSExactPass219H36GlobalLatencySelectionV1 *out_selection,
    HHSExactPass219H36StackCacheReceiptV1 *out_cache_receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_global_latency_select_branch_ref(
    HHSExactPass219H36BranchReferenceCacheV1 *branch_cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t branch_id,
    uint8_t target_lane_role,
    uint32_t requested_tier,
    HHSExactPass219H36GlobalLatencySelectionV1 *out_selection,
    HHSExactPass219H36BranchReceiptV1 *out_branch_receipt,
    HHSExactPass219H36CompositionReceiptMemoV1 *out_composition_receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_global_latency_selection_validate(
    const HHSExactPass219H36GlobalLatencySelectionV1 *selection);

#ifdef __cplusplus
}
#endif

#endif
