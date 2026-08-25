#include "hhs_pass219_inherited_pass200c_1_24.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass200CGuardedActiveWitnessV1 witness() {
    HHSExactPass200CGuardedActiveWitnessV1 w{};
    w.struct_size = static_cast<uint32_t>(sizeof(w));
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
    w.pass201_successor_preserved = 1U;
    std::strcpy(w.primary_base_commit, "beff24168bb81b0b1459e325ebaad29b2252b980");
    std::strcpy(w.validated_executable_head, "828402a739744e4b12fb63d76a3923964d067c6f");
    std::strcpy(w.evidence_head_commit, "73fa715ac8aee578b81e053fae99594df0b34889");
    std::strcpy(w.accepted_merge_commit, "a7868be1d98345cc7641bb7f59b716667cf1808d");
    std::strcpy(w.frozen_i123_commit, "30e1ae3a278ee19c3c167d3659ed71ca2a016873");
    std::strcpy(w.contract_blob, "bc06fcab22c5bd857566c5560b9fd05b83bcdc75");
    std::strcpy(w.workflow_blob, "bd54ffaf0c00c1b993dfa7f1d7cc759752bc9776");
    std::strcpy(w.runtime_v1_blob, "4c61dd428996372a9d8170092efde0a21c391134");
    std::strcpy(w.production_projection_blob, "92f0bef25882c0885f769bff4570610601e820ea");
    std::strcpy(w.active_routes_blob, "4b08c4e183793836f667ebacb73602341b1d45c2");
    std::strcpy(w.contract_test_blob, "e6bd83499193ec5242ec0b04696bd7d423cebd4a");
    std::strcpy(w.production_validator_blob, "9c4f4b545cecf6e14dbe7aff050eed90f3368fe8");
    return w;
}

int main() {
    auto good = witness();
    hhs::rna::InheritedPass200CGuardedActiveAdmission wired(good);
    assert(wired.status() == HHS_EXACT_STATUS_OK);
    assert(wired.wired());
    assert(wired.record().pass201_successor_bound == 1U);
    assert(wired.record().pass219_new_active_admission_authority == 0U);

    auto promoted = witness();
    promoted.frozen_constraint_promotion = 1U;
    hhs::rna::InheritedPass200CGuardedActiveAdmission reject_promotion(promoted);
    assert(reject_promotion.status() == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(!reject_promotion.wired());

    auto new_authority = witness();
    new_authority.pass219_new_active_admission_authority = 1U;
    hhs::rna::InheritedPass200CGuardedActiveAdmission reject_authority(new_authority);
    assert(reject_authority.status() == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(!reject_authority.wired());

    return 0;
}
