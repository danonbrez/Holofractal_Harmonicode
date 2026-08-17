#ifndef HHS_PASS219_RNA_STATE_RETRIEVAL_1_13_HPP
#define HHS_PASS219_RNA_STATE_RETRIEVAL_1_13_HPP

#include "hhs_pass219_rna_state_retrieval_1_13.h"
#include "hhs_pass219_rna_admission_lowering_1_12.hpp"

#include <type_traits>

namespace hhs::rna {

class AuthenticatedPriorState final {
public:
    AuthenticatedPriorState(
        const HHSExactPass219RNAIndexedPriorStateV1& indexed,
        const HHSExactPass219RNAPriorStateReferenceSealV1& reference_seal
    ) noexcept {
        status_ = hhs_exact_pass219_rna_state_retrieval_authenticate(
            &indexed, &reference_seal, &record_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    HHSExactPass219RNAStateRetrievalClass classification() const noexcept {
        return static_cast<HHSExactPass219RNAStateRetrievalClass>(record_.classification);
    }
    bool fallback_required() const noexcept { return record_.fallback_required == 1U; }
    bool index_invalidated() const noexcept { return record_.index_invalidated == 1U; }
    const HHSExactPass219RNAStateRetrievalV1& record() const noexcept { return record_; }

    HHSExactStatus prepare_candidate(
        const TranscriptionWitness& witness,
        const HHSExactVM81Frame& candidate_frame,
        HHSExactPass219RNAAdmissionCandidateV1& out_candidate
    ) const noexcept {
        if (status_ != HHS_EXACT_STATUS_OK)
            return status_;
        return hhs_exact_pass219_rna_admission_candidate_from_retrieval(
            &witness.record(), &record_, &candidate_frame, &out_candidate);
    }

private:
    HHSExactPass219RNAStateRetrievalV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass219RNAPriorStateIdentityV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219RNAPriorStateIdentityV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219RNAPriorStateReferenceSealV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219RNAPriorStateReferenceSealV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219RNAIndexedPriorStateV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219RNAIndexedPriorStateV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219RNAStateRetrievalV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219RNAStateRetrievalV1>);

}  // namespace hhs::rna

#endif
