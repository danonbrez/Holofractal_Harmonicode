#include "../include/hhs_pass219_hhcq_collapse_regret_1_27.h"

#include <string.h>

static uint64_t hhs_p219_hhcq_collapse_mix64(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static uint64_t hhs_p219_hhcq_collapse_abs64(int64_t value) {
    return value < 0 ? (uint64_t)(-(value + 1)) + UINT64_C(1) : (uint64_t)value;
}

static int16_t hhs_p219_hhcq_collapse_clamp_i16(int32_t value) {
    if (value > HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND)
        return (int16_t)HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND;
    if (value < -HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND)
        return (int16_t)-HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND;
    return (int16_t)value;
}

static int64_t hhs_p219_hhcq_collapse_residual(
    int64_t d,
    int64_t a,
    int64_t c,
    int32_t x
) {
    return d * (int64_t)x * (int64_t)x - a * (int64_t)x + c;
}

uint32_t hhs_exact_pass219_hhcq_collapse_regret_version(void) {
    return HHS_EXACT_PASS219_HHCQ_COLLAPSE_REGRET_VERSION;
}

HHSExactStatus hhs_exact_pass219_hhcq_collapse_regret_descriptor(
    HHSExactPass219HHCQCollapseRegretDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_HHCQ_COLLAPSE_REGRET_VERSION;
    out_descriptor->inherited_policy_state_bytes =
        (uint32_t)sizeof(HHSExactPass219HHCQJointStateV1);
    out_descriptor->max_pressure = HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_PRESSURE;
    out_descriptor->exact_quadratic_collapse = 1U;
    out_descriptor->radical_eliminated_from_canonical_path = 1U;
    out_descriptor->discrete_neighbor_direction = 1U;
    out_descriptor->training_only_regret_scale = 1U;
    out_descriptor->phase5_resolution_locked = 1U;
    out_descriptor->fixed_size_policy_state = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->exact_integer_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_collapse_witness(
    int32_t m,
    int32_t t,
    int32_t w,
    int32_t y,
    int32_t z,
    int32_t x,
    HHSExactPass219HHCQCollapseWitnessV1 *out_witness
) {
    int64_t mm1;
    int64_t tt;
    uint64_t abs_minus;
    uint64_t abs_zero;
    uint64_t abs_plus;
    uint64_t best;
    uint64_t signature;

    if (out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = HHS_EXACT_PASS219_HHCQ_COLLAPSE_REGRET_VERSION;
    out_witness->m = m;
    out_witness->t = t;
    out_witness->w = w;
    out_witness->y = y;
    out_witness->z = z;
    out_witness->x = x;
    out_witness->exact_integer_only = 1U;
    out_witness->candidate_only = 1U;

    if (m < 1 || m > (int32_t)HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_M ||
        t < 0 || t > (int32_t)HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_T ||
        w < 1 || w > (int32_t)HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_ROOT ||
        y < 1 || y > (int32_t)HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_ROOT ||
        z < 1 || z > (int32_t)HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_ROOT ||
        x < 1 || x > (int32_t)HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_X)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    mm1 = (int64_t)m * (int64_t)(m - 1);
    tt = (int64_t)t * ((int64_t)t * (int64_t)t - INT64_C(1));
    out_witness->coefficient_d =
        -mm1 * (int64_t)w * (int64_t)y * (int64_t)z -
        tt * (int64_t)y * (int64_t)y;
    out_witness->coefficient_a =
        mm1 * (int64_t)w * (int64_t)y * (int64_t)z *
        ((int64_t)w + (int64_t)y + (int64_t)z);
    out_witness->coefficient_c =
        mm1 * (int64_t)w * (int64_t)w * (int64_t)z * (int64_t)z;

    if (out_witness->coefficient_d == 0) {
        out_witness->singular = 1U;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_witness->residual_minus = hhs_p219_hhcq_collapse_residual(
        out_witness->coefficient_d, out_witness->coefficient_a,
        out_witness->coefficient_c, x - 1);
    out_witness->residual_zero = hhs_p219_hhcq_collapse_residual(
        out_witness->coefficient_d, out_witness->coefficient_a,
        out_witness->coefficient_c, x);
    out_witness->residual_plus = hhs_p219_hhcq_collapse_residual(
        out_witness->coefficient_d, out_witness->coefficient_a,
        out_witness->coefficient_c, x + 1);

    abs_minus = hhs_p219_hhcq_collapse_abs64(out_witness->residual_minus);
    abs_zero = hhs_p219_hhcq_collapse_abs64(out_witness->residual_zero);
    abs_plus = hhs_p219_hhcq_collapse_abs64(out_witness->residual_plus);
    out_witness->absolute_residual_zero = abs_zero;
    best = abs_zero;
    out_witness->collapse_direction = 0;
    if (abs_minus < best) {
        best = abs_minus;
        out_witness->collapse_direction = -1;
    }
    if (abs_plus < best) {
        best = abs_plus;
        out_witness->collapse_direction = 1;
    }
    out_witness->collapse_gain = abs_zero - best;

    signature = UINT64_C(0x219c011a95e00127) ^
        ((uint64_t)(uint32_t)m << 56U) ^
        ((uint64_t)(uint32_t)t << 48U) ^
        ((uint64_t)(uint32_t)w << 40U) ^
        ((uint64_t)(uint32_t)y << 32U) ^
        ((uint64_t)(uint32_t)z << 24U) ^
        ((uint64_t)(uint32_t)x << 16U) ^
        (uint64_t)(uint8_t)(out_witness->collapse_direction + 1);
    signature = hhs_p219_hhcq_collapse_mix64(
        signature ^ (uint64_t)out_witness->coefficient_d ^
        (uint64_t)out_witness->coefficient_a ^
        (uint64_t)out_witness->coefficient_c);
    signature = hhs_p219_hhcq_collapse_mix64(
        signature ^ (uint64_t)out_witness->residual_zero ^ out_witness->collapse_gain);
    out_witness->witness_signature64 = signature;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_collapse_regret_step(
    const HHSExactPass219HHCQJointPreparedV1 *prepared,
    uint8_t feedback_lane,
    uint64_t regret_margin_units,
    uint64_t regret_quantum_units,
    HHSExactPass219HHCQJointStateV1 *state,
    HHSExactPass219HHCQCollapseRegretDecisionV1 *out_decision
) {
    HHSExactStatus status;
    uint64_t bucket64;
    uint8_t selected;
    uint8_t pressure;
    uint32_t feature;
    int32_t m;
    int32_t t;
    int32_t w;
    int32_t y;
    int32_t z;
    int32_t x;

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
    out_decision->version = HHS_EXACT_PASS219_HHCQ_COLLAPSE_REGRET_VERSION;
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
    t = 1 + (int32_t)(prepared->resolution.rotated_phase72 % 9U);
    w = 1 + (int32_t)((prepared->touched_vm81_words - 1U) % 9U);
    y = (int32_t)prepared->loshu_value;
    z = 1 + (int32_t)((prepared->touched_h36_words - 1U) % 9U);
    x = (int32_t)out_decision->margin_bucket;
    status = hhs_exact_pass219_hhcq_collapse_witness(
        m, t, w, y, z, x, &out_decision->collapse);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    pressure = out_decision->margin_bucket;
    if (out_decision->collapse.collapse_direction != 0 &&
        out_decision->collapse.collapse_gain != 0U &&
        pressure < HHS_EXACT_PASS219_HHCQ_COLLAPSE_MAX_PRESSURE)
        ++pressure;
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
                hhs_p219_hhcq_collapse_clamp_i16(
                    (int32_t)state->lane_feature_weights[feedback_lane][feature] + delta);
            state->lane_feature_weights[selected][feature] =
                hhs_p219_hhcq_collapse_clamp_i16(
                    (int32_t)state->lane_feature_weights[selected][feature] - delta);
        }
        state->lane_bias[feedback_lane] = hhs_p219_hhcq_collapse_clamp_i16(
            (int32_t)state->lane_bias[feedback_lane] +
            (int32_t)pressure * (int32_t)HHS_EXACT_PASS219_HHCQ_JOINT_UPDATE_QUANTUM);
        state->lane_bias[selected] = hhs_p219_hhcq_collapse_clamp_i16(
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
    out_decision->decision_signature64 = hhs_p219_hhcq_collapse_mix64(
        UINT64_C(0x219c0575e7010127) ^
        out_decision->base_decision.decision_signature64 ^
        out_decision->collapse.witness_signature64 ^
        regret_margin_units ^ (regret_quantum_units << 1U) ^
        ((uint64_t)pressure << 56U) ^
        ((uint64_t)feedback_lane << 48U) ^
        state->step_count ^ ((uint64_t)state->update_count << 32U));

    return HHS_EXACT_STATUS_OK;
}
