#include "../include/hhs_pass219b_phase_quantized_hydration_1_0.h"

#include <string.h>

static uint32_t hhs_exact_pass219b_phase_version_word(void) {
    return (HHS_EXACT_PASS219B_PHASE_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219B_PHASE_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219B_PHASE_VERSION_PATCH;
}

static HHSExactStatus hhs_exact_pass219b_validate_parent(
    const HHSExactPass219HydrationCoordinateV1 *parent
) {
    uint8_t cell81;
    int8_t group;
    uint8_t operation64;
    uint16_t g243;
    if (parent == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    return hhs_exact_pass219_coordinate_to_pass189(
        parent, &cell81, &group, &operation64, &g243);
}

static uint8_t hhs_exact_pass219b_phase_position(
    uint8_t origin81,
    uint8_t step,
    int8_t direction
) {
    if (direction > 0)
        return (uint8_t)(((uint16_t)origin81 + (uint16_t)step) %
                         HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT);
    return (uint8_t)(((uint16_t)origin81 + HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT -
                      (uint16_t)step) % HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT);
}

uint32_t hhs_exact_pass219b_phase_version(void) {
    return hhs_exact_pass219b_phase_version_word();
}

const char *hhs_exact_pass219b_tensor_source(void) {
    return HHS_EXACT_PASS219B_TENSOR_SOURCE;
}

HHSExactStatus hhs_exact_pass219b_projection_index(
    const HHSExactPass219HydrationCoordinateV1 *parent,
    uint8_t phase_origin81,
    uint64_t *out_projection_index
) {
    uint64_t base;
    HHSExactStatus status;
    if (out_projection_index == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (phase_origin81 >= HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    status = hhs_exact_pass219b_validate_parent(parent);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    base = (uint64_t)parent->cell81;
    base = base * HHS_EXACT_PASS219_LO_SHU_GROUP_COUNT +
           (uint64_t)parent->lo_shu_group_offset41;
    base = base * HHS_EXACT_PASS219_TRIT_COUNT + (uint64_t)parent->trit;
    base = base * HHS_EXACT_PASS219_HYDRATION_SLOT_COUNT +
           (uint64_t)parent->slot5184;
    if (base >= HHS_EXACT_PASS219B_INHERITED_MANIFOLD_STATES)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    *out_projection_index = base * HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT +
                            (uint64_t)phase_origin81;
    if (*out_projection_index >= HHS_EXACT_PASS219B_FULL_PHASE_PROJECTION_CELLS)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219b_phase_cell(
    const HHSExactPass219HydrationCoordinateV1 *parent,
    uint8_t phase_origin81,
    HHSExactPass219BPhaseCellV1 *out_cell
) {
    static const uint8_t ring[HHS_EXACT_PASS219B_OUTER_CELL_COUNT] = {
        HHS_EXACT_PASS219B_RING_XY, HHS_EXACT_PASS219B_RING_ZW,
        HHS_EXACT_PASS219B_RING_XY, HHS_EXACT_PASS219B_RING_ZW,
        HHS_EXACT_PASS219B_RING_XY, HHS_EXACT_PASS219B_RING_ZW,
        HHS_EXACT_PASS219B_RING_XY, HHS_EXACT_PASS219B_RING_ZW
    };
    static const uint8_t step[HHS_EXACT_PASS219B_OUTER_CELL_COUNT] = {
        0U, 0U, 1U, 1U, 2U, 2U, 3U, 3U
    };
    static const uint8_t basis[HHS_EXACT_PASS219B_OUTER_CELL_COUNT] = {
        HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_W,
        HHS_EXACT_PHASE_YX, HHS_EXACT_PHASE_ZW,
        HHS_EXACT_PHASE_Y, HHS_EXACT_PHASE_Z,
        HHS_EXACT_PHASE_XY, HHS_EXACT_PHASE_WZ
    };
    static const uint8_t family[HHS_EXACT_PASS219B_OUTER_CELL_COUNT] = {
        HHS_EXACT_PASS219B_ROTATION_I, HHS_EXACT_PASS219B_ROTATION_I2,
        HHS_EXACT_PASS219B_ROTATION_I, HHS_EXACT_PASS219B_ROTATION_I2,
        HHS_EXACT_PASS219B_ROTATION_I, HHS_EXACT_PASS219B_ROTATION_I2,
        HHS_EXACT_PASS219B_ROTATION_I, HHS_EXACT_PASS219B_ROTATION_I2
    };
    static const int8_t direction[HHS_EXACT_PASS219B_OUTER_CELL_COUNT] = {
        1, -1, 1, -1, 1, -1, 1, -1
    };
    size_t i;
    uint64_t projection_index;
    HHSExactStatus status;

    if (out_cell == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219b_projection_index(
        parent, phase_origin81, &projection_index);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(out_cell, 0, sizeof(*out_cell));
    out_cell->struct_size = (uint32_t)sizeof(*out_cell);
    out_cell->version = hhs_exact_pass219b_phase_version_word();
    out_cell->parent = *parent;
    out_cell->projection_index = projection_index;
    out_cell->phase_origin81 = phase_origin81;
    out_cell->outer_count = HHS_EXACT_PASS219B_OUTER_CELL_COUNT;
    out_cell->center_closure_preserved = 1U;
    out_cell->tensor_source_preserved = 1U;
    out_cell->canonical_mutation_authority = 0U;
    out_cell->canonical_persistence_authority = 0U;
    out_cell->canonical_hash72_authority = 0U;

    for (i = 0U; i < HHS_EXACT_PASS219B_OUTER_CELL_COUNT; ++i) {
        HHSExactPass219BOuterPhaseCellV1 *outer = &out_cell->outer[i];
        outer->perimeter_index = (uint8_t)i;
        outer->ring = ring[i];
        outer->ring_step = step[i];
        outer->phase_basis = basis[i];
        outer->rotation_family = family[i];
        outer->direction = direction[i];
        outer->phase_position81 = hhs_exact_pass219b_phase_position(
            phase_origin81, step[i], direction[i]);
        outer->relation_role = (uint8_t)i;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219b_expansion_plan(
    uint64_t parent_count,
    uint32_t origin_count,
    HHSExactPass219BExpansionPlanV1 *out_plan
) {
    uint64_t max_value = ~(uint64_t)0;
    if (out_plan == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (parent_count == 0U || origin_count == 0U ||
        origin_count > HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (parent_count > max_value / (uint64_t)origin_count)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_plan, 0, sizeof(*out_plan));
    out_plan->struct_size = (uint32_t)sizeof(*out_plan);
    out_plan->version = hhs_exact_pass219b_phase_version_word();
    out_plan->parent_count = parent_count;
    out_plan->origin_count = origin_count;
    out_plan->required_phase_cells = parent_count * (uint64_t)origin_count;
    out_plan->phase_cells_per_5184 = HHS_EXACT_PASS219B_PHASE_CELLS_PER_5184;
    out_plan->inherited_manifold_states = HHS_EXACT_PASS219B_INHERITED_MANIFOLD_STATES;
    out_plan->full_phase_projection_cells = HHS_EXACT_PASS219B_FULL_PHASE_PROJECTION_CELLS;
    out_plan->full_materialization_required = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219b_expand_selected(
    const HHSExactPass219HydrationCoordinateV1 *parents,
    size_t parent_count,
    uint8_t first_origin81,
    uint8_t origin_count,
    HHSExactPass219BPhaseCellV1 *out_cells,
    size_t capacity,
    size_t *out_count
) {
    size_t required;
    size_t p;
    size_t o;
    HHSExactStatus status;

    if (parents == NULL || out_count == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (parent_count == 0U || origin_count == 0U ||
        first_origin81 >= HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT ||
        (uint16_t)first_origin81 + (uint16_t)origin_count >
            HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (parent_count > ((size_t)-1) / (size_t)origin_count)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    required = parent_count * (size_t)origin_count;
    *out_count = required;
    if (out_cells == NULL || capacity < required)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    for (p = 0U; p < parent_count; ++p) {
        status = hhs_exact_pass219b_validate_parent(&parents[p]);
        if (status != HHS_EXACT_STATUS_OK) {
            *out_count = 0U;
            return status;
        }
    }

    for (p = 0U; p < parent_count; ++p) {
        for (o = 0U; o < (size_t)origin_count; ++o) {
            size_t index = p * (size_t)origin_count + o;
            status = hhs_exact_pass219b_phase_cell(
                &parents[p], (uint8_t)((size_t)first_origin81 + o),
                &out_cells[index]);
            if (status != HHS_EXACT_STATUS_OK) {
                memset(out_cells, 0, required * sizeof(*out_cells));
                *out_count = 0U;
                return status;
            }
        }
    }
    return HHS_EXACT_STATUS_OK;
}
