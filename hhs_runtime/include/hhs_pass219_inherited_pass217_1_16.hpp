#ifndef HHS_PASS219_INHERITED_PASS217_1_16_HPP
#define HHS_PASS219_INHERITED_PASS217_1_16_HPP

#include "hhs_pass219_inherited_pass217_1_16.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass217Closure final {
public:
    explicit InheritedPass217Closure(
        const HHSExactPass217CumulativeClosureWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass217_cumulative_closure(
            &witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.cumulative_closure_bound == 1U &&
               binding_.canonical_execution_reachable == 1U;
    }
    bool all_required_authorities_nonbypassable() const noexcept {
        return wired() && binding_.all_required_authorities_nonbypassable == 1U;
    }
    bool genesis_rom_promotion_claimed() const noexcept {
        return binding_.genesis_rom_promotion_claimed == 1U;
    }
    const HHSExactPass219InheritedPass217BindingV1& record() const noexcept {
        return binding_;
    }

private:
    HHSExactPass219InheritedPass217BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass217CumulativeClosureWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass217CumulativeClosureWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass217BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass217BindingV1>);

}  // namespace hhs::rna

#endif
