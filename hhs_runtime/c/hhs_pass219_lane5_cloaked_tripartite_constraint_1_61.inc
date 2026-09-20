#include "../include/hhs_pass219_lane5_cloaked_tripartite_constraint_1_61.h"

#include <string.h>

#define HHS_P219_T5184_BIG_CAPACITY (HHS_EXACT_UQCEL_MAX_DERIVED_BYTES + 2U)
#define HHS_P219_T5184_COMMIT_MATERIAL_CAPACITY 6144U

typedef struct HHS_P219_T5184_Big {
    uint8_t bytes[HHS_P219_T5184_BIG_CAPACITY];
    size_t length;
} HHS_P219_T5184_Big;

typedef struct HHS_P219_T5184_Signed {
    HHS_P219_T5184_Big magnitude;
    int8_t sign;
} HHS_P219_T5184_Signed;

static int hhs_p219_t5184_view_valid(const HHSExactBigUIntView *view) {
    if (view == NULL || view->struct_size < sizeof(*view) || view->bytes_be == NULL)
        return 0;
    if (view->byte_length == 0U || view->byte_length > HHS_EXACT_UQCEL_MAX_P_BYTES)
        return 0;
    if (view->byte_length > 1U && view->bytes_be[0] == 0U)
        return 0;
    return 1;
}

static void hhs_p219_t5184_big_from_view(
    HHS_P219_T5184_Big *out,
    const HHSExactBigUIntView *view
) {
    memset(out, 0, sizeof(*out));
    out->length = (size_t)view->byte_length;
    memcpy(out->bytes, view->bytes_be, out->length);
}

static int hhs_p219_t5184_big_is_zero(const HHS_P219_T5184_Big *value) {
    return value->length == 1U && value->bytes[0] == 0U;
}

static int hhs_p219_t5184_big_equal(
    const HHS_P219_T5184_Big *a,
    const HHS_P219_T5184_Big *b
) {
    return a->length == b->length && memcmp(a->bytes, b->bytes, a->length) == 0;
}

static int hhs_p219_t5184_big_cmp(
    const HHS_P219_T5184_Big *a,
    const HHS_P219_T5184_Big *b
) {
    int cmp;
    if (a->length < b->length) return -1;
    if (a->length > b->length) return 1;
    cmp = memcmp(a->bytes, b->bytes, a->length);
    return cmp < 0 ? -1 : (cmp > 0 ? 1 : 0);
}

static int hhs_p219_t5184_big_add(
    const HHS_P219_T5184_Big *a,
    const HHS_P219_T5184_Big *b,
    HHS_P219_T5184_Big *out
) {
    uint8_t reversed[HHS_P219_T5184_BIG_CAPACITY];
    size_t max_length = a->length > b->length ? a->length : b->length;
    size_t i;
    uint16_t carry = 0U;

    if (max_length + 1U > HHS_P219_T5184_BIG_CAPACITY)
        return 0;
    memset(reversed, 0, sizeof(reversed));
    for (i = 0U; i < max_length; ++i) {
        uint16_t av = i < a->length ? a->bytes[a->length - 1U - i] : 0U;
        uint16_t bv = i < b->length ? b->bytes[b->length - 1U - i] : 0U;
        uint16_t sum = (uint16_t)(av + bv + carry);
        reversed[i] = (uint8_t)(sum & UINT16_C(0xff));
        carry = (uint16_t)(sum >> 8U);
    }
    if (carry != 0U)
        reversed[max_length++] = (uint8_t)carry;

    memset(out, 0, sizeof(*out));
    out->length = max_length;
    for (i = 0U; i < max_length; ++i)
        out->bytes[max_length - 1U - i] = reversed[i];
    return 1;
}

static int hhs_p219_t5184_big_sub_abs(
    const HHS_P219_T5184_Big *larger,
    const HHS_P219_T5184_Big *smaller,
    HHS_P219_T5184_Big *out
) {
    uint8_t reversed[HHS_P219_T5184_BIG_CAPACITY];
    size_t i;
    int16_t borrow = 0;
    size_t length;

    if (hhs_p219_t5184_big_cmp(larger, smaller) < 0)
        return 0;
    memset(reversed, 0, sizeof(reversed));
    for (i = 0U; i < larger->length; ++i) {
        int16_t av = (int16_t)larger->bytes[larger->length - 1U - i];
        int16_t bv = i < smaller->length
            ? (int16_t)smaller->bytes[smaller->length - 1U - i] : 0;
        int16_t diff = (int16_t)(av - bv - borrow);
        if (diff < 0) {
            diff = (int16_t)(diff + 256);
            borrow = 1;
        } else {
            borrow = 0;
        }
        reversed[i] = (uint8_t)diff;
    }
    if (borrow != 0)
        return 0;

    length = larger->length;
    while (length > 1U && reversed[length - 1U] == 0U)
        --length;
    memset(out, 0, sizeof(*out));
    out->length = length;
    for (i = 0U; i < length; ++i)
        out->bytes[length - 1U - i] = reversed[i];
    return 1;
}

static int hhs_p219_t5184_big_mul(
    const HHS_P219_T5184_Big *a,
    const HHS_P219_T5184_Big *b,
    HHS_P219_T5184_Big *out
) {
    uint64_t accum[HHS_P219_T5184_BIG_CAPACITY + 1U];
    size_t i;
    size_t j;
    size_t full_length;

    if (a->length + b->length > HHS_P219_T5184_BIG_CAPACITY + 1U)
        return 0;
    memset(accum, 0, sizeof(accum));
    for (i = 0U; i < a->length; ++i) {
        uint64_t av = a->bytes[a->length - 1U - i];
        for (j = 0U; j < b->length; ++j) {
            uint64_t bv = b->bytes[b->length - 1U - j];
            accum[i + j] += av * bv;
        }
    }

    full_length = a->length + b->length + 1U;
    if (full_length > HHS_P219_T5184_BIG_CAPACITY + 1U)
        return 0;
    for (i = 0U; i + 1U < full_length; ++i) {
        accum[i + 1U] += accum[i] >> 8U;
        accum[i] &= UINT64_C(0xff);
    }
    while (full_length > 1U && accum[full_length - 1U] == 0U)
        --full_length;
    if (full_length > HHS_P219_T5184_BIG_CAPACITY)
        return 0;

    memset(out, 0, sizeof(*out));
    out->length = full_length;
    for (i = 0U; i < full_length; ++i)
        out->bytes[full_length - 1U - i] = (uint8_t)accum[i];
    return 1;
}

static int hhs_p219_t5184_signed_diff(
    const HHS_P219_T5184_Big *a,
    const HHS_P219_T5184_Big *b,
    HHS_P219_T5184_Signed *out
) {
    int cmp = hhs_p219_t5184_big_cmp(a, b);
    memset(out, 0, sizeof(*out));
    if (cmp == 0) {
        out->magnitude.length = 1U;
        out->magnitude.bytes[0] = 0U;
        out->sign = 0;
        return 1;
    }
    if (cmp > 0) {
        if (!hhs_p219_t5184_big_sub_abs(a, b, &out->magnitude))
            return 0;
        out->sign = 1;
    } else {
        if (!hhs_p219_t5184_big_sub_abs(b, a, &out->magnitude))
            return 0;
        out->sign = -1;
    }
    return 1;
}

static int hhs_p219_t5184_signed_equal_positive(
    const HHS_P219_T5184_Signed *a,
    const HHS_P219_T5184_Big *b
) {
    if (hhs_p219_t5184_big_is_zero(b))
        return a->sign == 0 && hhs_p219_t5184_big_is_zero(&a->magnitude);
    return a->sign == 1 && hhs_p219_t5184_big_equal(&a->magnitude, b);
}

static int hhs_p219_t5184_append(
    uint8_t *material,
    size_t capacity,
    size_t *offset,
    const void *bytes,
    size_t length
) {
    if (*offset > capacity || length > capacity - *offset)
        return 0;
    memcpy(material + *offset, bytes, length);
    *offset += length;
    return 1;
}

static int hhs_p219_t5184_append_view(
    uint8_t *material,
    size_t capacity,
    size_t *offset,
    const HHSExactBigUIntView *view
) {
    uint32_t length = view->byte_length;
    return hhs_p219_t5184_append(material, capacity, offset, &length, sizeof(length)) &&
           hhs_p219_t5184_append(material, capacity, offset, view->bytes_be, (size_t)length);
}

uint32_t hhs_exact_pass219_lane5_tripartite_version(void) {
    return HHS_EXACT_PASS219_LANE5_TRIPARTITE_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_tripartite_authority(
    HHSExactPass219Lane5TripartiteAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5TripartiteAuthorityV1 a;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&a, 0, sizeof(a));
    a.struct_size = (uint32_t)sizeof(a);
    a.version = HHS_EXACT_PASS219_LANE5_TRIPARTITE_VERSION;
    a.namespace_id = HHS_EXACT_PASS219_LANE5_TRIPARTITE_NAMESPACE;
    a.theorem_revision = 5U;
    a.vm81_cells = 81U;
    a.local_cell_width = 64U;
    a.serialization_characters = 5184U;
    a.theorem_hhs_t5184_005 = 1U;
    a.ordered_curvature_surface_preserved = 1U;
    a.transition_surface_preserved = 1U;
    a.payload_delta_surface_preserved = 1U;
    a.exact_bigint_only = 1U;
    a.signed_difference_exact = 1U;
    a.equality_by_cross_product = 1U;
    a.denominator_cancellation_allowed = 0U;
    a.division_by_zero_allowed = 0U;
    a.fixed_5184_binding_required = 1U;
    a.rna_cell_wall_required_downstream = 1U;
    a.pqc_witness_required_downstream = 1U;
    a.exact_cpu_vm81_replay_required_downstream = 1U;
    a.hash216_receipt_only = 1U;
    a.legacy_physics_semantics_allowed = 0U;
    a.floating_point_canonical_authority = 0U;
    a.canonical_vm81_mutation_authority = 0U;
    a.canonical_hash72_authority = 0U;
    a.canonical_hash216_commit_authority = 0U;
    a.canonical_persistence_authority = 0U;
    *out_authority = a;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_tripartite_verify(
    const HHSExactPass219Lane5TripartiteInputV1 *input,
    HHSExactPass219Lane5TripartiteReceiptV1 *out_receipt
) {
    HHS_P219_T5184_Big gamma, rho, sigma, omega, P, p, q;
    HHS_P219_T5184_Big phase_denominator, p_sq, pq;
    HHS_P219_T5184_Big tmp1, tmp2, curvature_rhs;
    HHS_P219_T5184_Big transition_lhs_mag, payload_lhs_mag, payload_rhs;
    HHS_P219_T5184_Signed q_minus_p, transition, curvature_lhs, transition_lhs, payload_lhs;
    uint8_t material[HHS_P219_T5184_COMMIT_MATERIAL_CAPACITY];
    size_t material_length = 0U;
    static const char domain[] = "HHS-T5184-005|PASS219|LANE5|TRIPARTITE|1.61";

    if (input == NULL || out_receipt == NULL ||
        input->struct_size != sizeof(*input) ||
        input->version != HHS_EXACT_PASS219_LANE5_TRIPARTITE_VERSION ||
        out_receipt->struct_size != sizeof(*out_receipt)) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    if (!hhs_p219_t5184_view_valid(&input->Gamma_macro) ||
        !hhs_p219_t5184_view_valid(&input->Rho_payload) ||
        !hhs_p219_t5184_view_valid(&input->Sigma_2D) ||
        !hhs_p219_t5184_view_valid(&input->Omega_root) ||
        !hhs_p219_t5184_view_valid(&input->P_macro) ||
        !hhs_p219_t5184_view_valid(&input->p_ingress) ||
        !hhs_p219_t5184_view_valid(&input->q_egress)) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }

    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_LANE5_TRIPARTITE_VERSION;
    out_receipt->candidate_only = 1U;
    out_receipt->requires_rna_cell_wall = 1U;
    out_receipt->requires_pqc_witness = 1U;
    out_receipt->requires_exact_cpu_vm81_replay = 1U;

    if (input->serialization_5184 == NULL ||
        input->serialization_length != HHS_EXACT_PASS219_LANE5_TRIPARTITE_SERIALIZATION_CHARS) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_SERIALIZATION_WIDTH;
        return HHS_EXACT_STATUS_OK;
    }
    out_receipt->serialization_width_verified = 1U;
    hhs_hash216_compute_bytes(
        input->serialization_5184,
        input->serialization_length,
        out_receipt->serialization_hash216
    );

    hhs_p219_t5184_big_from_view(&gamma, &input->Gamma_macro);
    hhs_p219_t5184_big_from_view(&rho, &input->Rho_payload);
    hhs_p219_t5184_big_from_view(&sigma, &input->Sigma_2D);
    hhs_p219_t5184_big_from_view(&omega, &input->Omega_root);
    hhs_p219_t5184_big_from_view(&P, &input->P_macro);
    hhs_p219_t5184_big_from_view(&p, &input->p_ingress);
    hhs_p219_t5184_big_from_view(&q, &input->q_egress);

    if (hhs_p219_t5184_big_is_zero(&omega)) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_DELTA_ZERO;
        return HHS_EXACT_STATUS_OK;
    }
    out_receipt->omega_nonzero = 1U;

    if (!hhs_p219_t5184_big_add(&p, &q, &phase_denominator))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (hhs_p219_t5184_big_is_zero(&phase_denominator)) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_PHASE_DENOMINATOR_ZERO;
        return HHS_EXACT_STATUS_OK;
    }
    out_receipt->phase_denominator_nonzero = 1U;

    if (!hhs_p219_t5184_signed_diff(&q, &p, &q_minus_p))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    out_receipt->q_minus_p_sign = q_minus_p.sign;

    if (!hhs_p219_t5184_big_mul(&P, &P, &p_sq) ||
        !hhs_p219_t5184_big_mul(&p, &q, &pq) ||
        !hhs_p219_t5184_signed_diff(&p_sq, &pq, &transition))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    out_receipt->transition_coefficient_sign = transition.sign;

    if (!hhs_p219_t5184_big_mul(&gamma, &P, &tmp1) ||
        !hhs_p219_t5184_big_mul(&tmp1, &q_minus_p.magnitude, &curvature_lhs.magnitude) ||
        !hhs_p219_t5184_big_mul(&sigma, &phase_denominator, &curvature_rhs))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    curvature_lhs.sign = hhs_p219_t5184_big_is_zero(&curvature_lhs.magnitude) ? 0 : q_minus_p.sign;
    out_receipt->curvature_surface_equal =
        (uint8_t)hhs_p219_t5184_signed_equal_positive(&curvature_lhs, &curvature_rhs);

    if (!hhs_p219_t5184_big_mul(&gamma, &transition.magnitude, &transition_lhs_mag))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    transition_lhs.magnitude = transition_lhs_mag;
    transition_lhs.sign = hhs_p219_t5184_big_is_zero(&transition_lhs_mag) ? 0 : transition.sign;
    out_receipt->transition_surface_equal =
        (uint8_t)hhs_p219_t5184_signed_equal_positive(&transition_lhs, &sigma);

    if (!hhs_p219_t5184_big_mul(&transition.magnitude, &rho, &tmp1) ||
        !hhs_p219_t5184_big_mul(&tmp1, &gamma, &payload_lhs_mag) ||
        !hhs_p219_t5184_big_mul(&sigma, &omega, &payload_rhs))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    payload_lhs.magnitude = payload_lhs_mag;
    payload_lhs.sign = hhs_p219_t5184_big_is_zero(&payload_lhs_mag) ? 0 : transition.sign;
    out_receipt->payload_surface_equal =
        (uint8_t)hhs_p219_t5184_signed_equal_positive(&payload_lhs, &payload_rhs);

    if (out_receipt->curvature_surface_equal == 0U) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_CURVATURE_MISMATCH;
    } else if (out_receipt->transition_surface_equal == 0U) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_TRANSITION_SURFACE_MISMATCH;
    } else if (out_receipt->payload_surface_equal == 0U) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_PAYLOAD_MISMATCH;
    } else {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_TRIPARTITE_REASON_NONE;
        out_receipt->arithmetic_closure_delta_e_zero = 1U;
        out_receipt->closure_valid = 1U;
    }

    memset(material, 0, sizeof(material));
    if (!hhs_p219_t5184_append(material, sizeof(material), &material_length, domain, sizeof(domain) - 1U) ||
        !hhs_p219_t5184_append_view(material, sizeof(material), &material_length, &input->Gamma_macro) ||
        !hhs_p219_t5184_append_view(material, sizeof(material), &material_length, &input->Rho_payload) ||
        !hhs_p219_t5184_append_view(material, sizeof(material), &material_length, &input->Sigma_2D) ||
        !hhs_p219_t5184_append_view(material, sizeof(material), &material_length, &input->Omega_root) ||
        !hhs_p219_t5184_append_view(material, sizeof(material), &material_length, &input->P_macro) ||
        !hhs_p219_t5184_append_view(material, sizeof(material), &material_length, &input->p_ingress) ||
        !hhs_p219_t5184_append_view(material, sizeof(material), &material_length, &input->q_egress) ||
        !hhs_p219_t5184_append(
            material, sizeof(material), &material_length,
            out_receipt->serialization_hash216, HHS_HASH216_BYTES_LEN
        ) ||
        !hhs_p219_t5184_append(
            material, sizeof(material), &material_length,
            &out_receipt->curvature_surface_equal,
            sizeof(out_receipt->curvature_surface_equal)
        ) ||
        !hhs_p219_t5184_append(
            material, sizeof(material), &material_length,
            &out_receipt->transition_surface_equal,
            sizeof(out_receipt->transition_surface_equal)
        ) ||
        !hhs_p219_t5184_append(
            material, sizeof(material), &material_length,
            &out_receipt->payload_surface_equal,
            sizeof(out_receipt->payload_surface_equal)
        )) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    hhs_hash216_compute_bytes(material, material_length, out_receipt->commit_hash216);
    return HHS_EXACT_STATUS_OK;
}
