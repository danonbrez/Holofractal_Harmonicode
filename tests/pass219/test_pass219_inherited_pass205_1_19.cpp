#include "hhs_pass219_inherited_pass205_1_19.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass205DeterministicContinuationWitnessV1 witness() {
    HHSExactPass205DeterministicContinuationWitnessV1 w{};
    w.struct_size = static_cast<uint32_t>(sizeof(w));
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
    std::strcpy(w.grounding_baseline, "918121aeb6d1c55aa8fbd5d60b15f03c4eb22423");
    std::strcpy(w.implementation_merge, "7be753b36d5b4c7a370b6435ddb027b6b05965d8");
    std::strcpy(w.closure_merge, "c717ab9e0437e1f407bbd3b22ed1fdd14bcd29b6");
    std::strcpy(w.completion_evidence_merge, "8e6cded890b86e36a2acd2162acf91d1cb4331ac");
    std::strcpy(w.completion_evidence_head, "97f4e6a3828bd7fb85ad3cf9c2617c3ec99264e7");
    std::strcpy(w.candidate_merge_tree, "73e3b87d162cfc73a9d6967a153a7cbb17b96e0d");
    std::strcpy(w.completion_receipt_blob, "7884f6a2b00f1c2254fef5fdf87edca94ac5c6aa");
    std::strcpy(w.terminal_receipt_hash72, "87rndLmp6DJW!?V9S7ZZcP6xft4GX+(FCMTve!L(BNDEr4v>OoT/HV<RLeqQ4J9P64>HI8N4");
    return w;
}

int main() {
    const auto good = witness();
    const hhs::rna::InheritedPass205DeterministicContinuation wired(good);
    assert(wired.status() == HHS_EXACT_STATUS_OK);
    assert(wired.wired());
    assert(wired.record().pass_number == 205U);
    assert(wired.record().single_vm81_authority_bound == 1U);
    assert(wired.record().single_hash72_stream_bound == 1U);
    assert(wired.record().accelerator_candidate_only_bound == 1U);
    assert(wired.record().pass206_successor_bound == 1U);

    auto bad = witness();
    bad.pass205_new_mutation_authority = 1U;
    const hhs::rna::InheritedPass205DeterministicContinuation rejected(bad);
    assert(rejected.status() == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(!rejected.wired());
    return 0;
}
