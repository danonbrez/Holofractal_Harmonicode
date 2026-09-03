#ifndef HHS_PASS219_FULL_SYMBOLIC_UQCEL_LOWERING_1_22_H
#define HHS_PASS219_FULL_SYMBOLIC_UQCEL_LOWERING_1_22_H

#include "hhs_pass219_monolithic_constraint_abi_1_20.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_FULL_SYMBOLIC_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_FULL_SYMBOLIC_VERSION_MINOR 22U
#define HHS_EXACT_PASS219_FULL_SYMBOLIC_VERSION_PATCH 0U

#define HHS_EXACT_PASS219_FULL_SYMBOLIC_TERM_COUNT 15U
#define HHS_EXACT_PASS219_FULL_SYMBOLIC_EDGE_COUNT HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT
#define HHS_EXACT_PASS219_FULL_SYMBOLIC_FAMILY_COUNT HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT
#define HHS_EXACT_PASS219_FULL_SYMBOLIC_RATIO_MAX_BYTES HHS_EXACT_UQCEL_MAX_P_BYTES
#define HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_LEN HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN
#define HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_STRLEN HHS_EXACT_PASS219_MONOLITHIC_HASH216_STRLEN

typedef enum HHSExactPass219FullSymbolicTermIdV1 {
    HHS_EXACT_PASS219_FS_TERM_T3_MINUS_T = 0,
    HHS_EXACT_PASS219_FS_TERM_P3_MINUS_P_OVER_DELTA = 1,
    HHS_EXACT_PASS219_FS_TERM_T3_MINUS_T_OVER_DELTA = 2,
    HHS_EXACT_PASS219_FS_TERM_P2_MOD_PQ = 3,
    HHS_EXACT_PASS219_FS_TERM_M2_MINUS_M = 4,
    HHS_EXACT_PASS219_FS_TERM_S = 5,
    HHS_EXACT_PASS219_FS_TERM_S_SUBSTITUTION_RHS = 6,
    HHS_EXACT_PASS219_FS_TERM_MATRIX_PLUS_XY_OVER_AT = 7,
    HHS_EXACT_PASS219_FS_TERM_MOD_F_OVER_U_OVER_BT = 8,
    HHS_EXACT_PASS219_FS_TERM_AB_OVER_P2 = 9,
    HHS_EXACT_PASS219_FS_TERM_SQRT_AB = 10,
    HHS_EXACT_PASS219_FS_TERM_OUTER_LHS = 11,
    HHS_EXACT_PASS219_FS_TERM_TERMINAL_RHS = 12,
    HHS_EXACT_PASS219_FS_TERM_DELTA_OVER_P = 13,
    HHS_EXACT_PASS219_FS_TERM_DELTA_ROOT_RHS = 14
} HHSExactPass219FullSymbolicTermIdV1;

typedef enum HHSExactPass219FullSymbolicDecisionV1 {
    HHS_EXACT_PASS219_FULL_SYMBOLIC_UNRESOLVED = 0,
    HHS_EXACT_PASS219_FULL_SYMBOLIC_LOWERED = 1,
    HHS_EXACT_PASS219_FULL_SYMBOLIC_REJECTED = 2
} HHSExactPass219FullSymbolicDecisionV1;

typedef enum HHSExactPass219FullSymbolicRejectReasonV1 {
    HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_NONE = 0,
    HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_SOURCE_IDENTITY = 1,
    HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_PROVENANCE_ROOT = 2,
    HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_RATIO_ENCODING = 3,
    HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_EDGE_MISMATCH = 4,
    HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_ORDERED_PHASE = 5
} HHSExactPass219FullSymbolicRejectReasonV1;

/*
 * Exact ratio witness.  This is a proof-view, not a canonical persisted
 * numeric object.  Numerator and denominator components use canonical
 * minimal BigUInt byte encodings.  Equality is checked by exact
 * cross-multiplication, never floating-point conversion.
 *
 * sign = -1, 0, +1.
 * sign == 0 iff numerator == 0.
 * denominator is always positive and nonzero.
 */
typedef struct HHSExactPass219SignedRatioViewV1 {
    uint32_t struct_size;
    int8_t sign;
    uint8_t reserved0[3];
    HHSExactBigUIntView numerator;
    HHSExactBigUIntView denominator;
} HHSExactPass219SignedRatioViewV1;

typedef struct HHSExactPass219FullSymbolicWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t source_sha256[HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES];
    uint8_t pass159_provenance_root[HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES];
    HHSExactPass219OctonionStateV1 octonion_state;
    HHSExactPass219SignedRatioViewV1 terms[HHS_EXACT_PASS219_FULL_SYMBOLIC_TERM_COUNT];
} HHSExactPass219FullSymbolicWitnessV1;

typedef struct HHSExactPass219FullSymbolicDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t term_count;
    uint32_t edge_count;
    uint32_t family_count;
    uint64_t required_edge_mask;
    uint32_t required_family_mask;
    uint64_t residual_mask_on_complete_lowering;
    uint8_t source_structure_preserved;
    uint8_t all_edges_single_transaction;
    uint8_t pass159_provenance_required;
    uint8_t exact_big_ratio_cross_multiply;
    uint8_t ordered_octonion_state_required;
    uint8_t legacy_v1_full_symbolic_input_sufficient;
    uint8_t candidate_value_producer_included;
    uint8_t vm81_execution_included;
    uint8_t hash72_execution_receipt_included;
    uint8_t deterministic_replay_included;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t persistence_mutation_authority;
    uint8_t reserved0[2];
} HHSExactPass219FullSymbolicDescriptorV1;

typedef struct HHSExactPass219FullSymbolicLoweringV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reject_reason;
    uint32_t resolved_family_mask;
    uint32_t failed_family_mask;
    uint64_t edge_satisfied_mask;
    uint64_t edge_failed_mask;
    uint64_t edge_unresolved_mask;
    uint64_t residual_mask;
    uint8_t source_identity_exact;
    uint8_t provenance_root_bound;
    uint8_t all_values_exact;
    uint8_t one_candidate_state;
    uint8_t ordered_xy_yx_bound;
    uint8_t monolithic_chain_lowered;
    uint8_t candidate_value_producer_authority;
    uint8_t vm81_execution_verified;
    uint8_t hash72_execution_receipt_verified;
    uint8_t deterministic_replay_verified;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t persistence_mutation_authority;
    uint8_t reserved0[2];
    char candidate_state_hash216[HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_STRLEN];
    char family_witness_hash216[HHS_EXACT_PASS219_FULL_SYMBOLIC_FAMILY_COUNT][HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_STRLEN];
} HHSExactPass219FullSymbolicLoweringV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_full_symbolic_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_full_symbolic_descriptor(
    HHSExactPass219FullSymbolicDescriptorV1 *out_descriptor
);

/*
 * Lower one complete source-bound term-value witness into the exact
 * monolithic edge/family surface.
 *
 * LOWERED means every one of the ten frozen source equality edges is exact
 * in one Pass159-provenance-bound candidate transaction and all five
 * historical UQCEL residual bits are cleared for this witness.
 *
 * LOWERED does NOT mean VM81 execution/admission, Hash72 execution receipt,
 * deterministic replay, or terminal Pass169 proof. Those remain downstream
 * authority gates.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_full_symbolic_lower(
    const HHSExactPass219FullSymbolicWitnessV1 *witness,
    HHSExactPass219FullSymbolicLoweringV1 *out_lowering
);

#ifdef __cplusplus
}
#endif

#endif
