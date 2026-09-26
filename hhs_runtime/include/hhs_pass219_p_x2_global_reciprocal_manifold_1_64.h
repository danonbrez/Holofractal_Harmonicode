#ifndef HHS_PASS219_P_X2_GLOBAL_RECIPROCAL_MANIFOLD_1_64_H
#define HHS_PASS219_P_X2_GLOBAL_RECIPROCAL_MANIFOLD_1_64_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_PX2_MANIFOLD_VERSION UINT32_C(0x00010040)
#define HHS_EXACT_PASS219_PX2_MANIFOLD_NAMESPACE UINT32_C(0x00021940)
#define HHS_EXACT_PASS219_PX2_MANIFOLD_SOURCE_BYTES UINT32_C(579)
#define HHS_EXACT_PASS219_PX2_MANIFOLD_SOURCE_CHARS UINT32_C(569)
#define HHS_EXACT_PASS219_PX2_MANIFOLD_PAREN_PAIRS UINT32_C(61)
#define HHS_EXACT_PASS219_PX2_MANIFOLD_DOUBLE_EQ UINT32_C(12)
#define HHS_EXACT_PASS219_PX2_MANIFOLD_SINGLE_EQ UINT32_C(1)
#define HHS_EXACT_PASS219_PX2_MANIFOLD_RELATION_EDGES UINT32_C(13)
#define HHS_EXACT_PASS219_PX2_MANIFOLD_SHA256_BYTES UINT32_C(32)

enum {
    HHS_EXACT_PASS219_PX2_DECISION_INVALID = 0,
    HHS_EXACT_PASS219_PX2_DECISION_VERIFIED = 1,
    HHS_EXACT_PASS219_PX2_DECISION_REJECTED = 2
};

typedef struct HHSExactPass219PX2ManifoldAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t source_bytes;
    uint32_t source_chars;
    uint32_t relation_edges;
    uint8_t source_identity_mandatory;
    uint8_t source_order_mandatory;
    uint8_t typed_relation_edges;
    uint8_t outer_p_x2_closure;
    uint8_t delta_negative_p_boundary;
    uint8_t bx_negative_5184_carrier;
    uint8_t pass178_constraint_program_semantics;
    uint8_t lane5_preflight_required;
    uint8_t signed_environmental_preflight_required;
    uint8_t scalar_simplification_authority;
    uint8_t equality_reversal_authority;
    uint8_t delta_cancellation_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
} HHSExactPass219PX2ManifoldAuthorityV1;

typedef struct HHSExactPass219PX2ManifoldReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t decision;
    uint32_t source_bytes;
    uint32_t open_parens;
    uint32_t close_parens;
    uint32_t double_equals_edges;
    uint32_t single_equals_edges;
    uint32_t relation_edges;
    uint8_t source_sha256[HHS_EXACT_PASS219_PX2_MANIFOLD_SHA256_BYTES];
    uint8_t source_hash_verified;
    uint8_t parentheses_balanced;
    uint8_t outer_prefix_exact;
    uint8_t outer_denominator_exact;
    uint8_t ordered_markers_exact;
    uint8_t repeated_velocity_relation_preserved;
    uint8_t modular_ratio_order_preserved;
    uint8_t euler_phase_surface_preserved;
    uint8_t xyzw_nested_surface_preserved;
    uint8_t delta_bx_boundary_preserved;
    uint8_t typed_relation_edges_preserved;
    uint8_t scalar_simplification_authority;
    uint8_t equality_reversal_authority;
    uint8_t delta_cancellation_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t reserved0[6];
} HHSExactPass219PX2ManifoldReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_px2_manifold_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_px2_manifold_authority(
    HHSExactPass219PX2ManifoldAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_px2_manifold_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_px2_manifold_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219_PX2_MANIFOLD_SHA256_BYTES]
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_px2_manifold_verify(
    HHSExactPass219PX2ManifoldReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
