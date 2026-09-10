#include "hhs_pass219_rml14_route_bound_receipt_successor_1_27.h"

#include <openssl/sha.h>

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static uint32_t hhs219_rml14_version_word(void) {
    return (HHS_EXACT_PASS219_RML14_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_RML14_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_RML14_VERSION_PATCH;
}

static int hhs219_rml14_append(
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

static int hhs219_rml14_append_u32_be(
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
    return hhs219_rml14_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static int hhs219_rml14_append_u16_be(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    uint16_t value
) {
    const uint8_t bytes[2] = {
        (uint8_t)(value >> 8U),
        (uint8_t)value
    };
    return hhs219_rml14_append(out, capacity, cursor, bytes, sizeof(bytes));
}

static int hhs219_rml14_text_present(
    const char *value,
    size_t length
) {
    size_t i;
    if (value == NULL || value[length] != '\0')
        return 0;
    for (i = 0U; i < length; ++i) {
        if (value[i] == '\0')
            return 0;
    }
    return 1;
}

static int hhs219_rml14_parent_valid(
    const HHSExactPass219RML13BindingV1 *parent
) {
    if (parent == NULL ||
        parent->decision != HHS_EXACT_PASS219_RML13_VERIFIED ||
        parent->source_provenance_verified != 1U ||
        parent->route_witness_verified != 1U ||
        parent->witness_serialization_exact != 1U ||
        parent->witness_root_embedded_pre_hash != 1U ||
        parent->candidate_frame_committed != 1U ||
        parent->deterministic_replay_verified != 1U ||
        parent->route_change_hash72_bound_to_witness != 1U ||
        parent->route_hash216_identity_bound_to_witness != 1U ||
        parent->inherited_uqcel_receipt_material_frozen != 1U ||
        parent->inherited_receipt_hash72_directly_bound_to_route_witness != 0U ||
        parent->single_vm81_commit_authority_preserved != 1U ||
        parent->optimizer_transition_authority != 0U ||
        parent->floating_point_authority != 0U ||
        parent->hash216_persistence_authority != 0U ||
        parent->scalar_projection_substitution_authority != 0U)
        return 0;

    return hhs219_rml14_text_present(
               parent->change_hash72, HHS_EXACT_PASS219_RML14_HASH72_LEN) &&
           hhs219_rml14_text_present(
               parent->receipt_hash72, HHS_EXACT_PASS219_RML14_HASH72_LEN) &&
           hhs219_rml14_text_present(
               parent->hash216_triplet, HHS_EXACT_PASS219_RML14_HASH216_LEN) &&
           hhs219_rml14_text_present(
               parent->transition_hash216, HHS_EXACT_PASS219_RML14_HASH216_LEN);
}

static int hhs219_rml14_build_receipt_material(
    const HHSExactPass219RML13RouteWitnessV1 *witness,
    const HHSExactPass219RML13BindingV1 *parent,
    uint8_t out[HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL],
    size_t *out_length
) {
    static const uint8_t domain[] =
        "HHS-P219-RML14-ROUTE-BOUND-RECEIPT-SUCCESSOR-V1";
    size_t cursor = 0U;

    if (witness == NULL || parent == NULL || out == NULL || out_length == NULL)
        return 0;

    if (!hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, domain, sizeof(domain) - 1U) ||
        !hhs219_rml14_append_u32_be(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                                    &cursor, hhs219_rml14_version_word()) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, parent->witness_root_sha256,
                             HHS_EXACT_PASS219_RML14_SHA256_BYTES) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, parent->route_environment_root_sha256,
                             HHS_EXACT_PASS219_RML14_SHA256_BYTES) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, parent->candidate_frame_sha256,
                             HHS_EXACT_PASS219_RML14_SHA256_BYTES) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, witness->route_sha256,
                             HHS_EXACT_PASS219_RML14_SHA256_BYTES) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, witness->selection_sha256,
                             HHS_EXACT_PASS219_RML14_SHA256_BYTES) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, witness->bundle_sha256,
                             HHS_EXACT_PASS219_RML14_SHA256_BYTES) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, witness->source_state_sha256,
                             HHS_EXACT_PASS219_RML14_SHA256_BYTES) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, witness->target_state_sha256,
                             HHS_EXACT_PASS219_RML14_SHA256_BYTES) ||
        !hhs219_rml14_append_u32_be(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                                    &cursor, witness->edge_count) ||
        !hhs219_rml14_append_u32_be(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                                    &cursor, witness->pair_flip_edges) ||
        !hhs219_rml14_append_u32_be(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                                    &cursor, witness->coupled_move_edges) ||
        !hhs219_rml14_append_u32_be(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                                    &cursor, witness->hopf_same_base_edges) ||
        !hhs219_rml14_append_u32_be(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                                    &cursor, witness->hopf_base_moving_edges) ||
        !hhs219_rml14_append_u32_be(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                                    &cursor, witness->clifford_full_intertwiner_edges) ||
        !hhs219_rml14_append_u32_be(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                                    &cursor, witness->clifford_chirality_swap_edges) ||
        !hhs219_rml14_append_u32_be(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                                    &cursor, witness->clifford_even_sector_preserving_edges) ||
        !hhs219_rml14_append_u32_be(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                                    &cursor, witness->residual_u72_edges) ||
        !hhs219_rml14_append_u16_be(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                                    &cursor, parent->vm5184_address) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, parent->hash216_triplet,
                             HHS_EXACT_PASS219_RML14_HASH72_LEN) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, parent->change_hash72,
                             HHS_EXACT_PASS219_RML14_HASH72_LEN) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, parent->receipt_hash72,
                             HHS_EXACT_PASS219_RML14_HASH72_LEN) ||
        !hhs219_rml14_append(out, HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL,
                             &cursor, parent->transition_hash216,
                             HHS_EXACT_PASS219_RML14_HASH216_LEN))
        return 0;

    *out_length = cursor;
    return 1;
}

uint32_t hhs_exact_pass219_rml14_version(void) {
    return hhs219_rml14_version_word();
}

HHSExactStatus hhs_exact_pass219_rml14_bind_route_receipt_successor(
    const uint8_t *source_bytes,
    size_t source_length,
    const HHSExactPass219RML13RouteWitnessV1 *route_witness,
    HHSExactPass219RML14BindingV1 *out_binding
) {
    HHSExactPass219RML13BindingV1 parent;
    HHSHash216 frozen_parity;
    HHSHash72 successor_receipt;
    HHSHash216 successor_identity;
    uint8_t material[HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL];
    size_t material_length = 0U;
    HHSExactStatus status;

    if (source_bytes == NULL || route_witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_binding, 0, sizeof(*out_binding));
    memset(&parent, 0, sizeof(parent));
    memset(&frozen_parity, 0, sizeof(frozen_parity));
    memset(&successor_receipt, 0, sizeof(successor_receipt));
    memset(&successor_identity, 0, sizeof(successor_identity));
    memset(material, 0, sizeof(material));

    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs219_rml14_version_word();
    out_binding->decision = HHS_EXACT_PASS219_RML14_UNRESOLVED;
    out_binding->reason = HHS_EXACT_PASS219_RML14_REASON_RML13_PARENT;
    out_binding->single_vm81_commit_authority_preserved = 1U;
    out_binding->independent_hash_implementation_used = 0U;
    out_binding->second_vm81_commit_primitive_added = 0U;
    out_binding->optimizer_transition_authority = 0U;
    out_binding->floating_point_authority = 0U;
    out_binding->hash216_persistence_authority = 0U;
    out_binding->scalar_projection_substitution_authority = 0U;

    status = hhs_exact_pass219_rml13_bind_route_pre_hash(
        source_bytes, source_length, route_witness, &parent);
    if (status != HHS_EXACT_STATUS_OK || !hhs219_rml14_parent_valid(&parent)) {
        out_binding->decision = HHS_EXACT_PASS219_RML14_REJECTED;
        return status == HHS_EXACT_STATUS_OK ? HHS_EXACT_STATUS_INVARIANT_FAILURE : status;
    }
    out_binding->rml13_binding_verified = 1U;

    out_binding->reason = HHS_EXACT_PASS219_RML14_REASON_RECEIPT_MATERIAL;
    if (!hhs219_rml14_build_receipt_material(
            route_witness, &parent, material, &material_length) ||
        material_length == 0U ||
        material_length > HHS_EXACT_PASS219_RML14_MAX_RECEIPT_MATERIAL ||
        SHA256(material, material_length, out_binding->receipt_material_sha256) == NULL) {
        out_binding->decision = HHS_EXACT_PASS219_RML14_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->receipt_material_length = (uint32_t)material_length;
    out_binding->receipt_material_exact = 1U;
    out_binding->receipt_material_contains_route_witness_root = 1U;
    out_binding->receipt_material_contains_route_bound_change_hash72 = 1U;

    out_binding->edge_count = parent.edge_count;
    out_binding->pair_flip_edges = parent.pair_flip_edges;
    out_binding->coupled_move_edges = parent.coupled_move_edges;
    out_binding->hopf_same_base_edges = parent.hopf_same_base_edges;
    out_binding->hopf_base_moving_edges = parent.hopf_base_moving_edges;
    out_binding->clifford_full_intertwiner_edges = parent.clifford_full_intertwiner_edges;
    out_binding->clifford_chirality_swap_edges = parent.clifford_chirality_swap_edges;
    out_binding->clifford_even_sector_preserving_edges = parent.clifford_even_sector_preserving_edges;
    out_binding->residual_u72_edges = parent.residual_u72_edges;
    out_binding->vm5184_address = parent.vm5184_address;

    memcpy(out_binding->witness_root_sha256,
           parent.witness_root_sha256, sizeof(out_binding->witness_root_sha256));
    memcpy(out_binding->route_environment_root_sha256,
           parent.route_environment_root_sha256, sizeof(out_binding->route_environment_root_sha256));
    memcpy(out_binding->candidate_frame_sha256,
           parent.candidate_frame_sha256, sizeof(out_binding->candidate_frame_sha256));

    memcpy(out_binding->previous_hash72,
           parent.hash216_triplet, HHS_EXACT_PASS219_RML14_HASH72_LEN);
    out_binding->previous_hash72[HHS_EXACT_PASS219_RML14_HASH72_LEN] = '\0';
    memcpy(out_binding->change_hash72,
           parent.change_hash72, HHS_EXACT_PASS219_RML14_HASH72_STRLEN);
    memcpy(out_binding->frozen_uqcel_receipt_hash72,
           parent.receipt_hash72, HHS_EXACT_PASS219_RML14_HASH72_STRLEN);
    memcpy(out_binding->frozen_rml13_transition_hash216,
           parent.transition_hash216, HHS_EXACT_PASS219_RML14_HASH216_STRLEN);

    out_binding->reason = HHS_EXACT_PASS219_RML14_REASON_CANONICAL_HASH;
    hhs_hash216_compute(
        parent.hash216_triplet,
        HHS_EXACT_PASS219_RML14_HASH216_LEN,
        &frozen_parity);
    out_binding->canonical_hash216_delegate_used = 1U;
    if (strcmp(frozen_parity.value, parent.transition_hash216) != 0) {
        out_binding->decision = HHS_EXACT_PASS219_RML14_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_binding->canonical_hash216_parity_with_frozen_uqcel_verified = 1U;

    hhs_hash72_compute(material, material_length, &successor_receipt);
    out_binding->canonical_hash72_delegate_used = 1U;
    if (!hhs219_rml14_text_present(
            successor_receipt.value, HHS_EXACT_PASS219_RML14_HASH72_LEN)) {
        out_binding->decision = HHS_EXACT_PASS219_RML14_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    memcpy(out_binding->successor_receipt_hash72,
           successor_receipt.value, HHS_EXACT_PASS219_RML14_HASH72_STRLEN);
    out_binding->successor_receipt_hash72_route_bound = 1U;

    memcpy(out_binding->successor_hash216_triplet,
           out_binding->previous_hash72, HHS_EXACT_PASS219_RML14_HASH72_LEN);
    memcpy(out_binding->successor_hash216_triplet + HHS_EXACT_PASS219_RML14_HASH72_LEN,
           out_binding->change_hash72, HHS_EXACT_PASS219_RML14_HASH72_LEN);
    memcpy(out_binding->successor_hash216_triplet + (2U * HHS_EXACT_PASS219_RML14_HASH72_LEN),
           out_binding->successor_receipt_hash72, HHS_EXACT_PASS219_RML14_HASH72_LEN);
    out_binding->successor_hash216_triplet[HHS_EXACT_PASS219_RML14_HASH216_LEN] = '\0';
    out_binding->successor_hash216_triplet_route_bound = 1U;

    hhs_hash216_compute(
        out_binding->successor_hash216_triplet,
        HHS_EXACT_PASS219_RML14_HASH216_LEN,
        &successor_identity);
    if (!hhs219_rml14_text_present(
            successor_identity.value, HHS_EXACT_PASS219_RML14_HASH216_LEN)) {
        out_binding->decision = HHS_EXACT_PASS219_RML14_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    memcpy(out_binding->successor_transition_hash216,
           successor_identity.value, HHS_EXACT_PASS219_RML14_HASH216_STRLEN);
    out_binding->successor_hash216_identity_route_bound = 1U;

    out_binding->frozen_uqcel_receipt_preserved = 1U;
    out_binding->frozen_rml13_transition_preserved = 1U;

    out_binding->reason = HHS_EXACT_PASS219_RML14_REASON_AUTHORITY;
    if (out_binding->rml13_binding_verified != 1U ||
        out_binding->receipt_material_exact != 1U ||
        out_binding->receipt_material_contains_route_witness_root != 1U ||
        out_binding->receipt_material_contains_route_bound_change_hash72 != 1U ||
        out_binding->successor_receipt_hash72_route_bound != 1U ||
        out_binding->successor_hash216_triplet_route_bound != 1U ||
        out_binding->successor_hash216_identity_route_bound != 1U ||
        out_binding->frozen_uqcel_receipt_preserved != 1U ||
        out_binding->frozen_rml13_transition_preserved != 1U ||
        out_binding->canonical_hash72_delegate_used != 1U ||
        out_binding->canonical_hash216_delegate_used != 1U ||
        out_binding->canonical_hash216_parity_with_frozen_uqcel_verified != 1U ||
        out_binding->independent_hash_implementation_used != 0U ||
        out_binding->second_vm81_commit_primitive_added != 0U ||
        out_binding->single_vm81_commit_authority_preserved != 1U ||
        out_binding->optimizer_transition_authority != 0U ||
        out_binding->floating_point_authority != 0U ||
        out_binding->hash216_persistence_authority != 0U ||
        out_binding->scalar_projection_substitution_authority != 0U) {
        out_binding->decision = HHS_EXACT_PASS219_RML14_REJECTED;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_binding->reason = HHS_EXACT_PASS219_RML14_REASON_NONE;
    out_binding->decision = HHS_EXACT_PASS219_RML14_VERIFIED;
    return HHS_EXACT_STATUS_OK;
}
