#ifndef HHS_PASS219_HARMONIC36_NESTED_VM_1_0_H
#define HHS_PASS219_HARMONIC36_NESTED_VM_1_0_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_H36_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_H36_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_H36_WORD_BITS 36U
#define HHS_EXACT_PASS219_H36_WORD_COUNT 144U
#define HHS_EXACT_PASS219_H36_FRAME_BITS 5184U
#define HHS_EXACT_PASS219_H36_ET_CLASSES 12U
#define HHS_EXACT_PASS219_H36_ET_BANKS 3U
#define HHS_EXACT_PASS219_H36_ACCUMULATORS 16U
#define HHS_EXACT_PASS219_H36_ADDRESS_BITS 18U
#define HHS_EXACT_PASS219_H36_RULE_COUNT 64U
#define HHS_EXACT_PASS219_H36_WORD_MASK UINT64_C(0xFFFFFFFFF)
#define HHS_EXACT_PASS219_H36_HALF_MASK UINT64_C(0x3FFFF)

typedef enum HHSExactPass219H36TrapV1 {
    HHS_EXACT_PASS219_H36_TRAP_NONE = 0,
    HHS_EXACT_PASS219_H36_TRAP_RANGE = 1,
    HHS_EXACT_PASS219_H36_TRAP_UNIMPLEMENTED_UUO = 2,
    HHS_EXACT_PASS219_H36_TRAP_NONCANONICAL_FLOAT = 3,
    HHS_EXACT_PASS219_H36_TRAP_UNIMPLEMENTED_OPCODE = 4,
    HHS_EXACT_PASS219_H36_TRAP_INDIRECT_LIMIT = 5,
    HHS_EXACT_PASS219_H36_TRAP_HARMONIC_RULE = 6
} HHSExactPass219H36TrapV1;

typedef enum HHSExactPass219H36HarmonicEraV1 {
    HHS_EXACT_PASS219_H36_ERA_DIATONIC = 1,
    HHS_EXACT_PASS219_H36_ERA_ROMANTIC = 2,
    HHS_EXACT_PASS219_H36_ERA_JAZZ = 3,
    HHS_EXACT_PASS219_H36_ERA_MODERN_JAZZ = 4
} HHSExactPass219H36HarmonicEraV1;

typedef enum HHSExactPass219H36HarmonicFunctionV1 {
    HHS_EXACT_PASS219_H36_FUNCTION_TONIC = 1,
    HHS_EXACT_PASS219_H36_FUNCTION_PREDOMINANT = 2,
    HHS_EXACT_PASS219_H36_FUNCTION_DOMINANT = 3,
    HHS_EXACT_PASS219_H36_FUNCTION_MODAL = 4,
    HHS_EXACT_PASS219_H36_FUNCTION_EMBELLISHING = 5,
    HHS_EXACT_PASS219_H36_FUNCTION_SYMMETRIC = 6,
    HHS_EXACT_PASS219_H36_FUNCTION_TRANSFORM = 7
} HHSExactPass219H36HarmonicFunctionV1;

typedef enum HHSExactPass219H36HarmonicRuleV1 {
    HHS_EXACT_PASS219_H36_RULE_INVALID = 0,
    HHS_EXACT_PASS219_H36_RULE_I_MAJOR = 1,
    HHS_EXACT_PASS219_H36_RULE_II_MINOR7 = 2,
    HHS_EXACT_PASS219_H36_RULE_V7 = 3,
    HHS_EXACT_PASS219_H36_RULE_VI_MINOR7 = 4,
    HHS_EXACT_PASS219_H36_RULE_VII_DIM7 = 5,
    HHS_EXACT_PASS219_H36_RULE_SECONDARY_V_OF_V = 6,
    HHS_EXACT_PASS219_H36_RULE_SECONDARY_VII_OF_V = 7,
    HHS_EXACT_PASS219_H36_RULE_BORROWED_IV_MINOR = 8,
    HHS_EXACT_PASS219_H36_RULE_BORROWED_BVI_MAJOR = 9,
    HHS_EXACT_PASS219_H36_RULE_NEAPOLITAN6 = 10,
    HHS_EXACT_PASS219_H36_RULE_ITALIAN_AUG6 = 11,
    HHS_EXACT_PASS219_H36_RULE_FRENCH_AUG6 = 12,
    HHS_EXACT_PASS219_H36_RULE_GERMAN_AUG6 = 13,
    HHS_EXACT_PASS219_H36_RULE_SWISS_AUG6 = 14,
    HHS_EXACT_PASS219_H36_RULE_COMMON_TONE_DIM7 = 15,
    HHS_EXACT_PASS219_H36_RULE_COMMON_TONE_AUG6 = 16,
    HHS_EXACT_PASS219_H36_RULE_AUGMENTED_DOMINANT_PASSING = 17,
    HHS_EXACT_PASS219_H36_RULE_CHROMATIC_MEDIANT_BIII = 18,
    HHS_EXACT_PASS219_H36_RULE_CHROMATIC_MEDIANT_III = 19,
    HHS_EXACT_PASS219_H36_RULE_CHROMATIC_MEDIANT_BVI = 20,
    HHS_EXACT_PASS219_H36_RULE_CHROMATIC_MEDIANT_VI = 21,
    HHS_EXACT_PASS219_H36_RULE_EQUAL_DIVISION_MAJOR_THIRDS = 22,
    HHS_EXACT_PASS219_H36_RULE_EQUAL_DIVISION_MINOR_THIRDS = 23,
    HHS_EXACT_PASS219_H36_RULE_OMNIBUS_DOMINANT = 24,
    HHS_EXACT_PASS219_H36_RULE_JAZZ_II_MINOR7 = 25,
    HHS_EXACT_PASS219_H36_RULE_JAZZ_V7 = 26,
    HHS_EXACT_PASS219_H36_RULE_JAZZ_I_MAJOR7 = 27,
    HHS_EXACT_PASS219_H36_RULE_MINOR_II_HALFDIM7 = 28,
    HHS_EXACT_PASS219_H36_RULE_MINOR_V7_B9 = 29,
    HHS_EXACT_PASS219_H36_RULE_MINOR_I_MINMAJ7 = 30,
    HHS_EXACT_PASS219_H36_RULE_TRITONE_SUB_BII7 = 31,
    HHS_EXACT_PASS219_H36_RULE_BACKDOOR_BVII7 = 32,
    HHS_EXACT_PASS219_H36_RULE_V7_ALTERED = 33,
    HHS_EXACT_PASS219_H36_RULE_V7_LYDIAN_DOMINANT = 34,
    HHS_EXACT_PASS219_H36_RULE_V7_HALF_WHOLE = 35,
    HHS_EXACT_PASS219_H36_RULE_V7_WHOLE_TONE = 36,
    HHS_EXACT_PASS219_H36_RULE_DORIAN_MODAL_TONIC = 37,
    HHS_EXACT_PASS219_H36_RULE_LYDIAN_MODAL_TONIC = 38,
    HHS_EXACT_PASS219_H36_RULE_MIXOLYDIAN_MODAL_TONIC = 39,
    HHS_EXACT_PASS219_H36_RULE_QUARTAL_MODAL = 40,
    HHS_EXACT_PASS219_H36_RULE_UPPER_STRUCTURE_II_OVER_V7 = 41,
    HHS_EXACT_PASS219_H36_RULE_UPPER_STRUCTURE_BIII_OVER_V7 = 42,
    HHS_EXACT_PASS219_H36_RULE_HYBRID_SUS_DOMINANT = 43,
    HHS_EXACT_PASS219_H36_RULE_CONSTANT_STRUCTURE_MAJOR7 = 44,
    HHS_EXACT_PASS219_H36_RULE_COLTRANE_THREE_TONIC = 45,
    HHS_EXACT_PASS219_H36_RULE_BLUES_TONIC7 = 46,
    HHS_EXACT_PASS219_H36_RULE_DIMINISHED_PASSING_TO_II = 47,
    HHS_EXACT_PASS219_H36_RULE_PIVOT_CHORD_MODULATION = 48,
    HHS_EXACT_PASS219_H36_RULE_ENHARMONIC_DIM7_MODULATION = 49,
    HHS_EXACT_PASS219_H36_RULE_ENHARMONIC_GER6_DOM7 = 50,
    HHS_EXACT_PASS219_H36_RULE_PARALLEL_CHROMATIC_SEQUENCE = 51,
    HHS_EXACT_PASS219_H36_RULE_LAMENT_BASS = 52,
    HHS_EXACT_PASS219_H36_RULE_DOMINANT_PEDAL = 53,
    HHS_EXACT_PASS219_H36_RULE_MINOR_PLAGAL = 54,
    HHS_EXACT_PASS219_H36_RULE_DECEPTIVE_DOMINANT = 55,
    HHS_EXACT_PASS219_H36_RULE_EXTENDED_DOMINANT_CHAIN = 56,
    HHS_EXACT_PASS219_H36_RULE_RELATED_II_TRITONE = 57,
    HHS_EXACT_PASS219_H36_RULE_SUS_B9_DOMINANT = 58,
    HHS_EXACT_PASS219_H36_RULE_MAJOR6_TONIC = 59,
    HHS_EXACT_PASS219_H36_RULE_MINOR6_TONIC = 60,
    HHS_EXACT_PASS219_H36_RULE_MAJOR69_TONIC = 61,
    HHS_EXACT_PASS219_H36_RULE_MINOR69_TONIC = 62,
    HHS_EXACT_PASS219_H36_RULE_POLYCHORD_DOMINANT = 63,
    HHS_EXACT_PASS219_H36_RULE_FOUR_TONIC_MINOR_THIRDS = 64
} HHSExactPass219H36HarmonicRuleV1;

typedef struct HHSExactPass219H36InstructionV1 {
    uint64_t word36;
    uint16_t opcode9;
    uint8_t accumulator4;
    uint8_t indirect1;
    uint8_t index4;
    uint32_t address18;
} HHSExactPass219H36InstructionV1;

typedef struct HHSExactPass219H36CoordinateV1 {
    uint16_t linear5184;
    uint8_t word144;
    uint8_t bit36;
    uint8_t et_bank3;
    uint8_t et_pitch12;
    uint8_t q144_row12;
    uint8_t q144_col12;
    uint8_t vm81_cell81;
    uint8_t vm81_operation64;
    uint8_t hash72_row72;
    uint8_t hash72_col72;
    uint8_t phase_left8;
    uint8_t phase_right8;
    uint8_t harmonic_rule64;
} HHSExactPass219H36CoordinateV1;

typedef struct HHSExactPass219H36HarmonicRuleDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint16_t rule_id;
    uint8_t era;
    uint8_t function_class;
    uint16_t core_mask12;
    uint16_t tension_mask12;
    uint16_t resolution_mask12;
    uint16_t scale_mask12;
    uint8_t preferred_bass_pc12;
    uint8_t flags;
} HHSExactPass219H36HarmonicRuleDescriptorV1;

typedef struct HHSExactPass219H36HarmonicTransitionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint16_t common_tones;
    uint16_t semitone_resolutions;
    uint16_t exact_voice_leading_cost;
    uint16_t source_pitch_count;
    uint16_t target_pitch_count;
} HHSExactPass219H36HarmonicTransitionV1;

typedef struct HHSExactPass219H36VMStateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t memory[HHS_EXACT_PASS219_H36_WORD_COUNT];
    uint64_t accumulators[HHS_EXACT_PASS219_H36_ACCUMULATORS];
    uint32_t pc18;
    uint32_t steps;
    uint32_t last_effective_address18;
    uint16_t last_opcode9;
    uint8_t halted;
    uint8_t trap;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36VMStateV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_h36_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_validate(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_coordinate(uint16_t linear5184, HHSExactPass219H36CoordinateV1 *out);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_instruction_encode(uint16_t opcode9, uint8_t ac4, uint8_t indirect1, uint8_t index4, uint32_t address18, uint64_t *out_word36);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_instruction_decode(uint64_t word36, HHSExactPass219H36InstructionV1 *out);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_import_vm81(const HHSExactVM81Frame *frame, HHSExactPass219H36VMStateV1 *state);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_export_vm81(const HHSExactPass219H36VMStateV1 *state, HHSExactVM81Frame *frame);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_equal_temperament_seed(HHSExactPass219H36VMStateV1 *state);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_harmonic_pack(uint16_t core_mask12, uint16_t tension_mask12, uint16_t resolution_mask12, uint64_t *out_word36);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_harmonic_unpack(uint64_t word36, uint16_t *out_core_mask12, uint16_t *out_tension_mask12, uint16_t *out_resolution_mask12);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_harmonic_rule(uint16_t rule_id, HHSExactPass219H36HarmonicRuleDescriptorV1 *out);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_harmonic_render(uint16_t rule_id, uint8_t tonic_pc12, uint64_t *out_word36);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_harmonic_transpose(uint64_t word36, uint8_t semitones, uint64_t *out_word36);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_harmonic_transition(uint64_t source_word36, uint64_t target_word36, HHSExactPass219H36HarmonicTransitionV1 *out);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_vm_init(HHSExactPass219H36VMStateV1 *state);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_vm_step(HHSExactPass219H36VMStateV1 *state);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_vm_run(HHSExactPass219H36VMStateV1 *state, uint32_t max_steps, uint32_t *out_steps);

#ifdef __cplusplus
}
#endif
#endif
