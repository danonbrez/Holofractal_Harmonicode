#ifndef HHS_PASS220_I086_LANE5_CONWAY_CELL_WALL_V1_H
#define HHS_PASS220_I086_LANE5_CONWAY_CELL_WALL_V1_H

#include "hhs_pass220_i028_lane5_rna_g3_bridge_v1.h"
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_PASS220_I086_LANE5_CONWAY_VERSION UINT32_C(0x00010056)

/* The existing VM81 frame, exact Hash216 predecessor, UQCEL input and rooted
 * Lane5 constructor witness are mandatory. This is a candidate occupancy
 * projection only: never a replacement HNAN cell, VM81 state, or Hash72 mint.
 * Failure leaves out_candidate byte-identical. */
typedef struct HHSExactPass220I086Lane5ConwayCandidateV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 lane5_bridge;
    uint8_t occupancy_before[HHS_EXACT_VM81_CELLS];
    uint8_t occupancy_after[HHS_EXACT_VM81_CELLS];
    uint8_t mediated_via_pass219_rna_cell_wall;
    uint8_t mediated_via_lane5_bios;
    uint8_t holo4_four_lanes_prepared;
    uint8_t source_vm81_frame_unchanged;
    uint8_t predecessor_hash216_verified;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_mint_authority;
    uint8_t canonical_hash216_mint_authority;
    uint8_t canonical_persistence_authority;
    uint8_t signed_environmental_admission_invoked;
    uint8_t reserved0[5];
} HHSExactPass220I086Lane5ConwayCandidateV1;

HHS_EXACT_API HHSExactStatus hhs_pass220_i086_lane5_conway81_cell_wall(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *predecessor,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *constructor_witness,
    uint8_t ieee_cell81, uint8_t p4_cell81, uint8_t c4_cell81,
    HHSExactPass220I086Lane5ConwayCandidateV1 *out_candidate
)
#ifdef __cplusplus
noexcept
#endif
;

#ifdef __cplusplus
}
#endif
#endif
