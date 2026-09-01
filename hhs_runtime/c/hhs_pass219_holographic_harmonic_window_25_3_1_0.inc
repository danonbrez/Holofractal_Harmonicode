#include "../include/hhs_pass219_holographic_harmonic_window_25_3_1_0.h"

#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static const uint64_t HHS219_HOLO_POW3[HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_MAX_DEPTH + 1U] = {
    UINT64_C(1),
    UINT64_C(3),
    UINT64_C(9),
    UINT64_C(27),
    UINT64_C(81),
    UINT64_C(243),
    UINT64_C(729),
    UINT64_C(2187),
    UINT64_C(6561),
    UINT64_C(19683)
};

static const uint64_t HHS219_HOLO_POW25[HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_MAX_DEPTH + 1U] = {
    UINT64_C(1),
    UINT64_C(25),
    UINT64_C(625),
    UINT64_C(15625),
    UINT64_C(390625),
    UINT64_C(9765625),
    UINT64_C(244140625),
    UINT64_C(6103515625),
    UINT64_C(152587890625),
    UINT64_C(3814697265625)
};

static uint32_t hhs219_holographic_version_word(void) {
    return (HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_VERSION_PATCH;
}

static int hhs219_bool_u8(uint8_t value) {
    return value <= 1U;
}

static uint64_t hhs219_gcd_u64(uint64_t a, uint64_t b) {
    while (b != 0U) {
        const uint64_t r = a % b;
        a = b;
        b = r;
    }
    return a;
}

static int hhs219_mul_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL)
        return 0;
    if (a != 0U && b > UINT64_MAX / a)
        return 0;
    *out = a * b;
    return 1;
}

static int hhs219_mul_i64_positive(
    int64_t value,
    int64_t coefficient,
    int64_t *out
) {
    if (out == NULL || coefficient <= 0)
        return 0;

    if (value > 0 && value > INT64_MAX / coefficient)
        return 0;
    if (value < 0 && value < INT64_MIN / coefficient)
        return 0;

    *out = value * coefficient;
    return 1;
}

static int hhs219_add_i64(int64_t a, int64_t b, int64_t *out) {
    if (out == NULL)
        return 0;
    if (b > 0 && a > INT64_MAX - b)
        return 0;
    if (b < 0 && a < INT64_MIN - b)
        return 0;
    *out = a + b;
    return 1;
}

static int hhs219_fraction_compare_le(
    uint64_t a_num,
    uint64_t a_den,
    uint64_t b_num,
    uint64_t b_den,
    int *out_le
) {
    uint64_t g1;
    uint64_t g2;
    uint64_t left;
    uint64_t right;

    if (out_le == NULL || a_den == 0U || b_den == 0U)
        return 0;

    g1 = hhs219_gcd_u64(a_num, b_den);
    if (g1 != 0U) {
        a_num /= g1;
        b_den /= g1;
    }

    g2 = hhs219_gcd_u64(b_num, a_den);
    if (g2 != 0U) {
        b_num /= g2;
        a_den /= g2;
    }

    if (!hhs219_mul_u64(a_num, b_den, &left) ||
        !hhs219_mul_u64(b_num, a_den, &right))
        return 0;

    *out_le = left <= right ? 1 : 0;
    return 1;
}

static int hhs219_fraction_compare_lt(
    uint64_t a_num,
    uint64_t a_den,
    uint64_t b_num,
    uint64_t b_den,
    int *out_lt
) {
    uint64_t g1;
    uint64_t g2;
    uint64_t left;
    uint64_t right;

    if (out_lt == NULL || a_den == 0U || b_den == 0U)
        return 0;

    g1 = hhs219_gcd_u64(a_num, b_den);
    if (g1 != 0U) {
        a_num /= g1;
        b_den /= g1;
    }

    g2 = hhs219_gcd_u64(b_num, a_den);
    if (g2 != 0U) {
        b_num /= g2;
        a_den /= g2;
    }

    if (!hhs219_mul_u64(a_num, b_den, &left) ||
        !hhs219_mul_u64(b_num, a_den, &right))
        return 0;

    *out_lt = left < right ? 1 : 0;
    return 1;
}

uint32_t hhs_exact_pass219_holographic_harmonic_window_version(void) {
    return hhs219_holographic_version_word();
}

HHSExactStatus hhs_exact_pass219_holographic_harmonic_window_invariant(
    const HHSExactPass219HolographicWindowResiduesV1 *residues,
    HHSExactPass219HolographicWindowInvariantV1 *out_invariant
) {
    int64_t t_term;
    int64_t m_term;
    int64_t combined;
    uint64_t five_q;
    int positive_root;
    int negative_root;

    if (residues == NULL || out_invariant == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (residues->struct_size != sizeof(*residues) ||
        residues->version != hhs219_holographic_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (!hhs219_bool_u8(residues->exact_residue_witness) ||
        !hhs219_bool_u8(residues->canonical_authority_requested))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (residues->common_denominator == 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (residues->canonical_authority_requested != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (residues->common_denominator > (uint64_t)INT64_MAX / 5U)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    if (!hhs219_mul_i64_positive(
            residues->t3_minus_t_numerator,
            (int64_t)HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_B2,
            &t_term) ||
        !hhs219_mul_i64_positive(
            residues->m2_minus_m_numerator,
            (int64_t)(HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_A2 +
                      HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_B2),
            &m_term) ||
        !hhs219_add_i64(t_term, m_term, &combined))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    five_q = residues->common_denominator * 5U;
    positive_root =
        combined >= 0 && (uint64_t)combined == five_q;
    negative_root =
        combined < 0 &&
        combined != INT64_MIN &&
        (uint64_t)(-combined) == five_q;

    memset(out_invariant, 0, sizeof(*out_invariant));
    out_invariant->struct_size = (uint32_t)sizeof(*out_invariant);
    out_invariant->version = hhs219_holographic_version_word();
    out_invariant->combined_residue_numerator = combined;
    out_invariant->common_denominator = residues->common_denominator;
    out_invariant->ratio_numerator =
        HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_RATIO_NUMERATOR;
    out_invariant->ratio_denominator =
        HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_RATIO_DENOMINATOR;
    out_invariant->exact_residue_witness = residues->exact_residue_witness;
    out_invariant->positive_root = (uint8_t)(positive_root ? 1U : 0U);
    out_invariant->negative_root = (uint8_t)(negative_root ? 1U : 0U);
    out_invariant->harmonic_window_closed =
        (uint8_t)(residues->exact_residue_witness != 0U &&
                  (positive_root || negative_root) ? 1U : 0U);
    out_invariant->canonical_authority = 0U;
    out_invariant->floating_point_authority = 0U;
    out_invariant->singleton_vm81_authority_preserved = 1U;
    out_invariant->hash72_hash216_authority_preserved = 1U;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_holographic_harmonic_window_validate(void) {
    HHSExactPass219HolographicWindowResiduesV1 residues;
    HHSExactPass219HolographicWindowInvariantV1 invariant;
    uint64_t lhs;
    uint64_t rhs;

    memset(&residues, 0, sizeof(residues));
    residues.struct_size = (uint32_t)sizeof(residues);
    residues.version = hhs219_holographic_version_word();
    residues.t3_minus_t_numerator = 1;
    residues.m2_minus_m_numerator = 1;
    residues.common_denominator = 1U;
    residues.exact_residue_witness = 1U;

    if (hhs_exact_pass219_holographic_harmonic_window_invariant(
            &residues, &invariant) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (invariant.combined_residue_numerator != 5 ||
        invariant.common_denominator != 1U ||
        invariant.ratio_numerator != 25U ||
        invariant.ratio_denominator != 3U ||
        invariant.positive_root != 1U ||
        invariant.negative_root != 0U ||
        invariant.harmonic_window_closed != 1U ||
        invariant.canonical_authority != 0U ||
        invariant.floating_point_authority != 0U ||
        invariant.singleton_vm81_authority_preserved != 1U ||
        invariant.hash72_hash216_authority_preserved != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    /*
     * Exact cross-product proof:
     *
     * d^4/c^2 =
     * [b^2*T + (a^2+b^2)*M]^2 / (d^2-b^2)
     *
     * with T=M=1.
     */
    lhs =
        (uint64_t)HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_D2 *
        (uint64_t)HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_D2 *
        (uint64_t)(HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_D2 -
                   HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_B2);

    rhs =
        (uint64_t)HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_C2 *
        (uint64_t)invariant.combined_residue_numerator *
        (uint64_t)invariant.combined_residue_numerator;

    if (lhs != rhs || lhs != UINT64_C(75))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_holographic_branch_evaluate(
    const HHSExactPass219HolographicBranchRequestV1 *request,
    HHSExactPass219HolographicBranchResultV1 *out_result
) {
    HHSExactPass219HolographicWindowInvariantV1 invariant;
    uint64_t active_num;
    uint64_t active_den;
    int inside;

    if (request == NULL || out_result == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (request->struct_size != sizeof(*request) ||
        request->version != hhs219_holographic_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (!hhs219_bool_u8(request->include_upper_boundary))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (request->layer > HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_MAX_DEPTH ||
        request->root_window_denominator == 0U ||
        request->phase_coordinate_denominator == 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    if (hhs_exact_pass219_holographic_harmonic_window_invariant(
            &request->residues, &invariant) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (invariant.harmonic_window_closed != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs219_mul_u64(
            request->root_window_numerator,
            HHS219_HOLO_POW3[request->layer],
            &active_num) ||
        !hhs219_mul_u64(
            request->root_window_denominator,
            HHS219_HOLO_POW25[request->layer],
            &active_den))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    if (request->include_upper_boundary != 0U) {
        if (!hhs219_fraction_compare_le(
                request->phase_coordinate_numerator,
                request->phase_coordinate_denominator,
                active_num,
                active_den,
                &inside))
            return HHS_EXACT_STATUS_RANGE_ERROR;
    } else {
        if (!hhs219_fraction_compare_lt(
                request->phase_coordinate_numerator,
                request->phase_coordinate_denominator,
                active_num,
                active_den,
                &inside))
            return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (uint32_t)sizeof(*out_result);
    out_result->version = hhs219_holographic_version_word();
    out_result->layer = request->layer;
    out_result->decision =
        inside != 0
            ? HHS_EXACT_PASS219_HOLOGRAPHIC_BRANCH_THEN
            : HHS_EXACT_PASS219_HOLOGRAPHIC_BRANCH_ELSE;
    out_result->active_window_numerator = active_num;
    out_result->active_window_denominator = active_den;
    out_result->phase_coordinate_numerator =
        request->phase_coordinate_numerator;
    out_result->phase_coordinate_denominator =
        request->phase_coordinate_denominator;
    out_result->harmonic_window_closed = 1U;
    out_result->inside_active_window = (uint8_t)(inside ? 1U : 0U);
    out_result->direct_layer_addressed = 1U;
    out_result->recursion_stack_allocated = 0U;
    out_result->pointer_tree_traversal_required = 0U;
    out_result->bounded_fixed_width_branch_work = 1U;
    out_result->whole_path_depth_bounded = 1U;
    out_result->unbounded_depth_constant_time_claim = 0U;
    out_result->canonical_authority = 0U;
    out_result->floating_point_authority = 0U;
    out_result->complete_fallback_required_on_failure = 1U;

    return HHS_EXACT_STATUS_OK;
}
