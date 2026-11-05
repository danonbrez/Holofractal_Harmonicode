#include "hhs_pass219_prime_memristive_fifth_lane_1_9.hpp"

#include <algorithm>
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

static PrimeLanePrefetchCandidateV7 candidate(
    std::uint64_t query,
    std::uint64_t source,
    std::uint64_t composition,
    std::uint64_t binding,
    std::uint8_t modality,
    std::int32_t prefetch_score) {
    PrimeLanePrefetchCandidateV7 out{};
    out.transition.key.from_neighborhood_binding_signature64 = UINT64_C(0xa000000000000001);
    out.transition.key.target.query_context_signature64 = query;
    out.transition.key.target.source_context_signature64 = source;
    out.transition.key.target.composition_signature64 = composition;
    out.transition.key.target.neighborhood_binding_signature64 = binding;
    out.transition.key.target.modality_mask = modality;
    out.transition.transition_weight = prefetch_score;
    out.transition.observations = 1U;
    out.transition.last_sequence = 1U;
    out.neighborhood.key.source_context_signature64 = source;
    out.neighborhood.key.composition_signature64 = composition;
    out.neighborhood.key.modality_mask = modality;
    out.neighborhood.binding_signature64 = binding;
    out.neighborhood.observed_sequence = 1U;
    PrimeLaneHash216NeighborhoodMemberV6 member{};
    member.identity_signature64 = binding ^ UINT64_C(0x5a5a5a5a5a5a5a5a);
    if (member.identity_signature64 == 0U)
        member.identity_signature64 = 1U;
    member.alias_cardinality = 1U;
    out.neighborhood.members.push_back(member);
    out.prefetch_score = prefetch_score;
    return out;
}

static bool same_metabolic(
    const PrimeLaneMetabolicStateV9& a,
    const PrimeLaneMetabolicStateV9& b) {
    return a.neighborhood_binding_signature64 == b.neighborhood_binding_signature64 &&
           a.vitality_capacity == b.vitality_capacity &&
           a.vitality == b.vitality &&
           a.positive_verified == b.positive_verified &&
           a.negative_verified == b.negative_verified &&
           a.budget_credit_total == b.budget_credit_total &&
           a.decay_total == b.decay_total &&
           a.last_sequence == b.last_sequence &&
           a.metabolic_ordinal == b.metabolic_ordinal;
}

static bool same_budget(
    const PrimeLaneActivationBudgetStateV8& a,
    const PrimeLaneActivationBudgetStateV8& b) {
    return a.neighborhood_binding_signature64 == b.neighborhood_binding_signature64 &&
           a.capacity == b.capacity &&
           a.available == b.available &&
           a.consumed_total == b.consumed_total &&
           a.replenished_total == b.replenished_total &&
           a.debit_ordinal == b.debit_ordinal;
}

static bool same_receipt(
    const PrimeLaneArbitrationCandidateReceiptV10& a,
    const PrimeLaneArbitrationCandidateReceiptV10& b) {
    return a.query_context_signature64 == b.query_context_signature64 &&
           a.active_modality_mask == b.active_modality_mask &&
           a.neighborhood_binding_signature64 == b.neighborhood_binding_signature64 &&
           a.composition_signature64 == b.composition_signature64 &&
           a.inherited_prefetch_score == b.inherited_prefetch_score &&
           a.verified_vitality == b.verified_vitality &&
           a.remaining_budget == b.remaining_budget &&
           a.route_component == b.route_component &&
           a.vitality_component == b.vitality_component &&
           a.budget_component == b.budget_component &&
           a.raw_score == b.raw_score &&
           a.stronger_candidate_count == b.stronger_candidate_count &&
           a.inhibition == b.inhibition &&
           a.final_score == b.final_score &&
           a.exact_hop_floor == b.exact_hop_floor &&
           a.work_allocation == b.work_allocation &&
           a.competition_rank == b.competition_rank &&
           a.winner_ordinal == b.winner_ordinal &&
           a.exclusion == b.exclusion &&
           a.eligible == b.eligible &&
           a.winner == b.winner;
}

int main() {
    CHECK(HHS_EXACT_PASS219_HOLO4_LANE_COUNT == 4U);
    CHECK(hhs_pass219_prime_lane_sparse_arbitration_authority_valid(
        PrimeLaneSparseArbitrationAuthorityV10{}));
    CHECK(HHS_PASS219_PRIME_LANE_ARBITRATION_INHIBITION_QUANTUM == 32);
    CHECK(HHS_PASS219_PRIME_LANE_ARBITRATION_ACTIVE_LIMIT == 8U);

    HHSExactPass219Holo4StateV1 holo4_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&holo4_state) == HHS_EXACT_STATUS_OK);
    const HHSExactPass219Holo4StateV1 frozen_holo4_state = holo4_state;

    constexpr std::uint64_t query = UINT64_C(0xa100000000000001);
    constexpr std::uint64_t other_query = UINT64_C(0xa100000000000002);
    constexpr std::uint64_t source = UINT64_C(0xa200000000000001);
    constexpr std::uint64_t a = UINT64_C(0xa300000000000001);
    constexpr std::uint64_t b = UINT64_C(0xa300000000000002);
    constexpr std::uint64_t c = UINT64_C(0xa300000000000003);
    constexpr std::uint64_t d = UINT64_C(0xa300000000000004);
    constexpr std::uint64_t e = UINT64_C(0xa300000000000005);
    constexpr std::uint64_t f = UINT64_C(0xa300000000000006);
    constexpr std::uint64_t g = UINT64_C(0xa300000000000007);
    constexpr std::uint64_t h = UINT64_C(0xa300000000000008);

    PrimeLaneVerifiedOutcomeMetabolismV9 metabolism{};
    CHECK(metabolism.register_route(a, 74U));
    CHECK(metabolism.register_route(b, 120U));
    CHECK(metabolism.register_route(c, 200U));
    CHECK(metabolism.register_route(d, 20U));
    CHECK(metabolism.register_route(e, 256U));
    CHECK(metabolism.register_route(f, 256U));
    CHECK(metabolism.register_route(g, 256U));
    CHECK(metabolism.register_route(h, 128U));

    PrimeLaneBudgetedPredictiveHydratorV8 hydrator{};
    CHECK(hydrator.register_budget(a, 64U, 48U));
    CHECK(hydrator.register_budget(b, 64U, 64U));
    CHECK(hydrator.register_budget(c, 64U, 64U));
    CHECK(hydrator.register_budget(d, 64U, 64U));
    CHECK(hydrator.register_budget(e, 64U, 64U));
    CHECK(hydrator.register_budget(f, 64U, 64U));
    CHECK(hydrator.register_budget(g, 64U, 16U));
    CHECK(hydrator.register_budget(h, 64U, 64U));

    PrimeLaneMetabolicStateV9 a_metabolic_before{};
    PrimeLaneActivationBudgetStateV8 a_budget_before{};
    CHECK(metabolism.state_for(a, a_metabolic_before));
    CHECK(hydrator.budget_for(a, a_budget_before));
    const std::size_t consumed_verdicts_before = metabolism.consumed_verdict_count();

    std::vector<PrimeLanePrefetchCandidateV7> candidates{};
    candidates.push_back(candidate(query, source, UINT64_C(0xb001), a,
                                   HHS_PASS219_PRIME_LANE_MODALITY_TEXT, 320));
    candidates.push_back(candidate(query, source, UINT64_C(0xb002), b,
                                   HHS_PASS219_PRIME_LANE_MODALITY_TEXT, 256));
    candidates.push_back(candidate(query, source, UINT64_C(0xb003), c,
                                   HHS_PASS219_PRIME_LANE_MODALITY_TEXT, 192));
    candidates.push_back(candidate(query, source, UINT64_C(0xb004), d,
                                   HHS_PASS219_PRIME_LANE_MODALITY_TEXT, -64));
    candidates.push_back(candidate(other_query, source, UINT64_C(0xb005), e,
                                   HHS_PASS219_PRIME_LANE_MODALITY_TEXT, 500));
    candidates.push_back(candidate(query, source, UINT64_C(0xb006), f,
                                   HHS_PASS219_PRIME_LANE_MODALITY_VISION, 500));
    candidates.push_back(candidate(query, source, UINT64_C(0xb007), g,
                                   HHS_PASS219_PRIME_LANE_MODALITY_TEXT, 500));
    auto invalid = candidate(query, source, UINT64_C(0xb008), h,
                             HHS_PASS219_PRIME_LANE_MODALITY_TEXT, 500);
    invalid.authority.canonical_mutation_authority = true;
    candidates.push_back(invalid);

    PrimeLaneSparseArbitrationRequestV10 request{};
    request.query_context_signature64 = query;
    request.active_modality_mask = HHS_PASS219_PRIME_LANE_MODALITY_TEXT;
    request.max_active = 2U;
    request.per_route_work_cap = 40U;

    PrimeLaneSparseRouteArbiterV10 arbiter{};
    PrimeLaneSparseArbitrationResultV10 result{};
    CHECK(arbiter.arbitrate(request, candidates, metabolism, hydrator, result));
    CHECK(result.receipts.size() == 8U);
    CHECK(result.metrics.candidates_considered == 8U);
    CHECK(result.metrics.candidates_eligible == 4U);
    CHECK(result.metrics.winners == 2U);
    CHECK(result.metrics.query_rejections == 1U);
    CHECK(result.metrics.modality_rejections == 1U);
    CHECK(result.metrics.authority_rejections == 1U);
    CHECK(result.metrics.metabolic_rejections == 0U);
    CHECK(result.metrics.budget_rejections == 1U);
    CHECK(result.metrics.inhibited_rejections == 1U);
    CHECK(result.metrics.sparse_limit_rejections == 1U);
    CHECK(result.metrics.total_work_allocated == 80U);
    CHECK(result.metrics.arbitration_signature64 != 0U);

    CHECK(result.receipts[0].winner);
    CHECK(result.receipts[0].winner_ordinal == 1U);
    CHECK(result.receipts[0].neighborhood_binding_signature64 == a);
    CHECK(result.receipts[0].raw_score == 1476);
    CHECK(result.receipts[0].stronger_candidate_count == 0U);
    CHECK(result.receipts[0].inhibition == 0);
    CHECK(result.receipts[0].final_score == 1476);
    CHECK(result.receipts[0].exact_hop_floor == 17U);
    CHECK(result.receipts[0].work_allocation == 40U);

    CHECK(result.receipts[1].winner);
    CHECK(result.receipts[1].winner_ordinal == 2U);
    CHECK(result.receipts[1].neighborhood_binding_signature64 == b);
    CHECK(result.receipts[1].raw_score == 1328);
    CHECK(result.receipts[1].stronger_candidate_count == 1U);
    CHECK(result.receipts[1].inhibition == 32);
    CHECK(result.receipts[1].final_score == 1296);
    CHECK(result.receipts[1].work_allocation == 40U);

    bool found_sparse = false;
    bool found_inhibited = false;
    bool found_query = false;
    bool found_modality = false;
    bool found_budget = false;
    bool found_authority = false;
    for (const auto& receipt : result.receipts) {
        if (receipt.neighborhood_binding_signature64 == c) {
            CHECK(receipt.eligible && !receipt.winner);
            CHECK(receipt.raw_score == 1232);
            CHECK(receipt.stronger_candidate_count == 2U);
            CHECK(receipt.inhibition == 64);
            CHECK(receipt.final_score == 1168);
            CHECK(receipt.exclusion == PrimeLaneArbitrationExclusionV10::sparse_limit);
            found_sparse = true;
        } else if (receipt.neighborhood_binding_signature64 == d) {
            CHECK(receipt.eligible && !receipt.winner);
            CHECK(receipt.raw_score == -152);
            CHECK(receipt.inhibition == 96);
            CHECK(receipt.final_score == -248);
            CHECK(receipt.exclusion == PrimeLaneArbitrationExclusionV10::inhibited_nonpositive);
            found_inhibited = true;
        } else if (receipt.neighborhood_binding_signature64 == e) {
            CHECK(receipt.exclusion == PrimeLaneArbitrationExclusionV10::query_context_mismatch);
            found_query = true;
        } else if (receipt.neighborhood_binding_signature64 == f) {
            CHECK(receipt.exclusion == PrimeLaneArbitrationExclusionV10::modality_mismatch);
            found_modality = true;
        } else if (receipt.neighborhood_binding_signature64 == g) {
            CHECK(receipt.exclusion == PrimeLaneArbitrationExclusionV10::insufficient_work_budget);
            found_budget = true;
        } else if (receipt.neighborhood_binding_signature64 == h) {
            CHECK(receipt.exclusion == PrimeLaneArbitrationExclusionV10::invalid_authority);
            found_authority = true;
        }
    }
    CHECK(found_sparse && found_inhibited && found_query && found_modality &&
          found_budget && found_authority);

    PrimeLaneMetabolicStateV9 a_metabolic_after{};
    PrimeLaneActivationBudgetStateV8 a_budget_after{};
    CHECK(metabolism.state_for(a, a_metabolic_after));
    CHECK(hydrator.budget_for(a, a_budget_after));
    CHECK(same_metabolic(a_metabolic_before, a_metabolic_after));
    CHECK(same_budget(a_budget_before, a_budget_after));
    CHECK(metabolism.consumed_verdict_count() == consumed_verdicts_before);

    auto reversed = candidates;
    std::reverse(reversed.begin(), reversed.end());
    PrimeLaneSparseArbitrationResultV10 replay{};
    CHECK(arbiter.arbitrate(request, reversed, metabolism, hydrator, replay));
    CHECK(replay.metrics.arbitration_signature64 == result.metrics.arbitration_signature64);
    CHECK(replay.receipts.size() == result.receipts.size());
    for (std::size_t i = 0U; i < result.receipts.size(); ++i)
        CHECK(same_receipt(result.receipts[i], replay.receipts[i]));

    auto duplicate = candidates;
    duplicate.push_back(candidates[0]);
    PrimeLaneSparseArbitrationResultV10 rejected{};
    CHECK(!arbiter.arbitrate(request, duplicate, metabolism, hydrator, rejected));

    PrimeLaneSparseArbitrationRequestV10 bad_request = request;
    bad_request.per_route_work_cap = 16U;
    CHECK(!arbiter.arbitrate(bad_request, candidates, metabolism, hydrator, rejected));

    CHECK(std::memcmp(&holo4_state, &frozen_holo4_state, sizeof(holo4_state)) == 0);

    std::printf(
        "lane5_i10=PASS considered=%llu eligible=%llu winners=%llu work=%llu "
        "signature=%llu query_reject=%llu modality_reject=%llu authority_reject=%llu "
        "budget_reject=%llu inhibited=%llu sparse=%llu winner1=%llu winner2=%llu\n",
        static_cast<unsigned long long>(result.metrics.candidates_considered),
        static_cast<unsigned long long>(result.metrics.candidates_eligible),
        static_cast<unsigned long long>(result.metrics.winners),
        static_cast<unsigned long long>(result.metrics.total_work_allocated),
        static_cast<unsigned long long>(result.metrics.arbitration_signature64),
        static_cast<unsigned long long>(result.metrics.query_rejections),
        static_cast<unsigned long long>(result.metrics.modality_rejections),
        static_cast<unsigned long long>(result.metrics.authority_rejections),
        static_cast<unsigned long long>(result.metrics.budget_rejections),
        static_cast<unsigned long long>(result.metrics.inhibited_rejections),
        static_cast<unsigned long long>(result.metrics.sparse_limit_rejections),
        static_cast<unsigned long long>(result.receipts[0].neighborhood_binding_signature64),
        static_cast<unsigned long long>(result.receipts[1].neighborhood_binding_signature64));
    return 0;
}
