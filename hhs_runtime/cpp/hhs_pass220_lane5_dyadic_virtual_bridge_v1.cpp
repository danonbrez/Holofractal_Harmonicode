#include "hhs_pass220_lane5_dyadic_virtual_bridge_v1.h"

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>

namespace {
bool sha256_hex64(const char *bytes) noexcept {
    if (!bytes) return false;
    for (std::size_t i = 0; i < 64; ++i) {
        const unsigned char c = static_cast<unsigned char>(bytes[i]);
        if (!((c >= '0' && c <= '9') ||
              (c >= 'a' && c <= 'f') ||
              (c >= 'A' && c <= 'F'))) return false;
    }
    return bytes[64] == '\0';
}
bool address_valid(const std::uint8_t *digits) noexcept {
    if (!digits) return false;
    for (std::size_t i = 0; i < 72; ++i)
        if (digits[i] >= 72U) return false;
    return true;
}
}

extern "C" HHSExactStatus hhs_pass220_lane5_dyadic_virtual_candidate_route(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *predecessor,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *constructor_witness,
    std::uint8_t ieee, std::uint8_t p4, std::uint8_t c4,
    const std::uint8_t radix72_address[72], std::int64_t exponent,
    std::uint8_t phase, const char pass159_binding_sha256[65],
    HHSExactPass220Lane5DyadicVirtualCandidateV1 *out
) noexcept {
    if (!input || !frame || !predecessor || !constructor_witness || !out ||
        !address_valid(radix72_address) || phase >= 72U ||
        !sha256_hex64(pass159_binding_sha256) ||
        exponent == std::numeric_limits<std::int64_t>::min())
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    /* The existing native I028 route is mandatory: it mediates Pass219
     * RNA C++ cell wall, Holo4 and Lane5 BIOS constructor witnesses. */
    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 parent{};
    const auto status = hhs_exact_pass220_i028_lane5_rna_g3_route(
        input, frame, predecessor, constructor_witness,
        ieee, p4, c4, &parent);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (parent.cpp_rna_cell_wall_routed != 1U ||
        parent.lane5_zero_bypass_interposer != 1U ||
        parent.holo4_evidence_equivalent != 1U ||
        parent.pqc_firewall_required_for_canonical_admission != 1U ||
        parent.signed_environmental_vm81_required != 1U ||
        parent.direct_environmental_opcode_canonical_authority != 0U ||
        parent.direct_abi_canonical_authority != 0U ||
        parent.direct_vm81_bypass_authority != 0U ||
        parent.canonical_admission_invoked != 0U ||
        parent.external_egress_authority != 0U ||
        parent.g3_candidate.candidate_only != 1U ||
        parent.g3_candidate.candidate_frame_unchanged != 1U ||
        std::memcmp(&parent.g3_candidate.candidate_frame, frame, sizeof(*frame)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSExactPass220Lane5DyadicVirtualCandidateV1 candidate{};
    candidate.struct_size = static_cast<std::uint32_t>(sizeof(candidate));
    candidate.version = HHS_PASS220_LANE5_DYADIC_VIRTUAL_BRIDGE_VERSION;
    candidate.mediated = parent;
    std::memcpy(candidate.radix72_address, radix72_address, 72);
    candidate.signed_dyadic_exponent = exponent;
    candidate.phase_coordinate72 = phase;
    std::memcpy(candidate.pass159_binding_sha256, pass159_binding_sha256, 65);
    candidate.candidate_only = 1U;
    candidate.cplusplus_rna_cell_wall_routed = 1U;
    candidate.requires_pqc_firewall = 1U;
    candidate.requires_signed_environmental_vm81 = 1U;
    candidate.source_frame_unchanged = 1U;
    /* All canonical authority fields intentionally remain zero. */
    *out = candidate;
    return HHS_EXACT_STATUS_OK;
}
