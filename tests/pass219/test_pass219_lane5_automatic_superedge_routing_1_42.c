#include "hhs_pass219_lane5_automatic_superedge_routing_1_42.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); \
        return 1; \
    } \
} while (0)

int main(void) {
    HHSExactPass219Lane5AutomaticRoutingAuthorityV1 authority;
    HHSExactPass219Lane5AutomaticRouteDescriptorV1 descriptor;
    HHSExactPass219Lane5AutomaticRouteDescriptorV1 tampered;
    HHSExactPass219Lane5AutomaticRouteReceiptV1 receipt_a;
    HHSExactPass219Lane5AutomaticRouteReceiptV1 receipt_b;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_automatic_superedge_routing_version() == HHS_EXACT_PASS219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_VERSION);
    CHECK(hhs_exact_pass219_lane5_automatic_superedge_routing_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.struct_size == sizeof(authority));
    CHECK(authority.full_cycle == 20020U);
    CHECK(authority.quarter_cycle == 5005U);
    CHECK(authority.default_promotion_threshold == 2U);
    CHECK(authority.cross_level_exact_routing == 1U);
    CHECK(authority.automatic_repeated_route_promotion == 1U);
    CHECK(authority.durable_exact_observation_ledger == 1U);
    CHECK(authority.integer_only_routing_cost == 1U);
    CHECK(authority.exact_hash216_adjacency_required == 1U);
    CHECK(authority.exact_target_closure_required == 1U);
    CHECK(authority.mixed_level_candidate_routing_allowed == 1U);
    CHECK(authority.mixed_level_recursive_promotion_allowed == 0U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.pqc_key_authority == 0U);
    CHECK(authority.receipt_clock_authority == 0U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);
    CHECK(authority.floating_point_canonical_authority == 0U);

    memset(&descriptor, 0, sizeof(descriptor));
    descriptor.struct_size = (uint32_t)sizeof(descriptor);
    descriptor.version = HHS_EXACT_PASS219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_VERSION;
    descriptor.retrieval_count = 2U;
    descriptor.base_hops = 4U;
    descriptor.represented_span = 26U;
    descriptor.max_hierarchy_level = 1U;
    descriptor.phase_slot = 5005U;
    descriptor.layer_index = 7U;
    descriptor.cycle_index = UINT64_C(91);
    descriptor.parent_signature64 = UINT64_C(0x6201);
    descriptor.goal_signature64 = UINT64_C(0x6202);
    descriptor.route_signature64 = UINT64_C(0x6203);
    descriptor.ordered_candidate_signature64 = UINT64_C(0x6204);
    descriptor.exact_hash216_adjacency = 1U;
    descriptor.exact_target_closure = 1U;
    descriptor.dependencies_live = 1U;
    descriptor.selected_by_integer_cost = 1U;
    descriptor.candidate_only = 1U;
    descriptor.requires_signed_environmental_vm81_admission = 1U;

    memset(&receipt_a, 0, sizeof(receipt_a));
    memset(&receipt_b, 0, sizeof(receipt_b));
    CHECK(hhs_exact_pass219_lane5_automatic_route_validate(&descriptor, &receipt_a) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_automatic_route_validate(&descriptor, &receipt_b) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(&receipt_a, &receipt_b, sizeof(receipt_a)) == 0);
    CHECK(receipt_a.accepted == 1U);
    CHECK(receipt_a.retrieval_count == 2U);
    CHECK(receipt_a.base_hops == 4U);
    CHECK(receipt_a.represented_span == 26U);
    CHECK(receipt_a.max_hierarchy_level == 1U);
    CHECK(receipt_a.exact_hash216_adjacency == 1U);
    CHECK(receipt_a.exact_target_closure == 1U);
    CHECK(receipt_a.selected_by_integer_cost == 1U);
    CHECK(receipt_a.candidate_only == 1U);
    CHECK(receipt_a.canonical_mutation_authority == 0U);
    CHECK(receipt_a.canonical_hash216_authority == 0U);
    CHECK(receipt_a.canonical_persistence_authority == 0U);
    CHECK(receipt_a.requires_signed_environmental_vm81_admission == 1U);

    tampered = descriptor;
    tampered.retrieval_count = 0U;
    CHECK(hhs_exact_pass219_lane5_automatic_route_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    tampered = descriptor;
    tampered.base_hops = 1U;
    CHECK(hhs_exact_pass219_lane5_automatic_route_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    tampered = descriptor;
    tampered.exact_target_closure = 0U;
    CHECK(hhs_exact_pass219_lane5_automatic_route_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.dependencies_live = 0U;
    CHECK(hhs_exact_pass219_lane5_automatic_route_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.selected_by_integer_cost = 0U;
    CHECK(hhs_exact_pass219_lane5_automatic_route_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.canonical_hash216_authority = 1U;
    CHECK(hhs_exact_pass219_lane5_automatic_route_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.phase_slot = 20020U;
    CHECK(hhs_exact_pass219_lane5_automatic_route_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);

    printf(
        "PASS219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_PASS retrievals=%u base_hops=%u span=%u max_level=%u receipt=%llu\n",
        receipt_a.retrieval_count,
        receipt_a.base_hops,
        receipt_a.represented_span,
        receipt_a.max_hierarchy_level,
        (unsigned long long)receipt_a.route_receipt_signature64
    );
    return 0;
}
