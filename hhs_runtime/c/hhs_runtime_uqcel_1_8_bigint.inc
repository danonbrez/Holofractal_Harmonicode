#include "../include/hhs_runtime_uqcel_1_8.h"
#include <string.h>

static const uint8_t HHS_EXACT_UQCEL_SOURCE_SHA256[HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES] = {
    0x7eU, 0xb0U, 0xccU, 0x57U, 0x07U, 0xa4U, 0xa5U, 0x8aU,
    0x5aU, 0x8eU, 0x48U, 0x79U, 0xe0U, 0xe2U, 0xe3U, 0xbdU,
    0xabU, 0x22U, 0xc1U, 0x5fU, 0xe4U, 0x50U, 0x3fU, 0xb3U,
    0xa3U, 0xb0U, 0xe1U, 0x65U, 0x96U, 0x34U, 0x3dU, 0x42U
};

static uint32_t hhs_exact_uqcel_version_word(void) {
    return (HHS_EXACT_UQCEL_VERSION_MAJOR << 16) |
           (HHS_EXACT_UQCEL_VERSION_MINOR << 8) |
           HHS_EXACT_UQCEL_VERSION_PATCH;
}

/* ============================================================
 * PRIVATE CANONICAL HASH72 / HASH216 COPY
 *
 * These helpers intentionally copy the inherited canonical byte-mixing
 * algorithm under UQCEL-private static names.  This keeps the historical
 * hhs_runtime_abi.c one-file link contract intact while producing exactly the
 * same receipt bytes as hhs_runtime/src/hhs_hash216.c when that implementation
 * is linked.  Equivalence is covered by Pass 219 tests.
 * ============================================================
 */

static uint64_t hhs_exact_uqcel_hash_mix64(uint64_t value) {
    value ^= value >> 33U;
    value *= UINT64_C(0xff51afd7ed558ccd);
    value ^= value >> 33U;
    value *= UINT64_C(0xc4ceb9fe1a85ec53);
    value ^= value >> 33U;
    return value;
}

static uint64_t hhs_exact_uqcel_fold_bytes(const void *data, size_t size) {
    const uint8_t *bytes = (const uint8_t *)data;
    uint64_t state = UINT64_C(0x179971179971);
    size_t i;
    for (i = 0U; i < size; ++i) {
        state ^= ((uint64_t)bytes[i] << ((i % 8U) * 8U));
        state = hhs_exact_uqcel_hash_mix64(state + (uint64_t)i + UINT64_C(1));
    }
    return state;
}

static char hhs_exact_uqcel_hash72_symbol(uint64_t value) {
    return HHS_EXACT_HASH72_ALPHABET[value % HHS_EXACT_HASH72_LEN];
}

static void hhs_exact_uqcel_hash72_bytes(
    const void *data,
    size_t size,
    char out_hash72[HHS_EXACT_HASH72_STRLEN]
) {
    uint64_t state = hhs_exact_uqcel_fold_bytes(data, size);
    size_t i;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i) {
        state = hhs_exact_uqcel_hash_mix64(
            state + UINT64_C(0x9E3779B97F4A7C15) * ((uint64_t)i + UINT64_C(1))
        );
        out_hash72[i] = hhs_exact_uqcel_hash72_symbol(state);
    }
    out_hash72[HHS_EXACT_HASH72_LEN] = '\0';
}

static void hhs_exact_uqcel_hash216_bytes(
    const void *data,
    size_t size,
    char out_hash216[HHS_EXACT_UQCEL_HASH216_STRLEN]
) {
    uint64_t state = hhs_exact_uqcel_fold_bytes(data, size);
    size_t i;
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        state = hhs_exact_uqcel_hash_mix64(
            state + UINT64_C(0x517cc1b727220a95) * ((uint64_t)i + UINT64_C(1))
        );
        out_hash216[i] = hhs_exact_uqcel_hash72_symbol(state);
    }
    out_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
}

/* ============================================================
 * PASS 219 UNIVERSAL QUANTIZATION CONSTRAINT ENFORCEMENT
 * ============================================================
 */

typedef struct HHSExactBigBuffer {
    uint8_t bytes[HHS_EXACT_UQCEL_MAX_DERIVED_BYTES + 2U];
    size_t length;
} HHSExactBigBuffer;

static int hhs_exact_big_view_valid(
    const HHSExactBigUIntView *view,
    size_t max_length,
    int allow_zero
) {
    if (view == NULL || view->struct_size < sizeof(*view) || view->bytes_be == NULL)
        return 0;
    if (view->byte_length == 0U || view->byte_length > max_length)
        return 0;
    if (view->byte_length > 1U && view->bytes_be[0] == 0U)
        return 0;
    if (!allow_zero && view->byte_length == 1U && view->bytes_be[0] == 0U)
        return 0;
    return 1;
}

static int hhs_exact_big_equal_raw(
    const uint8_t *a,
    size_t a_length,
    const uint8_t *b,
    size_t b_length
) {
    return a_length == b_length && memcmp(a, b, a_length) == 0;
}

static int hhs_exact_big_equal_view_buffer(
    const HHSExactBigUIntView *view,
    const HHSExactBigBuffer *buffer
) {
    return hhs_exact_big_equal_raw(
        view->bytes_be, (size_t)view->byte_length,
        buffer->bytes, buffer->length
    );
}

static int hhs_exact_big_mul_raw(
    const uint8_t *a,
    size_t a_length,
    const uint8_t *b,
    size_t b_length,
    HHSExactBigBuffer *out
) {
    uint32_t accum[HHS_EXACT_UQCEL_MAX_DERIVED_BYTES + 2U];
    size_t i;
    size_t j;
    size_t full_length;

    if (a == NULL || b == NULL || out == NULL || a_length == 0U || b_length == 0U)
        return 0;
    if (a_length + b_length > HHS_EXACT_UQCEL_MAX_DERIVED_BYTES + 1U)
        return 0;

    memset(accum, 0, sizeof(accum));
    for (i = 0U; i < a_length; ++i) {
        uint32_t av = a[a_length - 1U - i];
        for (j = 0U; j < b_length; ++j) {
            uint32_t bv = b[b_length - 1U - j];
            accum[i + j] += av * bv;
        }
    }

    full_length = a_length + b_length + 1U;
    for (i = 0U; i + 1U < full_length; ++i) {
        accum[i + 1U] += accum[i] >> 8U;
        accum[i] &= UINT32_C(0xFF);
    }
    while (full_length > 1U && accum[full_length - 1U] == 0U)
        --full_length;
    if (full_length > HHS_EXACT_UQCEL_MAX_DERIVED_BYTES + 2U)
        return 0;

    out->length = full_length;
    for (i = 0U; i < full_length; ++i)
        out->bytes[full_length - 1U - i] = (uint8_t)accum[i];
    return 1;
}

static int hhs_exact_big_mul_view(
    const HHSExactBigUIntView *a,
    const HHSExactBigUIntView *b,
    HHSExactBigBuffer *out
) {
    return hhs_exact_big_mul_raw(
        a->bytes_be, (size_t)a->byte_length,
        b->bytes_be, (size_t)b->byte_length,
        out
    );
}

static int hhs_exact_big_square_view(
    const HHSExactBigUIntView *a,
    HHSExactBigBuffer *out
) {
    return hhs_exact_big_mul_view(a, a, out);
}

static int hhs_exact_big_mul_buffer(
    const HHSExactBigBuffer *a,
    const HHSExactBigBuffer *b,
    HHSExactBigBuffer *out
) {
    return hhs_exact_big_mul_raw(a->bytes, a->length, b->bytes, b->length, out);
}

static int hhs_exact_big_add_buffer_view(
    const HHSExactBigBuffer *a,
    const HHSExactBigUIntView *b,
    HHSExactBigBuffer *out
) {
    uint8_t reversed[HHS_EXACT_UQCEL_MAX_DERIVED_BYTES + 2U];
    size_t max_length;
    size_t i;
    uint16_t carry = 0U;

    if (a == NULL || b == NULL || out == NULL)
        return 0;
    max_length = a->length > (size_t)b->byte_length ? a->length : (size_t)b->byte_length;
    if (max_length + 1U > sizeof(reversed))
        return 0;
    memset(reversed, 0, sizeof(reversed));

    for (i = 0U; i < max_length; ++i) {
        uint16_t av = i < a->length ? a->bytes[a->length - 1U - i] : 0U;
        uint16_t bv = i < (size_t)b->byte_length ? b->bytes_be[(size_t)b->byte_length - 1U - i] : 0U;
        uint16_t sum = (uint16_t)(av + bv + carry);
        reversed[i] = (uint8_t)(sum & UINT16_C(0xFF));
        carry = (uint16_t)(sum >> 8U);
    }
    if (carry != 0U)
        reversed[max_length++] = (uint8_t)carry;

    out->length = max_length;
    for (i = 0U; i < max_length; ++i)
        out->bytes[max_length - 1U - i] = reversed[i];
    return 1;
}

static uint8_t hhs_exact_big_mod4(const HHSExactBigUIntView *value) {
    return (uint8_t)(value->bytes_be[value->byte_length - 1U] & UINT8_C(0x03));
}

static int hhs_exact_hash72_text_valid(const char value[HHS_EXACT_HASH72_STRLEN]) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_HASH72_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i) {
        if (strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}
