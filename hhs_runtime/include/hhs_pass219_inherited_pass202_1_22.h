#ifndef HHS_PASS219_INHERITED_PASS202_1_22_H
#define HHS_PASS219_INHERITED_PASS202_1_22_H

#include "hhs_pass219_inherited_pass203_1_21.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS202_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS202_VERSION_MINOR 22U
#define HHS_EXACT_PASS219_INHERITED_PASS202_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS202_NUMBER 202U
#define HHS_EXACT_PASS202_PRIMARY_PR 143U
#define HHS_EXACT_PASS202_BOOTSTRAP_PR 144U
#define HHS_EXACT_PASS202_INITIAL_CONTRACT_TEST_COUNT 5U
#define HHS_EXACT_PASS202_BOOTSTRAP_CONTRACT_TEST_COUNT 6U
#define HHS_EXACT_PASS202_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS202_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass202GuardedDeploymentWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t primary_pull_request;
    uint32_t bootstrap_pull_request;
    uint32_t initial_contract_test_count;
    uint32_t bootstrap_contract_test_count;
    uint32_t main_only_production_source;
    uint32_t trusted_label_author_gate;
    uint32_t same_repository_pull_request_required;
    uint32_t detached_candidate_validation;
    uint32_t fast_forward_only_promotion;
    uint32_t post_promotion_health_required;
    uint32_t rollback_to_exact_previous_commit;
    uint32_t durable_jsonl_receipts;
    uint32_t bounded_singleton_timer;
    uint32_t host_local_drift_blocked_historically;
    uint32_t bootstrap_dry_run_required;
    uint32_t explicit_operator_enable_required;
    uint32_t guarded_ci_blob_preserved;
    uint32_t service_timer_blobs_preserved;
    uint32_t successor_hardening_verified;
    uint32_t host_drift_preservation_verified;
    uint32_t runtime_os_bundle_sha_bound;
    uint32_t prebuilt_bundle_required_for_production;
    uint32_t install_promotion_default_disabled;
    uint32_t recovery_receipt_gated;
    uint32_t pass203_successor_preserved;
    uint32_t pass219_new_deployment_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char primary_base_commit[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char primary_head_commit[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char primary_merge_commit[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char bootstrap_head_commit[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char bootstrap_merge_commit[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char historical_guarded_ci_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char historical_updater_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char historical_env_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char historical_installer_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char historical_service_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char historical_timer_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char historical_validator_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char historical_contract_test_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char frozen_i121_commit[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char current_updater_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char current_env_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char current_installer_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char current_validator_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char current_runtime_os_bundle_blob[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
} HHSExactPass202GuardedDeploymentWitnessV1;

typedef struct HHSExactPass219InheritedPass202BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t historical_guarded_ci_bound;
    uint32_t dry_run_bootstrap_bound;
    uint32_t deployment_transition_bound;
    uint32_t exact_rollback_bound;
    uint32_t durable_receipt_boundary_bound;
    uint32_t successor_hardening_bound;
    uint32_t host_drift_preservation_bound;
    uint32_t runtime_os_bundle_boundary_bound;
    uint32_t pass203_successor_bound;
    uint32_t no_new_deployment_authority_bound;
    uint32_t no_new_canonical_mutation_authority_bound;
    uint32_t no_new_persistence_authority_bound;
    uint32_t no_new_hash72_clock_bound;
    uint32_t pass219_new_deployment_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char bootstrap_merge_commit[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
    char frozen_i121_commit[HHS_EXACT_PASS202_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass202BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass202_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass202_guarded_deployment(
    const HHSExactPass202GuardedDeploymentWitnessV1 *witness,
    HHSExactPass219InheritedPass202BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
