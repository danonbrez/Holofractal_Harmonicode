#ifndef HHS_PASS219_RAW5184_OCTONION_AUDIO_HYDRATION_1_0_H
#define HHS_PASS219_RAW5184_OCTONION_AUDIO_HYDRATION_1_0_H

#include "hhs_pass219_octonion_runtime_1_19.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_AUDIO5184_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_AUDIO5184_VERSION_MINOR 1U
#define HHS_EXACT_PASS219_AUDIO5184_VERSION_PATCH 0U

#define HHS_EXACT_PASS219_AUDIO5184_RAW_BITS HHS_EXACT_VM81_FRAME_BITS
#define HHS_EXACT_PASS219_AUDIO5184_RAW_BYTES HHS_EXACT_VM81_FRAME_BYTES
#define HHS_EXACT_PASS219_AUDIO5184_PCM_SAMPLES HHS_EXACT_VM81_CELLS
#define HHS_EXACT_PASS219_AUDIO5184_PHASE_QUADS 20U
#define HHS_EXACT_PASS219_AUDIO5184_PHASE_CHANNELS 8U
#define HHS_EXACT_PASS219_AUDIO5184_PILOT_CELL 80U
#define HHS_EXACT_PASS219_AUDIO5184_H36 36U
#define HHS_EXACT_PASS219_AUDIO5184_MONITOR_SCALE INT64_C(72057594037927936)
#define HHS_EXACT_PASS219_AUDIO5184_ROLE_SCALE INT64_C(281474976710656)
#define HHS_EXACT_PASS219_AUDIO5184_MONITOR_SAMPLES     (HHS_EXACT_PASS219_AUDIO5184_PHASE_QUADS * HHS_EXACT_PASS219_AUDIO5184_PHASE_CHANNELS)

typedef struct HHSExactPass219Audio5184PCM64V1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t sample_count;
    uint32_t bits_per_sample;
    uint64_t samples_bits[HHS_EXACT_PASS219_AUDIO5184_PCM_SAMPLES];
    uint8_t exact_bit_identity;
    uint8_t little_endian_byte_transport;
    uint8_t reversible_superframe;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219Audio5184PCM64V1;

typedef struct HHSExactPass219Audio5184PhaseChannelV1 {
    uint8_t phase72;
    uint8_t resonance36;
    uint8_t half_turn;
    int8_t signed_phase;
    uint8_t basis;
    uint8_t reserved0[3];
    int64_t monitor_pcm64;
} HHSExactPass219Audio5184PhaseChannelV1;

typedef struct HHSExactPass219Audio5184StereoTernaryV1 {
    int8_t numerator_role[3];
    int8_t denominator_role[3];
    uint8_t quotient_identity[3];
    uint8_t quotient_phase72[3];
    uint8_t left_mono_phase72[3];
    uint8_t right_mono_phase72[3];
    int64_t role_pcm64[3];
    uint8_t left_mono_yx_sum_xy;
    uint8_t right_mono_wz_sum_zw;
    uint8_t center_mono_xy_sum_colon_zw_sum;
    uint8_t exact_pcm64_role_bounds;
    uint8_t center_zero_over_zero_u0_mod_u72;
    uint8_t center_xy_sum_over_zw_sum_u0;
    uint8_t typed_quotient_only;
    uint8_t scalar_division_attempted;
    uint8_t scalar_projection_runtime_authority;
    uint8_t all_coordinates_close_to_identity;
    uint8_t reserved0[2];
} HHSExactPass219Audio5184StereoTernaryV1;

typedef struct HHSExactPass219Audio5184PhaseQuadV1 {
    uint8_t quad_index;
    uint8_t x_cell;
    uint8_t y_cell;
    uint8_t z_cell;
    uint8_t w_cell;
    uint8_t reserved0[3];
    uint64_t stereo_xy_left_bits;
    uint64_t stereo_xy_right_bits;
    uint64_t stereo_zw_left_bits;
    uint64_t stereo_zw_right_bits;
    HHSExactPass219OctonionStateV1 octonion;
    HHSExactPass219Audio5184PhaseChannelV1
        channels[HHS_EXACT_PASS219_AUDIO5184_PHASE_CHANNELS];
    HHSExactPass219Audio5184StereoTernaryV1 stereo_ternary;
} HHSExactPass219Audio5184PhaseQuadV1;

typedef struct HHSExactPass219Audio5184HydrationV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t raw_bits;
    uint32_t raw_bytes;
    uint32_t pcm_samples;
    uint32_t phase_quad_count;
    uint32_t monitor_sample_count;
    uint8_t pilot_cell;
    uint8_t exact_bit_roundtrip;
    uint8_t exact_phase_reconstruction;
    uint8_t dual_stereo_order_preserved;
    uint8_t ordered_octonion_preserved;
    uint8_t typed_ternary_quotient_preserved;
    uint8_t zero_over_zero_u0_mod_u72_preserved;
    uint8_t scalar_projection_runtime_authority;
    uint8_t h36_phase_coordinates_preserved;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[5];
    uint64_t pilot_pcm64_bits;
    HHSExactPass219Audio5184PhaseQuadV1
        quads[HHS_EXACT_PASS219_AUDIO5184_PHASE_QUADS];
    int64_t monitor_pcm64[HHS_EXACT_PASS219_AUDIO5184_MONITOR_SAMPLES];
} HHSExactPass219Audio5184HydrationV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_audio5184_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_audio5184_bitstring_import(
    const char *bits,
    size_t length,
    HHSExactVM81Frame *out_frame
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_audio5184_bitstring_export(
    const HHSExactVM81Frame *frame,
    char *out_bits,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_audio5184_bytes_import(
    const uint8_t *bytes,
    size_t length,
    HHSExactPass219Audio5184PCM64V1 *out_pcm
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_audio5184_bytes_export(
    const HHSExactPass219Audio5184PCM64V1 *pcm,
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_audio5184_frame_to_pcm64(
    const HHSExactVM81Frame *frame,
    HHSExactPass219Audio5184PCM64V1 *out_pcm
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_audio5184_pcm64_to_frame(
    const HHSExactPass219Audio5184PCM64V1 *pcm,
    HHSExactVM81Frame *out_frame
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_audio5184_hydrate(
    const HHSExactVM81Frame *frame,
    HHSExactPass219Audio5184HydrationV1 *out_hydration
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_audio5184_hydration_validate(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Audio5184HydrationV1 *hydration
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_audio5184_pipeline(
    const char *bits,
    size_t length,
    HHSExactPass219Audio5184PCM64V1 *out_pcm,
    HHSExactPass219Audio5184HydrationV1 *out_hydration
);

#ifdef __cplusplus
}
#endif

#endif
