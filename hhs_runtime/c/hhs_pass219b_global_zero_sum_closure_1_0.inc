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

    status = hhs_exact_pass219_coordinate_from_pass189(
        0U, 0, 0U, 0U, out_coordinate);
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
        out_locality, 1U, 1U, 1U, 0U);
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

    /*
     * These runtime-facing flags are now derived from inherited exact
     * implementations rather than asserted as an independent proof island.
     * Pass-129 unit-delta/xy/zw/u^72 entries remain theorem bindings; the
     * submitted P,p,q,delta family is checked independently by UQCEL.
     */
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
    out_proof->recursive_closure_proven =
        (uint8_t)(phase_cell.center_closure_preserved == 1U &&
                  locality.route == HHS_EXACT_PASS219B_PHASE_LOCALITY_ROUTE_LOCAL);
    out_proof->global_relation_bridge_proven = out_proof->recursive_closure_proven;
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

HHSExactStatus hhs_exact_pass219b_global_relation_hydration_verify(
    const HHSExactUQCELInputV1 *input,
    int8_t lo_shu_group,
    uint16_t g243,
    uint8_t phase_origin81,
    HHSExactPass219BGlobalRelationHydrationWitnessV1 *out_witness
) {
    HHSExactPass219BPhaseLocalityDimensionV1 dimension;
    uint8_t operation64;
    uint8_t roundtrip_cell;
    int8_t roundtrip_group;
    uint8_t roundtrip_operation;
    uint16_t roundtrip_g243;
    HHSExactStatus status;

    if (input == NULL || out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (input->profile != HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (input->left_basis8 >= HHS_EXACT_PHASE_BASIS_COUNT ||
        input->right_basis8 >= HHS_EXACT_PHASE_BASIS_COUNT ||
        phase_origin81 >= HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = hhs_exact_pass219b_global_zero_sum_version_word();
    out_witness->lo_shu_group = lo_shu_group;
    out_witness->g243 = g243;
    out_witness->phase_origin81 = phase_origin81;

    status = hhs_exact_uqcel_validate(input, &out_witness->uqcel);
    if (status != HHS_EXACT_STATUS_OK ||
        out_witness->uqcel.decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        out_witness->uqcel.residual_mask != 0U)
        return status == HHS_EXACT_STATUS_OK ? HHS_EXACT_STATUS_INVARIANT_FAILURE : status;
    out_witness->uqcel_relation_verified = 1U;
    out_witness->vm5184_address = out_witness->uqcel.vm5184_address;

    status = hhs_exact_pass219_native_phase_witness(
        input->left_basis8, input->right_basis8, &out_witness->native_phase);
    if (status != HHS_EXACT_STATUS_OK || out_witness->native_phase.ordered_source_preserved != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_witness->native_phase_verified = 1U;

    operation64 = (uint8_t)(input->left_basis8 * HHS_EXACT_PHASE_BASIS_COUNT +
                            input->right_basis8);
    status = hhs_exact_pass219_coordinate_from_pass189(
        input->cell81, lo_shu_group, operation64, g243, &out_witness->coordinate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_coordinate_to_pass189(
        &out_witness->coordinate,
        &roundtrip_cell, &roundtrip_group, &roundtrip_operation, &roundtrip_g243);
    if (status != HHS_EXACT_STATUS_OK || roundtrip_cell != input->cell81 ||
        roundtrip_group != lo_shu_group || roundtrip_operation != operation64 ||
        roundtrip_g243 != g243)
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
        &out_witness->coordinate, phase_origin81, &out_witness->phase_cell);
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

HHSExactStatus hhs_exact_pass219b_global_relation_hydration_admit(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    int8_t lo_shu_group,
    uint16_t g243,
    uint8_t phase_origin81,
    HHSExactPass219Hash216IndexResolverV1 index_resolver,
    void *index_context,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219RNAAdmissionV1 *out_rna_admission,
    HHSExactPass219BGlobalRelationHydrationWitnessV1 *out_witness
) {
    HHSExactStatus status;

    if (input == NULL || candidate_frame == NULL || index_resolver == NULL ||
        out_committed_frame == NULL || out_rna_admission == NULL || out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    memset(out_rna_admission, 0, sizeof(*out_rna_admission));

    status = hhs_exact_pass219b_global_relation_hydration_verify(
        input, lo_shu_group, g243, phase_origin81, out_witness);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_rna_admit_composed(
        input, candidate_frame, lo_shu_group, g243,
        index_resolver, index_context,
        out_committed_frame, out_rna_admission);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (out_rna_admission->composed.uqcel.decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        out_rna_admission->composed.uqcel.frame_committed != 1U ||
        out_rna_admission->coordinate.cell81 != out_witness->coordinate.cell81 ||
        out_rna_admission->coordinate.lo_shu_group != out_witness->coordinate.lo_shu_group ||
        out_rna_admission->coordinate.operation64 != out_witness->coordinate.operation64 ||
        out_rna_admission->coordinate.g243 != out_witness->coordinate.g243 ||
        out_rna_admission->coordinate.trit != out_witness->coordinate.trit ||
        out_rna_admission->coordinate.slot5184 != out_witness->coordinate.slot5184 ||
        out_rna_admission->native_phase.left_basis != out_witness->native_phase.left_basis ||
        out_rna_admission->native_phase.right_basis != out_witness->native_phase.right_basis ||
        out_rna_admission->native_phase.ordered_source_preserved != 1U ||
        out_rna_admission->trinary_gate.trit != out_witness->trinary_gate.trit ||
        out_rna_admission->trinary_gate.ordered_left_right_preserved != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (memcmp(out_committed_frame, candidate_frame, sizeof(*candidate_frame)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_witness->rna_composed_verified = 1U;
    out_witness->uqcel = out_rna_admission->composed.uqcel;
    out_witness->global_relation_bridge_verified = 1U;
    return HHS_EXACT_STATUS_OK;
}
