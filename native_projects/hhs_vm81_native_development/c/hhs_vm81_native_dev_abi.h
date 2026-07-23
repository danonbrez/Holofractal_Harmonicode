#ifndef HHS_VM81_NATIVE_DEV_ABI_H
#define HHS_VM81_NATIVE_DEV_ABI_H

#include <stdint.h>
#include "hhs_runtime_abi.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_VM81_NATIVE_DEV_ABI_VERSION 1U
#define HHS_VM81_NATIVE_AUTHORITY_NOT_ADMITTED 0U
#define HHS_VM81_NATIVE_AUTHORITY_ADMITTED 1U

typedef enum HHSVM81NativeStatus {
    HHS_VM81_NATIVE_STATUS_OK = 0,
    HHS_VM81_NATIVE_STATUS_INVALID_ARGUMENT = 1,
    HHS_VM81_NATIVE_STATUS_ABI_VERSION_MISMATCH = 2,
    HHS_VM81_NATIVE_STATUS_INVALID_OPCODE = 3,
    HHS_VM81_NATIVE_STATUS_INVALID_OPERAND = 4,
    HHS_VM81_NATIVE_STATUS_ARITHMETIC_OVERFLOW = 5,
    HHS_VM81_NATIVE_STATUS_HALTED = 6,
    HHS_VM81_NATIVE_STATUS_AUTHORITY_REJECTED = 7,
    HHS_VM81_NATIVE_STATUS_INTERNAL_INVARIANT_FAILURE = 8
} HHSVM81NativeStatus;

typedef enum HHSVM81NativeOperation {
    HHS_VM81_NATIVE_OP_VALIDATE_ABI = 1,
    HHS_VM81_NATIVE_OP_TENSOR_STEP = 2,
    HHS_VM81_NATIVE_OP_HALT = 3,
    HHS_VM81_NATIVE_OP_RESET = 4
} HHSVM81NativeOperation;

typedef struct HHSVM81NativeRequest {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t operation;
    uint32_t operand_count;
    uint32_t authority_admission;
    uint32_t reserved0;
    int64_t operands[3];
} HHSVM81NativeRequest;

typedef struct HHSVM81NativeResult {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t status;
    uint32_t operation;
    uint32_t mutation_performed;
    uint32_t state_unchanged;
    uint64_t output_u64;
    uint64_t step_before;
    uint64_t step_after;
    uint64_t witness_flags_before;
    uint64_t witness_flags_after;
} HHSVM81NativeResult;

/*
 * Contract-scoped typed execution wrapper.
 *
 * This wrapper does not replace or reinterpret frozen VM81 semantics. It
 * validates request structure, operand count, arithmetic bounds, halted state,
 * and the pre-admitted authority marker before dispatching to existing public
 * C ABI functions. The authority marker is not the later single-use mutation
 * capability required by the full elastic-memory contract.
 */
HHS_API
HHSVM81NativeStatus hhs_vm81_native_dev_execute(
    HHSRuntimeState* state,
    const HHSVM81NativeRequest* request,
    HHSVM81NativeResult* result
);

#ifdef __cplusplus
}
#endif

#endif
