#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

int main(void) {
    HHSExactPass219ConservationAuthorityV1 authority;
    HHSExactPass219ConservationReceiptV1 receipt;
    uint8_t source[HHS_EXACT_PASS219_CONSERVATION_1_66_SOURCE_BYTES + 1U];
    size_t source_len = 0U;

    memset(&authority, 0, sizeof(authority));
    assert(hhs_exact_pass219_conservation_1_66_authority(&authority) ==
           HHS_EXACT_STATUS_OK);
    assert(authority.parent_1_65_required == 1U);
    assert(authority.gate_scoped_projection_required == 1U);
    assert(authority.ordinary_ratio_qr_symbol_separated == 1U);
    assert(authority.polarity_s_independent_default == 1U);
    assert(authority.canonical_seed_sign_preserved == 1U);
    assert(authority.signed_metric_projection_separate == 1U);
    assert(authority.cross_gate_substitution_authority == 0U);
    assert(authority.canonical_constant_rewrite_authority == 0U);
    assert(authority.commutation_authority == 0U);
    assert(authority.delta_cancellation_authority == 0U);
    assert(authority.canonical_vm81_mutation_authority == 0U);

    assert(hhs_exact_pass219_conservation_1_66_source(
        source, sizeof(source), &source_len) == HHS_EXACT_STATUS_OK);
    assert(source_len == HHS_EXACT_PASS219_CONSERVATION_1_66_SOURCE_BYTES);
    source[source_len] = 0U;
    assert(strstr((const char *)source, "ratio!=qr_symbol") != NULL);

    memset(&receipt, 0, sizeof(receipt));
    assert(hhs_exact_pass219_conservation_1_66_verify(&receipt) ==
           HHS_EXACT_STATUS_OK);
    assert(receipt.decision ==
           HHS_EXACT_PASS219_CONSERVATION_DECISION_VERIFIED);
    assert(receipt.source_hash_verified == 1U);
    assert(receipt.parent_1_65_verified == 1U);
    assert(receipt.operator_typing_verified == 1U);
    assert(receipt.pell_branch_verified == 1U);
    assert(receipt.reciprocal_correction_verified == 1U);
    assert(receipt.negative_s_factor_verified == 1U);
    assert(receipt.phase72_seed_verified == 1U);
    assert(receipt.congruent_projection_verified == 1U);
    assert(receipt.unit_shell_verified == 1U);
    assert(receipt.master_delta_m_projection_verified == 1U);
    assert(receipt.signed_metric_null_cone_verified == 1U);
    assert(receipt.canonical_c2_preserved == 1U);
    assert(receipt.polarity_balance_projection_verified == 1U);
    assert(receipt.unit_shell_x_plus_y_zero_verified == 1U);
    assert(receipt.scalar_projection_witness_only == 1U);
    assert(receipt.cross_gate_substitution_authority == 0U);
    assert(receipt.canonical_constant_rewrite_authority == 0U);
    assert(receipt.commutation_authority == 0U);
    assert(receipt.equality_reversal_authority == 0U);
    assert(receipt.delta_cancellation_authority == 0U);
    assert(receipt.floating_point_canonical_authority == 0U);
    assert(receipt.canonical_vm81_mutation_authority == 0U);
    assert(receipt.canonical_hash72_authority == 0U);
    assert(receipt.canonical_hash216_authority == 0U);
    return 0;
}
