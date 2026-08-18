#ifndef HHS_PASS219_INHERITED_PASS212_1_16_HPP
#define HHS_PASS219_INHERITED_PASS212_1_16_HPP

#include "hhs_pass219_inherited_pass212_1_16.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass212FullHydrationRecovery final {
public:
    explicit InheritedPass212FullHydrationRecovery(
        const HHSExactPass212RecoveryWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass212_full_hydration_recovery(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.full_hydration_authority_bound == 1U &&
               binding_.physical_erasure_recovery_bound == 1U &&
               binding_.pass213_recovery_successor_bound == 1U;
    }
    const HHSExactPass219InheritedPass212BindingV1& record() const noexcept {
        return binding_;
    }

private:
    HHSExactPass219InheritedPass212BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass212RecoveryWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass212RecoveryWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass212BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass212BindingV1>);

}  // namespace hhs::rna

#endif
