#ifndef HHS_PASS219_GLOBAL_RAW5184_SERIALIZATION_HYDRATION_1_0_H
#define HHS_PASS219_GLOBAL_RAW5184_SERIALIZATION_HYDRATION_1_0_H

#include "hhs_pass219_raw5184_octonion_audio_hydration_1_0.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_GLOBAL_RAW5184_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_GLOBAL_RAW5184_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_GLOBAL_RAW5184_VERSION_PATCH 0U

typedef struct HHSExactPass219GlobalRaw5184DescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t raw_bits;
    uint32_t raw_bytes;
    uint32_t vm81_cells;
    uint32_t pcm64_samples;
    uint8_t mandatory_public_frame_ingress;
    uint8_t mandatory_public_frame_egress;
    uint8_t mandatory_raw_bitstring;
    uint8_t mandatory_648_byte_bytecode_copy;
    uint8_t exact_bit_identity;
    uint8_t dual_stereo_hydration_required;
    uint8_t ternary_pcm64_required;
    uint8_t center_u0_closure_required;
    uint8_t scalar_projection_runtime_authority;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t hash216_commit_authority;
    uint8_t reserved0[3];
} HHSExactPass219GlobalRaw5184DescriptorV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_global_raw5184_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_raw5184_descriptor(
    HHSExactPass219GlobalRaw5184DescriptorV1 *out_descriptor
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_raw5184_validate_frame(
    const HHSExactVM81Frame *frame
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_raw5184_bitstring_import(
    const char *bits,
    size_t length,
    HHSExactVM81Frame *out_frame
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_raw5184_bitstring_export(
    const HHSExactVM81Frame *frame,
    char *out_bits,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_raw5184_bytecode_copy(
    const uint8_t *input,
    size_t length,
    uint8_t *output,
    size_t capacity,
    size_t *out_length
);

#ifdef __cplusplus
}
#endif

#endif
