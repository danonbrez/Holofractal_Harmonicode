#include "../include/hhs_pass219_inherited_pass211_1_16.h"

#include <stddef.h>
#include <string.h>

static const char HHS_EXACT_PASS211_VALIDATED_BRANCH_HEAD[] = "5c877eeae86e1fd929e30a2c418f705f12921265";
static const char HHS_EXACT_PASS211_MAIN_MERGE_HEAD[] = "b80759e60bd78357d9d650aa23c99460f3952fd3";
static const char HHS_EXACT_PASS211_CONTRACT_GIT_BLOB[] = "685c6d1544cbae6966e84c0d05b6bf4b8687d903";
static const char HHS_EXACT_PASS211_RESTART_GIT_BLOB[] = "7065102a60501c797407fe7a40cdf760ab6a11b3";
static const char HHS_EXACT_PASS211_RUNTIME_GIT_BLOB[] = "0d11f3607c81b442b76dcd455b5c47450c9ed7e9";
static const char HHS_EXACT_PASS211_API_GIT_BLOB[] = "a3df09c2593fc0c3d1c331b103b86826cb1a7084";
static const char HHS_EXACT_PASS211_EVIDENCE_GIT_BLOB[] = "fa8807d66a28a5e38c0294cdac34e214dc39a8b6";
static const char HHS_EXACT_PASS211_VALIDATION_SCRIPT_GIT_BLOB[] = "4ae19dab0dd9d0b70398b6b433f92e799a6baf38";
static const char HHS_EXACT_PASS211_PASS212_CONTRACT_GIT_BLOB[] = "12f2c577e02f4436ee776366a1994ece5a765fca";
static const char HHS_EXACT_PASS211_DETERMINISTIC_PACKAGE_ROOT216[] = "2a87ecd5755a5bd22801b0b4f528b5edfbd442c8616f1bfde2a204d652ecdee2";
static const char HHS_EXACT_PASS211_MULTIREGISTER_PACKAGE_ROOT216[] = "b5b1e92df89a9422a7367b166c32c9362848573a065be3d2192981a4da4d1234";
static const char HHS_EXACT_PASS211_DETERMINISTIC_RECEIPT_HASH72[] = "m8h4vJSUoQ38FH8Ogr0B7xot1TwI9BA2KiCjwyyEzTz1ZfEUeQQwRLgswPeHvc>Fvk8zOYO-";

static uint32_t hhs_exact_pass219_inherited_pass211_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS211_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS211_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS211_VERSION_PATCH;
}

static int hhs_exact_pass211_exact_text(const char *value, size_t value_size, const char *expected, size_t expected_length) {
    return value != NULL && expected != NULL && value_size == expected_length + 1U &&
           value[expected_length] == '\0' && memcmp(value, expected, expected_length) == 0;
}

static int hhs_exact_pass211_exact_git_sha(const char value[HHS_EXACT_PASS211_GIT_SHA_STRLEN], const char expected[HHS_EXACT_PASS211_GIT_SHA_STRLEN]) {
    return hhs_exact_pass211_exact_text(value, HHS_EXACT_PASS211_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS211_GIT_SHA_LEN);
}

static int hhs_exact_pass211_exact_sha256(const char value[HHS_EXACT_PASS211_SHA256_HEX_STRLEN], const char expected[HHS_EXACT_PASS211_SHA256_HEX_STRLEN]) {
    return hhs_exact_pass211_exact_text(value, HHS_EXACT_PASS211_SHA256_HEX_STRLEN, expected, HHS_EXACT_PASS211_SHA256_HEX_LEN);
}

static int hhs_exact_pass211_exact_hash72(const char value[HHS_EXACT_PASS211_HASH72_STRLEN], const char expected[HHS_EXACT_PASS211_HASH72_STRLEN]) {
    return hhs_exact_pass211_exact_text(value, HHS_EXACT_PASS211_HASH72_STRLEN, expected, HHS_EXACT_PASS211_HASH72_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass211_version(void) {
    return hhs_exact_pass219_inherited_pass211_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass211_bigint_hfc_carrier(
    const HHSExactPass211BigIntHFCWitnessV1 *witness,
    HHSExactPass219InheritedPass211BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != hhs_exact_pass219_inherited_pass211_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->runtime_verified != 1U || witness->hfc_register_boolean_cells != 5184U ||
        witness->packed_shard_bytes != 648U || witness->snapshot_count != 36U ||
        witness->snapshot_width != 288U || witness->snapshot_stride != 144U ||
        witness->maximum_shards != 4096U || witness->pass133_corpus_roundtrips != 11U ||
        witness->pass133_single_bit_corrections != 512U || witness->fitting_package_count != 4U ||
        witness->fitting_erasure_recoveries != 144U || witness->anchored_corruption_cell != 1000U ||
        witness->multiregister_source_bits != 1024U || witness->multiregister_carrier_bytes != 811U ||
        witness->multiregister_shard_count != 2U || witness->multiregister_first_shard_bytes != 648U ||
        witness->multiregister_final_shard_bytes != 163U || witness->deterministic_replay_verified != 1U ||
        witness->strict_claim_boundary_preserved != 1U || witness->historical_integrity_requires_minted_anchor != 1U ||
        witness->missing_duplicate_reorder_substitution_fail_closed != 1U || witness->zero_negative_fail_closed != 1U ||
        witness->no_float_canonical_authority != 1U || witness->required_operation_count != HHS_EXACT_PASS211_REQUIRED_OPERATION_COUNT ||
        witness->pass212_contract_inherits_pass211 != 1U || witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->cxx_mutation_authority != 0U || witness->vm81_mutation_authority != 0U ||
        witness->branch_validation_run != 31005616936ULL || witness->main_validation_run != 31005763191ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs_exact_pass211_exact_git_sha(witness->validated_branch_head, HHS_EXACT_PASS211_VALIDATED_BRANCH_HEAD) ||
        !hhs_exact_pass211_exact_git_sha(witness->main_merge_head, HHS_EXACT_PASS211_MAIN_MERGE_HEAD) ||
        !hhs_exact_pass211_exact_git_sha(witness->contract_git_blob, HHS_EXACT_PASS211_CONTRACT_GIT_BLOB) ||
        !hhs_exact_pass211_exact_git_sha(witness->restart_git_blob, HHS_EXACT_PASS211_RESTART_GIT_BLOB) ||
        !hhs_exact_pass211_exact_git_sha(witness->runtime_git_blob, HHS_EXACT_PASS211_RUNTIME_GIT_BLOB) ||
        !hhs_exact_pass211_exact_git_sha(witness->api_git_blob, HHS_EXACT_PASS211_API_GIT_BLOB) ||
        !hhs_exact_pass211_exact_git_sha(witness->evidence_git_blob, HHS_EXACT_PASS211_EVIDENCE_GIT_BLOB) ||
        !hhs_exact_pass211_exact_git_sha(witness->validation_script_git_blob, HHS_EXACT_PASS211_VALIDATION_SCRIPT_GIT_BLOB) ||
        !hhs_exact_pass211_exact_git_sha(witness->pass212_contract_git_blob, HHS_EXACT_PASS211_PASS212_CONTRACT_GIT_BLOB) ||
        !hhs_exact_pass211_exact_sha256(witness->deterministic_package_root216, HHS_EXACT_PASS211_DETERMINISTIC_PACKAGE_ROOT216) ||
        !hhs_exact_pass211_exact_sha256(witness->multiregister_package_root216, HHS_EXACT_PASS211_MULTIREGISTER_PACKAGE_ROOT216) ||
        !hhs_exact_pass211_exact_hash72(witness->deterministic_package_receipt_hash72, HHS_EXACT_PASS211_DETERMINISTIC_RECEIPT_HASH72))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs_exact_pass219_inherited_pass211_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS211_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->pass133_bigint_carrier_bound = 1U;
    out_binding->pass210_hfc_multiregister_bound = 1U;
    out_binding->exact_shard_roundtrip_bound = 1U;
    out_binding->single_snapshot_recovery_bound = 1U;
    out_binding->anchored_historical_integrity_bound = 1U;
    out_binding->strict_compression_claim_boundary_bound = 1U;
    out_binding->pass212_successor_bound = 1U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    out_binding->packed_shard_bytes = witness->packed_shard_bytes;
    out_binding->snapshot_count = witness->snapshot_count;
    out_binding->multiregister_shard_count = witness->multiregister_shard_count;
    memcpy(out_binding->main_merge_head, witness->main_merge_head, HHS_EXACT_PASS211_GIT_SHA_STRLEN);
    memcpy(out_binding->deterministic_package_root216, witness->deterministic_package_root216, HHS_EXACT_PASS211_SHA256_HEX_STRLEN);
    memcpy(out_binding->deterministic_package_receipt_hash72, witness->deterministic_package_receipt_hash72, HHS_EXACT_PASS211_HASH72_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
