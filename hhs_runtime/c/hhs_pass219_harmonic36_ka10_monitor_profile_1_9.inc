#include "hhs_pass219_harmonic36_ka10_monitor_profile_1_9.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define H36_MONITOR_PROFILE_ID UINT32_C(02190019)
#define H36_MONITOR_TAPE_CAPACITY 256U
#define H36_MONITOR_EXECUTION_LIMIT 32U

static uint32_t h36_monitor_control_bit(uint32_t machine_bit) {
    return UINT32_C(1) << (35U - machine_bit);
}

static uint32_t h36_monitor_select_channel(uint8_t channel) {
    return h36_monitor_control_bit(28U + (uint32_t)channel);
}

static HHSExactStatus h36_monitor_enc(
    uint16_t opcode,
    uint8_t ac,
    uint32_t address,
    uint64_t *out
) {
    return hhs_exact_pass219_h36_instruction_encode(
        opcode, ac, 0U, 0U, address, out);
}

static HHSExactStatus h36_monitor_ioenc(
    uint8_t device,
    uint8_t function,
    uint32_t address,
    uint64_t *out
) {
    return hhs_exact_pass219_h36_io_instruction_encode(
        device, function, 0U, 0U, address, out);
}

static uint64_t h36_monitor_iowd(
    uint32_t count,
    uint32_t address_minus_one
) {
    uint32_t neg = ((UINT32_C(1) << 18U) - count) &
                   HHS_EXACT_PASS219_H36_HALF_MASK;
    return (((uint64_t)neg) << 18U) |
           ((uint64_t)address_minus_one &
            HHS_EXACT_PASS219_H36_HALF_MASK);
}

static void h36_monitor_emit_word(
    uint64_t word,
    uint8_t *frames,
    size_t *offset
) {
    int shift;
    for (shift = 30; shift >= 0; shift -= 6) {
        frames[*offset] = (uint8_t)(
            UINT8_C(0x80) |
            (uint8_t)((word >> (uint32_t)shift) & UINT64_C(0x3F))
        );
        *offset += 1U;
    }
}

static uint64_t h36_monitor_rotl36(uint64_t value, uint32_t shift) {
    uint32_t r = shift % 36U;
    value &= HHS_EXACT_PASS219_H36_WORD_MASK;
    if (r == 0U)
        return value;
    return ((value << r) | (value >> (36U - r))) &
           HHS_EXACT_PASS219_H36_WORD_MASK;
}

static uint64_t h36_monitor_signature36(
    const uint64_t *words,
    size_t count
) {
    size_t i;
    uint64_t signature = UINT64_C(021900190001) &
                         HHS_EXACT_PASS219_H36_WORD_MASK;
    for (i = 0U; i < count; ++i) {
        uint64_t term = h36_monitor_rotl36(
            words[i] & HHS_EXACT_PASS219_H36_WORD_MASK,
            (uint32_t)((i * 7U + 1U) % 36U)
        );
        signature = (signature ^ term ^
                     ((uint64_t)(i + 1U) * UINT64_C(01000001))) &
                    HHS_EXACT_PASS219_H36_WORD_MASK;
    }
    return signature;
}

static size_t h36_monitor_index(uint32_t address18) {
    return (size_t)(
        address18 - HHS_EXACT_PASS219_H36_MONITOR_IMAGE_START18);
}

HHSExactStatus hhs_exact_pass219_h36_ka10_monitor_image_build(
    uint64_t out_words[HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS]
) {
    HHSExactStatus status;
    uint32_t pi_control =
        h36_monitor_control_bit(25U) |
        h36_monitor_control_bit(28U) |
        h36_monitor_select_channel(1U) |
        h36_monitor_select_channel(2U) |
        h36_monitor_select_channel(3U) |
        h36_monitor_select_channel(4U);

    if (out_words == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(
        out_words,
        0,
        sizeof(uint64_t) *
            (size_t)HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS
    );

    status = h36_monitor_enc(
        UINT16_C(0254), 0U,
        HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
        &out_words[h36_monitor_index(UINT32_C(041))]);
    if (status != HHS_EXACT_STATUS_OK) return status;

    out_words[h36_monitor_index(UINT32_C(042))] =
        HHS_EXACT_PASS219_H36_MONITOR_TTY_ISR18;
    out_words[h36_monitor_index(UINT32_C(043))] =
        HHS_EXACT_PASS219_H36_MONITOR_PTR_ISR18;
    out_words[h36_monitor_index(UINT32_C(044))] =
        HHS_EXACT_PASS219_H36_MONITOR_PTP_ISR18;
    out_words[h36_monitor_index(UINT32_C(045))] =
        HHS_EXACT_PASS219_H36_MONITOR_APR_ISR18;

    out_words[h36_monitor_index(UINT32_C(046))] =
        HHS_EXACT_PASS219_H36_MONITOR_TASK0_18;
    out_words[h36_monitor_index(UINT32_C(047))] =
        HHS_EXACT_PASS219_H36_MONITOR_TASK1_18;

    status = h36_monitor_ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_TTY, 2U,
        HHS_EXACT_PASS219_H36_MONITOR_TTY_SCRATCH18,
        &out_words[h36_monitor_index(UINT32_C(050))]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_monitor_ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_TTY, 4U,
        (UINT32_C(1) << 7U) | UINT32_C(1),
        &out_words[h36_monitor_index(UINT32_C(051))]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_monitor_enc(
        UINT16_C(0254), UINT8_C(010),
        HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
        &out_words[h36_monitor_index(UINT32_C(052))]);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = h36_monitor_ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PTR, 2U,
        HHS_EXACT_PASS219_H36_MONITOR_PTR_SCRATCH18,
        &out_words[h36_monitor_index(UINT32_C(053))]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_monitor_enc(
        UINT16_C(0254), UINT8_C(010),
        HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
        &out_words[h36_monitor_index(UINT32_C(054))]);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = h36_monitor_ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PTP, 4U,
        UINT32_C(3),
        &out_words[h36_monitor_index(UINT32_C(056))]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_monitor_enc(
        UINT16_C(0254), UINT8_C(010),
        HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
        &out_words[h36_monitor_index(UINT32_C(057))]);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = h36_monitor_enc(
        UINT16_C(0254), 0U,
        HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
        &out_words[h36_monitor_index(UINT32_C(061))]);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = h36_monitor_ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_APR, 5U,
        HHS_EXACT_PASS219_H36_MONITOR_APR_SCRATCH18,
        &out_words[h36_monitor_index(UINT32_C(062))]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_monitor_enc(
        UINT16_C(0254), UINT8_C(010),
        HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
        &out_words[h36_monitor_index(UINT32_C(063))]);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = h36_monitor_enc(
        UINT16_C(0254), 0U,
        HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
        &out_words[h36_monitor_index(UINT32_C(064))]);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = h36_monitor_ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_TTY, 4U, UINT32_C(1),
        &out_words[h36_monitor_index(UINT32_C(070))]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_monitor_ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PTR, 4U,
        (UINT32_C(1) << 5U) | UINT32_C(2),
        &out_words[h36_monitor_index(UINT32_C(071))]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_monitor_ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PTP, 4U, UINT32_C(3),
        &out_words[h36_monitor_index(UINT32_C(072))]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_monitor_ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_APR, 4U,
        h36_monitor_control_bit(31U) | UINT32_C(4),
        &out_words[h36_monitor_index(UINT32_C(073))]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_monitor_ioenc(
        HHS_EXACT_PASS219_H36_DEVICE_PI, 4U, pi_control,
        &out_words[h36_monitor_index(UINT32_C(074))]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_monitor_enc(
        UINT16_C(0254), 0U,
        HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
        &out_words[h36_monitor_index(UINT32_C(075))]);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = h36_monitor_enc(
        UINT16_C(0040), 0U, UINT32_C(1),
        &out_words[h36_monitor_index(
            HHS_EXACT_PASS219_H36_MONITOR_TASK0_18)]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = h36_monitor_enc(
        UINT16_C(0040), 0U, UINT32_C(2),
        &out_words[h36_monitor_index(
            HHS_EXACT_PASS219_H36_MONITOR_TASK1_18)]);
    if (status != HHS_EXACT_STATUS_OK) return status;

    status = h36_monitor_enc(
        UINT16_C(0254), 0U,
        HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18,
        &out_words[h36_monitor_index(UINT32_C(0106))]);
    if (status != HHS_EXACT_STATUS_OK) return status;
    return h36_monitor_enc(
        UINT16_C(0254), 0U,
        HHS_EXACT_PASS219_H36_MONITOR_BOOT18,
        &out_words[h36_monitor_index(
            HHS_EXACT_PASS219_H36_MONITOR_IMAGE_LAST18)]);
}

static HHSExactStatus h36_monitor_build_tape(
    uint8_t *frames,
    size_t capacity,
    size_t *out_count,
    uint64_t *out_signature36
) {
    uint64_t image[HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS];
    size_t off = 0U;
    size_t i;
    size_t needed =
        ((size_t)HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS + 1U) * 6U;
    HHSExactStatus status;

    if (frames == NULL || out_count == NULL ||
        out_signature36 == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < needed)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;

    status = hhs_exact_pass219_h36_ka10_monitor_image_build(image);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    h36_monitor_emit_word(
        h36_monitor_iowd(
            HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS,
            HHS_EXACT_PASS219_H36_MONITOR_IMAGE_START18 - 1U),
        frames,
        &off
    );
    for (i = 0U;
         i < (size_t)HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS;
         ++i)
        h36_monitor_emit_word(image[i], frames, &off);

    *out_signature36 = h36_monitor_signature36(
        image, (size_t)HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS);
    *out_count = off;
    return HHS_EXACT_STATUS_OK;
}

static void h36_monitor_init_workload(
    HHSExactPass219H36MonitorWorkloadSignatureV1 *workload,
    uint64_t image_signature36
) {
    memset(workload, 0, sizeof(*workload));
    workload->struct_size = (uint32_t)sizeof(*workload);
    workload->version = HHS_EXACT_PASS219_H36_MONITOR_VERSION;
    workload->profile_id = H36_MONITOR_PROFILE_ID;
    workload->feature_mask =
        HHS_EXACT_PASS219_H36_MONITOR_FEATURE_MASK;
    workload->image_start18 =
        HHS_EXACT_PASS219_H36_MONITOR_IMAGE_START18;
    workload->image_words =
        HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS;
    workload->dispatch_entries =
        HHS_EXACT_PASS219_H36_MONITOR_DISPATCH_ENTRIES;
    workload->run_queue_slots =
        HHS_EXACT_PASS219_H36_MONITOR_RUN_QUEUE_SLOTS;
    workload->candidate_stack_only = 1U;
    workload->image_signature36 =
        image_signature36 & HHS_EXACT_PASS219_H36_WORD_MASK;
    workload->canonical_mutation_authority = 0U;
    workload->canonical_hash72_authority = 0U;
    workload->canonical_hash216_authority = 0U;
    workload->canonical_persistence_authority = 0U;
}

static HHSExactStatus h36_monitor_dispatch_next(
    HHSExactPass219H36VMStateV1 *state,
    HHSExactPass219H36MonitorStateV1 *monitor
) {
    uint32_t slot;
    uint32_t target;

    if (state == NULL || monitor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    slot = (uint32_t)(
        monitor->queue_cursor %
        HHS_EXACT_PASS219_H36_MONITOR_RUN_QUEUE_SLOTS
    );
    target = (uint32_t)(
        state->memory[
            HHS_EXACT_PASS219_H36_MONITOR_RUN_QUEUE_BASE18 + slot
        ] & HHS_EXACT_PASS219_H36_HALF_MASK
    );
    if (target >= HHS_EXACT_PASS219_H36_WORD_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    state->pc18 = target;
    monitor->queue_cursor = (uint8_t)(
        (slot + 1U) %
        HHS_EXACT_PASS219_H36_MONITOR_RUN_QUEUE_SLOTS
    );
    monitor->dispatch_count += 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_ka10_monitor_bootstrap(
    HHSExactPass219H36VMStateV1 *state,
    HHSExactPass219H36MonitorStateV1 *monitor,
    HHSExactPass219H36MonitorReceiptV1 *out_receipt
) {
    uint8_t tape[H36_MONITOR_TAPE_CAPACITY];
    size_t tape_count = 0U;
    uint64_t image_signature36 = 0U;
    uint32_t boot_steps = 0U;
    HHSExactStatus status;

    if (state == NULL || monitor == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    status = hhs_exact_pass219_h36_vm_init(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    memset(monitor, 0, sizeof(*monitor));
    monitor->struct_size = (uint32_t)sizeof(*monitor);
    monitor->version = HHS_EXACT_PASS219_H36_MONITOR_VERSION;

    status = hhs_exact_pass219_h36_legacy_uuo_mode_set(
        state, HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = h36_monitor_build_tape(
        tape, sizeof(tape), &tape_count, &image_signature36);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_h36_ptr_load_tape(
        state, tape, tape_count);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_h36_rim_bootstrap(
        state, &monitor->rim_receipt);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (monitor->rim_receipt.final_pc18 !=
        HHS_EXACT_PASS219_H36_MONITOR_BOOT18)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    state->legacy_priority_vector18[0] =
        HHS_EXACT_PASS219_H36_MONITOR_TTY_ISR18;
    state->legacy_priority_vector18[1] =
        HHS_EXACT_PASS219_H36_MONITOR_PTR_ISR18;
    state->legacy_priority_vector18[2] =
        HHS_EXACT_PASS219_H36_MONITOR_PTP_ISR18;
    state->legacy_priority_vector18[3] =
        HHS_EXACT_PASS219_H36_MONITOR_APR_ISR18;

    while (state->pc18 !=
           HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18 &&
           boot_steps < H36_MONITOR_EXECUTION_LIMIT) {
        status = hhs_exact_pass219_h36_vm_step(state);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        status = hhs_exact_pass219_h36_devices_step(state);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        status = hhs_exact_pass219_h36_internal_interrupt_refresh(state);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        boot_steps += 1U;
    }
    if (state->pc18 != HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (state->halted != 0U ||
        state->trap != HHS_EXACT_PASS219_H36_TRAP_NONE)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    h36_monitor_init_workload(
        &monitor->workload, image_signature36);
    monitor->initialized = 1U;

    return hhs_exact_pass219_h36_ka10_monitor_receipt_capture(
        state, monitor, out_receipt);
}

HHSExactStatus hhs_exact_pass219_h36_ka10_monitor_drive(
    HHSExactPass219H36VMStateV1 *state,
    HHSExactPass219H36MonitorStateV1 *monitor,
    uint32_t max_steps,
    uint32_t *out_steps
) {
    uint32_t completed = 0U;
    HHSExactStatus status;

    if (state == NULL || monitor == NULL || out_steps == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (monitor->struct_size != sizeof(*monitor) ||
        monitor->version != HHS_EXACT_PASS219_H36_MONITOR_VERSION ||
        monitor->initialized != 1U)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    while (completed < max_steps) {
        uint8_t channel = 0U;
        uint16_t uuo_before;

        status = hhs_exact_pass219_h36_devices_step(state);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        status = hhs_exact_pass219_h36_internal_interrupt_refresh(state);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        status = hhs_exact_pass219_h36_priority_enter(state, &channel);
        if (status != HHS_EXACT_STATUS_OK)
            return status;

        if (channel != 0U) {
            monitor->last_interrupt_channel = channel;
            if (channel == 1U) monitor->tty_service_count += 1U;
            else if (channel == 2U) monitor->ptr_service_count += 1U;
            else if (channel == 3U) monitor->ptp_service_count += 1U;
            else if (channel == 4U) monitor->apr_service_count += 1U;
        } else if (
            state->pc18 ==
            HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18
        ) {
            status = h36_monitor_dispatch_next(state, monitor);
            if (status != HHS_EXACT_STATUS_OK)
                return status;
        }

        uuo_before = state->legacy_uuo_dispatch_count;
        status = hhs_exact_pass219_h36_vm_step(state);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        if (state->legacy_uuo_dispatch_count != uuo_before) {
            monitor->uuo_service_count += (uint32_t)(
                (uint16_t)(
                    state->legacy_uuo_dispatch_count - uuo_before
                )
            );
        }

        monitor->executed_steps += 1U;
        completed += 1U;
        if (state->halted != 0U)
            break;
    }

    *out_steps = completed;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_ka10_monitor_receipt_capture(
    const HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36MonitorStateV1 *monitor,
    HHSExactPass219H36MonitorReceiptV1 *out_receipt
) {
    if (state == NULL || monitor == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (monitor->struct_size != sizeof(*monitor) ||
        monitor->version != HHS_EXACT_PASS219_H36_MONITOR_VERSION ||
        monitor->initialized != 1U)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (state->canonical_mutation_authority != 0U ||
        state->canonical_hash72_authority != 0U ||
        state->canonical_persistence_authority != 0U ||
        state->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = (uint32_t)sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_H36_MONITOR_VERSION;
    out_receipt->pc18 = state->pc18;
    out_receipt->dispatch_count = monitor->dispatch_count;
    out_receipt->executed_steps = monitor->executed_steps;
    out_receipt->tty_service_count = monitor->tty_service_count;
    out_receipt->ptr_service_count = monitor->ptr_service_count;
    out_receipt->ptp_service_count = monitor->ptp_service_count;
    out_receipt->apr_service_count = monitor->apr_service_count;
    out_receipt->uuo_service_count = monitor->uuo_service_count;
    out_receipt->core_uuo_dispatch_count =
        state->legacy_uuo_dispatch_count;
    out_receipt->queue_cursor = monitor->queue_cursor;
    out_receipt->last_interrupt_channel =
        monitor->last_interrupt_channel;
    out_receipt->exact_replayable = 1U;
    out_receipt->candidate_stack_only = 1U;
    out_receipt->canonical_mutation_authority = 0U;
    out_receipt->canonical_hash72_authority = 0U;
    out_receipt->canonical_hash216_authority = 0U;
    out_receipt->canonical_persistence_authority = 0U;
    out_receipt->floating_point_authority = 0U;
    out_receipt->rim_receipt = monitor->rim_receipt;
    out_receipt->workload = monitor->workload;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_ka10_monitor_receipt_validate(
    const HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36MonitorStateV1 *monitor,
    const HHSExactPass219H36MonitorReceiptV1 *receipt
) {
    uint64_t image[HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS];
    uint64_t signature36;
    HHSExactStatus status;

    if (state == NULL || monitor == NULL || receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (receipt->struct_size != sizeof(*receipt) ||
        receipt->version != HHS_EXACT_PASS219_H36_MONITOR_VERSION ||
        monitor->struct_size != sizeof(*monitor) ||
        monitor->version != HHS_EXACT_PASS219_H36_MONITOR_VERSION ||
        monitor->initialized != 1U)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    status = hhs_exact_pass219_h36_ka10_monitor_image_build(image);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    signature36 = h36_monitor_signature36(
        image, (size_t)HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS);

    if (receipt->pc18 != state->pc18 ||
        receipt->dispatch_count != monitor->dispatch_count ||
        receipt->executed_steps != monitor->executed_steps ||
        receipt->tty_service_count != monitor->tty_service_count ||
        receipt->ptr_service_count != monitor->ptr_service_count ||
        receipt->ptp_service_count != monitor->ptp_service_count ||
        receipt->apr_service_count != monitor->apr_service_count ||
        receipt->uuo_service_count != monitor->uuo_service_count ||
        receipt->core_uuo_dispatch_count !=
            state->legacy_uuo_dispatch_count ||
        receipt->queue_cursor != monitor->queue_cursor ||
        receipt->last_interrupt_channel !=
            monitor->last_interrupt_channel ||
        receipt->exact_replayable != 1U ||
        receipt->candidate_stack_only != 1U ||
        receipt->canonical_mutation_authority != 0U ||
        receipt->canonical_hash72_authority != 0U ||
        receipt->canonical_hash216_authority != 0U ||
        receipt->canonical_persistence_authority != 0U ||
        receipt->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (receipt->workload.struct_size !=
            sizeof(receipt->workload) ||
        receipt->workload.version !=
            HHS_EXACT_PASS219_H36_MONITOR_VERSION ||
        receipt->workload.profile_id != H36_MONITOR_PROFILE_ID ||
        receipt->workload.feature_mask !=
            HHS_EXACT_PASS219_H36_MONITOR_FEATURE_MASK ||
        receipt->workload.image_start18 !=
            HHS_EXACT_PASS219_H36_MONITOR_IMAGE_START18 ||
        receipt->workload.image_words !=
            HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS ||
        receipt->workload.dispatch_entries !=
            HHS_EXACT_PASS219_H36_MONITOR_DISPATCH_ENTRIES ||
        receipt->workload.run_queue_slots !=
            HHS_EXACT_PASS219_H36_MONITOR_RUN_QUEUE_SLOTS ||
        receipt->workload.candidate_stack_only != 1U ||
        receipt->workload.image_signature36 != signature36 ||
        receipt->workload.canonical_mutation_authority != 0U ||
        receipt->workload.canonical_hash72_authority != 0U ||
        receipt->workload.canonical_hash216_authority != 0U ||
        receipt->workload.canonical_persistence_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (state->legacy_uuo_mode !=
            HHS_EXACT_PASS219_H36_UUO_MODE_KA10_HISTORICAL ||
        state->memory[UINT32_C(042)] !=
            HHS_EXACT_PASS219_H36_MONITOR_TTY_ISR18 ||
        state->memory[UINT32_C(043)] !=
            HHS_EXACT_PASS219_H36_MONITOR_PTR_ISR18 ||
        state->memory[UINT32_C(044)] !=
            HHS_EXACT_PASS219_H36_MONITOR_PTP_ISR18 ||
        state->memory[UINT32_C(045)] !=
            HHS_EXACT_PASS219_H36_MONITOR_APR_ISR18 ||
        state->memory[UINT32_C(046)] !=
            HHS_EXACT_PASS219_H36_MONITOR_TASK0_18 ||
        state->memory[UINT32_C(047)] !=
            HHS_EXACT_PASS219_H36_MONITOR_TASK1_18 ||
        state->legacy_priority_vector18[0] !=
            HHS_EXACT_PASS219_H36_MONITOR_TTY_ISR18 ||
        state->legacy_priority_vector18[1] !=
            HHS_EXACT_PASS219_H36_MONITOR_PTR_ISR18 ||
        state->legacy_priority_vector18[2] !=
            HHS_EXACT_PASS219_H36_MONITOR_PTP_ISR18 ||
        state->legacy_priority_vector18[3] !=
            HHS_EXACT_PASS219_H36_MONITOR_APR_ISR18 ||
        state->canonical_mutation_authority != 0U ||
        state->canonical_hash72_authority != 0U ||
        state->canonical_persistence_authority != 0U ||
        state->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

#undef H36_MONITOR_PROFILE_ID
#undef H36_MONITOR_TAPE_CAPACITY
#undef H36_MONITOR_EXECUTION_LIMIT
