#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_3_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_3_HPP

#include "hhs_pass219_prime_memristive_fifth_lane_1_2.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <map>
#include <vector>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_ADAPTIVE_CONTEXT_VERSION = UINT32_C(0x00010003);
inline constexpr std::int32_t HHS_PASS219_PRIME_LANE_UTILITY_SCALE = INT32_C(1024);
inline constexpr std::int32_t HHS_PASS219_PRIME_LANE_FEEDBACK_QUANTUM = INT32_C(128);

struct PrimeLaneAdaptiveContextAuthorityV4 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool hash216_reference_only{true};
    bool route_utility_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    bool requires_inherited_vm81_hash216_admission{true};
};

constexpr bool hhs_pass219_prime_lane_adaptive_authority_valid(
    const PrimeLaneAdaptiveContextAuthorityV4& authority) noexcept {
    return authority.candidate_only && authority.exact_integer_only &&
           authority.hash216_reference_only && authority.route_utility_only &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority &&
           authority.requires_inherited_vm81_hash216_admission;
}

struct PrimeLaneRouteUtilityV4 final {
    PrimeLaneContextRouteV3 route{};
    std::uint64_t uses{};
    std::uint64_t positive_feedback{};
    std::uint64_t negative_feedback{};
    std::uint64_t candidate_reduction_sum{};
    std::uint64_t posting_work_sum{};
    std::uint64_t last_observed_sequence{};
    std::int32_t utility_q10{};
    PrimeLaneAdaptiveContextAuthorityV4 authority{};
};

struct PrimeLaneAdaptiveQueryMetricsV4 final {
    std::uint64_t context_lookups{};
    std::uint64_t route_candidates_examined{};
    std::uint64_t stale_rejections{};
    std::uint64_t warm_route_hits{};
    std::uint64_t warm_axis_materializations{};
    std::uint64_t warm_selector_evaluations_avoided{};
    std::uint64_t cold_selector_evaluations{};
    std::uint64_t fallback_count{};
    std::uint64_t insufficient_reduction_fallbacks{};
    PrimeLaneAdaptiveContextAuthorityV4 authority{};
};

struct PrimeLaneAdaptiveQueryResultV4 final {
    PrimeLaneRouteDecisionV1 decision{};
    PrimeLaneCandidateResultV2 raw{};
    PrimeLaneCanonicalCandidateResultV3 canonical{};
    PrimeLaneAdaptiveQueryMetricsV4 metrics{};
    std::uint64_t selected_composition_signature64{};
    bool used_warm_route{};
    bool used_cold_fallback{};
    PrimeLaneAdaptiveContextAuthorityV4 authority{};
};

class PrimeLaneAdaptiveContextRouterV4 final {
public:
    bool register_route(const PrimeLaneContextRouteV3& route) {
        if (!valid_route(route))
            return false;
        auto& by_signature = routes_[route.context_signature64];
        auto& utility = by_signature[route.composition_signature64];
        if (utility.route.composition_signature64 != 0U &&
            !same_route(utility.route, route))
            return false;
        utility.route = route;
        return hhs_pass219_prime_lane_adaptive_authority_valid(utility.authority);
    }

    std::size_t route_count(std::uint64_t context_signature64) const noexcept {
        const auto it = routes_.find(context_signature64);
        return it == routes_.end() ? 0U : it->second.size();
    }

    bool utility_for(
        std::uint64_t context_signature64,
        std::uint64_t composition_signature64,
        PrimeLaneRouteUtilityV4& out) const {
        out = PrimeLaneRouteUtilityV4{};
        const auto context_it = routes_.find(context_signature64);
        if (context_it == routes_.end())
            return false;
        const auto route_it = context_it->second.find(composition_signature64);
        if (route_it == context_it->second.end())
            return false;
        out = route_it->second;
        return true;
    }

    bool observe(
        std::uint64_t context_signature64,
        std::uint64_t composition_signature64,
        std::uint32_t corpus_size,
        std::uint32_t candidate_count,
        std::uint64_t posting_work,
        std::int8_t admission_feedback_trinary,
        std::uint64_t sequence) {
        if (corpus_size == 0U || candidate_count > corpus_size ||
            admission_feedback_trinary < -1 || admission_feedback_trinary > 1)
            return false;
        auto* utility = mutable_utility(context_signature64, composition_signature64);
        if (utility == nullptr || !hhs_pass219_prime_lane_adaptive_authority_valid(utility->authority))
            return false;

        const std::uint64_t reduction =
            static_cast<std::uint64_t>(corpus_size - candidate_count);
        const std::uint64_t bounded_work = std::min<std::uint64_t>(posting_work, corpus_size);
        const std::int32_t reduction_q10 = static_cast<std::int32_t>(
            (reduction * static_cast<std::uint64_t>(HHS_PASS219_PRIME_LANE_UTILITY_SCALE)) /
            corpus_size);
        const std::int32_t posting_q10 = static_cast<std::int32_t>(
            (bounded_work * static_cast<std::uint64_t>(HHS_PASS219_PRIME_LANE_UTILITY_SCALE)) /
            corpus_size);
        const std::int32_t delta = reduction_q10 - posting_q10 +
            static_cast<std::int32_t>(admission_feedback_trinary) *
                HHS_PASS219_PRIME_LANE_FEEDBACK_QUANTUM;

        utility->utility_q10 = clip_utility(
            static_cast<std::int64_t>(utility->utility_q10) + delta);
        saturating_increment(utility->uses);
        if (admission_feedback_trinary > 0)
            saturating_increment(utility->positive_feedback);
        else if (admission_feedback_trinary < 0)
            saturating_increment(utility->negative_feedback);
        utility->candidate_reduction_sum = saturating_add(
            utility->candidate_reduction_sum, reduction);
        utility->posting_work_sum = saturating_add(
            utility->posting_work_sum, posting_work);
        utility->last_observed_sequence = sequence;
        return true;
    }

    bool decay_context(
        std::uint64_t context_signature64,
        std::uint32_t quantum) noexcept {
        if (quantum == 0U)
            return false;
        auto context_it = routes_.find(context_signature64);
        if (context_it == routes_.end())
            return false;
        for (auto& pair : context_it->second) {
            auto& value = pair.second.utility_q10;
            if (value > 0)
                value = std::max<std::int32_t>(0, value - static_cast<std::int32_t>(quantum));
            else if (value < 0)
                value = std::min<std::int32_t>(0, value + static_cast<std::int32_t>(quantum));
        }
        return true;
    }

    bool select_route(
        std::uint64_t context_signature64,
        std::uint64_t current_sequence,
        std::uint64_t max_age,
        PrimeLaneRouteUtilityV4& out,
        std::uint64_t& out_examined,
        std::uint64_t& out_stale_rejections) const {
        out = PrimeLaneRouteUtilityV4{};
        out_examined = 0U;
        out_stale_rejections = 0U;
        const auto context_it = routes_.find(context_signature64);
        if (context_it == routes_.end())
            return false;

        const PrimeLaneRouteUtilityV4* best = nullptr;
        for (const auto& pair : context_it->second) {
            const auto& candidate = pair.second;
            ++out_examined;
            if (!valid_utility(candidate))
                return false;
            if (is_stale(candidate, current_sequence, max_age)) {
                ++out_stale_rejections;
                continue;
            }
            if (best == nullptr || better(candidate, *best))
                best = &candidate;
        }
        if (best == nullptr)
            return false;
        out = *best;
        return true;
    }

    bool query_with_fallback(
        const PrimeLaneHash216CandidateGraphV3& graph,
        std::uint64_t context_signature64,
        const PrimeLaneFingerprintV1& fingerprint,
        const PrimeLaneRouterStateV1& cold_state,
        std::uint8_t cold_selected_count,
        std::uint32_t candidate_budget,
        std::uint64_t current_sequence,
        std::uint64_t max_age,
        PrimeLaneAdaptiveQueryResultV4& out) const {
        out = PrimeLaneAdaptiveQueryResultV4{};
        if (!hhs_pass219_prime_lane_authority_valid(fingerprint.authority) ||
            !PrimeMemristiveFifthLaneV1::validate_state(cold_state) ||
            cold_selected_count == 0U ||
            cold_selected_count > HHS_PASS219_PRIME_LANE_FIBRE_COUNT ||
            candidate_budget == 0U)
            return false;

        ++out.metrics.context_lookups;
        PrimeLaneRouteUtilityV4 selected{};
        std::uint64_t examined = 0U;
        std::uint64_t stale = 0U;
        const bool have_warm = select_route(
            context_signature64, current_sequence, max_age,
            selected, examined, stale);
        out.metrics.route_candidates_examined += examined;
        out.metrics.stale_rejections += stale;

        if (have_warm) {
            PrimeLaneRouteDecisionV1 warm_decision{};
            if (!materialize(selected.route, fingerprint, warm_decision))
                return false;
            ++out.metrics.warm_route_hits;
            out.metrics.warm_axis_materializations += warm_decision.selected_count;
            out.metrics.warm_selector_evaluations_avoided +=
                PrimeLaneContextRouteCacheV3::cold_selector_evaluations(
                    warm_decision.selected_count);
            PrimeLaneCandidateResultV2 warm_raw{};
            PrimeLaneCanonicalCandidateResultV3 warm_canonical{};
            if (!graph.query(warm_decision, candidate_budget, warm_raw, warm_canonical))
                return false;
            if (warm_raw.candidate_budget_reached) {
                out.decision = warm_decision;
                out.raw = std::move(warm_raw);
                out.canonical = std::move(warm_canonical);
                out.selected_composition_signature64 =
                    selected.route.composition_signature64;
                out.used_warm_route = true;
                return true;
            }
            ++out.metrics.fallback_count;
            ++out.metrics.insufficient_reduction_fallbacks;
        } else {
            ++out.metrics.fallback_count;
        }

        PrimeLaneRouteDecisionV1 cold_decision{};
        if (PrimeMemristiveFifthLaneV1::route(
                fingerprint, cold_state, cold_selected_count, cold_decision) !=
            PrimeLaneStatusV1::OK)
            return false;
        out.metrics.cold_selector_evaluations +=
            PrimeLaneContextRouteCacheV3::cold_selector_evaluations(
                cold_decision.selected_count);
        if (!graph.query(
                cold_decision, candidate_budget, out.raw, out.canonical))
            return false;
        out.decision = cold_decision;
        out.used_cold_fallback = true;
        return true;
    }

private:
    using RouteMap = std::map<std::uint64_t, PrimeLaneRouteUtilityV4>;

    PrimeLaneRouteUtilityV4* mutable_utility(
        std::uint64_t context_signature64,
        std::uint64_t composition_signature64) noexcept {
        const auto context_it = routes_.find(context_signature64);
        if (context_it == routes_.end())
            return nullptr;
        const auto route_it = context_it->second.find(composition_signature64);
        if (route_it == context_it->second.end())
            return nullptr;
        return &route_it->second;
    }

    static bool valid_route(const PrimeLaneContextRouteV3& route) noexcept {
        if (!hhs_pass219_prime_lane_context_authority_valid(route.authority) ||
            route.context_signature64 == 0U ||
            route.composition_signature64 == 0U ||
            route.selected_count == 0U ||
            route.selected_count > HHS_PASS219_PRIME_LANE_FIBRE_COUNT)
            return false;
        std::array<bool, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> seen{};
        for (std::size_t i = 0U; i < route.selected_count; ++i) {
            const std::size_t fibre = route.fibre_index[i];
            if (fibre >= HHS_PASS219_PRIME_LANE_FIBRE_COUNT || seen[fibre])
                return false;
            seen[fibre] = true;
        }
        return true;
    }

    static bool same_route(
        const PrimeLaneContextRouteV3& a,
        const PrimeLaneContextRouteV3& b) noexcept {
        if (a.context_signature64 != b.context_signature64 ||
            a.composition_signature64 != b.composition_signature64 ||
            a.selected_count != b.selected_count)
            return false;
        for (std::size_t i = 0U; i < a.selected_count; ++i) {
            if (a.fibre_index[i] != b.fibre_index[i])
                return false;
        }
        return true;
    }

    static bool valid_utility(const PrimeLaneRouteUtilityV4& utility) noexcept {
        return valid_route(utility.route) &&
               hhs_pass219_prime_lane_adaptive_authority_valid(utility.authority) &&
               utility.utility_q10 <= HHS_PASS219_PRIME_LANE_WEIGHT_BOUND &&
               utility.utility_q10 >= -HHS_PASS219_PRIME_LANE_WEIGHT_BOUND;
    }

    static bool is_stale(
        const PrimeLaneRouteUtilityV4& utility,
        std::uint64_t current_sequence,
        std::uint64_t max_age) noexcept {
        if (utility.uses == 0U || current_sequence <= utility.last_observed_sequence)
            return false;
        return current_sequence - utility.last_observed_sequence > max_age;
    }

    static bool better(
        const PrimeLaneRouteUtilityV4& a,
        const PrimeLaneRouteUtilityV4& b) noexcept {
        if (a.utility_q10 != b.utility_q10)
            return a.utility_q10 > b.utility_q10;
        if (a.positive_feedback != b.positive_feedback)
            return a.positive_feedback > b.positive_feedback;
        if (a.candidate_reduction_sum != b.candidate_reduction_sum)
            return a.candidate_reduction_sum > b.candidate_reduction_sum;
        if (a.posting_work_sum != b.posting_work_sum)
            return a.posting_work_sum < b.posting_work_sum;
        if (a.last_observed_sequence != b.last_observed_sequence)
            return a.last_observed_sequence > b.last_observed_sequence;
        return a.route.composition_signature64 < b.route.composition_signature64;
    }

    static bool materialize(
        const PrimeLaneContextRouteV3& route,
        const PrimeLaneFingerprintV1& fingerprint,
        PrimeLaneRouteDecisionV1& out) noexcept {
        out = PrimeLaneRouteDecisionV1{};
        if (!valid_route(route) ||
            !hhs_pass219_prime_lane_authority_valid(fingerprint.authority))
            return false;
        out.selected_count = route.selected_count;
        std::uint64_t hash = UINT64_C(1469598103934665603);
        mix(hash, route.composition_signature64);
        mix(hash, fingerprint.fingerprint_signature64);
        for (std::size_t slot = 0U; slot < route.selected_count; ++slot) {
            const std::size_t fibre = route.fibre_index[slot];
            const auto& coordinate = fingerprint.fibres[fibre];
            out.fibre_index[slot] = static_cast<std::uint8_t>(fibre);
            out.prime[slot] = coordinate.prime;
            out.u[slot] = coordinate.u;
            out.v[slot] = coordinate.v;
            out.rho[slot] = coordinate.rho;
            out.score[slot] = 0;
            mix(hash, fibre);
            mix(hash, coordinate.u);
            mix(hash, coordinate.v);
            mix(hash, coordinate.rho);
        }
        out.route_signature64 = hash;
        return true;
    }

    static void mix(std::uint64_t& hash, std::uint64_t value) noexcept {
        for (unsigned shift = 0U; shift < 64U; shift += 8U) {
            hash ^= (value >> shift) & UINT64_C(0xff);
            hash *= UINT64_C(1099511628211);
        }
    }

    static std::int32_t clip_utility(std::int64_t value) noexcept {
        if (value > HHS_PASS219_PRIME_LANE_WEIGHT_BOUND)
            return HHS_PASS219_PRIME_LANE_WEIGHT_BOUND;
        if (value < -HHS_PASS219_PRIME_LANE_WEIGHT_BOUND)
            return -HHS_PASS219_PRIME_LANE_WEIGHT_BOUND;
        return static_cast<std::int32_t>(value);
    }

    static void saturating_increment(std::uint64_t& value) noexcept {
        if (value != std::numeric_limits<std::uint64_t>::max())
            ++value;
    }

    static std::uint64_t saturating_add(
        std::uint64_t a,
        std::uint64_t b) noexcept {
        if (std::numeric_limits<std::uint64_t>::max() - a < b)
            return std::numeric_limits<std::uint64_t>::max();
        return a + b;
    }

    std::map<std::uint64_t, RouteMap> routes_{};
};

} // namespace hhs::rna

#endif
