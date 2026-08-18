#ifndef HHS_PASS219_INHERITED_PASS207_1_17_HPP
#define HHS_PASS219_INHERITED_PASS207_1_17_HPP

#include "hhs_pass219_inherited_pass207_1_17.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass207GPUHyperthreadDriver final {
public:
    explicit InheritedPass207GPUHyperthreadDriver(const HHSExactPass207GPUHyperthreadWitnessV1& witness) noexcept {
        status_ = hhs_exact_pass219_bind_pass207_gpu_hyperthread_driver(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.stable_vm5184_lane_dispatch_bound == 1U &&
               binding_.lane_phase_bijection_bound == 1U &&
               binding_.ordered_cell_pack_bound == 1U &&
               binding_.ordered_hydration_bound == 1U &&
               binding_.exact_cpu_oracle_verification_bound == 1U &&
               binding_.content_keyed_cache_bound == 1U &&
               binding_.stable_vector_ranking_bound == 1U &&
               binding_.candidate_only_bound == 1U &&
               binding_.gpu_hash72_commit_forbidden == 1U &&
               binding_.gpu_canonical_mutation_forbidden == 1U &&
               binding_.gpu_vm81_bypass_forbidden == 1U &&
               binding_.pass205_singleton_vm81_admission_bound == 1U &&
               binding_.pass208_successor_bound == 1U;
    }
    const HHSExactPass219InheritedPass207BindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass207BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass207GPUHyperthreadWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass207GPUHyperthreadWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass207BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass207BindingV1>);

}  // namespace hhs::rna

#endif
