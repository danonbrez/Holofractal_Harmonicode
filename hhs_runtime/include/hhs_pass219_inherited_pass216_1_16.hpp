#ifndef HHS_PASS219_INHERITED_PASS216_1_16_HPP
#define HHS_PASS219_INHERITED_PASS216_1_16_HPP

#include "hhs_pass219_inherited_pass216_1_16.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass216Alignment final {
public:
    explicit InheritedPass216Alignment(
        const HHSExactPass216AlignmentWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass216_alignment(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.contract_alignment_bound == 1U &&
               binding_.pass215_terminal_reference_bound == 1U;
    }
    bool runtime_optimization_implementation_claimed() const noexcept {
        return binding_.runtime_optimization_implementation_claimed == 1U;
    }
    bool runtime_optimization_roadmap_complete() const noexcept {
        return binding_.runtime_optimization_roadmap_complete == 1U;
    }
    bool dependency_scoped_validation_bound() const noexcept {
        return wired() && binding_.dependency_scoped_validation_bound == 1U;
    }
    const HHSExactPass219InheritedPass216BindingV1& record() const noexcept {
        return binding_;
    }

private:
    HHSExactPass219InheritedPass216BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass216AlignmentWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass216AlignmentWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass216BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass216BindingV1>);

}  // namespace hhs::rna

#endif
