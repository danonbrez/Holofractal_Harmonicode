#include "../include/hhs_pass219_inherited_pass187_1_39.h"

#include <stddef.h>
#include <string.h>

static const char P187_I139_COMPOSITION_CONTRACT_COMMIT[] = "6584c8e118eb73e0884165b3d1afd1ec84f34f57";
static const char P187_I139_BOTT_MERGE_COMMIT[] = "5db45d6b72b93132997f815d16df4540fd13adfc";
static const char P187_I139_PASS188_BOTT_RUNTIME_COMMIT[] = "c77e3feef42448a111d8b8912a1d1cb157d51925";
static const char P187_I139_COMPOSITION_COMPLETION_HEAD[] = "c36beacd8d6748f65c30ca3b02ac237eac38c34d";
static const char P187_I139_FROZEN_I138[] = "6f59481b48903759395dfbe94a4dc61097b306b1";

static const char P187_I139_COMPOSITION_CONTRACT_BLOB[] = "ac25bc7084b1a5e7202e25da47a5890307cf5e27";
static const char P187_I139_BOTT_RECEIPT_BLOB[] = "79a8915337397a06d30bee4452ee273fa2bae105";
static const char P187_I139_COMPOSITION_RUNTIME_BLOB[] = "e5b41b12cb24158010f0dffc7a88b6f2740e5d2b";
static const char P187_I139_COMPOSITION_TESTS_BLOB[] = "64aa62e1ace43b49f8dbf4951ef0b87707129aeb";
static const char P187_I139_COMPOSITION_BROWSER_BLOB[] = "2fce626b94a4895800a9ffb48f3201078631d037";
static const char P187_I139_COMPOSITION_WORKFLOW_BLOB[] = "7692878d88efb260e9430295648e384e78e5a50d";

static uint32_t p187_i139_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS187_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS187_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS187_VERSION_PATCH;
}

static int p187_i139_git(
    const char value[HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS187_I139_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS187_I139_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass187_version(void) {
    return p187_i139_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass187_cumulative_authority(
    const HHSExactPass187CumulativeAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass187BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p187_i139_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->composition_contract_preserved != 1U ||
        witness->composition_completion_verified != 1U ||
        witness->composition_acceptance_scenario_count != 12U ||
        witness->harmonicode_roundtrip_verified != 1U ||
        witness->incremental_recomposition_verified != 1U ||
        witness->linux_adapter_integration_verified != 1U ||
        witness->visual_browser_acceptance_verified != 1U ||
        witness->cold_restart_recovery_verified != 1U ||
        witness->inherited_vm81_witness_required != 1U ||
        witness->local_event_evidence_is_mutation_authority != 0U ||
        witness->independent_vm81_authority != 0U ||
        witness->independent_hash72_clock != 0U ||
        witness->float_canonical_authority != 0U ||
        witness->historical_bott_contract_preserved != 1U ||
        witness->historical_bott_baseline_verified != 1U ||
        witness->historical_bott_runtime_gap_record_preserved != 1U ||
        witness->pass188_bott_runtime_closure_preserved != 1U ||
        witness->pass188_successor_preserved != 1U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p187_i139_git(witness->composition_contract_commit, P187_I139_COMPOSITION_CONTRACT_COMMIT) ||
        !p187_i139_git(witness->historical_bott_merge_commit, P187_I139_BOTT_MERGE_COMMIT) ||
        !p187_i139_git(witness->pass188_bott_runtime_commit, P187_I139_PASS188_BOTT_RUNTIME_COMMIT) ||
        !p187_i139_git(witness->composition_completion_head, P187_I139_COMPOSITION_COMPLETION_HEAD) ||
        !p187_i139_git(witness->frozen_i138_commit, P187_I139_FROZEN_I138) ||
        !p187_i139_git(witness->composition_contract_blob, P187_I139_COMPOSITION_CONTRACT_BLOB) ||
        !p187_i139_git(witness->bott_receipt_blob, P187_I139_BOTT_RECEIPT_BLOB) ||
        !p187_i139_git(witness->composition_runtime_blob, P187_I139_COMPOSITION_RUNTIME_BLOB) ||
        !p187_i139_git(witness->composition_tests_blob, P187_I139_COMPOSITION_TESTS_BLOB) ||
        !p187_i139_git(witness->composition_browser_blob, P187_I139_COMPOSITION_BROWSER_BLOB) ||
        !p187_i139_git(witness->composition_workflow_blob, P187_I139_COMPOSITION_WORKFLOW_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p187_i139_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS187_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->composition_contract_bound = 1U;
    out_binding->composition_completion_bound = 1U;
    out_binding->harmonicode_order_bound = 1U;
    out_binding->incremental_recomposition_bound = 1U;
    out_binding->linux_adapter_bound = 1U;
    out_binding->visual_interaction_bound = 1U;
    out_binding->replay_restart_bound = 1U;
    out_binding->vm81_witness_boundary_bound = 1U;
    out_binding->historical_bott_baseline_bound = 1U;
    out_binding->pass188_bott_runtime_closure_bound = 1U;
    out_binding->pass188_successor_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    out_binding->float_is_canonical_authority = 0U;
    out_binding->pass219_new_candidate_authority = 0U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->frozen_i138_commit, witness->frozen_i138_commit, HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN);
    memcpy(out_binding->composition_completion_head, witness->composition_completion_head, HHS_EXACT_PASS187_I139_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
