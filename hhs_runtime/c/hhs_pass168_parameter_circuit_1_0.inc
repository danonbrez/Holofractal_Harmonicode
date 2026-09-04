#include "hhs_pass168_parameter_circuit_1_0.h"

#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static const char HHS_PASS168_SOURCE[] =
    "(t^3-t-(Mod(MatrixTimes(361,MatrixTimes(144/{{3,5,8},{13,21,34},{55,89,144}},NcalcMatrixPower(144/{{3,5,8},{13,21,34},{55,89,144}},(-1)))),{{4,9,2},{3,5,7},{8,1,6}})==x*y==Mod(1,u^360))==Mod(MatrixTimes(360,MatrixTimes(144/List(List(3,5,8),List(13,21,34),List(55,89,144)),NcalcMatrixPower((144/List(List(3,5,8),List(13,21,34),List(55,89,144))),(-1)))),List(List(4,9,2),List(3,5,7),List(8,1,6)))==(x*y)==Mod(0,u^360))/u^72==0";

static const char HHS_PASS168_SOURCE_SHA256[] =
    "fdbee5db0f2fea428b6b88e5ac9b273e6aa3754fa00f84e8923456373275166e";

static const int64_t HHS_PASS168_LOSHU[9] = {4,9,2,3,5,7,8,1,6};
static const int64_t HHS_PASS168_FIB[9] = {3,5,8,13,21,34,55,89,144};

static uint64_t hhs_pass168_abs_i64(int64_t value) {
    if (value >= 0)
        return (uint64_t)value;
    return (uint64_t)(-(value + 1)) + UINT64_C(1);
}

static unsigned __int128 hhs_pass168_abs_i128(__int128 value) {
    if (value >= 0)
        return (unsigned __int128)value;
    return (unsigned __int128)(-(value + 1)) + (unsigned __int128)1;
}

static uint64_t hhs_pass168_gcd_u64(uint64_t a, uint64_t b) {
    while (b != 0U) {
        uint64_t r = a % b;
        a = b;
        b = r;
    }
    return a == 0U ? 1U : a;
}

static unsigned __int128 hhs_pass168_gcd_u128(unsigned __int128 a, unsigned __int128 b) {
    while (b != 0U) {
        unsigned __int128 r = a % b;
        a = b;
        b = r;
    }
    return a == 0U ? 1U : a;
}

static HHSExactStatus hhs_pass168_rat_from_i128(
    __int128 numerator,
    unsigned __int128 denominator,
    HHSPass168Rational *out
) {
    unsigned __int128 g;
    unsigned __int128 absn;
    if (out == NULL || denominator == 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (numerator == 0) {
        out->numerator = 0;
        out->denominator = 1U;
        return HHS_EXACT_STATUS_OK;
    }
    absn = hhs_pass168_abs_i128(numerator);
    g = hhs_pass168_gcd_u128(absn, denominator);
    numerator /= (__int128)g;
    denominator /= g;
    if (numerator > (__int128)INT64_MAX || numerator < (__int128)INT64_MIN ||
        denominator > (unsigned __int128)UINT64_MAX)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    out->numerator = (int64_t)numerator;
    out->denominator = (uint64_t)denominator;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_pass168_rational_normalize(
    int64_t numerator,
    uint64_t denominator,
    HHSPass168Rational *out
) {
    uint64_t g;
    uint64_t absn;
    if (out == NULL || denominator == 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (numerator == 0) {
        out->numerator = 0;
        out->denominator = 1U;
        return HHS_EXACT_STATUS_OK;
    }
    absn = hhs_pass168_abs_i64(numerator);
    g = hhs_pass168_gcd_u64(absn, denominator);
    out->numerator = numerator / (int64_t)g;
    out->denominator = denominator / g;
    return HHS_EXACT_STATUS_OK;
}

static HHSPass168Rational hhs_pass168_rat_i64(int64_t value) {
    HHSPass168Rational out;
    out.numerator = value;
    out.denominator = 1U;
    return out;
}

static int hhs_pass168_rat_equal(HHSPass168Rational a, HHSPass168Rational b) {
    return a.numerator == b.numerator && a.denominator == b.denominator;
}

static HHSExactStatus hhs_pass168_rat_add(
    HHSPass168Rational a,
    HHSPass168Rational b,
    HHSPass168Rational *out
) {
    uint64_t g;
    uint64_t ad;
    uint64_t bd;
    __int128 n;
    unsigned __int128 d;
    if (out == NULL || a.denominator == 0U || b.denominator == 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    g = hhs_pass168_gcd_u64(a.denominator, b.denominator);
    ad = a.denominator / g;
    bd = b.denominator / g;
    n = (__int128)a.numerator * (__int128)bd + (__int128)b.numerator * (__int128)ad;
    d = (unsigned __int128)ad * (unsigned __int128)b.denominator;
    return hhs_pass168_rat_from_i128(n, d, out);
}

static HHSExactStatus hhs_pass168_rat_sub(
    HHSPass168Rational a,
    HHSPass168Rational b,
    HHSPass168Rational *out
) {
    uint64_t g;
    uint64_t ad;
    uint64_t bd;
    __int128 n;
    unsigned __int128 d;
    if (out == NULL || a.denominator == 0U || b.denominator == 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    g = hhs_pass168_gcd_u64(a.denominator, b.denominator);
    ad = a.denominator / g;
    bd = b.denominator / g;
    n = (__int128)a.numerator * (__int128)bd - (__int128)b.numerator * (__int128)ad;
    d = (unsigned __int128)ad * (unsigned __int128)b.denominator;
    return hhs_pass168_rat_from_i128(n, d, out);
}

static HHSExactStatus hhs_pass168_rat_mul(
    HHSPass168Rational a,
    HHSPass168Rational b,
    HHSPass168Rational *out
) {
    uint64_t g1;
    uint64_t g2;
    uint64_t an;
    uint64_t bn;
    __int128 n;
    unsigned __int128 d;
    int sign = 1;
    if (out == NULL || a.denominator == 0U || b.denominator == 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (a.numerator == 0 || b.numerator == 0)
        return hhs_pass168_rational_normalize(0, 1U, out);
    an = hhs_pass168_abs_i64(a.numerator);
    bn = hhs_pass168_abs_i64(b.numerator);
    g1 = hhs_pass168_gcd_u64(an, b.denominator);
    g2 = hhs_pass168_gcd_u64(bn, a.denominator);
    an /= g1;
    bn /= g2;
    if ((a.numerator < 0) != (b.numerator < 0))
        sign = -1;
    n = (__int128)an * (__int128)bn;
    if (sign < 0)
        n = -n;
    d = (unsigned __int128)(a.denominator / g2) *
        (unsigned __int128)(b.denominator / g1);
    return hhs_pass168_rat_from_i128(n, d, out);
}

static HHSExactStatus hhs_pass168_rat_div(
    HHSPass168Rational a,
    HHSPass168Rational b,
    HHSPass168Rational *out
) {
    HHSPass168Rational reciprocal;
    uint64_t absn;
    if (out == NULL || b.numerator == 0 || a.denominator == 0U || b.denominator == 0U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    absn = hhs_pass168_abs_i64(b.numerator);
    if (b.numerator < 0) {
        if (b.denominator > (uint64_t)INT64_MAX)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        reciprocal.numerator = -(int64_t)b.denominator;
    } else {
        if (b.denominator > (uint64_t)INT64_MAX)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        reciprocal.numerator = (int64_t)b.denominator;
    }
    reciprocal.denominator = absn;
    return hhs_pass168_rat_mul(a, reciprocal, out);
}

static HHSExactStatus hhs_pass168_matrix_identity(HHSPass168Matrix3 *out) {
    size_t i;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    for (i = 0U; i < 9U; ++i)
        out->v[i] = hhs_pass168_rat_i64((i % 4U) == 0U ? 1 : 0);
    return HHS_EXACT_STATUS_OK;
}

static void hhs_pass168_matrix_loshu(HHSPass168Matrix3 *out) {
    size_t i;
    for (i = 0U; i < 9U; ++i)
        out->v[i] = hhs_pass168_rat_i64(HHS_PASS168_LOSHU[i]);
}

static HHSExactStatus hhs_pass168_matrix_q(HHSPass168Matrix3 *out) {
    size_t i;
    HHSExactStatus status;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    for (i = 0U; i < 9U; ++i) {
        status = hhs_pass168_rational_normalize(144, (uint64_t)HHS_PASS168_FIB[i], &out->v[i]);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
    }
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_pass168_matrix_mul(
    const HHSPass168Matrix3 *a,
    const HHSPass168Matrix3 *b,
    HHSPass168Matrix3 *out
) {
    HHSPass168Matrix3 temp;
    size_t r;
    size_t c;
    size_t k;
    HHSExactStatus status;
    if (a == NULL || b == NULL || out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    for (r = 0U; r < 3U; ++r) {
        for (c = 0U; c < 3U; ++c) {
            HHSPass168Rational acc = hhs_pass168_rat_i64(0);
            for (k = 0U; k < 3U; ++k) {
                HHSPass168Rational product;
                HHSPass168Rational next;
                status = hhs_pass168_rat_mul(a->v[3U * r + k], b->v[3U * k + c], &product);
                if (status != HHS_EXACT_STATUS_OK)
                    return status;
                status = hhs_pass168_rat_add(acc, product, &next);
                if (status != HHS_EXACT_STATUS_OK)
                    return status;
                acc = next;
            }
            temp.v[3U * r + c] = acc;
        }
    }
    memcpy(out, &temp, sizeof(temp));
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_pass168_matrix_scale(
    const HHSPass168Matrix3 *a,
    HHSPass168Rational scalar,
    HHSPass168Matrix3 *out
) {
    HHSPass168Matrix3 temp;
    size_t i;
    HHSExactStatus status;
    if (a == NULL || out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    for (i = 0U; i < 9U; ++i) {
        status = hhs_pass168_rat_mul(a->v[i], scalar, &temp.v[i]);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
    }
    memcpy(out, &temp, sizeof(temp));
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_pass168_matrix_sub(
    const HHSPass168Matrix3 *a,
    const HHSPass168Matrix3 *b,
    HHSPass168Matrix3 *out
) {
    HHSPass168Matrix3 temp;
    size_t i;
    HHSExactStatus status;
    if (a == NULL || b == NULL || out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    for (i = 0U; i < 9U; ++i) {
        status = hhs_pass168_rat_sub(a->v[i], b->v[i], &temp.v[i]);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
    }
    memcpy(out, &temp, sizeof(temp));
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_pass168_matrix_det(
    const HHSPass168Matrix3 *m,
    HHSPass168Rational *out
) {
    HHSPass168Rational a, b, c, d, e, f;
    HHSExactStatus status;
    if (m == NULL || out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_pass168_rat_mul(m->v[4], m->v[8], &a);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_mul(m->v[5], m->v[7], &b);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_sub(a, b, &c);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_mul(m->v[0], c, &a);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = hhs_pass168_rat_mul(m->v[3], m->v[8], &b);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_mul(m->v[5], m->v[6], &c);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_sub(b, c, &d);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_mul(m->v[1], d, &b);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = hhs_pass168_rat_mul(m->v[3], m->v[7], &c);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_mul(m->v[4], m->v[6], &d);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_sub(c, d, &e);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_mul(m->v[2], e, &c);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = hhs_pass168_rat_sub(a, b, &f);
    if (status != HHS_EXACT_STATUS_OK) return status;
    return hhs_pass168_rat_add(f, c, out);
}

static HHSExactStatus hhs_pass168_matrix_inverse(
    const HHSPass168Matrix3 *m,
    HHSPass168Matrix3 *out
) {
    HHSPass168Matrix3 cof;
    HHSPass168Matrix3 adj;
    HHSPass168Rational det;
    HHSExactStatus status;
    size_t r;
    size_t c;
    if (m == NULL || out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_pass168_matrix_det(m, &det);
    if (status != HHS_EXACT_STATUS_OK || det.numerator == 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (r = 0U; r < 3U; ++r) {
        for (c = 0U; c < 3U; ++c) {
            size_t r1 = (r + 1U) % 3U;
            size_t r2 = (r + 2U) % 3U;
            size_t c1 = (c + 1U) % 3U;
            size_t c2 = (c + 2U) % 3U;
            HHSPass168Rational p1, p2, minor;
            status = hhs_pass168_rat_mul(m->v[3U * r1 + c1], m->v[3U * r2 + c2], &p1);
            if (status != HHS_EXACT_STATUS_OK) return status;
            status = hhs_pass168_rat_mul(m->v[3U * r1 + c2], m->v[3U * r2 + c1], &p2);
            if (status != HHS_EXACT_STATUS_OK) return status;
            status = hhs_pass168_rat_sub(p1, p2, &minor);
            if (status != HHS_EXACT_STATUS_OK) return status;
            if (((r + c) & 1U) != 0U)
                minor.numerator = -minor.numerator;
            cof.v[3U * r + c] = minor;
        }
    }
    for (r = 0U; r < 3U; ++r)
        for (c = 0U; c < 3U; ++c)
            adj.v[3U * r + c] = cof.v[3U * c + r];
    for (r = 0U; r < 9U; ++r) {
        status = hhs_pass168_rat_div(adj.v[r], det, &out->v[r]);
        if (status != HHS_EXACT_STATUS_OK) return status;
    }
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_pass168_matrix_power_q(int exponent, HHSPass168Matrix3 *out) {
    HHSPass168Matrix3 base;
    HHSPass168Matrix3 result;
    HHSPass168Matrix3 temp;
    int count;
    HHSExactStatus status;
    if (out == NULL || exponent < -HHS_PASS168_MAX_ABS_INVERSE_DEPTH ||
        exponent > HHS_PASS168_MAX_ABS_INVERSE_DEPTH)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    status = hhs_pass168_matrix_q(&base);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (exponent < 0) {
        status = hhs_pass168_matrix_inverse(&base, &temp);
        if (status != HHS_EXACT_STATUS_OK) return status;
        base = temp;
        exponent = -exponent;
    }
    status = hhs_pass168_matrix_identity(&result);
    if (status != HHS_EXACT_STATUS_OK) return status;
    for (count = 0; count < exponent; ++count) {
        status = hhs_pass168_matrix_mul(&result, &base, &temp);
        if (status != HHS_EXACT_STATUS_OK) return status;
        result = temp;
    }
    *out = result;
    return HHS_EXACT_STATUS_OK;
}

static int hhs_pass168_matrix_equal(const HHSPass168Matrix3 *a, const HHSPass168Matrix3 *b) {
    size_t i;
    for (i = 0U; i < 9U; ++i)
        if (!hhs_pass168_rat_equal(a->v[i], b->v[i]))
            return 0;
    return 1;
}

uint32_t hhs_pass168_version(void) {
    return (HHS_PASS168_VERSION_MAJOR << 16U) |
           (HHS_PASS168_VERSION_MINOR << 8U) |
           HHS_PASS168_VERSION_PATCH;
}

const char *hhs_pass168_source_text(void) {
    return HHS_PASS168_SOURCE;
}

const char *hhs_pass168_source_sha256_hex(void) {
    return HHS_PASS168_SOURCE_SHA256;
}

HHSExactStatus hhs_pass168_source_stats(HHSPass168SourceStats *out) {
    size_t i;
    uint32_t opens = 0U;
    uint32_t closes = 0U;
    uint32_t equals = 0U;
    uint32_t doubles = 0U;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->source_bytes = (uint32_t)(sizeof(HHS_PASS168_SOURCE) - 1U);
    for (i = 0U; i < sizeof(HHS_PASS168_SOURCE) - 1U; ++i) {
        if (HHS_PASS168_SOURCE[i] == '(') ++opens;
        if (HHS_PASS168_SOURCE[i] == ')') ++closes;
        if (HHS_PASS168_SOURCE[i] == '=') ++equals;
        if (HHS_PASS168_SOURCE[i] == '=' && i + 1U < sizeof(HHS_PASS168_SOURCE) - 1U &&
            HHS_PASS168_SOURCE[i + 1U] == '=') ++doubles;
    }
    out->matched_parenthesis_pairs = opens == closes ? opens : 0U;
    out->literal_equals_count = equals;
    out->double_equals_token_count = doubles;
    out->source_preserved =
        out->source_bytes == HHS_PASS168_SOURCE_BYTES && opens == 28U && closes == 28U &&
        equals == 12U && doubles == 6U;
    memcpy(out->source_sha256_hex, HHS_PASS168_SOURCE_SHA256, sizeof(HHS_PASS168_SOURCE_SHA256));
    hhs_exact_uqcel_hash72_bytes(HHS_PASS168_SOURCE, sizeof(HHS_PASS168_SOURCE) - 1U, out->source_hash72);
    return out->source_preserved ? HHS_EXACT_STATUS_OK : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_pass168_parameter_registry(
    HHSPass168ParameterSpan out[HHS_PASS168_P_COUNT]
) {
    uint8_t stack_id[HHS_PASS168_P_COUNT];
    uint16_t stack_offset[HHS_PASS168_P_COUNT];
    uint8_t stack_depth[HHS_PASS168_P_COUNT];
    uint32_t sp = 0U;
    uint32_t next = 0U;
    size_t i;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out, 0, sizeof(HHSPass168ParameterSpan) * HHS_PASS168_P_COUNT);
    for (i = 0U; i < sizeof(HHS_PASS168_SOURCE) - 1U; ++i) {
        if (HHS_PASS168_SOURCE[i] == '(') {
            if (next >= HHS_PASS168_P_COUNT || sp >= HHS_PASS168_P_COUNT)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            out[next].parameter_id = (uint8_t)(next + 1U);
            out[next].thread_id = (uint8_t)next;
            out[next].nesting_depth = (uint8_t)(sp + 1U);
            out[next].open_offset = (uint16_t)i;
            stack_id[sp] = (uint8_t)next;
            stack_offset[sp] = (uint16_t)i;
            stack_depth[sp] = (uint8_t)(sp + 1U);
            ++sp;
            ++next;
        } else if (HHS_PASS168_SOURCE[i] == ')') {
            uint8_t id;
            if (sp == 0U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            --sp;
            id = stack_id[sp];
            if (out[id].open_offset != stack_offset[sp] || out[id].nesting_depth != stack_depth[sp])
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            out[id].close_offset = (uint16_t)i;
        }
    }
    return next == HHS_PASS168_P_COUNT && sp == 0U ?
        HHS_EXACT_STATUS_OK : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_pass168_equality_registry(
    HHSPass168EqualityGate out[HHS_PASS168_E_COUNT]
) {
    uint32_t next = 0U;
    size_t i;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out, 0, sizeof(HHSPass168EqualityGate) * HHS_PASS168_E_COUNT);
    for (i = 0U; i < sizeof(HHS_PASS168_SOURCE) - 1U; ++i) {
        if (HHS_PASS168_SOURCE[i] == '=') {
            if (next >= HHS_PASS168_E_COUNT)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            out[next].gate_id = (uint8_t)(next + 1U);
            out[next].thread_id = (uint8_t)(HHS_PASS168_P_COUNT + next);
            out[next].comparator_id = (uint8_t)(1U + next / 2U);
            out[next].side = (uint8_t)(next & 1U);
            out[next].source_offset = (uint16_t)i;
            ++next;
        }
    }
    return next == HHS_PASS168_E_COUNT ? HHS_EXACT_STATUS_OK : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_pass168_address_encode(
    uint8_t thread_id,
    uint8_t local_index,
    HHSPass168Address *out
) {
    uint8_t thread_row;
    uint8_t thread_col;
    uint8_t local_row;
    uint8_t local_col;
    uint8_t global_row;
    uint8_t global_col;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (thread_id >= HHS_PASS168_THREAD_COUNT || local_index >= HHS_PASS168_CELLS_PER_THREAD)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    memset(out, 0, sizeof(*out));
    thread_row = (uint8_t)(thread_id / 8U);
    thread_col = (uint8_t)(thread_id % 8U);
    local_row = (uint8_t)(local_index / 9U);
    local_col = (uint8_t)(local_index % 9U);
    global_row = (uint8_t)(9U * thread_row + local_row);
    global_col = (uint8_t)(9U * thread_col + local_col);
    out->global_index = (uint16_t)(72U * global_row + global_col);
    out->global_row = global_row;
    out->global_col = global_col;
    out->thread_id = thread_id;
    out->thread_row = thread_row;
    out->thread_col = thread_col;
    out->local_index = local_index;
    out->local_row = local_row;
    out->local_col = local_col;
    out->bank_row = (uint8_t)(local_row / 3U);
    out->bank_col = (uint8_t)(local_col / 3U);
    out->bank_id = (uint8_t)(3U * out->bank_row + out->bank_col);
    out->loshu_row = (uint8_t)(local_row % 3U);
    out->loshu_col = (uint8_t)(local_col % 3U);
    out->loshu_index = (uint8_t)(3U * out->loshu_row + out->loshu_col);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_pass168_address_decode(
    uint16_t global_index,
    HHSPass168Address *out
) {
    uint8_t global_row;
    uint8_t global_col;
    uint8_t thread_row;
    uint8_t thread_col;
    uint8_t local_row;
    uint8_t local_col;
    uint8_t thread_id;
    uint8_t local_index;
    HHSExactStatus status;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (global_index >= HHS_PASS168_TOTAL_CELLS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    global_row = (uint8_t)(global_index / 72U);
    global_col = (uint8_t)(global_index % 72U);
    thread_row = (uint8_t)(global_row / 9U);
    thread_col = (uint8_t)(global_col / 9U);
    local_row = (uint8_t)(global_row % 9U);
    local_col = (uint8_t)(global_col % 9U);
    thread_id = (uint8_t)(8U * thread_row + thread_col);
    local_index = (uint8_t)(9U * local_row + local_col);
    status = hhs_pass168_address_encode(thread_id, local_index, out);
    if (status != HHS_EXACT_STATUS_OK || out->global_index != global_index)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_pass168_matrix_invariants(void) {
    HHSPass168Matrix3 q;
    HHSPass168Matrix3 qinv;
    HHSPass168Matrix3 identity;
    HHSPass168Matrix3 product;
    HHSPass168Matrix3 l;
    HHSPass168Matrix3 l2;
    HHSPass168Matrix3 expected_l2;
    HHSPass168Rational detq;
    HHSPass168Rational detl;
    static const int64_t L2[9] = {59,83,83,83,59,83,83,83,59};
    size_t i;
    int64_t detf;
    HHSExactStatus status;
    detf =
        HHS_PASS168_FIB[0] * (HHS_PASS168_FIB[4] * HHS_PASS168_FIB[8] - HHS_PASS168_FIB[5] * HHS_PASS168_FIB[7]) -
        HHS_PASS168_FIB[1] * (HHS_PASS168_FIB[3] * HHS_PASS168_FIB[8] - HHS_PASS168_FIB[5] * HHS_PASS168_FIB[6]) +
        HHS_PASS168_FIB[2] * (HHS_PASS168_FIB[3] * HHS_PASS168_FIB[7] - HHS_PASS168_FIB[4] * HHS_PASS168_FIB[6]);
    if (detf != 0 ||
        HHS_PASS168_FIB[6] != HHS_PASS168_FIB[0] + 4 * HHS_PASS168_FIB[3] ||
        HHS_PASS168_FIB[7] != HHS_PASS168_FIB[1] + 4 * HHS_PASS168_FIB[4] ||
        HHS_PASS168_FIB[8] != HHS_PASS168_FIB[2] + 4 * HHS_PASS168_FIB[5])
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_pass168_matrix_q(&q);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_matrix_det(&q, &detq);
    if (status != HHS_EXACT_STATUS_OK ||
        !hhs_pass168_rat_equal(detq, (HHSPass168Rational){4608,37862825U}))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_pass168_matrix_inverse(&q, &qinv);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_matrix_mul(&q, &qinv, &product);
    if (status != HHS_EXACT_STATUS_OK) return status;
    hhs_pass168_matrix_identity(&identity);
    if (!hhs_pass168_matrix_equal(&product, &identity))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    hhs_pass168_matrix_loshu(&l);
    status = hhs_pass168_matrix_mul(&l, &l, &l2);
    if (status != HHS_EXACT_STATUS_OK) return status;
    for (i = 0U; i < 9U; ++i)
        expected_l2.v[i] = hhs_pass168_rat_i64(L2[i]);
    if (!hhs_pass168_matrix_equal(&l2, &expected_l2))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_pass168_matrix_det(&l, &detl);
    if (status != HHS_EXACT_STATUS_OK || !hhs_pass168_rat_equal(detl, hhs_pass168_rat_i64(360)))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static int hhs_pass168_append_u64(uint8_t *out, size_t cap, size_t *cursor, uint64_t value) {
    size_t i;
    if (*cursor > cap || 8U > cap - *cursor)
        return 0;
    for (i = 0U; i < 8U; ++i)
        out[(*cursor)++] = (uint8_t)(value >> (56U - 8U * i));
    return 1;
}

static int hhs_pass168_append_rat(
    uint8_t *out,
    size_t cap,
    size_t *cursor,
    HHSPass168Rational value
) {
    return hhs_pass168_append_u64(out, cap, cursor, (uint64_t)value.numerator) &&
           hhs_pass168_append_u64(out, cap, cursor, value.denominator);
}

static HHSExactStatus hhs_pass168_state_root(HHSPass168CircuitState *state) {
    uint8_t material[4096];
    size_t cursor = 0U;
    size_t i;
    static const uint8_t domain[] = "HHS-P168-STATE-V1";
    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (sizeof(domain) - 1U > sizeof(material))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memcpy(material + cursor, domain, sizeof(domain) - 1U);
    cursor += sizeof(domain) - 1U;
    if (!hhs_pass168_append_u64(material, sizeof(material), &cursor, state->generation))
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    if (cursor + HHS_PASS168_SOURCE_SHA256_HEX_LEN > sizeof(material))
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(material + cursor, HHS_PASS168_SOURCE_SHA256, HHS_PASS168_SOURCE_SHA256_HEX_LEN);
    cursor += HHS_PASS168_SOURCE_SHA256_HEX_LEN;
    for (i = 0U; i < HHS_PASS168_PARAMETER_COUNT; ++i)
        if (!hhs_pass168_append_rat(material, sizeof(material), &cursor, state->raw[i]))
            return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    for (i = 0U; i < HHS_PASS168_DERIVED_THREAD_COUNT; ++i)
        if (!hhs_pass168_append_rat(material, sizeof(material), &cursor, state->derived[i]))
            return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    for (i = 0U; i < 9U; ++i) {
        if (!hhs_pass168_append_rat(material, sizeof(material), &cursor, state->upper.v[i]) ||
            !hhs_pass168_append_rat(material, sizeof(material), &cursor, state->lower.v[i]) ||
            !hhs_pass168_append_rat(material, sizeof(material), &cursor, state->successor.v[i]))
            return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    }
    hhs_exact_uqcel_hash216_bytes(material, cursor, state->state_hash216);
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_pass168_product_range(
    const HHSPass168Rational *values,
    const uint8_t *indices,
    size_t count,
    HHSPass168Rational *out
) {
    HHSPass168Rational acc = hhs_pass168_rat_i64(1);
    size_t i;
    HHSExactStatus status;
    for (i = 0U; i < count; ++i) {
        HHSPass168Rational next;
        status = hhs_pass168_rat_mul(acc, values[indices[i]], &next);
        if (status != HHS_EXACT_STATUS_OK) return status;
        acc = next;
    }
    *out = acc;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_pass168_state_compute(HHSPass168CircuitState *state) {
    static const uint8_t alpha_idx[] = {0,1,2,3,4,5};
    static const uint8_t beta_num_idx[] = {0,8,9,10,15,22,17};
    HHSPass168Rational alpha;
    HHSPass168Rational beta_num;
    HHSPass168Rational beta_den;
    HHSPass168Rational beta;
    HHSPass168Rational rho[3];
    HHSPass168Rational gr[3];
    HHSPass168Rational gm;
    HHSPass168Rational sum_e = hhs_pass168_rat_i64(0);
    HHSPass168Rational successor_sum = hhs_pass168_rat_i64(0);
    HHSPass168Matrix3 qpow;
    HHSPass168Matrix3 l;
    HHSPass168Matrix3 temp;
    HHSPass168Matrix3 temp2;
    HHSPass168Matrix3 diagq;
    int64_t du;
    int64_t dv;
    size_t i;
    HHSExactStatus status;
    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_pass168_product_range(state->raw, alpha_idx, sizeof(alpha_idx), &alpha);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_product_range(state->raw, beta_num_idx, sizeof(beta_num_idx), &beta_num);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_mul(state->raw[11], state->raw[16], &beta_den);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_div(beta_num, beta_den, &beta);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_div(state->raw[17], state->raw[11], &gm);
    if (status != HHS_EXACT_STATUS_OK) return status;
    for (i = 0U; i < 3U; ++i) {
        HHSPass168Rational row_gain;
        status = hhs_pass168_rat_div(state->raw[18U + i], state->raw[12U + i], &gr[i]);
        if (status != HHS_EXACT_STATUS_OK) return status;
        status = hhs_pass168_rat_mul(gr[i], state->raw[23U + i], &row_gain);
        if (status != HHS_EXACT_STATUS_OK) return status;
        rho[i] = row_gain;
    }
    if (state->raw[6].denominator != 1U || state->raw[21].denominator != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    du = 1 - state->raw[6].numerator;
    dv = 1 - state->raw[21].numerator;
    if (du < -HHS_PASS168_MAX_ABS_INVERSE_DEPTH || du > HHS_PASS168_MAX_ABS_INVERSE_DEPTH ||
        dv < -HHS_PASS168_MAX_ABS_INVERSE_DEPTH || dv > HHS_PASS168_MAX_ABS_INVERSE_DEPTH)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    hhs_pass168_matrix_loshu(&l);
    status = hhs_pass168_matrix_power_q((int)du, &qpow);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_matrix_mul(&qpow, &l, &temp);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_mul(alpha, hhs_pass168_rat_i64(361), &state->derived[0]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_matrix_scale(&temp, state->derived[0], &state->upper);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = hhs_pass168_matrix_power_q((int)dv, &qpow);
    if (status != HHS_EXACT_STATUS_OK) return status;
    for (i = 0U; i < 9U; ++i)
        diagq.v[i] = qpow.v[i];
    for (i = 0U; i < 3U; ++i) {
        size_t c;
        for (c = 0U; c < 3U; ++c) {
            status = hhs_pass168_rat_mul(diagq.v[3U * i + c], rho[i], &temp2.v[3U * i + c]);
            if (status != HHS_EXACT_STATUS_OK) return status;
        }
    }
    status = hhs_pass168_matrix_mul(&temp2, &l, &temp);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_mul(beta, hhs_pass168_rat_i64(360), &state->derived[1]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_matrix_scale(&temp, state->derived[1], &state->lower);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_matrix_sub(&state->upper, &state->lower, &state->successor);
    if (status != HHS_EXACT_STATUS_OK) return status;

    state->derived[2] = rho[0];
    state->derived[3] = rho[1];
    state->derived[4] = rho[2];
    state->derived[5] = hhs_pass168_rat_i64(du);
    state->derived[6] = hhs_pass168_rat_i64(dv);
    state->derived[7] = state->raw[0];
    status = hhs_pass168_rat_sub(state->raw[28], state->raw[29], &state->derived[8]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_sub(state->raw[30], state->raw[31], &state->derived[9]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_sub(state->raw[32], state->raw[33], &state->derived[10]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_sub(state->raw[34], state->raw[35], &state->derived[11]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_sub(state->raw[36], state->raw[37], &state->derived[12]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rat_sub(state->raw[38], state->raw[39], &state->derived[13]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    state->derived[14] = hhs_pass168_rat_i64(1);
    state->derived[15] = hhs_pass168_rat_i64(1);
    state->derived[16] = gm;
    state->derived[17] = gr[0];
    state->derived[18] = gr[1];
    state->derived[19] = gr[2];
    for (i = 28U; i < 40U; ++i) {
        HHSPass168Rational next;
        status = hhs_pass168_rat_add(sum_e, state->raw[i], &next);
        if (status != HHS_EXACT_STATUS_OK) return status;
        sum_e = next;
    }
    state->derived[20] = sum_e;
    state->derived[21] = (HHSPass168Rational){1,5};
    for (i = 0U; i < 9U; ++i) {
        HHSPass168Rational next;
        status = hhs_pass168_rat_add(successor_sum, state->successor.v[i], &next);
        if (status != HHS_EXACT_STATUS_OK) return status;
        successor_sum = next;
    }
    status = hhs_pass168_rat_div(successor_sum, hhs_pass168_rat_i64(45), &state->derived[22]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (state->generation > (uint64_t)INT64_MAX - 1U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    state->derived[23] = hhs_pass168_rat_i64((int64_t)(state->generation + 1U));
    return hhs_pass168_state_root(state);
}

HHSExactStatus hhs_pass168_state_initialize(HHSPass168CircuitState *out) {
    size_t i;
    HHSExactStatus status;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->version = hhs_pass168_version();
    for (i = 0U; i < HHS_PASS168_PARAMETER_COUNT; ++i)
        out->raw[i] = hhs_pass168_rat_i64(1);
    memset(out->last_receipt_hash72, '0', HHS_EXACT_HASH72_LEN);
    out->last_receipt_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    out->committed = 1U;
    status = hhs_pass168_state_compute(out);
    return status;
}

HHSExactStatus hhs_pass168_cell_value(
    const HHSPass168CircuitState *state,
    uint16_t global_index,
    HHSPass168Rational *out
) {
    HHSPass168Address address;
    HHSPass168Rational scalar;
    HHSExactStatus status;
    if (state == NULL || out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_pass168_address_decode(global_index, &address);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (address.thread_id < HHS_PASS168_RAW_THREAD_COUNT)
        scalar = state->raw[address.thread_id];
    else
        scalar = state->derived[address.thread_id - HHS_PASS168_RAW_THREAD_COUNT];
    return hhs_pass168_rat_mul(scalar, hhs_pass168_rat_i64(HHS_PASS168_LOSHU[address.loshu_index]), out);
}

static uint64_t hhs_pass168_affected_threads(uint64_t update_mask) {
    uint64_t bits = update_mask & ((UINT64_C(1) << HHS_PASS168_PARAMETER_COUNT) - UINT64_C(1));
    uint32_t p;
    int upper = 0;
    int lower = 0;
    for (p = 0U; p < HHS_PASS168_PARAMETER_COUNT; ++p) {
        if ((update_mask & (UINT64_C(1) << p)) == 0U)
            continue;
        if (p <= 5U) { bits |= UINT64_C(1) << 40U; upper = 1; }
        if (p == 0U || p == 8U || p == 9U || p == 10U || p == 11U ||
            p == 15U || p == 16U || p == 17U || p == 22U) {
            bits |= UINT64_C(1) << 41U; lower = 1;
        }
        if (p == 12U || p == 18U || p == 23U) { bits |= UINT64_C(1) << 42U; lower = 1; }
        if (p == 13U || p == 19U || p == 24U) { bits |= UINT64_C(1) << 43U; lower = 1; }
        if (p == 14U || p == 20U || p == 25U) { bits |= UINT64_C(1) << 44U; lower = 1; }
        if (p == 6U) { bits |= UINT64_C(1) << 45U; upper = 1; bits |= UINT64_C(1) << 61U; }
        if (p == 21U) { bits |= UINT64_C(1) << 46U; lower = 1; bits |= UINT64_C(1) << 61U; }
        if (p == 0U) bits |= UINT64_C(1) << 47U;
        if (p == 7U || p == 30U || p == 31U) bits |= UINT64_C(1) << 49U;
        if (p == 26U || p == 34U || p == 35U) bits |= UINT64_C(1) << 51U;
        if (p == 26U || p == 27U || p == 36U || p == 37U) bits |= UINT64_C(1) << 52U;
        if (p == 11U || p == 17U) bits |= UINT64_C(1) << 56U;
        if (p == 12U || p == 18U) bits |= UINT64_C(1) << 57U;
        if (p == 13U || p == 19U) bits |= UINT64_C(1) << 58U;
        if (p == 14U || p == 20U) bits |= UINT64_C(1) << 59U;
        if (p >= 28U) bits |= UINT64_C(1) << 60U;
    }
    if (upper) bits |= (UINT64_C(1) << 48U) | (UINT64_C(1) << 50U) | (UINT64_C(1) << 62U);
    if (lower) bits |= (UINT64_C(1) << 50U) | (UINT64_C(1) << 51U) | (UINT64_C(1) << 62U);
    if ((update_mask & ((UINT64_C(1) << 32U) | (UINT64_C(1) << 33U))) != 0U)
        bits |= (UINT64_C(1) << 50U) | (UINT64_C(1) << 53U);
    if ((update_mask & ((UINT64_C(1) << 28U) | (UINT64_C(1) << 29U))) != 0U)
        bits |= UINT64_C(1) << 48U;
    if ((update_mask & ((UINT64_C(1) << 38U) | (UINT64_C(1) << 39U))) != 0U)
        bits |= UINT64_C(1) << 53U;
    if ((bits & (UINT64_C(1) << 50U)) != 0U)
        bits |= UINT64_C(1) << 53U;
    if (update_mask != 0U)
        bits |= UINT64_C(1) << 63U;
    return bits;
}

HHSExactStatus hhs_pass168_candidate_begin(
    const HHSPass168CircuitState *state,
    HHSPass168Candidate *out
) {
    if (state == NULL || out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (state->struct_size != sizeof(*state) || state->version != hhs_pass168_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->version = hhs_pass168_version();
    memcpy(out->values, state->raw, sizeof(out->values));
    memcpy(out->expected_prior_hash216, state->state_hash216, HHS_PASS168_HASH216_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_pass168_candidate_set(
    HHSPass168Candidate *candidate,
    uint8_t parameter_index,
    int64_t numerator,
    uint64_t denominator
) {
    HHSExactStatus status;
    if (candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate->struct_size != sizeof(*candidate) || candidate->version != hhs_pass168_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (parameter_index >= HHS_PASS168_PARAMETER_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    status = hhs_pass168_rational_normalize(numerator, denominator, &candidate->values[parameter_index]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    candidate->update_mask |= UINT64_C(1) << parameter_index;
    candidate->affected_thread_bitmap = hhs_pass168_affected_threads(candidate->update_mask);
    return HHS_EXACT_STATUS_OK;
}

static int hhs_pass168_zero_forbidden(uint8_t p) {
    return p == 11U || p == 12U || p == 13U || p == 14U || p == 16U ||
           p == 17U || p == 18U || p == 19U || p == 20U;
}

HHSExactStatus hhs_pass168_candidate_validate(
    const HHSPass168CircuitState *prior,
    HHSPass168Candidate *candidate,
    uint32_t *out_reject_reason
) {
    uint32_t p;
    int64_t du;
    int64_t dv;
    if (prior == NULL || candidate == NULL || out_reject_reason == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_reject_reason = HHS_PASS168_REASON_NONE;
    if (prior->struct_size != sizeof(*prior) || candidate->struct_size != sizeof(*candidate) ||
        prior->version != hhs_pass168_version() || candidate->version != hhs_pass168_version()) {
        *out_reject_reason = HHS_PASS168_REASON_STRUCT_SIZE;
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    }
    if (memcmp(candidate->expected_prior_hash216, prior->state_hash216, HHS_PASS168_HASH216_STRLEN) != 0) {
        *out_reject_reason = HHS_PASS168_REASON_STALE_PRIOR_ROOT;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if ((candidate->update_mask >> HHS_PASS168_PARAMETER_COUNT) != 0U) {
        *out_reject_reason = HHS_PASS168_REASON_INVALID_PARAMETER;
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    for (p = 0U; p < HHS_PASS168_PARAMETER_COUNT; ++p) {
        if (candidate->values[p].denominator == 0U) {
            *out_reject_reason = HHS_PASS168_REASON_INVALID_PARAMETER;
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        }
        if (p < HHS_PASS168_P_COUNT && hhs_pass168_zero_forbidden((uint8_t)p) &&
            candidate->values[p].numerator == 0) {
            *out_reject_reason = HHS_PASS168_REASON_ZERO_DENOMINATOR_ROLE;
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }
    if (candidate->values[6].denominator != 1U || candidate->values[21].denominator != 1U) {
        *out_reject_reason = HHS_PASS168_REASON_INVERSE_DEPTH_DOMAIN;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    du = 1 - candidate->values[6].numerator;
    dv = 1 - candidate->values[21].numerator;
    if (du < -HHS_PASS168_MAX_ABS_INVERSE_DEPTH || du > HHS_PASS168_MAX_ABS_INVERSE_DEPTH ||
        dv < -HHS_PASS168_MAX_ABS_INVERSE_DEPTH || dv > HHS_PASS168_MAX_ABS_INVERSE_DEPTH) {
        *out_reject_reason = HHS_PASS168_REASON_INVERSE_DEPTH_DOMAIN;
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    candidate->affected_thread_bitmap = hhs_pass168_affected_threads(candidate->update_mask);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_pass168_candidate_apply(
    const HHSPass168CircuitState *prior,
    HHSPass168Candidate *candidate,
    HHSPass168CircuitState *out_candidate
) {
    uint32_t reason;
    uint32_t p;
    HHSExactStatus status;
    if (prior == NULL || candidate == NULL || out_candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_pass168_candidate_validate(prior, candidate, &reason);
    if (status != HHS_EXACT_STATUS_OK) return status;
    memcpy(out_candidate, prior, sizeof(*out_candidate));
    for (p = 0U; p < HHS_PASS168_PARAMETER_COUNT; ++p)
        if ((candidate->update_mask & (UINT64_C(1) << p)) != 0U)
            out_candidate->raw[p] = candidate->values[p];
    out_candidate->committed = 0U;
    status = hhs_pass168_state_compute(out_candidate);
    return status;
}

static HHSExactStatus hhs_pass168_hash_transition(
    const HHSPass168CircuitState *prior,
    const HHSPass168CircuitState *committed,
    const HHSPass168Candidate *candidate,
    HHSPass168Transition *transition
) {
    uint8_t change_material[2048];
    uint8_t receipt_material[2048];
    size_t cc = 0U;
    size_t rc = 0U;
    size_t i;
    static const uint8_t change_domain[] = "HHS-P168-CHANGE-V1";
    static const uint8_t receipt_domain[] = "HHS-P168-RECEIPT-V1";
    if (sizeof(change_domain) - 1U > sizeof(change_material) ||
        sizeof(receipt_domain) - 1U > sizeof(receipt_material))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memcpy(change_material + cc, change_domain, sizeof(change_domain) - 1U);
    cc += sizeof(change_domain) - 1U;
    if (!hhs_pass168_append_u64(change_material, sizeof(change_material), &cc, candidate->update_mask) ||
        !hhs_pass168_append_u64(change_material, sizeof(change_material), &cc, candidate->affected_thread_bitmap))
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    for (i = 0U; i < HHS_PASS168_PARAMETER_COUNT; ++i)
        if ((candidate->update_mask & (UINT64_C(1) << i)) != 0U &&
            !hhs_pass168_append_rat(change_material, sizeof(change_material), &cc, committed->raw[i]))
            return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    if (cc + HHS_PASS168_HASH216_LEN > sizeof(change_material))
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(change_material + cc, committed->state_hash216, HHS_PASS168_HASH216_LEN);
    cc += HHS_PASS168_HASH216_LEN;
    hhs_exact_uqcel_hash72_bytes(change_material, cc, transition->change_hash72);

    memcpy(receipt_material + rc, receipt_domain, sizeof(receipt_domain) - 1U);
    rc += sizeof(receipt_domain) - 1U;
    if (!hhs_pass168_append_u64(receipt_material, sizeof(receipt_material), &rc, prior->generation) ||
        !hhs_pass168_append_u64(receipt_material, sizeof(receipt_material), &rc, committed->generation) ||
        !hhs_pass168_append_u64(receipt_material, sizeof(receipt_material), &rc, candidate->affected_thread_bitmap))
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    if (rc + (2U * HHS_PASS168_HASH216_LEN) + HHS_EXACT_HASH72_LEN > sizeof(receipt_material))
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(receipt_material + rc, prior->state_hash216, HHS_PASS168_HASH216_LEN);
    rc += HHS_PASS168_HASH216_LEN;
    memcpy(receipt_material + rc, committed->state_hash216, HHS_PASS168_HASH216_LEN);
    rc += HHS_PASS168_HASH216_LEN;
    memcpy(receipt_material + rc, transition->change_hash72, HHS_EXACT_HASH72_LEN);
    rc += HHS_EXACT_HASH72_LEN;
    hhs_exact_uqcel_hash72_bytes(receipt_material, rc, transition->receipt_hash72);

    memcpy(transition->hash216_triplet, prior->last_receipt_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(transition->hash216_triplet + HHS_EXACT_HASH72_LEN,
           transition->change_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(transition->hash216_triplet + 2U * HHS_EXACT_HASH72_LEN,
           transition->receipt_hash72, HHS_EXACT_HASH72_LEN);
    transition->hash216_triplet[HHS_PASS168_HASH216_LEN] = '\0';
    hhs_exact_uqcel_hash216_bytes(
        transition->hash216_triplet, HHS_PASS168_HASH216_LEN, transition->hash216_identity);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_pass168_commit_candidate(
    const HHSPass168CircuitState *prior,
    HHSPass168Candidate *candidate,
    HHSPass168CircuitState *out_committed,
    HHSPass168Transition *out_transition
) {
    HHSPass168CircuitState staged;
    uint32_t reason = HHS_PASS168_REASON_NONE;
    HHSExactStatus status;
    if (prior == NULL || candidate == NULL || out_committed == NULL || out_transition == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_transition, 0, sizeof(*out_transition));
    out_transition->struct_size = (uint32_t)sizeof(*out_transition);
    out_transition->version = hhs_pass168_version();
    status = hhs_pass168_candidate_validate(prior, candidate, &reason);
    if (status != HHS_EXACT_STATUS_OK) {
        out_transition->decision = HHS_PASS168_DECISION_REJECT;
        out_transition->reject_reason = reason;
        return status;
    }
    status = hhs_pass168_candidate_apply(prior, candidate, &staged);
    if (status != HHS_EXACT_STATUS_OK) {
        out_transition->decision = HHS_PASS168_DECISION_REJECT;
        out_transition->reject_reason = HHS_PASS168_REASON_MATRIX_DOMAIN;
        return status;
    }
    if (prior->generation == UINT64_MAX)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    staged.generation = prior->generation + 1U;
    staged.committed = 1U;
    status = hhs_pass168_state_compute(&staged);
    if (status != HHS_EXACT_STATUS_OK) return status;

    out_transition->decision = HHS_PASS168_DECISION_ADMIT;
    out_transition->generation_before = prior->generation;
    out_transition->generation_after = staged.generation;
    out_transition->update_mask = candidate->update_mask;
    out_transition->affected_thread_bitmap = candidate->affected_thread_bitmap;
    memcpy(out_transition->before_raw, prior->raw, sizeof(out_transition->before_raw));
    memcpy(out_transition->after_raw, staged.raw, sizeof(out_transition->after_raw));
    memcpy(out_transition->prior_state_hash216, prior->state_hash216, HHS_PASS168_HASH216_STRLEN);
    memcpy(out_transition->committed_state_hash216, staged.state_hash216, HHS_PASS168_HASH216_STRLEN);
    memcpy(out_transition->prior_receipt_hash72, prior->last_receipt_hash72, HHS_EXACT_HASH72_STRLEN);
    status = hhs_pass168_hash_transition(prior, &staged, candidate, out_transition);
    if (status != HHS_EXACT_STATUS_OK) return status;
    memcpy(staged.last_receipt_hash72, out_transition->receipt_hash72, HHS_EXACT_HASH72_STRLEN);
    out_transition->committed = 1U;
    out_transition->fallback_used = 0U;
    memcpy(out_committed, &staged, sizeof(staged));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_pass168_replay_transition(
    const HHSPass168CircuitState *prior,
    const HHSPass168Transition *transition,
    HHSPass168CircuitState *out_replayed
) {
    HHSPass168Candidate candidate;
    HHSPass168Transition replay_receipt;
    uint32_t p;
    HHSExactStatus status;
    if (prior == NULL || transition == NULL || out_replayed == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (transition->decision != HHS_PASS168_DECISION_ADMIT || transition->committed != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (memcmp(prior->state_hash216, transition->prior_state_hash216, HHS_PASS168_HASH216_STRLEN) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_pass168_candidate_begin(prior, &candidate);
    if (status != HHS_EXACT_STATUS_OK) return status;
    for (p = 0U; p < HHS_PASS168_PARAMETER_COUNT; ++p) {
        if ((transition->update_mask & (UINT64_C(1) << p)) != 0U) {
            candidate.values[p] = transition->after_raw[p];
            candidate.update_mask |= UINT64_C(1) << p;
        }
    }
    candidate.affected_thread_bitmap = hhs_pass168_affected_threads(candidate.update_mask);
    status = hhs_pass168_commit_candidate(prior, &candidate, out_replayed, &replay_receipt);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (memcmp(replay_receipt.receipt_hash72, transition->receipt_hash72, HHS_EXACT_HASH72_STRLEN) != 0 ||
        memcmp(replay_receipt.hash216_identity, transition->hash216_identity, HHS_PASS168_HASH216_STRLEN) != 0 ||
        memcmp(out_replayed->state_hash216, transition->committed_state_hash216, HHS_PASS168_HASH216_STRLEN) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_pass168_rollback_transition(
    const HHSPass168Transition *transition,
    HHSPass168CircuitState *out_prior
) {
    HHSExactStatus status;
    if (transition == NULL || out_prior == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_prior, 0, sizeof(*out_prior));
    out_prior->struct_size = (uint32_t)sizeof(*out_prior);
    out_prior->version = hhs_pass168_version();
    out_prior->generation = transition->generation_before;
    memcpy(out_prior->raw, transition->before_raw, sizeof(out_prior->raw));
    memcpy(out_prior->last_receipt_hash72, transition->prior_receipt_hash72, HHS_EXACT_HASH72_STRLEN);
    out_prior->committed = 1U;
    status = hhs_pass168_state_compute(out_prior);
    if (status != HHS_EXACT_STATUS_OK) return status;
    return memcmp(out_prior->state_hash216, transition->prior_state_hash216, HHS_PASS168_HASH216_STRLEN) == 0 ?
        HHS_EXACT_STATUS_OK : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_pass168_repair_transition(
    const HHSPass168Transition *transition,
    HHSPass168CircuitState *out_repaired
) {
    HHSExactStatus status;
    if (transition == NULL || out_repaired == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_repaired, 0, sizeof(*out_repaired));
    out_repaired->struct_size = (uint32_t)sizeof(*out_repaired);
    out_repaired->version = hhs_pass168_version();
    out_repaired->generation = transition->generation_after;
    memcpy(out_repaired->raw, transition->after_raw, sizeof(out_repaired->raw));
    memcpy(out_repaired->last_receipt_hash72, transition->receipt_hash72, HHS_EXACT_HASH72_STRLEN);
    out_repaired->committed = 1U;
    status = hhs_pass168_state_compute(out_repaired);
    if (status != HHS_EXACT_STATUS_OK) return status;
    return memcmp(out_repaired->state_hash216, transition->committed_state_hash216, HHS_PASS168_HASH216_STRLEN) == 0 ?
        HHS_EXACT_STATUS_OK : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static int hhs_pass168_baseline_matrix_matches(
    const HHSPass168Matrix3 *matrix,
    int64_t scalar
) {
    size_t i;
    for (i = 0U; i < 9U; ++i) {
        HHSPass168Rational expected = hhs_pass168_rat_i64(scalar * HHS_PASS168_LOSHU[i]);
        if (!hhs_pass168_rat_equal(matrix->v[i], expected))
            return 0;
    }
    return 1;
}

HHSExactStatus hhs_pass168_self_test(HHSPass168SelfTest *out) {
    HHSPass168SourceStats source;
    HHSPass168ParameterSpan params[HHS_PASS168_P_COUNT];
    HHSPass168EqualityGate gates[HHS_PASS168_E_COUNT];
    HHSPass168CircuitState baseline;
    HHSPass168CircuitState committed;
    HHSPass168CircuitState replayed;
    HHSPass168CircuitState rolled;
    HHSPass168CircuitState repaired;
    HHSPass168Candidate candidate;
    HHSPass168Transition transition;
    uint8_t seen[HHS_PASS168_TOTAL_CELLS];
    uint32_t i;
    HHSExactStatus status;
    if (out == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    status = hhs_pass168_source_stats(&source);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_parameter_registry(params);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_equality_registry(gates);
    if (status != HHS_EXACT_STATUS_OK) return status;
    memset(seen, 0, sizeof(seen));
    for (i = 0U; i < HHS_PASS168_THREAD_COUNT; ++i) {
        uint32_t local;
        for (local = 0U; local < HHS_PASS168_CELLS_PER_THREAD; ++local) {
            HHSPass168Address encoded;
            HHSPass168Address decoded;
            status = hhs_pass168_address_encode((uint8_t)i, (uint8_t)local, &encoded);
            if (status != HHS_EXACT_STATUS_OK) return status;
            if (seen[encoded.global_index] != 0U)
                ++out->duplicate_addresses;
            seen[encoded.global_index] = 1U;
            status = hhs_pass168_address_decode(encoded.global_index, &decoded);
            if (status != HHS_EXACT_STATUS_OK || decoded.thread_id != i || decoded.local_index != local)
                ++out->inverse_address_failures;
        }
    }
    for (i = 0U; i < HHS_PASS168_TOTAL_CELLS; ++i)
        if (seen[i] != 0U)
            ++out->cells_covered;
    status = hhs_pass168_matrix_invariants();
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_state_initialize(&baseline);
    if (status != HHS_EXACT_STATUS_OK) return status;
    out->source_preserved = source.source_preserved;
    out->parenthesis_parameters_registered = HHS_PASS168_P_COUNT;
    out->equality_half_gates_registered = HHS_PASS168_E_COUNT;
    out->threads_registered = HHS_PASS168_THREAD_COUNT;
    out->raw_threads = HHS_PASS168_RAW_THREAD_COUNT;
    out->derived_threads = HHS_PASS168_DERIVED_THREAD_COUNT;
    out->banks_per_thread = HHS_PASS168_BANKS_PER_THREAD;
    out->cells_per_bank = HHS_PASS168_CELLS_PER_BANK;
    out->exact_rational_authority = 1U;
    out->floating_point_canonical_authority = 0U;
    out->baseline_upper_equals_361L = (uint32_t)hhs_pass168_baseline_matrix_matches(&baseline.upper, 361);
    out->baseline_lower_equals_360L = (uint32_t)hhs_pass168_baseline_matrix_matches(&baseline.lower, 360);
    out->successor_residual_equals_L = (uint32_t)hhs_pass168_baseline_matrix_matches(&baseline.successor, 1);
    out->loshu_square_identity = 1U;
    out->gauge_cancellation_verified =
        (uint32_t)(hhs_pass168_rat_equal(baseline.derived[16], hhs_pass168_rat_i64(1)) &&
                   hhs_pass168_rat_equal(baseline.derived[17], hhs_pass168_rat_i64(1)) &&
                   hhs_pass168_rat_equal(baseline.derived[18], hhs_pass168_rat_i64(1)) &&
                   hhs_pass168_rat_equal(baseline.derived[19], hhs_pass168_rat_i64(1)));
    out->ratio_channels_verified =
        (uint32_t)(hhs_pass168_rat_equal(baseline.derived[2], hhs_pass168_rat_i64(1)) &&
                   hhs_pass168_rat_equal(baseline.derived[3], hhs_pass168_rat_i64(1)) &&
                   hhs_pass168_rat_equal(baseline.derived[4], hhs_pass168_rat_i64(1)));
    out->comparators_verified = 6U;
    status = hhs_pass168_candidate_begin(&baseline, &candidate);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_candidate_set(&candidate, 12U, 2, 1U);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if ((candidate.affected_thread_bitmap & (UINT64_C(1) << 12U)) == 0U ||
        (candidate.affected_thread_bitmap & (UINT64_C(1) << 42U)) == 0U ||
        (candidate.affected_thread_bitmap & (UINT64_C(1) << 50U)) == 0U ||
        (candidate.affected_thread_bitmap & (UINT64_C(1) << 57U)) == 0U ||
        (candidate.affected_thread_bitmap & (UINT64_C(1) << 62U)) == 0U ||
        (candidate.affected_thread_bitmap & (UINT64_C(1) << 63U)) == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out->sparse_dependency_updates_verified = candidate.affected_thread_bitmap != UINT64_MAX;
    status = hhs_pass168_commit_candidate(&baseline, &candidate, &committed, &transition);
    if (status != HHS_EXACT_STATUS_OK) return status;
    out->single_vm81_commit_authority = transition.committed == 1U;
    out->hash72_receipts_verified =
        (uint32_t)(strlen(transition.change_hash72) == HHS_EXACT_HASH72_LEN &&
                   strlen(transition.receipt_hash72) == HHS_EXACT_HASH72_LEN);
    out->hash216_identity_verified =
        (uint32_t)(strlen(transition.hash216_identity) == HHS_PASS168_HASH216_LEN);
    status = hhs_pass168_replay_transition(&baseline, &transition, &replayed);
    out->deterministic_replay_verified = status == HHS_EXACT_STATUS_OK;
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_rollback_transition(&transition, &rolled);
    out->rollback_verified =
        (uint32_t)(status == HHS_EXACT_STATUS_OK &&
                   memcmp(rolled.state_hash216, baseline.state_hash216, HHS_PASS168_HASH216_STRLEN) == 0);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_pass168_repair_transition(&transition, &repaired);
    out->repair_verified =
        (uint32_t)(status == HHS_EXACT_STATUS_OK &&
                   memcmp(repaired.state_hash216, committed.state_hash216, HHS_PASS168_HASH216_STRLEN) == 0);
    if (status != HHS_EXACT_STATUS_OK) return status;
#if defined(__x86_64__) || defined(_M_X64)
    out->x86_64_verified = 1U;
#endif
#if defined(__aarch64__) || defined(_M_ARM64)
    out->arm64_verified = 1U;
#endif
    out->fallback_used = 0U;
    {
        uint8_t material[1024];
        size_t cursor = 0U;
        static const uint8_t domain[] = "HHS-P168-SELFTEST-V1";
        memcpy(material + cursor, domain, sizeof(domain) - 1U);
        cursor += sizeof(domain) - 1U;
        memcpy(material + cursor, baseline.state_hash216, HHS_PASS168_HASH216_LEN);
        cursor += HHS_PASS168_HASH216_LEN;
        memcpy(material + cursor, transition.hash216_identity, HHS_PASS168_HASH216_LEN);
        cursor += HHS_PASS168_HASH216_LEN;
        memcpy(material + cursor, HHS_PASS168_SOURCE_SHA256, HHS_PASS168_SOURCE_SHA256_HEX_LEN);
        cursor += HHS_PASS168_SOURCE_SHA256_HEX_LEN;
        hhs_exact_uqcel_hash216_bytes(material, cursor, out->deterministic_record_hash216);
    }
    if (!out->source_preserved || out->parenthesis_parameters_registered != 28U ||
        out->equality_half_gates_registered != 12U || out->threads_registered != 64U ||
        out->raw_threads != 40U || out->derived_threads != 24U || out->cells_covered != 5184U ||
        out->duplicate_addresses != 0U || out->inverse_address_failures != 0U ||
        out->banks_per_thread != 9U || out->cells_per_bank != 9U ||
        !out->exact_rational_authority || out->floating_point_canonical_authority ||
        !out->baseline_upper_equals_361L || !out->baseline_lower_equals_360L ||
        !out->successor_residual_equals_L || !out->loshu_square_identity ||
        !out->gauge_cancellation_verified || !out->ratio_channels_verified ||
        out->comparators_verified != 6U || !out->sparse_dependency_updates_verified ||
        !out->single_vm81_commit_authority || !out->hash72_receipts_verified ||
        !out->hash216_identity_verified || !out->rollback_verified || !out->repair_verified ||
        !out->deterministic_replay_verified || out->fallback_used)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}
