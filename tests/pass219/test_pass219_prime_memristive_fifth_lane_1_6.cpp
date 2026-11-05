#include "hhs_pass219_prime_memristive_fifth_lane_1_6.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>

using namespace hhs::rna;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static std::array<std::int64_t, HHS_PASS219_PRIME_LANE_CELL_COUNT>
synthetic_cells(std::uint32_t document) {
    std::array<std::int64_t, HHS_PASS219_PRIME_LANE_CELL_COUNT> cells{};
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

static void fill_identity216(
    char out[HHS_EXACT_UQCEL_HASH216_STRLEN],
    std::uint32_t record_id) {
    std::uint32_t value = record_id;
    for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        std::uint32_t digit = 0U;
        if (i < 3U) {
            digit = value % HHS_EXACT_HASH72_LEN;
            value /= HHS_EXACT_HASH72_LEN;
        } else {
            digit = static_cast<std::uint32_t>((i * 17U + 29U) % HHS_EXACT_HASH72_LEN);
        }
        out[i] = HHS_EXACT_HASH72_ALPHABET[digit];
    }
    out[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
}

static PrimeLaneRouteDecisionV1 decision_for(
    const PrimeLaneFingerprintV1& fingerprint,
    std::initializer_list<std::uint8_t> fibres) {
    PrimeLaneRouteDecisionV1 decision{};
    decision.selected_count = static_cast<std::uint8_t>(fibres.size());
    std::size_t slot = 0U;
    for (const std::uint8_t fibre : fibres) {
        const auto& coordinate = fingerprint.fibres[fibre];
        decision.fibre_index[slot] = fibre;
        decision.prime[slot] = coordinate.prime;
        decision.u[slot] = coordinate.u;
        decision.v[slot] = coordinate.v;
        decision.rho[slot] = coordinate.rho;
        ++slot;
    }
    return decision;
}

static PrimeLaneContextRouteV3 make_route(
    std::uint64_t context,
    std::uint64_t composition,
    std::initializer_list<std::uint8_t> fibres) {
    PrimeLaneContextRouteV3 route{};
    route.context_signature64 = context;
    route.component_plan_count = 1U;
    route.selected_count = static_cast<std::uint8_t>(fibres.size());
    std::size_t slot = 0U;
    for (const std::uint8_t fibre : fibres)
        route.fibre_index[slot++] = fibre;
    route.composition_signature64 = composition;
    return route;
}

static bool same_identity_set(
    const PrimeLaneHash216NeighborhoodRefV6& neighborhood,
    const PrimeLaneCanonicalCandidateResultV3& canonical) {
    if (neighborhood.members.size() != canonical.states.size())
        return false;
    for (const auto& member : neighborhood.members) {
        bool found = false;
        for (const auto& state : canonical.states) {
            if (member.identity216 == state.identity216 &&
                member.identity_signature64 == state.identity_signature64) {
                found = true;
                break;
            }
        }
        if (!found)
            return false;
    }
    return true;
}

int main() {
    CHECK(HHS_EXACT_PASS219_HOLO4_LANE_COUNT == 4U);
    CHECK(hhs_pass219_prime_lane_replay_prefetch_authority_valid(
        PrimeLaneReplayPrefetchAuthorityV7{}));

    HHSExactPass219Holo4StateV1 holo4_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&holo4_state) == HHS_EXACT_STATUS_OK);
    const HHSExactPass219Holo4StateV1 frozen_holo4_state = holo4_state;

    constexpr std::uint32_t corpus_size = 4096U;
    std::vector<PrimeLaneBoundRecordV3> bound{};
    bound.reserve(corpus_size);
    for (std::uint32_t record_id = 0U; record_id < corpus_size; ++record_id) {
        PrimeLanePreparedRecordV2 record{};
        record.record_id = record_id;
        record.cells = synthetic_cells(record_id);
        record.fingerprint = PrimeMemristiveFifthLaneV1::fingerprint(record.cells);
        char identity[HHS_EXACT_UQCEL_HASH216_STRLEN]{};
        fill_identity216(identity, record_id == 1U ? 0U : record_id);
        record.source_transition_signature64 =
            PrimeLaneHash216ReferenceBinderV3::identity_signature64(identity);
        CHECK(record.source_transition_signature64 != 0U);
        PrimeLaneBoundRecordV3 item{};
        CHECK(PrimeLaneHash216ReferenceBinderV3::bind_reference(record, identity, item));
        bound.push_back(item);
    }

    PrimeLaneHash216CandidateGraphV3 graph{};
    CHECK(graph.build(bound));
    CHECK(graph.record_count() == corpus_size);
    CHECK(graph.unique_hash216_count() == corpus_size - 1U);

    PrimeLaneHash216AliasGroupV3 alias_before{};
    CHECK(graph.alias_group_for_record(0U, alias_before));
    CHECK(alias_before.record_ids.size() == 2U);

    std::uint32_t target_id = corpus_size;
    PrimeLaneCandidateResultV2 target_raw{};
    PrimeLaneCanonicalCandidateResultV3 target_canonical{};
    PrimeLaneRouteDecisionV1 target_decision{};
    for (std::uint32_t record_id = 0U; record_id < corpus_size; ++record_id) {
        const auto& fp = bound[record_id].indexed.fingerprint;
        const auto one_axis = decision_for(fp, {0U});
        const auto three_axis = decision_for(fp, {0U, 1U, 2U});
        PrimeLaneCandidateResultV2 one_raw{};
        PrimeLaneCanonicalCandidateResultV3 one_canonical{};
        PrimeLaneCandidateResultV2 three_raw{};
        PrimeLaneCanonicalCandidateResultV3 three_canonical{};
        CHECK(graph.query(one_axis, 1U, one_raw, one_canonical));
        CHECK(graph.query(three_axis, 1U, three_raw, three_canonical));
        if (!one_raw.candidate_budget_reached && three_raw.candidate_budget_reached &&
            three_raw.record_ids.size() == 1U && three_raw.record_ids[0] == record_id) {
            target_id = record_id;
            target_raw = three_raw;
            target_canonical = three_canonical;
            target_decision = three_axis;
            break;
        }
    }
    CHECK(target_id < corpus_size);
    CHECK(target_canonical.states.size() == 1U);

    constexpr std::uint64_t root = UINT64_C(0x7100000000000001);
    constexpr std::uint64_t child = UINT64_C(0x7100000000000002);
    const auto root_route = make_route(root, UINT64_C(0x7101), {0U, 1U, 2U});
    const auto alternate_route = make_route(child, UINT64_C(0x7102), {3U, 4U, 5U});
    const auto vision_route = make_route(child, UINT64_C(0x7103), {64U, 63U, 62U});

    PrimeLaneMultimodalContextRouterV5 hierarchy{};
    CHECK(hierarchy.register_context(root, 0U, HHS_PASS219_PRIME_LANE_MODALITY_ALL));
    CHECK(hierarchy.register_context(
        child, root,
        static_cast<std::uint8_t>(HHS_PASS219_PRIME_LANE_MODALITY_TEXT |
                                  HHS_PASS219_PRIME_LANE_MODALITY_VISION)));
    CHECK(hierarchy.register_route(root, root_route, HHS_PASS219_PRIME_LANE_MODALITY_TEXT));
    CHECK(hierarchy.observe_route(root, root_route.composition_signature64,
                                  HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                                  300, 1, 10U));
    PrimeLaneInheritedRouteSelectionV5 inherited{};
    CHECK(hierarchy.select_route(child, HHS_PASS219_PRIME_LANE_MODALITY_TEXT, inherited));
    CHECK(inherited.source_context_signature64 == root);
    CHECK(inherited.inheritance_distance == 1U);

    PrimeLaneHash216NeighborhoodStoreV6 store{};
    PrimeLaneHash216NeighborhoodRefV6 target_neighborhood{};
    CHECK(store.bind(root, root_route.composition_signature64,
                     HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                     target_canonical, 100U, target_neighborhood));
    CHECK(same_identity_set(target_neighborhood, target_canonical));

    const std::uint32_t alternate_id = target_id == 128U ? 129U : 128U;
    PrimeLaneHash216AliasGroupV3 alternate_group{};
    CHECK(graph.alias_group_for_record(alternate_id, alternate_group));
    CHECK(alternate_group.identity216 != target_canonical.states[0].identity216);
    PrimeLaneCanonicalCandidateResultV3 alternate_canonical{};
    alternate_canonical.states.push_back(alternate_group);
    alternate_canonical.raw_record_count = 1U;
    alternate_canonical.unique_hash216_count = 1U;
    PrimeLaneHash216NeighborhoodRefV6 alternate_neighborhood{};
    CHECK(store.bind(child, alternate_route.composition_signature64,
                     HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                     alternate_canonical, 101U, alternate_neighborhood));

    const std::uint32_t vision_id = target_id == 256U || alternate_id == 256U ? 257U : 256U;
    PrimeLaneHash216AliasGroupV3 vision_group{};
    CHECK(graph.alias_group_for_record(vision_id, vision_group));
    PrimeLaneCanonicalCandidateResultV3 vision_canonical{};
    vision_canonical.states.push_back(vision_group);
    vision_canonical.raw_record_count = 1U;
    vision_canonical.unique_hash216_count = 1U;
    PrimeLaneHash216NeighborhoodRefV6 vision_neighborhood{};
    CHECK(store.bind(child, vision_route.composition_signature64,
                     HHS_PASS219_PRIME_LANE_MODALITY_VISION,
                     vision_canonical, 102U, vision_neighborhood));

    PrimeLaneReplayAssociationKeyV6 target_key{};
    target_key.query_context_signature64 = child;
    target_key.source_context_signature64 = root;
    target_key.composition_signature64 = root_route.composition_signature64;
    target_key.neighborhood_binding_signature64 = target_neighborhood.binding_signature64;
    target_key.modality_mask = HHS_PASS219_PRIME_LANE_MODALITY_TEXT;

    PrimeLaneReplayAssociationKeyV6 alternate_key{};
    alternate_key.query_context_signature64 = child;
    alternate_key.source_context_signature64 = child;
    alternate_key.composition_signature64 = alternate_route.composition_signature64;
    alternate_key.neighborhood_binding_signature64 = alternate_neighborhood.binding_signature64;
    alternate_key.modality_mask = HHS_PASS219_PRIME_LANE_MODALITY_TEXT;

    PrimeLaneReplayAssociationKeyV6 vision_key{};
    vision_key.query_context_signature64 = child;
    vision_key.source_context_signature64 = child;
    vision_key.composition_signature64 = vision_route.composition_signature64;
    vision_key.neighborhood_binding_signature64 = vision_neighborhood.binding_signature64;
    vision_key.modality_mask = HHS_PASS219_PRIME_LANE_MODALITY_VISION;

    PrimeLaneAdaptiveReplayLedgerV6 replay{};
    for (std::uint64_t sequence = 1U; sequence <= 3U; ++sequence) {
        PrimeLaneReplayEventV6 event{};
        event.key = target_key;
        event.admission_feedback_trinary = sequence < 3U ? 1 : -1;
        event.warm_reference_work = static_cast<std::uint32_t>(target_neighborhood.members.size());
        event.cold_posting_work = target_raw.posting_entries_examined;
        event.sequence = sequence;
        PrimeLaneReplayReceiptV6 receipt{};
        CHECK(replay.apply(event, receipt));
    }
    CHECK(replay.weight_for(target_key) == 192);

    PrimeLaneReplayConditionedPrefetchV7 prefetch{};
    CHECK(prefetch.register_target(target_key, target_neighborhood));
    CHECK(prefetch.register_target(alternate_key, alternate_neighborhood));
    CHECK(prefetch.register_target(vision_key, vision_neighborhood));
    CHECK(prefetch.target_count() == 3U);

    const std::uint64_t current_binding = target_neighborhood.binding_signature64;
    CHECK(prefetch.observe_transition(current_binding, target_key, 1, 1U));
    CHECK(prefetch.observe_transition(current_binding, alternate_key, 1, 1U));
    CHECK(prefetch.observe_transition(current_binding, alternate_key, 1, 2U));
    CHECK(prefetch.observe_transition(current_binding, vision_key, 1, 1U));
    CHECK(prefetch.observe_transition(current_binding, vision_key, 1, 2U));
    CHECK(prefetch.observe_transition(current_binding, vision_key, 1, 3U));
    CHECK(prefetch.observe_transition(current_binding, vision_key, 1, 4U));
    CHECK(prefetch.transition_count() == 3U);

    std::vector<PrimeLanePrefetchCandidateV7> ranked{};
    PrimeLanePrefetchMetricsV7 rank_metrics{};
    CHECK(prefetch.prefetch(current_binding,
                            HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                            replay, 2U, ranked, rank_metrics));
    CHECK(ranked.size() == 2U);
    CHECK(rank_metrics.modality_rejections == 1U);
    CHECK(ranked[0].neighborhood.binding_signature64 == target_neighborhood.binding_signature64);
    CHECK(ranked[0].transition.transition_weight == 128);
    CHECK(ranked[0].replay_weight == 192);
    CHECK(ranked[0].prefetch_score == 320);
    CHECK(ranked[1].neighborhood.binding_signature64 == alternate_neighborhood.binding_signature64);
    CHECK(ranked[1].prefetch_score == 256);
    const std::uint64_t deterministic_rank_signature = rank_metrics.ranking_signature64;
    CHECK(deterministic_rank_signature != 0U);

    std::uint64_t repeated_prefetch = 0U;
    std::uint64_t warm_reference_reads = 0U;
    std::uint64_t cold_posting_work = 0U;
    for (std::uint32_t iteration = 0U; iteration < 16U; ++iteration) {
        std::vector<PrimeLanePrefetchCandidateV7> one{};
        PrimeLanePrefetchMetricsV7 metrics{};
        CHECK(prefetch.prefetch(current_binding,
                                HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                                replay, 1U, one, metrics));
        CHECK(one.size() == 1U);
        CHECK(one[0].neighborhood.binding_signature64 == target_neighborhood.binding_signature64);
        CHECK(metrics.ranking_signature64 != 0U);
        PrimeLaneCandidateResultV2 cold_raw{};
        PrimeLaneCanonicalCandidateResultV3 cold_canonical{};
        CHECK(graph.query(target_decision, 1U, cold_raw, cold_canonical));
        CHECK(same_identity_set(one[0].neighborhood, cold_canonical));
        ++repeated_prefetch;
        warm_reference_reads += metrics.inherited_reference_reads;
        cold_posting_work += cold_raw.posting_entries_examined;
    }
    CHECK(repeated_prefetch == 16U);
    CHECK(warm_reference_reads < cold_posting_work);

    CHECK(prefetch.observe_transition(current_binding, target_key, -1, 2U));
    CHECK(prefetch.observe_transition(current_binding, target_key, -1, 3U));
    ranked.clear();
    rank_metrics = PrimeLanePrefetchMetricsV7{};
    CHECK(prefetch.prefetch(current_binding,
                            HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                            replay, 1U, ranked, rank_metrics));
    CHECK(ranked.size() == 1U);
    CHECK(ranked[0].neighborhood.binding_signature64 == alternate_neighborhood.binding_signature64);
    CHECK(ranked[0].prefetch_score == 256);
    CHECK(prefetch.target_count() == 3U);

    ranked.clear();
    rank_metrics = PrimeLanePrefetchMetricsV7{};
    CHECK(prefetch.prefetch(current_binding,
                            HHS_PASS219_PRIME_LANE_MODALITY_VISION,
                            replay, 1U, ranked, rank_metrics));
    CHECK(ranked.size() == 1U);
    CHECK(ranked[0].neighborhood.binding_signature64 == vision_neighborhood.binding_signature64);
    CHECK(rank_metrics.modality_rejections == 2U);

    PrimeLanePredictiveQueryResultV7 fallback{};
    const std::uint64_t unknown_binding = current_binding ^ UINT64_C(0xa5a5a5a5a5a5a5a5);
    CHECK(unknown_binding != 0U && unknown_binding != current_binding);
    CHECK(prefetch.query_with_fallback(
        unknown_binding, HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
        replay, 1U, graph, target_decision, 1U, fallback));
    CHECK(!fallback.used_prefetch);
    CHECK(fallback.used_cold_fallback);
    CHECK(fallback.metrics.cold_fallbacks == 1U);
    CHECK(fallback.cold_raw.record_ids.size() == 1U);
    CHECK(fallback.cold_raw.record_ids[0] == target_id);
    CHECK(same_identity_set(target_neighborhood, fallback.cold_canonical));

    PrimeLaneHash216AliasGroupV3 alias_after{};
    CHECK(graph.alias_group_for_record(0U, alias_after));
    CHECK(alias_after.identity216 == alias_before.identity216);
    CHECK(alias_after.identity_signature64 == alias_before.identity_signature64);
    CHECK(alias_after.record_ids == alias_before.record_ids);
    CHECK(std::memcmp(&holo4_state, &frozen_holo4_state, sizeof(holo4_state)) == 0);

    CHECK(!fallback.authority.canonical_mutation_authority);
    CHECK(!fallback.authority.canonical_hash72_authority);
    CHECK(!fallback.authority.canonical_hash216_authority);
    CHECK(!fallback.authority.canonical_persistence_authority);

    std::printf(
        "lane5_i7=PASS target=%u inherited_distance=%u replay_weight=%d "
        "initial_prefetch_score=%d demoted_prefetch_score=%d transitions=%zu "
        "repeated_prefetch=%llu warm_reference_reads=%llu cold_posting_work=%llu "
        "modality_rejections=%llu fallbacks=%llu alias_records=%zu unique_hash216=%zu\n",
        target_id,
        static_cast<unsigned>(inherited.inheritance_distance),
        replay.weight_for(target_key),
        320,
        256,
        prefetch.transition_count(),
        static_cast<unsigned long long>(repeated_prefetch),
        static_cast<unsigned long long>(warm_reference_reads),
        static_cast<unsigned long long>(cold_posting_work),
        static_cast<unsigned long long>(rank_metrics.modality_rejections),
        static_cast<unsigned long long>(fallback.metrics.cold_fallbacks),
        alias_after.record_ids.size(),
        graph.unique_hash216_count());

    return 0;
}
