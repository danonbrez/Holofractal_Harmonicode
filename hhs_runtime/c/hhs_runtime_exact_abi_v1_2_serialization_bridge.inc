/* Additive successor bridge: preserve frozen exact-v1.1 source identity while
 * retaining the global raw5184 serialization checks introduced after v1.1.
 * The frozen implementation is compiled under the established *_raw internal
 * names by hhs_runtime_exact_abi.c before this bridge publishes current names.
 */

static HHSExactStatus hhs_exact_vm81_frame_global_serialization_validate(
    const HHSExactVM81Frame *frame
);

HHSExactStatus hhs_exact_vm81_frame_import_le(
    const uint8_t *bytes,
    size_t length,
    HHSExactVM81Frame *out_frame
) {
    HHSExactStatus status = hhs_exact_vm81_frame_import_le_raw(
        bytes, length, out_frame);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_vm81_frame_global_serialization_validate(out_frame);
    if (status != HHS_EXACT_STATUS_OK) {
        memset(out_frame, 0, sizeof(*out_frame));
        return status;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_vm81_frame_export_le(
    const HHSExactVM81Frame *frame,
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    HHSExactStatus status;
    if (out_length != NULL)
        *out_length = HHS_EXACT_VM81_FRAME_BYTES;
    if (frame == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_vm81_frame_global_serialization_validate(frame);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_exact_vm81_frame_export_le_raw(
        frame, out_bytes, capacity, out_length);
}

HHSExactStatus hhs_x86_64_bytecode_copy_exact(
    const uint8_t *input,
    size_t length,
    uint8_t *output,
    size_t capacity,
    size_t *out_length
) {
    if (out_length != NULL)
        *out_length = length;
    if ((length != 0U && input == NULL) || (length != 0U && output == NULL))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < length)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    if (length == HHS_EXACT_VM81_FRAME_BYTES) {
        HHSExactVM81Frame frame;
        HHSExactStatus status = hhs_exact_vm81_frame_import_le(input, length, &frame);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        return hhs_exact_vm81_frame_export_le(
            &frame, output, capacity, out_length);
    }
    return hhs_x86_64_bytecode_copy_exact_raw(
        input, length, output, capacity, out_length);
}
