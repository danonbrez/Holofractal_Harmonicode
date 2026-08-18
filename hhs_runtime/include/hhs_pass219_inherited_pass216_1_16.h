#ifndef HHS_PASS219_INHERITED_PASS216_1_16_H
#define HHS_PASS219_INHERITED_PASS216_1_16_H

#include "hhs_pass219_inherited_pass217_1_16.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS216_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS216_VERSION_MINOR 16U
#define HHS_EXACT_PASS219_INHERITED_PASS216_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS216_NUMBER 216U
#define HHS_EXACT_PASS216_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS216_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS216_SHA256_HEX_LEN 64U
#define HHS_EXACT_PASS216_SHA256_HEX_STRLEN 65U
#define HHS_EXACT_PASS216_SELECTED_TOKEN_COUNT 7U

typedef struct HHSExactPass216AlignmentWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t contract_layer_complete;
    uint32_t parent_alignment_complete;
    uint32_t runtime_optimization_implementation_claimed;
    uint32_t runtime_optimization_required_before_pass217;
    uint32_t global_strict_mode_default;
    uint32_t unchanged_identity_requires_reexecution;
    uint32_t unchanged_identity_requires_identity_verification;
    uint32_t changed_transition_requires_dependency_scoped_validation;
    uint32_t full_system_reproof_required_by_default;
    uint32_t deterministic_truth_gate_closed_by_default;
    uint32_t pass219_must_inherit_pass215_pass216_pass217;
    uint32_t floating_point_canonical_authority;
    uint32_t lossy_authoritative_compression_allowed;
    uint32_t selected_token_count;
    uint32_t selected_token_ids[HHS_EXACT_PASS216_SELECTED_TOKEN_COUNT];
    char pass215_final_head[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
    char pass215_final_tree[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
    char pass215_main_merge[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
    char pass215_artifact_sha256[HHS_EXACT_PASS216_SHA256_HEX_STRLEN];
    char pass216_published_head[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
    char pass216_published_tree[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
    char pass216_merge_commit[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
    char contract_git_blob[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
    char addendum_git_blob[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
} HHSExactPass216AlignmentWitnessV1;

typedef struct HHSExactPass219InheritedPass216BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t contract_alignment_bound;
    uint32_t pass215_terminal_reference_bound;
    uint32_t truth_gate_closed_by_default;
    uint32_t dependency_scoped_validation_bound;
    uint32_t unchanged_authority_reuse_bound;
    uint32_t global_strict_mode_default;
    uint32_t runtime_optimization_implementation_claimed;
    uint32_t runtime_optimization_roadmap_complete;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint32_t floating_point_canonical_authority;
    uint32_t lossy_authoritative_compression_allowed;
    char pass216_published_head[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
    char pass216_merge_commit[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
    char pass215_artifact_sha256[HHS_EXACT_PASS216_SHA256_HEX_STRLEN];
    char contract_git_blob[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
    char addendum_git_blob[HHS_EXACT_PASS216_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass216BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass216_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass216_alignment(
    const HHSExactPass216AlignmentWitnessV1 *witness,
    HHSExactPass219InheritedPass216BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
