// hhs_runtime/hhs_ir_verify.c
//
// HARMONICODE IR / receipt verification layer
//
// Purpose:
//   Deterministic replay validation and integrity verification
//   for:
//
//     HHS IR blocks
//     receipt packets
//     Hash72 seals
//     parent-chain linkage
//     VM replay equivalence
//
// Properties:
//   - deterministic verification
//   - replay-safe
//   - Hash72-consistent
//   - receipt-chain compatible
//   - transport integrity aware
//

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include "HARMONICODE_VM_RUNTIME.h"


#define HHS_VERIFY_OK                 0x00000001u
#define HHS_VERIFY_BAD_MAGIC          0x00000002u
#define HHS_VERIFY_BAD_VERSION        0x00000004u
#define HHS_VERIFY_BAD_NODECOUNT      0x00000008u
#define HHS_VERIFY_BAD_PARENT         0x00000010u
#define HHS_VERIFY_BAD_HASH72         0x00000020u
#define HHS_VERIFY_BAD_RECEIPT        0x00000040u
#define HHS_VERIFY_BAD_REPLAY         0x00000080u
#define HHS_VERIFY_BAD_WITNESS        0x00000100u
#define HHS_VERIFY_BAD_ORIENTATION    0x00000200u
#define HHS_VERIFY_BAD_CONSTRAINT     0x00000400u


// ============================================================
// VERIFY RESULT
// ============================================================

typedef struct {

    uint32_t flags;

    char expected_hash72[73];
    char observed_hash72[73];

    uint64_t replay_steps;

    uint32_t expected_witness;
    uint32_t observed_witness;

} HHS_VerifyResult;


// ============================================================
// HASH72 COMPARISON
// ============================================================

static int hhs_hash72_equal(
    const char *A,
    const char *B
) {

    if (!A || !B)
        return 0;

    return strcmp(A, B) == 0;
}


// ============================================================
// ORIENTATION CHECK
// ============================================================

static int hhs_verify_orientation(
    VM81 *vm
) {

    int bal =
        wrap72(
            (int)vm->xyzw[0]
            + (int)vm->xyzw[1]
            - (int)vm->xyzw[2]
            - (int)vm->xyzw[3]
        );

    return bal == 0;
}


// ============================================================
// CONSTRAINT CHECK
// ============================================================

static int hhs_verify_constraints(
    VM81 *vm
) {

    for (uint64_t i = 0;
         i < vm->constraint_count;
         i++)
    {
        Constraint72 *k =
            &vm->constraints[i];

        if (
            k->active &&
            k->strength > CONSTRAINT_CLOSURE_THRESHOLD
        ) {
            return 0;
        }
    }

    return 1;
}


// ============================================================
// BLOCK HASH72 VERIFY
// ============================================================

int hhs_verify_ir_hash72(
    HHS_IR_Block *blk,
    const char *expected,
    HHS_VerifyResult *res
) {

    if (!blk || !expected || !res)
        return 0;

    char observed[73];

    memset(observed, 0, sizeof(observed));

    hhs_ir_hash72_seal(
        blk,
        observed
    );

    strncpy(
        res->expected_hash72,
        expected,
        72
    );

    strncpy(
        res->observed_hash72,
        observed,
        72
    );

    if (!hhs_hash72_equal(
            expected,
            observed
        ))
    {
        res->flags |= HHS_VERIFY_BAD_HASH72;
        return 0;
    }

    return 1;
}


// ============================================================
// RECEIPT VERIFY
// ============================================================

int hhs_verify_receipt_packet(
    VM81 *vm,
    HHS_ReceiptPacket *pkt,
    HHS_VerifyResult *res
) {

    if (!vm || !pkt || !res)
        return 0;

    if (pkt->magic != HHS_RECEIPT_MAGIC) {

        res->flags |= HHS_VERIFY_BAD_MAGIC;
        return 0;
    }

    if (!hhs_hash72_equal(
            pkt->state_hash72,
            vm->last_receipt.state_h72
        ))
    {
        res->flags |= HHS_VERIFY_BAD_RECEIPT;
        return 0;
    }

    if (pkt->witness != vm->last_receipt.witness) {

        res->flags |= HHS_VERIFY_BAD_WITNESS;
        return 0;
    }

    return 1;
}


// ============================================================
// PARENT CHAIN VERIFY
// ============================================================

int hhs_verify_parent_chain(
    HHS_IR_Block *parent,
    HHS_IR_Block *child,
    HHS_VerifyResult *res
) {

    if (!parent || !child || !res)
        return 0;

    char seal[73];

    hhs_ir_hash72_seal(
        parent,
        seal
    );

    uint64_t expected = 0;

    for (int i = 0; i < 16; i++) {

        expected <<= 4;

        expected ^=
            hash72_index(seal[i]);
    }

    if (child->parent_block != expected) {

        res->flags |= HHS_VERIFY_BAD_PARENT;

        return 0;
    }

    return 1;
}


// ============================================================
// VM REPLAY VERIFY
// ============================================================

int hhs_verify_replay(
    VM81 *vm,
    HHS_IR_Block *blk,
    const char *expected_hash72,
    HHS_VerifyResult *res
) {

    if (!vm || !blk || !res)
        return 0;

    char before[73];
    char after[73];

    project_hash72(vm, before);

    uint64_t start_step = vm->step;

    if (!hhs_ir_execute_block(
            vm,
            blk
        ))
    {
        res->flags |= HHS_VERIFY_BAD_REPLAY;
        return 0;
    }

    project_hash72(vm, after);

    res->replay_steps =
        vm->step - start_step;

    strncpy(
        res->observed_hash72,
        after,
        72
    );

    strncpy(
        res->expected_hash72,
        expected_hash72,
        72
    );

    if (!hhs_hash72_equal(
            after,
            expected_hash72
        ))
    {
        res->flags |= HHS_VERIFY_BAD_REPLAY;
        return 0;
    }

    if (!hhs_verify_orientation(vm)) {

        res->flags |= HHS_VERIFY_BAD_ORIENTATION;
    }

    if (!hhs_verify_constraints(vm)) {

        res->flags |= HHS_VERIFY_BAD_CONSTRAINT;
    }

    return 1;
}


// ============================================================
// FULL VERIFY
// ============================================================

int hhs_verify_full(
    VM81 *vm,
    HHS_IR_Block *parent,
    HHS_IR_Block *child,
    HHS_ReceiptPacket *pkt,
    const char *expected_hash72,
    HHS_VerifyResult *res
) {

    if (!res)
        return 0;

    memset(res, 0, sizeof(*res));

    int ok = 1;

    if (parent && child) {

        if (!hhs_verify_parent_chain(
                parent,
                child,
                res
            ))
        {
            ok = 0;
        }
    }

    if (child && expected_hash72) {

        if (!hhs_verify_ir_hash72(
                child,
                expected_hash72,
                res
            ))
        {
            ok = 0;
        }
    }

    if (vm && pkt) {

        if (!hhs_verify_receipt_packet(
                vm,
                pkt,
                res
            ))
        {
            ok = 0;
        }
    }

    if (vm && child && expected_hash72) {

        if (!hhs_verify_replay(
                vm,
                child,
                expected_hash72,
                res
            ))
        {
            ok = 0;
        }
    }

    if (ok)
        res->flags |= HHS_VERIFY_OK;

    return ok;
}


// ============================================================
// DEBUG PRINT
// ============================================================

void hhs_verify_print(
    HHS_VerifyResult *res
) {

    if (!res)
        return;

    printf("\n");

    printf("---- HHS VERIFY ----\n");

    printf(
        "flags            : 0x%08X\n",
        res->flags
    );

    printf(
        "replay_steps     : %llu\n",
        (unsigned long long)
        res->replay_steps
    );

    printf(
        "expected_hash72  : %s\n",
        res->expected_hash72
    );

    printf(
        "observed_hash72  : %s\n",
        res->observed_hash72
    );

    printf(
        "expected_witness : 0x%08X\n",
        res->expected_witness
    );

    printf(
        "observed_witness : 0x%08X\n",
        res->observed_witness
    );

    printf("--------------------\n");
}