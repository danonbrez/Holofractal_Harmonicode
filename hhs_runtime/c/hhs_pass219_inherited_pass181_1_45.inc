#include "../include/hhs_pass219_inherited_pass181_1_45.h"

#include <string.h>

static const char P181_I145_HISTORICAL_GREEN_HEAD[] =
    "3ae56827b27500c2c8187126d5825a901d4feb40";
static const char P181_I145_FROZEN_I144_CHECKPOINT[] =
    "132694cee0af4a43113ddc4c50f867c084a22bae";

static uint32_t p181_i145_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS181_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS181_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS181_VERSION_PATCH;
}

static int p181_i145_git(
    const char value[HHS_EXACT_PASS181_I145_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS181_I145_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS181_I145_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass181_version(void) {
    return p181_i145_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass181_graphics_hydration(
    const HHSExactPass181GraphicsHydrationWitnessV1 *witness,
    HHSExactPass219InheritedPass181BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != p181_i145_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->historical_contract_preserved != 1U ||
        witness->historical_implementation_preserved != 1U ||
        witness->historical_ci_green != 1U ||
        witness->read_only_reference_ingestion_bound != 1U ||
        witness->canonical_mp4_timeline_bound != 1U ||
        witness->native_recipe_residual_bound != 1U ||
        witness->bounded_optimization_bound != 1U ||
        witness->vector_hydration_bound != 1U ||
        witness->governed_constraint_registry_bound != 1U ||
        witness->vm81_admission_repair_bound != 1U ||
        witness->legacy_direct_promotion_disabled != 1U ||
        witness->cold_restart_constraint_registry_replay_bound != 1U ||
        witness->singleton_vm81_bound != 1U ||
        witness->hash72_evidence_bound != 1U ||
        witness->hash216_archival_only_bound != 1U ||
        witness->pass182_successor_preserved != 1U ||
        witness->terminal_pass181_completion != 0U ||
        witness->remaining_terminal_obligation_count !=
            HHS_EXACT_PASS181_I145_REMAINING_TERMINAL_OBLIGATIONS ||
        witness->independent_vm81_authority != 0U ||
        witness->independent_hash72_authority != 0U ||
        witness->hash216_mutation_authority != 0U ||
        witness->floating_point_canonical_authority != 0U ||
        witness->threejs_final_frame_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p181_i145_git(
            witness->historical_green_head,
            P181_I145_HISTORICAL_GREEN_HEAD) ||
        !p181_i145_git(
            witness->frozen_i144_checkpoint,
            P181_I145_FROZEN_I144_CHECKPOINT))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p181_i145_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS181_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_runtime_reachable = 1U;
    out_binding->read_only_reference_ingestion_bound = 1U;
    out_binding->canonical_mp4_timeline_bound = 1U;
    out_binding->native_recipe_residual_bound = 1U;
    out_binding->bounded_optimization_bound = 1U;
    out_binding->vector_hydration_bound = 1U;
    out_binding->governed_constraint_registry_bound = 1U;
    out_binding->vm81_admission_repair_bound = 1U;
    out_binding->legacy_direct_promotion_disabled = 1U;
    out_binding->cold_restart_constraint_registry_replay_bound = 1U;
    out_binding->singleton_vm81_bound = 1U;
    out_binding->hash72_evidence_bound = 1U;
    out_binding->hash216_archival_only_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->terminal_completion_claimed = 0U;
    out_binding->repair_forward_required = 1U;
    out_binding->remaining_terminal_obligation_count =
        HHS_EXACT_PASS181_I145_REMAINING_TERMINAL_OBLIGATIONS;
    memcpy(
        out_binding->historical_green_head,
        P181_I145_HISTORICAL_GREEN_HEAD,
        HHS_EXACT_PASS181_I145_GIT_SHA_STRLEN);
    memcpy(
        out_binding->frozen_i144_checkpoint,
        P181_I145_FROZEN_I144_CHECKPOINT,
        HHS_EXACT_PASS181_I145_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
