#include "../include/hhs_pass219_harmonic36_branch_knowledge_fabric_1_0.h"

#include <string.h>

static uint32_t h36_bkg_version_word(void) {
    return (HHS_EXACT_PASS219_H36_BKG_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_H36_BKG_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_H36_BKG_VERSION_PATCH;
}

static uint16_t h36_abs_u16(uint16_t a, uint16_t b) {
    return a >= b ? (uint16_t)(a - b) : (uint16_t)(b - a);
}

static uint16_t h36_phase_distance(
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *a,
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *b
) {
    uint16_t left = h36_abs_u16(a->phase_left8, b->phase_left8);
    uint16_t right = h36_abs_u16(a->phase_right8, b->phase_right8);
    return (uint16_t)(left + right);
}

static const char *h36_relation_name(uint32_t relation) {
    switch (relation) {
        case HHS_EXACT_PASS219_H36_GRAPH_RELATION_SUPPORTS: return "SUPPORTS";
        case HHS_EXACT_PASS219_H36_GRAPH_RELATION_REFINES: return "REFINES";
        case HHS_EXACT_PASS219_H36_GRAPH_RELATION_DEPENDS_ON: return "DEPENDS_ON";
        case HHS_EXACT_PASS219_H36_GRAPH_RELATION_EQUIVALENT_TO: return "EQUIVALENT_TO";
        case HHS_EXACT_PASS219_H36_GRAPH_RELATION_PART_OF: return "PART_OF";
        case HHS_EXACT_PASS219_H36_GRAPH_RELATION_PRECEDES: return "PRECEDES";
        case HHS_EXACT_PASS219_H36_GRAPH_RELATION_DEFINES: return "DEFINES";
        case HHS_EXACT_PASS219_H36_GRAPH_RELATION_INSTANCE_OF: return "INSTANCE_OF";
        default: return NULL;
    }
}

static int h36_candidate_less(
    const HHSExactPass219H36BranchCandidateV1 *a,
    const HHSExactPass219H36BranchCandidateV1 *b
) {
    if (a->harmonic_transition.exact_voice_leading_cost !=
        b->harmonic_transition.exact_voice_leading_cost)
        return a->harmonic_transition.exact_voice_leading_cost <
               b->harmonic_transition.exact_voice_leading_cost;
    if (a->harmonic_transition.common_tones !=
        b->harmonic_transition.common_tones)
        return a->harmonic_transition.common_tones >
               b->harmonic_transition.common_tones;
    if (a->harmonic_transition.semitone_resolutions !=
        b->harmonic_transition.semitone_resolutions)
        return a->harmonic_transition.semitone_resolutions >
               b->harmonic_transition.semitone_resolutions;
    if (a->phase_distance != b->phase_distance)
        return a->phase_distance < b->phase_distance;
    if (a->native_linear_distance != b->native_linear_distance)
        return a->native_linear_distance < b->native_linear_distance;
    if (a->directional_position_distance != b->directional_position_distance)
        return a->directional_position_distance <
               b->directional_position_distance;
    if (a->target.absolute_position216 != b->target.absolute_position216)
        return a->target.absolute_position216 <
               b->target.absolute_position216;
    return a->candidate_id < b->candidate_id;
}

static const HHSExactPass219H36BranchCandidateV1 *h36_find_candidate(
    const HHSExactPass219H36BranchCandidateV1 *candidates,
    size_t count,
    uint32_t id
) {
    size_t i;
    for (i = 0U; i < count; ++i) {
        if (candidates[i].candidate_id == id)
            return &candidates[i];
    }
    return NULL;
}

uint32_t hhs_exact_pass219_h36_branch_knowledge_version(void) {
    return h36_bkg_version_word();
}

HHSExactStatus hhs_exact_pass219_h36_branch_candidate(
    uint32_t candidate_id,
    uint8_t tonic_pc12,
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *source,
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *target,
    HHSExactPass219H36BranchCandidateV1 *out_candidate
) {
    uint64_t source_word;
    uint64_t target_word;
    HHSExactStatus status;

    if (source == NULL || target == NULL || out_candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (tonic_pc12 >= 12U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (source->struct_size < sizeof(*source) ||
        target->struct_size < sizeof(*target) ||
        source->version != hhs_exact_pass219_h36_rna_binding_version() ||
        target->version != hhs_exact_pass219_h36_rna_binding_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (source->directional_identity_preserved != 1U ||
        target->directional_identity_preserved != 1U ||
        source->canonical_mutation_authority != 0U ||
        target->canonical_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_h36_harmonic_render(
        source->harmonic_rule64, tonic_pc12, &source_word);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_h36_harmonic_render(
        target->harmonic_rule64, tonic_pc12, &target_word);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(out_candidate, 0, sizeof(*out_candidate));
    out_candidate->struct_size = (uint32_t)sizeof(*out_candidate);
    out_candidate->version = h36_bkg_version_word();
    out_candidate->candidate_id = candidate_id;
    out_candidate->tonic_pc12 = tonic_pc12;
    out_candidate->source = *source;
    out_candidate->target = *target;

    status = hhs_exact_pass219_h36_harmonic_transition(
        source_word, target_word, &out_candidate->harmonic_transition);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_candidate->phase_distance = h36_phase_distance(source, target);
    out_candidate->native_linear_distance =
        h36_abs_u16(source->native_hash72_linear5184,
                    target->native_hash72_linear5184);
    out_candidate->directional_position_distance =
        h36_abs_u16(source->absolute_position216,
                    target->absolute_position216);
    out_candidate->lane_role_forward_or_equal =
        (uint8_t)(target->lane_role >= source->lane_role);
    out_candidate->directional_identity_preserved = 1U;
    out_candidate->candidate_only = 1U;
    out_candidate->exact_integer_rankable = 1U;
    out_candidate->canonical_mutation_authority = 0U;
    out_candidate->canonical_hash72_authority = 0U;
    out_candidate->canonical_persistence_authority = 0U;
    out_candidate->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_branch_rank(
    const HHSExactPass219H36BranchCandidateV1 *candidates,
    size_t candidate_count,
    HHSExactPass219H36BranchRankingV1 *out_ranking
) {
    size_t i;
    if (candidates == NULL || out_ranking == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate_count == 0U ||
        candidate_count > HHS_EXACT_PASS219_H36_BRANCH_MAX_CANDIDATES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_ranking, 0, sizeof(*out_ranking));
    out_ranking->struct_size = (uint32_t)sizeof(*out_ranking);
    out_ranking->version = h36_bkg_version_word();
    out_ranking->candidate_count = (uint32_t)candidate_count;

    for (i = 0U; i < candidate_count; ++i) {
        size_t j;
        if (candidates[i].struct_size != sizeof(candidates[i]) ||
            candidates[i].version != h36_bkg_version_word())
            return HHS_EXACT_STATUS_VERSION_MISMATCH;
        if (candidates[i].candidate_only != 1U ||
            candidates[i].exact_integer_rankable != 1U ||
            candidates[i].canonical_mutation_authority != 0U ||
            candidates[i].floating_point_authority != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        for (j = 0U; j < i; ++j) {
            if (candidates[j].candidate_id == candidates[i].candidate_id)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        out_ranking->ranked_candidate_ids[i] = candidates[i].candidate_id;
    }

    for (i = 1U; i < candidate_count; ++i) {
        uint32_t key = out_ranking->ranked_candidate_ids[i];
        size_t j = i;
        const HHSExactPass219H36BranchCandidateV1 *key_candidate =
            h36_find_candidate(candidates, candidate_count, key);
        while (j > 0U) {
            const HHSExactPass219H36BranchCandidateV1 *prior =
                h36_find_candidate(
                    candidates, candidate_count,
                    out_ranking->ranked_candidate_ids[j - 1U]);
            if (key_candidate == NULL || prior == NULL)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            if (!h36_candidate_less(key_candidate, prior))
                break;
            out_ranking->ranked_candidate_ids[j] =
                out_ranking->ranked_candidate_ids[j - 1U];
            --j;
        }
        out_ranking->ranked_candidate_ids[j] = key;
    }

    out_ranking->lexicographic_exact_ranking = 1U;
    out_ranking->stable_tie_break_by_candidate_id = 1U;
    out_ranking->physical_completion_order_ignored = 1U;
    out_ranking->candidate_only = 1U;
    out_ranking->canonical_mutation_authority = 0U;
    out_ranking->canonical_hash72_authority = 0U;
    out_ranking->canonical_persistence_authority = 0U;
    out_ranking->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_branch_ranking_validate(
    const HHSExactPass219H36BranchCandidateV1 *candidates,
    size_t candidate_count,
    const HHSExactPass219H36BranchRankingV1 *ranking
) {
    HHSExactPass219H36BranchRankingV1 expected;
    HHSExactStatus status;

    if (ranking == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (ranking->struct_size != sizeof(*ranking) ||
        ranking->version != h36_bkg_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = hhs_exact_pass219_h36_branch_rank(
        candidates, candidate_count, &expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return memcmp(ranking, &expected, sizeof(expected)) == 0
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_h36_knowledge_evidence(
    const HHSExactPass219H36BranchCandidateV1 *candidate,
    uint32_t graph_relation_type,
    uint32_t confidence_numerator,
    uint32_t confidence_denominator,
    HHSExactPass219H36KnowledgeEvidenceV1 *out_evidence
) {
    const char *name;
    size_t name_len;

    if (candidate == NULL || out_evidence == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate->struct_size != sizeof(*candidate) ||
        candidate->version != h36_bkg_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (confidence_denominator == 0U ||
        confidence_numerator > confidence_denominator)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    name = h36_relation_name(graph_relation_type);
    if (name == NULL)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    name_len = strlen(name);
    if (name_len + 1U > HHS_EXACT_PASS219_H36_GRAPH_RELATION_NAME_MAX)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_evidence, 0, sizeof(*out_evidence));
    out_evidence->struct_size = (uint32_t)sizeof(*out_evidence);
    out_evidence->version = h36_bkg_version_word();
    out_evidence->graph_relation_type = graph_relation_type;
    memcpy(out_evidence->graph_relation_name, name, name_len + 1U);
    out_evidence->confidence_numerator = confidence_numerator;
    out_evidence->confidence_denominator = confidence_denominator;
    out_evidence->candidate_id = candidate->candidate_id;
    out_evidence->source_linear5184 =
        candidate->source.native_hash72_linear5184;
    out_evidence->target_linear5184 =
        candidate->target.native_hash72_linear5184;
    out_evidence->source_absolute_position216 =
        candidate->source.absolute_position216;
    out_evidence->target_absolute_position216 =
        candidate->target.absolute_position216;
    out_evidence->source_lane_role = candidate->source.lane_role;
    out_evidence->target_lane_role = candidate->target.lane_role;
    out_evidence->source_harmonic_rule64 =
        candidate->source.harmonic_rule64;
    out_evidence->target_harmonic_rule64 =
        candidate->target.harmonic_rule64;
    out_evidence->source_phase_left8 = candidate->source.phase_left8;
    out_evidence->source_phase_right8 = candidate->source.phase_right8;
    out_evidence->target_phase_left8 = candidate->target.phase_left8;
    out_evidence->target_phase_right8 = candidate->target.phase_right8;
    out_evidence->common_tones =
        candidate->harmonic_transition.common_tones;
    out_evidence->semitone_resolutions =
        candidate->harmonic_transition.semitone_resolutions;
    out_evidence->exact_voice_leading_cost =
        candidate->harmonic_transition.exact_voice_leading_cost;
    out_evidence->phase_distance = candidate->phase_distance;
    out_evidence->native_linear_distance =
        candidate->native_linear_distance;
    out_evidence->directional = 1U;
    out_evidence->evidence_grounded = 1U;
    out_evidence->knowledge_graph_projection_only = 1U;
    out_evidence->execution_authority = 0U;
    out_evidence->mutation_authority = 0U;
    out_evidence->canonical_persistence_authority = 0U;
    out_evidence->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}
