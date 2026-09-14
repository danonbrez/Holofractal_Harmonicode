#ifndef HHS_PASS219_RML14_ROUTE_BOUND_RECEIPT_SUCCESSOR_1_27_H
#define HHS_PASS219_RML14_ROUTE_BOUND_RECEIPT_SUCCESSOR_1_27_H

#include "hhs_pass219_rml13_native_route_witness_binding_1_26.h"
#include "hhs_hash216.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_RML14_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_RML14_VERSION_MINOR 27U
#define HHS_EXACT_PASS219_RML14_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_RML14_SHA256_BYTES 32U
#define HHS_EXACT_PASS219_RML14_HASH72_LEN 72U
#define HHS_EXACT_PASS219_RML14_HASH72_STRLEN 73U
#define HHS_EXACT_PASS219_RML14_HASH216_LEN 216U
#define HHS_EXACT_PASS219_RML14_HASH216_STRLEN 217U
#define HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL 1024U

typedef enum HHSExactPass219RML14DecisionV1 {
    HHS_EXACT_PASS219_RML14_UNRESOLVED = 0,
    HHS_EXACT_PASS219_RML14_VERIFIED = 1,
    HHS_EXACT_PASS219_RML14_REJECTED = 2
} HHSExactPass219RML14DecisionV1;

typedef enum HHSExactPass219RML14ReasonV1 {
    HHS_EXACT_PASS219_RML14_REASON_NONE = 0,
    HHS_EXACT_PASS219_RML14_REASON_RML13_PARENT = 1,
    HHS_EXACT_PASS219_RML14_REASON_RECEIPT_MATERIAL = 2,
    HHS_EXACT_PASS219_RML14_REASON_CANONICAL_HASH = 3,
    HHS_EXACT_PASS219_RML14_REASON_AUTHORITY = 4
} HHSExactPass219RML14ReasonV1;

typedef struct HHSExactPass219RML14BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason;

    uint32_t rml13_binding_verified;
    uint32_t receipt_material_exact;
    uint32_t receipt_material_contains_route_witness_root;
    uint32_t receipt_material_contains_route_bound_change_hash72;
    uint32_t successor_receipt_hash72_route_bound;
    uint32_t successor_hash216_triplet_route_bound;
    uint32_t successor_hash216_identity_route_bound;
    uint32_t frozen_uqcel_receipt_preserved;
    uint32_t frozen_rml13_transition_preserved;
    uint32_t canonical_hash72_delegate_used;
    uint32_t canonical_hash216_delegate_used;
    uint32_t canonical_hash216_parity_with_frozen_uqcel_verified;
    uint32_t independent_hash_implementation_used;
    uint32_t second_vm81_commit_primitive_added;
    uint32_t single_vm81_commit_authority_preserved;
    uint32_t optimizer_transition_authority;
    uint32_t floating_point_authority;
    uint32_t hash216_persistence_authority;
    uint32_t scalar_projection_substitution_authority;

    uint32_t receipt_material_length;
    uint32_t edge_count;
    uint32_t pair_flip_edges;
    uint32_t coupled_move_edges;
    uint32_t hopf_same_base_edges;
    uint32_t hopf_base_moving_edges;
    uint32_t clifford_full_intertwiner_edges;
    uint32_t clifford_chirality_swap_edges;
    uint32_t clifford_even_sector_preserving_edges;
    uint32_t residual_u72_edges;
    uint16_t vm5184_address;
    uint16_t reserved0;

    uint8_t receipt_material_sha256[HHS_EXACT_PASS219_RML14_SHA256_BYTES];
    uint8_t witness_root_sha256[HHS_EXACT_PASS219_RML14_SHA256_BYTES];
    uint8_t route_environment_root_sha256[HHS_EXACT_PASS219_RML14_SHA256_BYTES];
    uint8_t candidate_frame_sha256[HHS_EXACT_PASS219_RML14_SHA256_BYTES];

    char previous_hash72[HHS_EXACT_PASS219_RML14_HASH72_STRLEN];
    char change_hash72[HHS_EXACT_PASS219_RML14_HASH72_STRLEN];
    char frozen_uqcel_receipt_hash72[HHS_EXACT_PASS219_RML14_HASH72_STRLEN];
    char successor_receipt_hash72[HHS_EXACT_PASS219_RML14_HASH72_STRLEN];
    char frozen_rml13_transition_hash216[HHS_EXACT_PASS219_RML14_HASH216_STRLEN];
    char successor_hash216_triplet[HHS_EXACT_PASS219_RML14_HASH216_STRLEN];
    char successor_transition_hash216[HHS_EXACT_PASS219_RML14_HASH216_STRLEN];
} HHSExactPass219RML14BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_rml14_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml14_bind_route_receipt_successor(
    const uint8_t *source_bytes,
    size_t source_length,
    const HHSExactPass219RML13RouteWitnessV1 *route_witness,
    HHSExactPass219RML14BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
