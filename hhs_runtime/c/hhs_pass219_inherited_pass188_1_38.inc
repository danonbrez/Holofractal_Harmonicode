#include "../include/hhs_pass219_inherited_pass188_1_38.h"

#include <stddef.h>
#include <string.h>

static const char P188_I138_LICENSE_CONTRACT_COMMIT[] = "50aec3f624fe6cbaefa3220b7d709bb1b388a942";
static const char P188_I138_BOTT_RUNTIME_COMMIT[] = "c77e3feef42448a111d8b8912a1d1cb157d51925";
static const char P188_I138_LICENSE_COMPLETION_HEAD[] = "8e6f209aa8974da30d0b1dcb85a7ca2dc10060c6";
static const char P188_I138_FROZEN_I137[] = "ef27a1caf0d977e0f767b13126dba8fe49b09dab";

static const char P188_I138_LICENSE_CONTRACT_BLOB[] = "871ed3fff0a677ad6173eb00a099d010ac1a730b";
static const char P188_I138_BOTT_RECEIPT_BLOB[] = "492d60716896c66cdb507f6e76163d988d1d41e6";
static const char P188_I138_LICENSE_RUNTIME_BLOB[] = "9ead3669a04b211be09adca66b35f37269350056";
static const char P188_I138_LICENSE_TESTS_BLOB[] = "e55466723c0f15667fea93ecbb076a1f2fb5d570";
static const char P188_I138_LICENSE_WORKFLOW_BLOB[] = "943f93de78036622be13fe6f530e2a5c596de7e6";

static uint32_t p188_i138_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS188_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS188_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS188_VERSION_PATCH;
}

static int p188_i138_git(
    const char value[HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS188_I138_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS188_I138_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass188_version(void) {
    return p188_i138_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass188_cumulative_authority(
    const HHSExactPass188CumulativeAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass188BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p188_i138_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->license_contract_preserved != 1U ||
        witness->license_completion_verified != 1U ||
        witness->license_acceptance_scenario_count != 16U ||
        witness->immutable_content_versions != 1U ||
        witness->immutable_license_versions != 1U ||
        witness->inherited_vm81_witness_required != 1U ||
        witness->license_hash72_event_chain != 1U ||
        witness->license_hash216_identity != 1U ||
        witness->license_deterministic_replay != 1U ||
        witness->license_materialized_integrity != 1U ||
        witness->license_cold_restart_recovery != 1U ||
        witness->license_pass187_graph_impact != 1U ||
        witness->license_transfer_delegation != 1U ||
        witness->license_revocation_expiry != 1U ||
        witness->license_exact_royalty != 1U ||
        witness->license_external_chain_required != 0U ||
        witness->license_wallet_authority != 0U ||
        witness->license_browser_authority != 0U ||
        witness->license_marketplace_authority != 0U ||
        witness->license_float_canonical_authority != 0U ||
        witness->license_independent_vm81_authority != 0U ||
        witness->license_independent_hash72_clock != 0U ||
        witness->bott_runtime_verified != 1U ||
        witness->bott_projected_address_count != 1259712U ||
        witness->bott_deterministic_replay != 1U ||
        witness->bott_float_canonical_authority != 0U ||
        witness->bott_canonical_mutation_authority != 0U ||
        witness->pass189_successor_preserved != 1U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p188_i138_git(witness->license_contract_commit, P188_I138_LICENSE_CONTRACT_COMMIT) ||
        !p188_i138_git(witness->bott_runtime_commit, P188_I138_BOTT_RUNTIME_COMMIT) ||
        !p188_i138_git(witness->license_completion_head, P188_I138_LICENSE_COMPLETION_HEAD) ||
        !p188_i138_git(witness->frozen_i137_commit, P188_I138_FROZEN_I137) ||
        !p188_i138_git(witness->license_contract_blob, P188_I138_LICENSE_CONTRACT_BLOB) ||
        !p188_i138_git(witness->bott_receipt_blob, P188_I138_BOTT_RECEIPT_BLOB) ||
        !p188_i138_git(witness->license_runtime_blob, P188_I138_LICENSE_RUNTIME_BLOB) ||
        !p188_i138_git(witness->license_tests_blob, P188_I138_LICENSE_TESTS_BLOB) ||
        !p188_i138_git(witness->license_workflow_blob, P188_I138_LICENSE_WORKFLOW_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p188_i138_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS188_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->license_contract_bound = 1U;
    out_binding->license_completion_bound = 1U;
    out_binding->immutable_lineage_bound = 1U;
    out_binding->vm81_witness_boundary_bound = 1U;
    out_binding->license_receipt_replay_bound = 1U;
    out_binding->legacy_transfer_revocation_bound = 1U;
    out_binding->pass187_impact_bound = 1U;
    out_binding->bott_runtime_bound = 1U;
    out_binding->bott_nonmutation_bound = 1U;
    out_binding->pass189_successor_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->float_is_canonical_authority = 0U;
    out_binding->pass219_new_candidate_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->frozen_i137_commit, witness->frozen_i137_commit, HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN);
    memcpy(out_binding->license_completion_head, witness->license_completion_head, HHS_EXACT_PASS188_I138_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
