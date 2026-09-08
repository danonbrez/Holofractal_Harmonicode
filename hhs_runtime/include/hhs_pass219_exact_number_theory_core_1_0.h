#ifndef HHS_PASS219_EXACT_NUMBER_THEORY_CORE_1_0_H
#define HHS_PASS219_EXACT_NUMBER_THEORY_CORE_1_0_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_NUMBER_THEORY_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_NUMBER_THEORY_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_NUMBER_THEORY_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_NUMBER_THEORY_RELATION_COUNT 12U
#define HHS_EXACT_PASS219_NUMBER_THEORY_SOURCE_FNV1A64 UINT64_C(0xd98c7f1b67f5db00)

typedef enum HHSExactPass219NumberTheoryRelationV1 {
    HHS_EXACT_PASS219_NT_PRIMARY_CUBIC_PRIME_CHAIN = 0,
    HHS_EXACT_PASS219_NT_DELTA_RADICAL_BINDING = 1,
    HHS_EXACT_PASS219_NT_P2_MINUS_PQ_UNIT = 2,
    HHS_EXACT_PASS219_NT_AB_EQUALS_P4 = 3,
    HHS_EXACT_PASS219_NT_AB_RECIPROCAL_NORMALIZATION = 4,
    HHS_EXACT_PASS219_NT_PYTHAGOREAN_DYADIC_GEOMETRY = 5,
    HHS_EXACT_PASS219_NT_FIBONACCI_GEOMETRY_BINDING = 6,
    HHS_EXACT_PASS219_NT_B6C4_U72_BINDING = 7,
    HHS_EXACT_PASS219_NT_OCTONION_PHASE_GEAR_BALANCE = 8,
    HHS_EXACT_PASS219_NT_PHASE_GEOMETRY_EQUALITY_CHAIN = 9,
    HHS_EXACT_PASS219_NT_MATRIX_POWER_A2_BINDING = 10,
    HHS_EXACT_PASS219_NT_PRIME_QUADRATIC_RECIPROCITY = 11
} HHSExactPass219NumberTheoryRelationV1;

typedef enum HHSExactPass219NumberTheoryDecisionV1 {
    HHS_EXACT_PASS219_NUMBER_THEORY_REJECT = 0,
    HHS_EXACT_PASS219_NUMBER_THEORY_PROPAGATE = 1
} HHSExactPass219NumberTheoryDecisionV1;

enum {
    HHS_EXACT_PASS219_NT_REASON_MISSING_RELATION = 1U << 0,
    HHS_EXACT_PASS219_NT_REASON_SOURCE_IDENTITY = 1U << 1,
    HHS_EXACT_PASS219_NT_REASON_EQUALITY_CHAIN = 1U << 2,
    HHS_EXACT_PASS219_NT_REASON_SCALAR_AUTHORITY = 1U << 3,
    HHS_EXACT_PASS219_NT_REASON_NONCOMMUTATIVE_ORDER = 1U << 4,
    HHS_EXACT_PASS219_NT_REASON_FLOAT_AUTHORITY = 1U << 5,
    HHS_EXACT_PASS219_NT_REASON_SOURCE_SELFCHECK = 1U << 6
};

typedef struct HHSExactPass219NumberTheoryInputV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t relation_witness_mask;
    uint8_t source_identity_exact;
    uint8_t equality_chain_preserved;
    uint8_t scalar_projection_witness_only;
    uint8_t noncommutative_order_preserved;
    uint8_t no_float_authority;
    uint8_t reserved[3];
} HHSExactPass219NumberTheoryInputV1;

typedef struct HHSExactPass219NumberTheoryResultV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason_mask;
    uint64_t required_relation_mask;
    uint64_t observed_relation_mask;
    uint64_t missing_relation_mask;
    uint64_t source_fnv1a64;
    uint32_t first_missing_relation;
    uint8_t source_identity_exact;
    uint8_t equality_chain_preserved;
    uint8_t scalar_projection_witness_only;
    uint8_t noncommutative_order_preserved;
    uint8_t no_float_authority;
    uint8_t scalar_projection_authority;
    uint8_t floating_point_authority;
    uint8_t reserved;
} HHSExactPass219NumberTheoryResultV1;

uint32_t hhs_exact_pass219_number_theory_version(void);
uint64_t hhs_exact_pass219_number_theory_required_mask(void);
const char *hhs_exact_pass219_number_theory_equation_set(void);
uint64_t hhs_exact_pass219_number_theory_source_fnv1a64(void);
int hhs_exact_pass219_number_theory_selfcheck(void);
int hhs_exact_pass219_number_theory_evaluate(
    const HHSExactPass219NumberTheoryInputV1 *input,
    HHSExactPass219NumberTheoryResultV1 *out_result
);

#ifdef __cplusplus
}
#endif

#endif
