#include "../include/hhs_pass219_global_raw5184_serialization_hydration_1_0.h"

#include <string.h>

static uint32_t hhs_p219_global_raw5184_version_word(void) {
    return (HHS_EXACT_PASS219_GLOBAL_RAW5184_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_GLOBAL_RAW5184_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_GLOBAL_RAW5184_VERSION_PATCH;
}

static HHSExactStatus hhs_exact_vm81_frame_global_serialization_validate(
    const HHSExactVM81Frame *frame
) {
    HHSExactPass219Audio5184PCM64V1 pcm;
    HHSExactPass219Audio5184HydrationV1 hydration;
    HHSExactStatus status;
    uint32_t cell;

    if (frame == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_audio5184_frame_to_pcm64(frame, &pcm);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (pcm.sample_count != HHS_EXACT_VM81_CELLS ||
        pcm.bits_per_sample != HHS_EXACT_VM81_WORD_BITS ||
        pcm.exact_bit_identity != 1U ||
        pcm.little_endian_byte_transport != 1U ||
        pcm.reversible_superframe != 1U ||
        pcm.canonical_mutation_authority != 0U ||
        pcm.canonical_hash72_authority != 0U ||
        pcm.canonical_hash216_authority != 0U ||
        pcm.canonical_persistence_authority != 0U ||
        pcm.floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (cell = 0U; cell < HHS_EXACT_VM81_CELLS; ++cell) {
        if (pcm.samples_bits[cell] != frame->words[cell])
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    status = hhs_exact_pass219_audio5184_hydrate(frame, &hydration);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_audio5184_hydration_validate(frame, &hydration);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (hydration.raw_bits != HHS_EXACT_VM81_FRAME_BITS ||
        hydration.raw_bytes != HHS_EXACT_VM81_FRAME_BYTES ||
        hydration.pcm_samples != HHS_EXACT_VM81_CELLS ||
        hydration.dual_stereo_order_preserved != 1U ||
        hydration.ordered_octonion_preserved != 1U ||
        hydration.typed_ternary_quotient_preserved != 1U ||
        hydration.zero_over_zero_u0_mod_u72_preserved != 1U ||
        hydration.scalar_projection_runtime_authority != 0U ||
        hydration.floating_point_authority != 0U ||
        hydration.canonical_mutation_authority != 0U ||
        hydration.canonical_hash72_authority != 0U ||
        hydration.canonical_hash216_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

uint32_t hhs_exact_pass219_global_raw5184_version(void) {
    return hhs_p219_global_raw5184_version_word();
}

HHSExactStatus hhs_exact_pass219_global_raw5184_descriptor(
    HHSExactPass219GlobalRaw5184DescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs_p219_global_raw5184_version_word();
    out_descriptor->raw_bits = HHS_EXACT_VM81_FRAME_BITS;
    out_descriptor->raw_bytes = HHS_EXACT_VM81_FRAME_BYTES;
    out_descriptor->vm81_cells = HHS_EXACT_VM81_CELLS;
    out_descriptor->pcm64_samples = HHS_EXACT_VM81_CELLS;
    out_descriptor->mandatory_public_frame_ingress = 1U;
    out_descriptor->mandatory_public_frame_egress = 1U;
    out_descriptor->mandatory_raw_bitstring = 1U;
    out_descriptor->mandatory_648_byte_bytecode_copy = 1U;
    out_descriptor->exact_bit_identity = 1U;
    out_descriptor->dual_stereo_hydration_required = 1U;
    out_descriptor->ternary_pcm64_required = 1U;
    out_descriptor->center_u0_closure_required = 1U;
    out_descriptor->scalar_projection_runtime_authority = 0U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->vm81_mutation_authority = 0U;
    out_descriptor->hash72_commit_authority = 0U;
    out_descriptor->hash216_commit_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_global_raw5184_validate_frame(
    const HHSExactVM81Frame *frame
) {
    return hhs_exact_vm81_frame_global_serialization_validate(frame);
}

HHSExactStatus hhs_exact_pass219_global_raw5184_bitstring_import(
    const char *bits,
    size_t length,
    HHSExactVM81Frame *out_frame
) {
    return hhs_exact_pass219_audio5184_bitstring_import(bits, length, out_frame);
}

HHSExactStatus hhs_exact_pass219_global_raw5184_bitstring_export(
    const HHSExactVM81Frame *frame,
    char *out_bits,
    size_t capacity,
    size_t *out_length
) {
    return hhs_exact_pass219_audio5184_bitstring_export(
        frame, out_bits, capacity, out_length);
}

HHSExactStatus hhs_exact_pass219_global_raw5184_bytecode_copy(
    const uint8_t *input,
    size_t length,
    uint8_t *output,
    size_t capacity,
    size_t *out_length
) {
    if (length != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    return hhs_x86_64_bytecode_copy_exact(
        input, length, output, capacity, out_length);
}
