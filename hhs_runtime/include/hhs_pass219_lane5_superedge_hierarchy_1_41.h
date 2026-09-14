#ifndef HHS_PASS219_LANE5_SUPEREDGE_HIERARCHY_1_41_H
#define HHS_PASS219_LANE5_SUPEREDGE_HIERARCHY_1_41_H

#include "hhs_pass219_lane5_recursive_hash216_composition_graph_1_40.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_SUPEREDGE_HIERARCHY_VERSION UINT32_C(0x00010029)
#define HHS_EXACT_PASS219_LANE5_SUPEREDGE_MIN_LEVEL UINT32_C(1)
#define HHS_EXACT_PASS219_LANE5_SUPEREDGE_MIN_COMPONENTS UINT32_C(2)

typedef struct HHSExactPass219Lane5SuperedgeHierarchyAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t full_cycle;
    uint32_t quarter_cycle;
    uint8_t recursive_superedge_hierarchy;
    uint8_t restart_rehydratable_superedges;
    uint8_t one_snapshot_direct_reuse;
    uint8_t transitive_flattened_provenance_required;
    uint8_t hash216_hierarchy_seal_required;
    uint8_t exact_component_adjacency_required;
    uint8_t leaf_quarantine_propagation_required;
    uint8_t inherited_gpu_vector_rank_allowed;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t floating_point_canonical_authority;
} HHSExactPass219Lane5SuperedgeHierarchyAuthorityV1;

typedef struct HHSExactPass219Lane5SuperedgeDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t hierarchy_level;
    uint32_t direct_component_count;
    uint32_t base_hops;
    uint32_t total_span;
    uint32_t phase_slot;
    uint32_t layer_index;
    uint64_t cycle_index;
    uint64_t parent_signature64;
    uint64_t child_signature64;
    uint64_t route_signature64;
    uint64_t hierarchy_signature64;
    uint64_t metadata_signature64;
    uint64_t component_lineage_signature64;
    uint64_t flattened_leaf_signature64;
    uint8_t exact_component_adjacency;
    uint8_t lower_level_replay_authenticated;
    uint8_t terminal_snapshot_encrypted;
    uint8_t hierarchy_sealed;
    uint8_t leaf_dependencies_live;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[3];
} HHSExactPass219Lane5SuperedgeDescriptorV1;

typedef struct HHSExactPass219Lane5SuperedgeReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t hierarchy_level;
    uint32_t direct_component_count;
    uint32_t base_hops;
    uint32_t total_span;
    uint32_t phase_slot;
    uint32_t layer_index;
    uint64_t cycle_index;
    uint64_t descriptor_signature64;
    uint64_t hierarchy_receipt_signature64;
    uint8_t accepted;
    uint8_t exact_component_adjacency;
    uint8_t lower_level_replay_authenticated;
    uint8_t terminal_snapshot_encrypted;
    uint8_t hierarchy_sealed;
    uint8_t leaf_dependencies_live;
    uint8_t one_snapshot_direct_reuse;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0;
} HHSExactPass219Lane5SuperedgeReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_superedge_hierarchy_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_superedge_hierarchy_authority(
    HHSExactPass219Lane5SuperedgeHierarchyAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_superedge_validate(
    const HHSExactPass219Lane5SuperedgeDescriptorV1 *descriptor,
    HHSExactPass219Lane5SuperedgeReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
