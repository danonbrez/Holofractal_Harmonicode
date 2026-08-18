#include "../include/hhs_pass219_inherited_pass216_1_16.h"

#include <stddef.h>
#include <string.h>

static const uint32_t HHS_EXACT_PASS216_SELECTED_TOKEN_IDS[HHS_EXACT_PASS216_SELECTED_TOKEN_COUNT] = {
    450U, 6575U, 471U, 528U, 2827U, 322U, 278U
};
static const char HHS_EXACT_PASS216_PASS215_FINAL_HEAD[] =
    "b85ea7c340976a20a78f9c7d8d89a688a1b4f8fc";
static const char HHS_EXACT_PASS216_PASS215_FINAL_TREE[] =
    "17127e80a3f4852aeaedd1b807971fb4b4fba229";
static const char HHS_EXACT_PASS216_PASS215_MAIN_MERGE[] =
    "cc7a0d67d7d9e4bd1e800f62d5ef577cb4ab1086";
static const char HHS_EXACT_PASS216_PASS215_ARTIFACT_SHA256[] =
    "9e71ff3f48cd4da24c34854f8eadfa57f26d7c6ef5bddd1026c89e2ace63bf55";
static const char HHS_EXACT_PASS216_PUBLISHED_HEAD[] =
    "0ad2759a4379376244589aa3ee241e51d779df26";
static const char HHS_EXACT_PASS216_PUBLISHED_TREE[] =
    "b9ff48b17f1e3c8272cd8c5c7b4381df69d4c7e9";
static const char HHS_EXACT_PASS216_MERGE_COMMIT[] =
    "f10e453c5d7c7467cf5e57f6452958491fe763ad";
static const char HHS_EXACT_PASS216_CONTRACT_GIT_BLOB[] =
    "9e04e4aca8b127e009c0343ceb5e78092de40c43";
static const char HHS_EXACT_PASS216_ADDENDUM_GIT_BLOB[] =
    "3e4121afe2f5750283f5ef350c0afa416eb2addd";

static uint32_t hhs_exact_pass219_inherited_pass216_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS216_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS216_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS216_VERSION_PATCH;
}

static int hhs_exact_pass216_exact_text(
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

static int hhs_exact_pass216_exact_git_sha(
    const char value[HHS_EXACT_PASS216_GIT_SHA_STRLEN],
    const char expected[HHS_EXACT_PASS216_GIT_SHA_STRLEN]
) {
    return hhs_exact_pass216_exact_text(
        value,
        HHS_EXACT_PASS216_GIT_SHA_STRLEN,
        expected,
        HHS_EXACT_PASS216_GIT_SHA_LEN);
}

static int hhs_exact_pass216_exact_sha256(
    const char value[HHS_EXACT_PASS216_SHA256_HEX_STRLEN],
    const char expected[HHS_EXACT_PASS216_SHA256_HEX_STRLEN]
) {
    return hhs_exact_pass216_exact_text(
        value,
        HHS_EXACT_PASS216_SHA256_HEX_STRLEN,
        expected,
        HHS_EXACT_PASS216_SHA256_HEX_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass216_version(void) {
    return hhs_exact_pass219_inherited_pass216_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass216_alignment(
    const HHSExactPass216AlignmentWitnessV1 *witness,
    HHSExactPass219InheritedPass216BindingV1 *out_binding
) {
    size_t index;
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != hhs_exact_pass219_inherited_pass216_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->contract_layer_complete != 1U ||
        witness->parent_alignment_complete != 1U ||
        witness->runtime_optimization_implementation_claimed != 0U ||
        witness->runtime_optimization_required_before_pass217 != 0U ||
        witness->global_strict_mode_default != 0U ||
        witness->unchanged_identity_requires_reexecution != 0U ||
        witness->unchanged_identity_requires_identity_verification != 1U ||
        witness->changed_transition_requires_dependency_scoped_validation != 1U ||
        witness->full_system_reproof_required_by_default != 0U ||
        witness->deterministic_truth_gate_closed_by_default != 1U ||
        witness->pass219_must_inherit_pass215_pass216_pass217 != 1U ||
        witness->floating_point_canonical_authority != 0U ||
        witness->lossy_authoritative_compression_allowed != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (witness->selected_token_count != HHS_EXACT_PASS216_SELECTED_TOKEN_COUNT)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (index = 0U; index < HHS_EXACT_PASS216_SELECTED_TOKEN_COUNT; ++index) {
        if (witness->selected_token_ids[index] != HHS_EXACT_PASS216_SELECTED_TOKEN_IDS[index])
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (!hhs_exact_pass216_exact_git_sha(witness->pass215_final_head,
                                          HHS_EXACT_PASS216_PASS215_FINAL_HEAD) ||
        !hhs_exact_pass216_exact_git_sha(witness->pass215_final_tree,
                                          HHS_EXACT_PASS216_PASS215_FINAL_TREE) ||
        !hhs_exact_pass216_exact_git_sha(witness->pass215_main_merge,
                                          HHS_EXACT_PASS216_PASS215_MAIN_MERGE) ||
        !hhs_exact_pass216_exact_sha256(witness->pass215_artifact_sha256,
                                         HHS_EXACT_PASS216_PASS215_ARTIFACT_SHA256) ||
        !hhs_exact_pass216_exact_git_sha(witness->pass216_published_head,
                                          HHS_EXACT_PASS216_PUBLISHED_HEAD) ||
        !hhs_exact_pass216_exact_git_sha(witness->pass216_published_tree,
                                          HHS_EXACT_PASS216_PUBLISHED_TREE) ||
        !hhs_exact_pass216_exact_git_sha(witness->pass216_merge_commit,
                                          HHS_EXACT_PASS216_MERGE_COMMIT) ||
        !hhs_exact_pass216_exact_git_sha(witness->contract_git_blob,
                                          HHS_EXACT_PASS216_CONTRACT_GIT_BLOB) ||
        !hhs_exact_pass216_exact_git_sha(witness->addendum_git_blob,
                                          HHS_EXACT_PASS216_ADDENDUM_GIT_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs_exact_pass219_inherited_pass216_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS216_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->contract_alignment_bound = 1U;
    out_binding->pass215_terminal_reference_bound = 1U;
    out_binding->truth_gate_closed_by_default = 1U;
    out_binding->dependency_scoped_validation_bound = 1U;
    out_binding->unchanged_authority_reuse_bound = 1U;
    out_binding->global_strict_mode_default = 0U;
    out_binding->runtime_optimization_implementation_claimed = 0U;
    out_binding->runtime_optimization_roadmap_complete = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    out_binding->floating_point_canonical_authority = 0U;
    out_binding->lossy_authoritative_compression_allowed = 0U;
    memcpy(out_binding->pass216_published_head,
           witness->pass216_published_head,
           HHS_EXACT_PASS216_GIT_SHA_STRLEN);
    memcpy(out_binding->pass216_merge_commit,
           witness->pass216_merge_commit,
           HHS_EXACT_PASS216_GIT_SHA_STRLEN);
    memcpy(out_binding->pass215_artifact_sha256,
           witness->pass215_artifact_sha256,
           HHS_EXACT_PASS216_SHA256_HEX_STRLEN);
    memcpy(out_binding->contract_git_blob,
           witness->contract_git_blob,
           HHS_EXACT_PASS216_GIT_SHA_STRLEN);
    memcpy(out_binding->addendum_git_blob,
           witness->addendum_git_blob,
           HHS_EXACT_PASS216_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
