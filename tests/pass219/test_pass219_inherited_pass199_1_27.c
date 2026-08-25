#include "hhs_pass219_inherited_pass199_1_27.h"

#include <assert.h>
#include <string.h>

static HHSExactPass199RepairedCalibrationWitnessV3 witness(void) {
    HHSExactPass199RepairedCalibrationWitnessV3 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass199_version();
    w.primary_pull_request = 137U;
    w.production_states = 405U;
    w.production_branch_jobs = 810U;
    w.production_admitted = 320U;
    w.production_rejected = 85U;
    w.production_vm5184_comparisons = 1658880U;
    w.replayed_branch_jobs = 810U;
    w.singleton_commit_count = 1U;
    w.pass198_verification_count = 1U;
    w.max_claim_batch_size = 64U;
    w.review_finding_count = 6U;
    w.full_replay_required = 1U;
    w.full_replay_executed = 1U;
    w.deterministic_replay_required = 1U;
    w.pass198_single_verification_required = 1U;
    w.report_identity_excludes_pass198_attachment = 1U;
    w.existing_commit_receipt_continuity_required = 1U;
    w.stale_worker_recovery_before_slot_validation = 1U;
    w.durable_completion_total_reconciled = 1U;
    w.canonical_gate_payload_diversity_required = 1U;
    w.pass200a_successor_preserved = 1U;
    strcpy(w.historical_base_commit, "df50f29fda77d6093d3af40dd1e3896523c4aab5");
    strcpy(w.historical_reviewed_head, "98cda07e391bb19559670be0ed6a4ce073346cd8");
    strcpy(w.accepted_merge_commit, "426fe7786abff2e1e4688222a600f5ab39d14a5a");
    strcpy(w.frozen_i126_commit, "fca09c16d2e9008de5cd9a09347e14de695e4ef3");
    strcpy(w.validated_repair_head, "c2626fd4886b9e98e511c739b806dfc46863878d");
    strcpy(w.contract_blob, "5ecfcdf3a97df85a896f3948d53b3f47fc349abf");
    strcpy(w.fabric_v1_blob, "d89f3e0e53b3ad21394ddfe95fede3cbc5c3ef2b");
    strcpy(w.runtime_v1_blob, "81e6d87a04a7a23d5b1531a27208c18610dd6647");
    strcpy(w.runtime_v2_blob, "fba8a00f5402ab7517edc21cb731ccbe488a226c");
    strcpy(w.historical_production_blob, "c2e90f47b6f0a8996e5f5d26ba563f1a53ed17aa");
    strcpy(w.historical_workflow_blob, "4d290a9d22b5e1afebd065a51c7c493028b7e5c5");
    strcpy(w.historical_routes_blob, "196832b63877402bd8630a847bba5e214814055f");
    strcpy(w.historical_fabric_test_blob, "9b124554ab084119e034ecbc21c2b273b9a1ae4a");
    strcpy(w.historical_production_test_blob, "8038c45cc555df2aaa62aa817ef5755c0b977617");
    strcpy(w.historical_restart_blob, "63ef3add2fc334cee11ac012205941bf9897d76e");
    strcpy(w.repaired_runtime_v3_blob, "9e0d159f7a3ed5e4a706cb147c50a82949dcd6be");
    strcpy(w.repaired_production_blob, "50f9b9a4530a180e4a29942334f6faf4d8099776");
    strcpy(w.repaired_workflow_blob, "2e0a1b9319893a0a2faeb95f34f9886b6e08590c");
    strcpy(w.repaired_regression_blob, "07b4c72039421765746d302a8153c939b2b57862");
    strcpy(w.repaired_projection_test_blob, "8e5cb84788f00a573f025b14d5fe1ba1d72a5024");
    return w;
}

int main(void) {
    HHSExactPass199RepairedCalibrationWitnessV3 w = witness();
    HHSExactPass219InheritedPass199BindingV1 b;
    assert(hhs_exact_pass219_bind_pass199_repaired_calibration_authority(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.pass_number == 199U);
    assert(b.inherited_defects_repaired == 1U);
    assert(b.full_replay_bound == 1U);
    assert(b.single_pass198_verification_bound == 1U);
    assert(b.report_identity_compatibility_bound == 1U);
    assert(b.commit_receipt_continuity_bound == 1U);
    assert(b.stale_worker_recovery_bound == 1U);
    assert(b.durable_completion_bound == 1U);
    assert(b.canonical_gate_diversity_bound == 1U);
    assert(b.pass200a_successor_bound == 1U);
    assert(b.pass219_new_candidate_authority == 0U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.pass219_new_persistence_authority == 0U);
    assert(b.pass219_new_hash72_clock == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);

    w.full_replay_executed = 0U;
    assert(hhs_exact_pass219_bind_pass199_repaired_calibration_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.pass198_verification_count = 2U;
    assert(hhs_exact_pass219_bind_pass199_repaired_calibration_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.pass219_new_candidate_authority = 1U;
    assert(hhs_exact_pass219_bind_pass199_repaired_calibration_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
