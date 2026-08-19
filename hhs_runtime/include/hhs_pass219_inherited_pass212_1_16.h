#ifndef HHS_PASS219_INHERITED_PASS212_1_16_H
#define HHS_PASS219_INHERITED_PASS212_1_16_H

#include "hhs_pass219_inherited_pass213_1_16.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS212_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS212_VERSION_MINOR 16U
#define HHS_EXACT_PASS219_INHERITED_PASS212_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS212_NUMBER 212U
#define HHS_EXACT_PASS212_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS212_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS212_SHA256_HEX_LEN 64U
#define HHS_EXACT_PASS212_SHA256_HEX_STRLEN 65U
#define HHS_EXACT_PASS212_REQUIRED_OPERATION_COUNT 7U

typedef struct HHSExactPass212RecoveryWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t runtime_verified;
    uint32_t full_hydration_bits;
    uint32_t full_hydration_bytes;
    uint32_t local_leaf_bits;
    uint32_t local_leaf_bytes;
    uint32_t full_leaf_count;
    uint32_t hydration_lanes;
    uint32_t g243_controls;
    uint32_t affine_seed_bits;
    uint32_t affine_seed_bytes;
    uint32_t pure_affine_payload_bytes;
    uint32_t pure_affine_protected_bytes;
    uint32_t sparse_exception_count;
    uint32_t sparse_payload_bytes;
    uint32_t raw_data_shards;
    uint32_t raw_parity_shards;
    uint32_t raw_protected_bytes;
    uint32_t data_shards_per_stripe;
    uint32_t parity_shards_per_stripe;
    uint32_t recoverable_erasures_per_stripe;
    uint32_t physical_erasures_verified_per_stripe;
    uint32_t strict_claim_boundary_preserved;
    uint32_t arbitrary_raw_state_exact;
    uint32_t physical_recovery_requires_surviving_bytes;
    uint32_t three_missing_same_stripe_fail_closed;
    uint32_t corrupted_material_fail_closed;
    uint32_t no_float_canonical_authority;
    uint32_t required_operation_count;
    uint32_t pass213_recovery_admission_consumes_pass212;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint64_t branch_validation_run;
    uint64_t main_validation_run;
    char validated_branch_head[HHS_EXACT_PASS212_GIT_SHA_STRLEN];
    char main_merge_head[HHS_EXACT_PASS212_GIT_SHA_STRLEN];
    char contract_git_blob[HHS_EXACT_PASS212_GIT_SHA_STRLEN];
    char restart_git_blob[HHS_EXACT_PASS212_GIT_SHA_STRLEN];
    char runtime_git_blob[HHS_EXACT_PASS212_GIT_SHA_STRLEN];
    char api_git_blob[HHS_EXACT_PASS212_GIT_SHA_STRLEN];
    char evidence_git_blob[HHS_EXACT_PASS212_GIT_SHA_STRLEN];
    char validation_script_git_blob[HHS_EXACT_PASS212_GIT_SHA_STRLEN];
    char pass213_recovery_admission_git_blob[HHS_EXACT_PASS212_GIT_SHA_STRLEN];
    char affine_state_hash216[HHS_EXACT_PASS212_SHA256_HEX_STRLEN];
    char affine_full_root216[HHS_EXACT_PASS212_SHA256_HEX_STRLEN];
    char sparse_state_hash216[HHS_EXACT_PASS212_SHA256_HEX_STRLEN];
    char sparse_full_root216[HHS_EXACT_PASS212_SHA256_HEX_STRLEN];
    char raw_state_hash216[HHS_EXACT_PASS212_SHA256_HEX_STRLEN];
    char raw_full_root216[HHS_EXACT_PASS212_SHA256_HEX_STRLEN];
} HHSExactPass212RecoveryWitnessV1;

typedef struct HHSExactPass219InheritedPass212BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t full_hydration_authority_bound;
    uint32_t strict_compression_domain_bound;
    uint32_t raw_fallback_bound;
    uint32_t physical_erasure_recovery_bound;
    uint32_t hash216_hash72_integrity_bound;
    uint32_t pass213_recovery_successor_bound;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint32_t recoverable_erasures_per_stripe;
    uint32_t full_hydration_bits;
    uint32_t affine_seed_bytes;
    uint32_t raw_parity_shards;
    char main_merge_head[HHS_EXACT_PASS212_GIT_SHA_STRLEN];
    char affine_state_hash216[HHS_EXACT_PASS212_SHA256_HEX_STRLEN];
    char raw_state_hash216[HHS_EXACT_PASS212_SHA256_HEX_STRLEN];
} HHSExactPass219InheritedPass212BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass212_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass212_full_hydration_recovery(
    const HHSExactPass212RecoveryWitnessV1 *witness,
    HHSExactPass219InheritedPass212BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
