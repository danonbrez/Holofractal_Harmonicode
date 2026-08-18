#include "../include/hhs_pass219_inherited_pass212_1_16.h"

#include <stddef.h>
#include <string.h>

static const char HHS_EXACT_PASS212_VALIDATED_BRANCH_HEAD[] = "adc6737d12a371625413c63068de5a898fed0c0f";
static const char HHS_EXACT_PASS212_MAIN_MERGE_HEAD[] = "3fc3ec4596062a1f7e37de19165cfe0e6ed88483";
static const char HHS_EXACT_PASS212_CONTRACT_GIT_BLOB[] = "12f2c577e02f4436ee776366a1994ece5a765fca";
static const char HHS_EXACT_PASS212_RESTART_GIT_BLOB[] = "c2f2ef336de57a2897397e01e820c69e724fa1cc";
static const char HHS_EXACT_PASS212_RUNTIME_GIT_BLOB[] = "2688cf46e2f3084589d4ad961d53e89c33b40a7c";
static const char HHS_EXACT_PASS212_API_GIT_BLOB[] = "0699e1c720f88f47d1d8e4562cb9a73f6a3c0372";
static const char HHS_EXACT_PASS212_EVIDENCE_GIT_BLOB[] = "c27a29e5268bba4361741ed304c31fa293a9e0ae";
static const char HHS_EXACT_PASS212_VALIDATION_SCRIPT_GIT_BLOB[] = "923303154fa4703b897aad59c0b1b0411a52a276";
static const char HHS_EXACT_PASS212_PASS213_RECOVERY_ADMISSION_GIT_BLOB[] = "df7ee51a72991a10bdb25e1342d17cd26a826b9c";
static const char HHS_EXACT_PASS212_AFFINE_STATE_HASH216[] = "19c67438fd7d21eb20817d188f7906212a2507f9783acd82e2176d6fc6c97faa";
static const char HHS_EXACT_PASS212_AFFINE_FULL_ROOT216[] = "4b4e820cfcec05442e3b2db385dedbfbd17ad5de4c88fcd6fe67c3112df8be2c";
static const char HHS_EXACT_PASS212_SPARSE_STATE_HASH216[] = "5fd2c170d5500932fdd04d1ea520d2240175f032cd9540ad383acf4d23bd8dfa";
static const char HHS_EXACT_PASS212_SPARSE_FULL_ROOT216[] = "0ded0d6c6572cb11484c7eff3ce7c9cf5d62a5f1de3cc3a2e3769fcdde58ef3c";
static const char HHS_EXACT_PASS212_RAW_STATE_HASH216[] = "6da86f4b17915b107dada49a36b3b9374cccc7855fbbd793798996cbe1890cec";
static const char HHS_EXACT_PASS212_RAW_FULL_ROOT216[] = "d5753f8b8146a8beae63091652d9a8a0c51dbd9a179476257b83b4d22d2b687f";

static uint32_t hhs_exact_pass219_inherited_pass212_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS212_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS212_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS212_VERSION_PATCH;
}

static int hhs_exact_pass212_exact_text(const char *value, size_t value_size, const char *expected, size_t expected_length) {
    return value != NULL && expected != NULL && value_size == expected_length + 1U &&
           value[expected_length] == '\0' && memcmp(value, expected, expected_length) == 0;
}

static int hhs_exact_pass212_exact_git_sha(const char value[HHS_EXACT_PASS212_GIT_SHA_STRLEN], const char expected[HHS_EXACT_PASS212_GIT_SHA_STRLEN]) {
    return hhs_exact_pass212_exact_text(value, HHS_EXACT_PASS212_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS212_GIT_SHA_LEN);
}

static int hhs_exact_pass212_exact_sha256(const char value[HHS_EXACT_PASS212_SHA256_HEX_STRLEN], const char expected[HHS_EXACT_PASS212_SHA256_HEX_STRLEN]) {
    return hhs_exact_pass212_exact_text(value, HHS_EXACT_PASS212_SHA256_HEX_STRLEN, expected, HHS_EXACT_PASS212_SHA256_HEX_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass212_version(void) {
    return hhs_exact_pass219_inherited_pass212_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass212_full_hydration_recovery(
    const HHSExactPass212RecoveryWitnessV1 *witness,
    HHSExactPass219InheritedPass212BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != hhs_exact_pass219_inherited_pass212_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->runtime_verified != 1U || witness->full_hydration_bits != 50388480U ||
        witness->full_hydration_bytes != 6298560U || witness->local_leaf_bits != 5184U ||
        witness->local_leaf_bytes != 648U || witness->full_leaf_count != 9720U ||
        witness->hydration_lanes != 40U || witness->g243_controls != 243U ||
        witness->affine_seed_bits != 19440U || witness->affine_seed_bytes != 2430U ||
        witness->pure_affine_payload_bytes != 2473U || witness->pure_affine_protected_bytes != 3769U ||
        witness->sparse_exception_count != 4096U || witness->sparse_payload_bytes != 10665U ||
        witness->raw_data_shards != 9720U || witness->raw_parity_shards != 80U ||
        witness->raw_protected_bytes != 6350400U || witness->data_shards_per_stripe != 243U ||
        witness->parity_shards_per_stripe != 2U || witness->recoverable_erasures_per_stripe != 2U ||
        witness->physical_erasures_verified_per_stripe != 2U || witness->strict_claim_boundary_preserved != 1U ||
        witness->arbitrary_raw_state_exact != 1U || witness->physical_recovery_requires_surviving_bytes != 1U ||
        witness->three_missing_same_stripe_fail_closed != 1U || witness->corrupted_material_fail_closed != 1U ||
        witness->no_float_canonical_authority != 1U || witness->required_operation_count != HHS_EXACT_PASS212_REQUIRED_OPERATION_COUNT ||
        witness->pass213_recovery_admission_consumes_pass212 != 1U ||
        witness->pass219_new_canonical_mutation_authority != 0U || witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U || witness->branch_validation_run != 31015011012ULL ||
        witness->main_validation_run != 31015122160ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs_exact_pass212_exact_git_sha(witness->validated_branch_head, HHS_EXACT_PASS212_VALIDATED_BRANCH_HEAD) ||
        !hhs_exact_pass212_exact_git_sha(witness->main_merge_head, HHS_EXACT_PASS212_MAIN_MERGE_HEAD) ||
        !hhs_exact_pass212_exact_git_sha(witness->contract_git_blob, HHS_EXACT_PASS212_CONTRACT_GIT_BLOB) ||
        !hhs_exact_pass212_exact_git_sha(witness->restart_git_blob, HHS_EXACT_PASS212_RESTART_GIT_BLOB) ||
        !hhs_exact_pass212_exact_git_sha(witness->runtime_git_blob, HHS_EXACT_PASS212_RUNTIME_GIT_BLOB) ||
        !hhs_exact_pass212_exact_git_sha(witness->api_git_blob, HHS_EXACT_PASS212_API_GIT_BLOB) ||
        !hhs_exact_pass212_exact_git_sha(witness->evidence_git_blob, HHS_EXACT_PASS212_EVIDENCE_GIT_BLOB) ||
        !hhs_exact_pass212_exact_git_sha(witness->validation_script_git_blob, HHS_EXACT_PASS212_VALIDATION_SCRIPT_GIT_BLOB) ||
        !hhs_exact_pass212_exact_git_sha(witness->pass213_recovery_admission_git_blob, HHS_EXACT_PASS212_PASS213_RECOVERY_ADMISSION_GIT_BLOB) ||
        !hhs_exact_pass212_exact_sha256(witness->affine_state_hash216, HHS_EXACT_PASS212_AFFINE_STATE_HASH216) ||
        !hhs_exact_pass212_exact_sha256(witness->affine_full_root216, HHS_EXACT_PASS212_AFFINE_FULL_ROOT216) ||
        !hhs_exact_pass212_exact_sha256(witness->sparse_state_hash216, HHS_EXACT_PASS212_SPARSE_STATE_HASH216) ||
        !hhs_exact_pass212_exact_sha256(witness->sparse_full_root216, HHS_EXACT_PASS212_SPARSE_FULL_ROOT216) ||
        !hhs_exact_pass212_exact_sha256(witness->raw_state_hash216, HHS_EXACT_PASS212_RAW_STATE_HASH216) ||
        !hhs_exact_pass212_exact_sha256(witness->raw_full_root216, HHS_EXACT_PASS212_RAW_FULL_ROOT216))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs_exact_pass219_inherited_pass212_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS212_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->full_hydration_authority_bound = 1U;
    out_binding->strict_compression_domain_bound = 1U;
    out_binding->raw_fallback_bound = 1U;
    out_binding->physical_erasure_recovery_bound = 1U;
    out_binding->hash216_hash72_integrity_bound = 1U;
    out_binding->pass213_recovery_successor_bound = 1U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    out_binding->recoverable_erasures_per_stripe = witness->recoverable_erasures_per_stripe;
    out_binding->full_hydration_bits = witness->full_hydration_bits;
    out_binding->affine_seed_bytes = witness->affine_seed_bytes;
    out_binding->raw_parity_shards = witness->raw_parity_shards;
    memcpy(out_binding->main_merge_head, witness->main_merge_head, HHS_EXACT_PASS212_GIT_SHA_STRLEN);
    memcpy(out_binding->affine_state_hash216, witness->affine_state_hash216, HHS_EXACT_PASS212_SHA256_HEX_STRLEN);
    memcpy(out_binding->raw_state_hash216, witness->raw_state_hash216, HHS_EXACT_PASS212_SHA256_HEX_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
