#ifndef HHS_PASS219_INHERITED_PASS200C_1_24_HPP
#define HHS_PASS219_INHERITED_PASS200C_1_24_HPP

#include "hhs_pass219_inherited_pass200c_1_24.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass200CGuardedActiveAdmission final {
public:
    explicit InheritedPass200CGuardedActiveAdmission(
        const HHSExactPass200CGuardedActiveWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass200c_guarded_active_admission(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.pass_number == HHS_EXACT_PASS219_INHERITED_PASS200C_NUMBER &&
               binding_.pass_variant == HHS_EXACT_PASS219_INHERITED_PASS200C_VARIANT &&
               binding_.historical_squash_identity_bound == 1U &&
               binding_.immutable_source_identity_bound == 1U &&
               binding_.canary_evidence_gate_bound == 1U &&
               binding_.approval_and_activation_bound == 1U &&
               binding_.continuous_exact_guard_bound == 1U &&
               binding_.rollback_reference_restoration_bound == 1U &&
               binding_.durable_state_read_only_bound == 1U &&
               binding_.pass201_successor_bound == 1U &&
               binding_.no_new_active_admission_authority_bound == 1U &&
               binding_.no_new_canonical_mutation_authority_bound == 1U &&
               binding_.no_new_persistence_authority_bound == 1U &&
               binding_.no_new_hash72_clock_bound == 1U &&
               binding_.pass219_new_active_admission_authority == 0U &&
               binding_.pass219_new_canonical_mutation_authority == 0U &&
               binding_.pass219_new_persistence_authority == 0U &&
               binding_.pass219_new_hash72_clock == 0U &&
               binding_.cxx_mutation_authority == 0U &&
               binding_.vm81_mutation_authority == 0U;
    }

    const HHSExactPass219InheritedPass200CBindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass200CBindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass200CGuardedActiveWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass200CGuardedActiveWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass200CBindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass200CBindingV1>);

}  // namespace hhs::rna

#endif
