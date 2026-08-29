#ifndef HHS_PASS219_INHERITED_PASS190_1_36_H
#define HHS_PASS219_INHERITED_PASS190_1_36_H

#include "hhs_pass219_inherited_pass191_1_35.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS190_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS190_VERSION_MINOR 36U
#define HHS_EXACT_PASS219_INHERITED_PASS190_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS190_NUMBER 190U
#define HHS_EXACT_PASS190_I136_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass190FullCompletionAuthorityWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t full_contract_authorized;
    uint32_t historical_iteration7_preserved;
    uint32_t completion_coordinator_verified;
    uint32_t project_acceptance_overlay_verified;
    uint32_t python312_census_classified;
    uint32_t governed_operation_count;
    uint32_t historical_operation_count;
    uint32_t project_acceptance_operation_count;
    uint32_t constructor_python_shell_direct_parity;
    uint32_t canonical_public_gateway;
    uint32_t openapi_registry_projection;
    uint32_t websocket_receipt_projection;
    uint32_t actual_repository_hydration_reused;
    uint32_t mutation_capability_gated;
    uint32_t deterministic_replay;
    uint32_t hash72_receipt_chain;
    uint32_t hash216_registry_identity;
    uint32_t pass191_successor_preserved;
    uint32_t float_is_canonical_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char contract_authorization_commit[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char iteration7_merge_commit[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char frozen_i135_commit[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char validated_core_head[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char universal_contract_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char iteration7_receipt_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char init_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char python_compat_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char completion_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char acceptance_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char shell_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char public_api_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char python_registry_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char hydration_registry_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char network_registry_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char completion_test_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char validated_core_workflow_blob[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
} HHSExactPass190FullCompletionAuthorityWitnessV1;

typedef struct HHSExactPass219InheritedPass190BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t full_contract_bound;
    uint32_t historical_iteration7_bound;
    uint32_t completion_coordinator_bound;
    uint32_t registry_52_bound;
    uint32_t interface_parity_bound;
    uint32_t canonical_gateway_bound;
    uint32_t repository_hydration_bound;
    uint32_t inherited_vm81_receipt_bound;
    uint32_t hash216_registry_bound;
    uint32_t pass191_successor_bound;
    uint32_t no_new_authority_bound;
    uint32_t float_is_canonical_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char validated_core_head[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
    char frozen_i135_commit[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass190BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass190_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass190_full_completion_authority(
    const HHSExactPass190FullCompletionAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass190BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
