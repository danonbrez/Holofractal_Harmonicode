#include "hhs_pass219_core_holographic_rna_cell_wall_1_24.hpp"
#include "hhs_pass219_vm81_pqc_firewall_1_30.h"
#include "hhs_pass220_i086_lane5_conway_cell_wall_v1.h"

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

/* I086 Lane 5 ingress: route through the existing Pass 219 C++ membrane.
 * A candidate-only transition; no native VM81 commit or Hash72 mint.
 * The exact UQCEL input is required to establish the existing membrane.
 */
extern "C" HHS_EXACT_API HHSExactStatus
hhs_pass220_i086_lane5_conway81_cell_wall(
    const HHSExactUQCELInputV1* input,
    const std::uint8_t* occupancy81,
    std::uint8_t* next81
) noexcept {
    if (input == nullptr || occupancy81 == nullptr || next81 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    hhs::rna::OrthogonalGlyphMembrane membrane(input->delta, input->delta);
    if (membrane.status() != HHS_EXACT_STATUS_OK)
        return membrane.status();
    hhs::rna::CoreHolographicRNACellWall cell_wall(membrane);
    std::array<std::uint8_t, 81> input_cells{};
    std::array<std::uint8_t, 81> output_cells{};
    for (std::size_t i = 0; i < 81; ++i)
        input_cells[i] = occupancy81[i];
    const HHSExactStatus status = cell_wall.evolve_conway81(input_cells, output_cells);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    for (std::size_t i = 0; i < 81; ++i)
        next81[i] = output_cells[i];
    return HHS_EXACT_STATUS_OK;
}
