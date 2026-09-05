#ifndef HHS_PASS219_HARMONIC36_HASH216_RNA_BINDING_1_0_H
#define HHS_PASS219_HARMONIC36_HASH216_RNA_BINDING_1_0_H

#include "hhs_pass219_harmonic36_factorization_fabric_1_0.h"
#include "hhs_pass219_rna_transcription_1_10.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_RNA_BINDING_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_H36_RNA_BINDING_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_H36_RNA_BINDING_VERSION_PATCH 0U

typedef struct HHSExactPass219H36RNAOperationBindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t cell81;
    uint8_t operation64;
    uint16_t vm81_linear5184;
    uint16_t hydration_slot5184;
    uint16_t g243;
    int8_t lo_shu_group;
    uint8_t trit;
    uint8_t h36_word144;
    uint8_t h36_bit36;
    uint8_t phase_left8;
    uint8_t phase_right8;
    uint8_t harmonic_rule64;
    uint8_t factorization_identity_preserved;
    uint8_t hydration_axis_preserved;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
} HHSExactPass219H36RNAOperationBindingV1;

typedef struct HHSExactPass219H36Hash216OccurrenceBindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint16_t absolute_position216;
    uint8_t lane_role;
    uint8_t lane_position72;
    uint8_t glyph;
    uint8_t symbol_index72;
    uint16_t native_hash72_linear5184;
    uint8_t h36_word144;
    uint8_t h36_bit36;
    uint8_t vm81_cell81;
    uint8_t vm81_operation64;
    uint8_t phase_left8;
    uint8_t phase_right8;
    uint8_t harmonic_rule64;
    uint8_t sha256_index_present;
    uint8_t directional_identity_preserved;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t sha256_index_record[HHS_EXACT_PASS219_HASH216_SHA256_BYTES];
} HHSExactPass219H36Hash216OccurrenceBindingV1;

typedef struct HHSExactPass219H36Hash216TransitionBindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint16_t occurrence_count;
    uint16_t resolved_index_count;
    uint8_t lane_unique_symbol_count[3];
    uint8_t lane_repeat_count[3];
    uint8_t repeat_allowed_manifold;
    uint8_t no_repeat_core_recognized;
    uint8_t directional_lane_order_preserved;
    uint8_t vector_indexes_complete;
    uint8_t all_occurrences_factorized;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    HHSExactPass219H36Hash216OccurrenceBindingV1
        occurrences[HHS_EXACT_PASS219_HASH216_OCCURRENCES];
} HHSExactPass219H36Hash216TransitionBindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_h36_rna_binding_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_rna_operation_bind(
    const HHSExactPass219HydrationCoordinateV1 *coordinate,
    HHSExactPass219H36RNAOperationBindingV1 *out_binding
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_hash216_occurrence_bind(
    const HHSExactPass219Hash72TokenOccurrenceV1 *occurrence,
    HHSExactPass219H36Hash216OccurrenceBindingV1 *out_binding
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_hash216_transition_bind(
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    HHSExactPass219H36Hash216TransitionBindingV1 *out_binding
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_hash216_transition_binding_validate(
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    const HHSExactPass219H36Hash216TransitionBindingV1 *binding
);

#ifdef __cplusplus
}
#endif
#endif
