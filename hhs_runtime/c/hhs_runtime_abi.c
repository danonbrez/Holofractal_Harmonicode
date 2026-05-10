// ============================================================================
// hhs_runtime/c/hhs_runtime_abi.c
// HARMONICODE / HHS
// CANONICAL ABI IMPLEMENTATION LAYER
//
// PURPOSE
// -------
// Stable exported runtime surface for:
//
//   - Python ctypes bridge
//   - cffi bridge
//   - websocket runtime transport
//   - graph persistence
//   - replay engines
//   - multimodal routing
//   - vector cache systems
//
// This file MUST remain ABI-stable.
//
// ============================================================================

#include "hhs_runtime_abi.h"

#include <string.h>
#include <stdlib.h>
#include <math.h>

// ============================================================================
// INTERNAL CONSTANTS
// ============================================================================

static const char HASH72_ALPHABET[73] =
"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";

// ============================================================================
// INTERNAL HELPERS
// ============================================================================

static inline uint8_t hhs_wrap72(int64_t v) {

    int64_t r = v % 72;

    if (r < 0)
        r += 72;

    return (uint8_t)r;
}

// ============================================================================
// HASH72
// ============================================================================

void hhs_hash72_project(
    const uint8_t* cells,
    HHSHash72 out_hash
) {

    if (!cells || !out_hash)
        return;

    for (size_t i = 0; i < HHS_HASH72_LEN; i++) {

        uint8_t v = hhs_wrap72(
            cells[i] + ((int)i * 3)
        );

        out_hash[i] = HASH72_ALPHABET[v];
    }

    out_hash[72] = 0;
}

// ============================================================================
// HASH72 COMPARISON
// ============================================================================

uint64_t hhs_hash72_compare(
    const HHSHash72 a,
    const HHSHash72 b
) {

    if (!a || !b)
        return 0;

    uint64_t score = 0;

    for (size_t i = 0; i < HHS_HASH72_LEN; i++) {

        if (a[i] == b[i])
            score++;
    }

    return score;
}

// ============================================================================
// TENSOR RESET
// ============================================================================

void hhs_tensor_reset(
    HHSTensorState* tensor
) {

    if (!tensor)
        return;

    memset(tensor, 0, sizeof(HHSTensorState));
}

// ============================================================================
// APPLY XY TENSOR
// ============================================================================

void hhs_tensor_apply_xy(
    HHSTensorState* tensor,
    int64_t x,
    int64_t y
) {

    if (!tensor)
        return;

    tensor->xy = x * y;

    tensor->yx = y * x;

    tensor->transport =
        tensor->xy + tensor->yx;

    tensor->orientation =
        tensor->xy - tensor->yx;

    tensor->constraint =
        llabs(tensor->orientation);
}

// ============================================================================
// RUNTIME INIT
// ============================================================================

void hhs_runtime_init(
    HHSRuntimeState* state
) {

    if (!state)
        return;

    memset(state, 0, sizeof(HHSRuntimeState));

    state->runtime_magic = HHS_RUNTIME_MAGIC;

    state->abi_major = HHS_ABI_VERSION_MAJOR;
    state->abi_minor = HHS_ABI_VERSION_MINOR;
    state->abi_patch = HHS_ABI_VERSION_PATCH;

    state->lo_shu_slot = 5;

    state->closure_class = HHS_CLOSURE_NONE;

    state->genomic.genomic[0] = 1;
    state->genomic.genomic[1] = 3;
    state->genomic.genomic[2] = 5;
    state->genomic.genomic[3] = 7;

    memset(state->prev_hash72, 0, 73);
    memset(state->state_hash72, 0, 73);
    memset(state->receipt_hash72, 0, 73);
}

// ============================================================================
// RESET
// ============================================================================

void hhs_runtime_reset(
    HHSRuntimeState* state
) {

    hhs_runtime_init(state);
}

// ============================================================================
// TRANSPORT
// ============================================================================

void hhs_transport_apply(
    HHSRuntimeState* state,
    HHSTransportVector* flux
) {

    if (!state || !flux)
        return;

    state->flux.transport_flux +=
        flux->transport_flux;

    state->flux.orientation_flux +=
        flux->orientation_flux;

    state->flux.constraint_flux +=
        flux->constraint_flux;
}

// ============================================================================
// STEP
// ============================================================================

void hhs_runtime_step(
    HHSRuntimeState* state,
    HHSTensorState* tensor
) {

    if (!state)
        return;

    if (state->halted)
        return;

    state->step++;

    // --------------------------------------------------------------------
    // Tensor coupling
    // --------------------------------------------------------------------

    if (tensor) {

        state->tensor = *tensor;

        state->flux.transport_flux +=
            tensor->transport;

        state->flux.orientation_flux +=
            tensor->orientation;

        state->flux.constraint_flux +=
            tensor->constraint;
    }

    // --------------------------------------------------------------------
    // Closure logic
    // --------------------------------------------------------------------

    if (state->flux.orientation_flux == 0) {

        state->witness_flags |=
            W_ORIENTATION_CLOSED;
    }

    if (llabs(state->flux.constraint_flux) < 4) {

        state->witness_flags |=
            W_CONSTRAINT_CLOSED;
    }

    if ((state->step % 72) == 0) {

        state->witness_flags |=
            W_TRANSPORT_CLOSED;
    }

    uint64_t closure_mask =
        W_TRANSPORT_CLOSED |
        W_ORIENTATION_CLOSED |
        W_CONSTRAINT_CLOSED;

    if ((state->witness_flags & closure_mask)
        == closure_mask)
    {
        state->converged = 1;

        state->closure_class =
            HHS_CLOSURE_CONVERGED;

        state->witness_flags |=
            W_CONVERGED;
    }

    // --------------------------------------------------------------------
    // Orbit logic
    // --------------------------------------------------------------------

    if ((state->step % 144) == 0) {

        state->orbit_id++;

        state->witness_flags |=
            W_ORBIT_DETECTED;
    }

    // --------------------------------------------------------------------
    // Generate deterministic pseudo-cell layer
    // --------------------------------------------------------------------

    uint8_t cells[72];

    for (size_t i = 0; i < 72; i++) {

        cells[i] = hhs_wrap72(
            state->step
            + i
            + state->tensor.xy
            + state->tensor.yx
        );
    }

    memcpy(
        state->prev_hash72,
        state->state_hash72,
        73
    );

    hhs_hash72_project(
        cells,
        state->state_hash72
    );

    // --------------------------------------------------------------------
    // Receipt projection
    // --------------------------------------------------------------------

    for (size_t i = 0; i < 72; i++) {

        uint8_t v =
            hhs_wrap72(
                state->state_hash72[i]
                + state->step
                + i
            );

        state->receipt_hash72[i] =
            HASH72_ALPHABET[v];
    }

    state->receipt_hash72[72] = 0;
}

// ============================================================================
// HALT
// ============================================================================

void hhs_runtime_halt(
    HHSRuntimeState* state
) {

    if (!state)
        return;

    state->halted = 1;

    state->witness_flags |=
        W_HALT_REACHED;

    state->witness_flags |=
        W_LEDGER_FROZEN;
}

// ============================================================================
// RECEIPT RESET
// ============================================================================

void hhs_receipt_reset(
    HHSReceipt* receipt
) {

    if (!receipt)
        return;

    memset(receipt, 0, sizeof(HHSReceipt));
}

// ============================================================================
// RECEIPT COMMIT
// ============================================================================

void hhs_receipt_commit(
    HHSRuntimeState* state,
    HHSReceipt* receipt
) {

    if (!state || !receipt)
        return;

    memcpy(
        receipt->parent_receipt,
        state->prev_hash72,
        73
    );

    memcpy(
        receipt->current_receipt,
        state->receipt_hash72,
        73
    );

    receipt->step =
        state->step;

    receipt->witness_flags =
        state->witness_flags;

    receipt->entropy_delta =
        state->flux.constraint_flux;

    receipt->closure_delta =
        state->converged ? 1 : 0;
}

// ============================================================================
// VECTORIZE HASH72
// ============================================================================

void hhs_vectorize_hash72(
    const HHSHash72 hash72,
    float out_vector[72]
) {

    if (!hash72 || !out_vector)
        return;

    for (size_t i = 0; i < 72; i++) {

        out_vector[i] =
            ((float)((uint8_t)hash72[i])) / 255.0f;
    }
}

// ============================================================================
// GRAPH NODE HASH
// ============================================================================

uint64_t hhs_graph_node_hash(
    const HHSGraphNode* node
) {

    if (!node)
        return 0;

    uint64_t h = node->node_id;

    for (size_t i = 0; i < 72; i++) {

        h ^= ((uint64_t)node->hash72[i]) << (i % 8);
    }

    return h;
}

// ============================================================================
// ABI VALIDATION
// ============================================================================

int hhs_validate_abi(
    const HHSRuntimeState* state
) {

    if (!state)
        return 0;

    if (state->runtime_magic != HHS_RUNTIME_MAGIC)
        return 0;

    if (state->abi_major != HHS_ABI_VERSION_MAJOR)
        return 0;

    return 1;
}

// ============================================================================
// ABI SIZE EXPORTS
// ============================================================================

size_t hhs_sizeof_runtime_state(void) {

    return sizeof(HHSRuntimeState);
}

size_t hhs_sizeof_receipt(void) {

    return sizeof(HHSReceipt);
}

size_t hhs_sizeof_tensor_state(void) {

    return sizeof(HHSTensorState);
}

size_t hhs_sizeof_graph_node(void) {

    return sizeof(HHSGraphNode);
}

size_t hhs_sizeof_graph_edge(void) {

    return sizeof(HHSGraphEdge);
}