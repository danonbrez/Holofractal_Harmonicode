#include "hhs_vm81_native_dev_abi.h"

#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>

static HHSVM81NativeRequest request_for(
    uint32_t operation,
    uint32_t operand_count,
    uint32_t authority_admission
) {
    HHSVM81NativeRequest request;
    memset(&request, 0, sizeof(request));
    request.struct_size = (uint32_t)sizeof(request);
    request.abi_version = HHS_VM81_NATIVE_DEV_ABI_VERSION;
    request.operation = operation;
    request.operand_count = operand_count;
    request.authority_admission = authority_admission;
    return request;
}

static void assert_rejected_unchanged(
    HHSVM81NativeStatus observed,
    HHSVM81NativeStatus expected,
    const HHSRuntimeState* before,
    const HHSRuntimeState* after,
    const HHSVM81NativeResult* result
) {
    assert(observed == expected);
    assert(result->status == (uint32_t)expected);
    assert(result->mutation_performed == 0U);
    assert(result->state_unchanged == 1U);
    assert(memcmp(before, after, sizeof(*before)) == 0);
}

int main(void) {
    HHSRuntimeState state;
    HHSRuntimeState before;
    HHSVM81NativeRequest request;
    HHSVM81NativeResult result;
    HHSVM81NativeStatus status;

    hhs_runtime_init(&state);
    assert(hhs_validate_abi(&state) == 1);

    before = state;
    request = request_for(999U, 0U, HHS_VM81_NATIVE_AUTHORITY_ADMITTED);
    status = hhs_vm81_native_dev_execute(&state, &request, &result);
    assert_rejected_unchanged(
        status, HHS_VM81_NATIVE_STATUS_INVALID_OPCODE,
        &before, &state, &result
    );

    before = state;
    request = request_for(
        HHS_VM81_NATIVE_OP_TENSOR_STEP,
        1U,
        HHS_VM81_NATIVE_AUTHORITY_ADMITTED
    );
    request.operands[0] = 3;
    status = hhs_vm81_native_dev_execute(&state, &request, &result);
    assert_rejected_unchanged(
        status, HHS_VM81_NATIVE_STATUS_INVALID_OPERAND,
        &before, &state, &result
    );

    before = state;
    request = request_for(
        HHS_VM81_NATIVE_OP_TENSOR_STEP,
        2U,
        HHS_VM81_NATIVE_AUTHORITY_NOT_ADMITTED
    );
    request.operands[0] = 3;
    request.operands[1] = -3;
    status = hhs_vm81_native_dev_execute(&state, &request, &result);
    assert_rejected_unchanged(
        status, HHS_VM81_NATIVE_STATUS_AUTHORITY_REJECTED,
        &before, &state, &result
    );

    before = state;
    request = request_for(
        HHS_VM81_NATIVE_OP_TENSOR_STEP,
        2U,
        HHS_VM81_NATIVE_AUTHORITY_ADMITTED
    );
    request.operands[0] = INT64_MAX;
    request.operands[1] = 2;
    status = hhs_vm81_native_dev_execute(&state, &request, &result);
    assert_rejected_unchanged(
        status, HHS_VM81_NATIVE_STATUS_ARITHMETIC_OVERFLOW,
        &before, &state, &result
    );

    request = request_for(
        HHS_VM81_NATIVE_OP_TENSOR_STEP,
        2U,
        HHS_VM81_NATIVE_AUTHORITY_ADMITTED
    );
    request.operands[0] = 3;
    request.operands[1] = -3;
    status = hhs_vm81_native_dev_execute(&state, &request, &result);
    assert(status == HHS_VM81_NATIVE_STATUS_OK);
    assert(result.status == HHS_VM81_NATIVE_STATUS_OK);
    assert(result.mutation_performed == 1U);
    assert(result.state_unchanged == 0U);
    assert(state.step == 1U);
    assert(state.tensor.xy == -9);
    assert(state.tensor.yx == -9);
    assert(state.tensor.transport == -18);
    assert(state.flux.transport_flux == -18);

    request = request_for(
        HHS_VM81_NATIVE_OP_HALT,
        0U,
        HHS_VM81_NATIVE_AUTHORITY_ADMITTED
    );
    status = hhs_vm81_native_dev_execute(&state, &request, &result);
    assert(status == HHS_VM81_NATIVE_STATUS_OK);
    assert(result.mutation_performed == 1U);
    assert(state.halted == 1U);

    before = state;
    request = request_for(
        HHS_VM81_NATIVE_OP_TENSOR_STEP,
        2U,
        HHS_VM81_NATIVE_AUTHORITY_ADMITTED
    );
    request.operands[0] = 1;
    request.operands[1] = 1;
    status = hhs_vm81_native_dev_execute(&state, &request, &result);
    assert_rejected_unchanged(
        status, HHS_VM81_NATIVE_STATUS_HALTED,
        &before, &state, &result
    );

    request = request_for(
        HHS_VM81_NATIVE_OP_RESET,
        0U,
        HHS_VM81_NATIVE_AUTHORITY_ADMITTED
    );
    status = hhs_vm81_native_dev_execute(&state, &request, &result);
    assert(status == HHS_VM81_NATIVE_STATUS_OK);
    assert(result.mutation_performed == 1U);
    assert(state.step == 0U);
    assert(state.halted == 0U);
    assert(hhs_validate_abi(&state) == 1);

    request = request_for(
        HHS_VM81_NATIVE_OP_VALIDATE_ABI,
        0U,
        HHS_VM81_NATIVE_AUTHORITY_NOT_ADMITTED
    );
    status = hhs_vm81_native_dev_execute(&state, &request, &result);
    assert(status == HHS_VM81_NATIVE_STATUS_OK);
    assert(result.output_u64 == 1U);
    assert(result.mutation_performed == 0U);
    assert(result.state_unchanged == 1U);

    puts("VM81_TYPED_STATUS_AND_REJECTION_STATE_PRESERVATION_PASSED");
    return 0;
}
