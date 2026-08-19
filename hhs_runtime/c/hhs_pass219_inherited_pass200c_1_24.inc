#include "../include/hhs_pass219_inherited_pass200c_1_24.h"

#include <stddef.h>
#include <string.h>

static const char P200C_PRIMARY_BASE[] = "beff24168bb81b0b1459e325ebaad29b2252b980";
static const char P200C_VALIDATED_EXECUTABLE_HEAD[] = "828402a739744e4b12fb63d76a3923964d067c6f";
static const char P200C_EVIDENCE_HEAD[] = "73fa715ac8aee578b81e053fae99594df0b34889";
static const char P200C_ACCEPTED_MERGE[] = "a7868be1d98345cc7641bb7f59b716667cf1808d";
static const char P200C_FROZEN_I123[] = "30e1ae3a278ee19c3c167d3659ed71ca2a016873";
static const char P200C_CONTRACT_BLOB[] = "bc06fcab22c5bd857566c5560b9fd05b83bcdc75";
static const char P200C_WORKFLOW_BLOB[] = "bd54ffaf0c00c1b993dfa7f1d7cc759752bc9776";
static const char P200C_RUNTIME_V1_BLOB[] = "4c61dd428996372a9d8170092efde0a21c391134";
static const char P200C_PRODUCTION_PROJECTION_BLOB[] = "92f0bef25882c0885f769bff4570610601e820ea";
static const char P200C_ACTIVE_ROUTES_BLOB[] = "4b08c4e183793836f667ebacb73602341b1d45c2";
static const char P200C_CONTRACT_TEST_BLOB[] = "e6bd83499193ec5242ec0b04696bd7d423cebd4a";
static const char P200C_PRODUCTION_VALIDATOR_BLOB[] = "9c4f4b545cecf6e14dbe7aff050eed90f3368fe8";

static uint32_t p200c_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS200C_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS200C_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS200C_VERSION_PATCH;
}

static int p200c_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}

static int p200c_git(const char value[HHS_EXACT_PASS200C_GIT_SHA_STRLEN], const char *expected) {
    return p200c_text(value, HHS_EXACT_PASS200C_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS200C_GIT_SHA_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass200c_version(void) { return p200c_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass200c_guarded_active_admission(
    const HHSExactPass200CGuardedActiveWitnessV1 *witness,
    HHSExactPass219InheritedPass200CBindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p200c_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->primary_pull_request != HHS_EXACT_PASS200C_PRIMARY_PR ||
        witness->min_successful_canaries != HHS_EXACT_PASS200C_MIN_SUCCESSFUL_CANARIES ||
        witness->min_canary_invocations != HHS_EXACT_PASS200C_MIN_CANARY_INVOCATIONS ||
        witness->max_active_lease_invocations != HHS_EXACT_PASS200C_MAX_ACTIVE_LEASE_INVOCATIONS ||
        witness->lifecycle_test_count != HHS_EXACT_PASS200C_LIFECYCLE_TEST_COUNT ||
        witness->measured_canary_invocations != HHS_EXACT_PASS200C_MEASURED_CANARY_INVOCATIONS ||
        witness->measured_active_invocations != HHS_EXACT_PASS200C_MEASURED_ACTIVE_INVOCATIONS ||
        witness->measured_active_candidate_returns != HHS_EXACT_PASS200C_MEASURED_ACTIVE_CANDIDATE_RETURNS ||
        witness->measured_active_reference_returns != HHS_EXACT_PASS200C_MEASURED_ACTIVE_REFERENCE_RETURNS ||
        witness->measured_frontier_count != HHS_EXACT_PASS200C_MEASURED_FRONTIER_COUNT ||
        witness->measured_hash72_event_count != HHS_EXACT_PASS200C_MEASURED_HASH72_EVENT_COUNT ||
        witness->pass200a_candidate_bundle_required != 1U ||
        witness->pass200b_completed_canary_evidence_required != 1U ||
        witness->pass200b_rollback_disqualifies_bundle != 1U ||
        witness->three_distinct_approval_principals_required != 1U ||
        witness->compiler_runtime_operations_capabilities_required != 1U ||
        witness->distinct_approval_receipts_required != 1U ||
        witness->approvals_frontier_evidence_bundle_expiry_bound != 1U ||
        witness->singleton_vm81_activation_receipt_required != 1U ||
        witness->exact_result_guard_every_invocation != 1U ||
        witness->exact_witness_guard_every_invocation != 1U ||
        witness->exact_replay_guard_every_invocation != 1U ||
        witness->mismatch_restores_reference != 1U ||
        witness->expiry_restores_reference != 1U ||
        witness->lease_exhaustion_restores_reference != 1U ||
        witness->explicit_rollback_restores_reference != 1U ||
        witness->durable_state_and_hash72_history != 1U ||
        witness->persisted_evidence_tamper_rejected != 1U ||
        witness->persisted_frontier_tamper_rejected != 1U ||
        witness->candidate_self_authorization != 0U ||
        witness->frozen_constraint_promotion != 0U ||
        witness->pass201_successor_preserved != 1U ||
        witness->pass219_new_active_admission_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p200c_git(witness->primary_base_commit, P200C_PRIMARY_BASE) ||
        !p200c_git(witness->validated_executable_head, P200C_VALIDATED_EXECUTABLE_HEAD) ||
        !p200c_git(witness->evidence_head_commit, P200C_EVIDENCE_HEAD) ||
        !p200c_git(witness->accepted_merge_commit, P200C_ACCEPTED_MERGE) ||
        !p200c_git(witness->frozen_i123_commit, P200C_FROZEN_I123) ||
        !p200c_git(witness->contract_blob, P200C_CONTRACT_BLOB) ||
        !p200c_git(witness->workflow_blob, P200C_WORKFLOW_BLOB) ||
        !p200c_git(witness->runtime_v1_blob, P200C_RUNTIME_V1_BLOB) ||
        !p200c_git(witness->production_projection_blob, P200C_PRODUCTION_PROJECTION_BLOB) ||
        !p200c_git(witness->active_routes_blob, P200C_ACTIVE_ROUTES_BLOB) ||
        !p200c_git(witness->contract_test_blob, P200C_CONTRACT_TEST_BLOB) ||
        !p200c_git(witness->production_validator_blob, P200C_PRODUCTION_VALIDATOR_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p200c_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS200C_NUMBER;
    out_binding->pass_variant = HHS_EXACT_PASS219_INHERITED_PASS200C_VARIANT;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_squash_identity_bound = 1U;
    out_binding->immutable_source_identity_bound = 1U;
    out_binding->canary_evidence_gate_bound = 1U;
    out_binding->approval_and_activation_bound = 1U;
    out_binding->continuous_exact_guard_bound = 1U;
    out_binding->rollback_reference_restoration_bound = 1U;
    out_binding->durable_state_read_only_bound = 1U;
    out_binding->pass201_successor_bound = 1U;
    out_binding->no_new_active_admission_authority_bound = 1U;
    out_binding->no_new_canonical_mutation_authority_bound = 1U;
    out_binding->no_new_persistence_authority_bound = 1U;
    out_binding->no_new_hash72_clock_bound = 1U;
    out_binding->pass219_new_active_admission_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->accepted_merge_commit, witness->accepted_merge_commit, HHS_EXACT_PASS200C_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i123_commit, witness->frozen_i123_commit, HHS_EXACT_PASS200C_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
