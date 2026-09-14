#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

int main(void) {
    static const uint8_t expected_sha256[32] = {
        0xeeU, 0x76U, 0xa9U, 0x02U, 0x27U, 0x2fU, 0xd4U, 0x1bU,
        0x44U, 0x25U, 0x84U, 0x68U, 0x33U, 0x5fU, 0xf4U, 0x0eU,
        0x60U, 0xc5U, 0x88U, 0x05U, 0xfaU, 0x06U, 0xecU, 0x5eU,
        0x85U, 0x78U, 0x88U, 0x47U, 0xd6U, 0x00U, 0x73U, 0xd0U
    };
    uint8_t raw[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t source[HHS_EXACT_PASS219_CORE_CIRCUIT_SOURCE_BYTES];
    HHSExactVM81Frame frame;
    HHSExactPass219CoreCircuitDescriptorV1 descriptor;
    HHSExactPass219CoreCircuitStateV1 state;
    HHSExactPass219CoreCircuitFeaturesV1 features;
    HHSExactPass219CoreCircuitDecisionV1 decision;
    size_t source_length = 0U;
    uint32_t i;
    int8_t corrective_feedback;

    assert(hhs_exact_pass219_core_circuit_descriptor(&descriptor) ==
           HHS_EXACT_STATUS_OK);
    assert(descriptor.source_bytes == 542U);
    assert(descriptor.a2 == 1U);
    assert(descriptor.b2 == 2U);
    assert(descriptor.c2 == 3U);
    assert(descriptor.b4 == 4U);
    assert(descriptor.b6 == 8U);
    assert(descriptor.c4 == 9U);
    assert(descriptor.b6c4 == 72U);
    assert(descriptor.phase_modulus == 72U);
    assert(descriptor.update_quantum == 5U);
    assert(descriptor.verbatim_source_preserved == 1U);
    assert(descriptor.single_fused_circuit == 1U);
    assert(descriptor.exact_integer_only == 1U);
    assert(descriptor.online_learning_enabled == 1U);
    assert(descriptor.vm81_hydration_bridge == 1U);
    assert(descriptor.canonical_mutation_authority == 0U);
    assert(descriptor.canonical_hash72_authority == 0U);
    assert(descriptor.canonical_hash216_authority == 0U);
    assert(descriptor.canonical_persistence_authority == 0U);
    assert(descriptor.floating_point_authority == 0U);
    assert(memcmp(descriptor.source_sha256, expected_sha256,
                  sizeof(expected_sha256)) == 0);

    assert(hhs_exact_pass219_core_circuit_source(
               source, sizeof(source), &source_length) ==
           HHS_EXACT_STATUS_OK);
    assert(source_length == sizeof(source));
    assert(source[0] == (uint8_t)'P');
    assert(source[1] == (uint8_t)'^');
    assert(source[2] == (uint8_t)'2');

    for (i = 0U; i < HHS_EXACT_VM81_FRAME_BYTES; ++i)
        raw[i] = (uint8_t)((i * 37U + 11U) & 0xFFU);
    assert(hhs_exact_vm81_frame_import_le(raw, sizeof(raw), &frame) ==
           HHS_EXACT_STATUS_OK);

    assert(hhs_exact_pass219_core_circuit_state_init(&state) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_core_circuit_validate_state(&state) ==
           HHS_EXACT_STATUS_OK);

    assert(hhs_exact_pass219_global_raw5184_dynamic_circuit(
               &frame, 0, &state, &features, &decision) ==
           HHS_EXACT_STATUS_OK);
    assert(features.word_visits == 81U);
    assert(features.total_popcount > 0U);
    assert(features.nonzero_words == 81U);
    assert(decision.candidate_only == 1U);
    assert(decision.exact_integer_only == 1U);
    assert(decision.floating_point_authority == 0U);
    assert(decision.canonical_mutation_authority == 0U);
    assert(decision.canonical_hash72_authority == 0U);
    assert(decision.canonical_hash216_authority == 0U);
    assert(decision.canonical_persistence_authority == 0U);
    assert(state.update_count == 0U);
    assert(state.step_count == 1U);

    corrective_feedback =
        decision.prediction_trinary > 0 ? (int8_t)-1 : (int8_t)1;
    assert(hhs_exact_pass219_global_raw5184_dynamic_circuit(
               &frame, corrective_feedback, &state, &features, &decision) ==
           HHS_EXACT_STATUS_OK);
    assert(state.update_count == 1U);
    assert(state.step_count == 2U);
    assert(decision.updated == 1U);
    assert(decision.feedback_trinary == corrective_feedback);
    assert(hhs_exact_pass219_core_circuit_validate_state(&state) ==
           HHS_EXACT_STATUS_OK);

    return 0;
}
