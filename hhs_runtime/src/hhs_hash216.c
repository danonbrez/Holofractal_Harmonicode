// hhs_runtime/src/hhs_hash216.c
//
// HHS / HARMONICODE
// Canonical Hash72 / Hash216 Runtime Implementation
//
// Runtime Principle:
//
//   hash canonicalization
//   precedes
//   runtime propagation
//

#include "../include/hhs_hash216.h"

#include <string.h>
#include <stdint.h>

/* ============================================================
 * CANONICAL HASH72 ALPHABET
 * ============================================================
 */

const char HHS_HASH72_ALPHABET[
    HHS_HASH72_LEN + 1
] =
"0123456789"
"abcdefghijklmnopqrstuvwxyz"
"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
"-+*/()<>!?";

/* ============================================================
 * INTERNAL HELPERS
 * ============================================================
 */

static uint64_t hhs_hash_mix64(
    uint64_t x
) {
    x ^= x >> 33;
    x *= 0xff51afd7ed558ccdULL;

    x ^= x >> 33;
    x *= 0xc4ceb9fe1a85ec53ULL;

    x ^= x >> 33;

    return x;
}

static char hhs_hash72_symbol(
    uint64_t value
) {
    return HHS_HASH72_ALPHABET[
        value % HHS_HASH72_LEN
    ];
}

static void hhs_hash72_from_u64(
    uint64_t seed,
    HHSHash72* out_hash
) {
    uint64_t state = seed;

    for (size_t i = 0; i < HHS_HASH72_LEN; ++i) {

        state =
            hhs_hash_mix64(
                state + (0x9E3779B97F4A7C15ULL * (i + 1))
            );

        out_hash->value[i] =
            hhs_hash72_symbol(state);
    }

    out_hash->value[
        HHS_HASH72_LEN
    ] = '\0';
}

static void hhs_hash216_from_seed(
    uint64_t seed,
    HHSHash216* out_hash
) {
    uint64_t state = seed;

    for (size_t i = 0; i < HHS_HASH216_LEN; ++i) {

        state =
            hhs_hash_mix64(
                state + (0x517cc1b727220a95ULL * (i + 1))
            );

        out_hash->value[i] =
            hhs_hash72_symbol(state);
    }

    out_hash->value[
        HHS_HASH216_LEN
    ] = '\0';
}

static uint64_t hhs_fold_bytes(
    const void* data,
    size_t size
) {
    const uint8_t* bytes =
        (const uint8_t*)data;

    uint64_t state =
        0x179971179971ULL;

    for (size_t i = 0; i < size; ++i) {

        state ^=
            ((uint64_t)bytes[i] << ((i % 8) * 8));

        state =
            hhs_hash_mix64(
                state + i + 1
            );
    }

    return state;
}

/* ============================================================
 * HASH72 API
 * ============================================================
 */

void hhs_hash72_clear(
    HHSHash72* hash
) {
    if (!hash) {
        return;
    }

    memset(
        hash->value,
        0,
        sizeof(hash->value)
    );
}

void hhs_hash72_compute(
    const void* data,
    size_t size,
    HHSHash72* out_hash
) {
    if (!out_hash) {
        return;
    }

    uint64_t folded =
        hhs_fold_bytes(
            data,
            size
        );

    hhs_hash72_from_u64(
        folded,
        out_hash
    );
}

void hhs_hash72_reciprocal(
    const HHSHash72* in_hash,
    HHSHash72* out_hash
) {
    if (!in_hash || !out_hash) {
        return;
    }

    for (size_t i = 0; i < HHS_HASH72_LEN; ++i) {

        out_hash->value[i] =
            in_hash->value[
                (HHS_HASH72_LEN - 1) - i
            ];
    }

    out_hash->value[
        HHS_HASH72_LEN
    ] = '\0';
}

int hhs_hash72_equal(
    const HHSHash72* a,
    const HHSHash72* b
) {
    if (!a || !b) {
        return 0;
    }

    return
        memcmp(
            a->value,
            b->value,
            HHS_HASH72_LEN
        ) == 0;
}

/* ============================================================
 * HASH216 API
 * ============================================================
 */

void hhs_hash216_clear(
    HHSHash216* hash
) {
    if (!hash) {
        return;
    }

    memset(
        hash->value,
        0,
        sizeof(hash->value)
    );
}

void hhs_hash216_compute(
    const void* data,
    size_t size,
    HHSHash216* out_hash
) {
    if (!out_hash) {
        return;
    }

    uint64_t folded =
        hhs_fold_bytes(
            data,
            size
        );

    hhs_hash216_from_seed(
        folded,
        out_hash
    );
}

void hhs_hash216_reciprocal(
    const HHSHash216* in_hash,
    HHSHash216* out_hash
) {
    if (!in_hash || !out_hash) {
        return;
    }

    for (size_t i = 0; i < HHS_HASH216_LEN; ++i) {

        out_hash->value[i] =
            in_hash->value[
                (HHS_HASH216_LEN - 1) - i
            ];
    }

    out_hash->value[
        HHS_HASH216_LEN
    ] = '\0';
}

int hhs_hash216_equal(
    const HHSHash216* a,
    const HHSHash216* b
) {
    if (!a || !b) {
        return 0;
    }

    return
        memcmp(
            a->value,
            b->value,
            HHS_HASH216_LEN
        ) == 0;
}