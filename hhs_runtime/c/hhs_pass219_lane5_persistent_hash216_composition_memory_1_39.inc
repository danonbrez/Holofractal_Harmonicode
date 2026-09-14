#include "../include/hhs_pass219_lane5_persistent_hash216_composition_memory_1_39.h"

#include <string.h>

static uint64_t hhs_lane5_persistent_mix64(uint64_t x) {
    x ^= x >> 30;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31;
    return x;
}

static uint64_t hhs_lane5_persistent_descriptor_signature(
    const HHSExactPass219Lane5PersistentCompositionDescriptorV1 *d
) {
    uint64_t x = UINT64_C(0x4c35504552533139);
    x ^= hhs_lane5_persistent_mix64((uint64_t)d->jump_span);
    x ^= hhs_lane5_persistent_mix64((uint64_t)d->phase_slot << 32);
    x ^= hhs_lane5_persistent_mix64(d->cycle_index);
    x ^= hhs_lane5_persistent_mix64((uint64_t)d->layer_index);
    x ^= hhs_lane5_persistent_mix64((uint64_t)d->snapshot_bytes);
    x ^= hhs_lane5_persistent_mix64(d->parent_signature64);
    x ^= hhs_lane5_persistent_mix64(d->child_signature64);
    x ^= hhs_lane5_persistent_mix64(d->composition_signature64);
    x ^= hhs_lane5_persistent_mix64(d->metadata_signature64);
    x ^= hhs_lane5_persistent_mix64(d->vector_object_signature64);
    return hhs_lane5_persistent_mix64(x);
}

uint32_t hhs_exact_pass219_lane5_persistent_composition_memory_version(void) {
    return HHS_EXACT_PASS219_LANE5_PERSISTENT_COMPOSITION_MEMORY_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_persistent_composition_memory_authority(
    HHSExactPass219Lane5PersistentCompositionAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5PersistentCompositionAuthorityV1 value;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = HHS_EXACT_PASS219_LANE5_PERSISTENT_COMPOSITION_MEMORY_VERSION;
    value.full_cycle = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE;
    value.snapshot_bytes = HHS_EXACT_PASS219_LANE5_PERSISTENT_COMPOSITION_SNAPSHOT_BYTES;
    value.pass174_persistent_encrypted_vector_store_bound = 1U;
    value.pass194_hash216_positional_index_bound = 1U;
    value.sqlite_wal_required = 1U;
    value.sqlite_synchronous_full_required = 1U;
    value.aes_gcm_authenticated_snapshot_encryption = 1U;
    value.restart_rehydration_supported = 1U;
    value.metadata_hash216_seal_required = 1U;
    value.vm5184_little_endian_word_frame = 1U;
    value.recursive_layer_index_persisted = 1U;
    value.gpu_vector_search_candidate_only = 1U;
    value.canonical_vm81_mutation_authority = 0U;
    value.canonical_hash72_authority = 0U;
    value.canonical_hash216_authority = 0U;
    value.canonical_persistence_authority = 0U;
    value.requires_signed_environmental_vm81_admission = 1U;
    value.floating_point_canonical_authority = 0U;
    *out_authority = value;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_persistent_composition_validate(
    const HHSExactPass219Lane5PersistentCompositionDescriptorV1 *descriptor,
    HHSExactPass219Lane5PersistentCompositionReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5PersistentCompositionReceiptV1 receipt;
    uint64_t signature;
    if (descriptor == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->struct_size != sizeof(*descriptor) ||
        descriptor->version != HHS_EXACT_PASS219_LANE5_PERSISTENT_COMPOSITION_MEMORY_VERSION)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->jump_span < HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_MIN_SPAN ||
        descriptor->phase_slot >= HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE ||
        descriptor->snapshot_bytes != HHS_EXACT_PASS219_LANE5_PERSISTENT_COMPOSITION_SNAPSHOT_BYTES)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->parent_signature64 == 0U ||
        descriptor->child_signature64 == 0U ||
        descriptor->composition_signature64 == 0U ||
        descriptor->metadata_signature64 == 0U ||
        descriptor->vector_object_signature64 == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (descriptor->persisted != 1U || descriptor->encrypted != 1U ||
        descriptor->authenticated != 1U || descriptor->metadata_sealed != 1U ||
        descriptor->candidate_only != 1U ||
        descriptor->canonical_mutation_authority != 0U ||
        descriptor->canonical_hash72_authority != 0U ||
        descriptor->canonical_hash216_authority != 0U ||
        descriptor->canonical_persistence_authority != 0U ||
        descriptor->requires_signed_environmental_vm81_admission != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&receipt, 0, sizeof(receipt));
    signature = hhs_lane5_persistent_descriptor_signature(descriptor);
    receipt.struct_size = (uint32_t)sizeof(receipt);
    receipt.version = HHS_EXACT_PASS219_LANE5_PERSISTENT_COMPOSITION_MEMORY_VERSION;
    receipt.jump_span = descriptor->jump_span;
    receipt.phase_slot = descriptor->phase_slot;
    receipt.cycle_index = descriptor->cycle_index;
    receipt.layer_index = descriptor->layer_index;
    receipt.snapshot_bytes = descriptor->snapshot_bytes;
    receipt.descriptor_signature64 = signature;
    receipt.persistence_signature64 = hhs_lane5_persistent_mix64(
        signature ^ descriptor->metadata_signature64 ^
        descriptor->vector_object_signature64 ^ UINT64_C(0x2002005005130139)
    );
    receipt.accepted = 1U;
    receipt.restart_rehydratable = 1U;
    receipt.encrypted_vector_bound = 1U;
    receipt.metadata_hash216_bound = 1U;
    receipt.candidate_only = 1U;
    receipt.canonical_mutation_authority = 0U;
    receipt.canonical_hash72_authority = 0U;
    receipt.canonical_hash216_authority = 0U;
    receipt.canonical_persistence_authority = 0U;
    receipt.requires_signed_environmental_vm81_admission = 1U;
    *out_receipt = receipt;
    return HHS_EXACT_STATUS_OK;
}
