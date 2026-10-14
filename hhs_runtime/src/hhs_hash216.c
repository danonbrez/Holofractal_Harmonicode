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
#include "../include/hhs_hash216_bytes.h"

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

/* ============================================================
 * CONFLICT-FREE BYTE ADAPTERS
 * ============================================================
 */

void hhs_hash72_compute_bytes(
    const void *data,
    size_t size,
    char out_hash72[HHS_HASH72_BYTES_STRLEN]
) {
    HHSHash72 hash;
    if (out_hash72 == NULL)
        return;
    hhs_hash72_compute(data, size, &hash);
    memcpy(out_hash72, hash.value, HHS_HASH72_BYTES_STRLEN);
}

void hhs_hash216_compute_bytes(
    const void *data,
    size_t size,
    char out_hash216[HHS_HASH216_BYTES_STRLEN]
) {
    HHSHash216 hash;
    if (out_hash216 == NULL)
        return;
    hhs_hash216_compute(data, size, &hash);
    memcpy(out_hash216, hash.value, HHS_HASH216_BYTES_STRLEN);
}


/* Pass 220: exact Python hash216_lineage_witness projection.
 * The legacy byte-compute API above is kept ABI-stable; this additive
 * function preserves the three ordered Hash72 layers and 216 independent
 * SHA-256 digests. No native state mint or admission occurs here.
 */
#include <openssl/evp.h>

int hhs_hash216_lineage_vector_sha256(
    const char previous[HHS_HASH72_BYTES_STRLEN],
    const char change[HHS_HASH72_BYTES_STRLEN],
    const char receipt[HHS_HASH72_BYTES_STRLEN],
    char ordered_hash216[HHS_HASH216_BYTES_STRLEN],
    char sha256_vector_hex[HHS_HASH216_SHA256_VECTOR_HEX_STRLEN]
) {
    const char *layers[3] = {previous, change, receipt};
    static const char hex[] = "0123456789abcdef";
    if (!previous || !change || !receipt || !ordered_hash216 || !sha256_vector_hex)
        return 0;
    /* Validate all layers before touching caller outputs. */
    for (size_t layer = 0; layer < 3; ++layer) {
        for (size_t i = 0; i < HHS_HASH72_BYTES_LEN; ++i) {
            char symbol = layers[layer][i];
            if (!symbol || !memchr(HHS_HASH72_ALPHABET, symbol, HHS_HASH72_LEN))
                return 0;
        }
        if (layers[layer][HHS_HASH72_BYTES_LEN] != '\0')
            return 0;
    }
    for (size_t layer = 0; layer < 3; ++layer) {
        for (size_t i = 0; i < HHS_HASH72_BYTES_LEN; ++i) {
            size_t index = layer * HHS_HASH72_BYTES_LEN + i;
            unsigned char digest[EVP_MAX_MD_SIZE];
            unsigned int digest_len = 0;
            unsigned char symbol = (unsigned char)layers[layer][i];
            if (EVP_Digest(&symbol, 1U, digest, &digest_len, EVP_sha256(), NULL) != 1 ||
                digest_len != 32U)
                return 0;
            ordered_hash216[index] = (char)symbol;
            for (size_t byte = 0; byte < 32U; ++byte) {
                sha256_vector_hex[index * 64U + byte * 2U] = hex[digest[byte] >> 4];
                sha256_vector_hex[index * 64U + byte * 2U + 1U] = hex[digest[byte] & 15U];
            }
        }
    }
    ordered_hash216[HHS_HASH216_BYTES_LEN] = '\0';
    sha256_vector_hex[HHS_HASH216_SHA256_VECTOR_HEX_LEN] = '\0';
    return 1;
}
