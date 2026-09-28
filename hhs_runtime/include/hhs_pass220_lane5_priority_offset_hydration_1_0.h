#ifndef HHS_PASS220_LANE5_PRIORITY_OFFSET_HYDRATION_1_0_H
#define HHS_PASS220_LANE5_PRIORITY_OFFSET_HYDRATION_1_0_H

#include "hhs_pass219_lane5_global_holographic_nucleus_1_34.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS220_PRIORITY_OFFSET_VERSION UINT32_C(0x00010000)
#define HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS UINT32_C(81)
#define HHS_EXACT_PASS220_PRIORITY_OFFSET_BLOCK_WIDTH UINT32_C(9)
#define HHS_EXACT_PASS220_PRIORITY_OFFSET_BLOCK_COUNT UINT32_C(9)
#define HHS_EXACT_PASS220_PRIORITY_OFFSET_CHANNEL_COUNT UINT32_C(4)
#define HHS_EXACT_PASS220_PRIORITY_OFFSET_PHASE_MODULUS UINT32_C(72)
#define HHS_EXACT_PASS220_PRIORITY_OFFSET_FIRING_ORIGIN UINT32_C(8)
#define HHS_EXACT_PASS220_PRIORITY_OFFSET_FIRING_STEP UINT32_C(16)
#define HHS_EXACT_PASS220_PRIORITY_OFFSET_MACROCYCLE_ORDER UINT32_C(9)

enum {
    HHS_EXACT_PASS220_PRIORITY_OFFSET_CHANNEL_XY = 0,
    HHS_EXACT_PASS220_PRIORITY_OFFSET_CHANNEL_YX = 1,
    HHS_EXACT_PASS220_PRIORITY_OFFSET_CHANNEL_ZW = 2,
    HHS_EXACT_PASS220_PRIORITY_OFFSET_CHANNEL_WZ = 3
};

typedef struct HHSExactPass220PriorityOffsetTaggedCellV1 {
    uint64_t counted_value;
    uint8_t phase72;
    uint8_t rotation4;
    uint8_t source_index;
    uint8_t reserved0[5];
} HHSExactPass220PriorityOffsetTaggedCellV1;

typedef struct HHSExactPass220PriorityOffsetDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t vm81_cells;
    uint32_t block_width;
    uint32_t block_count;
    uint32_t channel_count;
    uint32_t phase_modulus;
    uint32_t firing_origin;
    uint32_t firing_step;
    uint32_t macrocycle_order;
    uint8_t literal_firing_pattern_bound;
    uint8_t u9_address_orbit_bound;
    uint8_t complete_tagged_state_preserved;
    uint8_t hnan_global_preflight_required;
    uint8_t dense_substitution_runtime_authority;
    uint8_t scalar_offset_priority_candidate;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t floating_point_canonical_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t reserved0[3];
} HHSExactPass220PriorityOffsetDescriptorV1;

typedef struct HHSExactPass220PriorityOffsetMediationWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t channel;
    uint32_t reserved0;
    uint64_t source_signature64;
    uint64_t transformed_signature64;
    uint64_t recovered_signature64;
    uint64_t firing_order_signature64;
    uint64_t request_signature64;
    uint64_t closure_signature64;
    uint64_t mediation_signature64;
    uint8_t inverse_round_trip_exact;
    uint8_t counted_values_preserved;
    uint8_t phase_coordinates_preserved;
    uint8_t rotations_preserved;
    uint8_t provenance_preserved;
    uint8_t literal_firing_pattern_bound;
    uint8_t hnan_global_preflight_passed;
    uint8_t exact_vm5184_bound;
    uint8_t rna_cell_wall_bound;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved1;
} HHSExactPass220PriorityOffsetMediationWitnessV1;

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_priority_offset_descriptor(
    HHSExactPass220PriorityOffsetDescriptorV1 *out_descriptor
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_priority_offset_transform(
    const HHSExactPass220PriorityOffsetTaggedCellV1 source[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    uint32_t channel,
    HHSExactPass220PriorityOffsetTaggedCellV1 output[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ]
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_priority_offset_inverse(
    const HHSExactPass220PriorityOffsetTaggedCellV1 source[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    uint32_t channel,
    HHSExactPass220PriorityOffsetTaggedCellV1 output[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ]
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_priority_offset_prepare_lane5_request(
    const HHSExactPass219Lane5MediationRequestV1 *template_request,
    const HHSExactPass220PriorityOffsetTaggedCellV1 transformed[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    uint32_t channel,
    HHSExactPass219Lane5MediationRequestV1 *out_request
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_priority_offset_mediate(
    const HHSExactPass220PriorityOffsetTaggedCellV1 source[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    uint32_t channel,
    const HHSExactPass219Lane5MediationRequestV1 *template_request,
    HHSExactPass220PriorityOffsetTaggedCellV1 transformed[
        HHS_EXACT_PASS220_PRIORITY_OFFSET_VM81_CELLS
    ],
    HHSExactPass219Lane5MediationReceiptV1 *out_receipt,
    HHSExactPass220PriorityOffsetMediationWitnessV1 *out_witness
);

#ifdef __cplusplus
}
#endif

#endif
