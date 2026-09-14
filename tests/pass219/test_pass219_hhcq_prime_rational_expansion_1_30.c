#include "../../hhs_runtime/include/hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <string.h>

static int check(int condition) {
    return condition ? 0 : 1;
}

static HHSExactPass219HHCQPrimeRationalCandidateV1 candidate_base(
    uint32_t route_id,
    uint8_t intrinsic_resolution_index,
    uint8_t effective_resolution_index,
    uint8_t required_resolution_index,
    uint8_t x,
    uint8_t y
) {
    HHSExactPass219HHCQPrimeRationalCandidateV1 c;
    memset(&c, 0, sizeof(c));
    c.struct_size = (uint32_t)sizeof(c);
    c.version = HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION;
    c.route_id = route_id;
    c.prime_p = 2U;
    c.prime_q = 3U;
    c.x_phase72 = x;
    c.y_phase72 = y;
    c.intrinsic_resolution_index = intrinsic_resolution_index;
    c.effective_resolution_index = effective_resolution_index;
    c.required_resolution_index = required_resolution_index;
    c.latency_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.memory_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.compression_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.translation_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    c.exact_semantic_closure = 1U;
    c.exact_reconstruction = 1U;
    c.all_native_modalities_translatable = 1U;
    c.one_step_translation = 1U;
    c.phase5_resolution_locked = 1U;
    c.candidate_only = 1U;
    return c;
}

int main(void) {
    static const uint8_t expected_sha[32] = {
        0x6dU, 0x91U, 0xbfU, 0x7dU, 0x4aU, 0x70U, 0xedU, 0xf3U,
        0x4eU, 0xc5U, 0xcdU, 0x30U, 0xa4U, 0xeaU, 0x7dU, 0x04U,
        0xccU, 0x08U, 0xafU, 0x50U, 0x13U, 0xf7U, 0x63U, 0x15U,
        0x76U, 0xb1U, 0x18U, 0xc3U, 0x69U, 0xb2U, 0xeaU, 0x14U
    };
    static const char expected_source[] =
        "Sqrt((A*B))*(A*B)/Sqrt((A*B))==A/B*B/A==((-x*y)^(((x+y^2)*(y+x^2))/((x\302\262+y\302\262)\302\262*Sqrt((a*b)))))^x\302\262 where A,B are two primes and AB=P\342\201\264";
    HHSExactPass219HHCQPrimeRationalDescriptorV1 descriptor;
    HHSExactPass219HHCQPrimeRationalExpansionV1 expansion;
    HHSExactPass219HHCQPrimeRationalResultV1 result;
    HHSExactPass219HHCQPrimeRationalSelectionV1 selection_a;
    HHSExactPass219HHCQPrimeRationalSelectionV1 selection_b;
    HHSExactPass219HHCQPrimeRationalCandidateV1 direct;
    HHSExactPass219HHCQPrimeRationalCandidateV1 proven_lower;
    HHSExactPass219HHCQPrimeRationalCandidateV1 unproven_lower;
    HHSExactPass219HHCQPrimeRationalCandidateV1 outside;
    HHSExactPass219HHCQPrimeRationalCandidateV1 candidates[2];
    uint8_t source[HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE_BYTES];
    size_t source_length = 0U;
    uint8_t seen[HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT];
    uint32_t x;
    uint32_t y;
    uint32_t coverage = 0U;

    memset(&descriptor, 0, sizeof(descriptor));
    if (check(hhs_exact_pass219_hhcq_prime_rational_version() ==
              HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION)) return 1;
    if (check(hhs_exact_pass219_hhcq_prime_rational_descriptor(&descriptor) ==
              HHS_EXACT_STATUS_OK)) return 2;
    if (check(descriptor.struct_size == sizeof(descriptor) &&
              descriptor.version == HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION &&
              descriptor.inherited_policy_state_bytes == 112U &&
              descriptor.source_bytes == 135U &&
              descriptor.economy_parity_units == 5184U &&
              descriptor.phase_modulus == 72U &&
              descriptor.divisor_count == 35U &&
              descriptor.verbatim_extension_source_preserved == 1U &&
              descriptor.two_prime_rational_boundary == 1U &&
              descriptor.ab_equals_p4_constructor == 1U &&
              descriptor.reciprocal_ab_ba_closure == 1U &&
              descriptor.normalized_product_scale_witness == 1U &&
              descriptor.symbolic_polynomial_root_retained == 1U &&
              descriptor.exact_rational_cross_multiplication == 1U &&
              descriptor.monotone_resolution_expansion == 1U &&
              descriptor.exact_one_to_one_information_closure == 1U &&
              descriptor.phase5_resolution_locked == 1U &&
              descriptor.fixed_size_policy_state == 1U &&
              descriptor.candidate_only == 1U &&
              descriptor.exact_integer_only == 1U &&
              descriptor.canonical_mutation_authority == 0U &&
              descriptor.canonical_hash72_authority == 0U &&
              descriptor.canonical_hash216_authority == 0U &&
              descriptor.canonical_persistence_authority == 0U &&
              descriptor.floating_point_authority == 0U &&
              memcmp(descriptor.source_sha256, expected_sha, sizeof(expected_sha)) == 0)) return 3;

    if (check(sizeof(expected_source) - 1U ==
              HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE_BYTES)) return 4;
    if (check(hhs_exact_pass219_hhcq_prime_rational_source(
                  source, sizeof(source), &source_length) == HHS_EXACT_STATUS_OK &&
              source_length == sizeof(source) &&
              memcmp(source, expected_source, sizeof(source)) == 0)) return 5;

    memset(&expansion, 0, sizeof(expansion));
    if (check(hhs_exact_pass219_hhcq_prime_rational_expand(
                  2U, 3U, 1U, 1U, 0U, &expansion) == HHS_EXACT_STATUS_OK)) return 6;
    if (check(expansion.a_over_b_numerator == 4U &&
              expansion.a_over_b_denominator == 9U &&
              expansion.b_over_a_numerator == 9U &&
              expansion.b_over_a_denominator == 4U &&
              expansion.polynomial_base == -1 &&
              expansion.polynomial_numerator == 1U &&
              expansion.polynomial_denominator == 1U &&
              expansion.product_ab_equals_p4 == 1U &&
              expansion.sqrt_ab_equals_p2 == 1U &&
              expansion.reciprocal_product_equals_one == 1U &&
              expansion.polynomial_fraction_reduced == 1U &&
              expansion.symbolic_sqrt_a_times_b_retained == 1U &&
              expansion.noncoarsening == 1U &&
              expansion.candidate_only == 1U &&
              expansion.exact_integer_only == 1U &&
              expansion.canonical_authority_changed == 0U &&
              expansion.floating_point_authority == 0U &&
              (uint32_t)expansion.expanded_resolution_parameters *
                  (uint32_t)expansion.expanded_region_count == 5184U)) return 7;

    if (check(hhs_exact_pass219_hhcq_prime_rational_expand(
                  4U, 3U, 1U, 1U, 0U, &expansion) == HHS_EXACT_STATUS_RANGE_ERROR)) return 8;
    if (check(hhs_exact_pass219_hhcq_prime_rational_expand(
                  2U, 2U, 1U, 1U, 0U, &expansion) == HHS_EXACT_STATUS_RANGE_ERROR)) return 9;
    if (check(hhs_exact_pass219_hhcq_prime_rational_expand(
                  2U, 3U, 0U, 0U, 0U, &expansion) == HHS_EXACT_STATUS_RANGE_ERROR)) return 10;
    if (check(hhs_exact_pass219_hhcq_prime_rational_expand(
                  2U, 3U, 72U, 1U, 0U, &expansion) == HHS_EXACT_STATUS_RANGE_ERROR)) return 11;
    if (check(hhs_exact_pass219_hhcq_prime_rational_expand(
                  2U, 3U, 1U, 1U, 35U, &expansion) == HHS_EXACT_STATUS_RANGE_ERROR)) return 12;

    memset(seen, 0, sizeof(seen));
    for (x = 0U; x < 72U; ++x) {
        for (y = 0U; y < 72U; ++y) {
            if (x == 0U && y == 0U) continue;
            memset(&expansion, 0, sizeof(expansion));
            if (check(hhs_exact_pass219_hhcq_prime_rational_expand(
                          2U, 3U, (uint8_t)x, (uint8_t)y, 0U, &expansion) ==
                      HHS_EXACT_STATUS_OK)) return 13;
            if (check(expansion.polynomial_resolution_index < 35U &&
                      expansion.expanded_resolution_index >= expansion.base_resolution_index &&
                      expansion.noncoarsening == 1U)) return 14;
            seen[expansion.polynomial_resolution_index] = 1U;
        }
    }
    for (x = 0U; x < 35U; ++x)
        coverage += seen[x] != 0U ? 1U : 0U;
    if (check(coverage == 35U)) return 15;

    memset(&expansion, 0, sizeof(expansion));
    if (check(hhs_exact_pass219_hhcq_prime_rational_expand(
                  2U, 3U, 0U, 17U, 30U, &expansion) == HHS_EXACT_STATUS_OK &&
              expansion.polynomial_resolution_index == 34U &&
              expansion.expanded_resolution_index == 34U &&
              expansion.expanded_resolution_parameters == 1U)) return 16;

    direct = candidate_base(100U, 34U, 34U, 34U, 1U, 1U);
    memset(&result, 0, sizeof(result));
    if (check(hhs_exact_pass219_hhcq_prime_rational_evaluate(&direct, &result) ==
                  HHS_EXACT_STATUS_OK &&
              result.decision == HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_ADMITTED &&
              result.rational_bounds_met == 1U &&
              result.information_one_to_one == 1U &&
              result.expanded_resolution_met == 1U &&
              result.net_budget_units == 0 &&
              result.canonical_authority_changed == 0U &&
              result.floating_point_authority == 0U)) return 17;

    proven_lower = candidate_base(200U, 30U, 30U, 34U, 0U, 17U);
    proven_lower.latency_units = 2592U;
    proven_lower.memory_units = 2592U;
    proven_lower.compression_units = 2592U;
    proven_lower.translation_units = 5184U;
    proven_lower.redundancy_spend_units = 1000U;
    proven_lower.ecc_spend_units = 1000U;
    proven_lower.precision_spend_units = 1000U;
    proven_lower.learning_spend_units = 1000U;
    proven_lower.lossy_information_units = 2592U;
    proven_lower.recovered_information_units = 2592U;
    memset(&result, 0, sizeof(result));
    if (check(hhs_exact_pass219_hhcq_prime_rational_evaluate(&proven_lower, &result) ==
                  HHS_EXACT_STATUS_OK &&
              result.decision == HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_ADMITTED &&
              result.expansion.expanded_resolution_index == 34U &&
              result.rational_bounds_met == 1U &&
              result.information_one_to_one == 1U &&
              result.lower_resolution_recovered == 1U &&
              result.total_savings_units == 7776U &&
              result.total_spend_units == 4000U &&
              result.net_budget_units == 3776)) return 18;

    unproven_lower = proven_lower;
    unproven_lower.route_id = 201U;
    unproven_lower.exact_semantic_closure = 0U;
    unproven_lower.exact_reconstruction = 0U;
    unproven_lower.all_native_modalities_translatable = 0U;
    memset(&result, 0, sizeof(result));
    if (check(hhs_exact_pass219_hhcq_prime_rational_evaluate(&unproven_lower, &result) ==
                  HHS_EXACT_STATUS_OK &&
              result.rational_bounds_met == 1U &&
              result.information_one_to_one == 1U &&
              result.budget_nonnegative == 1U &&
              result.lower_resolution_recovered == 0U &&
              result.decision == HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_REJECTED)) return 19;

    outside = direct;
    outside.route_id = 300U;
    outside.latency_units = 12000U;
    memset(&result, 0, sizeof(result));
    if (check(hhs_exact_pass219_hhcq_prime_rational_evaluate(&outside, &result) ==
                  HHS_EXACT_STATUS_OK &&
              result.rational_bounds_met == 0U &&
              result.decision == HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_REJECTED)) return 20;
    outside = direct;
    outside.route_id = 301U;
    outside.memory_units = 2000U;
    memset(&result, 0, sizeof(result));
    if (check(hhs_exact_pass219_hhcq_prime_rational_evaluate(&outside, &result) ==
                  HHS_EXACT_STATUS_OK &&
              result.rational_bounds_met == 0U &&
              result.decision == HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_REJECTED)) return 21;

    outside = proven_lower;
    outside.route_id = 302U;
    outside.recovered_information_units = 2591U;
    memset(&result, 0, sizeof(result));
    if (check(hhs_exact_pass219_hhcq_prime_rational_evaluate(&outside, &result) ==
                  HHS_EXACT_STATUS_OK &&
              result.information_one_to_one == 0U &&
              result.decision == HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_REJECTED)) return 22;

    outside = proven_lower;
    outside.route_id = 303U;
    outside.redundancy_spend_units = 12000U;
    memset(&result, 0, sizeof(result));
    if (check(hhs_exact_pass219_hhcq_prime_rational_evaluate(&outside, &result) ==
                  HHS_EXACT_STATUS_OK &&
              result.budget_nonnegative == 0U &&
              result.decision == HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_REJECTED)) return 23;

    candidates[0] = direct;
    candidates[1] = proven_lower;
    memset(&selection_a, 0, sizeof(selection_a));
    memset(&selection_b, 0, sizeof(selection_b));
    if (check(hhs_exact_pass219_hhcq_prime_rational_select(
                  candidates, 2U, &selection_a) == HHS_EXACT_STATUS_OK &&
              hhs_exact_pass219_hhcq_prime_rational_select(
                  candidates, 2U, &selection_b) == HHS_EXACT_STATUS_OK &&
              memcmp(&selection_a, &selection_b, sizeof(selection_a)) == 0 &&
              selection_a.admitted_count == 2U &&
              selection_a.selected_route_id == 200U &&
              selection_a.selected_candidate_index == 1U &&
              selection_a.selected_expanded_resolution_index == 34U &&
              selection_a.selected_expanded_resolution_parameters == 1U &&
              selection_a.selected_net_budget_units == 3776 &&
              selection_a.candidate_only == 1U &&
              selection_a.exact_integer_only == 1U &&
              selection_a.canonical_authority_changed == 0U &&
              selection_a.floating_point_authority == 0U)) return 24;

    outside = direct;
    outside.prime_p = 4U;
    memset(&result, 0, sizeof(result));
    if (check(hhs_exact_pass219_hhcq_prime_rational_evaluate(&outside, &result) ==
              HHS_EXACT_STATUS_RANGE_ERROR)) return 25;

    return 0;
}
