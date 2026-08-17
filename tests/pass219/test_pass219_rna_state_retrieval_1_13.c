#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static HHSExactPass219RNAPriorStateIdentityV1 make_identity(void) {
    HHSExactPass219RNAPriorStateIdentityV1 identity;
    size_t i;
    memset(&identity, 0, sizeof(identity));
    identity.struct_size = (uint32_t)sizeof(identity);
    identity.version = hhs_exact_pass219_rna_retrieval_version();
    memset(identity.program_hash216, '2', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    identity.program_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    memset(identity.predecessor_state_hash216, '1', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    identity.predecessor_state_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    memset(identity.predecessor_hash72, '0', HHS_EXACT_HASH72_LEN);
    identity.predecessor_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    identity.checkpoint_counter = UINT64_C(48);
    for (i = 0U; i < HHS_EXACT_PASS219_RNA_RETRIEVAL_SHA256_BYTES; ++i) {
        identity.predecessor_hash216_digest_sha256[i] = (uint8_t)(i + 1U);
        identity.retrieval_source_sha256[i] = (uint8_t)(i + 33U);
        identity.authenticated_index_sha256[i] = (uint8_t)(i + 65U);
    }
    for (i = 0U; i < HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES; ++i)
        identity.dependency_frontier_sha256[i] = (uint8_t)(i * 3U + 7U);
    return identity;
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
    assert(hhs_exact_pass219_rna_program_init(113U, &program) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_rule_init(
        1U, HHS_EXACT_PASS219_RNA_RULE_INHIBITION, 10U, 20U, &rule) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_program_add_rule(&program, &rule) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_program_execute(
        &strand, &program, &lineage, &witness) == HHS_EXACT_STATUS_OK);
    return witness;
}

int main(void) {
    HHSExactPass219RNAPriorStateIdentityV1 identity = make_identity();
    HHSExactPass219TranscriptionWitnessV1 witness = make_witness();
    HHSExactVM81Frame reference;
    HHSExactVM81Frame replay;
    HHSExactVM81Frame target;
    HHSExactVM81Frame reconstructed;
    HHSExactPass219RNAPriorStateReferenceSealV1 seal;
    HHSExactPass219RNAIndexedPriorStateV1 indexed;
    HHSExactPass219RNAIndexedPriorStateV1 tampered;
    HHSExactPass219RNAStateRetrievalV1 retrieval;
    HHSExactPass219RNAAdmissionCandidateV1 candidate;
    size_t i;

    assert(hhs_exact_pass219_rna_retrieval_version() == ((1U << 16) | (13U << 8)));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        reference.words[i] = UINT64_C(0x1122334400000000) ^ (uint64_t)i;
        replay.words[i] = reference.words[i];
        target.words[i] = UINT64_C(0x5566778800000000) ^ (uint64_t)i;
    }

    assert(hhs_exact_pass219_rna_reference_seal_from_replay(
        &identity, &reference, &replay, &seal) == HHS_EXACT_STATUS_OK);
    assert(seal.deterministic_replay_verified == 1U);
    assert(hhs_exact_pass219_rna_indexed_prior_state_init(
        &identity, &reference, &indexed) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_state_retrieval_authenticate(
        &indexed, &seal, &retrieval) == HHS_EXACT_STATUS_OK);
    assert(retrieval.classification == HHS_EXACT_RNA_STATE_RETRIEVAL_OK);
    assert(retrieval.reference_authenticated == 1U);
    assert(retrieval.fallback_required == 0U);
    assert(retrieval.index_invalidated == 0U);
    assert(retrieval.identity.checkpoint_counter == UINT64_C(48));
    assert(memcmp(&retrieval.predecessor_frame, &reference, sizeof(reference)) == 0);

    /* Normal continuation consumes the authenticated predecessor directly;
       no Genesis/reference replay frame is an input to this candidate path. */
    assert(hhs_exact_pass219_rna_admission_candidate_from_retrieval(
        &witness, &retrieval, &target, &candidate) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_candidate_reconstruct(
        &candidate, &reconstructed) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&reconstructed, &target, sizeof(target)) == 0);
    assert(memcmp(&candidate.predecessor_frame, &reference, sizeof(reference)) == 0);
    assert(memcmp(candidate.dependency_frontier_sha256,
                  identity.dependency_frontier_sha256,
                  HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES) == 0);

    tampered = indexed;
    tampered.predecessor_frame.words[17] ^= UINT64_C(1);
    assert(hhs_exact_pass219_rna_state_retrieval_authenticate(
        &tampered, &seal, &retrieval) == HHS_EXACT_STATUS_OK);
    assert(retrieval.classification == HHS_EXACT_RNA_STATE_RETRIEVAL_MISMATCH);
    assert(retrieval.fallback_required == 1U);
    assert(retrieval.index_invalidated == 1U);
    assert(hhs_exact_pass219_rna_admission_candidate_from_retrieval(
        &witness, &retrieval, &target, &candidate) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = indexed;
    tampered.identity.authenticated_index_sha256[0] ^= 1U;
    assert(hhs_exact_pass219_rna_state_retrieval_authenticate(
        &tampered, &seal, &retrieval) == HHS_EXACT_STATUS_OK);
    assert(retrieval.classification == HHS_EXACT_RNA_STATE_RETRIEVAL_MISMATCH);
    assert(retrieval.index_invalidated == 1U);

    tampered = indexed;
    assert(hhs_exact_pass219_rna_indexed_prior_state_invalidate(&tampered) == HHS_EXACT_STATUS_OK);
    assert(tampered.available == 0U);
    assert(hhs_exact_pass219_rna_state_retrieval_authenticate(
        &tampered, &seal, &retrieval) == HHS_EXACT_STATUS_OK);
    assert(retrieval.classification == HHS_EXACT_RNA_STATE_RETRIEVAL_UNAVAILABLE);
    assert(retrieval.fallback_required == 1U);
    assert(retrieval.index_invalidated == 0U);

    replay.words[0] ^= UINT64_C(1);
    assert(hhs_exact_pass219_rna_reference_seal_from_replay(
        &identity, &reference, &replay, &seal) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}
