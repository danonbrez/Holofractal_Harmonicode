#include "hhs_pass179_fixed_raster_v1.h"

#include <limits.h>

static void put_rgba8(uint8_t *pixel, uint32_t rgba8) {
    pixel[0] = (uint8_t)((rgba8 >> 24) & 0xffU);
    pixel[1] = (uint8_t)((rgba8 >> 16) & 0xffU);
    pixel[2] = (uint8_t)((rgba8 >> 8) & 0xffU);
    pixel[3] = (uint8_t)(rgba8 & 0xffU);
}

static int32_t q16_16_round_to_i32(int32_t value) {
    if (value >= 0) {
        return (value + (HHS179_FIXED_ONE_Q16_16 / 2)) / HHS179_FIXED_ONE_Q16_16;
    }
    return -(((-value) + (HHS179_FIXED_ONE_Q16_16 / 2)) / HHS179_FIXED_ONE_Q16_16);
}

static HHS179FixedRasterStatusV1 validate_surface(
    const uint8_t *framebuffer,
    uint32_t width,
    uint32_t height,
    uint32_t stride_bytes
) {
    uint64_t minimum_stride;
    if (framebuffer == NULL || width == 0U || height == 0U) {
        return HHS179_FIXED_RASTER_ERR_ARGUMENT;
    }
    minimum_stride = (uint64_t)width * UINT64_C(4);
    if (minimum_stride > UINT32_MAX || stride_bytes < (uint32_t)minimum_stride) {
        return HHS179_FIXED_RASTER_ERR_STRIDE;
    }
    return HHS179_FIXED_RASTER_OK;
}

HHS179FixedRasterStatusV1 hhs179_fixed_clear_rgba8(
    uint8_t *framebuffer,
    uint32_t width,
    uint32_t height,
    uint32_t stride_bytes,
    uint32_t rgba8
) {
    HHS179FixedRasterStatusV1 status = validate_surface(
        framebuffer, width, height, stride_bytes
    );
    uint32_t y;
    uint32_t x;
    if (status != HHS179_FIXED_RASTER_OK) return status;
    for (y = 0U; y < height; ++y) {
        uint8_t *row = framebuffer + (size_t)y * stride_bytes;
        for (x = 0U; x < width; ++x) {
            put_rgba8(row + (size_t)x * 4U, rgba8);
        }
    }
    return HHS179_FIXED_RASTER_OK;
}

HHS179FixedRasterStatusV1 hhs179_fixed_draw_points_q16_16(
    uint8_t *framebuffer,
    uint32_t width,
    uint32_t height,
    uint32_t stride_bytes,
    const HHS179FixedPointV1 *points,
    size_t point_count
) {
    HHS179FixedRasterStatusV1 status = validate_surface(
        framebuffer, width, height, stride_bytes
    );
    size_t i;
    if (status != HHS179_FIXED_RASTER_OK) return status;
    if (point_count != 0U && points == NULL) {
        return HHS179_FIXED_RASTER_ERR_ARGUMENT;
    }
    for (i = 0U; i < point_count; ++i) {
        const int32_t x = q16_16_round_to_i32(points[i].x_q16_16);
        const int32_t y = q16_16_round_to_i32(points[i].y_q16_16);
        uint8_t *pixel;
        if (x < 0 || y < 0 || (uint32_t)x >= width || (uint32_t)y >= height) {
            continue;
        }
        pixel = framebuffer + (size_t)(uint32_t)y * stride_bytes + (size_t)(uint32_t)x * 4U;
        put_rgba8(pixel, points[i].rgba8);
    }
    return HHS179_FIXED_RASTER_OK;
}

uint64_t hhs179_fixed_framebuffer_digest64(
    const uint8_t *framebuffer,
    uint32_t width,
    uint32_t height,
    uint32_t stride_bytes
) {
    uint64_t h = UINT64_C(14695981039346656037);
    uint32_t y;
    uint32_t x;
    if (validate_surface(framebuffer, width, height, stride_bytes) != HHS179_FIXED_RASTER_OK) {
        return 0U;
    }
    for (y = 0U; y < height; ++y) {
        const uint8_t *row = framebuffer + (size_t)y * stride_bytes;
        for (x = 0U; x < width * 4U; ++x) {
            h ^= (uint64_t)row[x];
            h *= UINT64_C(1099511628211);
        }
    }
    return h;
}
