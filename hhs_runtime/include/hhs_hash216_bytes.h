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

#ifdef __cplusplus
}
#endif

#endif
