#ifndef HHS_PASS219_HARMONICODE_GLOBAL_CONSTRAINT_MEMBRANE_1_21_9_H
#define HHS_PASS219_HARMONICODE_GLOBAL_CONSTRAINT_MEMBRANE_1_21_9_H

#include "hhs_pass219_authority_router_1_21_6.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_GLOBAL_MEMBRANE_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_GLOBAL_MEMBRANE_VERSION_MINOR 21U
#define HHS_EXACT_PASS219_GLOBAL_MEMBRANE_VERSION_PATCH 9U
#define HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES 32U
#define HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT 5U
#define HHS_EXACT_PASS219_GLOBAL_MEMBRANE_EQUALITY_TOKEN_COUNT 11U
#define HHS_EXACT_PASS219_GLOBAL_MEMBRANE_LITERAL_EQUALS_COUNT 16U
#define HHS_EXACT_PASS219_GLOBAL_MEMBRANE_NO_FALSE_GATE 0xffffffffU

typedef enum HHSExactPass219GlobalMembraneDecisionV1 {
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REJECT = 0,
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_PROPAGATE = 1
} HHSExactPass219GlobalMembraneDecisionV1;

typedef enum HHSExactPass219GlobalMembraneReasonV1 {
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_NONE = 0U,
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_BOOLEAN_GATE_FALSE = 1U << 0,
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_GLOBAL_ENVIRONMENT_INCOMPLETE = 1U << 1,
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_CROSS_LAYER_REVALIDATION_INCOMPLETE = 1U << 2,
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_LOCAL_SHADOWING_DETECTED = 1U << 3,
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_PASS169_REQUIRED = 1U << 4
} HHSExactPass219GlobalMembraneReasonV1;

typedef struct HHSExactPass219GlobalMembraneDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t combined_source_sha256[HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES];
    uint32_t boolean_gate_count;
    uint32_t equality_token_count;
    uint32_t literal_equals_count;
    uint8_t ordinary_boolean_equality;
    uint8_t all_nested_boolean_gates_must_be_true;
    uint8_t whole_equation_propagates_on_true;
    uint8_t shared_global_symbol_environment_required;
    uint8_t cross_layer_variable_effect_required;
    uint8_t final_cross_layer_revalidation_required;
    uint8_t local_symbol_shadowing_authorized;
    uint8_t pass169_whole_expression_authority_required;
    uint8_t canonical_monolithic_proof;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t persistence_mutation_authority;
    uint8_t reserved0[3];
} HHSExactPass219GlobalMembraneDescriptorV1;

typedef struct HHSExactPass219GlobalGateWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t gate_index;
    uint32_t source_offset;
    uint8_t boolean_result;
    uint8_t reserved0[3];
    uint8_t combined_source_sha256[HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES];
    uint8_t global_symbol_environment_root[HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES];
} HHSExactPass219GlobalGateWitnessV1;

typedef struct HHSExactPass219GlobalMembraneInputV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t combined_source_sha256[HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES];
    uint8_t global_symbol_environment_root[HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES];
    uint32_t gate_count;
    uint8_t global_symbol_environment_complete;
    uint8_t cross_layer_revalidation_complete;
    uint8_t local_symbol_shadowing_detected;
    uint8_t reserved0;
    HHSExactPass219GlobalGateWitnessV1 gates[HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT];
} HHSExactPass219GlobalMembraneInputV1;

typedef struct HHSExactPass219GlobalMembraneResultV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reason_mask;
    uint32_t first_false_gate;
    uint8_t source_identity_exact;
    uint8_t occurrence_provenance_exact;
    uint8_t shared_global_symbol_environment_exact;
    uint8_t all_nested_boolean_gates_true;
    uint8_t cross_layer_revalidation_complete;
    uint8_t whole_equation_propagated;
    uint8_t local_symbol_shadowing_authorized;
    uint8_t pass169_whole_expression_authority_required;
    uint8_t canonical_monolithic_proof;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t persistence_mutation_authority;
    uint8_t reserved0[3];
} HHSExactPass219GlobalMembraneResultV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_global_membrane_version(void);

/*
 * Describe the I121.9 Harmonicode gate semantics.
 *
 * `==` remains ordinary Boolean equality. The native Harmonicode extension is
 * scope-preserving propagation: only when every nested Boolean gate is true
 * under one shared symbol environment, and the final shared environment has
 * been revalidated across all layers, may the complete demarcated equation be
 * propagated to its enclosing membrane.
 *
 * This surface verifies witness structure only. It does not evaluate algebra,
 * mutate VM81, mint Hash72 receipts, persist canonical state, or replace the
 * inherited Pass169 whole-expression authority path.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_membrane_descriptor(
    HHSExactPass219GlobalMembraneDescriptorV1 *out_descriptor
);

/*
 * Evaluate one complete, source-bound gate witness bundle.
 *
 * Structural/source/provenance mismatches fail as INVARIANT_FAILURE. A valid
 * bundle containing a false Boolean gate, incomplete shared environment,
 * incomplete cross-layer revalidation, or local shadowing returns OK with a
 * REJECT decision. PROPAGATE is possible only when all of those conditions are
 * simultaneously satisfied.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_global_membrane_evaluate(
    const HHSExactPass219GlobalMembraneInputV1 *input,
    HHSExactPass219GlobalMembraneResultV1 *out_result
);

#ifdef __cplusplus
}
#endif

#endif