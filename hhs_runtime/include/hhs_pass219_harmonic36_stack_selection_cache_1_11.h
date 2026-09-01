#ifndef HHS_PASS219_HARMONIC36_STACK_SELECTION_CACHE_1_11_H
#define HHS_PASS219_HARMONIC36_STACK_SELECTION_CACHE_1_11_H

#include "hhs_pass219_harmonic36_stack_selection_1_10.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_STACK_CACHE_VERSION UINT32_C(0x0001000B)
#define HHS_EXACT_PASS219_H36_STACK_CACHE_CAPACITY UINT32_C(8)

typedef struct HHSExactPass219H36StackCacheEntryV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t sequence;
    uint64_t entry_signature64;
    uint8_t occupied;
    uint8_t candidate_only;
    uint8_t vector_store_metadata_only;
    uint8_t hash216_lineage_claim;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    HHSExactPass219H36StackSelectionV1 selection;
} HHSExactPass219H36StackCacheEntryV1;

typedef struct HHSExactPass219H36StackCacheV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t capacity;
    uint32_t entry_count;
    uint64_t next_sequence;
    uint8_t candidate_only;
    uint8_t vector_store_metadata_only;
    uint8_t hash216_lineage_claim;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    HHSExactPass219H36StackCacheEntryV1
        entries[HHS_EXACT_PASS219_H36_STACK_CACHE_CAPACITY];
} HHSExactPass219H36StackCacheV1;

typedef struct HHSExactPass219H36StackCacheReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t entry_index;
    uint32_t selected_candidate_id;
    uint32_t selected_stack_kind;
    uint64_t sequence;
    uint64_t workload_signature36;
    uint64_t semantic_result_signature64;
    uint64_t entry_signature64;
    uint64_t replay_signature64;
    uint8_t cache_hit;
    uint8_t fresh_selection_equal;
    uint8_t exact_replayable;
    uint8_t stale_signature_rejected;
    uint8_t candidate_only;
    uint8_t vector_store_metadata_only;
    uint8_t hash216_lineage_claim;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    char vector_key216[HHS_EXACT_UQCEL_HASH216_STRLEN];
} HHSExactPass219H36StackCacheReceiptV1;

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_stack_cache_init(
    HHSExactPass219H36StackCacheV1 *cache);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_stack_cache_store(
    HHSExactPass219H36StackCacheV1 *cache,
    const HHSExactPass219H36StackSelectionV1 *fresh_selection);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_stack_cache_lookup(
    const HHSExactPass219H36StackCacheV1 *cache,
    uint64_t workload_signature36,
    uint64_t semantic_result_signature64,
    const char vector_key216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    HHSExactPass219H36StackSelectionV1 *out_selection,
    HHSExactPass219H36StackCacheReceiptV1 *out_receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
    const HHSExactPass219H36StackSelectionV1 *cached_selection,
    const HHSExactPass219H36StackSelectionV1 *fresh_selection);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_stack_cache_receipt_validate(
    const HHSExactPass219H36StackCacheV1 *cache,
    const HHSExactPass219H36StackCacheReceiptV1 *receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_stack_cache_validate(
    const HHSExactPass219H36StackCacheV1 *cache);

#ifdef __cplusplus
}
#endif
#endif
