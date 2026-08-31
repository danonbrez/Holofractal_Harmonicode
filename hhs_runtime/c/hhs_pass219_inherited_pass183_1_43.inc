#include "../include/hhs_pass219_inherited_pass183_1_43.h"

#include <string.h>

static const char P183_I143_IMPLEMENTATION_COMMIT[] = "4a2797ffcf75e29b616ca37b3183ea3521e03a39";
static const char P183_I143_HISTORICAL_GREEN_HEAD[] = "3ae56827b27500c2c8187126d5825a901d4feb40";
static const char P183_I143_FROZEN_I142[] = "33004d347337cf8c57f9772609806e49503c1bd0";
static const char P183_I143_I142_RECEIPT_BLOB[] = "7677afce5fcbfecc4ef276a8be9d3efcee95e4ab";

static uint32_t p183_i143_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS183_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS183_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS183_VERSION_PATCH;
}

static int p183_i143_git(
    const char value[HHS_EXACT_PASS183_I143_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS183_I143_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS183_I143_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass183_version(void) {
    return p183_i143_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass183_probability_hydration(
    const HHSExactPass183ProbabilityHydrationWitnessV1 *witness,
    HHSExactPass219InheritedPass183BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p183_i143_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->historical_contract_preserved != 1U ||
        witness->historical_implementation_preserved != 1U ||
        witness->historical_ci_green != 1U ||
        witness->exact_probability_runtime_bound != 1U ||
        witness->factorial72_reciprocal_bound != 1U ||
        witness->membrane_boundary_bound != 1U ||
        witness->typed_zero_bypass_bound != 1U ||
        witness->global_modulus_bound != 1U ||
        witness->singleton_vm81_bound != 1U ||
        witness->canonical_hash72_after_vm81_bound != 1U ||
        witness->hash216_archive_after_hash72_bound != 1U ||
        witness->deterministic_replay_bound != 1U ||
        witness->runtime_os_gui_bound != 1U ||
        witness->legacy_native_hash_witness_noncanonical != 1U ||
        witness->native_hash72_authority != 0U ||
        witness->native_hash216_authority != 0U ||
        witness->hash216_precommit_authority != 0U ||
        witness->independent_vm81_authority != 0U ||
        witness->floating_point_canonical_authority != 0U ||
        witness->pass184_successor_preserved != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p183_i143_git(witness->implementation_commit, P183_I143_IMPLEMENTATION_COMMIT) ||
        !p183_i143_git(witness->historical_green_head, P183_I143_HISTORICAL_GREEN_HEAD) ||
        !p183_i143_git(witness->frozen_i142_commit, P183_I143_FROZEN_I142) ||
        !p183_i143_git(witness->i142_validation_receipt_blob, P183_I143_I142_RECEIPT_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p183_i143_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS183_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->exact_probability_runtime_bound = 1U;
    out_binding->singleton_vm81_bound = 1U;
    out_binding->canonical_hash72_receipt_bound = 1U;
    out_binding->hash216_archival_only_bound = 1U;
    out_binding->deterministic_replay_bound = 1U;
    out_binding->runtime_os_gui_bound = 1U;
    out_binding->legacy_native_hash_witness_noncanonical = 1U;
    out_binding->no_new_authority_bound = 1U;
    memcpy(out_binding->implementation_commit, P183_I143_IMPLEMENTATION_COMMIT, HHS_EXACT_PASS183_I143_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i142_commit, P183_I143_FROZEN_I142, HHS_EXACT_PASS183_I143_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
