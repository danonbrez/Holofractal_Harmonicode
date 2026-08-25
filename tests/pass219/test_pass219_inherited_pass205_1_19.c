#include "hhs_pass219_inherited_pass205_1_19.h"

#include <assert.h>
#include <string.h>

static HHSExactPass205DeterministicContinuationWitnessV1 witness(void) {
    HHSExactPass205DeterministicContinuationWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass205_version();
    w.production_verified = 1U;
    w.cell_count = 81U;
    w.bits_per_cell = 64U;
    w.state_bits = 5184U;
    w.control_count = 243U;
    w.q_address_count = 1259712U;
    w.projection_channel_count = 32U;
    w.canonical_mutation_authority_count = 1U;
    w.canonical_hash72_commit_stream_count = 1U;
    w.q_bijection_complete = 1U;
    w.sparse_full_equivalence_verified = 1U;
    w.parent_bound_hash216_lineage = 1U;
    w.retrieval_exact_rerank = 1U;
    w.accelerator_candidate_only = 1U;
    w.pass206_successor_preserved = 1U;
    w.implementation_pull_request = 149U;
    w.closure_pull_request = 150U;
    w.completion_evidence_pull_request = 151U;
    w.ordered_chain_generations = 73U;
    w.stored_snapshots = 77U;
    w.lineage_edges = 76U;
    w.closure_workflow_run = 30837753796ULL;
    w.closure_validation_job = 91766983285ULL;
    strcpy(w.grounding_baseline, "918121aeb6d1c55aa8fbd5d60b15f03c4eb22423");
    strcpy(w.implementation_merge, "7be753b36d5b4c7a370b6435ddb027b6b05965d8");
    strcpy(w.closure_merge, "c717ab9e0437e1f407bbd3b22ed1fdd14bcd29b6");
    strcpy(w.completion_evidence_merge, "8e6cded890b86e36a2acd2162acf91d1cb4331ac");
    strcpy(w.completion_evidence_head, "97f4e6a3828bd7fb85ad3cf9c2617c3ec99264e7");
    strcpy(w.candidate_merge_tree, "73e3b87d162cfc73a9d6967a153a7cbb17b96e0d");
    strcpy(w.completion_receipt_blob, "7884f6a2b00f1c2254fef5fdf87edca94ac5c6aa");
    strcpy(w.terminal_receipt_hash72, "87rndLmp6DJW!?V9S7ZZcP6xft4GX+(FCMTve!L(BNDEr4v>OoT/HV<RLeqQ4J9P64>HI8N4");
    return w;
}

int main(void) {
    HHSExactPass205DeterministicContinuationWitnessV1 w = witness();
    HHSExactPass219InheritedPass205BindingV1 b;
    assert(hhs_exact_pass219_bind_pass205_deterministic_continuation(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.pass_number == 205U);
    assert(b.vm5184_state_bound == 1U);
    assert(b.g243_control_bound == 1U);
    assert(b.q_bijection_bound == 1U);
    assert(b.projection_channels_bound == 1U);
    assert(b.single_vm81_authority_bound == 1U);
    assert(b.single_hash72_stream_bound == 1U);
    assert(b.hash216_lineage_bound == 1U);
    assert(b.exact_sparse_full_equivalence_bound == 1U);
    assert(b.exact_retrieval_rerank_bound == 1U);
    assert(b.accelerator_candidate_only_bound == 1U);
    assert(b.pass206_successor_bound == 1U);
    assert(b.no_new_mutation_authority_bound == 1U);
    assert(b.no_new_persistence_authority_bound == 1U);
    assert(b.no_new_hash72_clock_bound == 1U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);

    w.accelerator_may_commit_hash72 = 1U;
    assert(hhs_exact_pass219_bind_pass205_deterministic_continuation(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.canonical_hash72_commit_stream_count = 2U;
    assert(hhs_exact_pass219_bind_pass205_deterministic_continuation(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.pass206_successor_preserved = 0U;
    assert(hhs_exact_pass219_bind_pass205_deterministic_continuation(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.closure_merge[0] = '0';
    assert(hhs_exact_pass219_bind_pass205_deterministic_continuation(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.version = 0U;
    assert(hhs_exact_pass219_bind_pass205_deterministic_continuation(&w, &b) == HHS_EXACT_STATUS_VERSION_MISMATCH);
    return 0;
}
