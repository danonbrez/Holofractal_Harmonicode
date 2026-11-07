#ifndef HHS_PASS220_Q81_HNAN_NATIVE_PHASE_CANDIDATE_V1_H
#define HHS_PASS220_Q81_HNAN_NATIVE_PHASE_CANDIDATE_V1_H

#include "hhs_pass220_i028_lane5_rna_g3_bridge_v1.h"
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_PASS220_Q81_HNAN_NATIVE_PHASE_VERSION UINT32_C(0x00010001)
#define HHS_PASS220_Q81_HNAN_PHASE_CELLS UINT32_C(81)

/* Ordered source pairs MUST originate from an upstream typed constraint
 * candidate. This gate does NOT assert their native derivation. It only
 * projects them after real I028 -> Pass219 C++ wall -> Lane5 mediation.
 * No signed VM81 admission or canonical receipt/mutation authority. */
typedef struct HHSExactPass220Q81HNANPhaseCandidateV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 lane5_bridge;
    uint8_t binary[HHS_PASS220_Q81_HNAN_PHASE_CELLS];
    uint8_t orientation[HHS_PASS220_Q81_HNAN_PHASE_CELLS];
    int8_t ordered_pair[HHS_PASS220_Q81_HNAN_PHASE_CELLS][2];
    uint8_t mediated_via_pass219_cpp_cell_wall;
    uint8_t mediated_via_lane5_constructor;
    uint8_t source_phase_native_certified;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_mint_authority;
    uint8_t canonical_hash216_mint_authority;
    uint8_t signed_vm81_admission_invoked;
} HHSExactPass220Q81HNANPhaseCandidateV1;

/* Local exact code: Delta=0: (0,1),(1,0);
 * Delta=1: (-1,+1),(+1,-1). The orientation is DERIVED, never injected. */
HHS_EXACT_API HHSExactStatus hhs_pass220_q81_hnan_phase_encode_pair(
    int8_t lhs, int8_t rhs, uint8_t *binary, uint8_t *orientation
);

HHS_EXACT_API HHSExactStatus hhs_pass220_q81_hnan_phase_decode_pair(
    uint8_t binary, uint8_t orientation, int8_t *lhs, int8_t *rhs
);

/* Failure keeps output unchanged. Calls existing native I028 mediator. */
HHS_EXACT_API HHSExactStatus hhs_pass220_q81_hnan_phase_candidate(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *predecessor,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *witness,
    uint8_t ieee, uint8_t p4, uint8_t c4,
    const int8_t ordered_pairs[HHS_PASS220_Q81_HNAN_PHASE_CELLS][2],
    HHSExactPass220Q81HNANPhaseCandidateV1 *output
);

#ifdef __cplusplus
}
#endif

#endif
