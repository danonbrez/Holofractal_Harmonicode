#include "hhs_pass219_inherited_pass214_1_16.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void copy_text(char *target, size_t size, const char *value) {
    const size_t length = strlen(value);
    assert(length + 1U == size);
    memcpy(target, value, size);
}

static HHSExactPass214BenchmarkAuthorityWitnessV1 witness(void) {
    HHSExactPass214BenchmarkAuthorityWitnessV1 value;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = hhs_exact_pass219_inherited_pass214_version();
    value.terminal_iteration = 8U;
    value.terminal_roots_minted = 1U;
    value.benchmark_authority_promoted = 1U;
    value.pass215_authorized = 1U;
    value.pass213_gates_preserved = 1U;
    value.pass213_live_admission_required_before_canonical_mutation = 1U;
    value.workload_families = 15U;
    value.workload_modes_per_family = 11U;
    value.mode_executions = 165U;
    value.mandatory_ablations = 26U;
    value.benchmark_stage_count = 10U;
    value.pass197_address_comparisons = 1658880U;
    value.pass212_full_hydration_bits = 50388480U;
    value.pass212_full_state_recoveries = 3U;
    value.cross_process_replays = 15U;
    value.semantic_reuse_registry_entries = 306U;
    value.semantic_reuse_remaining_backlog = 1383U;
    value.exact_vm81_kernel_rebound = 1U;
    value.main_closure_run = 31195458960ULL;
    value.semantic_reuse_run = 31259979177ULL;

    copy_text(value.validated_terminal_head, sizeof(value.validated_terminal_head), "fb167f0ae88346c7894d60b794eeba0e1967a971");
    copy_text(value.merge_commit, sizeof(value.merge_commit), "1114a50c677f3f205d5858bc09b1249d3d365842");
    copy_text(value.main_closure_commit, sizeof(value.main_closure_commit), "063bcc1426b5bba106e139cb7dba1c540df090df");
    copy_text(value.main_closure_tree, sizeof(value.main_closure_tree), "9b21320cc72f3c77c79a9d76b083fe8b0c97f9d5");
    copy_text(value.main_closure_artifact_sha256, sizeof(value.main_closure_artifact_sha256), "8b2dc496bb856cc5627f1c66c79ee878b6305a2e5bdc4ff0bec94b0ff1a615c6");
    copy_text(value.repository_scan_root_hash216, sizeof(value.repository_scan_root_hash216), "8d527e0a562e05b0bac6a180cce1601f5808f22e2c1c9e5455b12b024b3d3d6a");
    copy_text(value.optimization_registry_root_hash216, sizeof(value.optimization_registry_root_hash216), "32d73ff8e68fd8893fc347fb4aa97c4c8027b75dfd61bc3dab45aeae44f6a5dc");
    copy_text(value.compatibility_graph_root_hash216, sizeof(value.compatibility_graph_root_hash216), "b229bddea971f76b386b615316a0926473a4f66b37de9e49ec661b85567a6439");
    copy_text(value.workload_corpus_root_hash216, sizeof(value.workload_corpus_root_hash216), "c4f00ab874c2f1daaffd073ff6c0a85113314a4e6c70b5c30474ced43ece1f99");
    copy_text(value.benchmark_method_root_hash216, sizeof(value.benchmark_method_root_hash216), "b1973a3145e370f4a85503dac540a5b9a12f7050bd6ccdb14f11f6a7506c6b0f");
    copy_text(value.compound_evidence_root_hash216, sizeof(value.compound_evidence_root_hash216), "983a947ac2f625b8bdca689d6fc15b270f9ea7b8550c814484a158d96e624361");
    copy_text(value.authority_root_hash216, sizeof(value.authority_root_hash216), "c1d7875acd45f02da75101f5953541b6e1ce8ea3bb2cac39645004ab2509aeb8");
    copy_text(value.pass215_profile_root_hash216, sizeof(value.pass215_profile_root_hash216), "a3079f0f0b94d9fb485970662455482d4dab86e01802ca5bfdef6af3fbb6d85e");
    copy_text(value.pass213_gate_preservation_root_hash216, sizeof(value.pass213_gate_preservation_root_hash216), "214106621723b579ffe4813c74d5df98a7e14387293b8ecc3e1edc81bf066092");
    copy_text(value.compound_benchmark_root_hash216, sizeof(value.compound_benchmark_root_hash216), "3193f1cf30306d193b3d4a19e0670e396f26943c148c29ef45d20ffad456e21b");
    copy_text(value.terminal_receipt_hash72, sizeof(value.terminal_receipt_hash72), "!(KTNH1zFC/ikVVJ1qCp8OKfOX8IoP<O8-/Df(NcNLYbY<<i+ICL5g2luJlws)AOvyX9XvJD");
    copy_text(value.semantic_reuse_head, sizeof(value.semantic_reuse_head), "54295e674d6bae1868bdb66b5d2aff0edaaac1d4");
    copy_text(value.semantic_reuse_tree, sizeof(value.semantic_reuse_tree), "9e28fcb36de76440e2ee5909c2b82c1bf5a4314d");
    copy_text(value.semantic_reuse_artifact_sha256, sizeof(value.semantic_reuse_artifact_sha256), "33a237ee8d76c598656b253f70ecf2a72a285a5e71d165414b6bf938b4f103f8");
    copy_text(value.exact_vm81_kernel_git_blob, sizeof(value.exact_vm81_kernel_git_blob), "81d9699b2d28d5d6a09ea4763653f3ba9eda9e15");
    copy_text(value.vm81_rebind_script_commit, sizeof(value.vm81_rebind_script_commit), "cf18b65bd1e3d7a3dce0081b97e1d4ff89b2c7d0");
    copy_text(value.vm81_rebind_test_commit, sizeof(value.vm81_rebind_test_commit), "2b753167522c0829a4f7e23eb4378d824c82eafe");
    return value;
}

int main(void) {
    HHSExactPass214BenchmarkAuthorityWitnessV1 input = witness();
    HHSExactPass219InheritedPass214BindingV1 output;
    HHSExactStatus status;

    memset(&output, 0, sizeof(output));
    status = hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(output.pass_number == 214U);
    assert(output.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(output.terminal_benchmark_authority_bound == 1U);
    assert(output.eight_root_terminal_closure_bound == 1U);
    assert(output.pass215_profile_authorization_bound == 1U);
    assert(output.semantic_equivalence_reuse_bound == 1U);
    assert(output.exact_vm81_kernel_rebind_bound == 1U);
    assert(output.pass213_gates_preserved == 1U);
    assert(output.runtime_mutation_authority_promoted == 0U);
    assert(output.canonical_mutation_authorized == 0U);
    assert(output.migration_active == 0U);
    assert(output.cxx_mutation_authority == 0U);
    assert(output.vm81_mutation_authority == 0U);
    assert(output.workload_families == 15U);
    assert(output.mandatory_ablations == 26U);

    input = witness(); input.runtime_mutation_authority_promoted = 1U;
    assert(hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.canonical_mutation_authorized = 1U;
    assert(hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.migration_active = 1U;
    assert(hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.pass213_gates_preserved = 0U;
    assert(hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.pass215_authorized = 0U;
    assert(hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.semantic_reuse_execution_authority_changed = 1U;
    assert(hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.semantic_reuse_automatic_promotion = 1U;
    assert(hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.exact_vm81_kernel_rebound = 0U;
    assert(hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.authority_root_hash216[0] = '0';
    assert(hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.exact_vm81_kernel_git_blob[0] = '0';
    assert(hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.terminal_receipt_hash72[0] = '0';
    assert(hhs_exact_pass219_bind_pass214_benchmark_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    puts("PASS219_INHERITED_PASS214_1_16_C_OK");
    return 0;
}
