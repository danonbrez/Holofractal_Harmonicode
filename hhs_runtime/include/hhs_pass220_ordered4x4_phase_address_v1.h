#ifndef HHS_PASS220_ORDERED4X4_PHASE_ADDRESS_V1_H
#define HHS_PASS220_ORDERED4X4_PHASE_ADDRESS_V1_H
#include "hhs_pass220_ordered4x4_outer_geometry_v1.h"
#include "hhs_pass219_rna_transcription_1_10.h"
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#define HHS220_ORDERED4X4_PHASE_BINDINGS 2U

typedef struct HHS220Ordered4x4PhaseAddressV1 {
 uint32_t struct_size;
 uint32_t version;
 uint16_t address5184;
 uint8_t symbol;
 uint8_t cell81;
 uint8_t operation64;
 uint8_t left_phase_basis8;
 uint8_t right_phase_basis8;
 uint8_t address_roundtrip_verified;
 uint8_t native_phase_operator_executed;
 uint8_t native_ordered_source_preserved;
 uint8_t reserved[3];
 HHSExactPass219NativePhaseWitnessV1 native_phase_witness;
 uint8_t source_bound_symbol_root[32];
 uint8_t directional_phase_address_root[32];
} HHS220Ordered4x4PhaseAddressV1;

typedef struct HHS220Ordered4x4PhaseAddressGateV1 {
 uint32_t struct_size;
 uint32_t version;
 HHS220Ordered4x4PhaseAddressV1 bindings[HHS220_ORDERED4X4_PHASE_BINDINGS];
 uint8_t verbatim_source_verified;
 uint8_t inherited_parent_index_verified;
 uint8_t ordered_outer_geometry_verified;
 uint8_t both_phase_address_roundtrips_verified;
 uint8_t both_native_phase_products_verified;
 uint8_t tensor_action_rank_resolved;
 uint8_t tensor_phase_state_fully_verified;
 uint8_t matrix_values_derived;
 uint8_t equation_equality_proved;
 uint8_t parent_signature_authenticated;
 uint8_t signed_vm81_admitted;
 uint8_t hash72_commit_authority;
 uint8_t hash216_commit_authority;
 uint8_t canonical_vm81_mutation_authority;
 uint8_t reserved[2];
 uint8_t source_sha256[32];
 uint8_t parent_reference_sha256[32];
 uint8_t phase_geometry_root_sha256[32];
} HHS220Ordered4x4PhaseAddressGateV1;

/*
 * Read-only derivation of the native ordered phase pair for each tensor's
 * VM81 address. The inherited VM81 address and native RNA phase APIs are
 * the only evaluators used here; no host phase arithmetic.
 *
 * Address phase-pair validity is NOT a witness for tensor action rank or
 * whole-state phase closure. This gate never claims signed parent provenance,
 * matrix results, equality proof, VM81 admission or canonical receipts.
 */
HHS_EXACT_API HHSExactStatus
hhs_exact_pass220_ordered4x4_phase_address_gate(
 const uint8_t *source, size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent_reference,
 HHS220Ordered4x4PhaseAddressGateV1 *out_gate
);
#ifdef __cplusplus
}
#endif
#endif
