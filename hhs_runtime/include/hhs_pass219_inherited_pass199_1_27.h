#ifndef HHS_PASS219_INHERITED_PASS199_1_27_H
#define HHS_PASS219_INHERITED_PASS199_1_27_H

#include "hhs_pass219_inherited_pass200a_1_26.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS199_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS199_VERSION_MINOR 27U
#define HHS_EXACT_PASS219_INHERITED_PASS199_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS199_NUMBER 199U
#define HHS_EXACT_PASS199_PRIMARY_PR 137U
#define HHS_EXACT_PASS199_PRODUCTION_STATES 405U
#define HHS_EXACT_PASS199_PRODUCTION_BRANCH_JOBS 810U
#define HHS_EXACT_PASS199_PRODUCTION_ADMITTED 320U
#define HHS_EXACT_PASS199_PRODUCTION_REJECTED 85U
#define HHS_EXACT_PASS199_PRODUCTION_VM5184_COMPARISONS 1658880U
#define HHS_EXACT_PASS199_REPLAY_BRANCH_JOBS 810U
#define HHS_EXACT_PASS199_SINGLETON_COMMIT_COUNT 1U
#define HHS_EXACT_PASS199_PASS198_VERIFICATION_COUNT 1U
#define HHS_EXACT_PASS199_MAX_CLAIM_BATCH_SIZE 64U
#define HHS_EXACT_PASS199_REVIEW_FINDING_COUNT 6U
#define HHS_EXACT_PASS199_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS199_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass199RepairedCalibrationWitnessV3 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t primary_pull_request;
    uint32_t production_states;
    uint32_t production_branch_jobs;
    uint32_t production_admitted;
    uint32_t production_rejected;
    uint32_t production_vm5184_comparisons;
    uint32_t replayed_branch_jobs;
    uint32_t singleton_commit_count;
    uint32_t pass198_verification_count;
    uint32_t max_claim_batch_size;
    uint32_t review_finding_count;
    uint32_t full_replay_required;
    uint32_t full_replay_executed;
    uint32_t deterministic_replay_required;
    uint32_t pass198_single_verification_required;
    uint32_t report_identity_excludes_pass198_attachment;
    uint32_t existing_commit_receipt_continuity_required;
    uint32_t stale_worker_recovery_before_slot_validation;
    uint32_t durable_completion_total_reconciled;
    uint32_t canonical_gate_payload_diversity_required;
    uint32_t pass200a_successor_preserved;
    uint32_t candidate_worker_is_authority;
    uint32_t candidate_may_commit;
    uint32_t pass198_mutation_authority;
    uint32_t api_mutation_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char historical_base_commit[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char historical_reviewed_head[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char accepted_merge_commit[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char frozen_i126_commit[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char validated_repair_head[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char contract_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char fabric_v1_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char runtime_v1_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char runtime_v2_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char historical_production_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char historical_workflow_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char historical_routes_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char historical_fabric_test_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char historical_production_test_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char historical_restart_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char repaired_runtime_v3_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char repaired_production_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char repaired_workflow_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char repaired_regression_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char repaired_projection_test_blob[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
} HHSExactPass199RepairedCalibrationWitnessV3;

typedef struct HHSExactPass219InheritedPass199BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t historical_squash_identity_bound;
    uint32_t inherited_defects_repaired;
    uint32_t production_totals_bound;
    uint32_t full_replay_bound;
    uint32_t single_pass198_verification_bound;
    uint32_t report_identity_compatibility_bound;
    uint32_t commit_receipt_continuity_bound;
    uint32_t stale_worker_recovery_bound;
    uint32_t durable_completion_bound;
    uint32_t canonical_gate_diversity_bound;
    uint32_t pass200a_successor_bound;
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
    char accepted_merge_commit[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char frozen_i126_commit[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
    char validated_repair_head[HHS_EXACT_PASS199_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass199BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass199_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass199_repaired_calibration_authority(
    const HHSExactPass199RepairedCalibrationWitnessV3 *witness,
    HHSExactPass219InheritedPass199BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
