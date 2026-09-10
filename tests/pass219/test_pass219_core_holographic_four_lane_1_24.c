#include "hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static unsigned popcount64(uint64_t x) {
    unsigned n = 0U;
    while (x != 0U) {
        x &= x - UINT64_C(1);
        ++n;
    }
    return n;
}

static void fill_hash72(char out[HHS_EXACT_HASH72_STRLEN], uint8_t offset) {
    size_t i;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

static void fill_identity216(char out[HHS_EXACT_UQCEL_HASH216_STRLEN], uint8_t offset) {
    size_t i;
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i * 7U + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
}

static HHSExactPass219Hash216TransitionViewV1 build_transition(uint8_t offset) {
    HHSExactPass219Hash216TransitionViewV1 transition;
    char previous[HHS_EXACT_HASH72_STRLEN];
    char change[HHS_EXACT_HASH72_STRLEN];
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    memset(&transition, 0, sizeof(transition));
    fill_hash72(previous, offset);
    fill_hash72(change, (uint8_t)(offset + 1U));
    fill_hash72(receipt, (uint8_t)(offset + 2U));
    fill_identity216(identity, (uint8_t)(offset + 3U));
    if (hhs_exact_pass219_hash216_transition_init(
            previous, change, receipt, identity, &transition) != HHS_EXACT_STATUS_OK)
        memset(&transition, 0, sizeof(transition));
    return transition;
}

static HHSExactVM81Frame build_frame(void) {
    HHSExactVM81Frame frame;
    uint32_t i;
    memset(&frame, 0, sizeof(frame));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        const uint64_t a = UINT64_C(0x9e3779b97f4a7c15) * (uint64_t)(i + 1U);
        const uint64_t b = UINT64_C(0x0102040810204081) ^ ((uint64_t)i << (i % 17U));
        frame.words[i] = a ^ b;
    }
    return frame;
}

int main(void) {
    HHSExactPass219Holo4DescriptorV1 descriptor;
    HHSExactPass219Holo4StateV1 state_a;
    HHSExactPass219Holo4StateV1 state_b;
    HHSExactPass219Holo4PreparedV1 prepared_a;
    HHSExactPass219Holo4PreparedV1 prepared_b;
    HHSExactPass219Holo4PreparedV1 prepared_other_identity;
    HHSExactPass219Holo4LaneScoreV1 lanes[HHS_EXACT_PASS219_HOLO4_LANE_COUNT];
    HHSExactPass219Holo4DecisionV1 decision_a;
    HHSExactPass219Holo4DecisionV1 decision_b;
    HHSExactPass219Hash216TransitionViewV1 transition = build_transition(5U);
    HHSExactPass219Hash216TransitionViewV1 transition_other = build_transition(17U);
    HHSExactVM81Frame frame = build_frame();
    uint32_t i;
    uint32_t lane;
    uint32_t graph_edges = 0U;

    CHECK(transition.struct_size == sizeof(transition));
    CHECK(transition_other.struct_size == sizeof(transition_other));
    CHECK(hhs_exact_pass219_holo4_version() == HHS_EXACT_PASS219_HOLO4_VERSION);
    CHECK(hhs_exact_pass219_holo4_descriptor(&descriptor) == HHS_EXACT_STATUS_OK);
    CHECK(descriptor.cell_count == 81U);
    CHECK(descriptor.bank_count == 9U);
    CHECK(descriptor.cells_per_bank == 9U);
    CHECK(descriptor.peers_per_cell == 20U);
    CHECK(descriptor.directed_graph_edges == 1620U);
    CHECK(descriptor.lane_count == 4U);
    CHECK(descriptor.phase_modulus == 72U);
    CHECK(descriptor.update_quantum == 5U);
    CHECK(descriptor.nested_loshu_tensor == 1U);
    CHECK(descriptor.sudoku_knowledge_graph == 1U);
    CHECK(descriptor.reciprocal_phase_gear == 1U);
    CHECK(descriptor.local_cell_learning == 1U);
    CHECK(descriptor.bank_learning == 1U);
    CHECK(descriptor.hash216_driven_routing == 1U);
    CHECK(descriptor.cpp_rna_cell_wall_composable == 1U);
    CHECK(descriptor.vm81_abi_carrier == 1U);
    CHECK(descriptor.candidate_only == 1U);
    CHECK(descriptor.canonical_mutation_authority == 0U);
    CHECK(descriptor.canonical_hash72_authority == 0U);
    CHECK(descriptor.canonical_hash216_authority == 0U);
    CHECK(descriptor.canonical_persistence_authority == 0U);
    CHECK(descriptor.floating_point_authority == 0U);

    CHECK(hhs_exact_pass219_holo4_state_init(&state_a) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_holo4_validate_state(&state_a) == HHS_EXACT_STATUS_OK);
    state_b = state_a;

    CHECK(hhs_exact_pass219_holo4_prepare(
              &frame, &transition, &state_a, &prepared_a) == HHS_EXACT_STATUS_OK);
    CHECK(prepared_a.word_visits == 81U);
    CHECK(prepared_a.graph_edge_visits == 1620U);
    CHECK(prepared_a.all_cells_have_20_peers == 1U);
    CHECK(prepared_a.reciprocal_phase_closure == 1U);
    CHECK(prepared_a.nested_loshu_complete == 1U);
    CHECK(prepared_a.hash216_positions_complete == 1U);
    CHECK(prepared_a.candidate_only == 1U);
    CHECK(prepared_a.canonical_mutation_authority == 0U);
    CHECK(prepared_a.canonical_hash72_authority == 0U);
    CHECK(prepared_a.canonical_hash216_authority == 0U);
    CHECK(prepared_a.canonical_persistence_authority == 0U);
    CHECK(prepared_a.floating_point_authority == 0U);

    for (i = 0U; i < HHS_EXACT_PASS219_HOLO4_CELL_COUNT; ++i) {
        const HHSExactPass219Holo4CellV1 *cell = &prepared_a.cells[i];
        const unsigned peers = popcount64(cell->peer_mask_lo64) + popcount64(cell->peer_mask_hi17);
        CHECK(cell->cell81 == i);
        CHECK(cell->row9 == i / 9U);
        CHECK(cell->column9 == i % 9U);
        CHECK(cell->peer_count == 20U);
        CHECK(peers == 20U);
        CHECK(cell->local_loshu >= 1U && cell->local_loshu <= 9U);
        CHECK(cell->macro_loshu >= 1U && cell->macro_loshu <= 9U);
        CHECK(cell->phase_basis < HHS_EXACT_PHASE_BASIS_COUNT);
        CHECK(cell->reciprocal_basis < HHS_EXACT_PHASE_BASIS_COUNT);
        CHECK(((uint32_t)cell->phase72 + (uint32_t)cell->reciprocal_phase72) % 72U == 0U);
        if (i < 64U)
            CHECK((cell->peer_mask_lo64 & (UINT64_C(1) << i)) == 0U);
        else
            CHECK((cell->peer_mask_hi17 & (UINT64_C(1) << (i - 64U))) == 0U);
        for (lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane)
            CHECK(cell->hash216_position[lane] < HHS_EXACT_PASS219_HASH216_OCCURRENCES);
        graph_edges += cell->peer_count;
    }
    CHECK(graph_edges == HHS_EXACT_PASS219_HOLO4_DIRECTED_GRAPH_EDGES);

    for (lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane)
        CHECK(hhs_exact_pass219_holo4_score_lane(
                  &prepared_a, &state_a, (uint8_t)lane, &lanes[lane]) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_holo4_finalize(
              &prepared_a, lanes, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              &state_a, &decision_a) == HHS_EXACT_STATUS_OK);

    CHECK(hhs_exact_pass219_holo4_route(
              &frame, &transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              &state_b, &prepared_b, &decision_b) == HHS_EXACT_STATUS_OK);
    CHECK(prepared_a.graph_signature64 == prepared_b.graph_signature64);
    CHECK(prepared_a.tensor_signature64 == prepared_b.tensor_signature64);
    CHECK(decision_a.selected_lane == decision_b.selected_lane);
    CHECK(decision_a.decision_signature64 == decision_b.decision_signature64);
    CHECK(decision_a.update_count == decision_b.update_count);
    CHECK(decision_a.step_count == decision_b.step_count);
    for (lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
        CHECK(decision_a.lanes[lane].score == decision_b.lanes[lane].score);
        CHECK(decision_a.lanes[lane].routing_signature64 == decision_b.lanes[lane].routing_signature64);
    }
    CHECK(memcmp(&state_a, &state_b, sizeof(state_a)) == 0);

    CHECK(hhs_exact_pass219_holo4_prepare(
              &frame, &transition_other, &state_b, &prepared_other_identity) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(prepared_a.source_transition_identity216,
                 prepared_other_identity.source_transition_identity216,
                 HHS_EXACT_UQCEL_HASH216_STRLEN) != 0);
    CHECK(prepared_a.tensor_signature64 != prepared_other_identity.tensor_signature64 ||
          prepared_a.graph_signature64 != prepared_other_identity.graph_signature64);

    CHECK(hhs_exact_pass219_holo4_score_lane(
              &prepared_a, &state_a, 4U, &lanes[0]) == HHS_EXACT_STATUS_RANGE_ERROR);
    CHECK(hhs_exact_pass219_holo4_route(
              &frame, &transition, 4U, 1, &state_b, &prepared_b, &decision_b) ==
          HHS_EXACT_STATUS_RANGE_ERROR);
    CHECK(hhs_exact_pass219_holo4_route(
              &frame, &transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 1,
              &state_b, &prepared_b, &decision_b) == HHS_EXACT_STATUS_RANGE_ERROR);

    return 0;
}
