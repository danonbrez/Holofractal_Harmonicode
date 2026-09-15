#include "hhs_pass219_prime_memristive_fifth_lane_1_0.hpp"

#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>

using hhs::rna::HHS_PASS219_PRIME_LANE_FIBRE_COUNT;
using hhs::rna::HHS_PASS219_PRIME_LANE_PRIMES;
using hhs::rna::HHS_PASS219_PRIME_LANE_UPDATE_QUANTUM;
using hhs::rna::HHS_PASS219_PRIME_LANE_WEIGHT_BOUND;
using hhs::rna::PrimeLaneFingerprintV1;
using hhs::rna::PrimeLaneRouteDecisionV1;
using hhs::rna::PrimeLaneRouterStateV1;
using hhs::rna::PrimeLaneStatusV1;
using hhs::rna::PrimeMemristiveFifthLaneV1;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static std::array<std::int64_t, 81> build_order9_magic_square() {
    std::array<std::int64_t, 81> square{};
    constexpr std::size_t n = 9U;
    std::size_t row = 0U;
    std::size_t column = n / 2U;
    for (std::int64_t value = 1; value <= 81; ++value) {
        square[row * n + column] = value;
        const std::size_t next_row = (row + n - 1U) % n;
        const std::size_t next_column = (column + 1U) % n;
        if (square[next_row * n + next_column] != 0) {
            row = (row + 1U) % n;
        } else {
            row = next_row;
            column = next_column;
        }
    }
    return square;
}

int main() {
    const auto descriptor = PrimeMemristiveFifthLaneV1::descriptor();
    CHECK(descriptor.version == hhs::rna::HHS_PASS219_PRIME_LANE_VERSION);
    CHECK(descriptor.base_modulus == 5184U);
    CHECK(descriptor.fibre_count == 65U);
    CHECK(descriptor.first_prime == 5U);
    CHECK(descriptor.last_prime == 331U);
    CHECK(descriptor.next_prime == 337U);
    CHECK(descriptor.square_coordinate_geometry);
    CHECK(descriptor.square_free_prime_product);
    CHECK(descriptor.modular_magic_witness);
    CHECK(descriptor.circuit_configuration_index);
    CHECK(descriptor.authority.candidate_only);
    CHECK(descriptor.authority.exact_integer_only);
    CHECK(!descriptor.authority.canonical_mutation_authority);
    CHECK(!descriptor.authority.canonical_hash72_authority);
    CHECK(!descriptor.authority.canonical_hash216_authority);
    CHECK(!descriptor.authority.canonical_persistence_authority);
    CHECK(!descriptor.authority.floating_point_authority);

    CHECK(HHS_PASS219_PRIME_LANE_PRIMES.size() == HHS_PASS219_PRIME_LANE_FIBRE_COUNT);
    for (std::size_t i = 0U; i < HHS_PASS219_PRIME_LANE_PRIMES.size(); ++i) {
        const std::uint16_t p = HHS_PASS219_PRIME_LANE_PRIMES[i];
        CHECK(hhs::rna::hhs_pass219_prime_lane_is_prime(p));
        CHECK(hhs::rna::hhs_pass219_prime_lane_gcd(p, 5184U) == 1U);
        if (i > 0U)
            CHECK(p > HHS_PASS219_PRIME_LANE_PRIMES[i - 1U]);
    }

    const auto magic = build_order9_magic_square();
    const PrimeLaneFingerprintV1 fingerprint = PrimeMemristiveFifthLaneV1::fingerprint(magic);
    const PrimeLaneFingerprintV1 replay = PrimeMemristiveFifthLaneV1::fingerprint(magic);
    CHECK(fingerprint.fingerprint_signature64 == replay.fingerprint_signature64);
    CHECK(std::memcmp(&fingerprint, &replay, sizeof(fingerprint)) == 0);
    CHECK(fingerprint.authority.candidate_only);
    CHECK(!fingerprint.authority.canonical_mutation_authority);

    for (std::size_t i = 0U; i < fingerprint.fibres.size(); ++i) {
        const auto& fibre = fingerprint.fibres[i];
        CHECK(fibre.prime == HHS_PASS219_PRIME_LANE_PRIMES[i]);
        CHECK(fibre.u < fibre.prime);
        CHECK(fibre.v < fibre.prime);
        CHECK(fibre.rho < fibre.prime);
        CHECK(fibre.magic_sum_residue < fibre.prime);
        CHECK(fibre.modular_magic_closure);
        CHECK(fibre.magic_sum_residue == static_cast<std::uint16_t>(369U % fibre.prime));
    }

    auto perturbed = magic;
    ++perturbed[1];
    const PrimeLaneFingerprintV1 perturbed_fingerprint =
        PrimeMemristiveFifthLaneV1::fingerprint(perturbed);
    CHECK(perturbed_fingerprint.fingerprint_signature64 != fingerprint.fingerprint_signature64);
    for (const auto& fibre : perturbed_fingerprint.fibres)
        CHECK(!fibre.modular_magic_closure);

    PrimeLaneRouterStateV1 state = PrimeMemristiveFifthLaneV1::initial_state();
    CHECK(PrimeMemristiveFifthLaneV1::validate_state(state));
    const PrimeLaneRouterStateV1 frozen_state = state;

    PrimeLaneRouteDecisionV1 decision{};
    CHECK(PrimeMemristiveFifthLaneV1::route(fingerprint, state, 4U, decision) == PrimeLaneStatusV1::OK);
    CHECK(decision.selected_count == 4U);
    CHECK(decision.prime[0] == 331U);
    CHECK(decision.prime[1] == 317U);
    CHECK(decision.prime[2] == 313U);
    CHECK(decision.prime[3] == 311U);
    CHECK(decision.authority.candidate_only);
    CHECK(!decision.authority.canonical_mutation_authority);
    CHECK(std::memcmp(&state, &frozen_state, sizeof(state)) == 0);

    PrimeLaneRouteDecisionV1 decision_replay{};
    CHECK(PrimeMemristiveFifthLaneV1::route(fingerprint, state, 4U, decision_replay) == PrimeLaneStatusV1::OK);
    CHECK(std::memcmp(&decision, &decision_replay, sizeof(decision)) == 0);

    PrimeLaneRouterStateV1 candidate{};
    CHECK(PrimeMemristiveFifthLaneV1::apply_feedback(state, decision, 1, candidate) == PrimeLaneStatusV1::OK);
    CHECK(candidate.step_count == 1U);
    CHECK(candidate.update_count == 1U);
    CHECK(std::memcmp(&state, &frozen_state, sizeof(state)) == 0);
    for (std::size_t slot = 0U; slot < decision.selected_count; ++slot) {
        const std::size_t fibre = decision.fibre_index[slot];
        CHECK(candidate.conductance[fibre] == HHS_PASS219_PRIME_LANE_UPDATE_QUANTUM);
        CHECK(candidate.activation_count[fibre] == 1U);
    }

    PrimeLaneRouteDecisionV1 learned_decision{};
    CHECK(PrimeMemristiveFifthLaneV1::route(fingerprint, candidate, 4U, learned_decision) == PrimeLaneStatusV1::OK);
    CHECK(learned_decision.selected_count == 4U);
    CHECK(learned_decision.prime[0] == 331U);

    /* A reinforced low-prime fibre must be able to override neutral high-prime selectivity. */
    PrimeLaneRouteDecisionV1 reinforce_low{};
    reinforce_low.selected_count = 1U;
    reinforce_low.fibre_index[0] = 0U;
    reinforce_low.prime[0] = HHS_PASS219_PRIME_LANE_PRIMES[0];
    PrimeLaneRouterStateV1 learned_low{};
    CHECK(PrimeMemristiveFifthLaneV1::apply_feedback(state, reinforce_low, 1, learned_low) == PrimeLaneStatusV1::OK);
    PrimeLaneRouteDecisionV1 low_override{};
    CHECK(PrimeMemristiveFifthLaneV1::route(fingerprint, learned_low, 1U, low_override) == PrimeLaneStatusV1::OK);
    CHECK(low_override.selected_count == 1U);
    CHECK(low_override.prime[0] == 5U);

    PrimeLaneRouterStateV1 negative_candidate{};
    CHECK(PrimeMemristiveFifthLaneV1::apply_feedback(candidate, learned_decision, -1, negative_candidate) == PrimeLaneStatusV1::OK);
    for (std::size_t slot = 0U; slot < learned_decision.selected_count; ++slot) {
        const std::size_t fibre = learned_decision.fibre_index[slot];
        CHECK(negative_candidate.conductance[fibre] == 0);
        CHECK(negative_candidate.activation_count[fibre] == 2U);
    }

    PrimeLaneRouterStateV1 invalid_feedback_candidate{};
    CHECK(PrimeMemristiveFifthLaneV1::apply_feedback(state, decision, 2, invalid_feedback_candidate) ==
          PrimeLaneStatusV1::INVALID_FEEDBACK);
    CHECK(std::memcmp(&invalid_feedback_candidate, &state, sizeof(state)) == 0);

    PrimeLaneRouterStateV1 bounded = state;
    for (std::size_t slot = 0U; slot < decision.selected_count; ++slot)
        bounded.conductance[decision.fibre_index[slot]] = HHS_PASS219_PRIME_LANE_WEIGHT_BOUND;
    PrimeLaneRouterStateV1 saturated{};
    CHECK(PrimeMemristiveFifthLaneV1::apply_feedback(bounded, decision, 1, saturated) == PrimeLaneStatusV1::OK);
    for (std::size_t slot = 0U; slot < decision.selected_count; ++slot)
        CHECK(saturated.conductance[decision.fibre_index[slot]] == HHS_PASS219_PRIME_LANE_WEIGHT_BOUND);

    state.activation_budget = 2U;
    PrimeLaneRouteDecisionV1 budgeted{};
    CHECK(PrimeMemristiveFifthLaneV1::route(fingerprint, state, 65U, budgeted) == PrimeLaneStatusV1::OK);
    CHECK(budgeted.selected_count == 2U);

    return 0;
}
