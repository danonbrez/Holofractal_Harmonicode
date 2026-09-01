#ifndef HHS_PASS219_HARMONIC36_GLOBAL_LATENCY_POLICY_1_16_H
#define HHS_PASS219_HARMONIC36_GLOBAL_LATENCY_POLICY_1_16_H

#include "hhs_pass219_harmonic36_stack_selection_1_10.h"
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

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_global_latency_select(
    const HHSExactPass219H36StackCandidateEvidenceV1 *first,
    const HHSExactPass219H36StackCandidateEvidenceV1 *second,
    uint32_t requested_tier,
    HHSExactPass219H36GlobalLatencySelectionV1 *out_selection);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_global_latency_selection_validate(
    const HHSExactPass219H36GlobalLatencySelectionV1 *selection);

#ifdef __cplusplus
}
#endif

#endif
