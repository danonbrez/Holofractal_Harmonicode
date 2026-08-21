#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static const uint32_t EXPECTED_GATE_OFFSETS[
    HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT
] = {96U, 240U, 266U, 274U, 285U};

static void fill_valid_input(
    HHSExactPass219GlobalMembraneInputV1 *input,
    const HHSExactPass219GlobalMembraneDescriptorV1 *descriptor
) {
    uint32_t i;

    memset(input, 0, sizeof(*input));
    input->struct_size = (uint32_t)sizeof(*input);
    input->version = hhs_exact_pass219_global_membrane_version();
    memcpy(input->combined_source_sha256,
           descriptor->combined_source_sha256,
           HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES);
    for (i = 0U; i < HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES; ++i)
        input->global_symbol_environment_root[i] = (uint8_t)(i + 1U);
    input->gate_count = HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT;
    input->global_symbol_environment_complete = 1U;
    input->cross_layer_revalidation_complete = 1U;
    input->local_symbol_shadowing_detected = 0U;

    for (i = 0U; i < HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT; ++i) {
        HHSExactPass219GlobalGateWitnessV1 *gate = &input->gates[i];
        gate->struct_size = (uint32_t)sizeof(*gate);
        gate->version = hhs_exact_pass219_global_membrane_version();
        gate->gate_index = i;
        gate->source_offset = EXPECTED_GATE_OFFSETS[i];
        gate->boolean_result = 1U;
        memcpy(gate->combined_source_sha256,
               descriptor->combined_source_sha256,
               HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES);
        memcpy(gate->global_symbol_environment_root,
               input->global_symbol_environment_root,
               HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES);
    }
}

int main(void) {
    HHSExactPass219GlobalMembraneDescriptorV1 descriptor;
    HHSExactPass219GlobalMembraneInputV1 input;
    HHSExactPass219GlobalMembraneInputV1 mutated;
    HHSExactPass219GlobalMembraneResultV1 result;
    HHSExactPass219GlobalMembraneResultV1 replay;
    uint32_t i;

    assert(hhs_exact_pass219_global_membrane_descriptor(&descriptor) ==
           HHS_EXACT_STATUS_OK);
    assert(descriptor.struct_size == sizeof(descriptor));
    assert(descriptor.version == hhs_exact_pass219_global_membrane_version());
    assert(descriptor.boolean_gate_count == 5U);
    assert(descriptor.equality_token_count == 11U);
    assert(descriptor.literal_equals_count == 16U);
    assert(descriptor.ordinary_boolean_equality == 1U);
    assert(descriptor.all_nested_boolean_gates_must_be_true == 1U);
    assert(descriptor.whole_equation_propagates_on_true == 1U);
    assert(descriptor.shared_global_symbol_environment_required == 1U);
    assert(descriptor.cross_layer_variable_effect_required == 1U);
    assert(descriptor.final_cross_layer_revalidation_required == 1U);
    assert(descriptor.local_symbol_shadowing_authorized == 0U);
    assert(descriptor.pass169_whole_expression_authority_required == 1U);
    assert(descriptor.canonical_monolithic_proof == 0U);
    assert(descriptor.floating_point_authority == 0U);
    assert(descriptor.vm81_mutation_authority == 0U);
    assert(descriptor.hash72_commit_authority == 0U);
    assert(descriptor.persistence_mutation_authority == 0U);

    fill_valid_input(&input, &descriptor);
    assert(hhs_exact_pass219_global_membrane_evaluate(&input, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.decision == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_PROPAGATE);
    assert(result.first_false_gate == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_NO_FALSE_GATE);
    assert(result.source_identity_exact == 1U);
    assert(result.occurrence_provenance_exact == 1U);
    assert(result.shared_global_symbol_environment_exact == 1U);
    assert(result.all_nested_boolean_gates_true == 1U);
    assert(result.cross_layer_revalidation_complete == 1U);
    assert(result.whole_equation_propagated == 1U);
    assert(result.local_symbol_shadowing_authorized == 0U);
    assert(result.pass169_whole_expression_authority_required == 1U);
    assert(result.canonical_monolithic_proof == 0U);
    assert(result.vm81_mutation_authority == 0U);
    assert(result.hash72_commit_authority == 0U);
    assert(result.persistence_mutation_authority == 0U);

    /* Deterministic replay of the same complete witness bundle. */
    assert(hhs_exact_pass219_global_membrane_evaluate(&input, &replay) ==
           HHS_EXACT_STATUS_OK);
    assert(memcmp(&result, &replay, sizeof(result)) == 0);

    /* Every Boolean gate is mandatory: any single false gate rejects the whole equation. */
    for (i = 0U; i < HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT; ++i) {
        mutated = input;
        mutated.gates[i].boolean_result = 0U;
        assert(hhs_exact_pass219_global_membrane_evaluate(&mutated, &result) ==
               HHS_EXACT_STATUS_OK);
        assert(result.decision == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REJECT);
        assert((result.reason_mask &
                HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_BOOLEAN_GATE_FALSE) != 0U);
        assert(result.first_false_gate == i);
        assert(result.all_nested_boolean_gates_true == 0U);
        assert(result.whole_equation_propagated == 0U);
    }

    /* The shared environment must be complete under the final cross-layer state. */
    mutated = input;
    mutated.global_symbol_environment_complete = 0U;
    assert(hhs_exact_pass219_global_membrane_evaluate(&mutated, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.decision == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REJECT);
    assert((result.reason_mask &
            HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_GLOBAL_ENVIRONMENT_INCOMPLETE) != 0U);
    assert(result.whole_equation_propagated == 0U);

    mutated = input;
    mutated.cross_layer_revalidation_complete = 0U;
    assert(hhs_exact_pass219_global_membrane_evaluate(&mutated, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.decision == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REJECT);
    assert((result.reason_mask &
            HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_CROSS_LAYER_REVALIDATION_INCOMPLETE) != 0U);
    assert(result.whole_equation_propagated == 0U);

    /* A canonical equation symbol cannot be locally shadowed in a nested layer. */
    mutated = input;
    mutated.local_symbol_shadowing_detected = 1U;
    assert(hhs_exact_pass219_global_membrane_evaluate(&mutated, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.decision == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REJECT);
    assert((result.reason_mask &
            HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REASON_LOCAL_SHADOWING_DETECTED) != 0U);
    assert(result.local_symbol_shadowing_authorized == 0U);
    assert(result.whole_equation_propagated == 0U);

    /* Source identity and gate occurrence provenance are structural, not advisory. */
    mutated = input;
    mutated.combined_source_sha256[0] ^= 1U;
    assert(hhs_exact_pass219_global_membrane_evaluate(&mutated, &result) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    mutated = input;
    mutated.gates[2].combined_source_sha256[0] ^= 1U;
    assert(hhs_exact_pass219_global_membrane_evaluate(&mutated, &result) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    mutated = input;
    mutated.gates[3].source_offset += 1U;
    assert(hhs_exact_pass219_global_membrane_evaluate(&mutated, &result) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    mutated = input;
    mutated.gates[1].global_symbol_environment_root[0] ^= 1U;
    assert(hhs_exact_pass219_global_membrane_evaluate(&mutated, &result) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    mutated = input;
    mutated.gate_count -= 1U;
    assert(hhs_exact_pass219_global_membrane_evaluate(&mutated, &result) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    mutated = input;
    memset(mutated.global_symbol_environment_root, 0,
           sizeof(mutated.global_symbol_environment_root));
    for (i = 0U; i < HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT; ++i)
        memset(mutated.gates[i].global_symbol_environment_root, 0,
               sizeof(mutated.gates[i].global_symbol_environment_root));
    assert(hhs_exact_pass219_global_membrane_evaluate(&mutated, &result) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    puts("PASS219 I121.9 Harmonicode global constraint membrane: PASS");
    return 0;
}