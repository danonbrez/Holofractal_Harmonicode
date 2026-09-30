#include "hhs_pass219_prime_memristive_fifth_lane_1_1.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>

using hhs::rna::PrimeLaneCandidateIndexV2;
using hhs::rna::PrimeLaneCandidateResultV2;
using hhs::rna::PrimeLaneHolo4AdapterV2;
using hhs::rna::PrimeLaneLinearResultV2;
using hhs::rna::PrimeLanePreparedRecordV2;
using hhs::rna::PrimeLaneRoutePlanCacheV2;
using hhs::rna::PrimeLaneRoutePlanV2;
using hhs::rna::PrimeMemristiveFifthLaneV1;

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
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i * 13U + offset) % HHS_EXACT_HASH72_LEN];
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

static HHSExactVM81Frame build_frame(std::uint64_t salt) {
    HHSExactVM81Frame frame{};
    for (std::uint32_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        const std::uint64_t v =
            (UINT64_C(0xd6e8feb86659fd93) ^ salt) * static_cast<std::uint64_t>(i + 1U);
        frame.words[i] = v ^ (UINT64_C(1) << (i % 63U)) ^ (salt << (i % 7U));
    }
    return frame;
}

static std::array<std::int64_t, hhs::rna::HHS_PASS219_PRIME_LANE_CELL_COUNT>
synthetic_cells(std::uint32_t document) {
    std::array<std::int64_t, hhs::rna::HHS_PASS219_PRIME_LANE_CELL_COUNT> cells{};
    const std::uint64_t base =
        (static_cast<std::uint64_t>(document) + UINT64_C(1)) * UINT64_C(0x9e3779b97f4a7c15);
    for (std::size_t i = 0U; i < cells.size(); ++i) {
        std::uint64_t z = base + (i + 1U) * UINT64_C(0xbf58476d1ce4e5b9);
        z ^= z >> 30U;
        z *= UINT64_C(0xbf58476d1ce4e5b9);
        z ^= z >> 27U;
        z *= UINT64_C(0x94d049bb133111eb);
        z ^= z >> 31U;
        cells[i] = static_cast<std::int64_t>(z & UINT64_C(0x7fffffffffffffff));
    }
    return cells;
}

int main() {
    const HHSExactVM81Frame frame = build_frame(UINT64_C(0x219511));
    const HHSExactPass219Hash216TransitionViewV1 transition = build_transition(23U);
    HHSExactPass219Holo4StateV1 holo4_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&holo4_state) == HHS_EXACT_STATUS_OK);
    HHSExactPass219Holo4PreparedV1 prepared{};
    CHECK(hhs_exact_pass219_holo4_prepare(
              &frame, &transition, &holo4_state, &prepared) == HHS_EXACT_STATUS_OK);

    const PrimeLanePreparedRecordV2 adapted_a = PrimeLaneHolo4AdapterV2::adapt(17U, prepared);
    const PrimeLanePreparedRecordV2 adapted_b = PrimeLaneHolo4AdapterV2::adapt(17U, prepared);
    CHECK(adapted_a.record_id == 17U);
    CHECK(adapted_a.source_transition_signature64 != 0U);
    CHECK(adapted_a.cells == adapted_b.cells);
    CHECK(adapted_a.fingerprint.fingerprint_signature64 == adapted_b.fingerprint.fingerprint_signature64);
    CHECK(hhs::rna::hhs_pass219_prime_lane_index_authority_valid(adapted_a.authority));
    CHECK(hhs::rna::hhs_pass219_prime_lane_authority_valid(adapted_a.fingerprint.authority));

    constexpr std::uint32_t corpus_size = 4096U;
    constexpr std::uint32_t target_id = 1234U;
    std::vector<PrimeLanePreparedRecordV2> records{};
    records.reserve(corpus_size);
    for (std::uint32_t document = 0U; document < corpus_size; ++document) {
        PrimeLanePreparedRecordV2 record{};
        record.record_id = document;
        record.source_transition_signature64 = UINT64_C(0x2195000000000000) | document;
        record.cells = synthetic_cells(document);
        record.fingerprint = PrimeMemristiveFifthLaneV1::fingerprint(record.cells);
        records.push_back(record);
    }

    PrimeLaneCandidateIndexV2 index{};
    CHECK(index.build(records));
    CHECK(index.record_count() == corpus_size);
    CHECK(index.posting_key_count() > corpus_size);

    const auto& query_fingerprint = records[target_id].fingerprint;

    auto neutral_state = PrimeMemristiveFifthLaneV1::initial_state();
    HHSExactPass219Holo4StateV1 frozen_holo4_state = holo4_state;
    hhs::rna::PrimeLaneRouteDecisionV1 neutral_route{};
    CHECK(PrimeMemristiveFifthLaneV1::route(
              query_fingerprint, neutral_state, 8U, neutral_route) ==
          hhs::rna::PrimeLaneStatusV1::OK);
    CHECK(neutral_route.selected_count == 8U);
    CHECK(neutral_route.prime[0] == 331U);

    PrimeLaneCandidateResultV2 neutral_indexed{};
    CHECK(index.query(neutral_route, 8U, neutral_indexed));
    CHECK(neutral_indexed.axes_used >= 1U);
    CHECK(neutral_indexed.candidate_budget_reached);
    CHECK(neutral_indexed.record_ids.size() <= 8U);

    PrimeLaneLinearResultV2 neutral_linear{};
    CHECK(index.linear_scan(neutral_route, neutral_indexed.axes_used, neutral_linear));
    CHECK(neutral_indexed.record_ids == neutral_linear.record_ids);
    CHECK(std::find(neutral_indexed.record_ids.begin(), neutral_indexed.record_ids.end(), target_id) !=
          neutral_indexed.record_ids.end());
    CHECK(neutral_indexed.posting_entries_examined < neutral_linear.record_visits);

    auto learned_state = PrimeMemristiveFifthLaneV1::initial_state();
    learned_state.conductance[0] = 15;
    learned_state.conductance[1] = 10;
    learned_state.conductance[2] = 5;
    hhs::rna::PrimeLaneRouteDecisionV1 learned_route{};
    CHECK(PrimeMemristiveFifthLaneV1::route(
              query_fingerprint, learned_state, 3U, learned_route) ==
          hhs::rna::PrimeLaneStatusV1::OK);
    CHECK(learned_route.selected_count == 3U);
    CHECK(learned_route.prime[0] == 5U);
    CHECK(learned_route.prime[1] == 7U);
    CHECK(learned_route.prime[2] == 11U);

    PrimeLaneCandidateResultV2 learned_indexed{};
    CHECK(index.query(learned_route, 1U, learned_indexed));
    CHECK(learned_indexed.axes_used == 3U);
    CHECK(learned_indexed.candidate_budget_reached);
    CHECK(learned_indexed.record_ids.size() == 1U);
    CHECK(learned_indexed.record_ids[0] == target_id);

    PrimeLaneLinearResultV2 learned_linear{};
    CHECK(index.linear_scan(learned_route, learned_indexed.axes_used, learned_linear));
    CHECK(learned_indexed.record_ids == learned_linear.record_ids);
    CHECK(learned_indexed.posting_entries_examined < learned_linear.record_visits);

    const PrimeLaneRoutePlanV2 plan = PrimeLaneRoutePlanCacheV2::plan_from(learned_route);
    PrimeLaneRoutePlanCacheV2 cache{};
    CHECK(cache.store(plan));
    CHECK(cache.size() == 1U);
    PrimeLaneRoutePlanV2 replayed_plan{};
    CHECK(cache.fetch(plan.plan_signature64, replayed_plan));
    CHECK(replayed_plan.selected_count == plan.selected_count);
    CHECK(replayed_plan.fibre_index == plan.fibre_index);
    CHECK(hhs::rna::hhs_pass219_prime_lane_index_authority_valid(replayed_plan.authority));

    auto candidate_state = learned_state;
    CHECK(PrimeMemristiveFifthLaneV1::apply_feedback(
              learned_state, learned_route, 1, candidate_state) ==
          hhs::rna::PrimeLaneStatusV1::OK);
    CHECK(candidate_state.conductance[0] == 20);
    CHECK(candidate_state.conductance[1] == 15);
    CHECK(candidate_state.conductance[2] == 10);
    CHECK(std::memcmp(&holo4_state, &frozen_holo4_state, sizeof(holo4_state)) == 0);
    CHECK(!candidate_state.authority.canonical_mutation_authority);
    CHECK(!candidate_state.authority.canonical_hash72_authority);
    CHECK(!candidate_state.authority.canonical_hash216_authority);
    CHECK(!candidate_state.authority.canonical_persistence_authority);

    std::printf(
        "lane5_i2=PASS neutral_axes=%u neutral_postings=%llu linear_records=%llu "
        "learned_axes=%u learned_postings=%llu learned_linear_records=%llu\n",
        static_cast<unsigned>(neutral_indexed.axes_used),
        static_cast<unsigned long long>(neutral_indexed.posting_entries_examined),
        static_cast<unsigned long long>(neutral_linear.record_visits),
        static_cast<unsigned>(learned_indexed.axes_used),
        static_cast<unsigned long long>(learned_indexed.posting_entries_examined),
        static_cast<unsigned long long>(learned_linear.record_visits));
    return 0;
}
