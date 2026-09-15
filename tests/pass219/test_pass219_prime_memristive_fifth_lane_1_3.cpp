#include "hhs_pass219_prime_memristive_fifth_lane_1_3.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

using hhs::rna::PrimeLaneAdaptiveContextRouterV4;
using hhs::rna::PrimeLaneAdaptiveQueryResultV4;
using hhs::rna::PrimeLaneCandidateResultV2;
using hhs::rna::PrimeLaneCanonicalCandidateResultV3;
using hhs::rna::PrimeLaneContextRouteCacheV3;
using hhs::rna::PrimeLaneContextRouteV3;
using hhs::rna::PrimeLaneHash216AliasGroupV3;
using hhs::rna::PrimeLaneHash216CandidateGraphV3;
using hhs::rna::PrimeLaneHash216ReferenceBinderV3;
using hhs::rna::PrimeLaneLinearResultV2;
using hhs::rna::PrimeLanePreparedRecordV2;
using hhs::rna::PrimeLaneRouteDecisionV1;
using hhs::rna::PrimeLaneRoutePlanCacheV2;
using hhs::rna::PrimeLaneRoutePlanV2;
using hhs::rna::PrimeLaneRouteUtilityV4;
using hhs::rna::PrimeMemristiveFifthLaneV1;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

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

static std::array<char, HHS_EXACT_UQCEL_HASH216_STRLEN>
identity_for(std::uint32_t record_id) {
    std::array<char, HHS_EXACT_UQCEL_HASH216_STRLEN> out{};
    std::uint32_t key = record_id;
    if (record_id == 18U)
        key = 17U; // deliberate two-record alias
    for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i * 13U + 7U) % HHS_EXACT_HASH72_LEN];
    out[0] = HHS_EXACT_HASH72_ALPHABET[key % HHS_EXACT_HASH72_LEN];
    key /= HHS_EXACT_HASH72_LEN;
    out[1] = HHS_EXACT_HASH72_ALPHABET[key % HHS_EXACT_HASH72_LEN];
    key /= HHS_EXACT_HASH72_LEN;
    out[2] = HHS_EXACT_HASH72_ALPHABET[key % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    return out;
}

static bool parity_with_linear(
    const PrimeLaneHash216CandidateGraphV3& graph,
    const PrimeLaneAdaptiveQueryResultV4& result,
    std::uint64_t expected_records) {
    PrimeLaneLinearResultV2 linear{};
    if (!graph.linear_scan(result.decision, result.raw.axes_used, linear))
        return false;
    return linear.record_visits == expected_records &&
           linear.record_ids == result.raw.record_ids;
}

int main() {
    constexpr std::uint32_t corpus_size = 4096U;
    std::vector<hhs::rna::PrimeLaneBoundRecordV3> bound{};
    bound.reserve(corpus_size);
    for (std::uint32_t document = 0U; document < corpus_size; ++document) {
        PrimeLanePreparedRecordV2 record{};
        record.record_id = document;
        record.cells = synthetic_cells(document);
        record.fingerprint = PrimeMemristiveFifthLaneV1::fingerprint(record.cells);
        const auto identity = identity_for(document);
        record.source_transition_signature64 =
            PrimeLaneHash216ReferenceBinderV3::identity_signature64(identity.data());
        hhs::rna::PrimeLaneBoundRecordV3 linked{};
        CHECK(PrimeLaneHash216ReferenceBinderV3::bind_reference(
            record, identity.data(), linked));
        bound.push_back(linked);
    }

    PrimeLaneHash216CandidateGraphV3 graph{};
    CHECK(graph.build(bound));
    CHECK(graph.record_count() == corpus_size);
    CHECK(graph.unique_hash216_count() == corpus_size - 1U);

    PrimeLaneHash216AliasGroupV3 alias_before{};
    CHECK(graph.alias_group_for_record(17U, alias_before));
    CHECK(alias_before.record_ids.size() == 2U);
    CHECK(alias_before.record_ids[0] == 17U);
    CHECK(alias_before.record_ids[1] == 18U);

    const auto baseline = PrimeMemristiveFifthLaneV1::initial_state();
    auto learned_state = baseline;
    learned_state.conductance[0] = 15;
    learned_state.conductance[1] = 10;
    learned_state.conductance[2] = 5;

    std::uint32_t target_id = corpus_size;
    PrimeLaneRouteDecisionV1 learned_route{};
    PrimeLaneRouteDecisionV1 low_route{};
    PrimeLaneCandidateResultV2 learned_raw{};
    PrimeLaneCanonicalCandidateResultV3 learned_canonical{};
    PrimeLaneCandidateResultV2 low_raw{};
    PrimeLaneCanonicalCandidateResultV3 low_canonical{};

    for (std::uint32_t candidate = 0U; candidate < corpus_size; ++candidate) {
        const auto& fingerprint = bound[candidate].indexed.fingerprint;
        PrimeLaneRouteDecisionV1 candidate_learned{};
        PrimeLaneRouteDecisionV1 candidate_low{};
        CHECK(PrimeMemristiveFifthLaneV1::route(
                  fingerprint, learned_state, 3U, candidate_learned) ==
              hhs::rna::PrimeLaneStatusV1::OK);
        CHECK(PrimeMemristiveFifthLaneV1::route(
                  fingerprint, learned_state, 1U, candidate_low) ==
              hhs::rna::PrimeLaneStatusV1::OK);
        PrimeLaneCandidateResultV2 candidate_learned_raw{};
        PrimeLaneCanonicalCandidateResultV3 candidate_learned_canonical{};
        PrimeLaneCandidateResultV2 candidate_low_raw{};
        PrimeLaneCanonicalCandidateResultV3 candidate_low_canonical{};
        CHECK(graph.query(candidate_learned, 1U,
                          candidate_learned_raw, candidate_learned_canonical));
        CHECK(graph.query(candidate_low, 1U,
                          candidate_low_raw, candidate_low_canonical));
        if (candidate_learned_raw.candidate_budget_reached &&
            candidate_learned_raw.record_ids.size() == 1U &&
            !candidate_low_raw.candidate_budget_reached) {
            target_id = candidate;
            learned_route = candidate_learned;
            low_route = candidate_low;
            learned_raw = candidate_learned_raw;
            learned_canonical = candidate_learned_canonical;
            low_raw = candidate_low_raw;
            low_canonical = candidate_low_canonical;
            break;
        }
    }
    CHECK(target_id < corpus_size);
    CHECK(learned_route.prime[0] == 5U);
    CHECK(learned_route.prime[1] == 7U);
    CHECK(learned_route.prime[2] == 11U);
    CHECK(low_route.prime[0] == 5U);
    CHECK(learned_raw.record_ids[0] == target_id);
    CHECK(!low_raw.candidate_budget_reached);
    (void)learned_canonical;
    (void)low_canonical;

    const auto& query_fingerprint = bound[target_id].indexed.fingerprint;
    PrimeLaneRouteDecisionV1 neutral_route{};
    CHECK(PrimeMemristiveFifthLaneV1::route(
              query_fingerprint, baseline, 1U, neutral_route) ==
          hhs::rna::PrimeLaneStatusV1::OK);
    CHECK(neutral_route.prime[0] == 331U);

    const PrimeLaneRoutePlanV2 learned_plan =
        PrimeLaneRoutePlanCacheV2::plan_from(learned_route);
    const PrimeLaneRoutePlanV2 neutral_plan =
        PrimeLaneRoutePlanCacheV2::plan_from(neutral_route);
    const PrimeLaneRoutePlanV2 low_plan =
        PrimeLaneRoutePlanCacheV2::plan_from(low_route);

    constexpr std::uint64_t good_context = UINT64_C(0x21940001);
    constexpr std::uint64_t insufficient_context = UINT64_C(0x21940002);
    PrimeLaneContextRouteCacheV3 learned_cache{};
    PrimeLaneContextRouteCacheV3 neutral_cache{};
    PrimeLaneContextRouteCacheV3 low_cache{};
    PrimeLaneContextRouteV3 learned_context_route{};
    PrimeLaneContextRouteV3 neutral_context_route{};
    PrimeLaneContextRouteV3 low_context_route{};
    CHECK(learned_cache.compose_and_store(
        good_context, {learned_plan}, learned_context_route));
    CHECK(neutral_cache.compose_and_store(
        good_context, {neutral_plan}, neutral_context_route));
    CHECK(low_cache.compose_and_store(
        insufficient_context, {low_plan}, low_context_route));

    PrimeLaneAdaptiveContextRouterV4 adaptive{};
    CHECK(adaptive.register_route(learned_context_route));
    CHECK(adaptive.register_route(neutral_context_route));
    CHECK(adaptive.register_route(low_context_route));
    CHECK(adaptive.route_count(good_context) == 2U);
    CHECK(adaptive.route_count(insufficient_context) == 1U);

    // Strengthen the successful learned route and give the alternate route a poor admission history.
    CHECK(adaptive.observe(
        good_context, learned_context_route.composition_signature64,
        corpus_size, static_cast<std::uint32_t>(learned_raw.record_ids.size()),
        learned_raw.posting_entries_examined, 1, 10U));
    CHECK(adaptive.observe(
        good_context, neutral_context_route.composition_signature64,
        corpus_size, corpus_size, corpus_size, -1, 10U));

    PrimeLaneRouteUtilityV4 selected{};
    std::uint64_t examined = 0U;
    std::uint64_t stale = 0U;
    CHECK(adaptive.select_route(good_context, 10U, 100U, selected, examined, stale));
    CHECK(examined == 2U);
    CHECK(stale == 0U);
    CHECK(selected.route.composition_signature64 ==
          learned_context_route.composition_signature64);

    // Two explicit bad observations weaken the learned route below the alternate.
    CHECK(adaptive.observe(
        good_context, learned_context_route.composition_signature64,
        corpus_size, corpus_size, corpus_size, -1, 11U));
    CHECK(adaptive.observe(
        good_context, learned_context_route.composition_signature64,
        corpus_size, corpus_size, corpus_size, -1, 12U));
    CHECK(adaptive.select_route(good_context, 12U, 100U, selected, examined, stale));
    CHECK(selected.route.composition_signature64 ==
          neutral_context_route.composition_signature64);

    // Two successful observations recover the learned route deterministically.
    CHECK(adaptive.observe(
        good_context, learned_context_route.composition_signature64,
        corpus_size, static_cast<std::uint32_t>(learned_raw.record_ids.size()),
        learned_raw.posting_entries_examined, 1, 13U));
    CHECK(adaptive.observe(
        good_context, learned_context_route.composition_signature64,
        corpus_size, static_cast<std::uint32_t>(learned_raw.record_ids.size()),
        learned_raw.posting_entries_examined, 1, 14U));
    CHECK(adaptive.select_route(good_context, 14U, 100U, selected, examined, stale));
    CHECK(selected.route.composition_signature64 ==
          learned_context_route.composition_signature64);

    PrimeLaneRouteUtilityV4 utility_before_decay{};
    CHECK(adaptive.utility_for(
        good_context, learned_context_route.composition_signature64,
        utility_before_decay));
    const std::int32_t magnitude_before = std::abs(utility_before_decay.utility_q10);
    CHECK(adaptive.decay_context(good_context, 100U));
    PrimeLaneRouteUtilityV4 utility_after_decay{};
    CHECK(adaptive.utility_for(
        good_context, learned_context_route.composition_signature64,
        utility_after_decay));
    CHECK(std::abs(utility_after_decay.utility_q10) <= magnitude_before);
    CHECK(utility_after_decay.utility_q10 <= hhs::rna::HHS_PASS219_PRIME_LANE_WEIGHT_BOUND);
    CHECK(utility_after_decay.utility_q10 >= -hhs::rna::HHS_PASS219_PRIME_LANE_WEIGHT_BOUND);

    HHSExactPass219Holo4StateV1 holo4_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&holo4_state) == HHS_EXACT_STATUS_OK);
    const HHSExactPass219Holo4StateV1 frozen_holo4_state = holo4_state;

    std::uint64_t repeated_warm = 0U;
    std::uint64_t warm_selector_avoided = 0U;
    for (std::uint32_t repetition = 0U; repetition < 16U; ++repetition) {
        PrimeLaneAdaptiveQueryResultV4 result{};
        CHECK(adaptive.query_with_fallback(
            graph, good_context, query_fingerprint, baseline,
            8U, 1U, 14U, 100U, result));
        CHECK(result.used_warm_route);
        CHECK(!result.used_cold_fallback);
        CHECK(result.selected_composition_signature64 ==
              learned_context_route.composition_signature64);
        CHECK(result.raw.record_ids == learned_raw.record_ids);
        CHECK(parity_with_linear(graph, result, corpus_size));
        ++repeated_warm;
        warm_selector_avoided += result.metrics.warm_selector_evaluations_avoided;
    }
    CHECK(repeated_warm == 16U);
    CHECK(warm_selector_avoided ==
          16U * PrimeLaneContextRouteCacheV3::cold_selector_evaluations(3U));

    // Missing context must deterministically fall back to inherited cold selection.
    PrimeLaneAdaptiveQueryResultV4 missing{};
    CHECK(adaptive.query_with_fallback(
        graph, UINT64_C(0xdeadbeef), query_fingerprint, baseline,
        8U, 1U, 14U, 100U, missing));
    CHECK(!missing.used_warm_route);
    CHECK(missing.used_cold_fallback);
    CHECK(missing.metrics.fallback_count == 1U);
    CHECK(parity_with_linear(graph, missing, corpus_size));

    // Both good-context routes have observation history and are stale at this sequence.
    PrimeLaneAdaptiveQueryResultV4 stale_result{};
    CHECK(adaptive.query_with_fallback(
        graph, good_context, query_fingerprint, baseline,
        8U, 1U, 1000U, 5U, stale_result));
    CHECK(stale_result.used_cold_fallback);
    CHECK(stale_result.metrics.stale_rejections == 2U);
    CHECK(parity_with_linear(graph, stale_result, corpus_size));

    // A warm p=5-only route cannot reach budget=1 and must fall back to cold routing.
    CHECK(adaptive.observe(
        insufficient_context, low_context_route.composition_signature64,
        corpus_size, static_cast<std::uint32_t>(low_raw.record_ids.size()),
        low_raw.posting_entries_examined, 1, 20U));
    PrimeLaneAdaptiveQueryResultV4 insufficient{};
    CHECK(adaptive.query_with_fallback(
        graph, insufficient_context, query_fingerprint, baseline,
        8U, 1U, 20U, 100U, insufficient));
    CHECK(insufficient.used_cold_fallback);
    CHECK(!insufficient.used_warm_route);
    CHECK(insufficient.metrics.insufficient_reduction_fallbacks == 1U);
    CHECK(parity_with_linear(graph, insufficient, corpus_size));

    PrimeLaneHash216AliasGroupV3 alias_after{};
    CHECK(graph.alias_group_for_record(17U, alias_after));
    CHECK(alias_after.identity216 == alias_before.identity216);
    CHECK(alias_after.record_ids == alias_before.record_ids);
    CHECK(std::memcmp(&holo4_state, &frozen_holo4_state, sizeof(holo4_state)) == 0);
    CHECK(hhs::rna::hhs_pass219_prime_lane_adaptive_authority_valid(
        utility_after_decay.authority));
    CHECK(!utility_after_decay.authority.canonical_mutation_authority);
    CHECK(!utility_after_decay.authority.canonical_hash72_authority);
    CHECK(!utility_after_decay.authority.canonical_hash216_authority);
    CHECK(!utility_after_decay.authority.canonical_persistence_authority);

    std::printf(
        "lane5_i4=PASS target=%u repeated_warm=%llu warm_selector_avoided=%llu "
        "missing_fallback=%llu stale_fallback=%llu reduction_fallback=%llu "
        "alias_records=%zu unique_hash216=%zu\n",
        target_id,
        static_cast<unsigned long long>(repeated_warm),
        static_cast<unsigned long long>(warm_selector_avoided),
        static_cast<unsigned long long>(missing.metrics.fallback_count),
        static_cast<unsigned long long>(stale_result.metrics.fallback_count),
        static_cast<unsigned long long>(insufficient.metrics.insufficient_reduction_fallbacks),
        alias_after.record_ids.size(),
        graph.unique_hash216_count());
    return 0;
}
