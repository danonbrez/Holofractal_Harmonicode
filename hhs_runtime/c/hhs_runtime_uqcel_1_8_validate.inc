#include "../include/hhs_pass219b_global_zero_sum_closure_1_0.h"

static int hhs_exact_uqcel_lo_shu_selfcheck(void) {
    static const uint8_t matrix[9] = {4U, 9U, 2U, 3U, 5U, 7U, 8U, 1U, 6U};
    static const uint8_t lines[8][3] = {
        {0U, 1U, 2U}, {3U, 4U, 5U}, {6U, 7U, 8U},
        {0U, 3U, 6U}, {1U, 4U, 7U}, {2U, 5U, 8U},
        {0U, 4U, 8U}, {2U, 4U, 6U}
    };
    size_t i;
    for (i = 0U; i < 8U; ++i) {
        uint16_t sum = (uint16_t)matrix[lines[i][0]] +
                       (uint16_t)matrix[lines[i][1]] +
                       (uint16_t)matrix[lines[i][2]];
        if (sum != 15U)
            return 0;
    }
    return 1;
}

uint32_t hhs_exact_uqcel_version(void) {
    return hhs_exact_uqcel_version_word();
}

HHSExactStatus hhs_exact_uqcel_source_sha256(
    uint8_t out_sha256[HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES]
) {
    if (out_sha256 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memcpy(out_sha256, HHS_EXACT_UQCEL_SOURCE_SHA256, HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES);
    return HHS_EXACT_STATUS_OK;
}

static void hhs_exact_uqcel_init_admission(
    const HHSExactUQCELInputV1 *input,
    HHSExactUQCELAdmissionV1 *out
) {
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->uqcel_version = hhs_exact_uqcel_version_word();
    out->profile = input != NULL ? input->profile : HHS_EXACT_UQCEL_PROFILE_NONE;
    out->decision = HHS_EXACT_UQCEL_DECISION_UNRESOLVED;
    out->reject_reason = HHS_EXACT_UQCEL_REASON_NONE;
    out->required_mask = HHS_UQCEL_CONSTRAINT_CORE_REQUIRED;
    out->residual_mask = HHS_UQCEL_RESIDUAL_FULL_SOURCE;
    out->primitive_metric_numerator = -11;
    out->primitive_metric_denominator = 12U;
    out->full_cycle_metric_exponent = -66;
    out->metric_power = 5256U;
}

static HHSExactStatus hhs_exact_uqcel_reject(
    HHSExactUQCELAdmissionV1 *out,
    uint64_t failed_bit,
    HHSExactUQCELRejectReason reason
) {
    out->failed_mask |= failed_bit;
    out->decision = HHS_EXACT_UQCEL_DECISION_REJECT;
    out->reject_reason = (uint32_t)reason;
    return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
}

HHSExactStatus hhs_exact_uqcel_validate(
    const HHSExactUQCELInputV1 *input,
    HHSExactUQCELAdmissionV1 *out_admission
) {
    HHSExactBigBuffer p_squared;
    HHSExactBigBuffer pq;
    HHSExactBigBuffer pq_plus_delta;
    HHSExactBigBuffer ab;
    HHSExactBigBuffer p_fourth;
    HHSExactPhaseProduct product;
    HHSExactPass219BGlobalZeroSumClosureV1 zero_sum_proof;
    uint8_t p_mod4;
    uint8_t q_mod4;
    uint8_t qr_bit;
    uint8_t expected_left;
    uint8_t expected_right;
    uint16_t address;

    if (out_admission == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    hhs_exact_uqcel_init_admission(input, out_admission);
    if (input == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (input->struct_size < sizeof(*input) || input->uqcel_version != hhs_exact_uqcel_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (input->profile != HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1 &&
        input->profile != HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (input->profile == HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1)
        out_admission->required_mask = HHS_UQCEL_CONSTRAINT_FULL_SYMBOLIC_REQUIRED;

    if (memcmp(input->source_envelope_sha256, HHS_EXACT_UQCEL_SOURCE_SHA256,
               HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES) != 0)
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_SOURCE, HHS_EXACT_UQCEL_REASON_SOURCE_HASH);
    out_admission->source_hash_match = 1U;
    out_admission->satisfied_mask |= HHS_UQCEL_CONSTRAINT_SOURCE;

    if (input->profile == HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1) {
        if (hhs_exact_pass219b_global_zero_sum_prove(&zero_sum_proof) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219b_global_zero_sum_verify(&zero_sum_proof) != HHS_EXACT_STATUS_OK)
            return hhs_exact_uqcel_reject(
                out_admission,
                HHS_UQCEL_CONSTRAINT_GLOBAL_ZERO_SUM_CLOSURE,
                HHS_EXACT_UQCEL_REASON_GLOBAL_ZERO_SUM_CLOSURE);
        out_admission->satisfied_mask |= HHS_UQCEL_CONSTRAINT_GLOBAL_ZERO_SUM_CLOSURE;
    }

    if (!hhs_exact_big_view_valid(&input->P, HHS_EXACT_UQCEL_MAX_P_BYTES, 0) ||
        !hhs_exact_big_view_valid(&input->p, HHS_EXACT_UQCEL_MAX_P_BYTES, 0) ||
        !hhs_exact_big_view_valid(&input->q, HHS_EXACT_UQCEL_MAX_P_BYTES, 0) ||
        !hhs_exact_big_view_valid(&input->delta, HHS_EXACT_UQCEL_MAX_P_BYTES, 1) ||
        !hhs_exact_big_view_valid(&input->A, HHS_EXACT_UQCEL_MAX_AB_BYTES, 0) ||
        !hhs_exact_big_view_valid(&input->B, HHS_EXACT_UQCEL_MAX_AB_BYTES, 0))
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_BIGINT_CANONICAL, HHS_EXACT_UQCEL_REASON_BIGINT_ENCODING);
    out_admission->bigint_domain_exact = 1U;
    out_admission->satisfied_mask |= HHS_UQCEL_CONSTRAINT_BIGINT_CANONICAL;

    if (!hhs_exact_uqcel_lo_shu_selfcheck())
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_LOSHU, HHS_EXACT_UQCEL_REASON_BIGINT_ENCODING);
    out_admission->satisfied_mask |= HHS_UQCEL_CONSTRAINT_LOSHU;

    if (out_admission->primitive_metric_numerator != -11 ||
        out_admission->primitive_metric_denominator != 12U ||
        out_admission->full_cycle_metric_exponent != -66 ||
        out_admission->metric_power != 5256U)
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_METRIC, HHS_EXACT_UQCEL_REASON_BIGINT_ENCODING);
    out_admission->satisfied_mask |= HHS_UQCEL_CONSTRAINT_METRIC;

    /*
     * Pass 219 1.15 semantic repair-forward boundary plus Pass 219B I6:
     * the V1 A/B fields remain integer/symmetric compatibility witnesses, not
     * the full-symbolic source A/B terms. Full-symbolic requests now bind the
     * exact global zero-sum closure theorem before reaching the unresolved
     * monolithic residual. The zero-sum theorem is necessary but not sufficient:
     * it cannot clear the aggregate monolithic equality-chain residual.
     * The aggregate monolithic residual remains set.
     */
    if (input->profile == HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1) {
        if ((out_admission->satisfied_mask & HHS_UQCEL_CONSTRAINT_GLOBAL_ZERO_SUM_CLOSURE) == 0U)
            return hhs_exact_uqcel_reject(
                out_admission,
                HHS_UQCEL_CONSTRAINT_GLOBAL_ZERO_SUM_CLOSURE,
                HHS_EXACT_UQCEL_REASON_GLOBAL_ZERO_SUM_CLOSURE);
        out_admission->decision = HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN;
        out_admission->reject_reason = HHS_EXACT_UQCEL_REASON_FULL_SYMBOLIC_RESIDUAL;
        return HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN;
    }

    if (!hhs_exact_big_square_view(&input->P, &p_squared) ||
        !hhs_exact_big_mul_view(&input->p, &input->q, &pq) ||
        !hhs_exact_big_add_buffer_view(&pq, &input->delta, &pq_plus_delta))
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_P_DELTA, HHS_EXACT_UQCEL_REASON_BIGINT_ENCODING);
    if (!hhs_exact_big_equal_raw(
            p_squared.bytes, p_squared.length,
            pq_plus_delta.bytes, pq_plus_delta.length))
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_P_DELTA, HHS_EXACT_UQCEL_REASON_P_DELTA);
    out_admission->satisfied_mask |= HHS_UQCEL_CONSTRAINT_P_DELTA;

    if (!hhs_exact_big_equal_view_buffer(&input->A, &p_squared) ||
        !hhs_exact_big_equal_view_buffer(&input->B, &p_squared))
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_AB_SYMMETRIC, HHS_EXACT_UQCEL_REASON_AB_SYMMETRY);
    out_admission->satisfied_mask |= HHS_UQCEL_CONSTRAINT_AB_SYMMETRIC;

    if (!hhs_exact_big_mul_view(&input->A, &input->B, &ab) ||
        !hhs_exact_big_mul_buffer(&p_squared, &p_squared, &p_fourth))
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_AB_QUARTIC, HHS_EXACT_UQCEL_REASON_BIGINT_ENCODING);
    if (!hhs_exact_big_equal_raw(ab.bytes, ab.length, p_fourth.bytes, p_fourth.length))
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_AB_QUARTIC, HHS_EXACT_UQCEL_REASON_AB_QUARTIC);
    out_admission->satisfied_mask |= HHS_UQCEL_CONSTRAINT_AB_QUARTIC;

    if ((input->p.bytes_be[input->p.byte_length - 1U] & UINT8_C(1)) == 0U ||
        (input->q.bytes_be[input->q.byte_length - 1U] & UINT8_C(1)) == 0U)
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_QR_DOMAIN, HHS_EXACT_UQCEL_REASON_QR_DOMAIN);
    p_mod4 = hhs_exact_big_mod4(&input->p);
    q_mod4 = hhs_exact_big_mod4(&input->q);
    qr_bit = (uint8_t)((p_mod4 == 3U && q_mod4 == 3U) ? 1U : 0U);
    out_admission->qr_bit = qr_bit;
    out_admission->expected_lane = qr_bit ? HHS_EXACT_PHASE_YX : HHS_EXACT_PHASE_XY;
    out_admission->expected_phase = qr_bit ? 36U : 0U;
    out_admission->satisfied_mask |= HHS_UQCEL_CONSTRAINT_QR_DOMAIN;

    expected_left = qr_bit ? HHS_EXACT_PHASE_Y : HHS_EXACT_PHASE_X;
    expected_right = qr_bit ? HHS_EXACT_PHASE_X : HHS_EXACT_PHASE_Y;
    if (input->left_basis8 != expected_left || input->right_basis8 != expected_right ||
        hhs_exact_phase_product(input->left_basis8, input->right_basis8, &product) != HHS_EXACT_STATUS_OK) {
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_QR_PHASE, HHS_EXACT_UQCEL_REASON_QR_PHASE);
    }
    out_admission->observed_phase = product.phase;
    out_admission->ordered_tag = product.ordered_tag;
    if (product.phase != out_admission->expected_phase ||
        product.ordered_tag != hhs_exact_basis_tag(out_admission->expected_lane))
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_QR_PHASE, HHS_EXACT_UQCEL_REASON_QR_PHASE);
    out_admission->satisfied_mask |= HHS_UQCEL_CONSTRAINT_QR_PHASE;

    if (hhs_exact_vm5184_address_encode(
            input->cell81, input->left_basis8, input->right_basis8, &address) != HHS_EXACT_STATUS_OK)
        return hhs_exact_uqcel_reject(
            out_admission, HHS_UQCEL_CONSTRAINT_VM5184, HHS_EXACT_UQCEL_REASON_VM5184);
    out_admission->vm5184_address = address;
    out_admission->satisfied_mask |= HHS_UQCEL_CONSTRAINT_VM5184;

    if ((out_admission->satisfied_mask & out_admission->required_mask) != out_admission->required_mask)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_admission->decision = HHS_EXACT_UQCEL_DECISION_ADMIT;
    out_admission->reject_reason = HHS_EXACT_UQCEL_REASON_NONE;
    return HHS_EXACT_STATUS_OK;
}
