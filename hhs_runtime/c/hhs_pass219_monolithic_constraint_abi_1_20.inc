#include "../include/hhs_pass219_monolithic_constraint_abi_1_20.h"

#include <string.h>

static const char HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE[] =
    "P^2/{(t^3-t=(P\302\263-P/(P\302\262-pq)=(t\302\263-t)/\342\210\206=P\302\262(MOD)(pq))=m^2-m)-"
    "(({{b^4,c^4,c^2-u^72},{c^2,5/u^((s==(b^(2c^2)c^b^4)^2)/(72P^2)),"
    "((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)))},"
    "{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,(72*(pq+xy)))/Bt==AB/P^2==Sqrt[AB])"
    "==(AB/(pq+\342\210\206)-P^2)/(t^3-t)*u^72} where \342\210\206/P=\342\210\232(pq+u\342\201\267\302\262)^x\302\262";

static const char HHS_EXACT_PASS219_MONOLITHIC_SOURCE[] =
    "P^2/{(t^3-t=(P^3-P/(P^2-pq)=(t^3-t)/Delta=P^2(MOD)(pq))=m^2-m)-"
    "(({{b^4,c^4,c^2-u^72},{c^2,5/u^((s==(b^(2c^2)c^b^4)^2)/(72P^2)),"
    "((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)))},"
    "{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,(72*(pq+xy)))/Bt==AB/P^2==Sqrt[AB])"
    "==(AB/(pq+Delta)-P^2)/(t^3-t)*u^72} where Delta/P=Sqrt(pq+u^72)^x^2\n";

static const uint8_t HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SHA256[
    HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES
] = {
    0xacU, 0x14U, 0x37U, 0x98U, 0x14U, 0x6dU, 0x89U, 0xa3U,
    0xfeU, 0x93U, 0x2fU, 0x39U, 0xccU, 0xb4U, 0xd6U, 0x12U,
    0xe4U, 0xfbU, 0x3eU, 0x45U, 0xc4U, 0x71U, 0xabU, 0xc1U,
    0xa8U, 0xbbU, 0xbeU, 0xbbU, 0x0fU, 0x9cU, 0x0aU, 0x6aU
};

static const uint8_t HHS_EXACT_PASS219_MONOLITHIC_MACHINE_SHA256[
    HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES
] = {
    0x7eU, 0xb0U, 0xccU, 0x57U, 0x07U, 0xa4U, 0xa5U, 0x8aU,
    0x5aU, 0x8eU, 0x48U, 0x79U, 0xe0U, 0xe2U, 0xe3U, 0xbdU,
    0xabU, 0x22U, 0xc1U, 0x5fU, 0xe4U, 0x50U, 0x3fU, 0xb3U,
    0xa3U, 0xb0U, 0xe1U, 0x65U, 0x96U, 0x34U, 0x3dU, 0x42U
};

static const uint8_t HHS_EXACT_PASS219_MONOLITHIC_TEX_SHA256[
    HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES
] = {
    0x9fU, 0x22U, 0x38U, 0x98U, 0x1bU, 0xf5U, 0x09U, 0xd2U,
    0x2fU, 0xfeU, 0xbbU, 0x46U, 0x81U, 0x63U, 0x46U, 0xf3U,
    0x89U, 0xfdU, 0x2dU, 0x94U, 0x9cU, 0xcdU, 0x79U, 0x56U,
    0xcdU, 0xe3U, 0x63U, 0x0aU, 0xb2U, 0xb5U, 0x69U, 0x44U
};

typedef struct HHSExactPass219FamilySpanConst {
    uint32_t begin;
    uint32_t end;
    uint32_t mask;
} HHSExactPass219FamilySpanConst;

static const HHSExactPass219FamilySpanConst HHS_EXACT_PASS219_FAMILY_SPANS[
    HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT
] = {
    {6U,   61U,  HHS_EXACT_PASS219_FAMILY_HARMONIC},
    {65U,  233U, HHS_EXACT_PASS219_FAMILY_MATRIX},
    {134U, 261U, HHS_EXACT_PASS219_FAMILY_ORDERED_PHASE},
    {96U,  267U, HHS_EXACT_PASS219_FAMILY_TENSOR_SUBSTITUTION},
    {243U, 264U, HHS_EXACT_PASS219_FAMILY_MODULAR},
    {269U, 285U, HHS_EXACT_PASS219_FAMILY_AB_ROOT},
    {288U, 320U, HHS_EXACT_PASS219_FAMILY_TERMINAL},
    {328U, 353U, HHS_EXACT_PASS219_FAMILY_DELTA_ROOT}
};

_Static_assert(sizeof(HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE) - 1U ==
               HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH,
               "native verbatim monolithic source length drift");
_Static_assert(sizeof(HHS_EXACT_PASS219_MONOLITHIC_SOURCE) - 1U ==
               HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH,
               "machine monolithic HARMONICODE source length drift");
_Static_assert(sizeof(HHS_EXACT_PASS219_FAMILY_SPANS) /
               sizeof(HHS_EXACT_PASS219_FAMILY_SPANS[0]) ==
               HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT,
               "monolithic semantic family count drift");

static uint32_t hhs_exact_pass219_monolithic_version_word(void) {
    return (HHS_EXACT_PASS219_MONOLITHIC_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_MONOLITHIC_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_MONOLITHIC_VERSION_PATCH;
}

static int hhs_exact_pass219_monolithic_hash_text_valid(
    const char *value,
    size_t length
) {
    size_t i;
    if (value == NULL || value[length] != '\0')
        return 0;
    for (i = 0U; i < length; ++i) {
        if (strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static int hhs_exact_pass219_monolithic_proof_hashes_valid(
    const HHSExactPass219MonolithicProofV1 *proof
) {
    uint32_t family;
    if (!hhs_exact_pass219_monolithic_hash_text_valid(
            proof->source_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs_exact_pass219_monolithic_hash_text_valid(
            proof->ast_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs_exact_pass219_monolithic_hash_text_valid(
            proof->constraint_graph_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs_exact_pass219_monolithic_hash_text_valid(
            proof->vmir_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs_exact_pass219_monolithic_hash_text_valid(
            proof->candidate_state_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs_exact_pass219_monolithic_hash_text_valid(
            proof->proof_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs_exact_pass219_monolithic_hash_text_valid(
            proof->receipt_hash72, HHS_EXACT_HASH72_LEN))
        return 0;

    for (family = 0U; family < HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT; ++family) {
        if (!hhs_exact_pass219_monolithic_hash_text_valid(
                proof->family_witness_hash216[family],
                HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN))
            return 0;
    }
    return 1;
}

static int hhs_exact_pass219_monolithic_ordered_xy_bound(
    const HHSExactPass219MonolithicProofV1 *proof
) {
    HHSExactPass219OctonionProductV1 xy;
    HHSExactPass219OctonionProductV1 yx;
    if (hhs_exact_pass219_octonion_validate_state(&proof->octonion_state) !=
        HHS_EXACT_STATUS_OK)
        return 0;
    if (hhs_exact_pass219_octonion_multiply(
            &proof->octonion_state,
            HHS_EXACT_PHASE_X,
            HHS_EXACT_PHASE_Y,
            &xy) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_octonion_multiply(
            &proof->octonion_state,
            HHS_EXACT_PHASE_Y,
            HHS_EXACT_PHASE_X,
            &yx) != HHS_EXACT_STATUS_OK)
        return 0;
    return xy.phase == proof->octonion_state.xy &&
           yx.phase == proof->octonion_state.yx &&
           xy.phase != yx.phase &&
           xy.ordered_tag != yx.ordered_tag;
}

static HHSExactStatus hhs_exact_pass219_monolithic_scan_edge(
    const char *source,
    size_t source_length,
    uint32_t ordinal,
    HHSExactPass219MonolithicEdgeV1 *out_edge
) {
    uint32_t found = 0U;
    uint16_t paren_depth = 0U;
    uint16_t brace_depth = 0U;
    uint16_t bracket_depth = 0U;
    size_t i;

    if (source == NULL || out_edge == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (ordinal >= HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    for (i = 0U; i < source_length; ++i) {
        const char ch = source[i];
        if (ch == '(')
            ++paren_depth;
        else if (ch == ')') {
            if (paren_depth == 0U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            --paren_depth;
        } else if (ch == '{')
            ++brace_depth;
        else if (ch == '}') {
            if (brace_depth == 0U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            --brace_depth;
        } else if (ch == '[')
            ++bracket_depth;
        else if (ch == ']') {
            if (bracket_depth == 0U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            --bracket_depth;
        } else if (ch == '=') {
            const uint8_t is_constraint =
                (uint8_t)(i + 1U < source_length && source[i + 1U] == '=');
            if (found == ordinal) {
                memset(out_edge, 0, sizeof(*out_edge));
                out_edge->struct_size = (uint32_t)sizeof(*out_edge);
                out_edge->version = hhs_exact_pass219_monolithic_version_word();
                out_edge->ordinal = ordinal;
                out_edge->byte_offset = (uint32_t)i;
                out_edge->paren_depth = paren_depth;
                out_edge->brace_depth = brace_depth;
                out_edge->bracket_depth = bracket_depth;
                out_edge->kind = is_constraint
                    ? HHS_EXACT_PASS219_MONOLITHIC_EDGE_CONSTRAINT
                    : HHS_EXACT_PASS219_MONOLITHIC_EDGE_BINDING;
                out_edge->token_length = is_constraint ? 2U : 1U;
                return HHS_EXACT_STATUS_OK;
            }
            ++found;
            if (is_constraint)
                ++i;
        }
    }
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

uint32_t hhs_exact_pass219_monolithic_version(void) {
    return hhs_exact_pass219_monolithic_version_word();
}

HHSExactStatus hhs_exact_pass219_monolithic_descriptor(
    HHSExactPass219MonolithicDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs_exact_pass219_monolithic_version_word();
    out_descriptor->source_length = HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH;
    out_descriptor->native_source_length = HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH;
    out_descriptor->equality_edge_count = HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT;
    out_descriptor->binding_edge_count = HHS_EXACT_PASS219_MONOLITHIC_BINDING_EDGE_COUNT;
    out_descriptor->constraint_edge_count = HHS_EXACT_PASS219_MONOLITHIC_CONSTRAINT_EDGE_COUNT;
    out_descriptor->semantic_family_count = HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT;
    out_descriptor->required_stage_mask = HHS_EXACT_PASS219_STAGE_REQUIRED;
    out_descriptor->required_family_mask = HHS_EXACT_PASS219_FAMILY_REQUIRED;
    out_descriptor->monolithic_admission_only = 1U;
    out_descriptor->source_structure_preserved = 1U;
    out_descriptor->pass159_constraint_graph_required = 1U;
    out_descriptor->vm81_proof_required = 1U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->vm81_mutation_authority = 0U;
    out_descriptor->hash72_commit_authority = 0U;
    memcpy(out_descriptor->native_source_sha256,
           HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SHA256,
           sizeof(out_descriptor->native_source_sha256));
    memcpy(out_descriptor->machine_source_sha256,
           HHS_EXACT_PASS219_MONOLITHIC_MACHINE_SHA256,
           sizeof(out_descriptor->machine_source_sha256));
    memcpy(out_descriptor->frozen_tex_sha256,
           HHS_EXACT_PASS219_MONOLITHIC_TEX_SHA256,
           sizeof(out_descriptor->frozen_tex_sha256));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_monolithic_native_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length != NULL)
        *out_length = HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH;
    if (out_bytes == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(out_bytes,
           HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE,
           HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_monolithic_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length != NULL)
        *out_length = HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH;
    if (out_bytes == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(out_bytes,
           HHS_EXACT_PASS219_MONOLITHIC_SOURCE,
           HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_monolithic_native_edge(
    uint32_t ordinal,
    HHSExactPass219MonolithicEdgeV1 *out_edge
) {
    return hhs_exact_pass219_monolithic_scan_edge(
        HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE,
        HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH,
        ordinal,
        out_edge);
}

HHSExactStatus hhs_exact_pass219_monolithic_edge(
    uint32_t ordinal,
    HHSExactPass219MonolithicEdgeV1 *out_edge
) {
    return hhs_exact_pass219_monolithic_scan_edge(
        HHS_EXACT_PASS219_MONOLITHIC_SOURCE,
        HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH,
        ordinal,
        out_edge);
}

HHSExactStatus hhs_exact_pass219_monolithic_family_span(
    uint32_t family,
    HHSExactPass219MonolithicFamilySpanV1 *out_span
) {
    const HHSExactPass219FamilySpanConst *span;
    if (out_span == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (family >= HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    span = &HHS_EXACT_PASS219_FAMILY_SPANS[family];
    memset(out_span, 0, sizeof(*out_span));
    out_span->struct_size = (uint32_t)sizeof(*out_span);
    out_span->version = hhs_exact_pass219_monolithic_version_word();
    out_span->family = family;
    out_span->byte_begin = span->begin;
    out_span->byte_end = span->end;
    out_span->required_mask_bit = span->mask;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_monolithic_verify_proof(
    const HHSExactPass219MonolithicProofV1 *proof,
    HHSExactPass219MonolithicVerificationV1 *out_verification
) {
    const uint64_t all_edges = HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK;
    uint64_t covered_edges;
    uint64_t overlap_edges;
    int source_valid;
    int ordered_xy_bound;
    int proof_hashes_valid;
    int explicit_failure;
    int unresolved;

    if (proof == NULL || out_verification == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (proof->struct_size < sizeof(*proof) ||
        proof->version != hhs_exact_pass219_monolithic_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    memset(out_verification, 0, sizeof(*out_verification));
    out_verification->struct_size = (uint32_t)sizeof(*out_verification);
    out_verification->version = hhs_exact_pass219_monolithic_version_word();
    out_verification->completed_stage_mask = proof->completed_stage_mask;
    out_verification->resolved_family_mask = proof->resolved_family_mask;
    out_verification->missing_stage_mask =
        HHS_EXACT_PASS219_STAGE_REQUIRED & ~proof->completed_stage_mask;
    out_verification->missing_family_mask =
        HHS_EXACT_PASS219_FAMILY_REQUIRED & ~proof->resolved_family_mask;
    out_verification->edge_satisfied_mask = proof->edge_satisfied_mask & all_edges;
    out_verification->edge_failed_mask = proof->edge_failed_mask & all_edges;
    out_verification->edge_unresolved_mask = proof->edge_unresolved_mask & all_edges;
    out_verification->floating_point_authority = 0U;
    out_verification->vm81_mutation_authority = 0U;
    out_verification->hash72_commit_authority = 0U;

    source_valid = memcmp(
        proof->source_sha256,
        HHS_EXACT_PASS219_MONOLITHIC_MACHINE_SHA256,
        HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES) == 0;
    ordered_xy_bound = hhs_exact_pass219_monolithic_ordered_xy_bound(proof);
    proof_hashes_valid = hhs_exact_pass219_monolithic_proof_hashes_valid(proof);

    out_verification->source_identity_valid = (uint8_t)source_valid;
    out_verification->ordered_xy_bound = (uint8_t)ordered_xy_bound;
    out_verification->proof_identity_valid = (uint8_t)proof_hashes_valid;

    overlap_edges =
        (proof->edge_satisfied_mask & proof->edge_failed_mask) |
        (proof->edge_satisfied_mask & proof->edge_unresolved_mask) |
        (proof->edge_failed_mask & proof->edge_unresolved_mask);
    covered_edges =
        (proof->edge_satisfied_mask |
         proof->edge_failed_mask |
         proof->edge_unresolved_mask) & all_edges;

    explicit_failure =
        !source_valid ||
        !ordered_xy_bound ||
        !proof_hashes_valid ||
        overlap_edges != 0U ||
        (proof->edge_failed_mask & all_edges) != 0U ||
        ((proof->completed_stage_mask & HHS_EXACT_PASS219_STAGE_REQUIRED) ==
             HHS_EXACT_PASS219_STAGE_REQUIRED &&
         (proof->resolved_family_mask & HHS_EXACT_PASS219_FAMILY_REQUIRED) ==
             HHS_EXACT_PASS219_FAMILY_REQUIRED &&
         covered_edges == all_edges &&
         (proof->edge_unresolved_mask & all_edges) == 0U &&
         proof->all_values_exact == 1U &&
         proof->one_candidate_state == 1U &&
         proof->lhs_rhs_equal != 1U);

    unresolved =
        out_verification->missing_stage_mask != 0U ||
        out_verification->missing_family_mask != 0U ||
        covered_edges != all_edges ||
        (proof->edge_unresolved_mask & all_edges) != 0U ||
        proof->all_values_exact != 1U ||
        proof->one_candidate_state != 1U;

    if (explicit_failure) {
        out_verification->decision = HHS_EXACT_PASS219_MONOLITHIC_REJECTED;
        out_verification->monolithic_chain_ok = 0U;
        return HHS_EXACT_STATUS_OK;
    }

    if (unresolved) {
        out_verification->decision = HHS_EXACT_PASS219_MONOLITHIC_UNRESOLVED;
        out_verification->monolithic_chain_ok = 0U;
        return HHS_EXACT_STATUS_OK;
    }

    if ((proof->edge_satisfied_mask & all_edges) != all_edges ||
        proof->lhs_rhs_equal != 1U) {
        out_verification->decision = HHS_EXACT_PASS219_MONOLITHIC_REJECTED;
        out_verification->monolithic_chain_ok = 0U;
        return HHS_EXACT_STATUS_OK;
    }

    out_verification->decision = HHS_EXACT_PASS219_MONOLITHIC_PROVEN;
    out_verification->monolithic_chain_ok = 1U;
    return HHS_EXACT_STATUS_OK;
}
