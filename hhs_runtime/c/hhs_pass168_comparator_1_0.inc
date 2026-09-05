#include "hhs_pass168_comparator_1_0.h"

static HHSExactStatus hhs_pass168_cmp_mul(
    HHSPass168Rational a,
    HHSPass168Rational b,
    HHSPass168Rational *out
) {
    return hhs_pass168_rat_mul(a, b, out);
}

HHSExactStatus hhs_pass168_compare_rational(
    HHSPass168Rational left_gain,
    HHSPass168Rational left_value,
    HHSPass168Rational right_gain,
    HHSPass168Rational right_value,
    HHSPass168Rational *out_shadow
) {
    HHSPass168Rational left;
    HHSPass168Rational right;
    HHSExactStatus status;
    if (out_shadow == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_pass168_cmp_mul(left_gain, left_value, &left);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_pass168_cmp_mul(right_gain, right_value, &right);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_pass168_rat_sub(left, right, out_shadow);
}

HHSExactStatus hhs_pass168_compare_matrix(
    HHSPass168Rational left_gain,
    const HHSPass168Matrix3 *left_value,
    HHSPass168Rational right_gain,
    const HHSPass168Matrix3 *right_value,
    HHSPass168Matrix3 *out_shadow
) {
    HHSPass168Matrix3 left;
    HHSPass168Matrix3 right;
    HHSExactStatus status;
    if (left_value == NULL || right_value == NULL || out_shadow == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_pass168_matrix_scale(left_value, left_gain, &left);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_pass168_matrix_scale(right_value, right_gain, &right);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_pass168_matrix_sub(&left, &right, out_shadow);
}

static int hhs_pass168_cmp_zero_matrix(const HHSPass168Matrix3 *matrix) {
    size_t i;
    if (matrix == NULL)
        return 0;
    for (i = 0U; i < 9U; ++i)
        if (matrix->v[i].numerator != 0 || matrix->v[i].denominator != 1U)
            return 0;
    return 1;
}

HHSExactStatus hhs_pass168_comparator_conformance(uint32_t *out_verified_count) {
    HHSPass168Rational shadow;
    HHSPass168Matrix3 loshu;
    HHSPass168Matrix3 upper;
    HHSPass168Matrix3 lower;
    HHSPass168Matrix3 matrix_shadow;
    HHSPass168Rational one = {1, 1U};
    HHSPass168Rational zero = {0, 1U};
    HHSPass168Rational two = {2, 1U};
    HHSPass168Rational three = {3, 1U};
    uint32_t comparator_id;
    HHSExactStatus status;
    if (out_verified_count == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_verified_count = 0U;

    for (comparator_id = 1U; comparator_id <= 6U; ++comparator_id) {
        status = hhs_pass168_compare_rational(one, three, one, three, &shadow);
        if (status != HHS_EXACT_STATUS_OK || !hhs_pass168_rat_equal(shadow, zero))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        status = hhs_pass168_compare_rational(two, three, two, three, &shadow);
        if (status != HHS_EXACT_STATUS_OK || !hhs_pass168_rat_equal(shadow, zero))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        status = hhs_pass168_compare_rational(one, three, zero, three, &shadow);
        if (status != HHS_EXACT_STATUS_OK || !hhs_pass168_rat_equal(shadow, three))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        status = hhs_pass168_compare_rational(zero, three, one, three, &shadow);
        if (status != HHS_EXACT_STATUS_OK || !hhs_pass168_rat_equal(shadow, (HHSPass168Rational){-3,1U}))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        status = hhs_pass168_compare_rational(one, three, (HHSPass168Rational){-1,1U}, three, &shadow);
        if (status != HHS_EXACT_STATUS_OK || !hhs_pass168_rat_equal(shadow, (HHSPass168Rational){6,1U}))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        status = hhs_pass168_compare_rational((HHSPass168Rational){360,1U}, (HHSPass168Rational){361,1U},
                                              (HHSPass168Rational){361,1U}, (HHSPass168Rational){360,1U}, &shadow);
        if (status != HHS_EXACT_STATUS_OK || !hhs_pass168_rat_equal(shadow, zero))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        ++(*out_verified_count);
    }

    hhs_pass168_matrix_loshu(&loshu);
    status = hhs_pass168_matrix_scale(&loshu, (HHSPass168Rational){361,1U}, &upper);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_pass168_matrix_scale(&loshu, (HHSPass168Rational){360,1U}, &lower);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_pass168_compare_matrix(
        (HHSPass168Rational){360,1U}, &upper,
        (HHSPass168Rational){361,1U}, &lower,
        &matrix_shadow);
    if (status != HHS_EXACT_STATUS_OK || !hhs_pass168_cmp_zero_matrix(&matrix_shadow))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return *out_verified_count == 6U ? HHS_EXACT_STATUS_OK : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}
