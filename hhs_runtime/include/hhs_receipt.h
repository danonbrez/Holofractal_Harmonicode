// hhs_runtime/include/hhs_receipt.h
//
// HHS / HARMONICODE
// Canonical Receipt ABI
//
// Runtime Principle:
//
//   receipts
//   =
//   reconstructible manifold witnesses
//
// NOT:
//   VM-local debug artifacts
//

#ifndef HHS_RECEIPT_H
#define HHS_RECEIPT_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

#define HHS_RECEIPT_HASH72_LEN 72

typedef struct HHSHash72 {

    char value[
        HHS_RECEIPT_HASH72_LEN + 1
    ];

} HHSHash72;

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

#ifdef __cplusplus
}
#endif

#endif