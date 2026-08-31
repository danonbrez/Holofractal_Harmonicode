#include "../include/hhs_pass219_harmonic36_factorization_fabric_1_0.h"

#include <string.h>

static uint32_t h36_fabric_version_word(void) {
    return (HHS_EXACT_PASS219_H36_FABRIC_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_H36_FABRIC_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_H36_FABRIC_VERSION_PATCH;
}

uint32_t hhs_exact_pass219_h36_factorization_fabric_version(void) {
    return h36_fabric_version_word();
}

HHSExactStatus hhs_exact_pass219_h36_factorization_circuit(
    uint16_t linear5184,
    HHSExactPass219H36FactorizationCircuitV1 *out_circuit
) {
    HHSExactPass219H36CoordinateV1 h36;
    HHSExactPass219GenesisAddressV1 genesis;
    HHSExactStatus status;

    if (out_circuit == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_h36_coordinate(linear5184, &h36);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_genesis_address_decode(linear5184, &genesis);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (genesis.linear5184 != h36.linear5184 ||
        genesis.cell81 != h36.vm81_cell81 ||
        genesis.operation64 != h36.vm81_operation64 ||
        genesis.phase_alpha8 != h36.phase_left8 ||
        genesis.phase_beta8 != h36.phase_right8 ||
        genesis.hash72_row != h36.hash72_row72 ||
        genesis.hash72_column != h36.hash72_col72)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_circuit, 0, sizeof(*out_circuit));
    out_circuit->struct_size = (uint32_t)sizeof(*out_circuit);
    out_circuit->version = h36_fabric_version_word();
    out_circuit->linear5184 = linear5184;
    out_circuit->vm81_cell81 = h36.vm81_cell81;
    out_circuit->vm81_operation64 = h36.vm81_operation64;
    out_circuit->hash72_row72 = h36.hash72_row72;
    out_circuit->hash72_col72 = h36.hash72_col72;
    out_circuit->phase_left8 = h36.phase_left8;
    out_circuit->phase_right8 = h36.phase_right8;
    out_circuit->h36_word144 = h36.word144;
    out_circuit->h36_bit36 = h36.bit36;
    out_circuit->q144_row12 = h36.q144_row12;
    out_circuit->q144_col12 = h36.q144_col12;
    out_circuit->et_bank3 = h36.et_bank3;
    out_circuit->et_pitch12 = h36.et_pitch12;
    out_circuit->harmonic_rule64 = h36.harmonic_rule64;
    out_circuit->genesis_equal = 1U;
    out_circuit->factorization_identity_preserved = 1U;
    out_circuit->canonical_mutation_authority = 0U;
    out_circuit->canonical_hash72_authority = 0U;
    out_circuit->canonical_persistence_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_factorization_circuit_validate(
    const HHSExactPass219H36FactorizationCircuitV1 *circuit
) {
    HHSExactPass219H36FactorizationCircuitV1 expected;
    HHSExactStatus status;

    if (circuit == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (circuit->struct_size != sizeof(*circuit) ||
        circuit->version != h36_fabric_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = hhs_exact_pass219_h36_factorization_circuit(
        circuit->linear5184, &expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return memcmp(circuit, &expected, sizeof(expected)) == 0
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_h36_hydration_roundtrip(
    const HHSExactVM81Frame *frame,
    HHSExactPass219H36HydrationWitnessV1 *out_witness
) {
    HHSExactPass219H36VMStateV1 h36;
    HHSExactVM81Frame reconstructed;
    HHSExactStatus status;
    uint8_t equal;

    if (frame == NULL || out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_h36_import_vm81(frame, &h36);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_h36_export_vm81(&h36, &reconstructed);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    equal = (uint8_t)(memcmp(frame, &reconstructed, sizeof(*frame)) == 0);

    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = h36_fabric_version_word();
    out_witness->frame_bits = HHS_EXACT_PASS219_H36_FRAME_BITS;
    out_witness->h36_word_count = HHS_EXACT_PASS219_H36_WORD_COUNT;
    out_witness->h36_word_bits = HHS_EXACT_PASS219_H36_WORD_BITS;
    out_witness->vm81_to_h36_equal = equal;
    out_witness->h36_to_vm81_equal = equal;
    out_witness->exact_roundtrip_equal = equal;
    out_witness->factorization_identity_preserved = equal;
    out_witness->canonical_mutation_authority = 0U;
    out_witness->canonical_hash72_authority = 0U;
    out_witness->canonical_persistence_authority = 0U;
    out_witness->floating_point_authority = 0U;

    return equal != 0U
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_h36_hydration_witness_validate(
    const HHSExactPass219H36HydrationWitnessV1 *witness
) {
    if (witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size != sizeof(*witness) ||
        witness->version != h36_fabric_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->frame_bits != HHS_EXACT_PASS219_H36_FRAME_BITS ||
        witness->h36_word_count != HHS_EXACT_PASS219_H36_WORD_COUNT ||
        witness->h36_word_bits != HHS_EXACT_PASS219_H36_WORD_BITS ||
        witness->vm81_to_h36_equal != 1U ||
        witness->h36_to_vm81_equal != 1U ||
        witness->exact_roundtrip_equal != 1U ||
        witness->factorization_identity_preserved != 1U ||
        witness->canonical_mutation_authority != 0U ||
        witness->canonical_hash72_authority != 0U ||
        witness->canonical_persistence_authority != 0U ||
        witness->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}
