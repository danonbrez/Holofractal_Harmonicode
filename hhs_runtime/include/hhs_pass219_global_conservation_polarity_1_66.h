#ifndef HHS_PASS219_GLOBAL_CONSERVATION_POLARITY_1_66_H
#define HHS_PASS219_GLOBAL_CONSERVATION_POLARITY_1_66_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_CONSERVATION_1_66_VERSION UINT32_C(0x00010042)
#define HHS_EXACT_PASS219_CONSERVATION_1_66_NAMESPACE UINT32_C(0x00021942)
#define HHS_EXACT_PASS219_CONSERVATION_1_66_SOURCE_BYTES UINT32_C(344)

enum {
    HHS_EXACT_PASS219_CONSERVATION_DECISION_INVALID = 0,
    HHS_EXACT_PASS219_CONSERVATION_DECISION_VERIFIED = 1,
    HHS_EXACT_PASS219_CONSERVATION_DECISION_REJECTED = 2
};

typedef struct HHSExactPass219ConservationAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint8_t parent_1_65_required;
    uint8_t gate_scoped_projection_required;
    uint8_t ordinary_ratio_qr_symbol_separated;
    uint8_t polarity_s_independent_default;
    uint8_t canonical_seed_sign_preserved;
    uint8_t signed_metric_projection_separate;
    uint8_t lane5_preflight_required;
    uint8_t signed_vm81_preflight_required;
    uint8_t scalar_projection_witness_only;
    uint8_t cross_gate_substitution_authority;
    uint8_t canonical_constant_rewrite_authority;
    uint8_t commutation_authority;
    uint8_t equality_reversal_authority;
    uint8_t delta_cancellation_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t floating_point_canonical_authority;
} HHSExactPass219ConservationAuthorityV1;

typedef struct HHSExactPass219ConservationReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t decision;
    uint8_t source_hash_verified;
    uint8_t parent_1_65_verified;
    uint8_t operator_typing_verified;
    uint8_t pell_branch_verified;
    uint8_t reciprocal_correction_verified;
    uint8_t negative_s_factor_verified;
    uint8_t phase72_seed_verified;
    uint8_t congruent_projection_verified;
    uint8_t unit_shell_verified;
    uint8_t master_delta_m_projection_verified;
    uint8_t signed_metric_null_cone_verified;
    uint8_t canonical_c2_preserved;
    uint8_t polarity_balance_projection_verified;
    uint8_t unit_shell_x_plus_y_zero_verified;
    uint8_t scalar_projection_witness_only;
    uint8_t cross_gate_substitution_authority;
    uint8_t canonical_constant_rewrite_authority;
    uint8_t commutation_authority;
    uint8_t equality_reversal_authority;
    uint8_t delta_cancellation_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved0[4];
} HHSExactPass219ConservationReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_conservation_1_66_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_conservation_1_66_authority(
    HHSExactPass219ConservationAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_conservation_1_66_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_conservation_1_66_verify(
    HHSExactPass219ConservationReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
