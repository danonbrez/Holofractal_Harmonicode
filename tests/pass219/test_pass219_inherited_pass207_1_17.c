#include "hhs_pass219_inherited_pass207_1_17.h"

#include <assert.h>
#include <string.h>

static HHSExactPass207GPUHyperthreadWitnessV1 witness(void) {
    HHSExactPass207GPUHyperthreadWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass207_version();
    w.runtime_verified = 1U;
    w.vm81_cells = 81U;
    w.logical_hyperthreads_per_cell = 64U;
    w.logical_lanes_per_batch = 5184U;
    w.phase_dimension = 72U;
    w.projection_channels = 32U;
    w.required_operation_count = 7U;
    w.stable_lane_identity = 1U;
    w.lane_phase_bijection_bound = 1U;
    w.disjoint_lane_writes = 1U;
    w.ordered_cell_pack_bound = 1U;
    w.ordered_projection_bound = 1U;
    w.ordered_hydration_bound = 1U;
    w.exact_cpu_oracle_equality_required = 1U;
    w.candidate_only = 1U;
    w.buffer_cache_content_keyed = 1U;
    w.cache_hit_authorizes_mutation = 0U;
    w.stable_vector_ranking_bound = 1U;
    w.gpu_may_commit_hash72 = 0U;
    w.gpu_may_mutate_canonical_state = 0U;
    w.gpu_may_bypass_vm81 = 0U;
    w.parallel_canonical_authorities_allowed = 0U;
    w.physical_completion_order_noncanonical = 1U;
    w.physical_gpu_fail_closed = 1U;
    w.pass205_singleton_vm81_admission_preserved = 1U;
    w.pass208_inherits_pass207 = 1U;
    w.pass219_new_canonical_mutation_authority = 0U;
    w.cxx_mutation_authority = 0U;
    w.direct_gpu_vm81_mutation_authority = 0U;
    w.branch_validation_run = 30915233211ULL;
    w.branch_validation_job = 92011562422ULL;
    strcpy(w.validated_branch_head, "406eee3d68ec6c06017374085a46c9992d5778e3");
    strcpy(w.main_merge_head, "b350afea4f7d5a45ba8b8b0bb9740e40731cdb97");
    strcpy(w.contract_git_blob, "727660f3b48c87a78d7e274a5b71ded1bf6e4910");
    strcpy(w.manifest_git_blob, "2f8bb40210b77430a3e6861338d99d06b2ab5596");
    strcpy(w.driver_header_git_blob, "d73b80f53f8843a8c015ebdd735ee419f0877ae0");
    strcpy(w.driver_source_git_blob, "d812005e5be19383472193a7a9cdc50efbe96277");
    strcpy(w.driver_part1_git_blob, "97bef9b58357f44e4801b35de1cda2fea3a726d3");
    strcpy(w.driver_part2_git_blob, "ca8245293cfecc2d73afc063af512e7ff6322a02");
    strcpy(w.driver_part3_git_blob, "c76665697aa3417a1cc8789c794dcebf0219c282");
    strcpy(w.driver_part4_git_blob, "85f8acf834487ff6dc6fa062bebc509b2ab526b7");
    strcpy(w.driver_part5_git_blob, "dbc87a68e0ecdccceb37bb0f6f99bd9491489a0b");
    strcpy(w.native_bridge_git_blob, "f66249e67b6a70b2e5d6bdd42e57e814043fe4d1");
    strcpy(w.python_bridge_git_blob, "53e409665471f126925e6119f9f20ead3978766b");
    strcpy(w.runtime_git_blob, "66a1f25489cde4748fe034bb4b050aef74942a49");
    strcpy(w.restart_git_blob, "af3c4d8ec508de5f5e99431df22ed65f58021205");
    strcpy(w.validation_workflow_git_blob, "5f6ff36b68cf02ec43b6a65b0493afbb56cee7d4");
    strcpy(w.native_test_git_blob, "326546d25004e5789a526ac83aadb22b17b57c7d");
    strcpy(w.python_test_git_blob, "88ad4fec4f883f284858d4850e429245438fe98d");
    strcpy(w.pass208_main_merge_head, "cbeabffff4e70db6207f8c349dd88ea8b7bd6ea9");
    return w;
}

int main(void) {
    HHSExactPass207GPUHyperthreadWitnessV1 w = witness();
    HHSExactPass219InheritedPass207BindingV1 b;
    assert(hhs_exact_pass219_bind_pass207_gpu_hyperthread_driver(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.pass_number == 207U);
    assert(b.stable_vm5184_lane_dispatch_bound == 1U);
    assert(b.lane_phase_bijection_bound == 1U);
    assert(b.ordered_cell_pack_bound == 1U);
    assert(b.ordered_hydration_bound == 1U);
    assert(b.exact_cpu_oracle_verification_bound == 1U);
    assert(b.content_keyed_cache_bound == 1U);
    assert(b.stable_vector_ranking_bound == 1U);
    assert(b.candidate_only_bound == 1U);
    assert(b.gpu_hash72_commit_forbidden == 1U);
    assert(b.gpu_canonical_mutation_forbidden == 1U);
    assert(b.gpu_vm81_bypass_forbidden == 1U);
    assert(b.pass205_singleton_vm81_admission_bound == 1U);
    assert(b.physical_gpu_fail_closed == 1U);
    assert(b.pass208_successor_bound == 1U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.direct_gpu_vm81_mutation_authority == 0U);
    assert(b.logical_lanes_per_batch == 5184U);
    assert(b.projection_channels == 32U);

    w.gpu_may_commit_hash72 = 1U;
    assert(hhs_exact_pass219_bind_pass207_gpu_hyperthread_driver(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.exact_cpu_oracle_equality_required = 0U;
    assert(hhs_exact_pass219_bind_pass207_gpu_hyperthread_driver(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.pass205_singleton_vm81_admission_preserved = 0U;
    assert(hhs_exact_pass219_bind_pass207_gpu_hyperthread_driver(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.driver_part3_git_blob[0] = '0';
    assert(hhs_exact_pass219_bind_pass207_gpu_hyperthread_driver(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
