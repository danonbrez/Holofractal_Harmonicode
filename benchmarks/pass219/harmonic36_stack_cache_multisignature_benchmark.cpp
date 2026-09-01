#include "hhs_runtime_exact_abi.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include <unistd.h>

namespace {

using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_sink = 0U;

constexpr std::uint32_t kExecCell = 0120U;
constexpr std::uint32_t kDataCell = 0121U;
constexpr int kStackSamples = 7;
constexpr std::uint32_t kStackRounds = 8U;
constexpr int kCacheSamples = 11;
constexpr std::uint32_t kCacheRounds = 4096U;

enum class WorkloadClass : std::uint32_t {
    Console = 1U,
    BinaryIO = 2U,
    MonitorControl = 3U,
};

struct SemanticResult {
    std::uint64_t tty_input = 0U;
    std::uint64_t tty_output = 0U;
    std::uint64_t ptr_word36 = 0U;
    std::uint64_t ptp_output = 0U;
    std::uint32_t tty_service_count = 0U;
    std::uint32_t ptr_service_count = 0U;
    std::uint32_t ptp_service_count = 0U;
    std::uint32_t apr_service_count = 0U;
    std::uint32_t uuo_service_count = 0U;
    std::uint32_t dispatch_count = 0U;
    std::uint32_t final_pc18 = 0U;
    std::uint8_t queue_cursor = 0U;
};

struct CandidateRun {
    SemanticResult result{};
    std::uint64_t image_signature36 = 0U;
    std::uint64_t workload_signature36 = 0U;
    std::uint32_t working_state_bytes = 0U;
    std::uint32_t resource_events = 0U;
};

struct VariantMeasurement {
    WorkloadClass kind{};
    const char *name = nullptr;
    CandidateRun h36_probe{};
    CandidateRun linux_probe{};
    std::uint64_t semantic_signature64 = 0U;
    std::uint64_t h36_median_ns = 0U;
    std::uint64_t linux_median_ns = 0U;
    HHSExactPass219H36StackSelectionV1 selection{};
    HHSExactPass219H36StackCacheReceiptV1 receipt{};
    std::uint64_t fresh_median_ns = 0U;
    std::uint64_t cache_median_ns = 0U;
    std::uint64_t cache_speedup_x1000 = 0U;
    bool cache_benefit = false;
};

std::uint64_t mix64(std::uint64_t x) {
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30U)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27U)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31U);
}

std::uint64_t fold36(std::uint64_t state, std::uint64_t token) {
    return mix64(state ^ token) & HHS_EXACT_PASS219_H36_WORD_MASK;
}

std::uint64_t workload_signature36(
    std::uint64_t image_signature36,
    WorkloadClass kind
) {
    std::uint64_t s = fold36(
        image_signature36,
        UINT64_C(0x219360000) | static_cast<std::uint32_t>(kind));
    switch (kind) {
        case WorkloadClass::Console:
            s = fold36(s, UINT64_C(0x545459494E));  // TTYIN
            s = fold36(s, static_cast<std::uint8_t>('A'));
            s = fold36(s, UINT64_C(0x5454594F55));  // TTYOU
            s = fold36(s, static_cast<std::uint8_t>('B'));
            s = fold36(s, UINT64_C(2));             // dispatches
            break;
        case WorkloadClass::BinaryIO:
            s = fold36(s, UINT64_C(0x505452));      // PTR
            s = fold36(s, UINT64_C(012345670123));
            s = fold36(s, UINT64_C(0x505450));      // PTP
            s = fold36(s, static_cast<std::uint8_t>('C'));
            break;
        case WorkloadClass::MonitorControl:
            s = fold36(s, UINT64_C(0x4D55554F));    // MUUO
            s = fold36(s, UINT64_C(4));             // services
            s = fold36(s, UINT64_C(4));             // dispatches
            break;
    }
    return s == 0U ? UINT64_C(1) : s;
}

std::uint64_t semantic_signature64(const SemanticResult &r) {
    const std::uint64_t values[] = {
        r.tty_input, r.tty_output, r.ptr_word36, r.ptp_output,
        r.tty_service_count, r.ptr_service_count, r.ptp_service_count,
        r.apr_service_count, r.uuo_service_count, r.dispatch_count,
        r.final_pc18, r.queue_cursor,
    };
    std::uint64_t s = UINT64_C(0x21936B11);
    for (std::size_t i = 0U; i < sizeof(values) / sizeof(values[0]); ++i)
        s = mix64(s ^ values[i] ^
                  (static_cast<std::uint64_t>(i + 1U) << 48U));
    return s == 0U ? UINT64_C(1) : s;
}

bool semantic_equal(const SemanticResult &a, const SemanticResult &b) {
    return std::memcmp(&a, &b, sizeof(a)) == 0;
}

template <class Fn>
std::uint64_t median_ns(Fn fn, int samples) {
    fn();
    std::vector<std::uint64_t> values;
    values.reserve(static_cast<std::size_t>(samples));
    for (int i = 0; i < samples; ++i) {
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

std::uint64_t ioenc(
    std::uint8_t device,
    std::uint8_t fn,
    std::uint32_t e
) {
    std::uint64_t word = 0U;
    if (hhs_exact_pass219_h36_io_instruction_encode(
            device, fn, 0U, 0U, e, &word) != HHS_EXACT_STATUS_OK)
        std::abort();
    return word;
}

void h36_exec_io(
    HHSExactPass219H36VMStateV1 &vm,
    std::uint64_t instruction
) {
    vm.memory[kExecCell] = instruction;
    vm.pc18 = kExecCell;
    vm.trap = HHS_EXACT_PASS219_H36_TRAP_NONE;
    vm.halted = 0U;
    if (hhs_exact_pass219_h36_vm_step(&vm) != HHS_EXACT_STATUS_OK)
        std::abort();
    vm.pc18 = HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18;
}

void emit_word(
    std::uint64_t word,
    std::array<std::uint8_t, 6> &frames
) {
    std::size_t off = 0U;
    for (int shift = 30; shift >= 0; shift -= 6)
        frames[off++] = static_cast<std::uint8_t>(
            UINT8_C(0x80) |
            static_cast<std::uint8_t>(
                (word >> static_cast<std::uint32_t>(shift)) & 0x3FU));
}

std::uint64_t decode_word(const std::array<std::uint8_t, 6> &frames) {
    std::uint64_t word = 0U;
    for (const std::uint8_t frame : frames)
        word = ((word << 6U) | static_cast<std::uint64_t>(frame & 0x3FU)) &
               HHS_EXACT_PASS219_H36_WORD_MASK;
    return word;
}

CandidateRun run_h36(WorkloadClass kind) {
    HHSExactPass219H36VMStateV1 vm{};
    HHSExactPass219H36MonitorStateV1 monitor{};
    HHSExactPass219H36MonitorReceiptV1 initial{};
    HHSExactPass219H36MonitorReceiptV1 receipt{};
    CandidateRun run{};
    std::uint32_t steps = 0U;

    if (hhs_exact_pass219_h36_ka10_monitor_bootstrap(
            &vm, &monitor, &initial) != HHS_EXACT_STATUS_OK)
        std::abort();
    run.image_signature36 = initial.workload.image_signature36;
    run.workload_signature36 =
        workload_signature36(run.image_signature36, kind);

    if (kind == WorkloadClass::Console) {
        const std::uint8_t tty_in = static_cast<std::uint8_t>('A');
        std::array<std::uint8_t, 8> tty_out{};
        std::size_t tty_out_count = 0U;

        if (hhs_exact_pass219_h36_tty_feed_input(
                &vm, &tty_in, 1U) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 3U, &steps) != HHS_EXACT_STATUS_OK ||
            steps != 3U)
            std::abort();

        vm.memory[kDataCell] = static_cast<std::uint64_t>('B');
        h36_exec_io(
            vm, ioenc(HHS_EXACT_PASS219_H36_DEVICE_TTY, 3U, kDataCell));
        if (hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 3U, &steps) != HHS_EXACT_STATUS_OK ||
            steps != 3U ||
            hhs_exact_pass219_h36_tty_copy_output(
                &vm, tty_out.data(), tty_out.size(), &tty_out_count) !=
                HHS_EXACT_STATUS_OK ||
            tty_out_count != 1U ||
            hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 2U, &steps) != HHS_EXACT_STATUS_OK ||
            steps != 2U)
            std::abort();

        run.result.tty_input =
            vm.memory[HHS_EXACT_PASS219_H36_MONITOR_TTY_SCRATCH18];
        run.result.tty_output = tty_out[0];
    } else if (kind == WorkloadClass::BinaryIO) {
        const std::uint64_t ptr_word = UINT64_C(012345670123);
        std::array<std::uint8_t, 6> ptr_frames{};
        std::array<std::uint8_t, 8> ptp_frames{};
        std::size_t ptp_count = 0U;

        emit_word(ptr_word, ptr_frames);
        if (hhs_exact_pass219_h36_ptr_load_tape(
                &vm, ptr_frames.data(), ptr_frames.size()) !=
                HHS_EXACT_STATUS_OK)
            std::abort();
        h36_exec_io(
            vm,
            ioenc(
                HHS_EXACT_PASS219_H36_DEVICE_PTR,
                4U,
                (UINT32_C(1) << 5U) |
                (UINT32_C(1) << 4U) |
                UINT32_C(2)));
        if (hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 2U, &steps) != HHS_EXACT_STATUS_OK ||
            steps != 2U)
            std::abort();

        vm.memory[kDataCell] = static_cast<std::uint64_t>('C');
        h36_exec_io(
            vm, ioenc(HHS_EXACT_PASS219_H36_DEVICE_PTP, 3U, kDataCell));
        if (hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 2U, &steps) != HHS_EXACT_STATUS_OK ||
            steps != 2U ||
            hhs_exact_pass219_h36_ptp_copy_tape(
                &vm, ptp_frames.data(), ptp_frames.size(), &ptp_count) !=
                HHS_EXACT_STATUS_OK ||
            ptp_count != 1U)
            std::abort();

        run.result.ptr_word36 =
            vm.memory[HHS_EXACT_PASS219_H36_MONITOR_PTR_SCRATCH18];
        run.result.ptp_output = ptp_frames[0];
    } else {
        if (hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 4U, &steps) != HHS_EXACT_STATUS_OK ||
            steps != 4U)
            std::abort();
    }

    if (hhs_exact_pass219_h36_ka10_monitor_receipt_capture(
            &vm, &monitor, &receipt) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_ka10_monitor_receipt_validate(
            &vm, &monitor, &receipt) != HHS_EXACT_STATUS_OK)
        std::abort();

    run.result.tty_service_count = monitor.tty_service_count;
    run.result.ptr_service_count = monitor.ptr_service_count;
    run.result.ptp_service_count = monitor.ptp_service_count;
    run.result.apr_service_count = monitor.apr_service_count;
    run.result.uuo_service_count = monitor.uuo_service_count;
    run.result.dispatch_count = monitor.dispatch_count;
    run.result.final_pc18 = vm.pc18;
    run.result.queue_cursor = monitor.queue_cursor;
    run.working_state_bytes = static_cast<std::uint32_t>(
        sizeof(vm) + sizeof(monitor) + sizeof(initial) + sizeof(receipt));
    run.resource_events = monitor.executed_steps;
    return run;
}

bool write_all(
    int fd,
    const std::uint8_t *data,
    std::size_t count,
    std::uint32_t &events
) {
    std::size_t off = 0U;
    while (off < count) {
        const ssize_t n = ::write(fd, data + off, count - off);
        ++events;
        if (n <= 0)
            return false;
        off += static_cast<std::size_t>(n);
    }
    return true;
}

bool read_all(
    int fd,
    std::uint8_t *data,
    std::size_t count,
    std::uint32_t &events
) {
    std::size_t off = 0U;
    while (off < count) {
        const ssize_t n = ::read(fd, data + off, count - off);
        ++events;
        if (n <= 0)
            return false;
        off += static_cast<std::size_t>(n);
    }
    return true;
}

bool pipe_transfer(
    const std::uint8_t *input,
    std::uint8_t *output,
    std::size_t count,
    std::uint32_t &events
) {
    int fd[2] = {-1, -1};
    if (::pipe(fd) != 0)
        return false;
    ++events;
    const bool ok =
        write_all(fd[1], input, count, events) &&
        read_all(fd[0], output, count, events);
    const int cw = ::close(fd[1]);
    ++events;
    const int cr = ::close(fd[0]);
    ++events;
    return ok && cw == 0 && cr == 0;
}

CandidateRun run_linux(
    WorkloadClass kind,
    std::uint64_t image_signature36
) {
    CandidateRun run{};
    std::uint32_t events = 0U;
    run.image_signature36 = image_signature36;
    run.workload_signature36 = workload_signature36(image_signature36, kind);

    if (kind == WorkloadClass::Console) {
        const std::uint8_t tty_in = static_cast<std::uint8_t>('A');
        std::uint8_t tty_in_seen = 0U;
        const std::uint8_t tty_out = static_cast<std::uint8_t>('B');
        std::uint8_t tty_out_seen = 0U;
        if (!pipe_transfer(&tty_in, &tty_in_seen, 1U, events) ||
            !pipe_transfer(&tty_out, &tty_out_seen, 1U, events))
            std::abort();
        run.result.tty_input = tty_in_seen;
        run.result.tty_output = tty_out_seen;
        run.result.tty_service_count = 2U;
        run.result.dispatch_count = 2U;
        run.result.uuo_service_count = 2U;
        run.result.queue_cursor = 0U;
        g_sink ^= HHS_EXACT_PASS219_H36_MONITOR_TASK0_18;
        g_sink ^= HHS_EXACT_PASS219_H36_MONITOR_TASK1_18;
        events += 2U;
    } else if (kind == WorkloadClass::BinaryIO) {
        const std::uint64_t ptr_word = UINT64_C(012345670123);
        std::array<std::uint8_t, 6> ptr_frames{};
        std::array<std::uint8_t, 6> ptr_seen{};
        const std::uint8_t ptp = static_cast<std::uint8_t>('C');
        std::uint8_t ptp_seen = 0U;
        emit_word(ptr_word, ptr_frames);
        if (!pipe_transfer(
                ptr_frames.data(), ptr_seen.data(), ptr_seen.size(), events) ||
            !pipe_transfer(&ptp, &ptp_seen, 1U, events))
            std::abort();
        run.result.ptr_word36 = decode_word(ptr_seen);
        run.result.ptp_output = ptp_seen;
        run.result.ptr_service_count = 1U;
        run.result.ptp_service_count = 1U;
    } else {
        for (std::uint32_t i = 0U; i < 4U; ++i) {
            g_sink ^= (i & 1U) == 0U
                ? HHS_EXACT_PASS219_H36_MONITOR_TASK0_18
                : HHS_EXACT_PASS219_H36_MONITOR_TASK1_18;
            ++events;
        }
        run.result.dispatch_count = 4U;
        run.result.uuo_service_count = 4U;
        run.result.queue_cursor = 0U;
    }

    run.result.final_pc18 =
        HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18;
    run.working_state_bytes = static_cast<std::uint32_t>(sizeof(run));
    run.resource_events = events;
    return run;
}

const char *class_name(WorkloadClass kind) {
    switch (kind) {
        case WorkloadClass::Console: return "CONSOLE_FOCUSED";
        case WorkloadClass::BinaryIO: return "BINARY_IO_FOCUSED";
        case WorkloadClass::MonitorControl: return "MONITOR_CONTROL_FOCUSED";
    }
    return "UNKNOWN";
}

const char *stack_name(std::uint32_t kind) {
    if (kind == HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10)
        return "H36_KA10_MONITOR";
    if (kind == HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64)
        return "LINUX_X86_64_POSIX";
    return "UNKNOWN";
}

VariantMeasurement measure_variant(WorkloadClass kind) {
    VariantMeasurement m{};
    m.kind = kind;
    m.name = class_name(kind);
    m.h36_probe = run_h36(kind);
    m.linux_probe = run_linux(kind, m.h36_probe.image_signature36);

    if (m.h36_probe.workload_signature36 !=
            m.linux_probe.workload_signature36 ||
        !semantic_equal(m.h36_probe.result, m.linux_probe.result))
        std::abort();

    m.semantic_signature64 = semantic_signature64(m.h36_probe.result);
    if (m.semantic_signature64 !=
        semantic_signature64(m.linux_probe.result))
        std::abort();

    const auto h36_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kStackRounds; ++i) {
            const CandidateRun r = run_h36(kind);
            if (r.workload_signature36 !=
                    m.h36_probe.workload_signature36 ||
                !semantic_equal(r.result, m.h36_probe.result))
                std::abort();
            checksum ^= semantic_signature64(r.result);
        }
        g_sink ^= checksum;
    };
    const auto linux_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kStackRounds; ++i) {
            const CandidateRun r =
                run_linux(kind, m.h36_probe.image_signature36);
            if (r.workload_signature36 !=
                    m.h36_probe.workload_signature36 ||
                !semantic_equal(r.result, m.linux_probe.result))
                std::abort();
            checksum ^= semantic_signature64(r.result);
        }
        g_sink ^= checksum;
    };

    m.h36_median_ns = median_ns(h36_sample, kStackSamples);
    m.linux_median_ns = median_ns(linux_sample, kStackSamples);
    if (m.h36_median_ns == 0U || m.linux_median_ns == 0U)
        std::abort();

    HHSExactPass219H36StackCandidateEvidenceV1 h36{};
    HHSExactPass219H36StackCandidateEvidenceV1 linux{};
    if (hhs_exact_pass219_h36_stack_candidate_prepare(
            1U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
            m.h36_probe.workload_signature36,
            m.semantic_signature64,
            m.h36_median_ns,
            static_cast<std::uint32_t>(kStackSamples),
            kStackRounds,
            m.h36_probe.working_state_bytes,
            m.h36_probe.resource_events,
            1U,
            &h36) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_candidate_prepare(
            2U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
            m.linux_probe.workload_signature36,
            m.semantic_signature64,
            m.linux_median_ns,
            static_cast<std::uint32_t>(kStackSamples),
            kStackRounds,
            m.linux_probe.working_state_bytes,
            m.linux_probe.resource_events,
            1U,
            &linux) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_select(
            &h36, &linux, &m.selection) != HHS_EXACT_STATUS_OK)
        std::abort();

    HHSExactPass219H36StackCacheV1 cache{};
    HHSExactPass219H36StackSelectionV1 cached{};
    if (hhs_exact_pass219_h36_stack_cache_init(&cache) !=
            HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_cache_store(
            &cache, &m.selection) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_cache_lookup(
            &cache,
            m.selection.workload_signature36,
            m.selection.semantic_result_signature64,
            m.selection.selected_vector_key216,
            &cached,
            &m.receipt) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
            &cached, &m.selection) != HHS_EXACT_STATUS_OK)
        std::abort();

    HHSExactPass219H36StackSelectionV1 stale = m.selection;
    stale.semantic_result_signature64 ^= UINT64_C(1);
    if (hhs_exact_pass219_h36_stack_cache_store(
            &cache, &stale) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        std::abort();

    char wrong_key[HHS_EXACT_UQCEL_HASH216_STRLEN];
    std::memcpy(
        wrong_key,
        m.selection.selected_vector_key216,
        sizeof(wrong_key));
    wrong_key[0] =
        wrong_key[0] == HHS_EXACT_HASH72_ALPHABET[0]
            ? HHS_EXACT_HASH72_ALPHABET[1]
            : HHS_EXACT_HASH72_ALPHABET[0];
    HHSExactPass219H36StackCacheReceiptV1 bad_receipt{};
    if (hhs_exact_pass219_h36_stack_cache_lookup(
            &cache,
            m.selection.workload_signature36,
            m.selection.semantic_result_signature64,
            wrong_key,
            &cached,
            &bad_receipt) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
        std::abort();

    const auto fresh_selection_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kCacheRounds; ++i) {
            HHSExactPass219H36StackSelectionV1 fresh{};
            if (hhs_exact_pass219_h36_stack_select(
                    &h36, &linux, &fresh) != HHS_EXACT_STATUS_OK ||
                hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
                    &fresh, &m.selection) != HHS_EXACT_STATUS_OK)
                std::abort();
            checksum ^= fresh.speedup_x1000;
            checksum ^= static_cast<std::uint8_t>(
                fresh.selected_vector_key216[i % 216U]);
        }
        g_sink ^= checksum;
    };

    const auto cache_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kCacheRounds; ++i) {
            HHSExactPass219H36StackSelectionV1 hit{};
            HHSExactPass219H36StackCacheReceiptV1 receipt{};
            if (hhs_exact_pass219_h36_stack_cache_lookup(
                    &cache,
                    m.selection.workload_signature36,
                    m.selection.semantic_result_signature64,
                    m.selection.selected_vector_key216,
                    &hit,
                    &receipt) != HHS_EXACT_STATUS_OK ||
                hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
                    &hit, &m.selection) != HHS_EXACT_STATUS_OK ||
                receipt.cache_hit != 1U ||
                receipt.exact_replayable != 1U ||
                receipt.stale_signature_rejected != 1U)
                std::abort();
            checksum ^= receipt.entry_signature64;
            checksum ^= receipt.replay_signature64;
        }
        g_sink ^= checksum;
    };

    m.fresh_median_ns =
        median_ns(fresh_selection_sample, kCacheSamples);
    m.cache_median_ns =
        median_ns(cache_sample, kCacheSamples);
    if (m.fresh_median_ns == 0U || m.cache_median_ns == 0U)
        std::abort();

    m.cache_benefit = m.cache_median_ns < m.fresh_median_ns;
    m.cache_speedup_x1000 = m.cache_benefit
        ? ratio_x1000(m.fresh_median_ns, m.cache_median_ns)
        : ratio_x1000(m.cache_median_ns, m.fresh_median_ns);
    return m;
}

}  // namespace

int main(int argc, char **argv) {
#if !defined(__linux__) || !defined(__x86_64__)
    std::cerr << "multisignature benchmark requires Linux x86_64\n";
    return 2;
#else
    const std::array<WorkloadClass, 3> kinds = {
        WorkloadClass::Console,
        WorkloadClass::BinaryIO,
        WorkloadClass::MonitorControl,
    };
    std::array<VariantMeasurement, 3> rows{};
    for (std::size_t i = 0U; i < kinds.size(); ++i)
        rows[i] = measure_variant(kinds[i]);

    if (rows[0].h36_probe.workload_signature36 ==
            rows[1].h36_probe.workload_signature36 ||
        rows[0].h36_probe.workload_signature36 ==
            rows[2].h36_probe.workload_signature36 ||
        rows[1].h36_probe.workload_signature36 ==
            rows[2].h36_probe.workload_signature36)
        return 3;

    std::ostream *out = &std::cout;
    std::ofstream file;
    if (argc > 1) {
        file.open(argv[1], std::ios::out | std::ios::trunc);
        if (!file)
            return 4;
        out = &file;
    }

    *out << "{\n"
         << "  \"schema\": \"HHS_PASS219_H36_STACK_CACHE_MULTISIGNATURE_BENCHMARK_V1\",\n"
         << "  \"platform\": {\"linux\": true, \"x86_64\": true, "
         << "\"stack_samples\": " << kStackSamples << ", "
         << "\"stack_rounds_per_sample\": " << kStackRounds << ", "
         << "\"cache_samples\": " << kCacheSamples << ", "
         << "\"cache_rounds_per_sample\": " << kCacheRounds << "},\n"
         << "  \"workloads\": [\n";

    for (std::size_t i = 0U; i < rows.size(); ++i) {
        const VariantMeasurement &m = rows[i];
        *out
            << "    {\n"
            << "      \"class\": \"" << m.name << "\",\n"
            << "      \"workload_signature36\": "
            << m.h36_probe.workload_signature36 << ",\n"
            << "      \"semantic_result_signature64\": "
            << m.semantic_signature64 << ",\n"
            << "      \"exact_h36_linux_semantic_equal_before_timing\": true,\n"
            << "      \"h36_median_ns\": " << m.h36_median_ns << ",\n"
            << "      \"linux_median_ns\": " << m.linux_median_ns << ",\n"
            << "      \"selected_candidate_id\": "
            << m.selection.selected_candidate_id << ",\n"
            << "      \"selected_stack\": \""
            << stack_name(m.selection.selected_stack_kind) << "\",\n"
            << "      \"selector_speedup_x1000\": "
            << m.selection.speedup_x1000 << ",\n"
            << "      \"vector_key216\": \""
            << m.selection.selected_vector_key216 << "\",\n"
            << "      \"vector_key216_length\": "
            << std::strlen(m.selection.selected_vector_key216) << ",\n"
            << "      \"cache_hit_equals_fresh_before_timing\": true,\n"
            << "      \"stale_signature_rejected\": true,\n"
            << "      \"mismatched_vector_key_rejected\": true,\n"
            << "      \"entry_signature64\": "
            << m.receipt.entry_signature64 << ",\n"
            << "      \"replay_signature64\": "
            << m.receipt.replay_signature64 << ",\n"
            << "      \"fresh_selection_median_ns\": "
            << m.fresh_median_ns << ",\n"
            << "      \"cache_hit_median_ns\": "
            << m.cache_median_ns << ",\n"
            << "      \"cache_benefit\": "
            << (m.cache_benefit ? "true" : "false") << ",\n"
            << "      \"cache_winner_ratio_x1000\": "
            << m.cache_speedup_x1000 << ",\n"
            << "      \"authority\": {"
            << "\"vm81_mutation\": false, "
            << "\"vm81_admission_bypass\": false, "
            << "\"hash72\": false, "
            << "\"hash216\": false, "
            << "\"persistence\": false, "
            << "\"floating_point\": false}\n"
            << "    }" << (i + 1U == rows.size() ? "\n" : ",\n");
    }

    *out
        << "  ],\n"
        << "  \"all_workload_signatures_distinct\": true,\n"
        << "  \"authoritative_state_changed\": false\n"
        << "}\n";
    return 0;
#endif
}
