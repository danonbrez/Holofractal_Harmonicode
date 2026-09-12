#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_4_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_4_HPP

#include "hhs_pass219_prime_memristive_fifth_lane_1_3.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <map>
#include <vector>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_MULTIMODAL_CONTEXT_VERSION = UINT32_C(0x00010004);
inline constexpr std::uint8_t HHS_PASS219_PRIME_LANE_MODALITY_TEXT = UINT8_C(1);
inline constexpr std::uint8_t HHS_PASS219_PRIME_LANE_MODALITY_VISION = UINT8_C(2);
inline constexpr std::uint8_t HHS_PASS219_PRIME_LANE_MODALITY_AUDIO = UINT8_C(4);
inline constexpr std::uint8_t HHS_PASS219_PRIME_LANE_MODALITY_CODE = UINT8_C(8);
inline constexpr std::uint8_t HHS_PASS219_PRIME_LANE_MODALITY_ALL = UINT8_C(15);
inline constexpr std::size_t HHS_PASS219_PRIME_LANE_MODALITY_COUNT = 4U;
inline constexpr std::uint8_t HHS_PASS219_PRIME_LANE_CONTEXT_MAX_DEPTH = UINT8_C(8);
inline constexpr std::size_t HHS_PASS219_PRIME_LANE_TOMBSTONE_LIMIT = 256U;

struct PrimeLaneMultimodalContextAuthorityV5 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool hash216_reference_only{true};
    bool route_utility_only{true};
    bool multimodal_route_metadata_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    bool requires_inherited_vm81_hash216_admission{true};
};

constexpr bool hhs_pass219_prime_lane_multimodal_authority_valid(
    const PrimeLaneMultimodalContextAuthorityV5& authority) noexcept {
    return authority.candidate_only && authority.exact_integer_only &&
           authority.hash216_reference_only && authority.route_utility_only &&
           authority.multimodal_route_metadata_only &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority &&
           authority.requires_inherited_vm81_hash216_admission;
}

struct PrimeLaneContextNodeV5 final {
    std::uint64_t context_signature64{};
    std::uint64_t parent_context_signature64{};
    std::uint8_t modality_mask{};
    std::uint8_t depth{};
    PrimeLaneMultimodalContextAuthorityV5 authority{};
};

struct PrimeLaneMultimodalRouteV5 final {
    PrimeLaneContextRouteV3 route{};
    std::uint8_t modality_mask{};
    std::array<std::int32_t, HHS_PASS219_PRIME_LANE_MODALITY_COUNT> utility_q10{};
    std::uint64_t observations{};
    std::uint64_t last_observed_sequence{};
    PrimeLaneMultimodalContextAuthorityV5 authority{};
};

enum class PrimeLaneRouteTombstoneReasonV5 : std::uint8_t {
    OBSOLETE = 1,
    NEGATIVE_FEEDBACK = 2,
    SUPERSEDED = 3,
    MANUAL_BOUNDARY = 4
};

struct PrimeLaneRouteTombstoneKeyV5 final {
    std::uint64_t query_context_signature64{};
    std::uint64_t source_context_signature64{};
    std::uint64_t composition_signature64{};

    bool operator<(const PrimeLaneRouteTombstoneKeyV5& other) const noexcept {
        if (query_context_signature64 != other.query_context_signature64)
            return query_context_signature64 < other.query_context_signature64;
        if (source_context_signature64 != other.source_context_signature64)
            return source_context_signature64 < other.source_context_signature64;
        return composition_signature64 < other.composition_signature64;
    }
};

struct PrimeLaneRouteTombstoneV5 final {
    PrimeLaneRouteTombstoneKeyV5 key{};
    std::uint64_t sequence{};
    PrimeLaneRouteTombstoneReasonV5 reason{PrimeLaneRouteTombstoneReasonV5::OBSOLETE};
    bool active{true};
    PrimeLaneMultimodalContextAuthorityV5 authority{};
};

struct PrimeLaneInheritedRouteSelectionV5 final {
    PrimeLaneMultimodalRouteV5 route{};
    std::uint64_t source_context_signature64{};
    std::uint8_t inheritance_distance{};
    std::uint8_t active_modality_mask{};
    std::int32_t active_utility_q10{};
    std::uint64_t candidates_examined{};
    std::uint64_t tombstones_skipped{};
    PrimeLaneMultimodalContextAuthorityV5 authority{};
};

struct PrimeLaneHierarchicalQueryMetricsV5 final {
    std::uint64_t hierarchy_lookups{};
    std::uint64_t route_candidates_examined{};
    std::uint64_t tombstones_skipped{};
    std::uint64_t inherited_route_hits{};
    std::uint64_t local_route_hits{};
    std::uint64_t warm_axis_materializations{};
    std::uint64_t warm_selector_evaluations_avoided{};
    std::uint64_t cold_selector_evaluations{};
    std::uint64_t fallback_count{};
    std::uint64_t insufficient_reduction_fallbacks{};
    PrimeLaneMultimodalContextAuthorityV5 authority{};
};

struct PrimeLaneHierarchicalQueryResultV5 final {
    PrimeLaneRouteDecisionV1 decision{};
    PrimeLaneCandidateResultV2 raw{};
    PrimeLaneCanonicalCandidateResultV3 canonical{};
    PrimeLaneHierarchicalQueryMetricsV5 metrics{};
    std::uint64_t selected_source_context_signature64{};
    std::uint64_t selected_composition_signature64{};
    std::uint8_t inheritance_distance{};
    bool used_warm_route{};
    bool used_cold_fallback{};
    PrimeLaneMultimodalContextAuthorityV5 authority{};
};

class PrimeLaneMultimodalContextRouterV5 final {
public:
    bool register_context(
        std::uint64_t context_signature64,
        std::uint64_t parent_context_signature64,
        std::uint8_t modality_mask) {
        if (context_signature64 == 0U || !valid_modality_mask(modality_mask) ||
            context_signature64 == parent_context_signature64 ||
            contexts_.find(context_signature64) != contexts_.end())
            return false;

        std::uint8_t depth = 0U;
        if (parent_context_signature64 != 0U) {
            const auto parent_it = contexts_.find(parent_context_signature64);
            if (parent_it == contexts_.end())
                return false;
            if (parent_it->second.depth >= HHS_PASS219_PRIME_LANE_CONTEXT_MAX_DEPTH)
                return false;
            depth = static_cast<std::uint8_t>(parent_it->second.depth + 1U);
        }

        PrimeLaneContextNodeV5 node{};
        node.context_signature64 = context_signature64;
        node.parent_context_signature64 = parent_context_signature64;
        node.modality_mask = modality_mask;
        node.depth = depth;
        if (!hhs_pass219_prime_lane_multimodal_authority_valid(node.authority))
            return false;
        contexts_[context_signature64] = node;
        return true;
    }

    bool register_route(
        std::uint64_t source_context_signature64,
        const PrimeLaneContextRouteV3& route,
        std::uint8_t modality_mask) {
        const auto context_it = contexts_.find(source_context_signature64);
        if (context_it == contexts_.end() || !valid_modality_mask(modality_mask) ||
            (modality_mask & static_cast<std::uint8_t>(~context_it->second.modality_mask)) != 0U ||
            !valid_route(route) ||
            route.context_signature64 != source_context_signature64)
            return false;

        auto& entry = routes_[source_context_signature64][route.composition_signature64];
        if (entry.route.composition_signature64 != 0U &&
            !same_route(entry.route, route))
            return false;
        entry.route = route;
        entry.modality_mask = modality_mask;
        return hhs_pass219_prime_lane_multimodal_authority_valid(entry.authority);
    }

    bool observe_route(
        std::uint64_t source_context_signature64,
        std::uint64_t composition_signature64,
        std::uint8_t modality_mask,
        std::int32_t gain_q10,
        std::int8_t admission_feedback_trinary,
        std::uint64_t sequence) noexcept {
        if (!valid_modality_mask(modality_mask) || admission_feedback_trinary < -1 ||
            admission_feedback_trinary > 1)
            return false;
        auto* route = mutable_route(source_context_signature64, composition_signature64);
        if (route == nullptr ||
            (modality_mask & route->modality_mask) == 0U ||
            !hhs_pass219_prime_lane_multimodal_authority_valid(route->authority))
            return false;

        const std::int32_t feedback =
            static_cast<std::int32_t>(admission_feedback_trinary) *
            HHS_PASS219_PRIME_LANE_FEEDBACK_QUANTUM;
        for (std::size_t i = 0U; i < HHS_PASS219_PRIME_LANE_MODALITY_COUNT; ++i) {
            const std::uint8_t bit = static_cast<std::uint8_t>(UINT8_C(1) << i);
            if ((modality_mask & route->modality_mask & bit) == 0U)
                continue;
            route->utility_q10[i] = clip_utility(
                static_cast<std::int64_t>(route->utility_q10[i]) + gain_q10 + feedback);
        }
        saturating_increment(route->observations);
        route->last_observed_sequence = sequence;
        return true;
    }

    bool set_tombstone(
        std::uint64_t query_context_signature64,
        std::uint64_t source_context_signature64,
        std::uint64_t composition_signature64,
        std::uint64_t sequence,
        PrimeLaneRouteTombstoneReasonV5 reason) {
        if (!is_ancestor_or_self(query_context_signature64, source_context_signature64) ||
            route_ptr(source_context_signature64, composition_signature64) == nullptr)
            return false;
        PrimeLaneRouteTombstoneKeyV5 key{
            query_context_signature64, source_context_signature64, composition_signature64};
        auto it = tombstones_.find(key);
        if (it == tombstones_.end() && tombstones_.size() >= HHS_PASS219_PRIME_LANE_TOMBSTONE_LIMIT)
            return false;
        PrimeLaneRouteTombstoneV5 tombstone{};
        tombstone.key = key;
        tombstone.sequence = sequence;
        tombstone.reason = reason;
        tombstone.active = true;
        if (!hhs_pass219_prime_lane_multimodal_authority_valid(tombstone.authority))
            return false;
        tombstones_[key] = tombstone;
        return true;
    }

    bool clear_tombstone(
        std::uint64_t query_context_signature64,
        std::uint64_t source_context_signature64,
        std::uint64_t composition_signature64,
        std::uint64_t sequence) noexcept {
        const PrimeLaneRouteTombstoneKeyV5 key{
            query_context_signature64, source_context_signature64, composition_signature64};
        const auto it = tombstones_.find(key);
        if (it == tombstones_.end())
            return false;
        it->second.active = false;
        it->second.sequence = sequence;
        return true;
    }

    bool tombstoned(
        std::uint64_t query_context_signature64,
        std::uint64_t source_context_signature64,
        std::uint64_t composition_signature64) const noexcept {
        const PrimeLaneRouteTombstoneKeyV5 key{
            query_context_signature64, source_context_signature64, composition_signature64};
        const auto it = tombstones_.find(key);
        return it != tombstones_.end() && it->second.active;
    }

    std::size_t tombstone_count() const noexcept { return tombstones_.size(); }

    bool select_route(
        std::uint64_t query_context_signature64,
        std::uint8_t query_modality_mask,
        PrimeLaneInheritedRouteSelectionV5& out) const {
        out = PrimeLaneInheritedRouteSelectionV5{};
        const auto query_it = contexts_.find(query_context_signature64);
        if (query_it == contexts_.end() || !valid_modality_mask(query_modality_mask) ||
            (query_it->second.modality_mask & query_modality_mask) == 0U)
            return false;

        bool found = false;
        std::uint64_t source_context = query_context_signature64;
        std::uint8_t distance = 0U;
        while (source_context != 0U && distance <= HHS_PASS219_PRIME_LANE_CONTEXT_MAX_DEPTH) {
            const auto routes_it = routes_.find(source_context);
            if (routes_it != routes_.end()) {
                for (const auto& pair : routes_it->second) {
                    const auto& candidate = pair.second;
                    ++out.candidates_examined;
                    const std::uint8_t active_mask =
                        static_cast<std::uint8_t>(candidate.modality_mask & query_modality_mask);
                    if (active_mask == 0U)
                        continue;
                    if (tombstoned(
                            query_context_signature64,
                            source_context,
                            candidate.route.composition_signature64)) {
                        ++out.tombstones_skipped;
                        continue;
                    }
                    const std::int32_t active_utility =
                        active_utility_q10(candidate, active_mask);
                    if (!found || better(
                            candidate, source_context, distance, active_mask, active_utility,
                            out.route, out.source_context_signature64,
                            out.inheritance_distance, out.active_modality_mask,
                            out.active_utility_q10)) {
                        found = true;
                        out.route = candidate;
                        out.source_context_signature64 = source_context;
                        out.inheritance_distance = distance;
                        out.active_modality_mask = active_mask;
                        out.active_utility_q10 = active_utility;
                    }
                }
            }
            const auto node_it = contexts_.find(source_context);
            if (node_it == contexts_.end())
                return false;
            source_context = node_it->second.parent_context_signature64;
            ++distance;
        }
        return found;
    }

    bool query_with_fallback(
        const PrimeLaneHash216CandidateGraphV3& graph,
        std::uint64_t query_context_signature64,
        std::uint8_t query_modality_mask,
        const PrimeLaneFingerprintV1& fingerprint,
        const PrimeLaneRouterStateV1& cold_state,
        std::uint8_t cold_selected_count,
        std::uint32_t candidate_budget,
        PrimeLaneHierarchicalQueryResultV5& out) const {
        out = PrimeLaneHierarchicalQueryResultV5{};
        if (!hhs_pass219_prime_lane_authority_valid(fingerprint.authority) ||
            !PrimeMemristiveFifthLaneV1::validate_state(cold_state) ||
            cold_selected_count == 0U ||
            cold_selected_count > HHS_PASS219_PRIME_LANE_FIBRE_COUNT ||
            candidate_budget == 0U)
            return false;

        ++out.metrics.hierarchy_lookups;
        PrimeLaneInheritedRouteSelectionV5 selected{};
        if (select_route(query_context_signature64, query_modality_mask, selected)) {
            out.metrics.route_candidates_examined = selected.candidates_examined;
            out.metrics.tombstones_skipped = selected.tombstones_skipped;
            PrimeLaneRouteDecisionV1 warm_decision{};
            if (!materialize(selected.route.route, fingerprint, warm_decision))
                return false;
            out.metrics.warm_axis_materializations = warm_decision.selected_count;
            out.metrics.warm_selector_evaluations_avoided =
                PrimeLaneContextRouteCacheV3::cold_selector_evaluations(
                    warm_decision.selected_count);
            if (selected.inheritance_distance == 0U)
                ++out.metrics.local_route_hits;
            else
                ++out.metrics.inherited_route_hits;

            PrimeLaneCandidateResultV2 warm_raw{};
            PrimeLaneCanonicalCandidateResultV3 warm_canonical{};
            if (!graph.query(warm_decision, candidate_budget, warm_raw, warm_canonical))
                return false;
            if (warm_raw.candidate_budget_reached) {
                out.decision = warm_decision;
                out.raw = std::move(warm_raw);
                out.canonical = std::move(warm_canonical);
                out.selected_source_context_signature64 =
                    selected.source_context_signature64;
                out.selected_composition_signature64 =
                    selected.route.route.composition_signature64;
                out.inheritance_distance = selected.inheritance_distance;
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
        out.metrics.cold_selector_evaluations =
            PrimeLaneContextRouteCacheV3::cold_selector_evaluations(
                cold_decision.selected_count);
        if (!graph.query(cold_decision, candidate_budget, out.raw, out.canonical))
            return false;
        out.decision = cold_decision;
        out.used_cold_fallback = true;
        return true;
    }

private:
    using RouteMap = std::map<std::uint64_t, PrimeLaneMultimodalRouteV5>;

    static bool valid_modality_mask(std::uint8_t mask) noexcept {
        return mask != 0U && (mask & static_cast<std::uint8_t>(~HHS_PASS219_PRIME_LANE_MODALITY_ALL)) == 0U;
    }

    static bool valid_route(const PrimeLaneContextRouteV3& route) noexcept {
        if (!hhs_pass219_prime_lane_context_authority_valid(route.authority) ||
            route.context_signature64 == 0U || route.composition_signature64 == 0U ||
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

    PrimeLaneMultimodalRouteV5* mutable_route(
        std::uint64_t source_context_signature64,
        std::uint64_t composition_signature64) noexcept {
        const auto context_it = routes_.find(source_context_signature64);
        if (context_it == routes_.end())
            return nullptr;
        const auto route_it = context_it->second.find(composition_signature64);
        if (route_it == context_it->second.end())
            return nullptr;
        return &route_it->second;
    }

    const PrimeLaneMultimodalRouteV5* route_ptr(
        std::uint64_t source_context_signature64,
        std::uint64_t composition_signature64) const noexcept {
        const auto context_it = routes_.find(source_context_signature64);
        if (context_it == routes_.end())
            return nullptr;
        const auto route_it = context_it->second.find(composition_signature64);
        if (route_it == context_it->second.end())
            return nullptr;
        return &route_it->second;
    }

    bool is_ancestor_or_self(
        std::uint64_t query_context_signature64,
        std::uint64_t possible_ancestor_signature64) const noexcept {
        std::uint64_t cursor = query_context_signature64;
        std::uint8_t depth = 0U;
        while (cursor != 0U && depth <= HHS_PASS219_PRIME_LANE_CONTEXT_MAX_DEPTH) {
            if (cursor == possible_ancestor_signature64)
                return true;
            const auto it = contexts_.find(cursor);
            if (it == contexts_.end())
                return false;
            cursor = it->second.parent_context_signature64;
            ++depth;
        }
        return false;
    }

    static std::int32_t active_utility_q10(
        const PrimeLaneMultimodalRouteV5& route,
        std::uint8_t active_mask) noexcept {
        std::int64_t total = 0;
        for (std::size_t i = 0U; i < HHS_PASS219_PRIME_LANE_MODALITY_COUNT; ++i) {
            const std::uint8_t bit = static_cast<std::uint8_t>(UINT8_C(1) << i);
            if ((active_mask & bit) != 0U)
                total += route.utility_q10[i];
        }
        if (total > std::numeric_limits<std::int32_t>::max())
            return std::numeric_limits<std::int32_t>::max();
        if (total < std::numeric_limits<std::int32_t>::min())
            return std::numeric_limits<std::int32_t>::min();
        return static_cast<std::int32_t>(total);
    }

    static bool better(
        const PrimeLaneMultimodalRouteV5& candidate,
        std::uint64_t candidate_source,
        std::uint8_t candidate_distance,
        std::uint8_t candidate_mask,
        std::int32_t candidate_utility,
        const PrimeLaneMultimodalRouteV5& current,
        std::uint64_t current_source,
        std::uint8_t current_distance,
        std::uint8_t current_mask,
        std::int32_t current_utility) noexcept {
        (void)candidate_source;
        (void)current_source;
        (void)candidate_mask;
        (void)current_mask;
        if (candidate_utility != current_utility)
            return candidate_utility > current_utility;
        if (candidate_distance != current_distance)
            return candidate_distance < current_distance;
        if (candidate.last_observed_sequence != current.last_observed_sequence)
            return candidate.last_observed_sequence > current.last_observed_sequence;
        return candidate.route.composition_signature64 <
               current.route.composition_signature64;
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
            mix(hash, static_cast<std::uint64_t>(fibre));
            mix(hash, coordinate.u);
            mix(hash, coordinate.v);
            mix(hash, coordinate.rho);
        }
        out.route_signature64 = hash;
        return true;
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

    static void mix(std::uint64_t& hash, std::uint64_t value) noexcept {
        for (unsigned shift = 0U; shift < 64U; shift += 8U) {
            hash ^= (value >> shift) & UINT64_C(0xff);
            hash *= UINT64_C(1099511628211);
        }
    }

    std::map<std::uint64_t, PrimeLaneContextNodeV5> contexts_{};
    std::map<std::uint64_t, RouteMap> routes_{};
    std::map<PrimeLaneRouteTombstoneKeyV5, PrimeLaneRouteTombstoneV5> tombstones_{};
};

} // namespace hhs::rna

#endif
