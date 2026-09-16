#include "hhs_pass219_lane5_direct_witness_routing_1_46.h"

#include <stdio.h>
#include <string.h>

static HHSExactPass219Lane5DirectWitnessRouteV1 make_route(
    uint64_t route_signature,
    uint64_t span,
    uint32_t evidence_count,
    uint32_t contradiction_checks,
    uint32_t phase_slot,
    int8_t trinary,
    uint8_t binary
) {
    HHSExactPass219Lane5DirectWitnessRouteV1 route;
    memset(&route, 0, sizeof(route));
    route.struct_size = (uint32_t)sizeof(route);
    route.version = HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_VERSION;
    route.previous_signature64 = UINT64_C(0x1001);
    route.current_signature64 = UINT64_C(0x2002);
    route.provenance_signature64 = UINT64_C(0x3003);
    route.goal_signature64 = UINT64_C(0x4004);
    route.forbidden_boundary_signature64 = UINT64_C(0x5005);
    route.reciprocal_inverse_signature64 = UINT64_C(0x6006);
    route.candidate_signature64 = route.goal_signature64;
    route.route_signature64 = route_signature;
    route.represented_span = span;
    route.evidence_count = evidence_count;
    route.contradiction_check_count = contradiction_checks;
    route.integer_route_cost = (uint64_t)evidence_count + (uint64_t)contradiction_checks + UINT64_C(1);
    route.materialized_intermediate_states = 0U;
    route.phase_slot = phase_slot;
    route.inverse_phase_slot = (phase_slot + UINT32_C(36)) % UINT32_C(72);
    route.trinary_collapse = trinary;
    route.binary_collapse = binary;
    route.nested_zero_slot = binary == 0U ? 1U : 0U;
    route.replay_witness_verified = 1U;
    route.exact_goal_reached = 1U;
    route.contradiction_free = 1U;
    route.goal_forbidden_conflict = 0U;
    route.reciprocal_phase_verified = 1U;
    route.bigint_serialization_addressed = 1U;
    route.candidate_only = 1U;
    route.requires_signed_environmental_vm81_admission = 1U;
    return route;
}

#define CHECK(expr) do { if (!(expr)) { fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); return 1; } } while (0)

int main(void) {
    HHSExactPass219Lane5DirectWitnessAuthorityV1 authority;
    HHSExactPass219Lane5DirectWitnessReceiptV1 receipt;
    HHSExactPass219Lane5DirectWitnessRouteV1 routes[4];
    HHSExactPass219Lane5DirectWitnessRouteV1 tampered;
    uint64_t first_signature;
    uint32_t selected_index;
    uint64_t selected_span;
    uint64_t selected_avoided;
    uint64_t selected_cost;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_direct_witness_routing_version() == HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_VERSION);
    CHECK(hhs_exact_pass219_lane5_direct_witness_routing_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.direct_composition_jump == 1U);
    CHECK(authority.intermediate_materialization_required == 0U);
    CHECK(authority.exact_reciprocal_phase_inversion == 1U);
    CHECK(authority.balanced_trinary_collapse == 1U);
    CHECK(authority.binary_qubit_collapse == 1U);
    CHECK(authority.nested_zero_layer == 1U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);

    routes[0] = make_route(UINT64_C(0x9004), UINT64_C(1000000), 7U, 3U, 0U, 0, 0U);
    routes[1] = make_route(UINT64_C(0x9003), UINT64_C(2500000), 5U, 2U, 18U, 1, 1U);
    routes[2] = make_route(UINT64_C(0x9002), UINT64_C(9000000), 5U, 2U, 36U, -1, 0U);
    routes[3] = make_route(UINT64_C(0x9001), UINT64_C(9000000), 5U, 2U, 54U, 0, 0U);

    memset(&receipt, 0, sizeof(receipt));
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&routes[0], &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(receipt.optimizer_selected == 0U);
    CHECK(receipt.selected_candidate_index == UINT32_MAX);
    CHECK(receipt.avoided_intermediate_states == UINT64_C(999999));
    first_signature = receipt.route_receipt_signature64;
    memset(&receipt, 0, sizeof(receipt));
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&routes[0], &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.route_receipt_signature64 == first_signature);

    memset(&receipt, 0, sizeof(receipt));
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_optimize(routes, 4U, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(receipt.optimizer_selected == 1U);
    CHECK(receipt.selected_candidate_index == 3U);
    CHECK(receipt.integer_route_cost == UINT64_C(8));
    CHECK(receipt.represented_span == UINT64_C(9000000));
    CHECK(receipt.avoided_intermediate_states == UINT64_C(8999999));
    CHECK(receipt.phase_slot == 54U);
    CHECK(receipt.inverse_phase_slot == 18U);
    selected_index = receipt.selected_candidate_index;
    selected_span = receipt.represented_span;
    selected_avoided = receipt.avoided_intermediate_states;
    selected_cost = receipt.integer_route_cost;

    tampered = routes[0];
    tampered.materialized_intermediate_states = 1U;
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&tampered, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = routes[0];
    tampered.inverse_phase_slot = 18U;
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&tampered, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = routes[0];
    tampered.goal_forbidden_conflict = 1U;
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&tampered, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = routes[0];
    tampered.forbidden_boundary_signature64 = tampered.goal_signature64;
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&tampered, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = routes[0];
    tampered.binary_collapse = 2U;
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&tampered, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = routes[0];
    tampered.trinary_collapse = 2;
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&tampered, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = routes[0];
    tampered.binary_collapse = 0U;
    tampered.nested_zero_slot = 0U;
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&tampered, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = routes[0];
    tampered.integer_route_cost += 1U;
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&tampered, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = routes[0];
    tampered.canonical_hash216_authority = 1U;
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&tampered, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    printf("PASS219_LANE5_DIRECT_WITNESS_ROUTING_1_46_PASS selected=%u span=%llu avoided=%llu cost=%llu\n",
           selected_index,
           (unsigned long long)selected_span,
           (unsigned long long)selected_avoided,
           (unsigned long long)selected_cost);
    return 0;
}
