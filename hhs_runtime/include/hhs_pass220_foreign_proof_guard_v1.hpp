#ifndef HHS_PASS220_FOREIGN_PROOF_GUARD_V1_HPP
#define HHS_PASS220_FOREIGN_PROOF_GUARD_V1_HPP
#include "hhs_pass219_pass169_gate_authority_binding_1_21_11.h"
#include <array>
#include <cstdint>

namespace hhs::lane5 {
// A source-specific Pass219 proof cannot be inherited as a proof for a
// different expression solely because both contracts contain five gates.
inline constexpr std::array<std::uint8_t, 32> kPhase3672SourceSha{
    0xce,0xec,0x28,0x24,0x99,0xdd,0xaf,0x48,
    0xeb,0xa1,0xd2,0x5b,0x63,0x13,0xc4,0x07,
    0xd9,0x46,0x6d,0x37,0x9e,0x32,0x1b,0x47,
    0xf9,0xa6,0xb3,0xf7,0x52,0xc2,0xa4,0x99
};
struct ForeignProofAudit final {
    bool source_identity_matches{false};
    bool five_gate_count_matches{false};
    bool source_reconstruction_declared{false};
    bool proof_import_admitted{false};
    bool vm81_admission_authorized{false};
};
inline ForeignProofAudit inspect_pass219_proof_for_five_gate_source(
    const HHSExactPass219Pass169AuthorityProofV1& proof
) noexcept {
    ForeignProofAudit out{};
    out.source_identity_matches = true;
    for (std::size_t i = 0; i < kPhase3672SourceSha.size(); ++i)
        out.source_identity_matches = out.source_identity_matches &&
            proof.combined_source_sha256[i] == kPhase3672SourceSha[i];
    out.five_gate_count_matches = proof.gate_count == 5U;
    out.source_reconstruction_declared = proof.source_reconstruction_verified == 1U;
    // This is a source-compatibility diagnostic, NEVER proof authentication.
    // Pass219 source-specific I162 proof must be regenerated/evaluated under
    // this exact source by a native provider before any authority handoff.
    return out;
}
} // namespace hhs::lane5
#endif
