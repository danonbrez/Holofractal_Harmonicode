#include "../include/hhs_pass219_hhcq_prime_rational_expansion_1_30.h"

#include <limits.h>
#include <string.h>

static const char HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE[] =
    "Sqrt((A*B))*(A*B)/Sqrt((A*B))==A/B*B/A==((-x*y)^(((x+y^2)*(y+x^2))/((x\302\262+y\302\262)\302\262*Sqrt((a*b)))))^x\302\262 where A,B are two primes and AB=P\342\201\264";

static const uint8_t HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE_SHA256[
    HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SHA256_BYTES
] = {
    0x6dU, 0x91U, 0xbfU, 0x7dU, 0x4aU, 0x70U, 0xedU, 0xf3U,
    0x4eU, 0xc5U, 0xcdU, 0x30U, 0xa4U, 0xeaU, 0x7dU, 0x04U,
    0xccU, 0x08U, 0xafU, 0x50U, 0x13U, 0xf7U, 0x63U, 0x15U,
    0x76U, 0xb1U, 0x18U, 0xc3U, 0x69U, 0xb2U, 0xeaU, 0x14U
};

_Static_assert(sizeof(HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE) - 1U ==
               HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE_BYTES,
               "Phase10 prime-rational source byte length drift");

static uint64_t hhs_p219_p10_mix64(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static uint64_t hhs_p219_p10_gcd64(uint64_t a, uint64_t b) {
    while (b != 0U) {
        uint64_t r = a % b;
        a = b;
        b = r;
    }
    return a;
}

static int hhs_p219_p10_is_prime(uint32_t n) {
    uint32_t d;
    if (n < 2U || n > HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_MAX_PRIME)
        return 0;
    if (n == 2U)
        return 1;
    if ((n & 1U) == 0U)
        return 0;
    for (d = 3U; d <= n / d; d += 2U) {
        if (n % d == 0U)
            return 0;
    }
    return 1;
}

static int hhs_p219_p10_flag(uint8_t value) {
    return value == 0U || value == 1U;
}

static int hhs_p219_p10_add_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL || UINT64_MAX - a < b)
        return 0;
    *out = a + b;
    return 1;
}

static int hhs_p219_p10_mul_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL || (a != 0U && b > UINT64_MAX / a))
        return 0;
    *out = a * b;
    return 1;
}

static void hhs_p219_p10_axis(
    uint64_t units,
    uint64_t *out_credit,
    uint64_t *out_debt
) {
    const uint64_t parity = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    if (units <= parity) {
        *out_credit = parity - units;
        *out_debt = 0U;
    } else {
        *out_credit = 0U;
        *out_debt = units - parity;
    }
}

static int hhs_p219_p10_axis_in_rational_bounds(
    uint64_t units,
    uint64_t lower_num,
    uint64_t lower_den,
    uint64_t upper_num,
    uint64_t upper_den
) {
    const uint64_t parity = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    uint64_t lhs_lower;
    uint64_t rhs_lower;
    uint64_t lhs_upper;
    uint64_t rhs_upper;
    if (units == 0U || lower_den == 0U || upper_den == 0U)
        return 0;
    if (!hhs_p219_p10_mul_u64(units, lower_den, &lhs_lower) ||
        !hhs_p219_p10_mul_u64(parity, lower_num, &rhs_lower) ||
        !hhs_p219_p10_mul_u64(units, upper_den, &lhs_upper) ||
        !hhs_p219_p10_mul_u64(parity, upper_num, &rhs_upper))
        return 0;
    return lhs_lower >= rhs_lower && lhs_upper <= rhs_upper;
}

uint32_t hhs_exact_pass219_hhcq_prime_rational_version(void) {
    return HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION;
}

HHSExactStatus hhs_exact_pass219_hhcq_prime_rational_descriptor(
    HHSExactPass219HHCQPrimeRationalDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION;
    out_descriptor->inherited_policy_state_bytes =
        (uint32_t)sizeof(HHSExactPass219HHCQJointStateV1);
    out_descriptor->source_bytes = HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE_BYTES;
    out_descriptor->economy_parity_units = HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS;
    out_descriptor->phase_modulus = HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS;
    out_descriptor->divisor_count = HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT;
    out_descriptor->verbatim_extension_source_preserved = 1U;
    out_descriptor->two_prime_rational_boundary = 1U;
    out_descriptor->ab_equals_p4_constructor = 1U;
    out_descriptor->reciprocal_ab_ba_closure = 1U;
    out_descriptor->normalized_product_scale_witness = 1U;
    out_descriptor->symbolic_polynomial_root_retained = 1U;
    out_descriptor->exact_rational_cross_multiplication = 1U;
    out_descriptor->monotone_resolution_expansion = 1U;
    out_descriptor->exact_one_to_one_information_closure = 1U;
    out_descriptor->phase5_resolution_locked = 1U;
    out_descriptor->fixed_size_policy_state = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->exact_integer_only = 1U;
    memcpy(out_descriptor->source_sha256,
           HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE_SHA256,
           sizeof(out_descriptor->source_sha256));
    if (out_descriptor->inherited_policy_state_bytes != 112U ||
        out_descriptor->economy_parity_units != 5184U ||
        out_descriptor->phase_modulus != 72U ||
        out_descriptor->divisor_count != 35U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_prime_rational_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length != NULL)
        *out_length = HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE_BYTES;
    if (out_bytes == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(out_bytes,
           HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE,
           HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_SOURCE_BYTES);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_prime_rational_expand(
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t x_phase72,
    uint8_t y_phase72,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQPrimeRationalExpansionV1 *out_expansion
) {
    uint64_t p2;
    uint64_t q2;
    uint64_t x2;
    uint64_t y2;
    uint64_t sum;
    uint64_t numerator;
    uint64_t denominator;
    uint64_t gcd;
    uint64_t signature;
    uint16_t parameters;
    uint8_t polynomial_index;
    uint8_t expanded_index;

    if (out_expansion == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_p219_p10_is_prime(prime_p) ||
        !hhs_p219_p10_is_prime(prime_q) ||
        prime_p == prime_q ||
        x_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        y_phase72 >= HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS ||
        (x_phase72 == 0U && y_phase72 == 0U) ||
        base_resolution_index >= HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    p2 = (uint64_t)prime_p * (uint64_t)prime_p;
    q2 = (uint64_t)prime_q * (uint64_t)prime_q;
    x2 = (uint64_t)x_phase72 * (uint64_t)x_phase72;
    y2 = (uint64_t)y_phase72 * (uint64_t)y_phase72;
    sum = x2 + y2;
    denominator = sum * sum;
    numerator = ((uint64_t)x_phase72 + y2) *
                ((uint64_t)y_phase72 + x2) * x2;
    if (denominator == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    gcd = hhs_p219_p10_gcd64(numerator, denominator);
    if (gcd == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    numerator /= gcd;
    denominator /= gcd;

    signature = UINT64_C(0x219ab10c00130) ^
        ((uint64_t)prime_p << 48U) ^
        ((uint64_t)prime_q << 32U) ^
        ((uint64_t)x_phase72 << 24U) ^
        ((uint64_t)y_phase72 << 16U) ^
        numerator ^ (denominator << 1U) ^
        (uint64_t)((uint32_t)((int32_t)x_phase72 * -(int32_t)y_phase72));
    signature = hhs_p219_p10_mix64(signature);
    polynomial_index = (uint8_t)(
        ((signature % HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS) *
         HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT) /
        HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS);
    expanded_index = polynomial_index > base_resolution_index
        ? polynomial_index
        : base_resolution_index;
    if (hhs_exact_pass219_hhcq_resolution_divisor(expanded_index, &parameters) !=
        HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_expansion, 0, sizeof(*out_expansion));
    out_expansion->struct_size = (uint32_t)sizeof(*out_expansion);
    out_expansion->version = HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION;
    out_expansion->prime_p = prime_p;
    out_expansion->prime_q = prime_q;
    out_expansion->x_phase72 = x_phase72;
    out_expansion->y_phase72 = y_phase72;
    out_expansion->base_resolution_index = base_resolution_index;
    out_expansion->polynomial_resolution_index = polynomial_index;
    out_expansion->expanded_resolution_index = expanded_index;
    out_expansion->expansion_phase72 = (uint8_t)(signature % HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS);
    out_expansion->expanded_resolution_parameters = parameters;
    out_expansion->expanded_region_count =
        (uint16_t)(HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT / parameters);
    out_expansion->a_over_b_numerator = p2;
    out_expansion->a_over_b_denominator = q2;
    out_expansion->b_over_a_numerator = q2;
    out_expansion->b_over_a_denominator = p2;
    out_expansion->polynomial_base = -((int32_t)x_phase72 * (int32_t)y_phase72);
    out_expansion->polynomial_numerator = numerator;
    out_expansion->polynomial_denominator = denominator;
    out_expansion->product_ab_equals_p4 = 1U;
    out_expansion->sqrt_ab_equals_p2 = 1U;
    out_expansion->reciprocal_product_equals_one = 1U;
    out_expansion->polynomial_fraction_reduced =
        hhs_p219_p10_gcd64(numerator, denominator) == 1U ? 1U : 0U;
    out_expansion->symbolic_sqrt_a_times_b_retained = 1U;
    out_expansion->noncoarsening = expanded_index >= base_resolution_index ? 1U : 0U;
    out_expansion->candidate_only = 1U;
    out_expansion->exact_integer_only = 1U;
    out_expansion->expansion_signature64 = hhs_p219_p10_mix64(
        signature ^ p2 ^ (q2 << 1U) ^
        ((uint64_t)expanded_index << 56U) ^
        ((uint64_t)parameters << 32U));
    if (out_expansion->expanded_region_count * parameters !=
            HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT ||
        out_expansion->noncoarsening != 1U ||
        out_expansion->polynomial_fraction_reduced != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_prime_rational_evaluate(
    const HHSExactPass219HHCQPrimeRationalCandidateV1 *candidate,
    HHSExactPass219HHCQPrimeRationalResultV1 *out_result
) {
    HHSExactPass219HHCQPrimeRationalExpansionV1 expansion;
    uint64_t lower_num;
    uint64_t lower_den;
    uint64_t upper_num;
    uint64_t upper_den;
    uint64_t total_savings = 0U;
    uint64_t total_debt = 0U;
    uint64_t total_spend = 0U;
    uint64_t total_cost;
    uint64_t signature;
    int admitted;

    if (candidate == NULL || out_result == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate->struct_size != sizeof(*candidate) ||
        candidate->version != HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (candidate->intrinsic_resolution_index >= HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT ||
        candidate->effective_resolution_index >= HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT ||
        candidate->required_resolution_index >= HHS_EXACT_PASS219_HHCQ_DIVISOR_COUNT ||
        candidate->latency_units == 0U || candidate->memory_units == 0U ||
        candidate->compression_units == 0U || candidate->translation_units == 0U ||
        candidate->lossy_information_units > HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS ||
        candidate->recovered_information_units > HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS ||
        !hhs_p219_p10_flag(candidate->exact_semantic_closure) ||
        !hhs_p219_p10_flag(candidate->exact_reconstruction) ||
        !hhs_p219_p10_flag(candidate->all_native_modalities_translatable) ||
        !hhs_p219_p10_flag(candidate->one_step_translation) ||
        !hhs_p219_p10_flag(candidate->phase5_resolution_locked) ||
        !hhs_p219_p10_flag(candidate->candidate_only) ||
        !hhs_p219_p10_flag(candidate->canonical_authority_requested) ||
        !hhs_p219_p10_flag(candidate->floating_point_authority_requested))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    if (hhs_exact_pass219_hhcq_prime_rational_expand(
            candidate->prime_p,
            candidate->prime_q,
            candidate->x_phase72,
            candidate->y_phase72,
            candidate->effective_resolution_index,
            &expansion) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    if (expansion.a_over_b_numerator <= expansion.a_over_b_denominator) {
        lower_num = expansion.a_over_b_numerator;
        lower_den = expansion.a_over_b_denominator;
        upper_num = expansion.b_over_a_numerator;
        upper_den = expansion.b_over_a_denominator;
    } else {
        lower_num = expansion.b_over_a_numerator;
        lower_den = expansion.b_over_a_denominator;
        upper_num = expansion.a_over_b_numerator;
        upper_den = expansion.a_over_b_denominator;
    }

    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (uint32_t)sizeof(*out_result);
    out_result->version = HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION;
    out_result->route_id = candidate->route_id;
    out_result->decision = HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_REJECTED;
    out_result->expansion = expansion;

    out_result->rational_bounds_met =
        hhs_p219_p10_axis_in_rational_bounds(candidate->latency_units,
                                             lower_num, lower_den,
                                             upper_num, upper_den) &&
        hhs_p219_p10_axis_in_rational_bounds(candidate->memory_units,
                                             lower_num, lower_den,
                                             upper_num, upper_den) &&
        hhs_p219_p10_axis_in_rational_bounds(candidate->compression_units,
                                             lower_num, lower_den,
                                             upper_num, upper_den) &&
        hhs_p219_p10_axis_in_rational_bounds(candidate->translation_units,
                                             lower_num, lower_den,
                                             upper_num, upper_den);

    hhs_p219_p10_axis(candidate->latency_units,
                      &out_result->latency_credit_units,
                      &out_result->latency_debt_units);
    hhs_p219_p10_axis(candidate->memory_units,
                      &out_result->memory_credit_units,
                      &out_result->memory_debt_units);
    hhs_p219_p10_axis(candidate->compression_units,
                      &out_result->compression_credit_units,
                      &out_result->compression_debt_units);
    hhs_p219_p10_axis(candidate->translation_units,
                      &out_result->translation_credit_units,
                      &out_result->translation_debt_units);

    if (!hhs_p219_p10_add_u64(out_result->latency_credit_units,
                               out_result->memory_credit_units,
                               &total_savings) ||
        !hhs_p219_p10_add_u64(total_savings,
                               out_result->compression_credit_units,
                               &total_savings) ||
        !hhs_p219_p10_add_u64(total_savings,
                               out_result->translation_credit_units,
                               &total_savings) ||
        !hhs_p219_p10_add_u64(out_result->latency_debt_units,
                               out_result->memory_debt_units,
                               &total_debt) ||
        !hhs_p219_p10_add_u64(total_debt,
                               out_result->compression_debt_units,
                               &total_debt) ||
        !hhs_p219_p10_add_u64(total_debt,
                               out_result->translation_debt_units,
                               &total_debt) ||
        !hhs_p219_p10_add_u64(candidate->redundancy_spend_units,
                               candidate->ecc_spend_units,
                               &total_spend) ||
        !hhs_p219_p10_add_u64(total_spend,
                               candidate->precision_spend_units,
                               &total_spend) ||
        !hhs_p219_p10_add_u64(total_spend,
                               candidate->learning_spend_units,
                               &total_spend) ||
        !hhs_p219_p10_add_u64(total_debt, total_spend, &total_cost) ||
        total_savings > (uint64_t)INT64_MAX || total_cost > (uint64_t)INT64_MAX)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    out_result->total_savings_units = total_savings;
    out_result->total_axis_debt_units = total_debt;
    out_result->total_spend_units = total_spend;
    if (total_savings >= total_cost)
        out_result->net_budget_units = (int64_t)(total_savings - total_cost);
    else
        out_result->net_budget_units = -(int64_t)(total_cost - total_savings);

    out_result->lossy_information_units = candidate->lossy_information_units;
    out_result->recovered_information_units = candidate->recovered_information_units;
    out_result->information_one_to_one =
        candidate->lossy_information_units == candidate->recovered_information_units;
    out_result->expanded_resolution_met =
        expansion.expanded_resolution_index >= candidate->required_resolution_index;
    out_result->lower_resolution_recovered =
        candidate->intrinsic_resolution_index < candidate->required_resolution_index &&
        out_result->expanded_resolution_met != 0U &&
        out_result->information_one_to_one != 0U &&
        candidate->lossy_information_units != 0U &&
        candidate->exact_reconstruction != 0U &&
        candidate->exact_semantic_closure != 0U &&
        candidate->all_native_modalities_translatable != 0U;
    out_result->exact_semantic_closure = candidate->exact_semantic_closure;
    out_result->exact_reconstruction = candidate->exact_reconstruction;
    out_result->all_native_modalities_translatable =
        candidate->all_native_modalities_translatable;
    out_result->one_step_translation = candidate->one_step_translation;
    out_result->phase5_resolution_locked = candidate->phase5_resolution_locked;
    out_result->budget_nonnegative = out_result->net_budget_units >= 0 ? 1U : 0U;
    out_result->candidate_only = 1U;
    out_result->exact_integer_only = 1U;

    admitted =
        out_result->rational_bounds_met != 0U &&
        out_result->information_one_to_one != 0U &&
        out_result->expanded_resolution_met != 0U &&
        candidate->exact_semantic_closure != 0U &&
        candidate->exact_reconstruction != 0U &&
        candidate->all_native_modalities_translatable != 0U &&
        candidate->one_step_translation != 0U &&
        candidate->phase5_resolution_locked != 0U &&
        candidate->candidate_only != 0U &&
        candidate->canonical_authority_requested == 0U &&
        candidate->floating_point_authority_requested == 0U &&
        out_result->budget_nonnegative != 0U;
    if (candidate->intrinsic_resolution_index < candidate->required_resolution_index &&
        out_result->lower_resolution_recovered == 0U)
        admitted = 0;
    if (admitted)
        out_result->decision = HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_ADMITTED;

    signature = UINT64_C(0x219ec0ab00130) ^
        expansion.expansion_signature64 ^
        ((uint64_t)candidate->route_id << 32U) ^
        total_savings ^ (total_debt << 1U) ^ (total_spend << 2U) ^
        (uint64_t)out_result->net_budget_units ^
        ((uint64_t)candidate->lossy_information_units << 32U) ^
        (uint64_t)candidate->recovered_information_units ^
        ((uint64_t)out_result->decision << 60U);
    out_result->result_signature64 = hhs_p219_p10_mix64(signature);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_prime_rational_select(
    const HHSExactPass219HHCQPrimeRationalCandidateV1 *candidates,
    size_t candidate_count,
    HHSExactPass219HHCQPrimeRationalSelectionV1 *out_selection
) {
    size_t i;
    size_t best_index = 0U;
    int have_best = 0;
    HHSExactPass219HHCQPrimeRationalResultV1 best_result;
    uint64_t signature = UINT64_C(0x2195e1ec00130);

    if (candidates == NULL || out_selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate_count == 0U ||
        candidate_count > HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_MAX_CANDIDATES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_selection, 0, sizeof(*out_selection));
    memset(&best_result, 0, sizeof(best_result));
    out_selection->struct_size = (uint32_t)sizeof(*out_selection);
    out_selection->version = HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION;
    out_selection->candidate_count = (uint32_t)candidate_count;
    out_selection->selected_route_id = UINT32_MAX;
    out_selection->selected_candidate_index = UINT32_MAX;
    out_selection->exact_integer_only = 1U;
    out_selection->candidate_only = 1U;

    for (i = 0U; i < candidate_count; ++i) {
        HHSExactPass219HHCQPrimeRationalResultV1 result;
        HHSExactStatus status = hhs_exact_pass219_hhcq_prime_rational_evaluate(
            &candidates[i], &result);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        signature = hhs_p219_p10_mix64(
            signature ^ result.result_signature64 ^ (uint64_t)i);
        if (result.decision != HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_DECISION_ADMITTED)
            continue;
        ++out_selection->admitted_count;
        if (!have_best ||
            result.expansion.expanded_resolution_index >
                best_result.expansion.expanded_resolution_index ||
            (result.expansion.expanded_resolution_index ==
                 best_result.expansion.expanded_resolution_index &&
             result.net_budget_units > best_result.net_budget_units) ||
            (result.expansion.expanded_resolution_index ==
                 best_result.expansion.expanded_resolution_index &&
             result.net_budget_units == best_result.net_budget_units &&
             candidates[i].latency_units < candidates[best_index].latency_units) ||
            (result.expansion.expanded_resolution_index ==
                 best_result.expansion.expanded_resolution_index &&
             result.net_budget_units == best_result.net_budget_units &&
             candidates[i].latency_units == candidates[best_index].latency_units &&
             candidates[i].memory_units < candidates[best_index].memory_units) ||
            (result.expansion.expanded_resolution_index ==
                 best_result.expansion.expanded_resolution_index &&
             result.net_budget_units == best_result.net_budget_units &&
             candidates[i].latency_units == candidates[best_index].latency_units &&
             candidates[i].memory_units == candidates[best_index].memory_units &&
             candidates[i].compression_units < candidates[best_index].compression_units) ||
            (result.expansion.expanded_resolution_index ==
                 best_result.expansion.expanded_resolution_index &&
             result.net_budget_units == best_result.net_budget_units &&
             candidates[i].latency_units == candidates[best_index].latency_units &&
             candidates[i].memory_units == candidates[best_index].memory_units &&
             candidates[i].compression_units == candidates[best_index].compression_units &&
             candidates[i].translation_units < candidates[best_index].translation_units) ||
            (result.expansion.expanded_resolution_index ==
                 best_result.expansion.expanded_resolution_index &&
             result.net_budget_units == best_result.net_budget_units &&
             candidates[i].latency_units == candidates[best_index].latency_units &&
             candidates[i].memory_units == candidates[best_index].memory_units &&
             candidates[i].compression_units == candidates[best_index].compression_units &&
             candidates[i].translation_units == candidates[best_index].translation_units &&
             candidates[i].route_id < candidates[best_index].route_id)) {
            have_best = 1;
            best_index = i;
            best_result = result;
        }
    }

    if (have_best) {
        out_selection->selected_route_id = candidates[best_index].route_id;
        out_selection->selected_candidate_index = (uint32_t)best_index;
        out_selection->selected_expanded_resolution_index =
            best_result.expansion.expanded_resolution_index;
        out_selection->selected_intrinsic_resolution_index =
            candidates[best_index].intrinsic_resolution_index;
        out_selection->selected_expanded_resolution_parameters =
            best_result.expansion.expanded_resolution_parameters;
        out_selection->selected_net_budget_units = best_result.net_budget_units;
    }
    out_selection->selection_signature64 = hhs_p219_p10_mix64(
        signature ^ ((uint64_t)out_selection->admitted_count << 48U) ^
        ((uint64_t)out_selection->selected_route_id << 16U) ^
        (uint64_t)out_selection->selected_candidate_index);
    return HHS_EXACT_STATUS_OK;
}
