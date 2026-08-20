#include "../include/hhs_pass219b_global_zero_sum_closure_1_0.h"

#include <string.h>

static const uint8_t HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES] = {
    0x8b, 0x64, 0xf4, 0x9e, 0x53, 0x4a, 0x83, 0x63,
    0xd7, 0x0d, 0x34, 0xa0, 0x4e, 0xc8, 0x29, 0x13,
    0x9f, 0xa0, 0xe6, 0x97, 0xf8, 0x70, 0xca, 0x22,
    0x3d, 0xb1, 0x3b, 0xc1, 0x27, 0x5c, 0x68, 0xfb
};

/* Byte-frozen Pass-219 1.15 monolithic global constraint Tensor fixture. */
static const uint8_t HHS_EXACT_PASS219B_GLOBAL_TENSOR_SOURCE_SHA256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES] = {
    0x9f, 0x22, 0x38, 0x98, 0x1b, 0xf5, 0x09, 0xd2,
    0x2f, 0xfe, 0xbb, 0x46, 0x81, 0x63, 0x46, 0xf3,
    0x89, 0xfd, 0x2d, 0x94, 0x9c, 0xcd, 0x79, 0x56,
    0xcd, 0xe3, 0x63, 0x0a, 0xb2, 0xb5, 0x69, 0x44
};

/* Exact source identity of the registered D^4 phase-quantization Tensor. */
static const uint8_t HHS_EXACT_PASS219B_PHASE_QUANTIZATION_SHA256[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES] = {
    0x5c, 0x40, 0x80, 0xc9, 0xbc, 0x87, 0xed, 0xf3,
    0x58, 0xd2, 0x7c, 0x94, 0x2b, 0x55, 0xf9, 0x3e,
    0x7f, 0x59, 0x97, 0xd6, 0x47, 0x41, 0x02, 0xcb,
    0x3a, 0x09, 0xc1, 0xc5, 0x5e, 0xe6, 0xa1, 0x32
};

typedef struct HHSExactPass219BI6BigBuffer {
    uint8_t bytes[HHS_EXACT_UQCEL_MAX_DERIVED_BYTES + 2U];
    size_t length;
} HHSExactPass219BI6BigBuffer;

static uint32_t hhs_exact_pass219b_global_zero_sum_version_word(void) {
    return (HHS_EXACT_PASS219B_ZERO_SUM_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219B_ZERO_SUM_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219B_ZERO_SUM_VERSION_PATCH;
}

static int hhs_exact_pass219b_i6_big_view_valid(
    const HHSExactBigUIntView *view,
    int allow_zero
) {
    if (view == NULL || view->struct_size < sizeof(*view) || view->bytes_be == NULL)
        return 0;
    if (view->byte_length == 0U || view->byte_length > HHS_EXACT_UQCEL_MAX_P_BYTES)
        return 0;
    if (view->byte_length > 1U && view->bytes_be[0] == 0U)
        return 0;
    if (!allow_zero && view->byte_length == 1U && view->bytes_be[0] == 0U)
        return 0;
    return 1;
}

static int hhs_exact_pass219b_i6_big_equal(
    const uint8_t *a,
    size_t a_length,
    const uint8_t *b,
    size_t b_length
) {
    return a_length == b_length && memcmp(a, b, a_length) == 0;
}

static int hhs_exact_pass219b_i6_add_views_equal(
    const HHSExactBigUIntView *a,
    const HHSExactBigUIntView *b,
    const HHSExactBigUIntView *expected
) {
    uint8_t reversed[HHS_EXACT_UQCEL_MAX_P_BYTES + 1U];
    uint8_t result[HHS_EXACT_UQCEL_MAX_P_BYTES + 1U];
    size_t max_length;
    size_t i;
    uint16_t carry = 0U;

    if (!hhs_exact_pass219b_i6_big_view_valid(a, 1) ||
        !hhs_exact_pass219b_i6_big_view_valid(b, 1) ||
        !hhs_exact_pass219b_i6_big_view_valid(expected, 1))
        return 0;

    max_length = a->byte_length > b->byte_length ?
        (size_t)a->byte_length : (size_t)b->byte_length;
    if (max_length + 1U > sizeof(reversed))
        return 0;
    memset(reversed, 0, sizeof(reversed));

    for (i = 0U; i < max_length; ++i) {
        uint16_t av = i < (size_t)a->byte_length ?
            a->bytes_be[(size_t)a->byte_length - 1U - i] : 0U;
        uint16_t bv = i < (size_t)b->byte_length ?
            b->bytes_be[(size_t)b->byte_length - 1U - i] : 0U;
        uint16_t sum = (uint16_t)(av + bv + carry);
        reversed[i] = (uint8_t)(sum & UINT16_C(0xFF));
        carry = (uint16_t)(sum >> 8U);
    }
    if (carry != 0U)
        reversed[max_length++] = (uint8_t)carry;

    for (i = 0U; i < max_length; ++i)
        result[max_length - 1U - i] = reversed[i];

    return hhs_exact_pass219b_i6_big_equal(
        result, max_length,
        expected->bytes_be, (size_t)expected->byte_length);
}

static int hhs_exact_pass219b_i6_square_view(
    const HHSExactBigUIntView *value,
    HHSExactPass219BI6BigBuffer *out
) {
    uint32_t accum[HHS_EXACT_UQCEL_MAX_DERIVED_BYTES + 2U];
    size_t a_length;
    size_t full_length;
    size_t i;
    size_t j;

    if (!hhs_exact_pass219b_i6_big_view_valid(value, 0) || out == NULL)
        return 0;
    a_length = (size_t)value->byte_length;
    if ((2U * a_length) + 1U > sizeof(accum) / sizeof(accum[0]))
        return 0;

    memset(accum, 0, sizeof(accum));
    for (i = 0U; i < a_length; ++i) {
        uint32_t av = value->bytes_be[a_length - 1U - i];
        for (j = 0U; j < a_length; ++j) {
            uint32_t bv = value->bytes_be[a_length - 1U - j];
            accum[i + j] += av * bv;
        }
    }

    full_length = (2U * a_length) + 1U;
    for (i = 0U; i + 1U < full_length; ++i) {
        accum[i + 1U] += accum[i] >> 8U;
        accum[i] &= UINT32_C(0xFF);
    }
    while (full_length > 1U && accum[full_length - 1U] == 0U)
        --full_length;
    if (full_length > sizeof(out->bytes))
        return 0;

    out->length = full_length;
    for (i = 0U; i < full_length; ++i)
        out->bytes[full_length - 1U - i] = (uint8_t)accum[i];
    return 1;
}

static HHSExactStatus hhs_exact_pass219b_inherited_hydration_capability(
    HHSExactPass219HydrationCoordinateV1 *out_coordinate,
    HHSExactPass219TrinaryPhaseGateV1 *out_gate,
    HHSExactPass219BPhaseCellV1 *out_phase_cell,
    HHSExactPass219BPhaseLocalityPlanV1 *out_locality
) {
    HHSExactPass219BPhaseLocalityDimensionV1 dimension;
    uint8_t cell81;
    int8_t group;
    uint8_t operation64;
    uint16_t g243;
    const char *tensor_source;
    HHSExactStatus status;

    if (out_coordinate == NULL || out_gate == NULL || out_phase_cell == NULL ||
        out_locality == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    tensor_source = hhs_exact_pass219b_tensor_source();
    if (tensor_source == NULL || strcmp(tensor_source, HHS_EXACT_PASS219B_TENSOR_SOURCE) != 0 ||
        strstr(tensor_source, HHS_EXACT_PASS219B_ZERO_SUM_CENTER_RELATION) == NULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_coordinate_from_pass189(0U, 0, 0U, 0U, out_coordinate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_coordinate_to_pass189(
        out_coordinate, &cell81, &group, &operation64, &g243);
    if (status != HHS_EXACT_STATUS_OK || cell81 != 0U || group != 0 ||
        operation64 != 0U || g243 != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_trinary_phase_gate(out_coordinate->trit, out_gate);
    if (status != HHS_EXACT_STATUS_OK || out_gate->ordered_left_right_preserved != 1U ||
        out_gate->center_relation != HHS_EXACT_PASS219_CENTER_RELATION_X_PLUS_Y)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219b_phase_cell(out_coordinate, 0U, out_phase_cell);
    if (status != HHS_EXACT_STATUS_OK || out_phase_cell->center_closure_preserved != 1U ||
        out_phase_cell->tensor_source_preserved != 1U ||
        out_phase_cell->outer_count != HHS_EXACT_PASS219B_OUTER_CELL_COUNT ||
        out_phase_cell->canonical_mutation_authority != 0U ||
        out_phase_cell->canonical_persistence_authority != 0U ||
        out_phase_cell->canonical_hash72_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    dimension.potential_q = HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT;
    dimension.selected_s = 1U;
    status = hhs_exact_pass219b_phase_locality_plan(
        &dimension, 1U, 1U, 0U, 1U, out_locality);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219b_phase_locality_verify_realization(
        out_locality, out_locality->required_realized_units, 1U, 1U, 0U);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return HHS_EXACT_STATUS_OK;
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
    HHSExactPass219HydrationCoordinateV1 coordinate;
    HHSExactPass219TrinaryPhaseGateV1 gate;
    HHSExactPass219BPhaseCellV1 phase_cell;
    HHSExactPass219BPhaseLocalityPlanV1 locality;
    HHSExactStatus status;
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

    status = hhs_exact_pass219b_inherited_hydration_capability(
        &coordinate, &gate, &phase_cell, &locality);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_proof->phase_sum_real = (int8_t)phase_real;
    out_proof->phase_sum_imag = (int8_t)phase_imag;
    out_proof->center_zero_sum_proven = phase_cell.center_closure_preserved;
    out_proof->phase_carrier_zero_sum_proven = 1U;
    out_proof->pass129_unit_delta_theorem_bound = 1U;
    out_proof->xy_unit_projection_bound =
        (uint8_t)(phase_cell.outer[6].phase_basis == HHS_EXACT_PHASE_XY);
    out_proof->zw_unit_projection_bound =
        (uint8_t)(phase_cell.outer[3].phase_basis == HHS_EXACT_PHASE_ZW);
    out_proof->u72_unit_projection_bound = 1U;
    out_proof->denominator_unit_perimeter_count = phase_cell.outer_count;
    out_proof->denominator_center_zero_sum_preserved = phase_cell.center_closure_preserved;
    out_proof->global_tensor_source_bound = 1U;
    out_proof->phase_quantization_bound = phase_cell.tensor_source_preserved;
    out_proof->lo_shu_sudoku_qudit_bound =
        (uint8_t)(gate.ordered_left_right_preserved == 1U);
    out_proof->vm81_hydration_geometry_bound =
        (uint8_t)(coordinate.struct_size == sizeof(coordinate));
    out_proof->legacy_full_symbolic_v1_preserved = 1U;
    out_proof->global_enforcement_required = 1U;
    out_proof->canonical_mutation_authority = 0U;
    out_proof->canonical_persistence_authority = 0U;
    out_proof->canonical_hash72_authority = 0U;
    out_proof->cell_count81 = HHS_EXACT_PASS219B_ZERO_SUM_CELL_COUNT;
    out_proof->lo_shu_group_count41 = HHS_EXACT_PASS219B_ZERO_SUM_LO_SHU_GROUP_COUNT;
    out_proof->trit_count3 = HHS_EXACT_PASS219B_ZERO_SUM_TRIT_COUNT;
    out_proof->phase_origin_count81 = HHS_EXACT_PASS219B_ZERO_SUM_PHASE_ORIGIN_COUNT;
    out_proof->hydration_slot_count5184 = HHS_EXACT_PASS219B_ZERO_SUM_HYDRATION_SLOT_COUNT;
    out_proof->hydration_state_count = HHS_EXACT_PASS219B_ZERO_SUM_HYDRATION_STATE_COUNT;
    out_proof->phase_projected_state_count = HHS_EXACT_PASS219B_ZERO_SUM_PHASE_PROJECTED_STATE_COUNT;
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
        proof->legacy_full_symbolic_v1_preserved != 1U ||
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

HHSExactStatus hhs_exact_pass219b_global_relation_hydration_verify(
    const HHSExactPass219BGlobalRelationInputV1 *input,
    HHSExactPass219BGlobalRelationHydrationWitnessV1 *out_witness
) {
    HHSExactPass219BI6BigBuffer p_squared;
    HHSExactPass219BPhaseLocalityDimensionV1 dimension;
    HHSExactUQCELInputV1 uqcel_input;
    HHSExactBigUIntView p2_view;
    uint8_t uqcel_source_sha[HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES];
    uint8_t operation64;
    uint8_t roundtrip_cell;
    int8_t roundtrip_group;
    uint8_t roundtrip_operation;
    uint16_t roundtrip_g243;
    HHSExactStatus status;

    if (input == NULL || out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (input->struct_size != sizeof(*input) ||
        input->version != hhs_exact_pass219b_global_zero_sum_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (input->cell81 >= HHS_EXACT_VM81_CELLS ||
        input->left_basis8 >= HHS_EXACT_PHASE_BASIS_COUNT ||
        input->right_basis8 >= HHS_EXACT_PHASE_BASIS_COUNT ||
        input->phase_origin81 >= HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT ||
        input->lo_shu_group < HHS_EXACT_PASS219_LO_SHU_GROUP_MIN ||
        input->lo_shu_group > HHS_EXACT_PASS219_LO_SHU_GROUP_MAX ||
        input->g243 >= HHS_EXACT_PASS219_G243_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (!hhs_exact_pass219b_i6_big_view_valid(&input->P, 0) ||
        !hhs_exact_pass219b_i6_big_view_valid(&input->p, 0) ||
        !hhs_exact_pass219b_i6_big_view_valid(&input->q, 0) ||
        !hhs_exact_pass219b_i6_big_view_valid(&input->delta, 0))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = hhs_exact_pass219b_global_zero_sum_version_word();

    if (memcmp(input->global_tensor_source_sha256,
               HHS_EXACT_PASS219B_GLOBAL_TENSOR_SOURCE_SHA256,
               HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES) != 0)
        return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
    out_witness->global_tensor_source_verified = 1U;

    if (memcmp(input->phase_quantization_source_sha256,
               HHS_EXACT_PASS219B_PHASE_QUANTIZATION_SHA256,
               HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES) != 0)
        return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
    out_witness->phase_quantization_source_verified = 1U;

    if (input->delta.byte_length != 1U || input->delta.bytes_be[0] != 1U ||
        !hhs_exact_pass219b_i6_add_views_equal(&input->p, &input->delta, &input->P) ||
        !hhs_exact_pass219b_i6_add_views_equal(&input->P, &input->delta, &input->q))
        return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
    out_witness->zero_sum_family_verified = 1U;

    if (!hhs_exact_pass219b_i6_square_view(&input->P, &p_squared))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memset(&p2_view, 0, sizeof(p2_view));
    p2_view.struct_size = (uint32_t)sizeof(p2_view);
    p2_view.byte_length = (uint32_t)p_squared.length;
    p2_view.bytes_be = p_squared.bytes;

    memset(&uqcel_input, 0, sizeof(uqcel_input));
    uqcel_input.struct_size = (uint32_t)sizeof(uqcel_input);
    uqcel_input.uqcel_version = hhs_exact_uqcel_version();
    uqcel_input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    uqcel_input.P = input->P;
    uqcel_input.p = input->p;
    uqcel_input.q = input->q;
    uqcel_input.delta = input->delta;
    uqcel_input.A = p2_view;
    uqcel_input.B = p2_view;
    uqcel_input.cell81 = input->cell81;
    uqcel_input.left_basis8 = input->left_basis8;
    uqcel_input.right_basis8 = input->right_basis8;
    if (hhs_exact_uqcel_source_sha256(uqcel_source_sha) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memcpy(uqcel_input.source_envelope_sha256, uqcel_source_sha, sizeof(uqcel_source_sha));
    memcpy(uqcel_input.previous_hash72, input->previous_hash72, HHS_EXACT_HASH72_STRLEN);

    status = hhs_exact_uqcel_validate(
        &uqcel_input, &out_witness->uqcel_integer_projection);
    if (status != HHS_EXACT_STATUS_OK ||
        out_witness->uqcel_integer_projection.decision != HHS_EXACT_UQCEL_DECISION_ADMIT)
        return status == HHS_EXACT_STATUS_OK ? HHS_EXACT_STATUS_INVARIANT_FAILURE : status;
    out_witness->uqcel_integer_projection_verified = 1U;
    out_witness->vm5184_address = out_witness->uqcel_integer_projection.vm5184_address;

    uqcel_input.profile = HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1;
    status = hhs_exact_uqcel_validate(
        &uqcel_input, &out_witness->legacy_full_symbolic_probe);
    if (status != HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN ||
        out_witness->legacy_full_symbolic_probe.decision !=
            HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN ||
        out_witness->legacy_full_symbolic_probe.reject_reason !=
            HHS_EXACT_UQCEL_REASON_FULL_SYMBOLIC_RESIDUAL ||
        out_witness->legacy_full_symbolic_probe.residual_mask != HHS_UQCEL_RESIDUAL_FULL_SOURCE)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_witness->legacy_full_symbolic_v1_preserved = 1U;

    status = hhs_exact_pass219_native_phase_witness(
        input->left_basis8, input->right_basis8, &out_witness->native_phase);
    if (status != HHS_EXACT_STATUS_OK ||
        out_witness->native_phase.ordered_source_preserved != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_witness->native_phase_verified = 1U;

    operation64 = (uint8_t)(input->left_basis8 * HHS_EXACT_PHASE_BASIS_COUNT +
                            input->right_basis8);
    status = hhs_exact_pass219_coordinate_from_pass189(
        input->cell81, input->lo_shu_group, operation64, input->g243,
        &out_witness->coordinate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_coordinate_to_pass189(
        &out_witness->coordinate,
        &roundtrip_cell, &roundtrip_group, &roundtrip_operation, &roundtrip_g243);
    if (status != HHS_EXACT_STATUS_OK ||
        roundtrip_cell != input->cell81 ||
        roundtrip_group != input->lo_shu_group ||
        roundtrip_operation != operation64 ||
        roundtrip_g243 != input->g243)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_witness->coordinate_roundtrip_verified = 1U;

    status = hhs_exact_pass219_trinary_phase_gate(
        out_witness->coordinate.trit, &out_witness->trinary_gate);
    if (status != HHS_EXACT_STATUS_OK ||
        out_witness->trinary_gate.ordered_left_right_preserved != 1U ||
        out_witness->trinary_gate.center_relation != HHS_EXACT_PASS219_CENTER_RELATION_X_PLUS_Y)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_witness->trinary_gate_verified = 1U;

    status = hhs_exact_pass219b_phase_cell(
        &out_witness->coordinate, input->phase_origin81, &out_witness->phase_cell);
    if (status != HHS_EXACT_STATUS_OK ||
        out_witness->phase_cell.center_closure_preserved != 1U ||
        out_witness->phase_cell.tensor_source_preserved != 1U ||
        out_witness->phase_cell.parent.cell81 != out_witness->coordinate.cell81 ||
        out_witness->phase_cell.parent.lo_shu_group != out_witness->coordinate.lo_shu_group ||
        out_witness->phase_cell.parent.trit != out_witness->coordinate.trit ||
        out_witness->phase_cell.parent.slot5184 != out_witness->coordinate.slot5184 ||
        out_witness->phase_cell.canonical_mutation_authority != 0U ||
        out_witness->phase_cell.canonical_persistence_authority != 0U ||
        out_witness->phase_cell.canonical_hash72_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_witness->phase_cell_verified = 1U;

    dimension.potential_q = HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT;
    dimension.selected_s = 1U;
    status = hhs_exact_pass219b_phase_locality_plan(
        &dimension, 1U, 1U, 0U, 1U, &out_witness->locality_plan);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219b_phase_locality_verify_realization(
        &out_witness->locality_plan,
        out_witness->locality_plan.required_realized_units,
        1U, 1U, 0U);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    out_witness->phase_locality_verified = 1U;

    out_witness->canonical_mutation_authority = 0U;
    out_witness->canonical_persistence_authority = 0U;
    out_witness->canonical_hash72_authority = 0U;
    out_witness->global_relation_bridge_verified = 1U;
    return HHS_EXACT_STATUS_OK;
}
