#include <openssl/sha.h>

#include <stddef.h>
#include <stdint.h>
#include <string.h>

_Static_assert(
    HHS_EXACT_PASS220_I078_MANIFOLD_WORDS == HHS_EXACT_VM81_CELLS,
    "I078 manifold must cover all 81 VM81 words"
);

static uint32_t hhs220_i078_version_word(void) {
    return (HHS_EXACT_PASS220_I078_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS220_I078_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS220_I078_VERSION_PATCH;
}

static void hhs220_i078_sha256_hex(
    const uint8_t digest[32],
    char out[HHS_EXACT_PASS220_I078_SHA256_HEX_STRLEN]
) {
    static const char HEX[] = "0123456789abcdef";
    size_t i;
    for (i = 0U; i < 32U; ++i) {
        out[2U * i] = HEX[(digest[i] >> 4U) & 0x0FU];
        out[(2U * i) + 1U] = HEX[digest[i] & 0x0FU];
    }
    out[64] = '\0';
}

static void hhs220_i078_pack_u64_le(
    uint64_t value,
    uint8_t out[8]
) {
    uint32_t i;
    for (i = 0U; i < 8U; ++i)
        out[i] = (uint8_t)((value >> (8U * i)) & UINT64_C(0xFF));
}

static void hhs220_i078_pack_u16_le(
    uint16_t value,
    uint8_t out[2]
) {
    out[0] = (uint8_t)(value & UINT16_C(0xFF));
    out[1] = (uint8_t)((value >> 8U) & UINT16_C(0xFF));
}

static int hhs220_i078_scale1001_witness(
    const HHSExactVM81Frame *candidate,
    uint8_t out_digest[32],
    uint32_t *out_words_verified,
    uint32_t *out_zero_words,
    uint32_t *out_zero_fixed_points
) {
    enum {
        BYTES_PER_WORD = 8 + 1 + 8 + 2,
        MATERIAL_BYTES =
            HHS_EXACT_PASS220_I078_MANIFOLD_WORDS * BYTES_PER_WORD
    };
    uint8_t material[MATERIAL_BYTES];
    size_t cursor = 0U;
    uint32_t words_verified = 0U;
    uint32_t zero_words = 0U;
    uint32_t zero_fixed = 0U;
    uint32_t i;

    if (candidate == NULL || out_digest == NULL ||
        out_words_verified == NULL || out_zero_words == NULL ||
        out_zero_fixed_points == NULL)
        return 0;

    for (i = 0U; i < HHS_EXACT_PASS220_I078_MANIFOLD_WORDS; ++i) {
        uint64_t word = candidate->words[i];
        uint64_t base_q = word / HHS_EXACT_PASS220_I078_SCALE_DENOMINATOR;
        uint16_t remainder =
            (uint16_t)(word % HHS_EXACT_PASS220_I078_SCALE_DENOMINATOR);
        uint64_t quotient_low = word + base_q;
        uint8_t quotient_carry = quotient_low < word ? 1U : 0U;
        uint64_t reconstructed =
            base_q * HHS_EXACT_PASS220_I078_SCALE_DENOMINATOR +
            (uint64_t)remainder;
        uint8_t packed64[8];
        uint8_t packed16[2];

        if (reconstructed != word)
            return 0;

        hhs220_i078_pack_u64_le(word, packed64);
        memcpy(material + cursor, packed64, sizeof(packed64));
        cursor += sizeof(packed64);

        material[cursor++] = quotient_carry;

        hhs220_i078_pack_u64_le(quotient_low, packed64);
        memcpy(material + cursor, packed64, sizeof(packed64));
        cursor += sizeof(packed64);

        hhs220_i078_pack_u16_le(remainder, packed16);
        memcpy(material + cursor, packed16, sizeof(packed16));
        cursor += sizeof(packed16);

        ++words_verified;
        if (word == 0U) {
            ++zero_words;
            if (quotient_carry == 0U &&
                quotient_low == 0U &&
                remainder == 0U)
                ++zero_fixed;
        }
    }

    if (cursor != sizeof(material))
        return 0;
    if (SHA256(material, sizeof(material), out_digest) == NULL)
        return 0;

    *out_words_verified = words_verified;
    *out_zero_words = zero_words;
    *out_zero_fixed_points = zero_fixed;
    return 1;
}

static int hhs220_i078_build_boundary_lineage(
    uint32_t node_id,
    const uint8_t candidate_digest[32],
    const uint8_t scale_digest[32],
    const HHSExactPass220I077ExecutionV1 *i077,
    HHSExactPass220I078BoundaryV1 *out_boundary
) {
    uint8_t change_material[68U];
    uint8_t receipt_material[
        HHS_EXACT_PASS220_I078_HASH216_LEN + 32U + 32U + 16U
    ];
    size_t cursor = 0U;
    uint8_t node_bytes[4];

    if (candidate_digest == NULL || scale_digest == NULL ||
        i077 == NULL || out_boundary == NULL)
        return 0;

    node_bytes[0] = (uint8_t)(node_id & 0xFFU);
    node_bytes[1] = (uint8_t)((node_id >> 8U) & 0xFFU);
    node_bytes[2] = (uint8_t)((node_id >> 16U) & 0xFFU);
    node_bytes[3] = (uint8_t)((node_id >> 24U) & 0xFFU);

    memcpy(change_material, candidate_digest, 32U);
    memcpy(change_material + 32U, scale_digest, 32U);
    memcpy(change_material + 64U, node_bytes, 4U);
    hhs_exact_uqcel_hash72_bytes(
        change_material,
        sizeof(change_material),
        out_boundary->boundary_change_hash72
    );

    memcpy(
        receipt_material + cursor,
        i077->transition_hash216,
        HHS_EXACT_PASS220_I078_HASH216_LEN
    );
    cursor += HHS_EXACT_PASS220_I078_HASH216_LEN;
    memcpy(receipt_material + cursor, candidate_digest, 32U);
    cursor += 32U;
    memcpy(receipt_material + cursor, scale_digest, 32U);
    cursor += 32U;
    memcpy(receipt_material + cursor, node_bytes, 4U);
    cursor += 4U;
    receipt_material[cursor++] = 1U; /* delta_e == 0 */
    receipt_material[cursor++] = 1U; /* psi == 0 */
    receipt_material[cursor++] = 1U; /* omega == true */
    receipt_material[cursor++] = 1U; /* exact scale 1001/1000 */
    receipt_material[cursor++] = 0U; /* host MatrixPower */
    receipt_material[cursor++] = 0U; /* square fallback */
    receipt_material[cursor++] = 0U; /* floating point */
    receipt_material[cursor++] = 0U; /* persistence */
    receipt_material[cursor++] =
        (uint8_t)(HHS_EXACT_PASS220_I078_SCALE_NUMERATOR & 0xFFU);
    receipt_material[cursor++] =
        (uint8_t)((HHS_EXACT_PASS220_I078_SCALE_NUMERATOR >> 8U) & 0xFFU);
    receipt_material[cursor++] =
        (uint8_t)(HHS_EXACT_PASS220_I078_SCALE_DENOMINATOR & 0xFFU);
    receipt_material[cursor++] =
        (uint8_t)((HHS_EXACT_PASS220_I078_SCALE_DENOMINATOR >> 8U) & 0xFFU);

    if (cursor > sizeof(receipt_material))
        return 0;

    hhs_exact_uqcel_hash72_bytes(
        receipt_material,
        cursor,
        out_boundary->boundary_receipt_hash72
    );

    memcpy(
        out_boundary->boundary_hash216,
        i077->receipt_hash72,
        HHS_EXACT_PASS220_I078_HASH72_LEN
    );
    memcpy(
        out_boundary->boundary_hash216 + HHS_EXACT_PASS220_I078_HASH72_LEN,
        out_boundary->boundary_change_hash72,
        HHS_EXACT_PASS220_I078_HASH72_LEN
    );
    memcpy(
        out_boundary->boundary_hash216 +
            (2U * HHS_EXACT_PASS220_I078_HASH72_LEN),
        out_boundary->boundary_receipt_hash72,
        HHS_EXACT_PASS220_I078_HASH72_LEN
    );
    out_boundary->boundary_hash216[HHS_EXACT_PASS220_I078_HASH216_LEN] = '\0';

    hhs_exact_uqcel_hash216_bytes(
        out_boundary->boundary_hash216,
        HHS_EXACT_PASS220_I078_HASH216_LEN,
        out_boundary->boundary_identity216
    );
    return 1;
}

uint32_t hhs_exact_pass220_i078_version(void) {
    return hhs220_i078_version_word();
}

HHSExactStatus hhs_exact_pass220_i078_descriptor(
    HHSExactPass220I078DescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs220_i078_version_word();
    out_descriptor->node_count = HHS_EXACT_PASS220_I077_NODE_COUNT;
    out_descriptor->frame_words = HHS_EXACT_PASS220_I078_MANIFOLD_WORDS;
    out_descriptor->scale_numerator =
        HHS_EXACT_PASS220_I078_SCALE_NUMERATOR;
    out_descriptor->scale_denominator =
        HHS_EXACT_PASS220_I078_SCALE_DENOMINATOR;
    out_descriptor->root_seed_numerator =
        HHS_EXACT_PASS220_I078_ROOT_SEED_NUMERATOR;
    out_descriptor->root_seed_denominator =
        HHS_EXACT_PASS220_I078_ROOT_SEED_DENOMINATOR;
    out_descriptor->i077_binding_required = 1U;
    out_descriptor->downstream_candidate_ingress = 1U;
    out_descriptor->byte_exact_candidate_identity = 1U;
    out_descriptor->uqcel_identity_evaluation = 1U;
    out_descriptor->exact_rational_scale1001 = 1U;
    out_descriptor->zero_energy_fixed_point = 1U;
    out_descriptor->delta_e_zero_required = 1U;
    out_descriptor->psi_zero_required = 1U;
    out_descriptor->omega_true_required = 1U;
    out_descriptor->deterministic_replay_required = 1U;
    out_descriptor->fail_closed_invalid_candidate = 1U;
    out_descriptor->host_matrixpower_authority = 0U;
    out_descriptor->host_square_matrix_fallback_authority = 0U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->numeric_exponent_evaluation_authority = 0U;
    out_descriptor->canonical_vm81_mutation_authority = 0U;
    out_descriptor->canonical_hash72_commit_authority = 0U;
    out_descriptor->canonical_hash216_commit_authority = 0U;
    out_descriptor->canonical_persistence_authority = 0U;
    out_descriptor->external_egress_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass220_i078_reference_candidate(
    uint32_t node_id,
    HHSExactVM81Frame *out_candidate
) {
    HHSExactPass220I077ExecutionV1 i077;
    uint8_t environment_root[32];
    HHSExactStatus status;

    if (out_candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (node_id >= HHS_EXACT_PASS220_I077_NODE_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(&i077, 0, sizeof(i077));
    status = hhs_exact_pass220_i077_execute(node_id, &i077);
    if (status != HHS_EXACT_STATUS_OK ||
        i077.decision != HHS_EXACT_PASS220_I077_VERIFIED)
        return status == HHS_EXACT_STATUS_OK
                   ? HHS_EXACT_STATUS_INVARIANT_FAILURE
                   : status;

    if (!hhs220_i077_build_environment_root(node_id, environment_root))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    hhs220_i077_build_frame(node_id, environment_root, out_candidate);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass220_i078_expand_candidate_boundary(
    uint32_t node_id,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactPass220I078BoundaryV1 *out_boundary
) {
    HHSExactVM81Frame reference;
    HHSExactPass220I077ExecutionV1 i077;
    HHSExactPass220I077ExecutionV1 downstream;
    uint8_t candidate_digest[32];
    uint8_t scale_digest[32];
    uint32_t scale_words = 0U;
    uint32_t zero_words = 0U;
    uint32_t zero_fixed = 0U;
    HHSExactStatus status;

    if (candidate_frame == NULL || out_boundary == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_boundary, 0, sizeof(*out_boundary));
    out_boundary->struct_size = (uint32_t)sizeof(*out_boundary);
    out_boundary->version = hhs220_i078_version_word();
    out_boundary->decision = HHS_EXACT_PASS220_I078_UNRESOLVED;
    out_boundary->reason = HHS_EXACT_PASS220_I078_REASON_NONE;
    out_boundary->node_id = node_id;
    out_boundary->frame_words = HHS_EXACT_PASS220_I078_MANIFOLD_WORDS;
    out_boundary->scale_numerator =
        HHS_EXACT_PASS220_I078_SCALE_NUMERATOR;
    out_boundary->scale_denominator =
        HHS_EXACT_PASS220_I078_SCALE_DENOMINATOR;
    out_boundary->delta_e_numerator = 0;
    out_boundary->delta_e_denominator = 1U;
    out_boundary->psi_numerator = 0;
    out_boundary->psi_denominator = 1U;
    out_boundary->fail_closed_boundary = 1U;
    out_boundary->host_matrixpower_used = 0U;
    out_boundary->square_matrix_fallback_used = 0U;
    out_boundary->floating_point_used = 0U;
    out_boundary->numeric_exponent_evaluated = 0U;
    out_boundary->canonical_state_persisted = 0U;

    if (node_id >= HHS_EXACT_PASS220_I077_NODE_COUNT) {
        out_boundary->decision = HHS_EXACT_PASS220_I078_REJECT;
        out_boundary->reason = HHS_EXACT_PASS220_I078_REASON_NODE_ID;
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }

    memset(&i077, 0, sizeof(i077));
    status = hhs_exact_pass220_i077_execute(node_id, &i077);
    if (status != HHS_EXACT_STATUS_OK ||
        i077.decision != HHS_EXACT_PASS220_I077_VERIFIED) {
        out_boundary->decision = HHS_EXACT_PASS220_I078_REJECT;
        out_boundary->reason = HHS_EXACT_PASS220_I078_REASON_I077_BINDING;
        return status == HHS_EXACT_STATUS_OK
                   ? HHS_EXACT_STATUS_INVARIANT_FAILURE
                   : status;
    }
    out_boundary->i077_execution_verified = 1U;
    memcpy(
        out_boundary->i077_receipt_hash72,
        i077.receipt_hash72,
        sizeof(out_boundary->i077_receipt_hash72)
    );
    memcpy(
        out_boundary->i077_transition_hash216,
        i077.transition_hash216,
        sizeof(out_boundary->i077_transition_hash216)
    );

    status = hhs_exact_pass220_i078_reference_candidate(
        node_id, &reference);
    if (status != HHS_EXACT_STATUS_OK ||
        memcmp(candidate_frame, &reference, sizeof(reference)) != 0) {
        out_boundary->decision = HHS_EXACT_PASS220_I078_REJECT;
        out_boundary->reason =
            HHS_EXACT_PASS220_I078_REASON_CANDIDATE_IDENTITY;
        return status == HHS_EXACT_STATUS_OK
                   ? HHS_EXACT_STATUS_INVARIANT_FAILURE
                   : status;
    }
    out_boundary->candidate_frame_exact = 1U;

    memset(&downstream, 0, sizeof(downstream));
    status = hhs220_i077_admit_and_replay(
        node_id, candidate_frame, &downstream);
    if (status != HHS_EXACT_STATUS_OK ||
        downstream.exact_vm81_admission_verified != 1U ||
        downstream.deterministic_replay_verified != 1U) {
        out_boundary->decision = HHS_EXACT_PASS220_I078_REJECT;
        out_boundary->reason = HHS_EXACT_PASS220_I078_REASON_UQCEL_IDENTITY;
        return status == HHS_EXACT_STATUS_OK
                   ? HHS_EXACT_STATUS_INVARIANT_FAILURE
                   : status;
    }
    out_boundary->uqcel_identity_evaluated = 1U;
    out_boundary->deterministic_replay_verified = 1U;

    if (strcmp(downstream.transition_hash216, i077.transition_hash216) != 0 ||
        strcmp(downstream.receipt_hash72, i077.receipt_hash72) != 0) {
        out_boundary->decision = HHS_EXACT_PASS220_I078_REJECT;
        out_boundary->reason = HHS_EXACT_PASS220_I078_REASON_UQCEL_IDENTITY;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_boundary->uqcel_transition_matches_i077 = 1U;

    if (SHA256(
            (const uint8_t *)candidate_frame,
            sizeof(*candidate_frame),
            candidate_digest) == NULL) {
        out_boundary->decision = HHS_EXACT_PASS220_I078_REJECT;
        out_boundary->reason =
            HHS_EXACT_PASS220_I078_REASON_CANDIDATE_IDENTITY;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    hhs220_i078_sha256_hex(
        candidate_digest, out_boundary->candidate_sha256);

    if (!hhs220_i078_scale1001_witness(
            candidate_frame,
            scale_digest,
            &scale_words,
            &zero_words,
            &zero_fixed)) {
        out_boundary->decision = HHS_EXACT_PASS220_I078_REJECT;
        out_boundary->reason = HHS_EXACT_PASS220_I078_REASON_SCALE_1001;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_boundary->scale_words_verified = scale_words;
    out_boundary->zero_word_count = zero_words;
    out_boundary->zero_fixed_point_words_verified = zero_fixed;
    hhs220_i078_sha256_hex(
        scale_digest, out_boundary->scale_witness_sha256);

    if (scale_words != HHS_EXACT_PASS220_I078_MANIFOLD_WORDS ||
        zero_fixed != zero_words) {
        out_boundary->decision = HHS_EXACT_PASS220_I078_REJECT;
        out_boundary->reason =
            HHS_EXACT_PASS220_I078_REASON_ZERO_FIXED_POINT;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_boundary->exact_scale1001_verified = 1U;
    out_boundary->zero_energy_fixed_point_verified = 1U;
    out_boundary->delta_e_zero = 1U;
    out_boundary->psi_zero = 1U;
    out_boundary->omega_true = 1U;

    if (!hhs220_i078_build_boundary_lineage(
            node_id,
            candidate_digest,
            scale_digest,
            &i077,
            out_boundary)) {
        out_boundary->decision = HHS_EXACT_PASS220_I078_REJECT;
        out_boundary->reason = HHS_EXACT_PASS220_I078_REASON_AUTHORITY;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (out_boundary->i077_execution_verified != 1U ||
        out_boundary->candidate_frame_exact != 1U ||
        out_boundary->uqcel_identity_evaluated != 1U ||
        out_boundary->uqcel_transition_matches_i077 != 1U ||
        out_boundary->exact_scale1001_verified != 1U ||
        out_boundary->zero_energy_fixed_point_verified != 1U ||
        out_boundary->delta_e_zero != 1U ||
        out_boundary->psi_zero != 1U ||
        out_boundary->omega_true != 1U ||
        out_boundary->deterministic_replay_verified != 1U ||
        out_boundary->host_matrixpower_used != 0U ||
        out_boundary->square_matrix_fallback_used != 0U ||
        out_boundary->floating_point_used != 0U ||
        out_boundary->numeric_exponent_evaluated != 0U ||
        out_boundary->canonical_state_persisted != 0U ||
        strlen(out_boundary->boundary_change_hash72) !=
            HHS_EXACT_PASS220_I078_HASH72_LEN ||
        strlen(out_boundary->boundary_receipt_hash72) !=
            HHS_EXACT_PASS220_I078_HASH72_LEN ||
        strlen(out_boundary->boundary_hash216) !=
            HHS_EXACT_PASS220_I078_HASH216_LEN ||
        strlen(out_boundary->boundary_identity216) !=
            HHS_EXACT_PASS220_I078_HASH216_LEN) {
        out_boundary->decision = HHS_EXACT_PASS220_I078_REJECT;
        out_boundary->reason = HHS_EXACT_PASS220_I078_REASON_AUTHORITY;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    out_boundary->decision = HHS_EXACT_PASS220_I078_ADMIT;
    out_boundary->reason = HHS_EXACT_PASS220_I078_REASON_NONE;
    return HHS_EXACT_STATUS_OK;
}
