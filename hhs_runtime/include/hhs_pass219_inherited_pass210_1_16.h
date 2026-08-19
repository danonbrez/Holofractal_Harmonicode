#ifndef HHS_PASS219_INHERITED_PASS210_1_16_H
#define HHS_PASS219_INHERITED_PASS210_1_16_H

#include "hhs_pass219_inherited_pass211_1_16.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS210_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS210_VERSION_MINOR 16U
#define HHS_EXACT_PASS219_INHERITED_PASS210_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS210_NUMBER 210U
#define HHS_EXACT_PASS210_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS210_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS210_SHA256_HEX_LEN 64U
#define HHS_EXACT_PASS210_SHA256_HEX_STRLEN 65U
#define HHS_EXACT_PASS210_HASH72_LEN 72U
#define HHS_EXACT_PASS210_HASH72_STRLEN 73U
#define HHS_EXACT_PASS210_REQUIRED_OPERATION_COUNT 11U
#define HHS_EXACT_PASS210_MODALITY_COUNT 5U

typedef struct HHSExactPass210HFCWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t runtime_verified;
    uint32_t register_len;
    uint32_t grid_lo_shu;
    uint32_t line_bytes;
    uint32_t snapshot_width;
    uint32_t snapshot_stride;
    uint32_t snapshot_count;
    uint32_t section_phi_hi;
    uint32_t section_phi_lo;
    uint32_t matrix_dim;
    uint32_t modality_count;
    uint32_t required_operation_count;
    uint32_t double_coverage_verified;
    uint32_t single_snapshot_erasure_drills;
    uint32_t corruption_localization_modalities;
    uint32_t deterministic_replay_verified;
    uint32_t strict_domain_boundary_preserved;
    uint32_t digest_only_reversibility_forbidden;
    uint32_t no_float_canonical_authority;
    uint32_t pass211_inherits_pass210;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint64_t branch_validation_run;
    uint64_t main_validation_run;
    char validated_branch_head[HHS_EXACT_PASS210_GIT_SHA_STRLEN];
    char main_merge_head[HHS_EXACT_PASS210_GIT_SHA_STRLEN];
    char contract_git_blob[HHS_EXACT_PASS210_GIT_SHA_STRLEN];
    char restart_git_blob[HHS_EXACT_PASS210_GIT_SHA_STRLEN];
    char runtime_git_blob[HHS_EXACT_PASS210_GIT_SHA_STRLEN];
    char api_git_blob[HHS_EXACT_PASS210_GIT_SHA_STRLEN];
    char evidence_git_blob[HHS_EXACT_PASS210_GIT_SHA_STRLEN];
    char validation_script_git_blob[HHS_EXACT_PASS210_GIT_SHA_STRLEN];
    char pass211_contract_git_blob[HHS_EXACT_PASS210_GIT_SHA_STRLEN];
    char pass211_runtime_git_blob[HHS_EXACT_PASS210_GIT_SHA_STRLEN];
    char reference_register_hash216[HHS_EXACT_PASS210_SHA256_HEX_STRLEN];
    char reference_register_sha256[HHS_EXACT_PASS210_SHA256_HEX_STRLEN];
    char strict_register_hash216[HHS_EXACT_PASS210_SHA256_HEX_STRLEN];
    char strict_domain_witness_hash216[HHS_EXACT_PASS210_SHA256_HEX_STRLEN];
    char strict_roundtrip_receipt_hash72[HHS_EXACT_PASS210_HASH72_STRLEN];
    char full_session_receipt_head_hash72[HHS_EXACT_PASS210_HASH72_STRLEN];
} HHSExactPass210HFCWitnessV1;

typedef struct HHSExactPass219InheritedPass210BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t exact_frame_authority_bound;
    uint32_t double_witness_coverage_bound;
    uint32_t single_snapshot_recovery_bound;
    uint32_t multimodal_agreement_bound;
    uint32_t strict_compression_domain_bound;
    uint32_t digest_decode_boundary_bound;
    uint32_t pass211_successor_bound;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint32_t register_len;
    uint32_t snapshot_count;
    uint32_t snapshot_width;
    uint32_t snapshot_stride;
    char main_merge_head[HHS_EXACT_PASS210_GIT_SHA_STRLEN];
    char reference_register_hash216[HHS_EXACT_PASS210_SHA256_HEX_STRLEN];
    char strict_register_hash216[HHS_EXACT_PASS210_SHA256_HEX_STRLEN];
    char full_session_receipt_head_hash72[HHS_EXACT_PASS210_HASH72_STRLEN];
} HHSExactPass219InheritedPass210BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass210_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass210_holographic_frame_compression(
    const HHSExactPass210HFCWitnessV1 *witness,
    HHSExactPass219InheritedPass210BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
