#include "../include/hhs_pass219_inherited_pass179_1_47.h"

#include <string.h>

static const char P179_I147_VALIDATED_NUCLEUS_HEAD[] =
    "ff149faeadf3e31764138a2316052a013b28599c";
static const char P179_I147_NUCLEUS_RECEIPT_BLOB[] =
    "b6c7c9b42d3892de6ddaff354514ceafaa695b8e";
static const char P179_I147_INHERITED_I146_HEAD[] =
    "f03491cd6744e56e2e81a689416b94a6fb0ae9a4";

static uint32_t p179_i147_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS179_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS179_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS179_VERSION_PATCH;
}

static int p179_i147_git(
    const char value[HHS_EXACT_PASS179_I147_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS179_I147_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS179_I147_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass179_version(void) {
    return p179_i147_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass179_native_graphics(
    const HHSExactPass179NativeGraphicsWitnessV1 *witness,
    HHSExactPass219InheritedPass179BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != p179_i147_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->contract_preserved != 1U ||
        witness->native_c11_core_bound != 1U ||
        witness->exact_scene_types_bound != 1U ||
        witness->vm81_scene_admission_bound != 1U ||
        witness->post_vm81_hash72_evidence_bound != 1U ||
        witness->archival_hash216_identity_bound != 1U ||
        witness->software_renderer_bound != 1U ||
        witness->typed_shader_ir_bound != 1U ||
        witness->deterministic_png_capture_bound != 1U ||
        witness->webgpu_projection_bound != 1U ||
        witness->webgl2_projection_bound != 1U ||
        witness->threejs_projection_bound != 1U ||
        witness->lattice_run_nucleus_bound != 1U ||
        witness->motion_5184_nucleus_bound != 1U ||
        witness->served_graphics_studio_bound != 1U ||
        witness->pre_cumulative_validation_green != 1U ||
        witness->pass180_successor_preserved != 1U ||
        witness->terminal_pass179_completion != 0U ||
        witness->repair_forward_required != 1U ||
        witness->remaining_terminal_category_count !=
            HHS_EXACT_PASS179_I147_REMAINING_TERMINAL_CATEGORY_COUNT ||
        witness->independent_vm81_authority != 0U ||
        witness->independent_hash72_commit_authority != 0U ||
        witness->hash216_mutation_authority != 0U ||
        witness->gpu_mutation_authority != 0U ||
        witness->browser_mutation_authority != 0U ||
        witness->floating_point_canonical_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p179_i147_git(
            witness->validated_nucleus_head,
            P179_I147_VALIDATED_NUCLEUS_HEAD) ||
        !p179_i147_git(
            witness->nucleus_receipt_blob,
            P179_I147_NUCLEUS_RECEIPT_BLOB) ||
        !p179_i147_git(
            witness->inherited_i146_head,
            P179_I147_INHERITED_I146_HEAD))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p179_i147_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS179_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->native_runtime_reachable = 1U;
    out_binding->native_c11_core_bound = 1U;
    out_binding->exact_scene_types_bound = 1U;
    out_binding->vm81_scene_admission_bound = 1U;
    out_binding->post_vm81_hash72_evidence_bound = 1U;
    out_binding->archival_hash216_identity_bound = 1U;
    out_binding->software_renderer_bound = 1U;
    out_binding->typed_shader_ir_bound = 1U;
    out_binding->deterministic_png_capture_bound = 1U;
    out_binding->browser_projection_packets_bound = 1U;
    out_binding->golden_scene_nuclei_bound = 1U;
    out_binding->served_graphics_studio_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->terminal_completion_claimed = 0U;
    out_binding->repair_forward_required = 1U;
    out_binding->remaining_terminal_category_count =
        HHS_EXACT_PASS179_I147_REMAINING_TERMINAL_CATEGORY_COUNT;
    memcpy(
        out_binding->validated_nucleus_head,
        P179_I147_VALIDATED_NUCLEUS_HEAD,
        HHS_EXACT_PASS179_I147_GIT_SHA_STRLEN);
    memcpy(
        out_binding->nucleus_receipt_blob,
        P179_I147_NUCLEUS_RECEIPT_BLOB,
        HHS_EXACT_PASS179_I147_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
