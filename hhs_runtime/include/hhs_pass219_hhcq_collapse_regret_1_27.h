#ifndef HHS_PASS219_HHCQ_COLLAPSE_REGRET_1_27_H
#define HHS_PASS219_HHCQ_COLLAPSE_REGRET_1_27_H

#include "hhs_pass219_hhcq_joint_local_router_1_26.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HHCQ_COLLAPSE_REGRET_VERSION UINT32_C(0x0001001B)
#define HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_M UINT32_C(36)
#define HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_T UINT32_C(9)
#define HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_ROOT UINT32_C(9)
#define HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_X UINT32_C(9)
#define HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_PRESSURE UINT32_C(9)

typedef struct HHSExactPass219HHCQCollapseRegretDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t inherited_policy_state_bytes;
    uint32_t max_pressure;
    uint8_t exact_quadratic_collapse;
    uint8_t radical_eliminated_from_canonical_path;
    uint8_t discrete_neighbor_direction;
    uint8_t training_only_regret_scale;
    uint8_t phase5_resolution_locked;
    uint8_t fixed_size_policy_state;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[3];
} HHSExactPass219HHCQCollapseRegretDescriptorV1;

typedef struct HHSExactPass219HHCQCollapseWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    int32_t m;
    int32_t t;
    int32_t w;
    int32_t y;
    int32_t z;
    int32_t x;
    int64_t coefficient_d;
    int64_t coefficient_a;
    int64_t coefficient_c;
    int64_t residual_minus;
    int64_t residual_zero;
    int64_t residual_plus;
    uint64_t absolute_residual_zero;
    uint64_t collapse_gain;
    int8_t collapse_direction;
    uint8_t singular;
    uint8_t exact_integer_only;
    uint8_t candidate_only;
    uint8_t floating_point_authority;
    uint8_t reserved0[3];
    uint64_t witness_signature64;
} HHSExactPass219HHCQCollapseWitnessV1;

typedef struct HHSExactPass219HHCQCollapseRegretDecisionV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219HHCQJointDecisionV1 base_decision;
    HHSExactPass219HHCQCollapseWitnessV1 collapse;
    uint64_t regret_margin_units;
    uint64_t regret_quantum_units;
    uint8_t margin_bucket;
    uint8_t update_pressure;
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
} HHSExactPass219HHCQCollapseRegretDecisionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_hhcq_collapse_regret_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_collapse_regret_descriptor(
    HHSExactPass219HHCQCollapseRegretDescriptorV1 *out_descriptor);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_collapse_witness(
    int32_t m,
    int32_t t,
    int32_t w,
    int32_t y,
    int32_t z,
    int32_t x,
    HHSExactPass219HHCQCollapseWitnessV1 *out_witness);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_collapse_regret_step(
    const HHSExactPass219HHCQJointPreparedV1 *prepared,
    uint8_t feedback_lane,
    uint64_t regret_margin_units,
    uint64_t regret_quantum_units,
    HHSExactPass219HHCQJointStateV1 *state,
    HHSExactPass219HHCQCollapseRegretDecisionV1 *out_decision);

#ifdef __cplusplus
}
#endif

#endif
