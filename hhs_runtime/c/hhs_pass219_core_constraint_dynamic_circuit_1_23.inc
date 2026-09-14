#include "../include/hhs_pass219_core_constraint_dynamic_circuit_1_23.h"

#include <limits.h>
#include <string.h>

static const char HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE[] =
    "P^2/{(t^3-t=(P\302\263-P/(P\302\262-pq)=(t\302\263-t)/\342\210\206=P\302\262(MOD)(pq))=m^2-m)-(({{b^"
    "4,c^4,c^2-u^(b\342\201\266c\342\201\264)},{c^2,((b^2)*(c^2)-(a^2))/u^((s==(b^(2c^2)c^b^4)^2)/((b\342"
    "\201\266c\342\201\264)P^2)),((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt("
    "c^4)))},{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,((b\342\201\266c\342\201\264)*(pq+xy)))/Bt==AB/P"
    "^2==Sqrt[AB])==(AB/(pq+\342\210\206)-P^2)/(t^3-t)*u^72} where \342\210\206/P=\342\210\232(pq+u\342"
    "\201\267\302\262)^x\302\262\n\na\302\262=(NcalcMatrixPower((List(List(x,w,(y*x)),List((w*z),x+y+z+w,"
    "(z*w)),List((x*y),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),List(I^4,I,I^3))),4))^b\342\201\264";

static const uint8_t HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE_SHA256[
    HHS_EXACT_PASS219_CORE_CIRCUIT_SHA256_BYTES
] = {
    0xeeU, 0x76U, 0xa9U, 0x02U, 0x27U, 0x2fU, 0xd4U, 0x1bU,
    0x44U, 0x25U, 0x84U, 0x68U, 0x33U, 0x5fU, 0xf4U, 0x0eU,
    0x60U, 0xc5U, 0x88U, 0x05U, 0xfaU, 0x06U, 0xecU, 0x5eU,
    0x85U, 0x78U, 0x88U, 0x47U, 0xd6U, 0x00U, 0x73U, 0xd0U
};

_Static_assert(sizeof(HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE) - 1U ==
               HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE_BYTES,
               "core circuit verbatim source byte length drift");

static uint32_t hhs_p219_core_popcount64(uint64_t value) {
    uint32_t count = 0U;
    while (value != 0U) {
        value &= value - UINT64_C(1);
        ++count;
    }
    return count;
}

static uint64_t hhs_p219_core_rotl64(uint64_t value, uint32_t shift) {
    shift &= 63U;
    if (shift == 0U)
        return value;
    return (value << shift) | (value >> (64U - shift));
}

static uint64_t hhs_p219_core_mix64(uint64_t x) {
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30U)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27U)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31U);
}

static int32_t hhs_p219_core_clamp_weight(int64_t value) {
    if (value > HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_BOUND)
        return HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_BOUND;
    if (value < -HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_BOUND)
        return -HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_BOUND;
    return (int32_t)value;
}

static int hhs_p219_core_features_valid(
    const HHSExactPass219CoreCircuitFeaturesV1 *features
) {
    uint32_t phase_total = 0U;
    uint32_t row_total = 0U;
    uint32_t i;
    if (features == NULL ||
        features->struct_size != sizeof(*features) ||
        features->version != HHS_EXACT_PASS219_CORE_CIRCUIT_VERSION ||
        features->word_visits != HHS_EXACT_VM81_CELLS)
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_FEATURES; ++i) {
        phase_total += features->phase_popcount[i];
        if (features->trinary_phase[i] < -1 || features->trinary_phase[i] > 1)
            return 0;
    }
    for (i = 0U; i < HHS_EXACT_PASS219_CORE_CIRCUIT_LOSHU_FEATURES; ++i)
        row_total += features->loshu_popcount[i];
    return phase_total == features->total_popcount &&
           row_total == features->total_popcount;
}

uint32_t hhs_exact_pass219_core_circuit_version(void) {
    return HHS_EXACT_PASS219_CORE_CIRCUIT_VERSION;
}

HHSExactStatus hhs_exact_pass219_core_circuit_descriptor(
    HHSExactPass219CoreCircuitDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_CORE_CIRCUIT_VERSION;
    out_descriptor->source_bytes = HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE_BYTES;
    out_descriptor->a2 = 1U;
    out_descriptor->b2 = 2U;
    out_descriptor->c2 = 3U;
    out_descriptor->b4 = out_descriptor->b2 * out_descriptor->b2;
    out_descriptor->b6 = out_descriptor->b4 * out_descriptor->b2;
    out_descriptor->c4 = out_descriptor->c2 * out_descriptor->c2;
    out_descriptor->b6c4 = out_descriptor->b6 * out_descriptor->c4;
    out_descriptor->update_quantum =
        out_descriptor->b2 * out_descriptor->c2 - out_descriptor->a2;
    out_descriptor->phase_modulus = out_descriptor->b6c4;
    memcpy(out_descriptor->source_sha256,
           HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE_SHA256,
           sizeof(out_descriptor->source_sha256));
    out_descriptor->verbatim_source_preserved = 1U;
    out_descriptor->single_fused_circuit = 1U;
    out_descriptor->exact_integer_only = 1U;
    out_descriptor->online_learning_enabled = 1U;
    out_descriptor->vm81_hydration_bridge = 1U;
    out_descriptor->canonical_mutation_authority = 0U;
    out_descriptor->canonical_hash72_authority = 0U;
    out_descriptor->canonical_hash216_authority = 0U;
    out_descriptor->canonical_persistence_authority = 0U;
    out_descriptor->floating_point_authority = 0U;
    if (out_descriptor->b6c4 != HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS ||
        out_descriptor->update_quantum != HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_core_circuit_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length != NULL)
        *out_length = HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE_BYTES;
    if (out_bytes == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(out_bytes,
           HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE,
           HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE_BYTES);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_core_circuit_state_init(
    HHSExactPass219CoreCircuitStateV1 *out_state
) {
    static const int32_t initial_weights[
        HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT
    ] = {4, 9, 2, 3, 5, 7, 8, 1};
    if (out_state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_state, 0, sizeof(*out_state));
    out_state->struct_size = (uint32_t)sizeof(*out_state);
    out_state->version = HHS_EXACT_PASS219_CORE_CIRCUIT_VERSION;
    memcpy(out_state->weights, initial_weights, sizeof(initial_weights));
    out_state->bias = 6;
    out_state->candidate_only = 1U;
    out_state->bounded_weights = 1U;
    out_state->exact_integer_only = 1U;
    out_state->floating_point_authority = 0U;
    out_state->canonical_mutation_authority = 0U;
    out_state->canonical_hash72_authority = 0U;
    out_state->canonical_hash216_authority = 0U;
    out_state->canonical_persistence_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_core_circuit_extract(
    const HHSExactVM81Frame *frame,
    HHSExactPass219CoreCircuitFeaturesV1 *out_features
) {
    uint32_t cell;
    uint64_t xor_signature = 0U;
    uint64_t sum_signature = 0U;
    if (frame == NULL || out_features == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_features, 0, sizeof(*out_features));
    out_features->struct_size = (uint32_t)sizeof(*out_features);
    out_features->version = HHS_EXACT_PASS219_CORE_CIRCUIT_VERSION;

    for (cell = 0U; cell < HHS_EXACT_VM81_CELLS; ++cell) {
        const uint64_t word = frame->words[cell];
        const uint32_t pc = hhs_p219_core_popcount64(word);
        const uint32_t phase = cell & 7U;
        const uint32_t row = cell % 9U;
        out_features->phase_popcount[phase] += pc;
        out_features->loshu_popcount[row] += pc;
        out_features->total_popcount += pc;
        out_features->nonzero_words += word != 0U ? 1U : 0U;
        xor_signature ^= hhs_p219_core_rotl64(word, cell & 63U);
        sum_signature += word;
        ++out_features->word_visits;
    }

    for (cell = 0U; cell < HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_FEATURES; ++cell) {
        const uint32_t phase =
            out_features->phase_popcount[cell] %
            HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS;
        out_features->trinary_phase[cell] =
            phase < 24U ? (int8_t)-1 :
            (phase < 48U ? (int8_t)0 : (int8_t)1);
    }

    out_features->xor_signature64 = xor_signature;
    out_features->sum_signature64 = sum_signature;
    out_features->hydration_signature64 =
        hhs_p219_core_mix64(
            xor_signature ^
            hhs_p219_core_rotl64(sum_signature, 17U) ^
            ((uint64_t)out_features->total_popcount << 32U) ^
            (uint64_t)out_features->nonzero_words ^
            UINT64_C(0x2190000000000048));

    return hhs_p219_core_features_valid(out_features)
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_core_circuit_validate_state(
    const HHSExactPass219CoreCircuitStateV1 *state
) {
    uint32_t i;
    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (state->struct_size != sizeof(*state) ||
        state->version != HHS_EXACT_PASS219_CORE_CIRCUIT_VERSION ||
        state->candidate_only != 1U ||
        state->bounded_weights != 1U ||
        state->exact_integer_only != 1U ||
        state->floating_point_authority != 0U ||
        state->canonical_mutation_authority != 0U ||
        state->canonical_hash72_authority != 0U ||
        state->canonical_hash216_authority != 0U ||
        state->canonical_persistence_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (state->bias < -HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_BOUND ||
        state->bias > HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_BOUND)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (i = 0U; i < HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT; ++i) {
        if (state->weights[i] < -HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_BOUND ||
            state->weights[i] > HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_BOUND)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_core_circuit_predict(
    const HHSExactPass219CoreCircuitFeaturesV1 *features,
    const HHSExactPass219CoreCircuitStateV1 *state,
    HHSExactPass219CoreCircuitDecisionV1 *out_decision
) {
    int64_t score;
    uint32_t i;
    HHSExactStatus status;
    if (features == NULL || state == NULL || out_decision == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_p219_core_features_valid(features))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_exact_pass219_core_circuit_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    score = state->bias;
    for (i = 0U; i < HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT; ++i)
        score += (int64_t)state->weights[i] *
                 (int64_t)features->trinary_phase[i];
    if (score > INT32_MAX)
        score = INT32_MAX;
    else if (score < INT32_MIN)
        score = INT32_MIN;

    memset(out_decision, 0, sizeof(*out_decision));
    out_decision->struct_size = (uint32_t)sizeof(*out_decision);
    out_decision->version = HHS_EXACT_PASS219_CORE_CIRCUIT_VERSION;
    out_decision->score = (int32_t)score;
    out_decision->prediction_trinary =
        score > 0 ? (int8_t)1 : (score < 0 ? (int8_t)-1 : (int8_t)0);
    out_decision->predicted_candidate_id =
        out_decision->prediction_trinary > 0 ? 2U : 1U;
    out_decision->update_count = state->update_count;
    out_decision->step_count = state->step_count;
    out_decision->hydration_signature64 = features->hydration_signature64;
    out_decision->candidate_only = 1U;
    out_decision->exact_integer_only = 1U;
    out_decision->floating_point_authority = 0U;
    out_decision->canonical_mutation_authority = 0U;
    out_decision->canonical_hash72_authority = 0U;
    out_decision->canonical_hash216_authority = 0U;
    out_decision->canonical_persistence_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_core_circuit_step(
    const HHSExactVM81Frame *frame,
    int8_t feedback_trinary,
    HHSExactPass219CoreCircuitStateV1 *state,
    HHSExactPass219CoreCircuitFeaturesV1 *out_features,
    HHSExactPass219CoreCircuitDecisionV1 *out_decision
) {
    HHSExactStatus status;
    int8_t target;
    uint8_t did_update = 0U;
    uint32_t i;
    if (frame == NULL || state == NULL ||
        out_features == NULL || out_decision == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (feedback_trinary < -1 || feedback_trinary > 1)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    status = hhs_exact_pass219_core_circuit_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_core_circuit_extract(frame, out_features);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_core_circuit_predict(
        out_features, state, out_decision);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_decision->feedback_trinary = feedback_trinary;
    target = feedback_trinary;
    if (target != 0 && out_decision->prediction_trinary != target) {
        for (i = 0U; i < HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT; ++i) {
            const int64_t delta =
                (int64_t)target *
                (int64_t)out_features->trinary_phase[i] *
                HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM;
            state->weights[i] =
                hhs_p219_core_clamp_weight((int64_t)state->weights[i] + delta);
        }
        state->bias = hhs_p219_core_clamp_weight(
            (int64_t)state->bias +
            (int64_t)target * HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM);
        ++state->update_count;
        did_update = 1U;
    }
    ++state->step_count;

    status = hhs_exact_pass219_core_circuit_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_core_circuit_predict(
        out_features, state, out_decision);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    out_decision->feedback_trinary = feedback_trinary;
    out_decision->updated = did_update;
    out_decision->update_count = state->update_count;
    out_decision->step_count = state->step_count;
    return HHS_EXACT_STATUS_OK;
}
