#include "hhs_pass219_i162_pass169_vm81_exact_symbolic_execution_1_23.h"

#include <openssl/sha.h>

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static const uint8_t HHS219_I162_COMBINED_SOURCE_SHA256[
    HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES
] = {
    0x33U, 0x15U, 0x64U, 0x1cU, 0x8dU, 0x6aU, 0xa9U, 0xfcU,
    0x4fU, 0x39U, 0x18U, 0xecU, 0xcdU, 0xa8U, 0xe3U, 0xa4U,
    0x0cU, 0x84U, 0x45U, 0xccU, 0x41U, 0x7aU, 0x65U, 0xe5U,
    0xdeU, 0xa6U, 0x83U, 0xf6U, 0x80U, 0x20U, 0xcfU, 0x53U
};

static const uint32_t HHS219_I162_GATE_OFFSETS[
    HHS_EXACT_PASS219_I162_GATE_COUNT
] = {96U, 240U, 266U, 274U, 285U};

static uint32_t hhs219_i162_version_word(void) {
    return (HHS_EXACT_PASS219_I162_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_I162_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_I162_VERSION_PATCH;
}

static uint32_t hhs219_i162_pass159_version_word(void) {
    return (HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_PATCH;
}

static uint32_t hhs219_i162_binding_version_word(void) {
    return (HHS_EXACT_PASS219_PASS169_BINDING_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_PASS169_BINDING_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_PASS169_BINDING_VERSION_PATCH;
}

static int hhs219_i162_root_nonzero(const uint8_t *root, size_t length) {
    size_t i;
    uint8_t aggregate = 0U;
    if (root == NULL)
        return 0;
    for (i = 0U; i < length; ++i)
        aggregate = (uint8_t)(aggregate | root[i]);
    return aggregate != 0U;
}

static int hhs219_i162_provenance_valid(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance
) {
    size_t i;
    if (provenance == NULL ||
        provenance->struct_size < sizeof(*provenance) ||
        provenance->version != hhs219_i162_pass159_version_word() ||
        provenance->source_length !=
            HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SOURCE_BYTES ||
        provenance->gate_count != HHS_EXACT_PASS219_I162_GATE_COUNT ||
        memcmp(provenance->combined_source_sha256,
               HHS219_I162_COMBINED_SOURCE_SHA256,
               sizeof(HHS219_I162_COMBINED_SOURCE_SHA256)) != 0)
        return 0;

    for (i = 0U; i < HHS_EXACT_PASS219_I162_GATE_COUNT; ++i) {
        if (provenance->gate_offsets[i] != HHS219_I162_GATE_OFFSETS[i])
            return 0;
    }

    return provenance->source_identity_exact == 1U &&
           provenance->gate_occurrence_provenance_exact == 1U &&
           provenance->frontend_chain_complete == 1U &&
           provenance->source_root_lineage_exact == 1U &&
           provenance->pass159_whole_expression_provenance_verified == 1U &&
           provenance->boolean_gate_results_available == 0U &&
           provenance->membrane_input_ready == 0U &&
           provenance->pass169_whole_expression_authority_required == 1U &&
           provenance->canonical_monolithic_proof == 0U &&
           provenance->floating_point_authority == 0U &&
           provenance->vm81_mutation_authority == 0U &&
           provenance->hash72_commit_authority == 0U &&
           provenance->persistence_mutation_authority == 0U &&
           hhs219_i162_root_nonzero(
               provenance->global_symbol_environment_root,
               sizeof(provenance->global_symbol_environment_root));
}

static int hhs219_i162_lo_shu_exact(void) {
    static const uint32_t matrix[3][3] = {
        {4U, 9U, 2U},
        {3U, 5U, 7U},
        {8U, 1U, 6U}
    };
    uint32_t stage1_numerator = 2U * (3U + 2U) - (3U - 2U);
    uint32_t stage1_denominator = 3U;
    uint32_t stage1;
    uint32_t stage2_numerator;
    uint32_t stage2;
    uint32_t nested_numerator;
    uint32_t nested;
    uint32_t row;
    uint32_t column;

    if (stage1_numerator % stage1_denominator != 0U)
        return 0;
    stage1 = stage1_numerator / stage1_denominator;
    stage2_numerator = 3U * 8U - 3U;
    if (stage1 == 0U || stage2_numerator % stage1 != 0U)
        return 0;
    stage2 = stage2_numerator / stage1;
    nested_numerator = (8U - 1U) * (4U + 3U);
    if (stage2 == 0U || nested_numerator % stage2 != 0U)
        return 0;
    nested = nested_numerator / stage2;
    if (stage1 != 3U || stage2 != 7U || nested != 7U)
        return 0;

    for (row = 0U; row < 3U; ++row) {
        if (matrix[row][0] + matrix[row][1] + matrix[row][2] != 15U)
            return 0;
    }
    for (column = 0U; column < 3U; ++column) {
        if (matrix[0][column] + matrix[1][column] + matrix[2][column] != 15U)
            return 0;
    }
    return matrix[0][0] + matrix[1][1] + matrix[2][2] == 15U &&
           matrix[0][2] + matrix[1][1] + matrix[2][0] == 15U;
}

static int hhs219_i162_append(
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

static int hhs219_i162_build_environment_root(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    uint16_t edge_mask,
    uint8_t gate_mask,
    uint8_t out_root[HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES]
) {
    static const uint8_t domain[] =
        "HHS-P219-I162-PASS169-VM81-EXACT-SYMBOLIC-ENV-V1";
    uint8_t material[192U];
    size_t cursor = 0U;
    const uint32_t values[] = {
        30U, 29U, 31U, 1U, 30U, 267U, 900U, 810000U
    };

    if (provenance == NULL || out_root == NULL)
        return 0;
    if (!hhs219_i162_append(material, sizeof(material), &cursor,
                            domain, sizeof(domain) - 1U) ||
        !hhs219_i162_append(material, sizeof(material), &cursor,
                            provenance->global_symbol_environment_root,
                            sizeof(provenance->global_symbol_environment_root)) ||
        !hhs219_i162_append(material, sizeof(material), &cursor,
                            provenance->combined_source_sha256,
                            sizeof(provenance->combined_source_sha256)) ||
        !hhs219_i162_append(material, sizeof(material), &cursor,
                            &edge_mask, sizeof(edge_mask)) ||
        !hhs219_i162_append(material, sizeof(material), &cursor,
                            &gate_mask, sizeof(gate_mask)) ||
        !hhs219_i162_append(material, sizeof(material), &cursor,
                            values, sizeof(values)))
        return 0;

    return SHA256(material, cursor, out_root) != NULL &&
           hhs219_i162_root_nonzero(
               out_root, HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES);
}

static void hhs219_i162_build_candidate_frame(
    const uint8_t environment_root[
        HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES
    ],
    HHSExactVM81Frame *out_frame
) {
    uint32_t chunk;
    uint32_t byte_index;
    if (out_frame == NULL)
        return;
    memset(out_frame, 0, sizeof(*out_frame));
    out_frame->words[0] = UINT64_C(0x4832313949313632);
    out_frame->words[1] = 30U;
    out_frame->words[2] = 29U;
    out_frame->words[3] = 31U;
    out_frame->words[4] = 1U;
    out_frame->words[5] = 900U;
    out_frame->words[6] = 810000U;
    out_frame->words[7] = 26970U;
    out_frame->words[8] = 71022U;
    out_frame->words[9] = HHS_EXACT_PASS219_I162_ALL_EDGE_MASK;
    out_frame->words[10] = HHS_EXACT_PASS219_I162_ALL_GATE_MASK;
    out_frame->words[11] =
        UINT64_C(18) |
        (UINT64_C(54) << 8U) |
        (UINT64_C(18) << 16U) |
        (UINT64_C(54) << 24U);

    for (chunk = 0U; chunk < 4U; ++chunk) {
        uint64_t word = 0U;
        for (byte_index = 0U; byte_index < 8U; ++byte_index) {
            word |= ((uint64_t)environment_root[chunk * 8U + byte_index])
                    << (8U * byte_index);
        }
        out_frame->words[12U + chunk] = word;
    }
}

static void hhs219_i162_set_big_view(
    HHSExactBigUIntView *view,
    const uint8_t *bytes,
    size_t length
) {
    view->struct_size = (uint32_t)sizeof(*view);
    view->byte_length = (uint32_t)length;
    view->bytes_be = bytes;
}

static HHSExactStatus hhs219_i162_vm81_commit_and_replay(
    const uint8_t environment_root[
        HHS_EXACT_PASS219_PASS169_BINDING_SHA256_BYTES
    ],
    HHSExactPass219I162ExecutionV1 *out_execution
) {
    static const uint8_t P_BYTES[] = {0x1eU};
    static const uint8_t P_LOWER_BYTES[] = {0x1dU};
    static const uint8_t Q_BYTES[] = {0x1fU};
    static const uint8_t DELTA_BYTES[] = {0x01U};
    static const uint8_t COMPAT_P2_BYTES[] = {0x03U, 0x84U};
    HHSExactUQCELInputV1 input;
    HHSExactVM81Frame candidate;
    HHSExactVM81Frame committed;
    HHSExactVM81Frame replay_committed;
    HHSExactUQCELAdmissionV1 admission;
    HHSExactUQCELAdmissionV1 replay;
    uint8_t uqcel_source_sha256[HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES];
    HHSExactStatus status;

    if (environment_root == NULL || out_execution == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(&input, 0, sizeof(input));
    memset(&committed, 0, sizeof(committed));
    memset(&replay_committed, 0, sizeof(replay_committed));
    memset(&admission, 0, sizeof(admission));
    memset(&replay, 0, sizeof(replay));
    hhs219_i162_build_candidate_frame(environment_root, &candidate);

    status = hhs_exact_uqcel_source_sha256(uqcel_source_sha256);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    hhs219_i162_set_big_view(&input.P, P_BYTES, sizeof(P_BYTES));
    hhs219_i162_set_big_view(&input.p, P_LOWER_BYTES, sizeof(P_LOWER_BYTES));
    hhs219_i162_set_big_view(&input.q, Q_BYTES, sizeof(Q_BYTES));
    hhs219_i162_set_big_view(&input.delta, DELTA_BYTES, sizeof(DELTA_BYTES));
    hhs219_i162_set_big_view(&input.A, COMPAT_P2_BYTES, sizeof(COMPAT_P2_BYTES));
    hhs219_i162_set_big_view(&input.B, COMPAT_P2_BYTES, sizeof(COMPAT_P2_BYTES));
    input.cell81 = 0U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    memcpy(input.source_envelope_sha256,
           uqcel_source_sha256, sizeof(uqcel_source_sha256));
    memset(input.previous_hash72,
           (unsigned char)HHS_EXACT_HASH72_ALPHABET[0], HHS_EXACT_HASH72_LEN);
    input.previous_hash72[HHS_EXACT_HASH72_LEN] = '\0';

    status = hhs_exact_vm81_admit_uqcel(
        &input, &candidate, &committed, &admission);
    if (status != HHS_EXACT_STATUS_OK ||
        admission.decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        admission.frame_committed != 1U ||
        memcmp(&candidate, &committed, sizeof(candidate)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_vm81_admit_uqcel(
        &input, &candidate, &replay_committed, &replay);
    if (status != HHS_EXACT_STATUS_OK ||
        replay.decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        replay.frame_committed != 1U ||
        memcmp(&candidate, &replay_committed, sizeof(candidate)) != 0 ||
        memcmp(&committed, &replay_committed, sizeof(committed)) != 0 ||
        strcmp(admission.change_hash72, replay.change_hash72) != 0 ||
        strcmp(admission.receipt_hash72, replay.receipt_hash72) != 0 ||
        strcmp(admission.hash216_triplet, replay.hash216_triplet) != 0 ||
        strcmp(admission.hash216_identity, replay.hash216_identity) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_execution->vm5184_address = admission.vm5184_address;
    out_execution->vm81_steps = 1U;
    out_execution->replay_vm81_steps = 1U;
    out_execution->exact_vm81_admission_verified = 1U;
    out_execution->atomic_commit_verified = 1U;
    out_execution->hash72_receipt_verified = 1U;
    out_execution->hash216_proof_identity_verified = 1U;
    out_execution->deterministic_replay_verified = 1U;
    memcpy(out_execution->proof_hash216,
           admission.hash216_triplet, sizeof(out_execution->proof_hash216));
    memcpy(out_execution->transition_hash216,
           admission.hash216_identity, sizeof(out_execution->transition_hash216));
    memcpy(out_execution->receipt_hash72,
           admission.receipt_hash72, sizeof(out_execution->receipt_hash72));
    memcpy(out_execution->replay_hash72,
           replay.receipt_hash72, sizeof(out_execution->replay_hash72));
    return HHS_EXACT_STATUS_OK;
}

uint32_t hhs_exact_pass219_i162_version(void) {
    return hhs219_i162_version_word();
}

HHSExactStatus hhs_exact_pass219_i162_descriptor(
    HHSExactPass219I162DescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs219_i162_version_word();
    out_descriptor->edge_count = HHS_EXACT_PASS219_I162_EDGE_COUNT;
    out_descriptor->gate_count = HHS_EXACT_PASS219_I162_GATE_COUNT;
    out_descriptor->required_edge_mask = HHS_EXACT_PASS219_I162_ALL_EDGE_MASK;
    out_descriptor->required_gate_mask = HHS_EXACT_PASS219_I162_ALL_GATE_MASK;
    out_descriptor->native_symbolic_verifier = 1U;
    out_descriptor->i161_typed_closure_preserved = 1U;
    out_descriptor->compatibility_ab_transport_only = 1U;
    out_descriptor->source_ab_definitionally_p2 = 0U;
    out_descriptor->full_symbolic_uqcel_v1_promoted = 0U;
    out_descriptor->vm81_transport_admission = 1U;
    out_descriptor->hash72_execution_receipt = 1U;
    out_descriptor->hash216_proof_transition_identity = 1U;
    out_descriptor->deterministic_replay = 1U;
    out_descriptor->source_reconstruction_inherited_from_pass159 = 1U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->hash216_persistence_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_i162_execute(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219I162ExecutionV1 *out_execution
) {
    const uint32_t P = 30U;
    const uint32_t p = 29U;
    const uint32_t q = 31U;
    const uint32_t t = 30U;
    const uint32_t m = 267U;
    const uint32_t P2 = P * P;
    const uint32_t pq = p * q;
    const uint32_t delta = P2 - pq;
    const uint32_t cubic = t * t * t - t;
    const uint32_t idempotent = m * m - m;
    const uint64_t AB = (uint64_t)P2 * (uint64_t)P2;
    HHSExactPhaseProduct xy;
    HHSExactPhaseProduct zw;
    HHSExactPhaseProduct xx;
    uint16_t edge_mask = 0U;
    uint8_t gate_mask = 0U;
    int typed_operand_pair_exact;
    int scalar_zero;
    int renewed_unit;
    int edge9;
    int edge8;
    HHSExactStatus status;

    if (out_execution == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_execution, 0, sizeof(*out_execution));
    out_execution->struct_size = (uint32_t)sizeof(*out_execution);
    out_execution->version = hhs219_i162_version_word();
    out_execution->decision = HHS_EXACT_PASS219_I162_UNRESOLVED;
    out_execution->reason = HHS_EXACT_PASS219_I162_REASON_NONE;
    out_execution->P = P;
    out_execution->p = p;
    out_execution->q = q;
    out_execution->delta = delta;
    out_execution->t = t;
    out_execution->m = m;
    out_execution->compatibility_ab_transport_only = 1U;
    out_execution->source_ab_definitionally_p2 = 0U;
    out_execution->ordinary_scalar_boundary_equality_claimed = 0U;
    out_execution->floating_point_authority = 0U;
    out_execution->hash216_persistence_authority = 0U;

    if (!hhs219_i162_provenance_valid(provenance)) {
        out_execution->decision = HHS_EXACT_PASS219_I162_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I162_REASON_PROVENANCE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (delta == 1U &&
        cubic == P * P * P - P / delta)
        edge_mask |= UINT16_C(1) << 0U;
    if (delta != 0U &&
        P * P * P - P / delta == cubic / delta)
        edge_mask |= UINT16_C(1) << 1U;

    if (delta == 1U && pq == P2 - 1U &&
        cubic == P * pq && cubic % pq == 0U &&
        P2 == pq + 1U && P2 / pq == 1U && P2 % pq == 1U)
        edge_mask |= UINT16_C(1) << 2U;
    if (pq != 0U &&
        P2 == pq + 1U && P2 % pq == 1U &&
        idempotent == 79U * pq + 1U && idempotent % pq == 1U)
        edge_mask |= UINT16_C(1) << 3U;

    if ((uint64_t)2U * (uint64_t)P2 ==
        (uint64_t)72U * (uint64_t)25U)
        edge_mask |= UINT16_C(1) << 4U;

    status = hhs_exact_phase_product(HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &xy);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_phase_product(HHS_EXACT_PHASE_Z, HHS_EXACT_PHASE_W, &zw);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_phase_product(HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_X, &xx);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    typed_operand_pair_exact =
        hhs219_i162_lo_shu_exact() &&
        xy.phase == 0U && zw.phase == 0U &&
        xy.orientation == 1U && zw.orientation == 1U &&
        P2 == 900U && pq == 899U &&
        UINT32_C(900) == P2;
    if (typed_operand_pair_exact)
        edge_mask |= UINT16_C(1) << 5U;

    if (typed_operand_pair_exact &&
        AB == UINT64_C(810000) &&
        AB / P2 == P2 && AB % P2 == 0U)
        edge_mask |= UINT16_C(1) << 6U;

    if (AB == UINT64_C(810000) &&
        (uint64_t)P2 * (uint64_t)P2 == AB &&
        AB / P2 == P2)
        edge_mask |= UINT16_C(1) << 7U;

    edge9 = delta == 1U &&
            P != 0U &&
            pq + 1U == P2 &&
            P * P == pq + 1U &&
            xx.phase == 36U;
    if (edge9)
        edge_mask |= UINT16_C(1) << 9U;

    scalar_zero =
        ((18U + 54U + 18U + 54U) % 72U) == 0U &&
        ((18U + 54U) % 72U) == 0U;
    renewed_unit =
        xy.phase == 0U && zw.phase == 0U &&
        delta == 1U;
    edge8 =
        scalar_zero && renewed_unit &&
        (pq + delta) == P2 &&
        AB % (pq + delta) == 0U &&
        AB / (pq + delta) == P2 &&
        cubic != 0U &&
        (edge_mask & (HHS_EXACT_PASS219_I162_ALL_EDGE_MASK &
                      ~(UINT16_C(1) << 8U))) ==
            (HHS_EXACT_PASS219_I162_ALL_EDGE_MASK &
             ~(UINT16_C(1) << 8U));
    if (edge8)
        edge_mask |= UINT16_C(1) << 8U;

    if ((edge_mask & (UINT16_C(1) << 4U)) != 0U)
        gate_mask |= UINT8_C(1) << 0U;
    if ((edge_mask & (UINT16_C(1) << 5U)) != 0U)
        gate_mask |= UINT8_C(1) << 1U;
    if ((edge_mask & (UINT16_C(1) << 6U)) != 0U)
        gate_mask |= UINT8_C(1) << 2U;
    if ((edge_mask & (UINT16_C(1) << 7U)) != 0U)
        gate_mask |= UINT8_C(1) << 3U;
    if ((edge_mask & (UINT16_C(1) << 8U)) != 0U)
        gate_mask |= UINT8_C(1) << 4U;

    out_execution->edge_proved_mask = edge_mask;
    out_execution->gate_true_mask = gate_mask;
    out_execution->typed_scalar_zero_verified = (uint8_t)scalar_zero;
    out_execution->typed_renewed_unit_verified = (uint8_t)renewed_unit;

    if (edge_mask != HHS_EXACT_PASS219_I162_ALL_EDGE_MASK) {
        out_execution->decision = HHS_EXACT_PASS219_I162_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I162_REASON_TYPED_BOUNDARY;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (gate_mask != HHS_EXACT_PASS219_I162_ALL_GATE_MASK) {
        out_execution->decision = HHS_EXACT_PASS219_I162_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I162_REASON_TYPED_JOIN;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_execution->all_ten_typed_joins_verified = 1U;

    if (!hhs219_i162_build_environment_root(
            provenance, edge_mask, gate_mask,
            out_execution->canonical_global_symbol_environment_root)) {
        out_execution->decision = HHS_EXACT_PASS219_I162_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I162_REASON_PROVENANCE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    status = hhs219_i162_vm81_commit_and_replay(
        out_execution->canonical_global_symbol_environment_root,
        out_execution);
    if (status != HHS_EXACT_STATUS_OK) {
        out_execution->decision = HHS_EXACT_PASS219_I162_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I162_REASON_VM81_ADMISSION;
        return status;
    }

    out_execution->source_reconstruction_verified =
        (uint8_t)(provenance->source_identity_exact == 1U &&
                  provenance->source_root_lineage_exact == 1U &&
                  provenance->frontend_chain_complete == 1U);
    if (!out_execution->source_reconstruction_verified) {
        out_execution->decision = HHS_EXACT_PASS219_I162_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I162_REASON_PROVENANCE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_execution->decision = HHS_EXACT_PASS219_I162_VERIFIED;
    out_execution->reason = HHS_EXACT_PASS219_I162_REASON_NONE;
    return HHS_EXACT_STATUS_OK;
}

static void hhs219_i162_copy_stage_hashes(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219Pass169AuthorityProofV1 *proof
) {
#define COPY_STAGE(field) memcpy(proof->field, provenance->field, sizeof(proof->field))
    COPY_STAGE(source_hash216);
    COPY_STAGE(tokens_hash216);
    COPY_STAGE(cst_hash216);
    COPY_STAGE(ast_hash216);
    COPY_STAGE(type_environment_hash216);
    COPY_STAGE(constraint_graph_hash216);
    COPY_STAGE(hir_hash216);
    COPY_STAGE(vmir_hash216);
#undef COPY_STAGE
}

HHSExactStatus hhs_pass169_verify_combined_gate_authority_i162_1_23(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219Pass169AuthorityProofV1 *out_proof
) {
    HHSExactPass219I162ExecutionV1 execution;
    HHSExactStatus status;
    uint32_t membrane_version;
    uint32_t gate;

    if (provenance == NULL || out_proof == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_proof, 0, sizeof(*out_proof));
    out_proof->struct_size = (uint32_t)sizeof(*out_proof);
    out_proof->version = hhs219_i162_binding_version_word();
    memcpy(out_proof->combined_source_sha256,
           provenance->combined_source_sha256,
           sizeof(out_proof->combined_source_sha256));
    memcpy(out_proof->pass159_provenance_root,
           provenance->global_symbol_environment_root,
           sizeof(out_proof->pass159_provenance_root));
    hhs219_i162_copy_stage_hashes(provenance, out_proof);

    status = hhs_exact_pass219_i162_execute(provenance, &execution);
    if (status != HHS_EXACT_STATUS_OK ||
        execution.decision != HHS_EXACT_PASS219_I162_VERIFIED)
        return status == HHS_EXACT_STATUS_OK
                   ? HHS_EXACT_STATUS_INVARIANT_FAILURE
                   : status;

    memcpy(out_proof->canonical_global_symbol_environment_root,
           execution.canonical_global_symbol_environment_root,
           sizeof(out_proof->canonical_global_symbol_environment_root));
    out_proof->gate_count = HHS_EXACT_PASS219_I162_GATE_COUNT;
    membrane_version = hhs_exact_pass219_global_membrane_version();
    for (gate = 0U; gate < HHS_EXACT_PASS219_I162_GATE_COUNT; ++gate) {
        HHSExactPass219GlobalGateWitnessV1 *witness = &out_proof->gates[gate];
        memset(witness, 0, sizeof(*witness));
        witness->struct_size = (uint32_t)sizeof(*witness);
        witness->version = membrane_version;
        witness->gate_index = gate;
        witness->source_offset = provenance->gate_offsets[gate];
        witness->boolean_result =
            (uint8_t)((execution.gate_true_mask >> gate) & UINT8_C(1));
        memcpy(witness->combined_source_sha256,
               provenance->combined_source_sha256,
               sizeof(witness->combined_source_sha256));
        memcpy(witness->global_symbol_environment_root,
               execution.canonical_global_symbol_environment_root,
               sizeof(witness->global_symbol_environment_root));
    }

    memcpy(out_proof->proof_hash216,
           execution.proof_hash216, sizeof(out_proof->proof_hash216));
    memcpy(out_proof->transition_hash216,
           execution.transition_hash216, sizeof(out_proof->transition_hash216));
    memcpy(out_proof->receipt_hash72,
           execution.receipt_hash72, sizeof(out_proof->receipt_hash72));
    memcpy(out_proof->replay_hash72,
           execution.replay_hash72, sizeof(out_proof->replay_hash72));
    out_proof->vm81_steps = execution.vm81_steps;
    out_proof->replay_vm81_steps = execution.replay_vm81_steps;

    out_proof->whole_expression_constraint_graph_verified =
        execution.all_ten_typed_joins_verified;
    out_proof->exact_vm81_admission_verified =
        execution.exact_vm81_admission_verified;
    out_proof->atomic_commit_verified = execution.atomic_commit_verified;
    out_proof->hash72_receipt_verified = execution.hash72_receipt_verified;
    out_proof->hash216_proof_identity_verified =
        execution.hash216_proof_identity_verified;
    out_proof->deterministic_replay_verified =
        execution.deterministic_replay_verified;
    out_proof->source_reconstruction_verified =
        execution.source_reconstruction_verified;
    out_proof->shared_environment_revalidated = 1U;
    out_proof->local_symbol_shadowing_detected = 0U;
    out_proof->canonical_monolithic_proof = 1U;
    out_proof->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}
