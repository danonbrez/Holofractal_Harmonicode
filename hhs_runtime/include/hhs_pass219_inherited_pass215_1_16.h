#ifndef HHS_PASS219_INHERITED_PASS215_1_16_H
#define HHS_PASS219_INHERITED_PASS215_1_16_H

#include "hhs_pass219_inherited_pass216_1_16.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS215_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS215_VERSION_MINOR 16U
#define HHS_EXACT_PASS219_INHERITED_PASS215_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS215_NUMBER 215U
#define HHS_EXACT_PASS215_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS215_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS215_SHA256_HEX_LEN 64U
#define HHS_EXACT_PASS215_SHA256_HEX_STRLEN 65U
#define HHS_EXACT_PASS215_SELECTED_TOKEN_COUNT 7U
#define HHS_EXACT_PASS215_HASH72_STRLEN 73U

typedef struct HHSExactPass215TerminalClosureWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t cumulative_test_count;
    uint32_t selected_token_count;
    uint32_t selected_token_ids[HHS_EXACT_PASS215_SELECTED_TOKEN_COUNT];
    uint32_t terminal_iteration;
    uint32_t contracted_benchmark_complete;
    uint32_t bounded_profile_only;
    uint32_t broader_generation_authority_promoted;
    uint32_t output_projection_pruning_executed;
    uint32_t candidates_pruned;
    uint32_t probabilistic_sampling_executed;
    uint32_t canonical_float_interpretation_performed;
    uint32_t transport_compression_numerical_authority;
    uint32_t runtime_mutation_authority_promoted;
    uint32_t canonical_mutation_authorized;
    uint32_t cross_process_replay;
    uint32_t semantic_exactness;
    uint32_t earlier_restore_prefix_forward_replays;
    uint32_t earlier_restore_generated_forward_replays;
    uint32_t later_restore_prefix_forward_replays;
    uint32_t later_restore_generated_forward_replays;
    uint32_t reused_unique_chunk_count;
    uint64_t reused_compressed_blob_bytes;
    uint64_t incremental_later_compressed_blob_bytes;
    uint64_t later_standalone_compressed_blob_bytes;
    uint64_t shared_store_savings_bytes;
    uint64_t validation_run;
    uint64_t validation_job;
    char final_head[HHS_EXACT_PASS215_GIT_SHA_STRLEN];
    char final_tree[HHS_EXACT_PASS215_GIT_SHA_STRLEN];
    char main_merge[HHS_EXACT_PASS215_GIT_SHA_STRLEN];
    char artifact_sha256[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char model_sha256[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char earlier_checkpoint_root_hash216[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char later_checkpoint_root_hash216[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char shared_content_store_root_hash216[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char shared_checkpoint_bundle_root_hash216[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char sequential_checkpoint_reuse_root_hash216[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char terminal_completion_root_hash216[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char suite_root_hash216[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char evidence_root_hash216[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char receipt_hash72[HHS_EXACT_PASS215_HASH72_STRLEN];
} HHSExactPass215TerminalClosureWitnessV1;

typedef struct HHSExactPass219InheritedPass215BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t terminal_closure_bound;
    uint32_t exact_checkpoint_reuse_bound;
    uint32_t strict_argmax_chain_bound;
    uint32_t zero_restore_replay_bound;
    uint32_t bounded_profile_only;
    uint32_t broader_generation_authority_promoted;
    uint32_t output_projection_pruning_executed;
    uint32_t probabilistic_sampling_executed;
    uint32_t floating_point_canonical_authority;
    uint32_t transport_compression_numerical_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint32_t canonical_mutation_authorized;
    uint32_t cumulative_test_count;
    char final_head[HHS_EXACT_PASS215_GIT_SHA_STRLEN];
    char final_tree[HHS_EXACT_PASS215_GIT_SHA_STRLEN];
    char main_merge[HHS_EXACT_PASS215_GIT_SHA_STRLEN];
    char artifact_sha256[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char terminal_completion_root_hash216[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char evidence_root_hash216[HHS_EXACT_PASS215_SHA256_HEX_STRLEN];
    char receipt_hash72[HHS_EXACT_PASS215_HASH72_STRLEN];
} HHSExactPass219InheritedPass215BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass215_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass215_terminal_closure(
    const HHSExactPass215TerminalClosureWitnessV1 *witness,
    HHSExactPass219InheritedPass215BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
