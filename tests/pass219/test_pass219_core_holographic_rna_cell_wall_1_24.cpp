#include "hhs_pass219_core_holographic_rna_cell_wall_1_24.hpp"

#include <cstdint>
#include <cstdio>
#include <cstring>

using hhs::rna::CoreHolographicRNACellWall;
using hhs::rna::OrthogonalGlyphMembrane;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static void fill_hash72(char out[HHS_EXACT_HASH72_STRLEN], std::uint8_t offset) {
    for (std::size_t i = 0U; i < HHS_EXACT_HASH72_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

static void fill_identity216(char out[HHS_EXACT_UQCEL_HASH216_STRLEN], std::uint8_t offset) {
    for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i * 11U + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
}

static HHSExactPass219Hash216TransitionViewV1 build_transition(std::uint8_t offset) {
    HHSExactPass219Hash216TransitionViewV1 transition{};
    char previous[HHS_EXACT_HASH72_STRLEN]{};
    char change[HHS_EXACT_HASH72_STRLEN]{};
    char receipt[HHS_EXACT_HASH72_STRLEN]{};
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN]{};
    fill_hash72(previous, offset);
    fill_hash72(change, static_cast<std::uint8_t>(offset + 1U));
    fill_hash72(receipt, static_cast<std::uint8_t>(offset + 2U));
    fill_identity216(identity, static_cast<std::uint8_t>(offset + 3U));
    if (hhs_exact_pass219_hash216_transition_init(
            previous, change, receipt, identity, &transition) != HHS_EXACT_STATUS_OK)
        std::memset(&transition, 0, sizeof(transition));
    return transition;
}

static HHSExactVM81Frame build_frame() {
    HHSExactVM81Frame frame{};
    for (std::uint32_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        const std::uint64_t v = UINT64_C(0xd6e8feb86659fd93) * static_cast<std::uint64_t>(i + 1U);
        frame.words[i] = v ^ (UINT64_C(1) << (i % 63U));
    }
    return frame;
}

static bool same_decision(
    const HHSExactPass219Holo4DecisionV1& a,
    const HHSExactPass219Holo4DecisionV1& b
) {
    if (a.selected_lane != b.selected_lane ||
        a.feedback_lane != b.feedback_lane ||
        a.feedback_trinary != b.feedback_trinary ||
        a.updated != b.updated ||
        a.update_count != b.update_count ||
        a.step_count != b.step_count ||
        a.decision_signature64 != b.decision_signature64 ||
        std::memcmp(a.source_transition_identity216, b.source_transition_identity216,
                    HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
        return false;
    for (std::uint32_t lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
        if (a.lanes[lane].lane_id != b.lanes[lane].lane_id ||
            a.lanes[lane].score != b.lanes[lane].score ||
            a.lanes[lane].routing_signature64 != b.lanes[lane].routing_signature64)
            return false;
    }
    return true;
}

int main() {
    std::uint8_t one = 1U;
    HHSExactBigUIntView a2{
        static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)), 1U, &one};
    HHSExactBigUIntView delta{
        static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)), 1U, &one};
    OrthogonalGlyphMembrane membrane(a2, delta);
    CHECK(membrane.status() == HHS_EXACT_STATUS_OK);
    CoreHolographicRNACellWall wall(membrane);
    CHECK(wall.status() == HHS_EXACT_STATUS_OK);
    CHECK(&wall.membrane() == &membrane);

    const HHSExactVM81Frame frame = build_frame();
    const HHSExactPass219Hash216TransitionViewV1 transition = build_transition(9U);
    CHECK(transition.struct_size == sizeof(transition));

    HHSExactPass219Holo4StateV1 sequential_state{};
    HHSExactPass219Holo4StateV1 parallel_state{};
    HHSExactPass219Holo4PreparedV1 sequential_prepared{};
    HHSExactPass219Holo4PreparedV1 parallel_prepared{};
    HHSExactPass219Holo4DecisionV1 sequential_decision{};
    HHSExactPass219Holo4DecisionV1 parallel_decision{};

    CHECK(hhs_exact_pass219_holo4_state_init(&sequential_state) == HHS_EXACT_STATUS_OK);
    parallel_state = sequential_state;
    CHECK(hhs_exact_pass219_holo4_route(
              &frame, &transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              &sequential_state, &sequential_prepared, &sequential_decision) == HHS_EXACT_STATUS_OK);
    CHECK(wall.route_parallel(
              frame, transition, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              parallel_state, parallel_prepared, parallel_decision) == HHS_EXACT_STATUS_OK);
    CHECK(sequential_prepared.graph_signature64 == parallel_prepared.graph_signature64);
    CHECK(sequential_prepared.tensor_signature64 == parallel_prepared.tensor_signature64);
    CHECK(same_decision(sequential_decision, parallel_decision));
    CHECK(std::memcmp(&sequential_state, &parallel_state, sizeof(sequential_state)) == 0);

    const std::uint8_t target_lane = static_cast<std::uint8_t>(
        (sequential_decision.selected_lane + 1U) % HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
    CHECK(hhs_exact_pass219_holo4_route(
              &frame, &transition, target_lane, 1,
              &sequential_state, &sequential_prepared, &sequential_decision) == HHS_EXACT_STATUS_OK);
    CHECK(wall.route_parallel(
              frame, transition, target_lane, 1,
              parallel_state, parallel_prepared, parallel_decision) == HHS_EXACT_STATUS_OK);
    CHECK(same_decision(sequential_decision, parallel_decision));
    CHECK(std::memcmp(&sequential_state, &parallel_state, sizeof(sequential_state)) == 0);
    CHECK(sequential_decision.updated == 1U);
    CHECK(sequential_state.update_count == parallel_state.update_count);

    CHECK(hhs_exact_pass219_holo4_validate_state(&parallel_state) == HHS_EXACT_STATUS_OK);
    CHECK(parallel_decision.candidate_only == 1U);
    CHECK(parallel_decision.canonical_mutation_authority == 0U);
    CHECK(parallel_decision.canonical_hash72_authority == 0U);
    CHECK(parallel_decision.canonical_hash216_authority == 0U);
    CHECK(parallel_decision.canonical_persistence_authority == 0U);
    CHECK(parallel_decision.floating_point_authority == 0U);
    return 0;
}
