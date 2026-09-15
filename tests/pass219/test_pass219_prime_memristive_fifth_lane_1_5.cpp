#include "hhs_pass219_prime_memristive_fifth_lane_1_5.hpp"

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
    CHECK(hhs_pass219_prime_lane_neighborhood_replay_authority_valid(
        PrimeLaneNeighborhoodReplayAuthorityV6{}));

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

    constexpr std::uint64_t root = UINT64_C(0x6100000000000001);
    constexpr std::uint64_t child = UINT64_C(0x6100000000000002);
    const auto root_text_route = make_route(root, UINT64_C(0x6101), {0U, 1U, 2U});
    const auto child_vision_route = make_route(child, UINT64_C(0x6102), {64U, 63U, 62U});

    PrimeLaneMultimodalContextRouterV5 router{};
    CHECK(router.register_context(root, 0U, HHS_PASS219_PRIME_LANE_MODALITY_ALL));
    CHECK(router.register_context(
        child, root,
        static_cast<std::uint8_t>(HHS_PASS219_PRIME_LANE_MODALITY_TEXT |
                                  HHS_PASS219_PRIME_LANE_MODALITY_VISION)));
    CHECK(router.register_route(root, root_text_route, HHS_PASS219_PRIME_LANE_MODALITY_TEXT));
    CHECK(router.register_route(child, child_vision_route, HHS_PASS219_PRIME_LANE_MODALITY_VISION));
    CHECK(router.observe_route(root, root_text_route.composition_signature64,
                               HHS_PASS219_PRIME_LANE_MODALITY_TEXT, 300, 1, 10U));
    CHECK(router.observe_route(child, child_vision_route.composition_signature64,
                               HHS_PASS219_PRIME_LANE_MODALITY_VISION, 500, 1, 11U));
    PrimeLaneInheritedRouteSelectionV5 inherited{};
    CHECK(router.select_route(child, HHS_PASS219_PRIME_LANE_MODALITY_TEXT, inherited));
    CHECK(inherited.source_context_signature64 == root);
    CHECK(inherited.inheritance_distance == 1U);

    PrimeLaneHash216NeighborhoodStoreV6 store{};
    PrimeLaneHash216NeighborhoodRefV6 text_neighborhood{};
    CHECK(store.bind(
        inherited.source_context_signature64,
        inherited.route.route.composition_signature64,
        HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
        target_canonical, 100U, text_neighborhood));
    CHECK(text_neighborhood.members.size() == 1U);
    CHECK(text_neighborhood.members[0].alias_cardinality ==
          target_canonical.states[0].record_ids.size());

    const std::uint32_t other_id = target_id == 128U ? 129U : 128U;
    PrimeLaneHash216AliasGroupV3 other_group{};
    CHECK(graph.alias_group_for_record(other_id, other_group));
    CHECK(other_group.identity216 != target_canonical.states[0].identity216);
    PrimeLaneCanonicalCandidateResultV3 vision_canonical = target_canonical;
    vision_canonical.states.push_back(other_group);
    vision_canonical.unique_hash216_count = 2U;

    PrimeLaneHash216NeighborhoodRefV6 vision_neighborhood{};
    CHECK(store.bind(
        child, child_vision_route.composition_signature64,
        HHS_PASS219_PRIME_LANE_MODALITY_VISION,
        vision_canonical, 101U, vision_neighborhood));
    CHECK(vision_neighborhood.members.size() == 2U);

    PrimeLaneHash216NeighborhoodRefV6 composed{};
    PrimeLaneNeighborhoodRecallMetricsV6 compose_metrics{};
    CHECK(store.compose(
        {vision_neighborhood, text_neighborhood},
        static_cast<std::uint8_t>(HHS_PASS219_PRIME_LANE_MODALITY_TEXT |
                                  HHS_PASS219_PRIME_LANE_MODALITY_VISION),
        composed, compose_metrics));
    CHECK(compose_metrics.composed_reference_inputs == 2U);
    CHECK(compose_metrics.duplicate_identities_collapsed == 1U);
    CHECK(composed.members.size() == 2U);

    PrimeLaneHash216NeighborhoodRefV6 warm{};
    PrimeLaneNeighborhoodRecallMetricsV6 warm_metrics{};
    CHECK(store.recall(
        root, root_text_route.composition_signature64,
        HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
        warm, warm_metrics));
    CHECK(same_identity_set(warm, target_canonical));

    PrimeLaneReplayAssociationKeyV6 replay_key{};
    replay_key.query_context_signature64 = child;
    replay_key.source_context_signature64 = root;
    replay_key.composition_signature64 = root_text_route.composition_signature64;
    replay_key.neighborhood_binding_signature64 = text_neighborhood.binding_signature64;
    replay_key.modality_mask = HHS_PASS219_PRIME_LANE_MODALITY_TEXT;

    std::vector<PrimeLaneReplayEventV6> events{};
    for (std::uint64_t sequence = 1U; sequence <= 3U; ++sequence) {
        PrimeLaneReplayEventV6 event{};
        event.key = replay_key;
        event.admission_feedback_trinary = sequence < 3U ? 1 : -1;
        event.warm_reference_work = static_cast<std::uint32_t>(text_neighborhood.members.size());
        event.cold_posting_work = target_raw.posting_entries_examined;
        event.sequence = sequence;
        events.push_back(event);
    }

    PrimeLaneAdaptiveReplayLedgerV6 ledger{};
    std::array<PrimeLaneReplayReceiptV6, 3> receipts{};
    CHECK(ledger.apply(events[0], receipts[0]));
    CHECK(receipts[0].after_weight > 0);
    CHECK(ledger.apply(events[1], receipts[1]));
    CHECK(receipts[1].after_weight > receipts[0].after_weight);
    CHECK(ledger.apply(events[2], receipts[2]));
    CHECK(receipts[2].after_weight < receipts[1].after_weight);
    CHECK(!ledger.reverse_last(receipts[0]));
    CHECK(ledger.reverse_last(receipts[2]));
    CHECK(ledger.weight_for(replay_key) == receipts[1].after_weight);
    PrimeLaneReplayReceiptV6 replayed_tip{};
    CHECK(ledger.apply(events[2], replayed_tip));
    CHECK(replayed_tip.receipt_signature64 == receipts[2].receipt_signature64);

    PrimeLaneAdaptiveReplayLedgerV6 replay_copy{};
    PrimeLaneReplayReceiptV6 copy_receipt{};
    for (const auto& event : events)
        CHECK(replay_copy.apply(event, copy_receipt));
    CHECK(replay_copy.weight_for(replay_key) == ledger.weight_for(replay_key));
    CHECK(replay_copy.tip_signature64() == ledger.tip_signature64());

    std::uint64_t repeated_warm = 0U;
    std::uint64_t warm_reference_reads = 0U;
    std::uint64_t cold_posting_work = 0U;
    for (std::uint32_t iteration = 0U; iteration < 16U; ++iteration) {
        PrimeLaneHash216NeighborhoodRefV6 recalled{};
        PrimeLaneNeighborhoodRecallMetricsV6 metrics{};
        CHECK(store.recall(
            root, root_text_route.composition_signature64,
            HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
            recalled, metrics));
        PrimeLaneCandidateResultV2 cold_raw{};
        PrimeLaneCanonicalCandidateResultV3 cold_canonical{};
        CHECK(graph.query(target_decision, 1U, cold_raw, cold_canonical));
        CHECK(same_identity_set(recalled, cold_canonical));
        ++repeated_warm;
        warm_reference_reads += metrics.inherited_reference_reads;
        cold_posting_work += cold_raw.posting_entries_examined;
    }
    CHECK(repeated_warm == 16U);
    CHECK(warm_reference_reads < cold_posting_work);

    PrimeLaneHash216AliasGroupV3 alias_after{};
    CHECK(graph.alias_group_for_record(0U, alias_after));
    CHECK(alias_after.identity216 == alias_before.identity216);
    CHECK(alias_after.identity_signature64 == alias_before.identity_signature64);
    CHECK(alias_after.record_ids == alias_before.record_ids);
    CHECK(std::memcmp(&holo4_state, &frozen_holo4_state, sizeof(holo4_state)) == 0);

    CHECK(!text_neighborhood.authority.canonical_mutation_authority);
    CHECK(!text_neighborhood.authority.canonical_hash72_authority);
    CHECK(!text_neighborhood.authority.canonical_hash216_authority);
    CHECK(!text_neighborhood.authority.canonical_persistence_authority);

    std::printf(
        "lane5_i6=PASS target=%u inherited_distance=%u neighborhood_members=%zu "
        "composed_members=%zu duplicate_collapsed=%llu replay_receipts=%zu "
        "replay_weight=%d repeated_warm=%llu warm_reference_reads=%llu "
        "cold_posting_work=%llu alias_records=%zu unique_hash216=%zu\n",
        target_id,
        static_cast<unsigned>(inherited.inheritance_distance),
        text_neighborhood.members.size(),
        composed.members.size(),
        static_cast<unsigned long long>(compose_metrics.duplicate_identities_collapsed),
        ledger.receipt_count(),
        ledger.weight_for(replay_key),
        static_cast<unsigned long long>(repeated_warm),
        static_cast<unsigned long long>(warm_reference_reads),
        static_cast<unsigned long long>(cold_posting_work),
        alias_after.record_ids.size(),
        graph.unique_hash216_count());
    return 0;
}
