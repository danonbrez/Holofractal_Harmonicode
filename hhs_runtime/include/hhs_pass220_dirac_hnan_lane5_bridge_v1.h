#ifndef HHS_PASS220_DIRAC_HNAN_LANE5_BRIDGE_V1_H
#define HHS_PASS220_DIRAC_HNAN_LANE5_BRIDGE_V1_H
#include "hhs_pass220_i028_lane5_rna_g3_bridge_v1.h"
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define HHS_PASS220_DIRAC_HNAN_LANE5_VERSION UINT32_C(0x00010001)
typedef struct HHSDiracGaussianIntV1 { int64_t real; int64_t imaginary; } HHSDiracGaussianIntV1;
typedef struct HHSDiracSectorInputV1 {
    uint8_t address_binary[3]; /* 000,001,010,011,100,101,110,111; ordered */
    HHSDiracGaussianIntV1 spinor[4]; /* phi[0..1] then chi[0..1] */
    uint8_t group_mapping_verified; /* diagnostic only, NOT proof */
} HHSDiracSectorInputV1;
typedef struct HHSDiracEightCandidateV1 {
    uint32_t struct_size,version;
    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 mediated;
    uint8_t exact_reference_boundary_pass;
    uint8_t mapping_flags_all_set;
    uint8_t native_rna_cell_wall_routed;
    uint8_t source_frame_unchanged;
    uint8_t candidate_only;
    uint8_t native_admission;
    uint8_t canonical_hash_mint_authority;
    uint8_t reserved;
} HHSDiracEightCandidateV1;
/* Guarded I028 route: failure MUST leave output unchanged. Passing candidate
 * does not certify center HNAN gate, real source mapping or conservation.
 * No movement integrator or VM81 mutation is performed here. */
HHS_EXACT_API HHSExactStatus hhs_pass220_dirac_eight_lane5_candidate(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *predecessor,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *witness,
    uint8_t ieee, uint8_t p4, uint8_t c4,
    const HHSDiracSectorInputV1 sectors[8],
    HHSDiracEightCandidateV1 *output
);
#ifdef __cplusplus
}
#endif
#endif
