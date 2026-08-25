#ifndef HHS_PASS219_INHERITED_PASS200B_1_25_HPP
#define HHS_PASS219_INHERITED_PASS200B_1_25_HPP

#include "hhs_pass219_inherited_pass200b_1_25.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass200BGovernedCanaryAdmission final {
public:
    explicit InheritedPass200BGovernedCanaryAdmission(
        const HHSExactPass200BGovernedCanaryWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass200b_governed_canary_admission(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.pass_number == HHS_EXACT_PASS219_INHERITED_PASS200B_NUMBER &&
               binding_.pass_variant == HHS_EXACT_PASS219_INHERITED_PASS200B_VARIANT &&
               binding_.historical_squash_identity_bound == 1U &&
               binding_.immutable_source_identity_bound == 1U &&
               binding_.pass200a_shadow_gate_bound == 1U &&
               binding_.dual_approval_and_activation_bound == 1U &&
               binding_.bounded_integer_selection_bound == 1U &&
               binding_.exact_comparison_bound == 1U &&
               binding_.rollback_and_exhaustion_bound == 1U &&
               binding_.durable_state_read_only_bound == 1U &&
               binding_.pass200c_successor_bound == 1U &&
               binding_.no_new_canary_admission_authority_bound == 1U &&
               binding_.no_new_canonical_mutation_authority_bound == 1U &&
               binding_.no_new_persistence_authority_bound == 1U &&
               binding_.no_new_hash72_clock_bound == 1U &&
               binding_.pass219_new_canary_admission_authority == 0U &&
               binding_.pass219_new_canonical_mutation_authority == 0U &&
               binding_.pass219_new_persistence_authority == 0U &&
               binding_.pass219_new_hash72_clock == 0U &&
               binding_.cxx_mutation_authority == 0U &&
               binding_.vm81_mutation_authority == 0U;
    }

    const HHSExactPass219InheritedPass200BBindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass200BBindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass200BGovernedCanaryWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass200BGovernedCanaryWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass200BBindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass200BBindingV1>);

}  // namespace hhs::rna

#endif
