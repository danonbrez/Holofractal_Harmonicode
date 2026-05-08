// ============================================================================
// hhs_runtime/hhs_vm_dispatch.h
// HARMONICODE IR → VM dispatch layer
//
// Purpose:
//   Deterministic execution bridge between:
//
//       Python lowering
//           ↓
//       HHS IR
//           ↓
//       VM81 substrate runtime
//
// This layer is authoritative for:
//
// - IR opcode execution routing
// - VM instruction emission
// - receipt boundary coordination
// - replay-compatible execution
// - closure scheduling
//
// ============================================================================

#ifndef HHS_VM_DISPATCH_H
#define HHS_VM_DISPATCH_H

#include <stdint.h>

#include "HARMONICODE_VM_RUNTIME.h"
#include "hhs_ir.h"

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// DISPATCH FLAGS
// ============================================================================

#define HHS_DISPATCH_DETERMINISTIC      0x0001
#define HHS_DISPATCH_INSERT_RECEIPTS    0x0002
#define HHS_DISPATCH_VERIFY_REPLAY      0x0004
#define HHS_DISPATCH_AUTO_CLOSURE       0x0008
#define HHS_DISPATCH_TRACE              0x0010

// ============================================================================
// DISPATCH STATUS
// ============================================================================

typedef enum {

    HHS_DISPATCH_OK = 0,

    HHS_DISPATCH_ERR_NULL_VM,
    HHS_DISPATCH_ERR_NULL_IR,
    HHS_DISPATCH_ERR_INVALID_OPCODE,
    HHS_DISPATCH_ERR_PROGRAM_OVERFLOW,
    HHS_DISPATCH_ERR_REPLAY_FAILURE,
    HHS_DISPATCH_ERR_CLOSURE_FAILURE

} HHSDispatchStatus;

// ============================================================================
// DISPATCH CONTEXT
// ============================================================================

typedef struct {

    uint64_t ops_dispatched;
    uint64_t receipts_generated;
    uint64_t closures_generated;
    uint64_t replay_checks;

    uint64_t dispatch_flags;

    int deterministic_only;
    int replay_verified;

    HHSDispatchStatus last_status;

} HHSDispatchContext;

// ============================================================================
// VM EXECUTION RESULT
// ============================================================================

typedef struct {

    int success;

    uint64_t instructions_emitted;
    uint64_t instructions_executed;

    uint64_t final_step;
    uint64_t final_sweep;

    uint32_t final_witness;

    int closure_transport;
    int closure_orientation;
    int closure_constraint;
    int closure_converged;

    char final_hash72[73];

} HHSDispatchResult;

// ============================================================================
// CONTEXT API
// ============================================================================

void hhs_dispatch_init(
    HHSDispatchContext *ctx
);

// ============================================================================
// MAIN DISPATCH
// ============================================================================

// Execute IR program through VM substrate
int hhs_dispatch_ir_program(
    HHSDispatchContext *ctx,
    VM81 *vm,
    HHSIRProgram *ir,
    HHSDispatchResult *result
);

// Dispatch single IR op
int hhs_dispatch_ir_op(
    HHSDispatchContext *ctx,
    VM81 *vm,
    HHSIROp *op
);

// ============================================================================
// VM INSTRUCTION EMISSION
// ============================================================================

// Emit VM instruction from IR op
int hhs_emit_vm_instruction(
    VM81 *vm,
    HHSIROp *op
);

// Emit receipt boundary
int hhs_emit_receipt_boundary(
    VM81 *vm
);

// Emit closure verification
int hhs_emit_closure_boundary(
    VM81 *vm
);

// ============================================================================
// REPLAY / VALIDATION
// ============================================================================

// Replay verify current VM state
int hhs_dispatch_verify_replay(
    HHSDispatchContext *ctx,
    VM81 *vm
);

// Verify closure state
int hhs_dispatch_verify_closure(
    HHSDispatchContext *ctx,
    VM81 *vm
);

// ============================================================================
// HASH72
// ============================================================================

// Extract final Hash72 projection
void hhs_dispatch_project_hash72(
    VM81 *vm,
    char out[73]
);

// ============================================================================
// DEBUG / TRACE
// ============================================================================

void hhs_dispatch_print_stats(
    HHSDispatchContext *ctx
);

void hhs_dispatch_print_result(
    HHSDispatchResult *result
);

#ifdef __cplusplus
}
#endif

#endif

// ============================================================================
// END
// ============================================================================