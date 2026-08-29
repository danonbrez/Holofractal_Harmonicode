#include "../include/hhs_pass219_inherited_pass192_1_34.h"

#include <stddef.h>
#include <string.h>

static const char P192_I134_AUTHORIZATION_COMMIT[] = "c3da7e2b7125754b65f08fb8922a151bf01df2b8";
static const char P192_I134_FROZEN_I133[] = "8380d2dbc9cf1b0245f006eaa440b47a921d4901";
static const char P192_I134_CONTRACT_BLOB[] = "cab24f1b2e7510321f6449814302ea31b704d5a8";
static const char P192_I134_COMPRESSION_HEADER_BLOB[] = "8e2d0a1620ff8ce88f588ce9dc55d79f5503f354";
static const char P192_I134_COMPRESSION_INC_BLOB[] = "2034a9cacb07d09c4b5786ccec28e61d64de635b";
static const char P192_I134_COMPRESSION_REFERENCE_BLOB[] = "bda83c1a8791dd4bd9e807a88e0a419848d1d140";
static const char P192_I134_RUNTIME_BLOB[] = "279495e7b88adbd01e56eb6b8897c4d2f88bb948";
static const char P192_I134_SDK_BLOB[] = "2e0727e9e078fdbb5ad9f866d05f6d886576a9e1";
static const char P192_I134_CLI_BLOB[] = "1718211edd8739c43837aea9ba53d8de613e3f1b";
static const char P192_I134_API_BLOB[] = "1e2f9f37f46310d0dffecba66b5c044958b585bc";
static const char P192_I134_VISUAL_SERVER_BLOB[] = "aefc759cccf3ebd75f81f220814a225a592b4140";
static const char P192_I134_TENSOR_SCHEMA_BLOB[] = "697b0bf3ba811f82ef0a62b4e9bd3615d59bdcb9";
static const char P192_I134_OPERATION_REGISTRY_BLOB[] = "33384a6886117c45b6b6ff96514ac85477fbb14d";
static const char P192_I134_PRECONTRACT_TEST_BLOB[] = "a72e7b8ab6dc0f891540fe2192d92d80f4a0cf52";
static const char P192_I134_COMPRESSION_TEST_BLOB[] = "b615c6c192761bdb565c7e6cecf6daa03e95c8ab";
static const char P192_I134_RUNTIME_TEST_BLOB[] = "a0ce335f5e263c980f30d8427162d321a8ffa122";
static const char P192_I134_API_TEST_BLOB[] = "7586e0270a44b83e6838ca10d43ac33806143774";
static const char P192_I134_CLI_TEST_BLOB[] = "250275392c6b1ee2809512673d7f1864243527a3";
static const char P192_I134_VISUAL_TEST_BLOB[] = "c56aa9e67f331bbc61430317667ea80272549bc2";
static const char P192_I134_FOCUSED_WORKFLOW_BLOB[] = "7d23c8867cb9647295b34c0975b5842e6c96adc0";

static uint32_t p192_i134_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS192_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS192_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS192_VERSION_PATCH;
}

static int p192_i134_git(
    const char value[HHS_EXACT_PASS192_I134_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS192_I134_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS192_I134_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass192_version(void) {
    return p192_i134_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass192_cellular_fibonacci_tensor(
    const HHSExactPass192CellularFibonacciTensorAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass192BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p192_i134_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->canonical_source_preserved != 1U ||
        witness->lo_shu_cellular_tensor != 1U ||
        witness->five_magnitude_rows != 1U ||
        witness->exact_fibonacci_rational_scales != 1U ||
        witness->unbounded_declarative_depth != 1U ||
        witness->bounded_finite_materialization != 1U ||
        witness->non_destructive_membrane_depth != 1U ||
        witness->outer_modulus_separation != 1U ||
        witness->inherited_pass219_1_9_compression_preserved != 1U ||
        witness->operation_registry_bound != 1U ||
        witness->python_sdk_parity != 1U ||
        witness->cli_grammar_parity != 1U ||
        witness->openapi_parity != 1U ||
        witness->production_router_registered != 1U ||
        witness->public_api_federation_preserved != 1U ||
        witness->vm81_authorized_mutations != 1U ||
        witness->hash72_mutation_receipts != 1U ||
        witness->hash216_canonical_identity != 1U ||
        witness->safe_filesystem_locator_projection != 1U ||
        witness->replay_verified != 1U ||
        witness->pass193_successor_preserved != 1U ||
        witness->float_is_canonical_authority != 0U ||
        witness->filesystem_locator_is_canonical_authority != 0U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p192_i134_git(witness->contract_authorization_commit, P192_I134_AUTHORIZATION_COMMIT) ||
        !p192_i134_git(witness->frozen_i133_commit, P192_I134_FROZEN_I133) ||
        !p192_i134_git(witness->contract_blob, P192_I134_CONTRACT_BLOB) ||
        !p192_i134_git(witness->compression_header_blob, P192_I134_COMPRESSION_HEADER_BLOB) ||
        !p192_i134_git(witness->compression_inc_blob, P192_I134_COMPRESSION_INC_BLOB) ||
        !p192_i134_git(witness->compression_reference_blob, P192_I134_COMPRESSION_REFERENCE_BLOB) ||
        !p192_i134_git(witness->runtime_blob, P192_I134_RUNTIME_BLOB) ||
        !p192_i134_git(witness->sdk_blob, P192_I134_SDK_BLOB) ||
        !p192_i134_git(witness->cli_blob, P192_I134_CLI_BLOB) ||
        !p192_i134_git(witness->api_blob, P192_I134_API_BLOB) ||
        !p192_i134_git(witness->visual_server_blob, P192_I134_VISUAL_SERVER_BLOB) ||
        !p192_i134_git(witness->tensor_schema_blob, P192_I134_TENSOR_SCHEMA_BLOB) ||
        !p192_i134_git(witness->operation_registry_blob, P192_I134_OPERATION_REGISTRY_BLOB) ||
        !p192_i134_git(witness->precontract_test_blob, P192_I134_PRECONTRACT_TEST_BLOB) ||
        !p192_i134_git(witness->compression_test_blob, P192_I134_COMPRESSION_TEST_BLOB) ||
        !p192_i134_git(witness->runtime_test_blob, P192_I134_RUNTIME_TEST_BLOB) ||
        !p192_i134_git(witness->api_test_blob, P192_I134_API_TEST_BLOB) ||
        !p192_i134_git(witness->cli_test_blob, P192_I134_CLI_TEST_BLOB) ||
        !p192_i134_git(witness->visual_registration_test_blob, P192_I134_VISUAL_TEST_BLOB) ||
        !p192_i134_git(witness->focused_workflow_blob, P192_I134_FOCUSED_WORKFLOW_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p192_i134_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS192_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->canonical_source_bound = 1U;
    out_binding->lo_shu_tensor_bound = 1U;
    out_binding->exact_fibonacci_bound = 1U;
    out_binding->bounded_materialization_bound = 1U;
    out_binding->membrane_depth_bound = 1U;
    out_binding->outer_modulus_separation_bound = 1U;
    out_binding->inherited_compression_bound = 1U;
    out_binding->interface_parity_bound = 1U;
    out_binding->production_registration_bound = 1U;
    out_binding->inherited_vm81_receipt_bound = 1U;
    out_binding->hash216_identity_bound = 1U;
    out_binding->filesystem_projection_safety_bound = 1U;
    out_binding->replay_bound = 1U;
    out_binding->pass193_successor_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->float_is_canonical_authority = 0U;
    out_binding->filesystem_locator_is_canonical_authority = 0U;
    out_binding->pass219_new_candidate_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(
        out_binding->contract_authorization_commit,
        witness->contract_authorization_commit,
        HHS_EXACT_PASS192_I134_GIT_SHA_STRLEN
    );
    memcpy(
        out_binding->frozen_i133_commit,
        witness->frozen_i133_commit,
        HHS_EXACT_PASS192_I134_GIT_SHA_STRLEN
    );
    return HHS_EXACT_STATUS_OK;
}
