#include "../../hhs_runtime/include/hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

#define CHECK_BAD(expr) do { \
    HHSExactPass219BPhaseCellV1 bad = cell; \
    expr; \
    memset(&lift, 0, sizeof(lift)); \
    assert(hhs_exact_pass219_hhcq_structural_phase_lift_from_cell( \
        &bad, 2U, 3U, 17U, &lift) != HHS_EXACT_STATUS_OK); \
} while (0)

int main(void) {
    HHSExactPass219HHCQStructuralPhaseDescriptorV1 descriptor;
    HHSExactPass219HydrationCoordinateV1 parent;
    HHSExactPass219BPhaseCellV1 cell;
    HHSExactPass219HHCQStructuralPhaseLiftV1 lift;
    HHSExactPass219HHCQStructuralPhaseLiftV1 replay;
    HHSExactStatus status;
    uint32_t origin;

    memset(&descriptor, 0, sizeof(descriptor));
    status = hhs_exact_pass219_hhcq_structural_phase_descriptor(&descriptor);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(descriptor.version == HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_LIFT_VERSION);
    assert(descriptor.pass219b_phase_version == hhs_exact_pass219b_phase_version());
    assert(descriptor.symbolic_phase_version == hhs_exact_pass219_hhcq_symbolic_phase_version());
    assert(descriptor.relation_role_count == 8U);
    assert(descriptor.phase_origin_count == 81U);
    assert(descriptor.pass219b_structural_source_required == 1U);
    assert(descriptor.complete_role_graph_required == 1U);
    assert(descriptor.orientation_from_structural_direction == 1U);
    assert(descriptor.raw_vm81_word_semantic_authority == 0U);
    assert(descriptor.raw_phase_residue_semantic_authority == 0U);
    assert(descriptor.scalar_phase_position_semantic_authority == 0U);
    assert(descriptor.scalar_integer_semantic_authority == 0U);
    assert(descriptor.canonical_mutation_authority == 0U);
    assert(descriptor.canonical_hash72_authority == 0U);
    assert(descriptor.canonical_hash216_authority == 0U);
    assert(descriptor.canonical_persistence_authority == 0U);
    assert(descriptor.floating_point_authority == 0U);

    memset(&parent, 0, sizeof(parent));
    status = hhs_exact_pass219_coordinate_from_pass189(7U, 0, 13U, 42U, &parent);
    assert(status == HHS_EXACT_STATUS_OK);

    for (origin = 0U; origin < HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT; ++origin) {
        memset(&lift, 0, sizeof(lift));
        status = hhs_exact_pass219_hhcq_structural_phase_lift_from_coordinate(
            &parent, (uint8_t)origin, 2U, 3U, 17U, &lift);
        assert(status == HHS_EXACT_STATUS_OK);
        assert(lift.phase_cell.phase_origin81 == (uint8_t)origin);
        assert(lift.relation_role_mask == HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_ROLE_MASK);
        assert(lift.xy_ring_orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT);
        assert(lift.zw_ring_orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED);
        assert(lift.structural_topology_exact == 1U);
        assert(lift.parent_coordinate_exact == 1U);
        assert(lift.relation_roles_exact == 1U);
        assert(lift.ring_topology_exact == 1U);
        assert(lift.phase_positions_exact == 1U);
        assert(lift.tensor_source_preserved == 1U);
        assert(lift.center_closure_preserved == 1U);
        assert(lift.symbolic_carrier_admitted == 1U);
        assert(lift.constraint_intersection_satisfied == 1U);
        assert(lift.raw_vm81_word_semantic_authority == 0U);
        assert(lift.raw_phase_residue_semantic_authority == 0U);
        assert(lift.scalar_phase_position_semantic_authority == 0U);
        assert(lift.scalar_integer_semantic_authority == 0U);
        assert(lift.manifold.scalar_integer_semantic_authority == 0U);
        assert(lift.manifold.raw_projection_authority == 0U);
        assert(lift.carrier.projection_residue_authority == 0U);
        assert(lift.manifold.gate.scalar_x_parity_evaluated == 0U);
        assert(lift.manifold.gate.x_squared_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2);
        assert(lift.candidate_only == 1U);
        assert(lift.canonical_mutation_authority == 0U);
        assert(lift.canonical_hash72_authority == 0U);
        assert(lift.canonical_hash216_authority == 0U);
        assert(lift.canonical_persistence_authority == 0U);
        assert(lift.floating_point_authority == 0U);
        assert(hhs_exact_pass219_hhcq_structural_phase_lift_validate(&lift) == HHS_EXACT_STATUS_OK);

        memset(&replay, 0, sizeof(replay));
        status = hhs_exact_pass219_hhcq_structural_phase_lift_from_coordinate(
            &parent, (uint8_t)origin, 2U, 3U, 17U, &replay);
        assert(status == HHS_EXACT_STATUS_OK);
        assert(memcmp(&lift, &replay, sizeof(lift)) == 0);
    }

    memset(&cell, 0, sizeof(cell));
    status = hhs_exact_pass219b_phase_cell(&parent, 17U, &cell);
    assert(status == HHS_EXACT_STATUS_OK);
    memset(&lift, 0, sizeof(lift));
    status = hhs_exact_pass219_hhcq_structural_phase_lift_from_cell(
        &cell, 2U, 3U, 17U, &lift);
    assert(status == HHS_EXACT_STATUS_OK);

    /* XY structural roles are forward/direct, ZW roles reverse/reversed: one mixed carrier. */
    assert(cell.outer[0].ring == HHS_EXACT_PASS219B_RING_XY);
    assert(cell.outer[0].direction == HHS_EXACT_PASS219_HHCQ_STRUCTURAL_DIRECTION_FORWARD);
    assert(cell.outer[1].ring == HHS_EXACT_PASS219B_RING_ZW);
    assert(cell.outer[1].direction == HHS_EXACT_PASS219_HHCQ_STRUCTURAL_DIRECTION_REVERSE);
    assert(lift.xy_ring_orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT);
    assert(lift.zw_ring_orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED);

    CHECK_BAD(bad.projection_index ^= UINT64_C(1));
    CHECK_BAD(bad.outer_count = 7U);
    CHECK_BAD(bad.center_closure_preserved = 0U);
    CHECK_BAD(bad.tensor_source_preserved = 0U);
    CHECK_BAD(bad.canonical_mutation_authority = 1U);
    CHECK_BAD(bad.canonical_persistence_authority = 1U);
    CHECK_BAD(bad.canonical_hash72_authority = 1U);
    CHECK_BAD(bad.phase_origin81 = 18U);
    CHECK_BAD(bad.outer[0].ring = HHS_EXACT_PASS219B_RING_ZW);
    CHECK_BAD(bad.outer[0].ring_step = 1U);
    CHECK_BAD(bad.outer[0].phase_basis = HHS_EXACT_PHASE_Y);
    CHECK_BAD(bad.outer[0].rotation_family = HHS_EXACT_PASS219B_ROTATION_I2);
    CHECK_BAD(bad.outer[0].direction = HHS_EXACT_PASS219_HHCQ_STRUCTURAL_DIRECTION_REVERSE);
    CHECK_BAD(bad.outer[0].phase_position81 = (uint8_t)((bad.outer[0].phase_position81 + 1U) % 81U));
    CHECK_BAD(bad.outer[0].relation_role = HHS_EXACT_PASS219B_REL_W_OPPOSITION);
    CHECK_BAD(bad.parent.slot5184 = (uint16_t)((bad.parent.slot5184 + 1U) % HHS_EXACT_PASS219_HYDRATION_SLOT_COUNT));
    CHECK_BAD(bad.parent.reserved0 = 1U);

    memset(&lift, 0, sizeof(lift));
    assert(hhs_exact_pass219_hhcq_structural_phase_lift_from_cell(
        &cell, 4U, 3U, 17U, &lift) != HHS_EXACT_STATUS_OK);
    memset(&lift, 0, sizeof(lift));
    assert(hhs_exact_pass219_hhcq_structural_phase_lift_from_cell(
        &cell, 2U, 3U, 35U, &lift) != HHS_EXACT_STATUS_OK);

    return 0;
}
