#ifndef HHS_PASS219_INHERITED_PASS200B_1_25_H
#define HHS_PASS219_INHERITED_PASS200B_1_25_H

#include "hhs_pass219_inherited_pass200c_1_24.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS200B_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS200B_VERSION_MINOR 25U
#define HHS_EXACT_PASS219_INHERITED_PASS200B_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS200B_NUMBER 200U
#define HHS_EXACT_PASS219_INHERITED_PASS200B_VARIANT 2U
#define HHS_EXACT_PASS200B_PRIMARY_PR 139U
#define HHS_EXACT_PASS200B_MAX_CANARY_INVOCATIONS 64U
#define HHS_EXACT_PASS200B_LIFECYCLE_TEST_COUNT 8U
#define HHS_EXACT_PASS200B_MEASURED_PASS200A_ENVELOPES 4U
#define HHS_EXACT_PASS200B_MEASURED_PASS200A_BUNDLES 4U
#define HHS_EXACT_PASS200B_MEASURED_PASS200A_SHADOW_MATCHES 4U
#define HHS_EXACT_PASS200B_MEASURED_CANARY_FRONTIERS 2U
#define HHS_EXACT_PASS200B_MEASURED_SINGLETON_ACTIVATIONS 2U
#define HHS_EXACT_PASS200B_MEASURED_INVOCATIONS 9U
#define HHS_EXACT_PASS200B_MEASURED_CANDIDATE_RETURNS 2U
#define HHS_EXACT_PASS200B_MEASURED_REFERENCE_RETURNS 7U
#define HHS_EXACT_PASS200B_MEASURED_ROLLBACK_FRONTIERS 1U
#define HHS_EXACT_PASS200B_MEASURED_EXHAUSTED_FRONTIERS 1U
#define HHS_EXACT_PASS200B_MEASURED_FRONTIER_COUNT 5U
#define HHS_EXACT_PASS200B_MEASURED_HASH72_EVENT_COUNT 14U
#define HHS_EXACT_PASS200B_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS200B_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass200BGovernedCanaryWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t primary_pull_request;
    uint32_t max_canary_invocations;
    uint32_t lifecycle_test_count;
    uint32_t measured_pass200a_envelopes;
    uint32_t measured_pass200a_bundles;
    uint32_t measured_pass200a_shadow_matches;
    uint32_t measured_canary_frontiers;
    uint32_t measured_singleton_activations;
    uint32_t measured_invocations;
    uint32_t measured_candidate_returns;
    uint32_t measured_reference_returns;
    uint32_t measured_rollback_frontiers;
    uint32_t measured_exhausted_frontiers;
    uint32_t measured_frontier_count;
    uint32_t measured_hash72_event_count;
    uint32_t pass200a_closed_proof_required;
    uint32_t compiler_candidate_required;
    uint32_t shadow_mode_required;
    uint32_t persisted_exact_shadow_match_required;
    uint32_t exactly_two_approvals_required;
    uint32_t distinct_approval_principals_required;
    uint32_t distinct_approval_receipts_required;
    uint32_t compiler_runtime_capabilities_required;
    uint32_t approval_bundle_frontier_expiry_receipt_bound;
    uint32_t singleton_vm81_activation_receipt_required;
    uint32_t deterministic_integer_selection_required;
    uint32_t exact_result_match_required;
    uint32_t exact_witness_match_required;
    uint32_t exact_replay_match_required;
    uint32_t mismatch_restores_reference;
    uint32_t expiry_restores_reference;
    uint32_t exhaustion_restores_reference;
    uint32_t explicit_rollback_restores_reference;
    uint32_t durable_state_and_hash72_history;
    uint32_t persisted_frontier_tamper_rejected;
    uint32_t event_chain_tamper_rejected;
    uint32_t candidate_self_authorization;
    uint32_t automatic_active_promotion;
    uint32_t frozen_constraint_promotion;
    uint32_t candidate_canonical_commit;
    uint32_t pass200c_successor_preserved;
    uint32_t pass219_new_canary_admission_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char primary_base_commit[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char validated_executable_head[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char evidence_head_commit[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char accepted_merge_commit[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char frozen_i124_commit[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char contract_blob[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char workflow_blob[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char runtime_v1_blob[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char production_projection_blob[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char canary_routes_blob[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char contract_test_blob[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char visual_panel_blob[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char restart_record_blob[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
} HHSExactPass200BGovernedCanaryWitnessV1;

typedef struct HHSExactPass219InheritedPass200BBindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t pass_variant;
    uint32_t classification;
    uint32_t historical_squash_identity_bound;
    uint32_t immutable_source_identity_bound;
    uint32_t pass200a_shadow_gate_bound;
    uint32_t dual_approval_and_activation_bound;
    uint32_t bounded_integer_selection_bound;
    uint32_t exact_comparison_bound;
    uint32_t rollback_and_exhaustion_bound;
    uint32_t durable_state_read_only_bound;
    uint32_t pass200c_successor_bound;
    uint32_t no_new_canary_admission_authority_bound;
    uint32_t no_new_canonical_mutation_authority_bound;
    uint32_t no_new_persistence_authority_bound;
    uint32_t no_new_hash72_clock_bound;
    uint32_t pass219_new_canary_admission_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char accepted_merge_commit[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
    char frozen_i124_commit[HHS_EXACT_PASS200B_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass200BBindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass200b_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass200b_governed_canary_admission(
    const HHSExactPass200BGovernedCanaryWitnessV1 *witness,
    HHSExactPass219InheritedPass200BBindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
