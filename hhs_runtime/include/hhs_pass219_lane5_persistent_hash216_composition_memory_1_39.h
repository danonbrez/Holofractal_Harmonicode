#ifndef HHS_PASS219_LANE5_PERSISTENT_HASH216_COMPOSITION_MEMORY_1_39_H
#define HHS_PASS219_LANE5_PERSISTENT_HASH216_COMPOSITION_MEMORY_1_39_H

#include "hhs_pass219_lane5_hash216_composition_jump_store_1_38.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_PERSISTENT_COMPOSITION_MEMORY_VERSION UINT32_C(0x00010027)
#define HHS_EXACT_PASS219_LANE5_PERSISTENT_COMPOSITION_SNAPSHOT_BYTES UINT32_C(648)

typedef struct HHSExactPass219Lane5PersistentCompositionAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t full_cycle;
    uint32_t snapshot_bytes;
    uint8_t pass174_persistent_encrypted_vector_store_bound;
    uint8_t pass194_hash216_positional_index_bound;
    uint8_t sqlite_wal_required;
    uint8_t sqlite_synchronous_full_required;
    uint8_t aes_gcm_authenticated_snapshot_encryption;
    uint8_t restart_rehydration_supported;
    uint8_t metadata_hash216_seal_required;
    uint8_t vm5184_little_endian_word_frame;
    uint8_t recursive_layer_index_persisted;
    uint8_t gpu_vector_search_candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t floating_point_canonical_authority;
} HHSExactPass219Lane5PersistentCompositionAuthorityV1;

typedef struct HHSExactPass219Lane5PersistentCompositionDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t jump_span;
    uint32_t phase_slot;
    uint64_t cycle_index;
    uint32_t layer_index;
    uint32_t snapshot_bytes;
    uint64_t parent_signature64;
    uint64_t child_signature64;
    uint64_t composition_signature64;
    uint64_t metadata_signature64;
    uint64_t vector_object_signature64;
    uint8_t persisted;
    uint8_t encrypted;
    uint8_t authenticated;
    uint8_t metadata_sealed;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[6];
} HHSExactPass219Lane5PersistentCompositionDescriptorV1;

typedef struct HHSExactPass219Lane5PersistentCompositionReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t jump_span;
    uint32_t phase_slot;
    uint64_t cycle_index;
    uint32_t layer_index;
    uint32_t snapshot_bytes;
    uint64_t descriptor_signature64;
    uint64_t persistence_signature64;
    uint8_t accepted;
    uint8_t restart_rehydratable;
    uint8_t encrypted_vector_bound;
    uint8_t metadata_hash216_bound;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[6];
} HHSExactPass219Lane5PersistentCompositionReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_persistent_composition_memory_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_persistent_composition_memory_authority(
    HHSExactPass219Lane5PersistentCompositionAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_persistent_composition_validate(
    const HHSExactPass219Lane5PersistentCompositionDescriptorV1 *descriptor,
    HHSExactPass219Lane5PersistentCompositionReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
