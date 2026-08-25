#ifndef HHS_PASS219_INHERITED_PASS205_1_19_HPP
#define HHS_PASS219_INHERITED_PASS205_1_19_HPP

#include "hhs_pass219_inherited_pass205_1_19.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass205DeterministicContinuation final {
public:
    explicit InheritedPass205DeterministicContinuation(
        const HHSExactPass205DeterministicContinuationWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass205_deterministic_continuation(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.pass_number == HHS_EXACT_PASS219_INHERITED_PASS205_NUMBER &&
               binding_.vm5184_state_bound == 1U &&
               binding_.g243_control_bound == 1U &&
               binding_.q_bijection_bound == 1U &&
               binding_.projection_channels_bound == 1U &&
               binding_.single_vm81_authority_bound == 1U &&
               binding_.single_hash72_stream_bound == 1U &&
               binding_.hash216_lineage_bound == 1U &&
               binding_.exact_sparse_full_equivalence_bound == 1U &&
               binding_.exact_retrieval_rerank_bound == 1U &&
               binding_.accelerator_candidate_only_bound == 1U &&
               binding_.pass206_successor_bound == 1U &&
               binding_.no_new_mutation_authority_bound == 1U &&
               binding_.no_new_persistence_authority_bound == 1U &&
               binding_.no_new_hash72_clock_bound == 1U &&
               binding_.pass219_new_canonical_mutation_authority == 0U &&
               binding_.cxx_mutation_authority == 0U &&
               binding_.vm81_mutation_authority == 0U;
    }

    const HHSExactPass219InheritedPass205BindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass205BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass205DeterministicContinuationWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass205DeterministicContinuationWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass205BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass205BindingV1>);

}  // namespace hhs::rna

#endif
