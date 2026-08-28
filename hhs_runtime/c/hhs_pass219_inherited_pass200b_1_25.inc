#include "../include/hhs_pass219_inherited_pass200b_1_25.h"

#include <stddef.h>
#include <string.h>

static const char P200B_PRIMARY_BASE[] = "483a18b618dbe51b31025eeb15a8a6435e4040c5";
static const char P200B_VALIDATED_EXECUTABLE_HEAD[] = "f13eed02531e77737562b23fb207962c0744ed0d";
static const char P200B_EVIDENCE_HEAD[] = "07f12ba91d78d28f0d9f73ec54e3167d4f1fa5b3";
static const char P200B_ACCEPTED_MERGE[] = "eb7dd08b8bc52451c2e179b68949097ade5499af";
static const char P200B_FROZEN_I124[] = "18ca57da270785483679e36a4d861c2002c69323";
static const char P200B_CONTRACT_BLOB[] = "1e442f002bd0936090a5b7154150021e0a543948";
static const char P200B_WORKFLOW_BLOB[] = "e0b2335d509839f9175c5e6a08eef6bbbd18d437";
static const char P200B_RUNTIME_V1_BLOB[] = "8034383ec6dcad463c45296c9eeb241f3e1123c5";
static const char P200B_PRODUCTION_PROJECTION_BLOB[] = "67e79a10250bfa3e9678937d28ed4bc22fed9937";
static const char P200B_CANARY_ROUTES_BLOB[] = "abb2bee87c7ad12e0d3e441840bdb0643d425b05";
static const char P200B_CONTRACT_TEST_BLOB[] = "ad843727f95b517c6f9c77b2338434c6605ba5d0";
static const char P200B_VISUAL_PANEL_BLOB[] = "def9ff882023c310ffd1ab3ff0d040115f2a76b2";
static const char P200B_RESTART_RECORD_BLOB[] = "435fd4f65b0d9f423e3ec6ec1a155f4d35948c13";

static uint32_t p200b_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS200B_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS200B_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS200B_VERSION_PATCH;
}

static int p200b_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}

static int p200b_git(const char value[HHS_EXACT_PASS200B_GIT_SHA_STRLEN], const char *expected) {
    return p200b_text(value, HHS_EXACT_PASS200B_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS200B_GIT_SHA_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass200b_version(void) { return p200b_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass200b_governed_canary_admission(
    const HHSExactPass200BGovernedCanaryWitnessV1 *witness,
    HHSExactPass219InheritedPass200BBindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p200b_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->primary_pull_request != HHS_EXACT_PASS200B_PRIMARY_PR ||
        witness->max_canary_invocations != HHS_EXACT_PASS200B_MAX_CANARY_INVOCATIONS ||
        witness->lifecycle_test_count != HHS_EXACT_PASS200B_LIFECYCLE_TEST_COUNT ||
        witness->measured_pass200a_envelopes != HHS_EXACT_PASS200B_MEASURED_PASS200A_ENVELOPES ||
        witness->measured_pass200a_bundles != HHS_EXACT_PASS200B_MEASURED_PASS200A_BUNDLES ||
        witness->measured_pass200a_shadow_matches != HHS_EXACT_PASS200B_MEASURED_PASS200A_SHADOW_MATCHES ||
        witness->measured_canary_frontiers != HHS_EXACT_PASS200B_MEASURED_CANARY_FRONTIERS ||
        witness->measured_singleton_activations != HHS_EXACT_PASS200B_MEASURED_SINGLETON_ACTIVATIONS ||
        witness->measured_invocations != HHS_EXACT_PASS200B_MEASURED_INVOCATIONS ||
        witness->measured_candidate_returns != HHS_EXACT_PASS200B_MEASURED_CANDIDATE_RETURNS ||
        witness->measured_reference_returns != HHS_EXACT_PASS200B_MEASURED_REFERENCE_RETURNS ||
        witness->measured_rollback_frontiers != HHS_EXACT_PASS200B_MEASURED_ROLLBACK_FRONTIERS ||
        witness->measured_exhausted_frontiers != HHS_EXACT_PASS200B_MEASURED_EXHAUSTED_FRONTIERS ||
        witness->measured_frontier_count != HHS_EXACT_PASS200B_MEASURED_FRONTIER_COUNT ||
        witness->measured_hash72_event_count != HHS_EXACT_PASS200B_MEASURED_HASH72_EVENT_COUNT ||
        witness->pass200a_closed_proof_required != 1U ||
        witness->compiler_candidate_required != 1U ||
        witness->shadow_mode_required != 1U ||
        witness->persisted_exact_shadow_match_required != 1U ||
        witness->exactly_two_approvals_required != 1U ||
        witness->distinct_approval_principals_required != 1U ||
        witness->distinct_approval_receipts_required != 1U ||
        witness->compiler_runtime_capabilities_required != 1U ||
        witness->approval_bundle_frontier_expiry_receipt_bound != 1U ||
        witness->singleton_vm81_activation_receipt_required != 1U ||
        witness->deterministic_integer_selection_required != 1U ||
        witness->exact_result_match_required != 1U ||
        witness->exact_witness_match_required != 1U ||
        witness->exact_replay_match_required != 1U ||
        witness->mismatch_restores_reference != 1U ||
        witness->expiry_restores_reference != 1U ||
        witness->exhaustion_restores_reference != 1U ||
        witness->explicit_rollback_restores_reference != 1U ||
        witness->durable_state_and_hash72_history != 1U ||
        witness->persisted_frontier_tamper_rejected != 1U ||
        witness->event_chain_tamper_rejected != 1U ||
        witness->candidate_self_authorization != 0U ||
        witness->automatic_active_promotion != 0U ||
        witness->frozen_constraint_promotion != 0U ||
        witness->candidate_canonical_commit != 0U ||
        witness->pass200c_successor_preserved != 1U ||
        witness->pass219_new_canary_admission_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p200b_git(witness->primary_base_commit, P200B_PRIMARY_BASE) ||
        !p200b_git(witness->validated_executable_head, P200B_VALIDATED_EXECUTABLE_HEAD) ||
        !p200b_git(witness->evidence_head_commit, P200B_EVIDENCE_HEAD) ||
        !p200b_git(witness->accepted_merge_commit, P200B_ACCEPTED_MERGE) ||
        !p200b_git(witness->frozen_i124_commit, P200B_FROZEN_I124) ||
        !p200b_git(witness->contract_blob, P200B_CONTRACT_BLOB) ||
        !p200b_git(witness->workflow_blob, P200B_WORKFLOW_BLOB) ||
        !p200b_git(witness->runtime_v1_blob, P200B_RUNTIME_V1_BLOB) ||
        !p200b_git(witness->production_projection_blob, P200B_PRODUCTION_PROJECTION_BLOB) ||
        !p200b_git(witness->canary_routes_blob, P200B_CANARY_ROUTES_BLOB) ||
        !p200b_git(witness->contract_test_blob, P200B_CONTRACT_TEST_BLOB) ||
        !p200b_git(witness->visual_panel_blob, P200B_VISUAL_PANEL_BLOB) ||
        !p200b_git(witness->restart_record_blob, P200B_RESTART_RECORD_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p200b_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS200B_NUMBER;
    out_binding->pass_variant = HHS_EXACT_PASS219_INHERITED_PASS200B_VARIANT;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_squash_identity_bound = 1U;
    out_binding->immutable_source_identity_bound = 1U;
    out_binding->pass200a_shadow_gate_bound = 1U;
    out_binding->dual_approval_and_activation_bound = 1U;
    out_binding->bounded_integer_selection_bound = 1U;
    out_binding->exact_comparison_bound = 1U;
    out_binding->rollback_and_exhaustion_bound = 1U;
    out_binding->durable_state_read_only_bound = 1U;
    out_binding->pass200c_successor_bound = 1U;
    out_binding->no_new_canary_admission_authority_bound = 1U;
    out_binding->no_new_canonical_mutation_authority_bound = 1U;
    out_binding->no_new_persistence_authority_bound = 1U;
    out_binding->no_new_hash72_clock_bound = 1U;
    out_binding->pass219_new_canary_admission_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->accepted_merge_commit, witness->accepted_merge_commit, HHS_EXACT_PASS200B_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i124_commit, witness->frozen_i124_commit, HHS_EXACT_PASS200B_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
