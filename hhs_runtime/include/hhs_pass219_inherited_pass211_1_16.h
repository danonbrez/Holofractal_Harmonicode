#ifndef HHS_PASS219_INHERITED_PASS211_1_16_H
#define HHS_PASS219_INHERITED_PASS211_1_16_H

#include "hhs_pass219_inherited_pass212_1_16.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS211_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS211_VERSION_MINOR 16U
#define HHS_EXACT_PASS219_INHERITED_PASS211_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS211_NUMBER 211U
#define HHS_EXACT_PASS211_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS211_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS211_SHA256_HEX_LEN 64U
#define HHS_EXACT_PASS211_SHA256_HEX_STRLEN 65U
#define HHS_EXACT_PASS211_HASH72_LEN 72U
#define HHS_EXACT_PASS211_HASH72_STRLEN 73U
#define HHS_EXACT_PASS211_REQUIRED_OPERATION_COUNT 6U

typedef struct HHSExactPass211BigIntHFCWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t runtime_verified;
    uint32_t hfc_register_boolean_cells;
    uint32_t packed_shard_bytes;
    uint32_t snapshot_count;
    uint32_t snapshot_width;
    uint32_t snapshot_stride;
    uint32_t maximum_shards;
    uint32_t pass133_corpus_roundtrips;
    uint32_t pass133_single_bit_corrections;
    uint32_t fitting_package_count;
    uint32_t fitting_erasure_recoveries;
    uint32_t anchored_corruption_cell;
    uint32_t multiregister_source_bits;
    uint32_t multiregister_carrier_bytes;
    uint32_t multiregister_shard_count;
    uint32_t multiregister_first_shard_bytes;
    uint32_t multiregister_final_shard_bytes;
    uint32_t deterministic_replay_verified;
    uint32_t strict_claim_boundary_preserved;
    uint32_t historical_integrity_requires_minted_anchor;
    uint32_t missing_duplicate_reorder_substitution_fail_closed;
    uint32_t zero_negative_fail_closed;
    uint32_t no_float_canonical_authority;
    uint32_t required_operation_count;
    uint32_t pass212_contract_inherits_pass211;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint64_t branch_validation_run;
    uint64_t main_validation_run;
    char validated_branch_head[HHS_EXACT_PASS211_GIT_SHA_STRLEN];
    char main_merge_head[HHS_EXACT_PASS211_GIT_SHA_STRLEN];
    char contract_git_blob[HHS_EXACT_PASS211_GIT_SHA_STRLEN];
    char restart_git_blob[HHS_EXACT_PASS211_GIT_SHA_STRLEN];
    char runtime_git_blob[HHS_EXACT_PASS211_GIT_SHA_STRLEN];
    char api_git_blob[HHS_EXACT_PASS211_GIT_SHA_STRLEN];
    char evidence_git_blob[HHS_EXACT_PASS211_GIT_SHA_STRLEN];
    char validation_script_git_blob[HHS_EXACT_PASS211_GIT_SHA_STRLEN];
    char pass212_contract_git_blob[HHS_EXACT_PASS211_GIT_SHA_STRLEN];
    char deterministic_package_root216[HHS_EXACT_PASS211_SHA256_HEX_STRLEN];
    char multiregister_package_root216[HHS_EXACT_PASS211_SHA256_HEX_STRLEN];
    char deterministic_package_receipt_hash72[HHS_EXACT_PASS211_HASH72_STRLEN];
} HHSExactPass211BigIntHFCWitnessV1;

typedef struct HHSExactPass219InheritedPass211BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t pass133_bigint_carrier_bound;
    uint32_t pass210_hfc_multiregister_bound;
    uint32_t exact_shard_roundtrip_bound;
    uint32_t single_snapshot_recovery_bound;
    uint32_t anchored_historical_integrity_bound;
    uint32_t strict_compression_claim_boundary_bound;
    uint32_t pass212_successor_bound;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint32_t packed_shard_bytes;
    uint32_t snapshot_count;
    uint32_t multiregister_shard_count;
    char main_merge_head[HHS_EXACT_PASS211_GIT_SHA_STRLEN];
    char deterministic_package_root216[HHS_EXACT_PASS211_SHA256_HEX_STRLEN];
    char deterministic_package_receipt_hash72[HHS_EXACT_PASS211_HASH72_STRLEN];
} HHSExactPass219InheritedPass211BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass211_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass211_bigint_hfc_carrier(
    const HHSExactPass211BigIntHFCWitnessV1 *witness,
    HHSExactPass219InheritedPass211BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
