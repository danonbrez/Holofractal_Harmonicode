#ifndef HHS_PASS219_HARMONIC36_HASH216_M_EXPONENT_LATTICE_1_0_H
#define HHS_PASS219_HARMONIC36_HASH216_M_EXPONENT_LATTICE_1_0_H

#include "hhs_pass219_harmonic36_hash216_rna_binding_1_0.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_M_LATTICE_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_H36_M_LATTICE_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_H36_M_LATTICE_VERSION_PATCH 0U

typedef struct HHSExactPass219MExponentCoordinateV1 {
    uint16_t exp2;
    uint16_t exp3;
} HHSExactPass219MExponentCoordinateV1;

typedef struct HHSExactPass219H36Hash216MExponentWitnessV1 {
    uint32_t struct_size;
    uint32_t version;

    uint16_t native_hash72_linear5184;
    uint8_t h36_word144;
    uint8_t h36_bit36;
    uint8_t vm81_cell81;
    uint8_t vm81_operation64;

    HHSExactPass219MExponentCoordinateV1 unit1;
    HHSExactPass219MExponentCoordinateV1 binary2;
    HHSExactPass219MExponentCoordinateV1 ternary3;
    HHSExactPass219MExponentCoordinateV1 loshu4;
    HHSExactPass219MExponentCoordinateV1 loshu6;
    HHSExactPass219MExponentCoordinateV1 loshu8;
    HHSExactPass219MExponentCoordinateV1 p4_9;
    HHSExactPass219MExponentCoordinateV1 h36_36;
    HHSExactPass219MExponentCoordinateV1 hash72_72;
    HHSExactPass219MExponentCoordinateV1 hash216_216;
    HHSExactPass219MExponentCoordinateV1 vm5184;
    HHSExactPass219MExponentCoordinateV1 manifold_m;

    uint16_t h36_depth36;
    uint16_t hash72_depth72;

    uint8_t same_linear5184_identity;
    uint8_t factor_support_2_3_only;
    uint8_t h36_to_hash72_binary_step;
    uint8_t hash72_to_hash216_ternary_step;
    uint8_t vm5184_h36_depth_closes_m;
    uint8_t hash72_depth_closes_m;
    uint8_t loshu_binary_ladder_from_one;
    uint8_t loshu_six_is_binary_ternary_product;
    uint8_t p4_is_ternary_square;
    uint8_t ab_equals_p4_projection;
    uint8_t one_is_p4_over9_projection;
    uint8_t direct_shared_m_binding;
    uint8_t translator_required;

    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36Hash216MExponentWitnessV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_h36_m_exponent_lattice_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_hash216_m_exponent_bind(
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence,
    HHSExactPass219H36Hash216MExponentWitnessV1 *out_witness
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_hash216_m_exponent_validate(
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *occurrence,
    const HHSExactPass219H36Hash216MExponentWitnessV1 *witness
);

#ifdef __cplusplus
}
#endif
#endif
