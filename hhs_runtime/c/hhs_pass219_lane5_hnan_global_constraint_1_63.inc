#include "../include/hhs_pass219_lane5_hnan_global_constraint_1_63.h"

#include <stdint.h>
#include <string.h>

static const HHSExactPass219HNANRuleV1 HHS_P219_HNAN_RULES[
    HHS_EXACT_PASS219_HNAN_GLOBAL_RULE_COUNT
] = {
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 1U,
     HHS_EXACT_HNAN_NODE_ZERO, HHS_EXACT_HNAN_NODE_EMPTYSET,
     HHS_EXACT_HNAN_REL_ORDERED_CLOSURE, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 2U,
     HHS_EXACT_HNAN_NODE_EMPTYSET, HHS_EXACT_HNAN_NODE_AB_P4_EMPTYSET,
     HHS_EXACT_HNAN_REL_ORDERED_CLOSURE, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 3U,
     HHS_EXACT_HNAN_NODE_AB_P4_EMPTYSET, HHS_EXACT_HNAN_NODE_HNAN,
     HHS_EXACT_HNAN_REL_ORDERED_CLOSURE, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 4U,
     HHS_EXACT_HNAN_NODE_ZERO, HHS_EXACT_HNAN_NODE_XYZW_SUM,
     HHS_EXACT_HNAN_REL_TYPED_VIEW, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 5U,
     HHS_EXACT_HNAN_NODE_U72, HHS_EXACT_HNAN_NODE_U0,
     HHS_EXACT_HNAN_REL_PHASE_CLOSURE, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 6U,
     HHS_EXACT_HNAN_NODE_INFINITY, HHS_EXACT_HNAN_NODE_DELTA,
     HHS_EXACT_HNAN_REL_DIRECTED_RECIPROCAL, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 7U,
     HHS_EXACT_HNAN_NODE_DELTA, HHS_EXACT_HNAN_NODE_X,
     HHS_EXACT_HNAN_REL_DIRECTED_RECIPROCAL, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 8U,
     HHS_EXACT_HNAN_NODE_INFINITY_DELTA, HHS_EXACT_HNAN_NODE_BX5184,
     HHS_EXACT_HNAN_REL_UNBOUNDED_CARRIER, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 9U,
     HHS_EXACT_HNAN_NODE_P, HHS_EXACT_HNAN_NODE_BX5184_OVER_DELTA,
     HHS_EXACT_HNAN_REL_GLOBAL_DENOMINATOR, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 10U,
     HHS_EXACT_HNAN_NODE_ONE_OVER_ZERO, HHS_EXACT_HNAN_NODE_HNAN_GATE,
     HHS_EXACT_HNAN_REL_HNAN_BOUNDARY, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 11U,
     HHS_EXACT_HNAN_NODE_J2_ZERO, HHS_EXACT_HNAN_NODE_HNAN_GATE,
     HHS_EXACT_HNAN_REL_JORDAN_CORRESPONDENCE, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 12U,
     HHS_EXACT_HNAN_NODE_XY, HHS_EXACT_HNAN_NODE_YX,
     HHS_EXACT_HNAN_REL_NONCOMMUTATIVE_DISTINCTION, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 13U,
     HHS_EXACT_HNAN_NODE_ZW, HHS_EXACT_HNAN_NODE_WZ,
     HHS_EXACT_HNAN_REL_NONCOMMUTATIVE_DISTINCTION, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 14U,
     HHS_EXACT_HNAN_NODE_X, HHS_EXACT_HNAN_NODE_GAMMA_X,
     HHS_EXACT_HNAN_REL_DIRECTED_TYPED_IDENTITY, 1U,1U,1U,0U,0U,0U,0U,0U},
    {sizeof(HHSExactPass219HNANRuleV1), HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION, 15U,
     HHS_EXACT_HNAN_NODE_U0, HHS_EXACT_HNAN_NODE_ZERO_POWER4,
     HHS_EXACT_HNAN_REL_TYPED_VIEW, 1U,1U,1U,0U,0U,0U,0U,0U}
};

static uint64_t hhs_p219_hnan_mix(uint64_t h, uint64_t v) {
    unsigned shift;
    for (shift = 0U; shift < 64U; shift += 8U) {
        h ^= (v >> shift) & UINT64_C(0xff);
        h *= UINT64_C(1099511628211);
    }
    return h;
}

static const HHSExactPass219HNANRuleV1 *hhs_p219_hnan_rule(uint32_t rule_id) {
    if (rule_id == 0U || rule_id > HHS_EXACT_PASS219_HNAN_GLOBAL_RULE_COUNT)
        return NULL;
    return &HHS_P219_HNAN_RULES[rule_id - 1U];
}

static void hhs_p219_hnan_zero_resolution(
    HHSExactPass219HNANResolutionV1 *r
) {
    memset(r, 0, sizeof(*r));
    r->struct_size = (uint32_t)sizeof(*r);
    r->version = HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
    r->decision = HHS_EXACT_HNAN_DECISION_INVALID;
    r->reason = HHS_EXACT_HNAN_REASON_INVALID_ARGUMENT;
}

static void hhs_p219_hnan_zero_receipt(
    HHSExactPass219HNANGlobalReceiptV1 *r
) {
    memset(r, 0, sizeof(*r));
    r->struct_size = (uint32_t)sizeof(*r);
    r->version = HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
    r->namespace_id = HHS_EXACT_PASS219_HNAN_GLOBAL_NAMESPACE;
    r->decision = HHS_EXACT_HNAN_DECISION_INVALID;
    r->reason = HHS_EXACT_HNAN_REASON_INVALID_ARGUMENT;
    r->required_rule_mask = HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES;
    r->first_rejected_index = UINT32_MAX;
    r->first_unresolved_index = UINT32_MAX;
    r->candidate_only = 1U;
}

static int hhs_p219_hnan_rank(
    const int64_t *input,
    size_t rows,
    size_t cols
) {
    int64_t work[16][4];
    size_t r;
    size_t c;
    size_t rank = 0U;
    size_t col = 0U;

    if (input == NULL || rows == 0U || rows > 16U || cols == 0U || cols > 4U)
        return -1;
    memset(work, 0, sizeof(work));
    for (r = 0U; r < rows; ++r)
        for (c = 0U; c < cols; ++c)
            work[r][c] = input[r * cols + c];

    while (rank < rows && col < cols) {
        size_t pivot = rank;
        int found = 0;
        for (r = rank; r < rows; ++r) {
            if (work[r][col] != 0) {
                pivot = r;
                found = 1;
                break;
            }
        }
        if (!found) {
            ++col;
            continue;
        }
        if (pivot != rank) {
            for (c = 0U; c < cols; ++c) {
                int64_t tmp = work[rank][c];
                work[rank][c] = work[pivot][c];
                work[pivot][c] = tmp;
            }
        }
        for (r = rank + 1U; r < rows; ++r) {
            int64_t factor;
            int64_t pivot_value;
            if (work[r][col] == 0)
                continue;
            factor = work[r][col];
            pivot_value = work[rank][col];
            for (c = col; c < cols; ++c)
                work[r][c] =
                    work[r][c] * pivot_value - work[rank][c] * factor;
        }
        ++rank;
        ++col;
    }
    return (int)rank;
}

static void hhs_p219_hnan_matmul(
    const int64_t a[4][4],
    const int64_t b[4][4],
    int64_t out[4][4]
) {
    size_t i, j, k;
    for (i = 0U; i < 4U; ++i) {
        for (j = 0U; j < 4U; ++j) {
            int64_t v = 0;
            for (k = 0U; k < 4U; ++k)
                v += a[i][k] * b[k][j];
            out[i][j] = v;
        }
    }
}

static int hhs_p219_hnan_jordan_verify(
    HHSExactPass219HNANGlobalReceiptV1 *receipt
) {
    static const int64_t m[4][4] = {
        {0,0,0,1},
        {1,0,1,1},
        {1,1,1,0},
        {0,1,0,0}
    };
    static const int64_t identity[4][4] = {
        {1,0,0,0},
        {0,1,0,0},
        {0,0,1,0},
        {0,0,0,1}
    };
    int64_t m2[4][4];
    int64_t m3[4][4];
    int64_t m4[4][4];
    int64_t krylov[16][4];
    int rank_m;
    int rank_m2;
    int rank_k;
    size_t i, j;
    int recurrence = 1;

    hhs_p219_hnan_matmul(m, m, m2);
    hhs_p219_hnan_matmul(m2, m, m3);
    hhs_p219_hnan_matmul(m3, m, m4);

    rank_m = hhs_p219_hnan_rank(&m[0][0], 4U, 4U);
    rank_m2 = hhs_p219_hnan_rank(&m2[0][0], 4U, 4U);
    for (i = 0U; i < 4U; ++i) {
        for (j = 0U; j < 4U; ++j) {
            const size_t p = i * 4U + j;
            krylov[p][0] = identity[i][j];
            krylov[p][1] = m[i][j];
            krylov[p][2] = m2[i][j];
            krylov[p][3] = m3[i][j];
            if (m4[i][j] != m3[i][j] + 2 * m2[i][j])
                recurrence = 0;
        }
    }
    rank_k = hhs_p219_hnan_rank(&krylov[0][0], 16U, 4U);
    if (rank_m != 3 || rank_m2 != 2 || rank_k != 4 || !recurrence)
        return 0;

    receipt->rank_m01 = 3U;
    receipt->nullity_m01 = 1U;
    receipt->nullity_m01_squared = 2U;
    receipt->jordan_depth2_verified = 1U;
    receipt->minimal_polynomial_degree4_verified = 1U;
    receipt->degree4_recurrence_verified = 1U;
    return 1;
}

uint32_t hhs_exact_pass219_hnan_global_version(void) {
    return HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
}

HHSExactStatus hhs_exact_pass219_hnan_global_authority(
    HHSExactPass219HNANAuthorityV1 *out_authority
) {
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_authority, 0, sizeof(*out_authority));
    out_authority->struct_size = (uint32_t)sizeof(*out_authority);
    out_authority->version = HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
    out_authority->namespace_id = HHS_EXACT_PASS219_HNAN_GLOBAL_NAMESPACE;
    out_authority->mandatory_rule_count = HHS_EXACT_PASS219_HNAN_GLOBAL_RULE_COUNT;
    out_authority->mandatory_rule_mask = HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES;
    out_authority->system_wide_lane5_constraint = 1U;
    out_authority->vm81_preflight_required = 1U;
    out_authority->signed_environmental_preflight_required = 1U;
    out_authority->exact_integer_only = 1U;
    out_authority->ordered_source_preserving = 1U;
    out_authority->typed_projection_only = 1U;
    out_authority->contradiction_resolution_fail_closed = 1U;
    out_authority->jordan_hnan_correspondence = 1U;
    out_authority->delta_global_denominator = 1U;
    out_authority->infinity_symbolic_unbounded_carrier = 1U;
    out_authority->bx5184_relation_preserved = 1U;
    out_authority->u0_phase_closure_preserved = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hnan_global_rule(
    uint32_t rule_id,
    HHSExactPass219HNANRuleV1 *out_rule
) {
    const HHSExactPass219HNANRuleV1 *rule;
    if (out_rule == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    rule = hhs_p219_hnan_rule(rule_id);
    if (rule == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_rule = *rule;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hnan_resolve(
    const HHSExactPass219HNANClaimV1 *claim,
    HHSExactPass219HNANResolutionV1 *out_resolution
) {
    const HHSExactPass219HNANRuleV1 *rule;
    if (out_resolution == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    hhs_p219_hnan_zero_resolution(out_resolution);
    if (claim == NULL ||
        claim->struct_size != sizeof(*claim) ||
        claim->version != HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    out_resolution->rule_id = claim->rule_id;
    out_resolution->lhs_node = claim->lhs_node;
    out_resolution->rhs_node = claim->rhs_node;
    out_resolution->relation = claim->relation;

    if (claim->scalar_substitution_requested) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_SCALARIZATION;
        return HHS_EXACT_STATUS_OK;
    }
    if (claim->delta_cancellation_requested) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_DELTA_CANCELLATION;
        return HHS_EXACT_STATUS_OK;
    }
    if (claim->floating_infinity_requested) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_FLOAT_INFINITY;
        return HHS_EXACT_STATUS_OK;
    }
    if (claim->commutation_requested) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_COMMUTATION;
        return HHS_EXACT_STATUS_OK;
    }
    if (claim->emptyset_cancellation_requested) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_EMPTYSET_CANCELLATION;
        return HHS_EXACT_STATUS_OK;
    }
    if (claim->equality_reversal_requested) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_EQUALITY_REVERSAL;
        return HHS_EXACT_STATUS_OK;
    }
    if (!claim->source_order_preserved) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_SOURCE_ORDER;
        return HHS_EXACT_STATUS_OK;
    }
    if (!claim->typed_identity_preserved) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_TYPE_ERASURE;
        return HHS_EXACT_STATUS_OK;
    }

    rule = hhs_p219_hnan_rule(claim->rule_id);
    if (rule == NULL) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_UNRESOLVED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_UNKNOWN_RULE;
        return HHS_EXACT_STATUS_OK;
    }
    if (claim->relation != rule->relation) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_RELATION_MISMATCH;
        return HHS_EXACT_STATUS_OK;
    }
    if (claim->lhs_node == rule->rhs_node &&
        claim->rhs_node == rule->lhs_node &&
        rule->directional) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_SOURCE_ORDER;
        return HHS_EXACT_STATUS_OK;
    }
    if (claim->lhs_node != rule->lhs_node ||
        claim->rhs_node != rule->rhs_node) {
        out_resolution->decision = HHS_EXACT_HNAN_DECISION_UNRESOLVED;
        out_resolution->reason = HHS_EXACT_HNAN_REASON_NODE_MISMATCH;
        return HHS_EXACT_STATUS_OK;
    }

    out_resolution->decision = HHS_EXACT_HNAN_DECISION_VERIFIED;
    out_resolution->reason = HHS_EXACT_HNAN_REASON_NONE;
    out_resolution->exact_rule_match = 1U;
    out_resolution->source_order_preserved = 1U;
    out_resolution->typed_identity_preserved = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hnan_resolve_set(
    const HHSExactPass219HNANClaimV1 *claims,
    size_t claim_count,
    HHSExactPass219HNANGlobalReceiptV1 *out_receipt
) {
    size_t i;
    uint64_t signature = UINT64_C(1469598103934665603);

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    hhs_p219_hnan_zero_receipt(out_receipt);
    if (claims == NULL || claim_count == 0U ||
        claim_count > HHS_EXACT_PASS219_HNAN_GLOBAL_RULE_COUNT)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    out_receipt->request_count = (uint32_t)claim_count;
    out_receipt->decision = HHS_EXACT_HNAN_DECISION_VERIFIED;
    out_receipt->reason = HHS_EXACT_HNAN_REASON_NONE;

    for (i = 0U; i < claim_count; ++i) {
        HHSExactPass219HNANResolutionV1 resolution;
        HHSExactStatus status = hhs_exact_pass219_hnan_resolve(
            &claims[i], &resolution);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        if (resolution.decision == HHS_EXACT_HNAN_DECISION_REJECTED) {
            out_receipt->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
            out_receipt->reason = resolution.reason;
            out_receipt->first_rejected_index = (uint32_t)i;
            return HHS_EXACT_STATUS_OK;
        }
        if (resolution.decision != HHS_EXACT_HNAN_DECISION_VERIFIED) {
            out_receipt->decision = HHS_EXACT_HNAN_DECISION_UNRESOLVED;
            out_receipt->reason = resolution.reason;
            out_receipt->first_unresolved_index = (uint32_t)i;
            return HHS_EXACT_STATUS_OK;
        }
        out_receipt->verified_rule_mask |=
            UINT32_C(1) << (claims[i].rule_id - 1U);
        signature = hhs_p219_hnan_mix(signature, claims[i].rule_id);
        signature = hhs_p219_hnan_mix(signature, claims[i].lhs_node);
        signature = hhs_p219_hnan_mix(signature, claims[i].rhs_node);
        signature = hhs_p219_hnan_mix(signature, claims[i].relation);
    }
    out_receipt->system_signature64 = signature;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hnan_global_system_verify(
    HHSExactPass219HNANGlobalReceiptV1 *out_receipt
) {
    HHSExactPass219HNANClaimV1 claims[HHS_EXACT_PASS219_HNAN_GLOBAL_RULE_COUNT];
    HHSExactStatus status;
    uint32_t i;

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(claims, 0, sizeof(claims));
    for (i = 0U; i < HHS_EXACT_PASS219_HNAN_GLOBAL_RULE_COUNT; ++i) {
        const HHSExactPass219HNANRuleV1 *rule = &HHS_P219_HNAN_RULES[i];
        claims[i].struct_size = (uint32_t)sizeof(claims[i]);
        claims[i].version = HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
        claims[i].rule_id = rule->rule_id;
        claims[i].lhs_node = rule->lhs_node;
        claims[i].rhs_node = rule->rhs_node;
        claims[i].relation = rule->relation;
        claims[i].source_order_preserved = 1U;
        claims[i].typed_identity_preserved = 1U;
    }

    status = hhs_exact_pass219_hnan_resolve_set(
        claims, HHS_EXACT_PASS219_HNAN_GLOBAL_RULE_COUNT, out_receipt);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (out_receipt->decision != HHS_EXACT_HNAN_DECISION_VERIFIED ||
        out_receipt->verified_rule_mask !=
            HHS_EXACT_PASS219_HNAN_GLOBAL_ALL_RULES) {
        out_receipt->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_receipt->reason = HHS_EXACT_HNAN_REASON_MANDATORY_INCOMPLETE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (!hhs_p219_hnan_jordan_verify(out_receipt)) {
        out_receipt->decision = HHS_EXACT_HNAN_DECISION_REJECTED;
        out_receipt->reason = HHS_EXACT_HNAN_REASON_JORDAN_FAILURE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_receipt->hnan_channel_order_preserved = 1U;
    out_receipt->ordered_zero_closure_preserved = 1U;
    out_receipt->global_delta_denominator_preserved = 1U;
    out_receipt->delta_cancellation_forbidden = 1U;
    out_receipt->unbounded_carrier_symbolic = 1U;
    out_receipt->u72_to_u0_closure_preserved = 1U;
    out_receipt->xy_yx_distinct = 1U;
    out_receipt->zw_wz_distinct = 1U;
    out_receipt->canonical_vm81_mutation_authority = 0U;
    out_receipt->canonical_hash72_authority = 0U;
    out_receipt->canonical_hash216_authority = 0U;
    out_receipt->floating_point_canonical_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}
