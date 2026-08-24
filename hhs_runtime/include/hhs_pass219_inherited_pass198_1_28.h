#ifndef HHS_PASS219_INHERITED_PASS198_1_28_H
#define HHS_PASS219_INHERITED_PASS198_1_28_H

#include "hhs_pass219_inherited_pass199_1_27.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS198_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS198_VERSION_MINOR 28U
#define HHS_EXACT_PASS219_INHERITED_PASS198_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS198_NUMBER 198U
#define HHS_EXACT_PASS198_PRIMARY_PR 136U
#define HHS_EXACT_PASS198_DEFAULT_STATES 405U
#define HHS_EXACT_PASS198_DEFAULT_ADMITTED 320U
#define HHS_EXACT_PASS198_DEFAULT_REJECTED 85U
#define HHS_EXACT_PASS198_VM5184_COMPARISONS 1658880U
#define HHS_EXACT_PASS198_SIMPLIFICATION_COUNT 4U
#define HHS_EXACT_PASS198_NEGATIVE_MUTATION_COUNT 6U
#define HHS_EXACT_PASS198_REVIEW_FINDING_COUNT 13U
#define HHS_EXACT_PASS198_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS198_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass198RepairedCalibrationRegistryWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t primary_pull_request;
    uint32_t default_parameter_states;
    uint32_t default_admitted_states;
    uint32_t default_rejected_states;
    uint32_t vm5184_address_comparisons;
    uint32_t simplification_count;
    uint32_t negative_mutation_count;
    uint32_t review_finding_count;
    uint32_t full_replay_required;
    uint32_t full_replay_executed;
    uint32_t nonzero_admitted_coverage_required;
    uint32_t exact_builtin_adapter_spec_binding_required;
    uint32_t registration_vm81_receipt_persisted;
    uint32_t recursive_float_identity_rejection;
    uint32_t atomic_builtin_registration;
    uint32_t normalized_persistent_identifier_updates;
    uint32_t transactional_promotion_state_recheck;
    uint32_t checkpoint_receipt_independent;
    uint32_t distinct_workload_promotion_required;
    uint32_t per_simplification_cost_unmeasured;
    uint32_t executed_negative_mutations_required;
    uint32_t executed_negative_mutation_count;
    uint32_t all_negative_mutations_detected;
    uint32_t pass199_successor_preserved;
    uint32_t compiler_auto_promotion;
    uint32_t runtime_auto_admission;
    uint32_t api_mutation_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char historical_base_commit[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char historical_reviewed_head[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char accepted_merge_commit[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char frozen_i127_commit[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char validated_repair_head[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char accepted_contract_blob[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char accepted_runtime_blob[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char accepted_api_blob[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char accepted_test_blob[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char accepted_workflow_blob[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char repaired_runtime_blob[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char repaired_api_blob[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char repaired_regression_blob[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char repaired_workflow_blob[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
} HHSExactPass198RepairedCalibrationRegistryWitnessV1;

typedef struct HHSExactPass219InheritedPass198BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t historical_squash_identity_bound;
    uint32_t inherited_defects_repaired;
    uint32_t production_totals_bound;
    uint32_t deterministic_replay_bound;
    uint32_t exact_adapter_binding_bound;
    uint32_t vm81_registration_receipt_bound;
    uint32_t exact_identity_rejection_bound;
    uint32_t transaction_and_restart_bound;
    uint32_t distinct_workload_promotion_bound;
    uint32_t unmeasured_cost_claim_bound;
    uint32_t executed_negative_mutation_bound;
    uint32_t pass199_successor_bound;
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
    char accepted_merge_commit[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char frozen_i127_commit[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
    char validated_repair_head[HHS_EXACT_PASS198_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass198BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass198_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass198_repaired_calibration_registry(
    const HHSExactPass198RepairedCalibrationRegistryWitnessV1 *witness,
    HHSExactPass219InheritedPass198BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
