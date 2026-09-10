#include "../include/hhs_pass219_hhcq_rotational_resolution_1_25.h"

#include <string.h>

static const uint16_t HHS_P219_HHCQ_DIVISORS[HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT] = {
    UINT16_C(5184), UINT16_C(2592), UINT16_C(1728), UINT16_C(1296), UINT16_C(864),
    UINT16_C(648), UINT16_C(576), UINT16_C(432), UINT16_C(324), UINT16_C(288),
    UINT16_C(216), UINT16_C(192), UINT16_C(162), UINT16_C(144), UINT16_C(108),
    UINT16_C(96), UINT16_C(81), UINT16_C(72), UINT16_C(64), UINT16_C(54),
    UINT16_C(48), UINT16_C(36), UINT16_C(32), UINT16_C(27), UINT16_C(24),
    UINT16_C(18), UINT16_C(16), UINT16_C(12), UINT16_C(9), UINT16_C(8),
    UINT16_C(6), UINT16_C(4), UINT16_C(3), UINT16_C(2), UINT16_C(1)
};

static uint64_t hhs_p219_hhcq_mix64(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static uint64_t hhs_p219_hhcq_frame_signature(const HHSExactVM81Frame *frame) {
    uint32_t i;
    uint64_t sig = UINT64_C(0x2195184072000125);
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        sig = hhs_p219_hhcq_mix64(sig ^ frame->words[i] ^ ((uint64_t)i << 48U));
    }
    return sig;
}

static int hhs_p219_hhcq_selection_valid(
    const HHSExactPass219HHCQResolutionSelectionV1 *selection
) {
    uint16_t divisor;
    if (selection == NULL ||
        selection->struct_size != sizeof(*selection) ||
        selection->version != HHS_EXACT_PASS219_HHCQ_RESOLUTION_VERSION ||
        selection->x_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        selection->y_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        selection->z_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        selection->w_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        selection->trinary_direction < -1 || selection->trinary_direction > 1 ||
        selection->xz_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        selection->yw_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        selection->quotient_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        selection->rotated_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        selection->resolution_index >= HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT ||
        selection->candidate_only != 1U ||
        selection->exact_integer_only != 1U ||
        selection->canonical_mutation_authority != 0U ||
        selection->canonical_hash72_authority != 0U ||
        selection->canonical_hash216_authority != 0U ||
        selection->canonical_persistence_authority != 0U ||
        selection->floating_point_authority != 0U)
        return 0;
    divisor = HHS_P219_HHCQ_DIVISORS[selection->resolution_index];
    if (selection->resolution_parameters != divisor || divisor == 0U ||
        (HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT % divisor) != 0U ||
        selection->region_count != HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT / divisor)
        return 0;
    return 1;
}

uint32_t hhs_exact_pass219_hhcq_resolution_version(void) {
    return HHS_EXACT_PASS219_HHCQ_RESOLUTION_VERSION;
}

HHSExactStatus hhs_exact_pass219_hhcq_resolution_descriptor(
    HHSExactPass219HHCQResolutionDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_HHCQ_RESOLUTION_VERSION;
    out_descriptor->parameter_count = HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT;
    out_descriptor->phase_modulus = HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS;
    out_descriptor->divisor_count = HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT;
    out_descriptor->trinary_step = HHS_EXACT_PASS219_HHCQ_TRINARY_STEP;
    out_descriptor->complete_2a3b_divisor_lattice = 1U;
    out_descriptor->ordered_xz_over_yw_phase_quotient = 1U;
    out_descriptor->dyadic_trinary_dual_primitive = 1U;
    out_descriptor->exact_orthogonal_decomposition = 1U;
    out_descriptor->core_equation_constructor_bound = 1U;
    out_descriptor->u72_rotational_ring = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->exact_integer_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_resolution_divisor(
    uint8_t resolution_index,
    uint16_t *out_parameters
) {
    if (out_parameters == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (resolution_index >= HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *out_parameters = HHS_P219_HHCQ_DIVISORS[resolution_index];
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_resolution_select(
    uint8_t x_phase72,
    uint8_t y_phase72,
    uint8_t z_phase72,
    uint8_t w_phase72,
    int8_t trinary_direction,
    HHSExactPass219HHCQResolutionSelectionV1 *out_selection
) {
    HHSExactPass219OctonionStateV1 octonion;
    HHSExactPass219OctonionProductV1 xz;
    HHSExactPass219OctonionProductV1 yw;
    HHSExactStatus status;
    int32_t rotated;
    uint32_t index;
    uint16_t divisor;
    uint64_t sig;

    if (out_selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (x_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        y_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        z_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        w_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        trinary_direction < -1 || trinary_direction > 1)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    status = hhs_exact_pass219_octonion_expand(
        x_phase72, y_phase72, z_phase72, w_phase72, &octonion);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_octonion_multiply(
        &octonion, HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Z, &xz);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_octonion_multiply(
        &octonion, HHS_EXACT_PHASE_Y, HHS_EXACT_PHASE_W, &yw);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(out_selection, 0, sizeof(*out_selection));
    out_selection->struct_size = (uint32_t)sizeof(*out_selection);
    out_selection->version = HHS_EXACT_PASS219_HHCQ_RESOLUTION_VERSION;
    out_selection->x_phase72 = x_phase72;
    out_selection->y_phase72 = y_phase72;
    out_selection->z_phase72 = z_phase72;
    out_selection->w_phase72 = w_phase72;
    out_selection->trinary_direction = trinary_direction;
    out_selection->xz_phase72 = xz.phase;
    out_selection->yw_phase72 = yw.phase;
    out_selection->quotient_phase72 = (uint8_t)(
        ((uint32_t)xz.phase + HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS - (uint32_t)yw.phase) %
        HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS);
    rotated = (int32_t)out_selection->quotient_phase72 +
        (int32_t)trinary_direction * (int32_t)HHS_EXACT_PASS219_HHCQ_TRINARY_STEP;
    while (rotated < 0)
        rotated += (int32_t)HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS;
    rotated %= (int32_t)HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS;
    out_selection->rotated_phase72 = (uint8_t)rotated;
    index = ((uint32_t)out_selection->rotated_phase72 * HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT) /
        HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS;
    if (index >= HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    divisor = HHS_P219_HHCQ_DIVISORS[index];
    if ((HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT % divisor) != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_selection->resolution_index = (uint8_t)index;
    out_selection->resolution_parameters = divisor;
    out_selection->region_count = (uint16_t)(HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT / divisor);
    out_selection->xz_orientation = xz.orientation;
    out_selection->yw_orientation = yw.orientation;
    out_selection->candidate_only = 1U;
    out_selection->exact_integer_only = 1U;
    sig = UINT64_C(0x2190725184000125) ^
        ((uint64_t)x_phase72 << 56U) ^ ((uint64_t)y_phase72 << 48U) ^
        ((uint64_t)z_phase72 << 40U) ^ ((uint64_t)w_phase72 << 32U) ^
        ((uint64_t)out_selection->quotient_phase72 << 24U) ^
        ((uint64_t)out_selection->rotated_phase72 << 16U) ^
        ((uint64_t)out_selection->resolution_parameters << 1U) ^
        (uint64_t)(uint8_t)(trinary_direction + 1);
    out_selection->selection_signature64 = hhs_p219_hhcq_mix64(sig);

    return hhs_p219_hhcq_selection_valid(out_selection)
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_hhcq_parameter_locate(
    const HHSExactPass219HHCQResolutionSelectionV1 *selection,
    uint16_t parameter_index,
    HHSExactPass219HHCQParameterCoordinateV1 *out_coordinate
) {
    uint16_t divisor;
    if (out_coordinate == NULL || selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_p219_hhcq_selection_valid(selection))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if ((uint32_t)parameter_index >= HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    divisor = selection->resolution_parameters;
    memset(out_coordinate, 0, sizeof(*out_coordinate));
    out_coordinate->struct_size = (uint32_t)sizeof(*out_coordinate);
    out_coordinate->version = HHS_EXACT_PASS219_HHCQ_RESOLUTION_VERSION;
    out_coordinate->parameter_index = parameter_index;
    out_coordinate->region_index = (uint16_t)(parameter_index / divisor);
    out_coordinate->local_offset = (uint16_t)(parameter_index % divisor);
    out_coordinate->region_start = (uint16_t)(out_coordinate->region_index * divisor);
    out_coordinate->resolution_parameters = divisor;
    out_coordinate->region_count = selection->region_count;
    out_coordinate->exact_integer_only = 1U;
    if ((uint32_t)out_coordinate->region_start + out_coordinate->local_offset != parameter_index ||
        out_coordinate->region_index >= selection->region_count)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_decompose_recompose(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219HHCQResolutionSelectionV1 *selection,
    HHSExactVM81Frame *out_frame,
    HHSExactPass219HHCQRoundtripReportV1 *out_report
) {
    uint64_t visited[HHS_EXACT_VM81_CELLS];
    uint32_t parameter;
    uint8_t overlap = 0U;
    uint8_t gap = 0U;
    uint64_t decomp_sig = UINT64_C(0x219d3c0a51840125);

    if (frame == NULL || selection == NULL || out_frame == NULL || out_report == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_p219_hhcq_selection_valid(selection))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_frame, 0, sizeof(*out_frame));
    memset(out_report, 0, sizeof(*out_report));
    memset(visited, 0, sizeof(visited));

    for (parameter = 0U; parameter < HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT; ++parameter) {
        HHSExactPass219HHCQParameterCoordinateV1 coordinate;
        uint32_t reconstructed;
        uint32_t source_word;
        uint32_t source_bit;
        uint32_t target_word;
        uint32_t target_bit;
        uint64_t target_mask;
        HHSExactStatus status = hhs_exact_pass219_hhcq_parameter_locate(
            selection, (uint16_t)parameter, &coordinate);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        reconstructed = (uint32_t)coordinate.region_start + (uint32_t)coordinate.local_offset;
        if (reconstructed >= HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        source_word = parameter / HHS_EXACT_VM81_WORD_BITS;
        source_bit = parameter % HHS_EXACT_VM81_WORD_BITS;
        target_word = reconstructed / HHS_EXACT_VM81_WORD_BITS;
        target_bit = reconstructed % HHS_EXACT_VM81_WORD_BITS;
        target_mask = UINT64_C(1) << target_bit;
        if ((visited[target_word] & target_mask) != 0U)
            overlap = 1U;
        visited[target_word] |= target_mask;
        if ((frame->words[source_word] & (UINT64_C(1) << source_bit)) != 0U)
            out_frame->words[target_word] |= target_mask;
        decomp_sig = hhs_p219_hhcq_mix64(
            decomp_sig ^ ((uint64_t)coordinate.region_index << 48U) ^
            ((uint64_t)coordinate.local_offset << 32U) ^
            ((uint64_t)selection->resolution_parameters << 16U) ^ parameter);
    }

    for (parameter = 0U; parameter < HHS_EXACT_VM81_CELLS; ++parameter) {
        if (visited[parameter] != UINT64_MAX)
            gap = 1U;
    }

    out_report->struct_size = (uint32_t)sizeof(*out_report);
    out_report->version = HHS_EXACT_PASS219_HHCQ_RESOLUTION_VERSION;
    out_report->parameters_visited = HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT;
    out_report->resolution_parameters = selection->resolution_parameters;
    out_report->region_count = selection->region_count;
    out_report->input_signature64 = hhs_p219_hhcq_frame_signature(frame);
    out_report->output_signature64 = hhs_p219_hhcq_frame_signature(out_frame);
    out_report->decomposition_signature64 = decomp_sig;
    out_report->no_overlap = overlap == 0U ? 1U : 0U;
    out_report->no_gap = gap == 0U ? 1U : 0U;
    out_report->orthogonal_partition_complete =
        out_report->no_overlap == 1U && out_report->no_gap == 1U &&
        ((uint32_t)selection->resolution_parameters * (uint32_t)selection->region_count ==
         HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT) ? 1U : 0U;
    out_report->exact_recomposition =
        memcmp(frame, out_frame, sizeof(*frame)) == 0 &&
        out_report->input_signature64 == out_report->output_signature64 ? 1U : 0U;
    out_report->candidate_only = 1U;
    out_report->exact_integer_only = 1U;
    out_report->canonical_authority_changed = 0U;
    out_report->floating_point_authority = 0U;

    return out_report->orthogonal_partition_complete == 1U &&
           out_report->exact_recomposition == 1U
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}
