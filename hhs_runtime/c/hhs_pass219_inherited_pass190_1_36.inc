#include "../include/hhs_pass219_inherited_pass190_1_36.h"

#include <stddef.h>
#include <string.h>

static const char P190_I136_CONTRACT_AUTH[] = "88e7ae935990b1c36db6d39bc46d3b89b2e465cb";
static const char P190_I136_ITERATION7_MERGE[] = "7b4825ae1437c2325bc9bb348086c0957cfd5c28";
static const char P190_I136_FROZEN_I135[] = "5e593b384732ffb065480cdd2d1098f1f32a990e";
static const char P190_I136_VALIDATED_CORE_HEAD[] = "fbbc3ff37b6dea6c31e73612731e4e323a54475f";
static const char P190_I136_UNIVERSAL_CONTRACT_BLOB[] = "3fcdd91c52f5054ee075e9f4fd7b4a0c9c90ec74";
static const char P190_I136_ITERATION7_RECEIPT_BLOB[] = "d89d16e0c2a8fb99ae67ca0317b5ab3b824f3805";
static const char P190_I136_INIT_BLOB[] = "00e6463075cb62f3e1913d301456fbefcb4044d1";
static const char P190_I136_PYTHON_COMPAT_BLOB[] = "fb08250159d0c8e55e0947f041dc88a5285824af";
static const char P190_I136_COMPLETION_BLOB[] = "74c343fdb0d1dd42c1cc99abd2d7c81e49e60dd9";
static const char P190_I136_ACCEPTANCE_BLOB[] = "c27f8aa589976e495003328f51bc1afaa83d5d9f";
static const char P190_I136_SHELL_BLOB[] = "d723ef6f0a65fe055d8c2ebceeeb67635f2c0a77";
static const char P190_I136_PUBLIC_API_BLOB[] = "6431f246ef973211b71d97c2137c482e3b7a11d6";
static const char P190_I136_PYTHON_REGISTRY_BLOB[] = "d2f82c74d6fab051d009099155857d3ecde9b4b5";
static const char P190_I136_HYDRATION_REGISTRY_BLOB[] = "d80c8e949a310049852208784df9de594678f354";
static const char P190_I136_NETWORK_REGISTRY_BLOB[] = "48e17afa9ab9e84879acda80214f6998c90663b6";
static const char P190_I136_COMPLETION_TEST_BLOB[] = "0fce98eb5364bbdd4b90b8ce72f474f21551b751";
static const char P190_I136_VALIDATED_CORE_WORKFLOW_BLOB[] = "e40d396334b8b440cd20ccc0544987288ff986ff";

static uint32_t p190_i136_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS190_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS190_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS190_VERSION_PATCH;
}

static int p190_i136_git(
    const char value[HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS190_I136_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS190_I136_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass190_version(void) {
    return p190_i136_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass190_full_completion_authority(
    const HHSExactPass190FullCompletionAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass190BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p190_i136_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->full_contract_authorized != 1U ||
        witness->historical_iteration7_preserved != 1U ||
        witness->completion_coordinator_verified != 1U ||
        witness->project_acceptance_overlay_verified != 1U ||
        witness->python312_census_classified != 1U ||
        witness->governed_operation_count != 52U ||
        witness->historical_operation_count != 42U ||
        witness->project_acceptance_operation_count != 10U ||
        witness->constructor_python_shell_direct_parity != 1U ||
        witness->canonical_public_gateway != 1U ||
        witness->openapi_registry_projection != 1U ||
        witness->websocket_receipt_projection != 1U ||
        witness->actual_repository_hydration_reused != 1U ||
        witness->mutation_capability_gated != 1U ||
        witness->deterministic_replay != 1U ||
        witness->hash72_receipt_chain != 1U ||
        witness->hash216_registry_identity != 1U ||
        witness->pass191_successor_preserved != 1U ||
        witness->float_is_canonical_authority != 0U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p190_i136_git(witness->contract_authorization_commit, P190_I136_CONTRACT_AUTH) ||
        !p190_i136_git(witness->iteration7_merge_commit, P190_I136_ITERATION7_MERGE) ||
        !p190_i136_git(witness->frozen_i135_commit, P190_I136_FROZEN_I135) ||
        !p190_i136_git(witness->validated_core_head, P190_I136_VALIDATED_CORE_HEAD) ||
        !p190_i136_git(witness->universal_contract_blob, P190_I136_UNIVERSAL_CONTRACT_BLOB) ||
        !p190_i136_git(witness->iteration7_receipt_blob, P190_I136_ITERATION7_RECEIPT_BLOB) ||
        !p190_i136_git(witness->init_blob, P190_I136_INIT_BLOB) ||
        !p190_i136_git(witness->python_compat_blob, P190_I136_PYTHON_COMPAT_BLOB) ||
        !p190_i136_git(witness->completion_blob, P190_I136_COMPLETION_BLOB) ||
        !p190_i136_git(witness->acceptance_blob, P190_I136_ACCEPTANCE_BLOB) ||
        !p190_i136_git(witness->shell_blob, P190_I136_SHELL_BLOB) ||
        !p190_i136_git(witness->public_api_blob, P190_I136_PUBLIC_API_BLOB) ||
        !p190_i136_git(witness->python_registry_blob, P190_I136_PYTHON_REGISTRY_BLOB) ||
        !p190_i136_git(witness->hydration_registry_blob, P190_I136_HYDRATION_REGISTRY_BLOB) ||
        !p190_i136_git(witness->network_registry_blob, P190_I136_NETWORK_REGISTRY_BLOB) ||
        !p190_i136_git(witness->completion_test_blob, P190_I136_COMPLETION_TEST_BLOB) ||
        !p190_i136_git(witness->validated_core_workflow_blob, P190_I136_VALIDATED_CORE_WORKFLOW_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p190_i136_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS190_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->full_contract_bound = 1U;
    out_binding->historical_iteration7_bound = 1U;
    out_binding->completion_coordinator_bound = 1U;
    out_binding->registry_52_bound = 1U;
    out_binding->interface_parity_bound = 1U;
    out_binding->canonical_gateway_bound = 1U;
    out_binding->repository_hydration_bound = 1U;
    out_binding->inherited_vm81_receipt_bound = 1U;
    out_binding->hash216_registry_bound = 1U;
    out_binding->pass191_successor_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->float_is_canonical_authority = 0U;
    out_binding->pass219_new_candidate_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->validated_core_head, witness->validated_core_head, HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i135_commit, witness->frozen_i135_commit, HHS_EXACT_PASS190_I136_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
