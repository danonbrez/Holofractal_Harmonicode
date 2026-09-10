#ifndef HHS_PASS219_RML13_NATIVE_ROUTE_WITNESS_BINDING_1_26_H
#define HHS_PASS219_RML13_NATIVE_ROUTE_WITNESS_BINDING_1_26_H

#include "hhs_runtime_exact_abi_v1_1_base.h"
#include "hhs_runtime_uqcel_1_8.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_RML13_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_RML13_VERSION_MINOR 26U
#define HHS_EXACT_PASS219_RML13_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_RML13_SOURCE_BYTES 632U
#define HHS_EXACT_PASS219_RML13_SHA256_BYTES 32U
#define HHS_EXACT_PASS219_RML13_HASH72_LEN 72U
#define HHS_EXACT_PASS219_RML13_HASH72_STRLEN 73U
#define HHS_EXACT_PASS219_RML13_HASH216_LEN 216U
#define HHS_EXACT_PASS219_RML13_HASH216_STRLEN 217U

typedef enum HHSExactPass219RML13DecisionV1 {
    HHS_EXACT_PASS219_RML13_UNRESOLVED = 0,
    HHS_EXACT_PASS219_RML13_VERIFIED = 1,
    HHS_EXACT_PASS219_RML13_REJECTED = 2
} HHSExactPass219RML13DecisionV1;

typedef enum HHSExactPass219RML13ReasonV1 {
    HHS_EXACT_PASS219_RML13_REASON_NONE = 0,
    HHS_EXACT_PASS219_RML13_REASON_SOURCE_PROVENANCE = 1,
    HHS_EXACT_PASS219_RML13_REASON_ROUTE_WITNESS = 2,
    HHS_EXACT_PASS219_RML13_REASON_PREHASH_FRAME = 3,
    HHS_EXACT_PASS219_RML13_REASON_VM81_ADMISSION = 4,
    HHS_EXACT_PASS219_RML13_REASON_REPLAY = 5,
    HHS_EXACT_PASS219_RML13_REASON_AUTHORITY = 6
} HHSExactPass219RML13ReasonV1;

/*
 * Fixed-width route witness packet produced from one validated RML12 selected
 * route.  All digests are raw SHA-256 bytes decoded from the corresponding
 * RML12 hexadecimal fields.  The packet has no transition authority by itself.
 */
typedef struct HHSExactPass219RML13RouteWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t edge_count;
    uint32_t pair_flip_edges;
    uint32_t coupled_move_edges;
    uint32_t hopf_same_base_edges;
    uint32_t hopf_base_moving_edges;
    uint32_t clifford_full_intertwiner_edges;
    uint32_t clifford_chirality_swap_edges;
    uint32_t residual_u72_edges;
    uint32_t product_geometry_admissible;
    uint32_t all_edges_reversible;
    uint32_t target_reached_exactly;
    uint32_t reverse_restores_source_exactly;
    uint32_t optimizer_transition_authority;
    uint32_t floating_point_authority;
    uint8_t route_sha256[HHS_EXACT_PASS219_RML13_SHA256_BYTES];
    uint8_t selection_sha256[HHS_EXACT_PASS219_RML13_SHA256_BYTES];
    uint8_t bundle_sha256[HHS_EXACT_PASS219_RML13_SHA256_BYTES];
    uint8_t source_state_sha256[HHS_EXACT_PASS219_RML13_SHA256_BYTES];
    uint8_t target_state_sha256[HHS_EXACT_PASS219_RML13_SHA256_BYTES];
} HHSExactPass219RML13RouteWitnessV1;

typedef struct HHSExactPass219RML13BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason;
    uint32_t source_provenance_verified;
    uint32_t route_witness_verified;
    uint32_t witness_serialization_exact;
    uint32_t witness_root_embedded_pre_hash;
    uint32_t candidate_frame_committed;
    uint32_t deterministic_replay_verified;
    uint32_t route_change_hash72_bound_to_witness;
    uint32_t route_hash216_identity_bound_to_witness;
    uint32_t inherited_uqcel_receipt_material_frozen;
    uint32_t inherited_receipt_hash72_directly_bound_to_route_witness;
    uint32_t single_vm81_commit_authority_preserved;
    uint32_t optimizer_transition_authority;
    uint32_t floating_point_authority;
    uint32_t hash216_persistence_authority;
    uint32_t scalar_projection_substitution_authority;
    uint32_t edge_count;
    uint32_t pair_flip_edges;
    uint32_t coupled_move_edges;
    uint32_t hopf_same_base_edges;
    uint32_t hopf_base_moving_edges;
    uint32_t clifford_full_intertwiner_edges;
    uint32_t clifford_chirality_swap_edges;
    uint32_t residual_u72_edges;
    uint16_t vm5184_address;
    uint16_t reserved0;
    uint8_t witness_root_sha256[HHS_EXACT_PASS219_RML13_SHA256_BYTES];
    uint8_t route_environment_root_sha256[HHS_EXACT_PASS219_RML13_SHA256_BYTES];
    uint8_t candidate_frame_sha256[HHS_EXACT_PASS219_RML13_SHA256_BYTES];
    char change_hash72[HHS_EXACT_PASS219_RML13_HASH72_STRLEN];
    char receipt_hash72[HHS_EXACT_PASS219_RML13_HASH72_STRLEN];
    char replay_hash72[HHS_EXACT_PASS219_RML13_HASH72_STRLEN];
    char hash216_triplet[HHS_EXACT_PASS219_RML13_HASH216_STRLEN];
    char transition_hash216[HHS_EXACT_PASS219_RML13_HASH216_STRLEN];
} HHSExactPass219RML13BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_rml13_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rml13_bind_route_pre_hash(
    const uint8_t *source_bytes,
    size_t source_length,
    const HHSExactPass219RML13RouteWitnessV1 *route_witness,
    HHSExactPass219RML13BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
