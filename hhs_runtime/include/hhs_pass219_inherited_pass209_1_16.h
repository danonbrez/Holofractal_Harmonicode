#ifndef HHS_PASS219_INHERITED_PASS209_1_16_H
#define HHS_PASS219_INHERITED_PASS209_1_16_H

#include "hhs_pass219_inherited_pass210_1_16.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS209_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS209_VERSION_MINOR 16U
#define HHS_EXACT_PASS219_INHERITED_PASS209_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS209_NUMBER 209U
#define HHS_EXACT_PASS209_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS209_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS209_STATUS_CATALOG_COUNT 9U
#define HHS_EXACT_PASS209_REQUIRED_OPERATION_COUNT 7U

typedef struct HHSExactPass209RuntimeBootstrapWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t runtime_verified;
    uint32_t status_catalog_count;
    uint32_t required_operation_count;
    uint32_t persistent_cache_bound;
    uint32_t stale_while_revalidate_bound;
    uint32_t isolated_sequential_probe_bound;
    uint32_t cold_miss_warming_projection_bound;
    uint32_t direct_status_intercept_bound;
    uint32_t browser_readiness_coordination_bound;
    uint32_t external_state_roots_bound;
    uint32_t repository_checkout_readonly_bound;
    uint32_t canonical_backend_authority_preserved;
    uint32_t cache_projection_noncanonical;
    uint32_t pass210_inherits_pass209;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint64_t branch_validation_run;
    uint64_t branch_validation_job;
    char validated_branch_head[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
    char main_merge_head[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
    char restart_git_blob[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
    char cache_git_blob[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
    char probe_git_blob[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
    char gateway_git_blob[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
    char production_gateway_git_blob[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
    char service_git_blob[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
    char gateway_test_git_blob[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
    char production_test_git_blob[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
    char validation_workflow_git_blob[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
    char pass210_contract_git_blob[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
} HHSExactPass209RuntimeBootstrapWitnessV1;

typedef struct HHSExactPass219InheritedPass209BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t nonblocking_bootstrap_bound;
    uint32_t persistent_status_cache_bound;
    uint32_t isolated_probe_bound;
    uint32_t warming_fail_open_to_projection_bound;
    uint32_t external_state_root_boundary_bound;
    uint32_t canonical_backend_authority_preserved;
    uint32_t pass210_successor_bound;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint32_t status_catalog_count;
    char main_merge_head[HHS_EXACT_PASS209_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass209BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass209_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass209_runtime_bootstrap_gateway(
    const HHSExactPass209RuntimeBootstrapWitnessV1 *witness,
    HHSExactPass219InheritedPass209BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
