#ifndef HHS_PASS219_INHERITED_PASS209_1_16_HPP
#define HHS_PASS219_INHERITED_PASS209_1_16_HPP

#include "hhs_pass219_inherited_pass209_1_16.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass209RuntimeBootstrapGateway final {
public:
    explicit InheritedPass209RuntimeBootstrapGateway(const HHSExactPass209RuntimeBootstrapWitnessV1& witness) noexcept {
        status_ = hhs_exact_pass219_bind_pass209_runtime_bootstrap_gateway(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.nonblocking_bootstrap_bound == 1U &&
               binding_.persistent_status_cache_bound == 1U &&
               binding_.isolated_probe_bound == 1U &&
               binding_.canonical_backend_authority_preserved == 1U &&
               binding_.pass210_successor_bound == 1U;
    }
    const HHSExactPass219InheritedPass209BindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass209BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass209RuntimeBootstrapWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass209RuntimeBootstrapWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass209BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass209BindingV1>);

}  // namespace hhs::rna

#endif
