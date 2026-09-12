#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_9_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_9_HPP

#include "hhs_pass219_prime_memristive_fifth_lane_1_8.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <set>
#include <vector>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_SPARSE_ARBITRATION_VERSION = UINT32_C(0x00010009);
inline constexpr std::int64_t HHS_PASS219_PRIME_LANE_ARBITRATION_ROUTE_MULTIPLIER = INT64_C(4);
inline constexpr std::int64_t HHS_PASS219_PRIME_LANE_ARBITRATION_VITALITY_MULTIPLIER = INT64_C(2);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_ARBITRATION_BUDGET_SCORE_CAP = UINT64_C(256);
inline constexpr std::int64_t HHS_PASS219_PRIME_LANE_ARBITRATION_INHIBITION_QUANTUM = INT64_C(32);
inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_ARBITRATION_ACTIVE_LIMIT = UINT32_C(8);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_ARBITRATION_WORK_CAP = UINT64_C(4096);

struct PrimeLaneSparseArbitrationAuthorityV10 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool query_scoped_only{true};
    bool modality_scoped_only{true};
    bool verified_vitality_only{true};
    bool inherited_route_score_only{true};
    bool remaining_budget_only{true};
    bool deterministic_sparse_activation_only{true};
    bool reciprocal_inhibition_only{true};
    bool bounded_work_allocation_only{true};
    bool arbitration_receipt_only{true};
    bool inherited_budget_mutation{false};
    bool speculative_reinforcement{false};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    bool requires_inherited_vm81_hash216_admission{true};
};

constexpr bool hhs_pass219_prime_lane_sparse_arbitration_authority_valid(
    const PrimeLaneSparseArbitrationAuthorityV10& authority) noexcept {
    return authority.candidate_only && authority.exact_integer_only &&
           authority.query_scoped_only && authority.modality_scoped_only &&
           authority.verified_vitality_only && authority.inherited_route_score_only &&
           authority.remaining_budget_only &&
           authority.deterministic_sparse_activation_only &&
           authority.reciprocal_inhibition_only &&
           authority.bounded_work_allocation_only && authority.arbitration_receipt_only &&
           !authority.inherited_budget_mutation && !authority.speculative_reinforcement &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority &&
           authority.requires_inherited_vm81_hash216_admission;
}

enum class PrimeLaneArbitrationExclusionV10 : std::uint8_t {
    none = 0U,
    invalid_authority = 1U,
    query_context_mismatch = 2U,
    modality_mismatch = 3U,
    missing_verified_vitality = 4U,
    missing_activation_budget = 5U,
    insufficient_work_budget = 6U,
    inhibited_nonpositive = 7U,
    sparse_limit = 8U,
};

struct PrimeLaneSparseArbitrationRequestV10 final {
    std::uint64_t query_context_signature64{};
    std::uint8_t active_modality_mask{};
    std::uint32_t max_active{};
    std::uint64_t per_route_work_cap{};
};

struct PrimeLaneArbitrationCandidateReceiptV10 final {
    std::uint64_t query_context_signature64{};
    std::uint8_t active_modality_mask{};
    std::uint64_t neighborhood_binding_signature64{};
    std::uint64_t composition_signature64{};
    std::int32_t inherited_prefetch_score{};
    std::uint64_t verified_vitality{};
    std::uint64_t remaining_budget{};
    std::int64_t route_component{};
    std::int64_t vitality_component{};
    std::int64_t budget_component{};
    std::int64_t raw_score{};
    std::uint32_t stronger_candidate_count{};
    std::int64_t inhibition{};
    std::int64_t final_score{};
    std::uint64_t exact_hop_floor{};
    std::uint64_t work_allocation{};
    std::uint32_t competition_rank{};
    std::uint32_t winner_ordinal{};
    PrimeLaneArbitrationExclusionV10 exclusion{PrimeLaneArbitrationExclusionV10::none};
    bool eligible{};
    bool winner{};
    PrimeLaneSparseArbitrationAuthorityV10 authority{};
};

struct PrimeLaneSparseArbitrationMetricsV10 final {
    std::uint64_t candidates_considered{};
    std::uint64_t candidates_eligible{};
    std::uint64_t winners{};
    std::uint64_t query_rejections{};
    std::uint64_t modality_rejections{};
    std::uint64_t authority_rejections{};
    std::uint64_t metabolic_rejections{};
    std::uint64_t budget_rejections{};
    std::uint64_t inhibited_rejections{};
    std::uint64_t sparse_limit_rejections{};
    std::uint64_t total_work_allocated{};
    std::uint64_t arbitration_signature64{};
    PrimeLaneSparseArbitrationAuthorityV10 authority{};
};

struct PrimeLaneSparseArbitrationResultV10 final {
    std::vector<PrimeLaneArbitrationCandidateReceiptV10> receipts{};
    PrimeLaneSparseArbitrationMetricsV10 metrics{};
    PrimeLaneSparseArbitrationAuthorityV10 authority{};
};

class PrimeLaneSparseRouteArbiterV10 final {
public:
    bool arbitrate(
        const PrimeLaneSparseArbitrationRequestV10& request,
        const std::vector<PrimeLanePrefetchCandidateV7>& candidates,
        const PrimeLaneVerifiedOutcomeMetabolismV9& metabolism,
        const PrimeLaneBudgetedPredictiveHydratorV8& hydrator,
        PrimeLaneSparseArbitrationResultV10& out) const {
        out = PrimeLaneSparseArbitrationResultV10{};
        if (!request_valid(request) || candidates.empty() ||
            candidates.size() > HHS_PASS219_PRIME_LANE_PREFETCH_LIMIT)
            return false;

        std::set<std::uint64_t> seen_bindings{};
        for (const auto& candidate : candidates) {
            const std::uint64_t binding = candidate.neighborhood.binding_signature64;
            if (binding != 0U && !seen_bindings.insert(binding).second)
                return false;
        }

        out.metrics.candidates_considered = candidates.size();
        out.receipts.reserve(candidates.size());

        for (const auto& candidate : candidates) {
            PrimeLaneArbitrationCandidateReceiptV10 receipt{};
            receipt.query_context_signature64 = request.query_context_signature64;
            receipt.active_modality_mask = request.active_modality_mask;
            receipt.neighborhood_binding_signature64 = candidate.neighborhood.binding_signature64;
            receipt.composition_signature64 = candidate.transition.key.target.composition_signature64;
            receipt.inherited_prefetch_score = candidate.prefetch_score;

            if (!candidate_valid(candidate)) {
                receipt.exclusion = PrimeLaneArbitrationExclusionV10::invalid_authority;
                ++out.metrics.authority_rejections;
                out.receipts.push_back(receipt);
                continue;
            }
            if (candidate.transition.key.target.query_context_signature64 !=
                request.query_context_signature64) {
                receipt.exclusion = PrimeLaneArbitrationExclusionV10::query_context_mismatch;
                ++out.metrics.query_rejections;
                out.receipts.push_back(receipt);
                continue;
            }
            if ((candidate.transition.key.target.modality_mask &
                 request.active_modality_mask) == 0U) {
                receipt.exclusion = PrimeLaneArbitrationExclusionV10::modality_mismatch;
                ++out.metrics.modality_rejections;
                out.receipts.push_back(receipt);
                continue;
            }

            PrimeLaneMetabolicStateV9 metabolic{};
            if (!metabolism.state_for(receipt.neighborhood_binding_signature64, metabolic) ||
                !hhs_pass219_prime_lane_verified_metabolism_authority_valid(metabolic.authority)) {
                receipt.exclusion = PrimeLaneArbitrationExclusionV10::missing_verified_vitality;
                ++out.metrics.metabolic_rejections;
                out.receipts.push_back(receipt);
                continue;
            }

            PrimeLaneActivationBudgetStateV8 budget{};
            if (!hydrator.budget_for(receipt.neighborhood_binding_signature64, budget) ||
                !hhs_pass219_prime_lane_budgeted_hydration_authority_valid(budget.authority)) {
                receipt.exclusion = PrimeLaneArbitrationExclusionV10::missing_activation_budget;
                ++out.metrics.budget_rejections;
                out.receipts.push_back(receipt);
                continue;
            }

            if (candidate.neighborhood.members.size() >
                std::numeric_limits<std::uint64_t>::max() -
                    HHS_PASS219_PRIME_LANE_HOP_ENERGY_QUANTUM)
                return false;
            receipt.exact_hop_floor = HHS_PASS219_PRIME_LANE_HOP_ENERGY_QUANTUM +
                static_cast<std::uint64_t>(candidate.neighborhood.members.size());
            receipt.verified_vitality = metabolic.vitality;
            receipt.remaining_budget = budget.available;

            if (budget.available < receipt.exact_hop_floor ||
                request.per_route_work_cap < receipt.exact_hop_floor) {
                receipt.exclusion = PrimeLaneArbitrationExclusionV10::insufficient_work_budget;
                ++out.metrics.budget_rejections;
                out.receipts.push_back(receipt);
                continue;
            }

            receipt.route_component =
                static_cast<std::int64_t>(candidate.prefetch_score) *
                HHS_PASS219_PRIME_LANE_ARBITRATION_ROUTE_MULTIPLIER;
            receipt.vitality_component =
                static_cast<std::int64_t>(metabolic.vitality) *
                HHS_PASS219_PRIME_LANE_ARBITRATION_VITALITY_MULTIPLIER;
            receipt.budget_component = static_cast<std::int64_t>(std::min(
                budget.available, HHS_PASS219_PRIME_LANE_ARBITRATION_BUDGET_SCORE_CAP));
            receipt.raw_score = receipt.route_component + receipt.vitality_component +
                receipt.budget_component;
            receipt.eligible = true;
            ++out.metrics.candidates_eligible;
            out.receipts.push_back(receipt);
        }

        std::vector<std::size_t> competition{};
        competition.reserve(out.receipts.size());
        for (std::size_t i = 0U; i < out.receipts.size(); ++i) {
            if (out.receipts[i].eligible)
                competition.push_back(i);
        }
        std::sort(competition.begin(), competition.end(), [&](std::size_t a, std::size_t b) {
            return stronger(out.receipts[a], out.receipts[b]);
        });

        std::uint32_t winner_count = 0U;
        for (std::size_t rank = 0U; rank < competition.size(); ++rank) {
            auto& receipt = out.receipts[competition[rank]];
            if (rank > std::numeric_limits<std::uint32_t>::max())
                return false;
            receipt.stronger_candidate_count = static_cast<std::uint32_t>(rank);
            receipt.competition_rank = static_cast<std::uint32_t>(rank + 1U);
            receipt.inhibition = static_cast<std::int64_t>(rank) *
                HHS_PASS219_PRIME_LANE_ARBITRATION_INHIBITION_QUANTUM;
            receipt.final_score = receipt.raw_score - receipt.inhibition;

            if (receipt.final_score <= 0) {
                receipt.exclusion = PrimeLaneArbitrationExclusionV10::inhibited_nonpositive;
                ++out.metrics.inhibited_rejections;
                continue;
            }
            if (winner_count >= request.max_active) {
                receipt.exclusion = PrimeLaneArbitrationExclusionV10::sparse_limit;
                ++out.metrics.sparse_limit_rejections;
                continue;
            }

            receipt.winner = true;
            receipt.winner_ordinal = ++winner_count;
            receipt.work_allocation = std::min(
                receipt.remaining_budget, request.per_route_work_cap);
            if (receipt.work_allocation < receipt.exact_hop_floor)
                return false;
            if (receipt.work_allocation > std::numeric_limits<std::uint64_t>::max() -
                                          out.metrics.total_work_allocated)
                return false;
            out.metrics.total_work_allocated += receipt.work_allocation;
            ++out.metrics.winners;
        }

        std::sort(out.receipts.begin(), out.receipts.end(), output_order);
        out.metrics.arbitration_signature64 = signature(request, out.receipts, out.metrics);
        return hhs_pass219_prime_lane_sparse_arbitration_authority_valid(out.authority) &&
               hhs_pass219_prime_lane_sparse_arbitration_authority_valid(out.metrics.authority) &&
               out.metrics.arbitration_signature64 != 0U;
    }

private:
    static bool request_valid(const PrimeLaneSparseArbitrationRequestV10& request) noexcept {
        return request.query_context_signature64 != 0U &&
               request.active_modality_mask != 0U &&
               (request.active_modality_mask &
                static_cast<std::uint8_t>(~HHS_PASS219_PRIME_LANE_MODALITY_ALL)) == 0U &&
               request.max_active != 0U &&
               request.max_active <= HHS_PASS219_PRIME_LANE_ARBITRATION_ACTIVE_LIMIT &&
               request.per_route_work_cap >= HHS_PASS219_PRIME_LANE_HOP_ENERGY_QUANTUM + 1U &&
               request.per_route_work_cap <= HHS_PASS219_PRIME_LANE_ARBITRATION_WORK_CAP;
    }

    static bool candidate_valid(const PrimeLanePrefetchCandidateV7& candidate) noexcept {
        if (!hhs_pass219_prime_lane_replay_prefetch_authority_valid(candidate.authority) ||
            !hhs_pass219_prime_lane_replay_prefetch_authority_valid(candidate.transition.authority) ||
            !hhs_pass219_prime_lane_neighborhood_replay_authority_valid(candidate.neighborhood.authority) ||
            candidate.neighborhood.binding_signature64 == 0U ||
            candidate.neighborhood.members.empty() ||
            candidate.transition.key.target.query_context_signature64 == 0U ||
            candidate.transition.key.target.source_context_signature64 == 0U ||
            candidate.transition.key.target.composition_signature64 == 0U ||
            candidate.transition.key.target.neighborhood_binding_signature64 !=
                candidate.neighborhood.binding_signature64 ||
            candidate.transition.key.target.modality_mask == 0U ||
            (candidate.transition.key.target.modality_mask &
             static_cast<std::uint8_t>(~HHS_PASS219_PRIME_LANE_MODALITY_ALL)) != 0U)
            return false;
        for (const auto& member : candidate.neighborhood.members) {
            if (!hhs_pass219_prime_lane_neighborhood_replay_authority_valid(member.authority) ||
                member.identity_signature64 == 0U || member.alias_cardinality == 0U)
                return false;
        }
        return true;
    }

    static bool stronger(
        const PrimeLaneArbitrationCandidateReceiptV10& a,
        const PrimeLaneArbitrationCandidateReceiptV10& b) noexcept {
        if (a.raw_score != b.raw_score)
            return a.raw_score > b.raw_score;
        if (a.verified_vitality != b.verified_vitality)
            return a.verified_vitality > b.verified_vitality;
        if (a.remaining_budget != b.remaining_budget)
            return a.remaining_budget > b.remaining_budget;
        if (a.inherited_prefetch_score != b.inherited_prefetch_score)
            return a.inherited_prefetch_score > b.inherited_prefetch_score;
        if (a.neighborhood_binding_signature64 != b.neighborhood_binding_signature64)
            return a.neighborhood_binding_signature64 < b.neighborhood_binding_signature64;
        return a.composition_signature64 < b.composition_signature64;
    }

    static bool output_order(
        const PrimeLaneArbitrationCandidateReceiptV10& a,
        const PrimeLaneArbitrationCandidateReceiptV10& b) noexcept {
        if (a.winner != b.winner)
            return a.winner > b.winner;
        if (a.winner && a.winner_ordinal != b.winner_ordinal)
            return a.winner_ordinal < b.winner_ordinal;
        if (a.eligible != b.eligible)
            return a.eligible > b.eligible;
        if (a.eligible && a.competition_rank != b.competition_rank)
            return a.competition_rank < b.competition_rank;
        if (a.exclusion != b.exclusion)
            return static_cast<std::uint8_t>(a.exclusion) <
                   static_cast<std::uint8_t>(b.exclusion);
        if (a.neighborhood_binding_signature64 != b.neighborhood_binding_signature64)
            return a.neighborhood_binding_signature64 < b.neighborhood_binding_signature64;
        return a.composition_signature64 < b.composition_signature64;
    }

    static std::uint64_t signature(
        const PrimeLaneSparseArbitrationRequestV10& request,
        const std::vector<PrimeLaneArbitrationCandidateReceiptV10>& receipts,
        const PrimeLaneSparseArbitrationMetricsV10& metrics) noexcept {
        std::uint64_t hash = UINT64_C(1469598103934665603);
        mix(hash, request.query_context_signature64);
        mix(hash, request.active_modality_mask);
        mix(hash, request.max_active);
        mix(hash, request.per_route_work_cap);
        for (const auto& receipt : receipts) {
            mix(hash, receipt.neighborhood_binding_signature64);
            mix(hash, receipt.composition_signature64);
            mix(hash, static_cast<std::uint64_t>(static_cast<std::int64_t>(
                receipt.inherited_prefetch_score)));
            mix(hash, receipt.verified_vitality);
            mix(hash, receipt.remaining_budget);
            mix(hash, static_cast<std::uint64_t>(receipt.route_component));
            mix(hash, static_cast<std::uint64_t>(receipt.vitality_component));
            mix(hash, static_cast<std::uint64_t>(receipt.budget_component));
            mix(hash, static_cast<std::uint64_t>(receipt.raw_score));
            mix(hash, receipt.stronger_candidate_count);
            mix(hash, static_cast<std::uint64_t>(receipt.inhibition));
            mix(hash, static_cast<std::uint64_t>(receipt.final_score));
            mix(hash, receipt.exact_hop_floor);
            mix(hash, receipt.work_allocation);
            mix(hash, receipt.competition_rank);
            mix(hash, receipt.winner_ordinal);
            mix(hash, static_cast<std::uint8_t>(receipt.exclusion));
            mix(hash, receipt.eligible ? 1U : 0U);
            mix(hash, receipt.winner ? 1U : 0U);
        }
        mix(hash, metrics.candidates_considered);
        mix(hash, metrics.candidates_eligible);
        mix(hash, metrics.winners);
        mix(hash, metrics.total_work_allocated);
        return hash;
    }

    static void mix(std::uint64_t& hash, std::uint64_t value) noexcept {
        for (unsigned shift = 0U; shift < 64U; shift += 8U) {
            hash ^= (value >> shift) & UINT64_C(0xff);
            hash *= UINT64_C(1099511628211);
        }
    }
};

} // namespace hhs::rna

#endif
