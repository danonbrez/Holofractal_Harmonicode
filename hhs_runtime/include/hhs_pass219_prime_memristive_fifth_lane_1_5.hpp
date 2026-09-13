#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_5_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_5_HPP

#include "hhs_pass219_prime_memristive_fifth_lane_1_4.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <map>
#include <string>
#include <vector>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_NEIGHBORHOOD_REPLAY_VERSION = UINT32_C(0x00010005);
inline constexpr std::size_t HHS_PASS219_PRIME_LANE_REPLAY_RECEIPT_LIMIT = 1024U;
inline constexpr std::int32_t HHS_PASS219_PRIME_LANE_REPLAY_FEEDBACK_QUANTUM = INT32_C(128);
inline constexpr std::int32_t HHS_PASS219_PRIME_LANE_REPLAY_EFFICIENCY_CAP = INT32_C(64);

struct PrimeLaneNeighborhoodReplayAuthorityV6 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool hash216_reference_only{true};
    bool route_utility_only{true};
    bool multimodal_route_metadata_only{true};
    bool neighborhood_reference_only{true};
    bool replay_receipt_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    bool requires_inherited_vm81_hash216_admission{true};
};

constexpr bool hhs_pass219_prime_lane_neighborhood_replay_authority_valid(
    const PrimeLaneNeighborhoodReplayAuthorityV6& authority) noexcept {
    return authority.candidate_only && authority.exact_integer_only &&
           authority.hash216_reference_only && authority.route_utility_only &&
           authority.multimodal_route_metadata_only &&
           authority.neighborhood_reference_only && authority.replay_receipt_only &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority &&
           authority.requires_inherited_vm81_hash216_admission;
}

struct PrimeLaneHash216NeighborhoodMemberV6 final {
    std::array<char, HHS_EXACT_UQCEL_HASH216_STRLEN> identity216{};
    std::uint64_t identity_signature64{};
    std::uint32_t alias_cardinality{};
    PrimeLaneNeighborhoodReplayAuthorityV6 authority{};
};

struct PrimeLaneHash216NeighborhoodKeyV6 final {
    std::uint64_t source_context_signature64{};
    std::uint64_t composition_signature64{};
    std::uint8_t modality_mask{};

    bool operator<(const PrimeLaneHash216NeighborhoodKeyV6& other) const noexcept {
        if (source_context_signature64 != other.source_context_signature64)
            return source_context_signature64 < other.source_context_signature64;
        if (composition_signature64 != other.composition_signature64)
            return composition_signature64 < other.composition_signature64;
        return modality_mask < other.modality_mask;
    }
};

struct PrimeLaneHash216NeighborhoodRefV6 final {
    PrimeLaneHash216NeighborhoodKeyV6 key{};
    std::vector<PrimeLaneHash216NeighborhoodMemberV6> members{};
    std::uint64_t binding_signature64{};
    std::uint64_t observed_sequence{};
    PrimeLaneNeighborhoodReplayAuthorityV6 authority{};
};

struct PrimeLaneNeighborhoodRecallMetricsV6 final {
    std::uint64_t neighborhood_lookups{};
    std::uint64_t inherited_reference_reads{};
    std::uint64_t composed_reference_inputs{};
    std::uint64_t duplicate_identities_collapsed{};
    PrimeLaneNeighborhoodReplayAuthorityV6 authority{};
};

class PrimeLaneHash216NeighborhoodStoreV6 final {
public:
    bool bind(
        std::uint64_t source_context_signature64,
        std::uint64_t composition_signature64,
        std::uint8_t modality_mask,
        const PrimeLaneCanonicalCandidateResultV3& canonical,
        std::uint64_t sequence,
        PrimeLaneHash216NeighborhoodRefV6& out) {
        out = PrimeLaneHash216NeighborhoodRefV6{};
        if (source_context_signature64 == 0U || composition_signature64 == 0U ||
            !valid_modality_mask(modality_mask) || canonical.states.empty() ||
            !hhs_pass219_prime_lane_context_authority_valid(canonical.authority))
            return false;

        PrimeLaneHash216NeighborhoodRefV6 candidate{};
        candidate.key = {source_context_signature64, composition_signature64, modality_mask};
        candidate.observed_sequence = sequence;
        for (const auto& group : canonical.states) {
            if (!hhs_pass219_prime_lane_context_authority_valid(group.authority) ||
                group.identity_signature64 == 0U || group.record_ids.empty() ||
                !identity_exact(group.identity216))
                return false;
            PrimeLaneHash216NeighborhoodMemberV6 member{};
            member.identity216 = group.identity216;
            member.identity_signature64 = group.identity_signature64;
            member.alias_cardinality = static_cast<std::uint32_t>(group.record_ids.size());
            candidate.members.push_back(member);
        }
        normalize_members(candidate.members);
        if (candidate.members.empty())
            return false;
        candidate.binding_signature64 = binding_signature(candidate);
        if (candidate.binding_signature64 == 0U)
            return false;

        const auto it = neighborhoods_.find(candidate.key);
        if (it != neighborhoods_.end() &&
            it->second.binding_signature64 != candidate.binding_signature64 &&
            sequence <= it->second.observed_sequence)
            return false;
        neighborhoods_[candidate.key] = candidate;
        out = candidate;
        return true;
    }

    bool recall(
        std::uint64_t source_context_signature64,
        std::uint64_t composition_signature64,
        std::uint8_t active_modality_mask,
        PrimeLaneHash216NeighborhoodRefV6& out,
        PrimeLaneNeighborhoodRecallMetricsV6& metrics) const {
        out = PrimeLaneHash216NeighborhoodRefV6{};
        metrics = PrimeLaneNeighborhoodRecallMetricsV6{};
        if (source_context_signature64 == 0U || composition_signature64 == 0U ||
            !valid_modality_mask(active_modality_mask))
            return false;
        ++metrics.neighborhood_lookups;

        const PrimeLaneHash216NeighborhoodRefV6* best = nullptr;
        std::uint8_t best_overlap = 0U;
        for (const auto& pair : neighborhoods_) {
            const auto& n = pair.second;
            if (n.key.source_context_signature64 != source_context_signature64 ||
                n.key.composition_signature64 != composition_signature64)
                continue;
            const std::uint8_t overlap = static_cast<std::uint8_t>(
                n.key.modality_mask & active_modality_mask);
            if (overlap == 0U)
                continue;
            const std::uint8_t width = popcount(overlap);
            if (best == nullptr || width > best_overlap ||
                (width == best_overlap && n.observed_sequence > best->observed_sequence) ||
                (width == best_overlap && n.observed_sequence == best->observed_sequence &&
                 n.binding_signature64 < best->binding_signature64)) {
                best = &n;
                best_overlap = width;
            }
        }
        if (best == nullptr)
            return false;
        out = *best;
        metrics.inherited_reference_reads = out.members.size();
        return true;
    }

    bool compose(
        std::vector<PrimeLaneHash216NeighborhoodRefV6> inputs,
        std::uint8_t active_modality_mask,
        PrimeLaneHash216NeighborhoodRefV6& out,
        PrimeLaneNeighborhoodRecallMetricsV6& metrics) const {
        out = PrimeLaneHash216NeighborhoodRefV6{};
        metrics = PrimeLaneNeighborhoodRecallMetricsV6{};
        if (inputs.empty() || !valid_modality_mask(active_modality_mask))
            return false;
        std::sort(inputs.begin(), inputs.end(), [](const auto& a, const auto& b) {
            return a.binding_signature64 < b.binding_signature64;
        });
        std::map<std::string, PrimeLaneHash216NeighborhoodMemberV6> merged{};
        std::uint64_t newest = 0U;
        for (const auto& input : inputs) {
            if (!valid_neighborhood(input) ||
                (input.key.modality_mask & active_modality_mask) == 0U)
                continue;
            ++metrics.composed_reference_inputs;
            newest = std::max(newest, input.observed_sequence);
            for (const auto& member : input.members) {
                const std::string key(member.identity216.data(), HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
                const auto it = merged.find(key);
                if (it == merged.end()) {
                    merged[key] = member;
                } else {
                    if (it->second.identity_signature64 != member.identity_signature64)
                        return false;
                    it->second.alias_cardinality =
                        std::max(it->second.alias_cardinality, member.alias_cardinality);
                    ++metrics.duplicate_identities_collapsed;
                }
            }
        }
        if (merged.empty())
            return false;
        out.key.modality_mask = active_modality_mask;
        out.observed_sequence = newest;
        for (const auto& pair : merged)
            out.members.push_back(pair.second);
        out.binding_signature64 = binding_signature(out);
        metrics.inherited_reference_reads = out.members.size();
        return out.binding_signature64 != 0U;
    }

    std::size_t size() const noexcept { return neighborhoods_.size(); }

private:
    static bool valid_modality_mask(std::uint8_t mask) noexcept {
        return mask != 0U && (mask & static_cast<std::uint8_t>(~HHS_PASS219_PRIME_LANE_MODALITY_ALL)) == 0U;
    }

    static std::uint8_t popcount(std::uint8_t value) noexcept {
        std::uint8_t count = 0U;
        while (value != 0U) {
            count = static_cast<std::uint8_t>(count + (value & 1U));
            value = static_cast<std::uint8_t>(value >> 1U);
        }
        return count;
    }

    static bool identity_exact(
        const std::array<char, HHS_EXACT_UQCEL_HASH216_STRLEN>& identity) noexcept {
        for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
            if (identity[i] == '\0')
                return false;
        }
        return identity[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] == '\0';
    }

    static bool member_less(
        const PrimeLaneHash216NeighborhoodMemberV6& a,
        const PrimeLaneHash216NeighborhoodMemberV6& b) noexcept {
        return std::lexicographical_compare(
            a.identity216.begin(), a.identity216.begin() + HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN,
            b.identity216.begin(), b.identity216.begin() + HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    }

    static void normalize_members(std::vector<PrimeLaneHash216NeighborhoodMemberV6>& members) {
        std::sort(members.begin(), members.end(), member_less);
        members.erase(std::unique(members.begin(), members.end(), [](const auto& a, const auto& b) {
            return a.identity216 == b.identity216 && a.identity_signature64 == b.identity_signature64;
        }), members.end());
    }

    static bool valid_neighborhood(const PrimeLaneHash216NeighborhoodRefV6& n) noexcept {
        if (!hhs_pass219_prime_lane_neighborhood_replay_authority_valid(n.authority) ||
            n.binding_signature64 == 0U || n.members.empty() ||
            !valid_modality_mask(n.key.modality_mask))
            return false;
        for (const auto& member : n.members) {
            if (!hhs_pass219_prime_lane_neighborhood_replay_authority_valid(member.authority) ||
                member.identity_signature64 == 0U || member.alias_cardinality == 0U ||
                !identity_exact(member.identity216))
                return false;
        }
        return true;
    }

    static std::uint64_t binding_signature(const PrimeLaneHash216NeighborhoodRefV6& n) noexcept {
        std::uint64_t hash = UINT64_C(1469598103934665603);
        mix(hash, n.key.source_context_signature64);
        mix(hash, n.key.composition_signature64);
        mix(hash, n.key.modality_mask);
        for (const auto& member : n.members) {
            for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
                hash ^= static_cast<unsigned char>(member.identity216[i]);
                hash *= UINT64_C(1099511628211);
            }
            mix(hash, member.identity_signature64);
            mix(hash, member.alias_cardinality);
        }
        mix(hash, n.members.size());
        return hash;
    }

    static void mix(std::uint64_t& hash, std::uint64_t value) noexcept {
        for (unsigned shift = 0U; shift < 64U; shift += 8U) {
            hash ^= (value >> shift) & UINT64_C(0xff);
            hash *= UINT64_C(1099511628211);
        }
    }

    std::map<PrimeLaneHash216NeighborhoodKeyV6, PrimeLaneHash216NeighborhoodRefV6> neighborhoods_{};
};

struct PrimeLaneReplayAssociationKeyV6 final {
    std::uint64_t query_context_signature64{};
    std::uint64_t source_context_signature64{};
    std::uint64_t composition_signature64{};
    std::uint64_t neighborhood_binding_signature64{};
    std::uint8_t modality_mask{};

    bool operator<(const PrimeLaneReplayAssociationKeyV6& other) const noexcept {
        if (query_context_signature64 != other.query_context_signature64)
            return query_context_signature64 < other.query_context_signature64;
        if (source_context_signature64 != other.source_context_signature64)
            return source_context_signature64 < other.source_context_signature64;
        if (composition_signature64 != other.composition_signature64)
            return composition_signature64 < other.composition_signature64;
        if (neighborhood_binding_signature64 != other.neighborhood_binding_signature64)
            return neighborhood_binding_signature64 < other.neighborhood_binding_signature64;
        return modality_mask < other.modality_mask;
    }
};

struct PrimeLaneReplayEventV6 final {
    PrimeLaneReplayAssociationKeyV6 key{};
    std::int8_t admission_feedback_trinary{};
    std::uint32_t warm_reference_work{};
    std::uint64_t cold_posting_work{};
    std::uint64_t sequence{};
    PrimeLaneNeighborhoodReplayAuthorityV6 authority{};
};

struct PrimeLaneReplayReceiptV6 final {
    PrimeLaneReplayAssociationKeyV6 key{};
    std::uint64_t sequence{};
    std::int32_t before_weight{};
    std::int32_t delta_weight{};
    std::int32_t after_weight{};
    std::uint64_t event_signature64{};
    std::uint64_t previous_receipt_signature64{};
    std::uint64_t receipt_signature64{};
    PrimeLaneNeighborhoodReplayAuthorityV6 authority{};
};

class PrimeLaneAdaptiveReplayLedgerV6 final {
public:
    bool apply(const PrimeLaneReplayEventV6& event, PrimeLaneReplayReceiptV6& out) {
        out = PrimeLaneReplayReceiptV6{};
        if (!valid_event(event) || receipts_.size() >= HHS_PASS219_PRIME_LANE_REPLAY_RECEIPT_LIMIT ||
            (last_sequence_ != 0U && event.sequence <= last_sequence_))
            return false;
        const std::int32_t before = weight_for(event.key);
        const std::int32_t delta = delta_for(event);
        const std::int32_t after = clip_weight(static_cast<std::int64_t>(before) + delta);
        PrimeLaneReplayReceiptV6 receipt{};
        receipt.key = event.key;
        receipt.sequence = event.sequence;
        receipt.before_weight = before;
        receipt.delta_weight = delta;
        receipt.after_weight = after;
        receipt.event_signature64 = event_signature(event);
        receipt.previous_receipt_signature64 = tip_signature64_;
        receipt.receipt_signature64 = receipt_signature(receipt);
        if (receipt.event_signature64 == 0U || receipt.receipt_signature64 == 0U)
            return false;
        weights_[event.key] = after;
        receipts_.push_back(receipt);
        tip_signature64_ = receipt.receipt_signature64;
        last_sequence_ = event.sequence;
        out = receipt;
        return true;
    }

    bool reverse_last(const PrimeLaneReplayReceiptV6& receipt) {
        if (receipts_.empty() ||
            receipts_.back().receipt_signature64 != receipt.receipt_signature64 ||
            receipt.receipt_signature64 != receipt_signature(receipt) ||
            tip_signature64_ != receipt.receipt_signature64 ||
            weight_for(receipt.key) != receipt.after_weight)
            return false;
        weights_[receipt.key] = receipt.before_weight;
        receipts_.pop_back();
        tip_signature64_ = receipt.previous_receipt_signature64;
        last_sequence_ = receipts_.empty() ? 0U : receipts_.back().sequence;
        return true;
    }

    std::int32_t weight_for(const PrimeLaneReplayAssociationKeyV6& key) const noexcept {
        const auto it = weights_.find(key);
        return it == weights_.end() ? 0 : it->second;
    }

    std::size_t receipt_count() const noexcept { return receipts_.size(); }
    std::uint64_t tip_signature64() const noexcept { return tip_signature64_; }
    std::uint64_t last_sequence() const noexcept { return last_sequence_; }

private:
    static bool valid_modality_mask(std::uint8_t mask) noexcept {
        return mask != 0U && (mask & static_cast<std::uint8_t>(~HHS_PASS219_PRIME_LANE_MODALITY_ALL)) == 0U;
    }

    static bool valid_event(const PrimeLaneReplayEventV6& event) noexcept {
        return hhs_pass219_prime_lane_neighborhood_replay_authority_valid(event.authority) &&
               event.key.query_context_signature64 != 0U &&
               event.key.source_context_signature64 != 0U &&
               event.key.composition_signature64 != 0U &&
               event.key.neighborhood_binding_signature64 != 0U &&
               valid_modality_mask(event.key.modality_mask) &&
               event.admission_feedback_trinary >= -1 && event.admission_feedback_trinary <= 1 &&
               event.sequence != 0U;
    }

    static std::int32_t delta_for(const PrimeLaneReplayEventV6& event) noexcept {
        if (event.admission_feedback_trinary == 0)
            return 0;
        const std::uint64_t saving = event.cold_posting_work > event.warm_reference_work
            ? event.cold_posting_work - event.warm_reference_work : 0U;
        const std::int32_t efficiency = static_cast<std::int32_t>(
            std::min<std::uint64_t>(saving, HHS_PASS219_PRIME_LANE_REPLAY_EFFICIENCY_CAP));
        const std::int32_t magnitude = HHS_PASS219_PRIME_LANE_REPLAY_FEEDBACK_QUANTUM + efficiency;
        return event.admission_feedback_trinary > 0 ? magnitude : -magnitude;
    }

    static std::uint64_t event_signature(const PrimeLaneReplayEventV6& event) noexcept {
        std::uint64_t hash = UINT64_C(1469598103934665603);
        mix(hash, event.key.query_context_signature64);
        mix(hash, event.key.source_context_signature64);
        mix(hash, event.key.composition_signature64);
        mix(hash, event.key.neighborhood_binding_signature64);
        mix(hash, event.key.modality_mask);
        mix(hash, static_cast<std::uint64_t>(static_cast<std::int64_t>(event.admission_feedback_trinary)));
        mix(hash, event.warm_reference_work);
        mix(hash, event.cold_posting_work);
        mix(hash, event.sequence);
        return hash;
    }

    static std::uint64_t receipt_signature(const PrimeLaneReplayReceiptV6& receipt) noexcept {
        std::uint64_t hash = UINT64_C(1469598103934665603);
        mix(hash, receipt.previous_receipt_signature64);
        mix(hash, receipt.event_signature64);
        mix(hash, receipt.sequence);
        mix(hash, static_cast<std::uint64_t>(static_cast<std::int64_t>(receipt.before_weight)));
        mix(hash, static_cast<std::uint64_t>(static_cast<std::int64_t>(receipt.delta_weight)));
        mix(hash, static_cast<std::uint64_t>(static_cast<std::int64_t>(receipt.after_weight)));
        return hash;
    }

    static std::int32_t clip_weight(std::int64_t value) noexcept {
        if (value > HHS_PASS219_PRIME_LANE_WEIGHT_BOUND)
            return HHS_PASS219_PRIME_LANE_WEIGHT_BOUND;
        if (value < -HHS_PASS219_PRIME_LANE_WEIGHT_BOUND)
            return -HHS_PASS219_PRIME_LANE_WEIGHT_BOUND;
        return static_cast<std::int32_t>(value);
    }

    static void mix(std::uint64_t& hash, std::uint64_t value) noexcept {
        for (unsigned shift = 0U; shift < 64U; shift += 8U) {
            hash ^= (value >> shift) & UINT64_C(0xff);
            hash *= UINT64_C(1099511628211);
        }
    }

    std::map<PrimeLaneReplayAssociationKeyV6, std::int32_t> weights_{};
    std::vector<PrimeLaneReplayReceiptV6> receipts_{};
    std::uint64_t tip_signature64_{};
    std::uint64_t last_sequence_{};
};

} // namespace hhs::rna

#endif
