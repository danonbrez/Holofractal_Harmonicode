#ifndef HHS_PASS219_RML15_ROUTE_REVERSE_REPLAY_1_28_H
#define HHS_PASS219_RML15_ROUTE_REVERSE_REPLAY_1_28_H

#include "hhs_pass219_rml14_route_bound_receipt_successor_1_27.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_RML15_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_RML15_VERSION_MINOR 28U
#define HHS_EXACT_PASS219_RML15_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_RML15_CHANNELS 8U
#define HHS_EXACT_PASS219_RML15_PRODUCTS 4U
#define HHS_EXACT_PASS219_RML15_MAX_EDGES 6U
#define HHS_EXACT_PASS219_RML15_SHA256_BYTES 32U
#define HHS_EXACT_PASS219_RML15_HASH72_STRLEN 73U
#define HHS_EXACT_PASS219_RML15_HASH216_STRLEN 217U

#define HHS_EXACT_PASS219_RML15_EDGE_COUPLED_MOVE 1U
#define HHS_EXACT_PASS219_RML15_EDGE_PAIR_FLIP 2U

typedef enum HHSExactPass219RML15DecisionV1 {
    HHS_EXACT_PASS219_RML15_UNRESOLVED = 0,
    HHS_EXACT_PASS219_RML15_VERIFIED = 1,
    HHS_EXACT_PASS219_RML15_REJECTED = 2
} HHSExactPass219RML15DecisionV1;

typedef enum HHSExactPass219RML15ReasonV1 {
    HHS_EXACT_PASS219_RML15_REASON_NONE = 0,
    HHS_EXACT_PASS219_RML15_REASON_RML14_FORWARD = 1,
    HHS_EXACT_PASS219_RML15_REASON_RML14_REPLAY = 2,
    HHS_EXACT_PASS219_RML15_REASON_RETAINED_ANCESTRY = 3,
    HHS_EXACT_PASS219_RML15_REASON_REVERSE_EXECUTION = 4,
    HHS_EXACT_PASS219_RML15_REASON_REVERSE_RECEIPT = 5,
    HHS_EXACT_PASS219_RML15_REASON_AUTHORITY = 6
} HHSExactPass219RML15ReasonV1;

typedef struct HHSExactPass219RML15PhaseStateV1 {
    uint8_t phases[HHS_EXACT_PASS219_RML15_CHANNELS];
    int8_t quarter_turn_signs[HHS_EXACT_PASS219_RML15_PRODUCTS];
    uint8_t reserved0[4];
    uint64_t ambient_state_index;
} HHSExactPass219RML15PhaseStateV1;

typedef struct HHSExactPass219RML15ReverseEdgeV1 {
    uint32_t kind;
    uint32_t selector;
    int32_t signed_steps;
    uint32_t reserved0;
} HHSExactPass219RML15ReverseEdgeV1;

typedef struct HHSExactPass219RML15ReverseWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t edge_count;
    uint32_t retained_forward_ancestry_used;
    uint32_t reverse_edges_are_exact_inverses;
    uint32_t reverse_terminal_matches_retained_source;
    uint32_t hash216_cryptographic_inversion_used;
    uint32_t floating_point_authority;

    uint8_t route_sha256[HHS_EXACT_PASS219_RML15_SHA256_BYTES];
    uint8_t source_state_sha256[HHS_EXACT_PASS219_RML15_SHA256_BYTES];
    uint8_t target_state_sha256[HHS_EXACT_PASS219_RML15_SHA256_BYTES];

    HHSExactPass219RML15PhaseStateV1 source_state;
    HHSExactPass219RML15PhaseStateV1 target_state;
    HHSExactPass219RML15ReverseEdgeV1 edges[HHS_EXACT_PASS219_RML15_MAX_EDGES];
} HHSExactPass219RML15ReverseWitnessV1;

typedef struct HHSExactPass219RML15BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason;

    uint32_t rml14_forward_verified;
    uint32_t rml14_replay_verified;
    uint32_t forward_replay_identity_equal;
    uint32_t retained_ancestry_verified;
    uint32_t reverse_instruction_sequence_verified;
    uint32_t reverse_phase_state_restored;
    uint32_t reverse_ambient_index_restored;
    uint32_t reverse_product_geometry_preserved;
    uint32_t reverse_chirality_preserved;
    uint32_t reverse_receipt_is_ancestry_witness_not_hash_inverse;
    uint32_t canonical_hash72_delegate_used;
    uint32_t canonical_hash216_delegate_used;
    uint32_t historical_uqcel_receipt_preserved;
    uint32_t historical_rml13_transition_preserved;
    uint32_t rml14_successor_chain_preserved;
    uint32_t hash216_cryptographic_inversion_used;
    uint32_t second_vm81_commit_primitive_added;
    uint32_t optimizer_transition_authority;
    uint32_t floating_point_authority;
    uint32_t hash216_persistence_authority;
    uint32_t scalar_projection_substitution_authority;

    uint32_t edge_count;
    uint32_t pair_flip_edges;
    uint32_t coupled_move_edges;
    uint32_t reverse_material_length;
    uint64_t restored_ambient_state_index;

    uint8_t reverse_instruction_root_sha256[HHS_EXACT_PASS219_RML15_SHA256_BYTES];
    uint8_t reverse_material_sha256[HHS_EXACT_PASS219_RML15_SHA256_BYTES];

    char previous_hash72[HHS_EXACT_PASS219_RML15_HASH72_STRLEN];
    char route_bound_change_hash72[HHS_EXACT_PASS219_RML15_HASH72_STRLEN];
    char frozen_uqcel_receipt_hash72[HHS_EXACT_PASS219_RML15_HASH72_STRLEN];
    char rml14_successor_receipt_hash72[HHS_EXACT_PASS219_RML15_HASH72_STRLEN];
    char reverse_receipt_hash72[HHS_EXACT_PASS219_RML15_HASH72_STRLEN];
    char frozen_rml13_transition_hash216[HHS_EXACT_PASS219_RML15_HASH216_STRLEN];
    char rml14_successor_transition_hash216[HHS_EXACT_PASS219_RML15_HASH216_STRLEN];
    char reverse_witness_hash216[HHS_EXACT_PASS219_RML15_HASH216_STRLEN];
} HHSExactPass219RML15BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_rml15_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml15_verify_route_reverse_replay(
    const uint8_t *source_bytes,
    size_t source_length,
    const HHSExactPass219RML13RouteWitnessV1 *route_witness,
    const HHSExactPass219RML15ReverseWitnessV1 *reverse_witness,
    HHSExactPass219RML15BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
