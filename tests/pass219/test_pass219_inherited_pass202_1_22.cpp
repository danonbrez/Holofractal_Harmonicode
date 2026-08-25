#include "hhs_pass219_inherited_pass202_1_22.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass202GuardedDeploymentWitnessV1 witness() {
    HHSExactPass202GuardedDeploymentWitnessV1 w{};
    w.struct_size = static_cast<uint32_t>(sizeof(w));
    w.version = hhs_exact_pass219_inherited_pass202_version();
    w.primary_pull_request = 143U;
    w.bootstrap_pull_request = 144U;
    w.initial_contract_test_count = 5U;
    w.bootstrap_contract_test_count = 6U;
    w.main_only_production_source = 1U;
    w.trusted_label_author_gate = 1U;
    w.same_repository_pull_request_required = 1U;
    w.detached_candidate_validation = 1U;
    w.fast_forward_only_promotion = 1U;
    w.post_promotion_health_required = 1U;
    w.rollback_to_exact_previous_commit = 1U;
    w.durable_jsonl_receipts = 1U;
    w.bounded_singleton_timer = 1U;
    w.host_local_drift_blocked_historically = 1U;
    w.bootstrap_dry_run_required = 1U;
    w.explicit_operator_enable_required = 1U;
    w.guarded_ci_blob_preserved = 1U;
    w.service_timer_blobs_preserved = 1U;
    w.successor_hardening_verified = 1U;
    w.host_drift_preservation_verified = 1U;
    w.runtime_os_bundle_sha_bound = 1U;
    w.prebuilt_bundle_required_for_production = 1U;
    w.install_promotion_default_disabled = 1U;
    w.recovery_receipt_gated = 1U;
    w.pass203_successor_preserved = 1U;
    std::strcpy(w.primary_base_commit, "bdf19276b0974481bd69d70ca1154f284f238e48");
    std::strcpy(w.primary_head_commit, "1eb9326f8024b37b9fc1425d910bc20cae50abbb");
    std::strcpy(w.primary_merge_commit, "33ce89c7328180eb98d59f72df43f3036cf1edab");
    std::strcpy(w.bootstrap_head_commit, "8a8f1eaefa940f9416430f2746014e1716ddd23b");
    std::strcpy(w.bootstrap_merge_commit, "83b6fd89cd8adb1962aeb159917fe24ee4485441");
    std::strcpy(w.historical_guarded_ci_blob, "e6b4e7c7cda8a64ef59151eae0e33ff1a70c6cd4");
    std::strcpy(w.historical_updater_blob, "b1ad8ced814c8c58d3365c4f45cbb0cd338fb564");
    std::strcpy(w.historical_env_blob, "2cf1d20f60d26d1b476ebd268fdc85b1db1a0764");
    std::strcpy(w.historical_installer_blob, "97ab585e3e96122cbaded47e1a436fc0e143bac1");
    std::strcpy(w.historical_service_blob, "1cc1dce920213df7c0a5f1ee4e9823a9dc727ec5");
    std::strcpy(w.historical_timer_blob, "3296ee9787544542697d3915e01569562ef30046");
    std::strcpy(w.historical_validator_blob, "82250c50fa9d20a82d0b957d2637398760b1c416");
    std::strcpy(w.historical_contract_test_blob, "709afe1c0d612ad91744a5cd71cb87d8a313aad6");
    std::strcpy(w.frozen_i121_commit, "94a100766c582c83fa3e4f7cb815c08b0eacfa1a");
    std::strcpy(w.current_updater_blob, "c1815c56e5bceeca2a840c5a693bd22d6e85ef84");
    std::strcpy(w.current_env_blob, "7890657593b5d4dd03e4cf5eb2c4c1c7ba25e519");
    std::strcpy(w.current_installer_blob, "93dfbe6cc3a789de82b5249f32a129a31306aeb5");
    std::strcpy(w.current_validator_blob, "729d8e571160239094aaef612a17d039f310ca03");
    std::strcpy(w.current_runtime_os_bundle_blob, "23afbf9c99d77f57acd7334d767c483572d64e0a");
    return w;
}

int main() {
    auto w = witness();
    hhs::rna::InheritedPass202GuardedDeployment binding(w);
    assert(binding.status() == HHS_EXACT_STATUS_OK);
    assert(binding.wired());
    assert(binding.record().pass_number == 202U);
    assert(binding.record().dry_run_bootstrap_bound == 1U);
    assert(binding.record().runtime_os_bundle_boundary_bound == 1U);

    w = witness();
    w.explicit_operator_enable_required = 0U;
    hhs::rna::InheritedPass202GuardedDeployment rejected(w);
    assert(rejected.status() == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(!rejected.wired());
    return 0;
}
