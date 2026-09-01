#include "hhs_runtime_exact_abi.h"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_cache_benchmark_sink = 0U;

constexpr int kSamples = 11;
constexpr std::uint32_t kRoundsPerSample = 4096U;
constexpr std::uint64_t kWorkloadSignature36 = UINT64_C(3734727431);
constexpr std::uint64_t kSemanticResultSignature64 =
    UINT64_C(4176962402124975431);

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

void prepare_candidates(
    HHSExactPass219H36StackCandidateEvidenceV1 &h36,
    HHSExactPass219H36StackCandidateEvidenceV1 &linux
) {
    if (hhs_exact_pass219_h36_stack_candidate_prepare(
            1U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
            kWorkloadSignature36,
            kSemanticResultSignature64,
            UINT64_C(96531),
            9U,
            32U,
            5120U,
            14U,
            1U,
            &h36) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_candidate_prepare(
            2U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
            kWorkloadSignature36,
            kSemanticResultSignature64,
            UINT64_C(873043),
            9U,
            32U,
            100U,
            20U,
            1U,
            &linux) != HHS_EXACT_STATUS_OK)
        std::abort();
}

}  // namespace

int main(int argc, char **argv) {
#if !defined(__linux__) || !defined(__x86_64__)
    std::cerr << "cache benchmark requires Linux x86_64\n";
    return 2;
#else
    HHSExactPass219H36StackCandidateEvidenceV1 h36{};
    HHSExactPass219H36StackCandidateEvidenceV1 linux{};
    HHSExactPass219H36StackSelectionV1 fresh_probe{};
    HHSExactPass219H36StackSelectionV1 cached_probe{};
    HHSExactPass219H36StackCacheV1 cache{};
    HHSExactPass219H36StackCacheReceiptV1 receipt_probe{};

    prepare_candidates(h36, linux);
    if (hhs_exact_pass219_h36_stack_select(
            &h36, &linux, &fresh_probe) != HHS_EXACT_STATUS_OK ||
        fresh_probe.workload_signature36 != kWorkloadSignature36 ||
        fresh_probe.semantic_result_signature64 !=
            kSemanticResultSignature64 ||
        fresh_probe.selected_candidate_id != 1U ||
        hhs_exact_pass219_h36_stack_cache_init(&cache) !=
            HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_cache_store(
            &cache, &fresh_probe) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_cache_lookup(
            &cache,
            kWorkloadSignature36,
            kSemanticResultSignature64,
            fresh_probe.selected_vector_key216,
            &cached_probe,
            &receipt_probe) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
            &cached_probe, &fresh_probe) != HHS_EXACT_STATUS_OK) {
        std::cerr << "exact cache/fresh precondition failed before timing\n";
        return 3;
    }

    HHSExactPass219H36StackSelectionV1 stale_probe = fresh_probe;
    stale_probe.semantic_result_signature64 ^= UINT64_C(1);
    if (hhs_exact_pass219_h36_stack_cache_store(
            &cache, &stale_probe) != HHS_EXACT_STATUS_INVARIANT_FAILURE) {
        std::cerr << "stale-signature negative gate failed\n";
        return 4;
    }

    const auto fresh_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kRoundsPerSample; ++i) {
            HHSExactPass219H36StackSelectionV1 selection{};
            if (hhs_exact_pass219_h36_stack_select(
                    &h36, &linux, &selection) != HHS_EXACT_STATUS_OK ||
                hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
                    &selection, &fresh_probe) != HHS_EXACT_STATUS_OK)
                std::abort();
            checksum ^= selection.selected_candidate_id;
            checksum ^= selection.speedup_x1000;
            checksum ^= static_cast<std::uint8_t>(
                selection.selected_vector_key216[i % 216U]);
        }
        g_cache_benchmark_sink ^= checksum;
    };

    const auto cache_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kRoundsPerSample; ++i) {
            HHSExactPass219H36StackSelectionV1 selection{};
            HHSExactPass219H36StackCacheReceiptV1 receipt{};
            if (hhs_exact_pass219_h36_stack_cache_lookup(
                    &cache,
                    kWorkloadSignature36,
                    kSemanticResultSignature64,
                    fresh_probe.selected_vector_key216,
                    &selection,
                    &receipt) != HHS_EXACT_STATUS_OK ||
                hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
                    &selection, &fresh_probe) != HHS_EXACT_STATUS_OK ||
                receipt.cache_hit != 1U ||
                receipt.exact_replayable != 1U ||
                receipt.stale_signature_rejected != 1U)
                std::abort();
            checksum ^= receipt.entry_signature64;
            checksum ^= receipt.replay_signature64;
            checksum ^= static_cast<std::uint8_t>(
                receipt.vector_key216[i % 216U]);
        }
        g_cache_benchmark_sink ^= checksum;
    };

    const std::uint64_t fresh_median_ns = median_ns(fresh_sample);
    const std::uint64_t cache_median_ns = median_ns(cache_sample);
    if (fresh_median_ns == 0U || cache_median_ns == 0U) {
        std::cerr << "zero timing sample\n";
        return 5;
    }

    const bool cache_faster = cache_median_ns < fresh_median_ns;
    const std::uint64_t winner_ratio_x1000 =
        cache_faster
            ? ratio_x1000(fresh_median_ns, cache_median_ns)
            : ratio_x1000(cache_median_ns, fresh_median_ns);

    std::ostream *out = &std::cout;
    std::ofstream file;
    if (argc > 1) {
        file.open(argv[1], std::ios::out | std::ios::trunc);
        if (!file) {
            std::cerr << "unable to open output file\n";
            return 6;
        }
        out = &file;
    }

    *out
        << "{\n"
        << "  \"schema\": \"HHS_PASS219_H36_STACK_SELECTION_CACHE_BENCHMARK_V1\",\n"
        << "  \"platform\": {\"linux\": true, \"x86_64\": true, "
        << "\"samples\": " << kSamples << ", "
        << "\"rounds_per_sample\": " << kRoundsPerSample << "},\n"
        << "  \"identity\": {\n"
        << "    \"workload_signature36\": " << kWorkloadSignature36 << ",\n"
        << "    \"semantic_result_signature64\": "
        << kSemanticResultSignature64 << ",\n"
        << "    \"selected_candidate_id\": "
        << fresh_probe.selected_candidate_id << ",\n"
        << "    \"vector_key216\": \""
        << fresh_probe.selected_vector_key216 << "\",\n"
        << "    \"vector_key216_length\": "
        << std::strlen(fresh_probe.selected_vector_key216) << "\n"
        << "  },\n"
        << "  \"correctness\": {\n"
        << "    \"cache_hit_equals_fresh_before_timing\": true,\n"
        << "    \"stale_signature_rejected_before_timing\": true,\n"
        << "    \"deterministic_replay_receipt\": true,\n"
        << "    \"entry_signature64\": "
        << receipt_probe.entry_signature64 << ",\n"
        << "    \"replay_signature64\": "
        << receipt_probe.replay_signature64 << "\n"
        << "  },\n"
        << "  \"fresh_selection\": {\n"
        << "    \"median_ns\": " << fresh_median_ns << ",\n"
        << "    \"per_operation_median_ns\": "
        << (fresh_median_ns / kRoundsPerSample) << "\n"
        << "  },\n"
        << "  \"cache_hit\": {\n"
        << "    \"median_ns\": " << cache_median_ns << ",\n"
        << "    \"per_operation_median_ns\": "
        << (cache_median_ns / kRoundsPerSample) << "\n"
        << "  },\n"
        << "  \"measurement\": {\n"
        << "    \"cache_faster\": "
        << (cache_faster ? "true" : "false") << ",\n"
        << "    \"winner\": \""
        << (cache_faster ? "CACHE_HIT" : "FRESH_SELECTION") << "\",\n"
        << "    \"winner_ratio_x1000\": " << winner_ratio_x1000 << ",\n"
        << "    \"benefit_verified\": "
        << (cache_faster ? "true" : "false") << "\n"
        << "  },\n"
        << "  \"authority\": {\n"
        << "    \"vm81_mutation\": false,\n"
        << "    \"vm81_admission_bypass\": false,\n"
        << "    \"hash72\": false,\n"
        << "    \"hash216\": false,\n"
        << "    \"persistence\": false,\n"
        << "    \"floating_point\": false\n"
        << "  },\n"
        << "  \"authoritative_state_changed\": false\n"
        << "}\n";

    return 0;
#endif
}
