#include "hhs_runtime_exact_abi.h"

#include <inttypes.h>
#include <stdio.h>
#include <string.h>

static int same_rat(HHSPass168Rational a, int64_t n, uint64_t d) {
    return a.numerator == n && a.denominator == d;
}

int main(void) {
    HHSPass168SelfTest proof;
    HHSPass168SourceStats source;
    HHSPass168CircuitState baseline;
    HHSPass168CircuitState committed;
    HHSPass168CircuitState replayed;
    HHSPass168CircuitState rolled;
    HHSPass168CircuitState repaired;
    HHSPass168Candidate candidate;
    HHSPass168Candidate invalid;
    HHSPass168Transition transition;
    HHSPass168Address address;
    HHSPass168Rational cell;
    uint32_t reason = 0U;
    HHSExactStatus status;

    memset(&proof, 0, sizeof(proof));
    status = hhs_pass168_self_test(&proof);
    if (status != HHS_EXACT_STATUS_OK)
        return 10;

    status = hhs_pass168_source_stats(&source);
    if (status != HHS_EXACT_STATUS_OK || source.source_bytes != 424U ||
        source.matched_parenthesis_pairs != 28U || source.literal_equals_count != 12U ||
        source.double_equals_token_count != 6U)
        return 11;

    status = hhs_pass168_state_initialize(&baseline);
    if (status != HHS_EXACT_STATUS_OK || baseline.generation != 0U || baseline.committed != 1U)
        return 12;

    status = hhs_pass168_cell_value(&baseline, 0U, &cell);
    if (status != HHS_EXACT_STATUS_OK || !same_rat(cell, 4, 1U))
        return 13;
    status = hhs_pass168_address_decode(5183U, &address);
    if (status != HHS_EXACT_STATUS_OK || address.thread_id != 63U || address.local_index != 80U)
        return 14;

    status = hhs_pass168_candidate_begin(&baseline, &candidate);
    if (status != HHS_EXACT_STATUS_OK)
        return 15;
    status = hhs_pass168_candidate_set(&candidate, 12U, 2, 1U); /* P13 */
    if (status != HHS_EXACT_STATUS_OK || candidate.update_mask != (UINT64_C(1) << 12U) ||
        candidate.affected_thread_bitmap == UINT64_MAX)
        return 16;
    status = hhs_pass168_commit_candidate(&baseline, &candidate, &committed, &transition);
    if (status != HHS_EXACT_STATUS_OK || transition.decision != HHS_PASS168_DECISION_ADMIT ||
        transition.committed != 1U || transition.fallback_used != 0U || committed.generation != 1U)
        return 17;
    status = hhs_pass168_replay_transition(&baseline, &transition, &replayed);
    if (status != HHS_EXACT_STATUS_OK ||
        memcmp(replayed.state_hash216, committed.state_hash216, HHS_PASS168_HASH216_STRLEN) != 0)
        return 18;
    status = hhs_pass168_rollback_transition(&transition, &rolled);
    if (status != HHS_EXACT_STATUS_OK ||
        memcmp(rolled.state_hash216, baseline.state_hash216, HHS_PASS168_HASH216_STRLEN) != 0)
        return 19;
    status = hhs_pass168_repair_transition(&transition, &repaired);
    if (status != HHS_EXACT_STATUS_OK ||
        memcmp(repaired.state_hash216, committed.state_hash216, HHS_PASS168_HASH216_STRLEN) != 0)
        return 20;

    invalid = candidate;
    memcpy(invalid.expected_prior_hash216, baseline.state_hash216, HHS_PASS168_HASH216_STRLEN);
    status = hhs_pass168_candidate_set(&invalid, 11U, 0, 1U); /* P12 denominator role */
    if (status != HHS_EXACT_STATUS_OK)
        return 21;
    status = hhs_pass168_candidate_validate(&baseline, &invalid, &reason);
    if (status == HHS_EXACT_STATUS_OK || reason != HHS_PASS168_REASON_ZERO_DENOMINATOR_ROLE)
        return 22;

    status = hhs_pass168_candidate_begin(&baseline, &invalid);
    if (status != HHS_EXACT_STATUS_OK)
        return 23;
    invalid.expected_prior_hash216[0] =
        invalid.expected_prior_hash216[0] == '0' ? '1' : '0';
    status = hhs_pass168_candidate_validate(&baseline, &invalid, &reason);
    if (status == HHS_EXACT_STATUS_OK || reason != HHS_PASS168_REASON_STALE_PRIOR_ROOT)
        return 24;

    printf("{\"schema\":\"HHS_PASS219_I166_PASS168_EXACT_RECORD_V1\","
           "\"status\":0,\"source_bytes\":%u,\"parentheses\":%u,"
           "\"equals\":%u,\"threads\":%u,\"cells\":%u,"
           "\"duplicate_addresses\":%u,\"inverse_address_failures\":%u,"
           "\"comparators_verified\":%u,\"sparse_verified\":%u,"
           "\"hash72_verified\":%u,\"hash216_verified\":%u,"
           "\"replay_verified\":%u,\"rollback_verified\":%u,"
           "\"repair_verified\":%u,\"fallback_used\":%u,"
           "\"source_sha256\":\"%s\",\"record_hash216\":\"%s\"}\n",
           source.source_bytes,
           source.matched_parenthesis_pairs,
           source.literal_equals_count,
           proof.threads_registered,
           proof.cells_covered,
           proof.duplicate_addresses,
           proof.inverse_address_failures,
           proof.comparators_verified,
           proof.sparse_dependency_updates_verified,
           proof.hash72_receipts_verified,
           proof.hash216_identity_verified,
           proof.deterministic_replay_verified,
           proof.rollback_verified,
           proof.repair_verified,
           proof.fallback_used,
           source.source_sha256_hex,
           proof.deterministic_record_hash216);
    return 0;
}
