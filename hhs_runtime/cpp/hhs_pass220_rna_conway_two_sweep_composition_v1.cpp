#include "hhs_pass220_rna_conway_two_sweep_composition_v1.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>

extern "C" HHSExactStatus hhs_pass220_rna_conway_two_sweep_candidate(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *predecessor,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *witness,
    std::uint8_t ieee, std::uint8_t p4, std::uint8_t c4,
    std::uint64_t frame_id, std::uint32_t position,
    HHSExactPass220RNAConwayTwoSweepCandidateV1 *output
) noexcept {
    if (!input || !frame || !predecessor || !witness || !output ||
        position >= HHS_PASS220_NATIVE_SWEEP_WIDTH || ieee >= HHS_EXACT_VM81_CELLS ||
        frame_id > (std::numeric_limits<std::uint64_t>::max() /
                    HHS_PASS220_NATIVE_LAYER_COUNT) - 1U)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    // Use the inherited exact codec rather than defining a new byte order.
    std::array<std::uint8_t, HHS_EXACT_VM81_FRAME_BYTES> raw{};
    std::size_t written = 0U;
    HHSExactStatus status =
        hhs_exact_vm81_frame_export_le(frame, raw.data(), raw.size(), &written);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (written != raw.size()) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    HHSExactVM81Frame restored{};
    status = hhs_exact_vm81_frame_import_le(raw.data(), raw.size(), &restored);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (std::memcmp(&restored, frame, sizeof(restored)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSExactPass220I086Lane5ConwayCandidateV1 conway{};
    status = hhs_pass220_i086_lane5_conway81_cell_wall(
        input, &restored, predecessor, witness, ieee, p4, c4, &conway);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (conway.candidate_only != 1U ||
        conway.predecessor_hash216_verified != 1U ||
        conway.mediated_via_pass219_rna_cell_wall != 1U ||
        conway.mediated_via_lane5_bios != 1U ||
        conway.source_vm81_frame_unchanged != 1U ||
        conway.canonical_vm81_mutation_authority != 0U ||
        conway.canonical_hash72_mint_authority != 0U ||
        conway.canonical_hash216_mint_authority != 0U ||
        conway.canonical_persistence_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSExactPass220RNAConwayTwoSweepCandidateV1 candidate{};
    candidate.struct_size = static_cast<std::uint32_t>(sizeof(candidate));
    candidate.version = HHS_PASS220_RNA_CONWAY_TWO_SWEEP_VERSION;
    candidate.local_position5184 = position;
    candidate.layer0 = position;
    candidate.layer1 = HHS_PASS220_NATIVE_SWEEP_WIDTH + position;
    candidate.vm81_cell = position / 64U;
    candidate.vm81_local64 = position % 64U;
    candidate.mirror5184 = HHS_PASS220_NATIVE_SWEEP_WIDTH - 1U - position;
    candidate.logical_frame_id = frame_id;
    candidate.ieee_input_bits = frame->words[ieee];
    candidate.ieee_return_bits = restored.words[ieee];
    candidate.conway = conway;
    candidate.exact_raw648_roundtrip = 1U;
    candidate.paired_sweeps_verified = 1U;
    candidate.source_frame_unchanged = 1U;
    candidate.candidate_only = 1U;
    *output = candidate;
    return HHS_EXACT_STATUS_OK;
}
