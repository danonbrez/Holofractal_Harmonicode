#ifndef HHS_PASS219_INHERITED_PASS204_1_20_HPP
#define HHS_PASS219_INHERITED_PASS204_1_20_HPP

#include "hhs_pass219_inherited_pass204_1_20.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass204OpenCloudMainframe final {
public:
    explicit InheritedPass204OpenCloudMainframe(
        const HHSExactPass204OpenCloudWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass204_open_cloud_mainframe(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.pass_number == HHS_EXACT_PASS219_INHERITED_PASS204_NUMBER &&
               binding_.universal_declarations_bound == 1U &&
               binding_.zero_binding_gaps_bound == 1U &&
               binding_.fixed_sandbox_policy_bound == 1U &&
               binding_.capability_free_recall_bound == 1U &&
               binding_.immutable_history_boundary_bound == 1U &&
               binding_.canonical_core_abi_bound == 1U &&
               binding_.project_native_durable_job_bound == 1U &&
               binding_.inherited_pass204_persistence_bound == 1U &&
               binding_.pass203_inheritance_bound == 1U &&
               binding_.pass205_successor_bound == 1U &&
               binding_.no_new_canonical_mutation_authority_bound == 1U &&
               binding_.no_new_persistence_authority_bound == 1U &&
               binding_.no_new_hash72_clock_bound == 1U &&
               binding_.pass219_new_canonical_mutation_authority == 0U &&
               binding_.pass219_new_persistence_authority == 0U &&
               binding_.pass219_new_hash72_clock == 0U &&
               binding_.cxx_mutation_authority == 0U &&
               binding_.vm81_mutation_authority == 0U;
    }

    const HHSExactPass219InheritedPass204BindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass204BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass204OpenCloudWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass204OpenCloudWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass204BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass204BindingV1>);

}  // namespace hhs::rna

#endif
