#ifndef HHS_HASH216_BYTES_H
#define HHS_HASH216_BYTES_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_HASH72_BYTES_LEN 72U
#define HHS_HASH72_BYTES_STRLEN 73U
#define HHS_HASH216_BYTES_LEN 216U
#define HHS_HASH216_BYTES_STRLEN 217U

/*
 * Conflict-free byte-oriented adapters over the inherited canonical
 * Hash72/Hash216 implementation.  These preserve the existing hash types and
 * functions while allowing translation units that already own a historical
 * HHSHash72 typedef to consume canonical hash material without a type-name
 * collision.
 */
void hhs_hash72_compute_bytes(
    const void *data,
    size_t size,
    char out_hash72[HHS_HASH72_BYTES_STRLEN]
);

void hhs_hash216_compute_bytes(
    const void *data,
    size_t size,
    char out_hash216[HHS_HASH216_BYTES_STRLEN]
);

/*
 * Exact ordered 3 x Hash72 lineage and Python-equivalent SHA-256-per-character
 * vector. Does not mint a VM81 transition or confer canonical authority.
 * Returns 1 on success, 0 on malformed input. Caller provides fixed buffers.
 * Output vector is 216 consecutive lowercase 64-char hex SHA-256 digests.
 */
#define HHS_HASH216_SHA256_VECTOR_HEX_LEN (216U * 64U)
#define HHS_HASH216_SHA256_VECTOR_HEX_STRLEN (HHS_HASH216_SHA256_VECTOR_HEX_LEN + 1U)
int hhs_hash216_lineage_vector_sha256(
    const char previous[HHS_HASH72_BYTES_STRLEN],
    const char change[HHS_HASH72_BYTES_STRLEN],
    const char receipt[HHS_HASH72_BYTES_STRLEN],
    char ordered_hash216[HHS_HASH216_BYTES_STRLEN],
    char sha256_vector_hex[HHS_HASH216_SHA256_VECTOR_HEX_STRLEN]
);

#ifdef __cplusplus
}
#endif

#endif
