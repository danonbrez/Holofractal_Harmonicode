#include "hhs_pass219_rml15_route_reverse_replay_1_28.h"

#include <openssl/sha.h>

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define HHS219_RML15_PHASE_MODULUS 72U
#define HHS219_RML15_QUARTER_CYCLE 18
#define HHS219_RML15_HALF_CYCLE 36
#define HHS219_RML15_REVERSE_MATERIAL_MAX 2048U

static uint32_t hhs219_rml15_version_word(void) {
    return (HHS_EXACT_PASS219_RML15_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_RML15_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_RML15_VERSION_PATCH;
}

static int hhs219_rml15_nonzero(const uint8_t *bytes, size_t length) {
    size_t i;
    uint8_t aggregate = 0U;
    if (bytes == NULL)
        return 0;
    for (i = 0U; i < length; ++i)
        aggregate = (uint8_t)(aggregate | bytes[i]);
    return aggregate != 0U;
}

static int hhs219_rml15_append(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    const void *data,
    size_t length
) {
    if (out == NULL || cursor == NULL || data == NULL ||
        *cursor > capacity || length > capacity - *cursor)
        return 0;
    memcpy(out + *cursor, data, length);
    *cursor += length;
    return 1;
}

static int hhs219_rml15_append_u32_be(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    uint32_t value
) {
    const uint8_t bytes[4] = {
        (uint8_t)(value >> 24U),
        (uint8_t)(value >> 16U),
        (uint8_t)(value >> 8U),
        (uint8_t)value
    };
    return hhs219_rml15_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static int hhs219_rml15_append_u64_be(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    uint64_t value
) {
    const uint8_t bytes[8] = {
        (uint8_t)(value >> 56U),
        (uint8_t)(value >> 48U),
        (uint8_t)(value >> 40U),
        (uint8_t)(value >> 32U),
        (uint8_t)(value >> 24U),
        (uint8_t)(value >> 16U),
        (uint8_t)(value >> 8U),
        (uint8_t)value
    };
    return hhs219_rml15_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static int hhs219_rml15_mod72(int32_t value) {
    int32_t result = value % (int32_t)HHS219_RML15_PHASE_MODULUS;
    if (result < 0)
        result += (int32_t)HHS219_RML15_PHASE_MODULUS;
    return (int)result;
}

static uint8_t hhs219_rml15_expected_product(uint8_t generator, int8_t sign) {
    return (uint8_t)hhs219_rml15_mod72(
        (int32_t)generator + ((int32_t)sign * HHS219_RML15_QUARTER_CYCLE));
}

static uint64_t hhs219_rml15_ambient_index(
    const HHSExactPass219RML15PhaseStateV1 *state
) {
    uint64_t value = 0U;
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_PASS219_RML15_CHANNELS; ++i)
        value = value * HHS219_RML15_PHASE_MODULUS + state->phases[i];
    return value;
}

static int hhs219_rml15_state_valid(
    const HHSExactPass219RML15PhaseStateV1 *state
) {
    uint32_t i;
    if (state == NULL)
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_RML15_CHANNELS; ++i) {
        if (state->phases[i] >= HHS219_RML15_PHASE_MODULUS)
            return 0;
    }
    for (i = 0U; i < HHS_EXACT_PASS219_RML15_PRODUCTS; ++i) {
        if (state->quarter_turn_signs[i] != 1 &&
            state->quarter_turn_signs[i] != -1)
            return 0;
        if (state->phases[4U + i] !=
            hhs219_rml15_expected_product(
                state->phases[i], state->quarter_turn_signs[i]))
            return 0;
    }
    if (state->quarter_turn_signs[0] != -state->quarter_turn_signs[1] ||
        state->quarter_turn_signs[2] != -state->quarter_turn_signs[3])
        return 0;
    return state->ambient_state_index == hhs219_rml15_ambient_index(state);
}

static int hhs219_rml15_state_equal(
    const HHSExactPass219RML15PhaseStateV1 *left,
    const HHSExactPass219RML15PhaseStateV1 *right
) {
    return left != NULL && right != NULL &&
           memcmp(left->phases, right->phases, sizeof(left->phases)) == 0 &&
           memcmp(left->quarter_turn_signs,
                  right->quarter_turn_signs,
                  sizeof(left->quarter_turn_signs)) == 0 &&
           left->ambient_state_index == right->ambient_state_index;
}

static int hhs219_rml15_apply_reverse_edge(
    HHSExactPass219RML15PhaseStateV1 *state,
    const HHSExactPass219RML15ReverseEdgeV1 *edge
) {
    uint32_t product;
    uint32_t first;
    uint32_t second;
    if (state == NULL || edge == NULL || !hhs219_rml15_state_valid(state))
        return 0;

    if (edge->kind == HHS_EXACT_PASS219_RML15_EDGE_COUPLED_MOVE) {
        if (edge->selector >= 4U || edge->signed_steps == 0 ||
            edge->signed_steps < -71 || edge->signed_steps > 71)
            return 0;
        product = 4U + edge->selector;
        state->phases[edge->selector] = (uint8_t)hhs219_rml15_mod72(
            (int32_t)state->phases[edge->selector] + edge->signed_steps);
        state->phases[product] = (uint8_t)hhs219_rml15_mod72(
            (int32_t)state->phases[product] + edge->signed_steps);
    } else if (edge->kind == HHS_EXACT_PASS219_RML15_EDGE_PAIR_FLIP) {
        if (edge->selector >= 2U || edge->signed_steps != HHS219_RML15_HALF_CYCLE)
            return 0;
        first = edge->selector * 2U;
        second = first + 1U;
        state->quarter_turn_signs[first] =
            (int8_t)-state->quarter_turn_signs[first];
        state->quarter_turn_signs[second] =
            (int8_t)-state->quarter_turn_signs[second];
        state->phases[4U + first] = hhs219_rml15_expected_product(
            state->phases[first], state->quarter_turn_signs[first]);
        state->phases[4U + second] = hhs219_rml15_expected_product(
            state->phases[second], state->quarter_turn_signs[second]);
    } else {
        return 0;
    }

    state->ambient_state_index = hhs219_rml15_ambient_index(state);
    return hhs219_rml15_state_valid(state);
}

static int hhs219_rml15_reverse_witness_valid(
    const HHSExactPass219RML13RouteWitnessV1 *route,
    const HHSExactPass219RML15ReverseWitnessV1 *reverse,
    uint32_t *out_pair_flips,
    uint32_t *out_coupled_moves
) {
    uint32_t i;
    uint32_t pair_flips = 0U;
    uint32_t coupled_moves = 0U;
    if (route == NULL || reverse == NULL ||
        reverse->struct_size != sizeof(*reverse) ||
        reverse->version != hhs219_rml15_version_word() ||
        reverse->edge_count > HHS_EXACT_PASS219_RML15_MAX_EDGES ||
        reverse->edge_count != route->edge_count ||
        reverse->retained_forward_ancestry_used != 1U ||
        reverse->reverse_edges_are_exact_inverses != 1U ||
        reverse->reverse_terminal_matches_retained_source != 1U ||
        reverse->hash216_cryptographic_inversion_used != 0U ||
        reverse->floating_point_authority != 0U ||
        !hhs219_rml15_state_valid(&reverse->source_state) ||
        !hhs219_rml15_state_valid(&reverse->target_state) ||
        !hhs219_rml15_nonzero(reverse->route_sha256, sizeof(reverse->route_sha256)) ||
        !hhs219_rml15_nonzero(reverse->source_state_sha256, sizeof(reverse->source_state_sha256)) ||
        !hhs219_rml15_nonzero(reverse->target_state_sha256, sizeof(reverse->target_state_sha256)) ||
        memcmp(reverse->route_sha256, route->route_sha256, sizeof(reverse->route_sha256)) != 0 ||
        memcmp(reverse->source_state_sha256,
               route->source_state_sha256,
               sizeof(reverse->source_state_sha256)) != 0 ||
        memcmp(reverse->target_state_sha256,
               route->target_state_sha256,
               sizeof(reverse->target_state_sha256)) != 0)
        return 0;

    for (i = 0U; i < reverse->edge_count; ++i) {
        if (reverse->edges[i].kind == HHS_EXACT_PASS219_RML15_EDGE_PAIR_FLIP)
            ++pair_flips;
        else if (reverse->edges[i].kind == HHS_EXACT_PASS219_RML15_EDGE_COUPLED_MOVE)
            ++coupled_moves;
        else
            return 0;
    }
    if (pair_flips != route->pair_flip_edges ||
        coupled_moves != route->coupled_move_edges)
        return 0;

    if (out_pair_flips != NULL)
        *out_pair_flips = pair_flips;
    if (out_coupled_moves != NULL)
        *out_coupled_moves = coupled_moves;
    return 1;
}

static int hhs219_rml15_rml14_equal(
    const HHSExactPass219RML14BindingV1 *left,
    const HHSExactPass219RML14BindingV1 *right
) {
    return left != NULL && right != NULL &&
           left->decision == HHS_EXACT_PASS219_RML14_VERIFIED &&
           right->decision == HHS_EXACT_PASS219_RML14_VERIFIED &&
           left->edge_count == right->edge_count &&
           left->vm5184_address == right->vm5184_address &&
           memcmp(left->receipt_material_sha256,
                  right->receipt_material_sha256,
                  sizeof(left->receipt_material_sha256)) == 0 &&
           memcmp(left->witness_root_sha256,
                  right->witness_root_sha256,
                  sizeof(left->witness_root_sha256)) == 0 &&
           memcmp(left->route_environment_root_sha256,
                  right->route_environment_root_sha256,
                  sizeof(left->route_environment_root_sha256)) == 0 &&
           memcmp(left->candidate_frame_sha256,
                  right->candidate_frame_sha256,
                  sizeof(left->candidate_frame_sha256)) == 0 &&
           strcmp(left->previous_hash72, right->previous_hash72) == 0 &&
           strcmp(left->change_hash72, right->change_hash72) == 0 &&
           strcmp(left->frozen_uqcel_receipt_hash72,
                  right->frozen_uqcel_receipt_hash72) == 0 &&
           strcmp(left->successor_receipt_hash72,
                  right->successor_receipt_hash72) == 0 &&
           strcmp(left->frozen_rml13_transition_hash216,
                  right->frozen_rml13_transition_hash216) == 0 &&
           strcmp(left->successor_hash216_triplet,
                  right->successor_hash216_triplet) == 0 &&
           strcmp(left->successor_transition_hash216,
                  right->successor_transition_hash216) == 0;
}

static int hhs219_rml15_build_instruction_root(
    const HHSExactPass219RML15ReverseWitnessV1 *reverse,
    uint8_t out_root[HHS_EXACT_PASS219_RML15_SHA256_BYTES]
) {
    static const uint8_t domain[] = "HHS-P219-RML15-REVERSE-INSTRUCTIONS-V1";
    uint8_t material[512U];
    size_t cursor = 0U;
    uint32_t i;
    if (reverse == NULL || out_root == NULL)
        return 0;
    if (!hhs219_rml15_append(material, sizeof(material), &cursor,
                             domain, sizeof(domain) - 1U) ||
        !hhs219_rml15_append_u32_be(material, sizeof(material), &cursor,
                                    reverse->version) ||
        !hhs219_rml15_append_u32_be(material, sizeof(material), &cursor,
                                    reverse->edge_count) ||
        !hhs219_rml15_append(material, sizeof(material), &cursor,
                             reverse->route_sha256, sizeof(reverse->route_sha256)) ||
        !hhs219_rml15_append(material, sizeof(material), &cursor,
                             reverse->source_state_sha256,
                             sizeof(reverse->source_state_sha256)) ||
        !hhs219_rml15_append(material, sizeof(material), &cursor,
                             reverse->target_state_sha256,
                             sizeof(reverse->target_state_sha256)) ||
        !hhs219_rml15_append(material, sizeof(material), &cursor,
                             reverse->source_state.phases,
                             sizeof(reverse->source_state.phases)) ||
        !hhs219_rml15_append(material, sizeof(material), &cursor,
                             reverse->source_state.quarter_turn_signs,
                             sizeof(reverse->source_state.quarter_turn_signs)) ||
        !hhs219_rml15_append_u64_be(material, sizeof(material), &cursor,
                                    reverse->source_state.ambient_state_index) ||
        !hhs219_rml15_append(material, sizeof(material), &cursor,
                             reverse->target_state.phases,
                             sizeof(reverse->target_state.phases)) ||
        !hhs219_rml15_append(material, sizeof(material), &cursor,
                             reverse->target_state.quarter_turn_signs,
                             sizeof(reverse->target_state.quarter_turn_signs)) ||
        !hhs219_rml15_append_u64_be(material, sizeof(material), &cursor,
                                    reverse->target_state.ambient_state_index))
        return 0;

    for (i = 0U; i < reverse->edge_count; ++i) {
        if (!hhs219_rml15_append_u32_be(material, sizeof(material), &cursor,
                                        reverse->edges[i].kind) ||
            !hhs219_rml15_append_u32_be(material, sizeof(material), &cursor,
                                        reverse->edges[i].selector) ||
            !hhs219_rml15_append_u32_be(material, sizeof(material), &cursor,
                                        (uint32_t)reverse->edges[i].signed_steps))
            return 0;
    }

    return SHA256(material, cursor, out_root) != NULL &&
           hhs219_rml15_nonzero(out_root, HHS_EXACT_PASS219_RML15_SHA256_BYTES);
}

static int hhs219_rml15_build_reverse_material(
    const HHSExactPass219RML14BindingV1 *forward,
    const HHSExactPass219RML15ReverseWitnessV1 *reverse,
    const uint8_t instruction_root[HHS_EXACT_PASS219_RML15_SHA256_BYTES],
    uint8_t *material,
    size_t capacity,
    size_t *out_length
) {
    static const uint8_t domain[] = "HHS-P219-RML15-ROUTE-REVERSE-ANCESTRY-WITNESS-V1";
    size_t cursor = 0U;
    if (forward == NULL || reverse == NULL || instruction_root == NULL ||
        material == NULL || out_length == NULL)
        return 0;

    if (!hhs219_rml15_append(material, capacity, &cursor,
                             domain, sizeof(domain) - 1U) ||
        !hhs219_rml15_append_u32_be(material, capacity, &cursor,
                                    hhs219_rml15_version_word()) ||
        !hhs219_rml15_append_u32_be(material, capacity, &cursor,
                                    reverse->edge_count) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             reverse->route_sha256, sizeof(reverse->route_sha256)) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             reverse->source_state_sha256,
                             sizeof(reverse->source_state_sha256)) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             reverse->target_state_sha256,
                             sizeof(reverse->target_state_sha256)) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             instruction_root,
                             HHS_EXACT_PASS219_RML15_SHA256_BYTES) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             forward->witness_root_sha256,
                             sizeof(forward->witness_root_sha256)) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             forward->route_environment_root_sha256,
                             sizeof(forward->route_environment_root_sha256)) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             forward->candidate_frame_sha256,
                             sizeof(forward->candidate_frame_sha256)) ||
        !hhs219_rml15_append_u64_be(material, capacity, &cursor,
                                    reverse->source_state.ambient_state_index) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             forward->previous_hash72,
                             HHS_EXACT_PASS219_RML14_HASH72_LEN) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             forward->change_hash72,
                             HHS_EXACT_PASS219_RML14_HASH72_LEN) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             forward->frozen_uqcel_receipt_hash72,
                             HHS_EXACT_PASS219_RML14_HASH72_LEN) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             forward->successor_receipt_hash72,
                             HHS_EXACT_PASS219_RML14_HASH72_LEN) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             forward->frozen_rml13_transition_hash216,
                             HHS_EXACT_PASS219_RML14_HASH216_LEN) ||
        !hhs219_rml15_append(material, capacity, &cursor,
                             forward->successor_transition_hash216,
                             HHS_EXACT_PASS219_RML14_HASH216_LEN))
        return 0;

    *out_length = cursor;
    return 1;
}

uint32_t hhs_exact_pass219_rml15_version(void) {
    return hhs219_rml15_version_word();
}

HHSExactStatus hhs_exact_pass219_rml15_verify_route_reverse_replay(
    const uint8_t *source_bytes,
    size_t source_length,
    const HHSExactPass219RML13RouteWitnessV1 *route_witness,
    const HHSExactPass219RML15ReverseWitnessV1 *reverse_witness,
    HHSExactPass219RML15BindingV1 *out_binding
) {
    HHSExactPass219RML14BindingV1 forward;
    HHSExactPass219RML14BindingV1 replay;
    HHSExactPass219RML15PhaseStateV1 restored;
    uint8_t reverse_material[HHS219_RML15_REVERSE_MATERIAL_MAX];
    size_t reverse_material_length = 0U;
    HHSHash72 reverse_hash72;
    HHSHash216 reverse_hash216;
    uint32_t pair_flips = 0U;
    uint32_t coupled_moves = 0U;
    uint32_t i;
    HHSExactStatus status;

    if (source_bytes == NULL || route_witness == NULL ||
        reverse_witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_binding, 0, sizeof(*out_binding));
    memset(&forward, 0, sizeof(forward));
    memset(&replay, 0, sizeof(replay));
    memset(reverse_material, 0, sizeof(reverse_material));
    memset(&reverse_hash72, 0, sizeof(reverse_hash72));
    memset(&reverse_hash216, 0, sizeof(reverse_hash216));

    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs219_rml15_version_word();
    out_binding->decision = HHS_EXACT_PASS219_RML15_UNRESOLVED;
    out_binding->reason = HHS_EXACT_PASS219_RML15_REASON_RML14_FORWARD;
    out_binding->reverse_receipt_is_ancestry_witness_not_hash_inverse = 1U;
    out_binding->hash216_cryptographic_inversion_used = 0U;
    out_binding->second_vm81_commit_primitive_added = 0U;
    out_binding->optimizer_transition_authority = 0U;
    out_binding->floating_point_authority = 0U;
    out_binding->hash216_persistence_authority = 0U;
    out_binding->scalar_projection_substitution_authority = 0U;

    status = hhs_exact_pass219_rml14_bind_route_receipt_successor(
        source_bytes, source_length, route_witness, &forward);
    if (status != HHS_EXACT_STATUS_OK ||
        forward.decision != HHS_EXACT_PASS219_RML14_VERIFIED) {
        out_binding->decision = HHS_EXACT_PASS219_RML15_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->rml14_forward_verified = 1U;

    out_binding->reason = HHS_EXACT_PASS219_RML15_REASON_RML14_REPLAY;
    status = hhs_exact_pass219_rml14_bind_route_receipt_successor(
        source_bytes, source_length, route_witness, &replay);
    if (status != HHS_EXACT_STATUS_OK ||
        replay.decision != HHS_EXACT_PASS219_RML14_VERIFIED ||
        !hhs219_rml15_rml14_equal(&forward, &replay)) {
        out_binding->decision = HHS_EXACT_PASS219_RML15_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->rml14_replay_verified = 1U;
    out_binding->forward_replay_identity_equal = 1U;

    out_binding->reason = HHS_EXACT_PASS219_RML15_REASON_RETAINED_ANCESTRY;
    if (!hhs219_rml15_reverse_witness_valid(
            route_witness, reverse_witness, &pair_flips, &coupled_moves) ||
        !hhs219_rml15_build_instruction_root(
            reverse_witness, out_binding->reverse_instruction_root_sha256)) {
        out_binding->decision = HHS_EXACT_PASS219_RML15_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->retained_ancestry_verified = 1U;
    out_binding->edge_count = reverse_witness->edge_count;
    out_binding->pair_flip_edges = pair_flips;
    out_binding->coupled_move_edges = coupled_moves;

    out_binding->reason = HHS_EXACT_PASS219_RML15_REASON_REVERSE_EXECUTION;
    restored = reverse_witness->target_state;
    for (i = 0U; i < reverse_witness->edge_count; ++i) {
        if (!hhs219_rml15_apply_reverse_edge(
                &restored, &reverse_witness->edges[i])) {
            out_binding->decision = HHS_EXACT_PASS219_RML15_REJECTED;
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }
    if (!hhs219_rml15_state_valid(&restored) ||
        !hhs219_rml15_state_equal(&restored, &reverse_witness->source_state)) {
        out_binding->decision = HHS_EXACT_PASS219_RML15_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->reverse_instruction_sequence_verified = 1U;
    out_binding->reverse_phase_state_restored = 1U;
    out_binding->reverse_ambient_index_restored = 1U;
    out_binding->reverse_product_geometry_preserved = 1U;
    out_binding->reverse_chirality_preserved = 1U;
    out_binding->restored_ambient_state_index = restored.ambient_state_index;

    out_binding->reason = HHS_EXACT_PASS219_RML15_REASON_REVERSE_RECEIPT;
    if (!hhs219_rml15_build_reverse_material(
            &forward,
            reverse_witness,
            out_binding->reverse_instruction_root_sha256,
            reverse_material,
            sizeof(reverse_material),
            &reverse_material_length) ||
        reverse_material_length == 0U ||
        reverse_material_length > UINT32_MAX ||
        SHA256(reverse_material,
               reverse_material_length,
               out_binding->reverse_material_sha256) == NULL) {
        out_binding->decision = HHS_EXACT_PASS219_RML15_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->reverse_material_length = (uint32_t)reverse_material_length;

    hhs_hash72_compute(reverse_material, reverse_material_length, &reverse_hash72);
    hhs_hash216_compute(reverse_material, reverse_material_length, &reverse_hash216);
    memcpy(out_binding->reverse_receipt_hash72,
           reverse_hash72.value,
           sizeof(out_binding->reverse_receipt_hash72));
    memcpy(out_binding->reverse_witness_hash216,
           reverse_hash216.value,
           sizeof(out_binding->reverse_witness_hash216));
    out_binding->canonical_hash72_delegate_used = 1U;
    out_binding->canonical_hash216_delegate_used = 1U;

    memcpy(out_binding->previous_hash72,
           forward.previous_hash72,
           sizeof(out_binding->previous_hash72));
    memcpy(out_binding->route_bound_change_hash72,
           forward.change_hash72,
           sizeof(out_binding->route_bound_change_hash72));
    memcpy(out_binding->frozen_uqcel_receipt_hash72,
           forward.frozen_uqcel_receipt_hash72,
           sizeof(out_binding->frozen_uqcel_receipt_hash72));
    memcpy(out_binding->rml14_successor_receipt_hash72,
           forward.successor_receipt_hash72,
           sizeof(out_binding->rml14_successor_receipt_hash72));
    memcpy(out_binding->frozen_rml13_transition_hash216,
           forward.frozen_rml13_transition_hash216,
           sizeof(out_binding->frozen_rml13_transition_hash216));
    memcpy(out_binding->rml14_successor_transition_hash216,
           forward.successor_transition_hash216,
           sizeof(out_binding->rml14_successor_transition_hash216));
    out_binding->historical_uqcel_receipt_preserved = 1U;
    out_binding->historical_rml13_transition_preserved = 1U;
    out_binding->rml14_successor_chain_preserved = 1U;

    out_binding->reason = HHS_EXACT_PASS219_RML15_REASON_AUTHORITY;
    if (out_binding->rml14_forward_verified != 1U ||
        out_binding->rml14_replay_verified != 1U ||
        out_binding->forward_replay_identity_equal != 1U ||
        out_binding->retained_ancestry_verified != 1U ||
        out_binding->reverse_instruction_sequence_verified != 1U ||
        out_binding->reverse_phase_state_restored != 1U ||
        out_binding->reverse_ambient_index_restored != 1U ||
        out_binding->reverse_product_geometry_preserved != 1U ||
        out_binding->reverse_chirality_preserved != 1U ||
        out_binding->reverse_receipt_is_ancestry_witness_not_hash_inverse != 1U ||
        out_binding->canonical_hash72_delegate_used != 1U ||
        out_binding->canonical_hash216_delegate_used != 1U ||
        out_binding->historical_uqcel_receipt_preserved != 1U ||
        out_binding->historical_rml13_transition_preserved != 1U ||
        out_binding->rml14_successor_chain_preserved != 1U ||
        out_binding->hash216_cryptographic_inversion_used != 0U ||
        out_binding->second_vm81_commit_primitive_added != 0U ||
        out_binding->optimizer_transition_authority != 0U ||
        out_binding->floating_point_authority != 0U ||
        out_binding->hash216_persistence_authority != 0U ||
        out_binding->scalar_projection_substitution_authority != 0U) {
        out_binding->decision = HHS_EXACT_PASS219_RML15_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_binding->reason = HHS_EXACT_PASS219_RML15_REASON_NONE;
    out_binding->decision = HHS_EXACT_PASS219_RML15_VERIFIED;
    return HHS_EXACT_STATUS_OK;
}
