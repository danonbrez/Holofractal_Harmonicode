#ifndef HHS_PASS219_RNA_ADMISSION_LOWERING_1_12_HPP
#define HHS_PASS219_RNA_ADMISSION_LOWERING_1_12_HPP

#include "hhs_pass219_rna_admission_lowering_1_12.h"
#include "hhs_pass219_rna_rule_grammar_1_11.hpp"

#include <cstdint>
#include <type_traits>

namespace hhs::rna {

class AdmissionCandidate final {
public:
    AdmissionCandidate(
        const TranscriptionWitness& witness,
        const HHSExactVM81Frame& predecessor,
        const HHSExactVM81Frame& candidate,
        const std::uint8_t (&dependency_frontier_sha256)[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES]
    ) noexcept {
        if (witness.status() != HHS_EXACT_STATUS_OK) {
            status_ = HHS_EXACT_STATUS_INVALID_ARGUMENT;
            return;
        }
        status_ = hhs_exact_pass219_rna_admission_candidate_from_witness(
            &witness.record(), &predecessor, &candidate,
            dependency_frontier_sha256, &record_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    const HHSExactPass219RNAAdmissionCandidateV1& record() const noexcept { return record_; }

    HHSExactStatus reconstruct(HHSExactVM81Frame& out) const noexcept {
        if (status_ != HHS_EXACT_STATUS_OK)
            return status_;
        return hhs_exact_pass219_rna_candidate_reconstruct(&record_, &out);
    }

    HHSExactStatus rollback(HHSExactVM81Frame& out) const noexcept {
        if (status_ != HHS_EXACT_STATUS_OK)
            return status_;
        return hhs_exact_pass219_rna_candidate_rollback(&record_, &out);
    }

private:
    HHSExactPass219RNAAdmissionCandidateV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass219RNAAdmissionCandidateV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219RNAAdmissionCandidateV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219RNAAdmissionLoweringV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219RNAAdmissionLoweringV1>);

}  // namespace hhs::rna

#endif
