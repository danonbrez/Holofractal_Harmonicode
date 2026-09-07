#ifndef HHS_PASS219_HHCQ_TEMPORAL_CUBIC_1_28_H
#define HHS_PASS219_HHCQ_TEMPORAL_CUBIC_1_28_H

#include "hhs_pass219_hhcq_collapse_regret_1_27.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HHCQ_TEMPORAL_CUBIC_VERSION UINT32_C(0x0001001C)
#define HHS_EXACT_PASS219_HHCQ_TEMPORAL_PHASE_MODULUS UINT32_C(72)
#define HHS_EXACT_PASS219_HHCQ_TEMPORAL_CARDANO_BRANCH_COUNT UINT32_C(3)
#define HHS_EXACT_PASS219_HHCQ_TEMPORAL_NO_ROOT UINT8_C(0xFF)

typedef struct HHSExactPass219HHCQTemporalCubicDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t inherited_policy_state_bytes;
    uint32_t phase_modulus;
    uint32_t symbolic_cardano_branch_count;
    uint8_t compact_cubic_identity;
    uint8_t factored_discriminant_identity;
    uint8_t radical_eliminated_from_canonical_path;
    uint8_t z72_root_scan;
    uint8_t composite_ring_root_count_variable;
    uint8_t discrete_neighbor_direction;
    uint8_t temporal_regret_composition;
    uint8_t phase5_resolution_locked;
    uint8_t fixed_size_policy_state;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219HHCQTemporalCubicDescriptorV1;

typedef struct HHSExactPass219HHCQTemporalCubicWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    int32_t m;
    int32_t w;
    int32_t x;
    int32_t y;
    int32_t z;
    int32_t t;
    int64_t cross_phase_g;
    int64_t leading_x2y2;
    int64_t constant_term;
    int64_t residual_minus;
    int64_t residual_zero;
    int64_t residual_plus;
    uint64_t absolute_residual_zero;
    uint64_t temporal_gain;
    int8_t temporal_direction;
    uint8_t exact_integer_only;
    uint8_t candidate_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint64_t witness_signature64;
} HHSExactPass219HHCQTemporalCubicWitnessV1;

typedef struct HHSExactPass219HHCQTemporalCardanoFactorV1 {
    uint32_t struct_size;
    uint32_t version;
    int32_t m;
    int32_t w;
    int32_t x;
    int32_t y;
    int32_t z;
    int64_t cross_phase_g;
    int64_t cardano_b;
    int64_t x12y12;
    int64_t discriminant_r;
    uint8_t exact_factorization;
    uint8_t exact_integer_only;
    uint8_t candidate_only;
    uint8_t floating_point_authority;
    uint64_t witness_signature64;
} HHSExactPass219HHCQTemporalCardanoFactorV1;

typedef struct HHSExactPass219HHCQTemporalZ72RootsV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t roots_0_63;
    uint8_t roots_64_71;
    uint8_t root_count;
    uint8_t phase_hint72;
    uint8_t preferred_root72;
    int8_t preferred_direction;
    uint8_t symbolic_cardano_branch_count;
    uint8_t composite_ring_root_count_variable;
    uint8_t exact_integer_only;
    uint8_t candidate_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint8_t reserved0[2];
    uint64_t root_signature64;
} HHSExactPass219HHCQTemporalZ72RootsV1;

typedef struct HHSExactPass219HHCQTemporalRegretDecisionV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219HHCQJointDecisionV1 base_decision;
    HHSExactPass219HHCQCollapseWitnessV1 collapse;
    HHSExactPass219HHCQTemporalCubicWitnessV1 temporal;
    HHSExactPass219HHCQTemporalZ72RootsV1 roots;
    uint64_t regret_margin_units;
    uint64_t regret_quantum_units;
    uint8_t margin_bucket;
    uint8_t update_pressure;
    int8_t temporal_alignment;
    uint8_t updated;
    uint8_t phase5_resolution_locked;
    uint32_t inherited_policy_state_bytes;
    uint32_t update_count;
    uint64_t step_count;
    uint64_t decision_signature64;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
} HHSExactPass219HHCQTemporalRegretDecisionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_hhcq_temporal_cubic_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_temporal_cubic_descriptor(
    HHSExactPass219HHCQTemporalCubicDescriptorV1 *out_descriptor);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_temporal_cubic_witness(
    int32_t m,
    int32_t w,
    int32_t x,
    int32_t y,
    int32_t z,
    int32_t t,
    HHSExactPass219HHCQTemporalCubicWitnessV1 *out_witness);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_temporal_cardano_factor(
    int32_t m,
    int32_t w,
    int32_t x,
    int32_t y,
    int32_t z,
    HHSExactPass219HHCQTemporalCardanoFactorV1 *out_factor);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_temporal_z72_roots(
    int32_t m,
    int32_t w,
    int32_t x,
    int32_t y,
    int32_t z,
    uint8_t phase_hint72,
    HHSExactPass219HHCQTemporalZ72RootsV1 *out_roots);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_temporal_regret_step(
    const HHSExactPass219HHCQJointPreparedV1 *prepared,
    uint8_t feedback_lane,
    uint64_t regret_margin_units,
    uint64_t regret_quantum_units,
    HHSExactPass219HHCQJointStateV1 *state,
    HHSExactPass219HHCQTemporalRegretDecisionV1 *out_decision);

#ifdef __cplusplus
}
#endif

#endif
