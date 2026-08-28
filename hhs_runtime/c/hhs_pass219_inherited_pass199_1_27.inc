#include "../include/hhs_pass219_inherited_pass199_1_27.h"

#include <stddef.h>
#include <string.h>

static const char P199_BASE[] = "df50f29fda77d6093d3af40dd1e3896523c4aab5";
static const char P199_REVIEWED_HEAD[] = "98cda07e391bb19559670be0ed6a4ce073346cd8";
static const char P199_ACCEPTED_MERGE[] = "426fe7786abff2e1e4688222a600f5ab39d14a5a";
static const char P199_FROZEN_I126[] = "fca09c16d2e9008de5cd9a09347e14de695e4ef3";
static const char P199_VALIDATED_REPAIR_HEAD[] = "c2626fd4886b9e98e511c739b806dfc46863878d";
static const char P199_CONTRACT_BLOB[] = "5ecfcdf3a97df85a896f3948d53b3f47fc349abf";
static const char P199_FABRIC_V1_BLOB[] = "d89f3e0e53b3ad21394ddfe95fede3cbc5c3ef2b";
static const char P199_RUNTIME_V1_BLOB[] = "81e6d87a04a7a23d5b1531a27208c18610dd6647";
static const char P199_RUNTIME_V2_BLOB[] = "fba8a00f5402ab7517edc21cb731ccbe488a226c";
static const char P199_PRODUCTION_BLOB[] = "c2e90f47b6f0a8996e5f5d26ba563f1a53ed17aa";
static const char P199_WORKFLOW_BLOB[] = "4d290a9d22b5e1afebd065a51c7c493028b7e5c5";
static const char P199_ROUTES_BLOB[] = "196832b63877402bd8630a847bba5e214814055f";
static const char P199_FABRIC_TEST_BLOB[] = "9b124554ab084119e034ecbc21c2b273b9a1ae4a";
static const char P199_PRODUCTION_TEST_BLOB[] = "8038c45cc555df2aaa62aa817ef5755c0b977617";
static const char P199_RESTART_BLOB[] = "63ef3add2fc334cee11ac012205941bf9897d76e";
static const char P199_REPAIRED_V3_BLOB[] = "9e0d159f7a3ed5e4a706cb147c50a82949dcd6be";
static const char P199_REPAIRED_PRODUCTION_BLOB[] = "50f9b9a4530a180e4a29942334f6faf4d8099776";
static const char P199_REPAIRED_WORKFLOW_BLOB[] = "2e0a1b9319893a0a2faeb95f34f9886b6e08590c";
static const char P199_REPAIRED_REGRESSION_BLOB[] = "07b4c72039421765746d302a8153c939b2b57862";
static const char P199_REPAIRED_PROJECTION_TEST_BLOB[] = "8e5cb84788f00a573f025b14d5fe1ba1d72a5024";

static uint32_t p199_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS199_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS199_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS199_VERSION_PATCH;
}

static int p199_git(const char value[HHS_EXACT_PASS199_GIT_SHA_STRLEN], const char *expected) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS199_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS199_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass199_version(void) { return p199_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass199_repaired_calibration_authority(
    const HHSExactPass199RepairedCalibrationWitnessV3 *witness,
    HHSExactPass219InheritedPass199BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p199_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->primary_pull_request != HHS_EXACT_PASS199_PRIMARY_PR ||
        witness->production_states != HHS_EXACT_PASS199_PRODUCTION_STATES ||
        witness->production_branch_jobs != HHS_EXACT_PASS199_PRODUCTION_BRANCH_JOBS ||
        witness->production_admitted != HHS_EXACT_PASS199_PRODUCTION_ADMITTED ||
        witness->production_rejected != HHS_EXACT_PASS199_PRODUCTION_REJECTED ||
        witness->production_vm5184_comparisons != HHS_EXACT_PASS199_PRODUCTION_VM5184_COMPARISONS ||
        witness->replayed_branch_jobs != HHS_EXACT_PASS199_REPLAY_BRANCH_JOBS ||
        witness->singleton_commit_count != HHS_EXACT_PASS199_SINGLETON_COMMIT_COUNT ||
        witness->pass198_verification_count != HHS_EXACT_PASS199_PASS198_VERIFICATION_COUNT ||
        witness->max_claim_batch_size != HHS_EXACT_PASS199_MAX_CLAIM_BATCH_SIZE ||
        witness->review_finding_count != HHS_EXACT_PASS199_REVIEW_FINDING_COUNT ||
        witness->full_replay_required != 1U ||
        witness->full_replay_executed != 1U ||
        witness->deterministic_replay_required != 1U ||
        witness->pass198_single_verification_required != 1U ||
        witness->report_identity_excludes_pass198_attachment != 1U ||
        witness->existing_commit_receipt_continuity_required != 1U ||
        witness->stale_worker_recovery_before_slot_validation != 1U ||
        witness->durable_completion_total_reconciled != 1U ||
        witness->canonical_gate_payload_diversity_required != 1U ||
        witness->pass200a_successor_preserved != 1U ||
        witness->candidate_worker_is_authority != 0U ||
        witness->candidate_may_commit != 0U ||
        witness->pass198_mutation_authority != 0U ||
        witness->api_mutation_authority != 0U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p199_git(witness->historical_base_commit, P199_BASE) ||
        !p199_git(witness->historical_reviewed_head, P199_REVIEWED_HEAD) ||
        !p199_git(witness->accepted_merge_commit, P199_ACCEPTED_MERGE) ||
        !p199_git(witness->frozen_i126_commit, P199_FROZEN_I126) ||
        !p199_git(witness->validated_repair_head, P199_VALIDATED_REPAIR_HEAD) ||
        !p199_git(witness->contract_blob, P199_CONTRACT_BLOB) ||
        !p199_git(witness->fabric_v1_blob, P199_FABRIC_V1_BLOB) ||
        !p199_git(witness->runtime_v1_blob, P199_RUNTIME_V1_BLOB) ||
        !p199_git(witness->runtime_v2_blob, P199_RUNTIME_V2_BLOB) ||
        !p199_git(witness->historical_production_blob, P199_PRODUCTION_BLOB) ||
        !p199_git(witness->historical_workflow_blob, P199_WORKFLOW_BLOB) ||
        !p199_git(witness->historical_routes_blob, P199_ROUTES_BLOB) ||
        !p199_git(witness->historical_fabric_test_blob, P199_FABRIC_TEST_BLOB) ||
        !p199_git(witness->historical_production_test_blob, P199_PRODUCTION_TEST_BLOB) ||
        !p199_git(witness->historical_restart_blob, P199_RESTART_BLOB) ||
        !p199_git(witness->repaired_runtime_v3_blob, P199_REPAIRED_V3_BLOB) ||
        !p199_git(witness->repaired_production_blob, P199_REPAIRED_PRODUCTION_BLOB) ||
        !p199_git(witness->repaired_workflow_blob, P199_REPAIRED_WORKFLOW_BLOB) ||
        !p199_git(witness->repaired_regression_blob, P199_REPAIRED_REGRESSION_BLOB) ||
        !p199_git(witness->repaired_projection_test_blob, P199_REPAIRED_PROJECTION_TEST_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p199_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS199_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_squash_identity_bound = 1U;
    out_binding->inherited_defects_repaired = 1U;
    out_binding->production_totals_bound = 1U;
    out_binding->full_replay_bound = 1U;
    out_binding->single_pass198_verification_bound = 1U;
    out_binding->report_identity_compatibility_bound = 1U;
    out_binding->commit_receipt_continuity_bound = 1U;
    out_binding->stale_worker_recovery_bound = 1U;
    out_binding->durable_completion_bound = 1U;
    out_binding->canonical_gate_diversity_bound = 1U;
    out_binding->pass200a_successor_bound = 1U;
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
    memcpy(out_binding->accepted_merge_commit, witness->accepted_merge_commit, HHS_EXACT_PASS199_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i126_commit, witness->frozen_i126_commit, HHS_EXACT_PASS199_GIT_SHA_STRLEN);
    memcpy(out_binding->validated_repair_head, witness->validated_repair_head, HHS_EXACT_PASS199_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
