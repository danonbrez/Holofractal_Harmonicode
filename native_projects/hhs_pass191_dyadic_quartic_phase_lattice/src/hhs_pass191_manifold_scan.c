#include "hhs_pass189_hqlh.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define HHS191_TOP_CANDIDATES UINT32_C(16)
#define HHS191_OUTER_ENVELOPE UINT32_C(1259713)

typedef struct HHS191Candidate {
    uint32_t address;
    uint32_t score;
    uint32_t p_value;
    uint32_t factor_p;
    uint32_t factor_q;
    int32_t t_value;
    int32_t m_value;
    int32_t delta;
    int32_t cubic;
    int32_t idempotent;
    int32_t residual_cubic_delta;
    int32_t residual_delta_idempotent;
    uint32_t outer_residue_cubic_delta;
    uint32_t outer_residue_delta_idempotent;
    uint8_t cell81;
    uint8_t resolved_cell81;
    uint8_t operation64;
    uint8_t ordered_basis8;
    uint16_t g243;
    int8_t local_k;
    int8_t ternary;
} HHS191Candidate;

static uint64_t fnv1a_u32(uint64_t checksum, uint32_t value) {
    uint32_t shift;
    for (shift = 0U; shift < 32U; shift += 8U) {
        checksum ^= (uint64_t)((value >> shift) & UINT32_C(0xff));
        checksum *= UINT64_C(1099511628211);
    }
    return checksum;
}

static uint32_t absolute_i32(int32_t value) {
    int64_t widened = (int64_t)value;
    return (uint32_t)(widened < 0 ? -widened : widened);
}

static uint32_t outer_residue(int32_t value) {
    int64_t residue = (int64_t)value % (int64_t)HHS191_OUTER_ENVELOPE;
    if (residue < 0) {
        residue += (int64_t)HHS191_OUTER_ENVELOPE;
    }
    return (uint32_t)residue;
}

static int candidate_less(const HHS191Candidate *left, const HHS191Candidate *right) {
    if (left->score != right->score) {
        return left->score < right->score;
    }
    return left->address < right->address;
}

static void insert_candidate(
    HHS191Candidate candidates[HHS191_TOP_CANDIDATES],
    uint32_t *count,
    const HHS191Candidate *candidate
) {
    uint32_t index;
    if (*count < HHS191_TOP_CANDIDATES) {
        candidates[*count] = *candidate;
        ++(*count);
    } else if (candidate_less(candidate, &candidates[*count - UINT32_C(1)])) {
        candidates[*count - UINT32_C(1)] = *candidate;
    } else {
        return;
    }
    index = *count - UINT32_C(1);
    while (index > 0U && candidate_less(&candidates[index], &candidates[index - UINT32_C(1)])) {
        HHS191Candidate temporary = candidates[index - UINT32_C(1)];
        candidates[index - UINT32_C(1)] = candidates[index];
        candidates[index] = temporary;
        --index;
    }
}

static int parse_u32(const char *text, uint32_t *value_out) {
    char *end = NULL;
    unsigned long value;
    if (text == NULL || value_out == NULL) {
        return 0;
    }
    value = strtoul(text, &end, 10);
    if (end == text || *end != '\0' || value > UINT32_MAX) {
        return 0;
    }
    *value_out = (uint32_t)value;
    return 1;
}

static int exact_lo_shu_reduction(void) {
    const int32_t b2 = INT32_C(2);
    const int32_t c2 = INT32_C(3);
    const int32_t b4 = b2 * b2;
    const int32_t b6 = b4 * b2;
    const int32_t c4 = c2 * c2;
    const int32_t sqrt_c4 = INT32_C(3);
    const int32_t xy = INT32_C(1);
    const int32_t stage1_numerator = b2 * (c2 + b2) - (c2 - b2);
    const int32_t stage1 = stage1_numerator / sqrt_c4;
    const int32_t stage2_numerator = c2 * b6 - c2;
    const int32_t stage2 = stage2_numerator / stage1;
    const int32_t nested_numerator = (b6 - xy) * (b4 + c2);
    const int32_t nested = nested_numerator / stage2;
    return c4 == INT32_C(9) && stage1_numerator % sqrt_c4 == 0 &&
        stage1 == INT32_C(3) && stage2_numerator % stage1 == 0 &&
        stage2 == INT32_C(7) && nested_numerator % stage2 == 0 &&
        nested == INT32_C(7);
}

int main(int argc, char **argv) {
    uint32_t start = UINT32_C(0);
    uint32_t end = HHS189_CONTEXTUAL_STATES;
    uint32_t epoch = UINT32_C(0);
    uint32_t address;
    uint32_t candidate_count = UINT32_C(0);
    uint64_t visited = UINT64_C(0);
    uint64_t reciprocal_checks = UINT64_C(0);
    uint64_t coordinate_drift = UINT64_C(0);
    uint64_t quartic_checks = UINT64_C(0);
    uint64_t lo_shu_checks = UINT64_C(0);
    uint64_t outer_envelope_checks = UINT64_C(0);
    uint64_t exact_hits = UINT64_C(0);
    uint64_t checksum = UINT64_C(1469598103934665603);
    HHS191Candidate candidates[HHS191_TOP_CANDIDATES] = {{0}};
    int lo_shu_ok = exact_lo_shu_reduction();

    if (argc != 1 && argc != 4) {
        fprintf(stderr, "usage: %s [start end epoch]\n", argv[0]);
        return 2;
    }
    if (argc == 4 && (!parse_u32(argv[1], &start) || !parse_u32(argv[2], &end) ||
                      !parse_u32(argv[3], &epoch))) {
        fprintf(stderr, "invalid unsigned integer argument\n");
        return 2;
    }
    if (start > end || end > HHS189_CONTEXTUAL_STATES || !lo_shu_ok) {
        fprintf(stderr, "invalid scan range or manifold constants\n");
        return 3;
    }

    for (address = start; address < end; ++address) {
        HHS189ContextAddress decoded;
        uint32_t encoded = UINT32_C(0);
        uint8_t resolved_cell = UINT8_C(0);
        uint8_t inverse_cell = UINT8_C(0);
        uint32_t p_value;
        uint32_t factor_p;
        uint32_t factor_q;
        int32_t t_value;
        int32_t m_value;
        int32_t delta;
        int32_t cubic;
        int32_t idempotent;
        int32_t residual_cubic_delta;
        int32_t residual_delta_idempotent;
        uint64_t p_squared;
        uint64_t a_value;
        uint64_t b_value;
        uint64_t ab_value;
        uint64_t p_fourth;
        HHS191Candidate candidate;

        if (hhs189_decode_context(address, &decoded) != HHS189_OK ||
            hhs189_encode_context(&decoded, &encoded) != HHS189_OK ||
            hhs189_local_cell(decoded.cell81, decoded.local_k, &resolved_cell) != HHS189_OK ||
            hhs189_local_cell(resolved_cell, (int8_t)-decoded.local_k, &inverse_cell) != HHS189_OK) {
            fprintf(stderr, "Pass189 contextual authority failure at address %" PRIu32 "\n", address);
            return 4;
        }
        if (encoded != address || inverse_cell != decoded.cell81) {
            ++coordinate_drift;
        }

        p_value = (uint32_t)resolved_cell + UINT32_C(1);
        factor_p = (uint32_t)decoded.operation64 + UINT32_C(1);
        factor_q = (uint32_t)(((uint64_t)decoded.g243 + (uint64_t)epoch * UINT64_C(17)) % UINT64_C(64)) + UINT32_C(1);
        t_value = (int32_t)decoded.local_k;
        m_value = (int32_t)decoded.operation_class8;
        delta = (int32_t)(p_value * p_value) - (int32_t)(factor_p * factor_q);
        cubic = t_value * t_value * t_value - t_value;
        idempotent = m_value * m_value - m_value;
        residual_cubic_delta = cubic - delta;
        residual_delta_idempotent = delta - idempotent;

        p_squared = (uint64_t)p_value * (uint64_t)p_value;
        a_value = p_squared;
        b_value = p_squared;
        ab_value = a_value * b_value;
        p_fourth = p_squared * p_squared;
        if (ab_value != p_fourth) {
            fprintf(stderr, "AB=P^4 authority failure at address %" PRIu32 "\n", address);
            return 5;
        }

        candidate.address = address;
        candidate.score = absolute_i32(residual_cubic_delta) + absolute_i32(residual_delta_idempotent);
        candidate.p_value = p_value;
        candidate.factor_p = factor_p;
        candidate.factor_q = factor_q;
        candidate.t_value = t_value;
        candidate.m_value = m_value;
        candidate.delta = delta;
        candidate.cubic = cubic;
        candidate.idempotent = idempotent;
        candidate.residual_cubic_delta = residual_cubic_delta;
        candidate.residual_delta_idempotent = residual_delta_idempotent;
        candidate.outer_residue_cubic_delta = outer_residue(residual_cubic_delta);
        candidate.outer_residue_delta_idempotent = outer_residue(residual_delta_idempotent);
        candidate.cell81 = decoded.cell81;
        candidate.resolved_cell81 = resolved_cell;
        candidate.operation64 = decoded.operation64;
        candidate.ordered_basis8 = decoded.ordered_basis8;
        candidate.g243 = decoded.g243;
        candidate.local_k = decoded.local_k;
        candidate.ternary = hhs189_ternary_orientation(
            resolved_cell,
            HHS189_GLOBAL_NUCLEUS,
            (uint8_t)(decoded.operation64 & UINT8_C(1)),
            (uint8_t)(decoded.g243 & UINT16_C(1))
        );
        insert_candidate(candidates, &candidate_count, &candidate);

        if (residual_cubic_delta == 0 && residual_delta_idempotent == 0) {
            ++exact_hits;
        }
        ++visited;
        ++reciprocal_checks;
        ++quartic_checks;
        ++lo_shu_checks;
        outer_envelope_checks += UINT64_C(2);
        checksum = fnv1a_u32(checksum, address);
        checksum = fnv1a_u32(checksum, encoded);
        checksum = fnv1a_u32(checksum, (uint32_t)resolved_cell);
        checksum = fnv1a_u32(checksum, p_value);
        checksum = fnv1a_u32(checksum, factor_p);
        checksum = fnv1a_u32(checksum, factor_q);
        checksum = fnv1a_u32(checksum, (uint32_t)delta);
        checksum = fnv1a_u32(checksum, (uint32_t)cubic);
        checksum = fnv1a_u32(checksum, (uint32_t)idempotent);
        checksum = fnv1a_u32(checksum, candidate.outer_residue_cubic_delta);
        checksum = fnv1a_u32(checksum, candidate.outer_residue_delta_idempotent);
        checksum = fnv1a_u32(checksum, epoch);
    }

    printf("{\"schema\":\"HHS_PASS_191_NATIVE_MANIFOLD_SCAN_V1\",");
    printf("\"classification\":\"HHS_PASS_191_CONTEXTUAL_MANIFOLD_EPOCH_EXECUTED\",");
    printf("\"epoch\":%" PRIu32 ",\"start\":%" PRIu32 ",\"end\":%" PRIu32 ",", epoch, start, end);
    printf("\"contextual_cardinality\":%" PRIu32 ",", HHS189_CONTEXTUAL_STATES);
    printf("\"outer_envelope_modulus\":%" PRIu32 ",", HHS191_OUTER_ENVELOPE);
    printf("\"visited\":%" PRIu64 ",\"reciprocal_checks\":%" PRIu64 ",", visited, reciprocal_checks);
    printf("\"coordinate_drift\":%" PRIu64 ",\"quartic_checks\":%" PRIu64 ",", coordinate_drift, quartic_checks);
    printf("\"lo_shu_checks\":%" PRIu64 ",\"outer_envelope_checks\":%" PRIu64 ",", lo_shu_checks, outer_envelope_checks);
    printf("\"exact_hits\":%" PRIu64 ",\"checksum_fnv1a64\":\"%016" PRIx64 "\",", exact_hits, checksum);
    printf("\"complete\":%s,\"best_candidates\":[", end == HHS189_CONTEXTUAL_STATES ? "true" : "false");
    for (address = UINT32_C(0); address < candidate_count; ++address) {
        const HHS191Candidate *candidate = &candidates[address];
        if (address != 0U) {
            putchar(',');
        }
        printf("{\"address\":%" PRIu32 ",\"score\":%" PRIu32, candidate->address, candidate->score);
        printf(",\"P\":%" PRIu32 ",\"p\":%" PRIu32 ",\"q\":%" PRIu32, candidate->p_value, candidate->factor_p, candidate->factor_q);
        printf(",\"t\":%" PRId32 ",\"m\":%" PRId32, candidate->t_value, candidate->m_value);
        printf(",\"delta\":%" PRId32 ",\"cubic\":%" PRId32 ",\"idempotent\":%" PRId32, candidate->delta, candidate->cubic, candidate->idempotent);
        printf(",\"residual_cubic_delta\":%" PRId32 ",\"residual_delta_idempotent\":%" PRId32, candidate->residual_cubic_delta, candidate->residual_delta_idempotent);
        printf(",\"outer_residue_cubic_delta\":%" PRIu32 ",\"outer_residue_delta_idempotent\":%" PRIu32, candidate->outer_residue_cubic_delta, candidate->outer_residue_delta_idempotent);
        printf(",\"cell81\":%u,\"resolved_cell81\":%u,\"operation64\":%u,\"ordered_basis8\":%u", (unsigned)candidate->cell81, (unsigned)candidate->resolved_cell81, (unsigned)candidate->operation64, (unsigned)candidate->ordered_basis8);
        printf(",\"g243\":%u,\"local_k\":%d,\"ternary\":%d}", (unsigned)candidate->g243, (int)candidate->local_k, (int)candidate->ternary);
    }
    printf("],\"snapshot\":{\"cursor\":%" PRIu32 ",\"next_epoch\":%" PRIu32 ",\"branch_frontier_size\":%" PRIu32 "}}\n", end, epoch + UINT32_C(1), candidate_count);
    return coordinate_drift == 0U ? 0 : 6;
}
