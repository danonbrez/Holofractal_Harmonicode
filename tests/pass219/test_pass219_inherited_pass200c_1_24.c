#include "hhs_pass219_inherited_pass200c_1_24.h"

#include <assert.h>
#include <string.h>

static HHSExactPass200CGuardedActiveWitnessV1 witness(void) {
    HHSExactPass200CGuardedActiveWitnessV1 w = {0};
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass200c_version();
    w.primary_pull_request = 140U;
    w.min_successful_canaries = 2U;
    w.min_canary_invocations = 12U;
    w.max_active_lease_invocations = 64U;
    w.lifecycle_test_count = 10U;
    w.measured_canary_invocations = 16U;
    w.measured_active_invocations = 7U;
    w.measured_active_candidate_returns = 6U;
    w.measured_active_reference_returns = 1U;
    w.measured_frontier_count = 5U;
    w.measured_hash72_event_count = 13U;
    w.pass200a_candidate_bundle_required = 1U;
    w.pass200b_completed_canary_evidence_required = 1U;
    w.pass200b_rollback_disqualifies_bundle = 1U;
    w.three_distinct_approval_principals_required = 1U;
    w.compiler_runtime_operations_capabilities_required = 1U;
    w.distinct_approval_receipts_required = 1U;
    w.approvals_frontier_evidence_bundle_expiry_bound = 1U;
    w.singleton_vm81_activation_receipt_required = 1U;
    w.exact_result_guard_every_invocation = 1U;
    w.exact_witness_guard_every_invocation = 1U;
    w.exact_replay_guard_every_invocation = 1U;
    w.mismatch_restores_reference = 1U;
    w.expiry_restores_reference = 1U;
    w.lease_exhaustion_restores_reference = 1U;
    w.explicit_rollback_restores_reference = 1U;
    w.durable_state_and_hash72_history = 1U;
    w.persisted_evidence_tamper_rejected = 1U;
    w.persisted_frontier_tamper_rejected = 1U;
    w.candidate_self_authorization = 0U;
    w.frozen_constraint_promotion = 0U;
    w.pass201_successor_preserved = 1U;
    w.pass219_new_active_admission_authority = 0U;
    w.pass219_new_canonical_mutation_authority = 0U;
    w.pass219_new_persistence_authority = 0U;
    w.pass219_new_hash72_clock = 0U;
    w.cxx_mutation_authority = 0U;
    w.vm81_mutation_authority = 0U;
    memcpy(w.primary_base_commit, "beff24168bb81b0b1459e325ebaad29b2252b980", 41U);
    memcpy(w.validated_executable_head, "828402a739744e4b12fb63d76a3923964d067c6f", 41U);
    memcpy(w.evidence_head_commit, "73fa715ac8aee578b81e053fae99594df0b34889", 41U);
    memcpy(w.accepted_merge_commit, "a7868be1d98345cc7641bb7f59b716667cf1808d", 41U);
    memcpy(w.frozen_i123_commit, "30e1ae3a278ee19c3c167d3659ed71ca2a016873", 41U);
    memcpy(w.contract_blob, "bc06fcab22c5bd857566c5560b9fd05b83bcdc75", 41U);
    memcpy(w.workflow_blob, "bd54ffaf0c00c1b993dfa7f1d7cc759752bc9776", 41U);
    memcpy(w.runtime_v1_blob, "4c61dd428996372a9d8170092efde0a21c391134", 41U);
    memcpy(w.production_projection_blob, "92f0bef25882c0885f769bff4570610601e820ea", 41U);
    memcpy(w.active_routes_blob, "4b08c4e183793836f667ebacb73602341b1d45c2", 41U);
    memcpy(w.contract_test_blob, "e6bd83499193ec5242ec0b04696bd7d423cebd4a", 41U);
    memcpy(w.production_validator_blob, "9c4f4b545cecf6e14dbe7aff050eed90f3368fe8", 41U);
    return w;
}

static void reject(HHSExactPass200CGuardedActiveWitnessV1 w) {
    HHSExactPass219InheritedPass200CBindingV1 binding = {0};
    assert(hhs_exact_pass219_bind_pass200c_guarded_active_admission(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

int main(void) {
    HHSExactPass200CGuardedActiveWitnessV1 w = witness();
    HHSExactPass219InheritedPass200CBindingV1 binding = {0};
    assert(hhs_exact_pass219_bind_pass200c_guarded_active_admission(&w, &binding) == HHS_EXACT_STATUS_OK);
    assert(binding.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(binding.pass_number == 200U && binding.pass_variant == 3U);
    assert(binding.continuous_exact_guard_bound == 1U);
    assert(binding.durable_state_read_only_bound == 1U);
    assert(binding.pass201_successor_bound == 1U);
    assert(binding.pass219_new_active_admission_authority == 0U);
    assert(binding.vm81_mutation_authority == 0U);

    w = witness(); w.pass200b_completed_canary_evidence_required = 0U; reject(w);
    w = witness(); w.pass200b_rollback_disqualifies_bundle = 0U; reject(w);
    w = witness(); w.three_distinct_approval_principals_required = 0U; reject(w);
    w = witness(); w.singleton_vm81_activation_receipt_required = 0U; reject(w);
    w = witness(); w.exact_result_guard_every_invocation = 0U; reject(w);
    w = witness(); w.exact_witness_guard_every_invocation = 0U; reject(w);
    w = witness(); w.exact_replay_guard_every_invocation = 0U; reject(w);
    w = witness(); w.mismatch_restores_reference = 0U; reject(w);
    w = witness(); w.persisted_evidence_tamper_rejected = 0U; reject(w);
    w = witness(); w.candidate_self_authorization = 1U; reject(w);
    w = witness(); w.frozen_constraint_promotion = 1U; reject(w);
    w = witness(); w.pass201_successor_preserved = 0U; reject(w);
    w = witness(); w.pass219_new_active_admission_authority = 1U; reject(w);
    w = witness(); w.pass219_new_canonical_mutation_authority = 1U; reject(w);
    w = witness(); w.pass219_new_persistence_authority = 1U; reject(w);
    w = witness(); w.pass219_new_hash72_clock = 1U; reject(w);
    w = witness(); w.vm81_mutation_authority = 1U; reject(w);
    w = witness(); w.accepted_merge_commit[0] = '0'; reject(w);

    return 0;
}
