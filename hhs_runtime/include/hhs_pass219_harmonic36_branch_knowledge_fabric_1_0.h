#ifndef HHS_PASS219_HARMONIC36_BRANCH_KNOWLEDGE_FABRIC_1_0_H
#define HHS_PASS219_HARMONIC36_BRANCH_KNOWLEDGE_FABRIC_1_0_H

#include "hhs_pass219_harmonic36_compression_gpu_fabric_1_0.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_BKG_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_H36_BKG_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_H36_BKG_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_H36_BRANCH_MAX_CANDIDATES 64U
#define HHS_EXACT_PASS219_H36_GRAPH_RELATION_NAME_MAX 16U

typedef enum HHSExactPass219H36CanonicalGraphRelationV1 {
    HHS_EXACT_PASS219_H36_GRAPH_RELATION_INVALID = 0,
    HHS_EXACT_PASS219_H36_GRAPH_RELATION_SUPPORTS = 1,
    HHS_EXACT_PASS219_H36_GRAPH_RELATION_REFINES = 2,
    HHS_EXACT_PASS219_H36_GRAPH_RELATION_DEPENDS_ON = 3,
    HHS_EXACT_PASS219_H36_GRAPH_RELATION_EQUIVALENT_TO = 4,
    HHS_EXACT_PASS219_H36_GRAPH_RELATION_PART_OF = 5,
    HHS_EXACT_PASS219_H36_GRAPH_RELATION_PRECEDES = 6,
    HHS_EXACT_PASS219_H36_GRAPH_RELATION_DEFINES = 7,
    HHS_EXACT_PASS219_H36_GRAPH_RELATION_INSTANCE_OF = 8
} HHSExactPass219H36CanonicalGraphRelationV1;

typedef struct HHSExactPass219H36BranchCandidateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t candidate_id;
    uint8_t tonic_pc12;
    HHSExactPass219H36Hash216OccurrenceBindingV1 source;
    HHSExactPass219H36Hash216OccurrenceBindingV1 target;
    HHSExactPass219H36HarmonicTransitionV1 harmonic_transition;
    uint16_t phase_distance;
    uint16_t native_linear_distance;
    uint16_t directional_position_distance;
    uint8_t lane_role_forward_or_equal;
    uint8_t directional_identity_preserved;
    uint8_t candidate_only;
    uint8_t exact_integer_rankable;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36BranchCandidateV1;

typedef struct HHSExactPass219H36BranchRankingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t candidate_count;
    uint32_t ranked_candidate_ids[HHS_EXACT_PASS219_H36_BRANCH_MAX_CANDIDATES];
    uint8_t lexicographic_exact_ranking;
    uint8_t stable_tie_break_by_candidate_id;
    uint8_t physical_completion_order_ignored;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36BranchRankingV1;

typedef struct HHSExactPass219H36KnowledgeEvidenceV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t graph_relation_type;
    char graph_relation_name[HHS_EXACT_PASS219_H36_GRAPH_RELATION_NAME_MAX];
    uint32_t confidence_numerator;
    uint32_t confidence_denominator;
    uint32_t candidate_id;
    uint16_t source_linear5184;
    uint16_t target_linear5184;
    uint16_t source_absolute_position216;
    uint16_t target_absolute_position216;
    uint8_t source_lane_role;
    uint8_t target_lane_role;
    uint8_t source_harmonic_rule64;
    uint8_t target_harmonic_rule64;
    uint8_t source_phase_left8;
    uint8_t source_phase_right8;
    uint8_t target_phase_left8;
    uint8_t target_phase_right8;
    uint16_t common_tones;
    uint16_t semitone_resolutions;
    uint16_t exact_voice_leading_cost;
    uint16_t phase_distance;
    uint16_t native_linear_distance;
    uint8_t directional;
    uint8_t evidence_grounded;
    uint8_t knowledge_graph_projection_only;
    uint8_t execution_authority;
    uint8_t mutation_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36KnowledgeEvidenceV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_h36_branch_knowledge_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_branch_candidate(
    uint32_t candidate_id,
    uint8_t tonic_pc12,
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *source,
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *target,
    HHSExactPass219H36BranchCandidateV1 *out_candidate
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_branch_rank(
    const HHSExactPass219H36BranchCandidateV1 *candidates,
    size_t candidate_count,
    HHSExactPass219H36BranchRankingV1 *out_ranking
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_branch_ranking_validate(
    const HHSExactPass219H36BranchCandidateV1 *candidates,
    size_t candidate_count,
    const HHSExactPass219H36BranchRankingV1 *ranking
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_knowledge_evidence(
    const HHSExactPass219H36BranchCandidateV1 *candidate,
    uint32_t graph_relation_type,
    uint32_t confidence_numerator,
    uint32_t confidence_denominator,
    HHSExactPass219H36KnowledgeEvidenceV1 *out_evidence
);

#ifdef __cplusplus
}
#endif
#endif
