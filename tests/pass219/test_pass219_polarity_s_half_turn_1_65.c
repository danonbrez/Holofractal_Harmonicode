#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <string.h>

int main(void) {
    HHSExactPass219PolaritySAuthorityV1 authority;
    HHSExactPass219PolaritySReceiptV1 plus;
    HHSExactPass219PolaritySReceiptV1 minus;

    memset(&authority, 0, sizeof(authority));
    assert(hhs_exact_pass219_polarity_s_authority(&authority) == HHS_EXACT_STATUS_OK);
    assert(authority.phase_modulus == 72U);
    assert(authority.half_turn_steps == 36U);
    assert(authority.s_minus_one_is_half_turn == 1U);
    assert(authority.self_inverse == 1U);
    assert(authority.parent_1_64_required == 1U);
    assert(authority.commutation_authority == 0U);
    assert(authority.reciprocal_cancellation_authority == 0U);
    assert(authority.canonical_vm81_mutation_authority == 0U);

    memset(&plus, 0, sizeof(plus));
    assert(hhs_exact_pass219_polarity_s_verify(1, &plus) == HHS_EXACT_STATUS_OK);
    assert(plus.decision == HHS_EXACT_PASS219_POLARITY_S_DECISION_VERIFIED);
    assert(plus.phase_steps == 0U);
    assert(plus.xy_sign == 1);
    assert(plus.yx_sign == -1);
    assert(plus.zw_sign == 1);
    assert(plus.wz_sign == -1);
    assert(plus.p_minus_q_orientation == -1);
    assert(plus.q_minus_p_orientation == 1);

    memset(&minus, 0, sizeof(minus));
    assert(hhs_exact_pass219_polarity_s_verify(-1, &minus) == HHS_EXACT_STATUS_OK);
    assert(minus.decision == HHS_EXACT_PASS219_POLARITY_S_DECISION_VERIFIED);
    assert(minus.phase_steps == 36U);
    assert(minus.xy_sign == -1);
    assert(minus.yx_sign == 1);
    assert(minus.zw_sign == -1);
    assert(minus.wz_sign == 1);
    assert(minus.p_minus_q_orientation == 1);
    assert(minus.q_minus_p_orientation == -1);
    assert(minus.half_turn_verified == 1U);
    assert(minus.half_turn_self_inverse == 1U);
    assert(minus.chiral_pairs_opposed == 1U);
    assert(minus.parent_1_64_verified == 1U);
    assert(minus.correction_link_verified == 1U);
    assert(minus.scalar_projection_witness_only == 1U);
    assert(minus.commutation_authority == 0U);
    assert(minus.reciprocal_cancellation_authority == 0U);
    assert(minus.equality_reversal_authority == 0U);

    assert(hhs_exact_pass219_polarity_s_verify(0, &minus) == HHS_EXACT_STATUS_RANGE_ERROR);
    return 0;
}
