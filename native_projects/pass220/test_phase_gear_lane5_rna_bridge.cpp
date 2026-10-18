#include "phase_gear_lane5_rna_bridge.hpp"
#include <type_traits>
static_assert(HHS_EXACT_VM81_CELLS == 81);
static_assert(HHS_EXACT_VM81_FRAME_BITS == 5184);
static_assert(HHS_EXACT_VM81_FRAME_BYTES == 648);
static_assert(sizeof(HHSExactVM81Frame) == HHS_EXACT_VM81_FRAME_BYTES);
static_assert(std::is_same_v<decltype(&hhs::pass220::route_existing_lane5_phasegear),
    HHSExactStatus (*)(const hhs::pass220::FullCircuitCandidate&,
      const HHSExactUQCELInputV1*, const HHSExactVM81Frame*,
      const HHSExactPass219Hash216TransitionViewV1*, std::uint8_t,
      std::int8_t, HHSExactPass219Holo4PreparedV1*,
      HHSExactPass219Holo4DecisionV1*) noexcept>);
int main() { return 0; } // compile-only: no forged signed evidence
