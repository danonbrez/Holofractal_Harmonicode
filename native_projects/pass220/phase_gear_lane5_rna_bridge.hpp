#pragma once
// Pass220 candidate-only bridge into the existing Pass219 RNA VM5184 C ABI.
// Caller MUST supply a frame produced by the authoritative VM81/BigInt
// serializer and an authenticated, matching Hash216 transition view.
// This file does not invent a second serializer, mint, or state clock.
#include "hhs_pass219_rna_vm5184_abi_1_33.h"
#include "adjustable_phase_gear_candidate.hpp"

namespace hhs::pass220 {
inline HHSExactStatus route_existing_lane5_phasegear(
    const FullCircuitCandidate& circuit,
    const HHSExactUQCELInputV1* signed_input,
    const HHSExactVM81Frame* serialized_frame,
    const HHSExactPass219Hash216TransitionViewV1* inherited_transition,
    std::uint8_t feedback_lane,
    std::int8_t feedback_trinary,
    HHSExactPass219Holo4PreparedV1* prepared,
    HHSExactPass219Holo4DecisionV1* decision) noexcept {
    // Do not interpret a candidate's 216-character parent label as receipt
    // authentication; hhs_exact_pass219_rna_vm5184_route verifies the real
    // Hash216 reference and routes the frame through the native C++ cell wall.
    if (!circuit.candidate_only || signed_input == nullptr ||
        serialized_frame == nullptr || inherited_transition == nullptr ||
        prepared == nullptr || decision == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    // Coordinates are references within the SAME existing 5184 address space.
    // Reject collisions instead of silently overwriting 64 tensor identities.
    for (std::size_t i=0;i<kCircuitCells;++i) {
        if (circuit.inherited_linear5184[i]>=HHS_EXACT_VM81_FRAME_BITS)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        for (std::size_t j=0;j<i;++j)
            if (circuit.inherited_linear5184[i]==circuit.inherited_linear5184[j])
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    // No candidate-to-frame reinterpret_cast: the certified frame is supplied
    // by the inherited exact serializer and remains authoritative.
    return hhs_exact_pass219_rna_vm5184_route(
        signed_input,serialized_frame,inherited_transition,feedback_lane,
        feedback_trinary,prepared,decision);
}
} // namespace hhs::pass220
