#ifndef HHS_PASS219_POLARITY_S_HALF_TURN_1_65_H
#define HHS_PASS219_POLARITY_S_HALF_TURN_1_65_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_POLARITY_S_VERSION UINT32_C(0x00010041)
#define HHS_EXACT_PASS219_POLARITY_S_NAMESPACE UINT32_C(0x00021941)
#define HHS_EXACT_PASS219_POLARITY_S_PHASE_MODULUS UINT32_C(72)
#define HHS_EXACT_PASS219_POLARITY_S_HALF_TURN UINT32_C(36)

enum {
    HHS_EXACT_PASS219_POLARITY_S_DECISION_INVALID = 0,
    HHS_EXACT_PASS219_POLARITY_S_DECISION_VERIFIED = 1,
    HHS_EXACT_PASS219_POLARITY_S_DECISION_REJECTED = 2
};

typedef struct HHSExactPass219PolaritySAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t phase_modulus;
    uint32_t half_turn_steps;
    uint8_t ordered_xy_yx_pair;
    uint8_t ordered_zw_wz_pair;
    uint8_t s_minus_one_is_half_turn;
    uint8_t p_minus_q_pair_rotates;
    uint8_t self_inverse;
    uint8_t parent_1_64_required;
    uint8_t lane5_preflight_required;
    uint8_t signed_vm81_preflight_required;
    uint8_t scalar_projection_witness_only;
    uint8_t commutation_authority;
    uint8_t reciprocal_cancellation_authority;
    uint8_t equality_reversal_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t floating_point_canonical_authority;
} HHSExactPass219PolaritySAuthorityV1;

typedef struct HHSExactPass219PolaritySReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t decision;
    int32_t s_value;
    uint32_t phase_steps;
    int8_t xy_sign;
    int8_t yx_sign;
    int8_t zw_sign;
    int8_t wz_sign;
    int8_t p_minus_q_orientation;
    int8_t q_minus_p_orientation;
    uint8_t source_definitions_verified;
    uint8_t negative_s_surface_verified;
    uint8_t parent_1_64_verified;
    uint8_t chiral_pairs_opposed;
    uint8_t half_turn_verified;
    uint8_t half_turn_self_inverse;
    uint8_t p_q_pair_rotation_verified;
    uint8_t correction_link_verified;
    uint8_t scalar_projection_closed;
    uint8_t scalar_projection_witness_only;
    uint8_t commutation_authority;
    uint8_t reciprocal_cancellation_authority;
    uint8_t equality_reversal_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved0[4];
} HHSExactPass219PolaritySReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_polarity_s_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_polarity_s_authority(
    HHSExactPass219PolaritySAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_polarity_s_verify(
    int32_t s_value,
    HHSExactPass219PolaritySReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
