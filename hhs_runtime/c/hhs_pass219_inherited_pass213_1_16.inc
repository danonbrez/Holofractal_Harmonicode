#include "../include/hhs_pass219_inherited_pass213_1_16.h"

#include <stddef.h>
#include <string.h>

static const char HHS_EXACT_PASS213_FINAL_BRANCH_HEAD[] =
    "383ef8741f904ff1b770dd428530824640fbc83b";
static const char HHS_EXACT_PASS213_MAIN_MERGE_HEAD[] =
    "86ec461818682fc87232740758769602e8f9fe05";
static const char HHS_EXACT_PASS213_BRANCH_ARTIFACT_SHA256[] =
    "4541fdfef0b353257f16a58a6d1d9088f1dfe3dbbe37b8f0178fde1a86ebbc28";
static const char HHS_EXACT_PASS213_MAIN_ARTIFACT_SHA256[] =
    "93b478f73bbc2df96d67d86fc93ea85b6b48b0c960d9d35c16d7430a1551b6d6";
static const char HHS_EXACT_PASS213_SEMANTIC_ROOT[] =
    "b783eaf39ca3cdff05d31dbe1406dc4ed45943a48b1cf89f3ee451a2c0326c0d";
static const char HHS_EXACT_PASS213_TERMINAL_RECEIPT_HASH72[] =
    "mO(Wo87dXeN)Ua2hbw96>2mLKi)iBlLT0Qy-qsjl>1icjig(7cc/d)FJd<9(gmvC20YL?twn";
static const char HHS_EXACT_PASS213_OBSERVATION_ROOT[] =
    "d4bc7fdd97dac1d334711f6ce11e9a2ccdb16dcb1d89d23da8c5a178444d9c53";
static const char HHS_EXACT_PASS213_PASS214_GATE_ROOT[] =
    "214106621723b579ffe4813c74d5df98a7e14387293b8ecc3e1edc81bf066092";
static const char HHS_EXACT_PASS213_CONTRACT_GIT_BLOB[] =
    "4787901cb2e52e594431a92ae3a40e2cd87623ec";
static const char HHS_EXACT_PASS213_FINAL_EVIDENCE_GIT_BLOB[] =
    "089290d4b1baff61d8848e655d1fb4c3ef31bfb4";
static const char HHS_EXACT_PASS213_NATIVE_DISPATCH_SOURCE_GIT_BLOB[] =
    "a1dd0f29e1d4f166e1c9bae4ca14c8c2b5ebe75f";
static const char HHS_EXACT_PASS213_SECURE_ARENA_SOURCE_GIT_BLOB[] =
    "d92c36d904b77810b54593e60235491fc300d85d";
static const char HHS_EXACT_PASS213_GOVERNED_AUTHORITY_GIT_BLOB[] =
    "aea2ab6e7a2287fd066d99e0a2bb2c0481deb6e4";

static uint32_t hhs_exact_pass219_inherited_pass213_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS213_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS213_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS213_VERSION_PATCH;
}

static int hhs_exact_pass213_exact_text(
    const char *value,
    size_t value_size,
    const char *expected,
    size_t expected_length
) {
    if (value == NULL || expected == NULL || value_size != expected_length + 1U)
        return 0;
    if (value[expected_length] != '\0')
        return 0;
    return memcmp(value, expected, expected_length) == 0;
}

static int hhs_exact_pass213_exact_git_sha(
    const char value[HHS_EXACT_PASS213_GIT_SHA_STRLEN],
    const char expected[HHS_EXACT_PASS213_GIT_SHA_STRLEN]
) {
    return hhs_exact_pass213_exact_text(
        value,
        HHS_EXACT_PASS213_GIT_SHA_STRLEN,
        expected,
        HHS_EXACT_PASS213_GIT_SHA_LEN);
}

static int hhs_exact_pass213_exact_sha256(
    const char value[HHS_EXACT_PASS213_SHA256_HEX_STRLEN],
    const char expected[HHS_EXACT_PASS213_SHA256_HEX_STRLEN]
) {
    return hhs_exact_pass213_exact_text(
        value,
        HHS_EXACT_PASS213_SHA256_HEX_STRLEN,
        expected,
        HHS_EXACT_PASS213_SHA256_HEX_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass213_version(void) {
    return hhs_exact_pass219_inherited_pass213_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass213_compiled_rom_authority(
    const HHSExactPass213ClosureWitnessV1 *witness,
    HHSExactPass219InheritedPass213BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != hhs_exact_pass219_inherited_pass213_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->final_iteration != 11U ||
        witness->implementation_complete != 1U ||
        witness->inherited_passes_001_through_212 != 1U ||
        witness->superseded_authority_count != 0U ||
        witness->correction_before_interpretation != 1U ||
        witness->correction_before_execution != 1U ||
        witness->recovery_admission_required != 1U ||
        witness->native_protected_memory_required != 1U ||
        witness->zeroization_before_release_required != 1U ||
        witness->dependency_scoped_semantic_revalidation != 1U ||
        witness->persistent_inventory_and_tombstones_required != 1U ||
        witness->pqc_enclosure_required != 1U ||
        witness->rfc3161_external_timestamp_required != 1U ||
        witness->no_float_canonical_authority != 1U ||
        witness->governed_surface_projection_only != 1U ||
        witness->network_capability_issuance_forbidden != 1U ||
        witness->protected_material_nonexposure_required != 1U ||
        witness->physical_tensor_mapping_nonexposure_required != 1U ||
        witness->singleton_vm81_admission != 1U ||
        witness->immutable_compiled_rom_entries != 1U ||
        witness->native_dispatch_real_c_abi_required != 1U ||
        witness->native_dispatch_dynamic_allocation_forbidden != 1U ||
        witness->native_dispatch_ambient_state_forbidden != 1U ||
        witness->inherited_governed_canonical_mutation_authority != 1U ||
        witness->pass219_new_mutation_authority != 0U ||
        witness->pass219_cxx_mutation_authority != 0U ||
        witness->pass219_vm81_direct_mutation_authority != 0U ||
        witness->raw_native_dispatch_bypass_forbidden != 1U ||
        witness->full_hydration_bits != 50388480U ||
        witness->full_hydration_bytes != 6298560U ||
        witness->affine_seed_bytes != 2430U ||
        witness->compressed_payload_bytes != 2473U ||
        witness->missing_shard_count != 2U ||
        witness->moving_tensor_domain != 50388480U ||
        witness->exact_lookup_iterations != 2048U ||
        witness->parametric_iterations != 512U ||
        witness->tensor_route_iterations != 8192U ||
        witness->native_dispatch_iterations != 32U ||
        witness->recovery_boundary_sequence != 16U ||
        witness->dispatch_final_sequence != 32U ||
        witness->uninterrupted_resumed_receipts_equal != 1U ||
        witness->ledger_chains_valid != 1U ||
        witness->performance_timings_canonical != 0U ||
        witness->native_dispatch_id_count != HHS_EXACT_PASS213_NATIVE_DISPATCH_ID_COUNT ||
        witness->main_tests_passed != 124U ||
        witness->branch_validation_run != 31065370870ULL ||
        witness->branch_validation_job != 92501866672ULL ||
        witness->main_validation_run != 31065471241ULL ||
        witness->main_validation_job != 92502158212ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs_exact_pass213_exact_git_sha(witness->final_branch_head, HHS_EXACT_PASS213_FINAL_BRANCH_HEAD) ||
        !hhs_exact_pass213_exact_git_sha(witness->main_merge_head, HHS_EXACT_PASS213_MAIN_MERGE_HEAD) ||
        !hhs_exact_pass213_exact_sha256(witness->branch_artifact_sha256, HHS_EXACT_PASS213_BRANCH_ARTIFACT_SHA256) ||
        !hhs_exact_pass213_exact_sha256(witness->main_artifact_sha256, HHS_EXACT_PASS213_MAIN_ARTIFACT_SHA256) ||
        !hhs_exact_pass213_exact_sha256(witness->semantic_root_hash216, HHS_EXACT_PASS213_SEMANTIC_ROOT) ||
        !hhs_exact_pass213_exact_text(witness->terminal_receipt_hash72,
                                      HHS_EXACT_PASS213_HASH72_STRLEN,
                                      HHS_EXACT_PASS213_TERMINAL_RECEIPT_HASH72,
                                      HHS_EXACT_HASH72_LEN) ||
        !hhs_exact_pass213_exact_sha256(witness->observation_root_hash216, HHS_EXACT_PASS213_OBSERVATION_ROOT) ||
        !hhs_exact_pass213_exact_sha256(witness->pass214_gate_preservation_root_hash216, HHS_EXACT_PASS213_PASS214_GATE_ROOT) ||
        !hhs_exact_pass213_exact_git_sha(witness->contract_git_blob, HHS_EXACT_PASS213_CONTRACT_GIT_BLOB) ||
        !hhs_exact_pass213_exact_git_sha(witness->final_evidence_git_blob, HHS_EXACT_PASS213_FINAL_EVIDENCE_GIT_BLOB) ||
        !hhs_exact_pass213_exact_git_sha(witness->native_dispatch_source_git_blob, HHS_EXACT_PASS213_NATIVE_DISPATCH_SOURCE_GIT_BLOB) ||
        !hhs_exact_pass213_exact_git_sha(witness->secure_arena_source_git_blob, HHS_EXACT_PASS213_SECURE_ARENA_SOURCE_GIT_BLOB) ||
        !hhs_exact_pass213_exact_git_sha(witness->governed_authority_git_blob, HHS_EXACT_PASS213_GOVERNED_AUTHORITY_GIT_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs_exact_pass219_inherited_pass213_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS213_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->terminal_closure_bound = 1U;
    out_binding->compiled_rom_authority_bound = 1U;
    out_binding->correction_before_interpretation_bound = 1U;
    out_binding->protected_memory_bound = 1U;
    out_binding->pqc_timestamp_tensor_bound = 1U;
    out_binding->governed_native_dispatch_bound = 1U;
    out_binding->persistent_ledger_bound = 1U;
    out_binding->interruption_recovery_bound = 1U;
    out_binding->pass214_gate_preservation_bound = 1U;
    out_binding->inherited_governed_canonical_mutation_authority = 1U;
    out_binding->pass219_new_mutation_authority = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_direct_mutation_authority = 0U;
    out_binding->raw_native_dispatch_bypass_forbidden = 1U;
    out_binding->native_dispatch_id_count = witness->native_dispatch_id_count;
    out_binding->native_dispatch_iterations = witness->native_dispatch_iterations;
    out_binding->recovery_boundary_sequence = witness->recovery_boundary_sequence;
    memcpy(out_binding->main_merge_head, witness->main_merge_head, HHS_EXACT_PASS213_GIT_SHA_STRLEN);
    memcpy(out_binding->semantic_root_hash216, witness->semantic_root_hash216, HHS_EXACT_PASS213_SHA256_HEX_STRLEN);
    memcpy(out_binding->terminal_receipt_hash72, witness->terminal_receipt_hash72, HHS_EXACT_PASS213_HASH72_STRLEN);
    memcpy(out_binding->pass214_gate_preservation_root_hash216, witness->pass214_gate_preservation_root_hash216, HHS_EXACT_PASS213_SHA256_HEX_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
