#ifndef HHS_PASS220_ORDERED4X4_NEG4_H
#define HHS_PASS220_ORDERED4X4_NEG4_H
#include "hhs_runtime_exact_abi_v1_1_base.h"
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define HHS220_ORDERED4X4_SOURCE_BYTES 366U
#define HHS220_ORDERED4X4_CELL_COUNT 64U
#define HHS220_ORDERED4X4_ROWS 4U
#define HHS220_ORDERED4X4_COLUMNS 4U

typedef struct HHS220Ordered4x4HIRWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t rows;
    uint32_t columns;
    uint32_t matrix_occurrences;
    uint32_t literal_cells;
    uint32_t exponent_magnitude;
    uint8_t exponent_negative;
    uint8_t numerator_negative_operand_count;
    uint8_t source_identity_verified;
    uint8_t ordered_topology_verified;
    uint8_t typed_s_unresolved;
    uint8_t typed_v_unresolved;
    uint8_t matrix_power_value_derived;
    uint8_t native_matrix_division_evaluated;
    uint8_t vm81_admission_executed;
    uint8_t hash72_commit_authority;
    uint8_t hash216_commit_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t reserved0[2];
    uint8_t source_sha256[32];
    uint8_t topology_sha256[32];
} HHS220Ordered4x4HIRWitnessV1;

/*
 * Lower exact source into a read-only candidate VM81 frame.
 * This is NOT VM81 admission and does not prove equality or evaluate
 * MatrixTimes, quotient, or the negative fourth matrix power.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_ordered4x4_lower(
    const uint8_t *source,
    size_t source_size,
    HHSExactVM81Frame *out_candidate,
    HHS220Ordered4x4HIRWitnessV1 *out_witness
);
#ifdef __cplusplus
}
#endif
#endif
