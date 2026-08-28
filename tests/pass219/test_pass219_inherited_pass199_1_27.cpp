#include "hhs_pass219_inherited_pass199_1_27.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass199RepairedCalibrationWitnessV3 make_witness() {
    HHSExactPass199RepairedCalibrationWitnessV3 w{};
    w.struct_size = static_cast<uint32_t>(sizeof(w));
    w.version = hhs::rna::InheritedPass199RepairedCalibrationAuthority::version();
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
    std::strcpy(w.historical_base_commit, "df50f29fda77d6093d3af40dd1e3896523c4aab5");
    std::strcpy(w.historical_reviewed_head, "98cda07e391bb19559670be0ed6a4ce073346cd8");
    std::strcpy(w.accepted_merge_commit, "426fe7786abff2e1e4688222a600f5ab39d14a5a");
    std::strcpy(w.frozen_i126_commit, "fca09c16d2e9008de5cd9a09347e14de695e4ef3");
    std::strcpy(w.validated_repair_head, "c2626fd4886b9e98e511c739b806dfc46863878d");
    std::strcpy(w.contract_blob, "5ecfcdf3a97df85a896f3948d53b3f47fc349abf");
    std::strcpy(w.fabric_v1_blob, "d89f3e0e53b3ad21394ddfe95fede3cbc5c3ef2b");
    std::strcpy(w.runtime_v1_blob, "81e6d87a04a7a23d5b1531a27208c18610dd6647");
    std::strcpy(w.runtime_v2_blob, "fba8a00f5402ab7517edc21cb731ccbe488a226c");
    std::strcpy(w.historical_production_blob, "c2e90f47b6f0a8996e5f5d26ba563f1a53ed17aa");
    std::strcpy(w.historical_workflow_blob, "4d290a9d22b5e1afebd065a51c7c493028b7e5c5");
    std::strcpy(w.historical_routes_blob, "196832b63877402bd8630a847bba5e214814055f");
    std::strcpy(w.historical_fabric_test_blob, "9b124554ab084119e034ecbc21c2b273b9a1ae4a");
    std::strcpy(w.historical_production_test_blob, "8038c45cc555df2aaa62aa817ef5755c0b977617");
    std::strcpy(w.historical_restart_blob, "63ef3add2fc334cee11ac012205941bf9897d76e");
    std::strcpy(w.repaired_runtime_v3_blob, "9e0d159f7a3ed5e4a706cb147c50a82949dcd6be");
    std::strcpy(w.repaired_production_blob, "50f9b9a4530a180e4a29942334f6faf4d8099776");
    std::strcpy(w.repaired_workflow_blob, "2e0a1b9319893a0a2faeb95f34f9886b6e08590c");
    std::strcpy(w.repaired_regression_blob, "07b4c72039421765746d302a8153c939b2b57862");
    std::strcpy(w.repaired_projection_test_blob, "8e5cb84788f00a573f025b14d5fe1ba1d72a5024");
    return w;
}

int main() {
    using Surface = hhs::rna::InheritedPass199RepairedCalibrationAuthority;
    static_assert(!Surface::mutation_authority());
    static_assert(!Surface::persistence_authority());
    static_assert(!Surface::hash72_clock_authority());
    static_assert(!Surface::vm81_mutation_authority());
    static_assert(!Surface::candidate_authority());
    static_assert(!Surface::pass198_mutation_authority());
    static_assert(Surface::singleton_vm81_authority_remains_inherited());
    static_assert(Surface::full_replay_required_for_closure());

    auto w = make_witness();
    HHSExactPass219InheritedPass199BindingV1 b{};
    assert(Surface::bind(w, b) == HHS_EXACT_STATUS_OK);
    assert(b.inherited_defects_repaired == 1U);
    assert(b.pass200a_successor_bound == 1U);
    assert(b.pass219_new_candidate_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);
    return 0;
}
