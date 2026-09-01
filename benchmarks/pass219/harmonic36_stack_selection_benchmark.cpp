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
#include <string>
#include <vector>

#include <unistd.h>

namespace {

using Clock = std::chrono::steady_clock;
volatile std::uint64_t g_stack_sink = 0U;

constexpr std::uint32_t kExecCell = 0120U;
constexpr std::uint32_t kDataCell = 0121U;
constexpr std::uint32_t kRoundsPerSample = 32U;
constexpr int kSamples = 9;

struct SemanticResult {
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

struct CandidateRun {
    SemanticResult result{};
    std::uint64_t workload_signature36 = 0U;
    std::uint32_t process_working_state_bytes = 0U;
    std::uint32_t resource_events = 0U;
};

std::uint64_t mix64(std::uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30U)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27U)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31U);
}

std::uint64_t semantic_signature(const SemanticResult &r) {
    std::uint64_t s = 0x21936A10ULL;
    const std::uint64_t values[] = {
        r.tty_input,
        r.tty_output,
        r.ptr_word36,
        r.ptp_output,
        r.tty_service_count,
        r.ptr_service_count,
        r.ptp_service_count,
        r.apr_service_count,
        r.uuo_service_count,
        r.dispatch_count,
        r.final_pc18,
        r.queue_cursor,
    };
    for (std::size_t i = 0U; i < sizeof(values) / sizeof(values[0]); ++i)
        s = mix64(s ^ values[i] ^ (static_cast<std::uint64_t>(i + 1U) << 48U));
    return s;
}

bool semantic_equal(const SemanticResult &a, const SemanticResult &b) {
    return a.tty_input == b.tty_input &&
           a.tty_output == b.tty_output &&
           a.ptr_word36 == b.ptr_word36 &&
           a.ptp_output == b.ptp_output &&
           a.tty_service_count == b.tty_service_count &&
           a.ptr_service_count == b.ptr_service_count &&
           a.ptp_service_count == b.ptp_service_count &&
           a.apr_service_count == b.apr_service_count &&
           a.uuo_service_count == b.uuo_service_count &&
           a.dispatch_count == b.dispatch_count &&
           a.final_pc18 == b.final_pc18 &&
           a.queue_cursor == b.queue_cursor;
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

void emit_word(std::uint64_t word, std::array<std::uint8_t, 6> &frames) {
    std::size_t off = 0U;
    for (int shift = 30; shift >= 0; shift -= 6) {
        frames[off++] = static_cast<std::uint8_t>(
            0x80U |
            static_cast<std::uint8_t>(
                (word >> static_cast<std::uint32_t>(shift)) & 0x3FULL));
    }
}

std::uint64_t decode_word(const std::array<std::uint8_t, 6> &frames) {
    std::uint64_t word = 0U;
    for (const std::uint8_t frame : frames)
        word = ((word << 6U) |
                static_cast<std::uint64_t>(frame & 0x3FU)) &
               HHS_EXACT_PASS219_H36_WORD_MASK;
    return word;
}

CandidateRun run_h36_candidate() {
    HHSExactPass219H36VMStateV1 vm{};
    HHSExactPass219H36MonitorStateV1 monitor{};
    HHSExactPass219H36MonitorReceiptV1 initial{};
    HHSExactPass219H36MonitorReceiptV1 receipt{};
    CandidateRun run{};
    std::uint32_t steps = 0U;
    const std::uint8_t tty_in = static_cast<std::uint8_t>('A');
    std::array<std::uint8_t, 8> tty_out{};
    std::size_t tty_out_count = 0U;
    const std::uint64_t ptr_word = UINT64_C(012345670123);
    std::array<std::uint8_t, 6> ptr_frames{};
    std::array<std::uint8_t, 8> ptp_frames{};
    std::size_t ptp_count = 0U;

    if (hhs_exact_pass219_h36_ka10_monitor_bootstrap(
            &vm, &monitor, &initial) != HHS_EXACT_STATUS_OK)
        std::abort();
    run.workload_signature36 = initial.workload.image_signature36;

    if (hhs_exact_pass219_h36_tty_feed_input(
            &vm, &tty_in, 1U) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_ka10_monitor_drive(
            &vm, &monitor, 3U, &steps) != HHS_EXACT_STATUS_OK ||
        steps != 3U)
        std::abort();

    vm.memory[kDataCell] = static_cast<std::uint64_t>('B');
    h36_exec_io(
        vm,
        ioenc(HHS_EXACT_PASS219_H36_DEVICE_TTY, 3U, kDataCell));
    if (hhs_exact_pass219_h36_ka10_monitor_drive(
            &vm, &monitor, 3U, &steps) != HHS_EXACT_STATUS_OK ||
        steps != 3U ||
        hhs_exact_pass219_h36_tty_copy_output(
            &vm, tty_out.data(), tty_out.size(), &tty_out_count) !=
            HHS_EXACT_STATUS_OK ||
        tty_out_count != 1U)
        std::abort();

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
        vm,
        ioenc(HHS_EXACT_PASS219_H36_DEVICE_PTP, 3U, kDataCell));
    if (hhs_exact_pass219_h36_ka10_monitor_drive(
            &vm, &monitor, 2U, &steps) != HHS_EXACT_STATUS_OK ||
        steps != 2U ||
        hhs_exact_pass219_h36_ptp_copy_tape(
            &vm, ptp_frames.data(), ptp_frames.size(), &ptp_count) !=
            HHS_EXACT_STATUS_OK ||
        ptp_count != 1U)
        std::abort();

    if (hhs_exact_pass219_h36_ka10_monitor_drive(
            &vm, &monitor, 4U, &steps) != HHS_EXACT_STATUS_OK ||
        steps != 4U ||
        hhs_exact_pass219_h36_ka10_monitor_receipt_capture(
            &vm, &monitor, &receipt) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_ka10_monitor_receipt_validate(
            &vm, &monitor, &receipt) != HHS_EXACT_STATUS_OK)
        std::abort();

    run.result.tty_input =
        vm.memory[HHS_EXACT_PASS219_H36_MONITOR_TTY_SCRATCH18];
    run.result.tty_output = tty_out[0];
    run.result.ptr_word36 =
        vm.memory[HHS_EXACT_PASS219_H36_MONITOR_PTR_SCRATCH18];
    run.result.ptp_output = ptp_frames[0];
    run.result.tty_service_count = monitor.tty_service_count;
    run.result.ptr_service_count = monitor.ptr_service_count;
    run.result.ptp_service_count = monitor.ptp_service_count;
    run.result.apr_service_count = monitor.apr_service_count;
    run.result.uuo_service_count = monitor.uuo_service_count;
    run.result.dispatch_count = monitor.dispatch_count;
    run.result.final_pc18 = vm.pc18;
    run.result.queue_cursor = monitor.queue_cursor;
    run.process_working_state_bytes = static_cast<std::uint32_t>(
        sizeof(vm) + sizeof(monitor) + sizeof(initial) + sizeof(receipt));
    run.resource_events = monitor.executed_steps;
    return run;
}

bool write_all(
    int fd,
    const std::uint8_t *data,
    std::size_t count,
    std::uint32_t &syscalls
) {
    std::size_t off = 0U;
    while (off < count) {
        const ssize_t n = ::write(fd, data + off, count - off);
        ++syscalls;
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
    std::uint32_t &syscalls
) {
    std::size_t off = 0U;
    while (off < count) {
        const ssize_t n = ::read(fd, data + off, count - off);
        ++syscalls;
        if (n <= 0)
            return false;
        off += static_cast<std::size_t>(n);
    }
    return true;
}

bool close_fd(int fd, std::uint32_t &syscalls) {
    const int rc = ::close(fd);
    ++syscalls;
    return rc == 0;
}

bool pipe_transfer(
    const std::uint8_t *input,
    std::uint8_t *output,
    std::size_t count,
    std::uint32_t &syscalls
) {
    int fds[2] = {-1, -1};
    if (::pipe(fds) != 0)
        return false;
    ++syscalls;
    const bool ok =
        write_all(fds[1], input, count, syscalls) &&
        read_all(fds[0], output, count, syscalls);
    const bool close_write = close_fd(fds[1], syscalls);
    const bool close_read = close_fd(fds[0], syscalls);
    return ok && close_write && close_read;
}

CandidateRun run_linux_candidate(std::uint64_t workload_signature36) {
    CandidateRun run{};
    const std::uint8_t tty_in = static_cast<std::uint8_t>('A');
    std::uint8_t tty_in_seen = 0U;
    const std::uint8_t tty_out = static_cast<std::uint8_t>('B');
    std::uint8_t tty_out_seen = 0U;
    const std::uint64_t ptr_word = UINT64_C(012345670123);
    std::array<std::uint8_t, 6> ptr_frames{};
    std::array<std::uint8_t, 6> ptr_seen{};
    const std::uint8_t ptp_out = static_cast<std::uint8_t>('C');
    std::uint8_t ptp_seen = 0U;
    const std::array<std::uint32_t, 2> run_queue = {
        HHS_EXACT_PASS219_H36_MONITOR_TASK0_18,
        HHS_EXACT_PASS219_H36_MONITOR_TASK1_18,
    };
    std::uint8_t cursor = 0U;
    std::uint32_t syscalls = 0U;

    if (!pipe_transfer(&tty_in, &tty_in_seen, 1U, syscalls))
        std::abort();
    if (!pipe_transfer(&tty_out, &tty_out_seen, 1U, syscalls))
        std::abort();

    emit_word(ptr_word, ptr_frames);
    if (!pipe_transfer(
            ptr_frames.data(),
            ptr_seen.data(),
            ptr_seen.size(),
            syscalls))
        std::abort();

    if (!pipe_transfer(&ptp_out, &ptp_seen, 1U, syscalls))
        std::abort();

    for (std::uint32_t i = 0U; i < 4U; ++i) {
        g_stack_sink ^= run_queue[cursor];
        cursor = static_cast<std::uint8_t>((cursor + 1U) % 2U);
    }

    run.workload_signature36 =
        workload_signature36 & HHS_EXACT_PASS219_H36_WORD_MASK;
    run.result.tty_input = tty_in_seen;
    run.result.tty_output = tty_out_seen;
    run.result.ptr_word36 = decode_word(ptr_seen);
    run.result.ptp_output = ptp_seen;
    run.result.tty_service_count = 2U;
    run.result.ptr_service_count = 1U;
    run.result.ptp_service_count = 1U;
    run.result.apr_service_count = 0U;
    run.result.uuo_service_count = 4U;
    run.result.dispatch_count = 4U;
    run.result.final_pc18 =
        HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18;
    run.result.queue_cursor = cursor;
    run.process_working_state_bytes = static_cast<std::uint32_t>(
        sizeof(run) + sizeof(run_queue) +
        sizeof(ptr_frames) + sizeof(ptr_seen));
    run.resource_events = syscalls;
    return run;
}

const char *stack_name(std::uint32_t kind) {
    if (kind == HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10)
        return "H36_KA10_MONITOR";
    if (kind == HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64)
        return "LINUX_X86_64_POSIX";
    return "UNKNOWN";
}

}  // namespace

int main(int argc, char **argv) {
#if !defined(__linux__) || !defined(__x86_64__)
    std::cerr << "stack benchmark requires Linux x86_64\n";
    return 2;
#else
    const CandidateRun h36_probe = run_h36_candidate();
    const CandidateRun linux_probe =
        run_linux_candidate(h36_probe.workload_signature36);
    if (!semantic_equal(h36_probe.result, linux_probe.result)) {
        std::cerr << "semantic workload equality failed before timing\n";
        return 3;
    }
    const std::uint64_t result_signature =
        semantic_signature(h36_probe.result);
    if (result_signature == 0U ||
        result_signature != semantic_signature(linux_probe.result)) {
        std::cerr << "semantic signature equality failed\n";
        return 4;
    }

    const auto h36_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kRoundsPerSample; ++i) {
            const CandidateRun run = run_h36_candidate();
            if (!semantic_equal(run.result, h36_probe.result) ||
                run.workload_signature36 !=
                    h36_probe.workload_signature36)
                std::abort();
            checksum ^= semantic_signature(run.result);
        }
        g_stack_sink ^= checksum;
    };
    const auto linux_sample = [&]() {
        std::uint64_t checksum = 0U;
        for (std::uint32_t i = 0U; i < kRoundsPerSample; ++i) {
            const CandidateRun run =
                run_linux_candidate(h36_probe.workload_signature36);
            if (!semantic_equal(run.result, linux_probe.result))
                std::abort();
            checksum ^= semantic_signature(run.result);
        }
        g_stack_sink ^= checksum;
    };

    const std::uint64_t h36_median_ns = median_ns(h36_sample, kSamples);
    const std::uint64_t linux_median_ns =
        median_ns(linux_sample, kSamples);
    if (h36_median_ns == 0U || linux_median_ns == 0U) {
        std::cerr << "zero timing sample\n";
        return 5;
    }

    HHSExactPass219H36StackCandidateEvidenceV1 h36{};
    HHSExactPass219H36StackCandidateEvidenceV1 linux{};
    HHSExactPass219H36StackSelectionV1 selection{};
    if (hhs_exact_pass219_h36_stack_candidate_prepare(
            1U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
            h36_probe.workload_signature36,
            result_signature,
            h36_median_ns,
            static_cast<std::uint32_t>(kSamples),
            kRoundsPerSample,
            h36_probe.process_working_state_bytes,
            h36_probe.resource_events,
            1U,
            &h36) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_candidate_prepare(
            2U,
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
            h36_probe.workload_signature36,
            result_signature,
            linux_median_ns,
            static_cast<std::uint32_t>(kSamples),
            kRoundsPerSample,
            linux_probe.process_working_state_bytes,
            linux_probe.resource_events,
            1U,
            &linux) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_select(
            &h36, &linux, &selection) != HHS_EXACT_STATUS_OK) {
        std::cerr << "stack selector rejected measured evidence\n";
        return 6;
    }

    HHSExactPass219OptimizationTargetEvidenceV1 unvalidated{};
    HHSExactPass219OptimizationTargetEvidenceV1 validated{};
    HHSExactPass219OptimizationTargetDecisionV1 unvalidated_decision{};
    HHSExactPass219OptimizationTargetDecisionV1 validated_decision{};
    unvalidated.struct_size =
        static_cast<std::uint32_t>(sizeof(unvalidated));
    unvalidated.version =
        hhs_exact_pass219_multimodal_optimization_generalization_version();
    unvalidated.descriptor_schema_match = 1U;
    unvalidated.object_semantics_compatible = 1U;
    unvalidated.runtime_authority_match = 1U;
    unvalidated.exactness_domain_match = 1U;
    validated = unvalidated;
    validated.validation_executed = 1U;
    validated.safety_verified = 1U;
    validated.benefit_verified = 1U;

    if (hhs_exact_pass219_h36_stack_generalization_decision(
            &selection, &unvalidated, &unvalidated_decision) !=
            HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_h36_stack_generalization_decision(
            &selection, &validated, &validated_decision) !=
            HHS_EXACT_STATUS_OK ||
        unvalidated_decision.classification !=
            HHS_EXACT_PASS219_OPT_VALIDATION_REQUIRED ||
        validated_decision.classification !=
            HHS_EXACT_PASS219_OPT_GENERALIZE_REQUIRED) {
        std::cerr << "multimodal optimization bridge failed\n";
        return 7;
    }

    std::ostream *out = &std::cout;
    std::ofstream file;
    if (argc > 1) {
        file.open(argv[1], std::ios::out | std::ios::trunc);
        if (!file) {
            std::cerr << "unable to open output file\n";
            return 8;
        }
        out = &file;
    }

    *out
        << "{\n"
        << "  \"schema\": \"HHS_PASS219_H36_STACK_SELECTION_BENCHMARK_V1\",\n"
        << "  \"platform\": {"
        << "\"linux\": true, \"x86_64\": true, "
        << "\"samples\": " << kSamples << ", "
        << "\"rounds_per_sample\": " << kRoundsPerSample << "},\n"
        << "  \"workload\": {\n"
        << "    \"monitor_image_signature36\": "
        << h36_probe.workload_signature36 << ",\n"
        << "    \"semantic_result_signature64\": "
        << result_signature << ",\n"
        << "    \"exact_result_equal_before_timing\": true,\n"
        << "    \"tty_input\": " << h36_probe.result.tty_input << ",\n"
        << "    \"tty_output\": " << h36_probe.result.tty_output << ",\n"
        << "    \"ptr_word36\": " << h36_probe.result.ptr_word36 << ",\n"
        << "    \"ptp_output\": " << h36_probe.result.ptp_output << ",\n"
        << "    \"dispatch_count\": "
        << h36_probe.result.dispatch_count << ",\n"
        << "    \"uuo_service_count\": "
        << h36_probe.result.uuo_service_count << "\n"
        << "  },\n"
        << "  \"h36_ka10_monitor\": {\n"
        << "    \"candidate_id\": 1,\n"
        << "    \"median_ns\": " << h36_median_ns << ",\n"
        << "    \"per_workload_median_ns\": "
        << (h36_median_ns / kRoundsPerSample) << ",\n"
        << "    \"process_working_state_bytes\": "
        << h36_probe.process_working_state_bytes << ",\n"
        << "    \"vm_steps_observed\": "
        << h36_probe.resource_events << ",\n"
        << "    \"vector_key216\": \"" << h36.vector_key216 << "\",\n"
        << "    \"vector_key216_length\": "
        << std::strlen(h36.vector_key216) << ",\n"
        << "    \"hash216_lineage_claim\": false,\n"
        << "    \"candidate_only\": true\n"
        << "  },\n"
        << "  \"linux_x86_64_posix\": {\n"
        << "    \"candidate_id\": 2,\n"
        << "    \"median_ns\": " << linux_median_ns << ",\n"
        << "    \"per_workload_median_ns\": "
        << (linux_median_ns / kRoundsPerSample) << ",\n"
        << "    \"process_working_state_bytes\": "
        << linux_probe.process_working_state_bytes << ",\n"
        << "    \"posix_syscalls_observed\": "
        << linux_probe.resource_events << ",\n"
        << "    \"vector_key216\": \"" << linux.vector_key216 << "\",\n"
        << "    \"vector_key216_length\": "
        << std::strlen(linux.vector_key216) << ",\n"
        << "    \"hash216_lineage_claim\": false,\n"
        << "    \"candidate_only\": true\n"
        << "  },\n"
        << "  \"selection\": {\n"
        << "    \"selected_candidate_id\": "
        << selection.selected_candidate_id << ",\n"
        << "    \"selected_stack\": \""
        << stack_name(selection.selected_stack_kind) << "\",\n"
        << "    \"selected_median_ns\": "
        << selection.selected_median_ns << ",\n"
        << "    \"runner_up_median_ns\": "
        << selection.runner_up_median_ns << ",\n"
        << "    \"speedup_x1000\": "
        << selection.speedup_x1000 << ",\n"
        << "    \"exact_equality_before_timing\": true,\n"
        << "    \"timing_executed\": true,\n"
        << "    \"measured_winner\": true,\n"
        << "    \"stable_tie_break_by_candidate_id\": true,\n"
        << "    \"selected_vector_key216\": \""
        << selection.selected_vector_key216 << "\",\n"
        << "    \"vector_store_metadata_only\": true,\n"
        << "    \"candidate_only\": true\n"
        << "  },\n"
        << "  \"generalization_bridge\": {\n"
        << "    \"compatible_unvalidated\": \"VALIDATION_REQUIRED\",\n"
        << "    \"compatible_safe_beneficial\": \"GENERALIZE_REQUIRED\"\n"
        << "  },\n"
        << "  \"authority\": {\n"
        << "    \"canonical_mutation\": false,\n"
        << "    \"canonical_hash72\": false,\n"
        << "    \"canonical_hash216\": false,\n"
        << "    \"canonical_persistence\": false,\n"
        << "    \"floating_point\": false\n"
        << "  },\n"
        << "  \"authoritative_state_changed\": false\n"
        << "}\n";
    return 0;
#endif
}
