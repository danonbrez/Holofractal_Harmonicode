#include "hhs_runtime_exact_abi.h"

#include <stdio.h>
#include <string.h>

static void fill_hash(char *out, size_t length, char symbol) {
    memset(out, (unsigned char)symbol, length);
    out[length] = '\0';
}

static int build_proof(HHSExactPass219MonolithicProofV1 *proof) {
    HHSExactPass219MonolithicDescriptorV1 descriptor;
    uint32_t family;
    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK)
        return 0;
    memset(proof, 0, sizeof(*proof));
    proof->struct_size = (uint32_t)sizeof(*proof);
    proof->version = hhs_exact_pass219_monolithic_version();
    proof->completed_stage_mask = HHS_EXACT_PASS219_STAGE_REQUIRED;
    proof->resolved_family_mask = HHS_EXACT_PASS219_FAMILY_REQUIRED;
    proof->edge_satisfied_mask = HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK;
    memcpy(proof->source_sha256,
           descriptor.machine_source_sha256,
           HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES);
    proof->all_values_exact = 1U;
    proof->one_candidate_state = 1U;
    proof->lhs_rhs_equal = 1U;
    if (hhs_exact_pass219_octonion_expand(1U, 2U, 3U, 4U, &proof->octonion_state) !=
        HHS_EXACT_STATUS_OK)
        return 0;
    fill_hash(proof->source_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN, '0');
    fill_hash(proof->ast_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN, '1');
    fill_hash(proof->constraint_graph_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN, '2');
    fill_hash(proof->vmir_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN, '3');
    fill_hash(proof->candidate_state_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN, '4');
    fill_hash(proof->proof_hash216, HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN, '5');
    for (family = 0U; family < HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT; ++family)
        fill_hash(proof->family_witness_hash216[family],
                  HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN,
                  HHS_EXACT_HASH72_ALPHABET[6U + family]);
    fill_hash(proof->receipt_hash72, HHS_EXACT_HASH72_LEN, 'a');
    return 1;
}

int main(int argc, char **argv) {
    static const uint32_t expected_offsets[HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT] = {
        11U, 27U, 41U, 55U, 97U, 241U, 267U, 275U, 286U, 335U
    };
    static const uint16_t expected_paren[HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT] = {
        1U, 2U, 2U, 1U, 4U, 1U, 1U, 1U, 0U, 0U
    };
    static const uint16_t expected_brace[HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT] = {
        1U, 1U, 1U, 1U, 3U, 1U, 1U, 1U, 1U, 0U
    };
    static const uint8_t expected_kind[HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT] = {
        HHS_EXACT_PASS219_MONOLITHIC_EDGE_BINDING,
        HHS_EXACT_PASS219_MONOLITHIC_EDGE_BINDING,
        HHS_EXACT_PASS219_MONOLITHIC_EDGE_BINDING,
        HHS_EXACT_PASS219_MONOLITHIC_EDGE_BINDING,
        HHS_EXACT_PASS219_MONOLITHIC_EDGE_CONSTRAINT,
        HHS_EXACT_PASS219_MONOLITHIC_EDGE_CONSTRAINT,
        HHS_EXACT_PASS219_MONOLITHIC_EDGE_CONSTRAINT,
        HHS_EXACT_PASS219_MONOLITHIC_EDGE_CONSTRAINT,
        HHS_EXACT_PASS219_MONOLITHIC_EDGE_CONSTRAINT,
        HHS_EXACT_PASS219_MONOLITHIC_EDGE_BINDING
    };
    HHSExactPass219MonolithicDescriptorV1 descriptor;
    HHSExactPass219MonolithicProofV1 proof;
    HHSExactPass219MonolithicVerificationV1 verification;
    uint8_t source[HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH];
    size_t source_length = 0U;
    uint32_t i;

    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK)
        return 1;
    if (descriptor.source_length != HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH ||
        descriptor.equality_edge_count != HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT ||
        descriptor.binding_edge_count != HHS_EXACT_PASS219_MONOLITHIC_BINDING_EDGE_COUNT ||
        descriptor.constraint_edge_count != HHS_EXACT_PASS219_MONOLITHIC_CONSTRAINT_EDGE_COUNT ||
        descriptor.semantic_family_count != HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT ||
        descriptor.required_stage_mask != HHS_EXACT_PASS219_STAGE_REQUIRED ||
        descriptor.required_family_mask != HHS_EXACT_PASS219_FAMILY_REQUIRED ||
        descriptor.monolithic_admission_only != 1U ||
        descriptor.source_structure_preserved != 1U ||
        descriptor.pass159_constraint_graph_required != 1U ||
        descriptor.vm81_proof_required != 1U ||
        descriptor.floating_point_authority != 0U ||
        descriptor.vm81_mutation_authority != 0U ||
        descriptor.hash72_commit_authority != 0U)
        return 2;

    if (hhs_exact_pass219_monolithic_source(source, sizeof(source), &source_length) !=
            HHS_EXACT_STATUS_OK ||
        source_length != sizeof(source))
        return 3;

    if (argc == 2 && strcmp(argv[1], "--dump-source") == 0) {
        if (fwrite(source, 1U, source_length, stdout) != source_length)
            return 4;
        return 0;
    }

    for (i = 0U; i < HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT; ++i) {
        HHSExactPass219MonolithicEdgeV1 edge;
        if (hhs_exact_pass219_monolithic_edge(i, &edge) != HHS_EXACT_STATUS_OK)
            return 5;
        if (edge.ordinal != i || edge.byte_offset != expected_offsets[i] ||
            edge.paren_depth != expected_paren[i] ||
            edge.brace_depth != expected_brace[i] || edge.bracket_depth != 0U ||
            edge.kind != expected_kind[i] ||
            edge.token_length != (expected_kind[i] == HHS_EXACT_PASS219_MONOLITHIC_EDGE_CONSTRAINT ? 2U : 1U))
            return 6;
    }
    if (hhs_exact_pass219_monolithic_edge(
            HHS_EXACT_PASS219_MONOLITHIC_EDGE_COUNT, NULL) !=
        HHS_EXACT_STATUS_INVALID_ARGUMENT)
        return 7;

    for (i = 0U; i < HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT; ++i) {
        HHSExactPass219MonolithicFamilySpanV1 span;
        if (hhs_exact_pass219_monolithic_family_span(i, &span) != HHS_EXACT_STATUS_OK ||
            span.family != i || span.byte_begin >= span.byte_end ||
            span.byte_end > HHS_EXACT_PASS219_MONOLITHIC_SOURCE_LENGTH ||
            span.required_mask_bit != (UINT32_C(1) << i))
            return 8;
    }

    if (!build_proof(&proof))
        return 9;
    if (hhs_exact_pass219_monolithic_verify_proof(&proof, &verification) !=
            HHS_EXACT_STATUS_OK ||
        verification.decision != HHS_EXACT_PASS219_MONOLITHIC_PROVEN ||
        verification.monolithic_chain_ok != 1U ||
        verification.source_identity_valid != 1U ||
        verification.ordered_xy_bound != 1U ||
        verification.proof_identity_valid != 1U ||
        verification.floating_point_authority != 0U ||
        verification.vm81_mutation_authority != 0U ||
        verification.hash72_commit_authority != 0U)
        return 10;

    if (!build_proof(&proof))
        return 11;
    proof.edge_satisfied_mask &= ~(UINT64_C(1) << 9U);
    proof.edge_unresolved_mask = UINT64_C(1) << 9U;
    if (hhs_exact_pass219_monolithic_verify_proof(&proof, &verification) !=
            HHS_EXACT_STATUS_OK ||
        verification.decision != HHS_EXACT_PASS219_MONOLITHIC_UNRESOLVED ||
        verification.monolithic_chain_ok != 0U)
        return 12;

    if (!build_proof(&proof))
        return 13;
    proof.edge_satisfied_mask &= ~(UINT64_C(1) << 3U);
    proof.edge_failed_mask = UINT64_C(1) << 3U;
    if (hhs_exact_pass219_monolithic_verify_proof(&proof, &verification) !=
            HHS_EXACT_STATUS_OK ||
        verification.decision != HHS_EXACT_PASS219_MONOLITHIC_REJECTED ||
        verification.monolithic_chain_ok != 0U)
        return 14;

    if (!build_proof(&proof))
        return 15;
    proof.source_sha256[0] ^= UINT8_C(1);
    if (hhs_exact_pass219_monolithic_verify_proof(&proof, &verification) !=
            HHS_EXACT_STATUS_OK ||
        verification.decision != HHS_EXACT_PASS219_MONOLITHIC_REJECTED ||
        verification.source_identity_valid != 0U)
        return 16;

    if (!build_proof(&proof))
        return 17;
    proof.completed_stage_mask &= ~HHS_EXACT_PASS219_STAGE_VM81_PROOF;
    if (hhs_exact_pass219_monolithic_verify_proof(&proof, &verification) !=
            HHS_EXACT_STATUS_OK ||
        verification.decision != HHS_EXACT_PASS219_MONOLITHIC_UNRESOLVED ||
        verification.missing_stage_mask != HHS_EXACT_PASS219_STAGE_VM81_PROOF)
        return 18;

    if (!build_proof(&proof))
        return 19;
    proof.lhs_rhs_equal = 0U;
    if (hhs_exact_pass219_monolithic_verify_proof(&proof, &verification) !=
            HHS_EXACT_STATUS_OK ||
        verification.decision != HHS_EXACT_PASS219_MONOLITHIC_REJECTED)
        return 20;

    puts("PASS219_MONOLITHIC_CONSTRAINT_ABI_1_20_OK");
    return 0;
}
