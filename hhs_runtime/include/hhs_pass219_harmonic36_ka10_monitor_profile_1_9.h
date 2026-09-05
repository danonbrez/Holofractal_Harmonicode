#ifndef HHS_PASS219_HARMONIC36_KA10_MONITOR_PROFILE_1_9_H
#define HHS_PASS219_HARMONIC36_KA10_MONITOR_PROFILE_1_9_H

#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_MONITOR_VERSION UINT32_C(0x00010009)
#define HHS_EXACT_PASS219_H36_MONITOR_IMAGE_START18 UINT32_C(040)
#define HHS_EXACT_PASS219_H36_MONITOR_IMAGE_LAST18 UINT32_C(0107)
#define HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS \
    (HHS_EXACT_PASS219_H36_MONITOR_IMAGE_LAST18 - \
     HHS_EXACT_PASS219_H36_MONITOR_IMAGE_START18 + UINT32_C(1))
#define HHS_EXACT_PASS219_H36_MONITOR_DISPATCH_BASE18 UINT32_C(042)
#define HHS_EXACT_PASS219_H36_MONITOR_RUN_QUEUE_BASE18 UINT32_C(046)
#define HHS_EXACT_PASS219_H36_MONITOR_TTY_ISR18 UINT32_C(050)
#define HHS_EXACT_PASS219_H36_MONITOR_PTR_ISR18 UINT32_C(053)
#define HHS_EXACT_PASS219_H36_MONITOR_PTP_ISR18 UINT32_C(056)
#define HHS_EXACT_PASS219_H36_MONITOR_APR_ISR18 UINT32_C(062)
#define HHS_EXACT_PASS219_H36_MONITOR_SCHEDULER18 UINT32_C(064)
#define HHS_EXACT_PASS219_H36_MONITOR_BOOT18 UINT32_C(070)
#define HHS_EXACT_PASS219_H36_MONITOR_TTY_SCRATCH18 UINT32_C(0100)
#define HHS_EXACT_PASS219_H36_MONITOR_PTR_SCRATCH18 UINT32_C(0101)
#define HHS_EXACT_PASS219_H36_MONITOR_PTP_SCRATCH18 UINT32_C(0102)
#define HHS_EXACT_PASS219_H36_MONITOR_APR_SCRATCH18 UINT32_C(0103)
#define HHS_EXACT_PASS219_H36_MONITOR_TASK0_18 UINT32_C(0104)
#define HHS_EXACT_PASS219_H36_MONITOR_TASK1_18 UINT32_C(0105)
#define HHS_EXACT_PASS219_H36_MONITOR_DISPATCH_ENTRIES UINT8_C(4)
#define HHS_EXACT_PASS219_H36_MONITOR_RUN_QUEUE_SLOTS UINT8_C(2)

#define HHS_EXACT_PASS219_H36_MONITOR_FEATURE_RIM UINT32_C(0x01)
#define HHS_EXACT_PASS219_H36_MONITOR_FEATURE_APR_PI UINT32_C(0x02)
#define HHS_EXACT_PASS219_H36_MONITOR_FEATURE_TTY UINT32_C(0x04)
#define HHS_EXACT_PASS219_H36_MONITOR_FEATURE_PTR UINT32_C(0x08)
#define HHS_EXACT_PASS219_H36_MONITOR_FEATURE_PTP UINT32_C(0x10)
#define HHS_EXACT_PASS219_H36_MONITOR_FEATURE_UUO UINT32_C(0x20)
#define HHS_EXACT_PASS219_H36_MONITOR_FEATURE_RUN_QUEUE UINT32_C(0x40)
#define HHS_EXACT_PASS219_H36_MONITOR_FEATURE_MASK UINT32_C(0x7F)

typedef struct HHSExactPass219H36MonitorWorkloadSignatureV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t profile_id;
    uint32_t feature_mask;
    uint32_t image_start18;
    uint32_t image_words;
    uint8_t dispatch_entries;
    uint8_t run_queue_slots;
    uint8_t candidate_stack_only;
    uint8_t reserved0;
    uint64_t image_signature36;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
} HHSExactPass219H36MonitorWorkloadSignatureV1;

typedef struct HHSExactPass219H36MonitorStateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t initialized;
    uint8_t queue_cursor;
    uint8_t last_interrupt_channel;
    uint8_t reserved0;
    uint32_t dispatch_count;
    uint32_t executed_steps;
    uint32_t tty_service_count;
    uint32_t ptr_service_count;
    uint32_t ptp_service_count;
    uint32_t apr_service_count;
    uint32_t uuo_service_count;
    HHSExactPass219H36RIMReceiptV1 rim_receipt;
    HHSExactPass219H36MonitorWorkloadSignatureV1 workload;
} HHSExactPass219H36MonitorStateV1;

typedef struct HHSExactPass219H36MonitorReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pc18;
    uint32_t dispatch_count;
    uint32_t executed_steps;
    uint32_t tty_service_count;
    uint32_t ptr_service_count;
    uint32_t ptp_service_count;
    uint32_t apr_service_count;
    uint32_t uuo_service_count;
    uint16_t core_uuo_dispatch_count;
    uint8_t queue_cursor;
    uint8_t last_interrupt_channel;
    uint8_t exact_replayable;
    uint8_t candidate_stack_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0;
    HHSExactPass219H36RIMReceiptV1 rim_receipt;
    HHSExactPass219H36MonitorWorkloadSignatureV1 workload;
} HHSExactPass219H36MonitorReceiptV1;

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_ka10_monitor_image_build(
    uint64_t out_words[HHS_EXACT_PASS219_H36_MONITOR_IMAGE_WORDS]);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_ka10_monitor_bootstrap(
    HHSExactPass219H36VMStateV1 *state,
    HHSExactPass219H36MonitorStateV1 *monitor,
    HHSExactPass219H36MonitorReceiptV1 *out_receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_ka10_monitor_drive(
    HHSExactPass219H36VMStateV1 *state,
    HHSExactPass219H36MonitorStateV1 *monitor,
    uint32_t max_steps,
    uint32_t *out_steps);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_ka10_monitor_receipt_capture(
    const HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36MonitorStateV1 *monitor,
    HHSExactPass219H36MonitorReceiptV1 *out_receipt);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_ka10_monitor_receipt_validate(
    const HHSExactPass219H36VMStateV1 *state,
    const HHSExactPass219H36MonitorStateV1 *monitor,
    const HHSExactPass219H36MonitorReceiptV1 *receipt);

#ifdef __cplusplus
}
#endif
#endif
