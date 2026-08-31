#include "hhs_runtime_exact_abi.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
#include <unordered_map>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_sink = 0U;

std::uint64_t mix64(std::uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30U)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27U)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31U);
}

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
            std::chrono::duration_cast<std::chrono::nanoseconds>(
                end - begin
            ).count()
        ));
    }
    std::sort(samples.begin(), samples.end());
    return samples[samples.size() / 2U];
}

std::uint64_t ratio_x1000(
    std::uint64_t numerator,
    std::uint64_t denominator
) {
    if (denominator == 0U) return 0U;
    if (numerator >
        std::numeric_limits<std::uint64_t>::max() / 1000U)
        return (numerator / denominator) * 1000U;
    return (numerator * 1000U) / denominator;
}

void reference_import(
    const HHSExactVM81Frame &frame,
    HHSExactPass219H36VMStateV1 &state
) {
    if (hhs_exact_pass219_h36_vm_init(&state) != HHS_EXACT_STATUS_OK)
        std::abort();
    for (std::uint32_t linear = 0U; linear < 5184U; ++linear) {
        const std::uint64_t bit =
            (frame.words[linear / 64U] >> (linear % 64U)) & 1U;
        const std::uint32_t word144 = linear / 36U;
        const std::uint32_t bit36 = linear % 36U;
        state.memory[word144] |= bit << (35U - bit36);
    }
}

void reference_export(
    const HHSExactPass219H36VMStateV1 &state,
    HHSExactVM81Frame &frame
) {
    std::memset(&frame, 0, sizeof(frame));
    for (std::uint32_t linear = 0U; linear < 5184U; ++linear) {
        const std::uint32_t word144 = linear / 36U;
        const std::uint32_t bit36 = linear % 36U;
        const std::uint64_t bit =
            (state.memory[word144] >> (35U - bit36)) & 1U;
        frame.words[linear / 64U] |= bit << (linear % 64U);
    }
}

void init_pass207(HHSExactPass219InheritedPass207BindingV1 &p) {
    std::memset(&p, 0, sizeof(p));
    p.struct_size = sizeof(p);
    p.version = hhs_exact_pass219_inherited_pass207_version();
    p.pass_number = HHS_EXACT_PASS219_INHERITED_PASS207_NUMBER;
    p.classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    p.stable_vm5184_lane_dispatch_bound = 1U;
    p.lane_phase_bijection_bound = 1U;
    p.ordered_cell_pack_bound = 1U;
    p.ordered_hydration_bound = 1U;
    p.exact_cpu_oracle_verification_bound = 1U;
    p.content_keyed_cache_bound = 1U;
    p.stable_vector_ranking_bound = 1U;
    p.candidate_only_bound = 1U;
    p.gpu_hash72_commit_forbidden = 1U;
    p.gpu_canonical_mutation_forbidden = 1U;
    p.gpu_vm81_bypass_forbidden = 1U;
    p.pass205_singleton_vm81_admission_bound = 1U;
    p.physical_gpu_fail_closed = 1U;
    p.pass208_successor_bound = 1U;
    p.logical_lanes_per_batch = 5184U;
}

void init_pass208(HHSExactPass219InheritedPass208BindingV1 &p) {
    std::memset(&p, 0, sizeof(p));
    p.struct_size = sizeof(p);
    p.version = hhs_exact_pass219_inherited_pass208_version();
    p.pass_number = HHS_EXACT_PASS219_INHERITED_PASS208_NUMBER;
    p.classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    p.gpu_candidate_expansion_bound = 1U;
    p.exact_cpu_oracle_verification_bound = 1U;
    p.stable_integer_ranking_bound = 1U;
    p.pass205_singleton_vm81_commit_path_bound = 1U;
    p.gpu_hash72_commit_forbidden = 1U;
    p.gpu_canonical_persistence_forbidden = 1U;
    p.gpu_vm81_bypass_forbidden = 1U;
    p.physical_gpu_fail_closed = 1U;
    p.pass209_successor_bound = 1U;
    p.logical_lanes_per_branch = 5184U;
}

bool circuit_equal(
    const HHSExactPass219H36FactorizationCircuitV1 &a,
    const HHSExactPass219H36FactorizationCircuitV1 &b
) {
    return std::memcmp(&a, &b, sizeof(a)) == 0;
}

}  // namespace

int main(int argc, char **argv) {
    HHSExactVM81Frame input{};
    for (std::uint32_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        input.words[i] = mix64(0xA0761D6478BD642FULL + i);

    HHSExactPass219H36VMStateV1 reference_state{};
    HHSExactPass219H36VMStateV1 optimized_state{};
    HHSExactVM81Frame reference_frame{};
    HHSExactVM81Frame optimized_frame{};

    reference_import(input, reference_state);
    if (hhs_exact_pass219_h36_import_vm81(
            &input, &optimized_state) != HHS_EXACT_STATUS_OK) {
        std::cerr << "optimized import failed\n";
        return 2;
    }
    if (std::memcmp(
            reference_state.memory,
            optimized_state.memory,
            sizeof(reference_state.memory)) != 0) {
        std::cerr << "transcode import equality failed\n";
        return 3;
    }

    reference_export(reference_state, reference_frame);
    if (hhs_exact_pass219_h36_export_vm81(
            &optimized_state, &optimized_frame) != HHS_EXACT_STATUS_OK ||
        std::memcmp(&reference_frame, &optimized_frame,
                    sizeof(reference_frame)) != 0 ||
        std::memcmp(&input, &optimized_frame, sizeof(input)) != 0) {
        std::cerr << "transcode roundtrip equality failed\n";
        return 4;
    }

    constexpr std::uint32_t kTranscodeRounds = 256U;
    const auto reference_transcode = [&]() {
        HHSExactPass219H36VMStateV1 state{};
        HHSExactVM81Frame frame{};
        for (std::uint32_t r = 0U; r < kTranscodeRounds; ++r) {
            reference_import(input, state);
            reference_export(state, frame);
            g_sink ^= frame.words[(r * 17U) % HHS_EXACT_VM81_CELLS];
        }
    };
    const auto optimized_transcode = [&]() {
        HHSExactPass219H36VMStateV1 state{};
        HHSExactVM81Frame frame{};
        for (std::uint32_t r = 0U; r < kTranscodeRounds; ++r) {
            if (hhs_exact_pass219_h36_import_vm81(&input, &state) !=
                HHS_EXACT_STATUS_OK)
                std::abort();
            if (hhs_exact_pass219_h36_export_vm81(&state, &frame) !=
                HHS_EXACT_STATUS_OK)
                std::abort();
            g_sink ^= frame.words[(r * 17U) % HHS_EXACT_VM81_CELLS];
        }
    };
    const std::uint64_t reference_transcode_ns =
        median_ns(reference_transcode, 9);
    const std::uint64_t optimized_transcode_ns =
        median_ns(optimized_transcode, 9);

    std::array<std::uint8_t, 5184> register_bytes{};
    std::array<std::uint8_t, 36U * 288U> snapshots{};
    std::array<std::uint8_t, 36> available{};
    std::array<std::uint8_t, 5184> generic_reconstruction{};
    std::array<std::uint8_t, 5184> block_reconstruction{};

    if (hhs_exact_pass219_h36_boolean_expand(
            &input, register_bytes.data()) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_hfc_snapshot_encode(
            register_bytes.data(),
            snapshots.data(),
            snapshots.size()) != HHS_EXACT_STATUS_OK) {
        std::cerr << "HFC setup failed\n";
        return 5;
    }

    for (std::uint32_t erased = 0U; erased < 36U; ++erased) {
        available.fill(1U);
        available[erased] = 0U;
        if (hhs_exact_pass219_h36_hfc_snapshot_reconstruct(
                snapshots.data(), snapshots.size(), available.data(),
                generic_reconstruction.data()) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_hfc_snapshot_reconstruct_blocks(
                snapshots.data(), snapshots.size(), available.data(),
                block_reconstruction.data()) != HHS_EXACT_STATUS_OK ||
            generic_reconstruction != block_reconstruction ||
            generic_reconstruction != register_bytes) {
            std::cerr << "HFC block reconstruction equality failed at "
                      << erased << "\n";
            return 6;
        }
    }

    constexpr std::uint32_t kHfcRounds = 512U;
    available.fill(1U);
    available[17U] = 0U;
    const auto generic_hfc = [&]() {
        for (std::uint32_t r = 0U; r < kHfcRounds; ++r) {
            if (hhs_exact_pass219_h36_hfc_snapshot_reconstruct(
                    snapshots.data(), snapshots.size(), available.data(),
                    generic_reconstruction.data()) != HHS_EXACT_STATUS_OK)
                std::abort();
            g_sink ^= generic_reconstruction[(r * 97U) % 5184U];
        }
    };
    const auto block_hfc = [&]() {
        for (std::uint32_t r = 0U; r < kHfcRounds; ++r) {
            if (hhs_exact_pass219_h36_hfc_snapshot_reconstruct_blocks(
                    snapshots.data(), snapshots.size(), available.data(),
                    block_reconstruction.data()) != HHS_EXACT_STATUS_OK)
                std::abort();
            g_sink ^= block_reconstruction[(r * 97U) % 5184U];
        }
    };
    const std::uint64_t generic_hfc_ns = median_ns(generic_hfc, 9);
    const std::uint64_t block_hfc_ns = median_ns(block_hfc, 9);

    HHSExactPass219InheritedPass207BindingV1 pass207{};
    HHSExactPass219InheritedPass208BindingV1 pass208{};
    HHSExactPass219H36GPULocalityPlanV1 plan{};
    init_pass207(pass207);
    init_pass208(pass208);
    if (hhs_exact_pass219_h36_gpu_locality_plan(
            &pass207, &pass208,
            12U, 17U, 3U, 11U, &plan) != HHS_EXACT_STATUS_OK) {
        std::cerr << "locality plan failed\n";
        return 7;
    }

    std::vector<HHSExactPass219H36FactorizationCircuitV1> full(5184U);
    std::vector<HHSExactPass219H36FactorizationCircuitV1>
        selected(plan.selected_lane_count);

    const auto materialize_full = [&]() {
        for (std::uint32_t linear = 0U; linear < 5184U; ++linear) {
            if (hhs_exact_pass219_h36_factorization_circuit(
                    static_cast<std::uint16_t>(linear),
                    &full[linear]) != HHS_EXACT_STATUS_OK)
                std::abort();
        }
        g_sink ^= full[5179U].linear5184;
    };
    const auto materialize_selected = [&]() {
        for (std::uint32_t ordinal = 0U;
             ordinal < plan.selected_lane_count;
             ++ordinal) {
            if (hhs_exact_pass219_h36_gpu_locality_lane(
                    &plan, ordinal, &selected[ordinal]) !=
                HHS_EXACT_STATUS_OK)
                std::abort();
        }
        g_sink ^= selected.back().linear5184;
    };

    materialize_full();
    materialize_selected();
    for (std::uint32_t ordinal = 0U;
         ordinal < plan.selected_lane_count;
         ++ordinal) {
        const std::uint32_t word_offset = ordinal / plan.bit_count;
        const std::uint32_t bit_offset = ordinal % plan.bit_count;
        const std::uint32_t linear =
            (plan.first_word144 + word_offset) * 36U +
            (plan.first_bit36 + bit_offset);
        if (!circuit_equal(full[linear], selected[ordinal])) {
            std::cerr << "locality selected equality failed\n";
            return 8;
        }
    }
    const std::uint64_t full_locality_ns =
        median_ns(materialize_full, 7);
    const std::uint64_t selected_locality_ns =
        median_ns(materialize_selected, 9);

    constexpr std::size_t kCacheQueries = 200000U;
    std::vector<std::uint64_t> payloads(5184U);
    std::unordered_map<std::uint32_t, std::uint64_t> map_cache;
    map_cache.reserve(10368U);
    for (std::uint32_t i = 0U; i < 5184U; ++i) {
        payloads[i] = mix64(0xD1B54A32D192ED03ULL ^ i);
        map_cache.emplace(i, payloads[i]);
    }
    std::vector<std::uint32_t> cache_keys;
    cache_keys.reserve(kCacheQueries);
    for (std::size_t i = 0U; i < kCacheQueries; ++i)
        cache_keys.push_back(
            static_cast<std::uint32_t>(
                (i * 2654435761ULL + 97ULL) % 5184ULL
            )
        );

    const auto hash_lookup = [&]() -> std::uint64_t {
        std::uint64_t checksum = 0U;
        for (const std::uint32_t key : cache_keys) {
            const auto it = map_cache.find(key);
            if (it == map_cache.end())
                return std::numeric_limits<std::uint64_t>::max();
            checksum ^= it->second;
        }
        return checksum;
    };
    const auto direct_lookup = [&]() -> std::uint64_t {
        std::uint64_t checksum = 0U;
        for (const std::uint32_t key : cache_keys)
            checksum ^= payloads[key];
        return checksum;
    };
    const std::uint64_t hash_checksum = hash_lookup();
    const std::uint64_t direct_checksum = direct_lookup();
    if (hash_checksum != direct_checksum ||
        hash_checksum == std::numeric_limits<std::uint64_t>::max()) {
        std::cerr << "cache direct-address equality failed\n";
        return 9;
    }
    const std::uint64_t hash_lookup_ns = median_ns([&]() {
        g_sink ^= hash_lookup();
    }, 9);
    const std::uint64_t direct_lookup_ns = median_ns([&]() {
        g_sink ^= direct_lookup();
    }, 9);

    const bool transcode_winner =
        optimized_transcode_ns < reference_transcode_ns;
    const bool hfc_winner = block_hfc_ns < generic_hfc_ns;
    const bool locality_winner =
        selected_locality_ns < full_locality_ns;
    const bool cache_winner = direct_lookup_ns < hash_lookup_ns;

    std::ostream *out = &std::cout;
    std::ofstream file;
    if (argc > 1) {
        file.open(argv[1], std::ios::out | std::ios::trunc);
        if (!file) {
            std::cerr << "unable to open output file\n";
            return 10;
        }
        out = &file;
    }

    *out
        << "{\n"
        << "  \"schema\": \"HHS_PASS219_H36_OPTIMIZATION_BENCHMARK_V1\",\n"
        << "  \"cpu_reference\": true,\n"
        << "  \"physical_gpu_measured\": false,\n"
        << "  \"transcode\": {\n"
        << "    \"rounds_per_sample\": " << kTranscodeRounds << ",\n"
        << "    \"reference_median_ns\": " << reference_transcode_ns << ",\n"
        << "    \"optimized_median_ns\": " << optimized_transcode_ns << ",\n"
        << "    \"speedup_x1000\": "
        << ratio_x1000(reference_transcode_ns, optimized_transcode_ns) << ",\n"
        << "    \"exact_result_equal\": true,\n"
        << "    \"retained_winner\": "
        << (transcode_winner ? "true" : "false") << "\n"
        << "  },\n"
        << "  \"hfc_reconstruction\": {\n"
        << "    \"rounds_per_sample\": " << kHfcRounds << ",\n"
        << "    \"single_erasure_patterns_validated\": 36,\n"
        << "    \"generic_median_ns\": " << generic_hfc_ns << ",\n"
        << "    \"block_median_ns\": " << block_hfc_ns << ",\n"
        << "    \"speedup_x1000\": "
        << ratio_x1000(generic_hfc_ns, block_hfc_ns) << ",\n"
        << "    \"exact_result_equal\": true,\n"
        << "    \"retained_winner\": "
        << (hfc_winner ? "true" : "false") << "\n"
        << "  },\n"
        << "  \"gpu_locality_cpu_reference\": {\n"
        << "    \"full_lanes\": " << plan.full_lane_count << ",\n"
        << "    \"selected_lanes\": " << plan.selected_lane_count << ",\n"
        << "    \"avoided_lanes\": " << plan.avoided_lane_count << ",\n"
        << "    \"work_reduction_x1000\": "
        << ratio_x1000(plan.full_lane_count, plan.selected_lane_count) << ",\n"
        << "    \"full_median_ns\": " << full_locality_ns << ",\n"
        << "    \"selected_median_ns\": " << selected_locality_ns << ",\n"
        << "    \"speedup_x1000\": "
        << ratio_x1000(full_locality_ns, selected_locality_ns) << ",\n"
        << "    \"exact_selected_equal\": true,\n"
        << "    \"retained_winner\": "
        << (locality_winner ? "true" : "false") << "\n"
        << "  },\n"
        << "  \"native_cache_address\": {\n"
        << "    \"queries\": " << cache_keys.size() << ",\n"
        << "    \"hash_lookup_median_ns\": " << hash_lookup_ns << ",\n"
        << "    \"direct_lookup_median_ns\": " << direct_lookup_ns << ",\n"
        << "    \"speedup_x1000\": "
        << ratio_x1000(hash_lookup_ns, direct_lookup_ns) << ",\n"
        << "    \"exact_result_equal\": true,\n"
        << "    \"retained_winner\": "
        << (cache_winner ? "true" : "false") << "\n"
        << "  },\n"
        << "  \"all_candidate_winners\": "
        << ((transcode_winner && hfc_winner &&
             locality_winner && cache_winner) ? "true" : "false")
        << ",\n"
        << "  \"authoritative_state_changed\": false\n"
        << "}\n";

    return 0;
}
