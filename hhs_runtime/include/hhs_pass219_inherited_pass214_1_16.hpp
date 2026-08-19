#ifndef HHS_PASS219_INHERITED_PASS214_1_16_HPP
#define HHS_PASS219_INHERITED_PASS214_1_16_HPP

#include "hhs_pass219_inherited_pass214_1_16.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass214BenchmarkAuthority final {
public:
    explicit InheritedPass214BenchmarkAuthority(
        const HHSExactPass214BenchmarkAuthorityWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass214_benchmark_authority(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.terminal_benchmark_authority_bound == 1U &&
               binding_.eight_root_terminal_closure_bound == 1U &&
               binding_.pass213_gates_preserved == 1U;
    }
    bool semantic_reuse_bound() const noexcept {
        return wired() && binding_.semantic_equivalence_reuse_bound == 1U;
    }
    bool exact_vm81_kernel_bound() const noexcept {
        return wired() && binding_.exact_vm81_kernel_rebind_bound == 1U;
    }
    const HHSExactPass219InheritedPass214BindingV1& record() const noexcept {
        return binding_;
    }

private:
    HHSExactPass219InheritedPass214BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass214BenchmarkAuthorityWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass214BenchmarkAuthorityWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass214BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass214BindingV1>);

}  // namespace hhs::rna

#endif
