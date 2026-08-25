#ifndef HHS_PASS219_INHERITED_PASS197_1_29_H
#define HHS_PASS219_INHERITED_PASS197_1_29_H

#include "hhs_pass219_inherited_pass198_1_28.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS197_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS197_VERSION_MINOR 29U
#define HHS_EXACT_PASS219_INHERITED_PASS197_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS197_NUMBER 197U
#define HHS_EXACT_PASS197_PRIMARY_PR 133U
#define HHS_EXACT_PASS197_REVIEW_FINDING_COUNT 10U
#define HHS_EXACT_PASS197_DEFAULT_STATES 405U
#define HHS_EXACT_PASS197_DEFAULT_ADMITTED 320U
#define HHS_EXACT_PASS197_DEFAULT_REJECTED 85U
#define HHS_EXACT_PASS197_VM5184_COMPARISONS 1658880U
#define HHS_EXACT_PASS197_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS197_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass197RepairedHydrationCalibrationWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t primary_pull_request;
    uint32_t review_finding_count;
    uint32_t default_parameter_states;
    uint32_t default_admitted_states;
    uint32_t default_rejected_states;
    uint32_t vm5184_address_comparisons;
    uint32_t pre_persistence_kernel_audit_required;
    uint32_t fail_closed_hash72_authority;
    uint32_t full_replay_required_for_closure;
    uint32_t strict_rational_object_components;
    uint32_t state_root_run_serialization;
    uint32_t persisted_report_integrity_status_gate;
    uint32_t bounded_synchronous_envelope;
    uint32_t strict_exponent_ingress;
    uint32_t duplicate_coordinate_rejection;
    uint32_t closed_only_frontend_projection;
    uint32_t pass198_successor_preserved;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char historical_base_commit[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
    char historical_reviewed_head[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
    char accepted_merge_commit[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
    char frozen_i128_commit[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
    char repaired_exact_blob[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
    char repaired_state_blob[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
    char repaired_runtime_blob[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
    char repaired_api_blob[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
    char repaired_frontend_blob[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
    char repaired_regression_blob[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
    char repaired_workflow_blob[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
} HHSExactPass197RepairedHydrationCalibrationWitnessV1;

typedef struct HHSExactPass219InheritedPass197BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t historical_squash_identity_bound;
    uint32_t inherited_defects_repaired;
    uint32_t exact_ingress_bound;
    uint32_t pre_persistence_kernel_audit_bound;
    uint32_t full_replay_closure_bound;
    uint32_t state_root_serialization_bound;
    uint32_t verified_status_bound;
    uint32_t synchronous_envelope_bound;
    uint32_t frontend_projection_bound;
    uint32_t pass198_successor_bound;
    uint32_t no_new_candidate_authority_bound;
    uint32_t no_new_canonical_mutation_authority_bound;
    uint32_t no_new_persistence_authority_bound;
    uint32_t no_new_hash72_clock_bound;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char accepted_merge_commit[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
    char frozen_i128_commit[HHS_EXACT_PASS197_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass197BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass197_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass197_repaired_hydration_calibration(
    const HHSExactPass197RepairedHydrationCalibrationWitnessV1 *witness,
    HHSExactPass219InheritedPass197BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
