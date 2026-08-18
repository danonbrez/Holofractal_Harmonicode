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
    identity.checkpoint_counter = UINT64_C(49);
    for (i = 0U; i < HHS_EXACT_PASS219_RNA_RETRIEVAL_SHA256_BYTES; ++i) {
        identity.predecessor_hash216_digest_sha256[i] = (uint8_t)(i + 1U);
        identity.retrieval_source_sha256[i] = (uint8_t)(i + 33U);
        identity.authenticated_index_sha256[i] = (uint8_t)(i + 65U);
    }
    for (i = 0U; i < HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES; ++i)
        identity.dependency_frontier_sha256[i] = (uint8_t)(i * 5U + 7U);
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
    assert(hhs_exact_pass219_rna_program_init(114U, &program) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_rule_init(
        1U, HHS_EXACT_PASS219_RNA_RULE_INHIBITION, 10U, 20U, &rule) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_program_add_rule(&program, &rule) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_program_execute(
        &strand, &program, &lineage, &witness) == HHS_EXACT_STATUS_OK);
    return witness;
}

static HHSExactPass219RNAStateRetrievalV1 make_authenticated_retrieval(
    const HHSExactPass219RNAPriorStateIdentityV1 *identity,
    const HHSExactVM81Frame *reference,
    HHSExactPass219RNAPriorStateReferenceSealV1 *out_seal,
    HHSExactPass219RNAIndexedPriorStateV1 *out_indexed
) {
    HHSExactPass219RNAStateRetrievalV1 retrieval;
    assert(hhs_exact_pass219_rna_reference_seal_from_replay(
        identity, reference, reference, out_seal) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_indexed_prior_state_init(
        identity, reference, out_indexed) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_state_retrieval_authenticate(
        out_indexed, out_seal, &retrieval) == HHS_EXACT_STATUS_OK);
    assert(retrieval.classification == HHS_EXACT_RNA_STATE_RETRIEVAL_OK);
    return retrieval;
}

int main(void) {
    HHSExactPass219RNAPriorStateIdentityV1 identity = make_identity();
    HHSExactPass219TranscriptionWitnessV1 witness = make_witness();
    HHSExactPass219RNAPriorStateReferenceSealV1 seal;
    HHSExactPass219RNAIndexedPriorStateV1 indexed;
    HHSExactPass219RNAIndexedPriorStateV1 altered;
    HHSExactPass219RNAStateRetrievalV1 retrieval;
    HHSExactPass219RNAStateRetrievalV1 fallback_retrieval;
    HHSExactPass219RNAExecutionPlanV1 plan;
    HHSExactPass219RNAExecutionPlanV1 tampered_plan;
    HHSExactPass219RNAAdmissionCandidateV1 candidate;
    HHSExactVM81Frame reference;
    HHSExactVM81Frame target;
    HHSExactVM81Frame reconstructed;
    uint8_t frontier[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES];
    uint8_t changed_frontier[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES];
    const uint32_t explicit_reasons[] = {
        HHS_EXACT_PASS219_RNA_BYPASS_FIRST_PRINCIPLES_EXPORT,
        HHS_EXACT_PASS219_RNA_BYPASS_REFERENCE_ORACLE,
        HHS_EXACT_PASS219_RNA_BYPASS_ABLATION_OR_BENCHMARK_CONTROL,
        HHS_EXACT_PASS219_RNA_BYPASS_EXPLICITLY_AUTHORIZED_AUDIT
    };
    size_t i;

    assert(hhs_exact_pass219_rna_execution_composer_version() == ((1U << 16) | (14U << 8)));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        reference.words[i] = UINT64_C(0x3141592600000000) ^ (uint64_t)i;
        target.words[i] = UINT64_C(0x2718281800000000) ^ (uint64_t)i;
    }
    memcpy(frontier, identity.dependency_frontier_sha256, sizeof(frontier));
    memcpy(changed_frontier, frontier, sizeof(changed_frontier));
    changed_frontier[7] ^= 1U;

    retrieval = make_authenticated_retrieval(&identity, &reference, &seal, &indexed);

    /* Normal post-Pass218 path selects inherited indexed continuation by default. */
    assert(hhs_exact_pass219_rna_execution_compose(
        &retrieval, frontier, HHS_EXACT_PASS219_RNA_BYPASS_NONE, &plan) == HHS_EXACT_STATUS_OK);
    assert(plan.route == HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_INDEXED_CONTINUATION);
    assert(plan.requested_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_NONE);
    assert(plan.effective_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_NONE);
    assert(plan.indexed_lookup_observed == 1U);
    assert(plan.inherited_indexed_capability_selected == 1U);
    assert(plan.authenticated_predecessor_reused == 1U);
    assert(plan.indexed_reuse_count == 1U);
    assert(plan.genesis_replay_required == 0U);
    assert(plan.genesis_replay_count == 0U);
    assert(plan.current_dependency_frontier_verified == 1U);
    assert(plan.checkpoint_counter == identity.checkpoint_counter);
    assert(hhs_exact_pass219_rna_execution_prepare_candidate(
        &plan, &retrieval, &witness, &target, &candidate) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_candidate_reconstruct(
        &candidate, &reconstructed) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&reconstructed, &target, sizeof(target)) == 0);
    assert(memcmp(&candidate.predecessor_frame, &reference, sizeof(reference)) == 0);

    /* Deliberate first-principles/audit bypasses are typed and preserved in evidence. */
    for (i = 0U; i < sizeof(explicit_reasons) / sizeof(explicit_reasons[0]); ++i) {
        assert(hhs_exact_pass219_rna_execution_compose(
            &retrieval, frontier, explicit_reasons[i], &plan) == HHS_EXACT_STATUS_OK);
        assert(plan.route == HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_GENESIS_REPLAY);
        assert(plan.requested_bypass_reason == explicit_reasons[i]);
        assert(plan.effective_bypass_reason == explicit_reasons[i]);
        assert(plan.inherited_indexed_capability_selected == 0U);
        assert(plan.indexed_reuse_count == 0U);
        assert(plan.genesis_replay_required == 1U);
        assert(plan.genesis_replay_count == 1U);
        assert(hhs_exact_pass219_rna_execution_prepare_candidate(
            &plan, &retrieval, &witness, &target, &candidate) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    /* Dependency drift is scoped; it does not silently authorize whole-history Genesis replay. */
    assert(hhs_exact_pass219_rna_execution_compose(
        &retrieval, changed_frontier, HHS_EXACT_PASS219_RNA_BYPASS_NONE, &plan) == HHS_EXACT_STATUS_OK);
    assert(plan.route == HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_DEPENDENCY_SCOPED_RECOMPUTE);
    assert(plan.effective_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_DEPENDENCY_CHANGED);
    assert(plan.dependency_scoped_recompute_required == 1U);
    assert(plan.unaffected_reuse_preserved == 1U);
    assert(plan.genesis_replay_required == 0U);
    assert(plan.genesis_replay_count == 0U);
    assert(plan.current_dependency_frontier_verified == 0U);
    assert(hhs_exact_pass219_rna_execution_compose(
        &retrieval, changed_frontier, HHS_EXACT_PASS219_RNA_BYPASS_DEPENDENCY_CHANGED, &plan) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_execution_compose(
        &retrieval, frontier, HHS_EXACT_PASS219_RNA_BYPASS_DEPENDENCY_CHANGED, &plan) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    /* Unavailable authenticated predecessor becomes an explicit typed replay fallback. */
    altered = indexed;
    assert(hhs_exact_pass219_rna_indexed_prior_state_invalidate(&altered) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_state_retrieval_authenticate(
        &altered, &seal, &fallback_retrieval) == HHS_EXACT_STATUS_OK);
    assert(fallback_retrieval.classification == HHS_EXACT_RNA_STATE_RETRIEVAL_UNAVAILABLE);
    assert(hhs_exact_pass219_rna_execution_compose(
        &fallback_retrieval, frontier, HHS_EXACT_PASS219_RNA_BYPASS_NONE, &plan) == HHS_EXACT_STATUS_OK);
    assert(plan.route == HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_GENESIS_REPLAY);
    assert(plan.effective_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_UNAVAILABLE_AUTHENTICATED_PREDECESSOR);
    assert(plan.genesis_replay_count == 1U);

    /* Corrupted indexed predecessor is not trusted and becomes typed recovery. */
    altered = indexed;
    altered.predecessor_frame.words[3] ^= UINT64_C(1);
    assert(hhs_exact_pass219_rna_state_retrieval_authenticate(
        &altered, &seal, &fallback_retrieval) == HHS_EXACT_STATUS_OK);
    assert(fallback_retrieval.classification == HHS_EXACT_RNA_STATE_RETRIEVAL_MISMATCH);
    assert(fallback_retrieval.index_invalidated == 1U);
    assert(hhs_exact_pass219_rna_execution_compose(
        &fallback_retrieval, frontier, HHS_EXACT_PASS219_RNA_BYPASS_NONE, &plan) == HHS_EXACT_STATUS_OK);
    assert(plan.route == HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_RECOVERY_RECOMPUTE);
    assert(plan.effective_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_CORRUPTION_RECOVERY);
    assert(plan.recovery_recompute_required == 1U);
    assert(plan.index_invalidated == 1U);
    assert(plan.genesis_replay_count == 0U);

    assert(hhs_exact_pass219_rna_execution_compose(
        &retrieval, frontier, 99U, &plan) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(hhs_exact_pass219_rna_execution_compose(
        &retrieval, frontier, HHS_EXACT_PASS219_RNA_BYPASS_CORRUPTION_RECOVERY, &plan) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(hhs_exact_pass219_rna_execution_compose(
        &retrieval, frontier, HHS_EXACT_PASS219_RNA_BYPASS_NONE, &plan) == HHS_EXACT_STATUS_OK);
    tampered_plan = plan;
    tampered_plan.indexed_reuse_count = 0U;
    assert(hhs_exact_pass219_rna_execution_prepare_candidate(
        &tampered_plan, &retrieval, &witness, &target, &candidate) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}
