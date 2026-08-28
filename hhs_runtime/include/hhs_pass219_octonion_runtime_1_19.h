#ifndef HHS_PASS219_OCTONION_RUNTIME_1_19_H
#define HHS_PASS219_OCTONION_RUNTIME_1_19_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_OCTONION_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_OCTONION_VERSION_MINOR 19U
#define HHS_EXACT_PASS219_OCTONION_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_OCTONION_CHANNEL_COUNT HHS_EXACT_PHASE_BASIS_COUNT
#define HHS_EXACT_PASS219_OCTONION_PRODUCT_COUNT HHS_EXACT_PHASE_PAIR_COUNT

typedef enum HHSExactPass219OctonionOrientation {
    HHS_EXACT_PASS219_OCTONION_COMPOSED = 0,
    HHS_EXACT_PASS219_OCTONION_DIRECT = 1,
    HHS_EXACT_PASS219_OCTONION_REVERSED = 2
} HHSExactPass219OctonionOrientation;

typedef struct HHSExactPass219OctonionDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t ordered_basis_count;
    uint32_t ordered_product_count;
    uint32_t vm81_projection_supported;
    uint32_t exact_integer_phase_arithmetic;
    uint32_t floating_point_authority;
    uint32_t vm81_mutation_authority;
    uint32_t hash72_commit_authority;
} HHSExactPass219OctonionDescriptorV1;

typedef struct HHSExactPass219OctonionStateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t x;
    uint8_t y;
    uint8_t z;
    uint8_t w;
    uint8_t xy;
    uint8_t yx;
    uint8_t zw;
    uint8_t wz;
} HHSExactPass219OctonionStateV1;

typedef struct HHSExactPass219OctonionProductV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t left_basis;
    uint8_t right_basis;
    uint8_t left_phase;
    uint8_t right_phase;
    uint8_t raw_additive_phase;
    uint8_t phase;
    uint8_t orientation;
    uint8_t closure;
    uint8_t ordered_pair_index;
    uint8_t reserved0;
    uint16_t ordered_tag;
} HHSExactPass219OctonionProductV1;

typedef struct HHSExactPass219OctonionSurfaceV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t product_count;
    uint32_t noncommutative_generator_pairs;
    HHSExactPass219OctonionStateV1 state;
    HHSExactPass219OctonionProductV1 products[HHS_EXACT_PASS219_OCTONION_PRODUCT_COUNT];
} HHSExactPass219OctonionSurfaceV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_octonion_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_octonion_descriptor(
    HHSExactPass219OctonionDescriptorV1 *out_descriptor
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_octonion_expand(
    uint8_t x,
    uint8_t y,
    uint8_t z,
    uint8_t w,
    HHSExactPass219OctonionStateV1 *out_state
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_octonion_channel_phase(
    const HHSExactPass219OctonionStateV1 *state,
    uint8_t basis,
    uint8_t *out_phase
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_octonion_multiply(
    const HHSExactPass219OctonionStateV1 *state,
    uint8_t left_basis,
    uint8_t right_basis,
    HHSExactPass219OctonionProductV1 *out_product
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_octonion_surface(
    uint8_t x,
    uint8_t y,
    uint8_t z,
    uint8_t w,
    HHSExactPass219OctonionSurfaceV1 *out_surface
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_octonion_from_vm81(
    const HHSExactVM81Frame *frame,
    uint8_t x_cell,
    uint8_t y_cell,
    uint8_t z_cell,
    uint8_t w_cell,
    HHSExactPass219OctonionSurfaceV1 *out_surface
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_octonion_validate_state(
    const HHSExactPass219OctonionStateV1 *state
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_octonion_validate_surface(
    const HHSExactPass219OctonionSurfaceV1 *surface
);

#ifdef __cplusplus
}
#endif

#endif
