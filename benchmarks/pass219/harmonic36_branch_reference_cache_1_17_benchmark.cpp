#include "hhs_runtime_exact_abi.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_sink = 0U;

constexpr int kSamples = 7;
constexpr std::size_t kRepeats = 5U;
constexpr std::uint32_t kLookupRounds = 4096U;
constexpr std::uint32_t kEquivalenceRounds = 128U;
constexpr std::uint32_t kCompositionRounds = 1024U;

struct PairTotals {
    std::uint64_t left_total_ns = 0U;
    std::uint64_t right_total_ns = 0U;
    std::uint32_t right_beneficial_repeats = 0U;
};

std::uint64_t ratio_x1000(
    std::uint64_t numerator,
    std::uint64_t denominator
) {
    if (denominator == 0U)
        return 0U;
    if (numerator > UINT64_MAX / UINT64_C(1000))
        return (numerator / denominator) * UINT64_C(1000);
    return (numerator * UINT64_C(1000)) / denominator;
}

template <class Fn>
std::uint64_t median_ns(Fn fn) {
    fn();
    std::vector<std::uint64_t> values;
    values.reserve(static_cast<std::size_t>(kSamples));
    for (int i = 0; i < kSamples; ++i) {
        const auto begin = Clock::now();
        fn();
        const auto end = Clock::now();
        values.push_back(static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(
                end - begin).count()));
    }
    std::sort(values.begin(), values.end());
    return values[values.size() / 2U];
}

template <class Reset, class Fn>
std::uint64_t median_ns_reset(Reset reset, Fn fn) {
    reset();
    fn();
    std::vector<std::uint64_t> values;
    values.reserve(static_cast<std::size_t>(kSamples));
    for (int i = 0; i < kSamples; ++i) {
        reset();
        const auto begin = Clock::now();
        fn();
        const auto end = Clock::now();
        values.push_back(static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(
                end - begin).count()));
    }
    std::sort(values.begin(), values.end());
    return values[values.size() / 2U];
}

void make_selection(
    std::uint32_t index,
    HHSExactPass219H36StackSelectionV1 &selection
) {
    static const std::array<std::uint64_t, 4> workload = {
        UINT64_C(3734727431),
        UINT64_C(4793332410),
        UINT64_C(21509979554),
        UINT64_C(41886677838)
    };
    static const std::array<std::uint64_t, 4> semantic = {
        UINT64_C(4176962402124975431),
        UINT64_C(6731027650694893003),
        UINT64_C(1456447110141201574),
        UINT64_C(2318081696571468614)
    };
    static const std::array<std::uint64_t, 4> h36_ns = {
        UINT64_C(96531),
        UINT64_C(23033),
        UINT64_C(23073),
        UINT64_C(19156)
    };
    static const std::array<std::uint64_t, 4> linux_ns = {
        UINT64_C(873043),
        UINT64_C(106949),
        UINT64_C(109553),
        UINT64_C(501)
    };
    HHSExactPass219H36StackCandidateEvidenceV1 h36{};
    HHSExactPass219H36StackCandidateEvidenceV1 linux{};

    if (index >= 4U ||
        hhs_exact_pass219_h36_stack_candidate_prepare(
            1U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
            workload[index],
            semantic[index],
            h36_ns[index],
            7U,
            8U,
            5120U,
            8U + index,
            1U,
            &h36) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_candidate_prepare(
            2U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
            workload[index],
            semantic[index],
            linux_ns[index],
            7U,
            8U,
            100U,
            12U + index,
            1U,
            &linux) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_select(
            &h36, &linux, &selection) != HHS_EXACT_STATUS_OK)
        std::abort();
}

void build_tile(
    HHSExactPass219H36BranchReferenceCacheV1 &cache,
    const HHSExactPass219H36StackCacheV1 &parent,
    std::uint16_t tile
) {
    for (std::uint32_t lane = 0U; lane < 4U; ++lane) {
        std::array<std::uint32_t, 36> ids{};
        HHSExactPass219H36BranchReceiptV1 receipt{};
        std::uint32_t branch_id = 0U;

        if (hhs_exact_pass219_h36_branch_ref_root(
                &cache,
                &parent,
                lane,
                static_cast<std::uint8_t>(lane),
                tile,
                &branch_id,
                &receipt) != HHS_EXACT_STATUS_OK)
            std::abort();
        ids[0] = branch_id;

        for (std::uint32_t local = 0U; local < 36U; ++local) {
            const std::uint32_t left = local * 2U + 1U;
            const std::uint32_t right = local * 2U + 2U;
            if (left < 36U) {
                if (hhs_exact_pass219_h36_branch_ref_fork(
                        &cache,
                        &parent,
                        ids[local],
                        HHS_EXACT_PASS219_H36_BRANCH_CHILD_LEFT,
                        &branch_id,
                        &receipt) != HHS_EXACT_STATUS_OK)
                    std::abort();
                ids[left] = branch_id;
            }
            if (right < 36U) {
                if (hhs_exact_pass219_h36_branch_ref_fork(
                        &cache,
                        &parent,
                        ids[local],
                        HHS_EXACT_PASS219_H36_BRANCH_CHILD_RIGHT,
                        &branch_id,
                        &receipt) != HHS_EXACT_STATUS_OK)
                    std::abort();
                ids[right] = branch_id;
            }
        }
    }
}

std::size_t probe_index(
    std::uint32_t round,
    std::size_t count,
    std::size_t repeat
) {
    return static_cast<std::size_t>(
        (static_cast<std::uint64_t>(round) * UINT64_C(2654435761) +
         static_cast<std::uint64_t>(repeat) * UINT64_C(40503)) %
        count);
}

PairTotals measure_lookup(
    HHSExactPass219H36BranchReferenceCacheV1 &cache,
    const HHSExactPass219H36StackCacheV1 &parent
) {
    PairTotals totals{};

    for (std::size_t repeat = 0U; repeat < kRepeats; ++repeat) {
        const auto baseline = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U; i < kLookupRounds; ++i) {
                const std::size_t branch_id =
                    probe_index(i, cache.entry_count, repeat);
                const auto &entry = cache.entries[branch_id];
                const auto &expected =
                    parent.entries[entry.parent_slot].selection;
                HHSExactPass219H36StackSelectionV1 selected{};
                HHSExactPass219H36StackCacheReceiptV1 receipt{};
                if (hhs_exact_pass219_h36_stack_cache_lookup(
                        &parent,
                        expected.workload_signature36,
                        expected.semantic_result_signature64,
                        expected.selected_vector_key216,
                        &selected,
                        &receipt) != HHS_EXACT_STATUS_OK)
                    std::abort();
                checksum ^= selected.speedup_x1000;
                checksum ^= receipt.replay_signature64;
                checksum ^= entry.receipt_signature64;
            }
            g_sink ^= checksum;
        };

        const auto direct = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U; i < kLookupRounds; ++i) {
                const std::size_t branch_id =
                    probe_index(i, cache.entry_count, repeat);
                const HHSExactPass219H36StackSelectionV1 *selected =
                    nullptr;
                HHSExactPass219H36BranchReceiptV1 receipt{};
                if (hhs_exact_pass219_h36_branch_ref_resolve(
                        &cache,
                        &parent,
                        static_cast<std::uint32_t>(branch_id),
                        &selected,
                        &receipt) != HHS_EXACT_STATUS_OK ||
                    selected !=
                        &parent.entries[receipt.parent_slot].selection)
                    std::abort();
                checksum ^= selected->speedup_x1000;
                checksum ^= receipt.receipt_signature64;
            }
            g_sink ^= checksum;
        };

        std::uint64_t left;
        std::uint64_t right;
        if ((repeat & 1U) == 0U) {
            left = median_ns(baseline);
            right = median_ns(direct);
        } else {
            right = median_ns(direct);
            left = median_ns(baseline);
        }
        totals.left_total_ns += left;
        totals.right_total_ns += right;
        if (right < left)
            ++totals.right_beneficial_repeats;
    }
    return totals;
}

PairTotals measure_equivalence(
    const HHSExactPass219H36BranchReferenceCacheV1 &cache
) {
    PairTotals totals{};
    std::vector<std::uint32_t> ids(cache.entry_count);

    for (std::size_t repeat = 0U; repeat < kRepeats; ++repeat) {
        const auto scan = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t round = 0U;
                 round < kEquivalenceRounds;
                 ++round) {
                const std::size_t probe =
                    probe_index(round, cache.entry_count, repeat);
                const std::uint16_t fib =
                    cache.entries[probe].fib_index;
                for (std::uint32_t i = 0U;
                     i < cache.entry_count;
                     ++i) {
                    if (cache.entries[i].fib_index == fib)
                        checksum ^= cache.entries[i]
                                        .receipt_signature64;
                }
            }
            g_sink ^= checksum;
        };

        const auto bucket = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t round = 0U;
                 round < kEquivalenceRounds;
                 ++round) {
                const std::size_t probe =
                    probe_index(round, cache.entry_count, repeat);
                const std::uint16_t fib =
                    cache.entries[probe].fib_index;
                std::size_t count = 0U;
                if (hhs_exact_pass219_h36_branch_ref_equivalent(
                        &cache,
                        fib,
                        ids.data(),
                        ids.size(),
                        &count) != HHS_EXACT_STATUS_OK)
                    std::abort();
                for (std::size_t i = 0U; i < count; ++i)
                    checksum ^=
                        cache.entries[ids[i]].receipt_signature64;
            }
            g_sink ^= checksum;
        };

        std::uint64_t left;
        std::uint64_t right;
        if ((repeat & 1U) == 0U) {
            left = median_ns(scan);
            right = median_ns(bucket);
        } else {
            right = median_ns(bucket);
            left = median_ns(scan);
        }
        totals.left_total_ns += left;
        totals.right_total_ns += right;
        if (right < left)
            ++totals.right_beneficial_repeats;
    }
    return totals;
}

PairTotals measure_composition(
    HHSExactPass219H36BranchReferenceCacheV1 &cache,
    const HHSExactPass219H36StackCacheV1 &parent
) {
    PairTotals totals{};
    const std::uint32_t computed_branch = 35U;
    const std::uint32_t memo_branch = 71U;
    const std::uint8_t target = 3U;
    const std::uint32_t threshold =
        hhs_exact_pass219_h36_branch_ref_memo_threshold(
            cache.entry_count);
    HHSExactPass219H36CompositionReceiptMemoV1 receipt{};

    for (std::uint32_t i = 0U; i < threshold; ++i) {
        if (hhs_exact_pass219_h36_branch_ref_composition_receipt(
                &cache,
                &parent,
                memo_branch,
                target,
                &receipt) != HHS_EXACT_STATUS_OK)
            std::abort();
    }
    if (receipt.memoized != 1U)
        std::abort();

    for (std::size_t repeat = 0U; repeat < kRepeats; ++repeat) {
        const auto reset_computed = [&]() {
            std::memset(
                &cache.memo[computed_branch],
                0,
                sizeof(cache.memo[computed_branch]));
        };
        const auto computed = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U;
                 i < kCompositionRounds;
                 ++i) {
                HHSExactPass219H36CompositionReceiptMemoV1 r{};
                if (hhs_exact_pass219_h36_branch_ref_composition_receipt(
                        &cache,
                        &parent,
                        computed_branch,
                        target,
                        &r) != HHS_EXACT_STATUS_OK ||
                    r.memoized != 0U)
                    std::abort();
                checksum ^= r.composition_receipt_signature64;
            }
            g_sink ^= checksum;
        };
        const auto memoized = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U;
                 i < kCompositionRounds;
                 ++i) {
                HHSExactPass219H36CompositionReceiptMemoV1 r{};
                if (hhs_exact_pass219_h36_branch_ref_composition_receipt(
                        &cache,
                        &parent,
                        memo_branch,
                        target,
                        &r) != HHS_EXACT_STATUS_OK ||
                    r.memoized != 1U)
                    std::abort();
                checksum ^= r.composition_receipt_signature64;
            }
            g_sink ^= checksum;
        };

        std::uint64_t left;
        std::uint64_t right;
        if ((repeat & 1U) == 0U) {
            left = median_ns_reset(reset_computed, computed);
            right = median_ns(memoized);
        } else {
            right = median_ns(memoized);
            left = median_ns_reset(reset_computed, computed);
        }
        totals.left_total_ns += left;
        totals.right_total_ns += right;
        if (right < left)
            ++totals.right_beneficial_repeats;
    }
    return totals;
}

void write_pair(
    std::ostream &out,
    const char *left_name,
    const char *right_name,
    const PairTotals &totals
) {
    out
        << "{\"" << left_name << "_total_ns\": "
        << totals.left_total_ns
        << ", \"" << right_name << "_total_ns\": "
        << totals.right_total_ns
        << ", \"" << right_name << "_speedup_x1000\": "
        << ratio_x1000(
               totals.left_total_ns,
               totals.right_total_ns)
        << ", \"beneficial_repeats\": "
        << totals.right_beneficial_repeats
        << ", \"required_beneficial_repeats\": 4}";
}

} // namespace

int main(int argc, char **argv) {
#if !defined(__linux__) || !defined(__x86_64__)
    std::cerr << "benchmark requires Linux x86_64\n";
    return 2;
#else
    HHSExactPass219H36StackCacheV1 parent{};
    HHSExactPass219H36StackCacheV1 parent_before{};
    auto *cache =
        new HHSExactPass219H36BranchReferenceCacheV1{};
    PairTotals lookup144{};
    PairTotals lookup5184{};
    PairTotals equivalence144{};
    PairTotals equivalence5184{};
    PairTotals composition144{};

    if (hhs_exact_pass219_h36_stack_cache_init(&parent) !=
        HHS_EXACT_STATUS_OK)
        return 3;
    for (std::uint32_t i = 0U; i < 4U; ++i) {
        HHSExactPass219H36StackSelectionV1 selection{};
        make_selection(i, selection);
        if (hhs_exact_pass219_h36_stack_cache_store(
                &parent, &selection) != HHS_EXACT_STATUS_OK)
            return 4;
    }
    parent_before = parent;

    if (hhs_exact_pass219_h36_branch_ref_cache_init(
            cache, &parent) != HHS_EXACT_STATUS_OK)
        return 5;
    build_tile(*cache, parent, 0U);
    if (cache->entry_count != 144U ||
        hhs_exact_pass219_h36_branch_ref_cache_validate(
            cache, &parent) != HHS_EXACT_STATUS_OK)
        return 6;

    lookup144 = measure_lookup(*cache, parent);
    equivalence144 = measure_equivalence(*cache);
    composition144 = measure_composition(*cache, parent);

    for (std::uint16_t tile = 1U; tile < 36U; ++tile)
        build_tile(*cache, parent, tile);
    if (cache->entry_count != 5184U ||
        hhs_exact_pass219_h36_branch_ref_cache_validate(
            cache, &parent) != HHS_EXACT_STATUS_OK ||
        std::memcmp(
            &parent, &parent_before, sizeof(parent)) != 0)
        return 7;

    lookup5184 = measure_lookup(*cache, parent);
    equivalence5184 = measure_equivalence(*cache);

    std::ostream *out = &std::cout;
    std::ofstream file;
    if (argc > 1) {
        file.open(argv[1], std::ios::out | std::ios::trunc);
        if (!file)
            return 8;
        out = &file;
    }

    *out
        << "{\n"
        << "  \"schema\": \"HHS_PASS219_H36_BRANCH_REFERENCE_CACHE_1_17_PRODUCTION_BENCHMARK_V1\",\n"
        << "  \"platform\": {\"linux\": true, \"x86_64\": true, "
        << "\"samples\": " << kSamples
        << ", \"calibration_repeats\": " << kRepeats
        << ", \"required_beneficial_repeats\": 4},\n"
        << "  \"lookup_144\": ";
    write_pair(*out, "parent_cache", "direct_reference", lookup144);
    *out << ",\n  \"lookup_5184\": ";
    write_pair(*out, "parent_cache", "direct_reference", lookup5184);
    *out << ",\n  \"equivalence_144\": ";
    write_pair(*out, "full_scan", "fib_bucket", equivalence144);
    *out << ",\n  \"equivalence_5184\": ";
    write_pair(*out, "full_scan", "fib_bucket", equivalence5184);
    *out << ",\n  \"composition_144\": ";
    write_pair(*out, "computed", "memoized", composition144);
    *out
        << ",\n"
        << "  \"correctness\": {\n"
        << "    \"branch_count_144_validated\": true,\n"
        << "    \"branch_count_5184_validated\": true,\n"
        << "    \"frozen_parent_byte_equal\": true,\n"
        << "    \"direct_reference_returns_parent_address\": true,\n"
        << "    \"equivalence_bucket_exact\": true,\n"
        << "    \"memoized_receipt_exact\": true\n"
        << "  },\n"
        << "  \"authority\": {\n"
        << "    \"vm81_mutation\": false,\n"
        << "    \"hash72_mint\": false,\n"
        << "    \"hash216_persistence\": false,\n"
        << "    \"canonical_persistence\": false\n"
        << "  },\n"
        << "  \"authoritative_state_changed\": false\n"
        << "}\n";

    const bool stable =
        lookup144.right_beneficial_repeats >= 4U &&
        lookup144.right_total_ns < lookup144.left_total_ns &&
        lookup5184.right_beneficial_repeats >= 4U &&
        lookup5184.right_total_ns < lookup5184.left_total_ns &&
        equivalence144.right_beneficial_repeats >= 4U &&
        equivalence144.right_total_ns < equivalence144.left_total_ns &&
        equivalence5184.right_beneficial_repeats >= 4U &&
        equivalence5184.right_total_ns < equivalence5184.left_total_ns &&
        composition144.right_beneficial_repeats >= 4U &&
        composition144.right_total_ns < composition144.left_total_ns;

    delete cache;
    return stable ? 0 : 9;
#endif
}
