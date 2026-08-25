#ifndef HHS_PASS219_INHERITED_PASS204_1_20_H
#define HHS_PASS219_INHERITED_PASS204_1_20_H

#include "hhs_pass219_inherited_pass205_1_19.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS204_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS204_VERSION_MINOR 20U
#define HHS_EXACT_PASS219_INHERITED_PASS204_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS204_NUMBER 204U
#define HHS_EXACT_PASS204_DECLARATION_COUNT 2939U
#define HHS_EXACT_PASS204_BINDING_GAP_COUNT 0U
#define HHS_EXACT_PASS204_PUBLIC_ROUTE_COUNT 470U
#define HHS_EXACT_PASS204_OPENAPI_PATH_COUNT 441U
#define HHS_EXACT_PASS204_VALID_OUTCOME_COUNT 3U
#define HHS_EXACT_PASS204_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS204_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS204_HASH72_LEN 72U
#define HHS_EXACT_PASS204_HASH72_STRLEN 73U

typedef struct HHSExactPass204OpenCloudWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t production_verified;
    uint32_t declaration_count;
    uint32_t hydrated_count;
    uint32_t callable_count;
    uint32_t binding_gap_count;
    uint32_t public_route_count;
    uint32_t openapi_path_count;
    uint32_t valid_outcome_count;
    uint32_t all_declarations_executable;
    uint32_t valid_call_http_error;
    uint32_t remote_users_automatically_sandboxed;
    uint32_t ephemeral_compute;
    uint32_t persistent_capability_grants;
    uint32_t direct_host_kernel_access;
    uint32_t caller_adjustable_internal_policy;
    uint32_t session_recall_restores_capabilities;
    uint32_t admitted_history_mutable;
    uint32_t constraint_authority_mutable;
    uint32_t host_fault_can_rewrite_admitted_hash_history;
    uint32_t host_fault_can_mutate_constraint_contract;
    uint32_t canonical_ctypes_raw_pointer_exposed;
    uint32_t project_native_pointer_exposed;
    uint32_t core_native_completed;
    uint32_t project_native_accepted;
    uint32_t pass203_inheritance_verified;
    uint32_t pass205_successor_preserved;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint32_t implementation_pull_request;
    uint64_t final_validation_workflow_run;
    uint64_t final_validation_artifact_id;
    char base_commit[HHS_EXACT_PASS204_GIT_SHA_STRLEN];
    char validated_head[HHS_EXACT_PASS204_GIT_SHA_STRLEN];
    char merge_commit[HHS_EXACT_PASS204_GIT_SHA_STRLEN];
    char validation_receipt_blob[HHS_EXACT_PASS204_GIT_SHA_STRLEN];
    char status_hash72[HHS_EXACT_PASS204_HASH72_STRLEN];
    char snapshot_root[HHS_EXACT_PASS204_HASH72_STRLEN];
    char core_native_receipt_hash72[HHS_EXACT_PASS204_HASH72_STRLEN];
    char project_native_receipt_hash72[HHS_EXACT_PASS204_HASH72_STRLEN];
} HHSExactPass204OpenCloudWitnessV1;

typedef struct HHSExactPass219InheritedPass204BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t universal_declarations_bound;
    uint32_t zero_binding_gaps_bound;
    uint32_t fixed_sandbox_policy_bound;
    uint32_t capability_free_recall_bound;
    uint32_t immutable_history_boundary_bound;
    uint32_t canonical_core_abi_bound;
    uint32_t project_native_durable_job_bound;
    uint32_t inherited_pass204_persistence_bound;
    uint32_t pass203_inheritance_bound;
    uint32_t pass205_successor_bound;
    uint32_t no_new_canonical_mutation_authority_bound;
    uint32_t no_new_persistence_authority_bound;
    uint32_t no_new_hash72_clock_bound;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char merge_commit[HHS_EXACT_PASS204_GIT_SHA_STRLEN];
    char validation_receipt_blob[HHS_EXACT_PASS204_GIT_SHA_STRLEN];
    char status_hash72[HHS_EXACT_PASS204_HASH72_STRLEN];
    char snapshot_root[HHS_EXACT_PASS204_HASH72_STRLEN];
} HHSExactPass219InheritedPass204BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass204_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass204_open_cloud_mainframe(
    const HHSExactPass204OpenCloudWitnessV1 *witness,
    HHSExactPass219InheritedPass204BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
