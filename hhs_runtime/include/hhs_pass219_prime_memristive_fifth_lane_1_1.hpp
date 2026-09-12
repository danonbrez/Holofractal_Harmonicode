#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_1_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_1_HPP

#include "hhs_pass219_prime_memristive_fifth_lane_1_0.hpp"
#include "hhs_pass219_core_holographic_four_lane_1_24.h"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <map>
#include <vector>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_INDEX_VERSION = UINT32_C(0x00010001);
inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_DEFAULT_CANDIDATE_BUDGET = UINT32_C(8);

struct PrimeLaneIndexAuthorityV2 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    bool requires_inherited_vm81_hash216_admission{true};
};

constexpr bool hhs_pass219_prime_lane_index_authority_valid(
    const PrimeLaneIndexAuthorityV2& authority) noexcept {
    return authority.candidate_only && authority.exact_integer_only &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority &&
           authority.requires_inherited_vm81_hash216_admission;
}

struct PrimeLanePreparedRecordV2 final {
    std::uint32_t record_id{};
    std::uint64_t source_transition_signature64{};
    std::array<std::int64_t, HHS_PASS219_PRIME_LANE_CELL_COUNT> cells{};
    PrimeLaneFingerprintV1 fingerprint{};
    PrimeLaneIndexAuthorityV2 authority{};
};

class PrimeLaneHolo4AdapterV2 final {
public:
    static PrimeLanePreparedRecordV2 adapt(
        std::uint32_t record_id,
        const HHSExactPass219Holo4PreparedV1& prepared) noexcept {
        PrimeLanePreparedRecordV2 out{};
        out.record_id = record_id;
        out.source_transition_signature64 = transition_signature(prepared);
        for (std::size_t i = 0U; i < HHS_PASS219_PRIME_LANE_CELL_COUNT; ++i) {
            const auto& cell = prepared.cells[i];
            std::uint64_t value = cell.local_signature64 & UINT64_C(0x7fffffffffffffff);
            value ^= static_cast<std::uint64_t>(cell.neighbor_popcount) << 40U;
            value ^= static_cast<std::uint64_t>(cell.self_popcount) << 32U;
            value ^= static_cast<std::uint64_t>(cell.hash216_position[0]) << 16U;
            value ^= static_cast<std::uint64_t>(cell.hash216_position[1]);
            value ^= static_cast<std::uint64_t>(cell.local_loshu) << 8U;
            value ^= static_cast<std::uint64_t>(cell.macro_loshu);
            out.cells[i] = static_cast<std::int64_t>(value & UINT64_C(0x7fffffffffffffff));
        }
        out.fingerprint = PrimeMemristiveFifthLaneV1::fingerprint(out.cells);
        return out;
    }

private:
    static std::uint64_t transition_signature(
        const HHSExactPass219Holo4PreparedV1& prepared) noexcept {
        std::uint64_t hash = UINT64_C(1469598103934665603);
        for (std::size_t i = 0U; i < sizeof(prepared.source_transition_identity216); ++i) {
            const unsigned char c = static_cast<unsigned char>(prepared.source_transition_identity216[i]);
            hash ^= static_cast<std::uint64_t>(c);
            hash *= UINT64_C(1099511628211);
            if (c == 0U)
                break;
        }
        return hash;
    }
};

struct PrimeLaneIndexKeyV2 final {
    std::uint8_t fibre_index{};
    std::uint16_t u{};
    std::uint16_t v{};
    std::uint16_t rho{};

    bool operator<(const PrimeLaneIndexKeyV2& other) const noexcept {
        if (fibre_index != other.fibre_index) return fibre_index < other.fibre_index;
        if (u != other.u) return u < other.u;
        if (v != other.v) return v < other.v;
        return rho < other.rho;
    }
};

struct PrimeLaneCandidateResultV2 final {
    std::vector<std::uint32_t> record_ids{};
    std::uint16_t axes_used{};
    std::uint64_t posting_lookups{};
    std::uint64_t posting_entries_examined{};
    std::uint64_t intersection_comparisons{};
    bool candidate_budget_reached{};
    PrimeLaneIndexAuthorityV2 authority{};
};

struct PrimeLaneLinearResultV2 final {
    std::vector<std::uint32_t> record_ids{};
    std::uint64_t record_visits{};
    std::uint64_t coordinate_comparisons{};
    PrimeLaneIndexAuthorityV2 authority{};
};

struct PrimeLaneRoutePlanV2 final {
    std::uint8_t selected_count{};
    std::array<std::uint8_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> fibre_index{};
    std::uint64_t plan_signature64{};
    PrimeLaneIndexAuthorityV2 authority{};
};

class PrimeLaneRoutePlanCacheV2 final {
public:
    static PrimeLaneRoutePlanV2 plan_from(const PrimeLaneRouteDecisionV1& decision) noexcept {
        PrimeLaneRoutePlanV2 plan{};
        plan.selected_count = decision.selected_count;
        std::uint64_t hash = UINT64_C(1469598103934665603);
        for (std::size_t i = 0U; i < decision.selected_count; ++i) {
            plan.fibre_index[i] = decision.fibre_index[i];
            hash ^= static_cast<std::uint64_t>(decision.fibre_index[i]);
            hash *= UINT64_C(1099511628211);
        }
        hash ^= static_cast<std::uint64_t>(decision.selected_count);
        hash *= UINT64_C(1099511628211);
        plan.plan_signature64 = hash;
        return plan;
    }

    bool store(const PrimeLaneRoutePlanV2& plan) {
        if (!hhs_pass219_prime_lane_index_authority_valid(plan.authority)) return false;
        cache_[plan.plan_signature64] = plan;
        return true;
    }

    bool fetch(std::uint64_t signature, PrimeLaneRoutePlanV2& out) const {
        const auto it = cache_.find(signature);
        if (it == cache_.end()) return false;
        out = it->second;
        return true;
    }

    std::size_t size() const noexcept { return cache_.size(); }

private:
    std::map<std::uint64_t, PrimeLaneRoutePlanV2> cache_{};
};

class PrimeLaneCandidateIndexV2 final {
public:
    bool build(const std::vector<PrimeLanePreparedRecordV2>& records) {
        clear();
        records_ = records;
        for (const auto& record : records_) {
            if (!hhs_pass219_prime_lane_index_authority_valid(record.authority) ||
                !hhs_pass219_prime_lane_authority_valid(record.fingerprint.authority)) {
                clear();
                return false;
            }
            for (std::size_t fibre = 0U; fibre < HHS_PASS219_PRIME_LANE_FIBRE_COUNT; ++fibre) {
                const auto& c = record.fingerprint.fibres[fibre];
                PrimeLaneIndexKeyV2 key{
                    static_cast<std::uint8_t>(fibre), c.u, c.v, c.rho};
                postings_[key].push_back(record.record_id);
            }
        }
        for (auto& pair : postings_) {
            auto& ids = pair.second;
            std::sort(ids.begin(), ids.end());
            ids.erase(std::unique(ids.begin(), ids.end()), ids.end());
        }
        return true;
    }

    void clear() {
        postings_.clear();
        records_.clear();
    }

    std::size_t record_count() const noexcept { return records_.size(); }
    std::size_t posting_key_count() const noexcept { return postings_.size(); }

    bool query(
        const PrimeLaneRouteDecisionV1& decision,
        std::uint32_t candidate_budget,
        PrimeLaneCandidateResultV2& out) const {
        out = PrimeLaneCandidateResultV2{};
        if (!hhs_pass219_prime_lane_authority_valid(decision.authority) ||
            decision.selected_count > HHS_PASS219_PRIME_LANE_FIBRE_COUNT ||
            candidate_budget == 0U) {
            return false;
        }

        bool initialized = false;
        std::vector<std::uint32_t> candidates{};
        for (std::size_t slot = 0U; slot < decision.selected_count; ++slot) {
            const std::size_t fibre = decision.fibre_index[slot];
            if (fibre >= HHS_PASS219_PRIME_LANE_FIBRE_COUNT) return false;
            const PrimeLaneIndexKeyV2 key{
                static_cast<std::uint8_t>(fibre),
                decision.u[slot], decision.v[slot], decision.rho[slot]};
            ++out.posting_lookups;
            const auto it = postings_.find(key);
            if (it == postings_.end()) {
                candidates.clear();
                ++out.axes_used;
                initialized = true;
                out.candidate_budget_reached = true;
                break;
            }
            const auto& posting = it->second;
            out.posting_entries_examined += posting.size();
            if (!initialized) {
                candidates = posting;
                initialized = true;
            } else {
                candidates = intersect_sorted(candidates, posting, out.intersection_comparisons);
            }
            ++out.axes_used;
            if (candidates.size() <= candidate_budget) {
                out.candidate_budget_reached = true;
                break;
            }
        }
        out.record_ids = std::move(candidates);
        return true;
    }

    bool linear_scan(
        const PrimeLaneRouteDecisionV1& decision,
        std::uint16_t axes_used,
        PrimeLaneLinearResultV2& out) const {
        out = PrimeLaneLinearResultV2{};
        if (!hhs_pass219_prime_lane_authority_valid(decision.authority) ||
            axes_used > decision.selected_count ||
            axes_used > HHS_PASS219_PRIME_LANE_FIBRE_COUNT) {
            return false;
        }
        for (const auto& record : records_) {
            ++out.record_visits;
            bool match = true;
            for (std::size_t slot = 0U; slot < axes_used; ++slot) {
                ++out.coordinate_comparisons;
                const std::size_t fibre = decision.fibre_index[slot];
                const auto& c = record.fingerprint.fibres[fibre];
                if (c.u != decision.u[slot] || c.v != decision.v[slot] || c.rho != decision.rho[slot]) {
                    match = false;
                    break;
                }
            }
            if (match) out.record_ids.push_back(record.record_id);
        }
        std::sort(out.record_ids.begin(), out.record_ids.end());
        return true;
    }

private:
    static std::vector<std::uint32_t> intersect_sorted(
        const std::vector<std::uint32_t>& a,
        const std::vector<std::uint32_t>& b,
        std::uint64_t& comparisons) {
        std::vector<std::uint32_t> out{};
        out.reserve(std::min(a.size(), b.size()));
        std::size_t i = 0U;
        std::size_t j = 0U;
        while (i < a.size() && j < b.size()) {
            ++comparisons;
            if (a[i] == b[j]) {
                out.push_back(a[i]);
                ++i;
                ++j;
            } else if (a[i] < b[j]) {
                ++i;
            } else {
                ++j;
            }
        }
        return out;
    }

    std::map<PrimeLaneIndexKeyV2, std::vector<std::uint32_t>> postings_{};
    std::vector<PrimeLanePreparedRecordV2> records_{};
};

} // namespace hhs::rna

#endif
