#include "../include/hhs_pass219_harmonic36_stack_selection_cache_1_11.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static uint64_t h36_stack_cache_mix64(uint64_t x) {
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30U)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27U)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31U);
}

static int h36_stack_cache_key_valid(
    const char key[HHS_EXACT_UQCEL_HASH216_STRLEN]
) {
    size_t i;
    if (key == NULL ||
        key[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        if (strchr(HHS_EXACT_HASH72_ALPHABET, key[i]) == NULL)
            return 0;
    }
    return 1;
}

static uint64_t h36_stack_cache_entry_signature(
    const HHSExactPass219H36StackSelectionV1 *selection,
    uint64_t sequence
) {
    size_t i;
    uint64_t sig =
        h36_stack_cache_mix64(
            selection->workload_signature36 ^
            selection->semantic_result_signature64 ^
            ((uint64_t)selection->selected_candidate_id << 32U) ^
            (uint64_t)selection->selected_stack_kind ^
            sequence
        );
    sig = h36_stack_cache_mix64(sig ^ selection->selected_median_ns);
    sig = h36_stack_cache_mix64(sig ^ selection->runner_up_median_ns);
    sig = h36_stack_cache_mix64(sig ^ selection->speedup_x1000);
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        sig = h36_stack_cache_mix64(
            sig ^
            ((uint64_t)(uint8_t)selection->selected_vector_key216[i] <<
             ((i % 8U) * 8U)) ^
            (uint64_t)(i + 1U)
        );
    }
    return sig == 0U ? UINT64_C(1) : sig;
}

static uint64_t h36_stack_cache_replay_signature(
    const HHSExactPass219H36StackCacheEntryV1 *entry,
    uint32_t entry_index
) {
    uint64_t sig =
        h36_stack_cache_mix64(
            entry->entry_signature64 ^
            entry->sequence ^
            ((uint64_t)entry_index << 48U) ^
            entry->selection.workload_signature36
        );
    sig = h36_stack_cache_mix64(
        sig ^ entry->selection.semantic_result_signature64);
    return sig == 0U ? UINT64_C(1) : sig;
}

static int h36_stack_cache_exact_identity(
    const HHSExactPass219H36StackCacheEntryV1 *entry,
    uint64_t workload_signature36,
    uint64_t semantic_result_signature64,
    const char key[HHS_EXACT_UQCEL_HASH216_STRLEN]
) {
    return entry->occupied == 1U &&
           entry->selection.workload_signature36 ==
               workload_signature36 &&
           entry->selection.semantic_result_signature64 ==
               semantic_result_signature64 &&
           memcmp(
               entry->selection.selected_vector_key216,
               key,
               HHS_EXACT_UQCEL_HASH216_STRLEN
           ) == 0;
}

static int h36_stack_cache_partial_collision(
    const HHSExactPass219H36StackCacheEntryV1 *entry,
    uint64_t workload_signature36,
    uint64_t semantic_result_signature64,
    const char key[HHS_EXACT_UQCEL_HASH216_STRLEN]
) {
    int workload_match;
    int result_match;
    int key_match;
    if (entry->occupied != 1U)
        return 0;
    workload_match =
        entry->selection.workload_signature36 ==
        workload_signature36;
    result_match =
        entry->selection.semantic_result_signature64 ==
        semantic_result_signature64;
    key_match =
        memcmp(
            entry->selection.selected_vector_key216,
            key,
            HHS_EXACT_UQCEL_HASH216_STRLEN
        ) == 0;
    return (workload_match || result_match || key_match) &&
           !(workload_match && result_match && key_match);
}

HHSExactStatus hhs_exact_pass219_h36_stack_cache_init(
    HHSExactPass219H36StackCacheV1 *cache
) {
    if (cache == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(cache, 0, sizeof(*cache));
    cache->struct_size = (uint32_t)sizeof(*cache);
    cache->version = HHS_EXACT_PASS219_H36_STACK_CACHE_VERSION;
    cache->capacity = HHS_EXACT_PASS219_H36_STACK_CACHE_CAPACITY;
    cache->next_sequence = UINT64_C(1);
    cache->candidate_only = 1U;
    cache->vector_store_metadata_only = 1U;
    cache->hash216_lineage_claim = 0U;
    cache->canonical_mutation_authority = 0U;
    cache->canonical_hash72_authority = 0U;
    cache->canonical_hash216_authority = 0U;
    cache->canonical_persistence_authority = 0U;
    cache->floating_point_authority = 0U;
    return hhs_exact_pass219_h36_stack_cache_validate(cache);
}

HHSExactStatus hhs_exact_pass219_h36_stack_cache_store(
    HHSExactPass219H36StackCacheV1 *cache,
    const HHSExactPass219H36StackSelectionV1 *fresh_selection
) {
    uint32_t i;
    uint32_t first_empty = HHS_EXACT_PASS219_H36_STACK_CACHE_CAPACITY;
    HHSExactStatus status;
    HHSExactPass219H36StackCacheEntryV1 *entry;

    if (cache == NULL || fresh_selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_h36_stack_cache_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_h36_stack_selection_validate(
        fresh_selection);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    for (i = 0U; i < cache->capacity; ++i) {
        entry = &cache->entries[i];
        if (entry->occupied == 0U) {
            if (first_empty == cache->capacity)
                first_empty = i;
            continue;
        }
        if (h36_stack_cache_exact_identity(
                entry,
                fresh_selection->workload_signature36,
                fresh_selection->semantic_result_signature64,
                fresh_selection->selected_vector_key216)) {
            if (memcmp(
                    &entry->selection,
                    fresh_selection,
                    sizeof(*fresh_selection)) != 0)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            return HHS_EXACT_STATUS_OK;
        }
        if (h36_stack_cache_partial_collision(
                entry,
                fresh_selection->workload_signature36,
                fresh_selection->semantic_result_signature64,
                fresh_selection->selected_vector_key216))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (first_empty == cache->capacity)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    entry = &cache->entries[first_empty];
    memset(entry, 0, sizeof(*entry));
    entry->struct_size = (uint32_t)sizeof(*entry);
    entry->version = HHS_EXACT_PASS219_H36_STACK_CACHE_VERSION;
    entry->sequence = cache->next_sequence;
    entry->occupied = 1U;
    entry->candidate_only = 1U;
    entry->vector_store_metadata_only = 1U;
    entry->hash216_lineage_claim = 0U;
    entry->canonical_mutation_authority = 0U;
    entry->canonical_hash72_authority = 0U;
    entry->canonical_hash216_authority = 0U;
    entry->canonical_persistence_authority = 0U;
    memcpy(&entry->selection, fresh_selection, sizeof(*fresh_selection));
    entry->entry_signature64 =
        h36_stack_cache_entry_signature(
            &entry->selection, entry->sequence);
    cache->entry_count += 1U;
    cache->next_sequence += UINT64_C(1);

    return hhs_exact_pass219_h36_stack_cache_validate(cache);
}

HHSExactStatus hhs_exact_pass219_h36_stack_cache_lookup(
    const HHSExactPass219H36StackCacheV1 *cache,
    uint64_t workload_signature36,
    uint64_t semantic_result_signature64,
    const char vector_key216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    HHSExactPass219H36StackSelectionV1 *out_selection,
    HHSExactPass219H36StackCacheReceiptV1 *out_receipt
) {
    uint32_t i;
    HHSExactStatus status;
    const HHSExactPass219H36StackCacheEntryV1 *entry = NULL;
    uint32_t entry_index = 0U;

    if (cache == NULL || vector_key216 == NULL ||
        out_selection == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_h36_stack_cache_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (workload_signature36 == 0U ||
        (workload_signature36 & ~HHS_EXACT_PASS219_H36_WORD_MASK) != 0U ||
        semantic_result_signature64 == 0U ||
        !h36_stack_cache_key_valid(vector_key216))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < cache->capacity; ++i) {
        if (h36_stack_cache_exact_identity(
                &cache->entries[i],
                workload_signature36,
                semantic_result_signature64,
                vector_key216)) {
            entry = &cache->entries[i];
            entry_index = i;
            break;
        }
        if (h36_stack_cache_partial_collision(
                &cache->entries[i],
                workload_signature36,
                semantic_result_signature64,
                vector_key216))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    if (entry == NULL)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memcpy(out_selection, &entry->selection, sizeof(*out_selection));
    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_H36_STACK_CACHE_VERSION;
    out_receipt->entry_index = entry_index;
    out_receipt->selected_candidate_id =
        entry->selection.selected_candidate_id;
    out_receipt->selected_stack_kind =
        entry->selection.selected_stack_kind;
    out_receipt->sequence = entry->sequence;
    out_receipt->workload_signature36 =
        entry->selection.workload_signature36;
    out_receipt->semantic_result_signature64 =
        entry->selection.semantic_result_signature64;
    out_receipt->entry_signature64 = entry->entry_signature64;
    out_receipt->replay_signature64 =
        h36_stack_cache_replay_signature(entry, entry_index);
    out_receipt->cache_hit = 1U;
    out_receipt->selection_integrity_validated = 1U;
    out_receipt->exact_replayable = 1U;
    out_receipt->stale_signature_rejected = 1U;
    out_receipt->candidate_only = 1U;
    out_receipt->vector_store_metadata_only = 1U;
    out_receipt->hash216_lineage_claim = 0U;
    out_receipt->canonical_mutation_authority = 0U;
    out_receipt->canonical_hash72_authority = 0U;
    out_receipt->canonical_hash216_authority = 0U;
    out_receipt->canonical_persistence_authority = 0U;
    out_receipt->floating_point_authority = 0U;
    memcpy(
        out_receipt->vector_key216,
        entry->selection.selected_vector_key216,
        sizeof(out_receipt->vector_key216));

    return hhs_exact_pass219_h36_stack_cache_receipt_validate(
        cache, out_receipt);
}

HHSExactStatus hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
    const HHSExactPass219H36StackSelectionV1 *cached_selection,
    const HHSExactPass219H36StackSelectionV1 *fresh_selection
) {
    HHSExactStatus status;
    if (cached_selection == NULL || fresh_selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_h36_stack_selection_validate(
        cached_selection);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_h36_stack_selection_validate(
        fresh_selection);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (memcmp(
            cached_selection,
            fresh_selection,
            sizeof(*cached_selection)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_stack_cache_receipt_validate(
    const HHSExactPass219H36StackCacheV1 *cache,
    const HHSExactPass219H36StackCacheReceiptV1 *receipt
) {
    const HHSExactPass219H36StackCacheEntryV1 *entry;
    HHSExactStatus status;
    if (cache == NULL || receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_h36_stack_cache_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (receipt->struct_size != sizeof(*receipt) ||
        receipt->version != HHS_EXACT_PASS219_H36_STACK_CACHE_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (receipt->entry_index >= cache->capacity)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    entry = &cache->entries[receipt->entry_index];
    if (entry->occupied != 1U ||
        receipt->selected_candidate_id !=
            entry->selection.selected_candidate_id ||
        receipt->selected_stack_kind !=
            entry->selection.selected_stack_kind ||
        receipt->sequence != entry->sequence ||
        receipt->workload_signature36 !=
            entry->selection.workload_signature36 ||
        receipt->semantic_result_signature64 !=
            entry->selection.semantic_result_signature64 ||
        receipt->entry_signature64 != entry->entry_signature64 ||
        receipt->replay_signature64 !=
            h36_stack_cache_replay_signature(
                entry, receipt->entry_index) ||
        receipt->cache_hit != 1U ||
        receipt->selection_integrity_validated != 1U ||
        receipt->exact_replayable != 1U ||
        receipt->stale_signature_rejected != 1U ||
        receipt->candidate_only != 1U ||
        receipt->vector_store_metadata_only != 1U ||
        receipt->hash216_lineage_claim != 0U ||
        receipt->canonical_mutation_authority != 0U ||
        receipt->canonical_hash72_authority != 0U ||
        receipt->canonical_hash216_authority != 0U ||
        receipt->canonical_persistence_authority != 0U ||
        receipt->floating_point_authority != 0U ||
        memcmp(
            receipt->vector_key216,
            entry->selection.selected_vector_key216,
            HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_stack_cache_validate(
    const HHSExactPass219H36StackCacheV1 *cache
) {
    uint32_t i;
    uint32_t occupied = 0U;
    uint64_t max_sequence = 0U;
    if (cache == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (cache->struct_size != sizeof(*cache) ||
        cache->version != HHS_EXACT_PASS219_H36_STACK_CACHE_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (cache->capacity != HHS_EXACT_PASS219_H36_STACK_CACHE_CAPACITY ||
        cache->entry_count > cache->capacity ||
        cache->next_sequence == 0U ||
        cache->candidate_only != 1U ||
        cache->vector_store_metadata_only != 1U ||
        cache->hash216_lineage_claim != 0U ||
        cache->canonical_mutation_authority != 0U ||
        cache->canonical_hash72_authority != 0U ||
        cache->canonical_hash216_authority != 0U ||
        cache->canonical_persistence_authority != 0U ||
        cache->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < cache->capacity; ++i) {
        const HHSExactPass219H36StackCacheEntryV1 *entry =
            &cache->entries[i];
        if (entry->occupied == 0U)
            continue;
        occupied += 1U;
        if (entry->struct_size != sizeof(*entry) ||
            entry->version != HHS_EXACT_PASS219_H36_STACK_CACHE_VERSION ||
            entry->sequence == 0U ||
            entry->candidate_only != 1U ||
            entry->vector_store_metadata_only != 1U ||
            entry->hash216_lineage_claim != 0U ||
            entry->canonical_mutation_authority != 0U ||
            entry->canonical_hash72_authority != 0U ||
            entry->canonical_hash216_authority != 0U ||
            entry->canonical_persistence_authority != 0U ||
            hhs_exact_pass219_h36_stack_selection_validate(
                &entry->selection) != HHS_EXACT_STATUS_OK ||
            entry->entry_signature64 !=
                h36_stack_cache_entry_signature(
                    &entry->selection, entry->sequence))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (entry->sequence > max_sequence)
            max_sequence = entry->sequence;
    }
    if (occupied != cache->entry_count ||
        cache->next_sequence <= max_sequence)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < cache->capacity; ++i) {
        uint32_t j;
        const HHSExactPass219H36StackCacheEntryV1 *left =
            &cache->entries[i];
        if (left->occupied != 1U)
            continue;
        for (j = i + 1U; j < cache->capacity; ++j) {
            const HHSExactPass219H36StackCacheEntryV1 *right =
                &cache->entries[j];
            if (right->occupied != 1U)
                continue;
            if (left->sequence == right->sequence)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            if (h36_stack_cache_exact_identity(
                    right,
                    left->selection.workload_signature36,
                    left->selection.semantic_result_signature64,
                    left->selection.selected_vector_key216) ||
                h36_stack_cache_partial_collision(
                    right,
                    left->selection.workload_signature36,
                    left->selection.semantic_result_signature64,
                    left->selection.selected_vector_key216))
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }
    return HHS_EXACT_STATUS_OK;
}
