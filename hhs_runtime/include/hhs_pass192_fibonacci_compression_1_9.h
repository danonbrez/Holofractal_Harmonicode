#ifndef HHS_PASS192_FIBONACCI_COMPRESSION_1_9_H
#define HHS_PASS192_FIBONACCI_COMPRESSION_1_9_H

#include "hhs_runtime_uqcel_1_8.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS192_FIB_VERSION_MAJOR 1U
#define HHS_EXACT_PASS192_FIB_VERSION_MINOR 0U
#define HHS_EXACT_PASS192_FIB_VERSION_PATCH 0U
#define HHS_EXACT_PASS192_FIB_MAX_DEPTH 4096U
#define HHS_EXACT_PASS192_FIB_LO_SHU_CELLS 9U
#define HHS_EXACT_PASS192_FIB_MAGNITUDE_ROWS 5U
#define HHS_EXACT_PASS192_FIB_SHARED_SCHEDULES 1U
#define HHS_EXACT_PASS192_FIB_OUTER_MODULUS 1259713U
#define HHS_EXACT_PASS192_FIB_MAX_DESCRIPTOR_BYTES 2048U
#define HHS_EXACT_PASS219_UCE_FIBONACCI_DEPTH 10U
#define HHS_EXACT_PASS219_COMPOSED_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_COMPOSED_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_COMPOSED_VERSION_PATCH 0U

typedef struct HHSExactPass192FibonacciCompressionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t depth;
    uint32_t lo_shu_cell_count;
    uint32_t magnitude_row_count;
    uint32_t shared_schedule_count;
    uint32_t expanded_schedule_count;
    uint32_t outer_modulus;
    uint32_t membrane_modulus;
    uint32_t membrane_residue;
    uint32_t descriptor_length;
    uint8_t compression_applied;
    uint8_t shared_schedule_deduplicated;
    uint8_t membrane_preserved;
    uint8_t outer_modulus_preserved;
} HHSExactPass192FibonacciCompressionV1;

typedef struct HHSExactPass219ComposedAdmissionV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactUQCELAdmissionV1 uqcel;
    HHSExactPass192FibonacciCompressionV1 fibonacci;
    char final_receipt_hash72[HHS_EXACT_HASH72_STRLEN];
    char final_hash216_triplet[HHS_EXACT_UQCEL_HASH216_STRLEN];
    char final_hash216_identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
} HHSExactPass219ComposedAdmissionV1;

HHS_EXACT_API uint32_t hhs_exact_pass192_fibonacci_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass192_fibonacci_compress(
    uint32_t depth,
    uint8_t *out_descriptor,
    size_t capacity,
    size_t *out_length,
    HHSExactPass192FibonacciCompressionV1 *out_compression
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass192_fibonacci_validate_descriptor(
    uint32_t depth,
    const uint8_t *descriptor,
    size_t descriptor_length
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_admit_composed(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219ComposedAdmissionV1 *out_admission
);

#ifdef __cplusplus
}
#endif

#endif
