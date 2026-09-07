#ifndef HHS_PASS219_CORE_CONSTRAINT_DYNAMIC_CIRCUIT_1_23_H
#define HHS_PASS219_CORE_CONSTRAINT_DYNAMIC_CIRCUIT_1_23_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_CORE_CIRCUIT_VERSION UINT32_C(0x00010017)
#define HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE_BYTES UINT32_C(542)
#define HHS_EXACT_PASS219_CORE_CIRCUIT_SHA256_BYTES UINT32_C(32)
#define HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_FEATURES UINT32_C(8)
#define HHS_EXACT_PASS219_CORE_CIRCUIT_LOSHU_FEATURES UINT32_C(9)
#define HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT UINT32_C(8)
#define HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS UINT32_C(72)
#define HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM UINT32_C(5)
#define HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_BOUND INT32_C(5184)

typedef struct HHSExactPass219CoreCircuitDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t source_bytes;
    uint32_t a2;
    uint32_t b2;
    uint32_t c2;
    uint32_t b4;
    uint32_t b6;
    uint32_t c4;
    uint32_t b6c4;
    uint32_t update_quantum;
    uint32_t phase_modulus;
    uint8_t source_sha256[HHS_EXACT_PASS219_CORE_CIRCUIT_SHA256_BYTES];
    uint8_t verbatim_source_preserved;
    uint8_t single_fused_circuit;
    uint8_t exact_integer_only;
    uint8_t online_learning_enabled;
    uint8_t vm81_hydration_bridge;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[2];
} HHSExactPass219CoreCircuitDescriptorV1;

typedef struct HHSExactPass219CoreCircuitFeaturesV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t word_visits;
    uint32_t nonzero_words;
    uint32_t total_popcount;
    uint32_t phase_popcount[HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_FEATURES];
    uint32_t loshu_popcount[HHS_EXACT_PASS219_CORE_CIRCUIT_LOSHU_FEATURES];
    int8_t trinary_phase[HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_FEATURES];
    uint8_t reserved0[8];
    uint64_t xor_signature64;
    uint64_t sum_signature64;
    uint64_t hydration_signature64;
} HHSExactPass219CoreCircuitFeaturesV1;

typedef struct HHSExactPass219CoreCircuitStateV1 {
    uint32_t struct_size;
    uint32_t version;
    int32_t weights[HHS_EXACT_PASS219_CORE_CIRCUIT_WEIGHT_COUNT];
    int32_t bias;
    uint32_t update_count;
    uint64_t step_count;
    uint8_t candidate_only;
    uint8_t bounded_weights;
    uint8_t exact_integer_only;
    uint8_t floating_point_authority;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
} HHSExactPass219CoreCircuitStateV1;

typedef struct HHSExactPass219CoreCircuitDecisionV1 {
    uint32_t struct_size;
    uint32_t version;
    int32_t score;
    int8_t prediction_trinary;
    int8_t feedback_trinary;
    uint8_t predicted_candidate_id;
    uint8_t updated;
    uint32_t update_count;
    uint64_t step_count;
    uint64_t hydration_signature64;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t floating_point_authority;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t reserved0;
} HHSExactPass219CoreCircuitDecisionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_core_circuit_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_core_circuit_descriptor(
    HHSExactPass219CoreCircuitDescriptorV1 *out_descriptor
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_core_circuit_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_core_circuit_state_init(
    HHSExactPass219CoreCircuitStateV1 *out_state
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_core_circuit_extract(
    const HHSExactVM81Frame *frame,
    HHSExactPass219CoreCircuitFeaturesV1 *out_features
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_core_circuit_predict(
    const HHSExactPass219CoreCircuitFeaturesV1 *features,
    const HHSExactPass219CoreCircuitStateV1 *state,
    HHSExactPass219CoreCircuitDecisionV1 *out_decision
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_core_circuit_step(
    const HHSExactVM81Frame *frame,
    int8_t feedback_trinary,
    HHSExactPass219CoreCircuitStateV1 *state,
    HHSExactPass219CoreCircuitFeaturesV1 *out_features,
    HHSExactPass219CoreCircuitDecisionV1 *out_decision
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_core_circuit_validate_state(
    const HHSExactPass219CoreCircuitStateV1 *state
);

#ifdef __cplusplus
}
#endif

#endif
