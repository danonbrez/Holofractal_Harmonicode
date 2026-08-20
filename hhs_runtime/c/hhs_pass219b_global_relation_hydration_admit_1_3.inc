/*
 * Pass 219B I6 repair-forward canonical full-symbolic admission.
 *
 * The legacy 1.2 implementation is retained under a hidden forensic symbol by
 * the cumulative ABI aggregate.  This replacement owns the public ABI symbol
 * and defers the inherited VM81 commit finalizer until every caller-controlled
 * validation point has succeeded.
 *
 * No relation algebra is reimplemented here.  N/D membership, RNA coordinate
 * construction, trinary gate behavior, I1 phase projection, and I5 locality
 * are inherited through hhs_exact_pass219b_global_relation_hydration_verify().
 */

static HHSExactStatus hhs_exact_pass219b_prepare_i6_uqcel_receipt(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactUQCELAdmissionV1 *validated_admission,
    const uint8_t *receipt_extension,
    size_t receipt_extension_length,
    HHSExactUQCELAdmissionV1 *out_prepared_admission
) {
    HHSExactStatus material_status;
    char change[HHS_EXACT_HASH72_STRLEN];
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    uint8_t frame_bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t frame_length = 0U;
    uint8_t material[HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES];
    size_t material_length = 0U;

    if (input == NULL || candidate_frame == NULL || validated_admission == NULL ||
        out_prepared_admission == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (receipt_extension_length != 0U && receipt_extension == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (validated_admission->decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        validated_admission->residual_mask != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hhs_exact_hash72_text_valid(input->previous_hash72))
        return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;

    memcpy(out_prepared_admission, validated_admission,
           sizeof(*out_prepared_admission));
    out_prepared_admission->frame_committed = 0U;

    if (hhs_exact_vm81_frame_export_le(
            candidate_frame, frame_bytes, sizeof(frame_bytes), &frame_length) != HHS_EXACT_STATUS_OK ||
        frame_length != HHS_EXACT_VM81_FRAME_BYTES)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    hhs_exact_uqcel_hash72_bytes(frame_bytes, frame_length, change);
    memcpy(out_prepared_admission->change_hash72, change, HHS_EXACT_HASH72_STRLEN);

    material_status = hhs_exact_uqcel_receipt_material(
        input, out_prepared_admission, material, sizeof(material), &material_length);
    if (material_status != HHS_EXACT_STATUS_OK)
        return material_status;

    if (receipt_extension_length != 0U) {
        if (receipt_extension_length > UINT32_MAX)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        if (!hhs_exact_uqcel_append_u32(
                material, sizeof(material), &material_length,
                (uint32_t)receipt_extension_length) ||
            !hhs_exact_uqcel_append(
                material, sizeof(material), &material_length,
                receipt_extension, receipt_extension_length))
            return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    }

    hhs_exact_uqcel_hash72_bytes(material, material_length, receipt);
    memcpy(out_prepared_admission->receipt_hash72, receipt, HHS_EXACT_HASH72_STRLEN);

    memcpy(out_prepared_admission->hash216_triplet,
           input->previous_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(out_prepared_admission->hash216_triplet + HHS_EXACT_HASH72_LEN,
           out_prepared_admission->change_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(out_prepared_admission->hash216_triplet + (2U * HHS_EXACT_HASH72_LEN),
           out_prepared_admission->receipt_hash72, HHS_EXACT_HASH72_LEN);
    out_prepared_admission->hash216_triplet[
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    hhs_exact_uqcel_hash216_bytes(
        out_prepared_admission->hash216_triplet,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN, identity);
    memcpy(out_prepared_admission->hash216_identity,
           identity, HHS_EXACT_UQCEL_HASH216_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219b_global_relation_hydration_admit(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    int8_t lo_shu_group,
    uint16_t g243,
    uint8_t phase_origin81,
    HHSExactPass219Hash216IndexResolverV1 index_resolver,
    void *index_context,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219RNAAdmissionV1 *out_rna_admission,
    HHSExactPass219BGlobalRelationHydrationWitnessV1 *out_witness
) {
    static const uint8_t composed_domain[] =
        "HHS-P219B-I6-N-D-HYDRATION-P192-COMPOSED-V1";
    HHSExactStatus status;
    HHSExactVM81Frame staged_candidate;
    HHSExactUQCELAdmissionV1 prepared_admission;
    HHSExactUQCELAdmissionV1 committed_admission;
    uint8_t hydration_extension[1024];
    size_t hydration_extension_length = 0U;
    uint8_t descriptor[HHS_EXACT_PASS192_FIB_MAX_DESCRIPTOR_BYTES];
    size_t descriptor_length = 0U;
    uint8_t base_material[HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES];
    size_t base_material_length = 0U;
    uint8_t material[HHS_EXACT_UQCEL_MAX_RECEIPT_BYTES +
                     HHS_EXACT_PASS192_FIB_MAX_DESCRIPTOR_BYTES + 1536U];
    size_t material_length = 0U;
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    uint32_t composed_version = hhs_exact_pass219_composed_version_word();

    if (input == NULL || candidate_frame == NULL || index_resolver == NULL ||
        out_committed_frame == NULL || out_rna_admission == NULL || out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    memset(out_rna_admission, 0, sizeof(*out_rna_admission));
    memset(out_witness, 0, sizeof(*out_witness));
    memset(&prepared_admission, 0, sizeof(prepared_admission));
    memset(&committed_admission, 0, sizeof(committed_admission));
    memcpy(&staged_candidate, candidate_frame, sizeof(staged_candidate));

    status = hhs_exact_pass219b_global_relation_hydration_verify(
        input, lo_shu_group, g243, phase_origin81, out_witness);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219b_hydration_receipt_extension(
        out_witness, hydration_extension, sizeof(hydration_extension),
        &hydration_extension_length);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    /*
     * Prepare the exact VM81/UQCEL receipt without invoking mutation authority.
     * The prepared admission remains frame_committed=0 until every composed
     * proof and every Hash216 index resolution below succeeds.
     */
    status = hhs_exact_pass219b_prepare_i6_uqcel_receipt(
        input, &staged_candidate, &out_witness->uqcel,
        hydration_extension, hydration_extension_length,
        &prepared_admission);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_rna_admission->struct_size = (uint32_t)sizeof(*out_rna_admission);
    out_rna_admission->version = hhs_exact_pass219_rna_version();
    out_rna_admission->native_phase = out_witness->native_phase;
    out_rna_admission->trinary_gate = out_witness->trinary_gate;
    out_rna_admission->coordinate = out_witness->coordinate;
    out_rna_admission->composed.struct_size =
        (uint32_t)sizeof(out_rna_admission->composed);
    out_rna_admission->composed.version = composed_version;
    out_rna_admission->composed.uqcel = prepared_admission;

    status = hhs_exact_pass192_fibonacci_compress(
        HHS_EXACT_PASS219_UCE_FIBONACCI_DEPTH,
        descriptor, sizeof(descriptor), &descriptor_length,
        &out_rna_admission->composed.fibonacci);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass192_fibonacci_validate_descriptor(
        HHS_EXACT_PASS219_UCE_FIBONACCI_DEPTH,
        descriptor, descriptor_length);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_uqcel_receipt_material(
        input, &prepared_admission,
        base_material, sizeof(base_material), &base_material_length);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (base_material_length > UINT32_MAX ||
        hydration_extension_length > UINT32_MAX ||
        descriptor_length > UINT32_MAX)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    if (!hhs_exact_uqcel_append(material, sizeof(material), &material_length,
                                composed_domain, sizeof(composed_domain) - 1U) ||
        !hhs_exact_uqcel_append_u32(material, sizeof(material), &material_length,
                                    composed_version) ||
        !hhs_exact_uqcel_append_u32(material, sizeof(material), &material_length,
                                    (uint32_t)base_material_length) ||
        !hhs_exact_uqcel_append(material, sizeof(material), &material_length,
                                base_material, base_material_length) ||
        !hhs_exact_uqcel_append_u32(material, sizeof(material), &material_length,
                                    (uint32_t)hydration_extension_length) ||
        !hhs_exact_uqcel_append(material, sizeof(material), &material_length,
                                hydration_extension, hydration_extension_length) ||
        !hhs_exact_uqcel_append_u32(material, sizeof(material), &material_length,
                                    (uint32_t)descriptor_length) ||
        !hhs_exact_uqcel_append(material, sizeof(material), &material_length,
                                descriptor, descriptor_length))
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    hhs_exact_uqcel_hash72_bytes(material, material_length, receipt);
    memcpy(out_rna_admission->composed.final_receipt_hash72,
           receipt, HHS_EXACT_HASH72_STRLEN);
    memcpy(out_rna_admission->composed.final_hash216_triplet,
           input->previous_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(out_rna_admission->composed.final_hash216_triplet + HHS_EXACT_HASH72_LEN,
           prepared_admission.change_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(out_rna_admission->composed.final_hash216_triplet +
           (2U * HHS_EXACT_HASH72_LEN),
           out_rna_admission->composed.final_receipt_hash72,
           HHS_EXACT_HASH72_LEN);
    out_rna_admission->composed.final_hash216_triplet[
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    hhs_exact_uqcel_hash216_bytes(
        out_rna_admission->composed.final_hash216_triplet,
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN, identity);
    memcpy(out_rna_admission->composed.final_hash216_identity,
           identity, HHS_EXACT_UQCEL_HASH216_STRLEN);

    status = hhs_exact_pass219_hash216_transition_init(
        input->previous_hash72,
        prepared_admission.change_hash72,
        out_rna_admission->composed.final_receipt_hash72,
        out_rna_admission->composed.final_hash216_identity,
        &out_rna_admission->transition);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_hash216_resolve_indexes(
        &out_rna_admission->transition, index_resolver, index_context);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_hash216_indexes_complete(
        &out_rna_admission->transition);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    /*
     * First and only canonical mutation call for this public operation.
     * Every external/caller-controlled failure point has completed above.
     * The finalizer recomputes the same base receipt from the stable staged
     * candidate and exact hydration extension, then performs the VM81 copy.
     */
    status = hhs_exact_vm81_finalize_uqcel(
        input, &staged_candidate, &out_witness->uqcel,
        HHS_EXACT_STATUS_OK,
        hydration_extension, hydration_extension_length,
        out_committed_frame, &committed_admission);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_rna_admission->composed.uqcel = committed_admission;
    out_witness->uqcel = committed_admission;
    out_witness->rna_composed_verified = 1U;
    out_witness->global_relation_bridge_verified = 1U;
    return HHS_EXACT_STATUS_OK;
}
