#include "../include/hhs_pass219_harmonic36_default_binding_1_0.h"

#include <string.h>

static uint32_t h36_binding_version_word(void) {
    return (HHS_EXACT_PASS219_H36_BINDING_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_H36_BINDING_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_H36_BINDING_VERSION_PATCH;
}

uint32_t hhs_exact_pass219_h36_default_binding_version(void) {
    return h36_binding_version_word();
}

HHSExactStatus hhs_exact_pass219_h36_default_binding(
    HHSExactPass219H36DefaultBindingV1 *out_binding
) {
    if (out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = h36_binding_version_word();
    out_binding->frame_bits = HHS_EXACT_PASS219_H36_FRAME_BITS;
    out_binding->vm81_cells = HHS_EXACT_VM81_CELLS;
    out_binding->operation_count = HHS_EXACT_PASS219_H36_RULE_COUNT;
    out_binding->q144_cells = HHS_EXACT_PASS219_H36_WORD_COUNT;
    out_binding->word_bits = HHS_EXACT_PASS219_H36_WORD_BITS;

    out_binding->default_state_machine_required = 1U;
    out_binding->hydration_required = 1U;
    out_binding->compression_required = 1U;
    out_binding->phase_gear_required = 1U;
    out_binding->gpu_candidate_path_required = 1U;
    out_binding->hash216_vector_cache_required = 1U;
    out_binding->knowledge_graph_required = 1U;
    out_binding->quantum_like_branch_required = 1U;
    out_binding->rna_dna_transcription_required = 1U;
    out_binding->octonion_ternary_required = 1U;
    out_binding->loshu_sudoku_qudit_required = 1U;
    out_binding->native_36bit_execution_required = 1U;
    out_binding->multimodal_generalization_required = 1U;

    out_binding->singleton_vm81_authority_preserved = 1U;
    out_binding->independent_vm81_authority = 0U;
    out_binding->independent_hash72_authority = 0U;
    out_binding->independent_hash216_authority = 0U;
    out_binding->floating_point_canonical_authority = 0U;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_default_binding_validate(
    const HHSExactPass219H36DefaultBindingV1 *binding
) {
    HHSExactPass219H36DefaultBindingV1 expected;
    HHSExactStatus status;

    if (binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (binding->struct_size != sizeof(*binding) ||
        binding->version != h36_binding_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = hhs_exact_pass219_h36_default_binding(&expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return memcmp(binding, &expected, sizeof(expected)) == 0
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}
