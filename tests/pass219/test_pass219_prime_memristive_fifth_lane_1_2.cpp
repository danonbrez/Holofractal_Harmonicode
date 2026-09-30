#include "hhs_pass219_prime_memristive_fifth_lane_1_2.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>

using hhs::rna::PrimeLaneBoundRecordV3;
using hhs::rna::PrimeLaneCandidateResultV2;
using hhs::rna::PrimeLaneCanonicalCandidateResultV3;
using hhs::rna::PrimeLaneContextRouteCacheV3;
using hhs::rna::PrimeLaneContextRouteV3;
using hhs::rna::PrimeLaneHash216AliasGroupV3;
using hhs::rna::PrimeLaneHash216CandidateGraphV3;
using hhs::rna::PrimeLaneHash216ReferenceBinderV3;
using hhs::rna::PrimeLaneHolo4AdapterV2;
using hhs::rna::PrimeLaneLinearResultV2;
using hhs::rna::PrimeLanePreparedRecordV2;
using hhs::rna::PrimeLaneRoutePlanCacheV2;
using hhs::rna::PrimeLaneRoutePlanV2;
using hhs::rna::PrimeLaneRouterStateV1;
using hhs::rna::PrimeLaneWarmRouteMetricsV3;
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

static void fill_identity216(char out[HHS_EXACT_UQCEL_HASH216_STRLEN], std::uint32_t seed) {
    for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i * 13U + 17U) % HHS_EXACT_HASH72_LEN];
    out[0] = HHS_EXACT_HASH72_ALPHABET[seed % HHS_EXACT_HASH72_LEN];
    out[1] = HHS_EXACT_HASH72_ALPHABET[(seed / HHS_EXACT_HASH72_LEN) % HHS_EXACT_HASH72_LEN];
    out[2] = HHS_EXACT_HASH72_ALPHABET[
        (seed / (HHS_EXACT_HASH72_LEN * HHS_EXACT_HASH72_LEN)) % HHS_EXACT_HASH72_LEN];
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
    fill_identity216(identity, static_cast<std::uint32_t>(offset + 3U));
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
    const HHSExactVM81Frame frame = build_frame(UINT64_C(0x219512));
    const HHSExactPass219Hash216TransitionViewV1 transition = build_transition(29U);
    HHSExactPass219Holo4StateV1 holo4_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&holo4_state) == HHS_EXACT_STATUS_OK);
    const HHSExactPass219Holo4StateV1 frozen_holo4_state = holo4_state;
    HHSExactPass219Holo4PreparedV1 prepared{};
    CHECK(hhs_exact_pass219_holo4_prepare(
              &frame, &transition, &holo4_state, &prepared) == HHS_EXACT_STATUS_OK);

    const PrimeLanePreparedRecordV2 adapted = PrimeLaneHolo4AdapterV2::adapt(17U, prepared);
    PrimeLaneBoundRecordV3 adapted_bound{};
    CHECK(PrimeLaneHash216ReferenceBinderV3::bind_transition(
        adapted, transition, adapted_bound));
    CHECK(adapted_bound.indexed.record_id == 17U);
    CHECK(adapted_bound.hash216.record_id == 17U);
    CHECK(std::memcmp(
        adapted_bound.hash216.identity216.data(),
        transition.transition_identity216,
        HHS_EXACT_UQCEL_HASH216_STRLEN) == 0);
    CHECK(adapted_bound.hash216.identity_signature64 == adapted.source_transition_signature64);
    CHECK(hhs::rna::hhs_pass219_prime_lane_context_authority_valid(adapted_bound.authority));

    char mismatched_identity[HHS_EXACT_UQCEL_HASH216_STRLEN]{};
    std::memcpy(mismatched_identity, transition.transition_identity216, sizeof(mismatched_identity));
    mismatched_identity[0] =
        (mismatched_identity[0] == HHS_EXACT_HASH72_ALPHABET[0])
            ? HHS_EXACT_HASH72_ALPHABET[1]
            : HHS_EXACT_HASH72_ALPHABET[0];
    PrimeLaneBoundRecordV3 rejected{};
    CHECK(!PrimeLaneHash216ReferenceBinderV3::bind_reference(
        adapted, mismatched_identity, rejected));

    constexpr std::uint32_t corpus_size = 4096U;
    constexpr std::uint32_t target_id = 1234U;
    constexpr std::uint32_t alias_id = 2345U;
    std::vector<PrimeLaneBoundRecordV3> records{};
    records.reserve(corpus_size);

    for (std::uint32_t document = 0U; document < corpus_size; ++document) {
        PrimeLanePreparedRecordV2 record{};
        record.record_id = document;
        record.cells = synthetic_cells(document);
        record.fingerprint = PrimeMemristiveFifthLaneV1::fingerprint(record.cells);

        char identity[HHS_EXACT_UQCEL_HASH216_STRLEN]{};
        const std::uint32_t identity_seed = (document == alias_id) ? target_id : document;
        fill_identity216(identity, identity_seed);
        record.source_transition_signature64 =
            PrimeLaneHash216ReferenceBinderV3::identity_signature64(identity);
        CHECK(record.source_transition_signature64 != 0U);

        PrimeLaneBoundRecordV3 bound{};
        CHECK(PrimeLaneHash216ReferenceBinderV3::bind_reference(record, identity, bound));
        records.push_back(bound);
    }

    PrimeLaneHash216CandidateGraphV3 graph{};
    CHECK(graph.build(records));
    CHECK(graph.record_count() == corpus_size);
    CHECK(graph.unique_hash216_count() == corpus_size - 1U);
    CHECK(graph.posting_key_count() > corpus_size);

    PrimeLaneHash216AliasGroupV3 alias_group{};
    CHECK(graph.alias_group_for_record(target_id, alias_group));
    CHECK(alias_group.record_ids.size() == 2U);
    CHECK(alias_group.record_ids[0] == target_id);
    CHECK(alias_group.record_ids[1] == alias_id);

    const auto& query_fingerprint = records[target_id].indexed.fingerprint;
    auto learned_state = PrimeMemristiveFifthLaneV1::initial_state();
    learned_state.conductance[0] = 15;
    learned_state.conductance[1] = 10;
    learned_state.conductance[2] = 5;

    hhs::rna::PrimeLaneRouteDecisionV1 cold_route{};
    CHECK(PrimeMemristiveFifthLaneV1::route(
              query_fingerprint, learned_state, 3U, cold_route) ==
          hhs::rna::PrimeLaneStatusV1::OK);
    CHECK(cold_route.selected_count == 3U);
    CHECK(cold_route.prime[0] == 5U);
    CHECK(cold_route.prime[1] == 7U);
    CHECK(cold_route.prime[2] == 11U);

    PrimeLaneCandidateResultV2 cold_raw{};
    PrimeLaneCanonicalCandidateResultV3 cold_canonical{};
    CHECK(graph.query(cold_route, 1U, cold_raw, cold_canonical));
    CHECK(cold_raw.axes_used == 3U);
    CHECK(cold_raw.record_ids.size() == 1U);
    CHECK(cold_raw.record_ids[0] == target_id);
    CHECK(cold_canonical.raw_record_count == 1U);
    CHECK(cold_canonical.unique_hash216_count == 1U);
    CHECK(cold_canonical.states.size() == 1U);
    CHECK(cold_canonical.states[0].record_ids.size() == 2U);
    CHECK(cold_canonical.states[0].record_ids[0] == target_id);
    CHECK(cold_canonical.states[0].record_ids[1] == alias_id);

    PrimeLaneLinearResultV2 linear{};
    CHECK(graph.linear_scan(cold_route, cold_raw.axes_used, linear));
    CHECK(cold_raw.record_ids == linear.record_ids);

    const PrimeLaneRoutePlanV2 learned_plan = PrimeLaneRoutePlanCacheV2::plan_from(cold_route);
    PrimeLaneContextRouteCacheV3 context_cache{};
    constexpr std::uint64_t warm_context = UINT64_C(0x2195000000000003);
    PrimeLaneContextRouteV3 single_context{};
    CHECK(context_cache.compose_and_store(
        warm_context, std::vector<PrimeLaneRoutePlanV2>{learned_plan}, single_context));
    CHECK(single_context.selected_count == 3U);

    hhs::rna::PrimeLaneRouteDecisionV1 warm_route{};
    PrimeLaneWarmRouteMetricsV3 warm_metrics{};
    CHECK(context_cache.decision_for(
        warm_context, query_fingerprint, warm_route, warm_metrics));
    CHECK(warm_route.selected_count == cold_route.selected_count);
    for (std::size_t i = 0U; i < warm_route.selected_count; ++i) {
        CHECK(warm_route.fibre_index[i] == cold_route.fibre_index[i]);
        CHECK(warm_route.prime[i] == cold_route.prime[i]);
        CHECK(warm_route.u[i] == cold_route.u[i]);
        CHECK(warm_route.v[i] == cold_route.v[i]);
        CHECK(warm_route.rho[i] == cold_route.rho[i]);
    }
    CHECK(warm_metrics.context_cache_lookups == 1U);
    CHECK(warm_metrics.axis_materializations == 3U);
    CHECK(warm_metrics.cold_selector_evaluations_avoided == 192U);

    PrimeLaneCandidateResultV2 warm_raw{};
    PrimeLaneCanonicalCandidateResultV3 warm_canonical{};
    CHECK(graph.query(warm_route, 1U, warm_raw, warm_canonical));
    CHECK(warm_raw.record_ids == cold_raw.record_ids);
    CHECK(warm_canonical.unique_hash216_count == cold_canonical.unique_hash216_count);
    CHECK(warm_canonical.states[0].identity216 == cold_canonical.states[0].identity216);
    CHECK(warm_canonical.states[0].record_ids == cold_canonical.states[0].record_ids);

    auto neutral_state = PrimeMemristiveFifthLaneV1::initial_state();
    hhs::rna::PrimeLaneRouteDecisionV1 neutral_route{};
    CHECK(PrimeMemristiveFifthLaneV1::route(
              query_fingerprint, neutral_state, 2U, neutral_route) ==
          hhs::rna::PrimeLaneStatusV1::OK);
    const PrimeLaneRoutePlanV2 neutral_plan = PrimeLaneRoutePlanCacheV2::plan_from(neutral_route);

    constexpr std::uint64_t composed_context = UINT64_C(0x2195000000000005);
    PrimeLaneContextRouteV3 composed_a{};
    PrimeLaneContextRouteV3 composed_b{};
    CHECK(context_cache.compose_and_store(
        composed_context,
        std::vector<PrimeLaneRoutePlanV2>{learned_plan, neutral_plan},
        composed_a));
    CHECK(context_cache.compose_and_store(
        composed_context,
        std::vector<PrimeLaneRoutePlanV2>{neutral_plan, learned_plan},
        composed_b));
    CHECK(composed_a.selected_count == 5U);
    CHECK(composed_a.selected_count == composed_b.selected_count);
    CHECK(composed_a.fibre_index == composed_b.fibre_index);
    CHECK(composed_a.composition_signature64 == composed_b.composition_signature64);

    PrimeLaneContextRouteV3 replayed_context{};
    CHECK(context_cache.fetch(composed_context, replayed_context));
    CHECK(replayed_context.fibre_index == composed_a.fibre_index);
    CHECK(replayed_context.composition_signature64 == composed_a.composition_signature64);

    PrimeLaneRouterStateV1 seeded{};
    CHECK(context_cache.seed_router_state(warm_context, neutral_state, 5, seeded));
    CHECK(seeded.conductance[0] == 15);
    CHECK(seeded.conductance[1] == 10);
    CHECK(seeded.conductance[2] == 5);
    CHECK(!seeded.authority.canonical_mutation_authority);
    CHECK(!seeded.authority.canonical_hash72_authority);
    CHECK(!seeded.authority.canonical_hash216_authority);
    CHECK(!seeded.authority.canonical_persistence_authority);

    hhs::rna::PrimeLaneRouteDecisionV1 seeded_route{};
    CHECK(PrimeMemristiveFifthLaneV1::route(
              query_fingerprint, seeded, 3U, seeded_route) ==
          hhs::rna::PrimeLaneStatusV1::OK);
    CHECK(seeded_route.prime[0] == 5U);
    CHECK(seeded_route.prime[1] == 7U);
    CHECK(seeded_route.prime[2] == 11U);

    CHECK(std::memcmp(&holo4_state, &frozen_holo4_state, sizeof(holo4_state)) == 0);
    CHECK(hhs::rna::hhs_pass219_prime_lane_context_authority_valid(cold_canonical.authority));
    CHECK(hhs::rna::hhs_pass219_prime_lane_context_authority_valid(warm_canonical.authority));

    std::printf(
        "lane5_i3=PASS cold_axes=%u cold_postings=%llu linear_records=%llu "
        "warm_cache=%llu warm_axes=%llu cold_selector_evals=%llu "
        "alias_raw=%u alias_records=%zu unique_hash216=%u context_axes=%u\n",
        static_cast<unsigned>(cold_raw.axes_used),
        static_cast<unsigned long long>(cold_raw.posting_entries_examined),
        static_cast<unsigned long long>(linear.record_visits),
        static_cast<unsigned long long>(warm_metrics.context_cache_lookups),
        static_cast<unsigned long long>(warm_metrics.axis_materializations),
        static_cast<unsigned long long>(warm_metrics.cold_selector_evaluations_avoided),
        static_cast<unsigned>(cold_canonical.raw_record_count),
        cold_canonical.states[0].record_ids.size(),
        static_cast<unsigned>(cold_canonical.unique_hash216_count),
        static_cast<unsigned>(composed_a.selected_count));
    return 0;
}
