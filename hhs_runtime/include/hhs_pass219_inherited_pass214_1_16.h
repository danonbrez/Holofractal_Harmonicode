#ifndef HHS_PASS219_INHERITED_PASS214_1_16_H
#define HHS_PASS219_INHERITED_PASS214_1_16_H

#include "hhs_pass219_inherited_pass215_1_16.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS214_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS214_VERSION_MINOR 16U
#define HHS_EXACT_PASS219_INHERITED_PASS214_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS214_NUMBER 214U
#define HHS_EXACT_PASS214_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS214_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS214_SHA256_HEX_LEN 64U
#define HHS_EXACT_PASS214_SHA256_HEX_STRLEN 65U
#define HHS_EXACT_PASS214_TERMINAL_ROOT_COUNT 8U
#define HHS_EXACT_PASS214_HASH72_STRLEN 73U

typedef struct HHSExactPass214BenchmarkAuthorityWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t terminal_iteration;
    uint32_t terminal_roots_minted;
    uint32_t benchmark_authority_promoted;
    uint32_t pass215_authorized;
    uint32_t pass213_gates_preserved;
    uint32_t runtime_mutation_authority_promoted;
    uint32_t canonical_mutation_authorized;
    uint32_t migration_active;
    uint32_t pass213_live_admission_required_before_canonical_mutation;
    uint32_t workload_families;
    uint32_t workload_modes_per_family;
    uint32_t mode_executions;
    uint32_t mandatory_ablations;
    uint32_t benchmark_stage_count;
    uint32_t pass197_address_comparisons;
    uint32_t pass212_full_hydration_bits;
    uint32_t pass212_full_state_recoveries;
    uint32_t cross_process_replays;
    uint32_t semantic_reuse_execution_authority_changed;
    uint32_t semantic_reuse_automatic_promotion;
    uint32_t semantic_reuse_registry_entries;
    uint32_t semantic_reuse_remaining_backlog;
    uint32_t exact_vm81_kernel_rebound;
    uint64_t main_closure_run;
    uint64_t semantic_reuse_run;
    char validated_terminal_head[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
    char merge_commit[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
    char main_closure_commit[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
    char main_closure_tree[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
    char main_closure_artifact_sha256[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char repository_scan_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char optimization_registry_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char compatibility_graph_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char workload_corpus_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char benchmark_method_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char compound_evidence_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char authority_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char pass215_profile_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char pass213_gate_preservation_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char compound_benchmark_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char terminal_receipt_hash72[HHS_EXACT_PASS214_HASH72_STRLEN];
    char semantic_reuse_head[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
    char semantic_reuse_tree[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
    char semantic_reuse_artifact_sha256[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char exact_vm81_kernel_git_blob[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
    char vm81_rebind_script_commit[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
    char vm81_rebind_test_commit[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
} HHSExactPass214BenchmarkAuthorityWitnessV1;

typedef struct HHSExactPass219InheritedPass214BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t terminal_benchmark_authority_bound;
    uint32_t eight_root_terminal_closure_bound;
    uint32_t pass215_profile_authorization_bound;
    uint32_t semantic_equivalence_reuse_bound;
    uint32_t exact_vm81_kernel_rebind_bound;
    uint32_t pass213_gates_preserved;
    uint32_t runtime_mutation_authority_promoted;
    uint32_t canonical_mutation_authorized;
    uint32_t migration_active;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint32_t workload_families;
    uint32_t mandatory_ablations;
    char main_closure_commit[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
    char authority_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char pass215_profile_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char pass213_gate_preservation_root_hash216[HHS_EXACT_PASS214_SHA256_HEX_STRLEN];
    char terminal_receipt_hash72[HHS_EXACT_PASS214_HASH72_STRLEN];
    char semantic_reuse_head[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
    char exact_vm81_kernel_git_blob[HHS_EXACT_PASS214_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass214BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass214_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass214_benchmark_authority(
    const HHSExactPass214BenchmarkAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass214BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
