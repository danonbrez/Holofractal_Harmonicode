#include "../include/hhs_pass219_inherited_pass218_1_16.h"

#include <stddef.h>
#include <string.h>

static uint32_t hhs_exact_pass219_inherited_pass218_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS218_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS218_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS218_VERSION_PATCH;
}

static int hhs_exact_pass219_hash72_symbol_valid(char value) {
    size_t index;
    for (index = 0U; index < HHS_EXACT_HASH72_LEN; ++index) {
        if (HHS_EXACT_HASH72_ALPHABET[index] == value)
            return 1;
    }
    return 0;
}

static int hhs_exact_pass219_hash72_string_valid(
    const char value[HHS_EXACT_HASH72_STRLEN]
) {
    size_t index;
    if (value == NULL || value[HHS_EXACT_HASH72_LEN] != '\0')
        return 0;
    for (index = 0U; index < HHS_EXACT_HASH72_LEN; ++index) {
        if (!hhs_exact_pass219_hash72_symbol_valid(value[index]))
            return 0;
    }
    return 1;
}

static int hhs_exact_pass219_hash216_triplet_valid(
    const HHSExactPass218CompletionWitnessV1 *witness
) {
    if (witness->i48_hash216[216] != '\0')
        return 0;
    if (memcmp(witness->i48_hash216,
               witness->i47_receipt_hash72,
               HHS_EXACT_HASH72_LEN) != 0)
        return 0;
    if (memcmp(witness->i48_hash216 + HHS_EXACT_HASH72_LEN,
               witness->i33_advance_receipt_hash72,
               HHS_EXACT_HASH72_LEN) != 0)
        return 0;
    if (memcmp(witness->i48_hash216 + (2U * HHS_EXACT_HASH72_LEN),
               witness->i48_receipt_hash72,
               HHS_EXACT_HASH72_LEN) != 0)
        return 0;
    return 1;
}

static int hhs_exact_pass219_sha256_nonzero(
    const uint8_t value[HHS_EXACT_PASS219_SHA256_BYTES]
) {
    size_t index;
    uint8_t accumulator = 0U;
    for (index = 0U; index < HHS_EXACT_PASS219_SHA256_BYTES; ++index)
        accumulator = (uint8_t)(accumulator | value[index]);
    return accumulator != 0U;
}

uint32_t hhs_exact_pass219_inherited_pass218_version(void) {
    return hhs_exact_pass219_inherited_pass218_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass218_completion(
    const HHSExactPass218CompletionWitnessV1 *witness,
    HHSExactPass219InheritedPass218BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != hhs_exact_pass219_inherited_pass218_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->manifest_source_count == 0U ||
        witness->completed_source_count != witness->manifest_source_count)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (witness->terminal_completion_verified != 1U ||
        witness->authoritative_manifest_exhausted != 1U ||
        witness->final_cursor_exhausted != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (witness->pass219_handoff_authority_minted != 0U ||
        witness->vm81_authorization_invoked != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs_exact_pass219_hash72_string_valid(witness->i47_receipt_hash72) ||
        !hhs_exact_pass219_hash72_string_valid(witness->i33_advance_receipt_hash72) ||
        !hhs_exact_pass219_hash72_string_valid(witness->i48_receipt_hash72) ||
        !hhs_exact_pass219_hash72_string_valid(witness->completion_proof_hash72) ||
        !hhs_exact_pass219_hash72_string_valid(witness->curriculum_identity_hash72) ||
        !hhs_exact_pass219_hash72_string_valid(witness->final_closure_hash72) ||
        !hhs_exact_pass219_hash216_triplet_valid(witness))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hhs_exact_pass219_sha256_nonzero(witness->final_cursor_sha256) ||
        !hhs_exact_pass219_sha256_nonzero(witness->i30_generation_sha256))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs_exact_pass219_inherited_pass218_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS218_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->manifest_source_count = witness->manifest_source_count;
    out_binding->completed_source_count = witness->completed_source_count;
    out_binding->completion_seal_bound = 1U;
    out_binding->receipt_semantics_preserved = 1U;
    out_binding->continuation_identity_exposed = 1U;
    out_binding->canonical_execution_reachable = 1U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    out_binding->pass219_handoff_authority_minted = 0U;

    memcpy(out_binding->i48_receipt_hash72,
           witness->i48_receipt_hash72,
           HHS_EXACT_HASH72_STRLEN);
    memcpy(out_binding->completion_proof_hash72,
           witness->completion_proof_hash72,
           HHS_EXACT_HASH72_STRLEN);
    memcpy(out_binding->curriculum_identity_hash72,
           witness->curriculum_identity_hash72,
           HHS_EXACT_HASH72_STRLEN);
    memcpy(out_binding->final_closure_hash72,
           witness->final_closure_hash72,
           HHS_EXACT_HASH72_STRLEN);
    memcpy(out_binding->i48_hash216,
           witness->i48_hash216,
           HHS_EXACT_PASS219_HASH216_STRLEN);
    memcpy(out_binding->final_cursor_sha256,
           witness->final_cursor_sha256,
           HHS_EXACT_PASS219_SHA256_BYTES);
    memcpy(out_binding->i30_generation_sha256,
           witness->i30_generation_sha256,
           HHS_EXACT_PASS219_SHA256_BYTES);
    return HHS_EXACT_STATUS_OK;
}
