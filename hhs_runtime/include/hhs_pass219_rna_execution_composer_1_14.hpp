#ifndef HHS_PASS219_RNA_EXECUTION_COMPOSER_1_14_HPP
#define HHS_PASS219_RNA_EXECUTION_COMPOSER_1_14_HPP

#include "hhs_pass219_rna_execution_composer_1_14.h"
#include "hhs_pass219_rna_state_retrieval_1_13.hpp"

#include <cstdint>
#include <type_traits>

namespace hhs::rna {

class ExecutionPlan final {
public:
    ExecutionPlan(
        const AuthenticatedPriorState& prior_state,
        const std::uint8_t (&current_dependency_frontier_sha256)[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES],
        HHSExactPass219RNAExecutionBypassReason requested_bypass_reason = HHS_EXACT_PASS219_RNA_BYPASS_NONE
    ) noexcept {
        if (prior_state.status() != HHS_EXACT_STATUS_OK) {
            status_ = prior_state.status();
            return;
        }
        status_ = hhs_exact_pass219_rna_execution_compose(
            &prior_state.record(),
            current_dependency_frontier_sha256,
            static_cast<std::uint32_t>(requested_bypass_reason),
            &record_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    HHSExactPass219RNAExecutionRoute route() const noexcept {
        return static_cast<HHSExactPass219RNAExecutionRoute>(record_.route);
    }
    HHSExactPass219RNAExecutionBypassReason effective_bypass_reason() const noexcept {
        return static_cast<HHSExactPass219RNAExecutionBypassReason>(record_.effective_bypass_reason);
    }
    bool uses_indexed_continuation() const noexcept {
        return record_.route == HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_INDEXED_CONTINUATION &&
               record_.authenticated_predecessor_reused == 1U;
    }
    bool genesis_replay_required() const noexcept { return record_.genesis_replay_required == 1U; }
    const HHSExactPass219RNAExecutionPlanV1& record() const noexcept { return record_; }

    HHSExactStatus prepare_candidate(
        const AuthenticatedPriorState& prior_state,
        const TranscriptionWitness& witness,
        const HHSExactVM81Frame& candidate_frame,
        HHSExactPass219RNAAdmissionCandidateV1& out_candidate
    ) const noexcept {
        if (status_ != HHS_EXACT_STATUS_OK || prior_state.status() != HHS_EXACT_STATUS_OK)
            return status_ != HHS_EXACT_STATUS_OK ? status_ : prior_state.status();
        return hhs_exact_pass219_rna_execution_prepare_candidate(
            &record_, &prior_state.record(), &witness.record(),
            &candidate_frame, &out_candidate);
    }

private:
    HHSExactPass219RNAExecutionPlanV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass219RNAExecutionPlanV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219RNAExecutionPlanV1>);

}  // namespace hhs::rna

#endif
