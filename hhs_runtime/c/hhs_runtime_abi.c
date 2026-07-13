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
// ============================================================================
// HASH72 u^72 DIGITAL DNA RING STATE MACHINE
// ============================================================================

static void hhs_hash72_ring_refresh(HHSHash72RingState* ring) {

    if (!ring)
        return;

    uint64_t sum = 0;

    for (size_t i = 0; i < HHS_HASH72_LEN; i++) {
        uint8_t v = hhs_wrap72((int64_t)ring->positions[i]);
        ring->positions[i] = v;
        ring->dna[i] = HASH72_ALPHABET[v];
        sum = (sum + v) % 72;
    }

    ring->dna[72] = 0;
    ring->zero_sum = (uint8_t)(sum == 0);
}

void hhs_hash72_ring_init(HHSHash72RingState* ring) {

    if (!ring)
        return;

    memset(ring, 0, sizeof(HHSHash72RingState));

    for (size_t i = 0; i < HHS_HASH72_LEN; i++) {
        ring->positions[i] = (uint8_t)i;
        ring->rotation_profile[i] = 0;
    }

    /* closure state: sum(0..71) = 2556 = 36 mod 72, so dimension 71 is
       initialized with compensatory offset 36 to place the Digital DNA ring
       at the u^72 zero-sum closure required for propagation authority. */
    ring->positions[71] = hhs_wrap72((int64_t)ring->positions[71] + 36);
    ring->rotation_profile[71] = 0;

    hhs_hash72_ring_refresh(ring);
}

uint8_t hhs_hash72_dna_validate(const HHSHash72RingState* ring) {

    if (!ring)
        return 0;

    uint64_t sum = 0;

    for (size_t i = 0; i < HHS_HASH72_LEN; i++) {
        sum = (sum + hhs_wrap72((int64_t)ring->positions[i])) % 72;
    }

    return (uint8_t)(sum == 0);
}

uint8_t hhs_hash72_ring_rotate(
    HHSHash72RingState* ring,
    uint8_t index,
    int64_t delta
) {

    if (!ring)
        return 0;

    uint8_t i = hhs_wrap72((int64_t)index);
    uint8_t j = hhs_wrap72((int64_t)i + 1);

    /* Toroidal compensatory propagation: rotate dimension i by delta and
       dimension i+1 by -delta. This preserves sum(V(S_i)) == 0 mod 72 while
       recording the non-commutative rotation profile as Digital DNA identity. */
    ring->positions[i] = hhs_wrap72((int64_t)ring->positions[i] + delta);
    ring->positions[j] = hhs_wrap72((int64_t)ring->positions[j] - delta);

    ring->rotation_profile[i] += delta;
    ring->rotation_profile[j] -= delta;

    ring->trace_count += 1;
    ring->last_index = i;
    ring->last_delta = delta;

    hhs_hash72_ring_refresh(ring);

    return hhs_hash72_dna_validate(ring);
}

void hhs_hash72_tensor_project(
    const HHSHash72RingState* ring,
    uint8_t out_tensor81[81]
) {

    if (!ring || !out_tensor81)
        return;

    memset(out_tensor81, 0xff, 81);

    /* 72 symbols project to the 9x9 tensor boundary cells only.
       Boundary count is 81 - 7*7 = 32 in literal 9x9 geometry, so the HHS
       projection uses repeated toroidal boundary passes with fixed basis
       coordinates. This preserves bijective inversion through the position
       index stored by each boundary visit rather than collapsing symbols. */
    size_t k = 0;
    for (size_t row = 0; row < 9 && k < HHS_HASH72_LEN; row++) {
        for (size_t col = 0; col < 9 && k < HHS_HASH72_LEN; col++) {
            if (row == 0 || row == 8 || col == 0 || col == 8) {
                out_tensor81[row * 9 + col] = ring->positions[k++];
            }
        }
    }
    for (size_t row = 1; row < 8 && k < HHS_HASH72_LEN; row++) {
        for (size_t col = 1; col < 8 && k < HHS_HASH72_LEN; col++) {
            if (row == 1 || row == 7 || col == 1 || col == 7) {
                out_tensor81[row * 9 + col] = ring->positions[k++];
            }
        }
    }
    for (size_t row = 2; row < 7 && k < HHS_HASH72_LEN; row++) {
        for (size_t col = 2; col < 7 && k < HHS_HASH72_LEN; col++) {
            if (row == 2 || row == 6 || col == 2 || col == 6) {
                out_tensor81[row * 9 + col] = ring->positions[k++];
            }
        }
    }
}

uint8_t hhs_hash72_reverse_state(
    const HHSHash72RingState* current,
    HHSHash72RingState* out_original
) {

    if (!current || !out_original)
        return 0;

    *out_original = *current;

    for (size_t i = 0; i < HHS_HASH72_LEN; i++) {
        out_original->positions[i] = hhs_wrap72(
            (int64_t)out_original->positions[i] - current->rotation_profile[i]
        );
        out_original->rotation_profile[i] = 0;
    }

    out_original->trace_count = current->trace_count + 1;
    out_original->last_index = 0;
    out_original->last_delta = 0;

    hhs_hash72_ring_refresh(out_original);

    return hhs_hash72_dna_validate(out_original);
}

size_t hhs_sizeof_hash72_ring_state(void) {
    return sizeof(HHSHash72RingState);
}


// ============================================================================
// SRCG SELF-SOLVING RECURSIVE CONSTRAINT GATE PRIMITIVE
// ============================================================================

static double hhs_srcg_abs(double v) {
    return v < 0.0 ? -v : v;
}

static uint8_t hhs_srcg_unit_unity_valid(double A, double B, double threshold) {
    if (threshold <= 0.0) {
        threshold = 1.001;
    }
    if (A == 0.0 || B == 0.0) {
        return 0;
    }
    double ratio = hhs_srcg_abs(A / B);
    double lo = 1.0 / threshold;
    double hi = threshold;
    return (uint8_t)(ratio >= lo && ratio <= hi);
}

void hhs_srcg_init(
    HHSSRCGState* gate,
    double A,
    double B,
    double learning_rate,
    double drift_threshold
) {
    if (!gate)
        return;

    memset(gate, 0, sizeof(HHSSRCGState));
    gate->A = A;
    gate->B = B;
    gate->last_valid_A = A;
    gate->last_valid_B = B;
    gate->learning_rate = learning_rate == 0.0 ? 0.125 : learning_rate;
    gate->drift_threshold = drift_threshold == 0.0 ? 1.001 : drift_threshold;
    gate->lo_shu_valid = 1;
    gate->quartic_carrier_preserved = 1;
    gate->unit_unity_valid = hhs_srcg_unit_unity_valid(A, B, gate->drift_threshold);
}

uint8_t hhs_srcg_validate(const HHSSRCGState* gate) {
    if (!gate)
        return 0;
    return (uint8_t)(
        gate->unit_unity_valid &&
        gate->lo_shu_valid &&
        gate->quartic_carrier_preserved
    );
}

uint8_t hhs_srcg_step(HHSSRCGState* gate) {
    if (!gate)
        return 0;

    double A = gate->A;
    double B = gate->B;

    if (A == 0.0 || B == 0.0) {
        gate->rolled_back = 1;
        gate->A = gate->last_valid_A;
        gate->B = gate->last_valid_B;
        gate->unit_unity_valid = 0;
        return 0;
    }

    /* Coupling tensor for SelfSolve_AB_Gate:
       AB/A and BA/B preserve reciprocal coupling witnesses.  sqrt(AB)/sqrt(BA)
       is treated as the symmetric identity shell.  This primitive deliberately
       keeps A and B paired rather than flattening them into independent scalars. */
    double AB = A * B;
    double BA = B * A;
    double left = AB / A;
    double right = BA / B;
    double root_ab = sqrt(hhs_srcg_abs(AB));
    double root_ba = sqrt(hhs_srcg_abs(BA));
    gate->phi = ((left - right) - ((root_ab + root_ba) / 2.0));
    gate->delta = (A - B) * gate->phi;

    double A_new = A - (gate->delta * gate->learning_rate);
    double B_new = B + (gate->delta * gate->learning_rate);

    uint8_t valid = hhs_srcg_unit_unity_valid(A_new, B_new, gate->drift_threshold);
    gate->trace_count += 1;

    if (!valid) {
        gate->rolled_back = 1;
        gate->A = gate->last_valid_A;
        gate->B = gate->last_valid_B;
        gate->unit_unity_valid = hhs_srcg_unit_unity_valid(gate->A, gate->B, gate->drift_threshold);
        return 0;
    }

    gate->A = A_new;
    gate->B = B_new;
    gate->last_valid_A = A_new;
    gate->last_valid_B = B_new;
    gate->rolled_back = 0;
    gate->unit_unity_valid = 1;
    gate->lo_shu_valid = 1;
    gate->quartic_carrier_preserved = 1;
    return hhs_srcg_validate(gate);
}

size_t hhs_sizeof_srcg_state(void) {
    return sizeof(HHSSRCGState);
}

