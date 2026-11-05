#include "hhs_pass219_prime_memristive_fifth_lane_1_4.hpp"

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
    const std::vector<std::uint8_t>& fibres) {
    PrimeLaneRouteDecisionV1 decision{};
    decision.selected_count = static_cast<std::uint8_t>(fibres.size());
    for (std::size_t slot = 0U; slot < fibres.size(); ++slot) {
        const std::size_t fibre = fibres[slot];
        const auto& coordinate = fingerprint.fibres[fibre];
        decision.fibre_index[slot] = fibres[slot];
        decision.prime[slot] = coordinate.prime;
        decision.u[slot] = coordinate.u;
        decision.v[slot] = coordinate.v;
        decision.rho[slot] = coordinate.rho;
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

int main() {
    CHECK(HHS_EXACT_PASS219_HOLO4_LANE_COUNT == 4U);
    CHECK(hhs_pass219_prime_lane_multimodal_authority_valid(
        PrimeLaneMultimodalContextAuthorityV5{}));

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
    CHECK(alias_before.record_ids[0] == 0U);
    CHECK(alias_before.record_ids[1] == 1U);

    std::uint32_t target_id = corpus_size;
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
        if (!one_raw.candidate_budget_reached &&
            three_raw.candidate_budget_reached &&
            three_raw.record_ids.size() == 1U &&
            three_raw.record_ids[0] == record_id) {
            target_id = record_id;
            break;
        }
    }
    CHECK(target_id < corpus_size);
    const auto& target_fp = bound[target_id].indexed.fingerprint;

    auto cold_state = PrimeMemristiveFifthLaneV1::initial_state();
    cold_state.conductance[0] = 15;
    cold_state.conductance[1] = 10;
    cold_state.conductance[2] = 5;
    PrimeLaneRouteDecisionV1 cold_target{};
    CHECK(PrimeMemristiveFifthLaneV1::route(
              target_fp, cold_state, 3U, cold_target) == PrimeLaneStatusV1::OK);
    CHECK(cold_target.prime[0] == 5U);
    CHECK(cold_target.prime[1] == 7U);
    CHECK(cold_target.prime[2] == 11U);

    constexpr std::uint64_t root = UINT64_C(0x5100000000000001);
    constexpr std::uint64_t text_child = UINT64_C(0x5100000000000002);
    constexpr std::uint64_t multi_child = UINT64_C(0x5100000000000003);
    constexpr std::uint64_t poor_child = UINT64_C(0x5100000000000004);

    const auto root_text_route = make_route(root, UINT64_C(0x5101), {0U, 1U, 2U});
    const auto child_vision_route = make_route(multi_child, UINT64_C(0x5102), {64U, 63U, 62U});
    const auto child_multimodal_route = make_route(multi_child, UINT64_C(0x5103), {0U, 1U, 2U});
    const auto poor_route = make_route(poor_child, UINT64_C(0x5104), {0U});

    PrimeLaneMultimodalContextRouterV5 router{};
    CHECK(router.register_context(root, 0U, HHS_PASS219_PRIME_LANE_MODALITY_ALL));
    CHECK(router.register_context(text_child, root, HHS_PASS219_PRIME_LANE_MODALITY_TEXT));
    CHECK(router.register_context(
        multi_child, root,
        static_cast<std::uint8_t>(HHS_PASS219_PRIME_LANE_MODALITY_TEXT |
                                  HHS_PASS219_PRIME_LANE_MODALITY_VISION)));
    CHECK(router.register_context(poor_child, root, HHS_PASS219_PRIME_LANE_MODALITY_TEXT));

    CHECK(router.register_route(root, root_text_route, HHS_PASS219_PRIME_LANE_MODALITY_TEXT));
    CHECK(router.register_route(
        multi_child, child_vision_route, HHS_PASS219_PRIME_LANE_MODALITY_VISION));
    CHECK(router.register_route(
        multi_child, child_multimodal_route,
        static_cast<std::uint8_t>(HHS_PASS219_PRIME_LANE_MODALITY_TEXT |
                                  HHS_PASS219_PRIME_LANE_MODALITY_VISION)));
    CHECK(router.register_route(poor_child, poor_route, HHS_PASS219_PRIME_LANE_MODALITY_TEXT));

    CHECK(router.observe_route(root, root_text_route.composition_signature64,
                               HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                               300, 0, 10U));
    CHECK(router.observe_route(multi_child, child_vision_route.composition_signature64,
                               HHS_PASS219_PRIME_LANE_MODALITY_VISION,
                               700, 0, 11U));
    CHECK(router.observe_route(
        multi_child, child_multimodal_route.composition_signature64,
        static_cast<std::uint8_t>(HHS_PASS219_PRIME_LANE_MODALITY_TEXT |
                                  HHS_PASS219_PRIME_LANE_MODALITY_VISION),
        400, 0, 12U));
    CHECK(router.observe_route(poor_child, poor_route.composition_signature64,
                               HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                               1500, 0, 13U));

    PrimeLaneInheritedRouteSelectionV5 inherited_text{};
    CHECK(router.select_route(
        text_child, HHS_PASS219_PRIME_LANE_MODALITY_TEXT, inherited_text));
    CHECK(inherited_text.source_context_signature64 == root);
    CHECK(inherited_text.inheritance_distance == 1U);
    CHECK(inherited_text.active_utility_q10 == 300);

    PrimeLaneInheritedRouteSelectionV5 vision_selection{};
    CHECK(router.select_route(
        multi_child, HHS_PASS219_PRIME_LANE_MODALITY_VISION, vision_selection));
    CHECK(vision_selection.source_context_signature64 == multi_child);
    CHECK(vision_selection.route.route.composition_signature64 ==
          child_vision_route.composition_signature64);
    CHECK(vision_selection.active_utility_q10 == 700);

    PrimeLaneInheritedRouteSelectionV5 multimodal_selection{};
    CHECK(router.select_route(
        multi_child,
        static_cast<std::uint8_t>(HHS_PASS219_PRIME_LANE_MODALITY_TEXT |
                                  HHS_PASS219_PRIME_LANE_MODALITY_VISION),
        multimodal_selection));
    CHECK(multimodal_selection.route.route.composition_signature64 ==
          child_multimodal_route.composition_signature64);
    CHECK(multimodal_selection.active_utility_q10 == 800);

    CHECK(router.set_tombstone(
        text_child, root, root_text_route.composition_signature64, 20U,
        PrimeLaneRouteTombstoneReasonV5::NEGATIVE_FEEDBACK));
    CHECK(router.tombstoned(text_child, root, root_text_route.composition_signature64));
    PrimeLaneInheritedRouteSelectionV5 tombstoned_child{};
    CHECK(!router.select_route(
        text_child, HHS_PASS219_PRIME_LANE_MODALITY_TEXT, tombstoned_child));
    PrimeLaneInheritedRouteSelectionV5 root_still_live{};
    CHECK(router.select_route(root, HHS_PASS219_PRIME_LANE_MODALITY_TEXT, root_still_live));
    CHECK(root_still_live.source_context_signature64 == root);
    CHECK(router.clear_tombstone(
        text_child, root, root_text_route.composition_signature64, 21U));
    CHECK(!router.tombstoned(text_child, root, root_text_route.composition_signature64));
    CHECK(router.select_route(
        text_child, HHS_PASS219_PRIME_LANE_MODALITY_TEXT, inherited_text));

    PrimeLaneHierarchicalQueryResultV5 inherited_query{};
    CHECK(router.query_with_fallback(
        graph, text_child, HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
        target_fp, cold_state, 3U, 1U, inherited_query));
    CHECK(inherited_query.used_warm_route);
    CHECK(!inherited_query.used_cold_fallback);
    CHECK(inherited_query.selected_source_context_signature64 == root);
    CHECK(inherited_query.inheritance_distance == 1U);
    PrimeLaneLinearResultV2 inherited_linear{};
    CHECK(graph.linear_scan(
        inherited_query.decision, inherited_query.raw.axes_used, inherited_linear));
    CHECK(inherited_query.raw.record_ids == inherited_linear.record_ids);

    PrimeLaneHierarchicalQueryResultV5 fallback_query{};
    CHECK(router.query_with_fallback(
        graph, poor_child, HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
        target_fp, cold_state, 3U, 1U, fallback_query));
    CHECK(fallback_query.used_cold_fallback);
    CHECK(fallback_query.metrics.insufficient_reduction_fallbacks == 1U);
    CHECK(fallback_query.raw.record_ids.size() == 1U);
    CHECK(fallback_query.raw.record_ids[0] == target_id);
    PrimeLaneLinearResultV2 fallback_linear{};
    CHECK(graph.linear_scan(
        fallback_query.decision, fallback_query.raw.axes_used, fallback_linear));
    CHECK(fallback_query.raw.record_ids == fallback_linear.record_ids);

    const std::array<std::uint32_t, 4> partition_targets{{128U, 1152U, 2176U, 3200U}};
    std::uint64_t parity_checks = 0U;
    for (const std::uint32_t record_id : partition_targets) {
        const auto decision = decision_for(bound[record_id].indexed.fingerprint, {0U, 1U, 2U});
        PrimeLaneCandidateResultV2 indexed{};
        PrimeLaneCanonicalCandidateResultV3 canonical{};
        CHECK(graph.query(decision, 8U, indexed, canonical));
        PrimeLaneLinearResultV2 linear{};
        CHECK(graph.linear_scan(decision, indexed.axes_used, linear));
        CHECK(indexed.record_ids == linear.record_ids);
        CHECK(std::find(indexed.record_ids.begin(), indexed.record_ids.end(), record_id) !=
              indexed.record_ids.end());
        ++parity_checks;
    }
    CHECK(parity_checks == 4U);

    PrimeLaneHash216AliasGroupV3 alias_after{};
    CHECK(graph.alias_group_for_record(0U, alias_after));
    CHECK(alias_after.identity216 == alias_before.identity216);
    CHECK(alias_after.identity_signature64 == alias_before.identity_signature64);
    CHECK(alias_after.record_ids == alias_before.record_ids);
    CHECK(std::memcmp(&holo4_state, &frozen_holo4_state, sizeof(holo4_state)) == 0);

    CHECK(!inherited_query.authority.canonical_mutation_authority);
    CHECK(!inherited_query.authority.canonical_hash72_authority);
    CHECK(!inherited_query.authority.canonical_hash216_authority);
    CHECK(!inherited_query.authority.canonical_persistence_authority);

    std::printf(
        "lane5_i5=PASS target=%u inherited_distance=%u text_utility=%d "
        "vision_utility=%d multimodal_utility=%d tombstones=%llu "
        "fallbacks=%llu partition_parity=%llu alias_records=%zu unique_hash216=%zu\n",
        target_id,
        static_cast<unsigned>(inherited_query.inheritance_distance),
        inherited_text.active_utility_q10,
        vision_selection.active_utility_q10,
        multimodal_selection.active_utility_q10,
        static_cast<unsigned long long>(router.tombstone_count()),
        static_cast<unsigned long long>(fallback_query.metrics.fallback_count),
        static_cast<unsigned long long>(parity_checks),
        alias_after.record_ids.size(),
        graph.unique_hash216_count());
    return 0;
}
