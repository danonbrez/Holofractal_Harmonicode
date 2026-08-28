#include "../include/hhs_pass219_inherited_pass202_1_22.h"

#include <stddef.h>
#include <string.h>

static const char P202_PRIMARY_BASE[] = "bdf19276b0974481bd69d70ca1154f284f238e48";
static const char P202_PRIMARY_HEAD[] = "1eb9326f8024b37b9fc1425d910bc20cae50abbb";
static const char P202_PRIMARY_MERGE[] = "33ce89c7328180eb98d59f72df43f3036cf1edab";
static const char P202_BOOTSTRAP_HEAD[] = "8a8f1eaefa940f9416430f2746014e1716ddd23b";
static const char P202_BOOTSTRAP_MERGE[] = "83b6fd89cd8adb1962aeb159917fe24ee4485441";
static const char P202_HISTORICAL_GUARDED_CI_BLOB[] = "e6b4e7c7cda8a64ef59151eae0e33ff1a70c6cd4";
static const char P202_HISTORICAL_UPDATER_BLOB[] = "b1ad8ced814c8c58d3365c4f45cbb0cd338fb564";
static const char P202_HISTORICAL_ENV_BLOB[] = "2cf1d20f60d26d1b476ebd268fdc85b1db1a0764";
static const char P202_HISTORICAL_INSTALLER_BLOB[] = "97ab585e3e96122cbaded47e1a436fc0e143bac1";
static const char P202_HISTORICAL_SERVICE_BLOB[] = "1cc1dce920213df7c0a5f1ee4e9823a9dc727ec5";
static const char P202_HISTORICAL_TIMER_BLOB[] = "3296ee9787544542697d3915e01569562ef30046";
static const char P202_HISTORICAL_VALIDATOR_BLOB[] = "82250c50fa9d20a82d0b957d2637398760b1c416";
static const char P202_HISTORICAL_CONTRACT_TEST_BLOB[] = "709afe1c0d612ad91744a5cd71cb87d8a313aad6";
static const char P202_FROZEN_I121[] = "94a100766c582c83fa3e4f7cb815c08b0eacfa1a";
static const char P202_CURRENT_UPDATER_BLOB[] = "c1815c56e5bceeca2a840c5a693bd22d6e85ef84";
static const char P202_CURRENT_ENV_BLOB[] = "7890657593b5d4dd03e4cf5eb2c4c1c7ba25e519";
static const char P202_CURRENT_INSTALLER_BLOB[] = "93dfbe6cc3a789de82b5249f32a129a31306aeb5";
static const char P202_CURRENT_VALIDATOR_BLOB[] = "729d8e571160239094aaef612a17d039f310ca03";
static const char P202_CURRENT_RUNTIME_OS_BUNDLE_BLOB[] = "23afbf9c99d77f57acd7334d767c483572d64e0a";

static uint32_t p202_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS202_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS202_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS202_VERSION_PATCH;
}

static int p202_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}

static int p202_git(const char value[HHS_EXACT_PASS202_GIT_SHA_STRLEN], const char *expected) {
    return p202_text(value, HHS_EXACT_PASS202_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS202_GIT_SHA_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass202_version(void) { return p202_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass202_guarded_deployment(
    const HHSExactPass202GuardedDeploymentWitnessV1 *witness,
    HHSExactPass219InheritedPass202BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p202_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->primary_pull_request != HHS_EXACT_PASS202_PRIMARY_PR ||
        witness->bootstrap_pull_request != HHS_EXACT_PASS202_BOOTSTRAP_PR ||
        witness->initial_contract_test_count != HHS_EXACT_PASS202_INITIAL_CONTRACT_TEST_COUNT ||
        witness->bootstrap_contract_test_count != HHS_EXACT_PASS202_BOOTSTRAP_CONTRACT_TEST_COUNT ||
        witness->main_only_production_source != 1U ||
        witness->trusted_label_author_gate != 1U ||
        witness->same_repository_pull_request_required != 1U ||
        witness->detached_candidate_validation != 1U ||
        witness->fast_forward_only_promotion != 1U ||
        witness->post_promotion_health_required != 1U ||
        witness->rollback_to_exact_previous_commit != 1U ||
        witness->durable_jsonl_receipts != 1U ||
        witness->bounded_singleton_timer != 1U ||
        witness->host_local_drift_blocked_historically != 1U ||
        witness->bootstrap_dry_run_required != 1U ||
        witness->explicit_operator_enable_required != 1U ||
        witness->guarded_ci_blob_preserved != 1U ||
        witness->service_timer_blobs_preserved != 1U ||
        witness->successor_hardening_verified != 1U ||
        witness->host_drift_preservation_verified != 1U ||
        witness->runtime_os_bundle_sha_bound != 1U ||
        witness->prebuilt_bundle_required_for_production != 1U ||
        witness->install_promotion_default_disabled != 1U ||
        witness->recovery_receipt_gated != 1U ||
        witness->pass203_successor_preserved != 1U ||
        witness->pass219_new_deployment_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p202_git(witness->primary_base_commit, P202_PRIMARY_BASE) ||
        !p202_git(witness->primary_head_commit, P202_PRIMARY_HEAD) ||
        !p202_git(witness->primary_merge_commit, P202_PRIMARY_MERGE) ||
        !p202_git(witness->bootstrap_head_commit, P202_BOOTSTRAP_HEAD) ||
        !p202_git(witness->bootstrap_merge_commit, P202_BOOTSTRAP_MERGE) ||
        !p202_git(witness->historical_guarded_ci_blob, P202_HISTORICAL_GUARDED_CI_BLOB) ||
        !p202_git(witness->historical_updater_blob, P202_HISTORICAL_UPDATER_BLOB) ||
        !p202_git(witness->historical_env_blob, P202_HISTORICAL_ENV_BLOB) ||
        !p202_git(witness->historical_installer_blob, P202_HISTORICAL_INSTALLER_BLOB) ||
        !p202_git(witness->historical_service_blob, P202_HISTORICAL_SERVICE_BLOB) ||
        !p202_git(witness->historical_timer_blob, P202_HISTORICAL_TIMER_BLOB) ||
        !p202_git(witness->historical_validator_blob, P202_HISTORICAL_VALIDATOR_BLOB) ||
        !p202_git(witness->historical_contract_test_blob, P202_HISTORICAL_CONTRACT_TEST_BLOB) ||
        !p202_git(witness->frozen_i121_commit, P202_FROZEN_I121) ||
        !p202_git(witness->current_updater_blob, P202_CURRENT_UPDATER_BLOB) ||
        !p202_git(witness->current_env_blob, P202_CURRENT_ENV_BLOB) ||
        !p202_git(witness->current_installer_blob, P202_CURRENT_INSTALLER_BLOB) ||
        !p202_git(witness->current_validator_blob, P202_CURRENT_VALIDATOR_BLOB) ||
        !p202_git(witness->current_runtime_os_bundle_blob, P202_CURRENT_RUNTIME_OS_BUNDLE_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p202_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS202_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_guarded_ci_bound = 1U;
    out_binding->dry_run_bootstrap_bound = 1U;
    out_binding->deployment_transition_bound = 1U;
    out_binding->exact_rollback_bound = 1U;
    out_binding->durable_receipt_boundary_bound = 1U;
    out_binding->successor_hardening_bound = 1U;
    out_binding->host_drift_preservation_bound = 1U;
    out_binding->runtime_os_bundle_boundary_bound = 1U;
    out_binding->pass203_successor_bound = 1U;
    out_binding->no_new_deployment_authority_bound = 1U;
    out_binding->no_new_canonical_mutation_authority_bound = 1U;
    out_binding->no_new_persistence_authority_bound = 1U;
    out_binding->no_new_hash72_clock_bound = 1U;
    out_binding->pass219_new_deployment_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->bootstrap_merge_commit, witness->bootstrap_merge_commit, HHS_EXACT_PASS202_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i121_commit, witness->frozen_i121_commit, HHS_EXACT_PASS202_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
