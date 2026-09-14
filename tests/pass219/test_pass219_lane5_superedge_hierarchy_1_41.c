#include "hhs_pass219_lane5_superedge_hierarchy_1_41.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); \
        return 1; \
    } \
} while (0)

int main(void) {
    HHSExactPass219Lane5SuperedgeHierarchyAuthorityV1 authority;
    HHSExactPass219Lane5SuperedgeDescriptorV1 descriptor;
    HHSExactPass219Lane5SuperedgeDescriptorV1 tampered;
    HHSExactPass219Lane5SuperedgeReceiptV1 receipt_a;
    HHSExactPass219Lane5SuperedgeReceiptV1 receipt_b;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_superedge_hierarchy_version() == HHS_EXACT_PASS219_LANE5_SUPEREDGE_HIERARCHY_VERSION);
    CHECK(hhs_exact_pass219_lane5_superedge_hierarchy_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.struct_size == sizeof(authority));
    CHECK(authority.full_cycle == 20020U);
    CHECK(authority.quarter_cycle == 5005U);
    CHECK(authority.recursive_superedge_hierarchy == 1U);
    CHECK(authority.restart_rehydratable_superedges == 1U);
    CHECK(authority.one_snapshot_direct_reuse == 1U);
    CHECK(authority.transitive_flattened_provenance_required == 1U);
    CHECK(authority.hash216_hierarchy_seal_required == 1U);
    CHECK(authority.exact_component_adjacency_required == 1U);
    CHECK(authority.leaf_quarantine_propagation_required == 1U);
    CHECK(authority.inherited_gpu_vector_rank_allowed == 1U);
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
    descriptor.version = HHS_EXACT_PASS219_LANE5_SUPEREDGE_HIERARCHY_VERSION;
    descriptor.hierarchy_level = 2U;
    descriptor.direct_component_count = 2U;
    descriptor.base_hops = 6U;
    descriptor.total_span = 39U;
    descriptor.phase_slot = 15015U;
    descriptor.layer_index = 7U;
    descriptor.cycle_index = UINT64_C(61);
    descriptor.parent_signature64 = UINT64_C(0x5101);
    descriptor.child_signature64 = UINT64_C(0x5102);
    descriptor.route_signature64 = UINT64_C(0x5103);
    descriptor.hierarchy_signature64 = UINT64_C(0x5104);
    descriptor.metadata_signature64 = UINT64_C(0x5105);
    descriptor.component_lineage_signature64 = UINT64_C(0x5106);
    descriptor.flattened_leaf_signature64 = UINT64_C(0x5107);
    descriptor.exact_component_adjacency = 1U;
    descriptor.lower_level_replay_authenticated = 1U;
    descriptor.terminal_snapshot_encrypted = 1U;
    descriptor.hierarchy_sealed = 1U;
    descriptor.leaf_dependencies_live = 1U;
    descriptor.candidate_only = 1U;
    descriptor.requires_signed_environmental_vm81_admission = 1U;

    memset(&receipt_a, 0, sizeof(receipt_a));
    memset(&receipt_b, 0, sizeof(receipt_b));
    CHECK(hhs_exact_pass219_lane5_superedge_validate(&descriptor, &receipt_a) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_superedge_validate(&descriptor, &receipt_b) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(&receipt_a, &receipt_b, sizeof(receipt_a)) == 0);
    CHECK(receipt_a.accepted == 1U);
    CHECK(receipt_a.hierarchy_level == 2U);
    CHECK(receipt_a.direct_component_count == 2U);
    CHECK(receipt_a.base_hops == 6U);
    CHECK(receipt_a.total_span == 39U);
    CHECK(receipt_a.one_snapshot_direct_reuse == 1U);
    CHECK(receipt_a.candidate_only == 1U);
    CHECK(receipt_a.canonical_mutation_authority == 0U);
    CHECK(receipt_a.canonical_hash216_authority == 0U);
    CHECK(receipt_a.canonical_persistence_authority == 0U);
    CHECK(receipt_a.requires_signed_environmental_vm81_admission == 1U);

    tampered = descriptor;
    tampered.hierarchy_level = 0U;
    CHECK(hhs_exact_pass219_lane5_superedge_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    tampered = descriptor;
    tampered.direct_component_count = 1U;
    CHECK(hhs_exact_pass219_lane5_superedge_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    tampered = descriptor;
    tampered.base_hops = 1U;
    CHECK(hhs_exact_pass219_lane5_superedge_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    tampered = descriptor;
    tampered.exact_component_adjacency = 0U;
    CHECK(hhs_exact_pass219_lane5_superedge_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.leaf_dependencies_live = 0U;
    CHECK(hhs_exact_pass219_lane5_superedge_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.canonical_hash216_authority = 1U;
    CHECK(hhs_exact_pass219_lane5_superedge_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.phase_slot = 20020U;
    CHECK(hhs_exact_pass219_lane5_superedge_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);

    printf(
        "PASS219_LANE5_SUPEREDGE_HIERARCHY_PASS level=%u components=%u base_hops=%u span=%u receipt=%llu\n",
        receipt_a.hierarchy_level,
        receipt_a.direct_component_count,
        receipt_a.base_hops,
        receipt_a.total_span,
        (unsigned long long)receipt_a.hierarchy_receipt_signature64
    );
    return 0;
}
