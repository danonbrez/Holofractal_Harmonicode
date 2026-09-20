#include "../include/hhs_pass219_lane5_raw_x86_vm5184_kernel_1_57.h"

#include <string.h>

uint32_t hhs_exact_pass219_lane5_raw_x86_vm5184_version(void) {
    return HHS_EXACT_PASS219_LANE5_RAW_X86_VM5184_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_raw_x86_vm5184_descriptor(
    HHSExactPass219Lane5RawX86VM5184DescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_LANE5_RAW_X86_VM5184_VERSION;
    out_descriptor->frame_bytes = HHS_EXACT_VM81_FRAME_BYTES;
    out_descriptor->frame_bits = HHS_EXACT_VM81_FRAME_BITS;
    out_descriptor->vm81_cells = HHS_EXACT_VM81_CELLS;
    out_descriptor->local_states_per_cell = HHS_EXACT_PHASE_PAIR_COUNT;
    out_descriptor->vm5184_addresses = HHS_EXACT_VM81_FRAME_BITS;
    out_descriptor->direct_raw_x86_ingress = 1U;
    out_descriptor->direct_vm81_kernel_execution = 0U;
    out_descriptor->exact_raw_egress = 1U;
    out_descriptor->format_translation_layer = 0U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->host_instruction_execution_authority = 0U;
    out_descriptor->canonical_vm81_mutation_authority = 0U;
    out_descriptor->canonical_hash72_authority = 0U;
    out_descriptor->canonical_hash216_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

static void hhs_lane5_raw_x86_vm5184_receipt_init(
    HHSExactPass219Lane5RawX86VM5184ReceiptV1 *receipt,
    uint32_t input_bytes,
    uint32_t output_bytes,
    uint32_t frames_processed,
    uint64_t step_count,
    uint64_t hydration_signature64,
    uint8_t byte_identity
) {
    if (receipt == NULL)
        return;
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = (uint32_t)sizeof(*receipt);
    receipt->version = HHS_EXACT_PASS219_LANE5_RAW_X86_VM5184_VERSION;
    receipt->input_bytes = input_bytes;
    receipt->output_bytes = output_bytes;
    receipt->vm5184_addresses = HHS_EXACT_VM81_FRAME_BITS;
    receipt->frames_processed = frames_processed;
    receipt->state_step_count = step_count;
    receipt->hydration_signature64 = hydration_signature64;
    receipt->exact_byte_identity = byte_identity;
    receipt->direct_raw_x86_ingress = 1U;
    receipt->direct_vm81_kernel_execution = 0U;
    receipt->format_translation_layer = 0U;
    receipt->floating_point_authority = 0U;
    receipt->host_instruction_execution_authority = 0U;
    receipt->canonical_vm81_mutation_authority = 0U;
}

HHSExactStatus hhs_exact_pass219_lane5_raw_x86_vm5184_step(
    const uint8_t *input,
    size_t length,
    int8_t feedback_trinary,
    HHSExactPass219CoreCircuitStateV1 *state,
    uint8_t *output,
    size_t capacity,
    size_t *out_length,
    HHSExactPass219CoreCircuitFeaturesV1 *out_features,
    HHSExactPass219CoreCircuitDecisionV1 *out_decision,
    HHSExactPass219Lane5RawX86VM5184ReceiptV1 *out_receipt
) {
    uint8_t ingress[HHS_EXACT_VM81_FRAME_BYTES];
    HHSExactVM81Frame frame;
    HHSExactStatus status;
    size_t ingress_length = 0U;
    size_t egress_length = 0U;

    if (out_length != NULL)
        *out_length = HHS_EXACT_VM81_FRAME_BYTES;

    if (input == NULL || state == NULL || output == NULL ||
        out_features == NULL || out_decision == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (length != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (capacity < HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    /*
     * Lane 5 smart optimization is resident BIOS/control-plane state.
     * Validate it as a kernel precondition without inserting a payload stage.
     */
    status = hhs_exact_pass219_lane5_virtual_bios_validate();
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_x86_64_bytecode_copy_exact(
        input, length, ingress, sizeof(ingress), &ingress_length);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (ingress_length != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_vm81_frame_import_le(
        ingress, ingress_length, &frame);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    /*
     * Pass 219 Lane 5 1.59 supersession: this legacy surface is exact raw
     * transport only. Canonical/runtime computation is available only through
     * hhs_exact_pass219_lane5_gateway_admit_raw5184.
     */
    (void)feedback_trinary;
    memset(out_features, 0, sizeof(*out_features));
    memset(out_decision, 0, sizeof(*out_decision));

    status = hhs_exact_vm81_frame_export_le(
        &frame, output, capacity, &egress_length);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (egress_length != length || memcmp(input, output, length) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (out_length != NULL)
        *out_length = egress_length;

    hhs_lane5_raw_x86_vm5184_receipt_init(
        out_receipt,
        (uint32_t)length,
        (uint32_t)egress_length,
        1U,
        state->step_count,
        UINT64_C(0),
        1U
    );
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_raw_x86_vm5184_stream(
    const uint8_t *input,
    size_t length,
    int8_t feedback_trinary,
    HHSExactPass219CoreCircuitStateV1 *state,
    uint8_t *output,
    size_t capacity,
    size_t *out_length,
    HHSExactPass219Lane5RawX86VM5184ReceiptV1 *out_receipt
) {
    size_t offset;
    uint32_t frames = 0U;
    HHSExactStatus status;
    HHSExactPass219CoreCircuitFeaturesV1 features;
    HHSExactPass219CoreCircuitDecisionV1 decision;
    HHSExactPass219Lane5RawX86VM5184ReceiptV1 frame_receipt;

    if (out_length != NULL)
        *out_length = length;
    if ((length != 0U && input == NULL) || state == NULL ||
        (length != 0U && output == NULL))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < length)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    if (length == 0U || (length % HHS_EXACT_VM81_FRAME_BYTES) != 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    for (offset = 0U; offset < length; offset += HHS_EXACT_VM81_FRAME_BYTES) {
        size_t written = 0U;
        memset(&features, 0, sizeof(features));
        memset(&decision, 0, sizeof(decision));
        memset(&frame_receipt, 0, sizeof(frame_receipt));
        status = hhs_exact_pass219_lane5_raw_x86_vm5184_step(
            input + offset,
            HHS_EXACT_VM81_FRAME_BYTES,
            feedback_trinary,
            state,
            output + offset,
            capacity - offset,
            &written,
            &features,
            &decision,
            &frame_receipt
        );
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        if (written != HHS_EXACT_VM81_FRAME_BYTES)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        frames += 1U;
    }

    if (memcmp(input, output, length) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    hhs_lane5_raw_x86_vm5184_receipt_init(
        out_receipt,
        (uint32_t)length,
        (uint32_t)length,
        frames,
        state->step_count,
        features.hydration_signature64,
        1U
    );
    return HHS_EXACT_STATUS_OK;
}
