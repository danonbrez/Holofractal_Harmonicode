#ifndef HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_0_HPP
#define HHS_PASS219_PRIME_MEMRISTIVE_FIFTH_LANE_1_0_HPP

#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>

namespace hhs::rna {

inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_VERSION = UINT32_C(0x00010000);
inline constexpr std::size_t HHS_PASS219_PRIME_LANE_CELL_COUNT = 81U;
inline constexpr std::size_t HHS_PASS219_PRIME_LANE_SIDE = 9U;
inline constexpr std::size_t HHS_PASS219_PRIME_LANE_FIBRE_COUNT = 65U;
inline constexpr std::uint16_t HHS_PASS219_PRIME_LANE_BASE_MODULUS = UINT16_C(5184);
inline constexpr std::uint16_t HHS_PASS219_PRIME_LANE_FIRST_PRIME = UINT16_C(5);
inline constexpr std::uint16_t HHS_PASS219_PRIME_LANE_LAST_PRIME = UINT16_C(331);
inline constexpr std::uint16_t HHS_PASS219_PRIME_LANE_NEXT_PRIME = UINT16_C(337);
inline constexpr std::int16_t HHS_PASS219_PRIME_LANE_WEIGHT_BOUND = INT16_C(5184);
inline constexpr std::int16_t HHS_PASS219_PRIME_LANE_UPDATE_QUANTUM = INT16_C(5);
inline constexpr std::uint16_t HHS_PASS219_PRIME_LANE_DEFAULT_ACTIVATION_BUDGET = UINT16_C(8);
inline constexpr std::uint32_t HHS_PASS219_PRIME_LANE_FOLD_RADIX = UINT32_C(72);

inline constexpr char HHS_PASS219_PRIME_LANE_Q5_DECIMAL[] =
    "1068103163011995411184840282162896324560236518293531267531867426517528182403757817713514927994276383606682153072208011255689398707445";

inline constexpr std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT>
HHS_PASS219_PRIME_LANE_PRIMES{{
    5U, 7U, 11U, 13U, 17U, 19U, 23U, 29U, 31U, 37U, 41U, 43U, 47U,
    53U, 59U, 61U, 67U, 71U, 73U, 79U, 83U, 89U, 97U, 101U, 103U,
    107U, 109U, 113U, 127U, 131U, 137U, 139U, 149U, 151U, 157U, 163U,
    167U, 173U, 179U, 181U, 191U, 193U, 197U, 199U, 211U, 223U, 227U,
    229U, 233U, 239U, 241U, 251U, 257U, 263U, 269U, 271U, 277U, 281U,
    283U, 293U, 307U, 311U, 313U, 317U, 331U
}};

constexpr std::uint16_t hhs_pass219_prime_lane_gcd(
    std::uint16_t a,
    std::uint16_t b) noexcept {
    while (b != 0U) {
        const std::uint16_t t = static_cast<std::uint16_t>(a % b);
        a = b;
        b = t;
    }
    return a;
}

constexpr bool hhs_pass219_prime_lane_is_prime(std::uint16_t value) noexcept {
    if (value < 2U)
        return false;
    for (std::uint16_t d = 2U; static_cast<std::uint32_t>(d) * d <= value; ++d) {
        if (value % d == 0U)
            return false;
    }
    return true;
}

constexpr bool hhs_pass219_prime_lane_table_is_exact() noexcept {
    if (HHS_PASS219_PRIME_LANE_PRIMES.front() != HHS_PASS219_PRIME_LANE_FIRST_PRIME ||
        HHS_PASS219_PRIME_LANE_PRIMES.back() != HHS_PASS219_PRIME_LANE_LAST_PRIME)
        return false;

    for (std::size_t i = 0U; i < HHS_PASS219_PRIME_LANE_PRIMES.size(); ++i) {
        const std::uint16_t p = HHS_PASS219_PRIME_LANE_PRIMES[i];
        if (!hhs_pass219_prime_lane_is_prime(p))
            return false;
        if (hhs_pass219_prime_lane_gcd(p, HHS_PASS219_PRIME_LANE_BASE_MODULUS) != 1U)
            return false;
        if (i == 0U)
            continue;
        const std::uint16_t previous = HHS_PASS219_PRIME_LANE_PRIMES[i - 1U];
        for (std::uint16_t candidate = static_cast<std::uint16_t>(previous + 1U);
             candidate < p;
             ++candidate) {
            if (hhs_pass219_prime_lane_is_prime(candidate))
                return false;
        }
    }
    return true;
}

static_assert(HHS_PASS219_PRIME_LANE_PRIMES.size() == 65U,
              "Lane 5 requires exactly 65 prime fibres");
static_assert(hhs_pass219_prime_lane_table_is_exact(),
              "Lane 5 prime fibres must be consecutive primes coprime to 5184");
static_assert(hhs_pass219_prime_lane_is_prime(HHS_PASS219_PRIME_LANE_NEXT_PRIME),
              "Lane 5 next-prime boundary must remain prime");

struct PrimeLaneAuthorityV1 final {
    bool candidate_only{true};
    bool exact_integer_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
};

constexpr bool hhs_pass219_prime_lane_authority_valid(
    const PrimeLaneAuthorityV1& authority) noexcept {
    return authority.candidate_only &&
           authority.exact_integer_only &&
           !authority.canonical_mutation_authority &&
           !authority.canonical_hash72_authority &&
           !authority.canonical_hash216_authority &&
           !authority.canonical_persistence_authority &&
           !authority.floating_point_authority;
}

struct PrimeMemristiveFifthLaneDescriptorV1 final {
    std::uint32_t version{HHS_PASS219_PRIME_LANE_VERSION};
    std::uint16_t base_modulus{HHS_PASS219_PRIME_LANE_BASE_MODULUS};
    std::uint16_t first_prime{HHS_PASS219_PRIME_LANE_FIRST_PRIME};
    std::uint16_t last_prime{HHS_PASS219_PRIME_LANE_LAST_PRIME};
    std::uint16_t next_prime{HHS_PASS219_PRIME_LANE_NEXT_PRIME};
    std::uint16_t fibre_count{static_cast<std::uint16_t>(HHS_PASS219_PRIME_LANE_FIBRE_COUNT)};
    std::uint16_t activation_budget{HHS_PASS219_PRIME_LANE_DEFAULT_ACTIVATION_BUDGET};
    std::int16_t update_quantum{HHS_PASS219_PRIME_LANE_UPDATE_QUANTUM};
    std::int16_t weight_bound{HHS_PASS219_PRIME_LANE_WEIGHT_BOUND};
    bool square_coordinate_geometry{true};
    bool square_free_prime_product{true};
    bool modular_magic_witness{true};
    bool circuit_configuration_index{true};
    PrimeLaneAuthorityV1 authority{};
};

struct PrimeFibreCoordinateV1 final {
    std::uint16_t prime{};
    std::uint16_t u{};
    std::uint16_t v{};
    std::uint16_t rho{};
    std::uint16_t magic_sum_residue{};
    bool modular_magic_closure{};
};

struct PrimeLaneFingerprintV1 final {
    std::array<std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_CELL_COUNT>,
               HHS_PASS219_PRIME_LANE_FIBRE_COUNT> cell_residue{};
    std::array<PrimeFibreCoordinateV1, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> fibres{};
    std::uint64_t fingerprint_signature64{};
    PrimeLaneAuthorityV1 authority{};
};

struct PrimeLaneRouterStateV1 final {
    std::array<std::int16_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> conductance{};
    std::array<std::uint32_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> activation_count{};
    std::uint16_t activation_budget{HHS_PASS219_PRIME_LANE_DEFAULT_ACTIVATION_BUDGET};
    std::uint32_t update_count{};
    std::uint64_t step_count{};
    PrimeLaneAuthorityV1 authority{};
};

struct PrimeLaneRouteDecisionV1 final {
    std::uint8_t selected_count{};
    std::array<std::uint8_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> fibre_index{};
    std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> prime{};
    std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> u{};
    std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> v{};
    std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> rho{};
    std::array<std::int32_t, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> score{};
    std::uint64_t route_signature64{};
    PrimeLaneAuthorityV1 authority{};
};

enum class PrimeLaneStatusV1 : std::uint8_t {
    OK = 0,
    INVALID_ARGUMENT = 1,
    INVALID_STATE = 2,
    INVALID_FEEDBACK = 3
};

class PrimeMemristiveFifthLaneV1 final {
public:
    static constexpr PrimeMemristiveFifthLaneDescriptorV1 descriptor() noexcept {
        return PrimeMemristiveFifthLaneDescriptorV1{};
    }

    static constexpr PrimeLaneRouterStateV1 initial_state() noexcept {
        return PrimeLaneRouterStateV1{};
    }

    static bool validate_state(const PrimeLaneRouterStateV1& state) noexcept {
        if (!hhs_pass219_prime_lane_authority_valid(state.authority))
            return false;
        if (state.activation_budget > HHS_PASS219_PRIME_LANE_FIBRE_COUNT)
            return false;
        for (const std::int16_t value : state.conductance) {
            if (value < -HHS_PASS219_PRIME_LANE_WEIGHT_BOUND ||
                value > HHS_PASS219_PRIME_LANE_WEIGHT_BOUND)
                return false;
        }
        return true;
    }

    static PrimeLaneFingerprintV1 fingerprint(
        const std::array<std::int64_t, HHS_PASS219_PRIME_LANE_CELL_COUNT>& cells) noexcept {
        PrimeLaneFingerprintV1 out{};
        std::uint64_t signature = fnv_offset_basis();

        for (std::size_t fibre = 0U; fibre < HHS_PASS219_PRIME_LANE_FIBRE_COUNT; ++fibre) {
            const std::uint16_t p = HHS_PASS219_PRIME_LANE_PRIMES[fibre];
            auto& residues = out.cell_residue[fibre];
            for (std::size_t cell = 0U; cell < HHS_PASS219_PRIME_LANE_CELL_COUNT; ++cell)
                residues[cell] = normalized_mod(cells[cell], p);

            PrimeFibreCoordinateV1 coordinate{};
            coordinate.prime = p;
            coordinate.u = fold_row_major(residues, p);
            coordinate.v = fold_column_major(residues, p);
            coordinate.rho = fold_relations(residues, p);
            coordinate.modular_magic_closure = magic_closure(residues, p, coordinate.magic_sum_residue);
            out.fibres[fibre] = coordinate;

            mix_u64(signature, static_cast<std::uint64_t>(p));
            mix_u64(signature, static_cast<std::uint64_t>(coordinate.u));
            mix_u64(signature, static_cast<std::uint64_t>(coordinate.v));
            mix_u64(signature, static_cast<std::uint64_t>(coordinate.rho));
            mix_u64(signature, static_cast<std::uint64_t>(coordinate.magic_sum_residue));
            mix_u64(signature, coordinate.modular_magic_closure ? UINT64_C(1) : UINT64_C(0));
            for (const std::uint16_t residue : residues)
                mix_u64(signature, static_cast<std::uint64_t>(residue));
        }

        out.fingerprint_signature64 = signature;
        return out;
    }

    static PrimeLaneStatusV1 route(
        const PrimeLaneFingerprintV1& fingerprint_value,
        const PrimeLaneRouterStateV1& state,
        std::uint16_t requested_axes,
        PrimeLaneRouteDecisionV1& out_decision) noexcept {
        out_decision = PrimeLaneRouteDecisionV1{};
        if (!hhs_pass219_prime_lane_authority_valid(fingerprint_value.authority))
            return PrimeLaneStatusV1::INVALID_ARGUMENT;
        if (!validate_state(state))
            return PrimeLaneStatusV1::INVALID_STATE;

        std::uint16_t count = requested_axes;
        if (count > state.activation_budget)
            count = state.activation_budget;
        if (count > HHS_PASS219_PRIME_LANE_FIBRE_COUNT)
            count = static_cast<std::uint16_t>(HHS_PASS219_PRIME_LANE_FIBRE_COUNT);

        std::array<bool, HHS_PASS219_PRIME_LANE_FIBRE_COUNT> used{};
        std::uint64_t signature = fnv_offset_basis();
        mix_u64(signature, fingerprint_value.fingerprint_signature64);
        mix_u64(signature, state.step_count);
        mix_u64(signature, static_cast<std::uint64_t>(count));

        for (std::uint16_t slot = 0U; slot < count; ++slot) {
            std::size_t best = HHS_PASS219_PRIME_LANE_FIBRE_COUNT;
            std::int32_t best_score = std::numeric_limits<std::int32_t>::min();

            for (std::size_t fibre = 0U; fibre < HHS_PASS219_PRIME_LANE_FIBRE_COUNT; ++fibre) {
                if (used[fibre])
                    continue;
                const std::int32_t candidate_score =
                    static_cast<std::int32_t>(state.conductance[fibre]) * INT32_C(1024) +
                    static_cast<std::int32_t>(HHS_PASS219_PRIME_LANE_PRIMES[fibre]);
                if (candidate_score > best_score) {
                    best_score = candidate_score;
                    best = fibre;
                }
            }

            if (best == HHS_PASS219_PRIME_LANE_FIBRE_COUNT)
                break;

            used[best] = true;
            const std::size_t out_index = static_cast<std::size_t>(slot);
            const auto& coordinate = fingerprint_value.fibres[best];
            out_decision.fibre_index[out_index] = static_cast<std::uint8_t>(best);
            out_decision.prime[out_index] = coordinate.prime;
            out_decision.u[out_index] = coordinate.u;
            out_decision.v[out_index] = coordinate.v;
            out_decision.rho[out_index] = coordinate.rho;
            out_decision.score[out_index] = best_score;
            ++out_decision.selected_count;

            mix_u64(signature, static_cast<std::uint64_t>(best));
            mix_u64(signature, static_cast<std::uint64_t>(coordinate.prime));
            mix_u64(signature, static_cast<std::uint64_t>(coordinate.u));
            mix_u64(signature, static_cast<std::uint64_t>(coordinate.v));
            mix_u64(signature, static_cast<std::uint64_t>(coordinate.rho));
            mix_u64(signature, static_cast<std::uint64_t>(
                static_cast<std::int64_t>(best_score) - std::numeric_limits<std::int32_t>::min()));
        }

        out_decision.route_signature64 = signature;
        return PrimeLaneStatusV1::OK;
    }

    static PrimeLaneStatusV1 apply_feedback(
        const PrimeLaneRouterStateV1& baseline,
        const PrimeLaneRouteDecisionV1& decision,
        std::int8_t feedback_trinary,
        PrimeLaneRouterStateV1& out_candidate) noexcept {
        out_candidate = baseline;
        if (!validate_state(baseline))
            return PrimeLaneStatusV1::INVALID_STATE;
        if (!hhs_pass219_prime_lane_authority_valid(decision.authority))
            return PrimeLaneStatusV1::INVALID_ARGUMENT;
        if (feedback_trinary < -1 || feedback_trinary > 1)
            return PrimeLaneStatusV1::INVALID_FEEDBACK;
        if (decision.selected_count > HHS_PASS219_PRIME_LANE_FIBRE_COUNT)
            return PrimeLaneStatusV1::INVALID_ARGUMENT;

        bool changed = false;
        for (std::size_t slot = 0U; slot < decision.selected_count; ++slot) {
            const std::size_t fibre = decision.fibre_index[slot];
            if (fibre >= HHS_PASS219_PRIME_LANE_FIBRE_COUNT)
                return PrimeLaneStatusV1::INVALID_ARGUMENT;
            if (out_candidate.activation_count[fibre] != std::numeric_limits<std::uint32_t>::max())
                ++out_candidate.activation_count[fibre];

            if (feedback_trinary == 0)
                continue;

            const std::int32_t proposed =
                static_cast<std::int32_t>(out_candidate.conductance[fibre]) +
                static_cast<std::int32_t>(feedback_trinary) * HHS_PASS219_PRIME_LANE_UPDATE_QUANTUM;
            const std::int16_t clipped = clip_weight(proposed);
            if (clipped != out_candidate.conductance[fibre]) {
                out_candidate.conductance[fibre] = clipped;
                changed = true;
            }
        }

        if (out_candidate.step_count != std::numeric_limits<std::uint64_t>::max())
            ++out_candidate.step_count;
        if (changed && out_candidate.update_count != std::numeric_limits<std::uint32_t>::max())
            ++out_candidate.update_count;
        return PrimeLaneStatusV1::OK;
    }

private:
    static constexpr std::uint64_t fnv_offset_basis() noexcept {
        return UINT64_C(1469598103934665603);
    }

    static void mix_u64(std::uint64_t& hash, std::uint64_t value) noexcept {
        for (unsigned shift = 0U; shift < 64U; shift += 8U) {
            hash ^= (value >> shift) & UINT64_C(0xff);
            hash *= UINT64_C(1099511628211);
        }
    }

    static std::uint16_t normalized_mod(std::int64_t value, std::uint16_t p) noexcept {
        std::int64_t residue = value % static_cast<std::int64_t>(p);
        if (residue < 0)
            residue += static_cast<std::int64_t>(p);
        return static_cast<std::uint16_t>(residue);
    }

    static std::uint16_t add_mod(
        std::uint16_t a,
        std::uint16_t b,
        std::uint16_t p) noexcept {
        return static_cast<std::uint16_t>((static_cast<std::uint32_t>(a) + b) % p);
    }

    static std::uint16_t fold_row_major(
        const std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_CELL_COUNT>& residues,
        std::uint16_t p) noexcept {
        std::uint32_t acc = 0U;
        for (std::size_t i = 0U; i < residues.size(); ++i) {
            const std::uint32_t positional = static_cast<std::uint32_t>((i + 1U) % p);
            acc = (acc * HHS_PASS219_PRIME_LANE_FOLD_RADIX + residues[i] + positional) % p;
        }
        return static_cast<std::uint16_t>(acc);
    }

    static std::uint16_t fold_column_major(
        const std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_CELL_COUNT>& residues,
        std::uint16_t p) noexcept {
        std::uint32_t acc = 0U;
        std::size_t ordinal = 0U;
        for (std::size_t column = 0U; column < HHS_PASS219_PRIME_LANE_SIDE; ++column) {
            for (std::size_t row = 0U; row < HHS_PASS219_PRIME_LANE_SIDE; ++row) {
                const std::size_t index = row * HHS_PASS219_PRIME_LANE_SIDE + column;
                const std::uint32_t positional = static_cast<std::uint32_t>((ordinal + 1U) % p);
                acc = (acc * HHS_PASS219_PRIME_LANE_FOLD_RADIX + residues[index] + positional) % p;
                ++ordinal;
            }
        }
        return static_cast<std::uint16_t>(acc);
    }

    static std::uint16_t fold_relations(
        const std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_CELL_COUNT>& residues,
        std::uint16_t p) noexcept {
        std::uint32_t acc = 0U;
        for (std::size_t row = 0U; row < HHS_PASS219_PRIME_LANE_SIDE; ++row) {
            for (std::size_t column = 0U; column < HHS_PASS219_PRIME_LANE_SIDE; ++column) {
                const std::size_t index = row * HHS_PASS219_PRIME_LANE_SIDE + column;
                const std::size_t right = row * HHS_PASS219_PRIME_LANE_SIDE +
                                          ((column + 1U) % HHS_PASS219_PRIME_LANE_SIDE);
                const std::size_t down = ((row + 1U) % HHS_PASS219_PRIME_LANE_SIDE) *
                                         HHS_PASS219_PRIME_LANE_SIDE + column;
                const std::uint32_t term =
                    static_cast<std::uint32_t>(residues[index]) +
                    UINT32_C(2) * residues[right] +
                    UINT32_C(3) * residues[down] +
                    static_cast<std::uint32_t>(index + 1U);
                acc = (acc * HHS_PASS219_PRIME_LANE_FOLD_RADIX + term) % p;
            }
        }
        return static_cast<std::uint16_t>(acc);
    }

    static bool magic_closure(
        const std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_CELL_COUNT>& residues,
        std::uint16_t p,
        std::uint16_t& out_magic_sum_residue) noexcept {
        std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_SIDE> row_sum{};
        std::array<std::uint16_t, HHS_PASS219_PRIME_LANE_SIDE> column_sum{};
        std::uint16_t diagonal_a = 0U;
        std::uint16_t diagonal_b = 0U;

        for (std::size_t row = 0U; row < HHS_PASS219_PRIME_LANE_SIDE; ++row) {
            for (std::size_t column = 0U; column < HHS_PASS219_PRIME_LANE_SIDE; ++column) {
                const std::size_t index = row * HHS_PASS219_PRIME_LANE_SIDE + column;
                row_sum[row] = add_mod(row_sum[row], residues[index], p);
                column_sum[column] = add_mod(column_sum[column], residues[index], p);
                if (row == column)
                    diagonal_a = add_mod(diagonal_a, residues[index], p);
                if (row + column + 1U == HHS_PASS219_PRIME_LANE_SIDE)
                    diagonal_b = add_mod(diagonal_b, residues[index], p);
            }
        }

        const std::uint16_t reference = row_sum[0];
        out_magic_sum_residue = reference;
        for (const std::uint16_t value : row_sum) {
            if (value != reference)
                return false;
        }
        for (const std::uint16_t value : column_sum) {
            if (value != reference)
                return false;
        }
        return diagonal_a == reference && diagonal_b == reference;
    }

    static std::int16_t clip_weight(std::int32_t value) noexcept {
        if (value > HHS_PASS219_PRIME_LANE_WEIGHT_BOUND)
            return HHS_PASS219_PRIME_LANE_WEIGHT_BOUND;
        if (value < -HHS_PASS219_PRIME_LANE_WEIGHT_BOUND)
            return static_cast<std::int16_t>(-HHS_PASS219_PRIME_LANE_WEIGHT_BOUND);
        return static_cast<std::int16_t>(value);
    }
};

} // namespace hhs::rna

#endif
