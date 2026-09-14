#ifndef HHS_PASS219_LANE5_HASH216_COMPOSITION_JUMP_STORE_1_38_H
#define HHS_PASS219_LANE5_HASH216_COMPOSITION_JUMP_STORE_1_38_H

#include "hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_VERSION UINT32_C(0x00010026)
#define HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_MIN_SPAN UINT32_C(2)

typedef struct HHSExactPass219Lane5CompositionJumpAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t full_cycle;
    uint8_t validated_hash216_jump_store;
    uint8_t exact_registration_replay_required;
    uint8_t direct_candidate_reuse_allowed;
    uint8_t prime_fingerprint_search_bound;
    uint8_t recursive_layer_tagged;
    uint8_t immutable_composition_seal_required;
    uint8_t gpu_vector_search_candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved0[3];
} HHSExactPass219Lane5CompositionJumpAuthorityV1;

typedef struct HHSExactPass219Lane5CompositionJumpDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t jump_span;
    uint32_t phase_slot;
    uint64_t cycle_index;
    uint32_t layer_index;
    uint32_t reserved0;
    uint64_t parent_signature64;
    uint64_t child_signature64;
    uint64_t composition_signature64;
    uint8_t validated;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved1[2];
} HHSExactPass219Lane5CompositionJumpDescriptorV1;

typedef struct HHSExactPass219Lane5CompositionJumpReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t jump_span;
    uint32_t phase_slot;
    uint64_t cycle_index;
    uint32_t layer_index;
    uint32_t reserved0;
    uint64_t descriptor_signature64;
    uint64_t reuse_signature64;
    uint8_t accepted;
    uint8_t validated_hash216_lineage;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved1;
} HHSExactPass219Lane5CompositionJumpReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_composition_jump_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_composition_jump_authority(
    HHSExactPass219Lane5CompositionJumpAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_composition_jump_validate(
    const HHSExactPass219Lane5CompositionJumpDescriptorV1 *descriptor,
    HHSExactPass219Lane5CompositionJumpReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
