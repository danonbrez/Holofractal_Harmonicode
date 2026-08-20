#ifndef HHS_PASS219B_GLOBAL_ZERO_SUM_CLOSURE_1_0_H
#define HHS_PASS219B_GLOBAL_ZERO_SUM_CLOSURE_1_0_H

#include "hhs_pass219b_universal_phase_locality_1_0.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219B_ZERO_SUM_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219B_ZERO_SUM_VERSION_MINOR 3U
#define HHS_EXACT_PASS219B_ZERO_SUM_VERSION_PATCH 0U
#define HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES 32U
#define HHS_EXACT_PASS219B_ZERO_SUM_UNIT_PERIMETER_COUNT 8U
#define HHS_EXACT_PASS219B_ZERO_SUM_CELL_COUNT 81U
#define HHS_EXACT_PASS219B_ZERO_SUM_LO_SHU_GROUP_COUNT 41U
#define HHS_EXACT_PASS219B_ZERO_SUM_TRIT_COUNT 3U
#define HHS_EXACT_PASS219B_ZERO_SUM_HYDRATION_SLOT_COUNT 5184U
#define HHS_EXACT_PASS219B_ZERO_SUM_HYDRATION_STATE_COUNT UINT64_C(51648192)
#define HHS_EXACT_PASS219B_ZERO_SUM_PHASE_ORIGIN_COUNT 81U
#define HHS_EXACT_PASS219B_ZERO_SUM_PHASE_PROJECTED_STATE_COUNT UINT64_C(4183503552)

#define HHS_EXACT_PASS219B_ZERO_SUM_CENTER_RELATION "x+y+z+w=0"
#define HHS_EXACT_PASS219B_ZERO_SUM_PHASE_RELATION "I+I^2+I^3+I^4=0"
#define HHS_EXACT_PASS219B_GLOBAL_RECURSIVE_RELATION "N/D^4=D^4"

#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_CENTER UINT64_C(0x0001)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_PHASE_CARRIER UINT64_C(0x0002)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_PASS129_UNIT_DELTA UINT64_C(0x0004)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_XY_UNIT UINT64_C(0x0008)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_ZW_UNIT UINT64_C(0x0010)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_U72_UNIT_BINDING UINT64_C(0x0020)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_DENOMINATOR_PROJECTION UINT64_C(0x0040)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_GLOBAL_TENSOR_SOURCE UINT64_C(0x0080)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_PHASE_QUANTIZATION UINT64_C(0x0100)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_LO_SHU_QUDIT UINT64_C(0x0200)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_VM81_HYDRATION UINT64_C(0x0400)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_UQCEL_V1_PRESERVED UINT64_C(0x0800)
#define HHS_EXACT_PASS219B_ZERO_SUM_PROOF_REQUIRED UINT64_C(0x0FFF)

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
    uint8_t global_tensor_source_bound;
    uint8_t phase_quantization_bound;
    uint8_t lo_shu_sudoku_qudit_bound;
    uint8_t vm81_hydration_geometry_bound;
    uint8_t legacy_full_symbolic_v1_preserved;
    uint8_t global_enforcement_required;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_persistence_authority;
    uint8_t canonical_hash72_authority;
    uint8_t cell_count81;
    uint8_t lo_shu_group_count41;
    uint8_t trit_count3;
    uint8_t phase_origin_count81;
    uint16_t hydration_slot_count5184;
    uint16_t reserved0;
    uint64_t hydration_state_count;
    uint64_t phase_projected_state_count;
    uint64_t proof_mask;
    uint8_t global_tensor_source_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    uint8_t phase_quantization_object_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    uint8_t closure_extension_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
} HHSExactPass219BGlobalZeroSumClosureV1;

/*
 * New additive I6 full-context input.  It does not resize or reinterpret
 * HHSExactUQCELInputV1.  N-source identity and D-source identity are carried
 * independently from the inherited UQCEL quantization subprojection.
 */
typedef struct HHSExactPass219BGlobalRelationInputV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactBigUIntView P;
    HHSExactBigUIntView p;
    HHSExactBigUIntView q;
    HHSExactBigUIntView delta;
    uint8_t cell81;
    uint8_t left_basis8;
    uint8_t right_basis8;
    uint8_t phase_origin81;
    int8_t lo_shu_group;
    uint8_t reserved0;
    uint16_t g243;
    uint8_t global_tensor_source_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    uint8_t phase_quantization_source_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    char previous_hash72[HHS_EXACT_HASH72_STRLEN];
} HHSExactPass219BGlobalRelationInputV1;

typedef struct HHSExactPass219BGlobalRelationHydrationWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint16_t vm5184_address;
    uint8_t global_tensor_source_verified;
    uint8_t phase_quantization_source_verified;
    uint8_t zero_sum_family_verified;
    uint8_t uqcel_integer_projection_verified;
    uint8_t legacy_full_symbolic_v1_preserved;
    uint8_t coordinate_roundtrip_verified;
    uint8_t native_phase_verified;
    uint8_t trinary_gate_verified;
    uint8_t phase_cell_verified;
    uint8_t phase_locality_verified;
    uint8_t global_relation_bridge_verified;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_persistence_authority;
    uint8_t canonical_hash72_authority;
    uint8_t reserved1[3];
    HHSExactPass219HydrationCoordinateV1 coordinate;
    HHSExactPass219NativePhaseWitnessV1 native_phase;
    HHSExactPass219TrinaryPhaseGateV1 trinary_gate;
    HHSExactPass219BPhaseCellV1 phase_cell;
    HHSExactPass219BPhaseLocalityPlanV1 locality_plan;
    HHSExactUQCELAdmissionV1 uqcel_integer_projection;
    HHSExactUQCELAdmissionV1 legacy_full_symbolic_probe;
} HHSExactPass219BGlobalRelationHydrationWitnessV1;

HHS_EXACT_API uint32_t hhs_exact_pass219b_global_zero_sum_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_global_zero_sum_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES]
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_global_tensor_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES]
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_phase_quantization_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES]
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_global_zero_sum_prove(
    HHSExactPass219BGlobalZeroSumClosureV1 *out_proof
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_global_zero_sum_verify(
    const HHSExactPass219BGlobalZeroSumClosureV1 *proof
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_global_relation_hydration_verify(
    const HHSExactPass219BGlobalRelationInputV1 *input,
    HHSExactPass219BGlobalRelationHydrationWitnessV1 *out_witness
);

#ifdef __cplusplus
}
#endif

#endif
