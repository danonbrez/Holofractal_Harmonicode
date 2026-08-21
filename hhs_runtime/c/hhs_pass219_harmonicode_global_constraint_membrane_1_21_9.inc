#include "hhs_pass219_harmonicode_global_constraint_membrane_1_21_9.h"

#include <string.h>

static const uint8_t HHS219_GLOBAL_MEMBRANE_SOURCE_SHA256[
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES
] = {
    0x33U, 0x15U, 0x64U, 0x1cU, 0x8dU, 0x6aU, 0xa9U, 0xfcU,
    0x4fU, 0x39U, 0x18U, 0xecU, 0xcdU, 0xa8U, 0xe3U, 0xa4U,
    0x0cU, 0x84U, 0x45U, 0xccU, 0x41U, 0x7aU, 0x65U, 0xe5U,
    0xdeU, 0xa6U, 0x83U, 0xf6U, 0x80U, 0x20U, 0xcfU, 0x53U
};

/* Zero-based UTF-8 byte offsets of the five literal `==` gate occurrences. */
static const uint32_t HHS219_GLOBAL_MEMBRANE_GATE_OFFSETS[
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT
] = {96U, 240U, 266U, 274U, 285U};

static uint32_t hhs219_global_membrane_version_word(void) {
    return (HHS_EXACT_PASS219_GLOBAL_MEMBRANE_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_GLOBAL_MEMBRANE_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_GLOBAL_MEMBRANE_VERSION_PATCH;
}

static int hhs219_global_membrane_flag(uint8_t value) {
    return value == 0U || value == 1U;
}

static int hhs219_global_membrane_nonzero_root(
    const uint8_t root[HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES]
) {
    size_t i;
    uint8_t aggregate = 0U;

    for (i = 0U; i < HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES; ++i)
        aggregate = (uint8_t)(aggregate | root[i]);
    return aggregate != 0U;
}

static int hhs219_global_membrane_source_exact(const uint8_t *source_sha256) {
    return memcmp(source_sha256,
                  HHS219_GLOBAL_MEMBRANE_SOURCE_SHA256,
                  HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES) == 0;
}

uint32_t hhs_exact_pass219_global_membrane_version(void) {
    return hhs219_global_membrane_version_word();
}

HHSExactStatus hhs_exact_pass219_global_membrane_descriptor(
    HHSExactPass219GlobalMembraneDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs219_global_membrane_version_word();
    memcpy(out_descriptor->combined_source_sha256,
           HHS219_GLOBAL_MEMBRANE_SOURCE_SHA256,
           HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES);
    out_descriptor->boolean_gate_count =
        HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT;
    out_descriptor->equality_token_count =
        HHS_EXACT_PASS219_GLOBAL_MEMBRANE_EQUALITY_TOKEN_COUNT;
    out_descriptor->literal_equals_count =
        HHS_EXACT_PASS219_GLOBAL_MEMBRANE_LITERAL_EQUALS_COUNT;
    out_descriptor->ordinary_boolean_equality = 1U;
    out_descriptor->all_nested_boolean_gates_must_be_true = 1U;
    out_descriptor->whole_equation_propagates_on_true = 1U;
    out_descriptor->shared_global_symbol_environment_required = 1U;
    out_descriptor->cross_layer_variable_effect_required = 1U;
    out_descriptor->final_cross_layer_revalidation_required = 1U;
    out_descriptor->local_symbol_shadowing_authorized = 0U;
    out_descriptor->pass169_whole_expression_authority_required = 1U;
    out_descriptor->canonical_monolithic_proof = 0U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->vm81_mutation_authority = 0U;
    out_descriptor->hash72_commit_authority = 0U;
    out_descriptor->persistence_mutation_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_global_membrane_evaluate(
    const HHSExactPass219GlobalMembraneInputV1 *input,
    HHSExactPass219GlobalMembraneResultV1 *out_result
) {
    uint32_t i;
    uint32_t reasons = HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_PASS169_REQUIRED;
    uint32_t first_false = HHS_EXACT_PASS219_GLOBAL_MEMBRANE_NO_FALSE_GATE;
    uint8_t all_true = 1U;

    if (input == NULL || out_result == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (input->struct_size < sizeof(*input) ||
        input->version != hhs219_global_membrane_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (input->gate_count != HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hhs219_global_membrane_flag(input->global_symbol_environment_complete) ||
        !hhs219_global_membrane_flag(input->cross_layer_revalidation_complete) ||
        !hhs219_global_membrane_flag(input->local_symbol_shadowing_detected))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hhs219_global_membrane_source_exact(input->combined_source_sha256))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hhs219_global_membrane_nonzero_root(input->global_symbol_environment_root))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT; ++i) {
        const HHSExactPass219GlobalGateWitnessV1 *gate = &input->gates[i];

        if (gate->struct_size < sizeof(*gate) ||
            gate->version != hhs219_global_membrane_version_word())
            return HHS_EXACT_STATUS_VERSION_MISMATCH;
        if (gate->gate_index != i ||
            gate->source_offset != HHS219_GLOBAL_MEMBRANE_GATE_OFFSETS[i])
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (!hhs219_global_membrane_flag(gate->boolean_result))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (!hhs219_global_membrane_source_exact(gate->combined_source_sha256))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (memcmp(gate->global_symbol_environment_root,
                   input->global_symbol_environment_root,
                   HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES) != 0)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        if (gate->boolean_result == 0U) {
            all_true = 0U;
            reasons |= HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_BOOLEAN_GATE_FALSE;
            if (first_false == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_NO_FALSE_GATE)
                first_false = i;
        }
    }

    if (input->global_symbol_environment_complete == 0U)
        reasons |= HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_GLOBAL_ENVIRONMENT_INCOMPLETE;
    if (input->cross_layer_revalidation_complete == 0U)
        reasons |= HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_CROSS_LAYER_REVALIDATION_INCOMPLETE;
    if (input->local_symbol_shadowing_detected != 0U)
        reasons |= HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_LOCAL_SHADOWING_DETECTED;

    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (uint32_t)sizeof(*out_result);
    out_result->version = hhs219_global_membrane_version_word();
    out_result->reason_mask = reasons;
    out_result->first_false_gate = first_false;
    out_result->source_identity_exact = 1U;
    out_result->occurrence_provenance_exact = 1U;
    out_result->shared_global_symbol_environment_exact = 1U;
    out_result->all_nested_boolean_gates_true = all_true;
    out_result->cross_layer_revalidation_complete = input->cross_layer_revalidation_complete;
    out_result->local_symbol_shadowing_authorized = 0U;
    out_result->pass169_whole_expression_authority_required = 1U;
    out_result->canonical_monolithic_proof = 0U;
    out_result->floating_point_authority = 0U;
    out_result->vm81_mutation_authority = 0U;
    out_result->hash72_commit_authority = 0U;
    out_result->persistence_mutation_authority = 0U;

    if (all_true != 0U &&
        input->global_symbol_environment_complete != 0U &&
        input->cross_layer_revalidation_complete != 0U &&
        input->local_symbol_shadowing_detected == 0U) {
        out_result->decision = HHS_EXACT_PASS219_GLOBAL_MEMBRANE_PROPAGATE;
        out_result->whole_equation_propagated = 1U;
    } else {
        out_result->decision = HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REJECT;
        out_result->whole_equation_propagated = 0U;
    }

    return HHS_EXACT_STATUS_OK;
}