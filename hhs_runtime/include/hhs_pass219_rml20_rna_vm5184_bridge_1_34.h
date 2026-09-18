#ifndef HHS_PASS219_RML20_RNA_VM5184_BRIDGE_1_34_H
#define HHS_PASS219_RML20_RNA_VM5184_BRIDGE_1_34_H

#include "hhs_pass219_rna_vm5184_abi_1_33.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * RML20 repair-forward ABI.
 *
 * The historical branch encoded 4 lanes x 64 operations x 72 phases x 81 cells
 * and accepted a separate six-way transport direction. Current sealed RML17
 * instead defines one exact directed address:
 *
 *   operation64 x phase72 x cell81 x direction4
 *
 * with direction4=(x,y,z,w) as the low mixed-radix digit. RML20 preserves its
 * RNA/VM5184 lowering role, but its transport surface is now extentionally
 * identical to current RML17.
 */
#define HHS_EXACT_PASS219_RML20_RNA_VM5184_VERSION UINT32_C(0x00010023)
#define HHS_EXACT_PASS219_RML20_OPERATION_COUNT UINT32_C(64)
#define HHS_EXACT_PASS219_RML20_PHASE_COUNT UINT32_C(72)
#define HHS_EXACT_PASS219_RML20_CELL_COUNT UINT32_C(81)
#define HHS_EXACT_PASS219_RML20_DIRECTION_COUNT UINT32_C(4)
#define HHS_EXACT_PASS219_RML20_NODE_COUNT \
    (HHS_EXACT_PASS219_RML20_OPERATION_COUNT * \
     HHS_EXACT_PASS219_RML20_PHASE_COUNT * \
     HHS_EXACT_PASS219_RML20_CELL_COUNT)
#define HHS_EXACT_PASS219_RML20_ADDRESS_COUNT \
    (HHS_EXACT_PASS219_RML20_NODE_COUNT * \
     HHS_EXACT_PASS219_RML20_DIRECTION_COUNT)

typedef enum HHSExactPass219RML20DirectionV1 {
    HHS_EXACT_PASS219_RML20_X = 0,
    HHS_EXACT_PASS219_RML20_Y = 1,
    HHS_EXACT_PASS219_RML20_Z = 2,
    HHS_EXACT_PASS219_RML20_W = 3
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
    uint8_t current_rml17_parity_surface;
    uint8_t direction_embedded_address;
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
    uint8_t source_operation;
    uint8_t source_phase;
    uint8_t source_cell;
    uint8_t source_direction;
    uint8_t target_operation;
    uint8_t target_phase;
    uint8_t target_cell;
    uint8_t target_direction;
    uint8_t requested_direction;
    uint8_t inverse_direction;
    int8_t forward_flux;
    int8_t reverse_flux;
    int8_t discrete_divergence;
    uint8_t encode_decode_bijective;
    uint8_t reciprocal_neighbor_restores_source;
    uint8_t reciprocal_flux_balanced;
    uint8_t operation_cell_preserved;
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
    uint8_t operation,
    uint8_t phase,
    uint8_t cell,
    uint8_t direction,
    uint32_t *out_address
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml20_transport_address_decode(
    uint32_t address,
    uint8_t *out_operation,
    uint8_t *out_phase,
    uint8_t *out_cell,
    uint8_t *out_direction
);

/*
 * The explicit direction is an equality guard against the direction4 embedded
 * in source_address. It cannot override the RML17 address geometry.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml20_transport_neighbor(
    uint32_t source_address,
    uint8_t expected_direction,
    uint32_t *out_target_address
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml20_transport_flux(
    uint8_t direction,
    int8_t *out_flux
);

/*
 * Candidate-only current-RML17 transport binding into the exact 648-byte
 * VM5184 carrier and Pass 219 C++ RNA cell wall. direction4 is bound to the
 * Holo4 feedback lane and signed flux (+1/-1) to feedback trinary. Evidence
 * only: no VM81 commit, Hash72/Hash216 mint/persistence, or canonical state
 * mutation authority is introduced.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml20_rna_vm5184_route(
    const HHSExactUQCELInputV1 *input,
    const uint8_t *raw_frame_le,
    size_t raw_frame_length,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint32_t source_address,
    uint8_t expected_direction,
    HHSExactPass219RML20RNAVM5184ReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
