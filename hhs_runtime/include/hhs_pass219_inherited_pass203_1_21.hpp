#ifndef HHS_PASS219_INHERITED_PASS203_1_21_HPP
#define HHS_PASS219_INHERITED_PASS203_1_21_HPP

#include "hhs_pass219_inherited_pass203_1_21.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass203IntegratedMainframe final {
public:
    explicit InheritedPass203IntegratedMainframe(
        const HHSExactPass203IntegratedMainframeWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass203_integrated_mainframe(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.pass_number == HHS_EXACT_PASS219_INHERITED_PASS203_NUMBER &&
               binding_.historical_mainframe_bound == 1U &&
               binding_.fail_closed_binding_gaps_bound == 1U &&
               binding_.exact_execution_policy_bound == 1U &&
               binding_.renderer_subauthority_bound == 1U &&
               binding_.renderer_read_only_constants_bound == 1U &&
               binding_.native_frame_identity_bound == 1U &&
               binding_.pass202_inheritance_bound == 1U &&
               binding_.pass204_successor_bound == 1U &&
               binding_.pass204_standalone_replay_bound == 1U &&
               binding_.dynamic_catalog_growth_compatible_bound == 1U &&
               binding_.no_new_execution_authority_bound == 1U &&
               binding_.no_new_canonical_mutation_authority_bound == 1U &&
               binding_.no_new_persistence_authority_bound == 1U &&
               binding_.no_new_hash72_clock_bound == 1U &&
               binding_.pass219_new_execution_authority == 0U &&
               binding_.pass219_new_canonical_mutation_authority == 0U &&
               binding_.pass219_new_persistence_authority == 0U &&
               binding_.pass219_new_hash72_clock == 0U &&
               binding_.cxx_mutation_authority == 0U &&
               binding_.vm81_mutation_authority == 0U;
    }

    const HHSExactPass219InheritedPass203BindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass203BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass203IntegratedMainframeWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass203IntegratedMainframeWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass203BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass203BindingV1>);

}  // namespace hhs::rna

#endif
