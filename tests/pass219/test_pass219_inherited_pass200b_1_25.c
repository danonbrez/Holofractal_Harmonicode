#include "hhs_pass219_inherited_pass200b_1_25.h"

#include <assert.h>
#include <string.h>

static HHSExactPass200BGovernedCanaryWitnessV1 witness(void) {
    HHSExactPass200BGovernedCanaryWitnessV1 w = {0};
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass200b_version();
    w.primary_pull_request = 139U;
    w.max_canary_invocations = 64U;
    w.lifecycle_test_count = 8U;
    w.measured_pass200a_envelopes = 4U;
    w.measured_pass200a_bundles = 4U;
    w.measured_pass200a_shadow_matches = 4U;
    w.measured_canary_frontiers = 2U;
    w.measured_singleton_activations = 2U;
    w.measured_invocations = 9U;
    w.measured_candidate_returns = 2U;
    w.measured_reference_returns = 7U;
    w.measured_rollback_frontiers = 1U;
    w.measured_exhausted_frontiers = 1U;
    w.measured_frontier_count = 5U;
    w.measured_hash72_event_count = 14U;
    w.pass200a_closed_proof_required = 1U;
    w.compiler_candidate_required = 1U;
    w.shadow_mode_required = 1U;
    w.persisted_exact_shadow_match_required = 1U;
    w.exactly_two_approvals_required = 1U;
    w.distinct_approval_principals_required = 1U;
    w.distinct_approval_receipts_required = 1U;
    w.compiler_runtime_capabilities_required = 1U;
    w.approval_bundle_frontier_expiry_receipt_bound = 1U;
    w.singleton_vm81_activation_receipt_required = 1U;
    w.deterministic_integer_selection_required = 1U;
    w.exact_result_match_required = 1U;
    w.exact_witness_match_required = 1U;
    w.exact_replay_match_required = 1U;
    w.mismatch_restores_reference = 1U;
    w.expiry_restores_reference = 1U;
    w.exhaustion_restores_reference = 1U;
    w.explicit_rollback_restores_reference = 1U;
    w.durable_state_and_hash72_history = 1U;
    w.persisted_frontier_tamper_rejected = 1U;
    w.event_chain_tamper_rejected = 1U;
    w.candidate_self_authorization = 0U;
    w.automatic_active_promotion = 0U;
    w.frozen_constraint_promotion = 0U;
    w.candidate_canonical_commit = 0U;
    w.pass200c_successor_preserved = 1U;
    w.pass219_new_canary_admission_authority = 0U;
    w.pass219_new_canonical_mutation_authority = 0U;
    w.pass219_new_persistence_authority = 0U;
    w.pass219_new_hash72_clock = 0U;
    w.cxx_mutation_authority = 0U;
    w.vm81_mutation_authority = 0U;
    memcpy(w.primary_base_commit, "483a18b618dbe51b31025eeb15a8a6435e4040c5", 41U);
    memcpy(w.validated_executable_head, "f13eed02531e77737562b23fb207962c0744ed0d", 41U);
    memcpy(w.evidence_head_commit, "07f12ba91d78d28f0d9f73ec54e3167d4f1fa5b3", 41U);
    memcpy(w.accepted_merge_commit, "eb7dd08b8bc52451c2e179b68949097ade5499af", 41U);
    memcpy(w.frozen_i124_commit, "18ca57da270785483679e36a4d861c2002c69323", 41U);
    memcpy(w.contract_blob, "1e442f002bd0936090a5b7154150021e0a543948", 41U);
    memcpy(w.workflow_blob, "e0b2335d509839f9175c5e6a08eef6bbbd18d437", 41U);
    memcpy(w.runtime_v1_blob, "8034383ec6dcad463c45296c9eeb241f3e1123c5", 41U);
    memcpy(w.production_projection_blob, "67e79a10250bfa3e9678937d28ed4bc22fed9937", 41U);
    memcpy(w.canary_routes_blob, "abb2bee87c7ad12e0d3e441840bdb0643d425b05", 41U);
    memcpy(w.contract_test_blob, "ad843727f95b517c6f9c77b2338434c6605ba5d0", 41U);
    memcpy(w.visual_panel_blob, "def9ff882023c310ffd1ab3ff0d040115f2a76b2", 41U);
    memcpy(w.restart_record_blob, "435fd4f65b0d9f423e3ec6ec1a155f4d35948c13", 41U);
    return w;
}

static void reject(HHSExactPass200BGovernedCanaryWitnessV1 w) {
    HHSExactPass219InheritedPass200BBindingV1 binding = {0};
    assert(hhs_exact_pass219_bind_pass200b_governed_canary_admission(&w, &binding) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

int main(void) {
    HHSExactPass200BGovernedCanaryWitnessV1 w = witness();
    HHSExactPass219InheritedPass200BBindingV1 binding = {0};
    assert(hhs_exact_pass219_bind_pass200b_governed_canary_admission(&w, &binding) == HHS_EXACT_STATUS_OK);
    assert(binding.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(binding.pass_number == 200U && binding.pass_variant == 2U);
    assert(binding.pass200a_shadow_gate_bound == 1U);
    assert(binding.dual_approval_and_activation_bound == 1U);
    assert(binding.bounded_integer_selection_bound == 1U);
    assert(binding.exact_comparison_bound == 1U);
    assert(binding.rollback_and_exhaustion_bound == 1U);
    assert(binding.durable_state_read_only_bound == 1U);
    assert(binding.pass200c_successor_bound == 1U);
    assert(binding.pass219_new_canary_admission_authority == 0U);
    assert(binding.vm81_mutation_authority == 0U);

    w = witness(); w.pass200a_closed_proof_required = 0U; reject(w);
    w = witness(); w.exactly_two_approvals_required = 0U; reject(w);
    w = witness(); w.distinct_approval_principals_required = 0U; reject(w);
    w = witness(); w.singleton_vm81_activation_receipt_required = 0U; reject(w);
    w = witness(); w.deterministic_integer_selection_required = 0U; reject(w);
    w = witness(); w.exact_result_match_required = 0U; reject(w);
    w = witness(); w.exact_witness_match_required = 0U; reject(w);
    w = witness(); w.exact_replay_match_required = 0U; reject(w);
    w = witness(); w.mismatch_restores_reference = 0U; reject(w);
    w = witness(); w.exhaustion_restores_reference = 0U; reject(w);
    w = witness(); w.persisted_frontier_tamper_rejected = 0U; reject(w);
    w = witness(); w.candidate_self_authorization = 1U; reject(w);
    w = witness(); w.automatic_active_promotion = 1U; reject(w);
    w = witness(); w.frozen_constraint_promotion = 1U; reject(w);
    w = witness(); w.candidate_canonical_commit = 1U; reject(w);
    w = witness(); w.pass200c_successor_preserved = 0U; reject(w);
    w = witness(); w.pass219_new_canary_admission_authority = 1U; reject(w);
    w = witness(); w.pass219_new_canonical_mutation_authority = 1U; reject(w);
    w = witness(); w.pass219_new_persistence_authority = 1U; reject(w);
    w = witness(); w.pass219_new_hash72_clock = 1U; reject(w);
    w = witness(); w.vm81_mutation_authority = 1U; reject(w);
    w = witness(); w.accepted_merge_commit[0] = '0'; reject(w);

    return 0;
}
