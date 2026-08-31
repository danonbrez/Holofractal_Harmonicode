#ifndef HHS_PASS219_HARMONIC36_COMPOSITION_GRAMMAR_1_0_H
#define HHS_PASS219_HARMONIC36_COMPOSITION_GRAMMAR_1_0_H

#include "hhs_pass219_harmonic36_branch_knowledge_fabric_1_0.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_COMPOSITION_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_H36_COMPOSITION_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_H36_COMPOSITION_VERSION_PATCH 1U

#define HHS_EXACT_PASS219_H36_COMPOSITION_VOICES 4U
#define HHS_EXACT_PASS219_H36_COMPOSITION_MAX_CANDIDATES 64U
#define HHS_EXACT_PASS219_H36_NO_SECONDARY_TARGET 255U
#define HHS_EXACT_PASS219_H36_COMPOSITION_MAX_PROGRAM_STEPS 8U
#define HHS_EXACT_PASS219_H36_COMPOSITION_TEMPLATE_COUNT 16U

typedef enum HHSExactPass219H36CompositionModeV1 {
    HHS_EXACT_PASS219_H36_MODE_MAJOR = 1,
    HHS_EXACT_PASS219_H36_MODE_MINOR = 2,
    HHS_EXACT_PASS219_H36_MODE_DORIAN = 3,
    HHS_EXACT_PASS219_H36_MODE_LYDIAN = 4,
    HHS_EXACT_PASS219_H36_MODE_MIXOLYDIAN = 5,
    HHS_EXACT_PASS219_H36_MODE_CHROMATIC = 6
} HHSExactPass219H36CompositionModeV1;

typedef enum HHSExactPass219H36CadenceV1 {
    HHS_EXACT_PASS219_H36_CADENCE_NONE = 0,
    HHS_EXACT_PASS219_H36_CADENCE_PERFECT_AUTHENTIC = 1,
    HHS_EXACT_PASS219_H36_CADENCE_IMPERFECT_AUTHENTIC = 2,
    HHS_EXACT_PASS219_H36_CADENCE_HALF = 3,
    HHS_EXACT_PASS219_H36_CADENCE_DECEPTIVE = 4,
    HHS_EXACT_PASS219_H36_CADENCE_PLAGAL = 5,
    HHS_EXACT_PASS219_H36_CADENCE_BACKDOOR = 6,
    HHS_EXACT_PASS219_H36_CADENCE_MODAL = 7
} HHSExactPass219H36CadenceV1;

typedef enum HHSExactPass219H36CompositionTemplateV1 {
    HHS_EXACT_PASS219_H36_TEMPLATE_DIATONIC_AUTHENTIC = 1,
    HHS_EXACT_PASS219_H36_TEMPLATE_DIATONIC_DECEPTIVE = 2,
    HHS_EXACT_PASS219_H36_TEMPLATE_MINOR_AUTHENTIC = 3,
    HHS_EXACT_PASS219_H36_TEMPLATE_NEAPOLITAN_CADENCE = 4,
    HHS_EXACT_PASS219_H36_TEMPLATE_ITALIAN_AUG6_CADENCE = 5,
    HHS_EXACT_PASS219_H36_TEMPLATE_FRENCH_AUG6_CADENCE = 6,
    HHS_EXACT_PASS219_H36_TEMPLATE_GERMAN_AUG6_CADENCE = 7,
    HHS_EXACT_PASS219_H36_TEMPLATE_SECONDARY_DOMINANT_CHAIN = 8,
    HHS_EXACT_PASS219_H36_TEMPLATE_JAZZ_II_V_I = 9,
    HHS_EXACT_PASS219_H36_TEMPLATE_MINOR_JAZZ_II_V_I = 10,
    HHS_EXACT_PASS219_H36_TEMPLATE_TRITONE_SUB_CHAIN = 11,
    HHS_EXACT_PASS219_H36_TEMPLATE_BACKDOOR_CADENCE = 12,
    HHS_EXACT_PASS219_H36_TEMPLATE_ALTERED_DOMINANT_CHAIN = 13,
    HHS_EXACT_PASS219_H36_TEMPLATE_COLTRANE_THREE_TONIC = 14,
    HHS_EXACT_PASS219_H36_TEMPLATE_CONSTANT_STRUCTURE = 15,
    HHS_EXACT_PASS219_H36_TEMPLATE_FOUR_TONIC_MINOR_THIRDS = 16
} HHSExactPass219H36CompositionTemplateV1;

typedef enum HHSExactPass219H36CompositionRelationV1 {
    HHS_EXACT_PASS219_H36_RELATION_INVALID = 0,
    HHS_EXACT_PASS219_H36_RELATION_FUNCTIONAL = 1,
    HHS_EXACT_PASS219_H36_RELATION_SECONDARY_FUNCTION = 2,
    HHS_EXACT_PASS219_H36_RELATION_MODAL_INTERCHANGE = 3,
    HHS_EXACT_PASS219_H36_RELATION_AUGMENTED_SIXTH = 4,
    HHS_EXACT_PASS219_H36_RELATION_NEAPOLITAN = 5,
    HHS_EXACT_PASS219_H36_RELATION_TRITONE_SUBSTITUTION = 6,
    HHS_EXACT_PASS219_H36_RELATION_BACKDOOR = 7,
    HHS_EXACT_PASS219_H36_RELATION_CHROMATIC_MEDIANT = 8,
    HHS_EXACT_PASS219_H36_RELATION_ENHARMONIC_REINTERPRETATION = 9,
    HHS_EXACT_PASS219_H36_RELATION_EQUAL_DIVISION = 10,
    HHS_EXACT_PASS219_H36_RELATION_CONSTANT_STRUCTURE = 11,
    HHS_EXACT_PASS219_H36_RELATION_MODAL = 12,
    HHS_EXACT_PASS219_H36_RELATION_JAZZ_CHORD_SCALE = 13,
    HHS_EXACT_PASS219_H36_RELATION_UPPER_STRUCTURE = 14,
    HHS_EXACT_PASS219_H36_RELATION_SYMMETRIC = 15
} HHSExactPass219H36CompositionRelationV1;

enum {
    HHS_EXACT_PASS219_H36_CONTEXT_MODAL_INTERCHANGE = 1U << 0,
    HHS_EXACT_PASS219_H36_CONTEXT_SECONDARY_FUNCTION = 1U << 1,
    HHS_EXACT_PASS219_H36_CONTEXT_ALTERED_DOMINANT = 1U << 2,
    HHS_EXACT_PASS219_H36_CONTEXT_UPPER_STRUCTURE = 1U << 3,
    HHS_EXACT_PASS219_H36_CONTEXT_POLYCHORD = 1U << 4,
    HHS_EXACT_PASS219_H36_CONTEXT_CONSTANT_STRUCTURE = 1U << 5,
    HHS_EXACT_PASS219_H36_CONTEXT_MODULATION = 1U << 6,
    HHS_EXACT_PASS219_H36_CONTEXT_MODAL = 1U << 7,
    HHS_EXACT_PASS219_H36_CONTEXT_SYMMETRIC = 1U << 8
};

typedef struct HHSExactPass219H36CompositionStateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t tonic_pc12;
    uint8_t key_center_pc12;
    uint8_t mode;
    uint8_t harmonic_rule64;
    uint8_t inversion;
    uint8_t voice_count;
    uint8_t voices[HHS_EXACT_PASS219_H36_COMPOSITION_VOICES];
    uint8_t bass_pc12;
    uint8_t soprano_pc12;
    uint8_t secondary_target_pc12;
    uint8_t target_key_center_pc12;
    uint16_t context_flags;
    uint16_t tendency_mask12;
    uint16_t chord_mask12;
    uint16_t scale_mask12;
    uint64_t rendered_word36;
    uint8_t voice_order_valid;
    uint8_t inversion_valid;
    uint8_t fixed_operation64_preserved;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36CompositionStateV1;

typedef struct HHSExactPass219H36CompositionTransitionV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219H36CompositionStateV1 source;
    HHSExactPass219H36CompositionStateV1 target;
    uint32_t relation;
    uint32_t cadence;
    uint16_t exact_voice_leading_cost;
    uint16_t common_tones;
    uint16_t semitone_resolutions;
    uint16_t contrary_motion_pairs;
    uint16_t unresolved_tendency_count;
    uint16_t parallel_perfect_count;
    uint16_t grammar_penalty;
    uint8_t progression_allowed;
    uint8_t cadence_match;
    uint8_t tendency_resolution_valid;
    uint8_t voice_leading_valid;
    uint8_t modulation_observed;
    uint8_t fixed_operation64_preserved;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36CompositionTransitionV1;

typedef struct HHSExactPass219H36CompositionCandidateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t candidate_id;
    HHSExactPass219H36BranchCandidateV1 directional_branch;
    HHSExactPass219H36CompositionTransitionV1 composition;
    uint32_t exact_rank_score;
    uint8_t candidate_only;
    uint8_t hash216_direction_preserved;
    uint8_t pass128_evidence_compatible;
    uint8_t singleton_vm81_admission_required;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36CompositionCandidateV1;

typedef struct HHSExactPass219H36CompositionRankingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t candidate_count;
    uint32_t ranked_candidate_ids[
        HHS_EXACT_PASS219_H36_COMPOSITION_MAX_CANDIDATES
    ];
    uint8_t grammar_first;
    uint8_t exact_integer_ranking;
    uint8_t stable_candidate_id_tie_break;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36CompositionRankingV1;

typedef struct HHSExactPass219H36CompositionProgramV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t template_id;
    uint8_t root_tonic_pc12;
    uint8_t step_count;
    uint16_t exact_total_voice_leading_cost;
    uint16_t total_grammar_penalty;
    uint16_t total_unresolved_tendencies;
    uint16_t total_parallel_perfects;
    uint8_t modulation_count;
    uint8_t fixed_operation64_preserved;
    uint8_t deterministic_replay;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    HHSExactPass219H36CompositionStateV1 states[
        HHS_EXACT_PASS219_H36_COMPOSITION_MAX_PROGRAM_STEPS
    ];
    HHSExactPass219H36CompositionTransitionV1 transitions[
        HHS_EXACT_PASS219_H36_COMPOSITION_MAX_PROGRAM_STEPS - 1U
    ];
} HHSExactPass219H36CompositionProgramV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_h36_composition_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_composition_state(
    uint16_t harmonic_rule64,
    uint8_t tonic_pc12,
    uint8_t key_center_pc12,
    uint8_t mode,
    uint8_t inversion,
    uint8_t secondary_target_pc12,
    uint8_t target_key_center_pc12,
    uint16_t context_flags,
    const HHSExactPass219H36CompositionStateV1 *previous,
    HHSExactPass219H36CompositionStateV1 *out_state
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_composition_transition(
    const HHSExactPass219H36CompositionStateV1 *source,
    const HHSExactPass219H36CompositionStateV1 *target,
    HHSExactPass219H36CompositionTransitionV1 *out_transition
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_composition_candidate(
    uint32_t candidate_id,
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *source_occurrence,
    const HHSExactPass219H36Hash216OccurrenceBindingV1 *target_occurrence,
    const HHSExactPass219H36CompositionTransitionV1 *transition,
    HHSExactPass219H36CompositionCandidateV1 *out_candidate
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_composition_rank(
    const HHSExactPass219H36CompositionCandidateV1 *candidates,
    size_t candidate_count,
    HHSExactPass219H36CompositionRankingV1 *out_ranking
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_composition_ranking_validate(
    const HHSExactPass219H36CompositionCandidateV1 *candidates,
    size_t candidate_count,
    const HHSExactPass219H36CompositionRankingV1 *ranking
);

HHS_EXACT_API uint32_t hhs_exact_pass219_h36_composition_template_count(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_composition_program_build(
    uint32_t template_id,
    uint8_t root_tonic_pc12,
    HHSExactPass219H36CompositionProgramV1 *out_program
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_composition_program_validate(
    const HHSExactPass219H36CompositionProgramV1 *program
);

#ifdef __cplusplus
}
#endif
#endif
