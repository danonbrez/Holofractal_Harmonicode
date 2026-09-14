#ifndef HHS_PASS219_DELTA_RECIPROCAL_CONSTRUCTOR_1_36_H
#define HHS_PASS219_DELTA_RECIPROCAL_CONSTRUCTOR_1_36_H

#include "hhs_pass219_lane5_exact_boundary_quantum_thermo_1_35.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_VERSION UINT32_C(0x00010024)
#define HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SOURCE_BYTES UINT32_C(326)
#define HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SHA256_BYTES UINT32_C(32)
#define HHS_EXACT_PASS219_FULL_MANIFOLD_MODULUS_BYTES UINT32_C(56)

typedef struct HHSExactPass219DeltaConstructorAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t constructor_source_bytes;
    uint8_t constructor_source_sha256[HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SHA256_BYTES];
    uint8_t infinity_is_full_manifold_bigint_modulus;
    uint8_t modulus_is_72_pow_72;
    uint8_t universal_delta_p_gt_one_domain;
    uint8_t reciprocal_surface_indivisible;
    uint8_t directional_reciprocity_not_scalarized;
    uint8_t lhs_rhs_are_typed_A_B_carriers;
    uint8_t ab_equals_p4_source_bound;
    uint8_t p4_not_one_source_bound;
    uint8_t zero_one_infinity_state_geometry;
    uint8_t trinary_boundary_geometry_distinct;
    uint8_t full_delta_constructor_evaluator_available;
    uint8_t candidate_only;
    uint8_t floating_point_canonical_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_lane5_boundary_1_35;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[11];
} HHSExactPass219DeltaConstructorAuthorityV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_delta_constructor_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_delta_constructor_authority(
    HHSExactPass219DeltaConstructorAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_delta_constructor_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_delta_constructor_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219_DELTA_CONSTRUCTOR_SHA256_BYTES]
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_full_manifold_modulus72_72(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_full_manifold_residue_validate(
    const HHSExactBigUIntView *residue,
    uint8_t *out_encoding_canonical,
    uint8_t *out_less_than_modulus
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_delta_p_domain_validate(
    const HHSExactBigUIntView *p,
    uint8_t *out_encoding_canonical,
    uint8_t *out_greater_than_one
);

#ifdef __cplusplus
}
#endif

#endif
