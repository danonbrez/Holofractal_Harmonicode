#ifndef HHS_PASS179_FIXED_RASTER_V1_H
#define HHS_PASS179_FIXED_RASTER_V1_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS179_FIXED_ONE_Q16_16 65536
#define HHS179_FIXED_POINT_BYTES 12U

typedef enum HHS179FixedRasterStatusV1 {
    HHS179_FIXED_RASTER_OK = 0,
    HHS179_FIXED_RASTER_ERR_ARGUMENT = 1,
    HHS179_FIXED_RASTER_ERR_BOUNDS = 2,
    HHS179_FIXED_RASTER_ERR_STRIDE = 3
} HHS179FixedRasterStatusV1;

typedef struct HHS179FixedPointV1 {
    int32_t x_q16_16;
    int32_t y_q16_16;
    uint32_t rgba8;
} HHS179FixedPointV1;

#ifdef __cplusplus
static_assert(sizeof(HHS179FixedPointV1) == HHS179_FIXED_POINT_BYTES, "HHS179FixedPointV1 must remain 12 bytes");
#else
_Static_assert(sizeof(HHS179FixedPointV1) == HHS179_FIXED_POINT_BYTES, "HHS179FixedPointV1 must remain 12 bytes");
#endif

HHS179FixedRasterStatusV1 hhs179_fixed_clear_rgba8(
    uint8_t *framebuffer,
    uint32_t width,
    uint32_t height,
    uint32_t stride_bytes,
    uint32_t rgba8
);

HHS179FixedRasterStatusV1 hhs179_fixed_draw_points_q16_16(
    uint8_t *framebuffer,
    uint32_t width,
    uint32_t height,
    uint32_t stride_bytes,
    const HHS179FixedPointV1 *points,
    size_t point_count
);

uint64_t hhs179_fixed_framebuffer_digest64(
    const uint8_t *framebuffer,
    uint32_t width,
    uint32_t height,
    uint32_t stride_bytes
);

#ifdef __cplusplus
}
#endif

#endif
