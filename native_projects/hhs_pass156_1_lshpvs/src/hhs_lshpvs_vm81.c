#include "hhs_lshpvs.h"
#include "hhs_runtime_abi.h"

#include <limits.h>
#include <string.h>

static int exact_rotation_reconstructs(const HHSLshpvsEntry *entry) {
    int64_t product;
    int64_t reconstructed;

#if defined(__GNUC__) || defined(__clang__)
    if (__builtin_mul_overflow(
            entry->index.overflow_quotient_q,
            entry->index.modulus_M,
            &product)) {
        return 0;
    }
    if (__builtin_add_overflow(
            product,
            entry->index.local_residue_r,
            &reconstructed)) {
        return 0;
    }
#else
    if (entry->index.overflow_quotient_q != 0 &&
        (entry->index.modulus_M > INT64_MAX /
             (entry->index.overflow_quotient_q > 0
                  ? entry->index.overflow_quotient_q
                  : -entry->index.overflow_quotient_q))) {
        return 0;
    }
    product = entry->index.overflow_quotient_q * entry->index.modulus_M;
    if ((entry->index.local_residue_r > 0 &&
         product > INT64_MAX - entry->index.local_residue_r) ||
        (entry->index.local_residue_r < 0 &&
         product < INT64_MIN - entry->index.local_residue_r)) {
        return 0;
    }
    reconstructed = product + entry->index.local_residue_r;
#endif
    return reconstructed == entry->index.full_rotation_n;
}

HHSLshpvsStatus hhs_lshpvs_entry_admit_vm81(
    HHSLshpvsEntry *entry,
    void *runtime_state
) {
    HHSRuntimeState *runtime;
    HHSTensorState tensor;
    HHSReceipt receipt;

    if (entry == NULL || runtime_state == NULL) {
        return HHS_LSHPVS_INVALID_ARGUMENT;
    }
    runtime = (HHSRuntimeState *)runtime_state;
    if (!hhs_validate_abi(runtime) || runtime->halted != 0U) {
        return HHS_LSHPVS_VM81_REJECTED;
    }
    if (entry->hermitian_verified == 0U || entry->norm_verified == 0U ||
        entry->rotation_reconstruction_verified == 0U ||
        !exact_rotation_reconstructs(entry)) {
        return HHS_LSHPVS_VM81_REJECTED;
    }

    hhs_tensor_reset(&tensor);
    tensor.xy = entry->index.full_rotation_n;
    tensor.yx = entry->index.full_rotation_n;
    tensor.transport = tensor.xy + tensor.yx;
    tensor.orientation = tensor.xy - tensor.yx;
    tensor.constraint = 0;
    hhs_runtime_step(runtime, &tensor);
    if (runtime->step == 0U || tensor.orientation != 0) {
        return HHS_LSHPVS_VM81_REJECTED;
    }

    hhs_receipt_reset(&receipt);
    receipt.opcode = 1561U;
    hhs_receipt_commit(runtime, &receipt);
    memcpy(
        entry->hash72_head,
        receipt.current_receipt,
        HHS_LSHPVS_HASH72_STRLEN
    );
    entry->vm81_admitted = 1U;
    return HHS_LSHPVS_OK;
}
