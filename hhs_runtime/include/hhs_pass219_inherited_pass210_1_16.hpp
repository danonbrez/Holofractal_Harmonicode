#ifndef HHS_PASS219_INHERITED_PASS210_1_16_HPP
#define HHS_PASS219_INHERITED_PASS210_1_16_HPP

#include "hhs_pass219_inherited_pass210_1_16.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass210HolographicFrameCompression final {
public:
    explicit InheritedPass210HolographicFrameCompression(const HHSExactPass210HFCWitnessV1& witness) noexcept {
        status_ = hhs_exact_pass219_bind_pass210_holographic_frame_compression(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.exact_frame_authority_bound == 1U &&
               binding_.single_snapshot_recovery_bound == 1U &&
               binding_.strict_compression_domain_bound == 1U &&
               binding_.pass211_successor_bound == 1U;
    }
    const HHSExactPass219InheritedPass210BindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass210BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass210HFCWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass210HFCWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass210BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass210BindingV1>);

}  // namespace hhs::rna

#endif
