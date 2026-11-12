#ifndef HHS_PASS219_RNA_VM5184_ABI_1_33_H
#define HHS_PASS219_RNA_VM5184_ABI_1_33_H

#include "hhs_pass219_vm81_pqc_firewall_1_30.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_RNA_VM5184_ABI_VERSION UINT32_C(0x00010021)

typedef struct HHSExactPass219RNAVM5184ABIDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t vm81_cells;
    uint32_t vm81_word_bits;
    uint32_t vm5184_bits;
    uint32_t vm5184_bytes;
    uint32_t lane_count;
    uint8_t cpp_rna_cell_wall;
    uint8_t exact_vm5184_carrier;
    uint8_t raw5184_ingress;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[6];
} HHSExactPass219RNAVM5184ABIDescriptorV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_rna_vm5184_abi_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_vm5184_abi_descriptor(
    HHSExactPass219RNAVM5184ABIDescriptorV1 *out_descriptor
);

/*
 * Candidate-only C ABI entry into the Pass 219 C++ RNA cell wall.
 *
 * The supplied HHSExactVM81Frame is the exact VM5184 carrier defined by the
 * base ABI (81 cells x 64 bits == 5184 bits).  This route may prepare, score,
 * and select a hydration lane, but it cannot commit VM81 state, mint Hash72 or
 * Hash216 lineage, or persist canonical state.  Canonical mutation remains
 * exclusively beneath the signed/environmental VM81 authority boundary.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_vm5184_route(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Holo4PreparedV1 *out_prepared,
    HHSExactPass219Holo4DecisionV1 *out_decision
);

/*
 * Raw 648-byte ingress companion.  Bytes are lowered exclusively through the
 * exact VM81 frame importer before entering the same C++ RNA cell-wall route.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_raw5184_route(
    const HHSExactUQCELInputV1 *input,
    const uint8_t *raw_frame_le,
    size_t raw_frame_length,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Holo4PreparedV1 *out_prepared,
    HHSExactPass219Holo4DecisionV1 *out_decision
);

#ifdef __cplusplus
}
#endif

#endif
