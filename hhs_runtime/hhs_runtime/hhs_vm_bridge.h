// ============================================================================
// hhs_runtime/hhs_vm_bridge.h
// HARMONICODE VM ↔ Python bridge ABI
//
// Purpose:
//   Stable FFI boundary between:
//
//       Python backend
//           ↓
//       HHS dispatch layer
//           ↓
//       VM81 substrate runtime
//
// This file defines:
//
// - deterministic runtime bridge ABI
// - Python-callable execution structures
// - receipt extraction interface
// - replay verification interface
// - vector-cache serialization boundary
//
// Once stabilized, Python becomes the primary development layer.
//
// ============================================================================

#ifndef HHS_VM_BRIDGE_H
#define HHS_VM_BRIDGE_H

#include <stdint.h>

#include "HARMONICODE_VM_RUNTIME.h"
#include "hhs_vm_dispatch.h"
#include "hhs_ir.h"

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// ABI VERSION
// ============================================================================

#define HHS_VM_BRIDGE_ABI_VERSION 1

// ============================================================================
// EXECUTION MODES
// ============================================================================

typedef enum {

    HHS_EXEC_MODE_NORMAL = 0,
    HHS_EXEC_MODE_TRACE,
    HHS_EXEC_MODE_VERIFY,
    HHS_EXEC_MODE_REPLAY,
    HHS_EXEC_MODE_VECTOR_CACHE,
    HHS_EXEC_MODE_SANDBOX

} HHSExecMode;

// ============================================================================
// PYTHON REQUEST
// ============================================================================

typedef struct {

    const char *source_code;

    const char *source_name;

    uint64_t execution_flags;

    HHSExecMode mode;

    int deterministic_only;
    int insert_receipts;
    int auto_closure;
    int replay_verify;

} HHSPythonRequest;

// ============================================================================
// PYTHON RESPONSE
// ============================================================================

typedef struct {

    int success;

    uint64_t steps;
    uint64_t sweeps;

    uint32_t final_witness;

    int closure_transport;
    int closure_orientation;
    int closure_constraint;
    int closure_converged;

    char final_hash72[73];
    char receipt_hash72[73];

    double identity_residual;

} HHSPythonResponse;

// ============================================================================
// VECTOR CACHE RECORD
// ============================================================================

typedef struct {

    char state_hash72[73];
    char receipt_hash72[73];
    char parent_hash72[73];

    uint32_t witness;

    uint64_t step;
    uint64_t timestamp;

    int converged;

} HHSVectorCacheRecord;

// ============================================================================
// BRIDGE API
// ============================================================================

// Initialize bridge runtime
int hhs_bridge_init(void);

// Shutdown bridge runtime
void hhs_bridge_shutdown(void);

// Execute Python-lowered IR through VM
int hhs_bridge_execute_ir(

    HHSPythonRequest *request,
    HHSIRProgram *program,
    HHSPythonResponse *response
);

// Execute already-emitted VM program
int hhs_bridge_execute_vm(

    HHSPythonRequest *request,
    VM81 *vm,
    HHSPythonResponse *response
);

// ============================================================================
// RECEIPT API
// ============================================================================

// Extract current receipt state
int hhs_bridge_extract_receipt(

    VM81 *vm,
    HHSVectorCacheRecord *record
);

// Verify receipt replay
int hhs_bridge_verify_receipt(

    HHSVectorCacheRecord *record
);

// ============================================================================
// VECTOR CACHE API
// ============================================================================

// Serialize VM state into cache record
int hhs_bridge_serialize_state(

    VM81 *vm,
    HHSVectorCacheRecord *record
);

// Restore VM state from cache record
int hhs_bridge_restore_state(

    VM81 *vm,
    HHSVectorCacheRecord *record
);

// ============================================================================
// HASH72 API
// ============================================================================

// Project VM state into Hash72
void hhs_bridge_project_hash72(

    VM81 *vm,
    char out[73]
);

// ============================================================================
// DEBUG
// ============================================================================

// Print bridge diagnostics
void hhs_bridge_print_debug(

    VM81 *vm
);

// Print cache record
void hhs_bridge_print_record(

    HHSVectorCacheRecord *record
);

#ifdef __cplusplus
}
#endif

#endif

// ============================================================================
// END
// ============================================================================