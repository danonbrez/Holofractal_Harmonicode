#include "../include/hhs_pass219_mandatory_genesis_scaling_1_22.h"

#include <limits.h>
#include <string.h>

static const uint8_t HHS219_GENESIS_SUDOKU[HHS_EXACT_PASS219_GENESIS_CELL_COUNT] = {
    0,1,2,3,4,5,6,7,8,
    3,4,5,6,7,8,0,1,2,
    6,7,8,0,1,2,3,4,5,
    8,2,4,1,3,0,7,5,6,
    5,0,6,4,2,7,1,8,3,
    7,3,1,5,8,6,4,2,0,
    1,8,7,2,0,3,5,6,4,
    2,6,0,7,5,4,8,3,1,
    4,5,3,8,6,1,2,0,7
};

static const uint8_t HHS219_GENESIS_LOSHU[HHS_EXACT_PASS219_GENESIS_SIDE] = {
    4,9,2,3,5,7,8,1,6
};

static uint32_t hhs219_mandatory_version_word(void) {
    return (HHS_EXACT_PASS219_MANDATORY_GENESIS_SCALING_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_MANDATORY_GENESIS_SCALING_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_MANDATORY_GENESIS_SCALING_VERSION_PATCH;
}

static int hhs219_bool_u8(uint8_t value) {
    return value <= 1U;
}

static int hhs219_work_kind_valid(uint32_t work_kind) {
    return work_kind >= HHS_EXACT_PASS219_WORK_DATA_INGEST &&
           work_kind <= HHS_EXACT_PASS219_WORK_REPLAY;
}

static uint8_t hhs219_phase_channel_for_loshu(uint8_t value) {
    switch (value) {
        case 4U: return HHS_EXACT_PASS219_GENESIS_PHASE_X;
        case 9U: return HHS_EXACT_PASS219_GENESIS_PHASE_Y;
        case 2U: return HHS_EXACT_PASS219_GENESIS_PHASE_Z;
        case 3U: return HHS_EXACT_PASS219_GENESIS_PHASE_W;
        case 5U: return HHS_EXACT_PASS219_GENESIS_PHASE_ONE;
        case 7U: return HHS_EXACT_PASS219_GENESIS_PHASE_XY;
        case 8U: return HHS_EXACT_PASS219_GENESIS_PHASE_YX;
        case 1U: return HHS_EXACT_PASS219_GENESIS_PHASE_ZW;
        case 6U: return HHS_EXACT_PASS219_GENESIS_PHASE_WZ;
        default: return UINT8_MAX;
    }
}

static int8_t hhs219_trit_for_symbol(uint8_t symbol) {
    return (int8_t)((int32_t)(symbol % 3U) - 1);
}

static uint16_t hhs219_symbol_bit(uint8_t symbol) {
    return (uint16_t)(UINT16_C(1) << symbol);
}

static uint64_t hhs219_selected_prefix(uint64_t count, uint32_t p, uint32_t q) {
    const uint64_t blocks = count / (uint64_t)q;
    const uint64_t remainder = count % (uint64_t)q;
    const uint64_t tail = remainder < (uint64_t)p ? remainder : (uint64_t)p;
    return blocks * (uint64_t)p + tail;
}

static int hhs219_mul_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL)
        return 0;
    if (a != 0U && b > UINT64_MAX / a)
        return 0;
    *out = a * b;
    return 1;
}

uint32_t hhs_exact_pass219_mandatory_genesis_scaling_version(void) {
    return hhs219_mandatory_version_word();
}

HHSExactStatus hhs_exact_pass219_genesis_descriptor(
    HHSExactPass219GenesisDescriptorV1 *out_descriptor
) {
    uint16_t row_masks[HHS_EXACT_PASS219_GENESIS_SIDE] = {0};
    uint16_t column_masks[HHS_EXACT_PASS219_GENESIS_SIDE] = {0};
    uint16_t block_masks[HHS_EXACT_PASS219_GENESIS_SIDE] = {0};
    int32_t row_sums[HHS_EXACT_PASS219_GENESIS_SIDE] = {0};
    int32_t column_sums[HHS_EXACT_PASS219_GENESIS_SIDE] = {0};
    int32_t block_sums[HHS_EXACT_PASS219_GENESIS_SIDE] = {0};
    uint16_t diagonal_masks[2] = {0, 0};
    int32_t diagonal_sums[2] = {0, 0};
    uint32_t cell;
    int sudoku_valid = 1;
    int row_zero = 1;
    int column_zero = 1;
    int block_zero = 1;
    int diagonal_zero = 1;
    int loshu_valid = 1;
    int phase_valid = 1;

    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs219_mandatory_version_word();
    out_descriptor->cell_count = HHS_EXACT_PASS219_GENESIS_CELL_COUNT;
    out_descriptor->address_count = HHS_EXACT_PASS219_GENESIS_ADDRESS_COUNT;

    for (cell = 0U; cell < HHS_EXACT_PASS219_GENESIS_CELL_COUNT; ++cell) {
        const uint8_t row = (uint8_t)(cell / HHS_EXACT_PASS219_GENESIS_SIDE);
        const uint8_t column = (uint8_t)(cell % HHS_EXACT_PASS219_GENESIS_SIDE);
        const uint8_t symbol = HHS219_GENESIS_SUDOKU[cell];
        const uint8_t local_row = (uint8_t)(row % 3U);
        const uint8_t local_column = (uint8_t)(column % 3U);
        const uint8_t loshu = HHS219_GENESIS_LOSHU[(uint32_t)local_row * 3U + local_column];
        const uint8_t phase = hhs219_phase_channel_for_loshu(loshu);
        const int8_t trit = hhs219_trit_for_symbol(symbol);
        const uint32_t block = (uint32_t)(row / 3U) * 3U + (uint32_t)(column / 3U);
        HHSExactPass219GenesisCellV1 *record = &out_descriptor->cells[cell];

        if (symbol >= 9U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        record->cell81 = (uint8_t)cell;
        record->row9 = row;
        record->column9 = column;
        record->sudoku_symbol9 = symbol;
        record->trit = trit;
        record->lo_shu_value = loshu;
        record->phase_channel = phase;
        record->reserved0 = 0U;

        row_masks[row] |= hhs219_symbol_bit(symbol);
        column_masks[column] |= hhs219_symbol_bit(symbol);
        block_masks[block] |= hhs219_symbol_bit(symbol);
        row_sums[row] += trit;
        column_sums[column] += trit;
        block_sums[block] += trit;

        if (row == column) {
            diagonal_masks[0] |= hhs219_symbol_bit(symbol);
            diagonal_sums[0] += trit;
        }
        if ((uint32_t)row + (uint32_t)column == 8U) {
            diagonal_masks[1] |= hhs219_symbol_bit(symbol);
            diagonal_sums[1] += trit;
        }

        if (loshu != HHS219_GENESIS_LOSHU[(uint32_t)(row % 3U) * 3U + (column % 3U)])
            loshu_valid = 0;
        if (phase == UINT8_MAX || phase != hhs219_phase_channel_for_loshu(loshu))
            phase_valid = 0;
    }

    for (cell = 0U; cell < HHS_EXACT_PASS219_GENESIS_SIDE; ++cell) {
        if (row_masks[cell] != UINT16_C(0x1FF) ||
            column_masks[cell] != UINT16_C(0x1FF) ||
            block_masks[cell] != UINT16_C(0x1FF))
            sudoku_valid = 0;
        if (row_sums[cell] != 0)
            row_zero = 0;
        if (column_sums[cell] != 0)
            column_zero = 0;
        if (block_sums[cell] != 0)
            block_zero = 0;
    }

    if (diagonal_masks[0] != UINT16_C(0x1FF) ||
        diagonal_masks[1] != UINT16_C(0x1FF))
        sudoku_valid = 0;
    if (diagonal_sums[0] != 0 || diagonal_sums[1] != 0)
        diagonal_zero = 0;

    out_descriptor->sudoku_valid = (uint8_t)(sudoku_valid ? 1U : 0U);
    out_descriptor->trinary_zero_sum_rows = (uint8_t)(row_zero ? 1U : 0U);
    out_descriptor->trinary_zero_sum_columns = (uint8_t)(column_zero ? 1U : 0U);
    out_descriptor->trinary_zero_sum_blocks = (uint8_t)(block_zero ? 1U : 0U);
    out_descriptor->trinary_zero_sum_diagonals = (uint8_t)(diagonal_zero ? 1U : 0U);
    out_descriptor->lo_shu_binding_valid = (uint8_t)(loshu_valid ? 1U : 0U);
    out_descriptor->phase_channel_binding_valid = (uint8_t)(phase_valid ? 1U : 0U);
    out_descriptor->hydration_rom_empty_state = 1U;
    out_descriptor->addressable_geometry_initialized = 1U;
    out_descriptor->hydrated_payload_present = 0U;
    out_descriptor->canonical_pass219_data_plane = 1U;

    if (!sudoku_valid || !row_zero || !column_zero || !block_zero ||
        !diagonal_zero || !loshu_valid || !phase_valid)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_genesis_validate(
    const HHSExactPass219GenesisDescriptorV1 *descriptor
) {
    HHSExactPass219GenesisDescriptorV1 expected;
    HHSExactStatus status;

    if (descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->struct_size != sizeof(*descriptor) ||
        descriptor->version != hhs219_mandatory_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = hhs_exact_pass219_genesis_descriptor(&expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return memcmp(descriptor, &expected, sizeof(expected)) == 0
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_genesis_address_encode(
    uint8_t cell81,
    uint8_t operation64,
    HHSExactPass219GenesisAddressV1 *out_address
) {
    uint16_t linear;

    if (out_address == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (cell81 >= HHS_EXACT_PASS219_GENESIS_CELL_COUNT ||
        operation64 >= HHS_EXACT_PASS219_GENESIS_OPERATIONS_PER_CELL)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    linear = (uint16_t)((uint16_t)cell81 * HHS_EXACT_PASS219_GENESIS_OPERATIONS_PER_CELL +
                        (uint16_t)operation64);
    out_address->linear5184 = linear;
    out_address->cell81 = cell81;
    out_address->operation64 = operation64;
    out_address->phase_alpha8 = (uint8_t)(operation64 / HHS_EXACT_PASS219_GENESIS_PHASE_SIDE);
    out_address->phase_beta8 = (uint8_t)(operation64 % HHS_EXACT_PASS219_GENESIS_PHASE_SIDE);
    out_address->hash72_row = (uint8_t)(linear / HHS_EXACT_PASS219_GENESIS_HASH72_SIDE);
    out_address->hash72_column = (uint8_t)(linear % HHS_EXACT_PASS219_GENESIS_HASH72_SIDE);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_genesis_address_decode(
    uint16_t linear5184,
    HHSExactPass219GenesisAddressV1 *out_address
) {
    uint8_t cell;
    uint8_t operation;

    if (out_address == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (linear5184 >= HHS_EXACT_PASS219_GENESIS_ADDRESS_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    cell = (uint8_t)(linear5184 / HHS_EXACT_PASS219_GENESIS_OPERATIONS_PER_CELL);
    operation = (uint8_t)(linear5184 % HHS_EXACT_PASS219_GENESIS_OPERATIONS_PER_CELL);
    return hhs_exact_pass219_genesis_address_encode(cell, operation, out_address);
}

HHSExactStatus hhs_exact_pass219_mandatory_scaling_plan(
    const HHSExactPass219MandatoryScalingRequestV1 *request,
    HHSExactPass219MandatoryScalingPlanV1 *out_plan
) {
    HHSExactPass219GenesisDescriptorV1 genesis;
    HHSExactPass219BPhaseLocalityDimensionV1 dimensions[HHS_EXACT_PASS219_GENESIS_MAX_PHASE_DEPTH];
    HHSExactPass219BPhaseLocalityPlanV1 phase_plan;
    HHSExactPass219BSelectiveProjectionPlanV1 projection_plan;
    uint64_t base_lane_units;
    uint64_t sparse_update = 0U;
    uint32_t dirty_count = 0U;
    uint32_t i;
    HHSExactStatus status;

    if (request == NULL || out_plan == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (request->struct_size != sizeof(*request) ||
        request->version != hhs219_mandatory_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (!hhs219_work_kind_valid(request->work_kind))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (request->source_count == 0U || request->source_count > UINT32_MAX ||
        request->candidate_family_count == 0U ||
        request->phase_depth == 0U ||
        request->phase_depth > HHS_EXACT_PASS219_GENESIS_MAX_PHASE_DEPTH ||
        request->projection_denominator_q == 0U ||
        request->projection_numerator_p == 0U ||
        request->projection_numerator_p > request->projection_denominator_q)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (!hhs219_bool_u8(request->exact_phase_selector_available) ||
        !hhs219_bool_u8(request->dirty_set_complete) ||
        !hhs219_bool_u8(request->canonical_authority_requested))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (request->canonical_authority_requested != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < HHS_EXACT_PASS219_GENESIS_MAX_PHASE_DEPTH; ++i) {
        if (i < request->phase_depth) {
            if (request->phase_selected_s[i] == 0U ||
                request->phase_selected_s[i] > 81U)
                return HHS_EXACT_STATUS_RANGE_ERROR;
            dimensions[i].potential_q = 81U;
            dimensions[i].selected_s = request->phase_selected_s[i];
        } else {
            if (request->phase_selected_s[i] != 0U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            dimensions[i].potential_q = 1U;
            dimensions[i].selected_s = 1U;
        }
    }

    for (i = 0U; i < HHS_EXACT_PASS219_GENESIS_CELL_COUNT; ++i) {
        if (!hhs219_bool_u8(request->dirty_cell_mask[i]))
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        if (request->dirty_cell_mask[i] != 0U)
            ++dirty_count;
    }

    status = hhs_exact_pass219_genesis_descriptor(&genesis);
    if (status != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_genesis_validate(&genesis) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs219_mul_u64(
            request->candidate_family_count,
            HHS_EXACT_PASS219_GENESIS_ADDRESS_COUNT,
            &base_lane_units))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    status = hhs_exact_pass219b_phase_locality_plan(
        dimensions,
        request->phase_depth,
        request->exact_phase_selector_available,
        0U,
        base_lane_units,
        &phase_plan);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219b_selective_projection_plan(
        request->source_count,
        request->projection_numerator_p,
        request->projection_denominator_q,
        &projection_plan);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (request->dirty_set_complete != 0U) {
        for (i = 0U; i < HHS_EXACT_PASS219_GENESIS_CELL_COUNT; ++i) {
            if (request->dirty_cell_mask[i] != 0U) {
                const uint64_t start = (request->source_count * (uint64_t)i) /
                                       HHS_EXACT_PASS219_GENESIS_CELL_COUNT;
                const uint64_t end = (request->source_count * (uint64_t)(i + 1U)) /
                                     HHS_EXACT_PASS219_GENESIS_CELL_COUNT;
                sparse_update +=
                    hhs219_selected_prefix(
                        end,
                        request->projection_numerator_p,
                        request->projection_denominator_q) -
                    hhs219_selected_prefix(
                        start,
                        request->projection_numerator_p,
                        request->projection_denominator_q);
            }
        }
        if (sparse_update > projection_plan.selected_count)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    } else {
        sparse_update = projection_plan.selected_count;
    }

    memset(out_plan, 0, sizeof(*out_plan));
    out_plan->struct_size = (uint32_t)sizeof(*out_plan);
    out_plan->version = hhs219_mandatory_version_word();
    out_plan->work_kind = request->work_kind;
    out_plan->phase_depth = request->phase_depth;
    out_plan->phase_route = phase_plan.route;
    out_plan->dirty_cell_count = dirty_count;
    out_plan->stage_count = HHS_EXACT_PASS219_SCALING_STAGE_COUNT;
    for (i = 0U; i < HHS_EXACT_PASS219_SCALING_STAGE_COUNT; ++i)
        out_plan->stage_order[i] = i + 1U;

    out_plan->source_count = request->source_count;
    out_plan->potential_phase_volume = phase_plan.potential_phase_volume;
    out_plan->materialized_phase_volume = phase_plan.materialized_phase_volume;
    out_plan->phase_reduction_numerator = phase_plan.reduction_numerator;
    out_plan->phase_reduction_denominator = phase_plan.reduction_denominator;
    out_plan->candidate_base_lane_units = base_lane_units;
    out_plan->candidate_realized_lane_units = phase_plan.required_realized_units;
    out_plan->selected_projection_count = projection_plan.selected_count;
    out_plan->projection_avoided_count = projection_plan.avoided_count;
    out_plan->sparse_update_count = sparse_update;
    out_plan->sparse_avoided_selected_count =
        projection_plan.selected_count - sparse_update;

    out_plan->derived_route =
        request->dirty_set_complete != 0U && sparse_update < projection_plan.selected_count
            ? HHS_EXACT_PASS219_DERIVED_ROUTE_SPARSE
            : HHS_EXACT_PASS219_DERIVED_ROUTE_FULL;

    out_plan->genesis_normalization_required = 1U;
    out_plan->pass207_deterministic_required = 1U;
    out_plan->pass208_candidate_only_required = 1U;
    out_plan->exact_cpu_vm_oracle_equality_required = 1U;
    out_plan->singleton_vm81_admission_required = 1U;
    out_plan->selective_projection_exact_equality_required = 1U;
    out_plan->sparse_exact_equality_required =
        (uint8_t)(out_plan->derived_route == HHS_EXACT_PASS219_DERIVED_ROUTE_SPARSE ? 1U : 0U);
    out_plan->dirty_set_completeness_required = 1U;
    out_plan->hash72_hash216_existing_authority_required = 1U;
    out_plan->fail_closed_complete_path_required = 1U;
    out_plan->canonical_mutation_authority = 0U;
    out_plan->canonical_persistence_authority = 0U;
    out_plan->canonical_hash72_authority = 0U;
    out_plan->floating_point_authority = 0U;
    out_plan->mandatory_for_pass219_data_ml = 1U;
    out_plan->reserved0 = 0U;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_mandatory_scaling_verify(
    const HHSExactPass219MandatoryScalingPlanV1 *plan,
    const HHSExactPass219MandatoryScalingWitnessV1 *witness
) {
    uint32_t i;

    if (plan == NULL || witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (plan->struct_size != sizeof(*plan) ||
        witness->struct_size != sizeof(*witness) ||
        plan->version != hhs219_mandatory_version_word() ||
        witness->version != hhs219_mandatory_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (!hhs219_work_kind_valid(plan->work_kind) ||
        plan->stage_count != HHS_EXACT_PASS219_SCALING_STAGE_COUNT ||
        plan->mandatory_for_pass219_data_ml != 1U ||
        plan->genesis_normalization_required != 1U ||
        plan->pass207_deterministic_required != 1U ||
        plan->pass208_candidate_only_required != 1U ||
        plan->exact_cpu_vm_oracle_equality_required != 1U ||
        plan->singleton_vm81_admission_required != 1U ||
        plan->selective_projection_exact_equality_required != 1U ||
        plan->dirty_set_completeness_required != 1U ||
        plan->hash72_hash216_existing_authority_required != 1U ||
        plan->fail_closed_complete_path_required != 1U ||
        plan->canonical_mutation_authority != 0U ||
        plan->canonical_persistence_authority != 0U ||
        plan->canonical_hash72_authority != 0U ||
        plan->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < HHS_EXACT_PASS219_SCALING_STAGE_COUNT; ++i) {
        if (plan->stage_order[i] != i + 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (!hhs219_bool_u8(witness->genesis_validated) ||
        !hhs219_bool_u8(witness->original_identity_preserved) ||
        !hhs219_bool_u8(witness->pass207_deterministic_integer_only) ||
        !hhs219_bool_u8(witness->pass207_stable_lane_identity) ||
        !hhs219_bool_u8(witness->pass208_candidate_only) ||
        !hhs219_bool_u8(witness->exact_cpu_vm_oracle_equal) ||
        !hhs219_bool_u8(witness->singleton_vm81_admission_preserved) ||
        !hhs219_bool_u8(witness->selective_projection_exact_equal) ||
        !hhs219_bool_u8(witness->dirty_set_complete) ||
        !hhs219_bool_u8(witness->sparse_projection_exact_equal) ||
        !hhs219_bool_u8(witness->hash72_hash216_authority_preserved) ||
        !hhs219_bool_u8(witness->canonical_authority_requested))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    if (witness->canonical_authority_requested != 0U ||
        witness->genesis_validated != 1U ||
        witness->original_identity_preserved != 1U ||
        witness->pass207_deterministic_integer_only != 1U ||
        witness->pass207_stable_lane_identity != 1U ||
        witness->pass208_candidate_only != 1U ||
        witness->exact_cpu_vm_oracle_equal != 1U ||
        witness->singleton_vm81_admission_preserved != 1U ||
        witness->selective_projection_exact_equal != 1U ||
        witness->hash72_hash216_authority_preserved != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (plan->derived_route == HHS_EXACT_PASS219_DERIVED_ROUTE_SPARSE) {
        if (plan->sparse_exact_equality_required != 1U ||
            witness->dirty_set_complete != 1U ||
            witness->sparse_projection_exact_equal != 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    } else if (plan->derived_route == HHS_EXACT_PASS219_DERIVED_ROUTE_FULL) {
        if (plan->sparse_exact_equality_required != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    } else {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    return HHS_EXACT_STATUS_OK;
}
