#include "hhs_runtime_exact_abi.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
#include <unordered_map>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_sink = 0;

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
            std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin).count()));
    }
    std::sort(samples.begin(), samples.end());
    return samples[samples.size() / 2U];
}

std::uint64_t ratio_x1000(std::uint64_t numerator, std::uint64_t denominator) {
    if (denominator == 0U) return 0U;
    if (numerator > std::numeric_limits<std::uint64_t>::max() / 1000U)
        return (numerator / denominator) * 1000U;
    return (numerator * 1000U) / denominator;
}

bool phase_cells_equivalent(
    const HHSExactPass219BPhaseCellV1 &left,
    const HHSExactPass219BPhaseCellV1 &right
) {
    if (left.projection_index != right.projection_index ||
        left.phase_origin81 != right.phase_origin81 ||
        left.outer_count != right.outer_count ||
        left.center_closure_preserved != right.center_closure_preserved ||
        left.tensor_source_preserved != right.tensor_source_preserved)
        return false;
    for (std::size_t i = 0; i < HHS_EXACT_PASS219B_OUTER_CELL_COUNT; ++i) {
        const auto &a = left.outer[i];
        const auto &b = right.outer[i];
        if (a.perimeter_index != b.perimeter_index || a.ring != b.ring ||
            a.ring_step != b.ring_step || a.phase_basis != b.phase_basis ||
            a.rotation_family != b.rotation_family || a.direction != b.direction ||
            a.phase_position81 != b.phase_position81 || a.relation_role != b.relation_role)
            return false;
    }
    return true;
}

}  // namespace

int main(int argc, char **argv) {
    constexpr std::size_t kParents = HHS_EXACT_PASS219B_PARENT_SLOT_COUNT;
    constexpr std::size_t kOrigins = HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT;
    constexpr std::size_t kSurfaceCells = kParents * kOrigins;
    constexpr std::size_t kVectorQueries = 16U;
    constexpr std::size_t kCacheQueries = 200000U;
    constexpr std::uint8_t kMaterializedOrigin = 37U;

    std::vector<HHSExactPass219HydrationCoordinateV1> parents(kParents);
    for (std::size_t slot = 0; slot < kParents; ++slot) {
        const std::uint32_t u = static_cast<std::uint32_t>(slot);
        const std::uint8_t operation64 = static_cast<std::uint8_t>(u / HHS_EXACT_PASS219_G243_COUNT);
        const std::uint16_t g243 = static_cast<std::uint16_t>(u % HHS_EXACT_PASS219_G243_COUNT);
        const HHSExactStatus status = hhs_exact_pass219_coordinate_from_pass189(
            0U, 0, operation64, g243, &parents[slot]);
        if (status != HHS_EXACT_STATUS_OK || parents[slot].trit != 0U ||
            parents[slot].slot5184 != slot) {
            std::cerr << "parent coordinate construction failed at slot " << slot << "\n";
            return 2;
        }
    }

    std::vector<std::uint64_t> flat_indices;
    flat_indices.reserve(kSurfaceCells);
    std::vector<std::uint64_t> parent_base(kParents);
    for (std::size_t p = 0; p < kParents; ++p) {
        for (std::size_t origin = 0; origin < kOrigins; ++origin) {
            std::uint64_t index = 0U;
            const HHSExactStatus status = hhs_exact_pass219b_projection_index(
                &parents[p], static_cast<std::uint8_t>(origin), &index);
            if (status != HHS_EXACT_STATUS_OK) {
                std::cerr << "projection index construction failed\n";
                return 3;
            }
            if (origin == 0U) parent_base[p] = index / kOrigins;
            flat_indices.push_back(index);
        }
    }
    if (flat_indices.size() != HHS_EXACT_PASS219B_PHASE_CELLS_PER_5184) {
        std::cerr << "surface cardinality mismatch\n";
        return 4;
    }

    std::array<std::uint8_t, kVectorQueries> query_origins{};
    for (std::size_t i = 0; i < query_origins.size(); ++i)
        query_origins[i] = static_cast<std::uint8_t>((11U + 37U * i) % kOrigins);

    const auto dense_vector_scan = [&]() -> std::uint64_t {
        std::uint64_t checksum = 0U;
        for (std::size_t q = 0; q < query_origins.size(); ++q) {
            const std::uint8_t origin = query_origins[q];
            std::uint64_t best = std::numeric_limits<std::uint64_t>::max();
            for (const std::uint64_t index : flat_indices) {
                if ((index % kOrigins) != origin) continue;
                const std::uint64_t score = mix64(index ^ (0xD1B54A32D192ED03ULL + q));
                if (score < best) best = score;
            }
            checksum ^= best;
        }
        return checksum;
    };

    const auto phase_vector_scan = [&]() -> std::uint64_t {
        std::uint64_t checksum = 0U;
        for (std::size_t q = 0; q < query_origins.size(); ++q) {
            const std::uint8_t origin = query_origins[q];
            std::uint64_t best = std::numeric_limits<std::uint64_t>::max();
            for (const std::uint64_t base : parent_base) {
                const std::uint64_t index = base * kOrigins + origin;
                const std::uint64_t score = mix64(index ^ (0xD1B54A32D192ED03ULL + q));
                if (score < best) best = score;
            }
            checksum ^= best;
        }
        return checksum;
    };

    const std::uint64_t dense_vector_checksum = dense_vector_scan();
    const std::uint64_t phase_vector_checksum = phase_vector_scan();
    if (dense_vector_checksum != phase_vector_checksum) {
        std::cerr << "vector shortlist equality failure\n";
        return 5;
    }
    const std::uint64_t dense_vector_ns = median_ns([&]() {
        g_sink ^= dense_vector_scan();
    }, 7);
    const std::uint64_t phase_vector_ns = median_ns([&]() {
        g_sink ^= phase_vector_scan();
    }, 7);

    std::unordered_map<std::uint64_t, std::uint64_t> hash_cache;
    hash_cache.reserve(kSurfaceCells * 2U);
    std::vector<std::uint64_t> dense_cache(kSurfaceCells);
    const std::uint64_t surface_base = flat_indices.front();
    for (std::size_t i = 0; i < flat_indices.size(); ++i) {
        const std::uint64_t payload = mix64(flat_indices[i] ^ 0xA0761D6478BD642FULL);
        hash_cache.emplace(flat_indices[i], payload);
        dense_cache[i] = payload;
    }

    std::vector<std::uint64_t> cache_keys;
    cache_keys.reserve(kCacheQueries);
    for (std::size_t i = 0; i < kCacheQueries; ++i) {
        const std::size_t parent = (i * 2654435761ULL + 97ULL) % kParents;
        const std::size_t origin = (i * 37ULL + 11ULL) % kOrigins;
        cache_keys.push_back(flat_indices[parent * kOrigins + origin]);
    }

    const auto hash_cache_lookup = [&]() -> std::uint64_t {
        std::uint64_t checksum = 0U;
        for (const std::uint64_t key : cache_keys) {
            const auto it = hash_cache.find(key);
            if (it == hash_cache.end()) return std::numeric_limits<std::uint64_t>::max();
            checksum ^= it->second;
        }
        return checksum;
    };

    const auto phase_address_lookup = [&]() -> std::uint64_t {
        std::uint64_t checksum = 0U;
        for (const std::uint64_t key : cache_keys) {
            if (key < surface_base) return std::numeric_limits<std::uint64_t>::max();
            const std::uint64_t local = key - surface_base;
            if (local >= dense_cache.size()) return std::numeric_limits<std::uint64_t>::max();
            checksum ^= dense_cache[static_cast<std::size_t>(local)];
        }
        return checksum;
    };

    const std::uint64_t hash_checksum = hash_cache_lookup();
    const std::uint64_t address_checksum = phase_address_lookup();
    if (hash_checksum != address_checksum ||
        hash_checksum == std::numeric_limits<std::uint64_t>::max()) {
        std::cerr << "cache lookup equality failure\n";
        return 6;
    }
    const std::uint64_t hash_cache_ns = median_ns([&]() {
        g_sink ^= hash_cache_lookup();
    }, 9);
    const std::uint64_t phase_address_ns = median_ns([&]() {
        g_sink ^= phase_address_lookup();
    }, 9);

    std::vector<HHSExactPass219BPhaseCellV1> full_cells(kSurfaceCells);
    std::vector<HHSExactPass219BPhaseCellV1> selected_cells(kParents);
    std::size_t full_count = 0U;
    std::size_t selected_count = 0U;

    const auto materialize_full = [&]() {
        std::size_t count = 0U;
        const HHSExactStatus status = hhs_exact_pass219b_expand_selected(
            parents.data(), parents.size(), 0U,
            static_cast<std::uint8_t>(kOrigins), full_cells.data(), full_cells.size(), &count);
        if (status != HHS_EXACT_STATUS_OK || count != kSurfaceCells) {
            std::cerr << "full materialization failed\n";
            std::exit(7);
        }
        full_count = count;
        g_sink ^= full_cells[count - 1U].projection_index;
    };

    const auto materialize_selected = [&]() {
        std::size_t count = 0U;
        const HHSExactStatus status = hhs_exact_pass219b_expand_selected(
            parents.data(), parents.size(), kMaterializedOrigin, 1U,
            selected_cells.data(), selected_cells.size(), &count);
        if (status != HHS_EXACT_STATUS_OK || count != kParents) {
            std::cerr << "selected materialization failed\n";
            std::exit(8);
        }
        selected_count = count;
        g_sink ^= selected_cells[count - 1U].projection_index;
    };

    materialize_full();
    materialize_selected();
    for (std::size_t p = 0; p < kParents; ++p) {
        if (!phase_cells_equivalent(
                full_cells[p * kOrigins + kMaterializedOrigin], selected_cells[p])) {
            std::cerr << "selected materialization equality failure at parent " << p << "\n";
            return 9;
        }
    }

    const std::uint64_t full_materialize_ns = median_ns(materialize_full, 5);
    const std::uint64_t selected_materialize_ns = median_ns(materialize_selected, 9);

    const std::uint64_t dense_examined =
        static_cast<std::uint64_t>(kSurfaceCells) * query_origins.size();
    const std::uint64_t phase_examined =
        static_cast<std::uint64_t>(kParents) * query_origins.size();
    const std::uint64_t full_bytes =
        static_cast<std::uint64_t>(full_count) * sizeof(HHSExactPass219BPhaseCellV1);
    const std::uint64_t selected_bytes =
        static_cast<std::uint64_t>(selected_count) * sizeof(HHSExactPass219BPhaseCellV1);

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

    *out << "{\n"
         << "  \"schema\": \"HHS_PASS_219B_I2_PHASE_LOCALITY_BENCHMARK_V1\",\n"
         << "  \"surface_parent_count\": " << kParents << ",\n"
         << "  \"phase_origin_count\": " << kOrigins << ",\n"
         << "  \"surface_phase_cells\": " << kSurfaceCells << ",\n"
         << "  \"phase_cell_size_bytes\": " << sizeof(HHSExactPass219BPhaseCellV1) << ",\n"
         << "  \"vector_shortlist\": {\n"
         << "    \"queries\": " << query_origins.size() << ",\n"
         << "    \"dense_candidates_examined\": " << dense_examined << ",\n"
         << "    \"phase_candidates_examined\": " << phase_examined << ",\n"
         << "    \"work_reduction_x1000\": " << ratio_x1000(dense_examined, phase_examined) << ",\n"
         << "    \"dense_median_ns\": " << dense_vector_ns << ",\n"
         << "    \"phase_median_ns\": " << phase_vector_ns << ",\n"
         << "    \"wall_speedup_x1000\": " << ratio_x1000(dense_vector_ns, phase_vector_ns) << ",\n"
         << "    \"exact_result_equal\": true\n"
         << "  },\n"
         << "  \"cache_exact_lookup\": {\n"
         << "    \"queries\": " << cache_keys.size() << ",\n"
         << "    \"hash_map_median_ns\": " << hash_cache_ns << ",\n"
         << "    \"phase_address_median_ns\": " << phase_address_ns << ",\n"
         << "    \"wall_speedup_x1000\": " << ratio_x1000(hash_cache_ns, phase_address_ns) << ",\n"
         << "    \"exact_result_equal\": true,\n"
         << "    \"scope\": \"LOCAL_5184_X_81_DENSE_SLICE\"\n"
         << "  },\n"
         << "  \"materialization\": {\n"
         << "    \"full_cells\": " << full_count << ",\n"
         << "    \"selected_cells\": " << selected_count << ",\n"
         << "    \"full_bytes\": " << full_bytes << ",\n"
         << "    \"selected_bytes\": " << selected_bytes << ",\n"
         << "    \"capacity_reduction_x1000\": " << ratio_x1000(full_bytes, selected_bytes) << ",\n"
         << "    \"full_median_ns\": " << full_materialize_ns << ",\n"
         << "    \"selected_median_ns\": " << selected_materialize_ns << ",\n"
         << "    \"wall_speedup_x1000\": " << ratio_x1000(full_materialize_ns, selected_materialize_ns) << ",\n"
         << "    \"exact_selected_equal\": true\n"
         << "  },\n"
         << "  \"authoritative_state_changed\": false\n"
         << "}\n";

    return 0;
}
