#ifndef HHS_PASS220_ORDERED4X4_I001_CARRIER_V1_H
#define HHS_PASS220_ORDERED4X4_I001_CARRIER_V1_H
#include "hhs_pass220_ordered4x4_readiness_v1.h"
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#define HHS220_4X4_I001_CELLS 81U
#define HHS220_4X4_I001_TOKEN_BYTES 64U
#define HHS220_4X4_I001_TOTAL_BYTES 5184U
#define HHS220_4X4_I001_PROFILE_VERSION UINT32_C(0x00010000)

typedef struct HHS220Ordered4x4I001CarrierV1 {
 uint32_t struct_size;
 uint32_t version;
 uint32_t profile_cells;
 uint32_t profile_token_bytes;
 uint32_t s_valid_cells;
 uint32_t v_valid_cells;
 uint8_t source_identity_verified;
 uint8_t inherited_hash216_structure_verified;
 uint8_t I001_normalization_token_profile_verified;
 uint8_t s_all_81_tokens_canonical;
 uint8_t v_all_81_tokens_canonical;
 uint8_t original_vm81_addresses_preserved;
 uint8_t original_noncommutative_graph_preserved;
 uint8_t deterministic_profile_replay_verified;
 uint8_t signed_predecessor_authenticated;
 uint8_t authenticated_tensor_rank_proved;
 uint8_t full_phase_action_proved;
 uint8_t native_matrix_values_computed;
 uint8_t equation_equality_proved;
 uint8_t signed_vm81_admission_executed;
 uint8_t hash72_commit_authority;
 uint8_t hash216_commit_authority;
 uint8_t canonical_vm81_mutation_authority;
 uint8_t reserved[3];
 uint16_t s_vm5184_address;
 uint16_t v_vm5184_address;
 uint8_t s_81_offset_digits[HHS220_4X4_I001_CELLS];
 uint8_t v_81_offset_digits[HHS220_4X4_I001_CELLS];
 uint8_t source_sha256[32];
 uint8_t parent_reference_sha256[32];
 uint8_t bound_graph_root_sha256[32];
 uint8_t s_carrier_position_root_sha256[32];
 uint8_t v_carrier_position_root_sha256[32];
 uint8_t carrier_profile_root_sha256[32];
} HHS220Ordered4x4I001CarrierV1;

/*
 * Validate the SPECIFIC I001 normalized Lo Shu 81x64 exact rational
 * scientific carrier produced by serialize_offsets_5184, not every legal
 * generic HARMONICODE 5184-character tensor representation.
 *
 * Format for each 64-byte cell token:
 *   +[20 zero-padded integer digits 0..8]/[20 digits = 1]e+[20 zero digits]
 * Canonical zero positions remain distinct through address and token index.
 *
 * No float, no ordinary scalar normalization, no implied rank or equality.
 * Never grant VM81 or receipt authority. Fail closed for shape-only strings.
 */
HHS_EXACT_API HHSExactStatus
hhs_exact_pass220_ordered4x4_i001_carrier_validate(
 const uint8_t *source,size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4I001CarrierV1 *out_carrier
);

/*
 * Exact inverse of the inherited I001 81x64 normalization-offset serializer.
 * Both length and offset alphabet are checked BEFORE writing any bytes.
 * Input and output may overlap: source positions are privately snapshotted.
 *
 * This is a representation encoder, not signed ingress or VM81 admission.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_ordered4x4_i001_offsets_emit(
 const uint8_t offsets[HHS220_4X4_I001_CELLS],
 uint8_t *out_bytes,size_t capacity,size_t *out_length
);

#ifdef __cplusplus
}
#endif
#endif
