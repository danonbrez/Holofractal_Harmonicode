static int hhs_exact_uqcel_append(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    const void *data,
    size_t length
) {
    if (*cursor > capacity || length > capacity - *cursor)
        return 0;
    if (length != 0U)
        memcpy(out + *cursor, data, length);
    *cursor += length;
    return 1;
}

static int hhs_exact_uqcel_append_u16(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    uint16_t value
) {
    uint8_t bytes[2] = {(uint8_t)(value >> 8U), (uint8_t)(value & UINT16_C(0xFF))};
    return hhs_exact_uqcel_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static int hhs_exact_uqcel_append_u32(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    uint32_t value
) {
    uint8_t bytes[4] = {
        (uint8_t)(value >> 24U), (uint8_t)(value >> 16U),
        (uint8_t)(value >> 8U), (uint8_t)value
    };
    return hhs_exact_uqcel_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static int hhs_exact_uqcel_append_u64(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    uint64_t value
) {
    uint8_t bytes[8];
    size_t i;
    for (i = 0U; i < 8U; ++i)
        bytes[7U - i] = (uint8_t)(value >> (8U * i));
    return hhs_exact_uqcel_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static int hhs_exact_uqcel_append_big(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    const HHSExactBigUIntView *value
) {
    if (value->byte_length > UINT16_MAX)
        return 0;
    return hhs_exact_uqcel_append_u16(out, capacity, cursor, (uint16_t)value->byte_length) &&
           hhs_exact_uqcel_append(out, capacity, cursor, value->bytes_be, value->byte_length);
}

HHSExactStatus hhs_exact_uqcel_receipt_material(
    const HHSExactUQCELInputV1 *input,
    const HHSExactUQCELAdmissionV1 *admission,
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    static const uint8_t domain[] = "HHS-P219-UQCEL-ADMISSION-V1";
    size_t cursor = 0U;
    if (input == NULL || admission == NULL || out_length == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (out_bytes == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    if (!hhs_exact_uqcel_append(out_bytes, capacity, &cursor, domain, sizeof(domain) - 1U) ||
        !hhs_exact_uqcel_append_u32(out_bytes, capacity, &cursor, input->uqcel_version) ||
        !hhs_exact_uqcel_append_u32(out_bytes, capacity, &cursor, input->profile) ||
        !hhs_exact_uqcel_append_u32(out_bytes, capacity, &cursor, admission->decision) ||
        !hhs_exact_uqcel_append_u32(out_bytes, capacity, &cursor, admission->reject_reason) ||
        !hhs_exact_uqcel_append_u64(out_bytes, capacity, &cursor, admission->required_mask) ||
        !hhs_exact_uqcel_append_u64(out_bytes, capacity, &cursor, admission->satisfied_mask) ||
        !hhs_exact_uqcel_append_u64(out_bytes, capacity, &cursor, admission->failed_mask) ||
        !hhs_exact_uqcel_append_u64(out_bytes, capacity, &cursor, admission->residual_mask) ||
        !hhs_exact_uqcel_append_u16(out_bytes, capacity, &cursor, admission->vm5184_address) ||
        !hhs_exact_uqcel_append(out_bytes, capacity, &cursor, input->source_envelope_sha256,
                                HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES) ||
        !hhs_exact_uqcel_append_big(out_bytes, capacity, &cursor, &input->P) ||
        !hhs_exact_uqcel_append_big(out_bytes, capacity, &cursor, &input->p) ||
        !hhs_exact_uqcel_append_big(out_bytes, capacity, &cursor, &input->q) ||
        !hhs_exact_uqcel_append_big(out_bytes, capacity, &cursor, &input->delta) ||
        !hhs_exact_uqcel_append_big(out_bytes, capacity, &cursor, &input->A) ||
        !hhs_exact_uqcel_append_big(out_bytes, capacity, &cursor, &input->B) ||
        !hhs_exact_uqcel_append(out_bytes, capacity, &cursor, &input->cell81, 1U) ||
        !hhs_exact_uqcel_append(out_bytes, capacity, &cursor, &input->left_basis8, 1U) ||
        !hhs_exact_uqcel_append(out_bytes, capacity, &cursor, &input->right_basis8, 1U) ||
        !hhs_exact_uqcel_append(out_bytes, capacity, &cursor, &admission->qr_bit, 1U) ||
        !hhs_exact_uqcel_append(out_bytes, capacity, &cursor, &admission->expected_phase, 1U) ||
        !hhs_exact_uqcel_append(out_bytes, capacity, &cursor, &admission->observed_phase, 1U)) {
        *out_length = cursor;
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    }

    *out_length = cursor;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_vm81_admit_uqcel(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactUQCELAdmissionV1 *out_admission
) {
    HHSExactStatus validation_status;
    HHSExactStatus material_status;
    char change[HHS_EXACT_HASH72_STRLEN];
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    uint8_t frame_bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t frame_length = 0U;
    uint8_t material[HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES];
    size_t material_length = 0U;

    if (input == NULL || candidate_frame == NULL || out_committed_frame == NULL || out_admission == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    validation_status = hhs_exact_uqcel_validate(input, out_admission);

    if (!hhs_exact_hash72_text_valid(input->previous_hash72)) {
        out_admission->decision = HHS_EXACT_UQCEL_DECISION_REJECT;
        out_admission->reject_reason = HHS_EXACT_UQCEL_REASON_SOURCE_HASH;
        out_admission->failed_mask |= HHS_UQCEL_CONSTRAINT_SOURCE;
        return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
    }

    if (hhs_exact_vm81_frame_export_le(
            candidate_frame, frame_bytes, sizeof(frame_bytes), &frame_length) != HHS_EXACT_STATUS_OK ||
        frame_length != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    hhs_exact_uqcel_hash72_bytes(frame_bytes, frame_length, change);
    memcpy(out_admission->change_hash72, change, HHS_EXACT_HASH72_STRLEN);

    material_status = hhs_exact_uqcel_receipt_material(
        input, out_admission, material, sizeof(material), &material_length);
    if (material_status != HHS_EXACT_STATUS_OK)
        return material_status;
    hhs_exact_uqcel_hash72_bytes(material, material_length, receipt);
    memcpy(out_admission->receipt_hash72, receipt, HHS_EXACT_HASH72_STRLEN);

    memcpy(out_admission->hash216_triplet, input->previous_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(out_admission->hash216_triplet + HHS_EXACT_HASH72_LEN,
           out_admission->change_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(out_admission->hash216_triplet + (2U * HHS_EXACT_HASH72_LEN),
           out_admission->receipt_hash72, HHS_EXACT_HASH72_LEN);
    out_admission->hash216_triplet[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    hhs_exact_uqcel_hash216_bytes(
        out_admission->hash216_triplet,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN,
        identity);
    memcpy(out_admission->hash216_identity, identity, HHS_EXACT_UQCEL_HASH216_STRLEN);

    if (validation_status == HHS_EXACT_STATUS_OK &&
        out_admission->decision == HHS_EXACT_UQCEL_DECISION_ADMIT) {
        memcpy(out_committed_frame, candidate_frame, sizeof(*out_committed_frame));
        out_admission->frame_committed = 1U;
        return HHS_EXACT_STATUS_OK;
    }
    return validation_status;
}
