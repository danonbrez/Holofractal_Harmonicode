#ifndef HHS_PASS219_INHERITED_PASS206_1_18_HPP
#define HHS_PASS219_INHERITED_PASS206_1_18_HPP

#include "hhs_pass219_inherited_pass206_1_18.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass206CumulativeEnforcement final {
public:
    explicit InheritedPass206CumulativeEnforcement(const HHSExactPass206CumulativeEnforcementWitnessV1& witness) noexcept {
        status_ = hhs_exact_pass219_bind_pass206_cumulative_enforcement(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.frozen_core_count == HHS_EXACT_PASS206_FROZEN_CORE_COUNT &&
               binding_.approved_successor_count == HHS_EXACT_PASS206_APPROVED_SUCCESSOR_COUNT &&
               binding_.single_vm81_authority_bound == 1U &&
               binding_.single_hash72_stream_bound == 1U &&
               binding_.enforcement_admitted_bound == 1U &&
               binding_.development_completion_bound == 1U &&
               binding_.canonical_main_pending_bound == 1U &&
               binding_.pass207_successor_bound == 1U &&
               binding_.no_new_mutation_authority_bound == 1U &&
               binding_.no_new_persistence_authority_bound == 1U &&
               binding_.no_new_hash72_clock_bound == 1U &&
               binding_.pass219_new_canonical_mutation_authority == 0U &&
               binding_.cxx_mutation_authority == 0U &&
               binding_.vm81_mutation_authority == 0U;
    }
    const HHSExactPass219InheritedPass206BindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass206BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass206CumulativeEnforcementWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass206CumulativeEnforcementWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass206BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass206BindingV1>);

}  // namespace hhs::rna

#endif
