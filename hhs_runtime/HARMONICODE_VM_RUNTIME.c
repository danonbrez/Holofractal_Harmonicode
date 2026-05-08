// hhs_vm81_runtime_freeze.c
// HARMONICODE / HHS substrate runtime CANONICAL FREEZE
//
// Canonical freeze policy:
// - Preserve v7.2 substrate / receipt / closure semantics as locked base.
// - Preserve verbatim-compatible common runtime structure.
// - Admit duplicated updates from independent branches where non-conflicting.
// - Layer additional functions on top of the locked structure.
//
// Build:
//   gcc -O2 -std=c11 hhs_vm81_runtime_freeze.c -lm -o hhs_vm81
//
// Run:
//   ./hhs_vm81 --trace
//   ./hhs_vm81 --halt-on-orbit --verify
//
// Freeze contents:
// - v7.2 receipt-advance gating: HALT does not extend the ledger
// - v7.2 closure class decomposition:
//     W_CLOSE_TRANSPORT, W_CLOSE_ORIENTATION, W_CLOSE_CONSTRAINT
//     W_CONVERGED = joint all-three closure
// - v7.2 explicit CONSTRAINT_CLOSURE_THRESHOLD
// - v7.2 frozen-receipt trace annotation
// - Duplicated branch update: math runtime / -lm support
// - Layered identity gate from v7.3
// - Layered HHS/tensor/manifold/genomic extension functions

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ============================================================
// CONSTANTS
// ============================================================

#define GRID_SIZE                     81
#define HASH_LEN                      72
#define MAX_PROGRAM                   256
#define MAX_STEPS                     (1 << 20)
#define MAX_SEEN                      8192
#define MAX_CONSTRAINTS               64
#define MAX_LINE                      256

#define CONSTRAINT_CLOSURE_THRESHOLD  4

#define IDENTITY_LOG_TOL              1.0e-6

#define MAX_TENSORS                   512
#define MANIFOLD_DIM                  9

// ============================================================
// HASH72
// ============================================================

static const char HASH72[73] =
"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";

static int16_t HASH72_IDX[256];

// ============================================================
// LO SHU
// ============================================================

static const uint8_t LOSHU[9] = {
    4,9,2,
    3,5,7,
    8,1,6
};

static uint8_t LOSHU_SLOTS[9];

static const uint64_t PALINDROME_SEED = 179971179971ULL;

// ============================================================
// OPCODES
// ============================================================

typedef enum {

    OP_NOP = 0,

    OP_ADD,
    OP_SUB,
    OP_ROT,
    OP_XOR,
    OP_AND,
    OP_OR,

    OP_LOAD,
    OP_STORE,

    OP_BRANCH,
    OP_BZ,
    OP_BNZ,

    OP_MULXY,
    OP_MULYX,

    OP_QGU,

    OP_GATE_APB,
    OP_GATE_CLOSURE,
    OP_GATE_IDENTITY,

    OP_QBRANCH,

    OP_CONSTRAIN,
    OP_RELAX,

    OP_SWEEP81,
    OP_CLOSE81,

    OP_HALT,

    OP__COUNT

} Opcode;

static const char *OP_NAMES[OP__COUNT] = {

    "NOP",

    "ADD",
    "SUB",
    "ROT",
    "XOR",
    "AND",
    "OR",

    "LOAD",
    "STORE",

    "BRANCH",
    "BZ",
    "BNZ",

    "MULXY",
    "MULYX",

    "QGU",

    "GATE_APB",
    "GATE_CLOSURE",
    "GATE_IDENTITY",

    "QBRANCH",

    "CONSTRAIN",
    "RELAX",

    "SWEEP81",
    "CLOSE81",

    "HALT"
};

// ============================================================
// LEDGER ADVANCE PREDICATE
// Ops that represent pure control transitions do not advance
// the receipt chain; they only annotate the terminal frame.
// ============================================================

static int op_advances_ledger(Opcode op) {

    switch (op) {

        case OP_HALT:
            return 0;

        default:
            return 1;
    }
}

// ============================================================
// EDGE
// ============================================================

typedef struct {
    uint8_t enabled;
    uint8_t target;
} Edge81;

// ============================================================
// INSTRUCTION
// ============================================================

typedef struct {

    Opcode op;

    uint8_t a;
    uint8_t b;
    uint8_t c;

    uint8_t cg_id;
    uint8_t phase;

    Edge81 next[4];

} Instruction;

// ============================================================
// LAYERED TENSOR EXTENSION
// ============================================================

typedef struct {

    double real;
    double imag;

    uint8_t phase;
    uint8_t orientation;

} HHSTensor;

// ============================================================
// WITNESS FLAGS
// ============================================================

#define W_GATE_APB_PASS        0x00001
#define W_GATE_APB_FAIL        0x00002

#define W_GATE_CLOSURE_PASS    0x00004
#define W_GATE_CLOSURE_FAIL    0x00008

#define W_QGU_APPLIED          0x00010
#define W_NONCOMMUTATIVE       0x00020

#define W_CONSTRAINT_FIRED     0x00040
#define W_ORBIT_DETECTED       0x00080

#define W_HALT                 0x00100
#define W_SWEEP                0x00200

// Decomposed closure classes
#define W_CLOSE_TRANSPORT      0x00400
#define W_CLOSE_ORIENTATION    0x00800
#define W_CLOSE_CONSTRAINT     0x01000

// Joint closure
#define W_CONVERGED            0x02000

// Ledger frozen
#define W_LEDGER_FROZEN        0x04000

// Layered identity-gate witness bits
#define W_GATE_IDENTITY_PASS   0x08000
#define W_GATE_IDENTITY_FAIL   0x10000
#define W_IDENTITY_DEGENERATE  0x20000

// ============================================================
// RECEIPT
// ============================================================

typedef struct {

    char prev_h72[73];
    char state_h72[73];
    char receipt_h72[73];

    uint8_t cg_id;

    uint32_t witness;

    uint64_t step;
    uint64_t orbit_period;

    int ledger_advanced;

    double identity_residual;
    int identity_has_data;

} VMReceipt;

// ============================================================
// CONSTRAINT
// ============================================================

typedef struct {

    uint8_t type;
    uint8_t phase;
    uint8_t strength;

    uint8_t active;

    uint64_t lineage;

} Constraint72;

// ============================================================
// ORBIT TABLE
// ============================================================

typedef struct {

    char hash[73];
    uint64_t step;

} SeenState;

// ============================================================
// VM
// ============================================================

typedef struct {

    uint8_t cells[GRID_SIZE];

    uint64_t step;
    uint64_t sweep;
    uint64_t pc;

    int halted;
    int orbit_halted;

    int converged;

    // Latched closure state across the whole run
    int ever_closed_transport;
    int ever_closed_orientation;
    int ever_closed_constraint;

    int ever_identity_pass;

    Instruction program[MAX_PROGRAM];
    uint64_t program_len;

    char genesis_hash[73];

    VMReceipt last_receipt;

    SeenState seen[MAX_SEEN];
    uint64_t seen_count;

    Constraint72 constraints[MAX_CONSTRAINTS];
    uint64_t constraint_count;

    uint8_t xyzw[4];

    HHSTensor tensors[MAX_TENSORS];
    uint64_t tensor_count;

    double manifold[MANIFOLD_DIM][MANIFOLD_DIM];

    uint8_t genomic[4];

} VM81;

// ============================================================
// SEED MODE
// ============================================================

typedef enum {
    SEED_PLAIN,
    SEED_LOSHU,
    SEED_PALINDROME
} SeedMode;

// ============================================================
// UTILITIES
// ============================================================

static inline uint8_t wrap72(int v) {

    int r = v % 72;

    if (r < 0)
        r += 72;

    return (uint8_t)r;
}

static inline uint8_t reciprocal_phase(uint8_t p) {
    return (uint8_t)((p + 36) % 72);
}

static inline uint8_t hash72_index(char ch) {

    int v = HASH72_IDX[(uint8_t)ch];

    if (v < 0 || v >= 72)
        return 0;

    return (uint8_t)v;
}

static inline uint8_t polarity_of(uint8_t p) {

    return (uint8_t)((p / 18) & 3);
}

// ============================================================
// INIT
// ============================================================

static void init_hash72(void) {

    memset(HASH72_IDX, -1, sizeof(HASH72_IDX));

    for (int i = 0; i < 72; i++) {
        HASH72_IDX[(uint8_t)HASH72[i]] = (int16_t)i;
    }

    for (int k = 0; k < 9; k++) {
        LOSHU_SLOTS[k] = (uint8_t)(LOSHU[k] * 8 - 1);
    }
}

// ============================================================
// CONSTRAINT FIELD
// ============================================================

static uint8_t constraint_bias_at(VM81 *vm, uint8_t phase) {

    uint32_t acc = 0;

    for (uint64_t i = 0; i < vm->constraint_count; i++) {

        Constraint72 *k = &vm->constraints[i];

        if (!k->active || k->strength == 0)
            continue;

        int d = (int)phase - (int)k->phase;

        d = ((d % 72) + 72) % 72;

        int dist = d < 36 ? d : 72 - d;

        if (dist < 6) {
            acc += (uint32_t)k->strength * (uint32_t)(6 - dist);
        }
    }

    return wrap72((int)(acc % 72));
}

static void constraint_add(
    VM81 *vm,
    uint8_t type,
    uint8_t phase,
    uint8_t strength
) {

    if (vm->constraint_count < MAX_CONSTRAINTS) {

        Constraint72 *k =
            &vm->constraints[vm->constraint_count++];

        k->type = type;
        k->phase = phase % 72;
        k->strength = strength;
        k->active = 1;
        k->lineage = vm->step;

        return;
    }

    uint64_t weakest = 0;

    for (uint64_t i = 1; i < vm->constraint_count; i++) {

        if (vm->constraints[i].strength <
            vm->constraints[weakest].strength)
        {
            weakest = i;
        }
    }

    Constraint72 *k = &vm->constraints[weakest];

    k->type = type;
    k->phase = phase % 72;
    k->strength = strength;
    k->active = 1;
    k->lineage = vm->step;
}

static void constraint_relax(VM81 *vm, uint8_t amount) {

    if (amount == 0)
        amount = 1;

    for (uint64_t i = 0; i < vm->constraint_count; i++) {

        Constraint72 *k = &vm->constraints[i];

        if (!k->active)
            continue;

        if (k->strength <= amount) {

            k->strength = 0;
            k->active = 0;
        }
        else {

            k->strength -= amount;
        }
    }
}

static void constraint_compete(VM81 *vm) {

    for (uint64_t i = 0; i < vm->constraint_count; i++) {

        Constraint72 *A = &vm->constraints[i];

        if (!A->active || A->strength == 0)
            continue;

        for (uint64_t j = i + 1;
             j < vm->constraint_count;
             j++)
        {
            Constraint72 *B = &vm->constraints[j];

            if (!B->active || B->strength == 0)
                continue;

            if (reciprocal_phase(A->phase) == B->phase) {

                uint8_t m =
                    A->strength < B->strength ?
                    A->strength :
                    B->strength;

                A->strength -= m;
                B->strength -= m;

                if (A->strength == 0)
                    A->active = 0;

                if (B->strength == 0)
                    B->active = 0;
            }
        }
    }
}

// ============================================================
// PHASE TRANSPORT
// ============================================================

static void propagate_phase_transport(
    VM81 *vm,
    uint8_t origin,
    uint8_t energy,
    uint8_t cg
) {

    vm->cells[origin] =
        wrap72(
            vm->cells[origin]
            + energy
            + cg
            + constraint_bias_at(vm, origin)
        );

    uint8_t r0 = reciprocal_phase(origin);

    vm->cells[r0] =
        wrap72(vm->cells[origin] + 36);

    for (int radius = 1; radius < 6; radius++) {

        uint8_t L =
            wrap72((int)origin - radius);

        uint8_t R =
            wrap72((int)origin + radius);

        vm->cells[L] =
            wrap72(
                vm->cells[L]
                + energy
                + cg
                + radius
                + constraint_bias_at(vm, L)
            );

        vm->cells[R] =
            wrap72(
                vm->cells[R]
                + energy
                + cg
                + radius
                + 1
                + constraint_bias_at(vm, R)
            );

        vm->cells[reciprocal_phase(L)] =
            wrap72(vm->cells[L] + 36);

        vm->cells[reciprocal_phase(R)] =
            wrap72(vm->cells[R] + 36);
    }

    for (int i = 0; i < 72; i++) {

        uint8_t delta =
            wrap72(i - origin);

        uint8_t h =
            (uint8_t)((energy + cg + delta) % 9);

        vm->cells[i] =
            wrap72(vm->cells[i] + h);
    }

    for (int i = 72; i < GRID_SIZE; i++) {

        uint8_t t =
            (uint8_t)((energy + cg + i + origin) % 72);

        vm->cells[i] =
            wrap72(vm->cells[i] + (t % 5));
    }
}

// ============================================================
// XYZW
// ============================================================

static void apply_xyzw_state(
    VM81 *vm,
    uint8_t a,
    uint8_t b,
    int xy_order
) {

    if (xy_order) {

        vm->xyzw[0] =
            wrap72(vm->xyzw[0] + a);

        vm->xyzw[1] =
            wrap72(vm->xyzw[1] + b);
    }
    else {

        vm->xyzw[1] =
            wrap72(vm->xyzw[1] + a);

        vm->xyzw[0] =
            wrap72(vm->xyzw[0] + b);
    }

    vm->xyzw[2] =
        wrap72(
            vm->xyzw[2]
            + (vm->xyzw[0] ^ vm->xyzw[1])
        );

    vm->xyzw[3] =
        wrap72(
            vm->xyzw[0]
            + vm->xyzw[1]
            - vm->xyzw[2]
        );
}

// ============================================================
// SWEEP81
// ============================================================

static void sweep81(VM81 *vm) {

    uint8_t next[GRID_SIZE];

    for (int r = 0; r < 9; r++) {

        for (int c = 0; c < 9; c++) {

            int i = r * 9 + c;

            int acc = vm->cells[i];

            acc += vm->cells[((r + 8) % 9) * 9 + c];
            acc += vm->cells[((r + 1) % 9) * 9 + c];

            acc += vm->cells[r * 9 + ((c + 8) % 9)];
            acc += vm->cells[r * 9 + ((c + 1) % 9)];

            next[i] = wrap72(acc * 29);
        }
    }

    memcpy(vm->cells, next, GRID_SIZE);
}

// ============================================================
// CLOSE81
// ============================================================

static void close81(VM81 *vm) {

    for (int k = 0; k < 9; k++) {

        int idx = 72 + k;

        vm->cells[idx] =
            wrap72(
                vm->cells[idx]
                + LOSHU[k]
            );
    }

    for (int k = 0; k < 9; k++) {

        int idx = 63 + k;

        vm->cells[idx] =
            wrap72(
                vm->cells[idx]
                + LOSHU[k]
            );
    }
}

// ============================================================
// PROJECTION
// ============================================================

static void project_hash72(
    VM81 *vm,
    char out[73]
) {

    uint8_t hidden_for_slot[HASH_LEN];

    memset(hidden_for_slot, 0xFF,
           sizeof(hidden_for_slot));

    for (int k = 0; k < 9; k++) {

        uint8_t slot = LOSHU_SLOTS[k];

        hidden_for_slot[slot] = 72 + k;
    }

    for (int i = 0; i < HASH_LEN; i++) {

        uint8_t g =
            hash72_index(vm->genesis_hash[i]);

        uint8_t h_contrib = 0;

        if (hidden_for_slot[i] != 0xFF) {

            uint8_t hcell =
                vm->cells[hidden_for_slot[i]];

            h_contrib =
                wrap72(
                    hcell
                    + (hidden_for_slot[i] - 72) * 7
                );
        }

        uint8_t v =
            wrap72(
                vm->cells[i]
                + g
                + h_contrib
                + (i * 3)
            );

        out[i] = HASH72[v];
    }

    out[72] = 0;
}

// ============================================================
// RECEIPT HASH
// ============================================================

static void compose_receipt_hash(
    const char *prev,
    uint8_t cg,
    uint32_t witness,
    const char *state,
    char out[73]
) {

    for (int i = 0; i < HASH_LEN; i++) {

        uint8_t p =
            hash72_index(prev[i]);

        uint8_t s =
            hash72_index(state[i]);

        uint8_t w =
            (uint8_t)(
                (
                    witness
                    ^ (witness >> 8)
                    ^ (witness >> 16)
                    ^ (witness >> 24)
                    ^ i
                ) & 0xFF
            );

        uint8_t r =
            (uint8_t)(
                (p + s + cg + w + (i * 7))
                % 72
            );

        out[i] = HASH72[r];
    }

    out[72] = 0;
}

// ============================================================
// ORBIT
// ============================================================

static uint64_t detect_orbit(
    VM81 *vm,
    const char *hash,
    uint64_t cur
) {

    for (uint64_t i = 0;
         i < vm->seen_count;
         i++)
    {
        if (strcmp(vm->seen[i].hash, hash) == 0) {

            return cur - vm->seen[i].step;
        }
    }

    if (vm->seen_count < MAX_SEEN) {

        strcpy(vm->seen[vm->seen_count].hash, hash);

        vm->seen[vm->seen_count].step = cur;

        vm->seen_count++;
    }

    return 0;
}

// ============================================================
// CLOSURE RECOGNIZERS
// ============================================================

static int close_orientation(VM81 *vm) {

    int bal =
        wrap72(
            (int)vm->xyzw[0]
            + (int)vm->xyzw[1]
            - (int)vm->xyzw[2]
            - (int)vm->xyzw[3]
        );

    return bal == 0;
}

static int close_constraint(VM81 *vm) {

    for (uint64_t i = 0;
         i < vm->constraint_count;
         i++)
    {
        Constraint72 *k = &vm->constraints[i];

        if (k->active &&
            k->strength > CONSTRAINT_CLOSURE_THRESHOLD)
        {
            return 0;
        }
    }

    return 1;
}

// ============================================================
// GATES
// ============================================================

static int check_gate_apb(
    VM81 *vm,
    uint8_t A,
    uint8_t P,
    uint8_t B
) {

    return
        (vm->cells[A] == vm->cells[P]) &&
        (vm->cells[P] == vm->cells[B]);
}

static int check_gate_closure(
    VM81 *vm,
    uint8_t Pc,
    uint8_t pc,
    uint8_t qc,
    uint8_t nc,
    uint8_t xc,
    uint8_t yc
) {

    uint8_t P = vm->cells[Pc];
    uint8_t p = vm->cells[pc];
    uint8_t q = vm->cells[qc];

    uint8_t n = vm->cells[nc];
    uint8_t x = vm->cells[xc];
    uint8_t y = vm->cells[yc];

    uint8_t P2 = wrap72(P * P);

    uint8_t pq = wrap72(p * q);

    uint8_t lhs =
        wrap72((int)P2 - (int)pq);

    uint8_t n4 =
        wrap72(
            wrap72(n * n)
            * wrap72(n * n)
        );

    uint8_t xy =
        wrap72(x * y);

    return
        (lhs == n4) &&
        (n4 == xy);
}

// ============================================================
// IDENTITY GATE
// ============================================================

static int check_gate_identity(
    VM81 *vm,
    uint8_t xc,
    uint8_t yc,
    uint8_t uc,
    double *residual_out
) {

    double x = ((double)vm->cells[xc] - 35.5) / 36.0;
    double y = ((double)vm->cells[yc] - 35.5) / 36.0;
    double u = ((double)vm->cells[uc] - 35.5) / 36.0;

    if (residual_out)
        *residual_out = INFINITY;

    if (fabs(x) < 1e-12 || fabs(y) < 1e-12)
        return -1;

    double A = (x / y) * (y / x);

    double base2 = -x * y;
    double exp2  = ((x * x + y) * (y * y + x)) / 4.0;

    double B;

    if (base2 <= 0.0) {

        double rexp = round(exp2);
        double eps  = fabs(exp2 - rexp);

        if (eps > 1e-9)
            return -1;

        double mag = pow(fabs(base2), exp2);
        int odd = ((long long)rexp) & 1LL;

        B = (base2 < 0.0 && odd) ? -mag : mag;
    }
    else {

        B = pow(base2, exp2);
    }

    if (fabs(u) < 1e-12)
        return -1;

    double logC =
        log(4.0 * M_PI)
        + (x * M_PI)
        - 144.0 * log(fabs(u));

    double C = exp(logC);

    if (A <= 0.0)
        return 0;

    if (!isfinite(B) || !isfinite(C))
        return -1;

    if (B <= 0.0 || C <= 0.0)
        return 0;

    double lA = log(A);
    double lB = log(B);
    double lC = log(C);

    double r_AB = fabs(lA - lB);
    double r_AC = fabs(lA - lC);
    double r_BC = fabs(lB - lC);

    double worst = r_AB;

    if (r_AC > worst)
        worst = r_AC;

    if (r_BC > worst)
        worst = r_BC;

    if (residual_out)
        *residual_out = worst;

    return (worst < IDENTITY_LOG_TOL) ? 1 : 0;
}

// ============================================================
// QGU
// ============================================================

static uint8_t qgu_delta(
    uint8_t q,
    uint8_t c,
    uint8_t d
) {

    uint8_t q2 =
        wrap72(q * q);

    uint8_t q4 =
        wrap72(q2 * q2);

    return
        wrap72(c * q2 + d * q4);
}

// ============================================================
// LAYERED EXTENSIONS
// These functions do not replace the frozen v7.2 instruction,
// receipt, or closure model. They are utility layers available
// to callers and future opcodes.
// ============================================================

static double hhs_calc_m_reciprocal(uint8_t xy_energy) {

    double base =
        (8.0 / 5.0)
        + (11.0 / 7.0)
        + (13.0 / 8.0)
        + (3.0 / 2.0)
        + (5.0 / 3.0)
        + (7.0 / 4.0);

    return base / (2.0 * ((double)xy_energy + 1.0));
}

static void hhs_apply_ouroboros_closure(VM81 *vm) {

    uint8_t x = vm->xyzw[0];

    uint8_t x2 = wrap72(x * x);
    uint8_t x4 = wrap72(x2 * x2);

    vm->xyzw[3] = wrap72(x4 / 4);

    sweep81(vm);
}

static void tensor_push(
    VM81 *vm,
    double r,
    double i,
    uint8_t phase
) {

    if (vm->tensor_count >= MAX_TENSORS)
        return;

    HHSTensor *t = &vm->tensors[vm->tensor_count++];

    t->real = r;
    t->imag = i;
    t->phase = phase;
    t->orientation = phase & 1;
}

static void tensor_reciprocal(HHSTensor *t) {

    double denom =
        (t->real * t->real)
        + (t->imag * t->imag);

    if (fabs(denom) < 1e-12)
        return;

    double r = t->real;
    double i = t->imag;

    t->real = r / denom;
    t->imag = -i / denom;
}

static void tensor_phase_lock(
    HHSTensor *A,
    HHSTensor *B
) {

    uint8_t p =
        wrap72((A->phase + B->phase) / 2);

    A->phase = p;
    B->phase = p;
}

static void hhs_tensor_seed_from_xyzw(VM81 *vm) {

    tensor_push(
        vm,
        (double)vm->xyzw[0],
        (double)vm->xyzw[1],
        vm->xyzw[2]
    );

    tensor_push(
        vm,
        (double)vm->xyzw[2],
        (double)vm->xyzw[3],
        vm->xyzw[0]
    );

    if (vm->tensor_count >= 2)
        tensor_phase_lock(&vm->tensors[0], &vm->tensors[1]);
}

static void hhs_genomic_map(VM81 *vm) {

    vm->genomic[0] =
        wrap72(vm->genomic[0] + vm->xyzw[0]);

    vm->genomic[1] =
        wrap72(vm->genomic[1] + vm->xyzw[1]);

    vm->genomic[2] =
        wrap72(vm->genomic[2] + vm->xyzw[2]);

    vm->genomic[3] =
        wrap72(
            vm->genomic[0]
            + vm->genomic[1]
            - vm->genomic[2]
        );
}

static void hhs_manifold_step(VM81 *vm, uint8_t driver) {

    for (int r = 0; r < MANIFOLD_DIM; r++) {

        for (int c = 0; c < MANIFOLD_DIM; c++) {

            vm->manifold[r][c] +=
                sin((double)(r + c + driver));
        }
    }
}

// ============================================================
// VM INIT
// ============================================================

static void vm81_init(
    VM81 *vm,
    uint64_t seed,
    SeedMode mode
) {

    memset(vm, 0, sizeof(VM81));

    uint64_t mixer = seed;

    if (mode == SEED_PALINDROME)
        mixer ^= PALINDROME_SEED;

    for (int i = 0; i < GRID_SIZE; i++) {

        uint64_t x =
            (uint64_t)i * 2654435761ULL
            ^ mixer * 0x9E3779B97F4A7C15ULL
            ^ (mixer >> 13);

        vm->cells[i] =
            (uint8_t)(x % 72);
    }

    if (mode == SEED_LOSHU) {

        for (int k = 0; k < 9; k++) {

            vm->cells[72 + k] =
                wrap72(LOSHU[k] * 8);

            vm->cells[63 + k] =
                wrap72(
                    LOSHU[k] * 8
                    + (int)seed
                );
        }
    }

    for (int i = 0; i < HASH_LEN; i++) {

        uint64_t x =
            ((uint64_t)i * 11400714819323198485ULL)
            ^ (mixer + (uint64_t)i * 0xC2B2AE3D27D4EB4FULL);

        if (mode == SEED_PALINDROME)
            x ^= PALINDROME_SEED * (i + 1);

        vm->genesis_hash[i] =
            HASH72[x % 72];
    }

    vm->genesis_hash[72] = 0;

    vm->genomic[0] = 1;
    vm->genomic[1] = 3;
    vm->genomic[2] = 5;
    vm->genomic[3] = 7;
}

// ============================================================
// EXECUTION
// ============================================================

static void apply_instruction(
    VM81 *vm,
    Instruction *ins,
    uint32_t *witness,
    double *identity_residual_out,
    int *identity_has_data_out
) {

    uint8_t *A =
        &vm->cells[ins->a % GRID_SIZE];

    uint8_t *B =
        &vm->cells[ins->b % GRID_SIZE];

    uint8_t *C =
        &vm->cells[ins->c % GRID_SIZE];

    uint8_t energy = 0;

    int branched = 0;

    uint64_t new_pc = vm->pc + 1;

    switch (ins->op) {

        case OP_NOP:

            energy = ins->cg_id;
            break;

        case OP_ADD:

            *C = wrap72((int)*A + (int)*B);

            energy = *C;
            break;

        case OP_SUB:

            *C = wrap72((int)*A - (int)*B);

            energy = *C;
            break;

        case OP_ROT:

            *C = wrap72((int)*A + ins->phase);

            energy = *C;
            break;

        case OP_XOR:

            *C =
                wrap72(
                    (*A ^ *B)
                    + ins->phase
                    + ins->cg_id
                );

            energy = *C;
            break;

        case OP_AND:

            *C =
                wrap72(
                    (*A & *B)
                    + ins->phase
                );

            energy = *C;
            break;

        case OP_OR:

            *C =
                wrap72(
                    (*A | *B)
                    + ins->phase
                );

            energy = *C;
            break;

        case OP_LOAD:

            *C = wrap72(ins->a);

            energy = *C;
            break;

        case OP_STORE:

            *C = *A;

            energy = *C;
            break;

        case OP_MULXY:

            *C = wrap72((*A) * (*B));

            apply_xyzw_state(vm, *A, *B, 1);

            propagate_phase_transport(
                vm, *A, *C, ins->cg_id);

            propagate_phase_transport(
                vm, *B, *C, ins->cg_id);

            *witness |= W_NONCOMMUTATIVE;

            energy = *C;

            goto finalize;

        case OP_MULYX:

            *C = wrap72((*B) * (*A));

            apply_xyzw_state(vm, *A, *B, 0);

            propagate_phase_transport(
                vm, *B, *C, ins->cg_id);

            propagate_phase_transport(
                vm, *A, *C, ins->cg_id);

            *witness |= W_NONCOMMUTATIVE;

            energy = *C;

            goto finalize;

        case OP_QGU: {

            uint8_t q = *A;
            uint8_t cc = *B;

            uint8_t dd =
                vm->cells[
                    ins->cg_id % GRID_SIZE
                ];

            uint8_t delta = qgu_delta(q, cc, dd);

            *C = wrap72(*C + delta);

            energy = *C;

            *witness |= W_QGU_APPLIED;

            break;
        }

        case OP_GATE_APB: {

            int pass =
                check_gate_apb(
                    vm, ins->a, ins->b, ins->c);

            *witness |=
                pass ?
                W_GATE_APB_PASS :
                W_GATE_APB_FAIL;

            energy =
                wrap72(
                    ins->cg_id + (pass ? 0 : 36));

            break;
        }

        case OP_GATE_CLOSURE: {

            uint8_t Pc = ins->a;
            uint8_t pc = ins->b;
            uint8_t qc = ins->c;

            uint8_t nc =
                (uint8_t)(ins->cg_id & 0x0F);

            uint8_t xc =
                (uint8_t)((ins->cg_id >> 4) & 0x0F);

            uint8_t yc =
                (uint8_t)(ins->phase & 0x0F);

            int pass =
                check_gate_closure(
                    vm, Pc, pc, qc, nc, xc, yc);

            *witness |=
                pass ?
                W_GATE_CLOSURE_PASS :
                W_GATE_CLOSURE_FAIL;

            energy =
                wrap72(
                    ins->cg_id + (pass ? 0 : 48));

            break;
        }

        case OP_GATE_IDENTITY: {

            double res = INFINITY;

            int verdict =
                check_gate_identity(
                    vm,
                    ins->a,
                    ins->b,
                    ins->c,
                    &res
                );

            if (verdict == 1) {

                *witness |= W_GATE_IDENTITY_PASS;
                vm->ever_identity_pass = 1;
            }
            else if (verdict == 0) {

                *witness |= W_GATE_IDENTITY_FAIL;
            }
            else {

                *witness |= W_IDENTITY_DEGENERATE;
            }

            if (identity_residual_out)
                *identity_residual_out = res;

            if (identity_has_data_out)
                *identity_has_data_out = 1;

            energy =
                wrap72(
                    ins->cg_id + (verdict == 1 ? 0 : 24));

            break;
        }

        case OP_QBRANCH: {

            uint8_t pol = polarity_of(*A);

            if (ins->next[pol].enabled &&
                ins->next[pol].target < vm->program_len)
            {
                new_pc = ins->next[pol].target;
                branched = 1;
            }
            else {
                vm->halted = 1;
            }

            energy =
                wrap72(ins->cg_id + pol * 9);

            break;
        }

        case OP_CONSTRAIN:

            constraint_add(
                vm,
                ins->a,
                vm->cells[ins->b % GRID_SIZE],
                ins->c
            );

            *witness |= W_CONSTRAINT_FIRED;

            energy =
                wrap72(ins->cg_id + ins->c);

            break;

        case OP_RELAX:

            constraint_relax(vm, ins->a);

            energy =
                wrap72(ins->cg_id + 1);

            break;

        case OP_SWEEP81:

            sweep81(vm);

            *witness |= W_SWEEP;

            energy = ins->cg_id;

            break;

        case OP_CLOSE81:

            close81(vm);

            energy = ins->cg_id;

            break;

        case OP_BRANCH:

            if (ins->a < vm->program_len) {
                new_pc = ins->a;
                branched = 1;
            }
            else {
                vm->halted = 1;
            }

            energy = ins->cg_id;

            break;

        case OP_BZ:

            if (*A == 0) {

                if (ins->b < vm->program_len) {
                    new_pc = ins->b;
                    branched = 1;
                }
                else {
                    vm->halted = 1;
                }
            }

            energy = ins->cg_id;

            break;

        case OP_BNZ:

            if (*A != 0) {

                if (ins->b < vm->program_len) {
                    new_pc = ins->b;
                    branched = 1;
                }
                else {
                    vm->halted = 1;
                }
            }

            energy = ins->cg_id;

            break;

        case OP_HALT:

            vm->halted = 1;

            *witness |= W_HALT;

            return;

        default:

            vm->halted = 1;
            return;
    }

    if (!vm->halted) {

        propagate_phase_transport(
            vm,
            ins->phase,
            energy,
            ins->cg_id
        );
    }

finalize:

    constraint_compete(vm);

    if (branched && new_pc <= vm->pc)
        vm->sweep++;

    vm->pc = new_pc;
}

// ============================================================
// STEP
// ============================================================

static void vm81_step(VM81 *vm) {

    if (vm->halted)
        return;

    if (vm->pc >= vm->program_len) {

        // Implicit terminal: freeze ledger
        vm->last_receipt.witness |= W_HALT;
        vm->last_receipt.witness |= W_LEDGER_FROZEN;
        vm->last_receipt.ledger_advanced = 0;
        vm->last_receipt.step = vm->step;
        vm->halted = 1;
        return;
    }

    Instruction *ins = &vm->program[vm->pc];

    // ---- LEDGER-FREEZING OPS ----
    // These do not extend the receipt chain.
    // They only annotate the terminal frame with witness bits.

    if (!op_advances_ledger(ins->op)) {

        uint32_t w = 0;
        double id_res = INFINITY;
        int id_has = 0;

        apply_instruction(vm, ins, &w, &id_res, &id_has);

        vm->last_receipt.witness |= w;
        vm->last_receipt.witness |= W_LEDGER_FROZEN;

        vm->last_receipt.ledger_advanced = 0;
        vm->last_receipt.step = vm->step;
        vm->last_receipt.orbit_period = 0;

        if (id_has) {
            vm->last_receipt.identity_residual = id_res;
            vm->last_receipt.identity_has_data = 1;
        }

        vm->step++;
        return;
    }

    // ---- LEDGER-ADVANCING OPS ----

    char prev[73];
    char state[73];
    char rec[73];

    uint32_t witness = 0;
    double id_res = INFINITY;
    int id_has = 0;

    project_hash72(vm, prev);

    apply_instruction(vm, ins, &witness, &id_res, &id_has);

    project_hash72(vm, state);

    // Transport closure: state hash recurrence
    uint64_t orbit = 0;

    orbit = detect_orbit(vm, state, vm->step);

    if (orbit > 0) {
        witness |= W_ORBIT_DETECTED;
        witness |= W_CLOSE_TRANSPORT;
        vm->orbit_halted = 1;
        vm->ever_closed_transport = 1;
    }

    // Orientation closure: xyzw balance
    if (close_orientation(vm)) {
        witness |= W_CLOSE_ORIENTATION;
        vm->ever_closed_orientation = 1;
    }

    // Constraint closure: field dissipated below threshold
    if (close_constraint(vm)) {
        witness |= W_CLOSE_CONSTRAINT;
        vm->ever_closed_constraint = 1;
    }

    // Joint convergence
    uint32_t closure_mask =
        W_CLOSE_TRANSPORT
        | W_CLOSE_ORIENTATION
        | W_CLOSE_CONSTRAINT;

    if ((witness & closure_mask) == closure_mask) {
        witness |= W_CONVERGED;
        vm->converged = 1;
    }

    compose_receipt_hash(
        prev,
        ins->cg_id,
        witness,
        state,
        rec
    );

    strcpy(vm->last_receipt.prev_h72, prev);
    strcpy(vm->last_receipt.state_h72, state);
    strcpy(vm->last_receipt.receipt_h72, rec);

    vm->last_receipt.cg_id = ins->cg_id;
    vm->last_receipt.witness = witness;

    vm->last_receipt.step = vm->step;
    vm->last_receipt.orbit_period = orbit;
    vm->last_receipt.ledger_advanced = 1;

    if (id_has) {
        vm->last_receipt.identity_residual = id_res;
        vm->last_receipt.identity_has_data = 1;
    }
    else {
        vm->last_receipt.identity_has_data = 0;
    }

    vm->step++;
}

// ============================================================
// PRINT
// ============================================================

static void print_witness(uint32_t w) {

    printf("WITNESS:");

    if (!w) {
        printf(" -");
    }

    if (w & W_GATE_APB_PASS)       printf(" APB+");
    if (w & W_GATE_APB_FAIL)       printf(" APB-");
    if (w & W_GATE_CLOSURE_PASS)   printf(" CLOSURE+");
    if (w & W_GATE_CLOSURE_FAIL)   printf(" CLOSURE-");
    if (w & W_GATE_IDENTITY_PASS)  printf(" ID+");
    if (w & W_GATE_IDENTITY_FAIL)  printf(" ID-");
    if (w & W_IDENTITY_DEGENERATE) printf(" ID?");
    if (w & W_QGU_APPLIED)         printf(" QGU");
    if (w & W_NONCOMMUTATIVE)      printf(" NC");
    if (w & W_CONSTRAINT_FIRED)    printf(" K");
    if (w & W_ORBIT_DETECTED)      printf(" ORB");
    if (w & W_SWEEP)               printf(" SWEEP");
    if (w & W_CLOSE_TRANSPORT)     printf(" cl:T");
    if (w & W_CLOSE_ORIENTATION)   printf(" cl:O");
    if (w & W_CLOSE_CONSTRAINT)    printf(" cl:K");
    if (w & W_CONVERGED)           printf(" CONVERGED");
    if (w & W_HALT)                printf(" HALT");
    if (w & W_LEDGER_FROZEN)       printf(" [FROZEN]");

    printf("\n");
}

static void print_vm(VM81 *vm) {

    printf("\n");

    printf(
        "STEP %llu   SWEEP %llu   PC %llu   K=%llu   LEDGER=%s\n",

        (unsigned long long)vm->last_receipt.step,
        (unsigned long long)vm->sweep,
        (unsigned long long)vm->pc,
        (unsigned long long)vm->constraint_count,

        vm->last_receipt.ledger_advanced
            ? "ADVANCED"
            : "FROZEN"
    );

    printf("CG%u\n", vm->last_receipt.cg_id);

    printf("PREV:    %s\n", vm->last_receipt.prev_h72);
    printf("STATE:   %s\n", vm->last_receipt.state_h72);
    printf("RECEIPT: %s\n", vm->last_receipt.receipt_h72);

    print_witness(vm->last_receipt.witness);

    printf(
        "XYZW: [%u %u %u %u]  bal=%d\n",
        vm->xyzw[0],
        vm->xyzw[1],
        vm->xyzw[2],
        vm->xyzw[3],
        wrap72(
            (int)vm->xyzw[0]
            + (int)vm->xyzw[1]
            - (int)vm->xyzw[2]
            - (int)vm->xyzw[3]
        )
    );

    if (vm->last_receipt.identity_has_data) {
        printf(
            "IDENTITY residual (log-space): %.3e\n",
            vm->last_receipt.identity_residual
        );
    }

    if (vm->last_receipt.orbit_period > 0) {
        printf(
            "ORBIT PERIOD: %llu\n",
            (unsigned long long)
            vm->last_receipt.orbit_period
        );
    }

    if (vm->halted)
        printf("HALTED\n");
}

static void print_closure_summary(VM81 *vm) {

    printf("\n---- RUN CLOSURE SUMMARY ----\n");

    printf("Transport   closure ever reached : %s\n",
           vm->ever_closed_transport ? "YES" : "no");

    printf("Orientation closure ever reached : %s\n",
           vm->ever_closed_orientation ? "YES" : "no");

    printf("Constraint  closure ever reached : %s\n",
           vm->ever_closed_constraint ? "YES" : "no");

    printf("Identity gate ever passed        : %s\n",
           vm->ever_identity_pass ? "YES" : "no");

    printf("Joint CONVERGED at some step     : %s\n",
           vm->converged ? "YES" : "no");

    printf("Tensor layer count               : %llu\n",
           (unsigned long long)vm->tensor_count);

    printf("Genomic layer                    : [%u %u %u %u]\n",
           vm->genomic[0],
           vm->genomic[1],
           vm->genomic[2],
           vm->genomic[3]);

    printf("-----------------------------\n");
}

// ============================================================
// DEMO
// ============================================================

static void load_demo(VM81 *vm) {

    vm->program_len = 0;

    // Seed cells used by the identity gate:
    //   cell 10 = x, cell 11 = y, cell 12 = u
    vm->cells[10] = 36;
    vm->cells[11] = 54;
    vm->cells[12] = 40;

    vm->program[vm->program_len++] =
        (Instruction){ OP_ADD,          0,1,2,  21,3 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_MULXY,        2,1,3,  16,7 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_QGU,          3,1,4,   2,11 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_GATE_APB,     0,0,0,  17,0 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_GATE_IDENTITY, 10,11,12, 25,0 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_CONSTRAIN,    1,4,40, 19,0 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_SWEEP81,      0,0,0,  22,0 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_CLOSE81,      0,0,0,  23,0 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_LOAD,        50,0,10,  5,0 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_LOAD,        20,0,11,  5,0 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_LOAD,        60,0,12,  5,0 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_GATE_IDENTITY, 10,11,12, 26,0 };

    // Strong relax — should push the K=1 constraint below
    // CONSTRAINT_CLOSURE_THRESHOLD.
    vm->program[vm->program_len++] =
        (Instruction){ OP_RELAX,       40,0,0,  18,0 };

    vm->program[vm->program_len++] =
        (Instruction){ OP_HALT,         0,0,0,   0,0 };
}

// ============================================================
// OPTIONS
// ============================================================

typedef struct {

    int steps;
    uint64_t seed;
    SeedMode mode;

    int trace;
    int halt_on_orbit;
    int verify;

} Options;

static void run_vm(VM81 *vm, Options *opt) {

    for (int i = 0;
         i < opt->steps && i < MAX_STEPS;
         i++)
    {
        vm81_step(vm);

        if (opt->trace)
            print_vm(vm);

        if (vm->halted)
            break;

        if (opt->halt_on_orbit && vm->orbit_halted)
            break;
    }
}

// ============================================================
// MAIN
// ============================================================

int main(int argc, char **argv) {

    init_hash72();

    Options opt;
    opt.steps = 128;
    opt.seed = 0;
    opt.mode = SEED_LOSHU;
    opt.trace = 1;
    opt.halt_on_orbit = 0;
    opt.verify = 0;

    for (int i = 1; i < argc; i++) {

        if (!strcmp(argv[i], "--steps") && i + 1 < argc) {
            opt.steps = atoi(argv[++i]);
        }
        else if (!strcmp(argv[i], "--seed") && i + 1 < argc) {
            opt.seed = strtoull(argv[++i], NULL, 10);
        }
        else if (!strcmp(argv[i], "--palindrome")) {
            opt.mode = SEED_PALINDROME;
        }
        else if (!strcmp(argv[i], "--loshu")) {
            opt.mode = SEED_LOSHU;
        }
        else if (!strcmp(argv[i], "--halt-on-orbit")) {
            opt.halt_on_orbit = 1;
        }
        else if (!strcmp(argv[i], "--verify")) {
            opt.verify = 1;
        }
        else if (!strcmp(argv[i], "--no-trace")) {
            opt.trace = 0;
        }
        else if (!strcmp(argv[i], "--trace")) {
            opt.trace = 1;
        }
    }

    VM81 vm;
    vm81_init(&vm, opt.seed, opt.mode);

    load_demo(&vm);

    run_vm(&vm, &opt);

    // Layered extension pass after locked runtime execution.
    // This does not rewrite receipt history.
    hhs_tensor_seed_from_xyzw(&vm);
    hhs_genomic_map(&vm);
    hhs_manifold_step(&vm, vm.xyzw[0]);

    if (opt.verify) {
        double mrec = hhs_calc_m_reciprocal(vm.xyzw[0]);
        printf("\nVERIFY m-reciprocal probe: %.12f\n", mrec);

        hhs_apply_ouroboros_closure(&vm);
        printf(
            "VERIFY ouroboros XYZW: [%u %u %u %u]\n",
            vm.xyzw[0],
            vm.xyzw[1],
            vm.xyzw[2],
            vm.xyzw[3]
        );
    }

    print_closure_summary(&vm);

    printf("\nFINAL HASH72:\n%s\n",
           vm.last_receipt.state_h72);

    return 0;
}// ============================================================================
// HHS PYTHON->VM BRIDGE LAYER
// Append below the canonical runtime freeze.
// This layer is additive-only and does not mutate the frozen substrate.
// ============================================================================

// ============================================================
// IR OPCODES
// ============================================================

typedef enum {

    IR_NOP = 0,

    IR_CONST,
    IR_MOVE,

    IR_ADD,
    IR_SUB,
    IR_MUL,
    IR_DIV,

    IR_MOD,

    IR_COMPARE_EQ,
    IR_COMPARE_NEQ,
    IR_COMPARE_LT,
    IR_COMPARE_GT,

    IR_BRANCH,
    IR_JUMP,

    IR_CALL,
    IR_RETURN,

    IR_CONSTRAIN,
    IR_QGU,

    IR_HASH72_PROJECT,

    IR_VM_NATIVE

} HHS_IROp;

// ============================================================
// IR NODE
// ============================================================

typedef struct {

    HHS_IROp op;

    uint32_t dst;

    uint32_t srcA;
    uint32_t srcB;

    uint64_t imm;

    uint32_t flags;

    uint32_t phase;
    uint32_t closure_class;

} HHS_IR_Node;

// ============================================================
// IR BLOCK
// ============================================================

typedef struct {

    HHS_IR_Node *nodes;

    uint32_t node_count;

    uint32_t entry_phase;

    uint32_t parent_block;

} HHS_IR_Block;

// ============================================================
// SYMBOL BINDING
// ============================================================

typedef struct {

    char symbol[64];

    uint32_t reg;

    uint32_t ir_block;

    uint32_t transport_phase;

    uint32_t witness_mask;

} HHS_SymbolBinding;

// ============================================================
// VM FRAME
// ============================================================

typedef struct {

    uint64_t registers[256];

    uint64_t stack[1024];

    uint32_t sp;

    uint32_t current_block;
    uint32_t current_node;

    uint64_t receipt_parent;

    uint8_t closure_state;

    uint8_t halted;

    uint32_t last_compare;

} HHS_VM_Frame;

// ============================================================
// IR PROGRAM
// ============================================================

typedef struct {

    HHS_IR_Block *blocks;

    uint32_t block_count;

    HHS_SymbolBinding symbols[256];

    uint32_t symbol_count;

} HHS_IR_Program;

// ============================================================
// FRAME INIT
// ============================================================

static void hhs_frame_init(HHS_VM_Frame *f) {

    memset(f, 0, sizeof(HHS_VM_Frame));

    f->sp = 0;
    f->halted = 0;
    f->current_block = 0;
    f->current_node = 0;
}

// ============================================================
// SYMBOL TABLE
// ============================================================

static int hhs_symbol_find(
    HHS_IR_Program *p,
    const char *name
) {
    for (uint32_t i = 0; i < p->symbol_count; i++) {
        if (!strcmp(p->symbols[i].symbol, name))
            return (int)i;
    }

    return -1;
}

static uint32_t hhs_symbol_register(
    HHS_IR_Program *p,
    const char *name
) {
    int idx = hhs_symbol_find(p, name);

    if (idx >= 0)
        return p->symbols[idx].reg;

    uint32_t n = p->symbol_count++;

    strncpy(
        p->symbols[n].symbol,
        name,
        sizeof(p->symbols[n].symbol) - 1
    );

    p->symbols[n].reg = n;

    p->symbols[n].ir_block = 0;
    p->symbols[n].transport_phase = 0;
    p->symbols[n].witness_mask = 0;

    return n;
}

// ============================================================
// HASH72 PROJECTION HELPERS
// ============================================================

static void hhs_ir_project_hash72(
    VM81 *vm,
    char out[73]
) {
    project_hash72(vm, out);
}

// ============================================================
// VM NATIVE EXECUTION
// ============================================================

static void hhs_vm_native_add(
    VM81 *vm,
    uint64_t a,
    uint64_t b,
    uint64_t *out
) {

    Instruction ins = {
        OP_ADD,
        (uint8_t)(a % GRID_SIZE),
        (uint8_t)(b % GRID_SIZE),
        0,
        31,
        7
    };

    uint32_t witness = 0;

    double id_res = 0.0;
    int id_has = 0;

    apply_instruction(
        vm,
        &ins,
        &witness,
        &id_res,
        &id_has
    );

    *out = vm->cells[0];
}

static void hhs_vm_native_mul(
    VM81 *vm,
    uint64_t a,
    uint64_t b,
    uint64_t *out
) {

    Instruction ins = {
        OP_MULXY,
        (uint8_t)(a % GRID_SIZE),
        (uint8_t)(b % GRID_SIZE),
        1,
        32,
        9
    };

    uint32_t witness = 0;

    double id_res = 0.0;
    int id_has = 0;

    apply_instruction(
        vm,
        &ins,
        &witness,
        &id_res,
        &id_has
    );

    *out = vm->cells[1];
}

// ============================================================
// IR EXECUTION
// ============================================================

static int hhs_execute_ir_node(
    VM81 *vm,
    HHS_VM_Frame *frame,
    HHS_IR_Node *node
) {

    uint64_t A = frame->registers[node->srcA];
    uint64_t B = frame->registers[node->srcB];

    switch (node->op) {

        case IR_NOP:
            break;

        case IR_CONST:

            frame->registers[node->dst] = node->imm;
            break;

        case IR_MOVE:

            frame->registers[node->dst] = A;
            break;

        case IR_ADD: {

            uint64_t out = 0;

            hhs_vm_native_add(
                vm,
                A,
                B,
                &out
            );

            frame->registers[node->dst] = out;

            break;
        }

        case IR_SUB:

            frame->registers[node->dst] =
                (uint64_t)((int64_t)A - (int64_t)B);

            break;

        case IR_MUL: {

            uint64_t out = 0;

            hhs_vm_native_mul(
                vm,
                A,
                B,
                &out
            );

            frame->registers[node->dst] = out;

            break;
        }

        case IR_DIV:

            if (B == 0)
                return 0;

            frame->registers[node->dst] = A / B;

            break;

        case IR_MOD:

            if (B == 0)
                return 0;

            frame->registers[node->dst] = A % B;

            break;

        case IR_COMPARE_EQ:

            frame->last_compare = (A == B);
            break;

        case IR_COMPARE_NEQ:

            frame->last_compare = (A != B);
            break;

        case IR_COMPARE_LT:

            frame->last_compare = (A < B);
            break;

        case IR_COMPARE_GT:

            frame->last_compare = (A > B);
            break;

        case IR_BRANCH:

            if (frame->last_compare) {
                frame->current_block = (uint32_t)node->imm;
                frame->current_node = 0;
            }

            break;

        case IR_JUMP:

            frame->current_block = (uint32_t)node->imm;
            frame->current_node = 0;

            break;

        case IR_CALL:

            if (frame->sp >= 1023)
                return 0;

            frame->stack[frame->sp++] =
                frame->current_block;

            frame->stack[frame->sp++] =
                frame->current_node;

            frame->current_block =
                (uint32_t)node->imm;

            frame->current_node = 0;

            break;

        case IR_RETURN:

            if (frame->sp < 2) {
                frame->halted = 1;
                break;
            }

            frame->current_node =
                (uint32_t)frame->stack[--frame->sp];

            frame->current_block =
                (uint32_t)frame->stack[--frame->sp];

            break;

        case IR_CONSTRAIN: {

            constraint_add(
                vm,
                (uint8_t)A,
                (uint8_t)B,
                (uint8_t)(node->imm & 0xFF)
            );

            break;
        }

        case IR_QGU: {

            uint8_t q =
                (uint8_t)(A % 72);

            uint8_t c =
                (uint8_t)(B % 72);

            uint8_t d =
                (uint8_t)(node->imm % 72);

            uint8_t delta =
                qgu_delta(q, c, d);

            frame->registers[node->dst] = delta;

            break;
        }

        case IR_HASH72_PROJECT: {

            char hash[73];

            hhs_ir_project_hash72(vm, hash);

            printf(
                "[IR HASH72] %s\n",
                hash
            );

            break;
        }

        case IR_VM_NATIVE:

            break;

        default:

            return 0;
    }

    return 1;
}

// ============================================================
// BLOCK EXECUTION
// ============================================================

static int hhs_execute_ir_block(
    VM81 *vm,
    HHS_IR_Program *prog,
    HHS_VM_Frame *frame
) {

    if (frame->current_block >= prog->block_count)
        return 0;

    HHS_IR_Block *blk =
        &prog->blocks[frame->current_block];

    while (
        frame->current_node < blk->node_count
    ) {

        HHS_IR_Node *node =
            &blk->nodes[frame->current_node];

        if (!hhs_execute_ir_node(
                vm,
                frame,
                node))
        {
            return 0;
        }

        frame->current_node++;

        if (frame->halted)
            return 1;
    }

    return 1;
}

// ============================================================
// PROGRAM EXECUTION
// ============================================================

static int hhs_execute_ir(
    VM81 *vm,
    HHS_IR_Program *prog,
    HHS_VM_Frame *frame
) {

    while (!frame->halted) {

        if (!hhs_execute_ir_block(
                vm,
                prog,
                frame))
        {
            return 0;
        }

        if (
            frame->current_block + 1
            >= prog->block_count
        ) {
            frame->halted = 1;
        }
        else {

            frame->current_block++;
            frame->current_node = 0;
        }
    }

    return 1;
}

// ============================================================
// DEMO IR PROGRAM
// ============================================================

static HHS_IR_Node DEMO_NODES[] = {

    { IR_CONST, 0,0,0, 5, 0,0,0 },
    { IR_CONST, 1,0,0, 7, 0,0,0 },

    { IR_ADD,   2,0,1, 0, 0,0,0 },

    { IR_MUL,   3,2,1, 0, 0,0,0 },

    { IR_QGU,   4,3,1, 9, 0,0,0 },

    { IR_HASH72_PROJECT, 0,0,0,0,0,0,0 }
};

static HHS_IR_Block DEMO_BLOCKS[] = {
    {
        DEMO_NODES,
        sizeof(DEMO_NODES)
            / sizeof(HHS_IR_Node),
        0,
        0
    }
};

static HHS_IR_Program DEMO_PROGRAM = {
    DEMO_BLOCKS,
    1,
    {0},
    0
};

// ============================================================
// BRIDGE ENTRYPOINT
// ============================================================

static void hhs_run_bridge_demo(VM81 *vm) {

    printf(
        "\n==== HHS PYTHON->VM BRIDGE DEMO ====\n"
    );

    HHS_VM_Frame frame;

    hhs_frame_init(&frame);

    hhs_execute_ir(
        vm,
        &DEMO_PROGRAM,
        &frame
    );

    printf(
        "R0=%llu\n",
        (unsigned long long)
        frame.registers[0]
    );

    printf(
        "R1=%llu\n",
        (unsigned long long)
        frame.registers[1]
    );

    printf(
        "R2=%llu\n",
        (unsigned long long)
        frame.registers[2]
    );

    printf(
        "R3=%llu\n",
        (unsigned long long)
        frame.registers[3]
    );

    printf(
        "R4=%llu\n",
        (unsigned long long)
        frame.registers[4]
    );

    printf(
        "===================================\n"
    );
}