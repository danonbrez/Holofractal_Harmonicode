#include "hhs_runtime_exact_abi.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_sink = 0U;

template <class Fn>
std::uint64_t median_ns(Fn fn, int repetitions) {
    fn();
    std::vector<std::uint64_t> samples;
    samples.reserve(static_cast<std::size_t>(repetitions));
    for (int i = 0; i < repetitions; ++i) {
        const auto begin = Clock::now();
        fn();
        const auto end = Clock::now();
        samples.push_back(static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin).count()));
    }
    std::sort(samples.begin(), samples.end());
    return samples[samples.size() / 2U];
}

HHSExactPass219LatencyRouteV1 make_route(
    std::uint32_t id,
    std::uint64_t ns,
    std::uint64_t work,
    std::uint8_t selector,
    std::uint8_t fallback
) {
    HHSExactPass219LatencyRouteV1 route{};
    route.struct_size = sizeof(route);
    route.version = hhs_exact_pass219_global_latency_policy_version();
    route.route_id = id;
    route.observed_ns = ns;
    route.work_units = work;
    route.exact_semantic_equal = 1U;
    route.exact_selector_proven = selector;
    route.complete_fallback = fallback;
    route.candidate_only = 1U;
    return route;
}

}  // namespace

int main(int argc, char **argv) {
    constexpr std::uint64_t kClassifyIterations = 500000ULL;
    constexpr std::uint64_t kRouteIterations = 100000ULL;
    constexpr std::uint64_t kWindowIterations = 50000ULL;

    if (hhs_exact_pass219_global_latency_policy_validate() != HHS_EXACT_STATUS_OK) {
        std::cerr << "latency policy validation failed\n";
        return 2;
    }

    HHSExactPass219LatencyRouteV1 routes[2] = {
        make_route(0U, 13400000ULL, 68024448ULL, 0U, 1U),
        make_route(729U, 1368750ULL, 7558272ULL, 1U, 0U),
    };

    HHSExactPass219LatencyWindowInputV1 window{};
    window.struct_size = sizeof(window);
    window.version = hhs_exact_pass219_global_latency_policy_version();
    window.sample_count = 20U;
    for (std::uint32_t i = 0U; i < 19U; ++i)
        window.samples_ns[i] = 8000000ULL + (i % 3U) * 100000ULL;
    window.samples_ns[19] = 12000000ULL;

    HHSExactPass219LatencySelectionV1 initial_selection{};
    if (hhs_exact_pass219_global_latency_select_route(
            routes,
            2U,
            HHS_EXACT_PASS219_LATENCY_TIER1_120FPS,
            &initial_selection) != HHS_EXACT_STATUS_OK ||
        initial_selection.selected_route_id != 729U ||
        initial_selection.budget_met != 1U) {
        std::cerr << "latency route fixture failed\n";
        return 3;
    }

    HHSExactPass219LatencyWindowResultV1 initial_window{};
    if (hhs_exact_pass219_global_latency_window_evaluate(&window, &initial_window) !=
            HHS_EXACT_STATUS_OK ||
        initial_window.window_policy_met != 1U) {
        std::cerr << "latency window fixture failed\n";
        return 4;
    }

    const std::uint64_t classify_batch_ns = median_ns([&]() {
        std::uint64_t checksum = 0U;
        for (std::uint64_t i = 0U; i < kClassifyIterations; ++i) {
            const std::uint64_t observed =
                1000000ULL + ((i * 2654435761ULL) % 40000000ULL);
            std::uint32_t tier = 0U;
            if (hhs_exact_pass219_global_latency_classify_ns(observed, &tier) !=
                HHS_EXACT_STATUS_OK) {
                std::abort();
            }
            checksum += tier;
        }
        g_sink ^= checksum;
    }, 7);

    const std::uint64_t route_batch_ns = median_ns([&]() {
        std::uint64_t checksum = 0U;
        for (std::uint64_t i = 0U; i < kRouteIterations; ++i) {
            HHSExactPass219LatencySelectionV1 selection{};
            if (hhs_exact_pass219_global_latency_select_route(
                    routes,
                    2U,
                    HHS_EXACT_PASS219_LATENCY_TIER1_120FPS,
                    &selection) != HHS_EXACT_STATUS_OK) {
                std::abort();
            }
            checksum += selection.selected_route_id + selection.selected_tier;
        }
        g_sink ^= checksum;
    }, 7);

    const std::uint64_t window_batch_ns = median_ns([&]() {
        std::uint64_t checksum = 0U;
        for (std::uint64_t i = 0U; i < kWindowIterations; ++i) {
            HHSExactPass219LatencyWindowResultV1 result{};
            if (hhs_exact_pass219_global_latency_window_evaluate(&window, &result) !=
                HHS_EXACT_STATUS_OK) {
                std::abort();
            }
            checksum += result.mean_tier + result.p95_tier + result.max_tier;
        }
        g_sink ^= checksum;
    }, 7);

    std::ostream *out = &std::cout;
    std::ofstream file;
    if (argc > 1) {
        file.open(argv[1], std::ios::out | std::ios::trunc);
        if (!file) {
            std::cerr << "unable to open output\n";
            return 5;
        }
        out = &file;
    }

    *out << "{\n"
         << "  \"schema\": \"HHS_PASS219_GLOBAL_LATENCY_POLICY_OVERHEAD_BENCHMARK_V1\",\n"
         << "  \"tier_quantum_ms\": {\"numerator\":25,\"denominator\":3},\n"
         << "  \"tier_fps\": [120,60,30],\n"
         << "  \"classify\": {\"iterations\":" << kClassifyIterations
         << ",\"median_batch_ns\":" << classify_batch_ns << "},\n"
         << "  \"route_select\": {\"iterations\":" << kRouteIterations
         << ",\"median_batch_ns\":" << route_batch_ns << "},\n"
         << "  \"window_evaluate\": {\"iterations\":" << kWindowIterations
         << ",\"median_batch_ns\":" << window_batch_ns << "},\n"
         << "  \"fixture\": {"
         << "\"dense_ns\":13400000,"
         << "\"optimized_ns\":1368750,"
         << "\"dense_work_units\":68024448,"
         << "\"optimized_work_units\":7558272,"
         << "\"selected_route_id\":" << initial_selection.selected_route_id << ","
         << "\"selected_tier\":" << initial_selection.selected_tier << ","
         << "\"budget_met\":" << static_cast<unsigned>(initial_selection.budget_met) << ","
         << "\"window_policy_met\":" << static_cast<unsigned>(initial_window.window_policy_met)
         << "},\n"
         << "  \"timing_is_noncanonical\": true,\n"
         << "  \"authoritative_state_changed\": false\n"
         << "}\n";

    return 0;
}
