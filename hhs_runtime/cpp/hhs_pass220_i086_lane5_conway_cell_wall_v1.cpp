#include "hhs_pass220_i086_lane5_conway_cell_wall_v1.h"
#include "hhs_pass219_core_holographic_rna_cell_wall_1_24.hpp"
#include <array>
#include <cstdint>
#include <cstring>

/* Additive I086 module: never modify protected Pass219 PQC translation unit.
 * The inherited I028 executable route requires Pass219 C++ RNA cell wall,
 * valid Hash216 predecessor, Holo4 and Lane5 BIOS constructor mediation.
 * Neither it nor Conway has canonical VM81/Hash72 mint authority here. */
extern "C" HHSExactStatus hhs_pass220_i086_lane5_conway81_cell_wall(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *predecessor,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *witness,
    std::uint8_t ieee, std::uint8_t p4, std::uint8_t c4,
    HHSExactPass220I086Lane5ConwayCandidateV1 *output
) noexcept {
    if (!input || !frame || !predecessor || !witness || !output)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 mediated{};
    const HHSExactStatus checked = hhs_exact_pass220_i028_lane5_rna_g3_route(
        input, frame, predecessor, witness, ieee, p4, c4, &mediated);
    if (checked != HHS_EXACT_STATUS_OK) return checked;
    if (mediated.cpp_rna_cell_wall_routed != 1U ||
        mediated.lane5_zero_bypass_interposer != 1U ||
        mediated.holo4_evidence_equivalent != 1U ||
        mediated.g3_candidate.holo4_four_lane_prepared != 1U ||
        mediated.g3_candidate.mandatory_constructor_graph_bound != 1U ||
        mediated.g3_candidate.candidate_only != 1U ||
        mediated.g3_candidate.candidate_frame_unchanged != 1U ||
        mediated.g3_candidate.canonical_vm81_mutation_authority != 0U ||
        mediated.direct_vm81_bypass_authority != 0U ||
        mediated.canonical_admission_invoked != 0U ||
        mediated.external_egress_authority != 0U ||
        std::memcmp(&mediated.g3_candidate.candidate_frame, frame,
                    sizeof(*frame)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    hhs::rna::OrthogonalGlyphMembrane membrane(input->delta, input->delta);
    if (membrane.status() != HHS_EXACT_STATUS_OK) return membrane.status();
    hhs::rna::CoreHolographicRNACellWall cell_wall(membrane);
    std::array<std::uint8_t, 81> before{}, after{};
    for (std::size_t i = 0; i < before.size(); ++i)
        before[i] = static_cast<std::uint8_t>(frame->words[i] & UINT64_C(1));
    const HHSExactStatus evolved = cell_wall.evolve_conway81(before, after);
    if (evolved != HHS_EXACT_STATUS_OK) return evolved;
    HHSExactPass220I086Lane5ConwayCandidateV1 candidate{};
    candidate.struct_size = static_cast<std::uint32_t>(sizeof(candidate));
    candidate.version = HHS_PASS220_I086_LANE5_CONWAY_VERSION;
    candidate.lane5_bridge = mediated;
    for (std::size_t i = 0; i < before.size(); ++i) {
        candidate.occupancy_before[i] = before[i];
        candidate.occupancy_after[i] = after[i];
    }
    candidate.mediated_via_pass219_rna_cell_wall = 1U;
    candidate.mediated_via_lane5_bios = 1U;
    candidate.holo4_four_lanes_prepared = 1U;
    candidate.source_vm81_frame_unchanged = 1U;
    candidate.predecessor_hash216_verified = 1U;
    candidate.candidate_only = 1U;
    *output = candidate;
    return HHS_EXACT_STATUS_OK;
}
