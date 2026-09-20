#ifndef HHS_PASS219_LANE5_CLOAKED_TRIPARTITE_CONSTRAINT_1_61_H
#define HHS_PASS219_LANE5_CLOAKED_TRIPARTITE_CONSTRAINT_1_61_H

#include "hhs_runtime_uqcel_1_8.h"
#include "hhs_hash216_bytes.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_TRIPARTITE_VERSION UINT32_C(0x0001003d)
#define HHS_EXACT_PASS219_LANE5_TRIPARTITE_NAMESPACE UINT32_C(0x0002193d)
#define HHS_EXACT_PASS219_LANE5_TRIPARTITE_SERIALIZATION_CHARS ((size_t)5184)

typedef enum HHSExactPass219Lane5TripartiteReasonV1 {
    HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_NONE = 0,
    HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_SERIALIZATION_WIDTH = 1,
    HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_DELTA_ZERO = 2,
    HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_PHASE_DENOMINATOR_ZERO = 3,
    HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_CURVATURE_MISMATCH = 4,
    HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_TRANSITION_SURFACE_MISMATCH = 5,
    HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_PAYLOAD_MISMATCH = 6
} HHSExactPass219Lane5TripartiteReasonV1;

typedef struct HHSExactPass219Lane5TripartiteAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t theorem_revision;
    uint32_t vm81_cells;
    uint32_t local_cell_width;
    uint32_t serialization_characters;
    uint8_t theorem_hhs_t5184_005;
    uint8_t ordered_curvature_surface_preserved;
    uint8_t transition_surface_preserved;
    uint8_t payload_delta_surface_preserved;
    uint8_t exact_bigint_only;
    uint8_t signed_difference_exact;
    uint8_t equality_by_cross_product;
    uint8_t denominator_cancellation_allowed;
    uint8_t division_by_zero_allowed;
    uint8_t fixed_5184_binding_required;
    uint8_t rna_cell_wall_required_downstream;
    uint8_t pqc_witness_required_downstream;
    uint8_t exact_cpu_vm81_replay_required_downstream;
    uint8_t hash216_receipt_only;
    uint8_t legacy_physics_semantics_allowed;
    uint8_t floating_point_canonical_authority;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_commit_authority;
    uint8_t canonical_persistence_authority;
    uint8_t reserved0[4];
} HHSExactPass219Lane5TripartiteAuthorityV1;

typedef struct HHSExactPass219Lane5TripartiteInputV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactBigUIntView Gamma_macro;
    HHSExactBigUIntView Rho_payload;
    HHSExactBigUIntView Sigma_2D;
    HHSExactBigUIntView Omega_root;
    HHSExactBigUIntView P_macro;
    HHSExactBigUIntView p_ingress;
    HHSExactBigUIntView q_egress;
    const char *serialization_5184;
    size_t serialization_length;
} HHSExactPass219Lane5TripartiteInputV1;

typedef struct HHSExactPass219Lane5TripartiteReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t reason;
    int8_t q_minus_p_sign;
    int8_t transition_coefficient_sign;
    uint8_t serialization_width_verified;
    uint8_t omega_nonzero;
    uint8_t phase_denominator_nonzero;
    uint8_t curvature_surface_equal;
    uint8_t transition_surface_equal;
    uint8_t payload_surface_equal;
    uint8_t arithmetic_closure_delta_e_zero;
    uint8_t closure_valid;
    uint8_t candidate_only;
    uint8_t requires_rna_cell_wall;
    uint8_t requires_pqc_witness;
    uint8_t requires_exact_cpu_vm81_replay;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_commit_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved0[5];
    char serialization_hash216[HHS_HASH216_BYTES_STRLEN];
    char commit_hash216[HHS_HASH216_BYTES_STRLEN];
} HHSExactPass219Lane5TripartiteReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_tripartite_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_tripartite_authority(
    HHSExactPass219Lane5TripartiteAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_tripartite_verify(
    const HHSExactPass219Lane5TripartiteInputV1 *input,
    HHSExactPass219Lane5TripartiteReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
