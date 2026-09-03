#include "../include/hhs_pass219_harmonic36_branch_reference_cache_1_17.h"

#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static uint64_t h36_branch_ref_mix64(uint64_t x) {
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30U)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27U)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31U);
}

static uint16_t h36_branch_ref_fib(uint16_t index) {
    static const uint16_t values[
        HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_BUCKETS] = {
        UINT16_C(0),
        UINT16_C(1),
        UINT16_C(1),
        UINT16_C(2),
        UINT16_C(3),
        UINT16_C(5),
        UINT16_C(8),
        UINT16_C(13),
        UINT16_C(21),
        UINT16_C(34),
        UINT16_C(55),
        UINT16_C(89),
        UINT16_C(144)
    };
    if (index >= HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_BUCKETS)
        return UINT16_C(0);
    return values[index];
}

static uint64_t h36_branch_ref_parent_entry_signature(
    const HHSExactPass219H36StackCacheEntryV1 *entry
) {
    const HHSExactPass219H36StackSelectionV1 *selection;
    size_t i;
    uint64_t sig;

    if (entry == NULL || entry->occupied != 1U)
        return UINT64_C(0);
    selection = &entry->selection;
    sig = h36_branch_ref_mix64(
        selection->workload_signature36 ^
        selection->semantic_result_signature64 ^
        ((uint64_t)selection->selected_candidate_id << 32U) ^
        (uint64_t)selection->selected_stack_kind ^
        entry->sequence);
    sig = h36_branch_ref_mix64(sig ^ selection->selected_median_ns);
    sig = h36_branch_ref_mix64(sig ^ selection->runner_up_median_ns);
    sig = h36_branch_ref_mix64(sig ^ selection->speedup_x1000);
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        sig = h36_branch_ref_mix64(
            sig ^
            ((uint64_t)(uint8_t)selection->selected_vector_key216[i] <<
             ((i % 8U) * 8U)) ^
            (uint64_t)(i + 1U));
    }
    return sig == 0U ? UINT64_C(1) : sig;
}

static uint64_t h36_branch_ref_parent_cache_signature(
    const HHSExactPass219H36StackCacheV1 *parent_cache
) {
    uint32_t i;
    uint64_t sig;

    if (parent_cache == NULL)
        return UINT64_C(0);
    sig = h36_branch_ref_mix64(
        parent_cache->next_sequence ^
        ((uint64_t)parent_cache->entry_count << 32U) ^
        (uint64_t)parent_cache->capacity);
    for (i = 0U; i < parent_cache->capacity; ++i) {
        const HHSExactPass219H36StackCacheEntryV1 *entry =
            &parent_cache->entries[i];
        if (entry->occupied != 1U)
            continue;
        sig = h36_branch_ref_mix64(
            sig ^
            h36_branch_ref_parent_entry_signature(entry) ^
            entry->entry_signature64 ^
            entry->sequence ^
            ((uint64_t)i << 48U));
    }
    return sig == 0U ? UINT64_C(1) : sig;
}

static HHSExactStatus h36_branch_ref_parent_header_validate(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *parent_cache
) {
    if (cache == NULL || parent_cache == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (parent_cache->struct_size != sizeof(*parent_cache) ||
        parent_cache->version !=
            HHS_EXACT_PASS219_H36_STACK_CACHE_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (parent_cache->capacity !=
            HHS_EXACT_PASS219_H36_STACK_CACHE_CAPACITY ||
        parent_cache->entry_count !=
            cache->frozen_parent_entry_count ||
        parent_cache->next_sequence !=
            cache->frozen_parent_next_sequence ||
        parent_cache->candidate_only != 1U ||
        parent_cache->vector_store_metadata_only != 1U ||
        parent_cache->hash216_lineage_claim != 0U ||
        parent_cache->canonical_mutation_authority != 0U ||
        parent_cache->canonical_hash72_authority != 0U ||
        parent_cache->canonical_hash216_authority != 0U ||
        parent_cache->canonical_persistence_authority != 0U ||
        parent_cache->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_branch_ref_parent_entry_validate_fast(
    const HHSExactPass219H36StackCacheV1 *parent_cache,
    uint32_t parent_slot,
    uint64_t expected_signature64
) {
    const HHSExactPass219H36StackCacheEntryV1 *entry;

    if (parent_cache == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (parent_slot >= parent_cache->capacity)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    entry = &parent_cache->entries[parent_slot];
    if (entry->occupied != 1U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (entry->struct_size != sizeof(*entry) ||
        entry->version != HHS_EXACT_PASS219_H36_STACK_CACHE_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (entry->sequence == 0U ||
        entry->entry_signature64 == 0U ||
        entry->candidate_only != 1U ||
        entry->vector_store_metadata_only != 1U ||
        entry->hash216_lineage_claim != 0U ||
        entry->canonical_mutation_authority != 0U ||
        entry->canonical_hash72_authority != 0U ||
        entry->canonical_hash216_authority != 0U ||
        entry->canonical_persistence_authority != 0U ||
        entry->entry_signature64 != expected_signature64)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_branch_ref_parent_entry_validate_full(
    const HHSExactPass219H36StackCacheV1 *parent_cache,
    uint32_t parent_slot,
    uint64_t expected_signature64
) {
    const HHSExactPass219H36StackCacheEntryV1 *entry;
    uint64_t recomputed;
    HHSExactStatus status;

    status = h36_branch_ref_parent_entry_validate_fast(
        parent_cache, parent_slot, expected_signature64);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    entry = &parent_cache->entries[parent_slot];
    recomputed = h36_branch_ref_parent_entry_signature(entry);
    if (recomputed == 0U ||
        recomputed != entry->entry_signature64)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus h36_branch_ref_header_validate(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache
) {
    if (cache == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (cache->struct_size != sizeof(*cache) ||
        cache->version != HHS_EXACT_PASS219_H36_BRANCH_REF_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (cache->capacity !=
            HHS_EXACT_PASS219_H36_BRANCH_REF_CAPACITY ||
        cache->entry_count > cache->capacity ||
        cache->next_sequence !=
            (uint64_t)cache->entry_count + UINT64_C(1) ||
        cache->frozen_parent_signature64 == 0U ||
        cache->branch_reference_only != 1U ||
        cache->append_only_branch_forking != 1U ||
        cache->fibonacci_equivalence_indexed != 1U ||
        cache->adaptive_composition_memoization != 1U ||
        cache->canonical_mutation_authority != 0U ||
        cache->canonical_hash72_authority != 0U ||
        cache->canonical_hash216_authority != 0U ||
        cache->canonical_persistence_authority != 0U ||
        cache->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static uint64_t h36_branch_ref_entry_signature(
    const HHSExactPass219H36BranchReferenceEntryV1 *entry
) {
    uint64_t sig;

    if (entry == NULL)
        return UINT64_C(0);
    sig = h36_branch_ref_mix64(
        entry->parent_entry_signature64 ^
        entry->prior_receipt_signature64 ^
        entry->sequence ^
        ((uint64_t)entry->branch_id << 17U) ^
        (uint64_t)entry->previous_branch_id);
    sig = h36_branch_ref_mix64(
        sig ^
        ((uint64_t)entry->previous_fib_member_branch_id << 7U) ^
        ((uint64_t)entry->tile144 << 48U) ^
        ((uint64_t)entry->fib_index << 40U) ^
        ((uint64_t)entry->fib_value << 24U) ^
        ((uint64_t)entry->h36_word144 << 8U) ^
        ((uint64_t)entry->lane_role << 6U) ^
        ((uint64_t)entry->parent_slot << 4U) ^
        ((uint64_t)entry->local_cell36 << 2U) ^
        (uint64_t)entry->child_side ^
        ((uint64_t)entry->depth << 56U));
    return sig == 0U ? UINT64_C(1) : sig;
}

static uint64_t h36_branch_ref_receipt_signature(
    const HHSExactPass219H36BranchReferenceEntryV1 *entry
) {
    uint64_t sig;

    if (entry == NULL)
        return UINT64_C(0);
    sig = h36_branch_ref_mix64(
        entry->entry_signature64 ^
        entry->parent_entry_signature64 ^
        entry->prior_receipt_signature64 ^
        ((uint64_t)entry->branch_id << 32U) ^
        ((uint64_t)entry->fib_value << 16U) ^
        (uint64_t)entry->h36_word144);
    return sig == 0U ? UINT64_C(1) : sig;
}

static uint64_t h36_branch_ref_composition_signature(
    const HHSExactPass219H36BranchReferenceEntryV1 *entry,
    uint8_t target_lane_role
) {
    uint64_t sig;

    if (entry == NULL)
        return UINT64_C(0);
    sig = h36_branch_ref_mix64(
        entry->receipt_signature64 ^
        entry->parent_entry_signature64 ^
        ((uint64_t)entry->lane_role << 56U) ^
        ((uint64_t)target_lane_role << 48U) ^
        (uint64_t)entry->branch_id);
    sig = h36_branch_ref_mix64(
        sig ^
        ((uint64_t)entry->fib_index << 40U) ^
        (uint64_t)entry->previous_branch_id);
    return sig == 0U ? UINT64_C(1) : sig;
}

static HHSExactStatus h36_branch_ref_entry_validate_fast(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *parent_cache,
    uint32_t branch_id
) {
    const HHSExactPass219H36BranchReferenceEntryV1 *entry;
    const HHSExactPass219H36BranchReferenceEntryV1 *previous;
    uint32_t expected_local;
    uint16_t expected_fib_index;
    uint16_t decrement;
    HHSExactStatus status;

    if (branch_id >= cache->entry_count)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    entry = &cache->entries[branch_id];
    if (entry->struct_size != sizeof(*entry) ||
        entry->version != HHS_EXACT_PASS219_H36_BRANCH_REF_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (entry->occupied != 1U ||
        entry->branch_id != branch_id ||
        entry->sequence != (uint64_t)branch_id + UINT64_C(1) ||
        entry->tile144 >=
            HHS_EXACT_PASS219_H36_BRANCH_REF_MAX_TILES ||
        entry->lane_role >=
            HHS_EXACT_PASS219_H36_BRANCH_REF_LANES ||
        entry->parent_slot >= parent_cache->capacity ||
        entry->local_cell36 >=
            HHS_EXACT_PASS219_H36_BRANCH_REF_CELLS_PER_LANE ||
        entry->fib_index >=
            HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_BUCKETS ||
        entry->fib_value != h36_branch_ref_fib(entry->fib_index) ||
        entry->h36_word144 !=
            (uint16_t)(
                (uint16_t)entry->lane_role *
                HHS_EXACT_PASS219_H36_BRANCH_REF_CELLS_PER_LANE +
                (uint16_t)entry->local_cell36) ||
        entry->branch_reference_only != 1U ||
        entry->exact_replayable != 1U ||
        entry->canonical_mutation_authority != 0U ||
        entry->canonical_hash72_authority != 0U ||
        entry->canonical_hash216_authority != 0U ||
        entry->canonical_persistence_authority != 0U ||
        entry->floating_point_authority != 0U ||
        entry->entry_signature64 !=
            h36_branch_ref_entry_signature(entry) ||
        entry->receipt_signature64 !=
            h36_branch_ref_receipt_signature(entry))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = h36_branch_ref_parent_entry_validate_fast(
        parent_cache,
        entry->parent_slot,
        entry->parent_entry_signature64);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (entry->previous_fib_member_branch_id !=
            HHS_EXACT_PASS219_H36_BRANCH_REF_NONE &&
        entry->previous_fib_member_branch_id >= branch_id)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (entry->previous_branch_id ==
        HHS_EXACT_PASS219_H36_BRANCH_REF_NONE) {
        if (entry->child_side !=
                HHS_EXACT_PASS219_H36_BRANCH_CHILD_ROOT ||
            entry->local_cell36 != 0U ||
            entry->depth != 0U ||
            entry->fib_index !=
                HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_ROOT_INDEX ||
            entry->fib_value !=
                HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_ROOT_VALUE ||
            entry->prior_receipt_signature64 !=
                entry->parent_entry_signature64 ||
            cache->root_branch_id[entry->tile144][entry->lane_role] !=
                branch_id)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        return HHS_EXACT_STATUS_OK;
    }

    if (entry->previous_branch_id >= branch_id)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    previous = &cache->entries[entry->previous_branch_id];
    if (previous->occupied != 1U ||
        previous->tile144 != entry->tile144 ||
        previous->lane_role != entry->lane_role ||
        previous->parent_slot != entry->parent_slot ||
        previous->parent_entry_signature64 !=
            entry->parent_entry_signature64 ||
        entry->prior_receipt_signature64 !=
            previous->receipt_signature64 ||
        entry->depth != (uint8_t)(previous->depth + 1U))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (entry->child_side ==
        HHS_EXACT_PASS219_H36_BRANCH_CHILD_LEFT) {
        expected_local =
            (uint32_t)previous->local_cell36 * UINT32_C(2) +
            UINT32_C(1);
        decrement = UINT16_C(1);
        if (cache->left_child_branch_id[
                entry->previous_branch_id] != branch_id)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    } else if (entry->child_side ==
               HHS_EXACT_PASS219_H36_BRANCH_CHILD_RIGHT) {
        expected_local =
            (uint32_t)previous->local_cell36 * UINT32_C(2) +
            UINT32_C(2);
        decrement = UINT16_C(2);
        if (cache->right_child_branch_id[
                entry->previous_branch_id] != branch_id)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    } else {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (expected_local >=
            HHS_EXACT_PASS219_H36_BRANCH_REF_CELLS_PER_LANE ||
        previous->fib_index <= decrement)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    expected_fib_index =
        (uint16_t)(previous->fib_index - decrement);
    if (entry->local_cell36 != (uint8_t)expected_local ||
        entry->fib_index != expected_fib_index)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

static void h36_branch_ref_fill_receipt(
    const HHSExactPass219H36BranchReferenceEntryV1 *entry,
    HHSExactPass219H36BranchReceiptV1 *receipt
) {
    memset(receipt, 0, sizeof(*receipt));
    receipt->struct_size = (uint32_t)sizeof(*receipt);
    receipt->version = HHS_EXACT_PASS219_H36_BRANCH_REF_VERSION;
    receipt->branch_id = entry->branch_id;
    receipt->previous_branch_id = entry->previous_branch_id;
    receipt->sequence = entry->sequence;
    receipt->parent_entry_signature64 =
        entry->parent_entry_signature64;
    receipt->prior_receipt_signature64 =
        entry->prior_receipt_signature64;
    receipt->entry_signature64 = entry->entry_signature64;
    receipt->receipt_signature64 = entry->receipt_signature64;
    receipt->tile144 = entry->tile144;
    receipt->fib_index = entry->fib_index;
    receipt->fib_value = entry->fib_value;
    receipt->h36_word144 = entry->h36_word144;
    receipt->lane_role = entry->lane_role;
    receipt->parent_slot = entry->parent_slot;
    receipt->local_cell36 = entry->local_cell36;
    receipt->child_side = entry->child_side;
    receipt->depth = entry->depth;
    receipt->frozen_parent_validated = 1U;
    receipt->exact_replayable = 1U;
    receipt->reversible_to_root = 1U;
    receipt->fibonacci_identity_preserved = 1U;
    receipt->branch_reference_only = 1U;
    receipt->canonical_mutation_authority = 0U;
    receipt->canonical_hash72_authority = 0U;
    receipt->canonical_hash216_authority = 0U;
    receipt->canonical_persistence_authority = 0U;
    receipt->floating_point_authority = 0U;
}

static HHSExactStatus h36_branch_ref_append(
    HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *parent_cache,
    uint32_t parent_slot,
    uint8_t lane_role,
    uint16_t tile144,
    uint32_t previous_branch_id,
    uint8_t child_side,
    uint32_t *out_branch_id,
    HHSExactPass219H36BranchReceiptV1 *out_receipt
) {
    HHSExactPass219H36BranchReferenceEntryV1 *entry;
    const HHSExactPass219H36BranchReferenceEntryV1 *previous = NULL;
    uint32_t branch_id;
    uint32_t local_cell = 0U;
    uint16_t fib_index =
        HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_ROOT_INDEX;
    uint8_t depth = 0U;
    uint64_t prior_receipt_signature64;
    uint16_t decrement = UINT16_C(0);
    HHSExactStatus status;

    status = h36_branch_ref_header_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = h36_branch_ref_parent_header_validate(
        cache, parent_cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (out_branch_id == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (cache->entry_count >= cache->capacity)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    if (parent_slot >= parent_cache->capacity ||
        lane_role >= HHS_EXACT_PASS219_H36_BRANCH_REF_LANES ||
        tile144 >= HHS_EXACT_PASS219_H36_BRANCH_REF_MAX_TILES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    status = h36_branch_ref_parent_entry_validate_fast(
        parent_cache,
        parent_slot,
        parent_cache->entries[parent_slot].entry_signature64);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (previous_branch_id ==
        HHS_EXACT_PASS219_H36_BRANCH_REF_NONE) {
        if (child_side !=
            HHS_EXACT_PASS219_H36_BRANCH_CHILD_ROOT)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (cache->root_branch_id[tile144][lane_role] !=
            HHS_EXACT_PASS219_H36_BRANCH_REF_NONE)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        prior_receipt_signature64 =
            parent_cache->entries[parent_slot].entry_signature64;
    } else {
        if (previous_branch_id >= cache->entry_count)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        previous = &cache->entries[previous_branch_id];
        status = h36_branch_ref_entry_validate_fast(
            cache, parent_cache, previous_branch_id);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        if (parent_slot != previous->parent_slot ||
            lane_role != previous->lane_role ||
            tile144 != previous->tile144)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        if (child_side ==
            HHS_EXACT_PASS219_H36_BRANCH_CHILD_LEFT) {
            if (cache->left_child_branch_id[
                    previous_branch_id] !=
                HHS_EXACT_PASS219_H36_BRANCH_REF_NONE)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            local_cell =
                (uint32_t)previous->local_cell36 * UINT32_C(2) +
                UINT32_C(1);
            decrement = UINT16_C(1);
        } else if (child_side ==
                   HHS_EXACT_PASS219_H36_BRANCH_CHILD_RIGHT) {
            if (cache->right_child_branch_id[
                    previous_branch_id] !=
                HHS_EXACT_PASS219_H36_BRANCH_REF_NONE)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            local_cell =
                (uint32_t)previous->local_cell36 * UINT32_C(2) +
                UINT32_C(2);
            decrement = UINT16_C(2);
        } else {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        if (local_cell >=
                HHS_EXACT_PASS219_H36_BRANCH_REF_CELLS_PER_LANE ||
            previous->fib_index <= decrement)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        fib_index = (uint16_t)(previous->fib_index - decrement);
        depth = (uint8_t)(previous->depth + 1U);
        prior_receipt_signature64 =
            previous->receipt_signature64;
    }

    branch_id = cache->entry_count;
    entry = &cache->entries[branch_id];
    memset(entry, 0, sizeof(*entry));
    entry->struct_size = (uint32_t)sizeof(*entry);
    entry->version = HHS_EXACT_PASS219_H36_BRANCH_REF_VERSION;
    entry->branch_id = branch_id;
    entry->previous_branch_id = previous_branch_id;
    entry->previous_fib_member_branch_id =
        cache->fib_bucket_head[fib_index];
    entry->sequence = cache->next_sequence;
    entry->parent_entry_signature64 =
        parent_cache->entries[parent_slot].entry_signature64;
    entry->prior_receipt_signature64 =
        prior_receipt_signature64;
    entry->tile144 = tile144;
    entry->fib_index = fib_index;
    entry->fib_value = h36_branch_ref_fib(fib_index);
    entry->h36_word144 =
        (uint16_t)(
            (uint16_t)lane_role *
            HHS_EXACT_PASS219_H36_BRANCH_REF_CELLS_PER_LANE +
            (uint16_t)local_cell);
    entry->lane_role = lane_role;
    entry->parent_slot = (uint8_t)parent_slot;
    entry->local_cell36 = (uint8_t)local_cell;
    entry->child_side = child_side;
    entry->depth = depth;
    entry->occupied = 1U;
    entry->branch_reference_only = 1U;
    entry->exact_replayable = 1U;
    entry->canonical_mutation_authority = 0U;
    entry->canonical_hash72_authority = 0U;
    entry->canonical_hash216_authority = 0U;
    entry->canonical_persistence_authority = 0U;
    entry->floating_point_authority = 0U;
    entry->entry_signature64 =
        h36_branch_ref_entry_signature(entry);
    entry->receipt_signature64 =
        h36_branch_ref_receipt_signature(entry);

    cache->fib_bucket_head[fib_index] = branch_id;
    cache->fib_bucket_count[fib_index] += UINT32_C(1);
    if (previous_branch_id ==
        HHS_EXACT_PASS219_H36_BRANCH_REF_NONE) {
        cache->root_branch_id[tile144][lane_role] = branch_id;
    } else if (child_side ==
               HHS_EXACT_PASS219_H36_BRANCH_CHILD_LEFT) {
        cache->left_child_branch_id[previous_branch_id] = branch_id;
    } else {
        cache->right_child_branch_id[previous_branch_id] = branch_id;
    }
    cache->entry_count += UINT32_C(1);
    cache->next_sequence += UINT64_C(1);

    *out_branch_id = branch_id;
    h36_branch_ref_fill_receipt(entry, out_receipt);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_branch_ref_cache_init(
    HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache
) {
    uint32_t i;
    uint32_t tile;
    uint32_t lane;
    HHSExactStatus status;

    if (cache == NULL || frozen_parent_cache == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_h36_stack_cache_validate(
        frozen_parent_cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(cache, 0, sizeof(*cache));
    cache->struct_size = (uint32_t)sizeof(*cache);
    cache->version = HHS_EXACT_PASS219_H36_BRANCH_REF_VERSION;
    cache->capacity = HHS_EXACT_PASS219_H36_BRANCH_REF_CAPACITY;
    cache->next_sequence = UINT64_C(1);
    cache->frozen_parent_signature64 =
        h36_branch_ref_parent_cache_signature(frozen_parent_cache);
    cache->frozen_parent_entry_count =
        frozen_parent_cache->entry_count;
    cache->frozen_parent_next_sequence =
        frozen_parent_cache->next_sequence;
    cache->branch_reference_only = 1U;
    cache->append_only_branch_forking = 1U;
    cache->fibonacci_equivalence_indexed = 1U;
    cache->adaptive_composition_memoization = 1U;
    cache->canonical_mutation_authority = 0U;
    cache->canonical_hash72_authority = 0U;
    cache->canonical_hash216_authority = 0U;
    cache->canonical_persistence_authority = 0U;
    cache->floating_point_authority = 0U;

    for (tile = 0U;
         tile < HHS_EXACT_PASS219_H36_BRANCH_REF_MAX_TILES;
         ++tile) {
        for (lane = 0U;
             lane < HHS_EXACT_PASS219_H36_BRANCH_REF_LANES;
             ++lane) {
            cache->root_branch_id[tile][lane] =
                HHS_EXACT_PASS219_H36_BRANCH_REF_NONE;
        }
    }
    for (i = 0U;
         i < HHS_EXACT_PASS219_H36_BRANCH_REF_CAPACITY;
         ++i) {
        cache->left_child_branch_id[i] =
            HHS_EXACT_PASS219_H36_BRANCH_REF_NONE;
        cache->right_child_branch_id[i] =
            HHS_EXACT_PASS219_H36_BRANCH_REF_NONE;
    }
    for (i = 0U;
         i < HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_BUCKETS;
         ++i) {
        cache->fib_bucket_head[i] =
            HHS_EXACT_PASS219_H36_BRANCH_REF_NONE;
        cache->fib_bucket_count[i] = UINT32_C(0);
    }

    return hhs_exact_pass219_h36_branch_ref_cache_validate(
        cache, frozen_parent_cache);
}

HHSExactStatus hhs_exact_pass219_h36_branch_ref_root(
    HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t parent_slot,
    uint8_t lane_role,
    uint16_t tile144,
    uint32_t *out_branch_id,
    HHSExactPass219H36BranchReceiptV1 *out_receipt
) {
    return h36_branch_ref_append(
        cache,
        frozen_parent_cache,
        parent_slot,
        lane_role,
        tile144,
        HHS_EXACT_PASS219_H36_BRANCH_REF_NONE,
        HHS_EXACT_PASS219_H36_BRANCH_CHILD_ROOT,
        out_branch_id,
        out_receipt);
}

HHSExactStatus hhs_exact_pass219_h36_branch_ref_fork(
    HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t previous_branch_id,
    uint8_t child_side,
    uint32_t *out_branch_id,
    HHSExactPass219H36BranchReceiptV1 *out_receipt
) {
    const HHSExactPass219H36BranchReferenceEntryV1 *previous;
    HHSExactStatus status;

    if (cache == NULL || frozen_parent_cache == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = h36_branch_ref_header_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (previous_branch_id >= cache->entry_count)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    previous = &cache->entries[previous_branch_id];
    return h36_branch_ref_append(
        cache,
        frozen_parent_cache,
        previous->parent_slot,
        previous->lane_role,
        previous->tile144,
        previous_branch_id,
        child_side,
        out_branch_id,
        out_receipt);
}

HHSExactStatus hhs_exact_pass219_h36_branch_ref_resolve(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t branch_id,
    const HHSExactPass219H36StackSelectionV1 **out_parent_selection,
    HHSExactPass219H36BranchReceiptV1 *out_receipt
) {
    const HHSExactPass219H36BranchReferenceEntryV1 *entry;
    HHSExactStatus status;

    if (out_parent_selection == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = h36_branch_ref_header_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = h36_branch_ref_parent_header_validate(
        cache, frozen_parent_cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = h36_branch_ref_entry_validate_fast(
        cache, frozen_parent_cache, branch_id);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    entry = &cache->entries[branch_id];
    *out_parent_selection =
        &frozen_parent_cache->entries[entry->parent_slot].selection;
    h36_branch_ref_fill_receipt(entry, out_receipt);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_branch_ref_equivalent(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    uint16_t fib_index,
    uint32_t *out_branch_ids,
    size_t out_capacity,
    size_t *out_count
) {
    uint32_t branch_id;
    size_t count = 0U;
    HHSExactStatus status;

    if (out_count == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = h36_branch_ref_header_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (fib_index >=
        HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_BUCKETS)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    *out_count = (size_t)cache->fib_bucket_count[fib_index];
    if (*out_count != 0U && out_branch_ids == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (out_capacity < *out_count)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    branch_id = cache->fib_bucket_head[fib_index];
    while (branch_id !=
           HHS_EXACT_PASS219_H36_BRANCH_REF_NONE) {
        const HHSExactPass219H36BranchReferenceEntryV1 *entry;
        if (branch_id >= cache->entry_count ||
            count >= *out_count)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        entry = &cache->entries[branch_id];
        if (entry->occupied != 1U ||
            entry->fib_index != fib_index)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out_branch_ids[count++] = branch_id;
        branch_id = entry->previous_fib_member_branch_id;
    }
    if (count != *out_count)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_branch_ref_reverse_to_root(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t branch_id,
    uint32_t *out_root_branch_id,
    uint32_t *out_steps
) {
    uint32_t current;
    uint32_t steps = 0U;
    HHSExactStatus status;

    if (out_root_branch_id == NULL || out_steps == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = h36_branch_ref_header_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = h36_branch_ref_parent_header_validate(
        cache, frozen_parent_cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (branch_id >= cache->entry_count)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    current = branch_id;
    while (1) {
        const HHSExactPass219H36BranchReferenceEntryV1 *entry;
        status = h36_branch_ref_entry_validate_fast(
            cache, frozen_parent_cache, current);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        entry = &cache->entries[current];
        if (entry->previous_branch_id ==
            HHS_EXACT_PASS219_H36_BRANCH_REF_NONE) {
            *out_root_branch_id = current;
            *out_steps = steps;
            return HHS_EXACT_STATUS_OK;
        }
        if (steps >=
            HHS_EXACT_PASS219_H36_BRANCH_REF_CELLS_PER_LANE)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        current = entry->previous_branch_id;
        steps += UINT32_C(1);
    }
}

uint32_t hhs_exact_pass219_h36_branch_ref_memo_threshold(
    uint32_t active_branch_count
) {
    if (active_branch_count <= UINT32_C(144))
        return UINT32_C(3172);
    if (active_branch_count <= UINT32_C(288))
        return UINT32_C(6254);
    if (active_branch_count <= UINT32_C(576))
        return UINT32_C(12580);
    if (active_branch_count <= UINT32_C(1152))
        return UINT32_C(19774);
    if (active_branch_count <= UINT32_C(2304))
        return UINT32_C(35269);
    return UINT32_C(87572);
}

HHSExactStatus hhs_exact_pass219_h36_branch_ref_composition_receipt(
    HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t branch_id,
    uint8_t target_lane_role,
    HHSExactPass219H36CompositionReceiptMemoV1 *out_receipt
) {
    const HHSExactPass219H36BranchReferenceEntryV1 *entry;
    HHSExactPass219H36BranchMemoStateV1 *memo;
    uint32_t threshold;
    uint32_t count;
    uint8_t bit;
    uint64_t signature64;
    HHSExactStatus status;

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = h36_branch_ref_header_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = h36_branch_ref_parent_header_validate(
        cache, frozen_parent_cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (target_lane_role >=
        HHS_EXACT_PASS219_H36_BRANCH_REF_COMPOSITION_TARGETS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    status = h36_branch_ref_entry_validate_fast(
        cache, frozen_parent_cache, branch_id);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    entry = &cache->entries[branch_id];
    memo = &cache->memo[branch_id];
    bit = (uint8_t)(UINT8_C(1) << target_lane_role);
    threshold =
        hhs_exact_pass219_h36_branch_ref_memo_threshold(
            cache->entry_count);

    if (memo->composition_query_count[target_lane_role] <
        UINT32_MAX) {
        memo->composition_query_count[target_lane_role] += UINT32_C(1);
    }
    count = memo->composition_query_count[target_lane_role];

    if ((memo->composition_memoized_mask & bit) != 0U) {
        signature64 =
            memo->composition_memo_signature64[target_lane_role];
        if (signature64 !=
            h36_branch_ref_composition_signature(
                entry, target_lane_role))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    } else {
        signature64 =
            h36_branch_ref_composition_signature(
                entry, target_lane_role);
        if (count >= threshold) {
            memo->composition_memo_signature64[
                target_lane_role] = signature64;
            memo->composition_memo_threshold_used[
                target_lane_role] = threshold;
            memo->composition_memoized_mask =
                (uint8_t)(
                    memo->composition_memoized_mask | bit);
        }
    }

    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version =
        HHS_EXACT_PASS219_H36_BRANCH_REF_VERSION;
    out_receipt->branch_id = branch_id;
    out_receipt->query_count = count;
    out_receipt->memoization_threshold =
        (memo->composition_memo_threshold_used[target_lane_role] != 0U)
            ? memo->composition_memo_threshold_used[target_lane_role]
            : threshold;
    out_receipt->branch_receipt_signature64 =
        entry->receipt_signature64;
    out_receipt->composition_receipt_signature64 = signature64;
    out_receipt->source_lane_role = entry->lane_role;
    out_receipt->target_lane_role = target_lane_role;
    out_receipt->memoized =
        (uint8_t)(
            (memo->composition_memoized_mask & bit) != 0U);
    out_receipt->exact_replayable = 1U;
    out_receipt->canonical_mutation_authority = 0U;
    out_receipt->canonical_hash72_authority = 0U;
    out_receipt->canonical_hash216_authority = 0U;
    out_receipt->canonical_persistence_authority = 0U;
    out_receipt->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus
hhs_exact_pass219_h36_branch_ref_composition_receipt_validate(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    const HHSExactPass219H36CompositionReceiptMemoV1 *receipt
) {
    const HHSExactPass219H36BranchReferenceEntryV1 *entry;
    const HHSExactPass219H36BranchMemoStateV1 *memo;
    uint8_t bit;
    uint64_t expected;
    HHSExactStatus status;

    if (receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = h36_branch_ref_header_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = h36_branch_ref_parent_header_validate(
        cache, frozen_parent_cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (receipt->struct_size != sizeof(*receipt) ||
        receipt->version !=
            HHS_EXACT_PASS219_H36_BRANCH_REF_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (receipt->branch_id >= cache->entry_count ||
        receipt->target_lane_role >=
            HHS_EXACT_PASS219_H36_BRANCH_REF_COMPOSITION_TARGETS)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    status = h36_branch_ref_entry_validate_fast(
        cache, frozen_parent_cache, receipt->branch_id);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    entry = &cache->entries[receipt->branch_id];
    memo = &cache->memo[receipt->branch_id];
    bit = (uint8_t)(UINT8_C(1) << receipt->target_lane_role);
    expected = h36_branch_ref_composition_signature(
        entry, receipt->target_lane_role);

    if (receipt->branch_receipt_signature64 !=
            entry->receipt_signature64 ||
        receipt->composition_receipt_signature64 != expected ||
        receipt->source_lane_role != entry->lane_role ||
        receipt->query_count == 0U ||
        receipt->query_count >
            memo->composition_query_count[
                receipt->target_lane_role] ||
        receipt->memoization_threshold == 0U ||
        receipt->exact_replayable != 1U ||
        receipt->canonical_mutation_authority != 0U ||
        receipt->canonical_hash72_authority != 0U ||
        receipt->canonical_hash216_authority != 0U ||
        receipt->canonical_persistence_authority != 0U ||
        receipt->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (receipt->memoized != 0U) {
        if ((memo->composition_memoized_mask & bit) == 0U ||
            memo->composition_memo_signature64[
                receipt->target_lane_role] != expected ||
            memo->composition_memo_threshold_used[
                receipt->target_lane_role] !=
                receipt->memoization_threshold ||
            receipt->query_count <
                receipt->memoization_threshold)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_branch_ref_receipt_validate(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    const HHSExactPass219H36BranchReceiptV1 *receipt
) {
    const HHSExactPass219H36BranchReferenceEntryV1 *entry;
    uint32_t root_branch_id;
    uint32_t steps;
    HHSExactStatus status;

    if (receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (receipt->struct_size != sizeof(*receipt) ||
        receipt->version !=
            HHS_EXACT_PASS219_H36_BRANCH_REF_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = h36_branch_ref_header_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = h36_branch_ref_parent_header_validate(
        cache, frozen_parent_cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = h36_branch_ref_entry_validate_fast(
        cache, frozen_parent_cache, receipt->branch_id);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    entry = &cache->entries[receipt->branch_id];

    if (receipt->previous_branch_id != entry->previous_branch_id ||
        receipt->sequence != entry->sequence ||
        receipt->parent_entry_signature64 !=
            entry->parent_entry_signature64 ||
        receipt->prior_receipt_signature64 !=
            entry->prior_receipt_signature64 ||
        receipt->entry_signature64 != entry->entry_signature64 ||
        receipt->receipt_signature64 !=
            entry->receipt_signature64 ||
        receipt->tile144 != entry->tile144 ||
        receipt->fib_index != entry->fib_index ||
        receipt->fib_value != entry->fib_value ||
        receipt->h36_word144 != entry->h36_word144 ||
        receipt->lane_role != entry->lane_role ||
        receipt->parent_slot != entry->parent_slot ||
        receipt->local_cell36 != entry->local_cell36 ||
        receipt->child_side != entry->child_side ||
        receipt->depth != entry->depth ||
        receipt->frozen_parent_validated != 1U ||
        receipt->exact_replayable != 1U ||
        receipt->reversible_to_root != 1U ||
        receipt->fibonacci_identity_preserved != 1U ||
        receipt->branch_reference_only != 1U ||
        receipt->canonical_mutation_authority != 0U ||
        receipt->canonical_hash72_authority != 0U ||
        receipt->canonical_hash216_authority != 0U ||
        receipt->canonical_persistence_authority != 0U ||
        receipt->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_h36_branch_ref_reverse_to_root(
        cache,
        frozen_parent_cache,
        receipt->branch_id,
        &root_branch_id,
        &steps);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    (void)root_branch_id;
    (void)steps;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_branch_ref_cache_validate(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache
) {
    uint8_t seen[
        HHS_EXACT_PASS219_H36_BRANCH_REF_CAPACITY];
    uint32_t i;
    uint32_t tile;
    uint32_t lane;
    uint32_t total_bucket_count = 0U;
    uint32_t threshold;
    HHSExactStatus status;

    status = h36_branch_ref_header_validate(cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_h36_stack_cache_validate(
        frozen_parent_cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = h36_branch_ref_parent_header_validate(
        cache, frozen_parent_cache);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (h36_branch_ref_parent_cache_signature(
            frozen_parent_cache) !=
        cache->frozen_parent_signature64)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(seen, 0, sizeof(seen));
    threshold =
        hhs_exact_pass219_h36_branch_ref_memo_threshold(
            cache->entry_count);

    for (tile = 0U;
         tile < HHS_EXACT_PASS219_H36_BRANCH_REF_MAX_TILES;
         ++tile) {
        for (lane = 0U;
             lane < HHS_EXACT_PASS219_H36_BRANCH_REF_LANES;
             ++lane) {
            uint32_t root_id = cache->root_branch_id[tile][lane];
            if (root_id ==
                HHS_EXACT_PASS219_H36_BRANCH_REF_NONE)
                continue;
            if (root_id >= cache->entry_count ||
                cache->entries[root_id].previous_branch_id !=
                    HHS_EXACT_PASS219_H36_BRANCH_REF_NONE ||
                cache->entries[root_id].tile144 != tile ||
                cache->entries[root_id].lane_role != lane)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }

    for (i = 0U; i < cache->entry_count; ++i) {
        const HHSExactPass219H36BranchReferenceEntryV1 *entry =
            &cache->entries[i];
        const HHSExactPass219H36BranchMemoStateV1 *memo =
            &cache->memo[i];
        uint32_t target;

        status = h36_branch_ref_entry_validate_fast(
            cache, frozen_parent_cache, i);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        status = h36_branch_ref_parent_entry_validate_full(
            frozen_parent_cache,
            entry->parent_slot,
            entry->parent_entry_signature64);
        if (status != HHS_EXACT_STATUS_OK)
            return status;

        if (cache->left_child_branch_id[i] !=
            HHS_EXACT_PASS219_H36_BRANCH_REF_NONE) {
            uint32_t child = cache->left_child_branch_id[i];
            if (child >= cache->entry_count ||
                cache->entries[child].previous_branch_id != i ||
                cache->entries[child].child_side !=
                    HHS_EXACT_PASS219_H36_BRANCH_CHILD_LEFT)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        if (cache->right_child_branch_id[i] !=
            HHS_EXACT_PASS219_H36_BRANCH_REF_NONE) {
            uint32_t child = cache->right_child_branch_id[i];
            if (child >= cache->entry_count ||
                cache->entries[child].previous_branch_id != i ||
                cache->entries[child].child_side !=
                    HHS_EXACT_PASS219_H36_BRANCH_CHILD_RIGHT)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        for (target = 0U;
             target <
                 HHS_EXACT_PASS219_H36_BRANCH_REF_COMPOSITION_TARGETS;
             ++target) {
            uint8_t bit = (uint8_t)(UINT8_C(1) << target);
            uint32_t count =
                memo->composition_query_count[target];
            uint32_t used =
                memo->composition_memo_threshold_used[target];
            uint64_t memo_sig =
                memo->composition_memo_signature64[target];
            int is_memoized =
                (memo->composition_memoized_mask & bit) != 0U;

            if (count == 0U) {
                if (used != 0U || memo_sig != 0U || is_memoized)
                    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
                continue;
            }
            if (is_memoized) {
                if (used == 0U ||
                    count < used ||
                    used > UINT32_C(87572) ||
                    memo_sig !=
                        h36_branch_ref_composition_signature(
                            entry, (uint8_t)target))
                    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            } else if (used != 0U || memo_sig != 0U) {
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            } else if (count >= threshold) {
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            }
        }
    }

    for (i = 0U;
         i < HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_BUCKETS;
         ++i) {
        uint32_t branch_id = cache->fib_bucket_head[i];
        uint32_t count = 0U;
        while (branch_id !=
               HHS_EXACT_PASS219_H36_BRANCH_REF_NONE) {
            const HHSExactPass219H36BranchReferenceEntryV1 *entry;
            if (branch_id >= cache->entry_count ||
                count >= cache->entry_count ||
                seen[branch_id] != 0U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            entry = &cache->entries[branch_id];
            if (entry->fib_index != i)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            seen[branch_id] = 1U;
            count += UINT32_C(1);
            branch_id = entry->previous_fib_member_branch_id;
        }
        if (count != cache->fib_bucket_count[i])
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        total_bucket_count += count;
    }

    if (total_bucket_count != cache->entry_count)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (i = 0U; i < cache->entry_count; ++i) {
        if (seen[i] != 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}
