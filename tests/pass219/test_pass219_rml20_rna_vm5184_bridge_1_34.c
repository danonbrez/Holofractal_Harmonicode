#include "hhs_pass219_rml20_rna_vm5184_bridge_1_34.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void init_input(HHSExactUQCELInputV1 *input, uint8_t *one) {
    memset(input, 0, sizeof(*input));
    input->struct_size = (uint32_t)sizeof(*input);
    input->uqcel_version = hhs_exact_uqcel_version();
    input->profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input->delta.struct_size = (uint32_t)sizeof(input->delta);
    input->delta.byte_length = 1U;
    input->delta.bytes_be = one;
}

static void assert_receipt(
    const HHSExactPass219RML20RNAVM5184ReceiptV1 *receipt,
    uint32_t source,
    uint8_t direction
) {
    uint32_t target = 0U;
    uint32_t reverse = 0U;
    int8_t flux = 0;
    int8_t reverse_flux = 0;

    assert(receipt->struct_size == sizeof(*receipt));
    assert(receipt->version == HHS_EXACT_PASS219_RML20_RNA_VM5184_VERSION);
    assert(receipt->source_address == source);
    assert(receipt->direction == direction);
    assert(hhs_exact_pass219_rml20_transport_neighbor(source, direction, &target) ==
           HHS_EXACT_STATUS_OK);
    assert(receipt->target_address == target);
    assert(hhs_exact_pass219_rml20_transport_neighbor(
               target, receipt->inverse_direction, &reverse) ==
           HHS_EXACT_STATUS_OK);
    assert(reverse == source);
    assert(hhs_exact_pass219_rml20_transport_flux(direction, &flux) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rml20_transport_flux(
               receipt->inverse_direction, &reverse_flux) ==
           HHS_EXACT_STATUS_OK);
    assert(receipt->forward_flux == flux);
    assert(receipt->reverse_flux == reverse_flux);
    assert(receipt->forward_flux == -receipt->reverse_flux);
    assert(receipt->discrete_divergence == 0);
    assert(receipt->source_lane == receipt->target_lane);
    assert(receipt->encode_decode_bijective == 1U);
    assert(receipt->reciprocal_neighbor_restores_source == 1U);
    assert(receipt->reciprocal_flux_balanced == 1U);
    assert(receipt->lane_identity_retained == 1U);
    assert(receipt->zero_discrete_divergence == 1U);
    assert(receipt->zero_diffusion_classification == 1U);
    assert(receipt->feedback_lane_bound == 1U);
    assert(receipt->feedback_trinary_bound == 1U);
    assert(receipt->rna_cell_wall_routed == 1U);
    assert(receipt->selected_lane < HHS_EXACT_PASS219_HOLO4_LANE_COUNT);
    assert(receipt->candidate_only == 1U);
    assert(receipt->exact_integer_only == 1U);
    assert(receipt->canonical_mutation_authority == 0U);
    assert(receipt->canonical_hash72_authority == 0U);
    assert(receipt->canonical_hash216_authority == 0U);
    assert(receipt->canonical_persistence_authority == 0U);
    assert(receipt->floating_point_authority == 0U);
    assert(receipt->transition_identity216[0] != '\0');
}

int main(void) {
    HHSExactPass219RML20RNAVM5184DescriptorV1 descriptor;
    HHSExactPass219Hash216TransitionViewV1 transition;
    HHSExactUQCELInputV1 input;
    HHSExactPass219RML20RNAVM5184ReceiptV1 receipt;
    uint8_t raw[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t one = 1U;
    const uint32_t samples[] = {
        0U,
        80U,
        81U,
        5183U,
        373247U,
        746496U,
        1119744U,
        HHS_EXACT_PASS219_RML20_ADDRESS_COUNT - 1U,
    };
    size_t i;
    uint8_t direction;

    assert(hhs_exact_pass219_rml20_rna_vm5184_version() ==
           HHS_EXACT_PASS219_RML20_RNA_VM5184_VERSION);
    memset(&descriptor, 0, sizeof(descriptor));
    assert(hhs_exact_pass219_rml20_rna_vm5184_descriptor(&descriptor) ==
           HHS_EXACT_STATUS_OK);
    assert(descriptor.struct_size == sizeof(descriptor));
    assert(descriptor.lane_count == 4U);
    assert(descriptor.operations_per_cell == 64U);
    assert(descriptor.phase_count == 72U);
    assert(descriptor.cell_count == 81U);
    assert(descriptor.address_count == 1492992U);
    assert(descriptor.direction_count == 6U);
    assert(descriptor.vm5184_bytes == 648U);
    assert(descriptor.cpp_rna_cell_wall == 1U);
    assert(descriptor.frozen_rml17_parity_surface == 1U);
    assert(descriptor.lane_retaining_transport == 1U);
    assert(descriptor.reciprocal_flux_transport == 1U);
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
    init_input(&input, &one);

    for (i = 0U; i < sizeof(raw); ++i)
        raw[i] = (uint8_t)((i * 131U + 17U) & 0xFFU);

    for (i = 0U; i < sizeof(samples) / sizeof(samples[0]); ++i) {
        for (direction = 0U;
             direction < HHS_EXACT_PASS219_RML20_DIRECTION_COUNT;
             ++direction) {
            memset(&receipt, 0, sizeof(receipt));
            assert(hhs_exact_pass219_rml20_rna_vm5184_route(
                       &input,
                       raw,
                       sizeof(raw),
                       &transition,
                       samples[i],
                       direction,
                       &receipt) == HHS_EXACT_STATUS_OK);
            assert_receipt(&receipt, samples[i], direction);
        }
    }

    memset(&receipt, 0xA5, sizeof(receipt));
    assert(hhs_exact_pass219_rml20_rna_vm5184_route(
               &input,
               raw,
               sizeof(raw) - 1U,
               &transition,
               0U,
               HHS_EXACT_PASS219_RML20_OPERATION_FORWARD,
               &receipt) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(receipt.struct_size == 0U);

    memset(&receipt, 0xA5, sizeof(receipt));
    assert(hhs_exact_pass219_rml20_rna_vm5184_route(
               &input,
               raw,
               sizeof(raw),
               &transition,
               HHS_EXACT_PASS219_RML20_ADDRESS_COUNT,
               HHS_EXACT_PASS219_RML20_OPERATION_FORWARD,
               &receipt) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(receipt.struct_size == 0U);

    memset(&receipt, 0xA5, sizeof(receipt));
    assert(hhs_exact_pass219_rml20_rna_vm5184_route(
               &input,
               raw,
               sizeof(raw),
               &transition,
               0U,
               HHS_EXACT_PASS219_RML20_DIRECTION_COUNT,
               &receipt) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(receipt.struct_size == 0U);

    printf(
        "PASS219_RML20_RNA_VM5184_BRIDGE_PASS samples=%zu directions=%u address_count=%u\n",
        sizeof(samples) / sizeof(samples[0]),
        (unsigned)HHS_EXACT_PASS219_RML20_DIRECTION_COUNT,
        (unsigned)HHS_EXACT_PASS219_RML20_ADDRESS_COUNT);
    return 0;
}
