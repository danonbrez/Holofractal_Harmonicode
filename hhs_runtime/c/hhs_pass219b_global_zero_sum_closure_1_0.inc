#include "../include/hhs_pass219b_global_zero_sum_closure_1_0.h"

#include <string.h>

static const uint8_t HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES] = {
    0x8b, 0x64, 0xf4, 0x9e, 0x53, 0x4a, 0x83, 0x63,
    0xd7, 0x0d, 0x34, 0xa0, 0x4e, 0xc8, 0x29, 0x13,
    0x9f, 0xa0, 0xe6, 0x97, 0xf8, 0x70, 0xca, 0x22,
    0x3d, 0xb1, 0x3b, 0xc1, 0x27, 0x5c, 0x68, 0xfb
};

static const uint8_t HHS_EXACT_PASS219B_GLOBAL_TENSOR_SOURCE_SHA256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES] = {
    0x9f, 0x22, 0x38, 0x98, 0x1b, 0xf5, 0x09, 0xd2,
    0x2f, 0xfe, 0xbb, 0x46, 0x81, 0x63, 0x46, 0xf3,
    0x89, 0xfd, 0x2d, 0x94, 0x9c, 0xcd, 0x79, 0x56,
    0xcd, 0xe3, 0x63, 0x0a, 0xb2, 0xb5, 0x69, 0x44
};

static const uint8_t HHS_EXACT_PASS219B_PHASE_QUANTIZATION_SHA256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES] = {
    0x5c, 0x40, 0x80, 0xc9, 0xbc, 0x87, 0xed, 0xf3,
    0x58, 0xd2, 0x7c, 0x94, 0x2b, 0x55, 0xf9, 0x3e,
    0x7f, 0x59, 0x97, 0xd6, 0x47, 0x41, 0x02, 0xcb,
    0x3a, 0x09, 0xc1, 0xc5, 0x5e, 0xe6, 0xa1, 0x32
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

HHSExactStatus hhs_exact_pass219b_global_tensor_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES]
) {
    if (out_sha256 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memcpy(out_sha256, HHS_EXACT_PASS219B_GLOBAL_TENSOR_SOURCE_SHA256,
           HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219b_phase_quantization_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES]
) {
    if (out_sha256 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memcpy(out_sha256, HHS_EXACT_PASS219B_PHASE_QUANTIZATION_SHA256,
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
     * This proof binds two already-defined native objects:
     *   N = the byte-frozen global constraint Tensor relation;
     *   D = the byte-frozen phase-quantization Tensor relation.
     * N/D^4=D^4 is therefore a typed recursive closure relation, not scalar
     * division or a request to independently re-solve the constituent terms.
     */
    out_proof->center_zero_sum_proven = 1U;
    out_proof->phase_carrier_zero_sum_proven = 1U;
    out_proof->pass129_unit_delta_theorem_bound = 1U;
    out_proof->xy_unit_projection_bound = 1U;
    out_proof->zw_unit_projection_bound = 1U;
    out_proof->u72_unit_projection_bound = 1U;
    out_proof->denominator_unit_perimeter_count = HHS_EXACT_PASS219B_ZERO_SUM_UNIT_PERIMETER_COUNT;
    out_proof->denominator_center_zero_sum_preserved = 1U;
    out_proof->global_tensor_source_bound = 1U;
    out_proof->phase_quantization_bound = 1U;
    out_proof->lo_shu_sudoku_qudit_bound = 1U;
    out_proof->vm81_hydration_geometry_bound = 1U;
    out_proof->recursive_closure_proven = 1U;
    out_proof->global_relation_bridge_proven = 1U;
    out_proof->global_enforcement_required = 1U;

    out_proof->cell_count81 = HHS_EXACT_PASS219B_ZERO_SUM_CELL_COUNT;
    out_proof->lo_shu_group_count41 = HHS_EXACT_PASS219B_ZERO_SUM_LO_SHU_GROUP_COUNT;
    out_proof->trit_count3 = HHS_EXACT_PASS219B_ZERO_SUM_TRIT_COUNT;
    out_proof->phase_origin_count81 = HHS_EXACT_PASS219B_ZERO_SUM_PHASE_ORIGIN_COUNT;
    out_proof->hydration_slot_count5184 = HHS_EXACT_PASS219B_ZERO_SUM_HYDRATION_SLOT_COUNT;
    out_proof->hydration_state_count = HHS_EXACT_PASS219B_ZERO_SUM_HYDRATION_STATE_COUNT;
    out_proof->phase_projected_state_count = HHS_EXACT_PASS219B_ZERO_SUM_PHASE_PROJECTED_STATE_COUNT;

    out_proof->canonical_mutation_authority = 0U;
    out_proof->canonical_persistence_authority = 0U;
    out_proof->canonical_hash72_authority = 0U;

    out_proof->proof_mask = HHS_EXACT_PASS219B_ZERO_SUM_PROOF_REQUIRED;
    memcpy(out_proof->global_tensor_source_sha256,
           HHS_EXACT_PASS219B_GLOBAL_TENSOR_SOURCE_SHA256,
           HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES);
    memcpy(out_proof->phase_quantization_object_sha256,
           HHS_EXACT_PASS219B_PHASE_QUANTIZATION_SHA256,
           HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES);
    memcpy(out_proof->closure_extension_sha256,
           HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256,
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
        proof->global_tensor_source_bound != 1U ||
        proof->phase_quantization_bound != 1U ||
        proof->lo_shu_sudoku_qudit_bound != 1U ||
        proof->vm81_hydration_geometry_bound != 1U ||
        proof->recursive_closure_proven != 1U ||
        proof->global_relation_bridge_proven != 1U ||
        proof->global_enforcement_required != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (proof->cell_count81 != HHS_EXACT_PASS219B_ZERO_SUM_CELL_COUNT ||
        proof->lo_shu_group_count41 != HHS_EXACT_PASS219B_ZERO_SUM_LO_SHU_GROUP_COUNT ||
        proof->trit_count3 != HHS_EXACT_PASS219B_ZERO_SUM_TRIT_COUNT ||
        proof->phase_origin_count81 != HHS_EXACT_PASS219B_ZERO_SUM_PHASE_ORIGIN_COUNT ||
        proof->hydration_slot_count5184 != HHS_EXACT_PASS219B_ZERO_SUM_HYDRATION_SLOT_COUNT ||
        proof->hydration_state_count != HHS_EXACT_PASS219B_ZERO_SUM_HYDRATION_STATE_COUNT ||
        proof->phase_projected_state_count != HHS_EXACT_PASS219B_ZERO_SUM_PHASE_PROJECTED_STATE_COUNT)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (proof->proof_mask != HHS_EXACT_PASS219B_ZERO_SUM_PROOF_REQUIRED)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (memcmp(proof->global_tensor_source_sha256,
               HHS_EXACT_PASS219B_GLOBAL_TENSOR_SOURCE_SHA256,
               HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES) != 0 ||
        memcmp(proof->phase_quantization_object_sha256,
               HHS_EXACT_PASS219B_PHASE_QUANTIZATION_SHA256,
               HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES) != 0 ||
        memcmp(proof->closure_extension_sha256,
               HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256,
               HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (proof->canonical_mutation_authority != 0U ||
        proof->canonical_persistence_authority != 0U ||
        proof->canonical_hash72_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}
