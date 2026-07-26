static uint64_t uabs64(int64_t value) {
    if (value < 0) {
        return (uint64_t)(-(value + 1)) + UINT64_C(1);
    }
    return (uint64_t)value;
}

static uint64_t gcd_u64(uint64_t a, uint64_t b) {
    while (b != UINT64_C(0)) {
        const uint64_t next = a % b;
        a = b;
        b = next;
    }
    return a == UINT64_C(0) ? UINT64_C(1) : a;
}

static HHSLshpvsStatus safe_add_i64(int64_t a, int64_t b, int64_t *out) {
    if (out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
#if defined(__GNUC__) || defined(__clang__)
    if (__builtin_add_overflow(a, b, out)) {
        return HHS_LSHPVS_OVERFLOW;
    }
#else
    if ((b > 0 && a > INT64_MAX - b) || (b < 0 && a < INT64_MIN - b)) {
        return HHS_LSHPVS_OVERFLOW;
    }
    *out = a + b;
#endif
    return HHS_LSHPVS_OK;
}

static HHSLshpvsStatus safe_mul_i64(int64_t a, int64_t b, int64_t *out) {
    if (out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
#if defined(__GNUC__) || defined(__clang__)
    if (__builtin_mul_overflow(a, b, out)) {
        return HHS_LSHPVS_OVERFLOW;
    }
#else
    if (a == 0 || b == 0) {
        *out = 0;
        return HHS_LSHPVS_OK;
    }
    if (a == -1 && b == INT64_MIN) {
        return HHS_LSHPVS_OVERFLOW;
    }
    if (b == -1 && a == INT64_MIN) {
        return HHS_LSHPVS_OVERFLOW;
    }
    if (a > 0) {
        if ((b > 0 && a > INT64_MAX / b) || (b < 0 && b < INT64_MIN / a)) {
            return HHS_LSHPVS_OVERFLOW;
        }
    } else if ((b > 0 && a < INT64_MIN / b) ||
               (b < 0 && a < INT64_MAX / b)) {
        return HHS_LSHPVS_OVERFLOW;
    }
    *out = a * b;
#endif
    return HHS_LSHPVS_OK;
}

static HHSLshpvsStatus rat_normalize(HHSLshpvsRational *value) {
    uint64_t divisor;

    if (value == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    if (value->den == 0) {
        return HHS_LSHPVS_DIVIDE_BY_ZERO;
    }
    if (value->den < 0) {
        if (value->num == INT64_MIN || value->den == INT64_MIN) {
            return HHS_LSHPVS_OVERFLOW;
        }
        value->num = -value->num;
        value->den = -value->den;
    }

    divisor = gcd_u64(uabs64(value->num), uabs64(value->den));
    value->num /= (int64_t)divisor;
    value->den /= (int64_t)divisor;
    if (value->num == 0) {
        value->den = 1;
    }
    return HHS_LSHPVS_OK;
}

HHSLshpvsStatus hhs_lshpvs_rational_make(
    int64_t num,
    int64_t den,
    HHSLshpvsRational *out
) {
    if (out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    out->num = num;
    out->den = den;
    return rat_normalize(out);
}

static HHSLshpvsStatus rat_add(
    HHSLshpvsRational a,
    HHSLshpvsRational b,
    HHSLshpvsRational *out
) {
    const uint64_t common = gcd_u64((uint64_t)a.den, (uint64_t)b.den);
    const int64_t a_scale = b.den / (int64_t)common;
    const int64_t b_scale = a.den / (int64_t)common;
    int64_t left;
    int64_t right;
    HHSLshpvsStatus status;

    if (out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    status = safe_mul_i64(a.num, a_scale, &left);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = safe_mul_i64(b.num, b_scale, &right);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = safe_add_i64(left, right, &out->num);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = safe_mul_i64(a.den, a_scale, &out->den);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    return rat_normalize(out);
}

static HHSLshpvsStatus rat_neg(
    HHSLshpvsRational value,
    HHSLshpvsRational *out
) {
    if (out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    if (value.num == INT64_MIN) {
        return HHS_LSHPVS_OVERFLOW;
    }
    out->num = -value.num;
    out->den = value.den;
    return HHS_LSHPVS_OK;
}

static HHSLshpvsStatus rat_sub(
    HHSLshpvsRational a,
    HHSLshpvsRational b,
    HHSLshpvsRational *out
) {
    HHSLshpvsRational negative_b;
    HHSLshpvsStatus status = rat_neg(b, &negative_b);

    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    return rat_add(a, negative_b, out);
}

static HHSLshpvsStatus rat_mul(
    HHSLshpvsRational a,
    HHSLshpvsRational b,
    HHSLshpvsRational *out
) {
    const uint64_t left_cancel = gcd_u64(uabs64(a.num), (uint64_t)b.den);
    const uint64_t right_cancel = gcd_u64(uabs64(b.num), (uint64_t)a.den);
    HHSLshpvsStatus status;

    if (out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }

    a.num /= (int64_t)left_cancel;
    b.den /= (int64_t)left_cancel;
    b.num /= (int64_t)right_cancel;
    a.den /= (int64_t)right_cancel;

    status = safe_mul_i64(a.num, b.num, &out->num);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = safe_mul_i64(a.den, b.den, &out->den);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    return rat_normalize(out);
}

static HHSLshpvsStatus rat_div(
    HHSLshpvsRational a,
    HHSLshpvsRational b,
    HHSLshpvsRational *out
) {
    HHSLshpvsRational inverse;
    HHSLshpvsStatus status;

    if (b.num == 0) {
        return HHS_LSHPVS_DIVIDE_BY_ZERO;
    }
    inverse.num = b.den;
    inverse.den = b.num;
    status = rat_normalize(&inverse);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    return rat_mul(a, inverse, out);
}

static int rat_equal(HHSLshpvsRational a, HHSLshpvsRational b) {
    return a.num == b.num && a.den == b.den;
}

static HHSLshpvsComplex complex_zero(void) {
    const HHSLshpvsComplex value = {{0, 1}, {0, 1}};
    return value;
}

static HHSLshpvsComplex complex_one(void) {
    const HHSLshpvsComplex value = {{1, 1}, {0, 1}};
    return value;
}

static HHSLshpvsStatus complex_normalize(HHSLshpvsComplex *value) {
    HHSLshpvsStatus status;

    if (value == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    status = rat_normalize(&value->re);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    return rat_normalize(&value->im);
}

static HHSLshpvsStatus complex_add(
    HHSLshpvsComplex a,
    HHSLshpvsComplex b,
    HHSLshpvsComplex *out
) {
    HHSLshpvsStatus status = rat_add(a.re, b.re, &out->re);

    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    return rat_add(a.im, b.im, &out->im);
}

static HHSLshpvsStatus complex_neg(
    HHSLshpvsComplex value,
    HHSLshpvsComplex *out
) {
    HHSLshpvsStatus status = rat_neg(value.re, &out->re);

    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    return rat_neg(value.im, &out->im);
}

static HHSLshpvsStatus complex_sub(
    HHSLshpvsComplex a,
    HHSLshpvsComplex b,
    HHSLshpvsComplex *out
) {
    HHSLshpvsComplex negative_b;
    HHSLshpvsStatus status = complex_neg(b, &negative_b);

    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    return complex_add(a, negative_b, out);
}

static HHSLshpvsStatus complex_mul(
    HHSLshpvsComplex a,
    HHSLshpvsComplex b,
    HHSLshpvsComplex *out
) {
    HHSLshpvsRational ac;
    HHSLshpvsRational bd;
    HHSLshpvsRational ad;
    HHSLshpvsRational bc;
    HHSLshpvsStatus status;

    status = rat_mul(a.re, b.re, &ac);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_mul(a.im, b.im, &bd);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_mul(a.re, b.im, &ad);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_mul(a.im, b.re, &bc);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_sub(ac, bd, &out->re);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    return rat_add(ad, bc, &out->im);
}

static HHSLshpvsStatus complex_conjugate(
    HHSLshpvsComplex value,
    HHSLshpvsComplex *out
) {
    if (out == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    out->re = value.re;
    return rat_neg(value.im, &out->im);
}

static HHSLshpvsStatus complex_div(
    HHSLshpvsComplex a,
    HHSLshpvsComplex b,
    HHSLshpvsComplex *out
) {
    HHSLshpvsRational real_square;
    HHSLshpvsRational imag_square;
    HHSLshpvsRational denominator;
    HHSLshpvsComplex conjugate;
    HHSLshpvsComplex numerator;
    HHSLshpvsStatus status;

    status = rat_mul(b.re, b.re, &real_square);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_mul(b.im, b.im, &imag_square);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_add(real_square, imag_square, &denominator);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    if (denominator.num == 0) {
        return HHS_LSHPVS_DIVIDE_BY_ZERO;
    }
    status = complex_conjugate(b, &conjugate);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = complex_mul(a, conjugate, &numerator);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    status = rat_div(numerator.re, denominator, &out->re);
    if (status != HHS_LSHPVS_OK) {
        return status;
    }
    return rat_div(numerator.im, denominator, &out->im);
}

static int complex_equal(HHSLshpvsComplex a, HHSLshpvsComplex b) {
    return rat_equal(a.re, b.re) && rat_equal(a.im, b.im);
}
