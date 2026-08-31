#include "hhs_pass219_harmonic36_composition_grammar_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void occurrence(
    uint8_t lane,
    uint8_t pos,
    uint8_t symbol,
    HHSExactPass219H36Hash216OccurrenceBindingV1 *out
) {
    HHSExactPass219Hash72TokenOccurrenceV1 raw;
    memset(&raw, 0, sizeof(raw));
    raw.struct_size = sizeof(raw);
    raw.version = hhs_exact_pass219_rna_version();
    raw.absolute_position216 = (uint16_t)((uint16_t)lane * 72U + pos);
    raw.lane_role = lane;
    raw.lane_position72 = pos;
    raw.glyph = (uint8_t)HHS_EXACT_HASH72_ALPHABET[symbol];
    raw.sha256_index_present = 1U;
    memset(raw.sha256_index_record, symbol, sizeof(raw.sha256_index_record));
    assert(hhs_exact_pass219_h36_hash216_occurrence_bind(
        &raw, out) == HHS_EXACT_STATUS_OK);
}

static void state(
    uint16_t rule,
    uint8_t tonic,
    uint8_t mode,
    uint8_t inversion,
    const HHSExactPass219H36CompositionStateV1 *previous,
    HHSExactPass219H36CompositionStateV1 *out
) {
    assert(hhs_exact_pass219_h36_composition_state(
        rule, tonic, tonic, mode, inversion,
        HHS_EXACT_PASS219_H36_NO_SECONDARY_TARGET,
        tonic, 0U, previous, out) == HHS_EXACT_STATUS_OK);
}

int main(void) {
    HHSExactPass219H36CompositionStateV1 ii;
    HHSExactPass219H36CompositionStateV1 v;
    HHSExactPass219H36CompositionStateV1 i;
    HHSExactPass219H36CompositionStateV1 minor_ii;
    HHSExactPass219H36CompositionStateV1 minor_v;
    HHSExactPass219H36CompositionStateV1 minor_i;
    HHSExactPass219H36CompositionStateV1 neo;
    HHSExactPass219H36CompositionStateV1 aug6;
    HHSExactPass219H36CompositionStateV1 tritone;
    HHSExactPass219H36CompositionStateV1 backdoor;
    HHSExactPass219H36CompositionStateV1 modal;
    HHSExactPass219H36CompositionTransitionV1 t;
    HHSExactPass219H36Hash216OccurrenceBindingV1 source_occ;
    HHSExactPass219H36Hash216OccurrenceBindingV1 target_occ;
    HHSExactPass219H36CompositionCandidateV1 candidates[3];
    HHSExactPass219H36CompositionRankingV1 ranking;

    /* Major ii-V-I composition over the fixed 64-rule basis. */
    state(HHS_EXACT_PASS219_H36_RULE_JAZZ_II_MINOR7, 0U,
          HHS_EXACT_PASS219_H36_MODE_MAJOR, 0U, NULL, &ii);
    state(HHS_EXACT_PASS219_H36_RULE_JAZZ_V7, 0U,
          HHS_EXACT_PASS219_H36_MODE_MAJOR, 0U, &ii, &v);
    state(HHS_EXACT_PASS219_H36_RULE_JAZZ_I_MAJOR7, 0U,
          HHS_EXACT_PASS219_H36_MODE_MAJOR, 0U, &v, &i);

    assert(ii.harmonic_rule64 ==
           HHS_EXACT_PASS219_H36_RULE_JAZZ_II_MINOR7);
    assert(v.harmonic_rule64 ==
           HHS_EXACT_PASS219_H36_RULE_JAZZ_V7);
    assert(i.harmonic_rule64 ==
           HHS_EXACT_PASS219_H36_RULE_JAZZ_I_MAJOR7);
    assert(ii.voice_order_valid == 1U && v.voice_order_valid == 1U &&
           i.voice_order_valid == 1U);
    assert(ii.fixed_operation64_preserved == 1U);

    assert(hhs_exact_pass219_h36_composition_transition(
        &ii, &v, &t) == HHS_EXACT_STATUS_OK);
    assert(t.progression_allowed == 1U);
    assert(t.cadence == HHS_EXACT_PASS219_H36_CADENCE_HALF);
    assert(t.relation == HHS_EXACT_PASS219_H36_RELATION_FUNCTIONAL);

    assert(hhs_exact_pass219_h36_composition_transition(
        &v, &i, &t) == HHS_EXACT_STATUS_OK);
    assert(t.progression_allowed == 1U);
    assert(t.cadence == HHS_EXACT_PASS219_H36_CADENCE_PERFECT_AUTHENTIC ||
           t.cadence == HHS_EXACT_PASS219_H36_CADENCE_IMPERFECT_AUTHENTIC);
    assert(t.fixed_operation64_preserved == 1U);

    /* Minor iiø-Vb9-i grammar. */
    state(HHS_EXACT_PASS219_H36_RULE_MINOR_II_HALFDIM7, 0U,
          HHS_EXACT_PASS219_H36_MODE_MINOR, 0U, NULL, &minor_ii);
    state(HHS_EXACT_PASS219_H36_RULE_MINOR_V7_B9, 0U,
          HHS_EXACT_PASS219_H36_MODE_MINOR, 0U, &minor_ii, &minor_v);
    state(HHS_EXACT_PASS219_H36_RULE_MINOR_I_MINMAJ7, 0U,
          HHS_EXACT_PASS219_H36_MODE_MINOR, 0U, &minor_v, &minor_i);

    assert(hhs_exact_pass219_h36_composition_transition(
        &minor_ii, &minor_v, &t) == HHS_EXACT_STATUS_OK);
    assert(t.progression_allowed == 1U);
    assert(hhs_exact_pass219_h36_composition_transition(
        &minor_v, &minor_i, &t) == HHS_EXACT_STATUS_OK);
    assert(t.progression_allowed == 1U);

    /* Romantic predominant colors resolve toward dominant. */
    state(HHS_EXACT_PASS219_H36_RULE_NEAPOLITAN6, 0U,
          HHS_EXACT_PASS219_H36_MODE_MAJOR, 1U, NULL, &neo);
    assert(hhs_exact_pass219_h36_composition_transition(
        &neo, &v, &t) == HHS_EXACT_STATUS_OK);
    assert(t.progression_allowed == 1U);
    assert(t.relation == HHS_EXACT_PASS219_H36_RELATION_NEAPOLITAN);

    state(HHS_EXACT_PASS219_H36_RULE_GERMAN_AUG6, 0U,
          HHS_EXACT_PASS219_H36_MODE_MAJOR, 0U, NULL, &aug6);
    assert(hhs_exact_pass219_h36_composition_transition(
        &aug6, &v, &t) == HHS_EXACT_STATUS_OK);
    assert(t.progression_allowed == 1U);
    assert(t.relation == HHS_EXACT_PASS219_H36_RELATION_AUGMENTED_SIXTH);

    /* Jazz substitutions remain typed rather than collapsed into V7. */
    state(HHS_EXACT_PASS219_H36_RULE_TRITONE_SUB_BII7, 0U,
          HHS_EXACT_PASS219_H36_MODE_MAJOR, 0U, NULL, &tritone);
    assert(hhs_exact_pass219_h36_composition_transition(
        &tritone, &i, &t) == HHS_EXACT_STATUS_OK);
    assert(t.progression_allowed == 1U);
    assert(t.relation ==
           HHS_EXACT_PASS219_H36_RELATION_TRITONE_SUBSTITUTION);

    state(HHS_EXACT_PASS219_H36_RULE_BACKDOOR_BVII7, 0U,
          HHS_EXACT_PASS219_H36_MODE_MAJOR, 0U, NULL, &backdoor);
    assert(hhs_exact_pass219_h36_composition_transition(
        &backdoor, &i, &t) == HHS_EXACT_STATUS_OK);
    assert(t.progression_allowed == 1U);
    assert(t.cadence == HHS_EXACT_PASS219_H36_CADENCE_BACKDOOR);

    /* Modal state has its own context/relation over the same op64 basis. */
    state(HHS_EXACT_PASS219_H36_RULE_DORIAN_MODAL_TONIC, 2U,
          HHS_EXACT_PASS219_H36_MODE_DORIAN, 0U, NULL, &modal);
    assert((modal.context_flags &
            HHS_EXACT_PASS219_H36_CONTEXT_MODAL) != 0U);
    assert(hhs_exact_pass219_h36_composition_transition(
        &modal, &modal, &t) == HHS_EXACT_STATUS_OK);
    assert(t.relation == HHS_EXACT_PASS219_H36_RELATION_MODAL);

    /* Hash216-bound composition candidates retain directional identity. */
    occurrence(0U, 0U, 24U, &source_occ);
    occurrence(1U, 0U, 25U, &target_occ);
    assert(source_occ.harmonic_rule64 == 25U);
    assert(target_occ.harmonic_rule64 == 26U);
    assert(hhs_exact_pass219_h36_composition_transition(
        &ii, &v, &t) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_composition_candidate(
        100U, &source_occ, &target_occ, &t, &candidates[0]) ==
        HHS_EXACT_STATUS_OK);
    assert(candidates[0].hash216_direction_preserved == 1U);
    assert(candidates[0].candidate_only == 1U);
    assert(candidates[0].singleton_vm81_admission_required == 1U);

    /* A disallowed minor-ii direct tonic jump ranks behind allowed ii-V. */
    {
        HHSExactPass219H36CompositionTransitionV1 bad;
        HHSExactPass219H36Hash216OccurrenceBindingV1 s2;
        HHSExactPass219H36Hash216OccurrenceBindingV1 t2;
        occurrence(0U, 0U, 27U, &s2);
        occurrence(1U, 0U, 29U, &t2);
        assert(s2.harmonic_rule64 == 28U);
        assert(t2.harmonic_rule64 == 30U);
        assert(hhs_exact_pass219_h36_composition_transition(
            &minor_ii, &minor_i, &bad) == HHS_EXACT_STATUS_OK);
        assert(bad.progression_allowed == 0U);
        assert(hhs_exact_pass219_h36_composition_candidate(
            101U, &s2, &t2, &bad, &candidates[1]) ==
            HHS_EXACT_STATUS_OK);
    }

    /* Second valid candidate for stable exact ranking. */
    {
        HHSExactPass219H36Hash216OccurrenceBindingV1 s3;
        HHSExactPass219H36Hash216OccurrenceBindingV1 t3;
        HHSExactPass219H36CompositionTransitionV1 good;
        occurrence(0U, 0U, 27U, &s3);
        occurrence(1U, 0U, 28U, &t3);
        assert(s3.harmonic_rule64 == 28U);
        assert(t3.harmonic_rule64 == 29U);
        assert(hhs_exact_pass219_h36_composition_transition(
            &minor_ii, &minor_v, &good) == HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_h36_composition_candidate(
            102U, &s3, &t3, &good, &candidates[2]) ==
            HHS_EXACT_STATUS_OK);
    }

    assert(hhs_exact_pass219_h36_composition_rank(
        candidates, 3U, &ranking) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_composition_ranking_validate(
        candidates, 3U, &ranking) == HHS_EXACT_STATUS_OK);
    assert(ranking.ranked_candidate_ids[2] == 101U);
    assert(ranking.grammar_first == 1U);
    assert(ranking.exact_integer_ranking == 1U);

    assert(candidates[0].canonical_mutation_authority == 0U);
    assert(candidates[0].canonical_hash72_authority == 0U);
    assert(candidates[0].canonical_persistence_authority == 0U);
    assert(candidates[0].floating_point_authority == 0U);

    puts("PASS219 Harmonic36 composition grammar 1.0 conformance: PASS");
    return 0;
}
