#include "../include/hhs_pass219_hash216_fractal_qudit_admission_1_45.h"
#include "../include/hhs_hash216_bytes.h"

#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static const uint8_t HHS_P219_FQ_WITNESS_DOMAIN[] =
    "HHS-P219-HASH216-FRACTAL-QUDIT-WITNESS-1.45";
static const uint8_t HHS_P219_FQ_RECEIPT_DOMAIN[] =
    "HHS-P219-HASH216-FRACTAL-QUDIT-RECEIPT-1.45";

static uint64_t hhs_fq_fnv_bytes(uint64_t hash, const void *data, size_t size) {
    const uint8_t *bytes = (const uint8_t *)data;
    size_t i;
    if (data == NULL && size != 0U)
        return UINT64_C(0);
    for (i = 0U; i < size; ++i) {
        hash ^= (uint64_t)bytes[i];
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static uint64_t hhs_fq_fnv_u64(uint64_t hash, uint64_t value) {
    uint8_t bytes[8];
    size_t i;
    for (i = 0U; i < 8U; ++i)
        bytes[7U - i] = (uint8_t)(value >> (8U * i));
    return hhs_fq_fnv_bytes(hash, bytes, sizeof(bytes));
}

static int hhs_fq_append(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    const void *data,
    size_t size
) {
    if (out == NULL || cursor == NULL || (data == NULL && size != 0U) ||
        *cursor > capacity || size > capacity - *cursor)
        return 0;
    if (size != 0U)
        memcpy(out + *cursor, data, size);
    *cursor += size;
    return 1;
}

static int hhs_fq_append_u16(
    uint8_t *out, size_t capacity, size_t *cursor, uint16_t value
) {
    uint8_t bytes[2] = {
        (uint8_t)(value >> 8U),
        (uint8_t)value
    };
    return hhs_fq_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static int hhs_fq_append_u32(
    uint8_t *out, size_t capacity, size_t *cursor, uint32_t value
) {
    uint8_t bytes[4] = {
        (uint8_t)(value >> 24U),
        (uint8_t)(value >> 16U),
        (uint8_t)(value >> 8U),
        (uint8_t)value
    };
    return hhs_fq_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static int hhs_fq_append_u64(
    uint8_t *out, size_t capacity, size_t *cursor, uint64_t value
) {
    uint8_t bytes[8];
    size_t i;
    for (i = 0U; i < 8U; ++i)
        bytes[7U - i] = (uint8_t)(value >> (8U * i));
    return hhs_fq_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static int hhs_fq_append_i64(
    uint8_t *out, size_t capacity, size_t *cursor, int64_t value
) {
    return hhs_fq_append_u64(out, capacity, cursor, (uint64_t)value);
}

static int hhs_fq_append_big(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    const HHSExactBigUIntView *value
) {
    if (value == NULL || value->bytes_be == NULL || value->byte_length == 0U ||
        value->byte_length > UINT16_MAX)
        return 0;
    return hhs_fq_append_u16(out, capacity, cursor, (uint16_t)value->byte_length) &&
           hhs_fq_append(out, capacity, cursor, value->bytes_be, value->byte_length);
}

static int hhs_fq_big_add(
    const HHSExactBigUIntView *left,
    const HHSExactBigUIntView *right,
    uint8_t out[HHS_EXACT_UQCEL_MAX_P_BYTES + 1U],
    size_t *out_length
) {
    uint8_t reverse[HHS_EXACT_UQCEL_MAX_P_BYTES + 1U];
    size_t max_length;
    size_t i;
    uint16_t carry = 0U;
    if (left == NULL || right == NULL || out == NULL || out_length == NULL ||
        left->bytes_be == NULL || right->bytes_be == NULL ||
        left->byte_length == 0U || right->byte_length == 0U ||
        left->byte_length > HHS_EXACT_UQCEL_MAX_P_BYTES ||
        right->byte_length > HHS_EXACT_UQCEL_MAX_P_BYTES)
        return 0;
    max_length = left->byte_length > right->byte_length
        ? (size_t)left->byte_length : (size_t)right->byte_length;
    memset(reverse, 0, sizeof(reverse));
    for (i = 0U; i < max_length; ++i) {
        const uint16_t a = i < (size_t)left->byte_length
            ? left->bytes_be[(size_t)left->byte_length - 1U - i] : 0U;
        const uint16_t b = i < (size_t)right->byte_length
            ? right->bytes_be[(size_t)right->byte_length - 1U - i] : 0U;
        const uint16_t sum = (uint16_t)(a + b + carry);
        reverse[i] = (uint8_t)(sum & UINT16_C(0xff));
        carry = (uint16_t)(sum >> 8U);
    }
    if (carry != 0U) {
        if (max_length >= sizeof(reverse))
            return 0;
        reverse[max_length++] = (uint8_t)carry;
    }
    for (i = 0U; i < max_length; ++i)
        out[max_length - 1U - i] = reverse[i];
    *out_length = max_length;
    return 1;
}

static int hhs_fq_big_sum_equal(
    const HHSExactBigUIntView *a,
    const HHSExactBigUIntView *b,
    const HHSExactBigUIntView *c,
    const HHSExactBigUIntView *d
) {
    uint8_t left[HHS_EXACT_UQCEL_MAX_P_BYTES + 1U];
    uint8_t right[HHS_EXACT_UQCEL_MAX_P_BYTES + 1U];
    size_t left_length = 0U;
    size_t right_length = 0U;
    return hhs_fq_big_add(a, b, left, &left_length) &&
           hhs_fq_big_add(c, d, right, &right_length) &&
           left_length == right_length &&
           memcmp(left, right, left_length) == 0;
}

static int hhs_fq_big_is_one(const HHSExactBigUIntView *value) {
    return value != NULL && value->bytes_be != NULL &&
           value->byte_length == 1U && value->bytes_be[0] == UINT8_C(1);
}

static uint64_t hhs_fq_abs_u64(int64_t value) {
    const uint64_t raw = (uint64_t)value;
    return value < 0 ? UINT64_C(0) - raw : raw;
}

static int hhs_fq_mul_i64(int64_t a, int64_t b, int64_t *out) {
    uint64_t ua;
    uint64_t ub;
    uint64_t product;
    const int negative = (a < 0) != (b < 0);
    if (out == NULL)
        return 0;
    ua = hhs_fq_abs_u64(a);
    ub = hhs_fq_abs_u64(b);
    if (ua != 0U && ub > UINT64_MAX / ua)
        return 0;
    product = ua * ub;
    if (!negative) {
        if (product > (uint64_t)INT64_MAX)
            return 0;
        *out = (int64_t)product;
        return 1;
    }
    if (product > (UINT64_C(1) << 63U))
        return 0;
    if (product == (UINT64_C(1) << 63U)) {
        *out = INT64_MIN;
        return 1;
    }
    *out = -(int64_t)product;
    return 1;
}

static int hhs_fq_add_i64(int64_t a, int64_t b, int64_t *out) {
    if (out == NULL)
        return 0;
    if ((b > 0 && a > INT64_MAX - b) ||
        (b < 0 && a < INT64_MIN - b))
        return 0;
    *out = a + b;
    return 1;
}

static int hhs_fq_sub_i64(int64_t a, int64_t b, int64_t *out) {
    if (out == NULL)
        return 0;
    if ((b > 0 && a < INT64_MIN + b) ||
        (b < 0 && a > INT64_MAX + b))
        return 0;
    *out = a - b;
    return 1;
}

static int hhs_fq_mass(
    int64_t t,
    int64_t x,
    int64_t y,
    int64_t *out_D,
    int64_t *out_N
) {
    int64_t t2;
    int64_t t3;
    int64_t t4;
    int64_t xy;
    int64_t txy;
    int64_t neg_txy;
    int64_t D;
    int64_t tmp;
    int64_t x2;
    int64_t y2;
    int64_t anisotropy;
    int64_t eight_a;
    int64_t complement;
    int64_t N;
    if (out_D == NULL || out_N == NULL || t == 0)
        return 0;
    if (!hhs_fq_mul_i64(t, t, &t2) ||
        !hhs_fq_mul_i64(t2, t, &t3) ||
        !hhs_fq_mul_i64(t2, t2, &t4) ||
        !hhs_fq_mul_i64(x, y, &xy) ||
        !hhs_fq_mul_i64(t, xy, &txy) ||
        !hhs_fq_sub_i64(0, txy, &neg_txy) ||
        !hhs_fq_add_i64(neg_txy, t4, &D) ||
        !hhs_fq_add_i64(D, t3, &tmp) ||
        !hhs_fq_sub_i64(tmp, t2, &D) ||
        !hhs_fq_mul_i64(x, x, &x2) ||
        !hhs_fq_mul_i64(y, y, &y2) ||
        !hhs_fq_sub_i64(x2, y2, &anisotropy) ||
        !hhs_fq_mul_i64(INT64_C(8), anisotropy, &eight_a) ||
        !hhs_fq_sub_i64(D, eight_a, &complement) ||
        !hhs_fq_mul_i64(D, complement, &N))
        return 0;
    if (D == 0)
        return 0;
    *out_D = D;
    *out_N = N;
    return 1;
}

static uint8_t hhs_fq_lo_shu_for_cell(uint8_t cell81) {
    static const uint8_t lo_shu[9] = {4U, 9U, 2U, 3U, 5U, 7U, 8U, 1U, 6U};
    return lo_shu[(size_t)cell81 % 9U];
}

static void hhs_fq_zero_receipt(
    HHSExactPass219Hash216FractalQuditReceiptV1 *receipt
) {
    if (receipt == NULL)
        return;
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = (uint32_t)sizeof(*receipt);
    receipt->version = HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_VERSION;
    receipt->namespace_id = HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_NAMESPACE;
    receipt->reason = HHS_EXACT_PASS219_FQ_REASON_NONE;
    receipt->exact_integer_only = 1U;
}

static HHSExactStatus hhs_fq_prevalidate(
    const HHSExactUQCELInputV1 *input,
    const HHSExactPass219Hash216TransitionViewV1 *parent,
    const HHSExactPass219Hash216FractalQuditWitnessV1 *witness,
    uint64_t *out_verified,
    uint64_t *out_failed,
    uint32_t *out_reason
) {
    HHSExactUQCELAdmissionV1 uqcel;
    HHSExactStatus status;
    uint64_t verified = 0U;
    uint64_t failed = 0U;
    uint32_t reason = HHS_EXACT_PASS219_FQ_REASON_NONE;
    uint16_t expected_local;
    uint8_t expected_operation;
    uint8_t expected_lo_shu;
    int64_t D;
    int64_t N;

    if (out_verified != NULL)
        *out_verified = 0U;
    if (out_failed != NULL)
        *out_failed = 0U;
    if (out_reason != NULL)
        *out_reason = HHS_EXACT_PASS219_FQ_REASON_NONE;
    if (input == NULL || parent == NULL || witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size != (uint32_t)sizeof(*witness) ||
        witness->version != HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->declared_scope_mask != HHS_EXACT_PASS219_FQ_SCOPE_REQUIRED) {
        failed |= HHS_EXACT_PASS219_FQ_SCOPE_REQUIRED & ~witness->declared_scope_mask;
        reason = HHS_EXACT_PASS219_FQ_REASON_SCOPE;
        goto rejected;
    }

    if (HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_BLOCK !=
            HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_HASH72_RADIX *
            HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_HASH72_RADIX ||
        HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_BLOCK !=
            HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_VM81_CELLS *
            HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_LANE64 ||
        HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_LEVELS * UINT32_C(2) !=
            HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_HASH72_RADIX) {
        failed |= HHS_EXACT_PASS219_FQ_SCOPE_SCALING;
        reason = HHS_EXACT_PASS219_FQ_REASON_SCALING;
        goto rejected;
    }
    verified |= HHS_EXACT_PASS219_FQ_SCOPE_SCALING;

    memset(&uqcel, 0, sizeof(uqcel));
    status = hhs_exact_uqcel_validate(input, &uqcel);
    if (status != HHS_EXACT_STATUS_OK ||
        uqcel.decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        input->profile != HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1 ||
        !hhs_fq_big_is_one(&input->delta)) {
        failed |= HHS_EXACT_PASS219_FQ_SCOPE_PQ_WINDOW;
        reason = HHS_EXACT_PASS219_FQ_REASON_PQ_WINDOW;
        goto rejected;
    }

    expected_operation = (uint8_t)(
        input->left_basis8 * HHS_EXACT_PHASE_BASIS_COUNT + input->right_basis8);
    expected_local = (uint16_t)(
        (uint16_t)input->cell81 * HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_LANE64 +
        (uint16_t)expected_operation);
    if (witness->local5184 >= HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_BLOCK ||
        witness->hash72_major >= HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_HASH72_RADIX ||
        witness->hash72_minor >= HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_HASH72_RADIX ||
        witness->cell81 >= HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_VM81_CELLS ||
        witness->operation64 >= HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_LANE64 ||
        witness->local5184 != (uint16_t)(
            (uint16_t)witness->hash72_major *
            HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_HASH72_RADIX +
            (uint16_t)witness->hash72_minor) ||
        witness->local5184 != (uint16_t)(
            (uint16_t)witness->cell81 *
            HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_LANE64 +
            (uint16_t)witness->operation64) ||
        witness->local5184 != expected_local ||
        witness->cell81 != input->cell81 ||
        witness->operation64 != expected_operation ||
        uqcel.vm5184_address != expected_local) {
        failed |= HHS_EXACT_PASS219_FQ_SCOPE_LOCAL_BIJECTION;
        reason = HHS_EXACT_PASS219_FQ_REASON_LOCAL_BIJECTION;
        goto rejected;
    }
    verified |= HHS_EXACT_PASS219_FQ_SCOPE_LOCAL_BIJECTION;

    if (!hhs_fq_big_sum_equal(&input->p, &input->q, &input->P, &input->P)) {
        failed |= HHS_EXACT_PASS219_FQ_SCOPE_PQ_WINDOW;
        reason = HHS_EXACT_PASS219_FQ_REASON_PQ_WINDOW;
        goto rejected;
    }
    verified |= HHS_EXACT_PASS219_FQ_SCOPE_PQ_WINDOW;

    if ((witness->u72_left != 1 && witness->u72_left != -1) ||
        (witness->u72_right != 1 && witness->u72_right != -1) ||
        (int)witness->u72_left * (int)witness->u72_right != 1 ||
        witness->xy_plus_zw != 2) {
        failed |= HHS_EXACT_PASS219_FQ_SCOPE_CONSTRUCTOR;
        reason = HHS_EXACT_PASS219_FQ_REASON_CONSTRUCTOR;
        goto rejected;
    }
    verified |= HHS_EXACT_PASS219_FQ_SCOPE_CONSTRUCTOR;

    expected_lo_shu = hhs_fq_lo_shu_for_cell(input->cell81);
    if (witness->lo_shu_n != expected_lo_shu ||
        witness->lo_shu_n < 1U || witness->lo_shu_n > 9U ||
        witness->lo_shu_antipode != (uint8_t)(10U - witness->lo_shu_n) ||
        (uint16_t)witness->lo_shu_n * (uint16_t)witness->lo_shu_antipode == 0U) {
        failed |= HHS_EXACT_PASS219_FQ_SCOPE_LO_SHU_RECIPROCAL;
        reason = HHS_EXACT_PASS219_FQ_REASON_LO_SHU_RECIPROCAL;
        goto rejected;
    }
    verified |= HHS_EXACT_PASS219_FQ_SCOPE_LO_SHU_RECIPROCAL;

    if (!hhs_fq_mass(
            witness->mass_t, witness->mass_x, witness->mass_y, &D, &N) ||
        witness->mass_D != D || witness->mass_N != N ||
        (witness->sigma != -1 && witness->sigma != 1) ||
        (N == 0 && witness->sigma != 1)) {
        failed |= HHS_EXACT_PASS219_FQ_SCOPE_MASS_FACTORIZATION;
        reason = HHS_EXACT_PASS219_FQ_REASON_MASS_FACTORIZATION;
        goto rejected;
    }
    verified |= HHS_EXACT_PASS219_FQ_SCOPE_MASS_FACTORIZATION;

    if (hhs_exact_pass219_vm81_pqc_hash216_reference_verify(parent) != HHS_EXACT_STATUS_OK ||
        memcmp(input->previous_hash72, parent->receipt_hash72, HHS_EXACT_HASH72_STRLEN) != 0) {
        failed |= HHS_EXACT_PASS219_FQ_SCOPE_PARENT_HASH216;
        reason = HHS_EXACT_PASS219_FQ_REASON_PARENT_HASH216;
        goto rejected;
    }
    verified |= HHS_EXACT_PASS219_FQ_SCOPE_PARENT_HASH216;

    if (out_verified != NULL)
        *out_verified = verified;
    if (out_failed != NULL)
        *out_failed = failed;
    if (out_reason != NULL)
        *out_reason = reason;
    return HHS_EXACT_STATUS_OK;

rejected:
    if (out_verified != NULL)
        *out_verified = verified;
    if (out_failed != NULL)
        *out_failed = failed;
    if (out_reason != NULL)
        *out_reason = reason;
    return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
}

static int hhs_fq_witness_material(
    const HHSExactUQCELInputV1 *input,
    const HHSExactPass219Hash216TransitionViewV1 *parent,
    const HHSExactPass219Hash216FractalQuditWitnessV1 *witness,
    uint8_t material[HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES],
    size_t *out_length
) {
    size_t cursor = 0U;
    if (input == NULL || parent == NULL || witness == NULL ||
        material == NULL || out_length == NULL)
        return 0;
    if (!hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       HHS_P219_FQ_WITNESS_DOMAIN, sizeof(HHS_P219_FQ_WITNESS_DOMAIN) - 1U) ||
        !hhs_fq_append_u32(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                           HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_VERSION) ||
        !hhs_fq_append_u64(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                           witness->declared_scope_mask) ||
        !hhs_fq_append_u16(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                           witness->local5184) ||
        !hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       &witness->hash72_major, 1U) ||
        !hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       &witness->hash72_minor, 1U) ||
        !hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       &witness->cell81, 1U) ||
        !hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       &witness->operation64, 1U) ||
        !hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       &witness->u72_left, 1U) ||
        !hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       &witness->u72_right, 1U) ||
        !hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       &witness->xy_plus_zw, 1U) ||
        !hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       &witness->lo_shu_n, 1U) ||
        !hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       &witness->lo_shu_antipode, 1U) ||
        !hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       &witness->sigma, 1U) ||
        !hhs_fq_append_i64(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                           witness->mass_t) ||
        !hhs_fq_append_i64(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                           witness->mass_x) ||
        !hhs_fq_append_i64(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                           witness->mass_y) ||
        !hhs_fq_append_i64(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                           witness->mass_D) ||
        !hhs_fq_append_i64(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                           witness->mass_N) ||
        !hhs_fq_append_big(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor, &input->P) ||
        !hhs_fq_append_big(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor, &input->p) ||
        !hhs_fq_append_big(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor, &input->q) ||
        !hhs_fq_append_big(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor, &input->delta) ||
        !hhs_fq_append(material, HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES, &cursor,
                       parent->transition_identity216, HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN))
        return 0;
    *out_length = cursor;
    return 1;
}

static uint64_t hhs_fq_transition_signature(
    const HHSExactPass219Hash216TransitionViewV1 *transition
) {
    uint64_t hash = UINT64_C(1469598103934665603);
    if (transition == NULL)
        return 0U;
    hash = hhs_fq_fnv_bytes(
        hash, transition->transition_identity216, HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    hash = hhs_fq_fnv_bytes(
        hash, transition->transition_word216, HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    return hash;
}

static uint64_t hhs_fq_receipt_signature(
    const HHSExactPass219Hash216FractalQuditReceiptV1 *receipt,
    const HHSExactPass219VM81PQCSignatureReceiptV1 *signature_receipt,
    const HHSExactPass219VM81EnvironmentReceiptV1 *environment_receipt
) {
    uint64_t hash = UINT64_C(1469598103934665603);
    if (receipt == NULL || signature_receipt == NULL || environment_receipt == NULL)
        return 0U;
    hash = hhs_fq_fnv_bytes(
        hash, HHS_P219_FQ_RECEIPT_DOMAIN, sizeof(HHS_P219_FQ_RECEIPT_DOMAIN) - 1U);
    hash = hhs_fq_fnv_u64(hash, receipt->declared_scope_mask);
    hash = hhs_fq_fnv_u64(hash, receipt->verified_scope_mask);
    hash = hhs_fq_fnv_u64(hash, receipt->witness_signature64);
    hash = hhs_fq_fnv_u64(hash, receipt->parent_signature64);
    hash = hhs_fq_fnv_u64(hash, receipt->child_signature64);
    hash = hhs_fq_fnv_u64(hash, receipt->inherited_decision_signature64);
    hash = hhs_fq_fnv_u64(hash, receipt->environment_witness_sequence);
    hash = hhs_fq_fnv_bytes(
        hash, receipt->witness_hash72, HHS_EXACT_HASH72_LEN);
    hash = hhs_fq_fnv_bytes(
        hash, receipt->proof_transition.transition_identity216,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    hash = hhs_fq_fnv_bytes(
        hash, signature_receipt->signature_sha256,
        HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_SHA256_BYTES);
    hash = hhs_fq_fnv_bytes(
        hash, environment_receipt->witness_sha256,
        HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    return hash;
}

uint32_t hhs_exact_pass219_hash216_fractal_qudit_admission_version(void) {
    return HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_VERSION;
}

HHSExactStatus hhs_exact_pass219_hash216_fractal_qudit_witness_validate(
    const HHSExactUQCELInputV1 *input,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    const HHSExactPass219Hash216FractalQuditWitnessV1 *witness
) {
    return hhs_fq_prevalidate(
        input, parent_hash216_reference, witness, NULL, NULL, NULL);
}

HHSExactStatus hhs_exact_pass219_hash216_fractal_qudit_hydrate_proof(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *committed_frame,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    const HHSExactPass219RNAAdmissionV1 *admission,
    const HHSExactPass219VM81PQCFirewallReceiptV1 *firewall_receipt,
    const HHSExactPass219VM81PQCSignatureReceiptV1 *signature_receipt,
    const HHSExactPass219VM81EnvironmentReceiptV1 *environment_receipt,
    const HHSExactPass219Hash216FractalQuditWitnessV1 *witness,
    HHSExactPass219Hash216FractalQuditReceiptV1 *out_proof_receipt
) {
    HHSExactStatus status;
    uint64_t verified = 0U;
    uint64_t failed = 0U;
    uint32_t reason = HHS_EXACT_PASS219_FQ_REASON_NONE;
    uint8_t frame_bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t frame_length = 0U;
    char frame_hash72[HHS_EXACT_HASH72_STRLEN];
    uint8_t witness_material[HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES];
    size_t witness_material_length = 0U;
    uint64_t witness_signature;

    if (out_proof_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    hhs_fq_zero_receipt(out_proof_receipt);
    if (input == NULL || committed_frame == NULL || parent_hash216_reference == NULL ||
        admission == NULL || firewall_receipt == NULL || signature_receipt == NULL ||
        environment_receipt == NULL || witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    out_proof_receipt->declared_scope_mask = witness->declared_scope_mask;
    out_proof_receipt->local5184 = witness->local5184;
    out_proof_receipt->hash72_major = witness->hash72_major;
    out_proof_receipt->hash72_minor = witness->hash72_minor;
    out_proof_receipt->cell81 = witness->cell81;
    out_proof_receipt->operation64 = witness->operation64;
    out_proof_receipt->lo_shu_n = witness->lo_shu_n;
    out_proof_receipt->lo_shu_antipode = witness->lo_shu_antipode;
    out_proof_receipt->sigma = witness->sigma;
    out_proof_receipt->mass_D = witness->mass_D;
    out_proof_receipt->mass_N = witness->mass_N;

    status = hhs_fq_prevalidate(
        input, parent_hash216_reference, witness, &verified, &failed, &reason);
    out_proof_receipt->verified_scope_mask = verified;
    out_proof_receipt->failed_scope_mask = failed;
    out_proof_receipt->reason = reason;
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (hhs_exact_vm81_frame_export_le(
            committed_frame, frame_bytes, sizeof(frame_bytes), &frame_length) != HHS_EXACT_STATUS_OK ||
        frame_length != sizeof(frame_bytes)) {
        out_proof_receipt->reason = HHS_EXACT_PASS219_FQ_REASON_CHILD_HASH216;
        out_proof_receipt->failed_scope_mask |= HHS_EXACT_PASS219_FQ_SCOPE_CHILD_HASH216;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    hhs_hash72_compute_bytes(frame_bytes, frame_length, frame_hash72);

    if (admission->struct_size != (uint32_t)sizeof(*admission) ||
        admission->composed.uqcel.decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        admission->composed.uqcel.frame_committed != 1U ||
        admission->composed.uqcel.vm5184_address != witness->local5184 ||
        hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&admission->transition) != HHS_EXACT_STATUS_OK ||
        memcmp(admission->transition.previous_hash72, input->previous_hash72,
               HHS_EXACT_HASH72_STRLEN) != 0 ||
        memcmp(admission->transition.change_hash72, frame_hash72,
               HHS_EXACT_HASH72_STRLEN) != 0 ||
        firewall_receipt->struct_size != (uint32_t)sizeof(*firewall_receipt) ||
        firewall_receipt->decision != HHS_EXACT_PASS219_VM81_PQC_DECISION_COMMITTED ||
        firewall_receipt->halted != 0U ||
        firewall_receipt->parent_hash216_verified != 1U ||
        firewall_receipt->child_hash216_verified != 1U ||
        firewall_receipt->inherited_rna_authority_invoked != 1U ||
        firewall_receipt->canonical_receipt_owned_by_inherited_authority != 1U ||
        firewall_receipt->firewall_is_canonical_authority != 0U ||
        memcmp(firewall_receipt->candidate_hash72, frame_hash72,
               HHS_EXACT_HASH72_STRLEN) != 0 ||
        memcmp(firewall_receipt->parent_hash216_identity,
               parent_hash216_reference->transition_identity216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) != 0 ||
        memcmp(firewall_receipt->child_hash216_identity,
               admission->transition.transition_identity216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) != 0) {
        out_proof_receipt->reason = HHS_EXACT_PASS219_FQ_REASON_CHILD_HASH216;
        out_proof_receipt->failed_scope_mask |= HHS_EXACT_PASS219_FQ_SCOPE_CHILD_HASH216;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    verified |= HHS_EXACT_PASS219_FQ_SCOPE_CHILD_HASH216;

    if (signature_receipt->struct_size != (uint32_t)sizeof(*signature_receipt) ||
        signature_receipt->version != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERSION ||
        signature_receipt->decision != HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_VERIFIED ||
        signature_receipt->provider_available != 1U ||
        signature_receipt->key_derived_from_kernel_root != 1U ||
        signature_receipt->signature_generated_inside_kernel != 1U ||
        signature_receipt->signature_verified_before_vm81 != 1U ||
        signature_receipt->external_key_authority != 0U ||
        signature_receipt->external_signature_authority != 0U ||
        signature_receipt->signature_is_canonical_receipt != 0U ||
        environment_receipt->struct_size != (uint32_t)sizeof(*environment_receipt) ||
        environment_receipt->version != HHS_EXACT_PASS219_VM81_ENV_VERSION ||
        environment_receipt->state != HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING ||
        environment_receipt->decision != HHS_EXACT_PASS219_VM81_ENV_DECISION_READY ||
        environment_receipt->reason != HHS_EXACT_PASS219_VM81_ENV_REASON_NONE ||
        environment_receipt->genesis_verified != 1U ||
        environment_receipt->witness_verified != 1U ||
        environment_receipt->environment_signature_verified != 1U ||
        environment_receipt->canonical_mutation_authority != 0U ||
        environment_receipt->canonical_receipt_authority != 0U) {
        out_proof_receipt->reason = HHS_EXACT_PASS219_FQ_REASON_INHERITED_ADMISSION;
        out_proof_receipt->failed_scope_mask |= HHS_EXACT_PASS219_FQ_SCOPE_SIGNED_ENVIRONMENT;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    verified |= HHS_EXACT_PASS219_FQ_SCOPE_SIGNED_ENVIRONMENT;

    if (!hhs_fq_witness_material(
            input, parent_hash216_reference, witness,
            witness_material, &witness_material_length)) {
        out_proof_receipt->reason = HHS_EXACT_PASS219_FQ_REASON_RECEIPT_REPLAY;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    witness_signature = hhs_fq_fnv_bytes(
        UINT64_C(1469598103934665603), witness_material, witness_material_length);
    hhs_hash72_compute_bytes(
        witness_material, witness_material_length, out_proof_receipt->witness_hash72);

    status = hhs_exact_pass219_vm81_pqc_hash216_reference_init(
        input->previous_hash72,
        out_proof_receipt->witness_hash72,
        admission->transition.receipt_hash72,
        &out_proof_receipt->proof_transition);
    if (status != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_vm81_pqc_hash216_reference_verify(
            &out_proof_receipt->proof_transition) != HHS_EXACT_STATUS_OK) {
        out_proof_receipt->reason = HHS_EXACT_PASS219_FQ_REASON_RECEIPT_REPLAY;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_proof_receipt->verified_scope_mask = verified;
    out_proof_receipt->failed_scope_mask = 0U;
    out_proof_receipt->reason = HHS_EXACT_PASS219_FQ_REASON_NONE;
    out_proof_receipt->witness_signature64 = witness_signature;
    out_proof_receipt->parent_signature64 =
        hhs_fq_transition_signature(parent_hash216_reference);
    out_proof_receipt->child_signature64 =
        hhs_fq_transition_signature(&admission->transition);
    out_proof_receipt->inherited_decision_signature64 = firewall_receipt->decision_signature64;
    out_proof_receipt->environment_witness_sequence = environment_receipt->witness_sequence;
    out_proof_receipt->accepted = 1U;
    out_proof_receipt->scaling_closed = 1U;
    out_proof_receipt->dual_coordinate_verified = 1U;
    out_proof_receipt->pq_window_verified = 1U;
    out_proof_receipt->constructor_verified = 1U;
    out_proof_receipt->lo_shu_reciprocal_verified = 1U;
    out_proof_receipt->mass_factorization_verified = 1U;
    out_proof_receipt->parent_hash216_verified = 1U;
    out_proof_receipt->child_hash216_verified = 1U;
    out_proof_receipt->signed_environment_verified = 1U;
    out_proof_receipt->inherited_canonical_admission_verified = 1U;
    out_proof_receipt->proof_transition_indexed = 1U;
    out_proof_receipt->canonical_vm81_mutation_authority = 0U;
    out_proof_receipt->canonical_hash72_authority = 0U;
    out_proof_receipt->canonical_hash216_authority = 0U;
    out_proof_receipt->canonical_persistence_authority = 0U;
    out_proof_receipt->receipt_clock_authority = 0U;
    out_proof_receipt->floating_point_canonical_authority = 0U;
    out_proof_receipt->receipt_signature64 = hhs_fq_receipt_signature(
        out_proof_receipt, signature_receipt, environment_receipt);

    if (out_proof_receipt->verified_scope_mask != HHS_EXACT_PASS219_FQ_SCOPE_REQUIRED ||
        out_proof_receipt->witness_signature64 == 0U ||
        out_proof_receipt->parent_signature64 == 0U ||
        out_proof_receipt->child_signature64 == 0U ||
        out_proof_receipt->receipt_signature64 == 0U) {
        hhs_fq_zero_receipt(out_proof_receipt);
        out_proof_receipt->reason = HHS_EXACT_PASS219_FQ_REASON_RECEIPT_REPLAY;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hash216_fractal_qudit_receipt_replay(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *committed_frame,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    const HHSExactPass219RNAAdmissionV1 *admission,
    const HHSExactPass219VM81PQCFirewallReceiptV1 *firewall_receipt,
    const HHSExactPass219VM81PQCSignatureReceiptV1 *signature_receipt,
    const HHSExactPass219VM81EnvironmentReceiptV1 *environment_receipt,
    const HHSExactPass219Hash216FractalQuditWitnessV1 *witness,
    const HHSExactPass219Hash216FractalQuditReceiptV1 *proof_receipt
) {
    HHSExactPass219Hash216FractalQuditReceiptV1 expected;
    HHSExactStatus status;
    if (proof_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (proof_receipt->struct_size != (uint32_t)sizeof(*proof_receipt) ||
        proof_receipt->version != HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_VERSION ||
        proof_receipt->namespace_id != HHS_EXACT_PASS219_HASH216_FRACTAL_QUDIT_NAMESPACE ||
        proof_receipt->accepted != 1U ||
        proof_receipt->canonical_vm81_mutation_authority != 0U ||
        proof_receipt->canonical_hash72_authority != 0U ||
        proof_receipt->canonical_hash216_authority != 0U ||
        proof_receipt->canonical_persistence_authority != 0U ||
        proof_receipt->receipt_clock_authority != 0U ||
        proof_receipt->floating_point_canonical_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&expected, 0, sizeof(expected));
    status = hhs_exact_pass219_hash216_fractal_qudit_hydrate_proof(
        input,
        committed_frame,
        parent_hash216_reference,
        admission,
        firewall_receipt,
        signature_receipt,
        environment_receipt,
        witness,
        &expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (memcmp(&expected, proof_receipt, sizeof(expected)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}
