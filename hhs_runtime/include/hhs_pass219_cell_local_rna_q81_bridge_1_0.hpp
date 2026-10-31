#ifndef HHS_PASS219_CELL_LOCAL_RNA_Q81_BRIDGE_1_0_HPP
#define HHS_PASS219_CELL_LOCAL_RNA_Q81_BRIDGE_1_0_HPP

#include "hhs_pass219_rna_admission_lowering_1_12.h"
#include "hhs_pass219_hash216_fractal_qudit_admission_1_45.h"

#include <cstdint>

namespace hhs::rna {

// Additive, read-only cell-local composition. No independent admission, proof,
// Hash72 mint, Hash216 persistence, or receipt-clock authority.
class CellLocalRNAQ81Bridge final {
public:
    struct CellBinding final {
        const HHSExactPass219RNAAdmissionCandidateV1* candidate;
        const HHSExactPass219Hash216FractalQuditWitnessV1* qudit;
        const HHSExactUQCELInputV1* input;
        const HHSExactPass219Hash216TransitionViewV1* parent;
    };

    // This verifies coordinate consistency and delegates the full Q81 witness
    // constraints to the inherited native verifier. It does NOT prove AB=P^4
    // or BA=-P^4 by substituting scalar projections into typed expressions.
    static HHSExactStatus validate(const CellBinding& b) noexcept {
        if (!b.candidate || !b.qudit || !b.input || !b.parent)
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        if (b.qudit->cell81 >= 81U || b.qudit->operation64 >= 64U ||
            b.qudit->hash72_major >= 72U || b.qudit->hash72_minor >= 72U)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        const auto slot = static_cast<std::uint32_t>(b.qudit->cell81) * 64U
                        + static_cast<std::uint32_t>(b.qudit->operation64);
        if (b.qudit->local5184 != slot ||
            b.qudit->hash72_major != slot / 72U ||
            b.qudit->hash72_minor != slot % 72U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        return hhs_exact_pass219_hash216_fractal_qudit_witness_validate(
            b.input, b.parent, b.qudit);
    }

    // Native RNA replay/rollback only; does not mutate or promote authority.
    static HHSExactStatus reconstruct(
        const CellBinding& b,
        HHSExactVM81Frame& successor,
        HHSExactVM81Frame& predecessor
    ) noexcept {
        const auto status = validate(b);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        const auto forward = hhs_exact_pass219_rna_candidate_reconstruct(
            b.candidate, &successor);
        if (forward != HHS_EXACT_STATUS_OK)
            return forward;
        return hhs_exact_pass219_rna_candidate_rollback(
            b.candidate, &predecessor);
    }
};

} // namespace hhs::rna

#endif
