#ifndef HHS_PASS219_INHERITED_PASS202_1_22_HPP
#define HHS_PASS219_INHERITED_PASS202_1_22_HPP

#include "hhs_pass219_inherited_pass202_1_22.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass202GuardedDeployment final {
public:
    explicit InheritedPass202GuardedDeployment(
        const HHSExactPass202GuardedDeploymentWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass202_guarded_deployment(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.pass_number == HHS_EXACT_PASS219_INHERITED_PASS202_NUMBER &&
               binding_.historical_guarded_ci_bound == 1U &&
               binding_.dry_run_bootstrap_bound == 1U &&
               binding_.deployment_transition_bound == 1U &&
               binding_.exact_rollback_bound == 1U &&
               binding_.durable_receipt_boundary_bound == 1U &&
               binding_.successor_hardening_bound == 1U &&
               binding_.host_drift_preservation_bound == 1U &&
               binding_.runtime_os_bundle_boundary_bound == 1U &&
               binding_.pass203_successor_bound == 1U &&
               binding_.no_new_deployment_authority_bound == 1U &&
               binding_.no_new_canonical_mutation_authority_bound == 1U &&
               binding_.no_new_persistence_authority_bound == 1U &&
               binding_.no_new_hash72_clock_bound == 1U &&
               binding_.pass219_new_deployment_authority == 0U &&
               binding_.pass219_new_canonical_mutation_authority == 0U &&
               binding_.pass219_new_persistence_authority == 0U &&
               binding_.pass219_new_hash72_clock == 0U &&
               binding_.cxx_mutation_authority == 0U &&
               binding_.vm81_mutation_authority == 0U;
    }

    const HHSExactPass219InheritedPass202BindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass202BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass202GuardedDeploymentWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass202GuardedDeploymentWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass202BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass202BindingV1>);

}  // namespace hhs::rna

#endif
