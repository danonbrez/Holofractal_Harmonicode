#include "hhs_pass219_raw5184_octonion_audio_hydration_1_0.h"

#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <string.h>

static void fill_bits(char bits[HHS_EXACT_PASS219_AUDIO5184_RAW_BITS]) {
    size_t i;
    for (i = 0U; i < HHS_EXACT_PASS219_AUDIO5184_RAW_BITS; ++i)
        bits[i] = (((i * 13U + 7U) % 17U) < 8U) ? '1' : '0';
}

int main(void) {
    char bits[HHS_EXACT_PASS219_AUDIO5184_RAW_BITS];
    char replay[HHS_EXACT_PASS219_AUDIO5184_RAW_BITS];
    uint8_t bytes[HHS_EXACT_PASS219_AUDIO5184_RAW_BYTES];
    uint8_t bytes_replay[HHS_EXACT_PASS219_AUDIO5184_RAW_BYTES];
    HHSExactVM81Frame frame;
    HHSExactVM81Frame frame_from_pcm;
    HHSExactPass219Audio5184PCM64V1 pcm;
    HHSExactPass219Audio5184PCM64V1 pcm_from_bytes;
    HHSExactPass219Audio5184HydrationV1 hydration;
    size_t length = 0U;
    uint32_t q;
    int64_t s0, s18, s36, s54;

    fill_bits(bits);

    assert(hhs_exact_pass219_audio5184_bitstring_import(
               bits, sizeof(bits), &frame) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_audio5184_bitstring_export(
               &frame, replay, sizeof(replay), &length) == HHS_EXACT_STATUS_OK);
    assert(length == HHS_EXACT_PASS219_AUDIO5184_RAW_BITS);
    assert(memcmp(bits, replay, sizeof(bits)) == 0);

    assert(hhs_exact_vm81_frame_export_le(
               &frame, bytes, sizeof(bytes), &length) == HHS_EXACT_STATUS_OK);
    assert(length == HHS_EXACT_PASS219_AUDIO5184_RAW_BYTES);
    assert(hhs_exact_pass219_audio5184_bytes_import(
               bytes, sizeof(bytes), &pcm_from_bytes) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_audio5184_bytes_export(
               &pcm_from_bytes, bytes_replay, sizeof(bytes_replay), &length) ==
           HHS_EXACT_STATUS_OK);
    assert(length == HHS_EXACT_PASS219_AUDIO5184_RAW_BYTES);
    assert(memcmp(bytes, bytes_replay, sizeof(bytes)) == 0);

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
    assert(pcm.floating_point_authority == 0U);

    assert(hhs_exact_pass219_audio5184_pcm64_to_frame(&pcm, &frame_from_pcm) ==
           HHS_EXACT_STATUS_OK);
    assert(memcmp(&frame, &frame_from_pcm, sizeof(frame)) == 0);

    assert(hhs_exact_pass219_audio5184_hydrate(&frame, &hydration) ==
           HHS_EXACT_STATUS_OK);
    assert(hydration.raw_bits == 5184U);
    assert(hydration.raw_bytes == 648U);
    assert(hydration.pcm_samples == 81U);
    assert(hydration.phase_quad_count == 20U);
    assert(hydration.sine_sample_count == 160U);
    assert(hydration.pilot_cell == 80U);
    assert(hydration.exact_bit_roundtrip == 1U);
    assert(hydration.dual_stereo_order_preserved == 1U);
    assert(hydration.ordered_octonion_preserved == 1U);
    assert(hydration.typed_ternary_quotient_preserved == 1U);
    assert(hydration.zero_over_zero_u0_mod_u72_preserved == 1U);
    assert(hydration.scalar_projection_runtime_authority == 0U);
    assert(hydration.floating_point_authority == 0U);

    for (q = 0U; q < HHS_EXACT_PASS219_AUDIO5184_PHASE_QUADS; ++q) {
        const HHSExactPass219Audio5184PhaseQuadV1 *quad = &hydration.quads[q];
        const HHSExactPass219Audio5184StereoTernaryV1 *t = &quad->stereo_ternary;
        assert(quad->x_cell == (uint8_t)(4U * q + 0U));
        assert(quad->y_cell == (uint8_t)(4U * q + 1U));
        assert(quad->z_cell == (uint8_t)(4U * q + 2U));
        assert(quad->w_cell == (uint8_t)(4U * q + 3U));
        assert(t->numerator_role[0] == -1);
        assert(t->numerator_role[1] == 0);
        assert(t->numerator_role[2] == 1);
        assert(t->denominator_role[0] == -1);
        assert(t->denominator_role[1] == 0);
        assert(t->denominator_role[2] == 1);
        assert(t->role_pcm64[0] == INT64_MIN);
        assert(t->role_pcm64[1] == INT64_C(0));
        assert(t->role_pcm64[2] == INT64_MAX);
        assert(t->left_mono_phase72[0] == quad->octonion.yx);
        assert(t->left_mono_phase72[1] ==
               (uint8_t)(((uint16_t)quad->octonion.x + quad->octonion.y) % 72U));
        assert(t->left_mono_phase72[2] == quad->octonion.xy);
        assert(t->right_mono_phase72[0] == quad->octonion.wz);
        assert(t->right_mono_phase72[1] ==
               (uint8_t)(((uint16_t)quad->octonion.z + quad->octonion.w) % 72U));
        assert(t->right_mono_phase72[2] == quad->octonion.zw);
        assert(t->left_mono_yx_sum_xy == 1U);
        assert(t->right_mono_wz_sum_zw == 1U);
        assert(t->center_mono_xy_sum_colon_zw_sum == 1U);
        assert(t->center_zero_over_zero_u0_mod_u72 == 1U);
        assert(t->center_xy_sum_over_zw_sum_u0 == 1U);
        assert(t->scalar_projection_runtime_authority == 0U);
        assert(t->quotient_identity[0] == 1U);
        assert(t->quotient_identity[1] == 1U);
        assert(t->quotient_identity[2] == 1U);
        assert(t->quotient_phase72[0] == 0U);
        assert(t->quotient_phase72[1] == 0U);
        assert(t->quotient_phase72[2] == 0U);
    }

    assert(hhs_exact_pass219_audio5184_sine_pcm64(0U, &s0) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_audio5184_sine_pcm64(18U, &s18) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_audio5184_sine_pcm64(36U, &s36) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_audio5184_sine_pcm64(54U, &s54) == HHS_EXACT_STATUS_OK);
    assert(s0 == 0);
    assert(s18 == HHS_EXACT_PASS219_AUDIO5184_SINE_Q62_SCALE);
    assert(s36 == 0);
    assert(s54 == -HHS_EXACT_PASS219_AUDIO5184_SINE_Q62_SCALE);

    assert(hhs_exact_pass219_audio5184_hydration_validate(&frame, &hydration) ==
           HHS_EXACT_STATUS_OK);

    hydration.quads[0].stereo_ternary.role_pcm64[0] = INT64_C(-1);
    assert(hhs_exact_pass219_audio5184_hydration_validate(&frame, &hydration) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    fill_bits(bits);
    bits[17] = 'x';
    assert(hhs_exact_pass219_audio5184_bitstring_import(
               bits, sizeof(bits), &frame) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(hhs_exact_pass219_audio5184_bitstring_import(
               bits, sizeof(bits) - 1U, &frame) == HHS_EXACT_STATUS_RANGE_ERROR);

    return 0;
}
