#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

extern "C" {
#include "hhs_pass219b_universal_phase_locality_1_0.h"
#include "hhs_pass219b_selective_projection_1_0.h"
#include "hhs_pass219b_sparse_dirty_projection_1_0.h"
}

namespace {

using Clock = std::chrono::steady_clock;

struct Ratio {
    uint32_t p;
    uint32_t q;
};

struct SparseResult {
    uint32_t p;
    uint32_t q;
    uint32_t dirty_cells;
    uint64_t selected_count;
    uint64_t update_count;
    uint64_t avoided_count;
    uint64_t full_work_units;
    uint64_t sparse_work_units;
    uint64_t full_ns;
    uint64_t sparse_ns;
    uint64_t work_reduction_x1000;
    uint64_t wall_speedup_x1000;
    bool exact_equal;
    uint32_t span_count;
};

static void require_ok(HHSExactStatus status, const char *what) {
    if (status != HHS_EXACT_STATUS_OK) {
        throw std::runtime_error(std::string(what) + " failed status=" + std::to_string(static_cast<int>(status)));
    }
}

static uint64_t elapsed_ns(const Clock::time_point &a, const Clock::time_point &b) {
    return static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(b - a).count()
    );
}

static uint64_t mix64(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static uint64_t current_value(uint32_t original_id, uint64_t previous, bool dirty) {
    if (!dirty) {
        return previous;
    }
    return previous ^ mix64(static_cast<uint64_t>(original_id) + UINT64_C(0x219b081));
}

static std::vector<uint32_t> dirty_cells_for_count(uint32_t count) {
    std::vector<uint32_t> cells;
    cells.reserve(count);
    if (count == 81U) {
        for (uint32_t c = 0; c < 81U; ++c) {
            cells.push_back(c);
        }
        return cells;
    }
    for (uint32_t i = 0; i < count; ++i) {
        const uint32_t c = static_cast<uint32_t>((static_cast<uint64_t>(i) * 81ULL) / count);
        if (cells.empty() || cells.back() != c) {
            cells.push_back(c);
        }
    }
    if (cells.size() != count) {
        throw std::runtime_error("dirty cell generator did not preserve requested cardinality");
    }
    return cells;
}

static bool is_dirty_cell(const std::vector<uint32_t> &dirty, uint32_t cell) {
    return std::binary_search(dirty.begin(), dirty.end(), cell);
}

static SparseResult run_sparse_case(
    uint64_t source_count,
    uint32_t p,
    uint32_t q,
    uint32_t dirty_count,
    const std::vector<uint32_t> &ids,
    const HHSExactPass219BProjectionCellRangeV1 ranges[81],
    const std::vector<uint64_t> &previous
) {
    const std::vector<uint32_t> dirty = dirty_cells_for_count(dirty_count);
    HHSExactPass219BSparseProjectionSpanV1 spans[81] = {};
    HHSExactPass219BSparseDirtyProjectionPlanV1 sparse_plan = {};
    require_ok(
        hhs_exact_pass219b_sparse_dirty_projection_build_spans(
            ranges,
            81U,
            ids.size(),
            dirty.data(),
            dirty.size(),
            spans,
            81U,
            &sparse_plan
        ),
        "sparse_dirty_projection_build_spans"
    );

    std::vector<uint64_t> full(ids.size());
    std::vector<uint64_t> sparse = previous;

    const auto full_a = Clock::now();
    for (uint32_t cell = 0; cell < 81U; ++cell) {
        const bool dirty_here = is_dirty_cell(dirty, cell);
        const uint64_t first = ranges[cell].first_selected;
        const uint64_t end = ranges[cell].end_selected;
        for (uint64_t pos = first; pos < end; ++pos) {
            full[static_cast<size_t>(pos)] = current_value(
                ids[static_cast<size_t>(pos)],
                previous[static_cast<size_t>(pos)],
                dirty_here
            );
        }
    }
    const auto full_b = Clock::now();

    const auto sparse_a = Clock::now();
    for (uint32_t s = 0; s < sparse_plan.span_count; ++s) {
        const uint64_t first = spans[s].first_selected;
        const uint64_t end = spans[s].end_selected;
        for (uint64_t pos = first; pos < end; ++pos) {
            sparse[static_cast<size_t>(pos)] = current_value(
                ids[static_cast<size_t>(pos)],
                previous[static_cast<size_t>(pos)],
                true
            );
        }
    }
    const auto sparse_b = Clock::now();

    const bool equal = (full == sparse);
    const HHSExactStatus verify = hhs_exact_pass219b_sparse_dirty_projection_verify(
        &sparse_plan,
        spans,
        sparse_plan.span_count,
        sparse_plan.update_selected_count,
        1U,
        equal ? 1U : 0U,
        0U
    );
    require_ok(verify, "sparse_dirty_projection_verify");

    const uint64_t full_ns = elapsed_ns(full_a, full_b);
    const uint64_t sparse_ns = elapsed_ns(sparse_a, sparse_b);
    const uint64_t sparse_work = sparse_plan.update_selected_count;
    const uint64_t work_x1000 = sparse_work == 0ULL
        ? 0ULL
        : (static_cast<uint64_t>(ids.size()) * 1000ULL) / sparse_work;
    const uint64_t wall_x1000 = sparse_ns == 0ULL ? 0ULL : (full_ns * 1000ULL) / sparse_ns;

    (void)source_count;
    return SparseResult{
        p,
        q,
        dirty_count,
        static_cast<uint64_t>(ids.size()),
        sparse_plan.update_selected_count,
        sparse_plan.avoided_selected_count,
        static_cast<uint64_t>(ids.size()),
        sparse_work,
        full_ns,
        sparse_ns,
        work_x1000,
        wall_x1000,
        equal,
        sparse_plan.span_count
    };
}

static void write_json_string(std::ofstream &out, const std::string &s) {
    out << '"';
    for (const char ch : s) {
        if (ch == '"' || ch == '\\') {
            out << '\\' << ch;
        } else if (ch == '\n') {
            out << "\\n";
        } else {
            out << ch;
        }
    }
    out << '"';
}

}  // namespace

int main(int argc, char **argv) {
    try {
        if (argc != 2) {
            std::cerr << "usage: pass219b_canonical_scaling_composition_benchmark OUTPUT.json\n";
            return 2;
        }

        constexpr uint64_t kSourceCount = 17625600ULL;
        constexpr uint64_t kPass208BaseLaneUnits = 2ULL * 5184ULL;
        constexpr uint32_t kCellCount = 81U;
        const Ratio ratios[] = {
            {1U, 3U},
            {7U, 20U},
            {5U, 14U},
            {4U, 11U},
            {3U, 8U},
            {2U, 5U},
            {5U, 12U},
        };
        const uint32_t dirty_counts[] = {1U, 3U, 7U, 27U, 81U};

        std::vector<HHSExactPass219BPhaseLocalityPlanV1> abstract_depth_plans;
        std::vector<int> lane_depth_status;
        std::vector<HHSExactPass219BPhaseLocalityPlanV1> lane_depth_plans;

        for (uint32_t depth = 1U; depth <= HHS_EXACT_PASS219B_PHASE_LOCALITY_MAX_DEPTH; ++depth) {
            std::vector<HHSExactPass219BPhaseLocalityDimensionV1> dims(depth);
            for (auto &dim : dims) {
                dim.potential_q = 81ULL;
                dim.selected_s = 1ULL;
            }

            HHSExactPass219BPhaseLocalityPlanV1 abstract_plan = {};
            require_ok(
                hhs_exact_pass219b_phase_locality_plan(
                    dims.data(),
                    dims.size(),
                    1U,
                    0U,
                    1ULL,
                    &abstract_plan
                ),
                "phase_locality_plan abstract"
            );
            abstract_depth_plans.push_back(abstract_plan);

            HHSExactPass219BPhaseLocalityPlanV1 lane_plan = {};
            const HHSExactStatus lane_status = hhs_exact_pass219b_phase_locality_plan(
                dims.data(),
                dims.size(),
                1U,
                0U,
                kPass208BaseLaneUnits,
                &lane_plan
            );
            lane_depth_status.push_back(static_cast<int>(lane_status));
            lane_depth_plans.push_back(lane_plan);
        }

        HHSExactPass219BPhaseLocalityDimensionV1 no_selector_dim{81ULL, 1ULL};
        HHSExactPass219BPhaseLocalityPlanV1 no_selector_plan = {};
        require_ok(
            hhs_exact_pass219b_phase_locality_plan(
                &no_selector_dim,
                1U,
                0U,
                0U,
                kPass208BaseLaneUnits,
                &no_selector_plan
            ),
            "phase_locality_plan no selector"
        );

        HHSExactPass219BPhaseLocalityPlanV1 authority_plan = {};
        require_ok(
            hhs_exact_pass219b_phase_locality_plan(
                &no_selector_dim,
                1U,
                1U,
                0U,
                kPass208BaseLaneUnits,
                &authority_plan
            ),
            "phase_locality_plan authority negative fixture"
        );
        const HHSExactStatus locality_authority_reject = hhs_exact_pass219b_phase_locality_verify_realization(
            &authority_plan,
            authority_plan.required_realized_units,
            1U,
            1U,
            1U
        );

        std::vector<SparseResult> sparse_results;
        std::vector<uint64_t> ratio_selected_counts;
        std::vector<uint64_t> ratio_build_ids_ns;

        HHSExactStatus dirty_incomplete_reject = HHS_EXACT_STATUS_OK;
        HHSExactStatus sparse_authority_reject = HHS_EXACT_STATUS_OK;

        for (const Ratio ratio : ratios) {
            HHSExactPass219BSelectiveProjectionPlanV1 projection_plan = {};
            require_ok(
                hhs_exact_pass219b_selective_projection_plan(
                    kSourceCount,
                    ratio.p,
                    ratio.q,
                    &projection_plan
                ),
                "selective_projection_plan"
            );

            std::vector<uint32_t> ids(static_cast<size_t>(projection_plan.selected_count));
            size_t built_count = 0U;
            const auto ids_a = Clock::now();
            require_ok(
                hhs_exact_pass219b_selective_projection_build_ids_u32(
                    kSourceCount,
                    ratio.p,
                    ratio.q,
                    ids.data(),
                    ids.size(),
                    &built_count
                ),
                "selective_projection_build_ids_u32"
            );
            const auto ids_b = Clock::now();
            if (built_count != ids.size()) {
                throw std::runtime_error("selected ID build count mismatch");
            }
            require_ok(
                hhs_exact_pass219b_selective_projection_validate_ids_u32(
                    kSourceCount,
                    ratio.p,
                    ratio.q,
                    ids.data(),
                    ids.size()
                ),
                "selective_projection_validate_ids_u32"
            );
            require_ok(
                hhs_exact_pass219b_selective_projection_verify(
                    &projection_plan,
                    ids.size(),
                    1U,
                    1U,
                    1U,
                    0U
                ),
                "selective_projection_verify"
            );

            HHSExactPass219BProjectionCellRangeV1 ranges[81] = {};
            require_ok(
                hhs_exact_pass219b_selective_projection_build_equal_cell_ranges(
                    ids.data(),
                    ids.size(),
                    kSourceCount,
                    kCellCount,
                    ranges,
                    kCellCount
                ),
                "selective_projection_build_equal_cell_ranges"
            );

            std::vector<uint64_t> previous(ids.size());
            for (size_t i = 0; i < ids.size(); ++i) {
                previous[i] = mix64(static_cast<uint64_t>(ids[i]) ^ UINT64_C(0x207208219b));
            }

            ratio_selected_counts.push_back(static_cast<uint64_t>(ids.size()));
            ratio_build_ids_ns.push_back(elapsed_ns(ids_a, ids_b));

            for (const uint32_t dirty_count : dirty_counts) {
                SparseResult result = run_sparse_case(
                    kSourceCount,
                    ratio.p,
                    ratio.q,
                    dirty_count,
                    ids,
                    ranges,
                    previous
                );
                sparse_results.push_back(result);

                if (ratio.p == 1U && ratio.q == 3U && dirty_count == 7U) {
                    const std::vector<uint32_t> dirty = dirty_cells_for_count(dirty_count);
                    HHSExactPass219BSparseProjectionSpanV1 spans[81] = {};
                    HHSExactPass219BSparseDirtyProjectionPlanV1 plan = {};
                    require_ok(
                        hhs_exact_pass219b_sparse_dirty_projection_build_spans(
                            ranges,
                            81U,
                            ids.size(),
                            dirty.data(),
                            dirty.size(),
                            spans,
                            81U,
                            &plan
                        ),
                        "sparse negative fixture build"
                    );
                    dirty_incomplete_reject = hhs_exact_pass219b_sparse_dirty_projection_verify(
                        &plan,
                        spans,
                        plan.span_count,
                        plan.update_selected_count,
                        0U,
                        1U,
                        0U
                    );
                    sparse_authority_reject = hhs_exact_pass219b_sparse_dirty_projection_verify(
                        &plan,
                        spans,
                        plan.span_count,
                        plan.update_selected_count,
                        1U,
                        1U,
                        1U
                    );
                }
            }
        }

        if (dirty_incomplete_reject != HHS_EXACT_STATUS_INVARIANT_FAILURE) {
            throw std::runtime_error("incomplete dirty witness did not fail closed");
        }
        if (sparse_authority_reject != HHS_EXACT_STATUS_INVARIANT_FAILURE) {
            throw std::runtime_error("sparse canonical authority request did not fail closed");
        }
        if (locality_authority_reject != HHS_EXACT_STATUS_INVARIANT_FAILURE) {
            throw std::runtime_error("phase locality canonical authority request did not fail closed");
        }
        for (const SparseResult &r : sparse_results) {
            if (!r.exact_equal) {
                throw std::runtime_error("sparse/full exact equality failure");
            }
        }

        std::ofstream out(argv[1], std::ios::binary);
        if (!out) {
            throw std::runtime_error("cannot open output");
        }

        out << "{\n";
        out << "  \"schema\": \"HHS_PASS219B_CANONICAL_SCALING_COMPOSITION_BENCHMARK_V1\",\n";
        out << "  \"source_count\": " << kSourceCount << ",\n";
        out << "  \"vm81_cells\": 81,\n";
        out << "  \"pass208_branch_families\": 2,\n";
        out << "  \"lanes_per_branch\": 5184,\n";
        out << "  \"phase_radix\": 81,\n";
        out << "  \"phase_max_depth\": " << HHS_EXACT_PASS219B_PHASE_LOCALITY_MAX_DEPTH << ",\n";

        out << "  \"phase_depth\": [\n";
        for (size_t i = 0; i < abstract_depth_plans.size(); ++i) {
            const auto &p = abstract_depth_plans[i];
            const auto &lp = lane_depth_plans[i];
            out << "    {\"depth\":" << (i + 1)
                << ",\"potential_phase_volume\":" << p.potential_phase_volume
                << ",\"materialized_phase_volume\":" << p.materialized_phase_volume
                << ",\"reduction_numerator\":" << p.reduction_numerator
                << ",\"reduction_denominator\":" << p.reduction_denominator
                << ",\"abstract_required_units\":" << p.required_realized_units
                << ",\"pass208_lane_status\":" << lane_depth_status[i];
            if (lane_depth_status[i] == static_cast<int>(HHS_EXACT_STATUS_OK)) {
                out << ",\"pass208_required_lane_units\":" << lp.required_realized_units;
            }
            out << "}";
            if (i + 1 != abstract_depth_plans.size()) out << ",";
            out << "\n";
        }
        out << "  ],\n";

        out << "  \"no_exact_selector\": {"
            << "\"route\":" << no_selector_plan.route
            << ",\"required_realized_units\":" << no_selector_plan.required_realized_units
            << ",\"dense_realization_forbidden\":" << static_cast<unsigned>(no_selector_plan.dense_realization_forbidden)
            << "},\n";

        out << "  \"projection_ratios\": [\n";
        for (size_t i = 0; i < (sizeof(ratios) / sizeof(ratios[0])); ++i) {
            out << "    {\"p\":" << ratios[i].p
                << ",\"q\":" << ratios[i].q
                << ",\"selected_count\":" << ratio_selected_counts[i]
                << ",\"avoided_count\":" << (kSourceCount - ratio_selected_counts[i])
                << ",\"build_ids_ns\":" << ratio_build_ids_ns[i]
                << "}";
            if (i + 1 != (sizeof(ratios) / sizeof(ratios[0]))) out << ",";
            out << "\n";
        }
        out << "  ],\n";

        out << "  \"sparse_cases\": [\n";
        for (size_t i = 0; i < sparse_results.size(); ++i) {
            const auto &r = sparse_results[i];
            out << "    {\"p\":" << r.p
                << ",\"q\":" << r.q
                << ",\"dirty_cells\":" << r.dirty_cells
                << ",\"selected_count\":" << r.selected_count
                << ",\"update_count\":" << r.update_count
                << ",\"avoided_count\":" << r.avoided_count
                << ",\"span_count\":" << r.span_count
                << ",\"full_work_units\":" << r.full_work_units
                << ",\"sparse_work_units\":" << r.sparse_work_units
                << ",\"work_reduction_x1000\":" << r.work_reduction_x1000
                << ",\"full_ns\":" << r.full_ns
                << ",\"sparse_ns\":" << r.sparse_ns
                << ",\"wall_speedup_x1000\":" << r.wall_speedup_x1000
                << ",\"exact_equal\":" << (r.exact_equal ? "true" : "false")
                << "}";
            if (i + 1 != sparse_results.size()) out << ",";
            out << "\n";
        }
        out << "  ],\n";

        out << "  \"negative_gates\": {"
            << "\"locality_authority_request_status\":" << static_cast<int>(locality_authority_reject)
            << ",\"dirty_incomplete_status\":" << static_cast<int>(dirty_incomplete_reject)
            << ",\"sparse_authority_request_status\":" << static_cast<int>(sparse_authority_reject)
            << "},\n";
        out << "  \"authoritative_state_changed\": false,\n";
        out << "  \"wall_clock_is_observational\": true,\n";
        out << "  \"physical_gpu_claimed\": false\n";
        out << "}\n";
        out.close();

        std::cout << "PASS219B canonical scaling composition benchmark: PASS\n";
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "PASS219B canonical scaling composition benchmark: FAIL: " << e.what() << "\n";
        return 1;
    }
}
