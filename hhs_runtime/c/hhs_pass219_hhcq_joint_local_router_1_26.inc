#include "../include/hhs_pass219_hhcq_joint_local_router_1_26.h"

#include <string.h>

static const uint8_t HHS_P219_HHCQ_JOINT_LOSHU[9] = {
    4U, 9U, 2U,
    3U, 5U, 7U,
    8U, 1U, 6U
};

static uint64_t hhs_p219_hhcq_joint_mix64(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static uint32_t hhs_p219_hhcq_joint_popcount64(uint64_t value) {
    uint32_t count = 0U;
    while (value != 0U) {
        value &= value - UINT64_C(1);
        ++count;
    }
    return count;
}

static int16_t hhs_p219_hhcq_joint_clamp_i16(int32_t value) {
    if (value > HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND)
        return HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND;
    if (value < -HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND)
        return (int16_t)-HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND;
    return (int16_t)value;
}

static uint64_t hhs_p219_hhcq_joint_region_mask(uint32_t lo, uint32_t hi) {
    uint64_t low_mask;
    uint64_t high_mask;
    if (lo >= hi || hi > 64U)
        return UINT64_C(0);
    low_mask = lo == 0U ? UINT64_MAX : (UINT64_MAX << lo);
    high_mask = hi == 64U ? UINT64_MAX : ((UINT64_C(1) << hi) - UINT64_C(1));
    return low_mask & high_mask;
}

static int hhs_p219_hhcq_joint_prepared_valid(
    const HHSExactPass219HHCQJointPreparedV1 *prepared
) {
    HHSExactPass219HHCQParameterCoordinateV1 coordinate;
    uint32_t i;
    if (prepared == NULL ||
        prepared->struct_size != sizeof(*prepared) ||
        prepared->version != HHS_EXACT_PASS219_HHCQ_JOINT_VERSION ||
        prepared->anchor_parameter >= HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT ||
        prepared->resolution.candidate_only != 1U ||
        prepared->resolution.exact_integer_only != 1U ||
        prepared->resolution.canonical_mutation_authority != 0U ||
        prepared->resolution.canonical_hash72_authority != 0U ||
        prepared->resolution.canonical_hash216_authority != 0U ||
        prepared->resolution.canonical_persistence_authority != 0U ||
        prepared->resolution.floating_point_authority != 0U ||
        prepared->coordinate.parameter_index != prepared->anchor_parameter ||
        prepared->coordinate.resolution_parameters != prepared->resolution.resolution_parameters ||
        prepared->coordinate.region_count != prepared->resolution.region_count ||
        prepared->region_popcount > prepared->resolution.resolution_parameters ||
        prepared->touched_vm81_words == 0U ||
        prepared->touched_h36_words == 0U ||
        prepared->loshu_value < 1U || prepared->loshu_value > 9U ||
        prepared->trinary_direction < -1 || prepared->trinary_direction > 1 ||
        prepared->candidate_only != 1U ||
        prepared->exact_integer_only != 1U ||
        prepared->canonical_authority_changed != 0U ||
        prepared->floating_point_authority != 0U)
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT; ++i) {
        if (prepared->features[i] < -1 || prepared->features[i] > 1)
            return 0;
    }
    if (hhs_exact_pass219_hhcq_parameter_locate(
            &prepared->resolution, prepared->anchor_parameter, &coordinate) !=
        HHS_EXACT_STATUS_OK)
        return 0;
    return coordinate.region_index == prepared->coordinate.region_index &&
           coordinate.local_offset == prepared->coordinate.local_offset &&
           coordinate.region_start == prepared->coordinate.region_start;
}

uint32_t hhs_exact_pass219_hhcq_joint_version(void) {
    return HHS_EXACT_PASS219_HHCQ_JOINT_VERSION;
}

HHSExactStatus hhs_exact_pass219_hhcq_joint_descriptor(
    HHSExactPass219HHCQJointDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_HHCQ_JOINT_VERSION;
    out_descriptor->parameter_count = HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT;
    out_descriptor->phase_modulus = HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS;
    out_descriptor->resolution_count = HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT;
    out_descriptor->lane_count = HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT;
    out_descriptor->feature_count = HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT;
    out_descriptor->update_quantum = HHS_EXACT_PASS219_HHCQ_JOINT_UPDATE_QUANTUM;
    out_descriptor->phase5_resolution_constraint_authority = 1U;
    out_descriptor->local_lane_learning = 1U;
    out_descriptor->fixed_size_policy_state = 1U;
    out_descriptor->exact_region_features = 1U;
    out_descriptor->orthogonal_parameter_identity = 1U;
    out_descriptor->dyadic_trinary_dual_primitive = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->exact_integer_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_joint_state_init(
    HHSExactPass219HHCQJointStateV1 *out_state
) {
    uint32_t lane;
    uint32_t feature;
    if (out_state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_state, 0, sizeof(*out_state));
    out_state->struct_size = (uint32_t)sizeof(*out_state);
    out_state->version = HHS_EXACT_PASS219_HHCQ_JOINT_VERSION;
    for (lane = 0U; lane < HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT; ++lane) {
        for (feature = 0U; feature < HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT; ++feature) {
            const uint32_t seed_index = (lane * 2U + feature) % 9U;
            out_state->lane_feature_weights[lane][feature] =
                (int16_t)((int32_t)HHS_P219_HHCQ_JOINT_LOSHU[seed_index] - 5);
        }
        out_state->lane_bias[lane] =
            (int16_t)((int32_t)HHS_P219_HHCQ_JOINT_LOSHU[(lane * 2U) % 9U] - 5);
    }
    out_state->candidate_only = 1U;
    out_state->bounded_weights = 1U;
    out_state->fixed_size_policy_state = 1U;
    out_state->exact_integer_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_joint_validate_state(
    const HHSExactPass219HHCQJointStateV1 *state
) {
    uint32_t lane;
    uint32_t feature;
    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (state->struct_size != sizeof(*state) ||
        state->version != HHS_EXACT_PASS219_HHCQ_JOINT_VERSION ||
        state->candidate_only != 1U || state->bounded_weights != 1U ||
        state->fixed_size_policy_state != 1U || state->exact_integer_only != 1U ||
        state->canonical_mutation_authority != 0U ||
        state->canonical_hash72_authority != 0U ||
        state->canonical_hash216_authority != 0U ||
        state->canonical_persistence_authority != 0U ||
        state->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (lane = 0U; lane < HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT; ++lane) {
        if (state->lane_bias[lane] < -HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND ||
            state->lane_bias[lane] > HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        for (feature = 0U; feature < HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT; ++feature) {
            if (state->lane_feature_weights[lane][feature] <
                    -HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND ||
                state->lane_feature_weights[lane][feature] >
                    HHS_EXACT_PASS219_HHCQ_JOINT_WEIGHT_BOUND)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_joint_prepare(
    const HHSExactVM81Frame *frame,
    uint16_t anchor_parameter,
    uint8_t x_phase72,
    uint8_t y_phase72,
    uint8_t z_phase72,
    uint8_t w_phase72,
    int8_t trinary_direction,
    HHSExactPass219HHCQJointPreparedV1 *out_prepared
) {
    uint32_t region_start;
    uint32_t region_end;
    uint32_t first_word;
    uint32_t last_word;
    uint32_t word;
    uint32_t popcount = 0U;
    uint32_t touched64;
    uint32_t touched36;
    uint32_t resolution;
    uint64_t signature;
    HHSExactStatus status;

    if (frame == NULL || out_prepared == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if ((uint32_t)anchor_parameter >= HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_prepared, 0, sizeof(*out_prepared));
    out_prepared->struct_size = (uint32_t)sizeof(*out_prepared);
    out_prepared->version = HHS_EXACT_PASS219_HHCQ_JOINT_VERSION;
    status = hhs_exact_pass219_hhcq_resolution_select(
        x_phase72, y_phase72, z_phase72, w_phase72, trinary_direction,
        &out_prepared->resolution);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_hhcq_parameter_locate(
        &out_prepared->resolution, anchor_parameter, &out_prepared->coordinate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_prepared->anchor_parameter = anchor_parameter;
    region_start = out_prepared->coordinate.region_start;
    resolution = out_prepared->resolution.resolution_parameters;
    region_end = region_start + resolution;
    if (region_end > HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT || resolution == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    first_word = region_start / HHS_EXACT_VM81_WORD_BITS;
    last_word = (region_end - 1U) / HHS_EXACT_VM81_WORD_BITS;
    touched64 = last_word - first_word + 1U;
    for (word = first_word; word <= last_word; ++word) {
        const uint32_t word_start = word * HHS_EXACT_VM81_WORD_BITS;
        const uint32_t lo = region_start > word_start ? region_start - word_start : 0U;
        const uint32_t capped_end = region_end < word_start + HHS_EXACT_VM81_WORD_BITS
            ? region_end : word_start + HHS_EXACT_VM81_WORD_BITS;
        const uint32_t hi = capped_end - word_start;
        const uint64_t mask = hhs_p219_hhcq_joint_region_mask(lo, hi);
        popcount += hhs_p219_hhcq_joint_popcount64(frame->words[word] & mask);
    }
    touched36 = ((region_end + 35U) / 36U) - (region_start / 36U);
    if (touched64 > UINT8_MAX || touched36 > UINT8_MAX || popcount > UINT16_MAX)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_prepared->region_popcount = (uint16_t)popcount;
    out_prepared->touched_vm81_words = (uint8_t)touched64;
    out_prepared->touched_h36_words = (uint8_t)touched36;
    out_prepared->byte_aligned =
        (uint8_t)((region_start % 8U) == 0U && (resolution % 8U) == 0U);
    out_prepared->word64_aligned =
        (uint8_t)((region_start % 64U) == 0U && (resolution % 64U) == 0U);
    out_prepared->word36_aligned =
        (uint8_t)((region_start % 36U) == 0U && (resolution % 36U) == 0U);
    out_prepared->loshu_value = HHS_P219_HHCQ_JOINT_LOSHU[
        ((uint32_t)out_prepared->coordinate.region_index +
         (uint32_t)out_prepared->resolution.rotated_phase72) % 9U];
    out_prepared->trinary_direction = trinary_direction;

    out_prepared->features[0] = trinary_direction;
    out_prepared->features[1] =
        popcount * 2U < resolution ? (int8_t)-1 :
        (popcount * 2U > resolution ? (int8_t)1 : (int8_t)0);
    out_prepared->features[2] = out_prepared->byte_aligned != 0U ? (int8_t)1 : (int8_t)-1;
    out_prepared->features[3] = out_prepared->word64_aligned != 0U ? (int8_t)1 : (int8_t)-1;
    out_prepared->features[4] = out_prepared->word36_aligned != 0U ? (int8_t)1 : (int8_t)-1;
    out_prepared->features[5] = (int8_t)((int32_t)(out_prepared->loshu_value % 3U) - 1);
    out_prepared->features[6] =
        (int8_t)((int32_t)(out_prepared->resolution.rotated_phase72 % 3U) - 1);
    out_prepared->features[7] =
        (int8_t)((int32_t)(out_prepared->coordinate.region_index % 3U) - 1);

    signature = UINT64_C(0x2195184072010126) ^
        out_prepared->resolution.selection_signature64 ^
        ((uint64_t)anchor_parameter << 48U) ^
        ((uint64_t)out_prepared->coordinate.region_index << 32U) ^
        ((uint64_t)out_prepared->region_popcount << 16U) ^
        ((uint64_t)out_prepared->touched_vm81_words << 8U) ^
        (uint64_t)out_prepared->touched_h36_words;
    for (word = 0U; word < HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT; ++word) {
        signature = hhs_p219_hhcq_joint_mix64(
            signature ^ ((uint64_t)(uint8_t)(out_prepared->features[word] + 1) <<
                         ((word & 7U) * 8U)));
    }
    out_prepared->feature_signature64 = signature;
    out_prepared->candidate_only = 1U;
    out_prepared->exact_integer_only = 1U;

    return hhs_p219_hhcq_joint_prepared_valid(out_prepared)
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_hhcq_joint_predict(
    const HHSExactPass219HHCQJointPreparedV1 *prepared,
    const HHSExactPass219HHCQJointStateV1 *state,
    HHSExactPass219HHCQJointDecisionV1 *out_decision
) {
    uint32_t lane;
    uint32_t feature;
    uint8_t selected = 0U;
    uint64_t signature;
    HHSExactStatus status;
    if (prepared == NULL || state == NULL || out_decision == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_p219_hhcq_joint_prepared_valid(prepared))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_exact_pass219_hhcq_joint_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(out_decision, 0, sizeof(*out_decision));
    out_decision->struct_size = (uint32_t)sizeof(*out_decision);
    out_decision->version = HHS_EXACT_PASS219_HHCQ_JOINT_VERSION;
    for (lane = 0U; lane < HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT; ++lane) {
        int64_t score = state->lane_bias[lane];
        for (feature = 0U; feature < HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT; ++feature) {
            score += (int64_t)state->lane_feature_weights[lane][feature] *
                (int64_t)prepared->features[feature];
        }
        out_decision->lane_score[lane] = score;
        if (lane != 0U && score > out_decision->lane_score[selected])
            selected = (uint8_t)lane;
    }
    out_decision->selected_lane = selected;
    out_decision->feedback_lane = HHS_EXACT_PASS219_HHCQ_JOINT_FEEDBACK_NONE;
    out_decision->resolution_index = prepared->resolution.resolution_index;
    out_decision->resolution_parameters = prepared->resolution.resolution_parameters;
    out_decision->region_index = prepared->coordinate.region_index;
    out_decision->region_start = prepared->coordinate.region_start;
    out_decision->update_count = state->update_count;
    out_decision->step_count = state->step_count;
    out_decision->feature_signature64 = prepared->feature_signature64;
    signature = UINT64_C(0x219a6714c0de0126) ^ prepared->feature_signature64 ^
        ((uint64_t)selected << 56U) ^
        ((uint64_t)out_decision->resolution_index << 48U) ^
        ((uint64_t)out_decision->resolution_parameters << 24U) ^ state->step_count;
    for (lane = 0U; lane < HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT; ++lane)
        signature = hhs_p219_hhcq_joint_mix64(signature ^ (uint64_t)out_decision->lane_score[lane]);
    out_decision->decision_signature64 = signature;
    out_decision->phase5_resolution_locked = 1U;
    out_decision->candidate_only = 1U;
    out_decision->exact_integer_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_joint_step(
    const HHSExactPass219HHCQJointPreparedV1 *prepared,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219HHCQJointStateV1 *state,
    HHSExactPass219HHCQJointDecisionV1 *out_decision
) {
    uint32_t feature;
    HHSExactStatus status;
    if (prepared == NULL || state == NULL || out_decision == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (feedback_lane == HHS_EXACT_PASS219_HHCQ_JOINT_FEEDBACK_NONE) {
        if (feedback_trinary != 0)
            return HHS_EXACT_STATUS_RANGE_ERROR;
    } else if (feedback_lane >= HHS_EXACT_PASS219_HHCQ_JOINT_LANE_COUNT ||
               feedback_trinary < -1 || feedback_trinary > 1) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    status = hhs_exact_pass219_hhcq_joint_predict(prepared, state, out_decision);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_decision->feedback_lane = feedback_lane;
    out_decision->feedback_trinary = feedback_trinary;
    if (feedback_lane != HHS_EXACT_PASS219_HHCQ_JOINT_FEEDBACK_NONE &&
        feedback_trinary != 0 && out_decision->selected_lane != feedback_lane) {
        const uint8_t selected = out_decision->selected_lane;
        for (feature = 0U; feature < HHS_EXACT_PASS219_HHCQ_JOINT_FEATURE_COUNT; ++feature) {
            const int32_t delta =
                (int32_t)feedback_trinary *
                (int32_t)HHS_EXACT_PASS219_HHCQ_JOINT_UPDATE_QUANTUM *
                (int32_t)prepared->features[feature];
            state->lane_feature_weights[feedback_lane][feature] =
                hhs_p219_hhcq_joint_clamp_i16(
                    (int32_t)state->lane_feature_weights[feedback_lane][feature] + delta);
            state->lane_feature_weights[selected][feature] =
                hhs_p219_hhcq_joint_clamp_i16(
                    (int32_t)state->lane_feature_weights[selected][feature] - delta);
        }
        state->lane_bias[feedback_lane] = hhs_p219_hhcq_joint_clamp_i16(
            (int32_t)state->lane_bias[feedback_lane] +
            (int32_t)feedback_trinary * (int32_t)HHS_EXACT_PASS219_HHCQ_JOINT_UPDATE_QUANTUM);
        state->lane_bias[selected] = hhs_p219_hhcq_joint_clamp_i16(
            (int32_t)state->lane_bias[selected] -
            (int32_t)feedback_trinary * (int32_t)HHS_EXACT_PASS219_HHCQ_JOINT_UPDATE_QUANTUM);
        ++state->update_count;
        out_decision->updated = 1U;
    }
    ++state->step_count;
    out_decision->update_count = state->update_count;
    out_decision->step_count = state->step_count;
    status = hhs_exact_pass219_hhcq_joint_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    out_decision->decision_signature64 = hhs_p219_hhcq_joint_mix64(
        out_decision->decision_signature64 ^ state->step_count ^
        ((uint64_t)state->update_count << 32U) ^
        ((uint64_t)feedback_lane << 16U) ^ (uint64_t)(uint8_t)(feedback_trinary + 1));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_joint_route(
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
    HHSExactPass219HHCQJointDecisionV1 *out_decision
) {
    HHSExactStatus status;
    if (frame == NULL || state == NULL || out_prepared == NULL || out_decision == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_hhcq_joint_prepare(
        frame, anchor_parameter, x_phase72, y_phase72, z_phase72, w_phase72,
        trinary_direction, out_prepared);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_exact_pass219_hhcq_joint_step(
        out_prepared, feedback_lane, feedback_trinary, state, out_decision);
}
