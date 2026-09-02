#include "../include/hhs_pass219_raw5184_octonion_audio_hydration_1_0.h"

#include <string.h>

static uint32_t hhs_p219_audio5184_version_word(void) {
    return (HHS_EXACT_PASS219_AUDIO5184_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_AUDIO5184_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_AUDIO5184_VERSION_PATCH;
}

static HHSExactStatus hhs_p219_audio5184_pcm_validate(
    const HHSExactPass219Audio5184PCM64V1 *pcm
) {
    if (pcm == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (pcm->struct_size < sizeof(*pcm) ||
        pcm->version != hhs_p219_audio5184_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (pcm->sample_count != HHS_EXACT_PASS219_AUDIO5184_PCM_SAMPLES ||
        pcm->bits_per_sample != HHS_EXACT_VM81_WORD_BITS ||
        pcm->exact_bit_identity != 1U ||
        pcm->little_endian_byte_transport != 1U ||
        pcm->reversible_superframe != 1U ||
        pcm->canonical_mutation_authority != 0U ||
        pcm->canonical_hash72_authority != 0U ||
        pcm->canonical_hash216_authority != 0U ||
        pcm->canonical_persistence_authority != 0U ||
        pcm->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_p219_audio5184_phase_channel(
    uint8_t basis,
    uint8_t phase,
    HHSExactPass219Audio5184PhaseChannelV1 *out
) {
    int16_t signed_phase;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (basis >= HHS_EXACT_PASS219_AUDIO5184_PHASE_CHANNELS ||
        phase >= HHS_EXACT_HASH72_LEN)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    signed_phase = phase >= HHS_EXACT_PASS219_AUDIO5184_H36
        ? (int16_t)((int16_t)(phase % HHS_EXACT_PASS219_AUDIO5184_H36) -
                    (int16_t)HHS_EXACT_PASS219_AUDIO5184_H36)
        : (int16_t)phase;

    memset(out, 0, sizeof(*out));
    out->phase72 = phase;
    out->resonance36 =
        (uint8_t)(phase % HHS_EXACT_PASS219_AUDIO5184_H36);
    out->half_turn =
        (uint8_t)(phase / HHS_EXACT_PASS219_AUDIO5184_H36);
    out->signed_phase = (int8_t)signed_phase;
    out->basis = basis;
    out->monitor_pcm64 = (int64_t)signed_phase * HHS_EXACT_PASS219_AUDIO5184_MONITOR_SCALE;

    if ((uint8_t)(
            out->resonance36 +
            HHS_EXACT_PASS219_AUDIO5184_H36 * out->half_turn) != phase)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static uint8_t hhs_p219_audio5184_phase_at(
    const HHSExactPass219OctonionStateV1 *state,
    uint8_t basis
) {
    switch (basis) {
        case HHS_EXACT_PHASE_X: return state->x;
        case HHS_EXACT_PHASE_Y: return state->y;
        case HHS_EXACT_PHASE_Z: return state->z;
        case HHS_EXACT_PHASE_W: return state->w;
        case HHS_EXACT_PHASE_XY: return state->xy;
        case HHS_EXACT_PHASE_YX: return state->yx;
        case HHS_EXACT_PHASE_ZW: return state->zw;
        case HHS_EXACT_PHASE_WZ: return state->wz;
        default: return HHS_EXACT_HASH72_LEN;
    }
}

static HHSExactStatus hhs_p219_audio5184_stereo_ternary(
    HHSExactPass219Audio5184StereoTernaryV1 *out
) {
    static const int8_t roles[3] = { -1, 0, 1 };
    uint8_t i;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out, 0, sizeof(*out));
    for (i = 0U; i < 3U; ++i) {
        out->numerator_role[i] = roles[i];
        out->denominator_role[i] = roles[i];
        out->quotient_identity[i] = 1U;
        out->quotient_phase72[i] = 0U;
    }
    out->center_zero_over_zero_u0_mod_u72 = 1U;
    out->center_xy_sum_over_zw_sum_u0 = 1U;
    out->typed_quotient_only = 1U;
    out->scalar_division_attempted = 0U;
    out->scalar_projection_runtime_authority = 0U;
    out->all_coordinates_close_to_identity = 1U;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_p219_audio5184_stereo_ternary_validate(
    const HHSExactPass219Audio5184StereoTernaryV1 *q
) {
    static const int8_t roles[3] = { -1, 0, 1 };
    uint8_t i;
    if (q == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (q->center_zero_over_zero_u0_mod_u72 != 1U ||
        q->center_xy_sum_over_zw_sum_u0 != 1U ||
        q->typed_quotient_only != 1U ||
        q->scalar_division_attempted != 0U ||
        q->scalar_projection_runtime_authority != 0U ||
        q->all_coordinates_close_to_identity != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (i = 0U; i < 3U; ++i) {
        if (q->numerator_role[i] != roles[i] ||
            q->denominator_role[i] != roles[i] ||
            q->quotient_identity[i] != 1U ||
            q->quotient_phase72[i] != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

uint32_t hhs_exact_pass219_audio5184_version(void) {
    return hhs_p219_audio5184_version_word();
}

HHSExactStatus hhs_exact_pass219_audio5184_bitstring_import(
    const char *bits,
    size_t length,
    HHSExactVM81Frame *out_frame
) {
    uint32_t cell;
    if (bits == NULL || out_frame == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (length != HHS_EXACT_PASS219_AUDIO5184_RAW_BITS)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_frame, 0, sizeof(*out_frame));
    for (cell = 0U; cell < HHS_EXACT_VM81_CELLS; ++cell) {
        uint64_t word = UINT64_C(0);
        uint32_t bit;
        for (bit = 0U; bit < HHS_EXACT_VM81_WORD_BITS; ++bit) {
            const char ch = bits[(size_t)cell * HHS_EXACT_VM81_WORD_BITS + bit];
            if (ch == '1') {
                word |= (UINT64_C(1) << bit);
            } else if (ch != '0') {
                memset(out_frame, 0, sizeof(*out_frame));
                return HHS_EXACT_STATUS_RANGE_ERROR;
            }
        }
        out_frame->words[cell] = word;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_audio5184_bitstring_export(
    const HHSExactVM81Frame *frame,
    char *out_bits,
    size_t capacity,
    size_t *out_length
) {
    uint32_t cell;
    if (frame == NULL || out_length == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_length = HHS_EXACT_PASS219_AUDIO5184_RAW_BITS;
    if (out_bits == NULL || capacity < HHS_EXACT_PASS219_AUDIO5184_RAW_BITS)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    for (cell = 0U; cell < HHS_EXACT_VM81_CELLS; ++cell) {
        uint32_t bit;
        for (bit = 0U; bit < HHS_EXACT_VM81_WORD_BITS; ++bit) {
            out_bits[(size_t)cell * HHS_EXACT_VM81_WORD_BITS + bit] =
                ((frame->words[cell] >> bit) & UINT64_C(1)) != 0U ? '1' : '0';
        }
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_audio5184_frame_to_pcm64(
    const HHSExactVM81Frame *frame,
    HHSExactPass219Audio5184PCM64V1 *out_pcm
) {
    uint32_t cell;
    if (frame == NULL || out_pcm == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_pcm, 0, sizeof(*out_pcm));
    out_pcm->struct_size = (uint32_t)sizeof(*out_pcm);
    out_pcm->version = hhs_p219_audio5184_version_word();
    out_pcm->sample_count = HHS_EXACT_PASS219_AUDIO5184_PCM_SAMPLES;
    out_pcm->bits_per_sample = HHS_EXACT_VM81_WORD_BITS;
    for (cell = 0U; cell < HHS_EXACT_VM81_CELLS; ++cell)
        out_pcm->samples_bits[cell] = frame->words[cell];
    out_pcm->exact_bit_identity = 1U;
    out_pcm->little_endian_byte_transport = 1U;
    out_pcm->reversible_superframe = 1U;
    out_pcm->canonical_mutation_authority = 0U;
    out_pcm->canonical_hash72_authority = 0U;
    out_pcm->canonical_hash216_authority = 0U;
    out_pcm->canonical_persistence_authority = 0U;
    out_pcm->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_audio5184_pcm64_to_frame(
    const HHSExactPass219Audio5184PCM64V1 *pcm,
    HHSExactVM81Frame *out_frame
) {
    uint32_t cell;
    HHSExactStatus status;
    if (pcm == NULL || out_frame == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_p219_audio5184_pcm_validate(pcm);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    for (cell = 0U; cell < HHS_EXACT_VM81_CELLS; ++cell)
        out_frame->words[cell] = pcm->samples_bits[cell];
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_audio5184_bytes_import(
    const uint8_t *bytes,
    size_t length,
    HHSExactPass219Audio5184PCM64V1 *out_pcm
) {
    HHSExactVM81Frame frame;
    HHSExactStatus status;
    if (bytes == NULL || out_pcm == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_vm81_frame_import_le(bytes, length, &frame);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_exact_pass219_audio5184_frame_to_pcm64(&frame, out_pcm);
}

HHSExactStatus hhs_exact_pass219_audio5184_bytes_export(
    const HHSExactPass219Audio5184PCM64V1 *pcm,
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    HHSExactVM81Frame frame;
    HHSExactStatus status;
    if (pcm == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_audio5184_pcm64_to_frame(pcm, &frame);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_exact_vm81_frame_export_le(
        &frame, out_bytes, capacity, out_length);
}

HHSExactStatus hhs_exact_pass219_audio5184_hydrate(
    const HHSExactVM81Frame *frame,
    HHSExactPass219Audio5184HydrationV1 *out_hydration
) {
    uint32_t q;
    if (frame == NULL || out_hydration == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_hydration, 0, sizeof(*out_hydration));
    out_hydration->struct_size = (uint32_t)sizeof(*out_hydration);
    out_hydration->version = hhs_p219_audio5184_version_word();
    out_hydration->raw_bits = HHS_EXACT_PASS219_AUDIO5184_RAW_BITS;
    out_hydration->raw_bytes = HHS_EXACT_PASS219_AUDIO5184_RAW_BYTES;
    out_hydration->pcm_samples = HHS_EXACT_PASS219_AUDIO5184_PCM_SAMPLES;
    out_hydration->phase_quad_count = HHS_EXACT_PASS219_AUDIO5184_PHASE_QUADS;
    out_hydration->monitor_sample_count =
        HHS_EXACT_PASS219_AUDIO5184_MONITOR_SAMPLES;
    out_hydration->pilot_cell = HHS_EXACT_PASS219_AUDIO5184_PILOT_CELL;
    out_hydration->pilot_pcm64_bits =
        frame->words[HHS_EXACT_PASS219_AUDIO5184_PILOT_CELL];

    for (q = 0U; q < HHS_EXACT_PASS219_AUDIO5184_PHASE_QUADS; ++q) {
        HHSExactPass219Audio5184PhaseQuadV1 *quad = &out_hydration->quads[q];
        HHSExactPass219OctonionSurfaceV1 surface;
        uint8_t basis;
        HHSExactStatus status;
        const uint8_t x_cell = (uint8_t)(4U * q);
        const uint8_t y_cell = (uint8_t)(x_cell + 1U);
        const uint8_t z_cell = (uint8_t)(x_cell + 2U);
        const uint8_t w_cell = (uint8_t)(x_cell + 3U);

        quad->quad_index = (uint8_t)q;
        quad->x_cell = x_cell;
        quad->y_cell = y_cell;
        quad->z_cell = z_cell;
        quad->w_cell = w_cell;
        quad->stereo_xy_left_bits = frame->words[x_cell];
        quad->stereo_xy_right_bits = frame->words[y_cell];
        quad->stereo_zw_left_bits = frame->words[z_cell];
        quad->stereo_zw_right_bits = frame->words[w_cell];

        status = hhs_exact_pass219_octonion_from_vm81(
            frame, x_cell, y_cell, z_cell, w_cell, &surface);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        quad->octonion = surface.state;

        if (hhs_p219_audio5184_stereo_ternary_validate(&a->stereo_ternary) !=
                HHS_EXACT_STATUS_OK ||
            memcmp(&a->stereo_ternary, &b->stereo_ternary,
                   sizeof(a->stereo_ternary)) != 0)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        for (basis = 0U; basis < HHS_EXACT_PASS219_AUDIO5184_PHASE_CHANNELS; ++basis) {
            const uint8_t phase = hhs_p219_audio5184_phase_at(
                &quad->octonion, basis);
            status = hhs_p219_audio5184_phase_channel(
                basis, phase, &quad->channels[basis]);
            if (status != HHS_EXACT_STATUS_OK)
                return status;
            out_hydration->monitor_pcm64[
                q * HHS_EXACT_PASS219_AUDIO5184_PHASE_CHANNELS + basis] =
                quad->channels[basis].monitor_pcm64;
        }
        status = hhs_p219_audio5184_stereo_ternary(&quad->stereo_ternary);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
    }

    out_hydration->exact_bit_roundtrip = 1U;
    out_hydration->exact_phase_reconstruction = 1U;
    out_hydration->dual_stereo_order_preserved = 1U;
    out_hydration->ordered_octonion_preserved = 1U;
    out_hydration->typed_ternary_quotient_preserved = 1U;
    out_hydration->zero_over_zero_u0_mod_u72_preserved = 1U;
    out_hydration->scalar_projection_runtime_authority = 0U;
    out_hydration->h36_phase_coordinates_preserved = 1U;
    out_hydration->canonical_mutation_authority = 0U;
    out_hydration->canonical_hash72_authority = 0U;
    out_hydration->canonical_hash216_authority = 0U;
    out_hydration->canonical_persistence_authority = 0U;
    out_hydration->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_audio5184_hydration_validate(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Audio5184HydrationV1 *hydration
) {
    HHSExactPass219Audio5184HydrationV1 expected;
    HHSExactStatus status;
    uint32_t q;

    if (frame == NULL || hydration == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (hydration->struct_size < sizeof(*hydration) ||
        hydration->version != hhs_p219_audio5184_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = hhs_exact_pass219_audio5184_hydrate(frame, &expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (hydration->raw_bits != expected.raw_bits ||
        hydration->raw_bytes != expected.raw_bytes ||
        hydration->pcm_samples != expected.pcm_samples ||
        hydration->phase_quad_count != expected.phase_quad_count ||
        hydration->monitor_sample_count != expected.monitor_sample_count ||
        hydration->pilot_cell != expected.pilot_cell ||
        hydration->pilot_pcm64_bits != expected.pilot_pcm64_bits ||
        hydration->exact_bit_roundtrip != 1U ||
        hydration->exact_phase_reconstruction != 1U ||
        hydration->dual_stereo_order_preserved != 1U ||
        hydration->ordered_octonion_preserved != 1U ||
        hydration->typed_ternary_quotient_preserved != 1U ||
        hydration->zero_over_zero_u0_mod_u72_preserved != 1U ||
        hydration->scalar_projection_runtime_authority != 0U ||
        hydration->h36_phase_coordinates_preserved != 1U ||
        hydration->canonical_mutation_authority != 0U ||
        hydration->canonical_hash72_authority != 0U ||
        hydration->canonical_hash216_authority != 0U ||
        hydration->canonical_persistence_authority != 0U ||
        hydration->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (q = 0U; q < HHS_EXACT_PASS219_AUDIO5184_PHASE_QUADS; ++q) {
        const HHSExactPass219Audio5184PhaseQuadV1 *a = &hydration->quads[q];
        const HHSExactPass219Audio5184PhaseQuadV1 *b = &expected.quads[q];
        uint8_t basis;
        if (a->quad_index != b->quad_index ||
            a->x_cell != b->x_cell ||
            a->y_cell != b->y_cell ||
            a->z_cell != b->z_cell ||
            a->w_cell != b->w_cell ||
            a->stereo_xy_left_bits != b->stereo_xy_left_bits ||
            a->stereo_xy_right_bits != b->stereo_xy_right_bits ||
            a->stereo_zw_left_bits != b->stereo_zw_left_bits ||
            a->stereo_zw_right_bits != b->stereo_zw_right_bits ||
            hhs_exact_pass219_octonion_validate_state(&a->octonion) !=
                HHS_EXACT_STATUS_OK)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        if (memcmp(&a->octonion, &b->octonion, sizeof(a->octonion)) != 0)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        for (basis = 0U; basis < HHS_EXACT_PASS219_AUDIO5184_PHASE_CHANNELS; ++basis) {
            if (a->channels[basis].phase72 != b->channels[basis].phase72 ||
                a->channels[basis].resonance36 != b->channels[basis].resonance36 ||
                a->channels[basis].half_turn != b->channels[basis].half_turn ||
                a->channels[basis].signed_phase != b->channels[basis].signed_phase ||
                a->channels[basis].basis != b->channels[basis].basis ||
                a->channels[basis].monitor_pcm64 != b->channels[basis].monitor_pcm64 ||
                hydration->monitor_pcm64[
                    q * HHS_EXACT_PASS219_AUDIO5184_PHASE_CHANNELS + basis] !=
                    expected.monitor_pcm64[
                    q * HHS_EXACT_PASS219_AUDIO5184_PHASE_CHANNELS + basis])
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_audio5184_pipeline(
    const char *bits,
    size_t length,
    HHSExactPass219Audio5184PCM64V1 *out_pcm,
    HHSExactPass219Audio5184HydrationV1 *out_hydration
) {
    HHSExactVM81Frame frame;
    HHSExactStatus status;
    if (bits == NULL || out_pcm == NULL || out_hydration == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_audio5184_bitstring_import(bits, length, &frame);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_audio5184_frame_to_pcm64(&frame, out_pcm);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_exact_pass219_audio5184_hydrate(&frame, out_hydration);
}
