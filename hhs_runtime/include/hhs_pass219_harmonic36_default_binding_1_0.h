#ifndef HHS_PASS219_HARMONIC36_DEFAULT_BINDING_1_0_H
#define HHS_PASS219_HARMONIC36_DEFAULT_BINDING_1_0_H

#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_BINDING_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_H36_BINDING_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_H36_BINDING_VERSION_PATCH 0U

typedef struct HHSExactPass219H36DefaultBindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t frame_bits;
    uint32_t vm81_cells;
    uint32_t operation_count;
    uint32_t q144_cells;
    uint32_t word_bits;

    uint8_t default_state_machine_required;
    uint8_t hydration_required;
    uint8_t compression_required;
    uint8_t phase_gear_required;
    uint8_t gpu_candidate_path_required;
    uint8_t hash216_vector_cache_required;
    uint8_t knowledge_graph_required;
    uint8_t quantum_like_branch_required;
    uint8_t rna_dna_transcription_required;
    uint8_t octonion_ternary_required;
    uint8_t loshu_sudoku_qudit_required;
    uint8_t native_36bit_execution_required;
    uint8_t multimodal_generalization_required;

    uint8_t singleton_vm81_authority_preserved;
    uint8_t independent_vm81_authority;
    uint8_t independent_hash72_authority;
    uint8_t independent_hash216_authority;
    uint8_t floating_point_canonical_authority;
} HHSExactPass219H36DefaultBindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_h36_default_binding_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_default_binding(
    HHSExactPass219H36DefaultBindingV1 *out_binding
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_default_binding_validate(
    const HHSExactPass219H36DefaultBindingV1 *binding
);

#ifdef __cplusplus
}
#endif
#endif
