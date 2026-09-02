#include "../include/hhs_pass219_inherited_pass180_1_46.h"

#include <string.h>

static const char P180_I146_HISTORICAL_GREEN_HEAD[] =
    "9d0e8ef4a60d450f69ef5bf4dab3ad1c18b30dba";
static const char P180_I146_FROZEN_I145_CHECKPOINT[] =
    "4762e1b5428f09a957905cc59669b7c9aeb36f06";
static const char P180_I146_I145_RECEIPT_BLOB[] =
    "331ca8095e5828dc8de0846f6c96c0336e260293";

static uint32_t p180_i146_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS180_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS180_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS180_VERSION_PATCH;
}

static int p180_i146_git(
    const char value[HHS_EXACT_PASS180_I146_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS180_I146_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS180_I146_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass180_version(void) {
    return p180_i146_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass180_application_factory(
    const HHSExactPass180ApplicationFactoryWitnessV1 *witness,
    HHSExactPass219InheritedPass180BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != p180_i146_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->historical_contract_preserved != 1U ||
        witness->historical_implementation_preserved != 1U ||
        witness->historical_ci_green != 1U ||
        witness->module_catalog_bound != 1U ||
        witness->workflow_catalog_bound != 1U ||
        witness->dependency_closure_bound != 1U ||
        witness->incremental_planning_bound != 1U ||
        witness->bounded_lifecycle_bound != 1U ||
        witness->eight_checkpoint_lifecycle_bound != 1U ||
        witness->deterministic_source_zip_bound != 1U ||
        witness->deterministic_project_replay_bound != 1U ||
        witness->visual_server_routes_bound != 1U ||
        witness->vm81_canonical_mutation_repair_bound != 1U ||
        witness->hash72_after_vm81_bound != 1U ||
        witness->external_success_nonfabrication_bound != 1U ||
        witness->singleton_vm81_bound != 1U ||
        witness->pass181_successor_preserved != 1U ||
        witness->i146_dependency_scoped_validation_green != 1U ||
        witness->terminal_pass180_completion != 1U ||
        witness->independent_vm81_authority != 0U ||
        witness->independent_hash72_authority != 0U ||
        witness->hash216_mutation_authority != 0U ||
        witness->floating_point_canonical_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p180_i146_git(
            witness->historical_green_head,
            P180_I146_HISTORICAL_GREEN_HEAD) ||
        !p180_i146_git(
            witness->frozen_i145_checkpoint,
            P180_I146_FROZEN_I145_CHECKPOINT) ||
        !p180_i146_git(
            witness->i145_validation_receipt_blob,
            P180_I146_I145_RECEIPT_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p180_i146_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS180_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_runtime_reachable = 1U;
    out_binding->module_catalog_bound = 1U;
    out_binding->workflow_catalog_bound = 1U;
    out_binding->dependency_closure_bound = 1U;
    out_binding->incremental_planning_bound = 1U;
    out_binding->bounded_lifecycle_bound = 1U;
    out_binding->eight_checkpoint_lifecycle_bound = 1U;
    out_binding->deterministic_source_zip_bound = 1U;
    out_binding->deterministic_project_replay_bound = 1U;
    out_binding->visual_server_routes_bound = 1U;
    out_binding->vm81_canonical_mutation_repair_bound = 1U;
    out_binding->hash72_after_vm81_bound = 1U;
    out_binding->external_success_nonfabrication_bound = 1U;
    out_binding->singleton_vm81_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->terminal_completion_claimed = 1U;
    out_binding->repair_forward_required = 0U;
    out_binding->remaining_terminal_obligation_count = 0U;
    memcpy(
        out_binding->historical_green_head,
        P180_I146_HISTORICAL_GREEN_HEAD,
        HHS_EXACT_PASS180_I146_GIT_SHA_STRLEN);
    memcpy(
        out_binding->frozen_i145_checkpoint,
        P180_I146_FROZEN_I145_CHECKPOINT,
        HHS_EXACT_PASS180_I146_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
