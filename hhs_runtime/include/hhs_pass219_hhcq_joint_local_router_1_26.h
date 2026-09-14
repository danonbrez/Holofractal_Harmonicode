#ifndef HHS_PASS219_HHCQ_JOINT_LOCAL_ROUTER_1_26_H
#define HHS_PASS219_HHCQ_JOINT_LOCAL_ROUTER_1_26_H

#include "hhs_pass219_core_holographic_four_lane_1_24.h"
#include "hhs_pass219_hhcq_rotational_resolution_1_25.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HHCQ_JOINT_VERSION UINT32_C(0x0001001A)
#define HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT HHS_EXACT_PASS219_HOLO4_LANE_COUNT
#define HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT UINT32_C(8)
#define HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND
#define HHS_EXACT_PASS219_HHCQ_JOINT_UPDATE_QUANTUM HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM
#define HHS_EXACT_PASS219_HHCQ_JOINT_FEEDBACK_NONE HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE

typedef struct HHSExactPass219HHCQJointDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t parameter_count;
    uint32_t phase_modulus;
    uint32_t resolution_count;
    uint32_t lane_count;
    uint32_t feature_count;
    uint32_t update_quantum;
    uint8_t phase5_resolution_constraint_authority;
    uint8_t local_lane_learning;
    uint8_t fixed_size_policy_state;
    uint8_t exact_region_features;
    uint8_t orthogonal_parameter_identity;
    uint8_t dyadic_trinary_dual_primitive;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[3];
} HHSExactPass219HHCQJointDescriptorV1;

typedef struct HHSExactPass219HHCQJointPreparedV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219HHCQResolutionSelectionV1 resolution;
    HHSExactPass219HHCQParameterCoordinateV1 coordinate;
    uint16_t anchor_parameter;
    uint16_t region_popcount;
    uint8_t touched_vm81_words;
    uint8_t touched_h36_words;
    uint8_t byte_aligned;
    uint8_t word64_aligned;
    uint8_t word36_aligned;
    uint8_t loshu_value;
    int8_t trinary_direction;
    int8_t features[HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT];
    uint64_t feature_signature64;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
} HHSExactPass219HHCQJointPreparedV1;

typedef struct HHSExactPass219HHCQJointStateV1 {
    uint32_t struct_size;
    uint32_t version;
    int16_t lane_feature_weights[HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT]
                                [HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT];
    int16_t lane_bias[HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT];
    uint32_t update_count;
    uint64_t step_count;
    uint8_t candidate_only;
    uint8_t bounded_weights;
    uint8_t fixed_size_policy_state;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[3];
} HHSExactPass219HHCQJointStateV1;

typedef struct HHSExactPass219HHCQJointDecisionV1 {
    uint32_t struct_size;
    uint32_t version;
    int64_t lane_score[HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT];
    uint8_t selected_lane;
    uint8_t feedback_lane;
    int8_t feedback_trinary;
    uint8_t updated;
    uint8_t resolution_index;
    uint16_t resolution_parameters;
    uint16_t region_index;
    uint16_t region_start;
    uint32_t update_count;
    uint64_t step_count;
    uint64_t feature_signature64;
    uint64_t decision_signature64;
    uint8_t phase5_resolution_locked;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219HHCQJointDecisionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_hhcq_joint_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_joint_descriptor(
    HHSExactPass219HHCQJointDescriptorV1 *out_descriptor);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_joint_state_init(
    HHSExactPass219HHCQJointStateV1 *out_state);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_joint_validate_state(
    const HHSExactPass219HHCQJointStateV1 *state);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_joint_prepare(
    const HHSExactVM81Frame *frame,
    uint16_t anchor_parameter,
    uint8_t x_phase72,
    uint8_t y_phase72,
    uint8_t z_phase72,
    uint8_t w_phase72,
    int8_t trinary_direction,
    HHSExactPass219HHCQJointPreparedV1 *out_prepared);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_joint_predict(
    const HHSExactPass219HHCQJointPreparedV1 *prepared,
    const HHSExactPass219HHCQJointStateV1 *state,
    HHSExactPass219HHCQJointDecisionV1 *out_decision);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_joint_step(
    const HHSExactPass219HHCQJointPreparedV1 *prepared,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219HHCQJointStateV1 *state,
    HHSExactPass219HHCQJointDecisionV1 *out_decision);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_joint_route(
    const HHSExactVM81Frame *frame,
    uint16_t anchor_parameter,
    uint8_t x_phase72,
    uint8_t y_phase72,
    uint8_t z_phase72,
    uint8_t w_phase72,
    int8_t trinary_direction,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219HHCQJointStateV1 *state,
    HHSExactPass219HHCQJointPreparedV1 *out_prepared,
    HHSExactPass219HHCQJointDecisionV1 *out_decision);

#ifdef __cplusplus
}
#endif

#endif
