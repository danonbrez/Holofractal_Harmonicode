#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_10_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_10_HPP

#include "hhs_pass219_prime_memristive_fifth_lane_1_9.hpp"
#include "hhs_pass219_core_holographic_four_lane_1_24.h"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <vector>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_BIGINT_ADDRESS_VERSION = UINT32_C(0x0001000A);
inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_I11_NAMESPACE = UINT32_C(0x21911);
inline constexpr std::size_t HHS_PASS219_PRIME_LANE_I11_MAX_ADDRESS_BYTES = 384U;
inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_I11_BYTE_RADIX = UINT32_C(256);
inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_I11_CELL_RADIX = UINT32_C(81);
inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_I11_HASH216_RADIX = UINT32_C(216);

struct PrimeLaneBigIntAddressAuthorityV11 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool pass133_canonical_bigint_serialization{true};
    bool pass211_hfc_frame_compatible{true};
    bool mixed_radix_reversible{true};
    bool five_lane_coordinate_address_only{true};
    bool inherited_i10_winners_only{true};
    bool inherited_i8_budget_debit_only{true};
    bool inherited_i9_verified_reinforcement_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
    bool requires_inherited_vm81_hash216_admission{true};
};

constexpr bool hhs_pass219_prime_lane_bigint_address_authority_valid(
    const PrimeLaneBigIntAddressAuthorityV11& authority) noexcept {
    return authority.candidate_only && authority.exact_integer_only &&
           authority.pass133_canonical_bigint_serialization &&
           authority.pass211_hfc_frame_compatible && authority.mixed_radix_reversible &&
           authority.five_lane_coordinate_address_only &&
           authority.inherited_i10_winners_only &&
           authority.inherited_i8_budget_debit_only &&
           authority.inherited_i9_verified_reinforcement_only &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority &&
           authority.requires_inherited_vm81_hash216_admission;
}

struct PrimeLaneFiveLaneAddressV11 final {
    std::vector<std::uint8_t> bytes_be{};
    std::uint32_t bit_length{};
    std::uint8_t cell81{};
    std::uint64_t tensor_signature64{};
    std::uint64_t fingerprint_signature64{};
    std::uint64_t local_signature64{};
    std::uint64_t address_signature64{};
    PrimeLaneBigIntAddressAuthorityV11 authority{};
};

struct PrimeLaneFiveLaneDecodedAddressV11 final {
    std::uint8_t cell81{};
    std::array<std::uint16_t, HHS_EXACT_PASS219_HOLO4_LANE_COUNT> hash216_position{};
    std::uint64_t tensor_signature64{};
    std::uint64_t fingerprint_signature64{};
    std::uint64_t local_signature64{};
    std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> cell_residue{};
    std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> u{};
    std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> v{};
    std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> rho{};
    std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> magic_sum_residue{};
    std::array<std::uint8_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> modular_magic_closure{};
    PrimeLaneBigIntAddressAuthorityV11 authority{};
};

class PrimeLanePass133BigUIntV11 final {
public:
    static PrimeLanePass133BigUIntV11 from_small(std::uint32_t value) {
        PrimeLanePass133BigUIntV11 out{};
        if (value == 0U)
            return out;
        bool started = false;
        for (int shift = 24; shift >= 0; shift -= 8) {
            const auto byte = static_cast<std::uint8_t>((value >> static_cast<unsigned>(shift)) & UINT32_C(0xff));
            if (byte != 0U || started) {
                out.bytes_.push_back(byte);
                started = true;
            }
        }
        return out;
    }

    static bool from_canonical_bytes(
        const std::vector<std::uint8_t>& bytes,
        PrimeLanePass133BigUIntV11& out) {
        out = PrimeLanePass133BigUIntV11{};
        if (bytes.empty() || bytes.front() == 0U ||
            bytes.size() > HHS_PASS219_PRIME_LANE_I11_MAX_ADDRESS_BYTES)
            return false;
        out.bytes_ = bytes;
        return true;
    }

    bool mul_add_small(std::uint32_t radix, std::uint32_t digit) {
        if (bytes_.empty() || radix < 2U || digit >= radix)
            return false;
        std::uint64_t carry = digit;
        for (std::size_t index = bytes_.size(); index-- > 0U;) {
            const std::uint64_t value =
                static_cast<std::uint64_t>(bytes_[index]) * radix + carry;
            bytes_[index] = static_cast<std::uint8_t>(value & UINT64_C(0xff));
            carry = value >> 8U;
        }
        std::vector<std::uint8_t> prefix{};
        while (carry != 0U) {
            prefix.push_back(static_cast<std::uint8_t>(carry & UINT64_C(0xff)));
            carry >>= 8U;
        }
        if (!prefix.empty()) {
            if (bytes_.size() + prefix.size() > HHS_PASS219_PRIME_LANE_I11_MAX_ADDRESS_BYTES)
                return false;
            std::reverse(prefix.begin(), prefix.end());
            bytes_.insert(bytes_.begin(), prefix.begin(), prefix.end());
        }
        return bytes_.size() <= HHS_PASS219_PRIME_LANE_I11_MAX_ADDRESS_BYTES &&
               !bytes_.empty() && bytes_.front() != 0U;
    }

    bool divmod_small(std::uint32_t radix, std::uint32_t& remainder) {
        remainder = 0U;
        if (bytes_.empty() || radix < 2U)
            return false;
        std::uint64_t rem = 0U;
        for (auto& byte : bytes_) {
            const std::uint64_t value = (rem << 8U) | byte;
            byte = static_cast<std::uint8_t>(value / radix);
            rem = value % radix;
        }
        remainder = static_cast<std::uint32_t>(rem);
        const auto first_nonzero = std::find_if(
            bytes_.begin(), bytes_.end(), [](std::uint8_t byte) { return byte != 0U; });
        if (first_nonzero == bytes_.end())
            bytes_.assign(1U, 0U);
        else if (first_nonzero != bytes_.begin())
            bytes_.erase(bytes_.begin(), first_nonzero);
        return true;
    }

    bool append_u64_be(std::uint64_t value) {
        for (int shift = 56; shift >= 0; shift -= 8) {
            if (!mul_add_small(
                    HHS_PASS219_PRIME_LANE_I11_BYTE_RADIX,
                    static_cast<std::uint32_t>((value >> static_cast<unsigned>(shift)) & UINT64_C(0xff))))
                return false;
        }
        return true;
    }

    bool extract_u64_be(std::uint64_t& out) {
        std::array<std::uint8_t, 8U> bytes{};
        for (std::size_t reverse = 8U; reverse-- > 0U;) {
            std::uint32_t digit = 0U;
            if (!divmod_small(HHS_PASS219_PRIME_LANE_I11_BYTE_RADIX, digit) || digit > 255U)
                return false;
            bytes[reverse] = static_cast<std::uint8_t>(digit);
        }
        out = 0U;
        for (const auto byte : bytes)
            out = (out << 8U) | byte;
        return true;
    }

    bool equals_small(std::uint32_t value) const {
        return bytes_ == from_small(value).bytes_;
    }

    const std::vector<std::uint8_t>& bytes() const noexcept { return bytes_; }

private:
    std::vector<std::uint8_t> bytes_{};
};

class PrimeLaneFiveLaneBigIntCodecV11 final {
public:
    static bool encode(
        const HHSExactPass219Holo4PreparedV1& prepared,
        const PrimeLaneFingerprintV1& fingerprint,
        std::uint8_t cell81,
        PrimeLaneFiveLaneAddressV11& out) {
        out = PrimeLaneFiveLaneAddressV11{};
        if (!prepared_valid(prepared) || !fingerprint_valid(fingerprint) ||
            cell81 >= HHS_PASS219_PRIME_LANE_CELL_COUNT)
            return false;

        const auto& cell = prepared.cells[cell81];
        if (cell.cell81 != cell81)
            return false;

        PrimeLanePass133BigUIntV11 bigint =
            PrimeLanePass133BigUIntV11::from_small(HHS_PASS219_PRIME_LANE_I11_NAMESPACE);
        if (bigint.bytes().empty() ||
            !bigint.append_u64_be(prepared.tensor_signature64) ||
            !bigint.append_u64_be(fingerprint.fingerprint_signature64) ||
            !bigint.append_u64_be(cell.local_signature64) ||
            !bigint.mul_add_small(HHS_PASS219_PRIME_LANE_I11_CELL_RADIX, cell81))
            return false;

        for (std::size_t lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
            if (!bigint.mul_add_small(
                    HHS_PASS219_PRIME_LANE_I11_HASH216_RADIX,
                    cell.hash216_position[lane]))
                return false;
        }

        for (std::size_t fibre = 0U; fibre < HHS_PASS219_PRIME_LANE_FIBRE_COUNT; ++fibre) {
            const std::uint32_t p = HHS_PASS219_PRIME_LANE_PRIMES[fibre];
            const auto& coordinate = fingerprint.fibres[fibre];
            if (!bigint.mul_add_small(p, fingerprint.cell_residue[fibre][cell81]) ||
                !bigint.mul_add_small(p, coordinate.u) ||
                !bigint.mul_add_small(p, coordinate.v) ||
                !bigint.mul_add_small(p, coordinate.rho) ||
                !bigint.mul_add_small(p, coordinate.magic_sum_residue) ||
                !bigint.mul_add_small(2U, coordinate.modular_magic_closure ? 1U : 0U))
                return false;
        }

        out.bytes_be = bigint.bytes();
        if (!canonical_bytes_valid(out.bytes_be))
            return false;
        out.bit_length = bit_length(out.bytes_be);
        out.cell81 = cell81;
        out.tensor_signature64 = prepared.tensor_signature64;
        out.fingerprint_signature64 = fingerprint.fingerprint_signature64;
        out.local_signature64 = cell.local_signature64;
        out.address_signature64 = signature(out.bytes_be);
        return out.address_signature64 != 0U &&
               hhs_pass219_prime_lane_bigint_address_authority_valid(out.authority);
    }

    static bool decode(
        const PrimeLaneFiveLaneAddressV11& address,
        PrimeLaneFiveLaneDecodedAddressV11& out) {
        out = PrimeLaneFiveLaneDecodedAddressV11{};
        if (!hhs_pass219_prime_lane_bigint_address_authority_valid(address.authority) ||
            !canonical_bytes_valid(address.bytes_be) ||
            address.bit_length != bit_length(address.bytes_be) ||
            address.address_signature64 != signature(address.bytes_be))
            return false;

        PrimeLanePass133BigUIntV11 bigint{};
        if (!PrimeLanePass133BigUIntV11::from_canonical_bytes(address.bytes_be, bigint))
            return false;

        for (std::size_t reverse = HHS_PASS219_PRIME_LANE_FIBRE_COUNT; reverse-- > 0U;) {
            const std::uint32_t p = HHS_PASS219_PRIME_LANE_PRIMES[reverse];
            std::uint32_t digit = 0U;
            if (!bigint.divmod_small(2U, digit))
                return false;
            out.modular_magic_closure[reverse] = static_cast<std::uint8_t>(digit);
            if (!bigint.divmod_small(p, digit))
                return false;
            out.magic_sum_residue[reverse] = static_cast<std::uint16_t>(digit);
            if (!bigint.divmod_small(p, digit))
                return false;
            out.rho[reverse] = static_cast<std::uint16_t>(digit);
            if (!bigint.divmod_small(p, digit))
                return false;
            out.v[reverse] = static_cast<std::uint16_t>(digit);
            if (!bigint.divmod_small(p, digit))
                return false;
            out.u[reverse] = static_cast<std::uint16_t>(digit);
            if (!bigint.divmod_small(p, digit))
                return false;
            out.cell_residue[reverse] = static_cast<std::uint16_t>(digit);
        }

        for (std::size_t reverse = HHS_EXACT_PASS219_HOLO4_LANE_COUNT; reverse-- > 0U;) {
            std::uint32_t digit = 0U;
            if (!bigint.divmod_small(HHS_PASS219_PRIME_LANE_I11_HASH216_RADIX, digit))
                return false;
            out.hash216_position[reverse] = static_cast<std::uint16_t>(digit);
        }

        std::uint32_t cell_digit = 0U;
        if (!bigint.divmod_small(HHS_PASS219_PRIME_LANE_I11_CELL_RADIX, cell_digit) ||
            cell_digit >= HHS_PASS219_PRIME_LANE_CELL_COUNT)
            return false;
        out.cell81 = static_cast<std::uint8_t>(cell_digit);

        if (!bigint.extract_u64_be(out.local_signature64) ||
            !bigint.extract_u64_be(out.fingerprint_signature64) ||
            !bigint.extract_u64_be(out.tensor_signature64) ||
            !bigint.equals_small(HHS_PASS219_PRIME_LANE_I11_NAMESPACE))
            return false;

        if (out.cell81 != address.cell81 ||
            out.tensor_signature64 != address.tensor_signature64 ||
            out.fingerprint_signature64 != address.fingerprint_signature64 ||
            out.local_signature64 != address.local_signature64)
            return false;
        return hhs_pass219_prime_lane_bigint_address_authority_valid(out.authority);
    }

    static bool matches(
        const HHSExactPass219Holo4PreparedV1& prepared,
        const PrimeLaneFingerprintV1& fingerprint,
        const PrimeLaneFiveLaneDecodedAddressV11& decoded) noexcept {
        if (!prepared_valid(prepared) || !fingerprint_valid(fingerprint) ||
            decoded.cell81 >= HHS_PASS219_PRIME_LANE_CELL_COUNT)
            return false;
        const auto& cell = prepared.cells[decoded.cell81];
        if (decoded.tensor_signature64 != prepared.tensor_signature64 ||
            decoded.fingerprint_signature64 != fingerprint.fingerprint_signature64 ||
            decoded.local_signature64 != cell.local_signature64)
            return false;
        for (std::size_t lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
            if (decoded.hash216_position[lane] != cell.hash216_position[lane])
                return false;
        }
        for (std::size_t fibre = 0U; fibre < HHS_PASS219_PRIME_LANE_FIBRE_COUNT; ++fibre) {
            const auto& coordinate = fingerprint.fibres[fibre];
            if (decoded.cell_residue[fibre] != fingerprint.cell_residue[fibre][decoded.cell81] ||
                decoded.u[fibre] != coordinate.u || decoded.v[fibre] != coordinate.v ||
                decoded.rho[fibre] != coordinate.rho ||
                decoded.magic_sum_residue[fibre] != coordinate.magic_sum_residue ||
                decoded.modular_magic_closure[fibre] !=
                    static_cast<std::uint8_t>(coordinate.modular_magic_closure ? 1U : 0U))
                return false;
        }
        return hhs_pass219_prime_lane_bigint_address_authority_valid(decoded.authority);
    }

    static bool canonical_bytes_valid(const std::vector<std::uint8_t>& bytes) noexcept {
        return !bytes.empty() && bytes.front() != 0U &&
               bytes.size() <= HHS_PASS219_PRIME_LANE_I11_MAX_ADDRESS_BYTES;
    }

private:
    static bool prepared_valid(const HHSExactPass219Holo4PreparedV1& prepared) noexcept {
        if (prepared.struct_size != sizeof(prepared) ||
            prepared.version != HHS_EXACT_PASS219_HOLO4_VERSION ||
            prepared.all_cells_have_20_peers != 1U ||
            prepared.reciprocal_phase_closure != 1U ||
            prepared.nested_loshu_complete != 1U ||
            prepared.hash216_positions_complete != 1U ||
            prepared.candidate_only != 1U || prepared.exact_integer_only != 1U ||
            prepared.canonical_mutation_authority != 0U ||
            prepared.canonical_hash72_authority != 0U ||
            prepared.canonical_hash216_authority != 0U ||
            prepared.canonical_persistence_authority != 0U ||
            prepared.floating_point_authority != 0U)
            return false;
        for (std::size_t cell = 0U; cell < HHS_EXACT_PASS219_HOLO4_CELL_COUNT; ++cell) {
            if (prepared.cells[cell].cell81 != cell)
                return false;
            for (std::size_t lane = 0U; lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT; ++lane) {
                if (prepared.cells[cell].hash216_position[lane] >=
                    HHS_EXACT_PASS219_HASH216_OCCURRENCES)
                    return false;
            }
        }
        return true;
    }

    static bool fingerprint_valid(const PrimeLaneFingerprintV1& fingerprint) noexcept {
        if (!hhs_pass219_prime_lane_authority_valid(fingerprint.authority))
            return false;
        for (std::size_t fibre = 0U; fibre < HHS_PASS219_PRIME_LANE_FIBRE_COUNT; ++fibre) {
            const std::uint16_t p = HHS_PASS219_PRIME_LANE_PRIMES[fibre];
            const auto& coordinate = fingerprint.fibres[fibre];
            if (coordinate.prime != p || coordinate.u >= p || coordinate.v >= p ||
                coordinate.rho >= p || coordinate.magic_sum_residue >= p)
                return false;
            for (const auto residue : fingerprint.cell_residue[fibre]) {
                if (residue >= p)
                    return false;
            }
        }
        return true;
    }

    static std::uint32_t bit_length(const std::vector<std::uint8_t>& bytes) noexcept {
        if (bytes.empty() || bytes.front() == 0U)
            return 0U;
        std::uint32_t leading = 0U;
        std::uint8_t mask = UINT8_C(0x80);
        while ((bytes.front() & mask) == 0U) {
            ++leading;
            mask >>= 1U;
        }
        const std::size_t total = bytes.size() * 8U - leading;
        return total > std::numeric_limits<std::uint32_t>::max()
            ? 0U : static_cast<std::uint32_t>(total);
    }

    static std::uint64_t signature(const std::vector<std::uint8_t>& bytes) noexcept {
        std::uint64_t hash = UINT64_C(1469598103934665603);
        for (const auto byte : bytes) {
            hash ^= byte;
            hash *= UINT64_C(1099511628211);
        }
        hash ^= bytes.size();
        hash *= UINT64_C(1099511628211);
        return hash;
    }
};

struct PrimeLaneSparseWinnerExecutionReceiptV11 final {
    std::uint64_t source_neighborhood_binding_signature64{};
    std::uint64_t target_neighborhood_binding_signature64{};
    std::uint32_t winner_ordinal{};
    std::uint64_t allocated_work{};
    std::uint64_t exact_work_spent{};
    std::uint64_t remaining_allocation{};
    PrimeLaneEnergyHopReceiptV8 inherited_budget_receipt{};
    PrimeLaneFiveLaneAddressV11 five_lane_address{};
    PrimeLaneBigIntAddressAuthorityV11 authority{};
};

class PrimeLaneSparseWinnerExecutorV11 final {
public:
    bool execute_one_hop(
        const PrimeLaneArbitrationCandidateReceiptV10& winner,
        const HHSExactPass219Holo4PreparedV1& prepared,
        const PrimeLaneFingerprintV1& fingerprint,
        std::uint8_t cell81,
        std::uint8_t active_modality_mask,
        const PrimeLaneAdaptiveReplayLedgerV6& replay,
        const PrimeLaneReplayConditionedPrefetchV7& prefetch,
        const PrimeLaneHash216CandidateGraphV3& graph,
        const PrimeLaneRouteDecisionV1& cold_decision,
        std::uint32_t candidate_budget,
        PrimeLaneBudgetedPredictiveHydratorV8& hydrator,
        PrimeLaneSparseWinnerExecutionReceiptV11& out) const {
        out = PrimeLaneSparseWinnerExecutionReceiptV11{};
        if (!winner_valid(winner) || candidate_budget == 0U ||
            active_modality_mask == 0U ||
            (active_modality_mask & static_cast<std::uint8_t>(~HHS_PASS219_PRIME_LANE_MODALITY_ALL)) != 0U)
            return false;

        PrimeLaneActivationBudgetStateV8 budget_before{};
        if (!hydrator.budget_for(winner.neighborhood_binding_signature64, budget_before) ||
            !hhs_pass219_prime_lane_budgeted_hydration_authority_valid(budget_before.authority))
            return false;

        std::vector<PrimeLanePrefetchCandidateV7> ranked{};
        PrimeLanePrefetchMetricsV7 ranking_metrics{};
        if (!prefetch.prefetch(
                winner.neighborhood_binding_signature64, active_modality_mask,
                replay, 1U, ranked, ranking_metrics) || ranked.size() != 1U)
            return false;
        const auto& chosen = ranked.front();
        if (chosen.neighborhood.binding_signature64 == 0U ||
            chosen.neighborhood.binding_signature64 == winner.neighborhood_binding_signature64 ||
            chosen.neighborhood.members.size() >
                std::numeric_limits<std::uint64_t>::max() - HHS_PASS219_PRIME_LANE_HOP_ENERGY_QUANTUM)
            return false;
        const std::uint64_t exact_cost = HHS_PASS219_PRIME_LANE_HOP_ENERGY_QUANTUM +
            static_cast<std::uint64_t>(chosen.neighborhood.members.size());
        if (exact_cost > winner.work_allocation || exact_cost > budget_before.available)
            return false;

        PrimeLaneFiveLaneAddressV11 address{};
        if (!PrimeLaneFiveLaneBigIntCodecV11::encode(prepared, fingerprint, cell81, address))
            return false;

        PrimeLaneBudgetedHydrationResultV8 hydration{};
        if (!hydrator.hydrate(
                winner.neighborhood_binding_signature64, active_modality_mask,
                replay, prefetch, 1U, 1U, graph, cold_decision,
                candidate_budget, hydration))
            return false;
        if (!hydration.used_predictive_hydration || hydration.used_cold_fallback ||
            hydration.hydrated.size() != 1U || hydration.receipts.size() != 1U ||
            hydration.metrics.hops_completed != 1U ||
            hydration.metrics.exact_energy_spent != exact_cost ||
            hydration.hydrated.front().neighborhood.binding_signature64 !=
                chosen.neighborhood.binding_signature64 ||
            hydration.receipts.front().source_neighborhood_binding_signature64 !=
                winner.neighborhood_binding_signature64 ||
            hydration.receipts.front().target_neighborhood_binding_signature64 !=
                chosen.neighborhood.binding_signature64 ||
            hydration.receipts.front().exact_hop_cost != exact_cost)
            return false;

        out.source_neighborhood_binding_signature64 = winner.neighborhood_binding_signature64;
        out.target_neighborhood_binding_signature64 = chosen.neighborhood.binding_signature64;
        out.winner_ordinal = winner.winner_ordinal;
        out.allocated_work = winner.work_allocation;
        out.exact_work_spent = exact_cost;
        out.remaining_allocation = winner.work_allocation - exact_cost;
        out.inherited_budget_receipt = hydration.receipts.front();
        out.five_lane_address = std::move(address);
        return hhs_pass219_prime_lane_bigint_address_authority_valid(out.authority) &&
               hhs_pass219_prime_lane_budgeted_hydration_authority_valid(
                   out.inherited_budget_receipt.authority);
    }

private:
    static bool winner_valid(const PrimeLaneArbitrationCandidateReceiptV10& winner) noexcept {
        return hhs_pass219_prime_lane_sparse_arbitration_authority_valid(winner.authority) &&
               winner.winner && winner.eligible && winner.winner_ordinal != 0U &&
               winner.exclusion == PrimeLaneArbitrationExclusionV10::none &&
               winner.neighborhood_binding_signature64 != 0U &&
               winner.work_allocation >= winner.exact_hop_floor &&
               winner.exact_hop_floor >= HHS_PASS219_PRIME_LANE_HOP_ENERGY_QUANTUM + 1U;
    }
};

} // namespace hhs::rna

#endif
