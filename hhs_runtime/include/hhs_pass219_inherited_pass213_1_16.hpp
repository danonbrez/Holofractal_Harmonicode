#ifndef HHS_PASS219_INHERITED_PASS213_1_16_HPP
#define HHS_PASS219_INHERITED_PASS213_1_16_HPP

#include "hhs_pass219_inherited_pass213_1_16.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass213CompiledROMAuthority final {
public:
    explicit InheritedPass213CompiledROMAuthority(
        const HHSExactPass213ClosureWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass213_compiled_rom_authority(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.terminal_closure_bound == 1U &&
               binding_.governed_native_dispatch_bound == 1U &&
               binding_.raw_native_dispatch_bypass_forbidden == 1U;
    }
    bool inherited_governed_mutation_authority() const noexcept {
        return wired() &&
               binding_.inherited_governed_canonical_mutation_authority == 1U &&
               binding_.pass219_new_mutation_authority == 0U &&
               binding_.cxx_mutation_authority == 0U &&
               binding_.vm81_direct_mutation_authority == 0U;
    }
    const HHSExactPass219InheritedPass213BindingV1& record() const noexcept {
        return binding_;
    }

private:
    HHSExactPass219InheritedPass213BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass213ClosureWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass213ClosureWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass213BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass213BindingV1>);

}  // namespace hhs::rna

#endif
