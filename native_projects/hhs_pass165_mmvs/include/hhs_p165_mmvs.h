#ifndef HHS_P165_MMVS_H
#define HHS_P165_MMVS_H
#include <stddef.h>
#include <stdint.h>
#define HHS_P165_ABI_VERSION 1u
#define HHS_P165_COORDINATES 5184u
#define HHS_P165_FRAME_BYTES 648u
#define HHS_P165_LANES 64u
#define HHS_P165_POSITIONS 81u
#define HHS_P165_MAX_SOURCE_BYTES (16u * 1024u * 1024u)
typedef enum {
 HHS_P165_OK=0, HHS_P165_INVALID_ARGUMENT=1, HHS_P165_OUT_OF_RANGE=2,
 HHS_P165_SIZE_BOUND=3, HHS_P165_NONCANONICAL_WEIGHT=4
} hhs_p165_status;
typedef struct { uint8_t bytes[HHS_P165_FRAME_BYTES]; } hhs_p165_frame;
typedef struct { int64_t numerator; uint64_t denominator; } hhs_p165_rational;
typedef struct {
 uint32_t abi_version; uint64_t byte_length; uint8_t source_sha256[32];
 uint32_t modality; uint32_t authorization_scope;
} hhs_p165_source_descriptor;
hhs_p165_status hhs_p165_frame_clear(hhs_p165_frame *frame);
hhs_p165_status hhs_p165_frame_set(hhs_p165_frame *frame, uint32_t position, uint32_t lane, uint8_t value);
hhs_p165_status hhs_p165_frame_get(const hhs_p165_frame *frame, uint32_t position, uint32_t lane, uint8_t *value);
uint32_t hhs_p165_frame_popcount(const hhs_p165_frame *frame);
hhs_p165_status hhs_p165_frame_residual(const hhs_p165_frame *actual, const hhs_p165_frame *predicted, hhs_p165_frame *residual);
hhs_p165_status hhs_p165_validate_source(const hhs_p165_source_descriptor *source);
hhs_p165_status hhs_p165_validate_weight(hhs_p165_rational weight, hhs_p165_rational minimum, hhs_p165_rational maximum);
#endif
