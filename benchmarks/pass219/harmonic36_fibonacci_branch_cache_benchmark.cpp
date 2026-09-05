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

constexpr std::size_t kLanes = 4U;
constexpr std::size_t kCellsPerLane = 36U;
constexpr std::size_t kBranches = kLanes * kCellsPerLane;
constexpr std::size_t kFibMaxIndex = 12U;
constexpr std::uint16_t kNoBranch = UINT16_C(0xFFFF);
constexpr int kSamples = 11;
constexpr std::size_t kCalibrationRepeats = 5U;
constexpr std::uint32_t kLocalRounds = 8192U;
constexpr std::uint32_t kEquivalenceRounds = 1024U;

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
    const char *name;
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
    std::uint16_t word144 = 0U;
    std::uint16_t previous_word144 = kNoBranch;
    std::uint16_t fib_index = 0U;
    std::uint16_t fib_value = 0U;
    std::uint8_t lane = 0U;
    std::uint8_t parent_slot = 0U;
    std::uint8_t depth = 0U;
    std::uint8_t reserved = 0U;
    std::uint64_t parent_entry_signature64 = 0U;
    std::uint64_t prior_receipt_signature64 = 0U;
    std::uint64_t receipt_signature64 = 0U;
};

struct FibIndex {
    std::array<std::uint16_t, kFibMaxIndex + 2U> offsets{};
    std::array<std::uint16_t, kBranches> members{};
};

struct TimingTotals {
    std::uint64_t baseline_cache_total_ns = 0U;
    std::uint64_t direct_ref_total_ns = 0U;
    std::uint64_t fib_bucket_ref_total_ns = 0U;
    std::uint64_t equivalence_scan_total_ns = 0U;
    std::uint64_t equivalence_bucket_total_ns = 0U;
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
            "FULL_MONITOR",
            UINT64_C(3734727431),
            UINT64_C(4176962402124975431),
            UINT64_C(96531),
            UINT64_C(873043),
            9U, 32U, 5120U, 100U, 14U, 20U, 1U,
            "5nlPI!0Xj!c(aKeM<IZL2nng*h7f>N)RQyPLzEJG6x(+(w27-U8c/AaCSlDdIwXzdTh1ayAOgIGCzpNKFcHCeTQjeQ>nvDGFbmh<KOu>5arETCTAQzeuT8q!M?IORbb-KUXE1kCW59lt7Paz74<G3NwPCa/n+BUc/WKbPPi(54!!Oor!xH7!gP1o!7IC((j--g5xg<KmJJJSWOii5M-Z9Kx1"
        },
        {
            "CONSOLE_FOCUSED",
            UINT64_C(4793332410),
            UINT64_C(6731027650694893003),
            UINT64_C(23033),
            UINT64_C(106949),
            7U, 8U, h36_working_bytes, linux_working_bytes, 8U, 12U, 1U,
            "tfuz(1iI-X7B1jH408c-6n60BAOrYQQLMA3-*O<L+kOiKL<QZ4)ABrcd3BVdRQ!70bDSzLKw2nl2cNHJzYg>(2H>gcld8e8eKYQ/JDf(pnFIan>AVJbRsT01p/8eHt(L5X?fzNw)5El3?D9RG+U!za81-</XVI-Mni(qEzL?6B+/hBs9vck0O8UPIcKHn1gnXA2ZU7eZ+pS1(u2Ujj!E5+wG"
        },
        {
            "BINARY_IO_FOCUSED",
            UINT64_C(21509979554),
            UINT64_C(1456447110141201574),
            UINT64_C(23073),
            UINT64_C(109553),
            7U, 8U, h36_working_bytes, linux_working_bytes, 4U, 10U, 1U,
            "jei)gdf/PEAs9MILOtuHOQXpnUt*Tf47PD?zy3gwy!tZT5)Int*XpA4SKMXYcEMAgr+k>Mtyimln!(PDfX3E?49PUHB2a12t5X2dOb+HT/P6z+x8(124)bX(CZXaW3<-RU(mRMEWy77XtVOU-cU<U?YXV9(aw3hQtZGE-J*6M9Nmc<kBcaIq3JCDgQ48pBMyi(O<qZy1!ag6VRtLP>WnnApX"
        },
        {
            "MONITOR_CONTROL_FOCUSED",
            UINT64_C(41886677838),
            UINT64_C(2318081696571468614),
            UINT64_C(19156),
            UINT64_C(501),
            7U, 8U, h36_working_bytes, linux_working_bytes, 4U, 4U, 2U,
            "q(IxvVjjUvereKtdppA>uu1yyYAvB3fxjJWuY!QVYp1+UiLu9IdfM+rk1m/L7bbkCTUP3ij1nlJiPvfoK)n34B1t!JNsJC>Plr96YIz*ryA9EJ(RHPeJ?bZJgvj77NPrdCO6r2Sr!WI/T!GSFi!jWlIQCPctCXujdyOXett3<ojTipoRPYVdO*+tNp4c/vTx3H8o1N3wiforBk5--61?!Q76"
        }
    }};
}

void prepare_parent(
    const ParentSpec &spec,
    ParentState &out
) {
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

std::uint64_t branch_receipt_signature(const BranchRef &ref) {
    std::uint64_t s = mix64(
        ref.parent_entry_signature64 ^
        ref.prior_receipt_signature64 ^
        (static_cast<std::uint64_t>(ref.word144) << 48U) ^
        (static_cast<std::uint64_t>(ref.previous_word144) << 32U));
    s = mix64(
        s ^
        (static_cast<std::uint64_t>(ref.fib_index) << 48U) ^
        (static_cast<std::uint64_t>(ref.fib_value) << 24U) ^
        (static_cast<std::uint64_t>(ref.lane) << 16U) ^
        (static_cast<std::uint64_t>(ref.parent_slot) << 8U) ^
        static_cast<std::uint64_t>(ref.depth));
    return s == 0U ? UINT64_C(1) : s;
}

std::uint64_t composition_receipt_signature(
    const BranchRef &ref,
    std::uint8_t target_lane
) {
    std::uint64_t s = mix64(
        ref.receipt_signature64 ^
        ref.parent_entry_signature64 ^
        (static_cast<std::uint64_t>(ref.lane) << 56U) ^
        (static_cast<std::uint64_t>(target_lane) << 48U) ^
        static_cast<std::uint64_t>(ref.word144));
    return s == 0U ? UINT64_C(1) : s;
}

std::array<BranchRef, kBranches> build_branches(
    const HHSExactPass219H36StackCacheV1 &cache
) {
    const auto fib = fibonacci();
    std::array<BranchRef, kBranches> branches{};

    for (std::size_t lane = 0U; lane < kLanes; ++lane) {
        for (std::size_t local = 0U; local < kCellsPerLane; ++local) {
            const std::size_t global = lane * kCellsPerLane + local;
            BranchRef &ref = branches[global];
            ref.word144 = static_cast<std::uint16_t>(global);
            ref.lane = static_cast<std::uint8_t>(lane);
            ref.parent_slot = static_cast<std::uint8_t>(lane);
            ref.parent_entry_signature64 = cache.entries[lane].entry_signature64;

            if (local == 0U) {
                ref.previous_word144 = kNoBranch;
                ref.fib_index = static_cast<std::uint16_t>(kFibMaxIndex);
                ref.depth = 0U;
                ref.prior_receipt_signature64 =
                    ref.parent_entry_signature64;
            } else {
                const std::size_t parent_local = (local - 1U) / 2U;
                const std::size_t parent_global =
                    lane * kCellsPerLane + parent_local;
                const BranchRef &parent = branches[parent_global];
                ref.previous_word144 =
                    static_cast<std::uint16_t>(parent_global);
                ref.depth = static_cast<std::uint8_t>(parent.depth + 1U);
                const std::uint16_t decrement =
                    (local & 1U) != 0U ? 1U : 2U;
                if (parent.fib_index <= decrement)
                    std::abort();
                ref.fib_index = static_cast<std::uint16_t>(
                    parent.fib_index - decrement);
                ref.prior_receipt_signature64 =
                    parent.receipt_signature64;
            }

            ref.fib_value = fib[ref.fib_index];
            ref.receipt_signature64 = branch_receipt_signature(ref);
        }
    }
    return branches;
}

FibIndex build_fib_index(
    const std::array<BranchRef, kBranches> &branches
) {
    FibIndex index{};
    std::array<std::uint16_t, kFibMaxIndex + 1U> counts{};

    for (const auto &ref : branches) {
        if (ref.fib_index > kFibMaxIndex)
            std::abort();
        counts[ref.fib_index] =
            static_cast<std::uint16_t>(counts[ref.fib_index] + 1U);
    }

    std::uint16_t cursor = 0U;
    for (std::size_t i = 0U; i <= kFibMaxIndex; ++i) {
        index.offsets[i] = cursor;
        cursor = static_cast<std::uint16_t>(cursor + counts[i]);
    }
    index.offsets[kFibMaxIndex + 1U] = cursor;
    if (cursor != kBranches)
        std::abort();

    auto next = index.offsets;
    for (std::size_t i = 0U; i < branches.size(); ++i) {
        const std::uint16_t fib_index = branches[i].fib_index;
        index.members[next[fib_index]++] = static_cast<std::uint16_t>(i);
    }
    return index;
}

bool validate_branch(
    const HHSExactPass219H36StackCacheV1 &cache,
    const std::array<BranchRef, kBranches> &branches,
    std::size_t branch_id
) {
    if (branch_id >= branches.size())
        return false;
    const BranchRef &ref = branches[branch_id];
    if (ref.word144 != branch_id ||
        ref.lane >= kLanes ||
        ref.parent_slot != ref.lane ||
        cache.entries[ref.parent_slot].occupied != 1U ||
        cache.entries[ref.parent_slot].entry_signature64 !=
            ref.parent_entry_signature64 ||
        branch_receipt_signature(ref) != ref.receipt_signature64)
        return false;

    if (ref.previous_word144 == kNoBranch) {
        if (branch_id != static_cast<std::size_t>(ref.lane) * kCellsPerLane ||
            ref.depth != 0U ||
            ref.prior_receipt_signature64 !=
                ref.parent_entry_signature64)
            return false;
    } else {
        if (ref.previous_word144 >= branch_id)
            return false;
        const BranchRef &previous = branches[ref.previous_word144];
        if (previous.lane != ref.lane ||
            ref.prior_receipt_signature64 !=
                previous.receipt_signature64 ||
            ref.depth != static_cast<std::uint8_t>(previous.depth + 1U))
            return false;
    }
    return true;
}

bool reverse_to_root(
    const std::array<BranchRef, kBranches> &branches,
    std::size_t branch_id,
    std::uint8_t expected_lane
) {
    for (std::size_t steps = 0U; steps < kCellsPerLane; ++steps) {
        const BranchRef &ref = branches[branch_id];
        if (ref.lane != expected_lane)
            return false;
        if (ref.previous_word144 == kNoBranch)
            return branch_id ==
                static_cast<std::size_t>(expected_lane) * kCellsPerLane;
        branch_id = ref.previous_word144;
    }
    return false;
}

void prove_fibonacci_additive_division(
    const std::array<BranchRef, kBranches> &branches
) {
    for (std::size_t lane = 0U; lane < kLanes; ++lane) {
        for (std::size_t parent = 0U; parent < kCellsPerLane; ++parent) {
            const std::size_t left = parent * 2U + 1U;
            const std::size_t right = parent * 2U + 2U;
            if (right >= kCellsPerLane)
                continue;
            const BranchRef &p =
                branches[lane * kCellsPerLane + parent];
            const BranchRef &l =
                branches[lane * kCellsPerLane + left];
            const BranchRef &r =
                branches[lane * kCellsPerLane + right];
            if (p.fib_value !=
                    static_cast<std::uint16_t>(
                        l.fib_value + r.fib_value) ||
                l.previous_word144 !=
                    lane * kCellsPerLane + parent ||
                r.previous_word144 !=
                    lane * kCellsPerLane + parent)
                std::abort();
        }
    }
}

void prove_all_receipts(
    const HHSExactPass219H36StackCacheV1 &cache,
    const std::array<BranchRef, kBranches> &branches
) {
    for (std::size_t i = 0U; i < branches.size(); ++i) {
        if (!validate_branch(cache, branches, i) ||
            !reverse_to_root(branches, i, branches[i].lane))
            std::abort();
        for (std::uint8_t target_lane = 0U;
             target_lane < kLanes;
             ++target_lane) {
            const std::uint64_t a =
                composition_receipt_signature(branches[i], target_lane);
            const std::uint64_t b =
                composition_receipt_signature(branches[i], target_lane);
            if (a == 0U || a != b)
                std::abort();
        }
    }
    prove_fibonacci_additive_division(branches);
}

std::uint64_t baseline_cache_resolve(
    const HHSExactPass219H36StackCacheV1 &cache,
    const std::array<ParentState, kLanes> &parents,
    const std::array<BranchRef, kBranches> &branches,
    std::size_t branch_id,
    std::uint8_t target_lane
) {
    const BranchRef &ref = branches[branch_id];
    const auto &selection = parents[ref.parent_slot].selection;
    HHSExactPass219H36StackSelectionV1 hit{};
    HHSExactPass219H36StackCacheReceiptV1 receipt{};
    if (hhs_exact_pass219_h36_stack_cache_lookup(
            &cache,
            selection.workload_signature36,
            selection.semantic_result_signature64,
            selection.selected_vector_key216,
            &hit,
            &receipt) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
            &hit, &selection) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_cache_receipt_validate(
            &cache, &receipt) != HHS_EXACT_STATUS_OK ||
        !validate_branch(cache, branches, branch_id))
        std::abort();

    return receipt.replay_signature64 ^
           ref.receipt_signature64 ^
           composition_receipt_signature(ref, target_lane);
}

std::uint64_t direct_ref_resolve(
    const HHSExactPass219H36StackCacheV1 &cache,
    const std::array<BranchRef, kBranches> &branches,
    std::size_t branch_id,
    std::uint8_t target_lane
) {
    const BranchRef &ref = branches[branch_id];
    if (!validate_branch(cache, branches, branch_id))
        std::abort();
    const auto &entry = cache.entries[ref.parent_slot];
    return entry.entry_signature64 ^
           ref.receipt_signature64 ^
           composition_receipt_signature(ref, target_lane) ^
           entry.selection.speedup_x1000 ^
           static_cast<std::uint8_t>(
               entry.selection.selected_vector_key216[
                   branch_id % HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]);
}

std::uint64_t fib_bucket_ref_resolve(
    const HHSExactPass219H36StackCacheV1 &cache,
    const std::array<BranchRef, kBranches> &branches,
    const FibIndex &index,
    std::size_t branch_id,
    std::uint8_t target_lane
) {
    const std::uint16_t fib_index = branches[branch_id].fib_index;
    const std::uint16_t begin = index.offsets[fib_index];
    const std::uint16_t end = index.offsets[fib_index + 1U];
    for (std::uint16_t p = begin; p < end; ++p) {
        if (index.members[p] == branch_id)
            return direct_ref_resolve(
                cache, branches, branch_id, target_lane);
    }
    std::abort();
}

std::uint64_t equivalence_scan(
    const HHSExactPass219H36StackCacheV1 &cache,
    const std::array<BranchRef, kBranches> &branches,
    std::uint16_t fib_index
) {
    std::uint64_t checksum = 0U;
    for (std::size_t i = 0U; i < branches.size(); ++i) {
        if (branches[i].fib_index == fib_index)
            checksum ^= direct_ref_resolve(
                cache,
                branches,
                i,
                static_cast<std::uint8_t>(i % kLanes));
    }
    return checksum;
}

std::uint64_t equivalence_bucket(
    const HHSExactPass219H36StackCacheV1 &cache,
    const std::array<BranchRef, kBranches> &branches,
    const FibIndex &index,
    std::uint16_t fib_index
) {
    std::uint64_t checksum = 0U;
    const std::uint16_t begin = index.offsets[fib_index];
    const std::uint16_t end = index.offsets[fib_index + 1U];
    for (std::uint16_t p = begin; p < end; ++p) {
        const std::size_t i = index.members[p];
        checksum ^= direct_ref_resolve(
            cache,
            branches,
            i,
            static_cast<std::uint8_t>(i % kLanes));
    }
    return checksum;
}

TimingTotals measure(
    const HHSExactPass219H36StackCacheV1 &cache,
    const std::array<ParentState, kLanes> &parents,
    const std::array<BranchRef, kBranches> &branches,
    const FibIndex &index
) {
    TimingTotals totals{};

    for (std::size_t repeat = 0U;
         repeat < kCalibrationRepeats;
         ++repeat) {
        const auto baseline = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U; i < kLocalRounds; ++i) {
                const std::size_t branch_id =
                    (static_cast<std::size_t>(i) * 37U +
                     repeat * 11U) % kBranches;
                const std::uint8_t target_lane =
                    static_cast<std::uint8_t>(
                        (branch_id + repeat) % kLanes);
                checksum ^= baseline_cache_resolve(
                    cache, parents, branches, branch_id, target_lane);
            }
            g_sink ^= checksum;
        };
        const auto direct = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U; i < kLocalRounds; ++i) {
                const std::size_t branch_id =
                    (static_cast<std::size_t>(i) * 37U +
                     repeat * 11U) % kBranches;
                const std::uint8_t target_lane =
                    static_cast<std::uint8_t>(
                        (branch_id + repeat) % kLanes);
                checksum ^= direct_ref_resolve(
                    cache, branches, branch_id, target_lane);
            }
            g_sink ^= checksum;
        };
        const auto bucket = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U; i < kLocalRounds; ++i) {
                const std::size_t branch_id =
                    (static_cast<std::size_t>(i) * 37U +
                     repeat * 11U) % kBranches;
                const std::uint8_t target_lane =
                    static_cast<std::uint8_t>(
                        (branch_id + repeat) % kLanes);
                checksum ^= fib_bucket_ref_resolve(
                    cache, branches, index, branch_id, target_lane);
            }
            g_sink ^= checksum;
        };
        const auto eq_scan = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U; i < kEquivalenceRounds; ++i) {
                const std::size_t branch_id =
                    (static_cast<std::size_t>(i) * 29U +
                     repeat * 7U) % kBranches;
                checksum ^= equivalence_scan(
                    cache, branches, branches[branch_id].fib_index);
            }
            g_sink ^= checksum;
        };
        const auto eq_bucket = [&]() {
            std::uint64_t checksum = 0U;
            for (std::uint32_t i = 0U; i < kEquivalenceRounds; ++i) {
                const std::size_t branch_id =
                    (static_cast<std::size_t>(i) * 29U +
                     repeat * 7U) % kBranches;
                checksum ^= equivalence_bucket(
                    cache,
                    branches,
                    index,
                    branches[branch_id].fib_index);
            }
            g_sink ^= checksum;
        };

        if ((repeat & 1U) == 0U) {
            totals.baseline_cache_total_ns += median_ns(baseline);
            totals.direct_ref_total_ns += median_ns(direct);
            totals.fib_bucket_ref_total_ns += median_ns(bucket);
            totals.equivalence_scan_total_ns += median_ns(eq_scan);
            totals.equivalence_bucket_total_ns += median_ns(eq_bucket);
        } else {
            totals.equivalence_bucket_total_ns += median_ns(eq_bucket);
            totals.equivalence_scan_total_ns += median_ns(eq_scan);
            totals.fib_bucket_ref_total_ns += median_ns(bucket);
            totals.direct_ref_total_ns += median_ns(direct);
            totals.baseline_cache_total_ns += median_ns(baseline);
        }
    }

    return totals;
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

    if (cache.entry_count != kLanes ||
        cache.next_sequence != UINT64_C(5) ||
        hhs_exact_pass219_h36_stack_cache_validate(&cache) !=
            HHS_EXACT_STATUS_OK)
        return 5;

    const auto branches = build_branches(cache);
    const auto index = build_fib_index(branches);
    prove_all_receipts(cache, branches);

    std::size_t composition_receipt_count = 0U;
    for (const auto &ref : branches) {
        for (std::uint8_t target_lane = 0U;
             target_lane < kLanes;
             ++target_lane) {
            if (composition_receipt_signature(ref, target_lane) == 0U)
                return 6;
            ++composition_receipt_count;
        }
    }
    if (composition_receipt_count != kBranches * kLanes)
        return 7;

    const TimingTotals timing =
        measure(cache, parents, branches, index);

    if (timing.baseline_cache_total_ns == 0U ||
        timing.direct_ref_total_ns == 0U ||
        timing.fib_bucket_ref_total_ns == 0U ||
        timing.equivalence_scan_total_ns == 0U ||
        timing.equivalence_bucket_total_ns == 0U)
        return 8;

    const char *best_local = "BASELINE_CACHE";
    std::uint64_t best_local_ns = timing.baseline_cache_total_ns;
    if (timing.direct_ref_total_ns < best_local_ns) {
        best_local = "DIRECT_BRANCH_REF";
        best_local_ns = timing.direct_ref_total_ns;
    }
    if (timing.fib_bucket_ref_total_ns < best_local_ns) {
        best_local = "FIB_BUCKET_BRANCH_REF";
        best_local_ns = timing.fib_bucket_ref_total_ns;
    }

    const char *best_equivalence =
        timing.equivalence_bucket_total_ns <=
                timing.equivalence_scan_total_ns
            ? "FIB_BUCKET"
            : "FULL_SCAN";

    const bool hybrid_selected =
        std::strcmp(best_local, "DIRECT_BRANCH_REF") == 0 &&
        std::strcmp(best_equivalence, "FIB_BUCKET") == 0;
    const char *best_configuration =
        hybrid_selected
            ? "HYBRID_DIRECT_FIB_REFERENCE"
            : best_local;

    const std::uint64_t duplicate_payload_bytes =
        static_cast<std::uint64_t>(kBranches) *
        sizeof(HHSExactPass219H36StackSelectionV1);
    const std::uint64_t shared_reference_bytes =
        sizeof(cache) + sizeof(branches) + sizeof(index);

    std::size_t distinct_fib_identities = 0U;
    std::size_t max_equivalence_width = 0U;
    for (std::size_t i = 0U; i <= kFibMaxIndex; ++i) {
        const std::size_t count =
            static_cast<std::size_t>(
                index.offsets[i + 1U] - index.offsets[i]);
        if (count != 0U)
            ++distinct_fib_identities;
        if (count > max_equivalence_width)
            max_equivalence_width = count;
    }

    std::ostream *out = &std::cout;
    std::ofstream file;
    if (argc > 1) {
        file.open(argv[1], std::ios::out | std::ios::trunc);
        if (!file)
            return 9;
        out = &file;
    }

    *out
        << "{\n"
        << "  \"schema\": \"HHS_PASS219_H36_FIBONACCI_BRANCH_CACHE_BENCHMARK_V1\",\n"
        << "  \"geometry\": {\n"
        << "    \"lanes\": 4,\n"
        << "    \"cells_per_lane\": 36,\n"
        << "    \"branch_cells\": 144,\n"
        << "    \"frame_bits\": 5184,\n"
        << "    \"root_fibonacci\": 144,\n"
        << "    \"asymmetric_additive_division_verified\": true,\n"
        << "    \"distinct_fibonacci_identities\": "
        << distinct_fib_identities << ",\n"
        << "    \"max_equivalence_width\": "
        << max_equivalence_width << "\n"
        << "  },\n"
        << "  \"immutability\": {\n"
        << "    \"frozen_parent_entries\": 4,\n"
        << "    \"parent_cache_next_sequence\": "
        << cache.next_sequence << ",\n"
        << "    \"branch_fork_by_previous_state_reference\": true,\n"
        << "    \"parent_state_modified\": false,\n"
        << "    \"copy_on_write_payload\": false\n"
        << "  },\n"
        << "  \"receipts\": {\n"
        << "    \"branch_receipts\": 144,\n"
        << "    \"compatible_lane_composition_receipts\": "
        << composition_receipt_count << ",\n"
        << "    \"all_branch_chains_reverse_to_frozen_root\": true,\n"
        << "    \"all_compatible_compositions_deterministic\": true\n"
        << "  },\n"
        << "  \"memory\": {\n"
        << "    \"selection_bytes\": "
        << sizeof(HHSExactPass219H36StackSelectionV1) << ",\n"
        << "    \"branch_ref_bytes\": " << sizeof(BranchRef) << ",\n"
        << "    \"fib_index_bytes\": " << sizeof(FibIndex) << ",\n"
        << "    \"duplicate_144_selection_payload_bytes\": "
        << duplicate_payload_bytes << ",\n"
        << "    \"shared_parent_reference_total_bytes\": "
        << shared_reference_bytes << ",\n"
        << "    \"duplicate_vs_shared_ratio_x1000\": "
        << ratio_x1000(
               duplicate_payload_bytes,
               shared_reference_bytes) << ",\n"
        << "    \"shared_reference_smaller\": "
        << (shared_reference_bytes < duplicate_payload_bytes
                ? "true" : "false") << "\n"
        << "  },\n"
        << "  \"measurement\": {\n"
        << "    \"samples\": " << kSamples << ",\n"
        << "    \"calibration_repeats\": "
        << kCalibrationRepeats << ",\n"
        << "    \"local_rounds_per_sample\": "
        << kLocalRounds << ",\n"
        << "    \"equivalence_rounds_per_sample\": "
        << kEquivalenceRounds << ",\n"
        << "    \"baseline_cache_total_ns\": "
        << timing.baseline_cache_total_ns << ",\n"
        << "    \"direct_branch_ref_total_ns\": "
        << timing.direct_ref_total_ns << ",\n"
        << "    \"fib_bucket_branch_ref_total_ns\": "
        << timing.fib_bucket_ref_total_ns << ",\n"
        << "    \"baseline_vs_direct_speedup_x1000\": "
        << ratio_x1000(
               timing.baseline_cache_total_ns,
               timing.direct_ref_total_ns) << ",\n"
        << "    \"baseline_vs_fib_bucket_speedup_x1000\": "
        << ratio_x1000(
               timing.baseline_cache_total_ns,
               timing.fib_bucket_ref_total_ns) << ",\n"
        << "    \"equivalence_full_scan_total_ns\": "
        << timing.equivalence_scan_total_ns << ",\n"
        << "    \"equivalence_fib_bucket_total_ns\": "
        << timing.equivalence_bucket_total_ns << ",\n"
        << "    \"equivalence_bucket_speedup_x1000\": "
        << ratio_x1000(
               timing.equivalence_scan_total_ns,
               timing.equivalence_bucket_total_ns) << "\n"
        << "  },\n"
        << "  \"selection\": {\n"
        << "    \"best_local_lookup\": \"" << best_local << "\",\n"
        << "    \"best_local_total_ns\": " << best_local_ns << ",\n"
        << "    \"best_equivalence_lookup\": \""
        << best_equivalence << "\",\n"
        << "    \"best_configuration\": \""
        << best_configuration << "\",\n"
        << "    \"hybrid_direct_plus_fibonacci_index\": "
        << (hybrid_selected ? "true" : "false") << "\n"
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
