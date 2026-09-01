#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void make_selection(
    HHSExactPass219H36StackSelectionV1 *selection
) {
    HHSExactPass219H36StackCandidateEvidenceV1 h36;
    HHSExactPass219H36StackCandidateEvidenceV1 linux;

    assert(hhs_exact_pass219_h36_stack_candidate_prepare(
        1U,
        HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
        UINT64_C(3734727431),
        UINT64_C(4176962402124975431),
        UINT64_C(96531),
        9U,
        32U,
        5120U,
        14U,
        1U,
        &h36
    ) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_stack_candidate_prepare(
        2U,
        HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
        UINT64_C(3734727431),
        UINT64_C(4176962402124975431),
        UINT64_C(873043),
        9U,
        32U,
        100U,
        20U,
        1U,
        &linux
    ) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_stack_select(
        &h36, &linux, selection) == HHS_EXACT_STATUS_OK);
    assert(selection->selected_candidate_id == 1U);
}

int main(void) {
    HHSExactPass219H36StackCacheV1 cache;
    HHSExactPass219H36StackSelectionV1 fresh;
    HHSExactPass219H36StackSelectionV1 cached;
    HHSExactPass219H36StackSelectionV1 replay_cached;
    HHSExactPass219H36StackSelectionV1 stale;
    HHSExactPass219H36StackCacheReceiptV1 receipt;
    HHSExactPass219H36StackCacheReceiptV1 replay_receipt;
    HHSExactPass219H36StackCacheReceiptV1 bad_receipt;
    char wrong_key[HHS_EXACT_UQCEL_HASH216_STRLEN];

    make_selection(&fresh);
    assert(hhs_exact_pass219_h36_stack_cache_init(&cache) ==
           HHS_EXACT_STATUS_OK);
    assert(cache.entry_count == 0U);
    assert(cache.candidate_only == 1U);
    assert(cache.vector_store_metadata_only == 1U);
    assert(cache.hash216_lineage_claim == 0U);

    assert(hhs_exact_pass219_h36_stack_cache_store(
        &cache, &fresh) == HHS_EXACT_STATUS_OK);
    assert(cache.entry_count == 1U);
    assert(cache.next_sequence == UINT64_C(2));

    assert(hhs_exact_pass219_h36_stack_cache_lookup(
        &cache,
        fresh.workload_signature36,
        fresh.semantic_result_signature64,
        fresh.selected_vector_key216,
        &cached,
        &receipt
    ) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
        &cached, &fresh) == HHS_EXACT_STATUS_OK);
    assert(receipt.cache_hit == 1U);
    assert(receipt.selection_integrity_validated == 1U);
    assert(receipt.exact_replayable == 1U);
    assert(receipt.stale_signature_rejected == 1U);
    assert(receipt.entry_signature64 != 0U);
    assert(receipt.replay_signature64 != 0U);
    assert(receipt.candidate_only == 1U);
    assert(receipt.vector_store_metadata_only == 1U);
    assert(receipt.hash216_lineage_claim == 0U);
    assert(receipt.canonical_mutation_authority == 0U);
    assert(receipt.canonical_hash72_authority == 0U);
    assert(receipt.canonical_hash216_authority == 0U);
    assert(receipt.canonical_persistence_authority == 0U);
    assert(receipt.floating_point_authority == 0U);

    assert(hhs_exact_pass219_h36_stack_cache_lookup(
        &cache,
        fresh.workload_signature36,
        fresh.semantic_result_signature64,
        fresh.selected_vector_key216,
        &replay_cached,
        &replay_receipt
    ) == HHS_EXACT_STATUS_OK);
    assert(memcmp(&cached, &replay_cached, sizeof(cached)) == 0);
    assert(memcmp(&receipt, &replay_receipt, sizeof(receipt)) == 0);
    assert(hhs_exact_pass219_h36_stack_cache_receipt_validate(
        &cache, &replay_receipt) == HHS_EXACT_STATUS_OK);

    assert(hhs_exact_pass219_h36_stack_cache_store(
        &cache, &fresh) == HHS_EXACT_STATUS_OK);
    assert(cache.entry_count == 1U);
    assert(cache.next_sequence == UINT64_C(2));

    assert(hhs_exact_pass219_h36_stack_cache_lookup(
        &cache,
        fresh.workload_signature36,
        fresh.semantic_result_signature64 ^ UINT64_C(1),
        fresh.selected_vector_key216,
        &cached,
        &receipt
    ) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    memcpy(
        wrong_key,
        fresh.selected_vector_key216,
        sizeof(wrong_key));
    wrong_key[0] =
        wrong_key[0] == HHS_EXACT_HASH72_ALPHABET[0]
            ? HHS_EXACT_HASH72_ALPHABET[1]
            : HHS_EXACT_HASH72_ALPHABET[0];
    assert(hhs_exact_pass219_h36_stack_cache_lookup(
        &cache,
        fresh.workload_signature36,
        fresh.semantic_result_signature64,
        wrong_key,
        &cached,
        &receipt
    ) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(hhs_exact_pass219_h36_stack_cache_lookup(
        &cache,
        UINT64_C(012345670123),
        UINT64_C(0xA55A123456789ABC),
        wrong_key,
        &cached,
        &receipt
    ) == HHS_EXACT_STATUS_RANGE_ERROR);

    stale = fresh;
    stale.semantic_result_signature64 ^= UINT64_C(1);
    assert(hhs_exact_pass219_h36_stack_cache_store(
        &cache, &stale) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad_receipt = replay_receipt;
    bad_receipt.replay_signature64 ^= UINT64_C(1);
    assert(hhs_exact_pass219_h36_stack_cache_receipt_validate(
        &cache, &bad_receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(hhs_exact_pass219_h36_stack_cache_validate(&cache) ==
           HHS_EXACT_STATUS_OK);

    printf(
        "PASS219 H36 stack cache 1.11: sequence=%llu entry_signature64=%llu replay_signature64=%llu key216=%s authority=0 replay=1 stale_reject=1 fresh_equal=1\n",
        (unsigned long long)replay_receipt.sequence,
        (unsigned long long)replay_receipt.entry_signature64,
        (unsigned long long)replay_receipt.replay_signature64,
        replay_receipt.vector_key216
    );
    return 0;
}
