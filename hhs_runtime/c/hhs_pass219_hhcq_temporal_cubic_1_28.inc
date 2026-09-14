#include "../include/hhs_pass219_hhcq_temporal_cubic_1_28.h"

#include <limits.h>
#include <string.h>

static uint64_t hhs_p219_hhcq_temporal_mix64(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static uint64_t hhs_p219_hhcq_temporal_abs64(int64_t value) {
    return value < 0 ? (uint64_t)(-(value + 1)) + UINT64_C(1) : (uint64_t)value;
}

static int hhs_p219_hhcq_temporal_add_i64(int64_t a, int64_t b, int64_t *out) {
    if (out == NULL)
        return 0;
    if ((b > 0 && a > INT64_MAX - b) ||
        (b < 0 && a < INT64_MIN - b))
        return 0;
    *out = a + b;
    return 1;
}

static int hhs_p219_hhcq_temporal_sub_i64(int64_t a, int64_t b, int64_t *out) {
    if (out == NULL)
        return 0;
    if ((b > 0 && a < INT64_MIN + b) ||
        (b < 0 && a > INT64_MAX + b))
        return 0;
    *out = a - b;
    return 1;
}

static int hhs_p219_hhcq_temporal_mul_i64(int64_t a, int64_t b, int64_t *out) {
    if (out == NULL)
        return 0;
    if (a == 0 || b == 0) {
        *out = 0;
        return 1;
    }
    if ((a == INT64_MIN && b == -1) || (b == INT64_MIN && a == -1))
        return 0;
    if (a > 0) {
        if (b > 0) {
            if (a > INT64_MAX / b)
                return 0;
        } else if (b < INT64_MIN / a) {
            return 0;
        }
    } else {
        if (b > 0) {
            if (a < INT64_MIN / b)
                return 0;
        } else if (a < INT64_MAX / b) {
            return 0;
        }
    }
    *out = a * b;
    return 1;
}

static int hhs_p219_hhcq_temporal_pow_i64(int64_t base, uint32_t exponent, int64_t *out) {
    uint32_t i;
    int64_t value = INT64_C(1);
    if (out == NULL)
        return 0;
    for (i = 0U; i < exponent; ++i) {
        if (!hhs_p219_hhcq_temporal_mul_i64(value, base, &value))
            return 0;
    }
    *out = value;
    return 1;
}

static int hhs_p219_hhcq_temporal_cross_phase_g(
    int32_t w,
    int32_t x,
    int32_t y,
    int32_t z,
    int64_t *out_g
) {
    int64_t sum;
    int64_t xy;
    int64_t xy_sum;
    int64_t wz;
    if (out_g == NULL)
        return 0;
    if (!hhs_p219_hhcq_temporal_add_i64((int64_t)x, (int64_t)y, &sum) ||
        !hhs_p219_hhcq_temporal_add_i64(sum, (int64_t)z, &sum) ||
        !hhs_p219_hhcq_temporal_add_i64(sum, (int64_t)w, &sum) ||
        !hhs_p219_hhcq_temporal_mul_i64((int64_t)x, (int64_t)y, &xy) ||
        !hhs_p219_hhcq_temporal_mul_i64(xy, sum, &xy_sum) ||
        !hhs_p219_hhcq_temporal_mul_i64((int64_t)w, (int64_t)z, &wz) ||
        !hhs_p219_hhcq_temporal_sub_i64(xy_sum, wz, out_g))
        return 0;
    return 1;
}

static int hhs_p219_hhcq_temporal_compact_coefficients(
    int32_t m,
    int32_t w,
    int32_t x,
    int32_t y,
    int32_t z,
    int64_t *out_g,
    int64_t *out_q,
    int64_t *out_c
) {
    int64_t x2;
    int64_t y2;
    int64_t mm1;
    int64_t temp;
    if (out_g == NULL || out_q == NULL || out_c == NULL)
        return 0;
    if (!hhs_p219_hhcq_temporal_cross_phase_g(w, x, y, z, out_g) ||
        !hhs_p219_hhcq_temporal_mul_i64((int64_t)x, (int64_t)x, &x2) ||
        !hhs_p219_hhcq_temporal_mul_i64((int64_t)y, (int64_t)y, &y2) ||
        !hhs_p219_hhcq_temporal_mul_i64(x2, y2, out_q) ||
        !hhs_p219_hhcq_temporal_mul_i64((int64_t)m, (int64_t)m - INT64_C(1), &mm1) ||
        !hhs_p219_hhcq_temporal_mul_i64(mm1, (int64_t)w, &temp) ||
        !hhs_p219_hhcq_temporal_mul_i64(temp, (int64_t)z, &temp) ||
        !hhs_p219_hhcq_temporal_mul_i64(temp, *out_g, out_c))
        return 0;
    return 1;
}

static int hhs_p219_hhcq_temporal_residual(
    int64_t q,
    int64_t c,
    int64_t t,
    int64_t *out_residual
) {
    int64_t t2;
    int64_t t3;
    int64_t t3_minus_t;
    int64_t scaled;
    if (out_residual == NULL)
        return 0;
    if (!hhs_p219_hhcq_temporal_mul_i64(t, t, &t2) ||
        !hhs_p219_hhcq_temporal_mul_i64(t2, t, &t3) ||
        !hhs_p219_hhcq_temporal_sub_i64(t3, t, &t3_minus_t) ||
        !hhs_p219_hhcq_temporal_mul_i64(q, t3_minus_t, &scaled) ||
        !hhs_p219_hhcq_temporal_add_i64(scaled, c, out_residual))
        return 0;
    return 1;
}

static uint32_t hhs_p219_hhcq_temporal_mod72_i64(int64_t value) {
    int64_t r = value % INT64_C(72);
    if (r < 0)
        r += INT64_C(72);
    return (uint32_t)r;
}

static uint32_t hhs_p219_hhcq_temporal_mul72(uint32_t a, uint32_t b) {
    return (a * b) % HHS_EXACT_PASS219_HHCQ_TEMPORAL_PHASE_MODULUS;
}

static uint32_t hhs_p219_hhcq_temporal_polynomial_mod72(
    int32_t m,
    int32_t w,
    int32_t x,
    int32_t y,
    int32_t z,
    uint32_t t
) {
    const uint32_t mm = hhs_p219_hhcq_temporal_mod72_i64((int64_t)m);
    const uint32_t wm = hhs_p219_hhcq_temporal_mod72_i64((int64_t)w);
    const uint32_t xm = hhs_p219_hhcq_temporal_mod72_i64((int64_t)x);
    const uint32_t ym = hhs_p219_hhcq_temporal_mod72_i64((int64_t)y);
    const uint32_t zm = hhs_p219_hhcq_temporal_mod72_i64((int64_t)z);
    const uint32_t m_minus_1 = (mm + 71U) % 72U;
    const uint32_t sum = (xm + ym + zm + wm) % 72U;
    const uint32_t xy = hhs_p219_hhcq_temporal_mul72(xm, ym);
    const uint32_t wz = hhs_p219_hhcq_temporal_mul72(wm, zm);
    const uint32_t g = (hhs_p219_hhcq_temporal_mul72(xy, sum) + 72U - wz) % 72U;
    const uint32_t x2 = hhs_p219_hhcq_temporal_mul72(xm, xm);
    const uint32_t y2 = hhs_p219_hhcq_temporal_mul72(ym, ym);
    const uint32_t q = hhs_p219_hhcq_temporal_mul72(x2, y2);
    uint32_t c = hhs_p219_hhcq_temporal_mul72(mm, m_minus_1);
    uint32_t t2;
    uint32_t t3;
    uint32_t cubic;
    c = hhs_p219_hhcq_temporal_mul72(c, wm);
    c = hhs_p219_hhcq_temporal_mul72(c, zm);
    c = hhs_p219_hhcq_temporal_mul72(c, g);
    t %= 72U;
    t2 = hhs_p219_hhcq_temporal_mul72(t, t);
    t3 = hhs_p219_hhcq_temporal_mul72(t2, t);
    cubic = (t3 + 72U - t) % 72U;
    return (hhs_p219_hhcq_temporal_mul72(q, cubic) + c) % 72U;
}

uint32_t hhs_exact_pass219_hhcq_temporal_cubic_version(void) {
    return HHS_EXACT_PASS219_HHCQ_TEMPORAL_CUBIC_VERSION;
}

HHSExactStatus hhs_exact_pass219_hhcq_temporal_cubic_descriptor(
    HHSExactPass219HHCQTemporalCubicDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_HHCQ_TEMPORAL_CUBIC_VERSION;
    out_descriptor->inherited_policy_state_bytes =
        (uint32_t)sizeof(HHSExactPass219HHCQJointStateV1);
    out_descriptor->phase_modulus = HHS_EXACT_PASS219_HHCQ_TEMPORAL_PHASE_MODULUS;
    out_descriptor->symbolic_cardano_branch_count =
        HHS_EXACT_PASS219_HHCQ_TEMPORAL_CARDANO_BRANCH_COUNT;
    out_descriptor->compact_cubic_identity = 1U;
    out_descriptor->factored_discriminant_identity = 1U;
    out_descriptor->radical_eliminated_from_canonical_path = 1U;
    out_descriptor->z72_root_scan = 1U;
    out_descriptor->composite_ring_root_count_variable = 1U;
    out_descriptor->discrete_neighbor_direction = 1U;
    out_descriptor->phase5_resolution_locked = 1U;
    out_descriptor->fixed_size_policy_state = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->exact_integer_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_temporal_cubic_witness(
    int32_t m,
    int32_t w,
    int32_t x,
    int32_t y,
    int32_t z,
    int32_t t,
    HHSExactPass219HHCQTemporalCubicWitnessV1 *out_witness
) {
    int64_t g;
    int64_t q;
    int64_t c;
    uint64_t abs_minus;
    uint64_t abs_zero;
    uint64_t abs_plus;
    uint64_t best;
    uint64_t signature;
    if (out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = HHS_EXACT_PASS219_HHCQ_TEMPORAL_CUBIC_VERSION;
    out_witness->m = m;
    out_witness->w = w;
    out_witness->x = x;
    out_witness->y = y;
    out_witness->z = z;
    out_witness->t = t;
    out_witness->exact_integer_only = 1U;
    out_witness->candidate_only = 1U;
    if (x == 0 || y == 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hhs_p219_hhcq_temporal_compact_coefficients(m, w, x, y, z, &g, &q, &c) ||
        !hhs_p219_hhcq_temporal_residual(q, c, (int64_t)t - INT64_C(1),
                                         &out_witness->residual_minus) ||
        !hhs_p219_hhcq_temporal_residual(q, c, (int64_t)t,
                                         &out_witness->residual_zero) ||
        !hhs_p219_hhcq_temporal_residual(q, c, (int64_t)t + INT64_C(1),
                                         &out_witness->residual_plus))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    out_witness->cross_phase_g = g;
    out_witness->leading_x2y2 = q;
    out_witness->constant_term = c;
    abs_minus = hhs_p219_hhcq_temporal_abs64(out_witness->residual_minus);
    abs_zero = hhs_p219_hhcq_temporal_abs64(out_witness->residual_zero);
    abs_plus = hhs_p219_hhcq_temporal_abs64(out_witness->residual_plus);
    out_witness->absolute_residual_zero = abs_zero;
    best = abs_zero;
    out_witness->temporal_direction = 0;
    if (abs_minus < best) {
        best = abs_minus;
        out_witness->temporal_direction = -1;
    }
    if (abs_plus < best) {
        best = abs_plus;
        out_witness->temporal_direction = 1;
    }
    out_witness->temporal_gain = abs_zero - best;
    signature = UINT64_C(0x2197e0c0b1c00128) ^
        ((uint64_t)(uint32_t)m << 56U) ^
        ((uint64_t)(uint32_t)w << 48U) ^
        ((uint64_t)(uint32_t)x << 40U) ^
        ((uint64_t)(uint32_t)y << 32U) ^
        ((uint64_t)(uint32_t)z << 24U) ^
        ((uint64_t)(uint32_t)t << 16U) ^
        (uint64_t)(uint8_t)(out_witness->temporal_direction + 1);
    signature = hhs_p219_hhcq_temporal_mix64(
        signature ^ (uint64_t)g ^ (uint64_t)q ^ (uint64_t)c);
    signature = hhs_p219_hhcq_temporal_mix64(
        signature ^ (uint64_t)out_witness->residual_zero ^ out_witness->temporal_gain);
    out_witness->witness_signature64 = signature;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_temporal_cardano_factor(
    int32_t m,
    int32_t w,
    int32_t x,
    int32_t y,
    int32_t z,
    HHSExactPass219HHCQTemporalCardanoFactorV1 *out_factor
) {
    int64_t g;
    int64_t x4;
    int64_t y4;
    int64_t x12;
    int64_t y12;
    int64_t mm1;
    int64_t temp;
    int64_t b2;
    int64_t correction;
    uint64_t signature;
    if (out_factor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_factor, 0, sizeof(*out_factor));
    out_factor->struct_size = (uint32_t)sizeof(*out_factor);
    out_factor->version = HHS_EXACT_PASS219_HHCQ_TEMPORAL_CUBIC_VERSION;
    out_factor->m = m;
    out_factor->w = w;
    out_factor->x = x;
    out_factor->y = y;
    out_factor->z = z;
    out_factor->exact_integer_only = 1U;
    out_factor->candidate_only = 1U;
    if (x == 0 || y == 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hhs_p219_hhcq_temporal_cross_phase_g(w, x, y, z, &g) ||
        !hhs_p219_hhcq_temporal_pow_i64((int64_t)x, 4U, &x4) ||
        !hhs_p219_hhcq_temporal_pow_i64((int64_t)y, 4U, &y4) ||
        !hhs_p219_hhcq_temporal_pow_i64((int64_t)x, 12U, &x12) ||
        !hhs_p219_hhcq_temporal_pow_i64((int64_t)y, 12U, &y12) ||
        !hhs_p219_hhcq_temporal_mul_i64((int64_t)m, (int64_t)m - INT64_C(1), &mm1) ||
        !hhs_p219_hhcq_temporal_mul_i64(INT64_C(27), mm1, &temp) ||
        !hhs_p219_hhcq_temporal_mul_i64(temp, (int64_t)w, &temp) ||
        !hhs_p219_hhcq_temporal_mul_i64(temp, x4, &temp) ||
        !hhs_p219_hhcq_temporal_mul_i64(temp, y4, &temp) ||
        !hhs_p219_hhcq_temporal_mul_i64(temp, (int64_t)z, &temp) ||
        !hhs_p219_hhcq_temporal_mul_i64(temp, g, &out_factor->cardano_b) ||
        !hhs_p219_hhcq_temporal_mul_i64(x12, y12, &out_factor->x12y12) ||
        !hhs_p219_hhcq_temporal_mul_i64(out_factor->cardano_b,
                                        out_factor->cardano_b, &b2) ||
        !hhs_p219_hhcq_temporal_mul_i64(INT64_C(108), out_factor->x12y12,
                                        &correction) ||
        !hhs_p219_hhcq_temporal_sub_i64(b2, correction,
                                        &out_factor->discriminant_r))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    out_factor->cross_phase_g = g;
    out_factor->exact_factorization = 1U;
    signature = hhs_p219_hhcq_temporal_mix64(
        UINT64_C(0x219ca4da90f00128) ^ (uint64_t)g ^
        (uint64_t)out_factor->cardano_b ^
        (uint64_t)out_factor->x12y12 ^
        (uint64_t)out_factor->discriminant_r);
    out_factor->witness_signature64 = signature;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_temporal_z72_roots(
    int32_t m,
    int32_t w,
    int32_t x,
    int32_t y,
    int32_t z,
    uint8_t phase_hint72,
    HHSExactPass219HHCQTemporalZ72RootsV1 *out_roots
) {
    uint32_t t;
    uint32_t best_distance = UINT32_MAX;
    uint64_t signature;
    if (out_roots == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (phase_hint72 >= HHS_EXACT_PASS219_HHCQ_TEMPORAL_PHASE_MODULUS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (x == 0 || y == 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memset(out_roots, 0, sizeof(*out_roots));
    out_roots->struct_size = (uint32_t)sizeof(*out_roots);
    out_roots->version = HHS_EXACT_PASS219_HHCQ_TEMPORAL_CUBIC_VERSION;
    out_roots->phase_hint72 = phase_hint72;
    out_roots->preferred_root72 = HHS_EXACT_PASS219_HHCQ_TEMPORAL_NO_ROOT;
    out_roots->symbolic_cardano_branch_count =
        (uint8_t)HHS_EXACT_PASS219_HHCQ_TEMPORAL_CARDANO_BRANCH_COUNT;
    out_roots->composite_ring_root_count_variable = 1U;
    out_roots->exact_integer_only = 1U;
    out_roots->candidate_only = 1U;
    for (t = 0U; t < HHS_EXACT_PASS219_HHCQ_TEMPORAL_PHASE_MODULUS; ++t) {
        if (hhs_p219_hhcq_temporal_polynomial_mod72(m, w, x, y, z, t) == 0U) {
            uint32_t forward;
            uint32_t distance;
            ++out_roots->root_count;
            if (t < 64U)
                out_roots->roots_0_63 |= UINT64_C(1) << t;
            else
                out_roots->roots_64_71 |= (uint8_t)(UINT8_C(1) << (t - 64U));
            forward = (t + 72U - (uint32_t)phase_hint72) % 72U;
            distance = forward <= 36U ? forward : 72U - forward;
            if (distance < best_distance) {
                best_distance = distance;
                out_roots->preferred_root72 = (uint8_t)t;
                if (forward == 0U)
                    out_roots->preferred_direction = 0;
                else if (forward <= 36U)
                    out_roots->preferred_direction = 1;
                else
                    out_roots->preferred_direction = -1;
            }
        }
    }
    signature = UINT64_C(0x219072c0b1c00128) ^ out_roots->roots_0_63 ^
        ((uint64_t)out_roots->roots_64_71 << 56U) ^
        ((uint64_t)out_roots->root_count << 48U) ^
        ((uint64_t)phase_hint72 << 40U) ^
        ((uint64_t)out_roots->preferred_root72 << 32U) ^
        ((uint64_t)(uint8_t)(out_roots->preferred_direction + 1) << 24U);
    out_roots->root_signature64 = hhs_p219_hhcq_temporal_mix64(signature);
    return HHS_EXACT_STATUS_OK;
}
