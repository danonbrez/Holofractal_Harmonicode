#include "../include/hhs_pass219_inherited_pass178_1_48.h"

#include <string.h>

static const char P178_I148_VALIDATED_NUCLEUS_HEAD[] =
    "1f63e08370d0e3c54390a7b4b3bec8ef042ddfa3";
static const char P178_I148_NUCLEUS_RECEIPT_BLOB[] =
    "1b74415c302f81e5fa424b8cf7e1d4daa036c529";

static uint32_t p178_i148_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS178_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS178_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS178_VERSION_PATCH;
}

static int p178_i148_git(
    const char value[HHS_EXACT_PASS178_I148_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS178_I148_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS178_I148_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass178_version(void) {
    return p178_i148_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass178_exact_physics(
    const HHSExactPass178PhysicsWitnessV1 *witness,
    HHSExactPass219InheritedPass178BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != p178_i148_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->contract_preserved != 1U ||
        witness->exact_rational_complex_bound != 1U ||
        witness->algebraic_root_branch_bound != 1U ||
        witness->constraint_graph_bound != 1U ||
        witness->relativistic_nucleus_bound != 1U ||
        witness->quantum_cayley_nucleus_bound != 1U ||
        witness->native_public_abi_bound != 1U ||
        witness->vm81_state_admission_bound != 1U ||
        witness->deterministic_replay_bound != 1U ||
        witness->immutable_render_packet_bound != 1U ||
        witness->served_physics_studio_bound != 1U ||
        witness->pre_cumulative_validation_green != 1U ||
        witness->pass179_successor_preserved != 1U ||
        witness->terminal_pass178_completion != 0U ||
        witness->repair_forward_required != 1U ||
        witness->complete_historical_constraint_corpus != 0U ||
        witness->remaining_terminal_category_count !=
            HHS_EXACT_PASS178_I148_REMAINING_TERMINAL_CATEGORY_COUNT ||
        witness->independent_vm81_authority != 0U ||
        witness->independent_hash72_commit_authority != 0U ||
        witness->hash216_mutation_authority != 0U ||
        witness->renderer_mutation_authority != 0U ||
        witness->gpu_mutation_authority != 0U ||
        witness->browser_mutation_authority != 0U ||
        witness->floating_point_canonical_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!p178_i148_git(witness->validated_nucleus_head, P178_I148_VALIDATED_NUCLEUS_HEAD) ||
        !p178_i148_git(witness->nucleus_receipt_blob, P178_I148_NUCLEUS_RECEIPT_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p178_i148_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS178_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->native_runtime_reachable = 1U;
    out_binding->exact_physics_nucleus_bound = 1U;
    out_binding->vm81_state_admission_bound = 1U;
    out_binding->deterministic_replay_bound = 1U;
    out_binding->immutable_render_packet_bound = 1U;
    out_binding->served_physics_studio_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->terminal_completion_claimed = 0U;
    out_binding->repair_forward_required = 1U;
    out_binding->complete_historical_constraint_corpus = 0U;
    out_binding->remaining_terminal_category_count = HHS_EXACT_PASS178_I148_REMAINING_TERMINAL_CATEGORY_COUNT;
    memcpy(out_binding->validated_nucleus_head, P178_I148_VALIDATED_NUCLEUS_HEAD, HHS_EXACT_PASS178_I148_GIT_SHA_STRLEN);
    memcpy(out_binding->nucleus_receipt_blob, P178_I148_NUCLEUS_RECEIPT_BLOB, HHS_EXACT_PASS178_I148_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
