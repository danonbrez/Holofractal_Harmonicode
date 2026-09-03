#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const uint64_t k_workload[4] = {
    UINT64_C(3734727431),
    UINT64_C(4793332410),
    UINT64_C(21509979554),
    UINT64_C(41886677838)
};

static const uint64_t k_semantic[4] = {
    UINT64_C(4176962402124975431),
    UINT64_C(6731027650694893003),
    UINT64_C(1456447110141201574),
    UINT64_C(2318081696571468614)
};

static const uint64_t k_h36_ns[4] = {
    UINT64_C(96531),
    UINT64_C(23033),
    UINT64_C(23073),
    UINT64_C(19156)
};

static const uint64_t k_linux_ns[4] = {
    UINT64_C(873043),
    UINT64_C(106949),
    UINT64_C(109553),
    UINT64_C(501)
};

static void make_selection(
    uint32_t index,
    HHSExactPass219H36StackSelectionV1 *selection
) {
    HHSExactPass219H36StackCandidateEvidenceV1 h36;
    HHSExactPass219H36StackCandidateEvidenceV1 linux;

    assert(index < 4U);
    assert(hhs_exact_pass219_h36_stack_candidate_prepare(
        1U,
        HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
        k_workload[index],
        k_semantic[index],
        k_h36_ns[index],
        7U,
        8U,
        5120U,
        8U + index,
        1U,
        &h36
    ) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_stack_candidate_prepare(
        2U,
        HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
        k_workload[index],
        k_semantic[index],
        k_linux_ns[index],
        7U,
        8U,
        100U,
        12U + index,
        1U,
        &linux
    ) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_stack_select(
        &h36, &linux, selection) == HHS_EXACT_STATUS_OK);
}

static void build_tile(
    HHSExactPass219H36BranchReferenceCacheV1 *cache,
    const HHSExactPass219H36StackCacheV1 *parent,
    uint16_t tile,
    uint32_t ids[4][36]
) {
    uint32_t lane;

    for (lane = 0U; lane < 4U; ++lane) {
        HHSExactPass219H36BranchReceiptV1 receipt;
        uint32_t branch_id;
        uint32_t local;

        assert(hhs_exact_pass219_h36_branch_ref_root(
            cache,
            parent,
            lane,
            (uint8_t)lane,
            tile,
            &branch_id,
            &receipt
        ) == HHS_EXACT_STATUS_OK);
        ids[lane][0] = branch_id;
        assert(receipt.local_cell36 == 0U);
        assert(receipt.fib_index == 12U);
        assert(receipt.fib_value == 144U);
        assert(receipt.h36_word144 == lane * 36U);
        assert(receipt.previous_branch_id ==
               HHS_EXACT_PASS219_H36_BRANCH_REF_NONE);
        assert(hhs_exact_pass219_h36_branch_ref_receipt_validate(
            cache, parent, &receipt) == HHS_EXACT_STATUS_OK);

        for (local = 0U; local < 36U; ++local) {
            uint32_t left = local * 2U + 1U;
            uint32_t right = local * 2U + 2U;

            if (left < 36U) {
                assert(hhs_exact_pass219_h36_branch_ref_fork(
                    cache,
                    parent,
                    ids[lane][local],
                    HHS_EXACT_PASS219_H36_BRANCH_CHILD_LEFT,
                    &branch_id,
                    &receipt
                ) == HHS_EXACT_STATUS_OK);
                ids[lane][left] = branch_id;
                assert(receipt.local_cell36 == left);
                assert(receipt.child_side ==
                       HHS_EXACT_PASS219_H36_BRANCH_CHILD_LEFT);
                assert(receipt.previous_branch_id ==
                       ids[lane][local]);
                assert(hhs_exact_pass219_h36_branch_ref_receipt_validate(
                    cache, parent, &receipt) == HHS_EXACT_STATUS_OK);
            }

            if (right < 36U) {
                assert(hhs_exact_pass219_h36_branch_ref_fork(
                    cache,
                    parent,
                    ids[lane][local],
                    HHS_EXACT_PASS219_H36_BRANCH_CHILD_RIGHT,
                    &branch_id,
                    &receipt
                ) == HHS_EXACT_STATUS_OK);
                ids[lane][right] = branch_id;
                assert(receipt.local_cell36 == right);
                assert(receipt.child_side ==
                       HHS_EXACT_PASS219_H36_BRANCH_CHILD_RIGHT);
                assert(receipt.previous_branch_id ==
                       ids[lane][local]);
                assert(hhs_exact_pass219_h36_branch_ref_receipt_validate(
                    cache, parent, &receipt) == HHS_EXACT_STATUS_OK);
            }

            if (right < 36U) {
                const HHSExactPass219H36BranchReferenceEntryV1 *p =
                    &cache->entries[ids[lane][local]];
                const HHSExactPass219H36BranchReferenceEntryV1 *l =
                    &cache->entries[ids[lane][left]];
                const HHSExactPass219H36BranchReferenceEntryV1 *r =
                    &cache->entries[ids[lane][right]];
                assert(p->fib_value ==
                       (uint16_t)(l->fib_value + r->fib_value));
            }
        }
    }
}

static void verify_equivalence_buckets(
    const HHSExactPass219H36BranchReferenceCacheV1 *cache
) {
    uint32_t *ids;
    uint16_t fib_index;

    ids = (uint32_t *)malloc(
        sizeof(uint32_t) * cache->entry_count);
    assert(ids != NULL);

    for (fib_index = 0U; fib_index < 13U; ++fib_index) {
        size_t count = 0U;
        size_t manual = 0U;
        uint32_t i;

        assert(hhs_exact_pass219_h36_branch_ref_equivalent(
            cache,
            fib_index,
            ids,
            cache->entry_count,
            &count
        ) == HHS_EXACT_STATUS_OK);

        for (i = 0U; i < cache->entry_count; ++i) {
            if (cache->entries[i].fib_index == fib_index)
                ++manual;
        }
        assert(count == manual);
        for (i = 0U; i < count; ++i) {
            assert(ids[i] < cache->entry_count);
            assert(cache->entries[ids[i]].fib_index ==
                   fib_index);
        }
    }

    free(ids);
}

int main(void) {
    HHSExactPass219H36StackCacheV1 parent;
    HHSExactPass219H36StackCacheV1 parent_before;
    HHSExactPass219H36StackCacheV1 bad_parent;
    HHSExactPass219H36StackSelectionV1 selection;
    HHSExactPass219H36BranchReferenceCacheV1 *cache;
    HHSExactPass219H36BranchReferenceCacheV1 *tampered;
    HHSExactPass219H36BranchReferenceEntryV1 entry_before_memo;
    HHSExactPass219H36CompositionReceiptMemoV1 composition;
    HHSExactPass219H36CompositionReceiptMemoV1 bad_composition;
    HHSExactPass219H36BranchReceiptV1 receipt;
    HHSExactPass219H36BranchReceiptV1 bad_receipt;
    const HHSExactPass219H36StackSelectionV1 *resolved;
    uint32_t tile0_ids[4][36];
    uint32_t ids[4][36];
    uint32_t memo_branch;
    uint32_t root_branch;
    uint32_t steps;
    uint32_t i;
    uint32_t threshold;
    size_t required = 0U;

    assert(hhs_exact_pass219_h36_stack_cache_init(&parent) ==
           HHS_EXACT_STATUS_OK);
    for (i = 0U; i < 4U; ++i) {
        make_selection(i, &selection);
        assert(hhs_exact_pass219_h36_stack_cache_store(
            &parent, &selection) == HHS_EXACT_STATUS_OK);
    }
    assert(parent.entry_count == 4U);
    assert(parent.next_sequence == UINT64_C(5));
    assert(hhs_exact_pass219_h36_stack_cache_validate(&parent) ==
           HHS_EXACT_STATUS_OK);
    parent_before = parent;

    cache = (HHSExactPass219H36BranchReferenceCacheV1 *)
        malloc(sizeof(*cache));
    tampered = (HHSExactPass219H36BranchReferenceCacheV1 *)
        malloc(sizeof(*tampered));
    assert(cache != NULL);
    assert(tampered != NULL);

    assert(hhs_exact_pass219_h36_branch_ref_cache_init(
        cache, &parent) == HHS_EXACT_STATUS_OK);
    assert(cache->entry_count == 0U);
    assert(cache->next_sequence == UINT64_C(1));
    assert(cache->branch_reference_only == 1U);
    assert(cache->append_only_branch_forking == 1U);
    assert(cache->fibonacci_equivalence_indexed == 1U);
    assert(cache->adaptive_composition_memoization == 1U);
    assert(cache->canonical_mutation_authority == 0U);
    assert(cache->canonical_hash72_authority == 0U);
    assert(cache->canonical_hash216_authority == 0U);
    assert(cache->canonical_persistence_authority == 0U);
    assert(cache->floating_point_authority == 0U);

    build_tile(cache, &parent, 0U, tile0_ids);
    assert(cache->entry_count == 144U);
    assert(cache->next_sequence == UINT64_C(145));
    assert(hhs_exact_pass219_h36_branch_ref_cache_validate(
        cache, &parent) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&parent, &parent_before, sizeof(parent)) == 0);

    {
        uint32_t branch_id = 0U;
        assert(hhs_exact_pass219_h36_branch_ref_root(
            cache,
            &parent,
            0U,
            0U,
            0U,
            &branch_id,
            &receipt
        ) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
        assert(hhs_exact_pass219_h36_branch_ref_fork(
            cache,
            &parent,
            tile0_ids[0][0],
            HHS_EXACT_PASS219_H36_BRANCH_CHILD_LEFT,
            &branch_id,
            &receipt
        ) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
        assert(hhs_exact_pass219_h36_branch_ref_fork(
            cache,
            &parent,
            tile0_ids[0][0],
            HHS_EXACT_PASS219_H36_BRANCH_CHILD_ROOT,
            &branch_id,
            &receipt
        ) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
        assert(cache->entry_count == 144U);
    }

    memo_branch = tile0_ids[2][35];
    assert(hhs_exact_pass219_h36_branch_ref_resolve(
        cache,
        &parent,
        memo_branch,
        &resolved,
        &receipt
    ) == HHS_EXACT_STATUS_OK);
    assert(resolved ==
           &parent.entries[receipt.parent_slot].selection);
    assert(receipt.branch_id == memo_branch);
    assert(receipt.branch_reference_only == 1U);
    assert(receipt.reversible_to_root == 1U);
    assert(hhs_exact_pass219_h36_branch_ref_receipt_validate(
        cache, &parent, &receipt) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_branch_ref_reverse_to_root(
        cache,
        &parent,
        memo_branch,
        &root_branch,
        &steps
    ) == HHS_EXACT_STATUS_OK);
    assert(root_branch == tile0_ids[2][0]);
    assert(steps == receipt.depth);

    bad_receipt = receipt;
    bad_receipt.receipt_signature64 ^= UINT64_C(1);
    assert(hhs_exact_pass219_h36_branch_ref_receipt_validate(
        cache, &parent, &bad_receipt) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);

    verify_equivalence_buckets(cache);
    assert(hhs_exact_pass219_h36_branch_ref_equivalent(
        cache,
        12U,
        tile0_ids[0],
        3U,
        &required
    ) == HHS_EXACT_STATUS_BUFFER_TOO_SMALL);
    assert(required == 4U);

    threshold =
        hhs_exact_pass219_h36_branch_ref_memo_threshold(
            cache->entry_count);
    assert(threshold == 3172U);
    entry_before_memo = cache->entries[memo_branch];
    for (i = 1U; i < threshold; ++i) {
        assert(hhs_exact_pass219_h36_branch_ref_composition_receipt(
            cache,
            &parent,
            memo_branch,
            3U,
            &composition
        ) == HHS_EXACT_STATUS_OK);
        assert(composition.query_count == i);
        assert(composition.memoized == 0U);
        assert(composition.memoization_threshold == threshold);
    }
    assert(hhs_exact_pass219_h36_branch_ref_composition_receipt(
        cache,
        &parent,
        memo_branch,
        3U,
        &composition
    ) == HHS_EXACT_STATUS_OK);
    assert(composition.query_count == threshold);
    assert(composition.memoized == 1U);
    assert(composition.memoization_threshold == threshold);
    assert(hhs_exact_pass219_h36_branch_ref_composition_receipt_validate(
        cache, &parent, &composition) == HHS_EXACT_STATUS_OK);
    assert(memcmp(
        &entry_before_memo,
        &cache->entries[memo_branch],
        sizeof(entry_before_memo)) == 0);

    bad_composition = composition;
    bad_composition.composition_receipt_signature64 ^= UINT64_C(1);
    assert(hhs_exact_pass219_h36_branch_ref_composition_receipt_validate(
        cache, &parent, &bad_composition) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);

    for (i = 1U; i < 36U; ++i)
        build_tile(cache, &parent, (uint16_t)i, ids);

    assert(cache->entry_count == 5184U);
    assert(cache->next_sequence == UINT64_C(5185));
    assert(hhs_exact_pass219_h36_branch_ref_memo_threshold(
        cache->entry_count) == 87572U);
    assert(hhs_exact_pass219_h36_branch_ref_cache_validate(
        cache, &parent) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&parent, &parent_before, sizeof(parent)) == 0);

    assert(hhs_exact_pass219_h36_branch_ref_composition_receipt(
        cache,
        &parent,
        memo_branch,
        3U,
        &composition
    ) == HHS_EXACT_STATUS_OK);
    assert(composition.memoized == 1U);
    assert(composition.memoization_threshold == 3172U);
    assert(hhs_exact_pass219_h36_branch_ref_composition_receipt_validate(
        cache, &parent, &composition) == HHS_EXACT_STATUS_OK);

    verify_equivalence_buckets(cache);
    {
        uint32_t *root_ids = (uint32_t *)malloc(
            sizeof(uint32_t) * 144U);
        assert(root_ids != NULL);
        assert(hhs_exact_pass219_h36_branch_ref_equivalent(
            cache,
            12U,
            root_ids,
            143U,
            &required
        ) == HHS_EXACT_STATUS_BUFFER_TOO_SMALL);
        assert(required == 144U);
        assert(hhs_exact_pass219_h36_branch_ref_equivalent(
            cache,
            12U,
            root_ids,
            144U,
            &required
        ) == HHS_EXACT_STATUS_OK);
        assert(required == 144U);
        free(root_ids);
    }

    assert(hhs_exact_pass219_h36_branch_ref_resolve(
        cache,
        &parent,
        5183U,
        &resolved,
        &receipt
    ) == HHS_EXACT_STATUS_OK);
    assert(resolved ==
           &parent.entries[receipt.parent_slot].selection);
    assert(hhs_exact_pass219_h36_branch_ref_reverse_to_root(
        cache,
        &parent,
        5183U,
        &root_branch,
        &steps
    ) == HHS_EXACT_STATUS_OK);
    assert(cache->entries[root_branch].previous_branch_id ==
           HHS_EXACT_PASS219_H36_BRANCH_REF_NONE);
    assert(cache->entries[root_branch].tile144 ==
           cache->entries[5183U].tile144);
    assert(cache->entries[root_branch].lane_role ==
           cache->entries[5183U].lane_role);

    {
        uint32_t branch_id = 0U;
        assert(hhs_exact_pass219_h36_branch_ref_root(
            cache,
            &parent,
            0U,
            0U,
            0U,
            &branch_id,
            &receipt
        ) == HHS_EXACT_STATUS_BUFFER_TOO_SMALL);
    }

    memcpy(tampered, cache, sizeof(*cache));
    tampered->entries[100U].receipt_signature64 ^= UINT64_C(1);
    assert(hhs_exact_pass219_h36_branch_ref_cache_validate(
        tampered, &parent) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    memcpy(tampered, cache, sizeof(*cache));
    tampered->fib_bucket_head[12U] = cache->entry_count + 1U;
    assert(hhs_exact_pass219_h36_branch_ref_cache_validate(
        tampered, &parent) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    memcpy(tampered, cache, sizeof(*cache));
    tampered->memo[memo_branch]
        .composition_memo_signature64[3U] ^= UINT64_C(1);
    assert(hhs_exact_pass219_h36_branch_ref_cache_validate(
        tampered, &parent) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad_parent = parent;
    bad_parent.entries[2U].entry_signature64 ^= UINT64_C(1);
    assert(hhs_exact_pass219_h36_branch_ref_cache_validate(
        cache, &bad_parent) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(hhs_exact_pass219_h36_branch_ref_resolve(
        cache,
        &bad_parent,
        memo_branch,
        &resolved,
        &receipt
    ) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(memcmp(&parent, &parent_before, sizeof(parent)) == 0);

    printf(
        "PASS219 H36 branch-reference cache 1.17: branches=%u roots_fib144=%zu memo_threshold_144=%u memo_threshold_5184=%u frozen_parent=1 reversible=1 equivalence_index=1 adaptive_memo=1 authority=0\n",
        cache->entry_count,
        required,
        3172U,
        87572U
    );

    free(tampered);
    free(cache);
    return 0;
}
