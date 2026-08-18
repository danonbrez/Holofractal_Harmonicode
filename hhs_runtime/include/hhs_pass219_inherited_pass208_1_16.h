#ifndef HHS_PASS219_INHERITED_PASS208_1_16_H
#define HHS_PASS219_INHERITED_PASS208_1_16_H

#include "hhs_pass219_inherited_pass209_1_16.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS208_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS208_VERSION_MINOR 16U
#define HHS_EXACT_PASS219_INHERITED_PASS208_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS208_NUMBER 208U
#define HHS_EXACT_PASS208_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS208_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS208_LOGICAL_LANES_PER_BRANCH 5184U
#define HHS_EXACT_PASS208_JSON_SPEC_FILE_COUNT 23U
#define HHS_EXACT_PASS208_MINIMUM_EXAMPLE_COUNT 4U
#define HHS_EXACT_PASS208_REQUIRED_OPERATION_COUNT 6U

typedef struct HHSExactPass208GPUBranchManifoldWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t runtime_verified;
    uint32_t logical_lanes_per_branch;
    uint32_t json_spec_file_count;
    uint32_t minimum_example_count;
    uint32_t required_operation_count;
    uint32_t same_kernel_bytecode_hydration_lattice;
    uint32_t same_parent_snapshot_required;
    uint32_t same_constraint_root_required;
    uint32_t same_hash216_lineage_required;
    uint32_t same_hash72_commit_stream_required;
    uint32_t branch_candidate_only;
    uint32_t gpu_cpu_equality_required;
    uint32_t stable_integer_ranking_bound;
    uint32_t gpu_may_commit_hash72;
    uint32_t gpu_may_persist_canonical_snapshot;
    uint32_t gpu_may_bypass_vm81;
    uint32_t cache_hit_authorizes_mutation;
    uint32_t pass205_singleton_vm81_commit_authority_preserved;
    uint32_t physical_gpu_fail_closed;
    uint32_t pass209_inherits_pass208;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t direct_gpu_vm81_mutation_authority;
    uint64_t branch_validation_run;
    uint64_t branch_validation_job;
    char validated_branch_head[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
    char main_merge_head[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
    char contract_git_blob[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
    char runtime_git_blob[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
    char routes_git_blob[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
    char restart_git_blob[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
    char validation_workflow_git_blob[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
    char runtime_test_git_blob[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
    char deployment_test_git_blob[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
    char preflight_git_blob[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
    char spec_validator_git_blob[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
    char pass209_main_merge_head[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
} HHSExactPass208GPUBranchManifoldWitnessV1;

typedef struct HHSExactPass219InheritedPass208BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t gpu_candidate_expansion_bound;
    uint32_t exact_cpu_oracle_verification_bound;
    uint32_t stable_integer_ranking_bound;
    uint32_t pass205_singleton_vm81_commit_path_bound;
    uint32_t gpu_hash72_commit_forbidden;
    uint32_t gpu_canonical_persistence_forbidden;
    uint32_t gpu_vm81_bypass_forbidden;
    uint32_t physical_gpu_fail_closed;
    uint32_t pass209_successor_bound;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t direct_gpu_vm81_mutation_authority;
    uint32_t logical_lanes_per_branch;
    uint32_t json_spec_file_count;
    char main_merge_head[HHS_EXACT_PASS208_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass208BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass208_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass208_gpu_branch_manifold(
    const HHSExactPass208GPUBranchManifoldWitnessV1 *witness,
    HHSExactPass219InheritedPass208BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
