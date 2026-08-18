#ifndef HHS_PASS219_INHERITED_PASS218_1_16_HPP
#define HHS_PASS219_INHERITED_PASS218_1_16_HPP

#include "hhs_pass219_inherited_pass218_1_16.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass218Completion final {
public:
    explicit InheritedPass218Completion(
        const HHSExactPass218CompletionWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass218_completion(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.completion_seal_bound == 1U &&
               binding_.receipt_semantics_preserved == 1U &&
               binding_.continuation_identity_exposed == 1U &&
               binding_.canonical_execution_reachable == 1U;
    }
    bool grants_mutation_authority() const noexcept {
        return binding_.cxx_mutation_authority != 0U ||
               binding_.vm81_mutation_authority != 0U ||
               binding_.pass219_handoff_authority_minted != 0U;
    }
    const HHSExactPass219InheritedPass218BindingV1& record() const noexcept {
        return binding_;
    }

private:
    HHSExactPass219InheritedPass218BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass218CompletionWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass218CompletionWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass218BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass218BindingV1>);

}  // namespace hhs::rna

#endif
