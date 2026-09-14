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

static uint64_t abs64(int64_t value) {
    return value < 0 ? (uint64_t)(-(value + 1)) + UINT64_C(1) : (uint64_t)value;
}

static int64_t residual(int64_t d, int64_t a, int64_t c, int32_t x) {
    return d * (int64_t)x * (int64_t)x - a * (int64_t)x + c;
}

int main(void) {
    HHSExactPass219HHCQCollapseRegretDescriptorV1 descriptor;
    HHSExactPass219HHCQCollapseWitnessV1 witness;
    HHSExactPass219HHCQCollapseWitnessV1 singular;
    HHSExactPass219HHCQJointStateV1 initial;
    HHSExactPass219HHCQJointStateV1 trained_a;
    HHSExactPass219HHCQJointStateV1 trained_b;
    HHSExactPass219HHCQJointPreparedV1 prepared;
    HHSExactPass219HHCQJointDecisionV1 pre;
    HHSExactPass219HHCQCollapseRegretDecisionV1 decision_a;
    HHSExactPass219HHCQCollapseRegretDecisionV1 decision_b;
    HHSExactVM81Frame frame = make_frame();
    HHSExactVM81Frame frozen = frame;
    int32_t m = 7;
    int32_t t = 4;
    int32_t w = 3;
    int32_t y = 5;
    int32_t z = 2;
    int32_t x = 6;
    int64_t mm1;
    int64_t tt;
    int64_t d;
    int64_t a;
    int64_t c;
    uint64_t best;
    int8_t expected_direction = 0;
    uint8_t feedback_lane;

    assert(hhs_exact_pass219_hhcq_collapse_regret_version() ==
           HHS_EXACT_PASS219_HHCQ_COLLAPSE_REGRET_VERSION);
    assert(hhs_exact_pass219_hhcq_collapse_regret_descriptor(&descriptor) ==
           HHS_EXACT_STATUS_OK);
    assert(descriptor.inherited_policy_state_bytes == sizeof(HHSExactPass219HHCQJointStateV1));
    assert(descriptor.inherited_policy_state_bytes == 112U);
    assert(descriptor.max_pressure == 9U);
    assert(descriptor.exact_quadratic_collapse == 1U);
    assert(descriptor.radical_eliminated_from_canonical_path == 1U);
    assert(descriptor.discrete_neighbor_direction == 1U);
    assert(descriptor.training_only_regret_scale == 1U);
    assert(descriptor.phase5_resolution_locked == 1U);
    assert(descriptor.fixed_size_policy_state == 1U);
    assert(descriptor.candidate_only == 1U);
    assert(descriptor.exact_integer_only == 1U);
    assert(descriptor.canonical_mutation_authority == 0U);
    assert(descriptor.canonical_hash72_authority == 0U);
    assert(descriptor.canonical_hash216_authority == 0U);
    assert(descriptor.canonical_persistence_authority == 0U);
    assert(descriptor.floating_point_authority == 0U);

    assert(hhs_exact_pass219_hhcq_collapse_witness(m, t, w, y, z, x, &witness) ==
           HHS_EXACT_STATUS_OK);
    mm1 = (int64_t)m * (int64_t)(m - 1);
    tt = (int64_t)t * ((int64_t)t * (int64_t)t - INT64_C(1));
    d = -mm1 * w * y * z - tt * y * y;
    a = mm1 * w * y * z * (w + y + z);
    c = mm1 * w * w * z * z;
    assert(witness.coefficient_d == d);
    assert(witness.coefficient_a == a);
    assert(witness.coefficient_c == c);
    assert(witness.residual_minus == residual(d, a, c, x - 1));
    assert(witness.residual_zero == residual(d, a, c, x));
    assert(witness.residual_plus == residual(d, a, c, x + 1));
    assert(witness.absolute_residual_zero == abs64(witness.residual_zero));
    best = witness.absolute_residual_zero;
    if (abs64(witness.residual_minus) < best) {
        best = abs64(witness.residual_minus);
        expected_direction = -1;
    }
    if (abs64(witness.residual_plus) < best) {
        best = abs64(witness.residual_plus);
        expected_direction = 1;
    }
    assert(witness.collapse_direction == expected_direction);
    assert(witness.collapse_gain == witness.absolute_residual_zero - best);
    assert(witness.singular == 0U);
    assert(witness.exact_integer_only == 1U);
    assert(witness.candidate_only == 1U);
    assert(witness.floating_point_authority == 0U);

    memset(&singular, 0, sizeof(singular));
    assert(hhs_exact_pass219_hhcq_collapse_witness(1, 1, 1, 1, 1, 1, &singular) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(singular.singular == 1U);
    assert(hhs_exact_pass219_hhcq_collapse_witness(37, 1, 1, 1, 1, 1, &witness) ==
           HHS_EXACT_STATUS_RANGE_ERROR);

    assert(hhs_exact_pass219_hhcq_joint_state_init(&initial) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_hhcq_joint_prepare(
        &frame, UINT16_C(257), 4U, 9U, 2U, 3U, 1, &prepared) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_hhcq_joint_predict(&prepared, &initial, &pre) ==
           HHS_EXACT_STATUS_OK);
    feedback_lane = (uint8_t)((pre.selected_lane + 1U) % HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT);

    trained_a = initial;
    trained_b = initial;
    assert(hhs_exact_pass219_hhcq_collapse_regret_step(
        &prepared, feedback_lane, UINT64_C(100), UINT64_C(25),
        &trained_a, &decision_a) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_hhcq_collapse_regret_step(
        &prepared, feedback_lane, UINT64_C(100), UINT64_C(25),
        &trained_b, &decision_b) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&trained_a, &trained_b, sizeof(trained_a)) == 0);
    assert(memcmp(&decision_a, &decision_b, sizeof(decision_a)) == 0);
    assert(decision_a.base_decision.selected_lane == pre.selected_lane);
    assert(decision_a.margin_bucket == 4U);
    assert(decision_a.update_pressure >= decision_a.margin_bucket);
    assert(decision_a.update_pressure <= 5U);
    assert(decision_a.updated == 1U);
    assert(decision_a.phase5_resolution_locked == 1U);
    assert(decision_a.base_decision.resolution_index == prepared.resolution.resolution_index);
    assert(decision_a.base_decision.resolution_parameters == prepared.resolution.resolution_parameters);
    assert(decision_a.inherited_policy_state_bytes == sizeof(HHSExactPass219HHCQJointStateV1));
    assert(decision_a.candidate_only == 1U);
    assert(decision_a.exact_integer_only == 1U);
    assert(decision_a.canonical_authority_changed == 0U);
    assert(decision_a.floating_point_authority == 0U);
    assert(trained_a.step_count == 1U);
    assert(trained_a.update_count == 1U);
    assert(hhs_exact_pass219_hhcq_joint_validate_state(&trained_a) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&frame, &frozen, sizeof(frame)) == 0);

    assert(hhs_exact_pass219_hhcq_collapse_regret_step(
        &prepared, feedback_lane, 0U, 25U, &trained_a, &decision_a) ==
           HHS_EXACT_STATUS_RANGE_ERROR);
    assert(hhs_exact_pass219_hhcq_collapse_regret_step(
        &prepared, feedback_lane, 100U, 0U, &trained_a, &decision_a) ==
           HHS_EXACT_STATUS_RANGE_ERROR);
    assert(hhs_exact_pass219_hhcq_collapse_regret_step(
        &prepared, HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT, 100U, 25U,
        &trained_a, &decision_a) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(memcmp(&frame, &frozen, sizeof(frame)) == 0);

    return 0;
}
