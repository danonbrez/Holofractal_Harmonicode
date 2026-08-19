#include "../../hhs_runtime/include/hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static uint64_t expected_projection_index(
    const HHSExactPass219HydrationCoordinateV1 *parent,
    uint8_t origin
) {
    uint64_t base = (uint64_t)parent->cell81;
    base = base * HHS_EXACT_PASS219_LO_SHU_GROUP_COUNT +
           (uint64_t)parent->lo_shu_group_offset41;
    base = base * HHS_EXACT_PASS219_TRIT_COUNT + (uint64_t)parent->trit;
    base = base * HHS_EXACT_PASS219_HYDRATION_SLOT_COUNT +
           (uint64_t)parent->slot5184;
    return base * HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT + (uint64_t)origin;
}

int main(void) {
    HHSExactPass219HydrationCoordinateV1 parent;
    HHSExactPass219HydrationCoordinateV1 bad_parent;
    HHSExactPass219BPhaseCellV1 cell;
    HHSExactPass219BPhaseCellV1 replay;
    HHSExactPass219BPhaseCellV1 cells[HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT];
    HHSExactPass219BExpansionPlanV1 plan;
    HHSExactStatus status;
    uint64_t index;
    size_t count;
    size_t i;

    assert(strcmp(
        hhs_exact_pass219b_tensor_source(),
        "List(List(x=1/y,w=-z,(y*x=-xy)),List((w*z=-zw),x+y+z+w=0,(z*w)),List((x*y),z=1/w,y=-x))") == 0);
    assert(hhs_exact_pass219b_phase_version() == ((1U << 16) | (0U << 8) | 0U));
    assert(HHS_EXACT_PASS219B_PHASE_CELLS_PER_5184 == 419904ULL);
    assert(HHS_EXACT_PASS219B_INHERITED_MANIFOLD_STATES == 51648192ULL);
    assert(HHS_EXACT_PASS219B_FULL_PHASE_PROJECTION_CELLS == 4183503552ULL);

    memset(&parent, 0, sizeof(parent));
    status = hhs_exact_pass219_coordinate_from_pass189(7U, 0, 13U, 42U, &parent);
    assert(status == HHS_EXACT_STATUS_OK);

    memset(&cell, 0, sizeof(cell));
    status = hhs_exact_pass219b_phase_cell(&parent, 17U, &cell);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(cell.phase_origin81 == 17U);
    assert(cell.outer_count == 8U);
    assert(cell.center_closure_preserved == 1U);
    assert(cell.tensor_source_preserved == 1U);
    assert(cell.canonical_mutation_authority == 0U);
    assert(cell.canonical_persistence_authority == 0U);
    assert(cell.canonical_hash72_authority == 0U);

    assert(cell.outer[0].phase_basis == HHS_EXACT_PHASE_X);
    assert(cell.outer[0].ring == HHS_EXACT_PASS219B_RING_XY);
    assert(cell.outer[0].rotation_family == HHS_EXACT_PASS219B_ROTATION_I);
    assert(cell.outer[0].direction == 1);
    assert(cell.outer[0].phase_position81 == 17U);

    assert(cell.outer[1].phase_basis == HHS_EXACT_PHASE_W);
    assert(cell.outer[1].ring == HHS_EXACT_PASS219B_RING_ZW);
    assert(cell.outer[1].rotation_family == HHS_EXACT_PASS219B_ROTATION_I2);
    assert(cell.outer[1].direction == -1);
    assert(cell.outer[1].phase_position81 == 17U);

    assert(cell.outer[2].phase_basis == HHS_EXACT_PHASE_YX);
    assert(cell.outer[2].phase_position81 == 18U);
    assert(cell.outer[3].phase_basis == HHS_EXACT_PHASE_ZW);
    assert(cell.outer[3].phase_position81 == 16U);
    assert(cell.outer[4].phase_basis == HHS_EXACT_PHASE_Y);
    assert(cell.outer[4].phase_position81 == 19U);
    assert(cell.outer[5].phase_basis == HHS_EXACT_PHASE_Z);
    assert(cell.outer[5].phase_position81 == 15U);
    assert(cell.outer[6].phase_basis == HHS_EXACT_PHASE_XY);
    assert(cell.outer[6].phase_position81 == 20U);
    assert(cell.outer[7].phase_basis == HHS_EXACT_PHASE_WZ);
    assert(cell.outer[7].phase_position81 == 14U);

    status = hhs_exact_pass219b_projection_index(&parent, 17U, &index);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(index == expected_projection_index(&parent, 17U));
    assert(index == cell.projection_index);
    assert(index < HHS_EXACT_PASS219B_FULL_PHASE_PROJECTION_CELLS);

    memset(&replay, 0, sizeof(replay));
    status = hhs_exact_pass219b_phase_cell(&parent, 17U, &replay);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(memcmp(&cell, &replay, sizeof(cell)) == 0);

    status = hhs_exact_pass219b_phase_cell(&parent, 80U, &replay);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(replay.outer[2].phase_position81 == 0U);
    assert(replay.outer[3].phase_position81 == 79U);

    count = 0U;
    status = hhs_exact_pass219b_expand_selected(
        &parent, 1U, 0U, HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT,
        cells, HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT, &count);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(count == HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT);
    for (i = 0U; i < count; ++i) {
        assert(cells[i].phase_origin81 == (uint8_t)i);
        assert(cells[i].projection_index == expected_projection_index(&parent, (uint8_t)i));
        if (i > 0U)
            assert(cells[i].projection_index == cells[i - 1U].projection_index + 1U);
    }

    count = 0U;
    status = hhs_exact_pass219b_expand_selected(
        &parent, 1U, 0U, HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT,
        cells, 1U, &count);
    assert(status == HHS_EXACT_STATUS_BUFFER_TOO_SMALL);
    assert(count == HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT);

    memset(&plan, 0, sizeof(plan));
    status = hhs_exact_pass219b_expansion_plan(5184ULL, 81U, &plan);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(plan.required_phase_cells == 419904ULL);
    assert(plan.full_materialization_required == 0U);

    status = hhs_exact_pass219b_expansion_plan(51648192ULL, 81U, &plan);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(plan.required_phase_cells == 4183503552ULL);
    assert(plan.full_phase_projection_cells == 4183503552ULL);
    assert(plan.full_materialization_required == 0U);

    status = hhs_exact_pass219b_phase_cell(&parent, 81U, &replay);
    assert(status == HHS_EXACT_STATUS_RANGE_ERROR);

    bad_parent = parent;
    bad_parent.trit = (uint8_t)((bad_parent.trit + 1U) % HHS_EXACT_PASS219_TRIT_COUNT);
    status = hhs_exact_pass219b_phase_cell(&bad_parent, 0U, &replay);
    assert(status == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}
