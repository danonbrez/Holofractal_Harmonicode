#include "../include/hhs_pass219_inherited_pass177_1_49.h"

#include <string.h>

static const char P177_I149_VALIDATED_AUTHORITY_HEAD[] =
    "15fa5a458c6755eab4d1af4b405b83b3467d45d9";
static const char P177_I149_AUTHORITY_RECEIPT_BLOB[] =
    "357365c6c55df87b1c199e64fb53d889c7315249";

static uint32_t p177_i149_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS177_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS177_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS177_VERSION_PATCH;
}

static int p177_i149_git(
    const char value[HHS_EXACT_PASS177_I149_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS177_I149_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS177_I149_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass177_version(void) {
    return p177_i149_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass177_creation_workflows(
    const HHSExactPass177WorkflowWitnessV1 *witness,
    HHSExactPass219InheritedPass177BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != p177_i149_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->contract_preserved != 1U ||
        witness->historical_merge_preserved != 1U ||
        witness->module_library_bound != 1U ||
        witness->project_factory_bound != 1U ||
        witness->workflow_engine_bound != 1U ||
        witness->browser_candidate_identity_bound != 1U ||
        witness->vm81_project_admission_bound != 1U ||
        witness->vm81_checkpoint_admission_bound != 1U ||
        witness->historical_stage_truth_preserved != 1U ||
        witness->pre_cumulative_validation_green != 1U ||
        witness->pass178_successor_preserved != 1U ||
        witness->terminal_pass177_completion != 0U ||
        witness->repair_forward_required != 1U ||
        witness->remaining_terminal_category_count !=
            HHS_EXACT_PASS177_I149_REMAINING_TERMINAL_CATEGORY_COUNT ||
        witness->independent_vm81_authority != 0U ||
        witness->independent_hash72_commit_authority != 0U ||
        witness->hash216_mutation_authority != 0U ||
        witness->browser_identity_authority != 0U ||
        witness->memory_checkpoint_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!p177_i149_git(witness->validated_authority_head, P177_I149_VALIDATED_AUTHORITY_HEAD) ||
        !p177_i149_git(witness->authority_receipt_blob, P177_I149_AUTHORITY_RECEIPT_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p177_i149_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS177_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_runtime_reachable = 1U;
    out_binding->browser_workflow_bound = 1U;
    out_binding->vm81_project_admission_bound = 1U;
    out_binding->vm81_checkpoint_admission_bound = 1U;
    out_binding->historical_stage_truth_preserved = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->terminal_completion_claimed = 0U;
    out_binding->repair_forward_required = 1U;
    out_binding->remaining_terminal_category_count =
        HHS_EXACT_PASS177_I149_REMAINING_TERMINAL_CATEGORY_COUNT;
    memcpy(
        out_binding->validated_authority_head,
        P177_I149_VALIDATED_AUTHORITY_HEAD,
        HHS_EXACT_PASS177_I149_GIT_SHA_STRLEN);
    memcpy(
        out_binding->authority_receipt_blob,
        P177_I149_AUTHORITY_RECEIPT_BLOB,
        HHS_EXACT_PASS177_I149_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
