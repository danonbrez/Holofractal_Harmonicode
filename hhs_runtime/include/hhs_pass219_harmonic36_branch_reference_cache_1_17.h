#ifndef HHS_PASS219_HARMONIC36_BRANCH_REFERENCE_CACHE_1_17_H
#define HHS_PASS219_HARMONIC36_BRANCH_REFERENCE_CACHE_1_17_H

#include "hhs_pass219_harmonic36_stack_selection_cache_1_11.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_BRANCH_REF_VERSION UINT32_C(0x00010011)
#define HHS_EXACT_PASS219_H36_BRANCH_REF_CAPACITY UINT32_C(5184)
#define HHS_EXACT_PASS219_H36_BRANCH_REF_LANES UINT32_C(4)
#define HHS_EXACT_PASS219_H36_BRANCH_REF_CELLS_PER_LANE UINT32_C(36)
#define HHS_EXACT_PASS219_H36_BRANCH_REF_TILE_CELLS UINT32_C(144)
#define HHS_EXACT_PASS219_H36_BRANCH_REF_MAX_TILES UINT32_C(36)
#define HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_BUCKETS UINT32_C(13)
#define HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_ROOT_INDEX UINT16_C(12)
#define HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_ROOT_VALUE UINT16_C(144)
#define HHS_EXACT_PASS219_H36_BRANCH_REF_COMPOSITION_TARGETS UINT32_C(4)
#define HHS_EXACT_PASS219_H36_BRANCH_REF_NONE UINT32_MAX

typedef enum HHSExactPass219H36BranchChildSideV1 {
    HHS_EXACT_PASS219_H36_BRANCH_CHILD_ROOT = 0,
    HHS_EXACT_PASS219_H36_BRANCH_CHILD_LEFT = 1,
    HHS_EXACT_PASS219_H36_BRANCH_CHILD_RIGHT = 2
} HHSExactPass219H36BranchChildSideV1;

typedef struct HHSExactPass219H36BranchReferenceEntryV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t branch_id;
    uint32_t previous_branch_id;
    uint32_t previous_fib_member_branch_id;
    uint64_t sequence;
    uint64_t parent_entry_signature64;
    uint64_t prior_receipt_signature64;
    uint64_t entry_signature64;
    uint64_t receipt_signature64;
    uint16_t tile144;
    uint16_t fib_index;
    uint16_t fib_value;
    uint16_t h36_word144;
    uint8_t lane_role;
    uint8_t parent_slot;
    uint8_t local_cell36;
    uint8_t child_side;
    uint8_t depth;
    uint8_t occupied;
    uint8_t branch_reference_only;
    uint8_t exact_replayable;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36BranchReferenceEntryV1;

typedef struct HHSExactPass219H36BranchMemoStateV1 {
    uint32_t composition_query_count[
        HHS_EXACT_PASS219_H36_BRANCH_REF_COMPOSITION_TARGETS];
    uint32_t composition_memo_threshold_used[
        HHS_EXACT_PASS219_H36_BRANCH_REF_COMPOSITION_TARGETS];
    uint64_t composition_memo_signature64[
        HHS_EXACT_PASS219_H36_BRANCH_REF_COMPOSITION_TARGETS];
    uint8_t composition_memoized_mask;
} HHSExactPass219H36BranchMemoStateV1;

typedef struct HHSExactPass219H36BranchReferenceCacheV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t capacity;
    uint32_t entry_count;
    uint64_t next_sequence;
    uint64_t frozen_parent_signature64;
    uint32_t frozen_parent_entry_count;
    uint64_t frozen_parent_next_sequence;
    uint8_t branch_reference_only;
    uint8_t append_only_branch_forking;
    uint8_t fibonacci_equivalence_indexed;
    uint8_t adaptive_composition_memoization;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint32_t root_branch_id[
        HHS_EXACT_PASS219_H36_BRANCH_REF_MAX_TILES]
        [HHS_EXACT_PASS219_H36_BRANCH_REF_LANES];
    uint32_t left_child_branch_id[
        HHS_EXACT_PASS219_H36_BRANCH_REF_CAPACITY];
    uint32_t right_child_branch_id[
        HHS_EXACT_PASS219_H36_BRANCH_REF_CAPACITY];
    uint32_t fib_bucket_head[
        HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_BUCKETS];
    uint32_t fib_bucket_count[
        HHS_EXACT_PASS219_H36_BRANCH_REF_FIB_BUCKETS];
    HHSExactPass219H36BranchReferenceEntryV1
        entries[HHS_EXACT_PASS219_H36_BRANCH_REF_CAPACITY];
    HHSExactPass219H36BranchMemoStateV1
        memo[HHS_EXACT_PASS219_H36_BRANCH_REF_CAPACITY];
} HHSExactPass219H36BranchReferenceCacheV1;

typedef struct HHSExactPass219H36BranchReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t branch_id;
    uint32_t previous_branch_id;
    uint64_t sequence;
    uint64_t parent_entry_signature64;
    uint64_t prior_receipt_signature64;
    uint64_t entry_signature64;
    uint64_t receipt_signature64;
    uint16_t tile144;
    uint16_t fib_index;
    uint16_t fib_value;
    uint16_t h36_word144;
    uint8_t lane_role;
    uint8_t parent_slot;
    uint8_t local_cell36;
    uint8_t child_side;
    uint8_t depth;
    uint8_t frozen_parent_validated;
    uint8_t exact_replayable;
    uint8_t reversible_to_root;
    uint8_t fibonacci_identity_preserved;
    uint8_t branch_reference_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36BranchReceiptV1;

typedef struct HHSExactPass219H36CompositionReceiptMemoV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t branch_id;
    uint32_t query_count;
    uint32_t memoization_threshold;
    uint64_t branch_receipt_signature64;
    uint64_t composition_receipt_signature64;
    uint8_t source_lane_role;
    uint8_t target_lane_role;
    uint8_t memoized;
    uint8_t exact_replayable;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36CompositionReceiptMemoV1;

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_branch_ref_cache_init(
    HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_branch_ref_root(
    HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t parent_slot,
    uint8_t lane_role,
    uint16_t tile144,
    uint32_t *out_branch_id,
    HHSExactPass219H36BranchReceiptV1 *out_receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_branch_ref_fork(
    HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t previous_branch_id,
    uint8_t child_side,
    uint32_t *out_branch_id,
    HHSExactPass219H36BranchReceiptV1 *out_receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_branch_ref_resolve(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t branch_id,
    const HHSExactPass219H36StackSelectionV1 **out_parent_selection,
    HHSExactPass219H36BranchReceiptV1 *out_receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_branch_ref_equivalent(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    uint16_t fib_index,
    uint32_t *out_branch_ids,
    size_t out_capacity,
    size_t *out_count);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_branch_ref_reverse_to_root(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t branch_id,
    uint32_t *out_root_branch_id,
    uint32_t *out_steps);

HHS_EXACT_API uint32_t
hhs_exact_pass219_h36_branch_ref_memo_threshold(
    uint32_t active_branch_count);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_branch_ref_composition_receipt(
    HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    uint32_t branch_id,
    uint8_t target_lane_role,
    HHSExactPass219H36CompositionReceiptMemoV1 *out_receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_branch_ref_composition_receipt_validate(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    const HHSExactPass219H36CompositionReceiptMemoV1 *receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_branch_ref_receipt_validate(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache,
    const HHSExactPass219H36BranchReceiptV1 *receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_branch_ref_cache_validate(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *frozen_parent_cache);

#ifdef __cplusplus
}
#endif
#endif
