#include "hhs_vm81_native_dev_abi.h"

#include <limits.h>
#include <string.h>

static int hhs_checked_add_i64(int64_t a, int64_t b, int64_t* out) {
    if (!out) {
        return 0;
    }
    if ((b > 0 && a > INT64_MAX - b) ||
        (b < 0 && a < INT64_MIN - b)) {
        return 0;
    }
    *out = a + b;
    return 1;
}

static int hhs_checked_mul_i64(int64_t a, int64_t b, int64_t* out) {
    if (!out) {
        return 0;
    }
    if (a == 0 || b == 0) {
        *out = 0;
        return 1;
    }
    if (a > 0) {
        if (b > 0) {
            if (a > INT64_MAX / b) {
                return 0;
            }
        } else if (b < INT64_MIN / a) {
            return 0;
        }
    } else {
        if (b > 0) {
            if (a < INT64_MIN / b) {
                return 0;
            }
        } else if (b < INT64_MAX / a) {
            return 0;
        }
    }
    *out = a * b;
    return 1;
}

static void hhs_result_initialize(
    HHSVM81NativeResult* result,
    const HHSVM81NativeRequest* request,
    const HHSRuntimeState* state
) {
    memset(result, 0, sizeof(*result));
    result->struct_size = (uint32_t)sizeof(*result);
    result->abi_version = HHS_VM81_NATIVE_DEV_ABI_VERSION;
    result->operation = request ? request->operation : 0U;
    if (state) {
        result->step_before = state->step;
        result->step_after = state->step;
        result->witness_flags_before = state->witness_flags;
        result->witness_flags_after = state->witness_flags;
    }
    result->state_unchanged = 1U;
}

static HHSVM81NativeStatus hhs_finish(
    HHSRuntimeState* state,
    const HHSRuntimeState* before,
    HHSVM81NativeResult* result,
    HHSVM81NativeStatus status,
    uint64_t output_u64,
    uint32_t mutation_performed
) {
    result->status = (uint32_t)status;
    result->output_u64 = output_u64;
    result->mutation_performed = mutation_performed;
    if (state) {
        result->step_after = state->step;
        result->witness_flags_after = state->witness_flags;
    }
    if (state && before) {
        result->state_unchanged =
            (uint32_t)(memcmp(before, state, sizeof(*state)) == 0);
    }
    if (status != HHS_VM81_NATIVE_STATUS_OK &&
        state && before && !result->state_unchanged) {
        *state = *before;
        result->step_after = state->step;
        result->witness_flags_after = state->witness_flags;
        result->state_unchanged = 1U;
        result->mutation_performed = 0U;
        result->status = HHS_VM81_NATIVE_STATUS_INTERNAL_INVARIANT_FAILURE;
        return HHS_VM81_NATIVE_STATUS_INTERNAL_INVARIANT_FAILURE;
    }
    return (HHSVM81NativeStatus)result->status;
}

static int hhs_operation_is_mutating(uint32_t operation) {
    return operation == HHS_VM81_NATIVE_OP_TENSOR_STEP ||
           operation == HHS_VM81_NATIVE_OP_HALT ||
           operation == HHS_VM81_NATIVE_OP_RESET;
}

HHSVM81NativeStatus hhs_vm81_native_dev_execute(
    HHSRuntimeState* state,
    const HHSVM81NativeRequest* request,
    HHSVM81NativeResult* result
) {
    HHSRuntimeState before;
    HHSRuntimeState* before_ptr = NULL;

    if (!result) {
        return HHS_VM81_NATIVE_STATUS_INVALID_ARGUMENT;
    }
    hhs_result_initialize(result, request, state);

    if (!state || !request) {
        return hhs_finish(
            state, NULL, result,
            HHS_VM81_NATIVE_STATUS_INVALID_ARGUMENT, 0U, 0U
        );
    }

    before = *state;
    before_ptr = &before;

    if (request->struct_size < sizeof(*request) ||
        request->abi_version != HHS_VM81_NATIVE_DEV_ABI_VERSION) {
        return hhs_finish(
            state, before_ptr, result,
            HHS_VM81_NATIVE_STATUS_ABI_VERSION_MISMATCH, 0U, 0U
        );
    }

    if (request->operation < HHS_VM81_NATIVE_OP_VALIDATE_ABI ||
        request->operation > HHS_VM81_NATIVE_OP_RESET) {
        return hhs_finish(
            state, before_ptr, result,
            HHS_VM81_NATIVE_STATUS_INVALID_OPCODE, 0U, 0U
        );
    }

    if (hhs_operation_is_mutating(request->operation) &&
        request->authority_admission != HHS_VM81_NATIVE_AUTHORITY_ADMITTED) {
        return hhs_finish(
            state, before_ptr, result,
            HHS_VM81_NATIVE_STATUS_AUTHORITY_REJECTED, 0U, 0U
        );
    }

    if (request->operation == HHS_VM81_NATIVE_OP_VALIDATE_ABI) {
        if (request->operand_count != 0U) {
            return hhs_finish(
                state, before_ptr, result,
                HHS_VM81_NATIVE_STATUS_INVALID_OPERAND, 0U, 0U
            );
        }
        return hhs_finish(
            state, before_ptr, result,
            HHS_VM81_NATIVE_STATUS_OK,
            (uint64_t)hhs_validate_abi(state),
            0U
        );
    }

    if (!hhs_validate_abi(state)) {
        return hhs_finish(
            state, before_ptr, result,
            HHS_VM81_NATIVE_STATUS_ABI_VERSION_MISMATCH, 0U, 0U
        );
    }

    if (request->operation == HHS_VM81_NATIVE_OP_TENSOR_STEP) {
        HHSTensorState tensor;
        int64_t product;
        int64_t transport;
        int64_t next_transport_flux;

        if (request->operand_count != 2U) {
            return hhs_finish(
                state, before_ptr, result,
                HHS_VM81_NATIVE_STATUS_INVALID_OPERAND, 0U, 0U
            );
        }
        if (state->halted) {
            return hhs_finish(
                state, before_ptr, result,
                HHS_VM81_NATIVE_STATUS_HALTED, 0U, 0U
            );
        }
        if (!hhs_checked_mul_i64(
                request->operands[0], request->operands[1], &product) ||
            !hhs_checked_add_i64(product, product, &transport) ||
            !hhs_checked_add_i64(
                state->flux.transport_flux, transport, &next_transport_flux)) {
            return hhs_finish(
                state, before_ptr, result,
                HHS_VM81_NATIVE_STATUS_ARITHMETIC_OVERFLOW, 0U, 0U
            );
        }

        hhs_tensor_reset(&tensor);
        hhs_tensor_apply_xy(
            &tensor,
            request->operands[0],
            request->operands[1]
        );
        hhs_runtime_step(state, &tensor);

        if (state->flux.transport_flux != next_transport_flux) {
            *state = before;
            return hhs_finish(
                state, before_ptr, result,
                HHS_VM81_NATIVE_STATUS_INTERNAL_INVARIANT_FAILURE, 0U, 0U
            );
        }
        return hhs_finish(
            state, before_ptr, result,
            HHS_VM81_NATIVE_STATUS_OK, 0U, 1U
        );
    }

    if (request->operation == HHS_VM81_NATIVE_OP_HALT) {
        if (request->operand_count != 0U) {
            return hhs_finish(
                state, before_ptr, result,
                HHS_VM81_NATIVE_STATUS_INVALID_OPERAND, 0U, 0U
            );
        }
        if (state->halted) {
            return hhs_finish(
                state, before_ptr, result,
                HHS_VM81_NATIVE_STATUS_HALTED, 0U, 0U
            );
        }
        hhs_runtime_halt(state);
        return hhs_finish(
            state, before_ptr, result,
            HHS_VM81_NATIVE_STATUS_OK, 0U, 1U
        );
    }

    if (request->operation == HHS_VM81_NATIVE_OP_RESET) {
        if (request->operand_count != 0U) {
            return hhs_finish(
                state, before_ptr, result,
                HHS_VM81_NATIVE_STATUS_INVALID_OPERAND, 0U, 0U
            );
        }
        hhs_runtime_reset(state);
        return hhs_finish(
            state, before_ptr, result,
            HHS_VM81_NATIVE_STATUS_OK, 0U, 1U
        );
    }

    return hhs_finish(
        state, before_ptr, result,
        HHS_VM81_NATIVE_STATUS_INVALID_OPCODE, 0U, 0U
    );
}
