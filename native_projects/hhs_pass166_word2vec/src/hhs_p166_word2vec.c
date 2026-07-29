#include "hhs_p166_word2vec.h"

#include <limits.h>
#include <string.h>

static uint64_t hhs_p166_abs_i64(int64_t value) {
    if (value >= 0) {
        return (uint64_t)value;
    }
    return (uint64_t)(-(value + 1)) + 1u;
}

hhs_p166_status hhs_p166_validate_geometry(const hhs_p166_manifest_geometry *geometry) {
    size_t index;
    uint8_t nonzero = 0u;
    if (geometry == NULL) {
        return HHS_P166_INVALID_ARGUMENT;
    }
    if (geometry->expected_bytes == 0u || geometry->dimension == 0u ||
        geometry->dimension > HHS_P166_MAX_DIMENSION || geometry->vocabulary_size == 0u ||
        geometry->vocabulary_size > HHS_P166_MAX_VOCABULARY) {
        return HHS_P166_RESOURCE_BOUND;
    }
    for (index = 0u; index < sizeof(geometry->digest_sha256); ++index) {
        nonzero = (uint8_t)(nonzero | geometry->digest_sha256[index]);
    }
    return nonzero == 0u ? HHS_P166_FORMAT_REJECTED : HHS_P166_OK;
}

hhs_p166_status hhs_p166_quantize_q16_16(int64_t numerator, int64_t denominator, int32_t *out) {
    uint64_t magnitude;
    uint64_t denominator_u;
    uint64_t scaled;
    uint64_t quotient;
    uint64_t remainder;
    uint64_t doubled;
    int negative;
    int64_t signed_value;
    if (out == NULL || denominator <= 0) {
        return HHS_P166_INVALID_ARGUMENT;
    }
    negative = numerator < 0;
    magnitude = hhs_p166_abs_i64(numerator);
    denominator_u = (uint64_t)denominator;
    if (magnitude > UINT64_MAX / (uint64_t)HHS_P166_QUANTIZATION_SCALE) {
        return HHS_P166_CONVERSION_FAILED;
    }
    scaled = magnitude * (uint64_t)HHS_P166_QUANTIZATION_SCALE;
    quotient = scaled / denominator_u;
    remainder = scaled % denominator_u;
    if (remainder > UINT64_MAX / 2u) {
        return HHS_P166_CONVERSION_FAILED;
    }
    doubled = remainder * 2u;
    if (doubled > denominator_u || (doubled == denominator_u && (quotient & 1u) != 0u)) {
        if (quotient == UINT64_MAX) {
            return HHS_P166_CONVERSION_FAILED;
        }
        ++quotient;
    }
    if ((!negative && quotient > (uint64_t)INT32_MAX) ||
        (negative && quotient > (uint64_t)INT32_MAX + 1u)) {
        return HHS_P166_CONVERSION_FAILED;
    }
    signed_value = negative ? -(int64_t)quotient : (int64_t)quotient;
    *out = (int32_t)signed_value;
    return HHS_P166_OK;
}

hhs_p166_status hhs_p166_dot_i32(const int32_t *left, const int32_t *right, size_t count, int64_t *out) {
    size_t index;
    int64_t total = 0;
    if (left == NULL || right == NULL || out == NULL || count == 0u || count > HHS_P166_MAX_DIMENSION) {
        return HHS_P166_INVALID_ARGUMENT;
    }
    for (index = 0u; index < count; ++index) {
        int64_t product = (int64_t)left[index] * (int64_t)right[index];
        if ((product > 0 && total > INT64_MAX - product) ||
            (product < 0 && total < INT64_MIN - product)) {
            return HHS_P166_INDEX_FAILED;
        }
        total += product;
    }
    *out = total;
    return HHS_P166_OK;
}

hhs_p166_status hhs_p166_projection_clear(hhs_p166_projection *projection) {
    if (projection == NULL) {
        return HHS_P166_INVALID_ARGUMENT;
    }
    (void)memset(projection->bytes, 0, sizeof(projection->bytes));
    return HHS_P166_OK;
}

hhs_p166_status hhs_p166_projection_set(hhs_p166_projection *projection, uint32_t coordinate, uint8_t value) {
    uint32_t byte_index;
    uint32_t bit_index;
    uint8_t mask;
    if (projection == NULL || coordinate >= HHS_P166_PROJECTION_BITS || value > 1u) {
        return HHS_P166_INVALID_ARGUMENT;
    }
    byte_index = coordinate / 8u;
    bit_index = coordinate % 8u;
    mask = (uint8_t)(1u << (7u - bit_index));
    if (value != 0u) {
        projection->bytes[byte_index] = (uint8_t)(projection->bytes[byte_index] | mask);
    } else {
        projection->bytes[byte_index] = (uint8_t)(projection->bytes[byte_index] & (uint8_t)~mask);
    }
    return HHS_P166_OK;
}

hhs_p166_status hhs_p166_projection_get(const hhs_p166_projection *projection, uint32_t coordinate, uint8_t *value_out) {
    uint32_t byte_index;
    uint32_t bit_index;
    if (projection == NULL || value_out == NULL || coordinate >= HHS_P166_PROJECTION_BITS) {
        return HHS_P166_INVALID_ARGUMENT;
    }
    byte_index = coordinate / 8u;
    bit_index = coordinate % 8u;
    *value_out = (uint8_t)((projection->bytes[byte_index] >> (7u - bit_index)) & 1u);
    return HHS_P166_OK;
}

uint32_t hhs_p166_projection_popcount(const hhs_p166_projection *projection) {
    uint32_t count = 0u;
    size_t index;
    if (projection == NULL) {
        return 0u;
    }
    for (index = 0u; index < sizeof(projection->bytes); ++index) {
        uint8_t value = projection->bytes[index];
        while (value != 0u) {
            count += (uint32_t)(value & 1u);
            value = (uint8_t)(value >> 1u);
        }
    }
    return count;
}
