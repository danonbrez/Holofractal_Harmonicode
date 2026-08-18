#include "../include/hhs_pass219_inherited_pass210_1_16.h"

#include <stddef.h>
#include <string.h>

static const char P210_VALIDATED_HEAD[] = "0d1433d30f9fe811dc42a3155afeafa089aa72ff";
static const char P210_MAIN_MERGE[] = "a8cd64e76828fd911e7e6e27ffd9ad02c7d74355";
static const char P210_CONTRACT_BLOB[] = "ac46a61f568b0443794f854cf84e5a3cfc1bf908";
static const char P210_RESTART_BLOB[] = "3dee1ac8eb16a9bd151514ddbc4490b51d6d1df8";
static const char P210_RUNTIME_BLOB[] = "bb85330627cd58a1cb57ab47f3d5520d8b1157b1";
static const char P210_API_BLOB[] = "6569f8f689ab48aa4239e0e2214ec1d27485dd35";
static const char P210_EVIDENCE_BLOB[] = "221afe26a8d9fd5ddc475c60e2a516aad414d7cd";
static const char P210_VALIDATION_BLOB[] = "939cdc583f3f245282c80217fcc1b132d2471783";
static const char P211_CONTRACT_BLOB[] = "685c6d1544cbae6966e84c0d05b6bf4b8687d903";
static const char P211_RUNTIME_BLOB[] = "0d11f3607c81b442b76dcd455b5c47450c9ed7e9";
static const char P210_REFERENCE_HASH216[] = "8997ab0f9c3aaa3b0d158c2855788042c7904060cf51b6f020bec4b25400567b";
static const char P210_REFERENCE_SHA256[] = "26232cd54a39e54a9bf9a71cdceebb92133c3787e218b15778783b9b0c16e8ea";
static const char P210_STRICT_HASH216[] = "02d1610350a72bace2d05cdb6447d30bd6492dd53c1ae12ecfdce5fedae7b25f";
static const char P210_STRICT_WITNESS_HASH216[] = "0832b78e97f63692ad0036d39395124139b563609e6e713a231642fdfcba6258";
static const char P210_STRICT_RECEIPT[] = "y97qyS8z(ChXMN2/CcdgtDl0cjdipoB(4WVdHtMGucWqv25ALrFwcLVc7o1!N!6FVvoWc!Ky";
static const char P210_SESSION_HEAD[] = "7TBLHLh0!9wHuBvCLeNCGyitXUagjDP8colu+WxSD7(f?nR4wCqyf)Fgc+Ct22YWV6uS8yQk";

static uint32_t p210_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS210_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS210_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS210_VERSION_PATCH;
}

static int p210_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}
static int p210_git(const char value[HHS_EXACT_PASS210_GIT_SHA_STRLEN], const char expected[HHS_EXACT_PASS210_GIT_SHA_STRLEN]) {
    return p210_text(value, HHS_EXACT_PASS210_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS210_GIT_SHA_LEN);
}
static int p210_sha256(const char value[HHS_EXACT_PASS210_SHA256_HEX_STRLEN], const char expected[HHS_EXACT_PASS210_SHA256_HEX_STRLEN]) {
    return p210_text(value, HHS_EXACT_PASS210_SHA256_HEX_STRLEN, expected, HHS_EXACT_PASS210_SHA256_HEX_LEN);
}
static int p210_hash72(const char value[HHS_EXACT_PASS210_HASH72_STRLEN], const char expected[HHS_EXACT_PASS210_HASH72_STRLEN]) {
    return p210_text(value, HHS_EXACT_PASS210_HASH72_STRLEN, expected, HHS_EXACT_PASS210_HASH72_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass210_version(void) { return p210_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass210_holographic_frame_compression(
    const HHSExactPass210HFCWitnessV1 *witness,
    HHSExactPass219InheritedPass210BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p210_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->runtime_verified != 1U || witness->register_len != 5184U || witness->grid_lo_shu != 81U ||
        witness->line_bytes != 64U || witness->snapshot_width != 288U || witness->snapshot_stride != 144U ||
        witness->snapshot_count != 36U || witness->section_phi_hi != 89U || witness->section_phi_lo != 55U ||
        witness->matrix_dim != 12U || witness->modality_count != HHS_EXACT_PASS210_MODALITY_COUNT ||
        witness->required_operation_count != HHS_EXACT_PASS210_REQUIRED_OPERATION_COUNT ||
        witness->double_coverage_verified != 1U || witness->single_snapshot_erasure_drills != 36U ||
        witness->corruption_localization_modalities != 5U || witness->deterministic_replay_verified != 1U ||
        witness->strict_domain_boundary_preserved != 1U || witness->digest_only_reversibility_forbidden != 1U ||
        witness->no_float_canonical_authority != 1U || witness->pass211_inherits_pass210 != 1U ||
        witness->pass219_new_canonical_mutation_authority != 0U || witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U || witness->branch_validation_run != 30994827355ULL ||
        witness->main_validation_run != 30994901959ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!p210_git(witness->validated_branch_head, P210_VALIDATED_HEAD) ||
        !p210_git(witness->main_merge_head, P210_MAIN_MERGE) ||
        !p210_git(witness->contract_git_blob, P210_CONTRACT_BLOB) ||
        !p210_git(witness->restart_git_blob, P210_RESTART_BLOB) ||
        !p210_git(witness->runtime_git_blob, P210_RUNTIME_BLOB) ||
        !p210_git(witness->api_git_blob, P210_API_BLOB) ||
        !p210_git(witness->evidence_git_blob, P210_EVIDENCE_BLOB) ||
        !p210_git(witness->validation_script_git_blob, P210_VALIDATION_BLOB) ||
        !p210_git(witness->pass211_contract_git_blob, P211_CONTRACT_BLOB) ||
        !p210_git(witness->pass211_runtime_git_blob, P211_RUNTIME_BLOB) ||
        !p210_sha256(witness->reference_register_hash216, P210_REFERENCE_HASH216) ||
        !p210_sha256(witness->reference_register_sha256, P210_REFERENCE_SHA256) ||
        !p210_sha256(witness->strict_register_hash216, P210_STRICT_HASH216) ||
        !p210_sha256(witness->strict_domain_witness_hash216, P210_STRICT_WITNESS_HASH216) ||
        !p210_hash72(witness->strict_roundtrip_receipt_hash72, P210_STRICT_RECEIPT) ||
        !p210_hash72(witness->full_session_receipt_head_hash72, P210_SESSION_HEAD))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p210_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS210_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->exact_frame_authority_bound = 1U;
    out_binding->double_witness_coverage_bound = 1U;
    out_binding->single_snapshot_recovery_bound = 1U;
    out_binding->multimodal_agreement_bound = 1U;
    out_binding->strict_compression_domain_bound = 1U;
    out_binding->digest_decode_boundary_bound = 1U;
    out_binding->pass211_successor_bound = 1U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    out_binding->register_len = witness->register_len;
    out_binding->snapshot_count = witness->snapshot_count;
    out_binding->snapshot_width = witness->snapshot_width;
    out_binding->snapshot_stride = witness->snapshot_stride;
    memcpy(out_binding->main_merge_head, witness->main_merge_head, HHS_EXACT_PASS210_GIT_SHA_STRLEN);
    memcpy(out_binding->reference_register_hash216, witness->reference_register_hash216, HHS_EXACT_PASS210_SHA256_HEX_STRLEN);
    memcpy(out_binding->strict_register_hash216, witness->strict_register_hash216, HHS_EXACT_PASS210_SHA256_HEX_STRLEN);
    memcpy(out_binding->full_session_receipt_head_hash72, witness->full_session_receipt_head_hash72, HHS_EXACT_PASS210_HASH72_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
