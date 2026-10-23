#include "hhs_pass219_prime_memristive_fifth_lane_1_7.hpp"

#define main hhs_pass219_i7_embedded_main
#include "test_pass219_prime_memristive_fifth_lane_1_6.cpp"
#undef main

int main() {
    CHECK(hhs_pass219_i7_embedded_main() == 0);
    CHECK(HHS_EXACT_PASS219_HOLO4_LANE_COUNT == 4U);
    CHECK(hhs_pass219_prime_lane_budgeted_hydration_authority_valid(
        PrimeLaneBudgetedHydrationAuthorityV8{}));
    CHECK(HHS_PASS219_PRIME_LANE_HOP_ENERGY_QUANTUM == 16U);

    HHSExactPass219Holo4StateV1 holo4_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&holo4_state) == HHS_EXACT_STATUS_OK);
    const HHSExactPass219Holo4StateV1 frozen_holo4_state = holo4_state;

    constexpr std::uint32_t corpus_size = 512U;
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

    PrimeLaneCanonicalCandidateResultV3 canonical_a{};
    PrimeLaneCanonicalCandidateResultV3 canonical_b{};
    PrimeLaneCanonicalCandidateResultV3 canonical_c{};
    PrimeLaneCanonicalCandidateResultV3 canonical_d{};
    PrimeLaneHash216AliasGroupV3 group_a{};
    PrimeLaneHash216AliasGroupV3 group_b{};
    PrimeLaneHash216AliasGroupV3 group_c{};
    PrimeLaneHash216AliasGroupV3 group_d{};
    CHECK(graph.alias_group_for_record(32U, group_a));
    CHECK(graph.alias_group_for_record(96U, group_b));
    CHECK(graph.alias_group_for_record(160U, group_c));
    CHECK(graph.alias_group_for_record(224U, group_d));
    canonical_a.states.push_back(group_a);
    canonical_b.states.push_back(group_b);
    canonical_c.states.push_back(group_c);
    canonical_d.states.push_back(group_d);
    canonical_a.raw_record_count = canonical_b.raw_record_count =
        canonical_c.raw_record_count = canonical_d.raw_record_count = 1U;
    canonical_a.unique_hash216_count = canonical_b.unique_hash216_count =
        canonical_c.unique_hash216_count = canonical_d.unique_hash216_count = 1U;

    constexpr std::uint64_t context_a = UINT64_C(0x8100000000000001);
    constexpr std::uint64_t context_b = UINT64_C(0x8100000000000002);
    constexpr std::uint64_t context_c = UINT64_C(0x8100000000000003);
    constexpr std::uint64_t context_d = UINT64_C(0x8100000000000004);
    constexpr std::uint64_t composition_a = UINT64_C(0x8101);
    constexpr std::uint64_t composition_b = UINT64_C(0x8102);
    constexpr std::uint64_t composition_c = UINT64_C(0x8103);
    constexpr std::uint64_t composition_d = UINT64_C(0x8104);

    PrimeLaneHash216NeighborhoodStoreV6 store{};
    PrimeLaneHash216NeighborhoodRefV6 neighborhood_a{};
    PrimeLaneHash216NeighborhoodRefV6 neighborhood_b{};
    PrimeLaneHash216NeighborhoodRefV6 neighborhood_c{};
    PrimeLaneHash216NeighborhoodRefV6 neighborhood_d{};
    CHECK(store.bind(context_a, composition_a, HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                     canonical_a, 201U, neighborhood_a));
    CHECK(store.bind(context_b, composition_b, HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                     canonical_b, 202U, neighborhood_b));
    CHECK(store.bind(context_c, composition_c, HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                     canonical_c, 203U, neighborhood_c));
    CHECK(store.bind(context_d, composition_d, HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                     canonical_d, 204U, neighborhood_d));
    CHECK(neighborhood_a.members.size() == 1U);
    CHECK(neighborhood_b.members.size() == 1U);
    CHECK(neighborhood_c.members.size() == 1U);
    CHECK(neighborhood_d.members.size() == 1U);

    PrimeLaneReplayAssociationKeyV6 key_a{};
    key_a.query_context_signature64 = context_d;
    key_a.source_context_signature64 = context_a;
    key_a.composition_signature64 = composition_a;
    key_a.neighborhood_binding_signature64 = neighborhood_a.binding_signature64;
    key_a.modality_mask = HHS_PASS219_PRIME_LANE_MODALITY_TEXT;

    PrimeLaneReplayAssociationKeyV6 key_b{};
    key_b.query_context_signature64 = context_a;
    key_b.source_context_signature64 = context_b;
    key_b.composition_signature64 = composition_b;
    key_b.neighborhood_binding_signature64 = neighborhood_b.binding_signature64;
    key_b.modality_mask = HHS_PASS219_PRIME_LANE_MODALITY_TEXT;

    PrimeLaneReplayAssociationKeyV6 key_c{};
    key_c.query_context_signature64 = context_b;
    key_c.source_context_signature64 = context_c;
    key_c.composition_signature64 = composition_c;
    key_c.neighborhood_binding_signature64 = neighborhood_c.binding_signature64;
    key_c.modality_mask = HHS_PASS219_PRIME_LANE_MODALITY_TEXT;

    PrimeLaneReplayAssociationKeyV6 key_d{};
    key_d.query_context_signature64 = context_c;
    key_d.source_context_signature64 = context_d;
    key_d.composition_signature64 = composition_d;
    key_d.neighborhood_binding_signature64 = neighborhood_d.binding_signature64;
    key_d.modality_mask = HHS_PASS219_PRIME_LANE_MODALITY_TEXT;

    PrimeLaneAdaptiveReplayLedgerV6 replay{};
    PrimeLaneReplayEventV6 replay_b{};
    replay_b.key = key_b;
    replay_b.admission_feedback_trinary = 1;
    replay_b.warm_reference_work = 1U;
    replay_b.cold_posting_work = 32U;
    replay_b.sequence = 1U;
    PrimeLaneReplayReceiptV6 replay_receipt{};
    CHECK(replay.apply(replay_b, replay_receipt));
    CHECK(replay.weight_for(key_b) > 0);

    PrimeLaneReplayConditionedPrefetchV7 prefetch{};
    CHECK(prefetch.register_target(key_b, neighborhood_b));
    CHECK(prefetch.register_target(key_c, neighborhood_c));
    CHECK(prefetch.register_target(key_d, neighborhood_d));
    CHECK(prefetch.observe_transition(neighborhood_a.binding_signature64, key_b, 1, 1U));
    CHECK(prefetch.observe_transition(neighborhood_b.binding_signature64, key_c, 1, 1U));
    CHECK(prefetch.observe_transition(neighborhood_c.binding_signature64, key_d, 1, 1U));

    const PrimeLaneRouteDecisionV1 cold_decision =
        decision_for(bound[0].indexed.fingerprint, {0U, 1U, 2U});

    PrimeLaneBudgetedPredictiveHydratorV8 hydrator{};
    CHECK(hydrator.register_budget(neighborhood_a.binding_signature64, 64U, 64U));
    CHECK(hydrator.register_budget(neighborhood_b.binding_signature64, 64U, 64U));
    CHECK(hydrator.register_budget(neighborhood_c.binding_signature64, 64U, 64U));
    CHECK(hydrator.budget_count() == 3U);

    PrimeLaneBudgetedHydrationResultV8 first{};
    CHECK(hydrator.hydrate(neighborhood_a.binding_signature64,
                          HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                          replay, prefetch, 3U, 1U,
                          graph, cold_decision, 1U, first));
    CHECK(first.used_predictive_hydration);
    CHECK(!first.used_cold_fallback);
    CHECK(first.hydrated.size() == 3U);
    CHECK(first.receipts.size() == 3U);
    CHECK(first.metrics.hops_completed == 3U);
    CHECK(first.metrics.exact_energy_spent == 51U);
    CHECK(first.metrics.inherited_reference_reads == 3U);
    CHECK(first.metrics.path_signature64 != 0U);
    CHECK(first.hydrated[0].neighborhood.binding_signature64 == neighborhood_b.binding_signature64);
    CHECK(first.hydrated[1].neighborhood.binding_signature64 == neighborhood_c.binding_signature64);
    CHECK(first.hydrated[2].neighborhood.binding_signature64 == neighborhood_d.binding_signature64);
    for (std::size_t i = 0U; i < first.receipts.size(); ++i) {
        CHECK(first.receipts[i].hop_index == i);
        CHECK(first.receipts[i].exact_hop_cost == 17U);
        CHECK(first.receipts[i].member_reference_work == 1U);
        CHECK(first.receipts[i].budget_before == 64U);
        CHECK(first.receipts[i].budget_after == 47U);
        CHECK(first.receipts[i].debit_ordinal == 1U);
    }

    PrimeLaneActivationBudgetStateV8 budget_a_after{};
    PrimeLaneActivationBudgetStateV8 budget_b_after{};
    PrimeLaneActivationBudgetStateV8 budget_c_after{};
    CHECK(hydrator.budget_for(neighborhood_a.binding_signature64, budget_a_after));
    CHECK(hydrator.budget_for(neighborhood_b.binding_signature64, budget_b_after));
    CHECK(hydrator.budget_for(neighborhood_c.binding_signature64, budget_c_after));
    CHECK(budget_a_after.available == 47U && budget_a_after.consumed_total == 17U);
    CHECK(budget_b_after.available == 47U && budget_b_after.consumed_total == 17U);
    CHECK(budget_c_after.available == 47U && budget_c_after.consumed_total == 17U);

    const std::uint64_t first_path_signature = first.metrics.path_signature64;
    CHECK(hydrator.reverse_receipts(first.receipts));
    PrimeLaneActivationBudgetStateV8 restored_a{};
    PrimeLaneActivationBudgetStateV8 restored_b{};
    PrimeLaneActivationBudgetStateV8 restored_c{};
    CHECK(hydrator.budget_for(neighborhood_a.binding_signature64, restored_a));
    CHECK(hydrator.budget_for(neighborhood_b.binding_signature64, restored_b));
    CHECK(hydrator.budget_for(neighborhood_c.binding_signature64, restored_c));
    CHECK(restored_a.available == 64U && restored_a.consumed_total == 0U && restored_a.debit_ordinal == 0U);
    CHECK(restored_b.available == 64U && restored_b.consumed_total == 0U && restored_b.debit_ordinal == 0U);
    CHECK(restored_c.available == 64U && restored_c.consumed_total == 0U && restored_c.debit_ordinal == 0U);

    PrimeLaneBudgetedHydrationResultV8 repeated{};
    CHECK(hydrator.hydrate(neighborhood_a.binding_signature64,
                          HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                          replay, prefetch, 3U, 1U,
                          graph, cold_decision, 1U, repeated));
    CHECK(repeated.metrics.path_signature64 == first_path_signature);
    CHECK(repeated.receipts.size() == first.receipts.size());
    CHECK(repeated.hydrated.size() == first.hydrated.size());
    CHECK(hydrator.reverse_receipts(repeated.receipts));

    PrimeLaneBudgetedPredictiveHydratorV8 budget_stop_hydrator{};
    CHECK(budget_stop_hydrator.register_budget(neighborhood_a.binding_signature64, 64U, 64U));
    CHECK(budget_stop_hydrator.register_budget(neighborhood_b.binding_signature64, 64U, 16U));
    CHECK(budget_stop_hydrator.register_budget(neighborhood_c.binding_signature64, 64U, 64U));
    PrimeLaneBudgetedHydrationResultV8 budget_stop{};
    CHECK(budget_stop_hydrator.hydrate(neighborhood_a.binding_signature64,
                                      HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                                      replay, prefetch, 3U, 1U,
                                      graph, cold_decision, 1U, budget_stop));
    CHECK(budget_stop.used_predictive_hydration);
    CHECK(budget_stop.stopped_by_budget);
    CHECK(budget_stop.used_cold_fallback);
    CHECK(budget_stop.metrics.budget_stops == 1U);
    CHECK(budget_stop.metrics.cold_fallbacks == 1U);
    CHECK(budget_stop.hydrated.size() == 1U);
    CHECK(budget_stop.receipts.size() == 1U);
    CHECK(budget_stop_hydrator.reverse_receipts(budget_stop.receipts));

    PrimeLaneReplayConditionedPrefetchV7 cycle_prefetch{};
    CHECK(cycle_prefetch.register_target(key_a, neighborhood_a));
    CHECK(cycle_prefetch.register_target(key_b, neighborhood_b));
    CHECK(cycle_prefetch.register_target(key_c, neighborhood_c));
    CHECK(cycle_prefetch.observe_transition(neighborhood_a.binding_signature64, key_b, 1, 1U));
    CHECK(cycle_prefetch.observe_transition(neighborhood_b.binding_signature64, key_c, 1, 1U));
    CHECK(cycle_prefetch.observe_transition(neighborhood_c.binding_signature64, key_a, 1, 1U));

    PrimeLaneBudgetedPredictiveHydratorV8 cycle_hydrator{};
    CHECK(cycle_hydrator.register_budget(neighborhood_a.binding_signature64, 64U, 64U));
    CHECK(cycle_hydrator.register_budget(neighborhood_b.binding_signature64, 64U, 64U));
    CHECK(cycle_hydrator.register_budget(neighborhood_c.binding_signature64, 64U, 64U));
    PrimeLaneBudgetedHydrationResultV8 cycle{};
    CHECK(cycle_hydrator.hydrate(neighborhood_a.binding_signature64,
                                HHS_PASS219_PRIME_LANE_MODALITY_TEXT,
                                replay, cycle_prefetch, 4U, 1U,
                                graph, cold_decision, 1U, cycle));
    CHECK(cycle.stopped_by_cycle);
    CHECK(cycle.used_cold_fallback);
    CHECK(cycle.metrics.cycle_stops == 1U);
    CHECK(cycle.metrics.cold_fallbacks == 1U);
    CHECK(cycle.hydrated.size() == 2U);
    CHECK(cycle.receipts.size() == 2U);
    CHECK(cycle_hydrator.reverse_receipts(cycle.receipts));

    std::vector<PrimeLanePrefetchCandidateV7> wrong_modality{};
    PrimeLanePrefetchMetricsV7 wrong_modality_metrics{};
    CHECK(prefetch.prefetch(neighborhood_a.binding_signature64,
                            HHS_PASS219_PRIME_LANE_MODALITY_VISION,
                            replay, 1U, wrong_modality, wrong_modality_metrics));
    CHECK(wrong_modality.empty());
    CHECK(wrong_modality_metrics.modality_rejections == 1U);

    PrimeLaneHash216AliasGroupV3 alias_after{};
    CHECK(graph.alias_group_for_record(0U, alias_after));
    CHECK(alias_after.identity216 == alias_before.identity216);
    CHECK(alias_after.identity_signature64 == alias_before.identity_signature64);
    CHECK(alias_after.record_ids == alias_before.record_ids);
    CHECK(graph.unique_hash216_count() == corpus_size - 1U);
    CHECK(std::memcmp(&holo4_state, &frozen_holo4_state, sizeof(holo4_state)) == 0);

    std::printf(
        "lane5_i8=PASS hops=%llu energy=%llu path_signature=%llu repeated_path_signature=%llu "
        "budget_stops=%llu cycle_stops=%llu fallbacks=%llu alias_records=%zu unique_hash216=%zu\n",
        static_cast<unsigned long long>(first.metrics.hops_completed),
        static_cast<unsigned long long>(first.metrics.exact_energy_spent),
        static_cast<unsigned long long>(first.metrics.path_signature64),
        static_cast<unsigned long long>(repeated.metrics.path_signature64),
        static_cast<unsigned long long>(budget_stop.metrics.budget_stops),
        static_cast<unsigned long long>(cycle.metrics.cycle_stops),
        static_cast<unsigned long long>(budget_stop.metrics.cold_fallbacks + cycle.metrics.cold_fallbacks),
        alias_after.record_ids.size(),
        graph.unique_hash216_count());
    return 0;
}
