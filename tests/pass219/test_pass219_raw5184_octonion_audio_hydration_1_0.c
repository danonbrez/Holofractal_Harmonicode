#include "hhs_pass219_raw5184_octonion_audio_hydration_1_0.h"

#include <assert.h>
#include <string.h>

static void make_bits(char *bits) {
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_PASS219_AUDIO5184_RAW_BITS; ++i)
        bits[i] = ((i * 17U + 3U) % 11U) < 5U ? '1' : '0';
}

int main(void) {
    char bits[HHS_EXACT_PASS219_AUDIO5184_RAW_BITS];
    char roundtrip[HHS_EXACT_PASS219_AUDIO5184_RAW_BITS];
    uint8_t bytes[HHS_EXACT_PASS219_AUDIO5184_RAW_BYTES];
    size_t out_len = 0U;
    HHSExactVM81Frame frame;
    HHSExactVM81Frame frame2;
    HHSExactPass219Audio5184PCM64V1 pcm;
    HHSExactPass219Audio5184PCM64V1 pcm2;
    HHSExactPass219Audio5184HydrationV1 hydration;
    uint32_t i;

    make_bits(bits);

    assert(hhs_exact_pass219_audio5184_bitstring_import(
               bits, sizeof(bits), &frame) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_audio5184_bitstring_export(
               &frame, roundtrip, sizeof(roundtrip), &out_len) ==
           HHS_EXACT_STATUS_OK);
    assert(out_len == HHS_EXACT_PASS219_AUDIO5184_RAW_BITS);
    assert(memcmp(bits, roundtrip, sizeof(bits)) == 0);

    assert(hhs_exact_pass219_audio5184_frame_to_pcm64(&frame, &pcm) ==
           HHS_EXACT_STATUS_OK);
    assert(pcm.sample_count == 81U);
    assert(pcm.bits_per_sample == 64U);
    assert(pcm.exact_bit_identity == 1U);
    assert(pcm.little_endian_byte_transport == 1U);
    assert(pcm.reversible_superframe == 1U);
    assert(pcm.canonical_mutation_authority == 0U);
    assert(pcm.canonical_hash72_authority == 0U);
    assert(pcm.canonical_hash216_authority == 0U);
    assert(pcm.canonical_persistence_authority == 0U);
    assert(pcm.floating_point_authority == 0U);

    assert(hhs_exact_pass219_audio5184_pcm64_to_frame(&pcm, &frame2) ==
           HHS_EXACT_STATUS_OK);
    assert(memcmp(&frame, &frame2, sizeof(frame)) == 0);

    assert(hhs_exact_pass219_audio5184_bytes_export(
               &pcm, bytes, sizeof(bytes), &out_len) == HHS_EXACT_STATUS_OK);
    assert(out_len == HHS_EXACT_PASS219_AUDIO5184_RAW_BYTES);
    assert(hhs_exact_pass219_audio5184_bytes_import(
               bytes, sizeof(bytes), &pcm2) == HHS_EXACT_STATUS_OK);
    assert(memcmp(pcm.samples_bits, pcm2.samples_bits,
                  sizeof(pcm.samples_bits)) == 0);

    assert(hhs_exact_pass219_audio5184_hydrate(&frame, &hydration) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_audio5184_hydration_validate(
               &frame, &hydration) == HHS_EXACT_STATUS_OK);

    assert(hydration.raw_bits == 5184U);
    assert(hydration.raw_bytes == 648U);
    assert(hydration.pcm_samples == 81U);
    assert(hydration.phase_quad_count == 20U);
    assert(hydration.pilot_cell == 80U);
    assert(hydration.pilot_pcm64_bits == frame.words[80]);
    assert(hydration.exact_bit_roundtrip == 1U);
    assert(hydration.exact_phase_reconstruction == 1U);
    assert(hydration.dual_stereo_order_preserved == 1U);
    assert(hydration.ordered_octonion_preserved == 1U);
    assert(hydration.typed_ternary_quotient_preserved == 1U);
    assert(hydration.zero_over_zero_u0_mod_u72_preserved == 1U);
    assert(hydration.scalar_projection_runtime_authority == 0U);
    assert(hydration.h36_phase_coordinates_preserved == 1U);
    assert(hydration.canonical_mutation_authority == 0U);
    assert(hydration.canonical_hash72_authority == 0U);
    assert(hydration.canonical_hash216_authority == 0U);
    assert(hydration.canonical_persistence_authority == 0U);
    assert(hydration.floating_point_authority == 0U);

    for (i = 0U; i < 20U; ++i) {
        const HHSExactPass219Audio5184PhaseQuadV1 *q = &hydration.quads[i];
        uint32_t j;

        assert(q->quad_index == i);
        assert(q->x_cell == 4U * i);
        assert(q->y_cell == 4U * i + 1U);
        assert(q->z_cell == 4U * i + 2U);
        assert(q->w_cell == 4U * i + 3U);

        assert(q->stereo_ternary.numerator_role[0] == -1);
        assert(q->stereo_ternary.numerator_role[1] == 0);
        assert(q->stereo_ternary.numerator_role[2] == 1);
        assert(q->stereo_ternary.denominator_role[0] == -1);
        assert(q->stereo_ternary.denominator_role[1] == 0);
        assert(q->stereo_ternary.denominator_role[2] == 1);
        assert(q->stereo_ternary.role_pcm64[0] == INT64_MIN);
        assert(q->stereo_ternary.role_pcm64[1] == INT64_C(0));
        assert(q->stereo_ternary.role_pcm64[2] == INT64_MAX);

        assert(q->stereo_ternary.left_mono_phase72[0] == q->octonion.yx);
        assert(q->stereo_ternary.left_mono_phase72[1] ==
               (uint8_t)(((uint16_t)q->octonion.x + q->octonion.y) % 72U));
        assert(q->stereo_ternary.left_mono_phase72[2] == q->octonion.xy);
        assert(q->stereo_ternary.right_mono_phase72[0] == q->octonion.wz);
        assert(q->stereo_ternary.right_mono_phase72[1] ==
               (uint8_t)(((uint16_t)q->octonion.z + q->octonion.w) % 72U));
        assert(q->stereo_ternary.right_mono_phase72[2] == q->octonion.zw);

        assert(q->stereo_ternary.left_mono_yx_sum_xy == 1U);
        assert(q->stereo_ternary.right_mono_wz_sum_zw == 1U);
        assert(q->stereo_ternary.center_mono_xy_sum_colon_zw_sum == 1U);
        assert(q->stereo_ternary.exact_pcm64_role_bounds == 1U);
        assert(q->stereo_ternary.center_zero_over_zero_u0_mod_u72 == 1U);
        assert(q->stereo_ternary.center_xy_sum_over_zw_sum_u0 == 1U);
        assert(q->stereo_ternary.typed_quotient_only == 1U);
        assert(q->stereo_ternary.scalar_division_attempted == 0U);
        assert(q->stereo_ternary.scalar_projection_runtime_authority == 0U);
        assert(q->stereo_ternary.all_coordinates_close_to_identity == 1U);

        for (j = 0U; j < 3U; ++j) {
            assert(q->stereo_ternary.quotient_identity[j] == 1U);
            assert(q->stereo_ternary.quotient_phase72[j] == 0U);
        }
        for (j = 0U; j < 8U; ++j) {
            const HHSExactPass219Audio5184PhaseChannelV1 *ch =
                &q->channels[j];
            assert(ch->phase72 < 72U);
            assert(ch->resonance36 < 36U);
            assert(ch->half_turn < 2U);
            assert((uint32_t)ch->resonance36 + 36U * ch->half_turn ==
                   ch->phase72);
        }
    }

    hydration.quads[0].stereo_ternary.scalar_projection_runtime_authority = 1U;
    assert(hhs_exact_pass219_audio5184_hydration_validate(
               &frame, &hydration) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    hydration = (HHSExactPass219Audio5184HydrationV1){0};
    assert(hhs_exact_pass219_audio5184_hydrate(&frame, &hydration) ==
           HHS_EXACT_STATUS_OK);
    hydration.quads[0].stereo_ternary.role_pcm64[0] = INT64_C(-1);
    assert(hhs_exact_pass219_audio5184_hydration_validate(
               &frame, &hydration) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(hhs_exact_pass219_audio5184_bitstring_import(
               bits, sizeof(bits) - 1U, &frame2) == HHS_EXACT_STATUS_RANGE_ERROR);
    bits[17] = '2';
    assert(hhs_exact_pass219_audio5184_bitstring_import(
               bits, sizeof(bits), &frame2) == HHS_EXACT_STATUS_RANGE_ERROR);

    return 0;
}
