#include "../include/hhs_pass219_inherited_pass200a_1_26.h"

#include <stddef.h>
#include <string.h>

static const char P200A_BASE[] = "649be68e1566002ce66c919463a386b8018bc2fb";
static const char P200A_REVIEWED_HEAD[] = "5ef1d3ab6c0ceb3a20d468447b991066626de366";
static const char P200A_ACCEPTED_MERGE[] = "eee6670f7d3c6743e1bf32c7e42a4150d07351e3";
static const char P200A_FROZEN_I125[] = "21bf16233a0c4573a754c29686d13782bcc4fc44";
static const char P200A_CONTRACT_BLOB[] = "46c9a8fdbacb80e1d136a67bd4b48e2e4a82c367";
static const char P200A_RUNTIME_V1_BLOB[] = "1f6d7b0092da3916705a58af9ae2ad2c22c3bab3";
static const char P200A_PRODUCTION_BLOB[] = "521e89fc1c8b3067574884fb69a79a4d856887a1";
static const char P200A_WORKFLOW_BLOB[] = "2817d207568e43f5621d56267f076503fa7e9628";
static const char P200A_ROUTES_BLOB[] = "3f123916520c6b7f877903d50bb924992895bff6";
static const char P200A_TEST_BLOB[] = "068a5e15e5a877ff439ab42535b1429cf77b00ad";
static const char P200A_RESTART_BLOB[] = "984950272cd9463319b163cb7a2a1e2037c0da12";

static uint32_t p200a_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS200A_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS200A_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS200A_VERSION_PATCH;
}

static int p200a_git(const char value[HHS_EXACT_PASS200A_GIT_SHA_STRLEN], const char *expected) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS200A_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS200A_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass200a_version(void) { return p200a_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass200a_repaired_shadow_authority(
    const HHSExactPass200ARepairedShadowWitnessV2 *witness,
    HHSExactPass219InheritedPass200ABindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p200a_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->primary_pull_request != HHS_EXACT_PASS200A_PRIMARY_PR ||
        witness->production_envelopes != HHS_EXACT_PASS200A_PRODUCTION_ENVELOPES ||
        witness->production_states != HHS_EXACT_PASS200A_PRODUCTION_STATES ||
        witness->production_branch_jobs != HHS_EXACT_PASS200A_PRODUCTION_BRANCH_JOBS ||
        witness->production_admitted != HHS_EXACT_PASS200A_PRODUCTION_ADMITTED ||
        witness->production_rejected != HHS_EXACT_PASS200A_PRODUCTION_REJECTED ||
        witness->production_vm5184_comparisons != HHS_EXACT_PASS200A_PRODUCTION_VM5184_COMPARISONS ||
        witness->negative_mutations != HHS_EXACT_PASS200A_NEGATIVE_MUTATIONS ||
        witness->optimization_bundles != HHS_EXACT_PASS200A_BUNDLES ||
        witness->shadow_matches != HHS_EXACT_PASS200A_SHADOW_MATCHES ||
        witness->reference_returns != HHS_EXACT_PASS200A_REFERENCE_RETURNS ||
        witness->candidate_activations != HHS_EXACT_PASS200A_CANDIDATE_ACTIVATIONS ||
        witness->vm81_receipt_chain_provenance_required != 1U ||
        witness->reference_lane_independently_executed != 1U ||
        witness->candidate_lane_independently_executed != 1U ||
        witness->exact_semantic_comparison_required != 1U ||
        witness->exact_witness_comparison_required != 1U ||
        witness->exact_replay_comparison_required != 1U ||
        witness->shadow_payload_hash_revalidated != 1U ||
        witness->shadow_event_payload_binding_required != 1U ||
        witness->current_pass198_proof_required != 1U ||
        witness->revoked_pass198_proof_rejected != 1U ||
        witness->production_profile_identity_required != 1U ||
        witness->production_acceptance_totals_required != 1U ||
        witness->singleton_upgraded_in_place != 1U ||
        witness->duplicate_default_authority_forbidden != 1U ||
        witness->partial_holdout_state_recoverable != 1U ||
        witness->reference_result_remains_authoritative != 1U ||
        witness->candidate_may_commit != 0U ||
        witness->candidate_may_activate != 0U ||
        witness->compiler_auto_activation != 0U ||
        witness->runtime_auto_admission != 0U ||
        witness->canary_enabled != 0U ||
        witness->active_enabled != 0U ||
        witness->frozen_constraint_enabled != 0U ||
        witness->pass200b_successor_preserved != 1U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p200a_git(witness->historical_base_commit, P200A_BASE) ||
        !p200a_git(witness->historical_reviewed_head, P200A_REVIEWED_HEAD) ||
        !p200a_git(witness->accepted_merge_commit, P200A_ACCEPTED_MERGE) ||
        !p200a_git(witness->frozen_i125_commit, P200A_FROZEN_I125) ||
        !p200a_git(witness->contract_blob, P200A_CONTRACT_BLOB) ||
        !p200a_git(witness->runtime_v1_blob, P200A_RUNTIME_V1_BLOB) ||
        !p200a_git(witness->historical_production_blob, P200A_PRODUCTION_BLOB) ||
        !p200a_git(witness->historical_workflow_blob, P200A_WORKFLOW_BLOB) ||
        !p200a_git(witness->historical_routes_blob, P200A_ROUTES_BLOB) ||
        !p200a_git(witness->historical_test_blob, P200A_TEST_BLOB) ||
        !p200a_git(witness->historical_restart_blob, P200A_RESTART_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p200a_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS200A_NUMBER;
    out_binding->pass_variant = HHS_EXACT_PASS219_INHERITED_PASS200A_VARIANT;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_squash_identity_bound = 1U;
    out_binding->inherited_defects_repaired = 1U;
    out_binding->vm81_receipt_provenance_bound = 1U;
    out_binding->independent_shadow_execution_bound = 1U;
    out_binding->persisted_shadow_integrity_bound = 1U;
    out_binding->live_pass198_proof_bound = 1U;
    out_binding->production_acceptance_bound = 1U;
    out_binding->singleton_identity_bound = 1U;
    out_binding->partial_restartability_bound = 1U;
    out_binding->pass200b_successor_bound = 1U;
    out_binding->no_new_candidate_authority_bound = 1U;
    out_binding->no_new_canonical_mutation_authority_bound = 1U;
    out_binding->no_new_persistence_authority_bound = 1U;
    out_binding->no_new_hash72_clock_bound = 1U;
    out_binding->pass219_new_candidate_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->accepted_merge_commit, witness->accepted_merge_commit, HHS_EXACT_PASS200A_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i125_commit, witness->frozen_i125_commit, HHS_EXACT_PASS200A_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
