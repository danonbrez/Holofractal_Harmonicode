#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_6_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_6_HPP

#include "hhs_pass219_prime_memristive_fifth_lane_1_5.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <map>
#include <vector>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_REPLAY_PREFETCH_VERSION = UINT32_C(0x00010006);
inline constexpr std::int32_t HHS_PASS219_PRIME_LANE_TRANSITION_FEEDBACK_QUANTUM = INT32_C(128);
inline constexpr std::size_t HHS_PASS219_PRIME_LANE_PREFETCH_LIMIT = 64U;

struct PrimeLaneReplayPrefetchAuthorityV7 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool hash216_reference_only{true};
    bool route_utility_only{true};
    bool multimodal_route_metadata_only{true};
    bool neighborhood_reference_only{true};
    bool replay_receipt_only{true};
    bool transition_association_only{true};
    bool predictive_prefetch_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    bool requires_inherited_vm81_hash216_admission{true};
};

constexpr bool hhs_pass219_prime_lane_replay_prefetch_authority_valid(
    const PrimeLaneReplayPrefetchAuthorityV7& authority) noexcept {
    return authority.candidate_only && authority.exact_integer_only &&
           authority.hash216_reference_only && authority.route_utility_only &&
           authority.multimodal_route_metadata_only &&
           authority.neighborhood_reference_only && authority.replay_receipt_only &&
           authority.transition_association_only && authority.predictive_prefetch_only &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority &&
           authority.requires_inherited_vm81_hash216_admission;
}

struct PrimeLaneNeighborhoodTransitionKeyV7 final {
    std::uint64_t from_neighborhood_binding_signature64{};
    PrimeLaneReplayAssociationKeyV6 target{};

    bool operator<(const PrimeLaneNeighborhoodTransitionKeyV7& other) const noexcept {
        if (from_neighborhood_binding_signature64 != other.from_neighborhood_binding_signature64)
            return from_neighborhood_binding_signature64 < other.from_neighborhood_binding_signature64;
        if (target < other.target)
            return true;
        if (other.target < target)
            return false;
        return false;
    }
};

struct PrimeLaneNeighborhoodTransitionStateV7 final {
    PrimeLaneNeighborhoodTransitionKeyV7 key{};
    std::int32_t transition_weight{};
    std::uint64_t observations{};
    std::uint64_t last_sequence{};
    PrimeLaneReplayPrefetchAuthorityV7 authority{};
};

struct PrimeLanePrefetchCandidateV7 final {
    PrimeLaneNeighborhoodTransitionStateV7 transition{};
    PrimeLaneHash216NeighborhoodRefV6 neighborhood{};
    std::int32_t replay_weight{};
    std::int32_t prefetch_score{};
    PrimeLaneReplayPrefetchAuthorityV7 authority{};
};

struct PrimeLanePrefetchMetricsV7 final {
    std::uint64_t transition_candidates_examined{};
    std::uint64_t modality_rejections{};
    std::uint64_t inherited_reference_reads{};
    std::uint64_t prefetch_hits{};
    std::uint64_t cold_fallbacks{};
    std::uint64_t ranking_signature64{};
    PrimeLaneReplayPrefetchAuthorityV7 authority{};
};

struct PrimeLanePredictiveQueryResultV7 final {
    std::vector<PrimeLanePrefetchCandidateV7> prefetched{};
    PrimeLaneCandidateResultV2 cold_raw{};
    PrimeLaneCanonicalCandidateResultV3 cold_canonical{};
    PrimeLanePrefetchMetricsV7 metrics{};
    bool used_prefetch{};
    bool used_cold_fallback{};
    PrimeLaneReplayPrefetchAuthorityV7 authority{};
};

class PrimeLaneReplayConditionedPrefetchV7 final {
public:
    bool register_target(
        const PrimeLaneReplayAssociationKeyV6& association,
        const PrimeLaneHash216NeighborhoodRefV6& neighborhood) {
        if (!valid_association(association) || !valid_neighborhood(neighborhood) ||
            association.neighborhood_binding_signature64 != neighborhood.binding_signature64 ||
            association.source_context_signature64 != neighborhood.key.source_context_signature64 ||
            association.composition_signature64 != neighborhood.key.composition_signature64 ||
            (association.modality_mask & neighborhood.key.modality_mask) == 0U)
            return false;
        const auto it = targets_.find(association);
        if (it != targets_.end() &&
            it->second.binding_signature64 != neighborhood.binding_signature64)
            return false;
        targets_[association] = neighborhood;
        return true;
    }

    bool observe_transition(
        std::uint64_t from_neighborhood_binding_signature64,
        const PrimeLaneReplayAssociationKeyV6& target,
        std::int8_t feedback_trinary,
        std::uint64_t sequence) {
        if (from_neighborhood_binding_signature64 == 0U ||
            feedback_trinary < -1 || feedback_trinary > 1 || sequence == 0U ||
            targets_.find(target) == targets_.end())
            return false;
        const PrimeLaneNeighborhoodTransitionKeyV7 key{
            from_neighborhood_binding_signature64, target};
        auto& state = transitions_[key];
        if (state.observations != 0U && sequence <= state.last_sequence)
            return false;
        state.key = key;
        const std::int32_t delta = static_cast<std::int32_t>(feedback_trinary) *
            HHS_PASS219_PRIME_LANE_TRANSITION_FEEDBACK_QUANTUM;
        state.transition_weight = clip_weight(
            static_cast<std::int64_t>(state.transition_weight) + delta);
        if (state.observations != std::numeric_limits<std::uint64_t>::max())
            ++state.observations;
        state.last_sequence = sequence;
        return hhs_pass219_prime_lane_replay_prefetch_authority_valid(state.authority);
    }

    bool transition_for(
        std::uint64_t from_neighborhood_binding_signature64,
        const PrimeLaneReplayAssociationKeyV6& target,
        PrimeLaneNeighborhoodTransitionStateV7& out) const {
        out = PrimeLaneNeighborhoodTransitionStateV7{};
        const PrimeLaneNeighborhoodTransitionKeyV7 key{
            from_neighborhood_binding_signature64, target};
        const auto it = transitions_.find(key);
        if (it == transitions_.end())
            return false;
        out = it->second;
        return true;
    }

    bool prefetch(
        std::uint64_t from_neighborhood_binding_signature64,
        std::uint8_t active_modality_mask,
        const PrimeLaneAdaptiveReplayLedgerV6& replay,
        std::size_t limit,
        std::vector<PrimeLanePrefetchCandidateV7>& out,
        PrimeLanePrefetchMetricsV7& metrics) const {
        out.clear();
        metrics = PrimeLanePrefetchMetricsV7{};
        if (from_neighborhood_binding_signature64 == 0U ||
            !valid_modality_mask(active_modality_mask) || limit == 0U ||
            limit > HHS_PASS219_PRIME_LANE_PREFETCH_LIMIT)
            return false;

        for (const auto& pair : transitions_) {
            const auto& state = pair.second;
            if (state.key.from_neighborhood_binding_signature64 !=
                from_neighborhood_binding_signature64)
                continue;
            ++metrics.transition_candidates_examined;
            const auto target_it = targets_.find(state.key.target);
            if (target_it == targets_.end() || !valid_neighborhood(target_it->second))
                return false;
            if ((state.key.target.modality_mask & active_modality_mask) == 0U) {
                ++metrics.modality_rejections;
                continue;
            }
            PrimeLanePrefetchCandidateV7 candidate{};
            candidate.transition = state;
            candidate.neighborhood = target_it->second;
            candidate.replay_weight = replay.weight_for(state.key.target);
            const std::int64_t score =
                static_cast<std::int64_t>(candidate.transition.transition_weight) +
                static_cast<std::int64_t>(candidate.replay_weight);
            candidate.prefetch_score = score > std::numeric_limits<std::int32_t>::max()
                ? std::numeric_limits<std::int32_t>::max()
                : score < std::numeric_limits<std::int32_t>::min()
                    ? std::numeric_limits<std::int32_t>::min()
                    : static_cast<std::int32_t>(score);
            out.push_back(candidate);
        }

        std::sort(out.begin(), out.end(), better_candidate);
        if (out.size() > limit)
            out.resize(limit);
        for (const auto& candidate : out)
            metrics.inherited_reference_reads += candidate.neighborhood.members.size();
        metrics.prefetch_hits = out.size();
        metrics.ranking_signature64 = ranking_signature(out);
        return true;
    }

    bool query_with_fallback(
        std::uint64_t from_neighborhood_binding_signature64,
        std::uint8_t active_modality_mask,
        const PrimeLaneAdaptiveReplayLedgerV6& replay,
        std::size_t prefetch_limit,
        const PrimeLaneHash216CandidateGraphV3& graph,
        const PrimeLaneRouteDecisionV1& cold_decision,
        std::uint32_t candidate_budget,
        PrimeLanePredictiveQueryResultV7& out) const {
        out = PrimeLanePredictiveQueryResultV7{};
        if (candidate_budget == 0U)
            return false;
        if (!prefetch(
                from_neighborhood_binding_signature64,
                active_modality_mask, replay, prefetch_limit,
                out.prefetched, out.metrics))
            return false;
        if (!out.prefetched.empty()) {
            out.used_prefetch = true;
            return true;
        }
        if (!graph.query(cold_decision, candidate_budget, out.cold_raw, out.cold_canonical))
            return false;
        out.used_cold_fallback = true;
        ++out.metrics.cold_fallbacks;
        return true;
    }

    std::size_t target_count() const noexcept { return targets_.size(); }
    std::size_t transition_count() const noexcept { return transitions_.size(); }

private:
    static bool valid_modality_mask(std::uint8_t mask) noexcept {
        return mask != 0U &&
            (mask & static_cast<std::uint8_t>(~HHS_PASS219_PRIME_LANE_MODALITY_ALL)) == 0U;
    }

    static bool valid_association(const PrimeLaneReplayAssociationKeyV6& key) noexcept {
        return key.query_context_signature64 != 0U &&
               key.source_context_signature64 != 0U &&
               key.composition_signature64 != 0U &&
               key.neighborhood_binding_signature64 != 0U &&
               valid_modality_mask(key.modality_mask);
    }

    static bool valid_neighborhood(const PrimeLaneHash216NeighborhoodRefV6& n) noexcept {
        if (!hhs_pass219_prime_lane_neighborhood_replay_authority_valid(n.authority) ||
            n.binding_signature64 == 0U || n.members.empty() ||
            !valid_modality_mask(n.key.modality_mask))
            return false;
        for (const auto& member : n.members) {
            if (!hhs_pass219_prime_lane_neighborhood_replay_authority_valid(member.authority) ||
                member.identity_signature64 == 0U || member.alias_cardinality == 0U)
                return false;
        }
        return true;
    }

    static bool better_candidate(
        const PrimeLanePrefetchCandidateV7& a,
        const PrimeLanePrefetchCandidateV7& b) noexcept {
        if (a.prefetch_score != b.prefetch_score)
            return a.prefetch_score > b.prefetch_score;
        if (a.transition.observations != b.transition.observations)
            return a.transition.observations > b.transition.observations;
        if (a.transition.last_sequence != b.transition.last_sequence)
            return a.transition.last_sequence > b.transition.last_sequence;
        if (a.neighborhood.binding_signature64 != b.neighborhood.binding_signature64)
            return a.neighborhood.binding_signature64 < b.neighborhood.binding_signature64;
        return a.transition.key.target.composition_signature64 <
               b.transition.key.target.composition_signature64;
    }

    static std::int32_t clip_weight(std::int64_t value) noexcept {
        if (value > HHS_PASS219_PRIME_LANE_WEIGHT_BOUND)
            return HHS_PASS219_PRIME_LANE_WEIGHT_BOUND;
        if (value < -HHS_PASS219_PRIME_LANE_WEIGHT_BOUND)
            return -HHS_PASS219_PRIME_LANE_WEIGHT_BOUND;
        return static_cast<std::int32_t>(value);
    }

    static std::uint64_t ranking_signature(
        const std::vector<PrimeLanePrefetchCandidateV7>& candidates) noexcept {
        std::uint64_t hash = UINT64_C(1469598103934665603);
        for (const auto& candidate : candidates) {
            mix(hash, candidate.transition.key.from_neighborhood_binding_signature64);
            mix(hash, candidate.transition.key.target.neighborhood_binding_signature64);
            mix(hash, candidate.transition.key.target.composition_signature64);
            mix(hash, candidate.transition.key.target.modality_mask);
            mix(hash, static_cast<std::uint64_t>(
                static_cast<std::int64_t>(candidate.transition.transition_weight)));
            mix(hash, static_cast<std::uint64_t>(
                static_cast<std::int64_t>(candidate.replay_weight)));
            mix(hash, static_cast<std::uint64_t>(
                static_cast<std::int64_t>(candidate.prefetch_score)));
        }
        mix(hash, candidates.size());
        return hash;
    }

    static void mix(std::uint64_t& hash, std::uint64_t value) noexcept {
        for (unsigned shift = 0U; shift < 64U; shift += 8U) {
            hash ^= (value >> shift) & UINT64_C(0xff);
            hash *= UINT64_C(1099511628211);
        }
    }

    std::map<PrimeLaneReplayAssociationKeyV6, PrimeLaneHash216NeighborhoodRefV6> targets_{};
    std::map<PrimeLaneNeighborhoodTransitionKeyV7, PrimeLaneNeighborhoodTransitionStateV7> transitions_{};
};

} // namespace hhs::rna

#endif
