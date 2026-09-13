#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_7_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_7_HPP

#include "hhs_pass219_prime_memristive_fifth_lane_1_6.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <map>
#include <set>
#include <vector>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_BUDGETED_HYDRATION_VERSION = UINT32_C(0x00010007);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_HOP_ENERGY_QUANTUM = UINT64_C(16);
inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_HYDRATION_HOP_LIMIT = UINT32_C(64);

struct PrimeLaneBudgetedHydrationAuthorityV8 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool hash216_reference_only{true};
    bool route_utility_only{true};
    bool multimodal_route_metadata_only{true};
    bool neighborhood_reference_only{true};
    bool replay_receipt_only{true};
    bool transition_association_only{true};
    bool predictive_prefetch_only{true};
    bool local_activation_budget_only{true};
    bool multi_hop_predictive_hydration_only{true};
    bool reversible_budget_receipt_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    bool requires_inherited_vm81_hash216_admission{true};
};

constexpr bool hhs_pass219_prime_lane_budgeted_hydration_authority_valid(
    const PrimeLaneBudgetedHydrationAuthorityV8& authority) noexcept {
    return authority.candidate_only && authority.exact_integer_only &&
           authority.hash216_reference_only && authority.route_utility_only &&
           authority.multimodal_route_metadata_only &&
           authority.neighborhood_reference_only && authority.replay_receipt_only &&
           authority.transition_association_only && authority.predictive_prefetch_only &&
           authority.local_activation_budget_only &&
           authority.multi_hop_predictive_hydration_only &&
           authority.reversible_budget_receipt_only &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority &&
           authority.requires_inherited_vm81_hash216_admission;
}

struct PrimeLaneActivationBudgetStateV8 final {
    std::uint64_t neighborhood_binding_signature64{};
    std::uint64_t capacity{};
    std::uint64_t available{};
    std::uint64_t consumed_total{};
    std::uint64_t replenished_total{};
    std::uint64_t debit_ordinal{};
    PrimeLaneBudgetedHydrationAuthorityV8 authority{};
};

struct PrimeLaneEnergyHopReceiptV8 final {
    std::uint32_t hop_index{};
    std::uint64_t source_neighborhood_binding_signature64{};
    std::uint64_t target_neighborhood_binding_signature64{};
    std::uint64_t budget_before{};
    std::uint64_t exact_hop_cost{};
    std::uint64_t budget_after{};
    std::uint64_t member_reference_work{};
    std::int32_t prefetch_score{};
    std::uint64_t ranking_signature64{};
    std::uint64_t debit_ordinal{};
    PrimeLaneBudgetedHydrationAuthorityV8 authority{};
};

struct PrimeLaneBudgetedHydrationMetricsV8 final {
    std::uint64_t hops_attempted{};
    std::uint64_t hops_completed{};
    std::uint64_t inherited_reference_reads{};
    std::uint64_t exact_energy_spent{};
    std::uint64_t budget_stops{};
    std::uint64_t no_path_stops{};
    std::uint64_t cycle_stops{};
    std::uint64_t cold_fallbacks{};
    std::uint64_t path_signature64{};
    PrimeLaneBudgetedHydrationAuthorityV8 authority{};
};

struct PrimeLaneBudgetedHydrationResultV8 final {
    std::vector<PrimeLanePrefetchCandidateV7> hydrated{};
    std::vector<PrimeLaneEnergyHopReceiptV8> receipts{};
    PrimeLaneCandidateResultV2 cold_raw{};
    PrimeLaneCanonicalCandidateResultV3 cold_canonical{};
    PrimeLaneBudgetedHydrationMetricsV8 metrics{};
    bool used_predictive_hydration{};
    bool used_cold_fallback{};
    bool stopped_by_budget{};
    bool stopped_by_no_path{};
    bool stopped_by_cycle{};
    PrimeLaneBudgetedHydrationAuthorityV8 authority{};
};

class PrimeLaneBudgetedPredictiveHydratorV8 final {
public:
    bool register_budget(
        std::uint64_t neighborhood_binding_signature64,
        std::uint64_t capacity,
        std::uint64_t initial_available) {
        if (neighborhood_binding_signature64 == 0U || capacity == 0U ||
            initial_available > capacity ||
            budgets_.find(neighborhood_binding_signature64) != budgets_.end())
            return false;
        PrimeLaneActivationBudgetStateV8 state{};
        state.neighborhood_binding_signature64 = neighborhood_binding_signature64;
        state.capacity = capacity;
        state.available = initial_available;
        budgets_.emplace(neighborhood_binding_signature64, state);
        return hhs_pass219_prime_lane_budgeted_hydration_authority_valid(state.authority);
    }

    bool replenish_budget(
        std::uint64_t neighborhood_binding_signature64,
        std::uint64_t exact_credit) {
        if (exact_credit == 0U)
            return false;
        auto it = budgets_.find(neighborhood_binding_signature64);
        if (it == budgets_.end())
            return false;
        auto& state = it->second;
        if (exact_credit > state.capacity - state.available ||
            exact_credit > std::numeric_limits<std::uint64_t>::max() - state.replenished_total)
            return false;
        state.available += exact_credit;
        state.replenished_total += exact_credit;
        return true;
    }

    bool budget_for(
        std::uint64_t neighborhood_binding_signature64,
        PrimeLaneActivationBudgetStateV8& out) const {
        out = PrimeLaneActivationBudgetStateV8{};
        const auto it = budgets_.find(neighborhood_binding_signature64);
        if (it == budgets_.end())
            return false;
        out = it->second;
        return true;
    }

    bool hydrate(
        std::uint64_t from_neighborhood_binding_signature64,
        std::uint8_t active_modality_mask,
        const PrimeLaneAdaptiveReplayLedgerV6& replay,
        const PrimeLaneReplayConditionedPrefetchV7& prefetch,
        std::uint32_t max_hops,
        std::size_t prefetch_limit,
        const PrimeLaneHash216CandidateGraphV3& graph,
        const PrimeLaneRouteDecisionV1& cold_decision,
        std::uint32_t candidate_budget,
        PrimeLaneBudgetedHydrationResultV8& out) {
        out = PrimeLaneBudgetedHydrationResultV8{};
        if (from_neighborhood_binding_signature64 == 0U ||
            !valid_modality_mask(active_modality_mask) || max_hops == 0U ||
            max_hops > HHS_PASS219_PRIME_LANE_HYDRATION_HOP_LIMIT ||
            prefetch_limit == 0U || prefetch_limit > HHS_PASS219_PRIME_LANE_PREFETCH_LIMIT ||
            candidate_budget == 0U)
            return false;

        std::set<std::uint64_t> visited{};
        std::uint64_t current = from_neighborhood_binding_signature64;
        visited.insert(current);

        for (std::uint32_t hop = 0U; hop < max_hops; ++hop) {
            ++out.metrics.hops_attempted;
            std::vector<PrimeLanePrefetchCandidateV7> ranked{};
            PrimeLanePrefetchMetricsV7 ranking_metrics{};
            if (!prefetch.prefetch(
                    current, active_modality_mask, replay, prefetch_limit,
                    ranked, ranking_metrics))
                return false;

            if (ranked.empty()) {
                out.stopped_by_no_path = true;
                ++out.metrics.no_path_stops;
                break;
            }

            const auto& chosen = ranked.front();
            const std::uint64_t target = chosen.neighborhood.binding_signature64;
            if (target == 0U)
                return false;
            if (visited.find(target) != visited.end()) {
                out.stopped_by_cycle = true;
                ++out.metrics.cycle_stops;
                break;
            }

            auto budget_it = budgets_.find(current);
            if (budget_it == budgets_.end()) {
                out.stopped_by_budget = true;
                ++out.metrics.budget_stops;
                break;
            }
            auto& budget = budget_it->second;
            const std::uint64_t member_work = chosen.neighborhood.members.size();
            if (member_work > std::numeric_limits<std::uint64_t>::max() -
                                  HHS_PASS219_PRIME_LANE_HOP_ENERGY_QUANTUM)
                return false;
            const std::uint64_t cost =
                HHS_PASS219_PRIME_LANE_HOP_ENERGY_QUANTUM + member_work;
            if (budget.available < cost) {
                out.stopped_by_budget = true;
                ++out.metrics.budget_stops;
                break;
            }
            if (cost > std::numeric_limits<std::uint64_t>::max() - budget.consumed_total ||
                budget.debit_ordinal == std::numeric_limits<std::uint64_t>::max())
                return false;

            PrimeLaneEnergyHopReceiptV8 receipt{};
            receipt.hop_index = hop;
            receipt.source_neighborhood_binding_signature64 = current;
            receipt.target_neighborhood_binding_signature64 = target;
            receipt.budget_before = budget.available;
            receipt.exact_hop_cost = cost;
            receipt.member_reference_work = member_work;
            receipt.prefetch_score = chosen.prefetch_score;
            receipt.ranking_signature64 = ranking_metrics.ranking_signature64;

            budget.available -= cost;
            budget.consumed_total += cost;
            ++budget.debit_ordinal;

            receipt.budget_after = budget.available;
            receipt.debit_ordinal = budget.debit_ordinal;
            out.hydrated.push_back(chosen);
            out.receipts.push_back(receipt);
            ++out.metrics.hops_completed;
            out.metrics.inherited_reference_reads += member_work;
            out.metrics.exact_energy_spent += cost;
            visited.insert(target);
            current = target;
        }

        out.used_predictive_hydration = !out.hydrated.empty();
        const bool needs_fallback =
            out.stopped_by_budget || out.stopped_by_no_path || out.stopped_by_cycle;
        if (needs_fallback) {
            if (!graph.query(cold_decision, candidate_budget,
                             out.cold_raw, out.cold_canonical))
                return false;
            out.used_cold_fallback = true;
            ++out.metrics.cold_fallbacks;
        }
        out.metrics.path_signature64 = path_signature(out.receipts);
        return hhs_pass219_prime_lane_budgeted_hydration_authority_valid(out.authority) &&
               hhs_pass219_prime_lane_budgeted_hydration_authority_valid(out.metrics.authority);
    }

    bool reverse_receipts(const std::vector<PrimeLaneEnergyHopReceiptV8>& receipts) {
        if (receipts.empty())
            return false;

        for (auto it = receipts.rbegin(); it != receipts.rend(); ++it) {
            const auto budget_it = budgets_.find(it->source_neighborhood_binding_signature64);
            if (budget_it == budgets_.end())
                return false;
            const auto& budget = budget_it->second;
            if (!hhs_pass219_prime_lane_budgeted_hydration_authority_valid(it->authority) ||
                it->exact_hop_cost == 0U ||
                it->budget_before < it->budget_after ||
                it->budget_before - it->budget_after != it->exact_hop_cost ||
                budget.available != it->budget_after ||
                budget.debit_ordinal != it->debit_ordinal ||
                budget.consumed_total < it->exact_hop_cost ||
                it->budget_before > budget.capacity)
                return false;
        }

        for (auto it = receipts.rbegin(); it != receipts.rend(); ++it) {
            auto& budget = budgets_.find(it->source_neighborhood_binding_signature64)->second;
            budget.available = it->budget_before;
            budget.consumed_total -= it->exact_hop_cost;
            --budget.debit_ordinal;
        }
        return true;
    }

    std::size_t budget_count() const noexcept { return budgets_.size(); }

private:
    static bool valid_modality_mask(std::uint8_t mask) noexcept {
        return mask != 0U &&
            (mask & static_cast<std::uint8_t>(~HHS_PASS219_PRIME_LANE_MODALITY_ALL)) == 0U;
    }

    static std::uint64_t path_signature(
        const std::vector<PrimeLaneEnergyHopReceiptV8>& receipts) noexcept {
        std::uint64_t hash = UINT64_C(1469598103934665603);
        for (const auto& receipt : receipts) {
            mix(hash, receipt.hop_index);
            mix(hash, receipt.source_neighborhood_binding_signature64);
            mix(hash, receipt.target_neighborhood_binding_signature64);
            mix(hash, receipt.budget_before);
            mix(hash, receipt.exact_hop_cost);
            mix(hash, receipt.budget_after);
            mix(hash, receipt.member_reference_work);
            mix(hash, static_cast<std::uint64_t>(
                static_cast<std::int64_t>(receipt.prefetch_score)));
            mix(hash, receipt.ranking_signature64);
            mix(hash, receipt.debit_ordinal);
        }
        mix(hash, receipts.size());
        return hash;
    }

    static void mix(std::uint64_t& hash, std::uint64_t value) noexcept {
        for (unsigned shift = 0U; shift < 64U; shift += 8U) {
            hash ^= (value >> shift) & UINT64_C(0xff);
            hash *= UINT64_C(1099511628211);
        }
    }

    std::map<std::uint64_t, PrimeLaneActivationBudgetStateV8> budgets_{};
};

} // namespace hhs::rna

#endif
