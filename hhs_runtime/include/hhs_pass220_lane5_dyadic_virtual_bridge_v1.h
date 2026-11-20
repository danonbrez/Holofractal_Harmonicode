#ifndef HHS_PASS220_LANE5_DYADIC_VIRTUAL_BRIDGE_V1_H
#define HHS_PASS220_LANE5_DYADIC_VIRTUAL_BRIDGE_V1_H

#include "hhs_pass220_i028_lane5_rna_g3_bridge_v1.h"
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_PASS220_LANE5_DYADIC_VIRTUAL_BRIDGE_VERSION UINT32_C(0x00010001)

/* Virtual 72-digit base-72 address and signed dyadic exponent metadata.
 * This structure is an exact candidate envelope, NOT a VM81 frame or commit.
 * Provenance digest is supplied by the caller and must be independently
 * checked against the Pass159 binding by the existing authority path. */
typedef struct HHSExactPass220Lane5DyadicVirtualCandidateV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 mediated;
    uint8_t radix72_address[72];
    int64_t signed_dyadic_exponent;
    uint8_t phase_coordinate72;
    char pass159_binding_sha256[65];
    uint8_t candidate_only;
    uint8_t cplusplus_rna_cell_wall_routed;
    uint8_t requires_pqc_firewall;
    uint8_t requires_signed_environmental_vm81;
    uint8_t source_frame_unchanged;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_mint_authority;
    uint8_t canonical_hash216_mint_authority;
    uint8_t canonical_persistence_authority;
} HHSExactPass220Lane5DyadicVirtualCandidateV1;

/* Extends existing I028 candidate route. No direct canonical admission.
 * On error, *out_candidate remains byte-identical.
 * Exponent is an exact signed coordinate, not an IEEE floating point value. */
HHS_EXACT_API HHSExactStatus hhs_pass220_lane5_dyadic_virtual_candidate_route(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *predecessor,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *constructor_witness,
    uint8_t ieee_cell81, uint8_t p4_cell81, uint8_t c4_cell81,
    const uint8_t radix72_address[72], int64_t signed_dyadic_exponent,
    uint8_t phase_coordinate72, const char pass159_binding_sha256[65],
    HHSExactPass220Lane5DyadicVirtualCandidateV1 *out_candidate
)
#ifdef __cplusplus
noexcept
#endif
;

/* Pure Pass220 proposal digest (not a VM81 signature or admission receipt).
 * Re-encodes 81 frame words as little-endian bytes; no raw struct hashing.
 * On invalid input, out_sha256 is unchanged. */
HHS_EXACT_API HHSExactStatus hhs_pass220_lane5_dyadic_binding_material_sha256(
    const HHSExactVM81Frame *frame,
    const uint8_t radix72_address[72],
    int64_t signed_dyadic_exponent,
    uint8_t phase_coordinate72,
    const char pass159_binding_sha256[65],
    uint8_t out_sha256[32]
)
#ifdef __cplusplus
noexcept
#endif
;

#ifdef __cplusplus
}
#endif
#endif
