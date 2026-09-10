#include "hhs_pass219_rml13_native_route_witness_binding_1_26.h"

#include "hhs_pass219_pass159_global_witness_provenance_1_21_10.h"

#include <openssl/sha.h>

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static uint32_t hhs219_rml13_version_word(void) {
    return (HHS_EXACT_PASS219_RML13_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_RML13_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_RML13_VERSION_PATCH;
}

static int hhs219_rml13_nonzero(const uint8_t *bytes, size_t length) {
    size_t i;
    uint8_t aggregate = 0U;
    if (bytes == NULL)
        return 0;
    for (i = 0U; i < length; ++i)
        aggregate = (uint8_t)(aggregate | bytes[i]);
    return aggregate != 0U;
}

static int hhs219_rml13_append(
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

static int hhs219_rml13_append_u32_be(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    uint32_t value
) {
    const uint8_t bytes[4] = {
        (uint8_t)(value >> 24U),
        (uint8_t)(value >> 16U),
        (uint8_t)(value >> 8U),
        (uint8_t)value
    };
    return hhs219_rml13_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static uint64_t hhs219_rml13_word_le(const uint8_t bytes[8]) {
    uint64_t word = 0U;
    uint32_t i;
    for (i = 0U; i < 8U; ++i)
        word |= ((uint64_t)bytes[i]) << (8U * i);
    return word;
}

static void hhs219_rml13_copy_digest_words(
    HHSExactVM81Frame *frame,
    uint32_t first_word,
    const uint8_t digest[HHS_EXACT_PASS219_RML13_SHA256_BYTES]
) {
    uint32_t chunk;
    for (chunk = 0U; chunk < 4U; ++chunk)
        frame->words[first_word + chunk] = hhs219_rml13_word_le(digest + (chunk * 8U));
}

static int hhs219_rml13_witness_valid(
    const HHSExactPass219RML13RouteWitnessV1 *witness
) {
    uint64_t edge_count;
    uint64_t clifford_count;
    if (witness == NULL ||
        witness->struct_size != sizeof(*witness) ||
        witness->version != hhs219_rml13_version_word())
        return 0;

    edge_count = witness->edge_count;
    clifford_count =
        (uint64_t)witness->clifford_full_intertwiner_edges +
        (uint64_t)witness->clifford_chirality_swap_edges +
        (uint64_t)witness->clifford_even_sector_preserving_edges +
        (uint64_t)witness->residual_u72_edges;

    if ((uint64_t)witness->pair_flip_edges + witness->coupled_move_edges != edge_count ||
        (uint64_t)witness->hopf_same_base_edges + witness->hopf_base_moving_edges != edge_count ||
        clifford_count != edge_count ||
        witness->product_geometry_admissible != 1U ||
        witness->all_edges_reversible != 1U ||
        witness->target_reached_exactly != 1U ||
        witness->reverse_restores_source_exactly != 1U ||
        witness->optimizer_transition_authority != 0U ||
        witness->floating_point_authority != 0U)
        return 0;

    return hhs219_rml13_nonzero(witness->route_sha256, sizeof(witness->route_sha256)) &&
           hhs219_rml13_nonzero(witness->selection_sha256, sizeof(witness->selection_sha256)) &&
           hhs219_rml13_nonzero(witness->bundle_sha256, sizeof(witness->bundle_sha256)) &&
           hhs219_rml13_nonzero(witness->source_state_sha256, sizeof(witness->source_state_sha256)) &&
           hhs219_rml13_nonzero(witness->target_state_sha256, sizeof(witness->target_state_sha256));
}

static int hhs219_rml13_build_witness_root(
    const HHSExactPass219RML13RouteWitnessV1 *witness,
    uint8_t out_root[HHS_EXACT_PASS219_RML13_SHA256_BYTES]
) {
    static const uint8_t domain[] =
        "HHS-P219-RML13-NATIVE-ROUTE-WITNESS-V1";
    uint8_t material[512U];
    size_t cursor = 0U;

    if (!hhs219_rml13_witness_valid(witness) || out_root == NULL)
        return 0;

    if (!hhs219_rml13_append(material, sizeof(material), &cursor,
                             domain, sizeof(domain) - 1U) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->version) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->edge_count) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->pair_flip_edges) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->coupled_move_edges) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->hopf_same_base_edges) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->hopf_base_moving_edges) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->clifford_full_intertwiner_edges) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->clifford_chirality_swap_edges) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->clifford_even_sector_preserving_edges) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->residual_u72_edges) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->product_geometry_admissible) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->all_edges_reversible) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->target_reached_exactly) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->reverse_restores_source_exactly) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->optimizer_transition_authority) ||
        !hhs219_rml13_append_u32_be(material, sizeof(material), &cursor, witness->floating_point_authority) ||
        !hhs219_rml13_append(material, sizeof(material), &cursor,
                             witness->route_sha256, sizeof(witness->route_sha256)) ||
        !hhs219_rml13_append(material, sizeof(material), &cursor,
                             witness->selection_sha256, sizeof(witness->selection_sha256)) ||
        !hhs219_rml13_append(material, sizeof(material), &cursor,
                             witness->bundle_sha256, sizeof(witness->bundle_sha256)) ||
        !hhs219_rml13_append(material, sizeof(material), &cursor,
                             witness->source_state_sha256, sizeof(witness->source_state_sha256)) ||
        !hhs219_rml13_append(material, sizeof(material), &cursor,
                             witness->target_state_sha256, sizeof(witness->target_state_sha256)))
        return 0;

    return SHA256(material, cursor, out_root) != NULL &&
           hhs219_rml13_nonzero(out_root, HHS_EXACT_PASS219_RML13_SHA256_BYTES);
}

static int hhs219_rml13_provenance_valid(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance
) {
    return provenance != NULL &&
           provenance->struct_size == sizeof(*provenance) &&
           provenance->pass159_status == 0 &&
           provenance->source_length == HHS_EXACT_PASS219_RML13_SOURCE_BYTES &&
           provenance->source_identity_exact == 1U &&
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
           hhs219_rml13_nonzero(
               provenance->combined_source_sha256,
               sizeof(provenance->combined_source_sha256)) &&
           hhs219_rml13_nonzero(
               provenance->global_symbol_environment_root,
               sizeof(provenance->global_symbol_environment_root));
}

static int hhs219_rml13_build_route_environment_root(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    const uint8_t witness_root[HHS_EXACT_PASS219_RML13_SHA256_BYTES],
    uint8_t out_root[HHS_EXACT_PASS219_RML13_SHA256_BYTES]
) {
    static const uint8_t domain[] =
        "HHS-P219-RML13-PASS169-PREHASH-ENV-V1";
    uint8_t material[160U];
    size_t cursor = 0U;

    if (!hhs219_rml13_provenance_valid(provenance) ||
        witness_root == NULL || out_root == NULL)
        return 0;

    if (!hhs219_rml13_append(material, sizeof(material), &cursor,
                             domain, sizeof(domain) - 1U) ||
        !hhs219_rml13_append(material, sizeof(material), &cursor,
                             provenance->global_symbol_environment_root,
                             sizeof(provenance->global_symbol_environment_root)) ||
        !hhs219_rml13_append(material, sizeof(material), &cursor,
                             provenance->combined_source_sha256,
                             sizeof(provenance->combined_source_sha256)) ||
        !hhs219_rml13_append(material, sizeof(material), &cursor,
                             witness_root, HHS_EXACT_PASS219_RML13_SHA256_BYTES))
        return 0;

    return SHA256(material, cursor, out_root) != NULL &&
           hhs219_rml13_nonzero(out_root, HHS_EXACT_PASS219_RML13_SHA256_BYTES);
}

static void hhs219_rml13_build_candidate_frame(
    const HHSExactPass219RML13RouteWitnessV1 *witness,
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    const uint8_t witness_root[HHS_EXACT_PASS219_RML13_SHA256_BYTES],
    const uint8_t route_environment_root[HHS_EXACT_PASS219_RML13_SHA256_BYTES],
    HHSExactVM81Frame *out_frame
) {
    if (witness == NULL || provenance == NULL || witness_root == NULL ||
        route_environment_root == NULL || out_frame == NULL)
        return;

    memset(out_frame, 0, sizeof(*out_frame));
    out_frame->words[0] = UINT64_C(0x4832524d4c313301); /* H2RML13 + schema byte */
    out_frame->words[1] = (uint64_t)hhs219_rml13_version_word();
    out_frame->words[2] = (uint64_t)witness->edge_count;
    out_frame->words[3] = (uint64_t)witness->pair_flip_edges |
                          ((uint64_t)witness->coupled_move_edges << 32U);
    out_frame->words[4] = (uint64_t)witness->hopf_same_base_edges |
                          ((uint64_t)witness->hopf_base_moving_edges << 32U);
    out_frame->words[5] = (uint64_t)witness->clifford_full_intertwiner_edges |
                          ((uint64_t)witness->clifford_chirality_swap_edges << 32U);
    out_frame->words[6] = (uint64_t)witness->clifford_even_sector_preserving_edges |
                          ((uint64_t)witness->residual_u72_edges << 32U);
    out_frame->words[7] = UINT64_C(0x000000000000000F); /* exact/reversible/read-only witness flags */

    hhs219_rml13_copy_digest_words(out_frame, 8U, witness->route_sha256);
    hhs219_rml13_copy_digest_words(out_frame, 12U, witness->selection_sha256);
    hhs219_rml13_copy_digest_words(out_frame, 16U, witness->bundle_sha256);
    hhs219_rml13_copy_digest_words(out_frame, 20U, witness->source_state_sha256);
    hhs219_rml13_copy_digest_words(out_frame, 24U, witness->target_state_sha256);
    hhs219_rml13_copy_digest_words(out_frame, 28U, witness_root);
    hhs219_rml13_copy_digest_words(out_frame, 32U, route_environment_root);
    hhs219_rml13_copy_digest_words(out_frame, 36U, provenance->combined_source_sha256);
    hhs219_rml13_copy_digest_words(out_frame, 40U, provenance->global_symbol_environment_root);
}

static void hhs219_rml13_set_big_view(
    HHSExactBigUIntView *view,
    const uint8_t *bytes,
    size_t length
) {
    view->struct_size = (uint32_t)sizeof(*view);
    view->byte_length = (uint32_t)length;
    view->bytes_be = bytes;
}

static HHSExactStatus hhs219_rml13_admit_and_replay(
    const HHSExactVM81Frame *candidate,
    HHSExactUQCELAdmissionV1 *out_admission,
    HHSExactUQCELAdmissionV1 *out_replay
) {
    static const uint8_t P_BYTES[] = {0x1eU};
    static const uint8_t P_LOWER_BYTES[] = {0x1dU};
    static const uint8_t Q_BYTES[] = {0x1fU};
    static const uint8_t DELTA_BYTES[] = {0x01U};
    static const uint8_t COMPAT_P2_BYTES[] = {0x03U, 0x84U};
    HHSExactUQCELInputV1 input;
    HHSExactVM81Frame committed;
    HHSExactVM81Frame replay_committed;
    uint8_t uqcel_source_sha256[HHS_EXACT_UQCEL_SOURCE_SHA256_BYTES];
    HHSExactStatus status;

    if (candidate == NULL || out_admission == NULL || out_replay == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(&input, 0, sizeof(input));
    memset(&committed, 0, sizeof(committed));
    memset(&replay_committed, 0, sizeof(replay_committed));
    memset(out_admission, 0, sizeof(*out_admission));
    memset(out_replay, 0, sizeof(*out_replay));

    status = hhs_exact_uqcel_source_sha256(uqcel_source_sha256);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    hhs219_rml13_set_big_view(&input.P, P_BYTES, sizeof(P_BYTES));
    hhs219_rml13_set_big_view(&input.p, P_LOWER_BYTES, sizeof(P_LOWER_BYTES));
    hhs219_rml13_set_big_view(&input.q, Q_BYTES, sizeof(Q_BYTES));
    hhs219_rml13_set_big_view(&input.delta, DELTA_BYTES, sizeof(DELTA_BYTES));
    hhs219_rml13_set_big_view(&input.A, COMPAT_P2_BYTES, sizeof(COMPAT_P2_BYTES));
    hhs219_rml13_set_big_view(&input.B, COMPAT_P2_BYTES, sizeof(COMPAT_P2_BYTES));
    input.cell81 = 0U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    memcpy(input.source_envelope_sha256, uqcel_source_sha256, sizeof(uqcel_source_sha256));
    memset(input.previous_hash72,
           (unsigned char)HHS_EXACT_HASH72_ALPHABET[0], HHS_EXACT_HASH72_LEN);
    input.previous_hash72[HHS_EXACT_HASH72_LEN] = '\0';

    status = hhs_exact_vm81_admit_uqcel(
        &input, candidate, &committed, out_admission);
    if (status != HHS_EXACT_STATUS_OK ||
        out_admission->decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        out_admission->frame_committed != 1U ||
        memcmp(candidate, &committed, sizeof(committed)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_vm81_admit_uqcel(
        &input, candidate, &replay_committed, out_replay);
    if (status != HHS_EXACT_STATUS_OK ||
        out_replay->decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
        out_replay->frame_committed != 1U ||
        memcmp(candidate, &replay_committed, sizeof(replay_committed)) != 0 ||
        memcmp(&committed, &replay_committed, sizeof(committed)) != 0 ||
        strcmp(out_admission->change_hash72, out_replay->change_hash72) != 0 ||
        strcmp(out_admission->receipt_hash72, out_replay->receipt_hash72) != 0 ||
        strcmp(out_admission->hash216_triplet, out_replay->hash216_triplet) != 0 ||
        strcmp(out_admission->hash216_identity, out_replay->hash216_identity) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

uint32_t hhs_exact_pass219_rml13_version(void) {
    return hhs219_rml13_version_word();
}

HHSExactStatus hhs_exact_pass219_rml13_bind_route_pre_hash(
    const uint8_t *source_bytes,
    size_t source_length,
    const HHSExactPass219RML13RouteWitnessV1 *route_witness,
    HHSExactPass219RML13BindingV1 *out_binding
) {
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 provenance;
    HHSExactUQCELAdmissionV1 admission;
    HHSExactUQCELAdmissionV1 replay;
    HHSExactVM81Frame candidate;
    uint8_t witness_root[HHS_EXACT_PASS219_RML13_SHA256_BYTES];
    uint8_t route_environment_root[HHS_EXACT_PASS219_RML13_SHA256_BYTES];
    uint8_t frame_bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t frame_length = 0U;
    HHSExactStatus status;

    if (source_bytes == NULL || route_witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs219_rml13_version_word();
    out_binding->decision = HHS_EXACT_PASS219_RML13_UNRESOLVED;
    out_binding->reason = HHS_EXACT_PASS219_RML13_REASON_SOURCE_PROVENANCE;
    out_binding->single_vm81_commit_authority_preserved = 1U;
    out_binding->optimizer_transition_authority = 0U;
    out_binding->floating_point_authority = 0U;
    out_binding->hash216_persistence_authority = 0U;
    out_binding->scalar_projection_substitution_authority = 0U;
    out_binding->inherited_uqcel_receipt_material_frozen = 1U;
    out_binding->inherited_receipt_hash72_directly_bound_to_route_witness = 0U;

    if (source_length != HHS_EXACT_PASS219_RML13_SOURCE_BYTES) {
        out_binding->decision = HHS_EXACT_PASS219_RML13_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    memset(&provenance, 0, sizeof(provenance));
    status = hhs_exact_pass219_pass159_global_witness_produce(
        source_bytes, source_length, &provenance);
    if (status != HHS_EXACT_STATUS_OK || !hhs219_rml13_provenance_valid(&provenance)) {
        out_binding->decision = HHS_EXACT_PASS219_RML13_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->source_provenance_verified = 1U;

    out_binding->reason = HHS_EXACT_PASS219_RML13_REASON_ROUTE_WITNESS;
    if (!hhs219_rml13_witness_valid(route_witness) ||
        !hhs219_rml13_build_witness_root(route_witness, witness_root) ||
        !hhs219_rml13_build_route_environment_root(
            &provenance, witness_root, route_environment_root)) {
        out_binding->decision = HHS_EXACT_PASS219_RML13_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->route_witness_verified = 1U;
    out_binding->witness_serialization_exact = 1U;
    memcpy(out_binding->witness_root_sha256, witness_root, sizeof(witness_root));
    memcpy(out_binding->route_environment_root_sha256,
           route_environment_root, sizeof(route_environment_root));

    out_binding->edge_count = route_witness->edge_count;
    out_binding->pair_flip_edges = route_witness->pair_flip_edges;
    out_binding->coupled_move_edges = route_witness->coupled_move_edges;
    out_binding->hopf_same_base_edges = route_witness->hopf_same_base_edges;
    out_binding->hopf_base_moving_edges = route_witness->hopf_base_moving_edges;
    out_binding->clifford_full_intertwiner_edges = route_witness->clifford_full_intertwiner_edges;
    out_binding->clifford_chirality_swap_edges = route_witness->clifford_chirality_swap_edges;
    out_binding->clifford_even_sector_preserving_edges = route_witness->clifford_even_sector_preserving_edges;
    out_binding->residual_u72_edges = route_witness->residual_u72_edges;

    out_binding->reason = HHS_EXACT_PASS219_RML13_REASON_PREHASH_FRAME;
    hhs219_rml13_build_candidate_frame(
        route_witness, &provenance, witness_root, route_environment_root, &candidate);
    status = hhs_exact_vm81_frame_export_le(
        &candidate, frame_bytes, sizeof(frame_bytes), &frame_length);
    if (status != HHS_EXACT_STATUS_OK || frame_length != HHS_EXACT_VM81_FRAME_BYTES ||
        SHA256(frame_bytes, frame_length, out_binding->candidate_frame_sha256) == NULL) {
        out_binding->decision = HHS_EXACT_PASS219_RML13_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->witness_root_embedded_pre_hash = 1U;

    out_binding->reason = HHS_EXACT_PASS219_RML13_REASON_VM81_ADMISSION;
    status = hhs219_rml13_admit_and_replay(&candidate, &admission, &replay);
    if (status != HHS_EXACT_STATUS_OK) {
        out_binding->decision = HHS_EXACT_PASS219_RML13_REJECTED;
        return status;
    }

    out_binding->candidate_frame_committed = 1U;
    out_binding->vm5184_address = admission.vm5184_address;
    memcpy(out_binding->change_hash72, admission.change_hash72,
           sizeof(out_binding->change_hash72));
    memcpy(out_binding->receipt_hash72, admission.receipt_hash72,
           sizeof(out_binding->receipt_hash72));
    memcpy(out_binding->replay_hash72, replay.receipt_hash72,
           sizeof(out_binding->replay_hash72));
    memcpy(out_binding->hash216_triplet, admission.hash216_triplet,
           sizeof(out_binding->hash216_triplet));
    memcpy(out_binding->transition_hash216, admission.hash216_identity,
           sizeof(out_binding->transition_hash216));
    out_binding->route_change_hash72_bound_to_witness = 1U;
    out_binding->route_hash216_identity_bound_to_witness = 1U;

    out_binding->reason = HHS_EXACT_PASS219_RML13_REASON_REPLAY;
    if (strcmp(out_binding->change_hash72, replay.change_hash72) != 0 ||
        strcmp(out_binding->receipt_hash72, out_binding->replay_hash72) != 0 ||
        strcmp(out_binding->hash216_triplet, replay.hash216_triplet) != 0 ||
        strcmp(out_binding->transition_hash216, replay.hash216_identity) != 0) {
        out_binding->decision = HHS_EXACT_PASS219_RML13_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->deterministic_replay_verified = 1U;

    out_binding->reason = HHS_EXACT_PASS219_RML13_REASON_AUTHORITY;
    if (out_binding->source_provenance_verified != 1U ||
        out_binding->route_witness_verified != 1U ||
        out_binding->witness_serialization_exact != 1U ||
        out_binding->witness_root_embedded_pre_hash != 1U ||
        out_binding->candidate_frame_committed != 1U ||
        out_binding->deterministic_replay_verified != 1U ||
        out_binding->route_change_hash72_bound_to_witness != 1U ||
        out_binding->route_hash216_identity_bound_to_witness != 1U ||
        out_binding->inherited_uqcel_receipt_material_frozen != 1U ||
        out_binding->inherited_receipt_hash72_directly_bound_to_route_witness != 0U ||
        out_binding->single_vm81_commit_authority_preserved != 1U ||
        out_binding->optimizer_transition_authority != 0U ||
        out_binding->floating_point_authority != 0U ||
        out_binding->hash216_persistence_authority != 0U ||
        out_binding->scalar_projection_substitution_authority != 0U) {
        out_binding->decision = HHS_EXACT_PASS219_RML13_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_binding->reason = HHS_EXACT_PASS219_RML13_REASON_NONE;
    out_binding->decision = HHS_EXACT_PASS219_RML13_VERIFIED;
    return HHS_EXACT_STATUS_OK;
}
