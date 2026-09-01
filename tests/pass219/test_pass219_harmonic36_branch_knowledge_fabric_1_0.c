#include "hhs_pass219_harmonic36_branch_knowledge_fabric_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void occurrence(
    uint32_t id,
    uint8_t lane,
    uint8_t pos,
    uint8_t symbol,
    HHSExactPass219H36Hash216OccurrenceBindingV1 *out
) {
    HHSExactPass219Hash72TokenOccurrenceV1 raw;
    memset(&raw, 0, sizeof(raw));
    raw.struct_size = sizeof(raw);
    raw.version = hhs_exact_pass219_rna_version();
    raw.absolute_position216 =
        (uint16_t)((uint16_t)lane * 72U + pos);
    raw.lane_role = lane;
    raw.lane_position72 = pos;
    raw.glyph = (uint8_t)HHS_EXACT_HASH72_ALPHABET[symbol];
    raw.sha256_index_present = 1U;
    memset(raw.sha256_index_record, (int)(id & 0xFFU),
           sizeof(raw.sha256_index_record));
    assert(hhs_exact_pass219_h36_hash216_occurrence_bind(
        &raw, out) == HHS_EXACT_STATUS_OK);
}

int main(void) {
    HHSExactPass219H36Hash216OccurrenceBindingV1 source;
    HHSExactPass219H36Hash216OccurrenceBindingV1 targets[4];
    HHSExactPass219H36BranchCandidateV1 candidates[4];
    HHSExactPass219H36BranchRankingV1 ranking;
    HHSExactPass219H36KnowledgeEvidenceV1 evidence;
    uint32_t i;

    occurrence(1U, 0U, 10U, 3U, &source);
    occurrence(2U, 1U, 11U, 5U, &targets[0]);
    occurrence(3U, 1U, 12U, 9U, &targets[1]);
    occurrence(4U, 2U, 13U, 15U, &targets[2]);
    occurrence(5U, 2U, 14U, 21U, &targets[3]);

    for (i = 0U; i < 4U; ++i) {
        assert(hhs_exact_pass219_h36_branch_candidate(
            100U + i, 0U, &source, &targets[i], &candidates[i]) ==
            HHS_EXACT_STATUS_OK);
        assert(candidates[i].candidate_only == 1U);
        assert(candidates[i].exact_integer_rankable == 1U);
        assert(candidates[i].directional_identity_preserved == 1U);
        assert(candidates[i].canonical_mutation_authority == 0U);
    }

    assert(hhs_exact_pass219_h36_branch_rank(
        candidates, 4U, &ranking) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_branch_ranking_validate(
        candidates, 4U, &ranking) == HHS_EXACT_STATUS_OK);
    assert(ranking.candidate_count == 4U);
    assert(ranking.lexicographic_exact_ranking == 1U);
    assert(ranking.physical_completion_order_ignored == 1U);
    assert(ranking.candidate_only == 1U);

    for (i = 1U; i < 4U; ++i) {
        uint32_t prev_id = ranking.ranked_candidate_ids[i - 1U];
        uint32_t curr_id = ranking.ranked_candidate_ids[i];
        const HHSExactPass219H36BranchCandidateV1 *prev = NULL;
        const HHSExactPass219H36BranchCandidateV1 *curr = NULL;
        uint32_t j;
        for (j = 0U; j < 4U; ++j) {
            if (candidates[j].candidate_id == prev_id) prev = &candidates[j];
            if (candidates[j].candidate_id == curr_id) curr = &candidates[j];
        }
        assert(prev != NULL && curr != NULL);
        assert(prev->harmonic_transition.exact_voice_leading_cost <=
               curr->harmonic_transition.exact_voice_leading_cost ||
               prev->harmonic_transition.common_tones >=
               curr->harmonic_transition.common_tones);
    }

    assert(hhs_exact_pass219_h36_knowledge_evidence(
        &candidates[0],
        HHS_EXACT_PASS219_H36_GRAPH_RELATION_PRECEDES,
        1U, 1U, &evidence) == HHS_EXACT_STATUS_OK);
    assert(strcmp(evidence.graph_relation_name, "PRECEDES") == 0);
    assert(evidence.confidence_numerator == 1U);
    assert(evidence.confidence_denominator == 1U);
    assert(evidence.directional == 1U);
    assert(evidence.evidence_grounded == 1U);
    assert(evidence.knowledge_graph_projection_only == 1U);
    assert(evidence.execution_authority == 0U);
    assert(evidence.mutation_authority == 0U);
    assert(evidence.floating_point_authority == 0U);

    assert(hhs_exact_pass219_h36_knowledge_evidence(
        &candidates[0],
        HHS_EXACT_PASS219_H36_GRAPH_RELATION_INVALID,
        1U, 1U, &evidence) == HHS_EXACT_STATUS_RANGE_ERROR);

    puts("PASS219 Harmonic36 branch/knowledge fabric: PASS");
    return 0;
}
