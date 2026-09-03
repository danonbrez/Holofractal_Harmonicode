#include "../include/hhs_pass219_inherited_pass176_1_50.h"

#include <string.h>

static const char P176_I150_TERMINAL_RECEIPT_SHA256[] =
    "f43d26f4932074d8de5e001a4de4dee2435ce216c4112c4612547f63ef771173";
static const char P176_I150_ARTIFACT_SHA256[] =
    "b20edde645e16c13eb7629778e3bce3a5f4293684abb605c722a8254cdc86282";

static uint32_t p176_i150_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS176_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS176_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS176_VERSION_PATCH;
}

static int p176_i150_sha256(
    const char value[HHS_EXACT_PASS176_I150_SHA256_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS176_I150_SHA256_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS176_I150_SHA256_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass176_version(void) {
    return p176_i150_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass176_terminal_ide(
    const HHSExactPass176TerminalWitnessV1 *witness,
    HHSExactPass219InheritedPass176BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != p176_i150_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->terminal_pass176_completion != 1U ||
        witness->all_verifier_checks_green != 1U ||
        witness->runtime_os_public_root_preserved != 1U ||
        witness->pass176_additive_route_preserved != 1U ||
        witness->browser_evidence_green != 1U ||
        witness->frontend_non_authority_verified != 1U ||
        witness->singleton_vm81_admission_preserved != 1U ||
        witness->hash72_commit_streams != 1U ||
        witness->pass177_successor_preserved != 1U ||
        witness->independent_vm81_authority != 0U ||
        witness->independent_hash72_commit_authority != 0U ||
        witness->hash216_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!p176_i150_sha256(witness->terminal_receipt_sha256, P176_I150_TERMINAL_RECEIPT_SHA256) ||
        !p176_i150_sha256(witness->artifact_sha256, P176_I150_ARTIFACT_SHA256))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p176_i150_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS176_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->terminal_completion_claimed = 1U;
    out_binding->browser_evidence_bound = 1U;
    out_binding->runtime_os_public_root_preserved = 1U;
    out_binding->additive_pass176_route_preserved = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->singleton_vm81_admission_preserved = 1U;
    out_binding->hash72_commit_streams = 1U;
    memcpy(out_binding->terminal_receipt_sha256, P176_I150_TERMINAL_RECEIPT_SHA256,
           HHS_EXACT_PASS176_I150_SHA256_STRLEN);
    memcpy(out_binding->artifact_sha256, P176_I150_ARTIFACT_SHA256,
           HHS_EXACT_PASS176_I150_SHA256_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
