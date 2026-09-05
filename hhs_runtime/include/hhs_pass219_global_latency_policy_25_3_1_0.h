#ifndef HHS_PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0_H
#define HHS_PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_GLOBAL_LATENCY_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_GLOBAL_LATENCY_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_GLOBAL_LATENCY_VERSION_PATCH 0U

#define HHS_EXACT_PASS219_LATENCY_A2 1U
#define HHS_EXACT_PASS219_LATENCY_B2 2U
#define HHS_EXACT_PASS219_LATENCY_C2 3U
#define HHS_EXACT_PASS219_LATENCY_D2 5U

#define HHS_EXACT_PASS219_LATENCY_MEAN_RATIO_NUMERATOR_MS 25U
#define HHS_EXACT_PASS219_LATENCY_MEAN_RATIO_DENOMINATOR_MS 3U

#define HHS_EXACT_PASS219_LATENCY_BASE_NUMERATOR_NS UINT64_C(25000000)
#define HHS_EXACT_PASS219_LATENCY_BASE_DENOMINATOR_NS UINT64_C(3)

#define HHS_EXACT_PASS219_LATENCY_TIER1_MULTIPLIER 1U
#define HHS_EXACT_PASS219_LATENCY_TIER2_MULTIPLIER 2U
#define HHS_EXACT_PASS219_LATENCY_TIER3_MULTIPLIER 4U

#define HHS_EXACT_PASS219_LATENCY_TIER1_FPS 120U
#define HHS_EXACT_PASS219_LATENCY_TIER2_FPS 60U
#define HHS_EXACT_PASS219_LATENCY_TIER3_FPS 30U

#define HHS_EXACT_PASS219_LATENCY_WINDOW_MAX_SAMPLES 64U
#define HHS_EXACT_PASS219_LATENCY_MAX_ROUTES 32U

typedef enum HHSExactPass219LatencyTierV1 {
    HHS_EXACT_PASS219_LATENCY_TIER_INVALID = 0,
    HHS_EXACT_PASS219_LATENCY_TIER1_120FPS = 1,
    HHS_EXACT_PASS219_LATENCY_TIER2_60FPS = 2,
    HHS_EXACT_PASS219_LATENCY_TIER3_30FPS = 3,
    HHS_EXACT_PASS219_LATENCY_TIER_OVER_BUDGET = 4
} HHSExactPass219LatencyTierV1;

typedef enum HHSExactPass219LatencyDecisionV1 {
    HHS_EXACT_PASS219_LATENCY_DECISION_INVALID = 0,
    HHS_EXACT_PASS219_LATENCY_DECISION_BUDGET_MET = 1,
    HHS_EXACT_PASS219_LATENCY_DECISION_BUDGET_UNMET = 2
} HHSExactPass219LatencyDecisionV1;

typedef struct HHSExactPass219GlobalLatencyPolicyV1 {
    uint32_t struct_size;
    uint32_t version;

    uint32_t a2;
    uint32_t b2;
    uint32_t c2;
    uint32_t d2;

    uint32_t mean_ratio_numerator_ms;
    uint32_t mean_ratio_denominator_ms;

    uint64_t base_numerator_ns;
    uint64_t base_denominator_ns;

    uint32_t tier1_multiplier;
    uint32_t tier2_multiplier;
    uint32_t tier3_multiplier;

    uint32_t tier1_fps;
    uint32_t tier2_fps;
    uint32_t tier3_fps;

    uint8_t exact_integer_classification_required;
    uint8_t timing_is_noncanonical;
    uint8_t semantic_equality_required_before_route_selection;
    uint8_t complete_path_preserved_if_budget_unmet;
    uint8_t singleton_vm81_authority_preserved;
    uint8_t hash72_hash216_authority_preserved;
    uint8_t candidate_acceleration_only;
    uint8_t global_promotion_requires_measured_benefit;
} HHSExactPass219GlobalLatencyPolicyV1;

typedef struct HHSExactPass219LatencyWindowInputV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t sample_count;
    uint32_t reserved0;
    uint64_t samples_ns[HHS_EXACT_PASS219_LATENCY_WINDOW_MAX_SAMPLES];
} HHSExactPass219LatencyWindowInputV1;

typedef struct HHSExactPass219LatencyWindowResultV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t sample_count;
    uint32_t p95_nearest_rank;

    uint64_t sum_ns;
    uint64_t mean_numerator_ns;
    uint64_t mean_denominator;
    uint64_t p95_ns;
    uint64_t max_ns;

    uint32_t mean_tier;
    uint32_t p95_tier;
    uint32_t max_tier;

    uint8_t mean_within_tier1;
    uint8_t p95_within_tier2;
    uint8_t max_within_tier3;
    uint8_t window_policy_met;
    uint8_t timing_is_noncanonical;
    uint8_t reserved1[3];
} HHSExactPass219LatencyWindowResultV1;

typedef struct HHSExactPass219LatencyRouteV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t route_id;
    uint32_t reserved0;

    uint64_t observed_ns;
    uint64_t work_units;

    uint8_t exact_semantic_equal;
    uint8_t exact_selector_proven;
    uint8_t complete_fallback;
    uint8_t candidate_only;
    uint8_t canonical_authority_requested;
    uint8_t reserved1[3];
} HHSExactPass219LatencyRouteV1;

typedef struct HHSExactPass219LatencySelectionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t requested_tier;
    uint32_t selected_route_id;
    uint32_t selected_tier;
    uint32_t decision;

    uint64_t selected_observed_ns;
    uint64_t selected_work_units;

    uint8_t exact_semantic_equal_required;
    uint8_t complete_fallback_present;
    uint8_t budget_met;
    uint8_t canonical_authority;
    uint8_t timing_is_noncanonical;
    uint8_t reserved0[3];
} HHSExactPass219LatencySelectionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_global_latency_policy_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_latency_policy(
    HHSExactPass219GlobalLatencyPolicyV1 *out_policy
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_latency_policy_validate(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_latency_classify_ns(
    uint64_t observed_ns,
    uint32_t *out_tier
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_latency_window_evaluate(
    const HHSExactPass219LatencyWindowInputV1 *input,
    HHSExactPass219LatencyWindowResultV1 *out_result
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_latency_select_route(
    const HHSExactPass219LatencyRouteV1 *routes,
    size_t route_count,
    uint32_t requested_tier,
    HHSExactPass219LatencySelectionV1 *out_selection
);

#ifdef __cplusplus
}
#endif

#endif
