#include "hhs_p166_word2vec.h"

#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    hhs_p166_manifest_geometry geometry;
    hhs_p166_projection projection;
    int32_t quantized = 0;
    int64_t dot = 0;
    uint8_t value = 0u;
    int32_t left[4] = {65536, 0, -65536, 32768};
    int32_t right[4] = {65536, 65536, -65536, 32768};

    (void)memset(&geometry, 0, sizeof(geometry));
    geometry.expected_bytes = 1024u;
    geometry.dimension = 4u;
    geometry.vocabulary_size = 4u;
    geometry.digest_sha256[0] = 1u;
    assert(hhs_p166_validate_geometry(&geometry) == HHS_P166_OK);
    geometry.dimension = HHS_P166_MAX_DIMENSION + 1u;
    assert(hhs_p166_validate_geometry(&geometry) == HHS_P166_RESOURCE_BOUND);
    geometry.dimension = 4u;

    assert(hhs_p166_quantize_q16_16(1, 2, &quantized) == HHS_P166_OK);
    assert(quantized == 32768);
    assert(hhs_p166_quantize_q16_16(-3, 2, &quantized) == HHS_P166_OK);
    assert(quantized == -98304);
    assert(hhs_p166_quantize_q16_16(1, 0, &quantized) == HHS_P166_INVALID_ARGUMENT);
    assert(hhs_p166_quantize_q16_16(INT64_MAX, 1, &quantized) == HHS_P166_CONVERSION_FAILED);

    assert(hhs_p166_dot_i32(left, right, 4u, &dot) == HHS_P166_OK);
    assert(dot == 9663676416LL);
    assert(hhs_p166_dot_i32(NULL, right, 4u, &dot) == HHS_P166_INVALID_ARGUMENT);

    assert(hhs_p166_projection_clear(&projection) == HHS_P166_OK);
    assert(hhs_p166_projection_popcount(&projection) == 0u);
    assert(hhs_p166_projection_set(&projection, 0u, 1u) == HHS_P166_OK);
    assert(hhs_p166_projection_set(&projection, 5183u, 1u) == HHS_P166_OK);
    assert(hhs_p166_projection_get(&projection, 0u, &value) == HHS_P166_OK && value == 1u);
    assert(hhs_p166_projection_get(&projection, 5183u, &value) == HHS_P166_OK && value == 1u);
    assert(hhs_p166_projection_popcount(&projection) == 2u);
    assert(hhs_p166_projection_set(&projection, 5184u, 1u) == HHS_P166_INVALID_ARGUMENT);
    assert(hhs_p166_projection_set(&projection, 0u, 0u) == HHS_P166_OK);
    assert(hhs_p166_projection_popcount(&projection) == 1u);

    puts("HHS_PASS_166_NATIVE_TESTS_PASS");
    return 0;
}
