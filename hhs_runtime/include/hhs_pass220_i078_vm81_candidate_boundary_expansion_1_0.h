#ifndef HHS_PASS220_I078_VM81_CANDIDATE_BOUNDARY_EXPANSION_1_0_H
#define HHS_PASS220_I078_VM81_CANDIDATE_BOUNDARY_EXPANSION_1_0_H

#include "hhs_pass220_i077_vm81_exact_matrix_power_execution_1_0.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS220_I078_VERSION_MAJOR 1U
#define HHS_EXACT_PASS220_I078_VERSION_MINOR 0U
#define HHS_EXACT_PASS220_I078_VERSION_PATCH 0U

#define HHS_EXACT_PASS220_I078_SCALE_NUMERATOR UINT32_C(1001)
#define HHS_EXACT_PASS220_I078_SCALE_DENOMINATOR UINT32_C(1000)
#define HHS_EXACT_PASS220_I078_ROOT_SEED_NUMERATOR UINT64_C(179971179971)
#define HHS_EXACT_PASS220_I078_ROOT_SEED_DENOMINATOR UINT32_C(1000000)
#define HHS_EXACT_PASS220_I078_MANIFOLD_WORDS HHS_EXACT_VM81_CELLS
#define HHS_EXACT_PASS220_I078_HASH72_LEN 72U
#define HHS_EXACT_PASS220_I078_HASH72_STRLEN 73U
#define HHS_EXACT_PASS220_I078_HASH216_LEN 216U
#define HHS_EXACT_PASS220_I078_HASH216_STRLEN 217U
#define HHS_EXACT_PASS220_I078_SHA256_HEX_STRLEN 65U

typedef enum HHSExactPass220I078DecisionV1 {
    HHS_EXACT_PASS220_I078_UNRESOLVED = 0,
    HHS_EXACT_PASS220_I078_ADMIT = 1,
    HHS_EXACT_PASS220_I078_REJECT = 2
} HHSExactPass220I078DecisionV1;

typedef enum HHSExactPass220I078ReasonV1 {
    HHS_EXACT_PASS220_I078_REASON_NONE = 0,
    HHS_EXACT_PASS220_I078_REASON_NODE_ID = 1,
    HHS_EXACT_PASS220_I078_REASON_I077_BINDING = 2,
    HHS_EXACT_PASS220_I078_REASON_CANDIDATE_IDENTITY = 3,
    HHS_EXACT_PASS220_I078_REASON_UQCEL_IDENTITY = 4,
    HHS_EXACT_PASS220_I078_REASON_SCALE_1001 = 5,
    HHS_EXACT_PASS220_I078_REASON_ZERO_FIXED_POINT = 6,
    HHS_EXACT_PASS220_I078_REASON_AUTHORITY = 7
} HHSExactPass220I078ReasonV1;

typedef struct HHSExactPass220I078DescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t node_count;
    uint32_t frame_words;
    uint32_t scale_numerator;
    uint32_t scale_denominator;
    uint64_t root_seed_numerator;
    uint32_t root_seed_denominator;
    uint8_t i077_binding_required;
    uint8_t downstream_candidate_ingress;
    uint8_t byte_exact_candidate_identity;
    uint8_t uqcel_identity_evaluation;
    uint8_t exact_rational_scale1001;
    uint8_t zero_energy_fixed_point;
    uint8_t delta_e_zero_required;
    uint8_t psi_zero_required;
    uint8_t omega_true_required;
    uint8_t deterministic_replay_required;
    uint8_t fail_closed_invalid_candidate;
    uint8_t host_matrixpower_authority;
    uint8_t host_square_matrix_fallback_authority;
    uint8_t floating_point_authority;
    uint8_t numeric_exponent_evaluation_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_commit_authority;
    uint8_t canonical_hash216_commit_authority;
    uint8_t canonical_persistence_authority;
    uint8_t external_egress_authority;
    uint8_t reserved0[4];
} HHSExactPass220I078DescriptorV1;

typedef struct HHSExactPass220I078BoundaryV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason;
    uint32_t node_id;
    uint32_t frame_words;
    uint32_t scale_numerator;
    uint32_t scale_denominator;
    uint32_t scale_words_verified;
    uint32_t zero_word_count;
    uint32_t zero_fixed_point_words_verified;
    uint8_t i077_execution_verified;
    uint8_t candidate_frame_exact;
    uint8_t uqcel_identity_evaluated;
    uint8_t uqcel_transition_matches_i077;
    uint8_t exact_scale1001_verified;
    uint8_t zero_energy_fixed_point_verified;
    uint8_t delta_e_zero;
    uint8_t psi_zero;
    uint8_t omega_true;
    uint8_t deterministic_replay_verified;
    uint8_t fail_closed_boundary;
    uint8_t host_matrixpower_used;
    uint8_t square_matrix_fallback_used;
    uint8_t floating_point_used;
    uint8_t numeric_exponent_evaluated;
    uint8_t canonical_state_persisted;
    uint8_t reserved0[7];
    int64_t delta_e_numerator;
    uint64_t delta_e_denominator;
    int64_t psi_numerator;
    uint64_t psi_denominator;
    char candidate_sha256[HHS_EXACT_PASS220_I078_SHA256_HEX_STRLEN];
    char scale_witness_sha256[HHS_EXACT_PASS220_I078_SHA256_HEX_STRLEN];
    char i077_receipt_hash72[HHS_EXACT_PASS220_I078_HASH72_STRLEN];
    char i077_transition_hash216[HHS_EXACT_PASS220_I078_HASH216_STRLEN];
    char boundary_change_hash72[HHS_EXACT_PASS220_I078_HASH72_STRLEN];
    char boundary_receipt_hash72[HHS_EXACT_PASS220_I078_HASH72_STRLEN];
    char boundary_hash216[HHS_EXACT_PASS220_I078_HASH216_STRLEN];
    char boundary_identity216[HHS_EXACT_PASS220_I078_HASH216_STRLEN];
} HHSExactPass220I078BoundaryV1;

HHS_EXACT_API uint32_t hhs_exact_pass220_i078_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_i078_descriptor(
    HHSExactPass220I078DescriptorV1 *out_descriptor
);

/*
 * Materialize the exact source-bound I077 candidate frame for downstream I078
 * boundary testing/admission. This is a candidate frame only and grants no
 * canonical mutation, receipt mint, persistence, or egress authority.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_i078_reference_candidate(
    uint32_t node_id,
    HHSExactVM81Frame *out_candidate
);

/*
 * Ingest one downstream candidate frame. The boundary first binds to the
 * verified I077 exact execution, requires byte identity with the source-bound
 * I077 candidate, evaluates the same exact UQCEL transport identity, applies
 * the exact 1001/1000 manifold-scale witness to all 81 words without floats,
 * proves the zero fixed point, and emits a candidate-only Hash216 boundary
 * lineage. Any mismatch rejects without fallback.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_i078_expand_candidate_boundary(
    uint32_t node_id,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactPass220I078BoundaryV1 *out_boundary
);

#ifdef __cplusplus
}
#endif

#endif
