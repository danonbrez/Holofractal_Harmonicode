#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_2_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_2_HPP

#include "hhs_pass219_prime_memristive_fifth_lane_1_1.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>
#include <map>
#include <string>
#include <vector>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_CONTEXT_VERSION = UINT32_C(0x00010002);

struct PrimeLaneContextAuthorityV3 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool hash216_reference_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    bool requires_inherited_vm81_hash216_admission{true};
};

constexpr bool hhs_pass219_prime_lane_context_authority_valid(
    const PrimeLaneContextAuthorityV3& authority) noexcept {
    return authority.candidate_only && authority.exact_integer_only &&
           authority.hash216_reference_only &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority &&
           authority.requires_inherited_vm81_hash216_admission;
}

struct PrimeLaneHash216ReferenceV3 final {
    std::uint32_t record_id{};
    std::array<char, HHS_EXACT_UQCEL_HASH216_STRLEN> identity216{};
    std::uint64_t identity_signature64{};
    PrimeLaneContextAuthorityV3 authority{};
};

struct PrimeLaneBoundRecordV3 final {
    PrimeLanePreparedRecordV2 indexed{};
    PrimeLaneHash216ReferenceV3 hash216{};
    PrimeLaneContextAuthorityV3 authority{};
};

class PrimeLaneHash216ReferenceBinderV3 final {
public:
    static std::uint64_t identity_signature64(
        const char identity216[HHS_EXACT_UQCEL_HASH216_STRLEN]) noexcept {
        if (!identity_exact(identity216))
            return 0U;
        std::uint64_t hash = UINT64_C(1469598103934665603);
        for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_STRLEN; ++i) {
            const unsigned char c = static_cast<unsigned char>(identity216[i]);
            hash ^= static_cast<std::uint64_t>(c);
            hash *= UINT64_C(1099511628211);
            if (c == 0U)
                break;
        }
        return hash;
    }

    static bool bind_reference(
        const PrimeLanePreparedRecordV2& record,
        const char inherited_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN],
        PrimeLaneBoundRecordV3& out) noexcept {
        out = PrimeLaneBoundRecordV3{};
        if (!hhs_pass219_prime_lane_index_authority_valid(record.authority) ||
            !hhs_pass219_prime_lane_authority_valid(record.fingerprint.authority) ||
            !identity_exact(inherited_identity216)) {
            return false;
        }
        const std::uint64_t signature = identity_signature64(inherited_identity216);
        if (signature == 0U || record.source_transition_signature64 != signature)
            return false;

        out.indexed = record;
        out.hash216.record_id = record.record_id;
        std::memcpy(
            out.hash216.identity216.data(),
            inherited_identity216,
            HHS_EXACT_UQCEL_HASH216_STRLEN);
        out.hash216.identity_signature64 = signature;
        return hhs_pass219_prime_lane_context_authority_valid(out.authority) &&
               hhs_pass219_prime_lane_context_authority_valid(out.hash216.authority);
    }

    static bool bind_transition(
        const PrimeLanePreparedRecordV2& record,
        const HHSExactPass219Hash216TransitionViewV1& transition,
        PrimeLaneBoundRecordV3& out) noexcept {
        return bind_reference(record, transition.transition_identity216, out);
    }

private:
    static bool identity_exact(
        const char identity216[HHS_EXACT_UQCEL_HASH216_STRLEN]) noexcept {
        if (identity216 == nullptr)
            return false;
        for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
            if (identity216[i] == '\0')
                return false;
        }
        return identity216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] == '\0';
    }
};

struct PrimeLaneHash216AliasGroupV3 final {
    std::array<char, HHS_EXACT_UQCEL_HASH216_STRLEN> identity216{};
    std::uint64_t identity_signature64{};
    std::vector<std::uint32_t> record_ids{};
    PrimeLaneContextAuthorityV3 authority{};
};

struct PrimeLaneCanonicalCandidateResultV3 final {
    std::vector<PrimeLaneHash216AliasGroupV3> states{};
    std::uint32_t raw_record_count{};
    std::uint32_t unique_hash216_count{};
    PrimeLaneContextAuthorityV3 authority{};
};

class PrimeLaneHash216CandidateGraphV3 final {
public:
    bool build(const std::vector<PrimeLaneBoundRecordV3>& records) {
        clear();
        std::vector<PrimeLanePreparedRecordV2> indexed{};
        indexed.reserve(records.size());

        for (const auto& record : records) {
            if (!valid_bound_record(record) ||
                record.hash216.record_id != record.indexed.record_id ||
                record_by_id_.find(record.indexed.record_id) != record_by_id_.end()) {
                clear();
                return false;
            }

            const std::size_t ordinal = records_.size();
            records_.push_back(record);
            record_by_id_[record.indexed.record_id] = ordinal;
            indexed.push_back(record.indexed);

            const std::string key = identity_key(record.hash216);
            auto& group = aliases_[key];
            if (group.record_ids.empty()) {
                group.identity216 = record.hash216.identity216;
                group.identity_signature64 = record.hash216.identity_signature64;
            } else if (group.identity_signature64 != record.hash216.identity_signature64 ||
                       group.identity216 != record.hash216.identity216) {
                clear();
                return false;
            }
            group.record_ids.push_back(record.indexed.record_id);
        }

        for (auto& pair : aliases_) {
            auto& ids = pair.second.record_ids;
            std::sort(ids.begin(), ids.end());
            ids.erase(std::unique(ids.begin(), ids.end()), ids.end());
        }

        if (!index_.build(indexed)) {
            clear();
            return false;
        }
        return true;
    }

    void clear() {
        index_.clear();
        records_.clear();
        record_by_id_.clear();
        aliases_.clear();
    }

    std::size_t record_count() const noexcept { return records_.size(); }
    std::size_t unique_hash216_count() const noexcept { return aliases_.size(); }
    std::size_t posting_key_count() const noexcept { return index_.posting_key_count(); }

    bool query(
        const PrimeLaneRouteDecisionV1& decision,
        std::uint32_t candidate_budget,
        PrimeLaneCandidateResultV2& out_raw,
        PrimeLaneCanonicalCandidateResultV3& out_canonical) const {
        out_canonical = PrimeLaneCanonicalCandidateResultV3{};
        if (!index_.query(decision, candidate_budget, out_raw))
            return false;
        return project_aliases(out_raw.record_ids, out_canonical);
    }

    bool linear_scan(
        const PrimeLaneRouteDecisionV1& decision,
        std::uint16_t axes_used,
        PrimeLaneLinearResultV2& out) const {
        return index_.linear_scan(decision, axes_used, out);
    }

    bool alias_group_for_record(
        std::uint32_t record_id,
        PrimeLaneHash216AliasGroupV3& out) const {
        out = PrimeLaneHash216AliasGroupV3{};
        const auto record_it = record_by_id_.find(record_id);
        if (record_it == record_by_id_.end())
            return false;
        const auto& record = records_[record_it->second];
        const auto alias_it = aliases_.find(identity_key(record.hash216));
        if (alias_it == aliases_.end())
            return false;
        out = alias_it->second;
        return true;
    }

private:
    static bool valid_bound_record(const PrimeLaneBoundRecordV3& record) noexcept {
        return hhs_pass219_prime_lane_context_authority_valid(record.authority) &&
               hhs_pass219_prime_lane_context_authority_valid(record.hash216.authority) &&
               hhs_pass219_prime_lane_index_authority_valid(record.indexed.authority) &&
               hhs_pass219_prime_lane_authority_valid(record.indexed.fingerprint.authority) &&
               record.hash216.identity_signature64 != 0U;
    }

    static std::string identity_key(const PrimeLaneHash216ReferenceV3& reference) {
        return std::string(
            reference.identity216.data(),
            static_cast<std::size_t>(HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN));
    }

    bool project_aliases(
        const std::vector<std::uint32_t>& raw_record_ids,
        PrimeLaneCanonicalCandidateResultV3& out) const {
        out = PrimeLaneCanonicalCandidateResultV3{};
        std::map<std::string, bool> selected{};
        for (const std::uint32_t record_id : raw_record_ids) {
            const auto record_it = record_by_id_.find(record_id);
            if (record_it == record_by_id_.end())
                return false;
            const auto& record = records_[record_it->second];
            selected[identity_key(record.hash216)] = true;
        }
        for (const auto& pair : selected) {
            const auto alias_it = aliases_.find(pair.first);
            if (alias_it == aliases_.end())
                return false;
            out.states.push_back(alias_it->second);
        }
        out.raw_record_count = static_cast<std::uint32_t>(raw_record_ids.size());
        out.unique_hash216_count = static_cast<std::uint32_t>(out.states.size());
        return true;
    }

    PrimeLaneCandidateIndexV2 index_{};
    std::vector<PrimeLaneBoundRecordV3> records_{};
    std::map<std::uint32_t, std::size_t> record_by_id_{};
    std::map<std::string, PrimeLaneHash216AliasGroupV3> aliases_{};
};

struct PrimeLaneContextRouteV3 final {
    std::uint64_t context_signature64{};
    std::uint16_t component_plan_count{};
    std::uint8_t selected_count{};
    std::array<std::uint8_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> fibre_index{};
    std::uint64_t composition_signature64{};
    PrimeLaneContextAuthorityV3 authority{};
};

struct PrimeLaneWarmRouteMetricsV3 final {
    std::uint64_t context_cache_lookups{};
    std::uint64_t axis_materializations{};
    std::uint64_t cold_selector_evaluations_avoided{};
    PrimeLaneContextAuthorityV3 authority{};
};

class PrimeLaneContextRouteCacheV3 final {
public:
    bool compose_and_store(
        std::uint64_t context_signature64,
        std::vector<PrimeLaneRoutePlanV2> plans,
        PrimeLaneContextRouteV3& out) {
        out = PrimeLaneContextRouteV3{};
        if (context_signature64 == 0U || plans.empty())
            return false;
        for (const auto& plan : plans) {
            if (!valid_plan(plan))
                return false;
        }

        std::sort(plans.begin(), plans.end(), plan_less);
        std::array<bool, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> used{};
        PrimeLaneContextRouteV3 composed{};
        composed.context_signature64 = context_signature64;
        composed.component_plan_count = static_cast<std::uint16_t>(plans.size());

        std::uint64_t hash = UINT64_C(1469598103934665603);
        mix(hash, context_signature64);
        mix(hash, static_cast<std::uint64_t>(plans.size()));
        for (const auto& plan : plans) {
            mix(hash, plan.plan_signature64);
            for (std::size_t slot = 0U; slot < plan.selected_count; ++slot) {
                const std::size_t fibre = plan.fibre_index[slot];
                if (used[fibre])
                    continue;
                used[fibre] = true;
                const std::size_t out_slot = composed.selected_count;
                composed.fibre_index[out_slot] = static_cast<std::uint8_t>(fibre);
                ++composed.selected_count;
                mix(hash, static_cast<std::uint64_t>(fibre));
            }
        }
        mix(hash, composed.selected_count);
        composed.composition_signature64 = hash;
        cache_[context_signature64] = composed;
        out = composed;
        return true;
    }

    bool fetch(std::uint64_t context_signature64, PrimeLaneContextRouteV3& out) const {
        out = PrimeLaneContextRouteV3{};
        const auto it = cache_.find(context_signature64);
        if (it == cache_.end())
            return false;
        out = it->second;
        return true;
    }

    bool decision_for(
        std::uint64_t context_signature64,
        const PrimeLaneFingerprintV1& fingerprint,
        PrimeLaneRouteDecisionV1& out_decision,
        PrimeLaneWarmRouteMetricsV3& out_metrics) const {
        out_decision = PrimeLaneRouteDecisionV1{};
        out_metrics = PrimeLaneWarmRouteMetricsV3{};
        if (!hhs_pass219_prime_lane_authority_valid(fingerprint.authority))
            return false;
        ++out_metrics.context_cache_lookups;
        const auto it = cache_.find(context_signature64);
        if (it == cache_.end())
            return false;
        const auto& route = it->second;
        if (!hhs_pass219_prime_lane_context_authority_valid(route.authority))
            return false;

        std::uint64_t signature = UINT64_C(1469598103934665603);
        mix(signature, route.composition_signature64);
        mix(signature, fingerprint.fingerprint_signature64);
        out_decision.selected_count = route.selected_count;
        for (std::size_t slot = 0U; slot < route.selected_count; ++slot) {
            const std::size_t fibre = route.fibre_index[slot];
            const auto& coordinate = fingerprint.fibres[fibre];
            out_decision.fibre_index[slot] = static_cast<std::uint8_t>(fibre);
            out_decision.prime[slot] = coordinate.prime;
            out_decision.u[slot] = coordinate.u;
            out_decision.v[slot] = coordinate.v;
            out_decision.rho[slot] = coordinate.rho;
            out_decision.score[slot] = 0;
            ++out_metrics.axis_materializations;
            mix(signature, static_cast<std::uint64_t>(fibre));
            mix(signature, coordinate.u);
            mix(signature, coordinate.v);
            mix(signature, coordinate.rho);
        }
        out_decision.route_signature64 = signature;
        out_metrics.cold_selector_evaluations_avoided =
            cold_selector_evaluations(route.selected_count);
        return true;
    }

    bool seed_router_state(
        std::uint64_t context_signature64,
        const PrimeLaneRouterStateV1& baseline,
        std::int16_t base_boost,
        PrimeLaneRouterStateV1& out_candidate) const noexcept {
        out_candidate = baseline;
        if (!PrimeMemristiveFifthLaneV1::validate_state(baseline) || base_boost == 0)
            return false;
        const auto it = cache_.find(context_signature64);
        if (it == cache_.end())
            return false;
        const auto& route = it->second;
        if (!hhs_pass219_prime_lane_context_authority_valid(route.authority))
            return false;

        bool changed = false;
        for (std::size_t slot = 0U; slot < route.selected_count; ++slot) {
            const std::size_t fibre = route.fibre_index[slot];
            const std::int32_t rank = static_cast<std::int32_t>(route.selected_count - slot);
            const std::int32_t delta = static_cast<std::int32_t>(base_boost) * rank;
            const std::int32_t proposed =
                static_cast<std::int32_t>(out_candidate.conductance[fibre]) + delta;
            const std::int16_t clipped = clip_weight(proposed);
            if (clipped != out_candidate.conductance[fibre]) {
                out_candidate.conductance[fibre] = clipped;
                changed = true;
            }
        }
        if (changed && out_candidate.update_count != std::numeric_limits<std::uint32_t>::max())
            ++out_candidate.update_count;
        if (out_candidate.step_count != std::numeric_limits<std::uint64_t>::max())
            ++out_candidate.step_count;
        return PrimeMemristiveFifthLaneV1::validate_state(out_candidate);
    }

    std::size_t size() const noexcept { return cache_.size(); }

    static std::uint64_t cold_selector_evaluations(std::uint8_t selected_count) noexcept {
        std::uint64_t total = 0U;
        for (std::uint8_t slot = 0U; slot < selected_count; ++slot)
            total += HHS_PASS219_PRIME_LANE_FIBRE_COUNT - slot;
        return total;
    }

private:
    static bool valid_plan(const PrimeLaneRoutePlanV2& plan) noexcept {
        if (!hhs_pass219_prime_lane_index_authority_valid(plan.authority) ||
            plan.selected_count > HHS_PASS219_PRIME_LANE_FIBRE_COUNT)
            return false;
        for (std::size_t i = 0U; i < plan.selected_count; ++i) {
            if (plan.fibre_index[i] >= HHS_PASS219_PRIME_LANE_FIBRE_COUNT)
                return false;
        }
        return true;
    }

    static bool plan_less(
        const PrimeLaneRoutePlanV2& a,
        const PrimeLaneRoutePlanV2& b) noexcept {
        if (a.plan_signature64 != b.plan_signature64)
            return a.plan_signature64 < b.plan_signature64;
        if (a.selected_count != b.selected_count)
            return a.selected_count < b.selected_count;
        return std::lexicographical_compare(
            a.fibre_index.begin(), a.fibre_index.begin() + a.selected_count,
            b.fibre_index.begin(), b.fibre_index.begin() + b.selected_count);
    }

    static void mix(std::uint64_t& hash, std::uint64_t value) noexcept {
        for (unsigned shift = 0U; shift < 64U; shift += 8U) {
            hash ^= (value >> shift) & UINT64_C(0xff);
            hash *= UINT64_C(1099511628211);
        }
    }

    static std::int16_t clip_weight(std::int32_t value) noexcept {
        if (value > HHS_PASS219_PRIME_LANE_WEIGHT_BOUND)
            return HHS_PASS219_PRIME_LANE_WEIGHT_BOUND;
        if (value < -HHS_PASS219_PRIME_LANE_WEIGHT_BOUND)
            return static_cast<std::int16_t>(-HHS_PASS219_PRIME_LANE_WEIGHT_BOUND);
        return static_cast<std::int16_t>(value);
    }

    std::map<std::uint64_t, PrimeLaneContextRouteV3> cache_{};
};

} // namespace hhs::rna

#endif
