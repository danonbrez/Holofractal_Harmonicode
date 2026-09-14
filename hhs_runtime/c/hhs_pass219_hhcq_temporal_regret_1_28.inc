#include "../include/hhs_pass219_hhcq_temporal_cubic_1_28.h"

#include <string.h>

static uint64_t hhs_p219_hhcq_temporal_regret_mix64(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static int16_t hhs_p219_hhcq_temporal_regret_clamp_i16(int32_t value) {
    if (value > HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND)
        return (int16_t)HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND;
    if (value < -HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND)
        return (int16_t)-HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND;
    return (int16_t)value;
}

HHSExactStatus hhs_exact_pass219_hhcq_temporal_regret_step(
    const HHSExactPass219HHCQJointPreparedV1 *prepared,
    uint8_t feedback_lane,
    uint64_t regret_margin_units,
    uint64_t regret_quantum_units,
    HHSExactPass219HHCQJointStateV1 *state,
    HHSExactPass219HHCQTemporalRegretDecisionV1 *out_decision
) {
    HHSExactStatus status;
    uint64_t bucket64;
    uint8_t selected;
    uint8_t pressure;
    uint32_t feature;
    int32_t m;
    int32_t w;
    int32_t x;
    int32_t y;
    int32_t z;
    int32_t collapse_t;
    int32_t collapse_x;
    int32_t temporal_t;

    if (prepared == NULL || state == NULL || out_decision == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (feedback_lane >= HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT ||
        regret_margin_units == 0U || regret_quantum_units == 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    status = hhs_exact_pass219_hhcq_joint_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(out_decision, 0, sizeof(*out_decision));
    out_decision->struct_size = (uint32_t)sizeof(*out_decision);
    out_decision->version = HHS_EXACT_PASS219_HHCQ_TEMPORAL_CUBIC_VERSION;
    status = hhs_exact_pass219_hhcq_joint_predict(
        prepared, state, &out_decision->base_decision);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (out_decision->base_decision.phase5_resolution_locked != 1U ||
        out_decision->base_decision.resolution_index != prepared->resolution.resolution_index ||
        out_decision->base_decision.resolution_parameters != prepared->resolution.resolution_parameters ||
        out_decision->base_decision.region_index != prepared->coordinate.region_index)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    bucket64 = UINT64_C(1) + (regret_margin_units - UINT64_C(1)) / regret_quantum_units;
    if (bucket64 > HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_PRESSURE)
        bucket64 = HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_PRESSURE;
    out_decision->margin_bucket = (uint8_t)bucket64;

    m = 2 + (int32_t)prepared->resolution.resolution_index;
    w = 1 + (int32_t)((prepared->touched_vm81_words - 1U) % 9U);
    y = (int32_t)prepared->loshu_value;
    z = 1 + (int32_t)((prepared->touched_h36_words - 1U) % 9U);
    collapse_t = 1 + (int32_t)(prepared->resolution.rotated_phase72 % 9U);
    collapse_x = (int32_t)out_decision->margin_bucket;
    status = hhs_exact_pass219_hhcq_collapse_witness(
        m, collapse_t, w, y, z, collapse_x, &out_decision->collapse);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    x = 1 + (int32_t)(prepared->anchor_parameter % 9U);
    temporal_t = (int32_t)prepared->resolution.rotated_phase72;
    status = hhs_exact_pass219_hhcq_temporal_cubic_witness(
        m, w, x, y, z, temporal_t, &out_decision->temporal);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_hhcq_temporal_z72_roots(
        m, w, x, y, z, prepared->resolution.rotated_phase72, &out_decision->roots);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    pressure = out_decision->margin_bucket;
    if (out_decision->collapse.collapse_direction != 0 &&
        out_decision->collapse.collapse_gain != 0U &&
        pressure < HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_PRESSURE)
        ++pressure;

    out_decision->temporal_alignment = 0;
    if (out_decision->roots.root_count != 0U) {
        if (out_decision->roots.preferred_direction == 0) {
            out_decision->temporal_alignment = 1;
        } else if (out_decision->temporal.temporal_direction != 0) {
            out_decision->temporal_alignment =
                out_decision->roots.preferred_direction == out_decision->temporal.temporal_direction
                    ? (int8_t)1 : (int8_t)-1;
        }
    }
    if (out_decision->temporal_alignment > 0 &&
        pressure < HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_PRESSURE)
        ++pressure;
    else if (out_decision->temporal_alignment < 0 && pressure > 1U)
        --pressure;

    out_decision->update_pressure = pressure;
    out_decision->regret_margin_units = regret_margin_units;
    out_decision->regret_quantum_units = regret_quantum_units;
    out_decision->phase5_resolution_locked = 1U;
    out_decision->inherited_policy_state_bytes =
        (uint32_t)sizeof(HHSExactPass219HHCQJointStateV1);

    selected = out_decision->base_decision.selected_lane;
    if (selected != feedback_lane) {
        for (feature = 0U; feature < HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT; ++feature) {
            const int32_t delta =
                (int32_t)pressure *
                (int32_t)HHS_EXACT_PASS219_HHCQ_JOINT_UPDATE_QUANTUM *
                (int32_t)prepared->features[feature];
            state->lane_feature_weights[feedback_lane][feature] =
                hhs_p219_hhcq_temporal_regret_clamp_i16(
                    (int32_t)state->lane_feature_weights[feedback_lane][feature] + delta);
            state->lane_feature_weights[selected][feature] =
                hhs_p219_hhcq_temporal_regret_clamp_i16(
                    (int32_t)state->lane_feature_weights[selected][feature] - delta);
        }
        state->lane_bias[feedback_lane] = hhs_p219_hhcq_temporal_regret_clamp_i16(
            (int32_t)state->lane_bias[feedback_lane] +
            (int32_t)pressure * (int32_t)HHS_EXACT_PASS219_HHCQ_JOINT_UPDATE_QUANTUM);
        state->lane_bias[selected] = hhs_p219_hhcq_temporal_regret_clamp_i16(
            (int32_t)state->lane_bias[selected] -
            (int32_t)pressure * (int32_t)HHS_EXACT_PASS219_HHCQ_JOINT_UPDATE_QUANTUM);
        ++state->update_count;
        out_decision->updated = 1U;
    }
    ++state->step_count;
    status = hhs_exact_pass219_hhcq_joint_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_decision->update_count = state->update_count;
    out_decision->step_count = state->step_count;
    out_decision->candidate_only = 1U;
    out_decision->exact_integer_only = 1U;
    out_decision->decision_signature64 = hhs_p219_hhcq_temporal_regret_mix64(
        UINT64_C(0x2197e0a1c0de0128) ^
        out_decision->base_decision.decision_signature64 ^
        out_decision->collapse.witness_signature64 ^
        out_decision->temporal.witness_signature64 ^
        out_decision->roots.root_signature64 ^
        regret_margin_units ^ (regret_quantum_units << 1U) ^
        ((uint64_t)pressure << 56U) ^
        ((uint64_t)(uint8_t)(out_decision->temporal_alignment + 1) << 48U) ^
        ((uint64_t)feedback_lane << 40U) ^
        state->step_count ^ ((uint64_t)state->update_count << 32U));
    return HHS_EXACT_STATUS_OK;
}
