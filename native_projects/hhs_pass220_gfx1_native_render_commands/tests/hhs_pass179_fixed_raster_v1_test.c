#include "hhs_pass179_fixed_raster_v1.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static const uint8_t *pixel(const uint8_t *fb, uint32_t stride, uint32_t x, uint32_t y) {
    return fb + (size_t)y * stride + (size_t)x * 4U;
}

int main(void) {
    enum { WIDTH = 4, HEIGHT = 4, STRIDE = WIDTH * 4 };
    uint8_t fb[HEIGHT * STRIDE];
    HHS179FixedPointV1 points[4];
    uint64_t first_digest;
    uint64_t second_digest;

    memset(fb, 0xff, sizeof(fb));
    assert(hhs179_fixed_clear_rgba8(
        fb, WIDTH, HEIGHT, STRIDE, UINT32_C(0x00000000)
    ) == HHS179_FIXED_RASTER_OK);

    points[0].x_q16_16 = 1 * HHS179_FIXED_ONE_Q16_16;
    points[0].y_q16_16 = 1 * HHS179_FIXED_ONE_Q16_16;
    points[0].rgba8 = UINT32_C(0xff0000ff);

    points[1].x_q16_16 = 2 * HHS179_FIXED_ONE_Q16_16 + HHS179_FIXED_ONE_Q16_16 / 2;
    points[1].y_q16_16 = 2 * HHS179_FIXED_ONE_Q16_16;
    points[1].rgba8 = UINT32_C(0x00ff00ff);

    points[2].x_q16_16 = -1 * HHS179_FIXED_ONE_Q16_16;
    points[2].y_q16_16 = 0;
    points[2].rgba8 = UINT32_C(0xffffffff);

    points[3].x_q16_16 = 0;
    points[3].y_q16_16 = 3 * HHS179_FIXED_ONE_Q16_16;
    points[3].rgba8 = UINT32_C(0x0000ffff);

    assert(hhs179_fixed_draw_points_q16_16(
        fb, WIDTH, HEIGHT, STRIDE, points, 4U
    ) == HHS179_FIXED_RASTER_OK);

    assert(pixel(fb, STRIDE, 1U, 1U)[0] == 0xffU);
    assert(pixel(fb, STRIDE, 1U, 1U)[1] == 0x00U);
    assert(pixel(fb, STRIDE, 1U, 1U)[2] == 0x00U);
    assert(pixel(fb, STRIDE, 1U, 1U)[3] == 0xffU);

    /* 2.5 rounds to x=3 in the exact Q16.16 reference rule. */
    assert(pixel(fb, STRIDE, 3U, 2U)[0] == 0x00U);
    assert(pixel(fb, STRIDE, 3U, 2U)[1] == 0xffU);
    assert(pixel(fb, STRIDE, 3U, 2U)[2] == 0x00U);
    assert(pixel(fb, STRIDE, 3U, 2U)[3] == 0xffU);

    assert(pixel(fb, STRIDE, 0U, 3U)[0] == 0x00U);
    assert(pixel(fb, STRIDE, 0U, 3U)[1] == 0x00U);
    assert(pixel(fb, STRIDE, 0U, 3U)[2] == 0xffU);
    assert(pixel(fb, STRIDE, 0U, 3U)[3] == 0xffU);

    first_digest = hhs179_fixed_framebuffer_digest64(fb, WIDTH, HEIGHT, STRIDE);
    assert(first_digest != 0U);

    memset(fb, 0xff, sizeof(fb));
    assert(hhs179_fixed_clear_rgba8(
        fb, WIDTH, HEIGHT, STRIDE, UINT32_C(0x00000000)
    ) == HHS179_FIXED_RASTER_OK);
    assert(hhs179_fixed_draw_points_q16_16(
        fb, WIDTH, HEIGHT, STRIDE, points, 4U
    ) == HHS179_FIXED_RASTER_OK);
    second_digest = hhs179_fixed_framebuffer_digest64(fb, WIDTH, HEIGHT, STRIDE);
    assert(first_digest == second_digest);

    puts("PASS hhs_pass179_fixed_raster_v1");
    return 0;
}
