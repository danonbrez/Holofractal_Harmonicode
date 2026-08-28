#ifndef HHS_PASS219_INHERITED_PASS200A_1_26_H
#define HHS_PASS219_INHERITED_PASS200A_1_26_H

#include "hhs_pass219_inherited_pass200b_1_25.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS200A_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS200A_VERSION_MINOR 26U
#define HHS_EXACT_PASS219_INHERITED_PASS200A_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS200A_NUMBER 200U
#define HHS_EXACT_PASS219_INHERITED_PASS200A_VARIANT 1U
#define HHS_EXACT_PASS200A_PRIMARY_PR 138U
#define HHS_EXACT_PASS200A_PRODUCTION_ENVELOPES 4U
#define HHS_EXACT_PASS200A_PRODUCTION_STATES 290U
#define HHS_EXACT_PASS200A_PRODUCTION_BRANCH_JOBS 580U
#define HHS_EXACT_PASS200A_PRODUCTION_ADMITTED 263U
#define HHS_EXACT_PASS200A_PRODUCTION_REJECTED 27U
#define HHS_EXACT_PASS200A_PRODUCTION_VM5184_COMPARISONS 1363392U
#define HHS_EXACT_PASS200A_NEGATIVE_MUTATIONS 24U
#define HHS_EXACT_PASS200A_BUNDLES 4U
#define HHS_EXACT_PASS200A_SHADOW_MATCHES 4U
#define HHS_EXACT_PASS200A_REFERENCE_RETURNS 4U
#define HHS_EXACT_PASS200A_CANDIDATE_ACTIVATIONS 0U
#define HHS_EXACT_PASS200A_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS200A_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass200ARepairedShadowWitnessV2 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t primary_pull_request;
    uint32_t production_envelopes;
    uint32_t production_states;
    uint32_t production_branch_jobs;
    uint32_t production_admitted;
    uint32_t production_rejected;
    uint32_t production_vm5184_comparisons;
    uint32_t negative_mutations;
    uint32_t optimization_bundles;
    uint32_t shadow_matches;
    uint32_t reference_returns;
    uint32_t candidate_activations;
    uint32_t vm81_receipt_chain_provenance_required;
    uint32_t reference_lane_independently_executed;
    uint32_t candidate_lane_independently_executed;
    uint32_t exact_semantic_comparison_required;
    uint32_t exact_witness_comparison_required;
    uint32_t exact_replay_comparison_required;
    uint32_t shadow_payload_hash_revalidated;
    uint32_t shadow_event_payload_binding_required;
    uint32_t current_pass198_proof_required;
    uint32_t revoked_pass198_proof_rejected;
    uint32_t production_profile_identity_required;
    uint32_t production_acceptance_totals_required;
    uint32_t singleton_upgraded_in_place;
    uint32_t duplicate_default_authority_forbidden;
    uint32_t partial_holdout_state_recoverable;
    uint32_t reference_result_remains_authoritative;
    uint32_t candidate_may_commit;
    uint32_t candidate_may_activate;
    uint32_t compiler_auto_activation;
    uint32_t runtime_auto_admission;
    uint32_t canary_enabled;
    uint32_t active_enabled;
    uint32_t frozen_constraint_enabled;
    uint32_t pass200b_successor_preserved;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char historical_base_commit[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
    char historical_reviewed_head[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
    char accepted_merge_commit[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
    char frozen_i125_commit[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
    char contract_blob[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
    char runtime_v1_blob[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
    char historical_production_blob[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
    char historical_workflow_blob[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
    char historical_routes_blob[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
    char historical_test_blob[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
    char historical_restart_blob[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
} HHSExactPass200ARepairedShadowWitnessV2;

typedef struct HHSExactPass219InheritedPass200ABindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t pass_variant;
    uint32_t classification;
    uint32_t historical_squash_identity_bound;
    uint32_t inherited_defects_repaired;
    uint32_t vm81_receipt_provenance_bound;
    uint32_t independent_shadow_execution_bound;
    uint32_t persisted_shadow_integrity_bound;
    uint32_t live_pass198_proof_bound;
    uint32_t production_acceptance_bound;
    uint32_t singleton_identity_bound;
    uint32_t partial_restartability_bound;
    uint32_t pass200b_successor_bound;
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
    char accepted_merge_commit[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
    char frozen_i125_commit[HHS_EXACT_PASS200A_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass200ABindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass200a_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass200a_repaired_shadow_authority(
    const HHSExactPass200ARepairedShadowWitnessV2 *witness,
    HHSExactPass219InheritedPass200ABindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
