#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static HHSExactVM81Frame make_frame(void) {
    HHSExactVM81Frame frame;
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        frame.words[i] =
            UINT64_C(0x9e3779b97f4a7c15) * (uint64_t)(i + 1U) ^
            (UINT64_C(0x0101010101010101) * (uint64_t)(i % 9U));
    }
    return frame;
}

static void assert_clean_decision(const HHSExactPass219HHCQJointDecisionV1 *decision) {
    assert(decision->phase5_resolution_locked == 1U);
    assert(decision->candidate_only == 1U);
    assert(decision->exact_integer_only == 1U);
    assert(decision->canonical_mutation_authority == 0U);
    assert(decision->canonical_hash72_authority == 0U);
    assert(decision->canonical_hash216_authority == 0U);
    assert(decision->canonical_persistence_authority == 0U);
    assert(decision->floating_point_authority == 0U);
    assert(decision->selected_lane < HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT);
}

int main(void) {
    HHSExactPass219HHCQJointDescriptorV1 descriptor;
    HHSExactPass219HHCQJointStateV1 initial;
    HHSExactPass219HHCQJointStateV1 replay_state;
    HHSExactPass219HHCQJointPreparedV1 prepared;
    HHSExactPass219HHCQJointPreparedV1 replay_prepared;
    HHSExactPass219HHCQJointDecisionV1 decision;
    HHSExactPass219HHCQJointDecisionV1 replay_decision;
    HHSExactPass219HHCQJointDecisionV1 trained_decision;
    HHSExactPass219HHCQJointStateV1 trained;
    HHSExactPass219HHCQJointStateV1 invalid;
    HHSExactVM81Frame frame = make_frame();
    HHSExactVM81Frame frozen = frame;
    uint8_t feedback_lane;
    uint8_t observed_resolution[HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT];
    uint32_t anchor;
    uint32_t resolution_seen = 0U;

    memset(observed_resolution, 0, sizeof(observed_resolution));

    assert(hhs_exact_pass219_hhcq_joint_version() == HHS_EXACT_PASS219_HHCQ_JOINT_VERSION);
    assert(hhs_exact_pass219_hhcq_joint_descriptor(&descriptor) == HHS_EXACT_STATUS_OK);
    assert(descriptor.parameter_count == HHS_EXACT_VM81_FRAME_BITS);
    assert(descriptor.phase_modulus == HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS);
    assert(descriptor.resolution_count == HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT);
    assert(descriptor.lane_count == HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
    assert(descriptor.feature_count == HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT);
    assert(descriptor.update_quantum == HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM);
    assert(descriptor.phase5_resolution_constraint_authority == 1U);
    assert(descriptor.local_lane_learning == 1U);
    assert(descriptor.fixed_size_policy_state == 1U);
    assert(descriptor.exact_region_features == 1U);
    assert(descriptor.orthogonal_parameter_identity == 1U);
    assert(descriptor.dyadic_trinary_dual_primitive == 1U);
    assert(descriptor.candidate_only == 1U);
    assert(descriptor.exact_integer_only == 1U);
    assert(descriptor.canonical_mutation_authority == 0U);
    assert(descriptor.canonical_hash72_authority == 0U);
    assert(descriptor.canonical_hash216_authority == 0U);
    assert(descriptor.canonical_persistence_authority == 0U);
    assert(descriptor.floating_point_authority == 0U);

    assert(hhs_exact_pass219_hhcq_joint_state_init(&initial) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_hhcq_joint_validate_state(&initial) == HHS_EXACT_STATUS_OK);
    assert(initial.fixed_size_policy_state == 1U);
    assert(initial.step_count == 0U && initial.update_count == 0U);

    assert(hhs_exact_pass219_hhcq_joint_prepare(
        &frame, UINT16_C(257), 4U, 9U, 2U, 3U, 1, &prepared) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&frame, &frozen, sizeof(frame)) == 0);
    assert(prepared.anchor_parameter == UINT16_C(257));
    assert(prepared.coordinate.parameter_index == prepared.anchor_parameter);
    assert((uint32_t)prepared.coordinate.region_start + prepared.coordinate.local_offset ==
           prepared.anchor_parameter);
    assert(prepared.coordinate.resolution_parameters == prepared.resolution.resolution_parameters);
    assert(prepared.resolution.candidate_only == 1U);
    assert(prepared.candidate_only == 1U);
    assert(prepared.canonical_authority_changed == 0U);
    assert(prepared.floating_point_authority == 0U);
    assert(prepared.region_popcount <= prepared.resolution.resolution_parameters);
    assert(prepared.touched_vm81_words > 0U);
    assert(prepared.touched_h36_words > 0U);

    assert(hhs_exact_pass219_hhcq_joint_predict(&prepared, &initial, &decision) ==
           HHS_EXACT_STATUS_OK);
    assert_clean_decision(&decision);
    assert(decision.resolution_index == prepared.resolution.resolution_index);
    assert(decision.resolution_parameters == prepared.resolution.resolution_parameters);
    assert(decision.region_index == prepared.coordinate.region_index);
    assert(decision.region_start == prepared.coordinate.region_start);
    assert(decision.step_count == 0U && decision.update_count == 0U);

    replay_state = initial;
    assert(hhs_exact_pass219_hhcq_joint_prepare(
        &frame, UINT16_C(257), 4U, 9U, 2U, 3U, 1, &replay_prepared) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&prepared, &replay_prepared, sizeof(prepared)) == 0);
    assert(hhs_exact_pass219_hhcq_joint_predict(&replay_prepared, &replay_state, &replay_decision) ==
           HHS_EXACT_STATUS_OK);
    assert(memcmp(&decision, &replay_decision, sizeof(decision)) == 0);

    feedback_lane = (uint8_t)((decision.selected_lane + 1U) %
                              HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT);
    trained = initial;
    assert(hhs_exact_pass219_hhcq_joint_step(
        &prepared, feedback_lane, 1, &trained, &trained_decision) == HHS_EXACT_STATUS_OK);
    assert_clean_decision(&trained_decision);
    assert(trained_decision.selected_lane == decision.selected_lane);
    assert(trained_decision.feedback_lane == feedback_lane);
    assert(trained_decision.updated == 1U);
    assert(trained.step_count == 1U && trained.update_count == 1U);
    assert(trained_decision.resolution_index == decision.resolution_index);
    assert(trained_decision.resolution_parameters == decision.resolution_parameters);
    assert(hhs_exact_pass219_hhcq_joint_validate_state(&trained) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&frame, &frozen, sizeof(frame)) == 0);

    assert(hhs_exact_pass219_hhcq_joint_step(
        &prepared, HHS_EXACT_PASS219_HHCQ_JOINT_FEEDBACK_NONE, 1,
        &trained, &trained_decision) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(hhs_exact_pass219_hhcq_joint_step(
        &prepared, HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT, 1,
        &trained, &trained_decision) == HHS_EXACT_STATUS_RANGE_ERROR);

    invalid = initial;
    invalid.canonical_hash72_authority = 1U;
    assert(hhs_exact_pass219_hhcq_joint_validate_state(&invalid) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    invalid = initial;
    invalid.lane_feature_weights[0][0] =
        (int16_t)(HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND + 1);
    assert(hhs_exact_pass219_hhcq_joint_validate_state(&invalid) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    for (anchor = 0U; anchor < HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT; anchor += 37U) {
        const uint8_t x = (uint8_t)(anchor % HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS);
        const uint8_t y = (uint8_t)((anchor * 5U + 9U) % HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS);
        const uint8_t z = (uint8_t)((anchor * 7U + 2U) % HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS);
        const uint8_t w = (uint8_t)((anchor * 11U + 3U) % HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS);
        const int8_t tri = (int8_t)((int32_t)(anchor % 3U) - 1);
        assert(hhs_exact_pass219_hhcq_joint_prepare(
            &frame, (uint16_t)anchor, x, y, z, w, tri, &prepared) == HHS_EXACT_STATUS_OK);
        assert(prepared.resolution.resolution_index < HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT);
        observed_resolution[prepared.resolution.resolution_index] = 1U;
        assert((uint32_t)prepared.coordinate.region_start + prepared.coordinate.local_offset ==
               anchor);
    }
    for (anchor = 0U; anchor < HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT; ++anchor)
        resolution_seen += observed_resolution[anchor] != 0U ? 1U : 0U;
    assert(resolution_seen > 1U);
    assert(memcmp(&frame, &frozen, sizeof(frame)) == 0);

    return 0;
}
