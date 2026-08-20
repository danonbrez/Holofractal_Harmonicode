#include "../include/hhs_pass219b_global_zero_sum_closure_1_0.h"

#include <string.h>

static const uint8_t HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES] = {
    0x8c, 0x38, 0x6a, 0x42, 0xe1, 0x2b, 0x4a, 0xdc,
    0x9d, 0x3d, 0xcc, 0xad, 0x70, 0x67, 0x81, 0x22,
    0x9a, 0x16, 0xe8, 0x22, 0x88, 0x67, 0x8a, 0x8e,
    0xd1, 0x8c, 0x5a, 0x16, 0x01, 0x04, 0x15, 0x28
};

static uint32_t hhs_exact_pass219b_global_zero_sum_version_word(void) {
    return (HHS_EXACT_PASS219B_ZERO_SUM_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219B_ZERO_SUM_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219B_ZERO_SUM_VERSION_PATCH;
}

uint32_t hhs_exact_pass219b_global_zero_sum_version(void) {
    return hhs_exact_pass219b_global_zero_sum_version_word();
}

HHSExactStatus hhs_exact_pass219b_global_zero_sum_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES]
) {
    if (out_sha256 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memcpy(out_sha256, HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256,
           HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219b_global_zero_sum_prove(
    HHSExactPass219BGlobalZeroSumClosureV1 *out_proof
) {
    static const int8_t phase_coefficients[4][2] = {
        { 0,  1},
        {-1,  0},
        { 0, -1},
        { 1,  0}
    };
    int phase_real = 0;
    int phase_imag = 0;
    size_t i;

    if (out_proof == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_proof, 0, sizeof(*out_proof));
    out_proof->struct_size = (uint32_t)sizeof(*out_proof);
    out_proof->version = hhs_exact_pass219b_global_zero_sum_version_word();

    for (i = 0U; i < 4U; ++i) {
        phase_real += phase_coefficients[i][0];
        phase_imag += phase_coefficients[i][1];
    }
    if (phase_real != 0 || phase_imag != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_proof->phase_sum_real = (int8_t)phase_real;
    out_proof->phase_sum_imag = (int8_t)phase_imag;

    /*
     * Source-level center closure is a registered relation atom, not an
     * ordinary scalar solution of x,y,z,w. Pass 129 independently proves the
     * exact rational projection family with delta=1, xy=zw=1 and xyzw_sum=0.
     * This ABI binds that inherited theorem; it does not re-solve base symbols.
     */
    out_proof->center_zero_sum_proven = 1U;
    out_proof->phase_carrier_zero_sum_proven = 1U;
    out_proof->pass129_unit_delta_theorem_bound = 1U;
    out_proof->xy_unit_projection_bound = 1U;
    out_proof->zw_unit_projection_bound = 1U;
    out_proof->u72_unit_projection_bound = 1U;
    out_proof->denominator_unit_perimeter_count = HHS_EXACT_PASS219B_ZERO_SUM_UNIT_PERIMETER_COUNT;
    out_proof->denominator_center_zero_sum_preserved = 1U;

    /*
     * These two obligations remain intentionally unresolved here. The global
     * recursive relation N/D^4=D^4 and the complete monolithic equality chain
     * require the later exact full-symbolic evaluator. Zero-sum closure is a
     * necessary global admission invariant, not a substitute evaluator.
     */
    out_proof->recursive_fixed_point_required = 1U;
    out_proof->monolithic_chain_required = 1U;
    out_proof->full_monolithic_evaluated = 0U;
    out_proof->global_enforcement_required = 1U;

    out_proof->canonical_mutation_authority = 0U;
    out_proof->canonical_persistence_authority = 0U;
    out_proof->canonical_hash72_authority = 0U;

    out_proof->proof_mask = HHS_EXACT_PASS219B_ZERO_SUM_PROOF_REQUIRED;
    memcpy(out_proof->closure_extension_sha256, HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256,
           HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES);

    return hhs_exact_pass219b_global_zero_sum_verify(out_proof);
}

HHSExactStatus hhs_exact_pass219b_global_zero_sum_verify(
    const HHSExactPass219BGlobalZeroSumClosureV1 *proof
) {
    if (proof == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (proof->struct_size != sizeof(*proof) ||
        proof->version != hhs_exact_pass219b_global_zero_sum_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (proof->phase_sum_real != 0 || proof->phase_sum_imag != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (proof->center_zero_sum_proven != 1U ||
        proof->phase_carrier_zero_sum_proven != 1U ||
        proof->pass129_unit_delta_theorem_bound != 1U ||
        proof->xy_unit_projection_bound != 1U ||
        proof->zw_unit_projection_bound != 1U ||
        proof->u72_unit_projection_bound != 1U ||
        proof->denominator_unit_perimeter_count != HHS_EXACT_PASS219B_ZERO_SUM_UNIT_PERIMETER_COUNT ||
        proof->denominator_center_zero_sum_preserved != 1U ||
        proof->recursive_fixed_point_required != 1U ||
        proof->monolithic_chain_required != 1U ||
        proof->global_enforcement_required != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (proof->full_monolithic_evaluated != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (proof->proof_mask != HHS_EXACT_PASS219B_ZERO_SUM_PROOF_REQUIRED)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (memcmp(proof->closure_extension_sha256, HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256,
               HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (proof->canonical_mutation_authority != 0U ||
        proof->canonical_persistence_authority != 0U ||
        proof->canonical_hash72_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}
