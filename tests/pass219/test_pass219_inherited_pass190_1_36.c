#include "hhs_pass219_inherited_pass190_1_36.h"

#include <assert.h>
#include <string.h>

static HHSExactPass190FullCompletionAuthorityWitnessV1 witness(void) {
    HHSExactPass190FullCompletionAuthorityWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass190_version();
    w.full_contract_authorized = 1U;
    w.historical_iteration7_preserved = 1U;
    w.completion_coordinator_verified = 1U;
    w.project_acceptance_overlay_verified = 1U;
    w.python312_census_classified = 1U;
    w.governed_operation_count = 52U;
    w.historical_operation_count = 42U;
    w.project_acceptance_operation_count = 10U;
    w.constructor_python_shell_direct_parity = 1U;
    w.canonical_public_gateway = 1U;
    w.openapi_registry_projection = 1U;
    w.websocket_receipt_projection = 1U;
    w.actual_repository_hydration_reused = 1U;
    w.mutation_capability_gated = 1U;
    w.deterministic_replay = 1U;
    w.hash72_receipt_chain = 1U;
    w.hash216_registry_identity = 1U;
    w.pass191_successor_preserved = 1U;

    strcpy(w.contract_authorization_commit, "88e7ae935990b1c36db6d39bc46d3b89b2e465cb");
    strcpy(w.iteration7_merge_commit, "7b4825ae1437c2325bc9bb348086c0957cfd5c28");
    strcpy(w.frozen_i135_commit, "5e593b384732ffb065480cdd2d1098f1f32a990e");
    strcpy(w.validated_core_head, "fbbc3ff37b6dea6c31e73612731e4e323a54475f");
    strcpy(w.universal_contract_blob, "3fcdd91c52f5054ee075e9f4fd7b4a0c9c90ec74");
    strcpy(w.iteration7_receipt_blob, "d89d16e0c2a8fb99ae67ca0317b5ab3b824f3805");
    strcpy(w.init_blob, "00e6463075cb62f3e1913d301456fbefcb4044d1");
    strcpy(w.python_compat_blob, "fb08250159d0c8e55e0947f041dc88a5285824af");
    strcpy(w.completion_blob, "74c343fdb0d1dd42c1cc99abd2d7c81e49e60dd9");
    strcpy(w.acceptance_blob, "c27f8aa589976e495003328f51bc1afaa83d5d9f");
    strcpy(w.shell_blob, "d723ef6f0a65fe055d8c2ebceeeb67635f2c0a77");
    strcpy(w.public_api_blob, "6431f246ef973211b71d97c2137c482e3b7a11d6");
    strcpy(w.python_registry_blob, "d2f82c74d6fab051d009099155857d3ecde9b4b5");
    strcpy(w.hydration_registry_blob, "d80c8e949a310049852208784df9de594678f354");
    strcpy(w.network_registry_blob, "48e17afa9ab9e84879acda80214f6998c90663b6");
    strcpy(w.completion_test_blob, "0fce98eb5364bbdd4b90b8ce72f474f21551b751");
    strcpy(w.validated_core_workflow_blob, "e40d396334b8b440cd20ccc0544987288ff986ff");
    return w;
}

int main(void) {
    HHSExactPass190FullCompletionAuthorityWitnessV1 w = witness();
    HHSExactPass219InheritedPass190BindingV1 b;

    assert(hhs_exact_pass219_bind_pass190_full_completion_authority(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 190U);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.full_contract_bound == 1U);
    assert(b.historical_iteration7_bound == 1U);
    assert(b.completion_coordinator_bound == 1U);
    assert(b.registry_52_bound == 1U);
    assert(b.interface_parity_bound == 1U);
    assert(b.canonical_gateway_bound == 1U);
    assert(b.repository_hydration_bound == 1U);
    assert(b.inherited_vm81_receipt_bound == 1U);
    assert(b.hash216_registry_bound == 1U);
    assert(b.pass191_successor_bound == 1U);
    assert(b.no_new_authority_bound == 1U);
    assert(b.float_is_canonical_authority == 0U);
    assert(b.pass219_new_candidate_authority == 0U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.pass219_new_persistence_authority == 0U);
    assert(b.pass219_new_hash72_clock == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);

    w = witness();
    w.governed_operation_count = 51U;
    assert(hhs_exact_pass219_bind_pass190_full_completion_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.float_is_canonical_authority = 1U;
    assert(hhs_exact_pass219_bind_pass190_full_completion_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.pass191_successor_preserved = 0U;
    assert(hhs_exact_pass219_bind_pass190_full_completion_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    strcpy(w.completion_blob, "0000000000000000000000000000000000000000");
    assert(hhs_exact_pass219_bind_pass190_full_completion_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
