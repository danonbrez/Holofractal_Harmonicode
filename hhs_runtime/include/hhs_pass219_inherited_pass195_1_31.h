#ifndef HHS_PASS219_INHERITED_PASS195_1_31_H
#define HHS_PASS219_INHERITED_PASS195_1_31_H

#include "hhs_pass219_inherited_pass196_1_30.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS195_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS195_VERSION_MINOR 31U
#define HHS_EXACT_PASS219_INHERITED_PASS195_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS195_NUMBER 195U
#define HHS_EXACT_PASS195_PRIMARY_PR 117U
#define HHS_EXACT_PASS195_REVIEW_FINDING_COUNT 12U
#define HHS_EXACT_PASS195_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS195_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass195RepairedKimiK3ContentEngineWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t primary_pull_request;
    uint32_t review_finding_count;
    uint32_t provider_plan_schema_validation;
    uint32_t input_content_receipt_binding;
    uint32_t frontend_ingress_rejection;
    uint32_t model_identity_bound_before_plan_hash;
    uint32_t template_before_style_overrides;
    uint32_t operator_authorization_and_throttle;
    uint32_t bounded_constraint_prompt;
    uint32_t storybook_handoff_bounds;
    uint32_t storybook_style_range_alignment;
    uint32_t image_analysis_capability_admission;
    uint32_t authorized_tick_graph_binding;
    uint32_t final_health_hash_binding;
    uint32_t historical_v1_preserved;
    uint32_t pass196_successor_preserved;
    uint32_t external_provider_is_canonical_authority;
    uint32_t browser_handoff_is_canonical_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char accepted_primary_merge[HHS_EXACT_PASS195_GIT_SHA_STRLEN];
    char frozen_i130_commit[HHS_EXACT_PASS195_GIT_SHA_STRLEN];
    char historical_v1_blob[HHS_EXACT_PASS195_GIT_SHA_STRLEN];
    char repaired_v2_blob[HHS_EXACT_PASS195_GIT_SHA_STRLEN];
    char repaired_api_blob[HHS_EXACT_PASS195_GIT_SHA_STRLEN];
    char repaired_frontend_blob[HHS_EXACT_PASS195_GIT_SHA_STRLEN];
    char repair_regression_blob[HHS_EXACT_PASS195_GIT_SHA_STRLEN];
    char repair_workflow_blob[HHS_EXACT_PASS195_GIT_SHA_STRLEN];
} HHSExactPass195RepairedKimiK3ContentEngineWitnessV1;

typedef struct HHSExactPass219InheritedPass195BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t inherited_findings_repaired;
    uint32_t strict_provider_plan_bound;
    uint32_t exact_input_receipt_bound;
    uint32_t governed_frontend_ingress_bound;
    uint32_t model_provenance_bound;
    uint32_t storybook_handoff_bound;
    uint32_t paid_route_authorization_bound;
    uint32_t multimodal_capability_bound;
    uint32_t exact_tick_graph_bound;
    uint32_t final_health_identity_bound;
    uint32_t pass196_successor_bound;
    uint32_t no_new_authority_bound;
    uint32_t external_provider_is_canonical_authority;
    uint32_t browser_handoff_is_canonical_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char accepted_primary_merge[HHS_EXACT_PASS195_GIT_SHA_STRLEN];
    char frozen_i130_commit[HHS_EXACT_PASS195_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass195BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass195_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass195_repaired_kimi_k3_content_engine(
    const HHSExactPass195RepairedKimiK3ContentEngineWitnessV1 *witness,
    HHSExactPass219InheritedPass195BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
