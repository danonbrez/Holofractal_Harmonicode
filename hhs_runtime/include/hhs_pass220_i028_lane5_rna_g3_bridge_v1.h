#ifndef HHS_PASS220_I028_LANE5_RNA_G3_BRIDGE_V1_H
#define HHS_PASS220_I028_LANE5_RNA_G3_BRIDGE_V1_H

#include "hhs_pass219_exact_vm81_candidate_adapter_1_21_3.h"
#include "hhs_pass219_rna_vm5184_abi_1_33.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS220_I028_LANE5_RNA_G3_BRIDGE_VERSION UINT32_C(0x00010001)

typedef struct HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219Holo4PreparedV1 rna_prepared;
    HHSExactPass219Holo4DecisionV1 rna_decision;
    HHSExactPass220I028Lane5G3CandidateV1 g3_candidate;
    uint8_t surface_linux_api_abi_ingress;
    uint8_t lane5_zero_bypass_interposer;
    uint8_t cpp_rna_cell_wall_routed;
    uint8_t holo4_evidence_equivalent;
    uint8_t pqc_firewall_required_for_canonical_admission;
    uint8_t signed_environmental_vm81_required;
    uint8_t direct_environmental_opcode_canonical_authority;
    uint8_t direct_abi_canonical_authority;
    uint8_t direct_vm81_bypass_authority;
    uint8_t canonical_admission_invoked;
    uint8_t external_egress_authority;
    uint8_t reserved0[5];
} HHSExactPass220I028Lane5RNAG3BridgeCandidateV1;

HHS_EXACT_API uint32_t hhs_exact_pass220_i028_lane5_rna_g3_bridge_version(void);

/*
 * Candidate-only I028 bridge.
 *
 * The frame must first traverse the public Pass 219 RNA VM5184 C ABI, which
 * enters the C++ CoreHolographicRNACellWall.  The bridge then executes the
 * already-rooted Lane5/Holo4/G3 candidate surface from a fresh Holo4 state and
 * requires exact semantic equivalence of the Holo4 evidence.
 *
 * This bridge never calls canonical admission.  The surviving candidate still
 * requires the inherited PQC environmental/instruction membrane and the signed
 * environmental VM81 authority before canonical mutation or external egress.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_i028_lane5_rna_g3_route(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *source_transition,
    const HHSExactPass220I028Lane5ConstructorWitnessV1 *constructor_witness,
    uint8_t ieee_cell81,
    uint8_t p4_cell81,
    uint8_t c4_cell81,
    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 *out_candidate
);

#ifdef __cplusplus
}
#endif

#endif
