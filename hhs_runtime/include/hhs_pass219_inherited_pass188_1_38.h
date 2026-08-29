#ifndef HHS_PASS219_INHERITED_PASS188_1_38_H
#define HHS_PASS219_INHERITED_PASS188_1_38_H

#include "hhs_pass219_inherited_pass189_1_37.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS188_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS188_VERSION_MINOR 38U
#define HHS_EXACT_PASS219_INHERITED_PASS188_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS188_NUMBER 188U
#define HHS_EXACT_PASS188_I138_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass188CumulativeAuthorityWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t license_contract_preserved;
    uint32_t license_completion_verified;
    uint32_t license_acceptance_scenario_count;
    uint32_t immutable_content_versions;
    uint32_t immutable_license_versions;
    uint32_t inherited_vm81_witness_required;
    uint32_t license_hash72_event_chain;
    uint32_t license_hash216_identity;
    uint32_t license_deterministic_replay;
    uint32_t license_materialized_integrity;
    uint32_t license_cold_restart_recovery;
    uint32_t license_pass187_graph_impact;
    uint32_t license_transfer_delegation;
    uint32_t license_revocation_expiry;
    uint32_t license_exact_royalty;
    uint32_t license_external_chain_required;
    uint32_t license_wallet_authority;
    uint32_t license_browser_authority;
    uint32_t license_marketplace_authority;
    uint32_t license_float_canonical_authority;
    uint32_t license_independent_vm81_authority;
    uint32_t license_independent_hash72_clock;
    uint32_t bott_runtime_verified;
    uint32_t bott_projected_address_count;
    uint32_t bott_deterministic_replay;
    uint32_t bott_float_canonical_authority;
    uint32_t bott_canonical_mutation_authority;
    uint32_t pass189_successor_preserved;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;

    char license_contract_commit[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN];
    char bott_runtime_commit[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN];
    char license_completion_head[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN];
    char frozen_i137_commit[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN];
    char license_contract_blob[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN];
    char bott_receipt_blob[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN];
    char license_runtime_blob[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN];
    char license_tests_blob[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN];
    char license_workflow_blob[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN];
} HHSExactPass188CumulativeAuthorityWitnessV1;

typedef struct HHSExactPass219InheritedPass188BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t license_contract_bound;
    uint32_t license_completion_bound;
    uint32_t immutable_lineage_bound;
    uint32_t vm81_witness_boundary_bound;
    uint32_t license_receipt_replay_bound;
    uint32_t legacy_transfer_revocation_bound;
    uint32_t pass187_impact_bound;
    uint32_t bott_runtime_bound;
    uint32_t bott_nonmutation_bound;
    uint32_t pass189_successor_bound;
    uint32_t no_new_authority_bound;
    uint32_t float_is_canonical_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char frozen_i137_commit[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN];
    char license_completion_head[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass188BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass188_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass188_cumulative_authority(
    const HHSExactPass188CumulativeAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass188BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
