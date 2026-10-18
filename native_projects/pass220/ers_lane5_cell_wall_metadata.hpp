#pragma once
// Pass 220 ERS relational metadata for the pre-existing Pass 219 C++ RNA cell wall.
// Metadata does not mint receipts, implement another VM81, or interpret == as scalar equality.
#include "phase_gear_lane5_rna_bridge.hpp"
#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace hhs::pass220 {
struct ERSRelation {
    std::string_view lhs;
    std::string_view rhs;
    std::string_view context;
};
inline constexpr std::array<ERSRelation, 6> kERSRelations{{
    {"AB", "P^4", "ordered-forward"},
    {"BA", "-P^4", "ordered-reverse"},
    {"P^4", "c^4=(Aa+Ab)(Ba+Bb)", "ordered-composition"},
    {"(Aa/Ba:Bb/Ab=Ab/Aa:Bb/Ba)^4/Delta", "Delta", "reciprocal-quadrature"},
    {"144", "36*4=(6+6)^2=((a^2+b^2+c^2)+(a^2b^2c^2))^((pxy+qzw)/P)=b^8c^4", "H36-H144-cross-lane"},
    {"3/4", "2/5", "independent-periodic-gears"},
}};
// Additional M17 relational index, not a replacement of the native cell wall.
inline constexpr std::array<std::uint8_t,8> kPrimeRingAddresses{{2,3,5,7,11,13,17,19}};
inline constexpr std::array<std::int8_t,8> kSignedSpins{{-4,-3,-2,-1,1,2,3,4}};
inline constexpr std::array<std::uint8_t,8> kPrimeResiduesMod8{{2,3,5,7,3,5,1,3}};
inline constexpr std::array<std::uint8_t,8> kLoShuOuterRing{{8,1,6,7,2,9,4,3}};
inline constexpr std::uint8_t kLoShuHub=5;
inline constexpr std::size_t prime_spin_linear(std::size_t prime_index,
                                                std::size_t spin_index) noexcept {
    return prime_index * 8 + spin_index;
}
inline constexpr bool valid_prime_spin_index(std::size_t p,std::size_t s) noexcept {
    return p < kPrimeRingAddresses.size() && s < kSignedSpins.size() &&
           prime_spin_linear(p,s)<64;
}
struct ERSMetadataView {
    const ERSRelation* relations;
    std::size_t relation_count;
    std::string_view source_payload;
    std::string_view source_modality;
    std::string_view ancestry_reference;
    std::uint16_t cell_address;
    bool source_order_preserved;
    bool authenticated_ancestry;
};
inline constexpr bool valid_ers_metadata(const ERSMetadataView& m) noexcept {
    return m.relations == kERSRelations.data() &&
           m.relation_count == kERSRelations.size() &&
           !m.source_payload.empty() && !m.source_modality.empty() &&
           !m.ancestry_reference.empty() && m.cell_address < 81 &&
           m.source_order_preserved && m.authenticated_ancestry;
}
// Entry to the inherited Pass 219 cell wall; caller supplies authoritative
// serializer output and source transition view, not generated metadata-as-receipts.
inline HHSExactStatus route_ers_lane5_metadata(
    const ERSMetadataView& metadata,
    const FullCircuitCandidate& existing_circuit,
    const HHSExactUQCELInputV1* signed_input,
    const HHSExactVM81Frame* serialized_frame,
    const HHSExactPass219Hash216TransitionViewV1* inherited_transition,
    std::uint8_t feedback_lane, std::int8_t feedback_trinary,
    HHSExactPass219Holo4PreparedV1* prepared,
    HHSExactPass219Holo4DecisionV1* decision) noexcept {
    if (!valid_ers_metadata(metadata))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return route_existing_lane5_phasegear(existing_circuit, signed_input,
        serialized_frame, inherited_transition, feedback_lane,
        feedback_trinary, prepared, decision);
}
} // namespace hhs::pass220
