// hhs_runtime/include/HARMONICODE_VM_RUNTIME.h
//
// HHS / HARMONICODE
// Canonical VM81 Runtime ABI
//
// Runtime Principle:
//
//   executable substrate authority
//   precedes bridge authority
//
// This file freezes the exported VM81 interface boundary
// WITHOUT modifying the VM81 runtime implementation.
//

#ifndef HARMONICODE_VM_RUNTIME_H
#define HARMONICODE_VM_RUNTIME_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* ============================================================
 * VERSION
 * ============================================================
 */

#define HHS_VM_RUNTIME_ABI_VERSION_MAJOR 1
#define HHS_VM_RUNTIME_ABI_VERSION_MINOR 0
#define HHS_VM_RUNTIME_ABI_VERSION_PATCH 0

#define HHS_VM_HASH72_LEN 72
#define HHS_VM_GRID_SIZE 81

/* ============================================================
 * WITNESS FLAGS
 * ============================================================
 */

typedef enum HHSWitnessFlags {

    W_GATE_APB_PASS           = 1 << 0,
    W_GATE_APB_FAIL           = 1 << 1,

    W_GATE_CLOSURE_PASS       = 1 << 2,
    W_GATE_CLOSURE_FAIL       = 1 << 3,

    W_QGU_APPLIED             = 1 << 4,
    W_NONCOMMUTATIVE          = 1 << 5,
    W_CONSTRAINT_FIRED        = 1 << 6,
    W_ORBIT_DETECTED          = 1 << 7,
    W_HALT                    = 1 << 8,
    W_SWEEP                   = 1 << 9,

    W_CLOSE_TRANSPORT         = 1 << 10,
    W_CLOSE_ORIENTATION       = 1 << 11,
    W_CLOSE_CONSTRAINT        = 1 << 12,
    W_CONVERGED               = 1 << 13,

    W_LEDGER_FROZEN           = 1 << 14

} HHSWitnessFlags;

/* ============================================================
 * HASH72
 * ============================================================
 */

typedef struct HHSHash72 {

    char value[HHS_VM_HASH72_LEN + 1];

} HHSHash72;

/* ============================================================
 * RECEIPT
 * ============================================================
 */

typedef struct HHSReceipt {

    uint64_t step;
    uint64_t witness_flags;

    HHSHash72 state_hash72;
    HHSHash72 prev_hash72;
    HHSHash72 receipt_hash72;

    double transport_flux;
    double orientation_flux;
    double constraint_flux;

    uint8_t converged;
    uint8_t frozen;

} HHSReceipt;

/* ============================================================
 * VM CELL
 * ============================================================
 */

typedef struct HHSVMCell {

    int64_t value;
    uint8_t phase;
    uint8_t occupied;

} HHSVMCell;

/* ============================================================
 * TENSOR81
 * ============================================================
 */

typedef struct HHSTensor81 {

    HHSVMCell cells[HHS_VM_GRID_SIZE];

} HHSTensor81;

/* ============================================================
 * VM STATE
 * ============================================================
 */

typedef struct HHSVMState {

    uint64_t pc;
    uint64_t step;

    uint64_t witness_flags;

    HHSTensor81 tensor;

    HHSHash72 current_hash72;
    HHSHash72 previous_hash72;

    double transport_flux;
    double orientation_flux;
    double constraint_flux;

    uint8_t halted;
    uint8_t converged;

} HHSVMState;

/* ============================================================
 * PROGRAM
 * ============================================================
 */

typedef struct HHSProgram {

    const void* bytecode;
    size_t bytecode_size;

} HHSProgram;

/* ============================================================
 * EXECUTION STATUS
 * ============================================================
 */

typedef enum HHSExecutionStatus {

    HHS_EXECUTION_OK = 0,
    HHS_EXECUTION_HALT = 1,
    HHS_EXECUTION_ERROR = 2,
    HHS_EXECUTION_CONVERGED = 3,
    HHS_EXECUTION_ORBIT = 4

} HHSExecutionStatus;

/* ============================================================
 * RUNTIME API
 * ============================================================
 */

/*
 * Runtime lifecycle
 */

void hhs_vm_init(
    HHSVMState* vm
);

void hhs_vm_reset(
    HHSVMState* vm
);

/*
 * Program execution
 */

HHSExecutionStatus hhs_vm_step(
    HHSVMState* vm,
    const HHSProgram* program
);

HHSExecutionStatus hhs_vm_run(
    HHSVMState* vm,
    const HHSProgram* program,
    uint64_t max_steps
);

/*
 * Receipt extraction
 */

void hhs_vm_get_receipt(
    const HHSVMState* vm,
    HHSReceipt* receipt
);

/*
 * Tensor access
 */

const HHSTensor81* hhs_vm_tensor81(
    const HHSVMState* vm
);

HHSVMCell* hhs_vm_cell(
    HHSVMState* vm,
    uint32_t index
);

/*
 * Hash72 access
 */

const char* hhs_vm_current_hash72(
    const HHSVMState* vm
);

const char* hhs_vm_previous_hash72(
    const HHSVMState* vm
);

/*
 * Witness access
 */

uint64_t hhs_vm_witness_flags(
    const HHSVMState* vm
);

/*
 * Closure state
 */

uint8_t hhs_vm_is_converged(
    const HHSVMState* vm
);

uint8_t hhs_vm_is_halted(
    const HHSVMState* vm
);

/*
 * Flux access
 */

double hhs_vm_transport_flux(
    const HHSVMState* vm
);

double hhs_vm_orientation_flux(
    const HHSVMState* vm
);

double hhs_vm_constraint_flux(
    const HHSVMState* vm
);

#ifdef __cplusplus
}
#endif

#endif