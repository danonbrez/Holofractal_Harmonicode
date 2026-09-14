#include "hhs_pass219_rna_vm5184_abi_1_33.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static int all_zero(const void *value, size_t size) {
    const uint8_t *bytes = (const uint8_t *)value;
    size_t i;
    for (i = 0U; i < size; ++i) {
        if (bytes[i] != 0U)
            return 0;
    }
    return 1;
}

int main(void) {
    HHSExactPass219RNAVM5184ABIDescriptorV1 descriptor;
    HHSExactPass219Hash216TransitionViewV1 transition;
    HHSExactPass219Hash216TransitionViewV1 bad_transition;
    HHSExactUQCELInputV1 input;
    HHSExactVM81Frame frame;
    HHSExactPass219Holo4PreparedV1 prepared_frame;
    HHSExactPass219Holo4PreparedV1 prepared_raw;
    HHSExactPass219Holo4PreparedV1 prepared_negative;
    HHSExactPass219Holo4DecisionV1 decision_frame;
    HHSExactPass219Holo4DecisionV1 decision_raw;
    HHSExactPass219Holo4DecisionV1 decision_negative;
    uint8_t raw[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t one = 1U;
    size_t written = 0U;
    size_t i;

    assert(hhs_exact_pass219_rna_vm5184_abi_version() ==
           HHS_EXACT_PASS219_RNA_VM5184_ABI_VERSION);
    memset(&descriptor, 0, sizeof(descriptor));
    assert(hhs_exact_pass219_rna_vm5184_abi_descriptor(&descriptor) ==
           HHS_EXACT_STATUS_OK);
    assert(descriptor.struct_size == sizeof(descriptor));
    assert(descriptor.vm81_cells == 81U);
    assert(descriptor.vm81_word_bits == 64U);
    assert(descriptor.vm5184_bits == 5184U);
    assert(descriptor.vm5184_bytes == 648U);
    assert(descriptor.lane_count == HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
    assert(descriptor.cpp_rna_cell_wall == 1U);
    assert(descriptor.exact_vm5184_carrier == 1U);
    assert(descriptor.raw5184_ingress == 1U);
    assert(descriptor.candidate_only == 1U);
    assert(descriptor.exact_integer_only == 1U);
    assert(descriptor.canonical_mutation_authority == 0U);
    assert(descriptor.canonical_hash72_authority == 0U);
    assert(descriptor.canonical_hash216_authority == 0U);
    assert(descriptor.canonical_persistence_authority == 0U);
    assert(descriptor.floating_point_authority == 0U);

    memset(&transition, 0, sizeof(transition));
    assert(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&transition) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&transition) ==
           HHS_EXACT_STATUS_OK);

    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.delta.struct_size = (uint32_t)sizeof(input.delta);
    input.delta.byte_length = 1U;
    input.delta.bytes_be = &one;

    memset(&frame, 0, sizeof(frame));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = UINT64_C(0x9E3779B97F4A7C15) ^
                         ((uint64_t)i * UINT64_C(0x100000001B3));

    assert(hhs_exact_vm81_frame_export_le(
               &frame, raw, sizeof(raw), &written) == HHS_EXACT_STATUS_OK);
    assert(written == HHS_EXACT_VM81_FRAME_BYTES);

    memset(&prepared_frame, 0, sizeof(prepared_frame));
    memset(&decision_frame, 0, sizeof(decision_frame));
    assert(hhs_exact_pass219_rna_vm5184_route(
               &input,
               &frame,
               &transition,
               HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
               0,
               &prepared_frame,
               &decision_frame) == HHS_EXACT_STATUS_OK);

    assert(prepared_frame.word_visits == HHS_EXACT_VM81_CELLS);
    assert(prepared_frame.graph_edge_visits ==
           HHS_EXACT_PASS219_HOLO4_DIRECTED_GRAPH_EDGES);
    assert(prepared_frame.hash216_positions_complete == 1U);
    assert(prepared_frame.candidate_only == 1U);
    assert(prepared_frame.exact_integer_only == 1U);
    assert(prepared_frame.canonical_mutation_authority == 0U);
    assert(prepared_frame.canonical_hash72_authority == 0U);
    assert(prepared_frame.canonical_hash216_authority == 0U);
    assert(prepared_frame.canonical_persistence_authority == 0U);
    assert(prepared_frame.floating_point_authority == 0U);
    assert(decision_frame.selected_lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
    assert(decision_frame.candidate_only == 1U);
    assert(decision_frame.exact_integer_only == 1U);
    assert(decision_frame.canonical_mutation_authority == 0U);
    assert(decision_frame.canonical_hash72_authority == 0U);
    assert(decision_frame.canonical_hash216_authority == 0U);
    assert(decision_frame.canonical_persistence_authority == 0U);
    assert(decision_frame.floating_point_authority == 0U);

    memset(&prepared_raw, 0, sizeof(prepared_raw));
    memset(&decision_raw, 0, sizeof(decision_raw));
    assert(hhs_exact_pass219_rna_raw5184_route(
               &input,
               raw,
               sizeof(raw),
               &transition,
               HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
               0,
               &prepared_raw,
               &decision_raw) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&prepared_frame, &prepared_raw, sizeof(prepared_frame)) == 0);
    assert(memcmp(&decision_frame, &decision_raw, sizeof(decision_frame)) == 0);

    memset(&prepared_negative, 0xA5, sizeof(prepared_negative));
    memset(&decision_negative, 0xA5, sizeof(decision_negative));
    assert(hhs_exact_pass219_rna_raw5184_route(
               &input,
               raw,
               sizeof(raw) - 1U,
               &transition,
               HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
               0,
               &prepared_negative,
               &decision_negative) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(all_zero(&prepared_negative, sizeof(prepared_negative)));
    assert(all_zero(&decision_negative, sizeof(decision_negative)));

    memcpy(&bad_transition, &transition, sizeof(bad_transition));
    bad_transition.transition_identity216[0] =
        bad_transition.transition_identity216[0] == '0' ? '1' : '0';
    memset(&prepared_negative, 0xA5, sizeof(prepared_negative));
    memset(&decision_negative, 0xA5, sizeof(decision_negative));
    assert(hhs_exact_pass219_rna_vm5184_route(
               &input,
               &frame,
               &bad_transition,
               HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
               0,
               &prepared_negative,
               &decision_negative) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(all_zero(&prepared_negative, sizeof(prepared_negative)));
    assert(all_zero(&decision_negative, sizeof(decision_negative)));

    printf("PASS219_RNA_VM5184_ABI_PASS selected_lane=%u graph=%llu tensor=%llu decision=%llu\n",
           (unsigned)decision_frame.selected_lane,
           (unsigned long long)prepared_frame.graph_signature64,
           (unsigned long long)prepared_frame.tensor_signature64,
           (unsigned long long)decision_frame.decision_signature64);
    return 0;
}
