#ifndef HHS_PASS219_INHERITED_PASS215_1_16_HPP
#define HHS_PASS219_INHERITED_PASS215_1_16_HPP

#include "hhs_pass219_inherited_pass215_1_16.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass215TerminalClosure final {
public:
    explicit InheritedPass215TerminalClosure(
        const HHSExactPass215TerminalClosureWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass215_terminal_closure(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.terminal_closure_bound == 1U &&
               binding_.exact_checkpoint_reuse_bound == 1U;
    }
    bool bounded_profile_only() const noexcept {
        return wired() && binding_.bounded_profile_only == 1U;
    }
    bool broader_generation_authority_promoted() const noexcept {
        return binding_.broader_generation_authority_promoted == 1U;
    }
    const HHSExactPass219InheritedPass215BindingV1& record() const noexcept {
        return binding_;
    }

private:
    HHSExactPass219InheritedPass215BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass215TerminalClosureWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass215TerminalClosureWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass215BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass215BindingV1>);

}  // namespace hhs::rna

#endif
