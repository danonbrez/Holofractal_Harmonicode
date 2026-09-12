#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_8_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_8_HPP

#include "hhs_pass219_prime_memristive_fifth_lane_1_7.hpp"

#include <algorithm>
#include <cstdint>
#include <limits>
#include <map>
#include <set>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_VERIFIED_METABOLISM_VERSION = UINT32_C(0x00010008);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_VITALITY_CAP = UINT64_C(256);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_REWARD = UINT64_C(8);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_PENALTY = UINT64_C(12);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_BUDGET_CREDIT = UINT64_C(8);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_DECAY_QUANTUM = UINT64_C(1);
inline constexpr std::uint64_t HHS_PASS219_PRIME_LANE_METABOLIC_DECAY_STEP_LIMIT = UINT64_C(16);

struct PrimeLaneVerifiedMetabolismAuthorityV9 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool verified_outcome_only{true};
    bool speculative_reinforcement{false};
    bool local_metabolic_state_only{true};
    bool budget_replenishment_only{true};
    bool bounded_decay_only{true};
    bool duplicate_verdict_replay{false};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    bool requires_inherited_vm81_hash216_admission{true};
};

constexpr bool hhs_pass219_prime_lane_verified_metabolism_authority_valid(
    const PrimeLaneVerifiedMetabolismAuthorityV9& authority) noexcept {
    return authority.candidate_only && authority.exact_integer_only &&
           authority.verified_outcome_only && !authority.speculative_reinforcement &&
           authority.local_metabolic_state_only && authority.budget_replenishment_only &&
           authority.bounded_decay_only && !authority.duplicate_verdict_replay &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority &&
           authority.requires_inherited_vm81_hash216_admission;
}

struct PrimeLaneVerifiedOutcomeV9 final {
    std::uint64_t verdict_signature64{};
    std::uint64_t neighborhood_binding_signature64{};
    std::uint64_t sequence{};
    std::int8_t admission_feedback_trinary{};
    bool vm81_hash216_verified{};
    bool speculative_only{};
};

struct PrimeLaneMetabolicStateV9 final {
    std::uint64_t neighborhood_binding_signature64{};
    std::uint64_t vitality_capacity{HHS_PASS219_PRIME_LANE_METABOLIC_VITALITY_CAP};
    std::uint64_t vitality{};
    std::uint64_t positive_verified{};
    std::uint64_t negative_verified{};
    std::uint64_t budget_credit_total{};
    std::uint64_t decay_total{};
    std::uint64_t last_sequence{};
    std::uint64_t metabolic_ordinal{};
    PrimeLaneVerifiedMetabolismAuthorityV9 authority{};
};

struct PrimeLaneMetabolicReceiptV9 final {
    std::uint64_t verdict_signature64{};
    std::uint64_t neighborhood_binding_signature64{};
    std::uint64_t sequence{};
    std::int8_t admission_feedback_trinary{};
    std::uint64_t vitality_before{};
    std::uint64_t decay_applied{};
    std::uint64_t reward_applied{};
    std::uint64_t penalty_applied{};
    std::uint64_t vitality_after{};
    std::uint64_t budget_before{};
    std::uint64_t budget_credit{};
    std::uint64_t budget_after{};
    std::uint64_t metabolic_ordinal{};
    PrimeLaneVerifiedMetabolismAuthorityV9 authority{};
};

class PrimeLaneVerifiedOutcomeMetabolismV9 final {
public:
    bool register_route(
        std::uint64_t neighborhood_binding_signature64,
        std::uint64_t initial_vitality) {
        if (neighborhood_binding_signature64 == 0U ||
            initial_vitality > HHS_PASS219_PRIME_LANE_METABOLIC_VITALITY_CAP ||
            states_.find(neighborhood_binding_signature64) != states_.end())
            return false;
        PrimeLaneMetabolicStateV9 state{};
        state.neighborhood_binding_signature64 = neighborhood_binding_signature64;
        state.vitality = initial_vitality;
        states_.emplace(neighborhood_binding_signature64, state);
        return hhs_pass219_prime_lane_verified_metabolism_authority_valid(state.authority);
    }

    bool state_for(
        std::uint64_t neighborhood_binding_signature64,
        PrimeLaneMetabolicStateV9& out) const {
        out = PrimeLaneMetabolicStateV9{};
        const auto it = states_.find(neighborhood_binding_signature64);
        if (it == states_.end())
            return false;
        out = it->second;
        return true;
    }

    bool apply_verified_outcome(
        const PrimeLaneVerifiedOutcomeV9& event,
        PrimeLaneBudgetedPredictiveHydratorV8& hydrator,
        PrimeLaneMetabolicReceiptV9& out) {
        out = PrimeLaneMetabolicReceiptV9{};
        if (!event_valid(event) || consumed_verdicts_.find(event.verdict_signature64) != consumed_verdicts_.end())
            return false;

        auto state_it = states_.find(event.neighborhood_binding_signature64);
        if (state_it == states_.end())
            return false;
        const auto& prior = state_it->second;
        if (event.sequence <= prior.last_sequence)
            return false;

        PrimeLaneActivationBudgetStateV8 budget{};
        if (!hydrator.budget_for(event.neighborhood_binding_signature64, budget))
            return false;
        if (!hhs_pass219_prime_lane_budgeted_hydration_authority_valid(budget.authority))
            return false;

        PrimeLaneMetabolicStateV9 next = prior;
        out.verdict_signature64 = event.verdict_signature64;
        out.neighborhood_binding_signature64 = event.neighborhood_binding_signature64;
        out.sequence = event.sequence;
        out.admission_feedback_trinary = event.admission_feedback_trinary;
        out.vitality_before = prior.vitality;
        out.budget_before = budget.available;

        const std::uint64_t gap_steps = decay_steps(prior.last_sequence, event.sequence);
        const std::uint64_t requested_decay = gap_steps * HHS_PASS219_PRIME_LANE_METABOLIC_DECAY_QUANTUM;
        out.decay_applied = std::min(next.vitality, requested_decay);
        next.vitality -= out.decay_applied;
        if (out.decay_applied > std::numeric_limits<std::uint64_t>::max() - next.decay_total)
            return false;
        next.decay_total += out.decay_applied;

        if (event.admission_feedback_trinary == 1) {
            const std::uint64_t room = next.vitality_capacity - next.vitality;
            out.reward_applied = std::min(room, HHS_PASS219_PRIME_LANE_METABOLIC_REWARD);
            next.vitality += out.reward_applied;
            if (next.positive_verified == std::numeric_limits<std::uint64_t>::max())
                return false;
            ++next.positive_verified;

            const std::uint64_t budget_room = budget.capacity - budget.available;
            out.budget_credit = std::min(budget_room, HHS_PASS219_PRIME_LANE_METABOLIC_BUDGET_CREDIT);
            if (out.budget_credit != 0U) {
                if (out.budget_credit > std::numeric_limits<std::uint64_t>::max() - next.budget_credit_total)
                    return false;
                if (!hydrator.replenish_budget(event.neighborhood_binding_signature64, out.budget_credit))
                    return false;
                next.budget_credit_total += out.budget_credit;
            }
        } else {
            out.penalty_applied = std::min(next.vitality, HHS_PASS219_PRIME_LANE_METABOLIC_PENALTY);
            next.vitality -= out.penalty_applied;
            if (next.negative_verified == std::numeric_limits<std::uint64_t>::max())
                return false;
            ++next.negative_verified;
        }

        if (next.metabolic_ordinal == std::numeric_limits<std::uint64_t>::max())
            return false;
        ++next.metabolic_ordinal;
        next.last_sequence = event.sequence;
        out.vitality_after = next.vitality;
        out.metabolic_ordinal = next.metabolic_ordinal;

        PrimeLaneActivationBudgetStateV8 budget_after{};
        if (!hydrator.budget_for(event.neighborhood_binding_signature64, budget_after))
            return false;
        out.budget_after = budget_after.available;
        if (out.budget_after - out.budget_before != out.budget_credit)
            return false;

        state_it->second = next;
        consumed_verdicts_.insert(event.verdict_signature64);
        return hhs_pass219_prime_lane_verified_metabolism_authority_valid(out.authority);
    }

    bool verdict_consumed(std::uint64_t verdict_signature64) const noexcept {
        return verdict_signature64 != 0U && consumed_verdicts_.find(verdict_signature64) != consumed_verdicts_.end();
    }

    std::size_t route_count() const noexcept { return states_.size(); }
    std::size_t consumed_verdict_count() const noexcept { return consumed_verdicts_.size(); }

private:
    static bool event_valid(const PrimeLaneVerifiedOutcomeV9& event) noexcept {
        return event.verdict_signature64 != 0U &&
               event.neighborhood_binding_signature64 != 0U &&
               event.sequence != 0U &&
               (event.admission_feedback_trinary == 1 || event.admission_feedback_trinary == -1) &&
               event.vm81_hash216_verified && !event.speculative_only;
    }

    static std::uint64_t decay_steps(
        std::uint64_t last_sequence,
        std::uint64_t sequence) noexcept {
        if (last_sequence == 0U || sequence <= last_sequence + 1U)
            return 0U;
        const std::uint64_t gap = sequence - last_sequence - 1U;
        return std::min(gap, HHS_PASS219_PRIME_LANE_METABOLIC_DECAY_STEP_LIMIT);
    }

    std::map<std::uint64_t, PrimeLaneMetabolicStateV9> states_{};
    std::set<std::uint64_t> consumed_verdicts_{};
};

} // namespace hhs::rna

#endif
