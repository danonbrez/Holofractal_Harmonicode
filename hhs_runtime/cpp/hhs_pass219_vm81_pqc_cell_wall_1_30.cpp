#include "hhs_pass219_core_holographic_rna_cell_wall_1_24.hpp"
#include "hhs_pass219_vm81_pqc_firewall_1_30.h"

#if defined(_WIN32)
#define HHS_P219_PQC_INTERNAL
#else
#define HHS_P219_PQC_INTERNAL __attribute__((visibility("hidden")))
#endif

extern "C" HHS_P219_PQC_INTERNAL HHSExactStatus
hhs_pass219_vm81_pqc_route_cpp_cell_wall(
    const HHSExactUQCELInputV1* input,
    const HHSExactVM81Frame* frame,
    const HHSExactPass219Hash216TransitionViewV1* transition,
    std::uint8_t feedback_lane,
    std::int8_t feedback_trinary,
    HHSExactPass219Holo4PreparedV1* out_prepared,
    HHSExactPass219Holo4DecisionV1* out_decision
) noexcept {
    if (input == nullptr || frame == nullptr || transition == nullptr ||
        out_prepared == nullptr || out_decision == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    /*
     * The canonical monolithic cell-wall invariant includes a^2 == delta.
     * UQCEL's compact compatibility input does not carry a distinct a^2 field,
     * so the exact delta projection is supplied to both constructor operands.
     * This is a typed lowering choice; it does not redefine the source equation.
     */
    hhs::rna::OrthogonalGlyphMembrane membrane(input->delta, input->delta);
    if (membrane.status() != HHS_EXACT_STATUS_OK)
        return membrane.status();

    hhs::rna::CoreHolographicRNACellWall cell_wall(membrane);
    HHSExactPass219Holo4StateV1 state{};
    HHSExactStatus status = hhs_exact_pass219_holo4_state_init(&state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return cell_wall.route_parallel(
        *frame,
        *transition,
        feedback_lane,
        feedback_trinary,
        state,
        *out_prepared,
        *out_decision);
}
