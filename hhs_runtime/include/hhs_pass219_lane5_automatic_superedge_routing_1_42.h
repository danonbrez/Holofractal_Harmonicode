#ifndef HHS_PASS219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42_H
#define HHS_PASS219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42_H

#include "hhs_pass219_lane5_superedge_hierarchy_1_41.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_VERSION UINT32_C(0x0001002A)
#define HHS_EXACT_PASS219_LANE5_AUTOMATIC_PROMOTION_THRESHOLD UINT32_C(2)
#define HHS_EXACT_PASS219_LANE5_AUTOMATIC_ROUTE_MIN_RETRIEVALS UINT32_C(1)

typedef struct HHSExactPass219Lane5AutomaticRoutingAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t full_cycle;
    uint32_t quarter_cycle;
    uint32_t default_promotion_threshold;
    uint8_t cross_level_exact_routing;
    uint8_t automatic_repeated_route_promotion;
    uint8_t durable_exact_observation_ledger;
    uint8_t integer_only_routing_cost;
    uint8_t exact_hash216_adjacency_required;
    uint8_t exact_target_closure_required;
    uint8_t mixed_level_candidate_routing_allowed;
    uint8_t mixed_level_recursive_promotion_allowed;
    uint8_t inherited_gpu_vector_rank_non_authoritative;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t floating_point_canonical_authority;
} HHSExactPass219Lane5AutomaticRoutingAuthorityV1;

typedef struct HHSExactPass219Lane5AutomaticRouteDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t retrieval_count;
    uint32_t base_hops;
    uint32_t represented_span;
    uint32_t max_hierarchy_level;
    uint32_t phase_slot;
    uint32_t layer_index;
    uint64_t cycle_index;
    uint64_t parent_signature64;
    uint64_t goal_signature64;
    uint64_t route_signature64;
    uint64_t ordered_candidate_signature64;
    uint8_t exact_hash216_adjacency;
    uint8_t exact_target_closure;
    uint8_t dependencies_live;
    uint8_t selected_by_integer_cost;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[4];
} HHSExactPass219Lane5AutomaticRouteDescriptorV1;

typedef struct HHSExactPass219Lane5AutomaticRouteReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t retrieval_count;
    uint32_t base_hops;
    uint32_t represented_span;
    uint32_t max_hierarchy_level;
    uint32_t phase_slot;
    uint32_t layer_index;
    uint64_t cycle_index;
    uint64_t descriptor_signature64;
    uint64_t route_receipt_signature64;
    uint8_t accepted;
    uint8_t exact_hash216_adjacency;
    uint8_t exact_target_closure;
    uint8_t dependencies_live;
    uint8_t selected_by_integer_cost;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[3];
} HHSExactPass219Lane5AutomaticRouteReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_automatic_superedge_routing_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_automatic_superedge_routing_authority(
    HHSExactPass219Lane5AutomaticRoutingAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_automatic_route_validate(
    const HHSExactPass219Lane5AutomaticRouteDescriptorV1 *descriptor,
    HHSExactPass219Lane5AutomaticRouteReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
