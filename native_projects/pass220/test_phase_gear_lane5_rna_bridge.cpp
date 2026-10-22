#include "phase_gear_lane5_rna_bridge.hpp"
#include <type_traits>
#include "hhs_pass220_i028_lane5_rna_g3_bridge_v1.h"
#include <cstddef>
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
// The inherited I028 bridge owns the actual constructor admission contract.
static_assert(std::is_standard_layout_v<HHSExactPass220I028Lane5ConstructorWitnessV1>);
static_assert(std::is_same_v<decltype(&hhs_exact_pass220_i028_lane5_rna_g3_route),
    HHSExactStatus (*)(const HHSExactUQCELInputV1*,
      const HHSExactVM81Frame*,
      const HHSExactPass219Hash216TransitionViewV1*,
      const HHSExactPass220I028Lane5ConstructorWitnessV1*,
      uint8_t,uint8_t,uint8_t,
      HHSExactPass220I028Lane5RNAG3BridgeCandidateV1*)>);
static_assert(offsetof(HHSExactPass220I028Lane5ConstructorWitnessV1,
                       lane5_hash72_mint_authority) <
              offsetof(HHSExactPass220I028Lane5ConstructorWitnessV1,
                       lane5_hash216_mint_authority));
int main() { return 0; } // compile-only: no forged signed evidence
