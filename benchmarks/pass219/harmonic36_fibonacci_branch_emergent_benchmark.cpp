#include "hhs_runtime_exact_abi.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <limits>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_sink = 0U;

constexpr std::size_t kLanes = 4U;
constexpr std::size_t kCellsPerLane = 36U;
constexpr std::size_t kTileCells = kLanes * kCellsPerLane;
constexpr std::size_t kFibMaxIndex = 12U;
constexpr std::uint32_t kNoBranch = UINT32_MAX;
constexpr int kSamples = 7;
constexpr std::size_t kCalibrationRepeats = 5U;
constexpr std::uint32_t kAccessRounds = 32768U;
constexpr std::uint32_t kCompositionRounds = 65536U;
constexpr std::uint32_t kEquivalenceRounds = 128U;

const std::array<std::size_t, 6> kScales = {
    144U, 288U, 576U, 1152U, 2304U, 5184U
};

struct SemanticResultLayout {
    std::uint64_t tty_input;
    std::uint64_t tty_output;
    std::uint64_t ptr_word36;
    std::uint64_t ptp_output;
    std::uint32_t tty_service_count;
    std::uint32_t ptr_service_count;
    std::uint32_t ptp_service_count;
    std::uint32_t apr_service_count;
    std::uint32_t uuo_service_count;
    std::uint32_t dispatch_count;
    std::uint32_t final_pc18;
    std::uint8_t queue_cursor;
};

struct CandidateRunLayout {
    SemanticResultLayout result;
    std::uint64_t image_signature36;
    std::uint64_t workload_signature36;
    std::uint32_t working_state_bytes;
    std::uint32_t resource_events;
};

struct ParentSpec {
    std::uint64_t workload_signature36;
    std::uint64_t semantic_signature64;
    std::uint64_t h36_median_ns;
    std::uint64_t linux_median_ns;
    std::uint32_t samples;
    std::uint32_t rounds;
    std::uint32_t h36_working_bytes;
    std::uint32_t linux_working_bytes;
    std::uint32_t h36_resource_events;
    std::uint32_t linux_resource_events;
    std::uint32_t expected_selected_candidate;
    const char *expected_key216;
};

struct ParentState {
    HHSExactPass219H36StackCandidateEvidenceV1 h36{};
    HHSExactPass219H36StackCandidateEvidenceV1 linux{};
    HHSExactPass219H36StackSelectionV1 selection{};
};

struct BranchRef {
    std::uint32_t branch_id = 0U;
    std::uint32_t previous_branch_id = kNoBranch;
    std::uint16_t fib_index = 0U;
    std::uint16_t fib_value = 0U;
    std::uint16_t tile = 0U;
    std::uint8_t lane = 0U;
    std::uint8_t parent_slot = 0U;
    std::uint8_t depth = 0U;
    std::uint8_t reserved = 0U;
    std::uint64_t parent_entry_signature64 = 0U;
    std::uint64_t prior_receipt_signature64 = 0U;
    std::uint64_t receipt_signature64 = 0U;
};

struct DuplicateState {
    HHSExactPass219H36StackSelectionV1 selection{};
    std::uint64_t receipt_signature64 = 0U;
};

struct FibIndex {
    std::array<std::uint32_t, kFibMaxIndex + 2U> offsets{};
    std::vector<std::uint32_t> members;
};

struct ScaleMeasurement {
    std::size_t branches = 0U;
    std::uint64_t duplicate_bytes = 0U;
    std::uint64_t reference_bytes = 0U;

    std::uint64_t fork_duplicate_total_ns = 0U;
    std::uint64_t fork_reference_total_ns = 0U;

    std::uint64_t access_duplicate_total_ns = 0U;
    std::uint64_t access_reference_total_ns = 0U;

    std::uint64_t equivalence_scan_total_ns = 0U;
    std::uint64_t equivalence_bucket_total_ns = 0U;

    std::uint64_t composition_compute_total_ns = 0U;
    std::uint64_t composition_memo_total_ns = 0U;
    std::uint64_t composition_memo_build_total_ns = 0U;

    std::uint64_t composition_break_even_queries = 0U;
};

std::uint64_t mix64(std::uint64_t x) {
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30U)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27U)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31U);
}

std::uint64_t ratio_x1000(std::uint64_t numerator, std::uint64_t denominator) {
    if (denominator == 0U)
        return 0U;
    if (numerator > UINT64_MAX / UINT64_C(1000))
        return (numerator / denominator) * UINT64_C(1000);
    return (numerator * UINT64_C(1000)) / denominator;
}

std::uint64_t ceil_div(std::uint64_t numerator, std::uint64_t denominator) {
    if (denominator == 0U)
        return 0U;
    return numerator / denominator +
           static_cast<std::uint64_t>(numerator % denominator != 0U);
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

std::array<ParentSpec, kLanes> parent_specs() {
    const std::uint32_t h36_working_bytes =
        static_cast<std::uint32_t>(
            sizeof(HHSExactPass219H36VMStateV1) +
            sizeof(HHSExactPass219H36MonitorStateV1) +
            sizeof(HHSExactPass219H36MonitorReceiptV1) * 2U);
    const std::uint32_t linux_working_bytes =
        static_cast<std::uint32_t>(sizeof(CandidateRunLayout));

    return {{
        {
            UINT64_C(3734727431), UINT64_C(4176962402124975431),
            UINT64_C(96531), UINT64_C(873043),
            9U, 32U, 5120U, 100U, 14U, 20U, 1U,
            "5nlPI!0Xj!c(aKeM<IZL2nng*h7f>N)RQyPLzEJG6x(+(w27-U8c/AaCSlDdIwXzdTh1ayAOgIGCzpNKFcHCeTQjeQ>nvDGFbmh<KOu>5arETCTAQzeuT8q!M?IORbb-KUXE1kCW59lt7Paz74<G3NwPCa/n+BUc/WKbPPi(54!!Oor!xH7!gP1o!7IC((j--g5xg<KmJJJSWOii5M-Z9Kx1"
        },
        {
            UINT64_C(4793332410), UINT64_C(6731027650694893003),
            UINT64_C(23033), UINT64_C(106949),
            7U, 8U, h36_working_bytes, linux_working_bytes, 8U, 12U, 1U,
            "tfuz(1iI-X7B1jH408c-6n60BAOrYQQLMA3-*O<L+kOiKL<QZ4)ABrcd3BVdRQ!70bDSzLKw2nl2cNHJzYg>(2H>gcld8e8eKYQ/JDf(pnFIan>AVJbRsT01p/8eHt(L5X?fzNw)5El3?D9RG+U!za81-</XVI-Mni(qEzL?6B+/hBs9vck0O8UPIcKHn1gnXA2ZU7eZ+pS1(u2Ujj!E5+wG"
        },
        {
            UINT64_C(21509979554), UINT64_C(1456447110141201574),
            UINT64_C(23073), UINT64_C(109553),
            7U, 8U, h36_working_bytes, linux_working_bytes, 4U, 10U, 1U,
            "jei)gdf/PEAs9MILOtuHOQXpnUt*Tf47PD?zy3gwy!tZT5)Int*XpA4SKMXYcEMAgr+k>Mtyimln!(PDfX3E?49PUHB2a12t5X2dOb+HT/P6z+x8(124)bX(CZXaW3<-RU(mRMEWy77XtVOU-cU<U?YXV9(aw3hQtZGE-J*6M9Nmc<kBcaIq3JCDgQ48pBMyi(O<qZy1!ag6VRtLP>WnnApX"
        },
        {
            UINT64_C(41886677838), UINT64_C(2318081696571468614),
            UINT64_C(19156), UINT64_C(501),
            7U, 8U, h36_working_bytes, linux_working_bytes, 4U, 4U, 2U,
            "q(IxvVjjUvereKtdppA>uu1yyYAvB3fxjJWuY!QVYp1+UiLu9IdfM+rk1m/L7bbkCTUP3ij1nlJiPvfoK)n34B1t!JNsJC>Plr96YIz*ryA9EJ(RHPeJ?bZJgvj77NPrdCO6r2Sr!WI/T!GSFi!jWlIQCPctCXujdyOXett3<ojTipoRPYVdO*+tNp4c/vTx3H8o1N3wiforBk5--61?!Q76"
        }
    }};
}

void prepare_parent(const ParentSpec &spec, ParentState &out) {
    if (hhs_exact_pass219_h36_stack_candidate_prepare(
            1U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
            spec.workload_signature36,
            spec.semantic_signature64,
            spec.h36_median_ns,
            spec.samples,
            spec.rounds,
            spec.h36_working_bytes,
            spec.h36_resource_events,
            1U,
            &out.h36) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_candidate_prepare(
            2U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
            spec.workload_signature36,
            spec.semantic_signature64,
            spec.linux_median_ns,
            spec.samples,
            spec.rounds,
            spec.linux_working_bytes,
            spec.linux_resource_events,
            1U,
            &out.linux) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_select(
            &out.h36, &out.linux, &out.selection) != HHS_EXACT_STATUS_OK ||
        out.selection.selected_candidate_id != spec.expected_selected_candidate ||
        std::strcmp(
            out.selection.selected_vector_key216,
            spec.expected_key216) != 0)
        std::abort();
}

std::array<std::uint16_t, kFibMaxIndex + 1U> fibonacci() {
    std::array<std::uint16_t, kFibMaxIndex + 1U> f{};
    f[0] = 0U;
    f[1] = 1U;
    for (std::size_t i = 2U; i <= kFibMaxIndex; ++i)
        f[i] = static_cast<std::uint16_t>(f[i - 1U] + f[i - 2U]);
    return f;
}

std::array<std::uint16_t, kCellsPerLane> local_fib_indices() {
    std::array<std::uint16_t, kCellsPerLane> out{};
    out[0] = static_cast<std::uint16_t>(kFibMaxIndex);
    for (std::size_t local = 1U; local < kCellsPerLane; ++local) {
        const std::size_t parent = (local - 1U) / 2U;
        const std::uint16_t decrement =
            (local & 1U) != 0U ? 1U : 2U;
        if (out[parent] <= decrement)
            std::abort();
        out[local] =
            static_cast<std::uint16_t>(out[parent] - decrement);
    }
    return out;
}

std::uint64_t branch_receipt_signature(const BranchRef &ref) {
    std::uint64_t s = mix64(
        ref.parent_entry_signature64 ^
        ref.prior_receipt_signature64 ^
        (static_cast<std::uint64_t>(ref.branch_id) << 17U) ^
        static_cast<std::uint64_t>(ref.previous_branch_id));
    s = mix64(
        s ^
        (static_cast<std::uint64_t>(ref.fib_index) << 52U) ^
        (static_cast<std::uint64_t>(ref.fib_value) << 32U) ^
        (static_cast<std::uint64_t>(ref.tile) << 16U) ^
        (static_cast<std::uint64_t>(ref.lane) << 8U) ^
        static_cast<std::uint64_t>(ref.depth));
    return s == 0U ? UINT64_C(1) : s;
}

std::uint64_t composition_signature(
    const BranchRef &ref,
    std::uint8_t target_lane
) {
    std::uint64_t s = mix64(
        ref.receipt_signature64 ^
        ref.parent_entry_signature64 ^
        (static_cast<std::uint64_t>(ref.lane) << 56U) ^
        (static_cast<std::uint64_t>(target_lane) << 48U) ^
        static_cast<std::uint64_t>(ref.branch_id));
    s = mix64(
        s ^
        (static_cast<std::uint64_t>(ref.fib_index) << 40U) ^
        static_cast<std::uint64_t>(ref.previous_branch_id));
    return s == 0U ? UINT64_C(1) : s;
}

std::vector<BranchRef> build_branches(
    std::size_t branch_count,
    const HHSExactPass219H36StackCacheV1 &cache
) {
    if (branch_count == 0U || branch_count % kTileCells != 0U)
        std::abort();

    const auto fib = fibonacci();
    const auto fib_indices = local_fib_indices();
    std::vector<BranchRef> branches(branch_count);

    for (std::size_t id = 0U; id < branch_count; ++id) {
        const std::size_t tile = id / kTileCells;
        const std::size_t in_tile = id % kTileCells;
        const std::size_t lane = in_tile / kCellsPerLane;
        const std::size_t local = in_tile % kCellsPerLane;

        BranchRef &ref = branches[id];
        ref.branch_id = static_cast<std::uint32_t>(id);
        ref.tile = static_cast<std::uint16_t>(tile);
        ref.lane = static_cast<std::uint8_t>(lane);
        ref.parent_slot = static_cast<std::uint8_t>(lane);
        ref.fib_index = fib_indices[local];
        ref.fib_value = fib[ref.fib_index];
        ref.parent_entry_signature64 =
            cache.entries[lane].entry_signature64;

        if (local == 0U) {
            ref.previous_branch_id = kNoBranch;
            ref.depth = 0U;
            ref.prior_receipt_signature64 =
                ref.parent_entry_signature64;
        } else {
            const std::size_t parent_local = (local - 1U) / 2U;
            const std::size_t previous =
                tile * kTileCells +
                lane * kCellsPerLane +
                parent_local;
            ref.previous_branch_id =
                static_cast<std::uint32_t>(previous);
            ref.depth =
                static_cast<std::uint8_t>(
                    branches[previous].depth + 1U);
            ref.prior_receipt_signature64 =
                branches[previous].receipt_signature64;
        }

        ref.receipt_signature64 = branch_receipt_signature(ref);
    }

    return branches;
}

std::vector<DuplicateState> build_duplicates(
    const std::vector<BranchRef> &branches,
    const std::array<ParentState, kLanes> &parents
) {
    std::vector<DuplicateState> duplicated(branches.size());
    for (std::size_t i = 0U; i < branches.size(); ++i) {
        const BranchRef &ref = branches[i];
        duplicated[i].selection =
            parents[ref.parent_slot].selection;
        duplicated[i].receipt_signature64 =
            ref.receipt_signature64;
    }
    return duplicated;
}

FibIndex build_fib_index(const std::vector<BranchRef> &branches) {
    FibIndex index{};
    std::array<std::uint32_t, kFibMaxIndex + 1U> counts{};

    for (const auto &ref : branches) {
        if (ref.fib_index > kFibMaxIndex)
            std::abort();
        ++counts[ref.fib_index];
    }

    std::uint32_t cursor = 0U;
    for (std::size_t i = 0U; i <= kFibMaxIndex; ++i) {
        index.offsets[i] = cursor;
        cursor += counts[i];
    }
    index.offsets[kFibMaxIndex + 1U] = cursor;
    if (cursor != branches.size())
        std::abort();

    index.members.resize(branches.size());
    auto next = index.offsets;
    for (std::size_t i = 0U; i < branches.size(); ++i) {
        const std::uint16_t fi = branches[i].fib_index;
        index.members[next[fi]++] = static_cast<std::uint32_t>(i);
    }
    return index;
}

std::vector<std::array<std::uint64_t, kLanes>> build_composition_memo(
    const std::vector<BranchRef> &branches
) {
    std::vector<std::array<std::uint64_t, kLanes>> memo(branches.size());
    for (std::size_t i = 0U; i < branches.size(); ++i) {
        for (std::uint8_t target = 0U; target < kLanes; ++target)
            memo[i][target] =
                composition_signature(branches[i], target);
    }
    return memo;
}

void validate_geometry(
    const std::vector<BranchRef> &branches,
    const HHSExactPass219H36StackCacheV1 &cache
) {
    const auto fib = fibonacci();
    for (std::size_t i = 0U; i < branches.size(); ++i) {
        const BranchRef &ref = branches[i];
        if (ref.branch_id != i ||
            ref.lane >= kLanes ||
            ref.parent_slot != ref.lane ||
            ref.fib_value != fib[ref.fib_index] ||
            cache.entries[ref.parent_slot].entry_signature64 !=
                ref.parent_entry_signature64 ||
            branch_receipt_signature(ref) !=
                ref.receipt_signature64)
            std::abort();

        if (ref.previous_branch_id == kNoBranch) {
            if (ref.depth != 0U ||
                ref.prior_receipt_signature64 !=
                    ref.parent_entry_signature64)
                std::abort();
        } else {
            if (ref.previous_branch_id >= i)
                std::abort();
            const BranchRef &previous =
                branches[ref.previous_branch_id];
            if (previous.lane != ref.lane ||
                previous.tile != ref.tile ||
                ref.depth !=
                    static_cast<std::uint8_t>(previous.depth + 1U) ||
                ref.prior_receipt_signature64 !=
                    previous.receipt_signature64)
                std::abort();
        }

        for (std::uint8_t target = 0U; target < kLanes; ++target) {
            const std::uint64_t a =
                composition_signature(ref, target);
            const std::uint64_t b =
                composition_signature(ref, target);
            if (a == 0U || a != b)
                std::abort();
        }
    }

    for (std::size_t tile = 0U;
         tile < branches.size() / kTileCells;
         ++tile) {
        for (std::size_t lane = 0U; lane < kLanes; ++lane) {
            for (std::size_t parent = 0U;
                 parent < kCellsPerLane;
                 ++parent) {
                const std::size_t left = parent * 2U + 1U;
                const std::size_t right = parent * 2U + 2U;
                if (right >= kCellsPerLane)
                    continue;
                const std::size_t base =
                    tile * kTileCells + lane * kCellsPerLane;
                const BranchRef &p = branches[base + parent];
                const BranchRef &l = branches[base + left];
                const BranchRef &r = branches[base + right];
                if (p.fib_value !=
                        static_cast<std::uint16_t>(
                            l.fib_value + r.fib_value) ||
                    l.previous_branch_id != base + parent ||
                    r.previous_branch_id != base + parent)
                    std::abort();
            }
        }
    }
}

void validate_equivalence(
    const std::vector<BranchRef> &branches,
    const FibIndex &index
) {
    for (std::uint16_t fi = 0U; fi <= kFibMaxIndex; ++fi) {
        std::uint64_t scan = 0U;
        std::uint64_t bucket = 0U;

        for (std::size_t i = 0U; i < branches.size(); ++i) {
            if (branches[i].fib_index == fi)
                scan ^= branches[i].receipt_signature64;
        }

        for (std::uint32_t p = index.offsets[fi];
             p < index.offsets[fi + 1U];
             ++p) {
            const std::size_t i = index.members[p];
            bucket ^= branches[i].receipt_signature64;
        }

        if (scan != bucket)
            std::abort();
    }
}

std::size_t access_index(
    std::uint32_t round,
    std::size_t branch_count,
    std::size_t repeat
) {
    const std::uint64_t mixed =
        static_cast<std::uint64_t>(round) * UINT64_C(2654435761) +
        static_cast<std::uint64_t>(repeat) * UINT64_C(40503);
    return static_cast<std::size_t>(mixed % branch_count);
}

std::uint64_t duplicate_access(
    const std::vector<DuplicateState> &duplicated,
    std::uint32_t rounds,
    std::size_t repeat
) {
    std::uint64_t checksum = 0U;
    for (std::uint32_t i = 0U; i < rounds; ++i) {
        const std::size_t index =
            access_index(i, duplicated.size(), repeat);
        const DuplicateState &d = duplicated[index];
        checksum ^= d.selection.semantic_result_signature64;
        checksum ^= d.selection.speedup_x1000;
        checksum ^= d.receipt_signature64;
        checksum ^= static_cast<std::uint8_t>(
            d.selection.selected_vector_key216[
                index % HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]);
    }
    return checksum;
}

std::uint64_t reference_access(
    const std::vector<BranchRef> &branches,
    const std::array<ParentState, kLanes> &parents,
    std::uint32_t rounds,
    std::size_t repeat
) {
    std::uint64_t checksum = 0U;
    for (std::uint32_t i = 0U; i < rounds; ++i) {
        const std::size_t index =
            access_index(i, branches.size(), repeat);
        const BranchRef &ref = branches[index];
        const auto &selection =
            parents[ref.parent_slot].selection;
        checksum ^= selection.semantic_result_signature64;
        checksum ^= selection.speedup_x1000;
        checksum ^= ref.receipt_signature64;
        checksum ^= static_cast<std::uint8_t>(
            selection.selected_vector_key216[
                index % HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]);
    }
    return checksum;
}

std::uint64_t equivalence_scan(
    const std::vector<BranchRef> &branches,
    std::uint16_t fi
) {
    std::uint64_t checksum = 0U;
    for (const auto &ref : branches) {
        if (ref.fib_index == fi)
            checksum ^= ref.receipt_signature64;
    }
    return checksum;
}

std::uint64_t equivalence_bucket(
    const std::vector<BranchRef> &branches,
    const FibIndex &index,
    std::uint16_t fi
) {
    std::uint64_t checksum = 0U;
    for (std::uint32_t p = index.offsets[fi];
         p < index.offsets[fi + 1U];
         ++p) {
        checksum ^=
            branches[index.members[p]].receipt_signature64;
    }
    return checksum;
}

ScaleMeasurement measure_scale(
    std::size_t branch_count,
    const HHSExactPass219H36StackCacheV1 &cache,
    const std::array<ParentState, kLanes> &parents
) {
    ScaleMeasurement out{};
    out.branches = branch_count;

    const auto branches = build_branches(branch_count, cache);
    const auto duplicated = build_duplicates(branches, parents);
    const auto fib_index = build_fib_index(branches);
    const auto memo = build_composition_memo(branches);

    validate_geometry(branches, cache);
    validate_equivalence(branches, fib_index);

    for (std::size_t i = 0U; i < branches.size(); ++i) {
        for (std::uint8_t target = 0U; target < kLanes; ++target) {
            if (memo[i][target] !=
                composition_signature(branches[i], target))
                std::abort();
        }
    }

    out.duplicate_bytes =
        static_cast<std::uint64_t>(
            duplicated.size() * sizeof(DuplicateState));
    out.reference_bytes =
        static_cast<std::uint64_t>(
            branches.size() * sizeof(BranchRef) +
            fib_index.members.size() * sizeof(std::uint32_t) +
            sizeof(fib_index.offsets) +
            parents.size() *
                sizeof(HHSExactPass219H36StackSelectionV1));

    for (std::size_t repeat = 0U;
         repeat < kCalibrationRepeats;
         ++repeat) {
        const auto duplicate_fork = [&]() {
            std::vector<DuplicateState> work(branch_count);
            std::uint64_t checksum = 0U;
            for (std::size_t i = 0U; i < branch_count; ++i) {
                const BranchRef &ref = branches[i];
                work[i].selection =
                    parents[ref.parent_slot].selection;
                work[i].receipt_signature64 =
                    ref.receipt_signature64;
                checksum ^=
                    work[i].selection.semantic_result_signature64;
                checksum ^= work[i].receipt_signature64;
                checksum ^= static_cast<std::uint8_t>(
                    work[i].selection.selected_vector_key216[
                        i % HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]);
            }
            g_sink ^= checksum;
        };

        const auto reference_fork = [&]() {
            const auto work = build_branches(branch_count, cache);
            std::uint64_t checksum = 0U;
            for (const auto &ref : work) {
                checksum ^= ref.parent_entry_signature64;
                checksum ^= ref.receipt_signature64;
                checksum ^= ref.fib_value;
            }
            g_sink ^= checksum;
        };

        const auto duplicate_read = [&]() {
            g_sink ^= duplicate_access(
                duplicated, kAccessRounds, repeat);
        };
        const auto reference_read = [&]() {
            g_sink ^= reference_access(
                branches, parents, kAccessRounds, repeat);
        };

        const auto scan = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U;
                 i < kEquivalenceRounds;
                 ++i) {
                const std::size_t probe =
                    access_index(i, branch_count, repeat);
                checksum ^= equivalence_scan(
                    branches, branches[probe].fib_index);
            }
            g_sink ^= checksum;
        };

        const auto bucket = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U;
                 i < kEquivalenceRounds;
                 ++i) {
                const std::size_t probe =
                    access_index(i, branch_count, repeat);
                checksum ^= equivalence_bucket(
                    branches,
                    fib_index,
                    branches[probe].fib_index);
            }
            g_sink ^= checksum;
        };

        const auto composition_compute = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U;
                 i < kCompositionRounds;
                 ++i) {
                const std::size_t probe =
                    access_index(i, branch_count, repeat);
                const std::uint8_t target =
                    static_cast<std::uint8_t>(
                        (i + repeat) % kLanes);
                checksum ^= composition_signature(
                    branches[probe], target);
            }
            g_sink ^= checksum;
        };

        const auto composition_memo = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U;
                 i < kCompositionRounds;
                 ++i) {
                const std::size_t probe =
                    access_index(i, branch_count, repeat);
                const std::uint8_t target =
                    static_cast<std::uint8_t>(
                        (i + repeat) % kLanes);
                checksum ^= memo[probe][target];
            }
            g_sink ^= checksum;
        };

        const auto composition_memo_build = [&]() {
            const auto built = build_composition_memo(branches);
            std::uint64_t checksum = 0U;
            for (std::size_t i = 0U; i < built.size(); ++i)
                checksum ^= built[i][i % kLanes];
            g_sink ^= checksum;
        };

        if ((repeat & 1U) == 0U) {
            out.fork_duplicate_total_ns += median_ns(duplicate_fork);
            out.fork_reference_total_ns += median_ns(reference_fork);
            out.access_duplicate_total_ns += median_ns(duplicate_read);
            out.access_reference_total_ns += median_ns(reference_read);
            out.equivalence_scan_total_ns += median_ns(scan);
            out.equivalence_bucket_total_ns += median_ns(bucket);
            out.composition_compute_total_ns +=
                median_ns(composition_compute);
            out.composition_memo_total_ns +=
                median_ns(composition_memo);
            out.composition_memo_build_total_ns +=
                median_ns(composition_memo_build);
        } else {
            out.composition_memo_build_total_ns +=
                median_ns(composition_memo_build);
            out.composition_memo_total_ns +=
                median_ns(composition_memo);
            out.composition_compute_total_ns +=
                median_ns(composition_compute);
            out.equivalence_bucket_total_ns += median_ns(bucket);
            out.equivalence_scan_total_ns += median_ns(scan);
            out.access_reference_total_ns += median_ns(reference_read);
            out.access_duplicate_total_ns += median_ns(duplicate_read);
            out.fork_reference_total_ns += median_ns(reference_fork);
            out.fork_duplicate_total_ns += median_ns(duplicate_fork);
        }
    }

    if (out.composition_compute_total_ns >
        out.composition_memo_total_ns) {
        const std::uint64_t delta =
            out.composition_compute_total_ns -
            out.composition_memo_total_ns;
        const std::uint64_t measured_queries =
            static_cast<std::uint64_t>(kCompositionRounds) *
            kCalibrationRepeats;
        out.composition_break_even_queries =
            ceil_div(
                out.composition_memo_build_total_ns *
                    measured_queries,
                delta);
    }

    return out;
}

std::size_t first_winner_scale(
    const std::vector<ScaleMeasurement> &rows,
    std::uint64_t ScaleMeasurement::*left,
    std::uint64_t ScaleMeasurement::*right
) {
    for (const auto &row : rows) {
        if (row.*right < row.*left)
            return row.branches;
    }
    return 0U;
}

} // namespace

int main(int argc, char **argv) {
#if !defined(__linux__) || !defined(__x86_64__)
    std::cerr << "benchmark requires Linux x86_64\n";
    return 2;
#else
    const auto specs = parent_specs();
    std::array<ParentState, kLanes> parents{};
    HHSExactPass219H36StackCacheV1 cache{};

    if (hhs_exact_pass219_h36_stack_cache_init(&cache) !=
        HHS_EXACT_STATUS_OK)
        return 3;

    for (std::size_t i = 0U; i < kLanes; ++i) {
        prepare_parent(specs[i], parents[i]);
        if (hhs_exact_pass219_h36_stack_cache_store(
                &cache, &parents[i].selection) != HHS_EXACT_STATUS_OK)
            return 4;
    }

    if (cache.entry_count != 4U ||
        cache.next_sequence != UINT64_C(5) ||
        hhs_exact_pass219_h36_stack_cache_validate(&cache) !=
            HHS_EXACT_STATUS_OK)
        return 5;

    const HHSExactPass219H36StackCacheV1 frozen_before = cache;

    std::vector<ScaleMeasurement> rows;
    rows.reserve(kScales.size());
    for (const std::size_t scale : kScales)
        rows.push_back(measure_scale(scale, cache, parents));

    if (std::memcmp(&cache, &frozen_before, sizeof(cache)) != 0)
        return 6;

    const std::size_t fork_ref_crossover =
        first_winner_scale(
            rows,
            &ScaleMeasurement::fork_duplicate_total_ns,
            &ScaleMeasurement::fork_reference_total_ns);
    const std::size_t access_ref_crossover =
        first_winner_scale(
            rows,
            &ScaleMeasurement::access_duplicate_total_ns,
            &ScaleMeasurement::access_reference_total_ns);
    const std::size_t bucket_crossover =
        first_winner_scale(
            rows,
            &ScaleMeasurement::equivalence_scan_total_ns,
            &ScaleMeasurement::equivalence_bucket_total_ns);
    const std::size_t memo_crossover =
        first_winner_scale(
            rows,
            &ScaleMeasurement::composition_compute_total_ns,
            &ScaleMeasurement::composition_memo_total_ns);

    std::ostream *out = &std::cout;
    std::ofstream file;
    if (argc > 1) {
        file.open(argv[1], std::ios::out | std::ios::trunc);
        if (!file)
            return 7;
        out = &file;
    }

    *out
        << "{\n"
        << "  \"schema\": \"HHS_PASS219_H36_FIBONACCI_BRANCH_EMERGENT_BENEFITS_V1\",\n"
        << "  \"platform\": {\"linux\": true, \"x86_64\": true, "
        << "\"samples\": " << kSamples << ", "
        << "\"calibration_repeats\": " << kCalibrationRepeats << ", "
        << "\"access_rounds\": " << kAccessRounds << ", "
        << "\"composition_rounds\": " << kCompositionRounds << ", "
        << "\"equivalence_rounds\": " << kEquivalenceRounds << "},\n"
        << "  \"frozen_parent\": {\"entries\": 4, "
        << "\"next_sequence\": " << cache.next_sequence << ", "
        << "\"unchanged_after_all_sweeps\": true},\n"
        << "  \"scales\": [\n";

    for (std::size_t i = 0U; i < rows.size(); ++i) {
        const auto &r = rows[i];
        *out
            << "    {\n"
            << "      \"branches\": " << r.branches << ",\n"
            << "      \"tiles144\": "
            << (r.branches / kTileCells) << ",\n"
            << "      \"memory\": {"
            << "\"duplicate_bytes\": " << r.duplicate_bytes << ", "
            << "\"reference_bytes\": " << r.reference_bytes << ", "
            << "\"duplicate_vs_reference_x1000\": "
            << ratio_x1000(r.duplicate_bytes, r.reference_bytes)
            << "},\n"
            << "      \"fork_creation\": {"
            << "\"duplicate_total_ns\": "
            << r.fork_duplicate_total_ns << ", "
            << "\"reference_total_ns\": "
            << r.fork_reference_total_ns << ", "
            << "\"reference_speedup_x1000\": "
            << ratio_x1000(
                   r.fork_duplicate_total_ns,
                   r.fork_reference_total_ns) << ", "
            << "\"winner\": \""
            << (r.fork_reference_total_ns <
                        r.fork_duplicate_total_ns
                    ? "REFERENCE"
                    : "DUPLICATE")
            << "\"},\n"
            << "      \"random_access\": {"
            << "\"duplicate_total_ns\": "
            << r.access_duplicate_total_ns << ", "
            << "\"reference_total_ns\": "
            << r.access_reference_total_ns << ", "
            << "\"reference_speedup_x1000\": "
            << ratio_x1000(
                   r.access_duplicate_total_ns,
                   r.access_reference_total_ns) << ", "
            << "\"winner\": \""
            << (r.access_reference_total_ns <
                        r.access_duplicate_total_ns
                    ? "REFERENCE"
                    : "DUPLICATE")
            << "\"},\n"
            << "      \"equivalence\": {"
            << "\"full_scan_total_ns\": "
            << r.equivalence_scan_total_ns << ", "
            << "\"fib_bucket_total_ns\": "
            << r.equivalence_bucket_total_ns << ", "
            << "\"bucket_speedup_x1000\": "
            << ratio_x1000(
                   r.equivalence_scan_total_ns,
                   r.equivalence_bucket_total_ns) << ", "
            << "\"winner\": \""
            << (r.equivalence_bucket_total_ns <
                        r.equivalence_scan_total_ns
                    ? "FIB_BUCKET"
                    : "FULL_SCAN")
            << "\"},\n"
            << "      \"composition_receipts\": {"
            << "\"compute_total_ns\": "
            << r.composition_compute_total_ns << ", "
            << "\"memo_total_ns\": "
            << r.composition_memo_total_ns << ", "
            << "\"memo_build_total_ns\": "
            << r.composition_memo_build_total_ns << ", "
            << "\"memo_query_speedup_x1000\": "
            << ratio_x1000(
                   r.composition_compute_total_ns,
                   r.composition_memo_total_ns) << ", "
            << "\"break_even_queries\": "
            << r.composition_break_even_queries << ", "
            << "\"winner\": \""
            << (r.composition_memo_total_ns <
                        r.composition_compute_total_ns
                    ? "MEMOIZED"
                    : "COMPUTED")
            << "\"}\n"
            << "    }"
            << (i + 1U == rows.size() ? "\n" : ",\n");
    }

    *out
        << "  ],\n"
        << "  \"crossovers\": {\n"
        << "    \"reference_fork_creation_first_win_branches\": "
        << fork_ref_crossover << ",\n"
        << "    \"reference_random_access_first_win_branches\": "
        << access_ref_crossover << ",\n"
        << "    \"fibonacci_bucket_first_win_branches\": "
        << bucket_crossover << ",\n"
        << "    \"composition_memo_first_win_branches\": "
        << memo_crossover << "\n"
        << "  },\n"
        << "  \"correctness\": {\n"
        << "    \"fibonacci_additive_division_all_tiles\": true,\n"
        << "    \"equivalence_scan_equals_bucket\": true,\n"
        << "    \"composition_memo_equals_recomputed_receipt\": true,\n"
        << "    \"all_branch_receipts_deterministic\": true,\n"
        << "    \"frozen_parent_state_unchanged\": true\n"
        << "  },\n"
        << "  \"authority\": {\n"
        << "    \"candidate_benchmark_only\": true,\n"
        << "    \"vm81_mutation\": false,\n"
        << "    \"hash72_mint\": false,\n"
        << "    \"hash216_persistence\": false,\n"
        << "    \"canonical_persistence\": false,\n"
        << "    \"floating_point\": false\n"
        << "  },\n"
        << "  \"authoritative_state_changed\": false\n"
        << "}\n";

    return 0;
#endif
}
