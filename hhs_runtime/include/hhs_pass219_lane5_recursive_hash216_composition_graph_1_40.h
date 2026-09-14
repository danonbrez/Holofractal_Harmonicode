#ifndef HHS_PASS219_LANE5_RECURSIVE_HASH216_COMPOSITION_GRAPH_1_40_H
#define HHS_PASS219_LANE5_RECURSIVE_HASH216_COMPOSITION_GRAPH_1_40_H

#include "hhs_pass219_lane5_persistent_hash216_composition_memory_1_39.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_RECURSIVE_COMPOSITION_GRAPH_VERSION UINT32_C(0x00010028)
#define HHS_EXACT_PASS219_LANE5_RECURSIVE_COMPOSITION_GRAPH_MIN_HOPS UINT32_C(1)

typedef struct HHSExactPass219Lane5RecursiveCompositionGraphAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t full_cycle;
    uint32_t quarter_cycle;
    uint8_t persistent_composition_graph;
    uint8_t recursive_multi_hop_search;
    uint8_t hash216_path_seal_required;
    uint8_t exact_hash216_adjacency_required;
    uint8_t persistent_edge_authentication_required;
    uint8_t inherited_gpu_vector_rank_required;
    uint8_t prime_phase_cycle_bound;
    uint8_t no_vertex_revisit_required;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t floating_point_canonical_authority;
} HHSExactPass219Lane5RecursiveCompositionGraphAuthorityV1;

typedef struct HHSExactPass219Lane5RecursiveCompositionGraphDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t hop_count;
    uint32_t total_span;
    uint32_t phase_slot;
    uint32_t reserved_phase;
    uint64_t cycle_index;
    uint64_t start_signature64;
    uint64_t goal_signature64;
    uint64_t terminal_signature64;
    uint64_t path_signature64;
    uint64_t ordered_lineage_signature64;
    uint8_t exact_adjacency;
    uint8_t persistent_edges_authenticated;
    uint8_t path_sealed;
    uint8_t no_vertex_revisit;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[4];
} HHSExactPass219Lane5RecursiveCompositionGraphDescriptorV1;

typedef struct HHSExactPass219Lane5RecursiveCompositionGraphReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t hop_count;
    uint32_t total_span;
    uint32_t phase_slot;
    uint32_t reserved_phase;
    uint64_t cycle_index;
    uint64_t descriptor_signature64;
    uint64_t graph_route_signature64;
    uint8_t accepted;
    uint8_t exact_adjacency;
    uint8_t persistent_edges_authenticated;
    uint8_t path_sealed;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[4];
} HHSExactPass219Lane5RecursiveCompositionGraphReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_recursive_composition_graph_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_recursive_composition_graph_authority(
    HHSExactPass219Lane5RecursiveCompositionGraphAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_recursive_composition_graph_validate(
    const HHSExactPass219Lane5RecursiveCompositionGraphDescriptorV1 *descriptor,
    HHSExactPass219Lane5RecursiveCompositionGraphReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
