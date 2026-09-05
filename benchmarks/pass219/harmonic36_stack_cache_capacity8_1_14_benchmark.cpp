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

#include <unistd.h>

namespace {

using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_sink = 0U;

constexpr std::size_t kResidents = 8U;
constexpr std::size_t kNewWorkloads = 4U;
constexpr int kStackSamples = 7;
constexpr std::uint32_t kStackRounds = 8U;
constexpr int kCacheSamples = 11;
constexpr std::uint32_t kCacheRounds = 4096U;
constexpr std::size_t kCalibrationRepeats = 5U;
constexpr std::uint32_t kRequiredBeneficialRepeats = 4U;
constexpr std::uint32_t kExecCell = 0120U;
constexpr std::uint32_t kDataCell = 0121U;

#define MBIT(n) (UINT32_C(1) << (35U - (std::uint32_t)(n)))

enum class NewWorkload : std::uint32_t {
    AprPi = 5U,
    RimBootstrap = 6U,
    MixedConsoleBinary = 7U,
    MixedSchedulerIoUuo = 8U,
    BoundaryConsoleAlternate = 9U,
};

struct SemanticResult {
    std::array<std::uint64_t, 12> v{};
};

struct CandidateRun {
    SemanticResult result{};
    std::uint64_t workload_signature36 = 0U;
    std::uint32_t working_state_bytes = 0U;
    std::uint32_t resource_events = 0U;
};

struct FrozenResidentSpec {
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
    std::uint32_t selected_candidate;
    const char *vector_key216;
};

struct Resident {
    const char *name = nullptr;
    HHSExactPass219H36StackCandidateEvidenceV1 h36{};
    HHSExactPass219H36StackCandidateEvidenceV1 linux{};
    HHSExactPass219H36StackSelectionV1 selection{};
    std::uint64_t h36_median_ns = 0U;
    std::uint64_t linux_median_ns = 0U;
};

struct CacheMeasurement {
    std::uint64_t fresh_ns = 0U;
    std::uint64_t occ1_ns = 0U;
    std::uint64_t occ4_ns = 0U;
    std::uint64_t occ8_ns = 0U;
    std::uint64_t fresh_total_ns = 0U;
    std::uint64_t occ1_total_ns = 0U;
    std::uint64_t occ4_total_ns = 0U;
    std::uint64_t occ8_total_ns = 0U;
    std::array<std::uint64_t, kCalibrationRepeats> fresh_repeat_ns{};
    std::array<std::uint64_t, kCalibrationRepeats> occ1_repeat_ns{};
    std::array<std::uint64_t, kCalibrationRepeats> occ4_repeat_ns{};
    std::array<std::uint64_t, kCalibrationRepeats> occ8_repeat_ns{};
    std::uint32_t beneficial_repeat_count = 0U;
    std::uint64_t occ8_vs_fresh_x1000 = 0U;
    std::uint64_t occ8_vs_occ1_x1000 = 0U;
    std::uint64_t occ8_vs_occ4_x1000 = 0U;
    bool aggregate_benefit = false;
    bool repeat_stability_pass = false;
    bool occ8_faster_than_fresh = false;
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

std::uint64_t workload_signature36(NewWorkload kind) {
    std::uint64_t s = fold36(
        UINT64_C(0x219360008),
        static_cast<std::uint32_t>(kind));
    switch (kind) {
        case NewWorkload::AprPi:
            s = fold36(s, UINT64_C(0x4150525049)); // APRPI
            s = fold36(s, UINT64_C(3));
            s = fold36(s, UINT64_C(50));
            break;
        case NewWorkload::RimBootstrap:
            s = fold36(s, UINT64_C(0x52494D)); // RIM
            s = fold36(s, UINT64_C(012345670123));
            s = fold36(s, UINT64_C(076543210765));
            s = fold36(s, UINT64_C(120));
            break;
        case NewWorkload::MixedConsoleBinary:
            s = fold36(s, UINT64_C(0x4D49584342)); // MIXCB
            s = fold36(s, static_cast<std::uint8_t>('A'));
            s = fold36(s, static_cast<std::uint8_t>('B'));
            s = fold36(s, UINT64_C(012345670123));
            s = fold36(s, static_cast<std::uint8_t>('C'));
            break;
        case NewWorkload::MixedSchedulerIoUuo:
            s = fold36(s, UINT64_C(0x4D49585355)); // MIXSU
            s = fold36(s, UINT64_C(4));
            s = fold36(s, static_cast<std::uint8_t>('D'));
            break;
        case NewWorkload::BoundaryConsoleAlternate:
            s = fold36(s, UINT64_C(0x424E445259)); // BNDRY
            s = fold36(s, static_cast<std::uint8_t>('Q'));
            s = fold36(s, static_cast<std::uint8_t>('R'));
            break;
    }
    return s == 0U ? UINT64_C(1) : s;
}

std::uint64_t semantic_signature64(const SemanticResult &r) {
    std::uint64_t s = UINT64_C(0x21936813);
    for (std::size_t i = 0U; i < r.v.size(); ++i)
        s = mix64(
            s ^ r.v[i] ^
            (static_cast<std::uint64_t>(i + 1U) << 48U));
    return s == 0U ? UINT64_C(1) : s;
}

bool semantic_equal(const SemanticResult &a, const SemanticResult &b) {
    return a.v == b.v;
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

std::uint64_t enc(
    std::uint16_t op,
    std::uint8_t ac,
    std::uint32_t e
) {
    std::uint64_t word = 0U;
    if (hhs_exact_pass219_h36_instruction_encode(
            op, ac, 0U, 0U, e, &word) != HHS_EXACT_STATUS_OK)
        std::abort();
    return word;
}

void exec_io(
    HHSExactPass219H36VMStateV1 &vm,
    std::uint64_t instruction
) {
    vm.memory[kExecCell] = instruction;
    vm.pc18 = kExecCell;
    vm.trap = HHS_EXACT_PASS219_H36_TRAP_NONE;
    vm.halted = 0U;
    if (hhs_exact_pass219_h36_vm_step(&vm) != HHS_EXACT_STATUS_OK)
        std::abort();
}

std::uint32_t select_channel(std::uint8_t channel) {
    if (channel < 1U || channel > 7U)
        std::abort();
    return MBIT(28U + channel);
}

std::uint64_t iowd(
    std::uint32_t count,
    std::uint32_t address_minus_one
) {
    const std::uint32_t neg =
        ((UINT32_C(1) << 18U) - count) &
        HHS_EXACT_PASS219_H36_HALF_MASK;
    return
        (static_cast<std::uint64_t>(neg) << 18U) |
        (static_cast<std::uint64_t>(address_minus_one) &
         HHS_EXACT_PASS219_H36_HALF_MASK);
}

void emit_word(
    std::uint64_t word,
    std::uint8_t *frames,
    std::size_t &offset
) {
    for (int shift = 30; shift >= 0; shift -= 6) {
        frames[offset++] = static_cast<std::uint8_t>(
            UINT8_C(0x80) |
            static_cast<std::uint8_t>(
                (word >> static_cast<std::uint32_t>(shift)) &
                UINT64_C(0x3F)));
    }
}

void build_rim_tape(
    std::array<std::uint8_t, 24> &frames,
    std::uint64_t &pointer,
    std::uint64_t &terminal
) {
    std::size_t off = 0U;
    pointer = iowd(3U, 99U);
    terminal = enc(UINT16_C(0254), 0U, 120U);
    emit_word(pointer, frames.data(), off);
    emit_word(UINT64_C(012345670123), frames.data(), off);
    emit_word(UINT64_C(076543210765), frames.data(), off);
    emit_word(terminal, frames.data(), off);
    if (off != frames.size())
        std::abort();
}

void emit_ptr_word(
    std::uint64_t word,
    std::array<std::uint8_t, 6> &frames
) {
    std::size_t off = 0U;
    emit_word(word, frames.data(), off);
    if (off != frames.size())
        std::abort();
}

void monitor_return_scheduler(HHSExactPass219H36VMStateV1 &vm) {
    vm.pc18 = HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18;
}

CandidateRun run_h36(NewWorkload kind) {
    CandidateRun run{};
    run.workload_signature36 = workload_signature36(kind);
    run.working_state_bytes = static_cast<std::uint32_t>(
        sizeof(HHSExactPass219H36VMStateV1) +
        sizeof(HHSExactPass219H36MonitorStateV1) +
        sizeof(HHSExactPass219H36MonitorReceiptV1));

    if (kind == NewWorkload::AprPi) {
        HHSExactPass219H36VMStateV1 vm{};
        if (hhs_exact_pass219_h36_vm_init(&vm) != HHS_EXACT_STATUS_OK)
            std::abort();

        exec_io(
            vm,
            ioenc(
                HHS_EXACT_PASS219_H36_DEVICE_PI,
                4U,
                MBIT(25U) | MBIT(28U) | select_channel(3U)));
        vm.legacy_overflow = 1U;
        exec_io(
            vm,
            ioenc(
                HHS_EXACT_PASS219_H36_DEVICE_APR,
                4U,
                MBIT(31U) | UINT32_C(3)));
        vm.legacy_priority_vector18[2] = 50U;
        if (hhs_exact_pass219_h36_internal_interrupt_refresh(&vm) !=
            HHS_EXACT_STATUS_OK)
            std::abort();
        std::uint8_t channel = 0U;
        if (hhs_exact_pass219_h36_priority_enter(
                &vm, &channel) != HHS_EXACT_STATUS_OK ||
            channel != 3U)
            std::abort();

        run.result.v = {
            channel,
            vm.pc18,
            vm.legacy_priority_enabled_mask,
            vm.legacy_priority_external_request_mask,
            vm.legacy_priority_active_channel,
            vm.legacy_apr_channel,
            vm.legacy_apr_overflow_interrupt_enable,
            vm.legacy_overflow,
            vm.canonical_mutation_authority,
            vm.canonical_hash72_authority,
            vm.canonical_persistence_authority,
            vm.floating_point_authority
        };
        run.resource_events = 4U;
        return run;
    }

    if (kind == NewWorkload::RimBootstrap) {
        HHSExactPass219H36VMStateV1 vm{};
        HHSExactPass219H36RIMReceiptV1 receipt{};
        std::array<std::uint8_t, 24> tape{};
        std::uint64_t pointer = 0U;
        std::uint64_t terminal = 0U;
        build_rim_tape(tape, pointer, terminal);
        if (hhs_exact_pass219_h36_vm_init(&vm) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_ptr_load_tape(
                &vm, tape.data(), tape.size()) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_rim_bootstrap(
                &vm, &receipt) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_rim_receipt_validate(
                &vm, &receipt) != HHS_EXACT_STATUS_OK)
            std::abort();

        run.result.v = {
            receipt.declared_word_count,
            receipt.loaded_word_count,
            receipt.first_loaded_address18,
            receipt.last_loaded_address18,
            receipt.initial_iowd36,
            receipt.final_iowd36,
            receipt.terminal_word36,
            receipt.final_pc18,
            vm.memory[100],
            vm.memory[101],
            vm.memory[102],
            receipt.exact_replayable
        };
        run.resource_events = 5U;
        return run;
    }

    HHSExactPass219H36VMStateV1 vm{};
    HHSExactPass219H36MonitorStateV1 monitor{};
    HHSExactPass219H36MonitorReceiptV1 initial{};
    HHSExactPass219H36MonitorReceiptV1 final_receipt{};
    std::uint32_t steps = 0U;

    if (hhs_exact_pass219_h36_ka10_monitor_bootstrap(
            &vm, &monitor, &initial) != HHS_EXACT_STATUS_OK)
        std::abort();

    if (kind == NewWorkload::MixedConsoleBinary) {
        const std::uint8_t tty_in = static_cast<std::uint8_t>('A');
        std::array<std::uint8_t, 8> tty_out{};
        std::size_t tty_out_count = 0U;
        std::array<std::uint8_t, 6> ptr_frames{};
        std::array<std::uint8_t, 8> ptp_frames{};
        std::size_t ptp_count = 0U;

        if (hhs_exact_pass219_h36_tty_feed_input(
                &vm, &tty_in, 1U) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 3U, &steps) != HHS_EXACT_STATUS_OK)
            std::abort();

        vm.memory[kDataCell] = static_cast<std::uint64_t>('B');
        exec_io(
            vm,
            ioenc(
                HHS_EXACT_PASS219_H36_DEVICE_TTY, 3U, kDataCell));
        monitor_return_scheduler(vm);
        if (hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 3U, &steps) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_tty_copy_output(
                &vm, tty_out.data(), tty_out.size(), &tty_out_count) !=
                HHS_EXACT_STATUS_OK ||
            tty_out_count != 1U)
            std::abort();

        emit_ptr_word(UINT64_C(012345670123), ptr_frames);
        if (hhs_exact_pass219_h36_ptr_load_tape(
                &vm, ptr_frames.data(), ptr_frames.size()) !=
                HHS_EXACT_STATUS_OK)
            std::abort();
        exec_io(
            vm,
            ioenc(
                HHS_EXACT_PASS219_H36_DEVICE_PTR,
                4U,
                (UINT32_C(1) << 5U) |
                (UINT32_C(1) << 4U) |
                UINT32_C(2)));
        monitor_return_scheduler(vm);
        if (hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 2U, &steps) != HHS_EXACT_STATUS_OK)
            std::abort();

        vm.memory[kDataCell] = static_cast<std::uint64_t>('C');
        exec_io(
            vm,
            ioenc(
                HHS_EXACT_PASS219_H36_DEVICE_PTP, 3U, kDataCell));
        monitor_return_scheduler(vm);
        if (hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 2U, &steps) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_ptp_copy_tape(
                &vm, ptp_frames.data(), ptp_frames.size(), &ptp_count) !=
                HHS_EXACT_STATUS_OK ||
            ptp_count != 1U)
            std::abort();

        run.result.v = {
            vm.memory[HHS_EXACT_PASS219_H36_MONITOR_TTY_SCRATCH18],
            tty_out[0],
            vm.memory[HHS_EXACT_PASS219_H36_MONITOR_PTR_SCRATCH18],
            ptp_frames[0],
            monitor.tty_service_count,
            monitor.ptr_service_count,
            monitor.ptp_service_count,
            monitor.dispatch_count,
            monitor.uuo_service_count,
            vm.pc18,
            monitor.queue_cursor,
            monitor.last_interrupt_channel
        };
        run.resource_events = monitor.executed_steps;
    } else {
        const std::uint8_t out_byte =
            kind == NewWorkload::MixedSchedulerIoUuo
                ? static_cast<std::uint8_t>('D')
                : static_cast<std::uint8_t>('R');
        const std::uint8_t in_byte =
            kind == NewWorkload::BoundaryConsoleAlternate
                ? static_cast<std::uint8_t>('Q')
                : static_cast<std::uint8_t>('P');
        std::array<std::uint8_t, 8> tty_out{};
        std::size_t tty_out_count = 0U;

        if (kind == NewWorkload::MixedSchedulerIoUuo) {
            if (hhs_exact_pass219_h36_ka10_monitor_drive(
                    &vm, &monitor, 2U, &steps) != HHS_EXACT_STATUS_OK)
                std::abort();
        }
        if (hhs_exact_pass219_h36_tty_feed_input(
                &vm, &in_byte, 1U) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 3U, &steps) != HHS_EXACT_STATUS_OK)
            std::abort();

        vm.memory[kDataCell] = out_byte;
        exec_io(
            vm,
            ioenc(
                HHS_EXACT_PASS219_H36_DEVICE_TTY, 3U, kDataCell));
        monitor_return_scheduler(vm);
        if (hhs_exact_pass219_h36_ka10_monitor_drive(
                &vm, &monitor, 3U, &steps) != HHS_EXACT_STATUS_OK ||
            hhs_exact_pass219_h36_tty_copy_output(
                &vm, tty_out.data(), tty_out.size(), &tty_out_count) !=
                HHS_EXACT_STATUS_OK ||
            tty_out_count != 1U)
            std::abort();

        if (kind == NewWorkload::MixedSchedulerIoUuo) {
            if (hhs_exact_pass219_h36_ka10_monitor_drive(
                    &vm, &monitor, 2U, &steps) != HHS_EXACT_STATUS_OK)
                std::abort();
        } else {
            if (hhs_exact_pass219_h36_ka10_monitor_drive(
                    &vm, &monitor, 1U, &steps) != HHS_EXACT_STATUS_OK)
                std::abort();
        }

        run.result.v = {
            vm.memory[HHS_EXACT_PASS219_H36_MONITOR_TTY_SCRATCH18],
            tty_out[0],
            monitor.tty_service_count,
            monitor.ptr_service_count,
            monitor.ptp_service_count,
            monitor.dispatch_count,
            monitor.uuo_service_count,
            monitor.executed_steps,
            vm.pc18,
            monitor.queue_cursor,
            monitor.last_interrupt_channel,
            vm.legacy_uuo_dispatch_count
        };
        run.resource_events = monitor.executed_steps;
    }

    if (hhs_exact_pass219_h36_ka10_monitor_receipt_capture(
            &vm, &monitor, &final_receipt) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_ka10_monitor_receipt_validate(
            &vm, &monitor, &final_receipt) != HHS_EXACT_STATUS_OK)
        std::abort();

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

CandidateRun run_linux(NewWorkload kind) {
    CandidateRun run{};
    run.workload_signature36 = workload_signature36(kind);
    run.working_state_bytes = static_cast<std::uint32_t>(sizeof(run));
    std::uint32_t events = 0U;

    if (kind == NewWorkload::AprPi) {
        const std::uint8_t channel = 3U;
        const std::uint32_t pc18 = 50U;
        const std::uint8_t enabled = UINT8_C(0x04);
        const std::uint8_t external = UINT8_C(0x04);
        const std::uint8_t active = 3U;
        const std::uint8_t apr_channel = 3U;
        const std::uint8_t overflow_enable = 1U;
        const std::uint8_t overflow = 1U;
        g_sink ^= channel ^ pc18 ^ enabled ^ external;
        events = 4U;
        run.result.v = {
            channel, pc18, enabled, external, active, apr_channel,
            overflow_enable, overflow, 0U, 0U, 0U, 0U
        };
        run.resource_events = events;
        return run;
    }

    if (kind == NewWorkload::RimBootstrap) {
        std::array<std::uint64_t, 3> media = {
            UINT64_C(012345670123),
            UINT64_C(076543210765),
            enc(UINT16_C(0254), 0U, 120U)
        };
        std::array<std::uint64_t, 3> memory{};
        std::copy(media.begin(), media.end(), memory.begin());
        ++events;
        const std::uint64_t pointer = iowd(3U, 99U);
        const std::uint64_t final_iowd = UINT64_C(102);
        run.result.v = {
            3U,
            3U,
            100U,
            102U,
            pointer,
            final_iowd,
            media[2],
            120U,
            memory[0],
            memory[1],
            memory[2],
            1U
        };
        run.resource_events = events;
        return run;
    }

    if (kind == NewWorkload::MixedConsoleBinary) {
        const std::uint8_t tty_in = static_cast<std::uint8_t>('A');
        std::uint8_t tty_in_seen = 0U;
        const std::uint8_t tty_out = static_cast<std::uint8_t>('B');
        std::uint8_t tty_out_seen = 0U;
        std::array<std::uint8_t, 6> ptr_frames{};
        std::array<std::uint8_t, 6> ptr_seen{};
        const std::uint8_t ptp = static_cast<std::uint8_t>('C');
        std::uint8_t ptp_seen = 0U;
        emit_ptr_word(UINT64_C(012345670123), ptr_frames);
        if (!pipe_transfer(&tty_in, &tty_in_seen, 1U, events) ||
            !pipe_transfer(&tty_out, &tty_out_seen, 1U, events) ||
            !pipe_transfer(
                ptr_frames.data(), ptr_seen.data(), ptr_seen.size(), events) ||
            !pipe_transfer(&ptp, &ptp_seen, 1U, events))
            std::abort();
        std::uint64_t ptr_word = 0U;
        for (const std::uint8_t frame : ptr_seen)
            ptr_word =
                ((ptr_word << 6U) |
                 static_cast<std::uint64_t>(frame & UINT8_C(0x3F))) &
                HHS_EXACT_PASS219_H36_WORD_MASK;
        run.result.v = {
            tty_in_seen,
            tty_out_seen,
            ptr_word,
            ptp_seen,
            2U,
            1U,
            1U,
            0U,
            0U,
            HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
            0U,
            3U
        };
        run.resource_events = events;
        return run;
    }

    const std::uint8_t in_byte =
        kind == NewWorkload::BoundaryConsoleAlternate
            ? static_cast<std::uint8_t>('Q')
            : static_cast<std::uint8_t>('P');
    const std::uint8_t out_byte =
        kind == NewWorkload::BoundaryConsoleAlternate
            ? static_cast<std::uint8_t>('R')
            : static_cast<std::uint8_t>('D');
    std::uint8_t in_seen = 0U;
    std::uint8_t out_seen = 0U;
    if (!pipe_transfer(&in_byte, &in_seen, 1U, events) ||
        !pipe_transfer(&out_byte, &out_seen, 1U, events))
        std::abort();

    if (kind == NewWorkload::MixedSchedulerIoUuo) {
        run.result.v = {
            in_seen,
            out_seen,
            2U,
            0U,
            0U,
            4U,
            4U,
            10U,
            HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
            0U,
            1U,
            4U
        };
        events += 4U;
    } else {
        run.result.v = {
            in_seen,
            out_seen,
            2U,
            0U,
            0U,
            1U,
            1U,
            7U,
            HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
            1U,
            1U,
            1U
        };
        ++events;
    }
    run.resource_events = events;
    return run;
}

const char *new_name(NewWorkload kind) {
    switch (kind) {
        case NewWorkload::AprPi: return "APR_PI_INTERRUPT_FOCUSED";
        case NewWorkload::RimBootstrap: return "RIM_BOOTSTRAP_FOCUSED";
        case NewWorkload::MixedConsoleBinary:
            return "MIXED_CONSOLE_BINARY_IO";
        case NewWorkload::MixedSchedulerIoUuo:
            return "MIXED_SCHEDULER_IO_UUO";
        case NewWorkload::BoundaryConsoleAlternate:
            return "BOUNDARY_CONSOLE_ALTERNATE";
    }
    return "UNKNOWN";
}

std::array<FrozenResidentSpec, 4> frozen_specs() {
    const std::uint32_t h36_working_bytes =
        static_cast<std::uint32_t>(
            sizeof(HHSExactPass219H36VMStateV1) +
            sizeof(HHSExactPass219H36MonitorStateV1) +
            sizeof(HHSExactPass219H36MonitorReceiptV1) * 2U);
    const std::uint32_t linux_working_bytes =
        static_cast<std::uint32_t>(sizeof(CandidateRun));

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
            7U, 8U, h36_working_bytes, linux_working_bytes,
            8U, 12U, 1U,
            "tfuz(1iI-X7B1jH408c-6n60BAOrYQQLMA3-*O<L+kOiKL<QZ4)ABrcd3BVdRQ!70bDSzLKw2nl2cNHJzYg>(2H>gcld8e8eKYQ/JDf(pnFIan>AVJbRsT01p/8eHt(L5X?fzNw)5El3?D9RG+U!za81-</XVI-Mni(qEzL?6B+/hBs9vck0O8UPIcKHn1gnXA2ZU7eZ+pS1(u2Ujj!E5+wG"
        },
        {
            "BINARY_IO_FOCUSED",
            UINT64_C(21509979554),
            UINT64_C(1456447110141201574),
            UINT64_C(23073),
            UINT64_C(109553),
            7U, 8U, h36_working_bytes, linux_working_bytes,
            4U, 10U, 1U,
            "jei)gdf/PEAs9MILOtuHOQXpnUt*Tf47PD?zy3gwy!tZT5)Int*XpA4SKMXYcEMAgr+k>Mtyimln!(PDfX3E?49PUHB2a12t5X2dOb+HT/P6z+x8(124)bX(CZXaW3<-RU(mRMEWy77XtVOU-cU<U?YXV9(aw3hQtZGE-J*6M9Nmc<kBcaIq3JCDgQ48pBMyi(O<qZy1!ag6VRtLP>WnnApX"
        },
        {
            "MONITOR_CONTROL_FOCUSED",
            UINT64_C(41886677838),
            UINT64_C(2318081696571468614),
            UINT64_C(19156),
            UINT64_C(501),
            7U, 8U, h36_working_bytes, linux_working_bytes,
            4U, 4U, 2U,
            "q(IxvVjjUvereKtdppA>uu1yyYAvB3fxjJWuY!QVYp1+UiLu9IdfM+rk1m/L7bbkCTUP3ij1nlJiPvfoK)n34B1t!JNsJC>Plr96YIz*ryA9EJ(RHPeJ?bZJgvj77NPrdCO6r2Sr!WI/T!GSFi!jWlIQCPctCXujdyOXett3<ojTipoRPYVdO*+tNp4c/vTx3H8o1N3wiforBk5--61?!Q76"
        }
    }};
}

void prepare_selection(
    std::uint64_t workload,
    std::uint64_t semantic,
    std::uint64_t h36_ns,
    std::uint64_t linux_ns,
    std::uint32_t samples,
    std::uint32_t rounds,
    std::uint32_t h36_bytes,
    std::uint32_t linux_bytes,
    std::uint32_t h36_events,
    std::uint32_t linux_events,
    HHSExactPass219H36StackCandidateEvidenceV1 &h36,
    HHSExactPass219H36StackCandidateEvidenceV1 &linux,
    HHSExactPass219H36StackSelectionV1 &selection
) {
    if (hhs_exact_pass219_h36_stack_candidate_prepare(
            1U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
            workload, semantic, h36_ns, samples, rounds,
            h36_bytes, h36_events, 1U, &h36) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_candidate_prepare(
            2U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
            workload, semantic, linux_ns, samples, rounds,
            linux_bytes, linux_events, 1U, &linux) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_select(
            &h36, &linux, &selection) != HHS_EXACT_STATUS_OK)
        std::abort();
}

Resident measure_new(NewWorkload kind) {
    Resident resident{};
    resident.name = new_name(kind);
    const CandidateRun h36_probe = run_h36(kind);
    const CandidateRun linux_probe = run_linux(kind);
    if (h36_probe.workload_signature36 !=
            linux_probe.workload_signature36 ||
        !semantic_equal(h36_probe.result, linux_probe.result))
        std::abort();

    const std::uint64_t semantic =
        semantic_signature64(h36_probe.result);
    if (semantic != semantic_signature64(linux_probe.result))
        std::abort();

    const auto h36_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kStackRounds; ++i) {
            const CandidateRun r = run_h36(kind);
            if (r.workload_signature36 !=
                    h36_probe.workload_signature36 ||
                !semantic_equal(r.result, h36_probe.result))
                std::abort();
            checksum ^= semantic_signature64(r.result);
        }
        g_sink ^= checksum;
    };
    const auto linux_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kStackRounds; ++i) {
            const CandidateRun r = run_linux(kind);
            if (r.workload_signature36 !=
                    linux_probe.workload_signature36 ||
                !semantic_equal(r.result, linux_probe.result))
                std::abort();
            checksum ^= semantic_signature64(r.result);
        }
        g_sink ^= checksum;
    };

    resident.h36_median_ns = median_ns(h36_sample, kStackSamples);
    resident.linux_median_ns = median_ns(linux_sample, kStackSamples);
    prepare_selection(
        h36_probe.workload_signature36,
        semantic,
        resident.h36_median_ns,
        resident.linux_median_ns,
        static_cast<std::uint32_t>(kStackSamples),
        kStackRounds,
        h36_probe.working_state_bytes,
        linux_probe.working_state_bytes,
        h36_probe.resource_events,
        linux_probe.resource_events,
        resident.h36,
        resident.linux,
        resident.selection);
    return resident;
}

void prepare_frozen(
    const FrozenResidentSpec &spec,
    Resident &resident
) {
    resident.name = spec.name;
    resident.h36_median_ns = spec.h36_median_ns;
    resident.linux_median_ns = spec.linux_median_ns;
    prepare_selection(
        spec.workload_signature36,
        spec.semantic_signature64,
        spec.h36_median_ns,
        spec.linux_median_ns,
        spec.samples,
        spec.rounds,
        spec.h36_working_bytes,
        spec.linux_working_bytes,
        spec.h36_resource_events,
        spec.linux_resource_events,
        resident.h36,
        resident.linux,
        resident.selection);
    if (resident.selection.selected_candidate_id !=
            spec.selected_candidate ||
        std::strcmp(
            resident.selection.selected_vector_key216,
            spec.vector_key216) != 0)
        std::abort();
}

void require_lookup(
    const HHSExactPass219H36StackCacheV1 &cache,
    const HHSExactPass219H36StackSelectionV1 &selection
) {
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
        receipt.cache_hit != 1U ||
        receipt.exact_replayable != 1U ||
        receipt.stale_signature_rejected != 1U)
        std::abort();
}

HHSExactPass219H36StackCacheV1 build_occ1(
    const HHSExactPass219H36StackSelectionV1 &selection
) {
    HHSExactPass219H36StackCacheV1 cache{};
    if (hhs_exact_pass219_h36_stack_cache_init(&cache) !=
            HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_cache_store(
            &cache, &selection) != HHS_EXACT_STATUS_OK)
        std::abort();
    return cache;
}

HHSExactPass219H36StackCacheV1 build_occ4(
    const std::array<Resident, kResidents> &residents,
    std::size_t target
) {
    HHSExactPass219H36StackCacheV1 cache{};
    if (hhs_exact_pass219_h36_stack_cache_init(&cache) !=
        HHS_EXACT_STATUS_OK)
        std::abort();
    for (std::size_t n = 0U; n < 4U; ++n) {
        const std::size_t i = (target + n) % residents.size();
        if (hhs_exact_pass219_h36_stack_cache_store(
                &cache, &residents[i].selection) != HHS_EXACT_STATUS_OK)
            std::abort();
    }
    return cache;
}

void prove_occ8_isolation(
    const HHSExactPass219H36StackCacheV1 &cache,
    const std::array<Resident, kResidents> &residents
) {
    for (std::size_t i = 0U; i < residents.size(); ++i) {
        require_lookup(cache, residents[i].selection);
        require_lookup(cache, residents[i].selection);

        HHSExactPass219H36StackSelectionV1 out{};
        HHSExactPass219H36StackCacheReceiptV1 receipt{};
        if (hhs_exact_pass219_h36_stack_cache_lookup(
                &cache,
                residents[i].selection.workload_signature36,
                residents[i].selection.semantic_result_signature64 ^
                    UINT64_C(1),
                residents[i].selection.selected_vector_key216,
                &out,
                &receipt) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
            std::abort();

        char wrong_key[HHS_EXACT_UQCEL_HASH216_STRLEN];
        std::memcpy(
            wrong_key,
            residents[i].selection.selected_vector_key216,
            sizeof(wrong_key));
        wrong_key[0] =
            wrong_key[0] == HHS_EXACT_HASH72_ALPHABET[0]
                ? HHS_EXACT_HASH72_ALPHABET[1]
                : HHS_EXACT_HASH72_ALPHABET[0];
        if (hhs_exact_pass219_h36_stack_cache_lookup(
                &cache,
                residents[i].selection.workload_signature36,
                residents[i].selection.semantic_result_signature64,
                wrong_key,
                &out,
                &receipt) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
            std::abort();

        const std::size_t other = (i + 1U) % residents.size();
        if (hhs_exact_pass219_h36_stack_cache_lookup(
                &cache,
                residents[i].selection.workload_signature36,
                residents[other].selection.semantic_result_signature64,
                residents[other].selection.selected_vector_key216,
                &out,
                &receipt) != HHS_EXACT_STATUS_INVARIANT_FAILURE)
            std::abort();
    }

    char unrelated[HHS_EXACT_UQCEL_HASH216_STRLEN];
    for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        unrelated[i] = HHS_EXACT_HASH72_ALPHABET[0];
    unrelated[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    HHSExactPass219H36StackSelectionV1 out{};
    HHSExactPass219H36StackCacheReceiptV1 receipt{};
    if (hhs_exact_pass219_h36_stack_cache_lookup(
            &cache, UINT64_C(1), UINT64_C(1), unrelated,
            &out, &receipt) != HHS_EXACT_STATUS_RANGE_ERROR)
        std::abort();

    HHSExactPass219H36StackCacheV1 dup_seq = cache;
    dup_seq.entries[7].sequence = dup_seq.entries[0].sequence;
    if (hhs_exact_pass219_h36_stack_cache_validate(&dup_seq) !=
        HHS_EXACT_STATUS_INVARIANT_FAILURE)
        std::abort();

    HHSExactPass219H36StackCacheV1 dup_identity = cache;
    dup_identity.entries[7].selection =
        dup_identity.entries[0].selection;
    if (hhs_exact_pass219_h36_stack_cache_validate(&dup_identity) !=
        HHS_EXACT_STATUS_INVARIANT_FAILURE)
        std::abort();

    HHSExactPass219H36StackCacheV1 partial = cache;
    partial.entries[7].selection.workload_signature36 =
        partial.entries[0].selection.workload_signature36;
    if (hhs_exact_pass219_h36_stack_cache_validate(&partial) !=
        HHS_EXACT_STATUS_INVARIANT_FAILURE)
        std::abort();
}

CacheMeasurement measure_cache(
    const Resident &resident,
    const HHSExactPass219H36StackCacheV1 &occ1,
    const HHSExactPass219H36StackCacheV1 &occ4,
    const HHSExactPass219H36StackCacheV1 &occ8
) {
    CacheMeasurement m{};

    const auto fresh = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kCacheRounds; ++i) {
            HHSExactPass219H36StackSelectionV1 selection{};
            if (hhs_exact_pass219_h36_stack_select(
                    &resident.h36,
                    &resident.linux,
                    &selection) != HHS_EXACT_STATUS_OK ||
                hhs_exact_pass219_h36_stack_cache_hit_equals_fresh(
                    &selection,
                    &resident.selection) != HHS_EXACT_STATUS_OK)
                std::abort();
            checksum ^= selection.speedup_x1000;
        }
        g_sink ^= checksum;
    };
    const auto lookup1 = [&]() {
        for (std::uint32_t i = 0U; i < kCacheRounds; ++i)
            require_lookup(occ1, resident.selection);
    };
    const auto lookup4 = [&]() {
        for (std::uint32_t i = 0U; i < kCacheRounds; ++i)
            require_lookup(occ4, resident.selection);
    };
    const auto lookup8 = [&]() {
        for (std::uint32_t i = 0U; i < kCacheRounds; ++i)
            require_lookup(occ8, resident.selection);
    };

    for (std::size_t repeat = 0U;
         repeat < kCalibrationRepeats;
         ++repeat) {
        if ((repeat & 1U) == 0U) {
            m.fresh_repeat_ns[repeat] =
                median_ns(fresh, kCacheSamples);
            m.occ1_repeat_ns[repeat] =
                median_ns(lookup1, kCacheSamples);
            m.occ4_repeat_ns[repeat] =
                median_ns(lookup4, kCacheSamples);
            m.occ8_repeat_ns[repeat] =
                median_ns(lookup8, kCacheSamples);
        } else {
            m.occ8_repeat_ns[repeat] =
                median_ns(lookup8, kCacheSamples);
            m.occ4_repeat_ns[repeat] =
                median_ns(lookup4, kCacheSamples);
            m.occ1_repeat_ns[repeat] =
                median_ns(lookup1, kCacheSamples);
            m.fresh_repeat_ns[repeat] =
                median_ns(fresh, kCacheSamples);
        }

        if (m.fresh_repeat_ns[repeat] == 0U ||
            m.occ1_repeat_ns[repeat] == 0U ||
            m.occ4_repeat_ns[repeat] == 0U ||
            m.occ8_repeat_ns[repeat] == 0U)
            std::abort();

        m.fresh_total_ns += m.fresh_repeat_ns[repeat];
        m.occ1_total_ns += m.occ1_repeat_ns[repeat];
        m.occ4_total_ns += m.occ4_repeat_ns[repeat];
        m.occ8_total_ns += m.occ8_repeat_ns[repeat];
        if (m.occ8_repeat_ns[repeat] <
            m.fresh_repeat_ns[repeat])
            ++m.beneficial_repeat_count;
    }

    {
        auto fresh_sorted = m.fresh_repeat_ns;
        auto occ1_sorted = m.occ1_repeat_ns;
        auto occ4_sorted = m.occ4_repeat_ns;
        auto occ8_sorted = m.occ8_repeat_ns;
        std::sort(fresh_sorted.begin(), fresh_sorted.end());
        std::sort(occ1_sorted.begin(), occ1_sorted.end());
        std::sort(occ4_sorted.begin(), occ4_sorted.end());
        std::sort(occ8_sorted.begin(), occ8_sorted.end());
        m.fresh_ns = fresh_sorted[kCalibrationRepeats / 2U];
        m.occ1_ns = occ1_sorted[kCalibrationRepeats / 2U];
        m.occ4_ns = occ4_sorted[kCalibrationRepeats / 2U];
        m.occ8_ns = occ8_sorted[kCalibrationRepeats / 2U];
    }

    m.aggregate_benefit =
        m.occ8_total_ns < m.fresh_total_ns;
    m.repeat_stability_pass =
        m.beneficial_repeat_count >=
            kRequiredBeneficialRepeats &&
        m.aggregate_benefit;
    m.occ8_faster_than_fresh = m.repeat_stability_pass;
    m.occ8_vs_fresh_x1000 =
        ratio_x1000(m.fresh_total_ns, m.occ8_total_ns);
    m.occ8_vs_occ1_x1000 =
        ratio_x1000(m.occ8_total_ns, m.occ1_total_ns);
    m.occ8_vs_occ4_x1000 =
        ratio_x1000(m.occ8_total_ns, m.occ4_total_ns);
    return m;
}

} // namespace

int main(int argc, char **argv) {
#if !defined(__linux__) || !defined(__x86_64__)
    std::cerr << "capacity-8 benchmark requires Linux x86_64\n";
    return 2;
#else
    std::array<Resident, kResidents> residents{};
    const auto frozen = frozen_specs();
    for (std::size_t i = 0U; i < frozen.size(); ++i)
        prepare_frozen(frozen[i], residents[i]);

    const std::array<NewWorkload, kNewWorkloads> new_kinds = {
        NewWorkload::AprPi,
        NewWorkload::RimBootstrap,
        NewWorkload::MixedConsoleBinary,
        NewWorkload::MixedSchedulerIoUuo
    };
    for (std::size_t i = 0U; i < new_kinds.size(); ++i)
        residents[i + 4U] = measure_new(new_kinds[i]);

    for (std::size_t i = 0U; i < residents.size(); ++i) {
        for (std::size_t j = i + 1U; j < residents.size(); ++j) {
            if (residents[i].selection.workload_signature36 ==
                residents[j].selection.workload_signature36)
                return 3;
        }
    }

    HHSExactPass219H36StackCacheV1 occ8{};
    if (hhs_exact_pass219_h36_stack_cache_init(&occ8) !=
        HHS_EXACT_STATUS_OK)
        return 4;
    for (const auto &resident : residents) {
        if (hhs_exact_pass219_h36_stack_cache_store(
                &occ8, &resident.selection) != HHS_EXACT_STATUS_OK)
            return 5;
    }
    if (occ8.entry_count != 8U ||
        occ8.next_sequence != UINT64_C(9) ||
        hhs_exact_pass219_h36_stack_cache_validate(&occ8) !=
            HHS_EXACT_STATUS_OK)
        return 6;

    prove_occ8_isolation(occ8, residents);

    const std::uint32_t count_before = occ8.entry_count;
    const std::uint64_t seq_before = occ8.next_sequence;
    if (hhs_exact_pass219_h36_stack_cache_store(
            &occ8, &residents[3].selection) != HHS_EXACT_STATUS_OK ||
        occ8.entry_count != count_before ||
        occ8.next_sequence != seq_before)
        return 7;

    const Resident boundary =
        measure_new(NewWorkload::BoundaryConsoleAlternate);
    if (hhs_exact_pass219_h36_stack_cache_store(
            &occ8,
            &boundary.selection) != HHS_EXACT_STATUS_BUFFER_TOO_SMALL)
        return 8;
    if (occ8.entry_count != 8U ||
        occ8.next_sequence != UINT64_C(9))
        return 9;

    std::array<CacheMeasurement, kResidents> measurements{};
    bool all_repeat_stability_pass = true;
    for (std::size_t i = 0U; i < residents.size(); ++i) {
        const auto occ1 = build_occ1(residents[i].selection);
        const auto occ4 = build_occ4(residents, i);
        require_lookup(occ1, residents[i].selection);
        require_lookup(occ4, residents[i].selection);
        require_lookup(occ8, residents[i].selection);
        measurements[i] =
            measure_cache(residents[i], occ1, occ4, occ8);
        all_repeat_stability_pass =
            all_repeat_stability_pass &&
            measurements[i].repeat_stability_pass;
    }

    std::ostream *out = &std::cout;
    std::ofstream file;
    if (argc > 1) {
        file.open(argv[1], std::ios::out | std::ios::trunc);
        if (!file)
            return 10;
        out = &file;
    }

    *out
        << "{\n"
        << "  \"schema\": \"HHS_PASS219_H36_STACK_CACHE_CAPACITY8_1_14_BENCHMARK_V1\",\n"
        << "  \"platform\": {\"linux\": true, \"x86_64\": true, "
        << "\"stack_samples\": " << kStackSamples << ", "
        << "\"stack_rounds_per_sample\": " << kStackRounds << ", "
        << "\"cache_samples\": " << kCacheSamples << ", "
        << "\"cache_rounds_per_sample\": " << kCacheRounds << ", "
        << "\"calibration_repeats\": " << kCalibrationRepeats << ", "
        << "\"required_beneficial_repeats\": "
        << kRequiredBeneficialRepeats << "},\n"
        << "  \"cache\": {\"capacity\": 8, \"resident_entries\": 8, "
        << "\"next_sequence\": " << occ8.next_sequence << "},\n"
        << "  \"boundary\": {\n"
        << "    \"ninth_store_workload\": \""
        << boundary.name << "\",\n"
        << "    \"ninth_store_workload_signature36\": "
        << boundary.selection.workload_signature36 << ",\n"
        << "    \"ninth_store_result\": \"BUFFER_TOO_SMALL\",\n"
        << "    \"full_capacity_idempotent_existing_store_ok\": true,\n"
        << "    \"full_capacity_count_sequence_unchanged\": true\n"
        << "  },\n"
        << "  \"correctness\": {\n"
        << "    \"eight_simultaneous_entries_valid\": true,\n"
        << "    \"all_exact_lookups_equal_fresh\": true,\n"
        << "    \"cross_signature_hits_rejected\": true,\n"
        << "    \"wrong_semantic_signature_rejected\": true,\n"
        << "    \"wrong_vector_key_rejected\": true,\n"
        << "    \"unrelated_identity_range_error\": true,\n"
        << "    \"duplicate_sequence_rejected\": true,\n"
        << "    \"duplicate_identity_tamper_rejected\": true,\n"
        << "    \"partial_identity_tamper_rejected\": true\n"
        << "  },\n"
        << "  \"residents\": [\n";

    for (std::size_t i = 0U; i < residents.size(); ++i) {
        const auto &r = residents[i];
        const auto &m = measurements[i];
        *out
            << "    {\n"
            << "      \"name\": \"" << r.name << "\",\n"
            << "      \"workload_signature36\": "
            << r.selection.workload_signature36 << ",\n"
            << "      \"semantic_result_signature64\": "
            << r.selection.semantic_result_signature64 << ",\n"
            << "      \"h36_median_ns\": " << r.h36_median_ns << ",\n"
            << "      \"linux_median_ns\": " << r.linux_median_ns << ",\n"
            << "      \"selected_candidate_id\": "
            << r.selection.selected_candidate_id << ",\n"
            << "      \"selected_vector_key216\": \""
            << r.selection.selected_vector_key216 << "\",\n"
            << "      \"entry_sequence\": "
            << occ8.entries[i].sequence << ",\n"
            << "      \"fresh_selection_median_ns\": "
            << m.fresh_ns << ",\n"
            << "      \"occupancy1_lookup_median_ns\": "
            << m.occ1_ns << ",\n"
            << "      \"occupancy4_lookup_median_ns\": "
            << m.occ4_ns << ",\n"
            << "      \"occupancy8_lookup_median_ns\": "
            << m.occ8_ns << ",\n"
            << "      \"fresh_selection_total_ns\": "
            << m.fresh_total_ns << ",\n"
            << "      \"occupancy1_lookup_total_ns\": "
            << m.occ1_total_ns << ",\n"
            << "      \"occupancy4_lookup_total_ns\": "
            << m.occ4_total_ns << ",\n"
            << "      \"occupancy8_lookup_total_ns\": "
            << m.occ8_total_ns << ",\n"
            << "      \"beneficial_repeat_count\": "
            << m.beneficial_repeat_count << ",\n"
            << "      \"aggregate_benefit\": "
            << (m.aggregate_benefit ? "true" : "false") << ",\n"
            << "      \"repeat_stability_pass\": "
            << (m.repeat_stability_pass ? "true" : "false") << ",\n"
            << "      \"occupancy8_faster_than_fresh\": "
            << (m.occ8_faster_than_fresh ? "true" : "false") << ",\n"
            << "      \"occupancy8_vs_fresh_ratio_x1000\": "
            << m.occ8_vs_fresh_x1000 << ",\n"
            << "      \"occupancy8_vs_occupancy1_ratio_x1000\": "
            << m.occ8_vs_occ1_x1000 << ",\n"
            << "      \"occupancy8_vs_occupancy4_ratio_x1000\": "
            << m.occ8_vs_occ4_x1000 << ",\n"
            << "      \"repeat_measurements\": [\n"
            << "        {\"repeat\": 1, \"measurement_order\": \"FRESH_OCC1_OCC4_OCC8\", \"fresh_ns\": "
            << m.fresh_repeat_ns[0] << ", \"occupancy1_ns\": "
            << m.occ1_repeat_ns[0] << ", \"occupancy4_ns\": "
            << m.occ4_repeat_ns[0] << ", \"occupancy8_ns\": "
            << m.occ8_repeat_ns[0] << "},\n"
            << "        {\"repeat\": 2, \"measurement_order\": \"OCC8_OCC4_OCC1_FRESH\", \"fresh_ns\": "
            << m.fresh_repeat_ns[1] << ", \"occupancy1_ns\": "
            << m.occ1_repeat_ns[1] << ", \"occupancy4_ns\": "
            << m.occ4_repeat_ns[1] << ", \"occupancy8_ns\": "
            << m.occ8_repeat_ns[1] << "},\n"
            << "        {\"repeat\": 3, \"measurement_order\": \"FRESH_OCC1_OCC4_OCC8\", \"fresh_ns\": "
            << m.fresh_repeat_ns[2] << ", \"occupancy1_ns\": "
            << m.occ1_repeat_ns[2] << ", \"occupancy4_ns\": "
            << m.occ4_repeat_ns[2] << ", \"occupancy8_ns\": "
            << m.occ8_repeat_ns[2] << "},\n"
            << "        {\"repeat\": 4, \"measurement_order\": \"OCC8_OCC4_OCC1_FRESH\", \"fresh_ns\": "
            << m.fresh_repeat_ns[3] << ", \"occupancy1_ns\": "
            << m.occ1_repeat_ns[3] << ", \"occupancy4_ns\": "
            << m.occ4_repeat_ns[3] << ", \"occupancy8_ns\": "
            << m.occ8_repeat_ns[3] << "},\n"
            << "        {\"repeat\": 5, \"measurement_order\": \"FRESH_OCC1_OCC4_OCC8\", \"fresh_ns\": "
            << m.fresh_repeat_ns[4] << ", \"occupancy1_ns\": "
            << m.occ1_repeat_ns[4] << ", \"occupancy4_ns\": "
            << m.occ4_repeat_ns[4] << ", \"occupancy8_ns\": "
            << m.occ8_repeat_ns[4] << "}\n"
            << "      ]\n"
            << "    }" << (i + 1U == residents.size() ? "\n" : ",\n");
    }

    *out
        << "  ],\n"
        << "  \"measurement\": {\n"
        << "    \"gate_kind\": \"EXACT_INTEGER_REPEAT_STABILITY\",\n"
        << "    \"calibration_repeats\": "
        << kCalibrationRepeats << ",\n"
        << "    \"required_beneficial_repeats\": "
        << kRequiredBeneficialRepeats << ",\n"
        << "    \"aggregate_requires_occupancy8_total_lt_fresh_total\": true,\n"
        << "    \"one_shot_boolean_authoritative\": false,\n"
        << "    \"all_repeat_stability_pass\": "
        << (all_repeat_stability_pass ? "true" : "false") << "\n"
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
#undef MBIT
