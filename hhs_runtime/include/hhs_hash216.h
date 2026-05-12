// hhs_runtime/include/hhs_hash216.h
//
// HHS / HARMONICODE
// Canonical Hash72 / Hash216 ABI
//
// Runtime Principle:
//
//   hashing
//   =
//   canonical manifold identity topology
//
// NOT:
//   utility digest generation
//

#ifndef HHS_HASH216_H
#define HHS_HASH216_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>

#define HHS_HASH72_LEN   72
#define HHS_HASH216_LEN  216

/*
 * Canonical Hash72 alphabet.
 */

extern const char HHS_HASH72_ALPHABET[
    HHS_HASH72_LEN + 1
];

/*
 * Canonical Hash72.
 */

typedef struct HHSHash72 {

    char value[
        HHS_HASH72_LEN + 1
    ];

} HHSHash72;

/*
 * Canonical Hash216.
 */

typedef struct HHSHash216 {

    char value[
        HHS_HASH216_LEN + 1
    ];

} HHSHash216;

/*
 * Hash canonicalization API
 */

void hhs_hash72_clear(
    HHSHash72* hash
);

void hhs_hash216_clear(
    HHSHash216* hash
);

/*
 * Canonical manifold hashing.
 */

void hhs_hash72_compute(
    const void* data,
    size_t size,
    HHSHash72* out_hash
);

void hhs_hash216_compute(
    const void* data,
    size_t size,
    HHSHash216* out_hash
);

/*
 * Reciprocal manifold transforms.
 */

void hhs_hash72_reciprocal(
    const HHSHash72* in_hash,
    HHSHash72* out_hash
);

void hhs_hash216_reciprocal(
    const HHSHash216* in_hash,
    HHSHash216* out_hash
);

/*
 * Equality
 */

int hhs_hash72_equal(
    const HHSHash72* a,
    const HHSHash72* b
);

int hhs_hash216_equal(
    const HHSHash216* a,
    const HHSHash216* b
);

#ifdef __cplusplus
}
#endif

#endif