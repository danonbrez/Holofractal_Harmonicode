#include "../../hhs_runtime/include/hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void fill_pattern(uint8_t *buffer, size_t length, uint8_t seed) {
    size_t i;
    for (i = 0U; i < length; ++i)
        buffer[i] = (uint8_t)(seed + (uint8_t)(i * 37U));
}

int main(void) {
    HHSExactPass219Lane5RawX86VM5184DescriptorV1 descriptor;
    HHSExactPass219CoreCircuitStateV1 state;
    HHSExactPass219CoreCircuitFeaturesV1 features;
    HHSExactPass219CoreCircuitDecisionV1 decision;
    HHSExactPass219Lane5RawX86VM5184ReceiptV1 receipt;
    uint8_t input[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t output[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t stream_input[HHS_EXACT_VM81_FRAME_BYTES * 2U];
    uint8_t stream_output[HHS_EXACT_VM81_FRAME_BYTES * 2U];
    size_t written = 0U;
    uint32_t address;
    uint8_t cell;
    uint8_t left;
    uint8_t right;

    memset(&descriptor, 0, sizeof(descriptor));
    assert(hhs_exact_pass219_lane5_raw_x86_vm5184_descriptor(&descriptor) ==
           HHS_EXACT_STATUS_OK);
    assert(descriptor.frame_bytes == 648U);
    assert(descriptor.frame_bits == 5184U);
    assert(descriptor.vm81_cells == 81U);
    assert(descriptor.local_states_per_cell == 64U);
    assert(descriptor.vm5184_addresses == 5184U);
    assert(descriptor.direct_raw_x86_ingress == 1U);
    assert(descriptor.direct_vm81_kernel_execution == 1U);
    assert(descriptor.exact_raw_egress == 1U);
    assert(descriptor.format_translation_layer == 0U);
    assert(descriptor.floating_point_authority == 0U);
    assert(descriptor.host_instruction_execution_authority == 0U);

    assert(hhs_exact_pass219_core_circuit_state_init(&state) ==
           HHS_EXACT_STATUS_OK);

    fill_pattern(input, sizeof(input), 0x31U);
    memset(output, 0, sizeof(output));
    memset(&features, 0, sizeof(features));
    memset(&decision, 0, sizeof(decision));
    memset(&receipt, 0, sizeof(receipt));

    assert(hhs_exact_pass219_lane5_raw_x86_vm5184_step(
               input, sizeof(input), 0, &state,
               output, sizeof(output), &written,
               &features, &decision, &receipt) ==
           HHS_EXACT_STATUS_OK);
    assert(written == sizeof(input));
    assert(memcmp(input, output, sizeof(input)) == 0);
    assert(receipt.input_bytes == 648U);
    assert(receipt.output_bytes == 648U);
    assert(receipt.vm5184_addresses == 5184U);
    assert(receipt.frames_processed == 1U);
    assert(receipt.exact_byte_identity == 1U);
    assert(receipt.direct_raw_x86_ingress == 1U);
    assert(receipt.direct_vm81_kernel_execution == 1U);
    assert(receipt.format_translation_layer == 0U);
    assert(receipt.host_instruction_execution_authority == 0U);
    assert(receipt.state_step_count == 1U);

    /* The raw 5,184 bits are the 81x64 virtual hardware address plane. */
    for (address = 0U; address < 5184U; ++address) {
        assert(hhs_exact_vm5184_address_decode(
                   (uint16_t)address, &cell, &left, &right) ==
               HHS_EXACT_STATUS_OK);
        assert(cell < 81U);
        assert(left < 8U);
        assert(right < 8U);
        {
            uint16_t encoded = UINT16_MAX;
            assert(hhs_exact_vm5184_address_encode(
                       cell, left, right, &encoded) ==
                   HHS_EXACT_STATUS_OK);
            assert(encoded == address);
        }
    }

    fill_pattern(stream_input, HHS_EXACT_VM81_FRAME_BYTES, 0x17U);
    fill_pattern(stream_input + HHS_EXACT_VM81_FRAME_BYTES,
                 HHS_EXACT_VM81_FRAME_BYTES, 0xA3U);
    memset(stream_output, 0, sizeof(stream_output));
    written = 0U;
    memset(&receipt, 0, sizeof(receipt));

    assert(hhs_exact_pass219_lane5_raw_x86_vm5184_stream(
               stream_input, sizeof(stream_input), 0, &state,
               stream_output, sizeof(stream_output), &written, &receipt) ==
           HHS_EXACT_STATUS_OK);
    assert(written == sizeof(stream_input));
    assert(memcmp(stream_input, stream_output, sizeof(stream_input)) == 0);
    assert(receipt.frames_processed == 2U);
    assert(receipt.exact_byte_identity == 1U);
    assert(receipt.state_step_count == 3U);

    /* No hidden tail padding or format translation. */
    assert(hhs_exact_pass219_lane5_raw_x86_vm5184_stream(
               stream_input, sizeof(stream_input) - 1U, 0, &state,
               stream_output, sizeof(stream_output), &written, &receipt) ==
           HHS_EXACT_STATUS_RANGE_ERROR);

    puts("PASS lane5 raw x86_64 VM5184 kernel");
    return 0;
}
