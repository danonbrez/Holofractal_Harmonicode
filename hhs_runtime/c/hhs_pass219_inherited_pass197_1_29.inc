#include "../include/hhs_pass219_inherited_pass197_1_29.h"

#include <stddef.h>
#include <string.h>

static const char P197_BASE[] = "e3d6694e06edbe8f04c02d6b665301b34f6ec074";
static const char P197_REVIEWED_HEAD[] = "aeadabcce0ea178ad5b6a27001e109f349808dde";
static const char P197_ACCEPTED_MERGE[] = "2321a1f05a6da410034a31ca141e3919091bb09a";
static const char P197_FROZEN_I128[] = "c85b2b29cdf26d21912eb06b7d50323526944cc2";
static const char P197_REPAIRED_EXACT_BLOB[] = "96be2009ca46cbcab7633f6fae97a0bea7621abb";
static const char P197_REPAIRED_STATE_BLOB[] = "10c986063d5fa2503d732e6725bb3b8665372666";
static const char P197_REPAIRED_RUNTIME_BLOB[] = "6d86629bdf25bdb03890197475a12dbf9190c618";
static const char P197_REPAIRED_API_BLOB[] = "0325974ff78c097b010b297971c2243d4132af43";
static const char P197_REPAIRED_FRONTEND_BLOB[] = "f68cac28e29a29da99c4cb415778fb1c196a19f2";
static const char P197_REPAIRED_REGRESSION_BLOB[] = "1924e7c9eb3642087b6b2792ce75fded38dbee00";
static const char P197_REPAIRED_WORKFLOW_BLOB[] = "76786543a6bac5f0884c19e8226369ae8f47ff0c";

static uint32_t p197_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS197_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS197_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS197_VERSION_PATCH;
}

static int p197_git(const char value[HHS_EXACT_PASS197_GIT_SHA_STRLEN], const char *expected) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS197_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS197_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass197_version(void) { return p197_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass197_repaired_hydration_calibration(
    const HHSExactPass197RepairedHydrationCalibrationWitnessV1 *witness,
    HHSExactPass219InheritedPass197BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p197_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->primary_pull_request != HHS_EXACT_PASS197_PRIMARY_PR ||
        witness->review_finding_count != HHS_EXACT_PASS197_REVIEW_FINDING_COUNT ||
        witness->default_parameter_states != HHS_EXACT_PASS197_DEFAULT_STATES ||
        witness->default_admitted_states != HHS_EXACT_PASS197_DEFAULT_ADMITTED ||
        witness->default_rejected_states != HHS_EXACT_PASS197_DEFAULT_REJECTED ||
        witness->vm5184_address_comparisons != HHS_EXACT_PASS197_VM5184_COMPARISONS ||
        witness->pre_persistence_kernel_audit_required != 1U ||
        witness->fail_closed_hash72_authority != 1U ||
        witness->full_replay_required_for_closure != 1U ||
        witness->strict_rational_object_components != 1U ||
        witness->state_root_run_serialization != 1U ||
        witness->persisted_report_integrity_status_gate != 1U ||
        witness->bounded_synchronous_envelope != 1U ||
        witness->strict_exponent_ingress != 1U ||
        witness->duplicate_coordinate_rejection != 1U ||
        witness->closed_only_frontend_projection != 1U ||
        witness->pass198_successor_preserved != 1U ||
        witness->pass219_new_candidate_authority != 0U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p197_git(witness->historical_base_commit, P197_BASE) ||
        !p197_git(witness->historical_reviewed_head, P197_REVIEWED_HEAD) ||
        !p197_git(witness->accepted_merge_commit, P197_ACCEPTED_MERGE) ||
        !p197_git(witness->frozen_i128_commit, P197_FROZEN_I128) ||
        !p197_git(witness->repaired_exact_blob, P197_REPAIRED_EXACT_BLOB) ||
        !p197_git(witness->repaired_state_blob, P197_REPAIRED_STATE_BLOB) ||
        !p197_git(witness->repaired_runtime_blob, P197_REPAIRED_RUNTIME_BLOB) ||
        !p197_git(witness->repaired_api_blob, P197_REPAIRED_API_BLOB) ||
        !p197_git(witness->repaired_frontend_blob, P197_REPAIRED_FRONTEND_BLOB) ||
        !p197_git(witness->repaired_regression_blob, P197_REPAIRED_REGRESSION_BLOB) ||
        !p197_git(witness->repaired_workflow_blob, P197_REPAIRED_WORKFLOW_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p197_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS197_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->historical_squash_identity_bound = 1U;
    out_binding->inherited_defects_repaired = 1U;
    out_binding->exact_ingress_bound = 1U;
    out_binding->pre_persistence_kernel_audit_bound = 1U;
    out_binding->full_replay_closure_bound = 1U;
    out_binding->state_root_serialization_bound = 1U;
    out_binding->verified_status_bound = 1U;
    out_binding->synchronous_envelope_bound = 1U;
    out_binding->frontend_projection_bound = 1U;
    out_binding->pass198_successor_bound = 1U;
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
    memcpy(out_binding->accepted_merge_commit, witness->accepted_merge_commit, HHS_EXACT_PASS197_GIT_SHA_STRLEN);
    memcpy(out_binding->frozen_i128_commit, witness->frozen_i128_commit, HHS_EXACT_PASS197_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
