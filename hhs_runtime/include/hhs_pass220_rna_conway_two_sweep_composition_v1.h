#ifndef HHS_PASS220_RNA_CONWAY_TWO_SWEEP_COMPOSITION_V1_H
#define HHS_PASS220_RNA_CONWAY_TWO_SWEEP_COMPOSITION_V1_H

#include "hhs_pass220_i086_lane5_conway_cell_wall_v1.h"
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#define HHS_PASS220_RNA_CONWAY_TWO_SWEEP_VERSION UINT32_C(0x00010001)
#define HHS_PASS220_NATIVE_SWEEP_WIDTH UINT32_C(5184)
#define HHS_PASS220_NATIVE_SWEEP_COUNT UINT32_C(2)
#define HHS_PASS220_NATIVE_LAYER_COUNT UINT32_C(10368)

/* Bounded, candidate-only C++ composition. A caller-supplied source frame is
 * serialized through the inherited exact 648-byte codec, imported again, and
 * passed through the existing RNA/I028/I086 C++ cell wall. The paired tick
 * geometry is checked, not independently minted as Hash216 authority.
 *
 * This deliberately does NOT claim Pass I073 scientific BigInt/RNA transcription,
 * I085 Hash216 array authentication, native 1.38/1.39/1.40 persistence, or
 * signed canonical VM81 admission. Those require additional typed witnesses.
 * On any failure output remains byte-for-byte unchanged.
 */
typedef struct HHSExactPass220RNAConwayTwoSweepCandidateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t local_position5184;
    uint32_t layer0;
    uint32_t layer1;
    uint32_t vm81_cell;
    uint32_t vm81_local64;
    uint32_t mirror5184;
    uint64_t logical_frame_id;
    uint64_t ieee_input_bits;
    uint64_t ieee_return_bits;
    HHSExactPass220I086Lane5ConwayCandidateV1 conway;
    uint8_t exact_raw648_roundtrip;
    uint8_t paired_sweeps_verified;
    uint8_t source_frame_unchanged;
    uint8_t candidate_only;
    uint8_t native_hash216_array_authenticated;
    uint8_t native_persistent_graph_authenticated;
    uint8_t signed_vm81_admission_invoked;
    uint8_t canonical_mutation_authority;
} HHSExactPass220RNAConwayTwoSweepCandidateV1;

HHS_EXACT_API HHSExactStatus hhs_pass220_rna_conway_two_sweep_candidate(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *predecessor,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *constructor_witness,
    uint8_t ieee_cell81, uint8_t p4_cell81, uint8_t c4_cell81,
    uint64_t frame_id, uint32_t local_position5184,
    HHSExactPass220RNAConwayTwoSweepCandidateV1 *out_candidate
)
#ifdef __cplusplus
noexcept
#endif
;
#ifdef __cplusplus
}
#endif
#endif
