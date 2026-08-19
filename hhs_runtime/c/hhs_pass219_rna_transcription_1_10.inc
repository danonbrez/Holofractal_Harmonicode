#include "../include/hhs_pass219_rna_transcription_1_10.h"

#include <string.h>

static uint32_t hhs_exact_pass219_rna_version_word(void) {
    return (HHS_EXACT_PASS219_RNA_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_RNA_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_RNA_VERSION_PATCH;
}

static int hhs_exact_pass219_hash72_valid(
    const char value[HHS_EXACT_HASH72_STRLEN]
) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_HASH72_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i) {
        if (strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static int hhs_exact_pass219_hash216_identity_valid(
    const char value[HHS_EXACT_UQCEL_HASH216_STRLEN]
) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        if (value[i] == '\0')
            return 0;
    }
    return 1;
}

uint32_t hhs_exact_pass219_rna_version(void) {
    return hhs_exact_pass219_rna_version_word();
}

HHSExactStatus hhs_exact_pass219_native_phase_witness(
    uint8_t left_basis,
    uint8_t right_basis,
    HHSExactPass219NativePhaseWitnessV1 *out_witness
) {
    HHSExactStatus status;
    if (out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = hhs_exact_pass219_rna_version_word();
    status = hhs_exact_phase_product(left_basis, right_basis, &out_witness->ordered_product);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    out_witness->ordered_source_preserved = 1U;
    out_witness->left_basis = left_basis;
    out_witness->right_basis = right_basis;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_trinary_phase_gate(
    uint8_t trit,
    HHSExactPass219TrinaryPhaseGateV1 *out_gate
) {
    HHSExactStatus status;
    if (out_gate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (trit >= HHS_EXACT_PASS219_TRIT_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_gate, 0, sizeof(*out_gate));
    out_gate->struct_size = (uint32_t)sizeof(*out_gate);
    out_gate->version = hhs_exact_pass219_rna_version_word();
    status = hhs_exact_phase_product(HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &out_gate->left_xy);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_phase_product(HHS_EXACT_PHASE_Y, HHS_EXACT_PHASE_X, &out_gate->right_yx);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_gate->trit = trit;
    out_gate->identity = trit;
    out_gate->center_relation = HHS_EXACT_PASS219_CENTER_RELATION_X_PLUS_Y;
    out_gate->center_left_basis = HHS_EXACT_PHASE_X;
    out_gate->center_right_basis = HHS_EXACT_PHASE_Y;
    out_gate->ordered_left_right_preserved = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hash216_transition_init(
    const char previous_hash72[HHS_EXACT_HASH72_STRLEN],
    const char change_hash72[HHS_EXACT_HASH72_STRLEN],
    const char receipt_hash72[HHS_EXACT_HASH72_STRLEN],
    const char transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    HHSExactPass219Hash216TransitionViewV1 *out_transition
) {
    size_t i;
    if (out_transition == NULL ||
        !hhs_exact_pass219_hash72_valid(previous_hash72) ||
        !hhs_exact_pass219_hash72_valid(change_hash72) ||
        !hhs_exact_pass219_hash72_valid(receipt_hash72) ||
        !hhs_exact_pass219_hash216_identity_valid(transition_identity216))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_transition, 0, sizeof(*out_transition));
    out_transition->struct_size = (uint32_t)sizeof(*out_transition);
    out_transition->version = hhs_exact_pass219_rna_version_word();
    memcpy(out_transition->previous_hash72, previous_hash72, HHS_EXACT_HASH72_STRLEN);
    memcpy(out_transition->change_hash72, change_hash72, HHS_EXACT_HASH72_STRLEN);
    memcpy(out_transition->receipt_hash72, receipt_hash72, HHS_EXACT_HASH72_STRLEN);
    memcpy(out_transition->transition_word216, previous_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(out_transition->transition_word216 + HHS_EXACT_HASH72_LEN,
           change_hash72, HHS_EXACT_HASH72_LEN);
    memcpy(out_transition->transition_word216 + (2U * HHS_EXACT_HASH72_LEN),
           receipt_hash72, HHS_EXACT_HASH72_LEN);
    out_transition->transition_word216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    memcpy(out_transition->transition_identity216,
           transition_identity216, HHS_EXACT_UQCEL_HASH216_STRLEN);

    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        HHSExactPass219Hash72TokenOccurrenceV1 *entry = &out_transition->occurrences[i];
        entry->struct_size = (uint32_t)sizeof(*entry);
        entry->version = hhs_exact_pass219_rna_version_word();
        entry->absolute_position216 = (uint16_t)i;
        entry->lane_role = (uint8_t)(i / HHS_EXACT_HASH72_LEN);
        entry->lane_position72 = (uint8_t)(i % HHS_EXACT_HASH72_LEN);
        entry->glyph = (uint8_t)out_transition->transition_word216[i];
        entry->sha256_index_present = 0U;
    }
    out_transition->resolved_index_count = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hash216_resolve_indexes(
    HHSExactPass219Hash216TransitionViewV1 *transition,
    HHSExactPass219Hash216IndexResolverV1 resolver,
    void *context
) {
    size_t i;
    if (transition == NULL || resolver == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (transition->struct_size < sizeof(*transition) ||
        transition->version != hhs_exact_pass219_rna_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        memset(transition->occurrences[i].sha256_index_record, 0,
               HHS_EXACT_PASS219_HASH216_SHA256_BYTES);
        transition->occurrences[i].sha256_index_present = 0U;
    }
    transition->resolved_index_count = 0U;

    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        HHSExactPass219Hash72TokenOccurrenceV1 *entry = &transition->occurrences[i];
        HHSExactStatus status = resolver(
            transition->transition_identity216,
            entry->lane_role,
            entry->lane_position72,
            entry->absolute_position216,
            entry->glyph,
            entry->sha256_index_record,
            context
        );
        if (status != HHS_EXACT_STATUS_OK) {
            size_t j;
            for (j = 0U; j < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++j) {
                memset(transition->occurrences[j].sha256_index_record, 0,
                       HHS_EXACT_PASS219_HASH216_SHA256_BYTES);
                transition->occurrences[j].sha256_index_present = 0U;
            }
            transition->resolved_index_count = 0U;
            return status;
        }
        entry->sha256_index_present = 1U;
        transition->resolved_index_count = (uint16_t)(i + 1U);
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hash216_indexes_complete(
    const HHSExactPass219Hash216TransitionViewV1 *transition
) {
    size_t i;
    if (transition == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (transition->struct_size < sizeof(*transition) ||
        transition->version != hhs_exact_pass219_rna_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (transition->resolved_index_count != HHS_EXACT_PASS219_HASH216_OCCURRENCES)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        if (transition->occurrences[i].sha256_index_present != 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_coordinate_from_pass189(
    uint8_t cell81,
    int8_t lo_shu_group,
    uint8_t operation64,
    uint16_t g243,
    HHSExactPass219HydrationCoordinateV1 *out_coordinate
) {
    uint32_t u;
    if (out_coordinate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (cell81 >= HHS_EXACT_VM81_CELLS ||
        lo_shu_group < HHS_EXACT_PASS219_LO_SHU_GROUP_MIN ||
        lo_shu_group > HHS_EXACT_PASS219_LO_SHU_GROUP_MAX ||
        operation64 >= HHS_EXACT_PASS219_OPERATION64_COUNT ||
        g243 >= HHS_EXACT_PASS219_G243_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    u = HHS_EXACT_PASS219_G243_COUNT * (uint32_t)operation64 + (uint32_t)g243;
    memset(out_coordinate, 0, sizeof(*out_coordinate));
    out_coordinate->struct_size = (uint32_t)sizeof(*out_coordinate);
    out_coordinate->version = hhs_exact_pass219_rna_version_word();
    out_coordinate->cell81 = cell81;
    out_coordinate->lo_shu_group = lo_shu_group;
    out_coordinate->lo_shu_group_offset41 = (uint8_t)((int)lo_shu_group + 20);
    out_coordinate->operation64 = operation64;
    out_coordinate->g243 = g243;
    out_coordinate->trit = (uint8_t)(u / HHS_EXACT_PASS219_HYDRATION_SLOT_COUNT);
    out_coordinate->slot5184 = (uint16_t)(u % HHS_EXACT_PASS219_HYDRATION_SLOT_COUNT);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_coordinate_to_pass189(
    const HHSExactPass219HydrationCoordinateV1 *coordinate,
    uint8_t *out_cell81,
    int8_t *out_lo_shu_group,
    uint8_t *out_operation64,
    uint16_t *out_g243
) {
    uint32_t u;
    uint8_t operation64;
    uint16_t g243;
    if (coordinate == NULL || out_cell81 == NULL || out_lo_shu_group == NULL ||
        out_operation64 == NULL || out_g243 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (coordinate->struct_size < sizeof(*coordinate) ||
        coordinate->version != hhs_exact_pass219_rna_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (coordinate->cell81 >= HHS_EXACT_VM81_CELLS ||
        coordinate->lo_shu_group < HHS_EXACT_PASS219_LO_SHU_GROUP_MIN ||
        coordinate->lo_shu_group > HHS_EXACT_PASS219_LO_SHU_GROUP_MAX ||
        coordinate->lo_shu_group_offset41 >= HHS_EXACT_PASS219_LO_SHU_GROUP_COUNT ||
        coordinate->trit >= HHS_EXACT_PASS219_TRIT_COUNT ||
        coordinate->slot5184 >= HHS_EXACT_PASS219_HYDRATION_SLOT_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (coordinate->lo_shu_group_offset41 != (uint8_t)((int)coordinate->lo_shu_group + 20))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    u = HHS_EXACT_PASS219_HYDRATION_SLOT_COUNT * (uint32_t)coordinate->trit +
        (uint32_t)coordinate->slot5184;
    operation64 = (uint8_t)(u / HHS_EXACT_PASS219_G243_COUNT);
    g243 = (uint16_t)(u % HHS_EXACT_PASS219_G243_COUNT);
    if (operation64 != coordinate->operation64 || g243 != coordinate->g243)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    *out_cell81 = coordinate->cell81;
    *out_lo_shu_group = coordinate->lo_shu_group;
    *out_operation64 = operation64;
    *out_g243 = g243;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_admit_composed(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    int8_t lo_shu_group,
    uint16_t g243,
    HHSExactPass219Hash216IndexResolverV1 index_resolver,
    void *index_context,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219RNAAdmissionV1 *out_admission
) {
    HHSExactVM81Frame staged_frame;
    HHSExactPass219ComposedAdmissionV1 staged_composed;
    HHSExactStatus status;
    uint8_t operation64;
    char previous[HHS_EXACT_HASH72_STRLEN];
    char change[HHS_EXACT_HASH72_STRLEN];
    char receipt[HHS_EXACT_HASH72_STRLEN];

    if (input == NULL || candidate_frame == NULL || index_resolver == NULL ||
        out_committed_frame == NULL || out_admission == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (input->left_basis8 >= HHS_EXACT_PHASE_BASIS_COUNT ||
        input->right_basis8 >= HHS_EXACT_PHASE_BASIS_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    memset(out_admission, 0, sizeof(*out_admission));
    out_admission->struct_size = (uint32_t)sizeof(*out_admission);
    out_admission->version = hhs_exact_pass219_rna_version_word();

    status = hhs_exact_pass219_native_phase_witness(
        input->left_basis8, input->right_basis8, &out_admission->native_phase);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    operation64 = (uint8_t)(input->left_basis8 * HHS_EXACT_PHASE_BASIS_COUNT +
                            input->right_basis8);
    status = hhs_exact_pass219_coordinate_from_pass189(
        input->cell81, lo_shu_group, operation64, g243, &out_admission->coordinate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_trinary_phase_gate(
        out_admission->coordinate.trit, &out_admission->trinary_gate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(&staged_frame, 0, sizeof(staged_frame));
    memset(&staged_composed, 0, sizeof(staged_composed));
    status = hhs_exact_pass219_admit_composed(
        input, candidate_frame, &staged_frame, &staged_composed);
    memcpy(&out_admission->composed, &staged_composed, sizeof(staged_composed));
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memcpy(previous, staged_composed.final_hash216_triplet, HHS_EXACT_HASH72_LEN);
    memcpy(change, staged_composed.final_hash216_triplet + HHS_EXACT_HASH72_LEN,
           HHS_EXACT_HASH72_LEN);
    memcpy(receipt, staged_composed.final_hash216_triplet + (2U * HHS_EXACT_HASH72_LEN),
           HHS_EXACT_HASH72_LEN);
    previous[HHS_EXACT_HASH72_LEN] = '\0';
    change[HHS_EXACT_HASH72_LEN] = '\0';
    receipt[HHS_EXACT_HASH72_LEN] = '\0';

    status = hhs_exact_pass219_hash216_transition_init(
        previous, change, receipt, staged_composed.final_hash216_identity,
        &out_admission->transition);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_hash216_resolve_indexes(
        &out_admission->transition, index_resolver, index_context);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_hash216_indexes_complete(&out_admission->transition);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memcpy(out_committed_frame, &staged_frame, sizeof(staged_frame));
    return HHS_EXACT_STATUS_OK;
}
