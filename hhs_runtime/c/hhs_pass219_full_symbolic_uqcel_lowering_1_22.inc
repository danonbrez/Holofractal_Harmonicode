#include "../include/hhs_pass219_full_symbolic_uqcel_lowering_1_22.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static uint32_t hhs219_i156_version_word(void) {
    return (HHS_EXACT_PASS219_FULL_SYMBOLIC_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_FULL_SYMBOLIC_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_FULL_SYMBOLIC_VERSION_PATCH;
}

static int hhs219_i156_nonzero_bytes(const uint8_t *bytes, size_t length) {
    size_t i;
    if (bytes == NULL)
        return 0;
    for (i = 0U; i < length; ++i) {
        if (bytes[i] != 0U)
            return 1;
    }
    return 0;
}

static int hhs219_i156_big_is_zero(const HHSExactBigUIntView *value) {
    return value != NULL &&
           value->byte_length == 1U &&
           value->bytes_be != NULL &&
           value->bytes_be[0] == 0U;
}

static int hhs219_i156_ratio_valid(
    const HHSExactPass219SignedRatioViewV1 *ratio
) {
    int numerator_zero;
    if (ratio == NULL || ratio->struct_size < sizeof(*ratio))
        return 0;
    if (ratio->sign < -1 || ratio->sign > 1)
        return 0;
    if (!hhs_exact_big_view_valid(
            &ratio->numerator,
            HHS_EXACT_PASS219_FULL_SYMBOLIC_RATIO_MAX_BYTES,
            1) ||
        !hhs_exact_big_view_valid(
            &ratio->denominator,
            HHS_EXACT_PASS219_FULL_SYMBOLIC_RATIO_MAX_BYTES,
            0))
        return 0;
    numerator_zero = hhs219_i156_big_is_zero(&ratio->numerator);
    if ((ratio->sign == 0 && !numerator_zero) ||
        (ratio->sign != 0 && numerator_zero))
        return 0;
    return 1;
}

static int hhs219_i156_ratio_equal(
    const HHSExactPass219SignedRatioViewV1 *left,
    const HHSExactPass219SignedRatioViewV1 *right
) {
    HHSExactBigBuffer lhs;
    HHSExactBigBuffer rhs;

    if (!hhs219_i156_ratio_valid(left) ||
        !hhs219_i156_ratio_valid(right))
        return 0;
    if (left->sign != right->sign)
        return 0;
    if (left->sign == 0)
        return 1;

    if (!hhs_exact_big_mul_view(
            &left->numerator, &right->denominator, &lhs) ||
        !hhs_exact_big_mul_view(
            &right->numerator, &left->denominator, &rhs))
        return 0;

    return hhs_exact_big_equal_raw(
        lhs.bytes, lhs.length, rhs.bytes, rhs.length);
}

static int hhs219_i156_append_u32(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    uint32_t value
) {
    if (out == NULL || cursor == NULL || *cursor > capacity ||
        capacity - *cursor < 4U)
        return 0;
    out[(*cursor)++] = (uint8_t)(value >> 24U);
    out[(*cursor)++] = (uint8_t)(value >> 16U);
    out[(*cursor)++] = (uint8_t)(value >> 8U);
    out[(*cursor)++] = (uint8_t)value;
    return 1;
}

static int hhs219_i156_append_bytes(
    uint8_t *out,
    size_t capacity,
    size_t *cursor,
    const uint8_t *bytes,
    size_t length
) {
    if (out == NULL || cursor == NULL || bytes == NULL ||
        *cursor > capacity || length > capacity - *cursor)
        return 0;
    memcpy(out + *cursor, bytes, length);
    *cursor += length;
    return 1;
}

static int hhs219_i156_hash_ratio(
    const HHSExactPass219SignedRatioViewV1 *ratio,
    char out_hash216[HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_STRLEN]
) {
    uint8_t material[
        (2U * HHS_EXACT_PASS219_FULL_SYMBOLIC_RATIO_MAX_BYTES) + 16U
    ];
    size_t cursor = 0U;

    if (!hhs219_i156_ratio_valid(ratio) || out_hash216 == NULL)
        return 0;

    material[cursor++] = (uint8_t)(ratio->sign + 1);
    if (!hhs219_i156_append_u32(
            material, sizeof(material), &cursor,
            ratio->numerator.byte_length) ||
        !hhs219_i156_append_bytes(
            material, sizeof(material), &cursor,
            ratio->numerator.bytes_be,
            ratio->numerator.byte_length) ||
        !hhs219_i156_append_u32(
            material, sizeof(material), &cursor,
            ratio->denominator.byte_length) ||
        !hhs219_i156_append_bytes(
            material, sizeof(material), &cursor,
            ratio->denominator.bytes_be,
            ratio->denominator.byte_length))
        return 0;

    hhs_exact_uqcel_hash216_bytes(material, cursor, out_hash216);
    return 1;
}

static int hhs219_i156_ordered_phase_valid(
    const HHSExactPass219OctonionStateV1 *state
) {
    HHSExactPass219OctonionProductV1 xy;
    HHSExactPass219OctonionProductV1 yx;

    if (state == NULL ||
        hhs_exact_pass219_octonion_validate_state(state) !=
            HHS_EXACT_STATUS_OK)
        return 0;
    if (hhs_exact_pass219_octonion_multiply(
            state, HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &xy) !=
            HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_octonion_multiply(
            state, HHS_EXACT_PHASE_Y, HHS_EXACT_PHASE_X, &yx) !=
            HHS_EXACT_STATUS_OK)
        return 0;

    return xy.ordered_tag != yx.ordered_tag ||
           xy.phase != yx.phase ||
           xy.orientation != yx.orientation;
}

static int hhs219_i156_hash_family(
    uint32_t family,
    char term_hashes[
        HHS_EXACT_PASS219_FULL_SYMBOLIC_TERM_COUNT
    ][HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_STRLEN],
    const HHSExactPass219OctonionStateV1 *state,
    char out_hash216[HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_STRLEN]
) {
    static const uint8_t FAMILY_TERMS[
        HHS_EXACT_PASS219_FULL_SYMBOLIC_FAMILY_COUNT
    ][6] = {
        {0U, 1U, 2U, 3U, 4U, 0xffU},
        {7U, 0xffU, 0xffU, 0xffU, 0xffU, 0xffU},
        {0xffU, 0xffU, 0xffU, 0xffU, 0xffU, 0xffU},
        {5U, 6U, 7U, 0xffU, 0xffU, 0xffU},
        {8U, 0xffU, 0xffU, 0xffU, 0xffU, 0xffU},
        {9U, 10U, 0xffU, 0xffU, 0xffU, 0xffU},
        {11U, 12U, 0xffU, 0xffU, 0xffU, 0xffU},
        {13U, 14U, 0xffU, 0xffU, 0xffU, 0xffU}
    };
    uint8_t material[1600U];
    size_t cursor = 0U;
    size_t slot;

    if (family >= HHS_EXACT_PASS219_FULL_SYMBOLIC_FAMILY_COUNT ||
        out_hash216 == NULL)
        return 0;

    material[cursor++] = (uint8_t)family;
    if (family == HHS_EXACT_PASS219_MONOLITHIC_FAMILY_ORDERED_PHASE) {
        const uint8_t phases[8] = {
            state->x, state->y, state->z, state->w,
            state->xy, state->yx, state->zw, state->wz
        };
        if (!hhs219_i156_append_bytes(
                material, sizeof(material), &cursor,
                phases, sizeof(phases)))
            return 0;
    } else {
        for (slot = 0U; slot < 6U; ++slot) {
            uint8_t term = FAMILY_TERMS[family][slot];
            if (term == 0xffU)
                break;
            if (!hhs219_i156_append_bytes(
                    material, sizeof(material), &cursor,
                    (const uint8_t *)term_hashes[term],
                    HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_LEN))
                return 0;
        }
    }

    hhs_exact_uqcel_hash216_bytes(material, cursor, out_hash216);
    return 1;
}

uint32_t hhs_exact_pass219_full_symbolic_version(void) {
    return hhs219_i156_version_word();
}

HHSExactStatus hhs_exact_pass219_full_symbolic_descriptor(
    HHSExactPass219FullSymbolicDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs219_i156_version_word();
    out_descriptor->term_count = HHS_EXACT_PASS219_FULL_SYMBOLIC_TERM_COUNT;
    out_descriptor->edge_count = HHS_EXACT_PASS219_FULL_SYMBOLIC_EDGE_COUNT;
    out_descriptor->family_count = HHS_EXACT_PASS219_FULL_SYMBOLIC_FAMILY_COUNT;
    out_descriptor->required_edge_mask =
        HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK;
    out_descriptor->required_family_mask =
        HHS_EXACT_PASS219_FAMILY_REQUIRED;
    out_descriptor->residual_mask_on_complete_lowering = 0U;
    out_descriptor->source_structure_preserved = 1U;
    out_descriptor->all_edges_single_transaction = 1U;
    out_descriptor->pass159_provenance_required = 1U;
    out_descriptor->exact_big_ratio_cross_multiply = 1U;
    out_descriptor->ordered_octonion_state_required = 1U;
    out_descriptor->legacy_v1_full_symbolic_input_sufficient = 0U;
    out_descriptor->candidate_value_producer_included = 0U;
    out_descriptor->vm81_execution_included = 0U;
    out_descriptor->hash72_execution_receipt_included = 0U;
    out_descriptor->deterministic_replay_included = 0U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->vm81_mutation_authority = 0U;
    out_descriptor->hash72_commit_authority = 0U;
    out_descriptor->persistence_mutation_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_full_symbolic_lower(
    const HHSExactPass219FullSymbolicWitnessV1 *witness,
    HHSExactPass219FullSymbolicLoweringV1 *out_lowering
) {
    static const uint8_t EDGE_TERMS[
        HHS_EXACT_PASS219_FULL_SYMBOLIC_EDGE_COUNT
    ][2] = {
        {0U, 1U},
        {1U, 2U},
        {2U, 3U},
        {3U, 4U},
        {5U, 6U},
        {7U, 8U},
        {8U, 9U},
        {9U, 10U},
        {11U, 12U},
        {13U, 14U}
    };
    static const uint32_t EDGE_FAMILY_BITS[
        HHS_EXACT_PASS219_FULL_SYMBOLIC_EDGE_COUNT
    ] = {
        HHS_EXACT_PASS219_FAMILY_HARMONIC,
        HHS_EXACT_PASS219_FAMILY_HARMONIC,
        HHS_EXACT_PASS219_FAMILY_HARMONIC,
        HHS_EXACT_PASS219_FAMILY_HARMONIC,
        HHS_EXACT_PASS219_FAMILY_TENSOR_SUBSTITUTION,
        HHS_EXACT_PASS219_FAMILY_MATRIX |
            HHS_EXACT_PASS219_FAMILY_TENSOR_SUBSTITUTION |
            HHS_EXACT_PASS219_FAMILY_MODULAR,
        HHS_EXACT_PASS219_FAMILY_MODULAR |
            HHS_EXACT_PASS219_FAMILY_AB_ROOT,
        HHS_EXACT_PASS219_FAMILY_AB_ROOT,
        HHS_EXACT_PASS219_FAMILY_TERMINAL,
        HHS_EXACT_PASS219_FAMILY_DELTA_ROOT
    };
    HHSExactPass219MonolithicDescriptorV1 descriptor;
    char term_hashes[
        HHS_EXACT_PASS219_FULL_SYMBOLIC_TERM_COUNT
    ][HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_STRLEN];
    uint8_t candidate_material[1900U];
    size_t candidate_cursor = 0U;
    uint32_t term;
    uint32_t edge;
    uint32_t family;
    int ordered_phase_ok;

    if (out_lowering == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_lowering, 0, sizeof(*out_lowering));
    out_lowering->struct_size = (uint32_t)sizeof(*out_lowering);
    out_lowering->version = hhs219_i156_version_word();
    out_lowering->decision = HHS_EXACT_PASS219_FULL_SYMBOLIC_UNRESOLVED;
    out_lowering->residual_mask = HHS_UQCEL_RESIDUAL_FULL_SOURCE;

    if (witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != hhs219_i156_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) !=
        HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (memcmp(
            witness->source_sha256,
            descriptor.machine_source_sha256,
            HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES) != 0) {
        out_lowering->decision = HHS_EXACT_PASS219_FULL_SYMBOLIC_REJECTED;
        out_lowering->reject_reason =
            HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_SOURCE_IDENTITY;
        return HHS_EXACT_STATUS_OK;
    }
    out_lowering->source_identity_exact = 1U;

    if (!hhs219_i156_nonzero_bytes(
            witness->pass159_provenance_root,
            sizeof(witness->pass159_provenance_root))) {
        out_lowering->decision = HHS_EXACT_PASS219_FULL_SYMBOLIC_REJECTED;
        out_lowering->reject_reason =
            HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_PROVENANCE_ROOT;
        return HHS_EXACT_STATUS_OK;
    }
    out_lowering->provenance_root_bound = 1U;

    memset(term_hashes, 0, sizeof(term_hashes));
    for (term = 0U;
         term < HHS_EXACT_PASS219_FULL_SYMBOLIC_TERM_COUNT;
         ++term) {
        if (!hhs219_i156_ratio_valid(&witness->terms[term]) ||
            !hhs219_i156_hash_ratio(
                &witness->terms[term], term_hashes[term])) {
            out_lowering->decision =
                HHS_EXACT_PASS219_FULL_SYMBOLIC_REJECTED;
            out_lowering->reject_reason =
                HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_RATIO_ENCODING;
            return HHS_EXACT_STATUS_OK;
        }
    }
    out_lowering->all_values_exact = 1U;

    ordered_phase_ok =
        hhs219_i156_ordered_phase_valid(&witness->octonion_state);
    if (!ordered_phase_ok) {
        out_lowering->decision = HHS_EXACT_PASS219_FULL_SYMBOLIC_REJECTED;
        out_lowering->reject_reason =
            HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_ORDERED_PHASE;
        out_lowering->failed_family_mask |=
            HHS_EXACT_PASS219_FAMILY_ORDERED_PHASE;
        return HHS_EXACT_STATUS_OK;
    }
    out_lowering->ordered_xy_yx_bound = 1U;

    for (edge = 0U;
         edge < HHS_EXACT_PASS219_FULL_SYMBOLIC_EDGE_COUNT;
         ++edge) {
        const HHSExactPass219SignedRatioViewV1 *left =
            &witness->terms[EDGE_TERMS[edge][0]];
        const HHSExactPass219SignedRatioViewV1 *right =
            &witness->terms[EDGE_TERMS[edge][1]];
        uint64_t bit = UINT64_C(1) << edge;
        if (hhs219_i156_ratio_equal(left, right)) {
            out_lowering->edge_satisfied_mask |= bit;
        } else {
            out_lowering->edge_failed_mask |= bit;
            out_lowering->failed_family_mask |= EDGE_FAMILY_BITS[edge];
        }
    }

    if (out_lowering->edge_failed_mask != 0U) {
        out_lowering->decision = HHS_EXACT_PASS219_FULL_SYMBOLIC_REJECTED;
        out_lowering->reject_reason =
            HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_EDGE_MISMATCH;
        return HHS_EXACT_STATUS_OK;
    }

    if ((out_lowering->edge_satisfied_mask &
         HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK) !=
        HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK) {
        out_lowering->edge_unresolved_mask =
            HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK &
            ~out_lowering->edge_satisfied_mask;
        return HHS_EXACT_STATUS_OK;
    }

    out_lowering->resolved_family_mask =
        HHS_EXACT_PASS219_FAMILY_REQUIRED;
    out_lowering->residual_mask = 0U;
    out_lowering->one_candidate_state = 1U;
    out_lowering->monolithic_chain_lowered = 1U;

    for (family = 0U;
         family < HHS_EXACT_PASS219_FULL_SYMBOLIC_FAMILY_COUNT;
         ++family) {
        if (!hhs219_i156_hash_family(
                family, term_hashes, &witness->octonion_state,
                out_lowering->family_witness_hash216[family]))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (!hhs219_i156_append_bytes(
            candidate_material, sizeof(candidate_material), &candidate_cursor,
            witness->source_sha256,
            sizeof(witness->source_sha256)) ||
        !hhs219_i156_append_bytes(
            candidate_material, sizeof(candidate_material), &candidate_cursor,
            witness->pass159_provenance_root,
            sizeof(witness->pass159_provenance_root)))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (family = 0U;
         family < HHS_EXACT_PASS219_FULL_SYMBOLIC_FAMILY_COUNT;
         ++family) {
        if (!hhs219_i156_append_bytes(
                candidate_material, sizeof(candidate_material),
                &candidate_cursor,
                (const uint8_t *)
                    out_lowering->family_witness_hash216[family],
                HHS_EXACT_PASS219_FULL_SYMBOLIC_HASH216_LEN))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    hhs_exact_uqcel_hash216_bytes(
        candidate_material, candidate_cursor,
        out_lowering->candidate_state_hash216);

    /*
     * Exact full-symbolic lowering is complete for this witness.  Execution
     * authority is deliberately not inferred here.
     */
    out_lowering->candidate_value_producer_authority = 0U;
    out_lowering->vm81_execution_verified = 0U;
    out_lowering->hash72_execution_receipt_verified = 0U;
    out_lowering->deterministic_replay_verified = 0U;
    out_lowering->floating_point_authority = 0U;
    out_lowering->vm81_mutation_authority = 0U;
    out_lowering->hash72_commit_authority = 0U;
    out_lowering->persistence_mutation_authority = 0U;
    out_lowering->decision = HHS_EXACT_PASS219_FULL_SYMBOLIC_LOWERED;
    out_lowering->reject_reason =
        HHS_EXACT_PASS219_FULL_SYMBOLIC_REASON_NONE;

    return HHS_EXACT_STATUS_OK;
}
