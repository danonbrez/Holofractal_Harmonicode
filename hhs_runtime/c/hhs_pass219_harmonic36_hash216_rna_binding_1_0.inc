#include "../include/hhs_pass219_harmonic36_hash216_rna_binding_1_0.h"

#include <string.h>

static uint32_t h36_rna_binding_version_word(void) {
    return (HHS_EXACT_PASS219_H36_RNA_BINDING_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_H36_RNA_BINDING_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_H36_RNA_BINDING_VERSION_PATCH;
}

static HHSExactStatus h36_symbol_index72(uint8_t glyph, uint8_t *out_index) {
    uint32_t i;
    if (out_index == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i) {
        if ((uint8_t)HHS_EXACT_HASH72_ALPHABET[i] == glyph) {
            *out_index = (uint8_t)i;
            return HHS_EXACT_STATUS_OK;
        }
    }
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

uint32_t hhs_exact_pass219_h36_rna_binding_version(void) {
    return h36_rna_binding_version_word();
}

HHSExactStatus hhs_exact_pass219_h36_rna_operation_bind(
    const HHSExactPass219HydrationCoordinateV1 *coordinate,
    HHSExactPass219H36RNAOperationBindingV1 *out_binding
) {
    HHSExactPass219H36FactorizationCircuitV1 circuit;
    uint8_t cell;
    int8_t lo_shu_group;
    uint8_t operation;
    uint16_t g243;
    uint16_t linear;
    HHSExactStatus status;

    if (coordinate == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_coordinate_to_pass189(
        coordinate, &cell, &lo_shu_group, &operation, &g243);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    linear = (uint16_t)((uint16_t)cell * HHS_EXACT_PASS219_OPERATION64_COUNT +
                        (uint16_t)operation);
    status = hhs_exact_pass219_h36_factorization_circuit(linear, &circuit);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (circuit.vm81_cell81 != cell ||
        circuit.vm81_operation64 != operation)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = h36_rna_binding_version_word();
    out_binding->cell81 = cell;
    out_binding->operation64 = operation;
    out_binding->vm81_linear5184 = linear;
    out_binding->hydration_slot5184 = coordinate->slot5184;
    out_binding->g243 = g243;
    out_binding->lo_shu_group = lo_shu_group;
    out_binding->trit = coordinate->trit;
    out_binding->h36_word144 = circuit.h36_word144;
    out_binding->h36_bit36 = circuit.h36_bit36;
    out_binding->phase_left8 = circuit.phase_left8;
    out_binding->phase_right8 = circuit.phase_right8;
    out_binding->harmonic_rule64 = circuit.harmonic_rule64;
    out_binding->factorization_identity_preserved = 1U;
    out_binding->hydration_axis_preserved = 1U;
    out_binding->canonical_mutation_authority = 0U;
    out_binding->canonical_hash72_authority = 0U;
    out_binding->canonical_persistence_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_hash216_occurrence_bind(
    const HHSExactPass219Hash72TokenOccurrenceV1 *occurrence,
    HHSExactPass219H36Hash216OccurrenceBindingV1 *out_binding
) {
    HHSExactPass219H36FactorizationCircuitV1 circuit;
    uint8_t symbol_index;
    uint16_t linear;
    HHSExactStatus status;

    if (occurrence == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (occurrence->struct_size < sizeof(*occurrence) ||
        occurrence->version != hhs_exact_pass219_rna_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (occurrence->lane_role > HHS_EXACT_PASS219_HASH216_LANE_RECEIPT ||
        occurrence->lane_position72 >= HHS_EXACT_HASH72_LEN ||
        occurrence->absolute_position216 !=
            (uint16_t)((uint16_t)occurrence->lane_role * HHS_EXACT_HASH72_LEN +
                       occurrence->lane_position72) ||
        occurrence->sha256_index_present > 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = h36_symbol_index72(occurrence->glyph, &symbol_index);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    linear = (uint16_t)((uint16_t)occurrence->lane_position72 *
                        HHS_EXACT_HASH72_LEN + symbol_index);
    status = hhs_exact_pass219_h36_factorization_circuit(linear, &circuit);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (circuit.hash72_row72 != occurrence->lane_position72 ||
        circuit.hash72_col72 != symbol_index)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = h36_rna_binding_version_word();
    out_binding->absolute_position216 = occurrence->absolute_position216;
    out_binding->lane_role = occurrence->lane_role;
    out_binding->lane_position72 = occurrence->lane_position72;
    out_binding->glyph = occurrence->glyph;
    out_binding->symbol_index72 = symbol_index;
    out_binding->native_hash72_linear5184 = linear;
    out_binding->h36_word144 = circuit.h36_word144;
    out_binding->h36_bit36 = circuit.h36_bit36;
    out_binding->vm81_cell81 = circuit.vm81_cell81;
    out_binding->vm81_operation64 = circuit.vm81_operation64;
    out_binding->phase_left8 = circuit.phase_left8;
    out_binding->phase_right8 = circuit.phase_right8;
    out_binding->harmonic_rule64 = circuit.harmonic_rule64;
    out_binding->sha256_index_present = occurrence->sha256_index_present;
    out_binding->directional_identity_preserved = 1U;
    out_binding->canonical_mutation_authority = 0U;
    out_binding->canonical_hash72_authority = 0U;
    out_binding->canonical_persistence_authority = 0U;
    memcpy(out_binding->sha256_index_record,
           occurrence->sha256_index_record,
           HHS_EXACT_PASS219_HASH216_SHA256_BYTES);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_hash216_transition_bind(
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    HHSExactPass219H36Hash216TransitionBindingV1 *out_binding
) {
    uint8_t seen[3][HHS_EXACT_HASH72_LEN];
    uint32_t present_count = 0U;
    uint32_t i;

    if (transition == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (transition->struct_size < sizeof(*transition) ||
        transition->version != hhs_exact_pass219_rna_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    memset(seen, 0, sizeof(seen));
    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = h36_rna_binding_version_word();
    out_binding->occurrence_count = HHS_EXACT_PASS219_HASH216_OCCURRENCES;
    out_binding->resolved_index_count = transition->resolved_index_count;
    out_binding->repeat_allowed_manifold = 1U;
    out_binding->directional_lane_order_preserved = 1U;
    out_binding->all_occurrences_factorized = 1U;
    out_binding->canonical_mutation_authority = 0U;
    out_binding->canonical_hash72_authority = 0U;
    out_binding->canonical_persistence_authority = 0U;

    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        HHSExactPass219H36Hash216OccurrenceBindingV1 *bound =
            &out_binding->occurrences[i];
        HHSExactStatus status =
            hhs_exact_pass219_h36_hash216_occurrence_bind(
                &transition->occurrences[i], bound);
        uint8_t lane;
        uint8_t symbol;

        if (status != HHS_EXACT_STATUS_OK)
            return status;
        if (transition->transition_word216[i] != (char)bound->glyph)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        lane = bound->lane_role;
        symbol = bound->symbol_index72;
        if (seen[lane][symbol] == 0U) {
            seen[lane][symbol] = 1U;
            out_binding->lane_unique_symbol_count[lane] += 1U;
        } else {
            out_binding->lane_repeat_count[lane] += 1U;
        }

        if (bound->sha256_index_present != 0U)
            ++present_count;
    }

    if (present_count != transition->resolved_index_count)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_binding->vector_indexes_complete =
        (uint8_t)(present_count == HHS_EXACT_PASS219_HASH216_OCCURRENCES);
    out_binding->no_repeat_core_recognized =
        (uint8_t)(out_binding->lane_unique_symbol_count[0] == HHS_EXACT_HASH72_LEN ||
                  out_binding->lane_unique_symbol_count[1] == HHS_EXACT_HASH72_LEN ||
                  out_binding->lane_unique_symbol_count[2] == HHS_EXACT_HASH72_LEN);

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_hash216_transition_binding_validate(
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    const HHSExactPass219H36Hash216TransitionBindingV1 *binding
) {
    HHSExactPass219H36Hash216TransitionBindingV1 expected;
    HHSExactStatus status;

    if (transition == NULL || binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (binding->struct_size != sizeof(*binding) ||
        binding->version != h36_rna_binding_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = hhs_exact_pass219_h36_hash216_transition_bind(
        transition, &expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return memcmp(binding, &expected, sizeof(expected)) == 0
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}
