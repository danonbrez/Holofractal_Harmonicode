#include "hhs_pass219_inherited_pass206_1_18.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass206CumulativeEnforcementWitnessV1 witness() {
    HHSExactPass206CumulativeEnforcementWitnessV1 w{};
    w.struct_size = static_cast<uint32_t>(sizeof(w));
    w.version = hhs_exact_pass219_inherited_pass206_version();
    w.enforcement_admitted = 1U;
    w.frozen_core_count = 10U;
    w.approved_successor_count = 1U;
    w.canonical_mutation_authority_count = 1U;
    w.canonical_hash72_commit_stream_count = 1U;
    w.development_implementation_complete = 1U;
    w.development_final_replay_complete = 1U;
    w.development_completion_receipt_emitted = 1U;
    w.ready_for_pass219_inherited_membrane = 1U;
    w.pass207_successor_preserved = 1U;
    w.dependency_validation_run = 32176768793ULL;
    w.dependency_validation_exact_job = 95840408861ULL;
    w.dependency_validation_synthetic_job = 95840408810ULL;
    w.final_replay_pass206_run = 32177179707ULL;
    w.final_replay_pass206_exact_job = 95841688861ULL;
    w.final_replay_pass206_synthetic_job = 95841688933ULL;
    w.final_replay_cumulative_run = 32177179709ULL;
    w.final_replay_cumulative_exact_job = 95841688968ULL;
    w.final_replay_cumulative_synthetic_job = 95841688796ULL;
    w.completion_validation_run = 32178471795ULL;
    w.completion_validation_exact_job = 95845723288ULL;
    w.completion_validation_synthetic_job = 95845723004ULL;
    std::strcpy(w.grounding_baseline, "918121aeb6d1c55aa8fbd5d60b15f03c4eb22423");
    std::strcpy(w.sealed_predecessor, "2fe770d68f6e1da172d2c7992a90e31d69577b90");
    std::strcpy(w.freeze_checkpoint, "84e057047e6c3da8753ea500a88193f769e49cca");
    std::strcpy(w.development_completion_head, "16d17c1db690116fdc5f5b63ef7a097548685885");
    std::strcpy(w.approved_repair_merge, "284bf652d9635cc0c940f79dfe6aff6f8b787c3c");
    std::strcpy(w.freeze_manifest_sha256, "d60f6191c3fd77d8255e629dc73a7050d4093fe94845ff1bc63bd81d2dfa6da2");
    std::strcpy(w.approved_repair_lineage_sha256, "29d0fa640d9a75b6520738826df3e17b769fc4129db4771c8720b7039b4f3440");
    std::strcpy(w.pre_receipt_matrix_sha256, "1f4da9ca815d99f76c30e26076435cc277c3912ce1658cb5ddb6876f5358406b");
    std::strcpy(w.completion_receipt_sha256, "c25d3db3f6d20aef54092d4fda7663370ec855e8841df691b7ef1bf6d9db2c24");
    std::strcpy(w.post_receipt_matrix_sha256, "ec6aaaeb917abb0bc1f8c1c54e2c721b175e841b603094eb6e687751bb6b79df");
    return w;
}

int main() {
    auto w = witness();
    hhs::rna::InheritedPass206CumulativeEnforcement membrane(w);
    assert(membrane.status() == HHS_EXACT_STATUS_OK);
    assert(membrane.wired());
    const auto& b = membrane.record();
    assert(b.pass_number == 206U);
    assert(b.canonical_main_pending_bound == 1U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);

    w.pass207_successor_preserved = 0U;
    hhs::rna::InheritedPass206CumulativeEnforcement rejected(w);
    assert(rejected.status() == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(!rejected.wired());
    return 0;
}
