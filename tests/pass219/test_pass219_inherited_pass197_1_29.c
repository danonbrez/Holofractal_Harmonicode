#include "hhs_pass219_inherited_pass197_1_29.h"

#include <assert.h>
#include <string.h>

static HHSExactPass197RepairedHydrationCalibrationWitnessV1 witness(void) {
    HHSExactPass197RepairedHydrationCalibrationWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass197_version();
    w.primary_pull_request = 133U;
    w.review_finding_count = 10U;
    w.default_parameter_states = 405U;
    w.default_admitted_states = 320U;
    w.default_rejected_states = 85U;
    w.vm5184_address_comparisons = 1658880U;
    w.pre_persistence_kernel_audit_required = 1U;
    w.fail_closed_hash72_authority = 1U;
    w.full_replay_required_for_closure = 1U;
    w.strict_rational_object_components = 1U;
    w.state_root_run_serialization = 1U;
    w.persisted_report_integrity_status_gate = 1U;
    w.bounded_synchronous_envelope = 1U;
    w.strict_exponent_ingress = 1U;
    w.duplicate_coordinate_rejection = 1U;
    w.closed_only_frontend_projection = 1U;
    w.pass198_successor_preserved = 1U;
    strcpy(w.historical_base_commit, "e3d6694e06edbe8f04c02d6b665301b34f6ec074");
    strcpy(w.historical_reviewed_head, "aeadabcce0ea178ad5b6a27001e109f349808dde");
    strcpy(w.accepted_merge_commit, "2321a1f05a6da410034a31ca141e3919091bb09a");
    strcpy(w.frozen_i128_commit, "c85b2b29cdf26d21912eb06b7d50323526944cc2");
    strcpy(w.repaired_exact_blob, "96be2009ca46cbcab7633f6fae97a0bea7621abb");
    strcpy(w.repaired_state_blob, "10c986063d5fa2503d732e6725bb3b8665372666");
    strcpy(w.repaired_runtime_blob, "6d86629bdf25bdb03890197475a12dbf9190c618");
    strcpy(w.repaired_api_blob, "0325974ff78c097b010b297971c2243d4132af43");
    strcpy(w.repaired_frontend_blob, "f68cac28e29a29da99c4cb415778fb1c196a19f2");
    strcpy(w.repaired_regression_blob, "1924e7c9eb3642087b6b2792ce75fded38dbee00");
    strcpy(w.repaired_workflow_blob, "76786543a6bac5f0884c19e8226369ae8f47ff0c");
    return w;
}

int main(void) {
    HHSExactPass197RepairedHydrationCalibrationWitnessV1 w = witness();
    HHSExactPass219InheritedPass197BindingV1 b;
    assert(hhs_exact_pass219_bind_pass197_repaired_hydration_calibration(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.pass_number == 197U);
    assert(b.inherited_defects_repaired == 1U);
    assert(b.pre_persistence_kernel_audit_bound == 1U);
    assert(b.full_replay_closure_bound == 1U);
    assert(b.state_root_serialization_bound == 1U);
    assert(b.pass198_successor_bound == 1U);
    assert(b.pass219_new_candidate_authority == 0U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.pass219_new_persistence_authority == 0U);
    assert(b.pass219_new_hash72_clock == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);

    w.full_replay_required_for_closure = 0U;
    assert(hhs_exact_pass219_bind_pass197_repaired_hydration_calibration(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.pass219_new_canonical_mutation_authority = 1U;
    assert(hhs_exact_pass219_bind_pass197_repaired_hydration_calibration(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.repaired_runtime_blob[0] = '0';
    assert(hhs_exact_pass219_bind_pass197_repaired_hydration_calibration(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
