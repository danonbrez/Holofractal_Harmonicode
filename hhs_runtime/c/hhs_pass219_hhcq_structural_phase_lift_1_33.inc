#include "../include/hhs_pass219_hhcq_structural_phase_lift_1_33.h"

#include <string.h>

static uint64_t p13_mix(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static HHSExactStatus p13_parent_canonical(
    const HHSExactPass219HydrationCoordinateV1 *parent
) {
    HHSExactPass219HydrationCoordinateV1 replay;
    uint8_t cell81;
    int8_t lo_shu_group;
    uint8_t operation64;
    uint16_t g243;
    HHSExactStatus status;

    if (parent == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_coordinate_to_pass189(
        parent, &cell81, &lo_shu_group, &operation64, &g243);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    memset(&replay, 0, sizeof(replay));
    status = hhs_exact_pass219_coordinate_from_pass189(
        cell81, lo_shu_group, operation64, g243, &replay);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return memcmp(parent, &replay, sizeof(replay)) == 0
        ? HHS_EXACT_STATUS_OK : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static HHSExactStatus p13_validate_structural_cell(
    const HHSExactPass219BPhaseCellV1 *cell,
    uint8_t *out_role_mask,
    uint8_t *out_xy_orientation,
    uint8_t *out_zw_orientation
) {
    HHSExactPass219BPhaseCellV1 expected;
    HHSExactStatus status;
    uint8_t role_mask = 0U;
    int8_t xy_direction = 0;
    int8_t zw_direction = 0;
    uint32_t i;

    if (cell == NULL || out_role_mask == NULL ||
        out_xy_orientation == NULL || out_zw_orientation == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (cell->struct_size < sizeof(*cell) ||
        cell->version != hhs_exact_pass219b_phase_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (cell->phase_origin81 >= HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT ||
        cell->outer_count != HHS_EXACT_PASS219B_OUTER_CELL_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (cell->center_closure_preserved != 1U ||
        cell->tensor_source_preserved != 1U ||
        cell->canonical_mutation_authority != 0U ||
        cell->canonical_persistence_authority != 0U ||
        cell->canonical_hash72_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = p13_parent_canonical(&cell->parent);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(&expected, 0, sizeof(expected));
    status = hhs_exact_pass219b_phase_cell(
        &cell->parent, cell->phase_origin81, &expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (memcmp(cell, &expected, sizeof(expected)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < HHS_EXACT_PASS219B_OUTER_CELL_COUNT; ++i) {
        const HHSExactPass219BOuterPhaseCellV1 *outer = &cell->outer[i];
        uint8_t role;
        if (outer->relation_role >= HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_ROLE_COUNT)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        role = (uint8_t)(UINT8_C(1) << outer->relation_role);
        if ((role_mask & role) != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        role_mask = (uint8_t)(role_mask | role);

        if (outer->ring == HHS_EXACT_PASS219B_RING_XY) {
            if (outer->direction != HHS_EXACT_PASS219_HHCQ_STRUCTURAL_DIRECTION_FORWARD &&
                outer->direction != HHS_EXACT_PASS219_HHCQ_STRUCTURAL_DIRECTION_REVERSE)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            if (xy_direction == 0)
                xy_direction = outer->direction;
            else if (xy_direction != outer->direction)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        } else if (outer->ring == HHS_EXACT_PASS219B_RING_ZW) {
            if (outer->direction != HHS_EXACT_PASS219_HHCQ_STRUCTURAL_DIRECTION_FORWARD &&
                outer->direction != HHS_EXACT_PASS219_HHCQ_STRUCTURAL_DIRECTION_REVERSE)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            if (zw_direction == 0)
                zw_direction = outer->direction;
            else if (zw_direction != outer->direction)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        } else {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }

    if (role_mask != HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_ROLE_MASK ||
        xy_direction == 0 || zw_direction == 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    *out_role_mask = role_mask;
    *out_xy_orientation =
        xy_direction == HHS_EXACT_PASS219_HHCQ_STRUCTURAL_DIRECTION_FORWARD
            ? HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT
            : HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED;
    *out_zw_orientation =
        zw_direction == HHS_EXACT_PASS219_HHCQ_STRUCTURAL_DIRECTION_FORWARD
            ? HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT
            : HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED;
    return HHS_EXACT_STATUS_OK;
}

static int p13_manifold_clean(
    const HHSExactPass219HHCQSymbolicManifoldV1 *m
) {
    if (m == NULL)
        return 0;
    return m->symbolic_carrier_admitted == 1U &&
           m->global_relation_graph_exact == 1U &&
           m->symbolic_equilibrium_exact == 1U &&
           m->symbolic_square_gate_exact == 1U &&
           m->ordered_products_exact == 1U &&
           m->constraint_intersection_satisfied == 1U &&
           m->raw_projection_authority == 0U &&
           m->scalar_integer_semantic_authority == 0U &&
           m->gate.scalar_x_parity_evaluated == 0U &&
           m->gate.phase10_projection_authority == 0U &&
           m->canonical_mutation_authority == 0U &&
           m->canonical_hash72_authority == 0U &&
           m->canonical_hash216_authority == 0U &&
           m->canonical_persistence_authority == 0U &&
           m->floating_point_authority == 0U;
}

static uint64_t p13_signature(
    const HHSExactPass219HHCQStructuralPhaseLiftV1 *lift
) {
    uint64_t v = UINT64_C(0x2195133000000001);
    v ^= lift->phase_cell.projection_index;
    v ^= (uint64_t)lift->phase_cell.phase_origin81 << 8U;
    v ^= (uint64_t)lift->phase_cell.parent.cell81 << 16U;
    v ^= (uint64_t)lift->phase_cell.parent.slot5184 << 24U;
    v ^= lift->carrier.carrier_signature64;
    v ^= lift->manifold.manifold_signature64;
    v ^= (uint64_t)lift->prime_p << 3U;
    v ^= (uint64_t)lift->prime_q << 19U;
    v ^= (uint64_t)lift->base_resolution_index << 40U;
    v ^= (uint64_t)lift->relation_role_mask << 48U;
    v ^= (uint64_t)lift->xy_ring_orientation << 56U;
    v ^= (uint64_t)lift->zw_ring_orientation << 60U;
    return p13_mix(v);
}

uint32_t hhs_exact_pass219_hhcq_structural_phase_lift_version(void) {
    return HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_LIFT_VERSION;
}

HHSExactStatus hhs_exact_pass219_hhcq_structural_phase_descriptor(
    HHSExactPass219HHCQStructuralPhaseDescriptorV1 *out
) {
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->version = HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_LIFT_VERSION;
    out->pass219b_phase_version = hhs_exact_pass219b_phase_version();
    out->symbolic_phase_version = hhs_exact_pass219_hhcq_symbolic_phase_version();
    out->relation_role_count = HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_ROLE_COUNT;
    out->phase_origin_count = HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT;
    out->pass219b_structural_source_required = 1U;
    out->parent_hydration_coordinate_required = 1U;
    out->complete_role_graph_required = 1U;
    out->ring_step_basis_family_direction_required = 1U;
    out->origin_relative_position_required = 1U;
    out->tensor_source_required = 1U;
    out->center_closure_required = 1U;
    out->orientation_from_structural_direction = 1U;
    out->raw_vm81_word_semantic_authority = 0U;
    out->raw_phase_residue_semantic_authority = 0U;
    out->scalar_phase_position_semantic_authority = 0U;
    out->scalar_integer_semantic_authority = 0U;
    out->candidate_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_structural_phase_lift_from_cell(
    const HHSExactPass219BPhaseCellV1 *phase_cell,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQStructuralPhaseLiftV1 *out
) {
    HHSExactPass219HHCQSymbolicCarrierV1 carrier;
    HHSExactPass219HHCQSymbolicManifoldV1 manifold;
    HHSExactStatus status;
    uint8_t role_mask;
    uint8_t xy_orientation;
    uint8_t zw_orientation;

    if (phase_cell == NULL || out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = p13_validate_structural_cell(
        phase_cell, &role_mask, &xy_orientation, &zw_orientation);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(&carrier, 0, sizeof(carrier));
    status = hhs_exact_pass219_hhcq_symbolic_carrier_construct(
        xy_orientation, zw_orientation, &carrier);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_hhcq_symbolic_carrier_validate(&carrier);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(&manifold, 0, sizeof(manifold));
    status = hhs_exact_pass219_hhcq_symbolic_manifold_from_carrier(
        &carrier, prime_p, prime_q, base_resolution_index, &manifold);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!p13_manifold_clean(&manifold))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->version = HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_LIFT_VERSION;
    out->phase_cell = *phase_cell;
    out->carrier = carrier;
    out->manifold = manifold;
    out->prime_p = prime_p;
    out->prime_q = prime_q;
    out->base_resolution_index = base_resolution_index;
    out->relation_role_mask = role_mask;
    out->xy_ring_orientation = xy_orientation;
    out->zw_ring_orientation = zw_orientation;
    out->structural_topology_exact = 1U;
    out->parent_coordinate_exact = 1U;
    out->relation_roles_exact = 1U;
    out->ring_topology_exact = 1U;
    out->phase_positions_exact = 1U;
    out->tensor_source_preserved = 1U;
    out->center_closure_preserved = 1U;
    out->symbolic_carrier_admitted = 1U;
    out->constraint_intersection_satisfied = 1U;
    out->raw_vm81_word_semantic_authority = 0U;
    out->raw_phase_residue_semantic_authority = 0U;
    out->scalar_phase_position_semantic_authority = 0U;
    out->scalar_integer_semantic_authority = 0U;
    out->candidate_only = 1U;
    out->structural_signature64 = p13_signature(out);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_structural_phase_lift_from_coordinate(
    const HHSExactPass219HydrationCoordinateV1 *parent,
    uint8_t phase_origin81,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQStructuralPhaseLiftV1 *out
) {
    HHSExactPass219BPhaseCellV1 cell;
    HHSExactStatus status;
    if (parent == NULL || out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&cell, 0, sizeof(cell));
    status = hhs_exact_pass219b_phase_cell(parent, phase_origin81, &cell);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_exact_pass219_hhcq_structural_phase_lift_from_cell(
        &cell, prime_p, prime_q, base_resolution_index, out);
}

HHSExactStatus hhs_exact_pass219_hhcq_structural_phase_lift_validate(
    const HHSExactPass219HHCQStructuralPhaseLiftV1 *lift
) {
    HHSExactPass219HHCQStructuralPhaseLiftV1 replay;
    HHSExactStatus status;
    if (lift == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (lift->struct_size < sizeof(*lift) ||
        lift->version != HHS_EXACT_PASS219_HHCQ_STRUCTURAL_PHASE_LIFT_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    memset(&replay, 0, sizeof(replay));
    status = hhs_exact_pass219_hhcq_structural_phase_lift_from_cell(
        &lift->phase_cell, lift->prime_p, lift->prime_q,
        lift->base_resolution_index, &replay);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return memcmp(lift, &replay, sizeof(replay)) == 0
        ? HHS_EXACT_STATUS_OK : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}
