#ifndef HHS_PASS219B_GLOBAL_ZERO_SUM_CLOSURE_1_0_H
#define HHS_PASS219B_GLOBAL_ZERO_SUM_CLOSURE_1_0_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219B_ZERO_SUM_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219B_ZERO_SUM_VERSION_MINOR 0U
#define HHS_EXACT_PASS219B_ZERO_SUM_VERSION_PATCH 0U
#define HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES 32U
#define HHS_EXACT_PASS219B_ZERO_SUM_UNIT_PERIMETER_COUNT 8U

#define HHS_EXACT_PASS219B_ZERO_SUM_CENTER_RELATION "x+y+z+w=0"
#define HHS_EXACT_PASS219B_ZERO_SUM_PHASE_RELATION "I+I^2+I^3+I^4=0"

#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_CENTER UINT64_C(0x0001)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_PHASE_CARRIER UINT64_C(0x0002)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_PASS129_UNIT_DELTA UINT64_C(0x0004)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_XY_UNIT UINT64_C(0x0008)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_ZW_UNIT UINT64_C(0x0010)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_U72_UNIT_BINDING UINT64_C(0x0020)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_DENOMINATOR_PROJECTION UINT64_C(0x0040)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_RECURSIVE_FIXED_POINT_REQUIRED UINT64_C(0x0080)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_MONOLITHIC_CHAIN_REQUIRED UINT64_C(0x0100)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_REQUIRED UINT64_C(0x01FF)

typedef struct HHSExactPass219BGlobalZeroSumClosureV1 {
    uint32_t struct_size;
    uint32_t version;
    int8_t phase_sum_real;
    int8_t phase_sum_imag;
    uint8_t center_zero_sum_proven;
    uint8_t phase_carrier_zero_sum_proven;
    uint8_t pass129_unit_delta_theorem_bound;
    uint8_t xy_unit_projection_bound;
    uint8_t zw_unit_projection_bound;
    uint8_t u72_unit_projection_bound;
    uint8_t denominator_unit_perimeter_count;
    uint8_t denominator_center_zero_sum_preserved;
    uint8_t recursive_fixed_point_required;
    uint8_t monolithic_chain_required;
    uint8_t full_monolithic_evaluated;
    uint8_t global_enforcement_required;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_persistence_authority;
    uint8_t canonical_hash72_authority;
    uint8_t reserved0[5];
    uint64_t proof_mask;
    uint8_t closure_extension_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
} HHSExactPass219BGlobalZeroSumClosureV1;

HHS_EXACT_API uint32_t hhs_exact_pass219b_global_zero_sum_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_global_zero_sum_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES]
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_global_zero_sum_prove(
    HHSExactPass219BGlobalZeroSumClosureV1 *out_proof
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_global_zero_sum_verify(
    const HHSExactPass219BGlobalZeroSumClosureV1 *proof
);

#ifdef __cplusplus
}
#endif

#endif
