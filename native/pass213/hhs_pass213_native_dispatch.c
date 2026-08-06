#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define HHS_PASS213_DISPATCH_ABI_VERSION 1u
#define HHS_PASS213_DISPATCH_MAX_OPERANDS 8u
#define HHS_PASS213_DISPATCH_MAX_RESULTS 4u

#define HHS_PASS213_DISPATCH_OK 0
#define HHS_PASS213_DISPATCH_ERR_NULL 1
#define HHS_PASS213_DISPATCH_ERR_ABI 2
#define HHS_PASS213_DISPATCH_ERR_OPCODE 3
#define HHS_PASS213_DISPATCH_ERR_INPUT_COUNT 4
#define HHS_PASS213_DISPATCH_ERR_ROUTE 5
#define HHS_PASS213_DISPATCH_ERR_MODULUS 6

#define HHS_PASS213_OPCODE_ADD_U64 1u
#define HHS_PASS213_OPCODE_SUB_U64 2u
#define HHS_PASS213_OPCODE_XOR_U64 3u
#define HHS_PASS213_OPCODE_AND_U64 4u
#define HHS_PASS213_OPCODE_OR_U64 5u
#define HHS_PASS213_OPCODE_MUL_MOD_U64 6u
#define HHS_PASS213_OPCODE_ROTL_U64 7u
#define HHS_PASS213_OPCODE_EQ_U64 8u
#define HHS_PASS213_OPCODE_SELECT_U64 9u

typedef struct hhs_pass213_dispatch_request {
    uint32_t abi_version;
    uint32_t opcode;
    uint32_t input_count;
    uint32_t result_capacity;
    uint32_t vm81_cell_id;
    uint32_t operation_slot;
    uint32_t g243_control_id;
    uint32_t reserved0;
    uint64_t request_sequence;
    uint64_t modulus;
    uint64_t operands[HHS_PASS213_DISPATCH_MAX_OPERANDS];
} hhs_pass213_dispatch_request;

typedef struct hhs_pass213_dispatch_response {
    uint32_t abi_version;
    uint32_t status;
    uint32_t result_count;
    uint32_t opcode;
    uint64_t request_sequence;
    uint64_t results[HHS_PASS213_DISPATCH_MAX_RESULTS];
} hhs_pass213_dispatch_response;

static int hhs_pass213_require_inputs(
    const hhs_pass213_dispatch_request *request,
    uint32_t expected
) {
    if (request->input_count != expected) {
        return HHS_PASS213_DISPATCH_ERR_INPUT_COUNT;
    }
    if (request->result_capacity < 1u) {
        return HHS_PASS213_DISPATCH_ERR_INPUT_COUNT;
    }
    return HHS_PASS213_DISPATCH_OK;
}

static uint64_t hhs_pass213_rotl64(uint64_t value, uint64_t shift_value) {
    const uint32_t shift = (uint32_t)(shift_value & 63u);
    if (shift == 0u) {
        return value;
    }
    return (value << shift) | (value >> (64u - shift));
}

int hhs_pass213_native_dispatch_execute(
    const hhs_pass213_dispatch_request *request,
    hhs_pass213_dispatch_response *response
) {
    int status = HHS_PASS213_DISPATCH_OK;

    if (request == NULL || response == NULL) {
        return HHS_PASS213_DISPATCH_ERR_NULL;
    }

    memset(response, 0, sizeof(*response));
    response->abi_version = HHS_PASS213_DISPATCH_ABI_VERSION;
    response->opcode = request->opcode;
    response->request_sequence = request->request_sequence;

    if (request->abi_version != HHS_PASS213_DISPATCH_ABI_VERSION) {
        response->status = HHS_PASS213_DISPATCH_ERR_ABI;
        return HHS_PASS213_DISPATCH_ERR_ABI;
    }
    if (request->input_count > HHS_PASS213_DISPATCH_MAX_OPERANDS) {
        response->status = HHS_PASS213_DISPATCH_ERR_INPUT_COUNT;
        return HHS_PASS213_DISPATCH_ERR_INPUT_COUNT;
    }
    if (
        request->vm81_cell_id >= 81u ||
        request->operation_slot >= 64u ||
        request->g243_control_id >= 243u
    ) {
        response->status = HHS_PASS213_DISPATCH_ERR_ROUTE;
        return HHS_PASS213_DISPATCH_ERR_ROUTE;
    }

    switch (request->opcode) {
        case HHS_PASS213_OPCODE_ADD_U64:
            status = hhs_pass213_require_inputs(request, 2u);
            if (status == HHS_PASS213_DISPATCH_OK) {
                response->results[0] = request->operands[0] + request->operands[1];
            }
            break;
        case HHS_PASS213_OPCODE_SUB_U64:
            status = hhs_pass213_require_inputs(request, 2u);
            if (status == HHS_PASS213_DISPATCH_OK) {
                response->results[0] = request->operands[0] - request->operands[1];
            }
            break;
        case HHS_PASS213_OPCODE_XOR_U64:
            status = hhs_pass213_require_inputs(request, 2u);
            if (status == HHS_PASS213_DISPATCH_OK) {
                response->results[0] = request->operands[0] ^ request->operands[1];
            }
            break;
        case HHS_PASS213_OPCODE_AND_U64:
            status = hhs_pass213_require_inputs(request, 2u);
            if (status == HHS_PASS213_DISPATCH_OK) {
                response->results[0] = request->operands[0] & request->operands[1];
            }
            break;
        case HHS_PASS213_OPCODE_OR_U64:
            status = hhs_pass213_require_inputs(request, 2u);
            if (status == HHS_PASS213_DISPATCH_OK) {
                response->results[0] = request->operands[0] | request->operands[1];
            }
            break;
        case HHS_PASS213_OPCODE_MUL_MOD_U64:
            status = hhs_pass213_require_inputs(request, 2u);
            if (status == HHS_PASS213_DISPATCH_OK) {
                if (request->modulus <= 1u) {
                    status = HHS_PASS213_DISPATCH_ERR_MODULUS;
                } else {
                    const __uint128_t product =
                        (__uint128_t)request->operands[0] *
                        (__uint128_t)request->operands[1];
                    response->results[0] = (uint64_t)(product % request->modulus);
                }
            }
            break;
        case HHS_PASS213_OPCODE_ROTL_U64:
            status = hhs_pass213_require_inputs(request, 2u);
            if (status == HHS_PASS213_DISPATCH_OK) {
                response->results[0] = hhs_pass213_rotl64(
                    request->operands[0],
                    request->operands[1]
                );
            }
            break;
        case HHS_PASS213_OPCODE_EQ_U64:
            status = hhs_pass213_require_inputs(request, 2u);
            if (status == HHS_PASS213_DISPATCH_OK) {
                response->results[0] =
                    request->operands[0] == request->operands[1] ? 1u : 0u;
            }
            break;
        case HHS_PASS213_OPCODE_SELECT_U64:
            status = hhs_pass213_require_inputs(request, 3u);
            if (status == HHS_PASS213_DISPATCH_OK) {
                response->results[0] =
                    request->operands[0] != 0u
                    ? request->operands[1]
                    : request->operands[2];
            }
            break;
        default:
            status = HHS_PASS213_DISPATCH_ERR_OPCODE;
            break;
    }

    response->status = (uint32_t)status;
    response->result_count = status == HHS_PASS213_DISPATCH_OK ? 1u : 0u;
    return status;
}

const char *hhs_pass213_native_dispatch_error_string(int code) {
    switch (code) {
        case HHS_PASS213_DISPATCH_OK:
            return "OK";
        case HHS_PASS213_DISPATCH_ERR_NULL:
            return "NULL_ARGUMENT";
        case HHS_PASS213_DISPATCH_ERR_ABI:
            return "ABI_VERSION_INVALID";
        case HHS_PASS213_DISPATCH_ERR_OPCODE:
            return "OPCODE_UNSUPPORTED";
        case HHS_PASS213_DISPATCH_ERR_INPUT_COUNT:
            return "INPUT_OR_RESULT_COUNT_INVALID";
        case HHS_PASS213_DISPATCH_ERR_ROUTE:
            return "VM81_VM5184_G243_ROUTE_INVALID";
        case HHS_PASS213_DISPATCH_ERR_MODULUS:
            return "MODULUS_INVALID";
        default:
            return "UNKNOWN_ERROR";
    }
}
