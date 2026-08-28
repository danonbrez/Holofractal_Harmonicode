#ifndef HHS_PASS219_INHERITED_PASS200C_1_24_H
#define HHS_PASS219_INHERITED_PASS200C_1_24_H

#include "hhs_pass219_inherited_pass201_1_23.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS200C_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS200C_VERSION_MINOR 24U
#define HHS_EXACT_PASS219_INHERITED_PASS200C_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS200C_NUMBER 200U
#define HHS_EXACT_PASS219_INHERITED_PASS200C_VARIANT 3U
#define HHS_EXACT_PASS200C_PRIMARY_PR 140U
#define HHS_EXACT_PASS200C_MIN_SUCCESSFUL_CANARIES 2U
#define HHS_EXACT_PASS200C_MIN_CANARY_INVOCATIONS 12U
#define HHS_EXACT_PASS200C_MAX_ACTIVE_LEASE_INVOCATIONS 64U
#define HHS_EXACT_PASS200C_LIFECYCLE_TEST_COUNT 10U
#define HHS_EXACT_PASS200C_MEASURED_CANARY_INVOCATIONS 16U
#define HHS_EXACT_PASS200C_MEASURED_ACTIVE_INVOCATIONS 7U
#define HHS_EXACT_PASS200C_MEASURED_ACTIVE_CANDIDATE_RETURNS 6U
#define HHS_EXACT_PASS200C_MEASURED_ACTIVE_REFERENCE_RETURNS 1U
#define HHS_EXACT_PASS200C_MEASURED_FRONTIER_COUNT 5U
#define HHS_EXACT_PASS200C_MEASURED_HASH72_EVENT_COUNT 13U
#define HHS_EXACT_PASS200C_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS200C_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass200CGuardedActiveWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t primary_pull_request;
    uint32_t min_successful_canaries;
    uint32_t min_canary_invocations;
    uint32_t max_active_lease_invocations;
    uint32_t lifecycle_test_count;
    uint32_t measured_canary_invocations;
    uint32_t measured_active_invocations;
    uint32_t measured_active_candidate_returns;
    uint32_t measured_active_reference_returns;
    uint32_t measured_frontier_count;
    uint32_t measured_hash72_event_count;
    uint32_t pass200a_candidate_bundle_required;
    uint32_t pass200b_completed_canary_evidence_required;
    uint32_t pass200b_rollback_disqualifies_bundle;
    uint32_t three_distinct_approval_principals_required;
    uint32_t compiler_runtime_operations_capabilities_required;
    uint32_t distinct_approval_receipts_required;
    uint32_t approvals_frontier_evidence_bundle_expiry_bound;
    uint32_t singleton_vm81_activation_receipt_required;
    uint32_t exact_result_guard_every_invocation;
    uint32_t exact_witness_guard_every_invocation;
    uint32_t exact_replay_guard_every_invocation;
    uint32_t mismatch_restores_reference;
    uint32_t expiry_restores_reference;
    uint32_t lease_exhaustion_restores_reference;
    uint32_t explicit_rollback_restores_reference;
    uint32_t durable_state_and_hash72_history;
    uint32_t persisted_evidence_tamper_rejected;
    uint32_t persisted_frontier_tamper_rejected;
    uint32_t candidate_self_authorization;
    uint32_t frozen_constraint_promotion;
    uint32_t pass201_successor_preserved;
    uint32_t pass219_new_active_admission_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char primary_base_commit[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char validated_executable_head[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char evidence_head_commit[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char accepted_merge_commit[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char frozen_i123_commit[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char contract_blob[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char workflow_blob[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char runtime_v1_blob[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char production_projection_blob[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char active_routes_blob[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char contract_test_blob[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char production_validator_blob[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
} HHSExactPass200CGuardedActiveWitnessV1;

typedef struct HHSExactPass219InheritedPass200CBindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t pass_variant;
    uint32_t classification;
    uint32_t historical_squash_identity_bound;
    uint32_t immutable_source_identity_bound;
    uint32_t canary_evidence_gate_bound;
    uint32_t approval_and_activation_bound;
    uint32_t continuous_exact_guard_bound;
    uint32_t rollback_reference_restoration_bound;
    uint32_t durable_state_read_only_bound;
    uint32_t pass201_successor_bound;
    uint32_t no_new_active_admission_authority_bound;
    uint32_t no_new_canonical_mutation_authority_bound;
    uint32_t no_new_persistence_authority_bound;
    uint32_t no_new_hash72_clock_bound;
    uint32_t pass219_new_active_admission_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char accepted_merge_commit[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
    char frozen_i123_commit[HHS_EXACT_PASS200C_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass200CBindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass200c_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass200c_guarded_active_admission(
    const HHSExactPass200CGuardedActiveWitnessV1 *witness,
    HHSExactPass219InheritedPass200CBindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
