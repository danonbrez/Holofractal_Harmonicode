#include <openssl/sha.h>

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static const char *const HHS220_I077_SOURCE_NODES[
    HHS_EXACT_PASS220_I077_NODE_COUNT
] = {
    "MatrixPower[M_wz,x^2]",
    "MatrixPower[M_xy,x^4]"
};

static const char *const HHS220_I077_EXPONENT_TOKENS[
    HHS_EXACT_PASS220_I077_NODE_COUNT
] = {
    "x^2",
    "x^4"
};

static const uint32_t HHS220_I077_EXPONENT_DEGREES[
    HHS_EXACT_PASS220_I077_NODE_COUNT
] = {
    2U,
    4U
};

static const uint8_t HHS220_I077_CELL_TOKENS[
    HHS_EXACT_PASS220_I077_NODE_COUNT
][HHS_EXACT_PASS220_I077_CELL_OCCURRENCES] = {
    {
        HHS_EXACT_PASS220_I077_CELL_NEG_WZ,
        HHS_EXACT_PASS220_I077_CELL_Z_MINUS_W,
        HHS_EXACT_PASS220_I077_CELL_Z_MINUS_W,
        HHS_EXACT_PASS220_I077_CELL_WZ,
        HHS_EXACT_PASS220_I077_CELL_WZ,
        HHS_EXACT_PASS220_I077_CELL_NEG_WZ,
        HHS_EXACT_PASS220_I077_CELL_Y_PLUS_X,
        HHS_EXACT_PASS220_I077_CELL_Z_MINUS_W
    },
    {
        HHS_EXACT_PASS220_I077_CELL_NEG_XY,
        HHS_EXACT_PASS220_I077_CELL_Y_PLUS_X,
        HHS_EXACT_PASS220_I077_CELL_Y_PLUS_X,
        HHS_EXACT_PASS220_I077_CELL_XY,
        HHS_EXACT_PASS220_I077_CELL_XY,
        HHS_EXACT_PASS220_I077_CELL_NEG_XY,
        HHS_EXACT_PASS220_I077_CELL_Y_PLUS_X,
        HHS_EXACT_PASS220_I077_CELL_Z_MINUS_W
    }
};

static uint32_t hhs220_i077_version_word(void) {
    return (HHS_EXACT_PASS220_I077_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS220_I077_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS220_I077_VERSION_PATCH;
}

static void hhs220_i077_sha256_hex(
    const uint8_t digest[HHS_EXACT_PASS220_I077_SHA256_BYTES],
    char out[HHS_EXACT_PASS220_I077_SHA256_HEX_STRLEN]
) {
    static const char HEX[] = "0123456789abcdef";
    size_t i;
    for (i = 0U; i < HHS_EXACT_PASS220_I077_SHA256_BYTES; ++i) {
        out[2U * i] = HEX[(digest[i] >> 4U) & 0x0FU];
        out[(2U * i) + 1U] = HEX[digest[i] & 0x0FU];
    }
    out[64] = '\0';
}

static int hhs220_i077_hash_bytes(
    const uint8_t *bytes,
    size_t length,
    uint8_t out[HHS_EXACT_PASS220_I077_SHA256_BYTES]
) {
    if (bytes == NULL || out == NULL)
        return 0;
    return SHA256(bytes, length, out) != NULL;
}

static int hhs220_i077_append(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    const void *data,
    size_t length
) {
    if (out == NULL || cursor == NULL || data == NULL ||
        *cursor > capacity || length > capacity - *cursor)
        return 0;
    memcpy(out + *cursor, data, length);
    *cursor += length;
    return 1;
}

static int hhs220_i077_build_environment_root(
    uint32_t node_id,
    uint8_t out[HHS_EXACT_PASS220_I077_SHA256_BYTES]
) {
    static const uint8_t DOMAIN[] =
        "HHS-P220-I077-VM81-EXACT-MATRIX-POWER-EXECUTION-V1";
    uint8_t material[256U];
    size_t cursor = 0U;
    const char *source;
    const char *exponent;

    if (node_id >= HHS_EXACT_PASS220_I077_NODE_COUNT || out == NULL)
        return 0;

    source = HHS220_I077_SOURCE_NODES[node_id];
    exponent = HHS220_I077_EXPONENT_TOKENS[node_id];

    if (!hhs220_i077_append(
            material, sizeof(material), &cursor,
            DOMAIN, sizeof(DOMAIN) - 1U) ||
        !hhs220_i077_append(
            material, sizeof(material), &cursor,
            &node_id, sizeof(node_id)) ||
        !hhs220_i077_append(
            material, sizeof(material), &cursor,
            source, strlen(source)) ||
        !hhs220_i077_append(
            material, sizeof(material), &cursor,
            exponent, strlen(exponent)) ||
        !hhs220_i077_append(
            material, sizeof(material), &cursor,
            HHS220_I077_CELL_TOKENS[node_id],
            HHS_EXACT_PASS220_I077_CELL_OCCURRENCES))
        return 0;

    return hhs220_i077_hash_bytes(material, cursor, out);
}

static void hhs220_i077_build_frame(
    uint32_t node_id,
    const uint8_t environment_root[HHS_EXACT_PASS220_I077_SHA256_BYTES],
    HHSExactVM81Frame *out_frame
) {
    uint32_t i;
    uint32_t chunk;
    uint32_t byte_index;

    memset(out_frame, 0, sizeof(*out_frame));
    out_frame->words[0] = UINT64_C(0x4832323049303737); /* H220I077 */
    out_frame->words[1] = (uint64_t)node_id;
    out_frame->words[2] = HHS_EXACT_PASS220_I077_ROWS;
    out_frame->words[3] = HHS_EXACT_PASS220_I077_COLUMNS;
    out_frame->words[4] = HHS220_I077_EXPONENT_DEGREES[node_id];
    out_frame->words[5] = HHS_EXACT_PASS220_I077_CELL_OCCURRENCES;
    out_frame->words[6] = UINT64_C(0x45584143544d5057); /* EXACTMPW */

    for (i = 0U; i < HHS_EXACT_PASS220_I077_CELL_OCCURRENCES; ++i)
        out_frame->words[7U + i] =
            (uint64_t)HHS220_I077_CELL_TOKENS[node_id][i];

    for (chunk = 0U; chunk < 4U; ++chunk) {
        uint64_t word = 0U;
        for (byte_index = 0U; byte_index < 8U; ++byte_index) {
            word |=
                ((uint64_t)environment_root[(chunk * 8U) + byte_index])
                << (8U * byte_index);
        }
        out_frame->words[15U + chunk] = word;
    }

    out_frame->words[19] = 1U; /* source identity exact */
    out_frame->words[20] = 1U; /* ordered topology exact */
    out_frame->words[21] = 1U; /* exact symbolic node executed */
    out_frame->words[22] = 0U; /* host MatrixPower */
    out_frame->words[23] = 0U; /* square-matrix fallback */
    out_frame->words[24] = 0U; /* numeric exponent evaluation */
    out_frame->words[25] = 0U; /* derived matrix-power value */
}

static void hhs220_i077_set_big_view(
    HHSExactBigUIntView *view,
    const uint8_t *bytes,
    size_t length
) {
    view->struct_size = (uint32_t)sizeof(*view);
    view->byte_length = (uint32_t)length;
    view->bytes_be = bytes;
}

static HHSExactStatus hhs220_i077_admit_and_replay(
    uint32_t node_id,
    const HHSExactVM81Frame *candidate,
    HHSExactPass220I077ExecutionV1 *out_execution
) {
    static const uint8_t P_BYTES[] = {0x02U};
    static const uint8_t P_LOWER_BYTES[] = {0x01U};
    static const uint8_t Q_BYTES[] = {0x03U};
    static const uint8_t DELTA_BYTES[] = {0x01U};
    static const uint8_t AB_BYTES[] = {0x04U};
    HHSExactUQCELInputV1 input;
    HHSExactVM81Frame committed;
    HHSExactVM81Frame replay_committed;
    HHSExactUQCELAdmissionV1 admission;
    HHSExactUQCELAdmissionV1 replay;
    uint8_t uqcel_source_sha256[HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES];
    HHSExactStatus status;

    memset(&input, 0, sizeof(input));
    memset(&committed, 0, sizeof(committed));
    memset(&replay_committed, 0, sizeof(replay_committed));
    memset(&admission, 0, sizeof(admission));
    memset(&replay, 0, sizeof(replay));

    status = hhs_exact_uqcel_source_sha256(uqcel_source_sha256);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    hhs220_i077_set_big_view(&input.P, P_BYTES, sizeof(P_BYTES));
    hhs220_i077_set_big_view(&input.p, P_LOWER_BYTES, sizeof(P_LOWER_BYTES));
    hhs220_i077_set_big_view(&input.q, Q_BYTES, sizeof(Q_BYTES));
    hhs220_i077_set_big_view(&input.delta, DELTA_BYTES, sizeof(DELTA_BYTES));
    hhs220_i077_set_big_view(&input.A, AB_BYTES, sizeof(AB_BYTES));
    hhs220_i077_set_big_view(&input.B, AB_BYTES, sizeof(AB_BYTES));
    input.cell81 = (uint8_t)node_id;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    memcpy(
        input.source_envelope_sha256,
        uqcel_source_sha256,
        sizeof(uqcel_source_sha256));
    memset(
        input.previous_hash72,
        (unsigned char)HHS_EXACT_HASH72_ALPHABET[0],
        HHS_EXACT_HASH72_LEN);
    input.previous_hash72[HHS_EXACT_HASH72_LEN] = '\0';

    status = hhs_exact_vm81_admit_uqcel(
        &input, candidate, &committed, &admission);
    if (status != HHS_EXACT_STATUS_OK ||
        admission.decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        admission.frame_committed != 1U ||
        memcmp(candidate, &committed, sizeof(*candidate)) != 0) {
        out_execution->reason =
            HHS_EXACT_PASS220_I077_REASON_VM81_ADMISSION;
        return status == HHS_EXACT_STATUS_OK
                   ? HHS_EXACT_STATUS_INVARIANT_FAILURE
                   : status;
    }

    status = hhs_exact_vm81_admit_uqcel(
        &input, candidate, &replay_committed, &replay);
    if (status != HHS_EXACT_STATUS_OK ||
        replay.decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        replay.frame_committed != 1U ||
        memcmp(candidate, &replay_committed, sizeof(*candidate)) != 0 ||
        memcmp(&committed, &replay_committed, sizeof(committed)) != 0 ||
        strcmp(admission.change_hash72, replay.change_hash72) != 0 ||
        strcmp(admission.receipt_hash72, replay.receipt_hash72) != 0 ||
        strcmp(admission.hash216_triplet, replay.hash216_triplet) != 0 ||
        strcmp(admission.hash216_identity, replay.hash216_identity) != 0) {
        out_execution->reason = HHS_EXACT_PASS220_I077_REASON_REPLAY;
        return status == HHS_EXACT_STATUS_OK
                   ? HHS_EXACT_STATUS_INVARIANT_FAILURE
                   : status;
    }

    out_execution->exact_vm81_admission_verified = 1U;
    out_execution->atomic_frame_commit_verified = 1U;
    out_execution->hash72_receipt_verified = 1U;
    out_execution->hash216_transition_identity_verified = 1U;
    out_execution->deterministic_replay_verified = 1U;
    out_execution->canonical_state_persisted = 0U;
    out_execution->vm5184_address = admission.vm5184_address;
    out_execution->vm81_steps = 1U;
    out_execution->replay_vm81_steps = 1U;
    memcpy(
        out_execution->change_hash72,
        admission.change_hash72,
        sizeof(out_execution->change_hash72));
    memcpy(
        out_execution->receipt_hash72,
        admission.receipt_hash72,
        sizeof(out_execution->receipt_hash72));
    memcpy(
        out_execution->replay_hash72,
        replay.receipt_hash72,
        sizeof(out_execution->replay_hash72));
    memcpy(
        out_execution->proof_hash216,
        admission.hash216_triplet,
        sizeof(out_execution->proof_hash216));
    memcpy(
        out_execution->transition_hash216,
        admission.hash216_identity,
        sizeof(out_execution->transition_hash216));

    return HHS_EXACT_STATUS_OK;
}

uint32_t hhs_exact_pass220_i077_version(void) {
    return hhs220_i077_version_word();
}

HHSExactStatus hhs_exact_pass220_i077_descriptor(
    HHSExactPass220I077DescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs220_i077_version_word();
    out_descriptor->node_count = HHS_EXACT_PASS220_I077_NODE_COUNT;
    out_descriptor->rows = HHS_EXACT_PASS220_I077_ROWS;
    out_descriptor->columns = HHS_EXACT_PASS220_I077_COLUMNS;
    out_descriptor->cell_occurrences_per_node =
        HHS_EXACT_PASS220_I077_CELL_OCCURRENCES;
    out_descriptor->unique_cell_roots =
        HHS_EXACT_PASS220_I077_UNIQUE_CELL_ROOTS;
    out_descriptor->exact_matrix_power_hir_required = 1U;
    out_descriptor->native_symbolic_executor = 1U;
    out_descriptor->rectangular_4x2_supported = 1U;
    out_descriptor->source_identity_required = 1U;
    out_descriptor->ordered_topology_required = 1U;
    out_descriptor->vm81_transport_admission = 1U;
    out_descriptor->hash72_execution_receipt = 1U;
    out_descriptor->hash216_transition_identity = 1U;
    out_descriptor->deterministic_replay = 1U;
    out_descriptor->matrix_power_value_derivation = 0U;
    out_descriptor->host_matrixpower_authority = 0U;
    out_descriptor->host_square_matrix_requirement_authority = 0U;
    out_descriptor->numeric_exponent_evaluation_authority = 0U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->canonical_state_persistence_authority = 0U;
    out_descriptor->canonical_vm81_mutation_authority = 0U;
    out_descriptor->canonical_hash72_commit_authority = 0U;
    out_descriptor->canonical_hash216_commit_authority = 0U;
    out_descriptor->external_egress_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass220_i077_execute(
    uint32_t node_id,
    HHSExactPass220I077ExecutionV1 *out_execution
) {
    HHSExactVM81Frame candidate;
    uint8_t environment_root[HHS_EXACT_PASS220_I077_SHA256_BYTES];
    uint8_t source_digest[HHS_EXACT_PASS220_I077_SHA256_BYTES];
    uint8_t cells_digest[HHS_EXACT_PASS220_I077_SHA256_BYTES];
    const char *source;
    const char *exponent;
    HHSExactStatus status;

    if (out_execution == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_execution, 0, sizeof(*out_execution));
    out_execution->struct_size = (uint32_t)sizeof(*out_execution);
    out_execution->version = hhs220_i077_version_word();
    out_execution->decision = HHS_EXACT_PASS220_I077_UNRESOLVED;
    out_execution->reason = HHS_EXACT_PASS220_I077_REASON_NONE;
    out_execution->node_id = node_id;
    out_execution->rows = HHS_EXACT_PASS220_I077_ROWS;
    out_execution->columns = HHS_EXACT_PASS220_I077_COLUMNS;
    out_execution->cell_occurrence_count =
        HHS_EXACT_PASS220_I077_CELL_OCCURRENCES;
    out_execution->unique_cell_root_count =
        HHS_EXACT_PASS220_I077_UNIQUE_CELL_ROOTS;
    out_execution->host_matrixpower_used = 0U;
    out_execution->square_matrix_requirement_imported = 0U;
    out_execution->numeric_exponent_evaluated = 0U;
    out_execution->matrix_power_value_derived = 0U;
    out_execution->canonical_state_persisted = 0U;
    out_execution->floating_point_authority = 0U;

    if (node_id >= HHS_EXACT_PASS220_I077_NODE_COUNT) {
        out_execution->decision = HHS_EXACT_PASS220_I077_REJECTED;
        out_execution->reason = HHS_EXACT_PASS220_I077_REASON_NODE_ID;
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    source = HHS220_I077_SOURCE_NODES[node_id];
    exponent = HHS220_I077_EXPONENT_TOKENS[node_id];
    out_execution->exponent_token_degree =
        HHS220_I077_EXPONENT_DEGREES[node_id];

    if (strlen(source) >= sizeof(out_execution->source_node) ||
        strlen(exponent) >= sizeof(out_execution->exponent_token)) {
        out_execution->decision = HHS_EXACT_PASS220_I077_REJECTED;
        out_execution->reason =
            HHS_EXACT_PASS220_I077_REASON_SOURCE_IDENTITY;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    memcpy(
        out_execution->source_node,
        source,
        strlen(source) + 1U);
    memcpy(
        out_execution->exponent_token,
        exponent,
        strlen(exponent) + 1U);
    memcpy(
        out_execution->cell_tokens,
        HHS220_I077_CELL_TOKENS[node_id],
        sizeof(out_execution->cell_tokens));

    if (!hhs220_i077_hash_bytes(
            (const uint8_t *)source,
            strlen(source),
            source_digest) ||
        !hhs220_i077_hash_bytes(
            HHS220_I077_CELL_TOKENS[node_id],
            HHS_EXACT_PASS220_I077_CELL_OCCURRENCES,
            cells_digest) ||
        !hhs220_i077_build_environment_root(
            node_id, environment_root)) {
        out_execution->decision = HHS_EXACT_PASS220_I077_REJECTED;
        out_execution->reason =
            HHS_EXACT_PASS220_I077_REASON_SOURCE_IDENTITY;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    hhs220_i077_sha256_hex(
        source_digest, out_execution->source_node_sha256);
    hhs220_i077_sha256_hex(
        cells_digest, out_execution->ordered_cells_sha256);

    out_execution->source_identity_exact = 1U;
    out_execution->ordered_topology_verified = 1U;
    out_execution->exact_symbolic_node_executed = 1U;

    hhs220_i077_build_frame(node_id, environment_root, &candidate);
    status = hhs220_i077_admit_and_replay(
        node_id, &candidate, out_execution);
    if (status != HHS_EXACT_STATUS_OK) {
        out_execution->decision = HHS_EXACT_PASS220_I077_REJECTED;
        if (out_execution->reason == HHS_EXACT_PASS220_I077_REASON_NONE)
            out_execution->reason =
                HHS_EXACT_PASS220_I077_REASON_VM81_ADMISSION;
        return status;
    }

    if (out_execution->source_identity_exact != 1U ||
        out_execution->ordered_topology_verified != 1U ||
        out_execution->exact_symbolic_node_executed != 1U ||
        out_execution->host_matrixpower_used != 0U ||
        out_execution->square_matrix_requirement_imported != 0U ||
        out_execution->numeric_exponent_evaluated != 0U ||
        out_execution->matrix_power_value_derived != 0U ||
        out_execution->exact_vm81_admission_verified != 1U ||
        out_execution->atomic_frame_commit_verified != 1U ||
        out_execution->hash72_receipt_verified != 1U ||
        out_execution->hash216_transition_identity_verified != 1U ||
        out_execution->deterministic_replay_verified != 1U ||
        out_execution->canonical_state_persisted != 0U ||
        out_execution->floating_point_authority != 0U) {
        out_execution->decision = HHS_EXACT_PASS220_I077_REJECTED;
        out_execution->reason = HHS_EXACT_PASS220_I077_REASON_AUTHORITY;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_execution->decision = HHS_EXACT_PASS220_I077_VERIFIED;
    out_execution->reason = HHS_EXACT_PASS220_I077_REASON_NONE;
    return HHS_EXACT_STATUS_OK;
}
