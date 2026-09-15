#include "hhs_pass219_lane5_persistent_hash216_composition_memory_1_39.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); \
        return 1; \
    } \
} while (0)

int main(void) {
    HHSExactPass219Lane5PersistentCompositionAuthorityV1 authority;
    HHSExactPass219Lane5PersistentCompositionDescriptorV1 descriptor;
    HHSExactPass219Lane5PersistentCompositionDescriptorV1 tampered;
    HHSExactPass219Lane5PersistentCompositionReceiptV1 receipt_a;
    HHSExactPass219Lane5PersistentCompositionReceiptV1 receipt_b;
    uint64_t swap64;
    uint32_t swap32;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_persistent_composition_memory_version() ==
          HHS_EXACT_PASS219_LANE5_PERSISTENT_COMPOSITION_MEMORY_VERSION);
    CHECK(hhs_exact_pass219_lane5_persistent_composition_memory_authority(&authority) ==
          HHS_EXACT_STATUS_OK);
    CHECK(authority.struct_size == sizeof(authority));
    CHECK(authority.full_cycle == 20020U);
    CHECK(authority.snapshot_bytes == 648U);
    CHECK(authority.pass174_persistent_encrypted_vector_store_bound == 1U);
    CHECK(authority.pass194_hash216_positional_index_bound == 1U);
    CHECK(authority.sqlite_wal_required == 1U);
    CHECK(authority.sqlite_synchronous_full_required == 1U);
    CHECK(authority.aes_gcm_authenticated_snapshot_encryption == 1U);
    CHECK(authority.restart_rehydration_supported == 1U);
    CHECK(authority.metadata_hash216_seal_required == 1U);
    CHECK(authority.vm5184_little_endian_word_frame == 1U);
    CHECK(authority.recursive_layer_index_persisted == 1U);
    CHECK(authority.gpu_vector_search_candidate_only == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);
    CHECK(authority.floating_point_canonical_authority == 0U);

    memset(&descriptor, 0, sizeof(descriptor));
    descriptor.struct_size = (uint32_t)sizeof(descriptor);
    descriptor.version = HHS_EXACT_PASS219_LANE5_PERSISTENT_COMPOSITION_MEMORY_VERSION;
    descriptor.jump_span = 64U;
    descriptor.phase_slot = 20019U;
    descriptor.cycle_index = UINT64_C(73);
    descriptor.layer_index = 5U;
    descriptor.snapshot_bytes = 648U;
    descriptor.parent_signature64 = UINT64_C(0x2101);
    descriptor.child_signature64 = UINT64_C(0x2102);
    descriptor.composition_signature64 = UINT64_C(0x2103);
    descriptor.metadata_signature64 = UINT64_C(0x2104);
    descriptor.vector_object_signature64 = UINT64_C(0x2105);
    descriptor.persisted = 1U;
    descriptor.encrypted = 1U;
    descriptor.authenticated = 1U;
    descriptor.metadata_sealed = 1U;
    descriptor.candidate_only = 1U;
    descriptor.requires_signed_environmental_vm81_admission = 1U;

    memset(&receipt_a, 0, sizeof(receipt_a));
    memset(&receipt_b, 0, sizeof(receipt_b));
    CHECK(hhs_exact_pass219_lane5_persistent_composition_validate(&descriptor, &receipt_a) ==
          HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_persistent_composition_validate(&descriptor, &receipt_b) ==
          HHS_EXACT_STATUS_OK);
    CHECK(memcmp(&receipt_a, &receipt_b, sizeof(receipt_a)) == 0);
    CHECK(receipt_a.accepted == 1U);
    CHECK(receipt_a.restart_rehydratable == 1U);
    CHECK(receipt_a.encrypted_vector_bound == 1U);
    CHECK(receipt_a.metadata_hash216_bound == 1U);
    CHECK(receipt_a.candidate_only == 1U);
    CHECK(receipt_a.canonical_mutation_authority == 0U);
    CHECK(receipt_a.canonical_persistence_authority == 0U);
    CHECK(receipt_a.requires_signed_environmental_vm81_admission == 1U);

    tampered = descriptor;
    tampered.snapshot_bytes = 647U;
    CHECK(hhs_exact_pass219_lane5_persistent_composition_validate(&tampered, &receipt_b) ==
          HHS_EXACT_STATUS_INVALID_ARGUMENT);
    tampered = descriptor;
    tampered.phase_slot = 20020U;
    CHECK(hhs_exact_pass219_lane5_persistent_composition_validate(&tampered, &receipt_b) ==
          HHS_EXACT_STATUS_INVALID_ARGUMENT);
    tampered = descriptor;
    tampered.metadata_signature64 = 0U;
    CHECK(hhs_exact_pass219_lane5_persistent_composition_validate(&tampered, &receipt_b) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.authenticated = 0U;
    CHECK(hhs_exact_pass219_lane5_persistent_composition_validate(&tampered, &receipt_b) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.canonical_persistence_authority = 1U;
    CHECK(hhs_exact_pass219_lane5_persistent_composition_validate(&tampered, &receipt_b) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = descriptor;
    swap64 = tampered.parent_signature64;
    tampered.parent_signature64 = tampered.child_signature64;
    tampered.child_signature64 = swap64;
    CHECK(hhs_exact_pass219_lane5_persistent_composition_validate(&tampered, &receipt_b) ==
          HHS_EXACT_STATUS_OK);
    CHECK(receipt_b.descriptor_signature64 != receipt_a.descriptor_signature64);
    CHECK(receipt_b.persistence_signature64 != receipt_a.persistence_signature64);

    tampered = descriptor;
    swap32 = tampered.jump_span;
    tampered.jump_span = tampered.layer_index;
    tampered.layer_index = swap32;
    CHECK(hhs_exact_pass219_lane5_persistent_composition_validate(&tampered, &receipt_b) ==
          HHS_EXACT_STATUS_OK);
    CHECK(receipt_b.descriptor_signature64 != receipt_a.descriptor_signature64);
    CHECK(receipt_b.persistence_signature64 != receipt_a.persistence_signature64);

    printf(
        "PASS219_LANE5_PERSISTENT_HASH216_COMPOSITION_MEMORY_PASS span=%u phase=%u layer=%u persistence=%llu\n",
        receipt_a.jump_span,
        receipt_a.phase_slot,
        receipt_a.layer_index,
        (unsigned long long)receipt_a.persistence_signature64);
    return 0;
}
