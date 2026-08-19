#include "../include/hhs_pass219_inherited_pass217_1_16.h"

#include <stddef.h>
#include <string.h>

static const char HHS_EXACT_PASS217_I4_CANDIDATE_SHA256[] =
    "97379c7ae7cdaebd8031a3a3fb58559c967b361b360c7db34ec096acabfc8fe8";
static const char HHS_EXACT_PASS217_I4_ADDRESS_MAP_SHA256[] =
    "2f8d8a23114b87f2dbe91f3d302ef089b750f9d91f533d744a4524e907717f5f";
static const char HHS_EXACT_PASS217_I4_HASH72_MATRIX_ROOT_SHA256[] =
    "6c0b2e9e354e8d7eb17a746d01c157b19aa95b58296884126cdf5bef7998e286";
static const char HHS_EXACT_PASS217_I4_HASH72_MANIFOLD_ROOT_SHA256[] =
    "c757bae150d9ab94485c680ec3143e715b674d35f445a72c6fb4ea2def6f7884";
static const char HHS_EXACT_PASS217_I4_NUCLEUS_IDENTITY_ROOT_SHA256[] =
    "da7b33fa1a419e00ce81eeeeb5f1c435acd6ae7b95d355e3a1749a6a238e3164";
static const char HHS_EXACT_PASS217_I4_NUCLEUS_SUPPORT_ROOT_SHA256[] =
    "ac46211412784990e08e5cf0b80df5db381aad612a7ccd8aa816815a105b0294";
static const char HHS_EXACT_PASS217_I4_RECORD_ROOT_SHA256[] =
    "5c996cda648db2074a144ab8b9b0834ef442ee8bc2b2c7ed91885bc38aa6d03f";
static const char HHS_EXACT_PASS217_CHECKPOINT15_GIT_SHA[] =
    "be71da59c9b8b7c7e055c03da703ca301849cfff";
static const char HHS_EXACT_PASS217_INTEGRATION_GIT_SHA[] =
    "b0656a92ab29507f81eae760e070f74e49db83f4";

static uint32_t hhs_exact_pass219_inherited_pass217_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS217_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS217_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS217_VERSION_PATCH;
}

static int hhs_exact_pass217_hash72_symbol_valid(char value) {
    size_t index;
    for (index = 0U; index < HHS_EXACT_HASH72_LEN; ++index) {
        if (HHS_EXACT_HASH72_ALPHABET[index] == value)
            return 1;
    }
    return 0;
}

static int hhs_exact_pass217_hash72_valid(
    const char value[HHS_EXACT_HASH72_STRLEN]
) {
    size_t index;
    if (value == NULL || value[HHS_EXACT_HASH72_LEN] != '\0')
        return 0;
    for (index = 0U; index < HHS_EXACT_HASH72_LEN; ++index) {
        if (!hhs_exact_pass217_hash72_symbol_valid(value[index]))
            return 0;
    }
    return 1;
}

static int hhs_exact_pass217_exact_text(
    const char *value,
    size_t value_size,
    const char *expected,
    size_t expected_length
) {
    if (value == NULL || expected == NULL || value_size != expected_length + 1U)
        return 0;
    if (value[expected_length] != '\0')
        return 0;
    return memcmp(value, expected, expected_length) == 0;
}

static int hhs_exact_pass217_exact_sha256(
    const char value[HHS_EXACT_PASS217_SHA256_HEX_STRLEN],
    const char expected[HHS_EXACT_PASS217_SHA256_HEX_STRLEN]
) {
    return hhs_exact_pass217_exact_text(
        value,
        HHS_EXACT_PASS217_SHA256_HEX_STRLEN,
        expected,
        HHS_EXACT_PASS217_SHA256_HEX_LEN);
}

static int hhs_exact_pass217_exact_git_sha(
    const char value[HHS_EXACT_PASS217_GIT_SHA_STRLEN],
    const char expected[HHS_EXACT_PASS217_GIT_SHA_STRLEN]
) {
    return hhs_exact_pass217_exact_text(
        value,
        HHS_EXACT_PASS217_GIT_SHA_STRLEN,
        expected,
        HHS_EXACT_PASS217_GIT_SHA_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass217_version(void) {
    return hhs_exact_pass219_inherited_pass217_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass217_cumulative_closure(
    const HHSExactPass217CumulativeClosureWitnessV1 *witness,
    HHSExactPass219InheritedPass217BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != hhs_exact_pass219_inherited_pass217_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->required_authority_count != HHS_EXACT_PASS217_REQUIRED_AUTHORITY_COUNT ||
        witness->published_route_count != HHS_EXACT_PASS217_PUBLISHED_ROUTE_COUNT ||
        witness->pass042_api_route_count != HHS_EXACT_PASS217_API_ROUTE_COUNT ||
        witness->bypass_omission_count != HHS_EXACT_PASS217_BYPASS_OMISSION_COUNT ||
        witness->hash72_symbol_count != HHS_EXACT_PASS217_HASH72_SYMBOL_COUNT ||
        witness->hash72_matrix_positions != HHS_EXACT_PASS217_HASH72_MATRIX_POSITIONS ||
        witness->wrapped_direction_count != HHS_EXACT_PASS217_WRAPPED_DIRECTION_COUNT)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (witness->cumulative_closure_admitted != 1U ||
        witness->global_surface_publication_complete != 1U ||
        witness->required_authority_bypass_matrix_complete != 1U ||
        witness->authority_profile_coverage_equal != 1U ||
        witness->incremental_tokenization_active_path_proven != 1U ||
        witness->structural_closure_hardening_complete != 1U ||
        witness->universal_utilization_reachability_complete != 1U ||
        witness->i4_hash72_manifold_validated != 1U ||
        witness->i4_immutable_nucleus_validated != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (witness->synthetic_bypass_fixtures_are_runtime_evidence != 0U ||
        witness->optional_profile_classes_promoted_to_core != 0U ||
        witness->experimental_profile_classes_promoted_to_core != 0U ||
        witness->floating_point_authority != 0U ||
        witness->i4_canonical_authority_promoted != 0U ||
        witness->i4_runtime_mutation_performed != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs_exact_pass217_hash72_valid(witness->closure_root_hash72) ||
        !hhs_exact_pass217_exact_sha256(witness->i4_candidate_sha256,
                                        HHS_EXACT_PASS217_I4_CANDIDATE_SHA256) ||
        !hhs_exact_pass217_exact_sha256(witness->i4_address_map_sha256,
                                        HHS_EXACT_PASS217_I4_ADDRESS_MAP_SHA256) ||
        !hhs_exact_pass217_exact_sha256(witness->i4_hash72_matrix_root_sha256,
                                        HHS_EXACT_PASS217_I4_HASH72_MATRIX_ROOT_SHA256) ||
        !hhs_exact_pass217_exact_sha256(witness->i4_hash72_manifold_root_sha256,
                                        HHS_EXACT_PASS217_I4_HASH72_MANIFOLD_ROOT_SHA256) ||
        !hhs_exact_pass217_exact_sha256(witness->i4_nucleus_identity_root_sha256,
                                        HHS_EXACT_PASS217_I4_NUCLEUS_IDENTITY_ROOT_SHA256) ||
        !hhs_exact_pass217_exact_sha256(witness->i4_nucleus_support_root_sha256,
                                        HHS_EXACT_PASS217_I4_NUCLEUS_SUPPORT_ROOT_SHA256) ||
        !hhs_exact_pass217_exact_sha256(witness->i4_record_root_sha256,
                                        HHS_EXACT_PASS217_I4_RECORD_ROOT_SHA256) ||
        !hhs_exact_pass217_exact_git_sha(witness->checkpoint15_git_sha,
                                         HHS_EXACT_PASS217_CHECKPOINT15_GIT_SHA) ||
        !hhs_exact_pass217_exact_git_sha(witness->integration_git_sha,
                                         HHS_EXACT_PASS217_INTEGRATION_GIT_SHA))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs_exact_pass219_inherited_pass217_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS217_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->required_authority_count = witness->required_authority_count;
    out_binding->published_route_count = witness->published_route_count;
    out_binding->bypass_omission_count = witness->bypass_omission_count;
    out_binding->cumulative_closure_bound = 1U;
    out_binding->all_required_authorities_nonbypassable = 1U;
    out_binding->canonical_execution_reachable = 1U;
    out_binding->hash72_manifold_bound = 1U;
    out_binding->immutable_nucleus_bound = 1U;
    out_binding->exact_incremental_tokenization_bound = 1U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    out_binding->genesis_rom_promotion_claimed = 0U;
    memcpy(out_binding->closure_root_hash72,
           witness->closure_root_hash72,
           HHS_EXACT_HASH72_STRLEN);
    memcpy(out_binding->i4_hash72_manifold_root_sha256,
           witness->i4_hash72_manifold_root_sha256,
           HHS_EXACT_PASS217_SHA256_HEX_STRLEN);
    memcpy(out_binding->i4_nucleus_identity_root_sha256,
           witness->i4_nucleus_identity_root_sha256,
           HHS_EXACT_PASS217_SHA256_HEX_STRLEN);
    memcpy(out_binding->checkpoint15_git_sha,
           witness->checkpoint15_git_sha,
           HHS_EXACT_PASS217_GIT_SHA_STRLEN);
    memcpy(out_binding->integration_git_sha,
           witness->integration_git_sha,
           HHS_EXACT_PASS217_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
