#include "hhs_pass219_inherited_pass213_1_16.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void copy_text(char *target, size_t size, const char *value) {
    const size_t length = strlen(value);
    assert(length + 1U == size);
    memcpy(target, value, size);
}

static HHSExactPass213ClosureWitnessV1 witness(void) {
    HHSExactPass213ClosureWitnessV1 value;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = hhs_exact_pass219_inherited_pass213_version();
    value.final_iteration = 11U;
    value.implementation_complete = 1U;
    value.inherited_passes_001_through_212 = 1U;
    value.correction_before_interpretation = 1U;
    value.correction_before_execution = 1U;
    value.recovery_admission_required = 1U;
    value.native_protected_memory_required = 1U;
    value.zeroization_before_release_required = 1U;
    value.dependency_scoped_semantic_revalidation = 1U;
    value.persistent_inventory_and_tombstones_required = 1U;
    value.pqc_enclosure_required = 1U;
    value.rfc3161_external_timestamp_required = 1U;
    value.no_float_canonical_authority = 1U;
    value.governed_surface_projection_only = 1U;
    value.network_capability_issuance_forbidden = 1U;
    value.protected_material_nonexposure_required = 1U;
    value.physical_tensor_mapping_nonexposure_required = 1U;
    value.singleton_vm81_admission = 1U;
    value.immutable_compiled_rom_entries = 1U;
    value.native_dispatch_real_c_abi_required = 1U;
    value.native_dispatch_dynamic_allocation_forbidden = 1U;
    value.native_dispatch_ambient_state_forbidden = 1U;
    value.inherited_governed_canonical_mutation_authority = 1U;
    value.raw_native_dispatch_bypass_forbidden = 1U;
    value.full_hydration_bits = 50388480U;
    value.full_hydration_bytes = 6298560U;
    value.affine_seed_bytes = 2430U;
    value.compressed_payload_bytes = 2473U;
    value.missing_shard_count = 2U;
    value.moving_tensor_domain = 50388480U;
    value.exact_lookup_iterations = 2048U;
    value.parametric_iterations = 512U;
    value.tensor_route_iterations = 8192U;
    value.native_dispatch_iterations = 32U;
    value.recovery_boundary_sequence = 16U;
    value.dispatch_final_sequence = 32U;
    value.uninterrupted_resumed_receipts_equal = 1U;
    value.ledger_chains_valid = 1U;
    value.native_dispatch_id_count = 9U;
    value.main_tests_passed = 124U;
    value.branch_validation_run = 31065370870ULL;
    value.branch_validation_job = 92501866672ULL;
    value.main_validation_run = 31065471241ULL;
    value.main_validation_job = 92502158212ULL;
    copy_text(value.final_branch_head, sizeof(value.final_branch_head), "383ef8741f904ff1b770dd428530824640fbc83b");
    copy_text(value.main_merge_head, sizeof(value.main_merge_head), "86ec461818682fc87232740758769602e8f9fe05");
    copy_text(value.branch_artifact_sha256, sizeof(value.branch_artifact_sha256), "4541fdfef0b353257f16a58a6d1d9088f1dfe3dbbe37b8f0178fde1a86ebbc28");
    copy_text(value.main_artifact_sha256, sizeof(value.main_artifact_sha256), "93b478f73bbc2df96d67d86fc93ea85b6b48b0c960d9d35c16d7430a1551b6d6");
    copy_text(value.semantic_root_hash216, sizeof(value.semantic_root_hash216), "b783eaf39ca3cdff05d31dbe1406dc4ed45943a48b1cf89f3ee451a2c0326c0d");
    copy_text(value.terminal_receipt_hash72, sizeof(value.terminal_receipt_hash72), "mO(Wo87dXeN)Ua2hbw96>2mLKi)iBlLT0Qy-qsjl>1icjig(7cc/d)FJd<9(gmvC20YL?twn");
    copy_text(value.observation_root_hash216, sizeof(value.observation_root_hash216), "d4bc7fdd97dac1d334711f6ce11e9a2ccdb16dcb1d89d23da8c5a178444d9c53");
    copy_text(value.pass214_gate_preservation_root_hash216, sizeof(value.pass214_gate_preservation_root_hash216), "214106621723b579ffe4813c74d5df98a7e14387293b8ecc3e1edc81bf066092");
    copy_text(value.contract_git_blob, sizeof(value.contract_git_blob), "4787901cb2e52e594431a92ae3a40e2cd87623ec");
    copy_text(value.final_evidence_git_blob, sizeof(value.final_evidence_git_blob), "089290d4b1baff61d8848e655d1fb4c3ef31bfb4");
    copy_text(value.native_dispatch_source_git_blob, sizeof(value.native_dispatch_source_git_blob), "a1dd0f29e1d4f166e1c9bae4ca14c8c2b5ebe75f");
    copy_text(value.secure_arena_source_git_blob, sizeof(value.secure_arena_source_git_blob), "d92c36d904b77810b54593e60235491fc300d85d");
    copy_text(value.governed_authority_git_blob, sizeof(value.governed_authority_git_blob), "aea2ab6e7a2287fd066d99e0a2bb2c0481deb6e4");
    return value;
}

int main(void) {
    HHSExactPass213ClosureWitnessV1 input = witness();
    HHSExactPass219InheritedPass213BindingV1 output;
    HHSExactStatus status;

    memset(&output, 0, sizeof(output));
    status = hhs_exact_pass219_bind_pass213_compiled_rom_authority(&input, &output);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(output.pass_number == 213U);
    assert(output.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(output.terminal_closure_bound == 1U);
    assert(output.compiled_rom_authority_bound == 1U);
    assert(output.correction_before_interpretation_bound == 1U);
    assert(output.protected_memory_bound == 1U);
    assert(output.pqc_timestamp_tensor_bound == 1U);
    assert(output.governed_native_dispatch_bound == 1U);
    assert(output.persistent_ledger_bound == 1U);
    assert(output.interruption_recovery_bound == 1U);
    assert(output.pass214_gate_preservation_bound == 1U);
    assert(output.inherited_governed_canonical_mutation_authority == 1U);
    assert(output.pass219_new_mutation_authority == 0U);
    assert(output.cxx_mutation_authority == 0U);
    assert(output.vm81_direct_mutation_authority == 0U);
    assert(output.raw_native_dispatch_bypass_forbidden == 1U);

    input = witness(); input.pass219_new_mutation_authority = 1U;
    assert(hhs_exact_pass219_bind_pass213_compiled_rom_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.pass219_cxx_mutation_authority = 1U;
    assert(hhs_exact_pass219_bind_pass213_compiled_rom_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.pass219_vm81_direct_mutation_authority = 1U;
    assert(hhs_exact_pass219_bind_pass213_compiled_rom_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.raw_native_dispatch_bypass_forbidden = 0U;
    assert(hhs_exact_pass219_bind_pass213_compiled_rom_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.inherited_governed_canonical_mutation_authority = 0U;
    assert(hhs_exact_pass219_bind_pass213_compiled_rom_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.no_float_canonical_authority = 0U;
    assert(hhs_exact_pass219_bind_pass213_compiled_rom_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.semantic_root_hash216[0] = '0';
    assert(hhs_exact_pass219_bind_pass213_compiled_rom_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.main_merge_head[0] = '0';
    assert(hhs_exact_pass219_bind_pass213_compiled_rom_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness(); input.pass214_gate_preservation_root_hash216[0] = '0';
    assert(hhs_exact_pass219_bind_pass213_compiled_rom_authority(&input, &output) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    puts("PASS219_INHERITED_PASS213_1_16_C_OK");
    return 0;
}
