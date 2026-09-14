#include "../include/hhs_pass219_core_holographic_four_lane_1_24.h"

#include <string.h>

static const uint8_t HHS_P219_HOLO4_LOSHU[9] = {
    4U, 9U, 2U,
    3U, 5U, 7U,
    8U, 1U, 6U
};

static const uint8_t HHS_P219_HOLO4_RECIPROCAL_BASIS[8] = {
    HHS_EXACT_PHASE_Y, HHS_EXACT_PHASE_X,
    HHS_EXACT_PHASE_W, HHS_EXACT_PHASE_Z,
    HHS_EXACT_PHASE_YX, HHS_EXACT_PHASE_XY,
    HHS_EXACT_PHASE_WZ, HHS_EXACT_PHASE_ZW
};

static int16_t hhs_p219_holo4_clamp_i16(int32_t value) {
    if (value > HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND)
        return HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND;
    if (value < -HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND)
        return (int16_t)-HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND;
    return (int16_t)value;
}

static int hhs_p219_holo4_hash216_valid(const char *value) {
    uint32_t i;
    if (value == NULL || value[HHS_EXACT_PASS219_HASH216_OCCURRENCES] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        if (value[i] == '\0' || strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static uint8_t hhs_p219_holo4_hash_rank(char glyph) {
    const char *found = strchr(HHS_EXACT_HASH72_ALPHABET, glyph);
    return found == NULL ? UINT8_C(255) : (uint8_t)(found - HHS_EXACT_HASH72_ALPHABET);
}

static int hhs_p219_holo4_transition_valid(
    const HHSExactPass219Hash216TransitionViewV1 *transition
) {
    if (transition == NULL ||
        transition->struct_size != sizeof(*transition) ||
        transition->version != hhs_exact_pass219_rna_version())
        return 0;
    return hhs_p219_holo4_hash216_valid(transition->transition_word216) &&
           hhs_p219_holo4_hash216_valid(transition->transition_identity216);
}

static int hhs_p219_holo4_prepared_valid(
    const HHSExactPass219Holo4PreparedV1 *prepared
) {
    uint32_t cell;
    if (prepared == NULL ||
        prepared->struct_size != sizeof(*prepared) ||
        prepared->version != HHS_EXACT_PASS219_HOLO4_VERSION ||
        prepared->word_visits != HHS_EXACT_VM81_CELLS ||
        prepared->graph_edge_visits != HHS_EXACT_PASS219_HOLO4_DIRECTED_GRAPH_EDGES ||
        prepared->all_cells_have_20_peers != 1U ||
        prepared->reciprocal_phase_closure != 1U ||
        prepared->nested_loshu_complete != 1U ||
        prepared->hash216_positions_complete != 1U ||
        prepared->candidate_only != 1U ||
        prepared->exact_integer_only != 1U ||
        prepared->canonical_mutation_authority != 0U ||
        prepared->canonical_hash72_authority != 0U ||
        prepared->canonical_hash216_authority != 0U ||
        prepared->canonical_persistence_authority != 0U ||
        prepared->floating_point_authority != 0U ||
        !hhs_p219_holo4_hash216_valid(prepared->source_transition_identity216))
        return 0;
    for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_CELL_COUNT; ++cell) {
        const HHSExactPass219Holo4CellV1 *c = &prepared->cells[cell];
        if (c->cell81 != cell || c->row9 >= 9U || c->column9 >= 9U ||
            c->bank9 >= 9U || c->local_loshu < 1U || c->local_loshu > 9U ||
            c->macro_loshu < 1U || c->macro_loshu > 9U ||
            c->phase_basis >= HHS_EXACT_PHASE_BASIS_COUNT ||
            c->reciprocal_basis >= HHS_EXACT_PHASE_BASIS_COUNT ||
            c->phase72 >= HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS ||
            c->reciprocal_phase72 >= HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS ||
            c->trinary_activation < -1 || c->trinary_activation > 1 ||
            c->peer_count != HHS_EXACT_PASS219_HOLO4_SUDOKU_PEERS ||
            ((uint32_t)c->phase72 + (uint32_t)c->reciprocal_phase72) %
                HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS != 0U)
            return 0;
    }
    return 1;
}

HHSExactStatus hhs_exact_pass219_core_circuit_extract_cells(
    const HHSExactVM81Frame *frame,
    HHSExactPass219CoreCircuitFeaturesV1 *out_features,
    uint8_t out_cell_popcount[HHS_EXACT_VM81_CELLS]
) {
    uint32_t cell;
    uint64_t xor_signature = 0U;
    uint64_t sum_signature = 0U;
    if (frame == NULL || out_features == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_features, 0, sizeof(*out_features));
    if (out_cell_popcount != NULL)
        memset(out_cell_popcount, 0, HHS_EXACT_VM81_CELLS);
    out_features->struct_size = (uint32_t)sizeof(*out_features);
    out_features->version = HHS_EXACT_PASS219_CORE_CIRCUIT_VERSION;

    for (cell = 0U; cell < HHS_EXACT_VM81_CELLS; ++cell) {
        const uint64_t word = frame->words[cell];
        const uint32_t pc = hhs_p219_core_popcount64(word);
        const uint32_t phase = cell & 7U;
        const uint32_t row = cell % 9U;
        if (out_cell_popcount != NULL)
            out_cell_popcount[cell] = (uint8_t)pc;
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

uint32_t hhs_exact_pass219_holo4_version(void) {
    return HHS_EXACT_PASS219_HOLO4_VERSION;
}

HHSExactStatus hhs_exact_pass219_holo4_descriptor(
    HHSExactPass219Holo4DescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_HOLO4_VERSION;
    out_descriptor->cell_count = HHS_EXACT_PASS219_HOLO4_CELL_COUNT;
    out_descriptor->bank_count = HHS_EXACT_PASS219_HOLO4_BANK_COUNT;
    out_descriptor->cells_per_bank = HHS_EXACT_PASS219_HOLO4_CELLS_PER_BANK;
    out_descriptor->peers_per_cell = HHS_EXACT_PASS219_HOLO4_SUDOKU_PEERS;
    out_descriptor->directed_graph_edges = HHS_EXACT_PASS219_HOLO4_DIRECTED_GRAPH_EDGES;
    out_descriptor->lane_count = HHS_EXACT_PASS219_HOLO4_LANE_COUNT;
    out_descriptor->phase_modulus = HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS;
    out_descriptor->update_quantum = HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM;
    out_descriptor->nested_loshu_tensor = 1U;
    out_descriptor->sudoku_knowledge_graph = 1U;
    out_descriptor->reciprocal_phase_gear = 1U;
    out_descriptor->local_cell_learning = 1U;
    out_descriptor->bank_learning = 1U;
    out_descriptor->hash216_driven_routing = 1U;
    out_descriptor->cpp_rna_cell_wall_composable = 1U;
    out_descriptor->vm81_abi_carrier = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->exact_integer_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_holo4_state_init(
    HHSExactPass219Holo4StateV1 *out_state
) {
    uint32_t lane;
    uint32_t cell;
    HHSExactStatus status;
    if (out_state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_state, 0, sizeof(*out_state));
    out_state->struct_size = (uint32_t)sizeof(*out_state);
    out_state->version = HHS_EXACT_PASS219_HOLO4_VERSION;
    status = hhs_exact_pass219_core_circuit_state_init(&out_state->core);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    for (lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
        for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_CELL_COUNT; ++cell) {
            const uint32_t row = cell / 9U;
            const uint32_t column = cell % 9U;
            const uint32_t bank = (row / 3U) * 3U + column / 3U;
            const int32_t seed =
                (int32_t)((HHS_P219_HOLO4_LOSHU[(row % 3U) * 3U + column % 3U] +
                           HHS_P219_HOLO4_LOSHU[bank] + lane) % 9U) - 4;
            out_state->cell_lane_weights[lane][cell] = (int16_t)seed;
        }
        for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_BANK_COUNT; ++cell) {
            const int32_t seed =
                (int32_t)((HHS_P219_HOLO4_LOSHU[(cell + lane) % 9U] + lane) % 9U) - 4;
            out_state->bank_lane_weights[lane][cell] = (int16_t)seed;
        }
        out_state->lane_bias[lane] =
            (int16_t)((int32_t)HHS_P219_HOLO4_LOSHU[(lane * 2U) % 9U] - 5);
    }
    out_state->candidate_only = 1U;
    out_state->bounded_weights = 1U;
    out_state->exact_integer_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_holo4_validate_state(
    const HHSExactPass219Holo4StateV1 *state
) {
    uint32_t lane;
    uint32_t cell;
    HHSExactStatus status;
    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (state->struct_size != sizeof(*state) ||
        state->version != HHS_EXACT_PASS219_HOLO4_VERSION ||
        state->candidate_only != 1U || state->bounded_weights != 1U ||
        state->exact_integer_only != 1U ||
        state->canonical_mutation_authority != 0U ||
        state->canonical_hash72_authority != 0U ||
        state->canonical_hash216_authority != 0U ||
        state->canonical_persistence_authority != 0U ||
        state->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_exact_pass219_core_circuit_validate_state(&state->core);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    for (lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
        if (state->lane_bias[lane] < -HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND ||
            state->lane_bias[lane] > HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_CELL_COUNT; ++cell) {
            if (state->cell_lane_weights[lane][cell] < -HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND ||
                state->cell_lane_weights[lane][cell] > HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_BANK_COUNT; ++cell) {
            if (state->bank_lane_weights[lane][cell] < -HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND ||
                state->bank_lane_weights[lane][cell] > HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_holo4_prepare(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    const HHSExactPass219Holo4StateV1 *state,
    HHSExactPass219Holo4PreparedV1 *out_prepared
) {
    uint8_t popcounts[HHS_EXACT_VM81_CELLS];
    uint32_t cell;
    HHSExactStatus status;
    uint64_t graph_signature = UINT64_C(0x2198104200000072);
    if (frame == NULL || transition == NULL || state == NULL || out_prepared == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_holo4_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hhs_p219_holo4_transition_valid(transition))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_prepared, 0, sizeof(*out_prepared));
    out_prepared->struct_size = (uint32_t)sizeof(*out_prepared);
    out_prepared->version = HHS_EXACT_PASS219_HOLO4_VERSION;
    status = hhs_exact_pass219_core_circuit_extract_cells(
        frame, &out_prepared->core_features, popcounts);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_core_circuit_predict(
        &out_prepared->core_features, &state->core, &out_prepared->core_decision);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    memcpy(out_prepared->source_transition_identity216,
           transition->transition_identity216,
           HHS_EXACT_UQCEL_HASH216_STRLEN);
    out_prepared->word_visits = out_prepared->core_features.word_visits;

    for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_CELL_COUNT; ++cell) {
        HHSExactPass219Holo4CellV1 *c = &out_prepared->cells[cell];
        HHSExactPhaseProduct ordered;
        uint32_t peer;
        uint32_t neighbor_popcount = 0U;
        uint32_t peer_count = 0U;
        uint32_t lane;
        uint32_t phase_material;
        uint8_t rank;
        c->cell81 = (uint8_t)cell;
        c->row9 = (uint8_t)(cell / 9U);
        c->column9 = (uint8_t)(cell % 9U);
        c->bank9 = (uint8_t)(((uint32_t)c->row9 / 3U) * 3U + (uint32_t)c->column9 / 3U);
        c->local_loshu = HHS_P219_HOLO4_LOSHU[((uint32_t)c->row9 % 3U) * 3U + (uint32_t)c->column9 % 3U];
        c->macro_loshu = HHS_P219_HOLO4_LOSHU[c->bank9];
        c->phase_basis = (uint8_t)(cell % HHS_EXACT_PHASE_BASIS_COUNT);
        c->reciprocal_basis = HHS_P219_HOLO4_RECIPROCAL_BASIS[c->phase_basis];
        c->self_popcount = popcounts[cell];

        for (peer = 0U; peer < HHS_EXACT_PASS219_HOLO4_CELL_COUNT; ++peer) {
            const uint32_t peer_row = peer / 9U;
            const uint32_t peer_column = peer % 9U;
            const uint32_t peer_bank = (peer_row / 3U) * 3U + peer_column / 3U;
            if (peer == cell)
                continue;
            if (peer_row == c->row9 || peer_column == c->column9 || peer_bank == c->bank9) {
                if (peer < 64U)
                    c->peer_mask_lo64 |= UINT64_C(1) << peer;
                else
                    c->peer_mask_hi17 |= UINT64_C(1) << (peer - 64U);
                neighbor_popcount += popcounts[peer];
                ++peer_count;
            }
        }
        c->peer_count = (uint8_t)peer_count;
        c->neighbor_popcount = (uint16_t)neighbor_popcount;
        out_prepared->graph_edge_visits += peer_count;
        if (peer_count != HHS_EXACT_PASS219_HOLO4_SUDOKU_PEERS)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        for (lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane)
            c->hash216_position[lane] =
                (uint16_t)((cell * HHS_EXACT_PASS219_HOLO4_LANE_COUNT + lane) %
                           HHS_EXACT_PASS219_HASH216_OCCURRENCES);

        status = hhs_exact_phase_product(c->phase_basis, c->reciprocal_basis, &ordered);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        rank = hhs_p219_holo4_hash_rank(
            out_prepared->source_transition_identity216[
                c->hash216_position[cell % HHS_EXACT_PASS219_HOLO4_LANE_COUNT]]);
        if (rank >= HHS_EXACT_HASH72_LEN)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        phase_material =
            (uint32_t)ordered.phase + (uint32_t)c->self_popcount + neighbor_popcount +
            (uint32_t)c->local_loshu + (uint32_t)c->macro_loshu + (uint32_t)rank +
            (uint32_t)(out_prepared->core_features.trinary_phase[c->phase_basis] + 1) * 12U;
        c->phase72 = (uint8_t)(phase_material % HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS);
        c->reciprocal_phase72 = (uint8_t)(
            (HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS - c->phase72) %
            HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS);
        c->trinary_activation =
            c->phase72 < 24U ? (int8_t)-1 :
            (c->phase72 < 48U ? (int8_t)0 : (int8_t)1);
        c->local_signature64 = hhs_p219_core_mix64(
            out_prepared->core_features.hydration_signature64 ^
            c->peer_mask_lo64 ^ hhs_p219_core_rotl64(c->peer_mask_hi17, cell & 63U) ^
            ((uint64_t)c->phase72 << 56U) ^ ((uint64_t)c->reciprocal_phase72 << 48U) ^
            ((uint64_t)c->local_loshu << 40U) ^ ((uint64_t)c->macro_loshu << 32U) ^
            ((uint64_t)rank << 24U) ^ (uint64_t)cell);
        graph_signature = hhs_p219_core_mix64(graph_signature ^ c->local_signature64);

        out_prepared->banks[c->bank9].cell_popcount = (uint16_t)(
            out_prepared->banks[c->bank9].cell_popcount + c->self_popcount);
        out_prepared->banks[c->bank9].activation_sum += c->trinary_activation;
    }

    out_prepared->graph_signature64 = graph_signature;
    out_prepared->tensor_signature64 = graph_signature;
    for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_BANK_COUNT; ++cell) {
        HHSExactPass219Holo4BankV1 *bank = &out_prepared->banks[cell];
        bank->bank9 = (uint8_t)cell;
        bank->macro_loshu = HHS_P219_HOLO4_LOSHU[cell];
        bank->bank_signature64 = hhs_p219_core_mix64(
            graph_signature ^ ((uint64_t)cell << 56U) ^
            ((uint64_t)bank->macro_loshu << 48U) ^
            ((uint64_t)bank->cell_popcount << 16U) ^
            (uint32_t)bank->activation_sum);
        out_prepared->tensor_signature64 = hhs_p219_core_mix64(
            out_prepared->tensor_signature64 ^ bank->bank_signature64);
    }
    for (cell = 0U; cell < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++cell) {
        const uint8_t rank = hhs_p219_holo4_hash_rank(out_prepared->source_transition_identity216[cell]);
        if (rank >= HHS_EXACT_HASH72_LEN)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out_prepared->tensor_signature64 = hhs_p219_core_mix64(
            out_prepared->tensor_signature64 ^ ((uint64_t)rank << (cell & 31U)) ^ cell);
    }

    out_prepared->all_cells_have_20_peers = 1U;
    out_prepared->reciprocal_phase_closure = 1U;
    out_prepared->nested_loshu_complete = 1U;
    out_prepared->hash216_positions_complete = 1U;
    out_prepared->candidate_only = 1U;
    out_prepared->exact_integer_only = 1U;
    return hhs_p219_holo4_prepared_valid(out_prepared)
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_holo4_score_lane(
    const HHSExactPass219Holo4PreparedV1 *prepared,
    const HHSExactPass219Holo4StateV1 *state,
    uint8_t lane_id,
    HHSExactPass219Holo4LaneScoreV1 *out_score
) {
    uint32_t cell;
    int64_t score;
    HHSExactStatus status;
    if (prepared == NULL || state == NULL || out_score == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (lane_id >= HHS_EXACT_PASS219_HOLO4_LANE_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (!hhs_p219_holo4_prepared_valid(prepared))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_exact_pass219_holo4_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(out_score, 0, sizeof(*out_score));
    out_score->struct_size = (uint32_t)sizeof(*out_score);
    out_score->version = HHS_EXACT_PASS219_HOLO4_VERSION;
    out_score->lane_id = lane_id;
    out_score->candidate_only = 1U;
    out_score->exact_integer_only = 1U;
    score = state->lane_bias[lane_id];

    for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_CELL_COUNT; ++cell) {
        const HHSExactPass219Holo4CellV1 *c = &prepared->cells[cell];
        const uint8_t rank = hhs_p219_holo4_hash_rank(
            prepared->source_transition_identity216[c->hash216_position[lane_id]]);
        const int32_t hash_term = (int32_t)(rank % 3U) - 1;
        const int32_t phase_term = (int32_t)((c->phase72 + lane_id) % 3U) - 1;
        const int32_t contribution =
            (int32_t)state->cell_lane_weights[lane_id][cell] *
                (int32_t)c->trinary_activation + hash_term + phase_term;
        out_score->cell_contribution[cell] = contribution;
        score += contribution;
    }
    for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_BANK_COUNT; ++cell) {
        const int32_t contribution =
            (int32_t)state->bank_lane_weights[lane_id][cell] *
            prepared->banks[cell].activation_sum;
        out_score->bank_contribution[cell] = contribution;
        score += contribution;
    }
    {
        const uint32_t first = ((uint32_t)lane_id * 2U) % HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT;
        const uint32_t second = (first + 1U) % HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT;
        score += (int64_t)state->core.weights[first] * prepared->core_features.trinary_phase[first];
        score += (int64_t)state->core.weights[second] * prepared->core_features.trinary_phase[second];
    }
    out_score->score = score;
    out_score->routing_signature64 = hhs_p219_core_mix64(
        prepared->tensor_signature64 ^ ((uint64_t)lane_id << 60U) ^ (uint64_t)score);
    return HHS_EXACT_STATUS_OK;
}

static uint8_t hhs_p219_holo4_select_lane(
    const HHSExactPass219Holo4LaneScoreV1 lanes[HHS_EXACT_PASS219_HOLO4_LANE_COUNT]
) {
    uint8_t selected = 0U;
    uint8_t lane;
    for (lane = 1U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
        if (lanes[lane].score > lanes[selected].score)
            selected = lane;
    }
    return selected;
}

HHSExactStatus hhs_exact_pass219_holo4_finalize(
    const HHSExactPass219Holo4PreparedV1 *prepared,
    const HHSExactPass219Holo4LaneScoreV1 lanes[HHS_EXACT_PASS219_HOLO4_LANE_COUNT],
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Holo4StateV1 *state,
    HHSExactPass219Holo4DecisionV1 *out_decision
) {
    uint8_t selected;
    uint8_t lane;
    uint8_t did_update = 0U;
    uint32_t cell;
    HHSExactStatus status;
    if (prepared == NULL || lanes == NULL || state == NULL || out_decision == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_p219_holo4_prepared_valid(prepared))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_exact_pass219_holo4_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (feedback_trinary < -1 || feedback_trinary > 1)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (feedback_lane != HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE &&
        feedback_lane >= HHS_EXACT_PASS219_HOLO4_LANE_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (feedback_lane == HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE && feedback_trinary != 0)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    for (lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
        if (lanes[lane].struct_size != sizeof(lanes[lane]) ||
            lanes[lane].version != HHS_EXACT_PASS219_HOLO4_VERSION ||
            lanes[lane].lane_id != lane || lanes[lane].candidate_only != 1U ||
            lanes[lane].exact_integer_only != 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    selected = hhs_p219_holo4_select_lane(lanes);
    memset(out_decision, 0, sizeof(*out_decision));
    out_decision->struct_size = (uint32_t)sizeof(*out_decision);
    out_decision->version = HHS_EXACT_PASS219_HOLO4_VERSION;
    memcpy(out_decision->lanes, lanes, sizeof(out_decision->lanes));
    out_decision->selected_lane = selected;
    out_decision->feedback_lane = feedback_lane;
    out_decision->feedback_trinary = feedback_trinary;
    memcpy(out_decision->source_transition_identity216,
           prepared->source_transition_identity216,
           HHS_EXACT_UQCEL_HASH216_STRLEN);

    if (feedback_trinary != 0 &&
        prepared->core_decision.prediction_trinary != feedback_trinary) {
        for (cell = 0U; cell < HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT; ++cell) {
            const int64_t delta =
                (int64_t)feedback_trinary *
                (int64_t)prepared->core_features.trinary_phase[cell] *
                HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM;
            state->core.weights[cell] = hhs_p219_core_clamp_weight(
                (int64_t)state->core.weights[cell] + delta);
        }
        state->core.bias = hhs_p219_core_clamp_weight(
            (int64_t)state->core.bias +
            (int64_t)feedback_trinary * HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM);
        ++state->core.update_count;
        did_update = 1U;
    }
    ++state->core.step_count;

    if (feedback_lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT && feedback_trinary > 0 &&
        selected != feedback_lane) {
        for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_CELL_COUNT; ++cell) {
            const int32_t delta =
                (int32_t)prepared->cells[cell].trinary_activation *
                HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM;
            state->cell_lane_weights[feedback_lane][cell] = hhs_p219_holo4_clamp_i16(
                (int32_t)state->cell_lane_weights[feedback_lane][cell] + delta);
            state->cell_lane_weights[selected][cell] = hhs_p219_holo4_clamp_i16(
                (int32_t)state->cell_lane_weights[selected][cell] - delta);
        }
        for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_BANK_COUNT; ++cell) {
            const int32_t delta =
                prepared->banks[cell].activation_sum *
                HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM;
            state->bank_lane_weights[feedback_lane][cell] = hhs_p219_holo4_clamp_i16(
                (int32_t)state->bank_lane_weights[feedback_lane][cell] + delta);
            state->bank_lane_weights[selected][cell] = hhs_p219_holo4_clamp_i16(
                (int32_t)state->bank_lane_weights[selected][cell] - delta);
        }
        state->lane_bias[feedback_lane] = hhs_p219_holo4_clamp_i16(
            (int32_t)state->lane_bias[feedback_lane] + HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM);
        state->lane_bias[selected] = hhs_p219_holo4_clamp_i16(
            (int32_t)state->lane_bias[selected] - HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM);
        ++state->update_count;
        did_update = 1U;
    } else if (feedback_lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT && feedback_trinary < 0) {
        for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_CELL_COUNT; ++cell) {
            const int32_t delta =
                (int32_t)prepared->cells[cell].trinary_activation *
                HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM;
            state->cell_lane_weights[feedback_lane][cell] = hhs_p219_holo4_clamp_i16(
                (int32_t)state->cell_lane_weights[feedback_lane][cell] - delta);
        }
        for (cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_BANK_COUNT; ++cell) {
            const int32_t delta =
                prepared->banks[cell].activation_sum *
                HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM;
            state->bank_lane_weights[feedback_lane][cell] = hhs_p219_holo4_clamp_i16(
                (int32_t)state->bank_lane_weights[feedback_lane][cell] - delta);
        }
        state->lane_bias[feedback_lane] = hhs_p219_holo4_clamp_i16(
            (int32_t)state->lane_bias[feedback_lane] - HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM);
        ++state->update_count;
        did_update = 1U;
    }
    ++state->step_count;

    status = hhs_exact_pass219_holo4_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    out_decision->updated = did_update;
    out_decision->update_count = state->update_count;
    out_decision->step_count = state->step_count;
    out_decision->decision_signature64 = prepared->tensor_signature64;
    for (lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane)
        out_decision->decision_signature64 = hhs_p219_core_mix64(
            out_decision->decision_signature64 ^ lanes[lane].routing_signature64);
    out_decision->decision_signature64 = hhs_p219_core_mix64(
        out_decision->decision_signature64 ^ ((uint64_t)selected << 56U) ^ state->step_count);
    out_decision->candidate_only = 1U;
    out_decision->exact_integer_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_holo4_route(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Holo4StateV1 *state,
    HHSExactPass219Holo4PreparedV1 *out_prepared,
    HHSExactPass219Holo4DecisionV1 *out_decision
) {
    HHSExactPass219Holo4LaneScoreV1 lanes[HHS_EXACT_PASS219_HOLO4_LANE_COUNT];
    uint8_t lane;
    HHSExactStatus status;
    if (frame == NULL || transition == NULL || state == NULL ||
        out_prepared == NULL || out_decision == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_holo4_prepare(frame, transition, state, out_prepared);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    for (lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
        status = hhs_exact_pass219_holo4_score_lane(out_prepared, state, lane, &lanes[lane]);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
    }
    return hhs_exact_pass219_holo4_finalize(
        out_prepared, lanes, feedback_lane, feedback_trinary, state, out_decision);
}
