#include "hhs_pass220_dirac_hnan_lane5_bridge_v1.h"
#include "hhs_pass220_dirac_hnan_eight_sector_candidate_v1.hpp"
#include <array>
#include <cstring>
#include <limits>

extern "C" HHSExactStatus hhs_pass220_dirac_eight_lane5_candidate(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *predecessor,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *witness,
    uint8_t ieee, uint8_t p4, uint8_t c4,
    const HHSDiracSectorInputV1 sectors[8],
    HHSDiracEightCandidateV1 *output
) {
    if (!input || !frame || !predecessor || !witness || !sectors || !output)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (input->struct_size != sizeof(*input) ||
        input->uqcel_version != hhs_exact_uqcel_version() ||
        input->profile != HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    using namespace hhs::pass220::dirac;
    std::array<Sector,8> native{};
    for (std::size_t i=0;i<8;++i) {
        const auto &s=sectors[i];
        for (std::size_t j=0;j<3;++j)
            if (s.address_binary[j] != static_cast<uint8_t>((i >> (2-j)) & 1U))
                return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        // Avoid signed overflow in Gaussian multiplications and future extensions:
        // the I/K projector itself only changes sign and permutes coefficients.
        for (std::size_t k=0;k<4;++k) {
            if (s.spinor[k].real==std::numeric_limits<int64_t>::min() ||
                s.spinor[k].imaginary==std::numeric_limits<int64_t>::min())
                return HHS_EXACT_STATUS_INVALID_ARGUMENT;
            native[i].psi[k]={s.spinor[k].real,s.spinor[k].imaginary};
        }
        native[i].address=addresses[i];
        native[i].role=roles[i];
        native[i].source_group_witness_verified=(s.group_mapping_verified==1U);
        if (s.group_mapping_verified>1U) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    const auto boundary=check(native);
    if (!boundary.ordered_roles || !boundary.reference_projector_admissible)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 mediated{};
    const auto status=hhs_exact_pass220_i028_lane5_rna_g3_route(
        input,frame,predecessor,witness,ieee,p4,c4,&mediated);
    if (status!=HHS_EXACT_STATUS_OK)return status;
    if (mediated.cpp_rna_cell_wall_routed!=1U ||
        mediated.lane5_zero_bypass_interposer!=1U ||
        mediated.holo4_evidence_equivalent!=1U ||
        mediated.g3_candidate.candidate_only!=1U ||
        mediated.g3_candidate.candidate_frame_unchanged!=1U ||
        mediated.g3_candidate.canonical_vm81_mutation_authority!=0U ||
        mediated.canonical_admission_invoked!=0U ||
        mediated.direct_vm81_bypass_authority!=0U ||
        std::memcmp(&mediated.g3_candidate.candidate_frame,frame,sizeof(*frame))!=0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    HHSDiracEightCandidateV1 candidate{};
    candidate.struct_size=static_cast<uint32_t>(sizeof(candidate));
    candidate.version=HHS_PASS220_DIRAC_HNAN_LANE5_VERSION;
    candidate.mediated=mediated;
    candidate.exact_reference_boundary_pass=1U;
    candidate.mapping_flags_all_set=boundary.all_group_mappings_verified?1U:0U;
    candidate.native_rna_cell_wall_routed=1U;
    candidate.source_frame_unchanged=1U;
    candidate.candidate_only=1U;
    candidate.native_admission=0U;
    candidate.canonical_hash_mint_authority=0U;
    *output=candidate;
    return HHS_EXACT_STATUS_OK;
}
