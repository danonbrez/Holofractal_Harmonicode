#ifndef HHS_PASS219_RML20_RNA_VM5184_BRIDGE_1_34_H
#define HHS_PASS219_RML20_RNA_VM5184_BRIDGE_1_34_H

#include "hhs_pass219_rna_vm5184_abi_1_33.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_RML20_RNA_VM5184_VERSION UINT32_C(0x00010022)
#define HHS_EXACT_PASS219_RML20_OPERATION_COUNT UINT32_C(64)
#define HHS_EXACT_PASS219_RML20_PHASE_COUNT UINT32_C(72)
#define HHS_EXACT_PASS219_RML20_CELL_COUNT UINT32_C(81)
#define HHS_EXACT_PASS219_RML20_DIRECTION_COUNT UINT32_C(6)
#define HHS_EXACT_PASS219_RML20_ADDRESS_COUNT \
    (HHS_EXACT_PASS219_HOLO4_LANE_COUNT * \
     HHS_EXACT_PASS219_RML20_OPERATION_COUNT * \
     HHS_EXACT_PASS219_RML20_PHASE_COUNT * \
     HHS_EXACT_PASS219_RML20_CELL_COUNT)

typedef enum HHSExactPass219RML20DirectionV1 {
    HHS_EXACT_PASS219_RML20_OPERATION_FORWARD = 0,
    HHS_EXACT_PASS219_RML20_OPERATION_REVERSE = 1,
    HHS_EXACT_PASS219_RML20_PHASE_FORWARD = 2,
    HHS_EXACT_PASS219_RML20_PHASE_REVERSE = 3,
    HHS_EXACT_PASS219_RML20_CELL_FORWARD = 4,
    HHS_EXACT_PASS219_RML20_CELL_REVERSE = 5
} HHSExactPass219RML20DirectionV1;

typedef struct HHSExactPass219RML20RNAVM5184DescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t lane_count;
    uint32_t operations_per_cell;
    uint32_t phase_count;
    uint32_t cell_count;
    uint32_t address_count;
    uint32_t direction_count;
    uint32_t vm5184_bytes;
    uint8_t cpp_rna_cell_wall;
    uint8_t frozen_rml17_parity_surface;
    uint8_t lane_retaining_transport;
    uint8_t reciprocal_flux_transport;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[5];
} HHSExactPass219RML20RNAVM5184DescriptorV1;

typedef struct HHSExactPass219RML20RNAVM5184ReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t source_address;
    uint32_t target_address;
    uint8_t source_lane;
    uint8_t source_operation;
    uint8_t source_phase;
    uint8_t source_cell;
    uint8_t target_lane;
    uint8_t target_operation;
    uint8_t target_phase;
    uint8_t target_cell;
    uint8_t direction;
    uint8_t inverse_direction;
    int8_t forward_flux;
    int8_t reverse_flux;
    int8_t discrete_divergence;
    uint8_t encode_decode_bijective;
    uint8_t reciprocal_neighbor_restores_source;
    uint8_t reciprocal_flux_balanced;
    uint8_t lane_identity_retained;
    uint8_t zero_discrete_divergence;
    uint8_t zero_diffusion_classification;
    uint8_t feedback_lane_bound;
    uint8_t feedback_trinary_bound;
    uint8_t rna_cell_wall_routed;
    uint8_t selected_lane;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[4];
    uint64_t graph_signature64;
    uint64_t tensor_signature64;
    uint64_t decision_signature64;
    char transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN];
} HHSExactPass219RML20RNAVM5184ReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_rml20_rna_vm5184_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml20_rna_vm5184_descriptor(
    HHSExactPass219RML20RNAVM5184DescriptorV1 *out_descriptor
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml20_transport_address_encode(
    uint8_t lane,
    uint8_t operation,
    uint8_t phase,
    uint8_t cell,
    uint32_t *out_address
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml20_transport_address_decode(
    uint32_t address,
    uint8_t *out_lane,
    uint8_t *out_operation,
    uint8_t *out_phase,
    uint8_t *out_cell
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml20_transport_neighbor(
    uint32_t source_address,
    uint8_t direction,
    uint32_t *out_target_address
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml20_transport_flux(
    uint8_t direction,
    int8_t *out_flux
);

/*
 * Candidate-only RML17 transport binding into the exact 648-byte VM5184
 * carrier and the Pass 219 C++ RNA cell wall.  The source RML17 lane is bound
 * as feedback_lane and the exact signed transport flux (+1/-1) is bound as
 * feedback_trinary.  The route emits evidence only: it cannot commit VM81,
 * mint Hash72/Hash216 lineage, or persist canonical state.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml20_rna_vm5184_route(
    const HHSExactUQCELInputV1 *input,
    const uint8_t *raw_frame_le,
    size_t raw_frame_length,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint32_t source_address,
    uint8_t direction,
    HHSExactPass219RML20RNAVM5184ReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
