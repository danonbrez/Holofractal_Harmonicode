#include "../include/hhs_pass219_inherited_pass198_1_28.h"

#include <stddef.h>
#include <string.h>

static const char P198_BASE[] = "b40e11315840781d1fd9c12932fad46eb32e383f";
static const char P198_REVIEWED_HEAD[] = "a383ab8ec6a55e04ab490477c7b8cfe5d107d098";
static const char P198_ACCEPTED_MERGE[] = "122d21565fd7f3f9bbe9fb73ad2182d1d468ba5e";
static const char P198_FROZEN_I127[] = "fa89488d84f845fa372551b5324e0ddd37e49daf";
static const char P198_VALIDATED_REPAIR_HEAD[] = "97faba2ec59c54d1cd17be5bb88ade370841f65f";
static const char P198_ACCEPTED_CONTRACT_BLOB[] = "c623794f920ebbefbb6cb21eaf20767a1fd78306";
static const char P198_ACCEPTED_RUNTIME_BLOB[] = "3ec97b653344cbaf28eee89e6debbe1b6a89975d";
static const char P198_ACCEPTED_API_BLOB[] = "0e2581a3ecb0044eaf328617be1ae85e69e1e9a7";
static const char P198_ACCEPTED_TEST_BLOB[] = "2f4285b15644e88fb46d74bf06fa5c8d266e8859";
static const char P198_ACCEPTED_WORKFLOW_BLOB[] = "d9eb8b172d81ed2d9e07916c13b914bab8ec6654";
static const char P198_REPAIRED_RUNTIME_BLOB[] = "9be70fd34fad007001a830fc225792a9a56a24e7";
static const char P198_REPAIRED_API_BLOB[] = "2b2663cab7f74a2e1c21b77c2d5317296d925911";
static const char P198_REPAIRED_REGRESSION_BLOB[] = "b05a76b0cb694a51b66b147583c95520f2e54a9b";
static const char P198_REPAIRED_WORKFLOW_BLOB[] = "879f6b10ed08f5be590f28510ba12b225da44d0b";

static uint32_t p198_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS198_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS198_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS198_VERSION_PATCH;
}

static int p198_git(const char value[HHS_EXACT_PASS198_GIT_SHA_STRLEN], const char *expected) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS198_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS198_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass198_version(void) { return p198_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass198_repaired_calibration_registry(
    const HHSExactPass198RepairedCalibrationRegistryWitnessV1 *witness,
    HHSExactPass219InheritedPass198BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p198_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->primary_pull_request != HHS_EXACT_PASS198_PRIMARY_PR ||
        witness->default_parameter_states != HHS_EXACT_PASS198_DEFAULT_STATES ||
        witness->default_admitted_states != HHS_EXACT_PASS198_DEFAULT_ADMITTED ||
        witness->default_rejected_states != HHS_EXACT_PASS198_DEFAULT_REJECTED ||
        witness->vm5184_address_comparisons != HHS_EXACT_PASS198_VM5184_COMPARISONS ||
        witness->simplification_count != HHS_EXACT_PASS198_SIMPLIFICATION_COUNT ||
        witness->negative_mutation_count != HHS_EXACT_PASS198_NEGATIVE_MUTATION_COUNT ||
        witness->review_finding_count != HHS_EXACT_PASS198_REVIEW_FINDING_COUNT ||
        witness->full_replay_required != 1U ||
        witness->full_replay_executed != 1U ||
        witness->nonzero_admitted_coverage_required != 1U ||
        witness->exact_builtin_adapter_spec_binding_required != 1U ||
        witness->registration_vm81_receipt_persisted != 1U ||
        witness->recursive_float_identity_rejection != 1U ||
        witness->atomic_builtin_registration != 1U ||
        witness->normalized_persistent_identifier_updates != 1U ||
        witness->transactional_promotion_state_recheck != 1U ||
        witness->checkpoint_receipt_independent != 1U ||
        witness->distinct_workload_promotion_required != 1U ||
        witness->per_simplification_cost_unmeasured != 1U ||
        witness->executed_negative_mutations_required != 1U ||
        witness->executed_negative_mutation_count != HHS_EXACT_PASS198_NEGATIVE_MUTATION_COUNT ||
        witness->all_negative_mutations_detected != 1U ||
        witness->pass199_successor_preserved != 1U ||
        witness->compiler_auto_promotion != 0U ||
        witness->runtime_auto_admission != 0U ||
        witness->api_mutation_authority != 0U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p198_git(witness->historical_base_commit, P198_BASE) ||
        !p198_git(witness->historical_reviewed_head, P198_REVIEWED_HEAD) ||
        !p198_git(witness->accepted_merge_commit, P198_ACCEPTED_MERGE) ||
        !p198_git(witness->frozen_i127_commit, P198_FROZEN_I127) ||
        !p198_git(witness->validated_repair_head, P198_VALIDATED_REPAIR_HEAD) ||
        !p198_git(witness->accepted_contract_blob, P198_ACCEPTED_CONTRACT_BLOB) ||
        !p198_git(witness->accepted_runtime_blob, P198_ACCEPTED_RUNTIME_BLOB) ||
        !p198_git(witness->accepted_api_blob, P198_ACCEPTED_API_BLOB) ||
        !p198_git(witness->accepted_test_blob, P198_ACCEPTED_TEST_BLOB) ||
        !p198_git(witness->accepted_workflow_blob, P198_ACCEPTED_WORKFLOW_BLOB) ||
        !p198_git(witness->repaired_runtime_blob, P198_REPAIRED_RUNTIME_BLOB) ||
        !p198_git(witness->repaired_api_blob, P198_REPAIRED_API_BLOB) ||
        !p198_git(witness->repaired_regression_blob, P198_REPAIRED_REGRESSION_BLOB) ||
        !p198_git(witness->repaired_workflow_blob, P198_REPAIRED_WORKFLOW_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p198_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS198_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_squash_identity_bound = 1U;
    out_binding->inherited_defects_repaired = 1U;
    out_binding->production_totals_bound = 1U;
    out_binding->deterministic_replay_bound = 1U;
    out_binding->exact_adapter_binding_bound = 1U;
    out_binding->vm81_registration_receipt_bound = 1U;
    out_binding->exact_identity_rejection_bound = 1U;
    out_binding->transaction_and_restart_bound = 1U;
    out_binding->distinct_workload_promotion_bound = 1U;
    out_binding->unmeasured_cost_claim_bound = 1U;
    out_binding->executed_negative_mutation_bound = 1U;
    out_binding->pass199_successor_bound = 1U;
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
    memcpy(out_binding->accepted_merge_commit, witness->accepted_merge_commit, HHS_EXACT_PASS198_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i127_commit, witness->frozen_i127_commit, HHS_EXACT_PASS198_GIT_SHA_STRLEN);
    memcpy(out_binding->validated_repair_head, witness->validated_repair_head, HHS_EXACT_PASS198_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
