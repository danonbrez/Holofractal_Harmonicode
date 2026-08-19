#ifndef HHS_PASS219_INHERITED_PASS211_1_16_HPP
#define HHS_PASS219_INHERITED_PASS211_1_16_HPP

#include "hhs_pass219_inherited_pass211_1_16.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass211BigIntHFCCarrier final {
public:
    explicit InheritedPass211BigIntHFCCarrier(
        const HHSExactPass211BigIntHFCWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass211_bigint_hfc_carrier(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.pass133_bigint_carrier_bound == 1U &&
               binding_.pass210_hfc_multiregister_bound == 1U &&
               binding_.pass212_successor_bound == 1U;
    }
    const HHSExactPass219InheritedPass211BindingV1& record() const noexcept {
        return binding_;
    }

private:
    HHSExactPass219InheritedPass211BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass211BigIntHFCWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass211BigIntHFCWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass211BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass211BindingV1>);

}  // namespace hhs::rna

#endif
