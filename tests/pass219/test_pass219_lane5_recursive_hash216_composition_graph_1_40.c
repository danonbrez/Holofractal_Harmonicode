#include "hhs_pass219_lane5_recursive_hash216_composition_graph_1_40.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); \
        return 1; \
    } \
} while (0)

int main(void) {
    HHSExactPass219Lane5RecursiveCompositionGraphAuthorityV1 authority;
    HHSExactPass219Lane5RecursiveCompositionGraphDescriptorV1 descriptor;
    HHSExactPass219Lane5RecursiveCompositionGraphDescriptorV1 tampered;
    HHSExactPass219Lane5RecursiveCompositionGraphReceiptV1 receipt_a;
    HHSExactPass219Lane5RecursiveCompositionGraphReceiptV1 receipt_b;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_recursive_composition_graph_version() == HHS_EXACT_PASS219_LANE5_RECURSIVE_COMPOSITION_GRAPH_VERSION);
    CHECK(hhs_exact_pass219_lane5_recursive_composition_graph_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.struct_size == sizeof(authority));
    CHECK(authority.full_cycle == 20020U);
    CHECK(authority.quarter_cycle == 5005U);
    CHECK(authority.persistent_composition_graph == 1U);
    CHECK(authority.recursive_multi_hop_search == 1U);
    CHECK(authority.hash216_path_seal_required == 1U);
    CHECK(authority.exact_hash216_adjacency_required == 1U);
    CHECK(authority.persistent_edge_authentication_required == 1U);
    CHECK(authority.inherited_gpu_vector_rank_required == 1U);
    CHECK(authority.prime_phase_cycle_bound == 1U);
    CHECK(authority.no_vertex_revisit_required == 1U);
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
    descriptor.version = HHS_EXACT_PASS219_LANE5_RECURSIVE_COMPOSITION_GRAPH_VERSION;
    descriptor.hop_count = 3U;
    descriptor.total_span = 24U;
    descriptor.phase_slot = 15015U;
    descriptor.cycle_index = UINT64_C(41);
    descriptor.start_signature64 = UINT64_C(0x4101);
    descriptor.goal_signature64 = UINT64_C(0x4102);
    descriptor.terminal_signature64 = UINT64_C(0x4102);
    descriptor.path_signature64 = UINT64_C(0x4103);
    descriptor.ordered_lineage_signature64 = UINT64_C(0x4104);
    descriptor.exact_adjacency = 1U;
    descriptor.persistent_edges_authenticated = 1U;
    descriptor.path_sealed = 1U;
    descriptor.no_vertex_revisit = 1U;
    descriptor.candidate_only = 1U;
    descriptor.requires_signed_environmental_vm81_admission = 1U;

    memset(&receipt_a, 0, sizeof(receipt_a));
    memset(&receipt_b, 0, sizeof(receipt_b));
    CHECK(hhs_exact_pass219_lane5_recursive_composition_graph_validate(&descriptor, &receipt_a) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_recursive_composition_graph_validate(&descriptor, &receipt_b) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(&receipt_a, &receipt_b, sizeof(receipt_a)) == 0);
    CHECK(receipt_a.accepted == 1U);
    CHECK(receipt_a.hop_count == 3U);
    CHECK(receipt_a.total_span == 24U);
    CHECK(receipt_a.exact_adjacency == 1U);
    CHECK(receipt_a.persistent_edges_authenticated == 1U);
    CHECK(receipt_a.path_sealed == 1U);
    CHECK(receipt_a.candidate_only == 1U);
    CHECK(receipt_a.canonical_mutation_authority == 0U);
    CHECK(receipt_a.canonical_hash216_authority == 0U);
    CHECK(receipt_a.canonical_persistence_authority == 0U);
    CHECK(receipt_a.requires_signed_environmental_vm81_admission == 1U);

    tampered = descriptor;
    tampered.exact_adjacency = 0U;
    CHECK(hhs_exact_pass219_lane5_recursive_composition_graph_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.path_sealed = 0U;
    CHECK(hhs_exact_pass219_lane5_recursive_composition_graph_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.total_span = 5U;
    CHECK(hhs_exact_pass219_lane5_recursive_composition_graph_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    tampered = descriptor;
    tampered.phase_slot = 20020U;
    CHECK(hhs_exact_pass219_lane5_recursive_composition_graph_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    tampered = descriptor;
    tampered.canonical_hash216_authority = 1U;
    CHECK(hhs_exact_pass219_lane5_recursive_composition_graph_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    printf(
        "PASS219_LANE5_RECURSIVE_HASH216_COMPOSITION_GRAPH_PASS hops=%u span=%u phase=%u graph=%llu\n",
        receipt_a.hop_count,
        receipt_a.total_span,
        receipt_a.phase_slot,
        (unsigned long long)receipt_a.graph_route_signature64);
    return 0;
}
