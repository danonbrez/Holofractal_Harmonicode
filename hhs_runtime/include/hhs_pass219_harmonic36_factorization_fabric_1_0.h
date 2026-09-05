#ifndef HHS_PASS219_HARMONIC36_FACTORIZATION_FABRIC_1_0_H
#define HHS_PASS219_HARMONIC36_FACTORIZATION_FABRIC_1_0_H

#include "hhs_pass219_harmonic36_default_binding_1_0.h"
#include "hhs_pass219_mandatory_genesis_scaling_1_22.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_FABRIC_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_H36_FABRIC_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_H36_FABRIC_VERSION_PATCH 0U

typedef struct HHSExactPass219H36FactorizationCircuitV1 {
    uint32_t struct_size;
    uint32_t version;
    uint16_t linear5184;
    uint8_t vm81_cell81;
    uint8_t vm81_operation64;
    uint8_t hash72_row72;
    uint8_t hash72_col72;
    uint8_t phase_left8;
    uint8_t phase_right8;
    uint8_t h36_word144;
    uint8_t h36_bit36;
    uint8_t q144_row12;
    uint8_t q144_col12;
    uint8_t et_bank3;
    uint8_t et_pitch12;
    uint8_t harmonic_rule64;
    uint8_t genesis_equal;
    uint8_t factorization_identity_preserved;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
} HHSExactPass219H36FactorizationCircuitV1;

typedef struct HHSExactPass219H36HydrationWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t frame_bits;
    uint32_t h36_word_count;
    uint32_t h36_word_bits;
    uint8_t vm81_to_h36_equal;
    uint8_t h36_to_vm81_equal;
    uint8_t exact_roundtrip_equal;
    uint8_t factorization_identity_preserved;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36HydrationWitnessV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_h36_factorization_fabric_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_factorization_circuit(
    uint16_t linear5184,
    HHSExactPass219H36FactorizationCircuitV1 *out_circuit
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_factorization_circuit_validate(
    const HHSExactPass219H36FactorizationCircuitV1 *circuit
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_hydration_roundtrip(
    const HHSExactVM81Frame *frame,
    HHSExactPass219H36HydrationWitnessV1 *out_witness
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_hydration_witness_validate(
    const HHSExactPass219H36HydrationWitnessV1 *witness
);

#ifdef __cplusplus
}
#endif
#endif
