#include "hhs_runtime_abi.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static int reject(const char* message) {
    fprintf(stderr, "%s\n", message);
    return 1;
}

int main(void) {
    HHSRuntimeState left_state;
    HHSRuntimeState right_state;
    HHSTensorState left_tensor;
    HHSTensorState right_tensor;
    HHSReceipt left_receipt;
    HHSReceipt right_receipt;
    uint8_t cells[HHS_HASH72_LEN];
    HHSHash72 left_hash;
    HHSHash72 right_hash;

    for (size_t i = 0; i < HHS_HASH72_LEN; ++i) {
        cells[i] = (uint8_t)i;
    }

    hhs_runtime_init(&left_state);
    hhs_runtime_init(&right_state);
    if (!hhs_validate_abi(&left_state) || !hhs_validate_abi(&right_state)) {
        return reject("ABI validation failed after initialization");
    }
    if (memcmp(&left_state, &right_state, sizeof(left_state)) != 0) {
        return reject("runtime initialization is not deterministic");
    }

    hhs_tensor_reset(&left_tensor);
    hhs_tensor_reset(&right_tensor);
    hhs_tensor_apply_xy(&left_tensor, 3, -3);
    hhs_tensor_apply_xy(&right_tensor, 3, -3);
    if (left_tensor.xy != -9 || left_tensor.yx != -9 ||
        left_tensor.orientation != 0 || left_tensor.constraint != 0) {
        return reject("exact integer tensor transition mismatch");
    }
    if (memcmp(&left_tensor, &right_tensor, sizeof(left_tensor)) != 0) {
        return reject("tensor transition is not deterministic");
    }

    hhs_runtime_step(&left_state, &left_tensor);
    hhs_runtime_step(&right_state, &right_tensor);
    if (left_state.step != 1 || memcmp(&left_state, &right_state, sizeof(left_state)) != 0) {
        return reject("runtime step is not deterministic");
    }

    hhs_receipt_reset(&left_receipt);
    hhs_receipt_reset(&right_receipt);
    hhs_receipt_commit(&left_state, &left_receipt);
    hhs_receipt_commit(&right_state, &right_receipt);
    if (memcmp(&left_receipt, &right_receipt, sizeof(left_receipt)) != 0) {
        return reject("receipt projection is not deterministic");
    }

    hhs_hash72_project(cells, left_hash);
    hhs_hash72_project(cells, right_hash);
    if (hhs_hash72_compare(left_hash, right_hash) != HHS_HASH72_LEN) {
        return reject("hash72 compare does not return the exact positional match score");
    }
    right_hash[0] = right_hash[0] == '0' ? '1' : '0';
    if (hhs_hash72_compare(left_hash, right_hash) != HHS_HASH72_LEN - 1) {
        return reject("hash72 compare score range does not match the C ABI semantics");
    }

    hhs_runtime_halt(&left_state);
    hhs_runtime_halt(&right_state);
    if (!left_state.halted || !right_state.halted) {
        return reject("halt transition did not close");
    }
    {
        uint64_t halted_step = left_state.step;
        hhs_runtime_step(&left_state, &left_tensor);
        if (left_state.step != halted_step) {
            return reject("halted runtime advanced unexpectedly");
        }
    }

    hhs_runtime_init(NULL);
    hhs_runtime_step(NULL, NULL);
    hhs_runtime_halt(NULL);

    puts("VM81_DIRECT_C_ABI_FOUNDATION_SMOKE_PASSED");
    return 0;
}
