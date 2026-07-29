#ifndef HHS_P166_WORD2VEC_H
#define HHS_P166_WORD2VEC_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_P166_PROJECTION_BITS 5184u
#define HHS_P166_PROJECTION_BYTES 648u
#define HHS_P166_QUANTIZATION_SCALE 65536LL
#define HHS_P166_MAX_DIMENSION 4096u
#define HHS_P166_MAX_VOCABULARY 5000000u

typedef enum {
    HHS_P166_OK = 0,
    HHS_P166_INVALID_ARGUMENT = 2,
    HHS_P166_FORMAT_REJECTED = 6,
    HHS_P166_CONVERSION_FAILED = 7,
    HHS_P166_INDEX_FAILED = 8,
    HHS_P166_RESOURCE_BOUND = 11
} hhs_p166_status;

typedef struct {
    uint64_t expected_bytes;
    uint32_t dimension;
    uint32_t vocabulary_size;
    uint8_t digest_sha256[32];
} hhs_p166_manifest_geometry;

typedef struct {
    uint8_t bytes[HHS_P166_PROJECTION_BYTES];
} hhs_p166_projection;

hhs_p166_status hhs_p166_validate_geometry(const hhs_p166_manifest_geometry *geometry);
hhs_p166_status hhs_p166_quantize_q16_16(int64_t numerator, int64_t denominator, int32_t *out);
hhs_p166_status hhs_p166_dot_i32(const int32_t *left, const int32_t *right, size_t count, int64_t *out);
hhs_p166_status hhs_p166_projection_clear(hhs_p166_projection *projection);
hhs_p166_status hhs_p166_projection_set(hhs_p166_projection *projection, uint32_t coordinate, uint8_t value);
hhs_p166_status hhs_p166_projection_get(const hhs_p166_projection *projection, uint32_t coordinate, uint8_t *value_out);
uint32_t hhs_p166_projection_popcount(const hhs_p166_projection *projection);

#ifdef __cplusplus
}
#endif

#endif
