#ifndef HHS_PASS219_INHERITED_PASS208_1_16_HPP
#define HHS_PASS219_INHERITED_PASS208_1_16_HPP

#include "hhs_pass219_inherited_pass208_1_16.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass208GPUBranchManifold final {
public:
    explicit InheritedPass208GPUBranchManifold(const HHSExactPass208GPUBranchManifoldWitnessV1& witness) noexcept {
        status_ = hhs_exact_pass219_bind_pass208_gpu_branch_manifold(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.gpu_candidate_expansion_bound == 1U &&
               binding_.exact_cpu_oracle_verification_bound == 1U &&
               binding_.stable_integer_ranking_bound == 1U &&
               binding_.pass205_singleton_vm81_commit_path_bound == 1U &&
               binding_.gpu_hash72_commit_forbidden == 1U &&
               binding_.gpu_canonical_persistence_forbidden == 1U &&
               binding_.gpu_vm81_bypass_forbidden == 1U &&
               binding_.pass209_successor_bound == 1U;
    }
    const HHSExactPass219InheritedPass208BindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass208BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass208GPUBranchManifoldWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass208GPUBranchManifoldWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass208BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass208BindingV1>);

}  // namespace hhs::rna

#endif
