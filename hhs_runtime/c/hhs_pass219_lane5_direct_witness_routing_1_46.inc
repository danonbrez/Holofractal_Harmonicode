#include "../include/hhs_pass219_lane5_direct_witness_routing_1_46.h"

#include <string.h>

static uint64_t hhs_lane5_dw_mix64(uint64_t x) {
    x ^= x >> 30;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31;
    return x;
}

static uint64_t hhs_lane5_dw_fold(uint64_t state, uint64_t tag, uint64_t value) {
    state ^= hhs_lane5_dw_mix64(tag);
    state = hhs_lane5_dw_mix64(state);
    state ^= hhs_lane5_dw_mix64(value ^ (tag * UINT64_C(0x9e3779b97f4a7c15)));
    return hhs_lane5_dw_mix64(state);
}

static int hhs_lane5_dw_valid_phase(uint32_t phase_slot) {
    return phase_slot == UINT32_C(0) ||
           phase_slot == UINT32_C(18) ||
           phase_slot == UINT32_C(36) ||
           phase_slot == UINT32_C(54);
}

static uint32_t hhs_lane5_dw_inverse_phase(uint32_t phase_slot) {
    return (phase_slot + HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_HALF) %
           HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_CYCLE;
}

static uint64_t hhs_lane5_dw_descriptor_signature(
    const HHSExactPass219Lane5DirectWitnessRouteV1 *route
) {
    uint64_t state = UINT64_C(0x4c35445752313436);
    state = hhs_lane5_dw_fold(state, UINT64_C(1), route->previous_signature64);
    state = hhs_lane5_dw_fold(state, UINT64_C(2), route->current_signature64);
    state = hhs_lane5_dw_fold(state, UINT64_C(3), route->provenance_signature64);
    state = hhs_lane5_dw_fold(state, UINT64_C(4), route->goal_signature64);
    state = hhs_lane5_dw_fold(state, UINT64_C(5), route->forbidden_boundary_signature64);
    state = hhs_lane5_dw_fold(state, UINT64_C(6), route->reciprocal_inverse_signature64);
    state = hhs_lane5_dw_fold(state, UINT64_C(7), route->candidate_signature64);
    state = hhs_lane5_dw_fold(state, UINT64_C(8), route->route_signature64);
    state = hhs_lane5_dw_fold(state, UINT64_C(9), route->represented_span);
    state = hhs_lane5_dw_fold(state, UINT64_C(10), route->integer_route_cost);
    state = hhs_lane5_dw_fold(state, UINT64_C(11), (uint64_t)route->evidence_count);
    state = hhs_lane5_dw_fold(state, UINT64_C(12), (uint64_t)route->contradiction_check_count);
    state = hhs_lane5_dw_fold(state, UINT64_C(13), (uint64_t)route->materialized_intermediate_states);
    state = hhs_lane5_dw_fold(state, UINT64_C(14), (uint64_t)route->phase_slot);
    state = hhs_lane5_dw_fold(state, UINT64_C(15), (uint64_t)route->inverse_phase_slot);
    state = hhs_lane5_dw_fold(state, UINT64_C(16), (uint64_t)(int64_t)route->trinary_collapse);
    state = hhs_lane5_dw_fold(state, UINT64_C(17), (uint64_t)route->binary_collapse);
    state = hhs_lane5_dw_fold(state, UINT64_C(18), (uint64_t)route->nested_zero_slot);
    state = hhs_lane5_dw_fold(state, UINT64_C(19), (uint64_t)route->replay_witness_verified);
    state = hhs_lane5_dw_fold(state, UINT64_C(20), (uint64_t)route->exact_goal_reached);
    state = hhs_lane5_dw_fold(state, UINT64_C(21), (uint64_t)route->contradiction_free);
    state = hhs_lane5_dw_fold(state, UINT64_C(22), (uint64_t)route->goal_forbidden_conflict);
    state = hhs_lane5_dw_fold(state, UINT64_C(23), (uint64_t)route->reciprocal_phase_verified);
    state = hhs_lane5_dw_fold(state, UINT64_C(24), (uint64_t)route->bigint_serialization_addressed);
    state = hhs_lane5_dw_fold(state, UINT64_C(25), (uint64_t)route->candidate_only);
    state = hhs_lane5_dw_fold(state, UINT64_C(26), (uint64_t)route->canonical_mutation_authority);
    state = hhs_lane5_dw_fold(state, UINT64_C(27), (uint64_t)route->canonical_hash72_authority);
    state = hhs_lane5_dw_fold(state, UINT64_C(28), (uint64_t)route->canonical_hash216_authority);
    state = hhs_lane5_dw_fold(state, UINT64_C(29), (uint64_t)route->canonical_persistence_authority);
    state = hhs_lane5_dw_fold(state, UINT64_C(30), (uint64_t)route->pqc_key_authority);
    state = hhs_lane5_dw_fold(state, UINT64_C(31), (uint64_t)route->receipt_clock_authority);
    state = hhs_lane5_dw_fold(state, UINT64_C(32), (uint64_t)route->requires_signed_environmental_vm81_admission);
    return state;
}

static HHSExactStatus hhs_lane5_dw_build_receipt(
    const HHSExactPass219Lane5DirectWitnessRouteV1 *route,
    uint32_t selected_candidate_index,
    HHSExactPass219Lane5DirectWitnessReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5DirectWitnessReceiptV1 receipt;
    uint64_t expected_cost;
    uint64_t descriptor_signature;

    if (route == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (route->struct_size != sizeof(*route) ||
        route->version != HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_VERSION)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    if (route->previous_signature64 == 0U ||
        route->current_signature64 == 0U ||
        route->provenance_signature64 == 0U ||
        route->goal_signature64 == 0U ||
        route->forbidden_boundary_signature64 == 0U ||
        route->reciprocal_inverse_signature64 == 0U ||
        route->candidate_signature64 == 0U ||
        route->route_signature64 == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (route->represented_span == 0U ||
        route->evidence_count < HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_MIN_EVIDENCE ||
        route->contradiction_check_count < HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_MIN_CONTRADICTION_CHECKS ||
        route->materialized_intermediate_states != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    expected_cost = (uint64_t)route->evidence_count +
                    (uint64_t)route->contradiction_check_count + UINT64_C(1);
    if (route->integer_route_cost != expected_cost)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs_lane5_dw_valid_phase(route->phase_slot) ||
        !hhs_lane5_dw_valid_phase(route->inverse_phase_slot) ||
        route->inverse_phase_slot != hhs_lane5_dw_inverse_phase(route->phase_slot))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (route->trinary_collapse < -1 || route->trinary_collapse > 1 ||
        route->binary_collapse > 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if ((route->binary_collapse == 0U && route->nested_zero_slot != 1U) ||
        (route->binary_collapse == 1U && route->nested_zero_slot != 0U))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (route->candidate_signature64 != route->goal_signature64 ||
        route->goal_signature64 == route->forbidden_boundary_signature64 ||
        route->replay_witness_verified != 1U ||
        route->exact_goal_reached != 1U ||
        route->contradiction_free != 1U ||
        route->goal_forbidden_conflict != 0U ||
        route->reciprocal_phase_verified != 1U ||
        route->bigint_serialization_addressed != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (route->candidate_only != 1U ||
        route->canonical_mutation_authority != 0U ||
        route->canonical_hash72_authority != 0U ||
        route->canonical_hash216_authority != 0U ||
        route->canonical_persistence_authority != 0U ||
        route->pqc_key_authority != 0U ||
        route->receipt_clock_authority != 0U ||
        route->requires_signed_environmental_vm81_admission != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&receipt, 0, sizeof(receipt));
    descriptor_signature = hhs_lane5_dw_descriptor_signature(route);
    receipt.struct_size = (uint32_t)sizeof(receipt);
    receipt.version = HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_VERSION;
    receipt.namespace_id = HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_NAMESPACE;
    receipt.selected_candidate_index = selected_candidate_index;
    receipt.represented_span = route->represented_span;
    receipt.integer_route_cost = route->integer_route_cost;
    receipt.avoided_intermediate_states = route->represented_span > 1U ? route->represented_span - 1U : 0U;
    receipt.descriptor_signature64 = descriptor_signature;
    receipt.route_receipt_signature64 = hhs_lane5_dw_fold(
        descriptor_signature,
        UINT64_C(0x5245434549505431),
        (uint64_t)selected_candidate_index
    );
    receipt.phase_slot = route->phase_slot;
    receipt.inverse_phase_slot = route->inverse_phase_slot;
    receipt.trinary_collapse = route->trinary_collapse;
    receipt.binary_collapse = route->binary_collapse;
    receipt.nested_zero_slot = route->nested_zero_slot;
    receipt.accepted = 1U;
    receipt.optimizer_selected = selected_candidate_index == UINT32_MAX ? 0U : 1U;
    receipt.replay_witness_verified = 1U;
    receipt.exact_goal_reached = 1U;
    receipt.contradiction_free = 1U;
    receipt.reciprocal_phase_verified = 1U;
    receipt.bigint_serialization_addressed = 1U;
    receipt.candidate_only = 1U;
    receipt.canonical_mutation_authority = 0U;
    receipt.canonical_hash72_authority = 0U;
    receipt.canonical_hash216_authority = 0U;
    receipt.canonical_persistence_authority = 0U;
    receipt.pqc_key_authority = 0U;
    receipt.receipt_clock_authority = 0U;
    receipt.requires_signed_environmental_vm81_admission = 1U;
    *out_receipt = receipt;
    return HHS_EXACT_STATUS_OK;
}

uint32_t hhs_exact_pass219_lane5_direct_witness_routing_version(void) {
    return HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_direct_witness_routing_authority(
    HHSExactPass219Lane5DirectWitnessAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5DirectWitnessAuthorityV1 value;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_VERSION;
    value.namespace_id = HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_NAMESPACE;
    value.phase_cycle = HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_CYCLE;
    value.phase_quarter = HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_PHASE_QUARTER;
    value.bigint_serialization_addressed = 1U;
    value.direct_composition_jump = 1U;
    value.intermediate_materialization_required = 0U;
    value.previous_current_witness_bound = 1U;
    value.goal_bound = 1U;
    value.contradiction_boundary_bound = 1U;
    value.exact_reciprocal_phase_inversion = 1U;
    value.balanced_trinary_collapse = 1U;
    value.binary_qubit_collapse = 1U;
    value.nested_zero_layer = 1U;
    value.integer_only_route_cost = 1U;
    value.deterministic_tie_break = 1U;
    value.candidate_only = 1U;
    value.canonical_vm81_mutation_authority = 0U;
    value.canonical_hash72_authority = 0U;
    value.canonical_hash216_authority = 0U;
    value.canonical_persistence_authority = 0U;
    value.pqc_key_authority = 0U;
    value.receipt_clock_authority = 0U;
    value.requires_signed_environmental_vm81_admission = 1U;
    value.floating_point_canonical_authority = 0U;
    *out_authority = value;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_direct_witness_route_validate(
    const HHSExactPass219Lane5DirectWitnessRouteV1 *route,
    HHSExactPass219Lane5DirectWitnessReceiptV1 *out_receipt
) {
    return hhs_lane5_dw_build_receipt(route, UINT32_MAX, out_receipt);
}

HHSExactStatus hhs_exact_pass219_lane5_direct_witness_route_optimize(
    const HHSExactPass219Lane5DirectWitnessRouteV1 *routes,
    uint32_t route_count,
    HHSExactPass219Lane5DirectWitnessReceiptV1 *out_receipt
) {
    uint32_t i;
    uint32_t best_index = UINT32_MAX;
    HHSExactPass219Lane5DirectWitnessReceiptV1 scratch;

    if (routes == NULL || out_receipt == NULL || route_count == 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    for (i = 0U; i < route_count; ++i) {
        HHSExactStatus status = hhs_lane5_dw_build_receipt(&routes[i], UINT32_MAX, &scratch);
        if (status != HHS_EXACT_STATUS_OK)
            continue;
        if (best_index == UINT32_MAX ||
            routes[i].integer_route_cost < routes[best_index].integer_route_cost ||
            (routes[i].integer_route_cost == routes[best_index].integer_route_cost &&
             routes[i].represented_span > routes[best_index].represented_span) ||
            (routes[i].integer_route_cost == routes[best_index].integer_route_cost &&
             routes[i].represented_span == routes[best_index].represented_span &&
             routes[i].route_signature64 < routes[best_index].route_signature64)) {
            best_index = i;
        }
    }

    if (best_index == UINT32_MAX)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return hhs_lane5_dw_build_receipt(&routes[best_index], best_index, out_receipt);
}
