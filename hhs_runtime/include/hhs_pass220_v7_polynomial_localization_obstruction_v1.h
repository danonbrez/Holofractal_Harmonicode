#ifndef HHS_PASS220_V7_POLYNOMIAL_LOCALIZATION_OBSTRUCTION_V1_H
#define HHS_PASS220_V7_POLYNOMIAL_LOCALIZATION_OBSTRUCTION_V1_H
#include "hhs_pass220_v7_quotient_gate_v1.h"
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define HHS220_V7_AUGMENT_VERSION UINT32_C(0x00010000)
#define HHS220_V7_AUGMENT_CELLS 9U
#define HHS220_V7_AUGMENT_TARGET_DIAGONAL UINT64_C(5184)
typedef enum HHS220V7AugmentDecision {
    HHS220_V7_AUGMENT_INVALID=0,
    HHS220_V7_AUGMENT_SOURCE_REJECTED=1,
    HHS220_V7_AUGMENT_POLYNOMIAL_OBSTRUCTION_PROVED=2
} HHS220V7AugmentDecision;
typedef struct HHS220V7AugmentResult {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t hnan_verified_mask;
    uint32_t requested_mode;
    uint32_t source_byte_offsets[HHS220_V7_AUGMENT_CELLS];
    uint32_t minimum_word_degree[HHS220_V7_AUGMENT_CELLS];
    uint32_t ordered_term_occurrences[HHS220_V7_AUGMENT_CELLS];
    uint8_t all_nine_augmentation_zero;
    uint8_t right_finite_polynomial_target_obstructed;
    uint8_t left_finite_polynomial_target_obstructed;
    uint8_t native_rational_localization_proved;
    uint8_t native_hhs_matrix_quotient_admitted;
    uint8_t signed_vm81_admission_verified;
    uint8_t canonical_hash72_hash216_transition_verified;
    uint8_t reserved[2];
    uint8_t source_sha256[32];
} HHS220V7AugmentResult;
/* Compares EXACT source with an auxiliary noncommutative free polynomial
 * algebra. Proves only that no finite polynomial Q can give QM=5184I_3 or
 * MQ=5184I_3 in that comparison algebra. The 5184I matrix target is a
 * TEST PROJECTION, not an inferred HHS source-level matrix coercion.
 * Does NOT exclude exact rational, inverse, phase, or VM81 constructors.
 */
int hhs220_v7_aux_polynomial_obstruction(
    const HHS220V7QuotientInput *source_input,
    HHS220V7AugmentResult *result
);
#ifdef __cplusplus
}
#endif
#endif
