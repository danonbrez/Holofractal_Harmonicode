#ifndef HHS_PASS219_INHERITED_PASS207_1_17_H
#define HHS_PASS219_INHERITED_PASS207_1_17_H

#include "hhs_pass219_inherited_pass208_1_16.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS207_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS207_VERSION_MINOR 17U
#define HHS_EXACT_PASS219_INHERITED_PASS207_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS207_NUMBER 207U
#define HHS_EXACT_PASS207_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS207_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS207_VM81_CELLS 81U
#define HHS_EXACT_PASS207_LOGICAL_HYPERTHREADS_PER_CELL 64U
#define HHS_EXACT_PASS207_LOGICAL_LANES_PER_BATCH 5184U
#define HHS_EXACT_PASS207_PHASE_DIMENSION 72U
#define HHS_EXACT_PASS207_PROJECTION_CHANNELS 32U
#define HHS_EXACT_PASS207_REQUIRED_OPERATION_COUNT 7U

typedef struct HHSExactPass207GPUHyperthreadWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t runtime_verified;
    uint32_t vm81_cells;
    uint32_t logical_hyperthreads_per_cell;
    uint32_t logical_lanes_per_batch;
    uint32_t phase_dimension;
    uint32_t projection_channels;
    uint32_t required_operation_count;
    uint32_t stable_lane_identity;
    uint32_t lane_phase_bijection_bound;
    uint32_t disjoint_lane_writes;
    uint32_t ordered_cell_pack_bound;
    uint32_t ordered_projection_bound;
    uint32_t ordered_hydration_bound;
    uint32_t exact_cpu_oracle_equality_required;
    uint32_t candidate_only;
    uint32_t buffer_cache_content_keyed;
    uint32_t cache_hit_authorizes_mutation;
    uint32_t stable_vector_ranking_bound;
    uint32_t gpu_may_commit_hash72;
    uint32_t gpu_may_mutate_canonical_state;
    uint32_t gpu_may_bypass_vm81;
    uint32_t parallel_canonical_authorities_allowed;
    uint32_t physical_completion_order_noncanonical;
    uint32_t physical_gpu_fail_closed;
    uint32_t pass205_singleton_vm81_admission_preserved;
    uint32_t pass208_inherits_pass207;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t direct_gpu_vm81_mutation_authority;
    uint64_t branch_validation_run;
    uint64_t branch_validation_job;
    char validated_branch_head[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char main_merge_head[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char contract_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char manifest_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char driver_header_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char driver_source_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char driver_part1_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char driver_part2_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char driver_part3_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char driver_part4_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char driver_part5_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char native_bridge_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char python_bridge_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char runtime_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char restart_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char validation_workflow_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char native_test_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char python_test_git_blob[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
    char pass208_main_merge_head[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
} HHSExactPass207GPUHyperthreadWitnessV1;

typedef struct HHSExactPass219InheritedPass207BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t stable_vm5184_lane_dispatch_bound;
    uint32_t lane_phase_bijection_bound;
    uint32_t ordered_cell_pack_bound;
    uint32_t ordered_hydration_bound;
    uint32_t exact_cpu_oracle_verification_bound;
    uint32_t content_keyed_cache_bound;
    uint32_t stable_vector_ranking_bound;
    uint32_t candidate_only_bound;
    uint32_t gpu_hash72_commit_forbidden;
    uint32_t gpu_canonical_mutation_forbidden;
    uint32_t gpu_vm81_bypass_forbidden;
    uint32_t pass205_singleton_vm81_admission_bound;
    uint32_t physical_gpu_fail_closed;
    uint32_t pass208_successor_bound;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t direct_gpu_vm81_mutation_authority;
    uint32_t logical_lanes_per_batch;
    uint32_t projection_channels;
    char main_merge_head[HHS_EXACT_PASS207_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass207BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass207_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass207_gpu_hyperthread_driver(
    const HHSExactPass207GPUHyperthreadWitnessV1 *witness,
    HHSExactPass219InheritedPass207BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
