#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

typedef struct ResolverContext {
    uint32_t calls;
} ResolverContext;

static HHSExactStatus test_index_resolver(
    const char transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    uint8_t lane_role,
    uint8_t lane_position72,
    uint16_t absolute_position216,
    uint8_t glyph,
    uint8_t out_sha256[HHS_EXACT_PASS219_HASH216_SHA256_BYTES],
    void *context
) {
    ResolverContext *ctx = (ResolverContext *)context;
    size_t i;
    if (transition_identity216 == NULL || out_sha256 == NULL || ctx == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (absolute_position216 != (uint16_t)((uint16_t)lane_role * 72U + lane_position72))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_SHA256_BYTES; ++i)
        out_sha256[i] = (uint8_t)(glyph ^ lane_role ^ lane_position72 ^
                                  (uint8_t)absolute_position216 ^ (uint8_t)i ^
                                  (uint8_t)transition_identity216[i % HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]);
    ctx->calls += 1U;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactBigUIntView one_byte_view(const uint8_t *value) {
    HHSExactBigUIntView view;
    view.struct_size = (uint32_t)sizeof(view);
    view.byte_length = 1U;
    view.bytes_be = value;
    return view;
}

static HHSExactUQCELInputV1 make_input(void) {
    static const uint8_t P = 4U;
    static const uint8_t p = 3U;
    static const uint8_t q = 5U;
    static const uint8_t delta = 1U;
    static const uint8_t A = 16U;
    static const uint8_t B = 16U;
    HHSExactUQCELInputV1 input;
    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.P = one_byte_view(&P);
    input.p = one_byte_view(&p);
    input.q = one_byte_view(&q);
    input.delta = one_byte_view(&delta);
    input.A = one_byte_view(&A);
    input.B = one_byte_view(&B);
    input.cell81 = 41U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    assert(hhs_exact_uqcel_source_sha256(input.source_envelope_sha256) == HHS_EXACT_STATUS_OK);
    memset(input.previous_hash72, '0', HHS_EXACT_HASH72_LEN);
    input.previous_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    return input;
}

static HHSExactPass219TranscriptionWitnessV1 make_witness(void) {
    HHSExactPass219RNADomainV1 a;
    HHSExactPass219RNADomainV1 b;
    HHSExactPass219RNAStrandV1 strand;
    HHSExactPass219RNAProgramV1 program;
    HHSExactPass219RNARuleV1 rule;
    HHSExactPass219RNALineageV1 lineage;
    HHSExactPass219TranscriptionWitnessV1 witness;

    memset(&lineage, 0, sizeof(lineage));
    lineage.struct_size = (uint32_t)sizeof(lineage);
    lineage.version = hhs_exact_pass219_rna_rule_version();
    assert(hhs_exact_pass219_native_phase_witness(
        HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &lineage.native_phase) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_coordinate_from_pass189(
        41U, 0, 1U, 0U, &lineage.coordinate) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_trinary_phase_gate(
        lineage.coordinate.trit, &lineage.trinary_gate) == HHS_EXACT_STATUS_OK);
    memset(lineage.predecessor_hash72, '0', HHS_EXACT_HASH72_LEN);
    lineage.predecessor_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    memset(lineage.predecessor_hash216_identity, '1', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    lineage.predecessor_hash216_identity[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    assert(hhs_exact_pass219_rna_domain_init(
        10U, 20U, HHS_EXACT_PHASE_X, 0U, HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD, &a) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_domain_init(
        20U, 10U, HHS_EXACT_PHASE_Y, 1U, HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN, &b) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_strand_init(7U, &strand) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_strand_add_domain(&strand, &a) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_strand_add_domain(&strand, &b) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_program_init(112U, &program) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_rule_init(
        1U, HHS_EXACT_PASS219_RNA_RULE_INHIBITION, 10U, 20U, &rule) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_program_add_rule(&program, &rule) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_program_execute(
        &strand, &program, &lineage, &witness) == HHS_EXACT_STATUS_OK);
    return witness;
}

int main(void) {
    HHSExactPass219TranscriptionWitnessV1 witness = make_witness();
    HHSExactUQCELInputV1 input = make_input();
    HHSExactVM81Frame predecessor;
    HHSExactVM81Frame candidate_frame;
    HHSExactVM81Frame reconstructed;
    HHSExactVM81Frame rolled_back;
    HHSExactVM81Frame committed;
    HHSExactPass219RNAAdmissionCandidateV1 candidate;
    HHSExactPass219RNAAdmissionCandidateV1 tampered;
    HHSExactPass219RNAAdmissionLoweringV1 lowering;
    ResolverContext resolver = {0U};
    uint8_t frontier[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES];
    size_t i;

    assert(hhs_exact_pass219_rna_lower_version() == ((1U << 16) | (12U << 8)));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        predecessor.words[i] = UINT64_C(0xA5A5A5A500000000) ^ (uint64_t)i;
        candidate_frame.words[i] = UINT64_C(0x0102030405060708) ^ (uint64_t)i;
    }
    for (i = 0U; i < sizeof(frontier); ++i)
        frontier[i] = (uint8_t)(i * 7U + 3U);

    assert(hhs_exact_pass219_rna_admission_candidate_from_witness(
        &witness, &predecessor, &candidate_frame, frontier, &candidate) == HHS_EXACT_STATUS_OK);
    assert(candidate.strand_id == witness.strand_id);
    assert(candidate.program_id == witness.program_id);
    assert(candidate.executed_rule_count == witness.executed_rule_count);
    assert(memcmp(candidate.dependency_frontier_sha256, frontier, sizeof(frontier)) == 0);
    assert(memcmp(&candidate.rollback_frame, &predecessor, sizeof(predecessor)) == 0);

    assert(hhs_exact_pass219_rna_candidate_reconstruct(
        &candidate, &reconstructed) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&reconstructed, &candidate_frame, sizeof(candidate_frame)) == 0);
    assert(hhs_exact_pass219_rna_candidate_rollback(
        &candidate, &rolled_back) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&rolled_back, &predecessor, sizeof(predecessor)) == 0);

    assert(hhs_exact_pass219_rna_lower_to_vm81(
        &candidate, &input, test_index_resolver, &resolver,
        &committed, &lowering) == HHS_EXACT_STATUS_OK);
    assert(resolver.calls == HHS_EXACT_PASS219_HASH216_OCCURRENCES);
    assert(memcmp(&committed, &candidate_frame, sizeof(candidate_frame)) == 0);
    assert(lowering.authority_invoked == 1U);
    assert(lowering.frame_committed == 1U);
    assert(lowering.rollback_verified == 1U);
    assert(lowering.strand_id == witness.strand_id);
    assert(lowering.program_id == witness.program_id);
    assert(lowering.admission.transition.resolved_index_count == HHS_EXACT_PASS219_HASH216_OCCURRENCES);
    assert(memcmp(lowering.admission.transition.previous_hash72,
                  input.previous_hash72, HHS_EXACT_HASH72_STRLEN) == 0);

    tampered = candidate;
    tampered.rollback_frame.words[0] ^= UINT64_C(1);
    assert(hhs_exact_pass219_rna_candidate_reconstruct(
        &tampered, &reconstructed) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = candidate;
    tampered.lineage.predecessor_hash72[0] = '1';
    memset(&lowering, 0xA5, sizeof(lowering));
    assert(hhs_exact_pass219_rna_lower_to_vm81(
        &tampered, &input, test_index_resolver, &resolver,
        &committed, &lowering) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(lowering.authority_invoked == 0U);
    assert(lowering.frame_committed == 0U);

    tampered = candidate;
    tampered.lineage.native_phase.left_basis = HHS_EXACT_PHASE_Z;
    assert(hhs_exact_pass219_rna_lower_to_vm81(
        &tampered, &input, test_index_resolver, &resolver,
        &committed, &lowering) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}
