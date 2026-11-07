#include "hhs_pass220_q81_hnan_native_phase_candidate_v1.h"
#include <cstddef>
#include <cstdint>
#include <cstring>

/* Pure ordered four-case phase code: NEVER scalarizes native HNAN tensor. */
extern "C" HHSExactStatus hhs_pass220_q81_hnan_phase_encode_pair(
    std::int8_t lhs, std::int8_t rhs, std::uint8_t *binary,
    std::uint8_t *orientation
) {
    if (!binary || !orientation) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    std::uint8_t bit = 0, direction = 0;
    if (lhs == 0 && rhs == 1) { bit = 0; direction = 0; }
    else if (lhs == 1 && rhs == 0) { bit = 0; direction = 1; }
    else if (lhs == -1 && rhs == 1) { bit = 1; direction = 0; }
    else if (lhs == 1 && rhs == -1) { bit = 1; direction = 1; }
    else return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *binary = bit;
    *orientation = direction;
    return HHS_EXACT_STATUS_OK;
}

extern "C" HHSExactStatus hhs_pass220_q81_hnan_phase_decode_pair(
    std::uint8_t binary, std::uint8_t orientation,
    std::int8_t *lhs, std::int8_t *rhs
) {
    if (!lhs || !rhs || binary > 1U || orientation > 1U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    static constexpr std::int8_t pair[2][2][2] = {
        {{0, 1}, {1, 0}},
        {{-1, 1}, {1, -1}}
    };
    *lhs = pair[binary][orientation][0];
    *rhs = pair[binary][orientation][1];
    return HHS_EXACT_STATUS_OK;
}

/* Execute the inherited I028 constructor and Pass219 C++ wall BEFORE projecting.
 * Candidate-only: never claims that the caller's ordered-pair source has been
 * established by the complete course-wide HNAN constraint solver. */
extern "C" HHSExactStatus hhs_pass220_q81_hnan_phase_candidate(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *predecessor,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *witness,
    std::uint8_t ieee, std::uint8_t p4, std::uint8_t c4,
    const std::int8_t ordered_pairs[HHS_PASS220_Q81_HNAN_PHASE_CELLS][2],
    HHSExactPass220Q81HNANPhaseCandidateV1 *output
) {
    if (!input || !frame || !predecessor || !witness || !ordered_pairs || !output)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (input->struct_size != sizeof(*input)
        || input->uqcel_version != hhs_exact_uqcel_version()
        || input->profile != HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    /* Reject all bad phase domains before invoking the inherited route. */
    HHSExactPass220Q81HNANPhaseCandidateV1 candidate{};
    candidate.struct_size = static_cast<std::uint32_t>(sizeof(candidate));
    candidate.version = HHS_PASS220_Q81_HNAN_NATIVE_PHASE_VERSION;
    for (std::size_t i = 0; i < HHS_PASS220_Q81_HNAN_PHASE_CELLS; ++i) {
        std::uint8_t bit = 0, orient = 0;
        auto status = hhs_pass220_q81_hnan_phase_encode_pair(
            ordered_pairs[i][0], ordered_pairs[i][1], &bit, &orient);
        if (status != HHS_EXACT_STATUS_OK) return status;
        std::int8_t recovered_lhs = 0, recovered_rhs = 0;
        status = hhs_pass220_q81_hnan_phase_decode_pair(
            bit, orient, &recovered_lhs, &recovered_rhs);
        if (status != HHS_EXACT_STATUS_OK || recovered_lhs != ordered_pairs[i][0]
            || recovered_rhs != ordered_pairs[i][1])
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        candidate.binary[i] = bit;
        candidate.orientation[i] = orient;
        candidate.ordered_pair[i][0] = recovered_lhs;
        candidate.ordered_pair[i][1] = recovered_rhs;
    }

    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 mediated{};
    const auto status = hhs_exact_pass220_i028_lane5_rna_g3_route(
        input, frame, predecessor, witness, ieee, p4, c4, &mediated);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (mediated.cpp_rna_cell_wall_routed != 1U
        || mediated.lane5_zero_bypass_interposer != 1U
        || mediated.holo4_evidence_equivalent != 1U
        || mediated.g3_candidate.holo4_four_lane_prepared != 1U
        || mediated.g3_candidate.mandatory_constructor_graph_bound != 1U
        || mediated.g3_candidate.candidate_only != 1U
        || mediated.g3_candidate.candidate_frame_unchanged != 1U
        || mediated.g3_candidate.canonical_vm81_mutation_authority != 0U
        || mediated.direct_vm81_bypass_authority != 0U
        || mediated.canonical_admission_invoked != 0U
        || mediated.external_egress_authority != 0U
        || std::memcmp(&mediated.g3_candidate.candidate_frame, frame,
                       sizeof(*frame)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    candidate.lane5_bridge = mediated;
    candidate.mediated_via_pass219_cpp_cell_wall = 1U;
    candidate.mediated_via_lane5_constructor = 1U;
    candidate.source_phase_native_certified = 0U;
    candidate.candidate_only = 1U;
    /* Remaining authority flags remain zero by value initialization. */
    *output = candidate;
    return HHS_EXACT_STATUS_OK;
}
