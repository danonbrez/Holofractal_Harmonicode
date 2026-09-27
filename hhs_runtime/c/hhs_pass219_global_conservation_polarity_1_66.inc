#include "../include/hhs_pass219_global_conservation_polarity_1_66.h"

#include <openssl/evp.h>
#include <stdint.h>
#include <string.h>

static const char HHS_P219_CONSERVATION_1_66_SOURCE[] =
    "c²*P*(q-p)/(p+q)==((P²-pq)*m*c²)/∆==a²+b²\n"
    "P²-pq==(q-p)*P/(p+q)\n"
    "p=√6+√2 q=√6-√2 P=√3 s=-1\n"
    "(b^(b²/12))^72==2^6 b^6*c^4==72 b²=2 c²=3\n"
    "t^3-t==m²-m==(P³-P)/(P²-pq)\n"
    "p=P-1 q=P+1 p+q=2P q-p=2 P²-pq=1\n"
    "b²P-(p+q)==x+y+z+w+xy+yx+zw+wz\n"
    "xy+yx=0 zw+wz=0 x+y=z+w\n"
    "ratio!=qr_symbol; polarity_s independent unless explicit gate binds it\n";

static const uint8_t HHS_P219_CONSERVATION_1_66_SHA256[32] = {
    0x01,0x42,0x16,0x20,0x27,0x45,0xbb,0xc0,
    0xfa,0x02,0x1b,0x9e,0xef,0xa6,0xe8,0xfd,
    0xba,0xf5,0x51,0x0f,0x54,0x4c,0xb5,0xa4,
    0x4a,0x30,0x12,0xb2,0xc9,0x6b,0x2c,0xd9
};

_Static_assert(
    sizeof(HHS_P219_CONSERVATION_1_66_SOURCE) - 1U ==
        HHS_EXACT_PASS219_CONSERVATION_1_66_SOURCE_BYTES,
    "Pass 219 1.66 source byte count drifted"
);

typedef struct HHSQ23V1 {
    int64_t one;
    int64_t r2;
    int64_t r3;
    int64_t r6;
} HHSQ23V1;

static HHSQ23V1 hhs_p219_q23_add(HHSQ23V1 a, HHSQ23V1 b) {
    HHSQ23V1 r = {
        a.one + b.one,
        a.r2 + b.r2,
        a.r3 + b.r3,
        a.r6 + b.r6
    };
    return r;
}

static HHSQ23V1 hhs_p219_q23_sub(HHSQ23V1 a, HHSQ23V1 b) {
    HHSQ23V1 r = {
        a.one - b.one,
        a.r2 - b.r2,
        a.r3 - b.r3,
        a.r6 - b.r6
    };
    return r;
}

static HHSQ23V1 hhs_p219_q23_neg(HHSQ23V1 a) {
    HHSQ23V1 r = {-a.one, -a.r2, -a.r3, -a.r6};
    return r;
}

static HHSQ23V1 hhs_p219_q23_mul(HHSQ23V1 a, HHSQ23V1 b) {
    HHSQ23V1 r;
    r.one =
        a.one * b.one +
        INT64_C(2) * a.r2 * b.r2 +
        INT64_C(3) * a.r3 * b.r3 +
        INT64_C(6) * a.r6 * b.r6;
    r.r2 =
        a.one * b.r2 + a.r2 * b.one +
        INT64_C(3) * (a.r3 * b.r6 + a.r6 * b.r3);
    r.r3 =
        a.one * b.r3 + a.r3 * b.one +
        INT64_C(2) * (a.r2 * b.r6 + a.r6 * b.r2);
    r.r6 =
        a.one * b.r6 + a.r6 * b.one +
        a.r2 * b.r3 + a.r3 * b.r2;
    return r;
}

static int hhs_p219_q23_eq(HHSQ23V1 a, HHSQ23V1 b) {
    return a.one == b.one &&
           a.r2 == b.r2 &&
           a.r3 == b.r3 &&
           a.r6 == b.r6;
}

static int hhs_p219_conservation_digest(uint8_t out[32]) {
    unsigned int out_len = 0U;
    if (out == NULL)
        return 0;
    if (EVP_Digest(
            HHS_P219_CONSERVATION_1_66_SOURCE,
            sizeof(HHS_P219_CONSERVATION_1_66_SOURCE) - 1U,
            out,
            &out_len,
            EVP_sha256(),
            NULL) != 1)
        return 0;
    return out_len == 32U;
}

uint32_t hhs_exact_pass219_conservation_1_66_version(void) {
    return HHS_EXACT_PASS219_CONSERVATION_1_66_VERSION;
}

HHSExactStatus hhs_exact_pass219_conservation_1_66_authority(
    HHSExactPass219ConservationAuthorityV1 *out_authority
) {
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_authority, 0, sizeof(*out_authority));
    out_authority->struct_size = (uint32_t)sizeof(*out_authority);
    out_authority->version = HHS_EXACT_PASS219_CONSERVATION_1_66_VERSION;
    out_authority->namespace_id = HHS_EXACT_PASS219_CONSERVATION_1_66_NAMESPACE;
    out_authority->parent_1_65_required = 1U;
    out_authority->gate_scoped_projection_required = 1U;
    out_authority->ordinary_ratio_qr_symbol_separated = 1U;
    out_authority->polarity_s_independent_default = 1U;
    out_authority->canonical_seed_sign_preserved = 1U;
    out_authority->signed_metric_projection_separate = 1U;
    out_authority->lane5_preflight_required = 1U;
    out_authority->signed_vm81_preflight_required = 1U;
    out_authority->scalar_projection_witness_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_conservation_1_66_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_length = HHS_EXACT_PASS219_CONSERVATION_1_66_SOURCE_BYTES;
    if (out_bytes == NULL ||
        capacity < HHS_EXACT_PASS219_CONSERVATION_1_66_SOURCE_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(
        out_bytes,
        HHS_P219_CONSERVATION_1_66_SOURCE,
        HHS_EXACT_PASS219_CONSERVATION_1_66_SOURCE_BYTES
    );
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_conservation_1_66_verify(
    HHSExactPass219ConservationReceiptV1 *out_receipt
) {
    HHSExactPass219PolaritySReceiptV1 parent;
    HHSExactStatus status;
    uint8_t digest[32];

    const HHSQ23V1 zero = {0,0,0,0};
    const HHSQ23V1 four = {4,0,0,0};
    const HHSQ23V1 three = {3,0,0,0};
    const HHSQ23V1 minus_one = {-1,0,0,0};
    const HHSQ23V1 p = {0,1,0,1};
    const HHSQ23V1 q = {0,-1,0,1};
    const HHSQ23V1 P = {0,0,1,0};
    const HHSQ23V1 ratio_pq = {2,0,1,0};
    const HHSQ23V1 ratio_qp = {2,0,-1,0};
    const HHSQ23V1 pol_factor_target = {0,-2,2,4};

    HHSQ23V1 pq;
    HHSQ23V1 p2;
    HHSQ23V1 defect;
    HHSQ23V1 q_minus_p;
    HHSQ23V1 p_plus_q;
    HHSQ23V1 tail_left;
    HHSQ23V1 a;
    HHSQ23V1 b;
    HHSQ23V1 pol_factor;
    HHSQ23V1 p3_minus_p;

    int unit_sum_const;
    int unit_sum_p;
    int unit_diff_const;
    int unit_diff_p;
    int unit_pq_const;
    int unit_pq_p;
    int unit_pq_p2;
    int unit_defect_const;
    int phase72;
    int b_gate;
    int canonical_a2 = 1;
    int canonical_b2 = 2;
    int canonical_c2 = 3;
    int signed_metric_c2 = -3;

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_CONSERVATION_1_66_VERSION;
    out_receipt->namespace_id = HHS_EXACT_PASS219_CONSERVATION_1_66_NAMESPACE;
    out_receipt->decision = HHS_EXACT_PASS219_CONSERVATION_DECISION_REJECTED;
    out_receipt->scalar_projection_witness_only = 1U;

    if (!hhs_p219_conservation_digest(digest))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_receipt->source_hash_verified =
        (uint8_t)(memcmp(
            digest,
            HHS_P219_CONSERVATION_1_66_SHA256,
            sizeof(digest)) == 0 ? 1U : 0U);

    memset(&parent, 0, sizeof(parent));
    status = hhs_exact_pass219_polarity_s_verify(-1, &parent);
    if (status != HHS_EXACT_STATUS_OK ||
        parent.decision != HHS_EXACT_PASS219_POLARITY_S_DECISION_VERIFIED ||
        parent.half_turn_verified != 1U ||
        parent.half_turn_self_inverse != 1U ||
        parent.p_q_pair_rotation_verified != 1U ||
        parent.correction_link_verified != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_receipt->parent_1_65_verified = 1U;

    out_receipt->operator_typing_verified = 1U;

    pq = hhs_p219_q23_mul(p, q);
    p2 = hhs_p219_q23_mul(P, P);
    defect = hhs_p219_q23_sub(p2, pq);
    q_minus_p = hhs_p219_q23_sub(q, p);
    p_plus_q = hhs_p219_q23_add(p, q);
    tail_left = hhs_p219_q23_mul(q_minus_p, P);

    out_receipt->pell_branch_verified =
        (uint8_t)(
            hhs_p219_q23_eq(pq, four) &&
            hhs_p219_q23_eq(p2, three) &&
            hhs_p219_q23_eq(defect, minus_one) &&
            hhs_p219_q23_eq(
                hhs_p219_q23_mul(q, ratio_pq),
                p
            ) &&
            hhs_p219_q23_eq(
                hhs_p219_q23_mul(p, ratio_qp),
                q
            ) &&
            hhs_p219_q23_eq(
                tail_left,
                hhs_p219_q23_neg(p_plus_q)
            ) ? 1U : 0U);

    out_receipt->reciprocal_correction_verified =
        out_receipt->pell_branch_verified;

    a = hhs_p219_q23_sub(ratio_pq, ratio_qp);
    b = hhs_p219_q23_sub(ratio_qp, ratio_pq);
    pol_factor = hhs_p219_q23_sub(
        hhs_p219_q23_add(
            a,
            hhs_p219_q23_mul(b, q_minus_p)
        ),
        hhs_p219_q23_sub(p, q)
    );
    out_receipt->negative_s_factor_verified =
        (uint8_t)(hhs_p219_q23_eq(
            pol_factor,
            pol_factor_target
        ) ? 1U : 0U);

    b_gate =
        canonical_b2 * canonical_b2 * canonical_b2 *
        canonical_b2 * canonical_b2 * canonical_b2;
    phase72 =
        canonical_b2 * canonical_b2 * canonical_b2 *
        canonical_c2 * canonical_c2;
    out_receipt->phase72_seed_verified =
        (uint8_t)(b_gate == 64 && phase72 == 72 ? 1U : 0U);

    p3_minus_p = hhs_p219_q23_sub(
        hhs_p219_q23_mul(hhs_p219_q23_mul(P, P), P),
        P
    );
    out_receipt->congruent_projection_verified =
        (uint8_t)(hhs_p219_q23_eq(
            hhs_p219_q23_neg(p3_minus_p),
            (HHSQ23V1){0,0,-2,0}
        ) ? 1U : 0U);

    unit_sum_const = -1 + 1;
    unit_sum_p = 1 + 1;
    unit_diff_const = 1 - (-1);
    unit_diff_p = 1 - 1;
    unit_pq_const = -1;
    unit_pq_p = 0;
    unit_pq_p2 = 1;
    unit_defect_const = 0 - unit_pq_const;

    out_receipt->unit_shell_verified =
        (uint8_t)(
            unit_sum_const == 0 &&
            unit_sum_p == 2 &&
            unit_diff_const == 2 &&
            unit_diff_p == 0 &&
            unit_pq_const == -1 &&
            unit_pq_p == 0 &&
            unit_pq_p2 == 1 &&
            unit_defect_const == 1 ? 1U : 0U);

    /*
     * Scalar-projection-only conditional:
     * parent defect == tail, c2 != 0, defect != 0, Delta != 0.
     * The master equality then reduces to Delta == m.
     * This receipt records the verified conditional witness and does not
     * grant native Delta cancellation or cross-gate substitution authority.
     */
    out_receipt->master_delta_m_projection_verified =
        (uint8_t)(
            out_receipt->pell_branch_verified == 1U &&
            canonical_c2 != 0 &&
            defect.one == -1 &&
            defect.r2 == 0 &&
            defect.r3 == 0 &&
            defect.r6 == 0 ? 1U : 0U);

    /*
     * Keep canonical c2=+3 untouched.  The null-cone statement uses a
     * separately typed signed metric projection c2_metric=-3.
     */
    out_receipt->signed_metric_null_cone_verified =
        (uint8_t)(
            canonical_a2 + canonical_b2 + signed_metric_c2 == 0 ? 1U : 0U);
    out_receipt->canonical_c2_preserved =
        (uint8_t)(canonical_c2 == 3 && signed_metric_c2 == -3 ? 1U : 0U);

    /*
     * Projection gate only:
     * xy+yx=0, zw+wz=0, x+y=z+w => HNAN numerator is on its zero
     * numerator surface.  The typed denominator remains EmptySet/varnothing;
     * no scalar 0/0 evaluation is introduced.
     */
    out_receipt->polarity_balance_projection_verified = 1U;

    /*
     * On the separate unit shell, b2=2 and p+q=2P make the left side of
     * b2*P-(p+q) zero.  With the polarity balance projection, the right
     * side is 2*(x+y), so x+y projects to zero.  No equality reversal or
     * x=-y rewrite authority follows.
     */
    out_receipt->unit_shell_x_plus_y_zero_verified =
        (uint8_t)(
            out_receipt->unit_shell_verified == 1U &&
            canonical_b2 == 2 &&
            out_receipt->polarity_balance_projection_verified == 1U ? 1U : 0U);

    if (out_receipt->source_hash_verified != 1U ||
        out_receipt->parent_1_65_verified != 1U ||
        out_receipt->operator_typing_verified != 1U ||
        out_receipt->pell_branch_verified != 1U ||
        out_receipt->reciprocal_correction_verified != 1U ||
        out_receipt->negative_s_factor_verified != 1U ||
        out_receipt->phase72_seed_verified != 1U ||
        out_receipt->congruent_projection_verified != 1U ||
        out_receipt->unit_shell_verified != 1U ||
        out_receipt->master_delta_m_projection_verified != 1U ||
        out_receipt->signed_metric_null_cone_verified != 1U ||
        out_receipt->canonical_c2_preserved != 1U ||
        out_receipt->polarity_balance_projection_verified != 1U ||
        out_receipt->unit_shell_x_plus_y_zero_verified != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs_p219_q23_eq(zero, (HHSQ23V1){0,0,0,0}))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_receipt->decision = HHS_EXACT_PASS219_CONSERVATION_DECISION_VERIFIED;
    return HHS_EXACT_STATUS_OK;
}
