// hhs_runtime/HARMONICODE_VM_RUNTIME.c
// HARMONICODE / HHS VM81 exact kernel runtime
//
// Repair-forward kernel alignment:
// - authoritative arithmetic is integer / exact rational / modular only
// - VM81 frame is 81 x 64-bit = 5184-bit x86_64-aligned canonical memory
// - native phase basis is ordered (x,y,z,w,xy,yx,zw,wz)
// - ordered products preserve noncommutative orientation over u^72
// - Hash72 is exactly 72 symbols at exactly 72 positions
// - each Hash72 token occurrence has a 72 x 72 = 5184 positional coordinate
// - the complete representable Hash72 word space is the base-72 vector space 72^72
// - no host transcendental or approximate numeric arithmetic participates in authority
//
// Standalone build:
//   gcc -O2 -std=c11 -Wall -Wextra hhs_runtime/HARMONICODE_VM_RUNTIME.c -o hhs_vm81

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <limits.h>

// ============================================================
// CONSTANTS
// ============================================================

#define GRID_SIZE                     81
#define VM81_WORD_BITS                64
#define VM81_FRAME_BITS               (GRID_SIZE * VM81_WORD_BITS)
#define VM81_FRAME_BYTES              (VM81_FRAME_BITS / 8)
#define HASH_LEN                      72
#define HASH72_COORDS                 (HASH_LEN * HASH_LEN)
#define HASH72_STATE_EXPONENT         72
#define PHASE_BASIS_COUNT             8
#define PHASE_PAIR_COUNT              64
#define MAX_PROGRAM                   256
#define MAX_STEPS                     (1 << 20)
#define MAX_SEEN                      8192
#define MAX_CONSTRAINTS               64
#define CONSTRAINT_CLOSURE_THRESHOLD  4
#define MAX_TENSORS                   512
#define MANIFOLD_DIM                  9

_Static_assert(VM81_FRAME_BITS == 5184, "VM81 frame must be 5184 bits");
_Static_assert(VM81_FRAME_BYTES == 648, "VM81 frame must be 648 bytes");
_Static_assert(HASH72_COORDS == 5184, "Hash72 positional plane must be 5184 coordinates");
_Static_assert(PHASE_BASIS_COUNT * PHASE_BASIS_COUNT == PHASE_PAIR_COUNT,
               "phase basis must expose 8x8 ordered products");

// ============================================================
// HASH72
// ============================================================

static const char HASH72[HASH_LEN + 1] =
"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";

static int16_t HASH72_IDX[256];

// A Hash72 word is a 72-digit base-72 vector.  This representation spans
// the full formal word space 72^72 without attempting to collapse it into
// a machine-sized scalar rank.
typedef struct {
    uint8_t digit[HASH_LEN];
} Hash72Vector;

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
// EXACT RATIONAL / EXACT COMPLEX-RATIONAL SUPPORT
// ============================================================

typedef struct {
    int64_t num;
    uint64_t den;
} HHSRational;

typedef struct {
    int64_t real_num;
    int64_t imag_num;
    uint64_t den;
    uint8_t phase;
    uint8_t orientation;
} HHSTensor;

static uint64_t abs_i64_u64(int64_t v) {
    if (v >= 0)
        return (uint64_t)v;
    return (uint64_t)(-(v + 1)) + 1ULL;
}

static uint64_t gcd_u64(uint64_t a, uint64_t b) {
    while (b != 0) {
        uint64_t t = a % b;
        a = b;
        b = t;
    }
    return a == 0 ? 1 : a;
}

static HHSRational rational_make(int64_t num, uint64_t den) {
    HHSRational r;
    if (den == 0) {
        r.num = 0;
        r.den = 0;
        return r;
    }
    uint64_t g = gcd_u64(abs_i64_u64(num), den);
    r.num = num / (int64_t)g;
    r.den = den / g;
    return r;
}

// ============================================================
// U^72 / ORDERED OCTONION-DNA PHASE BASIS
// Inherited basis candidate from hhs_octonion_digital_dna_u72_table_v1.py
// ============================================================

typedef enum {
    HHS_PHASE_X = 0,
    HHS_PHASE_Y,
    HHS_PHASE_Z,
    HHS_PHASE_W,
    HHS_PHASE_XY,
    HHS_PHASE_YX,
    HHS_PHASE_ZW,
    HHS_PHASE_WZ
} HHSPhaseBasis;

static const uint8_t HHS_PHASE_ANCHOR[PHASE_BASIS_COUNT] = {
    18, 54, 18, 54, 0, 36, 0, 36
};

typedef struct {
    uint8_t phase;
    uint8_t raw_additive_phase;
    uint8_t orientation; /* 0 composed, 1 direct, 2 reversed */
    uint8_t closure;
    uint8_t left;
    uint8_t right;
} HHSOrderedPhaseProduct;

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

typedef struct {
    uint8_t enabled;
    uint8_t target;
} Edge81;

typedef struct {
    Opcode op;
    uint8_t a;
    uint8_t b;
    uint8_t c;
    uint8_t cg_id;
    uint8_t phase;
    Edge81 next[4];
} Instruction;

static Instruction instruction_make(Opcode op, uint8_t a, uint8_t b,
                                    uint8_t c, uint8_t cg_id, uint8_t phase) {
    Instruction ins;
    memset(&ins, 0, sizeof(ins));
    ins.op = op;
    ins.a = a;
    ins.b = b;
    ins.c = c;
    ins.cg_id = cg_id;
    ins.phase = phase;
    return ins;
}

// ============================================================
// WITNESS FLAGS
// ============================================================

#define W_GATE_APB_PASS        0x00001u
#define W_GATE_APB_FAIL        0x00002u
#define W_GATE_CLOSURE_PASS    0x00004u
#define W_GATE_CLOSURE_FAIL    0x00008u
#define W_QGU_APPLIED          0x00010u
#define W_NONCOMMUTATIVE       0x00020u
#define W_CONSTRAINT_FIRED     0x00040u
#define W_ORBIT_DETECTED       0x00080u
#define W_HALT                 0x00100u
#define W_SWEEP                0x00200u
#define W_CLOSE_TRANSPORT      0x00400u
#define W_CLOSE_ORIENTATION    0x00800u
#define W_CLOSE_CONSTRAINT     0x01000u
#define W_CONVERGED            0x02000u
#define W_LEDGER_FROZEN        0x04000u
#define W_GATE_IDENTITY_PASS   0x08000u
#define W_GATE_IDENTITY_FAIL   0x10000u
#define W_IDENTITY_DEGENERATE  0x20000u
#define W_PHASE_TABLE_LOCKED   0x40000u
#define W_HASH72_POSITIONAL    0x80000u

// ============================================================
// RECEIPT / CONSTRAINT / STATE
// ============================================================

typedef struct {
    char prev_h72[HASH_LEN + 1];
    char state_h72[HASH_LEN + 1];
    char receipt_h72[HASH_LEN + 1];
    uint8_t cg_id;
    uint32_t witness;
    uint64_t step;
    uint64_t orbit_period;
    int ledger_advanced;
    uint64_t identity_exact_witness;
    int identity_has_data;
} VMReceipt;

typedef struct {
    uint8_t type;
    uint8_t phase;
    uint8_t strength;
    uint8_t active;
    uint64_t lineage;
} Constraint72;

typedef struct {
    char hash[HASH_LEN + 1];
    uint64_t step;
} SeenState;

typedef struct {
    // Canonical raw carrier: 81 x 64-bit x86_64-aligned words = 5184 bits.
    uint64_t cells[GRID_SIZE];

    uint64_t step;
    uint64_t sweep;
    uint64_t pc;
    int halted;
    int orbit_halted;
    int converged;
    int ever_closed_transport;
    int ever_closed_orientation;
    int ever_closed_constraint;
    int ever_identity_pass;

    Instruction program[MAX_PROGRAM];
    uint64_t program_len;

    char genesis_hash[HASH_LEN + 1];
    VMReceipt last_receipt;
    SeenState seen[MAX_SEEN];
    uint64_t seen_count;
    Constraint72 constraints[MAX_CONSTRAINTS];
    uint64_t constraint_count;

    // Native digital-DNA base state and full ordered 8-basis phase surface.
    uint8_t xyzw[4];
    uint8_t phase8[PHASE_BASIS_COUNT];

    HHSTensor tensors[MAX_TENSORS];
    uint64_t tensor_count;
    uint8_t manifold[MANIFOLD_DIM][MANIFOLD_DIM];
    uint8_t genomic[4];
} VM81;

_Static_assert(sizeof(((VM81 *)0)->cells) == VM81_FRAME_BYTES,
               "VM81 raw cell carrier must serialize to exactly 648 bytes");

typedef enum {
    SEED_PLAIN,
    SEED_LOSHU,
    SEED_PALINDROME
} SeedMode;

// ============================================================
// MODULAR UTILITIES
// ============================================================

static inline uint8_t wrap72_i64(int64_t v) {
    int64_t r = v % 72;
    if (r < 0)
        r += 72;
    return (uint8_t)r;
}

static inline uint8_t wrap72_u64(uint64_t v) {
    return (uint8_t)(v % 72ULL);
}

static inline uint16_t wrap5184_i64(int64_t v) {
    int64_t r = v % 5184;
    if (r < 0)
        r += 5184;
    return (uint16_t)r;
}

static inline uint8_t reciprocal_phase(uint8_t p) {
    return (uint8_t)((p + 36u) % 72u);
}

static inline uint8_t polarity_of(uint8_t p) {
    return (uint8_t)((p / 18u) & 3u);
}

static inline uint16_t hash72_coord(uint8_t position, uint8_t symbol_index) {
    return (uint16_t)(((uint16_t)(position % 72u) * 72u) + (symbol_index % 72u));
}

static inline void hash72_coord_decode(uint16_t coord, uint8_t *position, uint8_t *symbol_index) {
    uint16_t c = wrap5184_i64((int64_t)coord);
    if (position)
        *position = (uint8_t)(c / 72u);
    if (symbol_index)
        *symbol_index = (uint8_t)(c % 72u);
}

static int hash72_index_checked(char ch) {
    return HASH72_IDX[(uint8_t)ch];
}

static uint8_t fold_word72(uint64_t word) {
    uint32_t acc = 0;
    for (uint8_t i = 0; i < 8; i++) {
        uint8_t b = (uint8_t)((word >> (8u * i)) & 0xFFu);
        acc += (uint32_t)b * (uint32_t)(i + 1u);
    }
    return (uint8_t)(acc % 72u);
}

static void vm81_serialize_frame_le(const VM81 *vm, uint8_t out[VM81_FRAME_BYTES]) {
    for (uint16_t c = 0; c < GRID_SIZE; c++) {
        uint64_t w = vm->cells[c];
        for (uint8_t b = 0; b < 8; b++)
            out[(size_t)c * 8u + b] = (uint8_t)((w >> (8u * b)) & 0xFFu);
    }
}

static void vm81_deserialize_frame_le(VM81 *vm, const uint8_t in[VM81_FRAME_BYTES]) {
    for (uint16_t c = 0; c < GRID_SIZE; c++) {
        uint64_t w = 0;
        for (uint8_t b = 0; b < 8; b++)
            w |= ((uint64_t)in[(size_t)c * 8u + b]) << (8u * b);
        vm->cells[c] = w;
    }
}

// ============================================================
// PHASE-GEAR TABLE
// ============================================================

static int phase_pair_override(uint8_t l, uint8_t r, uint8_t *phase_out) {
    struct PairPhase { uint8_t l, r, p; };
    static const struct PairPhase table[] = {
        {HHS_PHASE_X,  HHS_PHASE_Y,  0},
        {HHS_PHASE_Y,  HHS_PHASE_X, 36},
        {HHS_PHASE_Z,  HHS_PHASE_W,  0},
        {HHS_PHASE_W,  HHS_PHASE_Z, 36},
        {HHS_PHASE_XY, HHS_PHASE_YX,36},
        {HHS_PHASE_YX, HHS_PHASE_XY,36},
        {HHS_PHASE_ZW, HHS_PHASE_WZ,36},
        {HHS_PHASE_WZ, HHS_PHASE_ZW,36},
        {HHS_PHASE_XY, HHS_PHASE_ZW, 0},
        {HHS_PHASE_ZW, HHS_PHASE_XY, 0},
        {HHS_PHASE_YX, HHS_PHASE_WZ, 0},
        {HHS_PHASE_WZ, HHS_PHASE_YX, 0}
    };
    for (size_t i = 0; i < sizeof(table) / sizeof(table[0]); i++) {
        if (table[i].l == l && table[i].r == r) {
            if (phase_out)
                *phase_out = table[i].p;
            return 1;
        }
    }
    return 0;
}

static HHSOrderedPhaseProduct hhs_phase_product_anchor(uint8_t left, uint8_t right) {
    HHSOrderedPhaseProduct w;
    memset(&w, 0, sizeof(w));
    w.left = (uint8_t)(left % PHASE_BASIS_COUNT);
    w.right = (uint8_t)(right % PHASE_BASIS_COUNT);
    w.raw_additive_phase = wrap72_i64((int64_t)HHS_PHASE_ANCHOR[w.left] +
                                      (int64_t)HHS_PHASE_ANCHOR[w.right]);
    w.phase = w.raw_additive_phase;
    (void)phase_pair_override(w.left, w.right, &w.phase);
    if ((w.left == HHS_PHASE_X && w.right == HHS_PHASE_Y) ||
        (w.left == HHS_PHASE_Z && w.right == HHS_PHASE_W))
        w.orientation = 1;
    else if ((w.left == HHS_PHASE_Y && w.right == HHS_PHASE_X) ||
             (w.left == HHS_PHASE_W && w.right == HHS_PHASE_Z))
        w.orientation = 2;
    else
        w.orientation = 0;
    w.closure = (uint8_t)(w.phase == 0 || w.phase == 36);
    return w;
}

static uint8_t hhs_dynamic_pair_phase(uint8_t left_basis, uint8_t right_basis,
                                      uint8_t left_phase, uint8_t right_phase) {
    uint8_t raw = wrap72_i64((int64_t)left_phase + (int64_t)right_phase);
    if ((left_basis == HHS_PHASE_Y && right_basis == HHS_PHASE_X) ||
        (left_basis == HHS_PHASE_W && right_basis == HHS_PHASE_Z))
        return reciprocal_phase(raw);
    return raw;
}

static void refresh_phase8(VM81 *vm) {
    vm->phase8[HHS_PHASE_X] = vm->xyzw[0];
    vm->phase8[HHS_PHASE_Y] = vm->xyzw[1];
    vm->phase8[HHS_PHASE_Z] = vm->xyzw[2];
    vm->phase8[HHS_PHASE_W] = vm->xyzw[3];
    vm->phase8[HHS_PHASE_XY] = hhs_dynamic_pair_phase(
        HHS_PHASE_X, HHS_PHASE_Y, vm->xyzw[0], vm->xyzw[1]);
    vm->phase8[HHS_PHASE_YX] = hhs_dynamic_pair_phase(
        HHS_PHASE_Y, HHS_PHASE_X, vm->xyzw[1], vm->xyzw[0]);
    vm->phase8[HHS_PHASE_ZW] = hhs_dynamic_pair_phase(
        HHS_PHASE_Z, HHS_PHASE_W, vm->xyzw[2], vm->xyzw[3]);
    vm->phase8[HHS_PHASE_WZ] = hhs_dynamic_pair_phase(
        HHS_PHASE_W, HHS_PHASE_Z, vm->xyzw[3], vm->xyzw[2]);
}

static uint16_t vm5184_address(uint8_t cell, uint8_t left_basis, uint8_t right_basis) {
    uint16_t op = (uint16_t)((left_basis % 8u) * 8u + (right_basis % 8u));
    return (uint16_t)((cell % 81u) * 64u + op);
}

static void vm5184_decode(uint16_t address, uint8_t *cell, uint8_t *left_basis, uint8_t *right_basis) {
    uint16_t s = wrap5184_i64((int64_t)address);
    uint8_t op = (uint8_t)(s % 64u);
    if (cell)
        *cell = (uint8_t)(s / 64u);
    if (left_basis)
        *left_basis = (uint8_t)(op / 8u);
    if (right_basis)
        *right_basis = (uint8_t)(op % 8u);
}

static int hhs_phase_table_selfcheck(void) {
    if (hhs_phase_product_anchor(HHS_PHASE_X, HHS_PHASE_Y).phase != 0)
        return 0;
    if (hhs_phase_product_anchor(HHS_PHASE_Y, HHS_PHASE_X).phase != 36)
        return 0;
    if (hhs_phase_product_anchor(HHS_PHASE_Z, HHS_PHASE_W).phase != 0)
        return 0;
    if (hhs_phase_product_anchor(HHS_PHASE_W, HHS_PHASE_Z).phase != 36)
        return 0;
    for (uint8_t l = 0; l < 8; l++) {
        for (uint8_t r = 0; r < 8; r++) {
            HHSOrderedPhaseProduct p = hhs_phase_product_anchor(l, r);
            if (p.phase >= 72 || p.raw_additive_phase >= 72)
                return 0;
            uint16_t a = vm5184_address(80, l, r);
            uint8_t c2, l2, r2;
            vm5184_decode(a, &c2, &l2, &r2);
            if (c2 != 80 || l2 != l || r2 != r)
                return 0;
        }
    }
    return 1;
}

// ============================================================
// INIT
// ============================================================

static int init_hash72(void) {
    if (strlen(HASH72) != HASH_LEN)
        return 0;
    memset(HASH72_IDX, 0xFF, sizeof(HASH72_IDX));
    for (int i = 0; i < HASH_LEN; i++) {
        uint8_t ch = (uint8_t)HASH72[i];
        if (HASH72_IDX[ch] >= 0)
            return 0;
        HASH72_IDX[ch] = (int16_t)i;
    }
    for (int k = 0; k < 9; k++)
        LOSHU_SLOTS[k] = (uint8_t)(LOSHU[k] * 8u - 1u);
    return hhs_phase_table_selfcheck();
}

static int op_advances_ledger(Opcode op) {
    return op != OP_HALT;
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
        if (dist < 6)
            acc += (uint32_t)k->strength * (uint32_t)(6 - dist);
    }
    return (uint8_t)(acc % 72u);
}

static void constraint_add(VM81 *vm, uint8_t type, uint8_t phase, uint8_t strength) {
    if (vm->constraint_count < MAX_CONSTRAINTS) {
        Constraint72 *k = &vm->constraints[vm->constraint_count++];
        k->type = type;
        k->phase = (uint8_t)(phase % 72u);
        k->strength = strength;
        k->active = 1;
        k->lineage = vm->step;
        return;
    }
    uint64_t weakest = 0;
    for (uint64_t i = 1; i < vm->constraint_count; i++) {
        if (vm->constraints[i].strength < vm->constraints[weakest].strength)
            weakest = i;
    }
    Constraint72 *k = &vm->constraints[weakest];
    k->type = type;
    k->phase = (uint8_t)(phase % 72u);
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
        } else {
            k->strength = (uint8_t)(k->strength - amount);
        }
    }
}

static void constraint_compete(VM81 *vm) {
    for (uint64_t i = 0; i < vm->constraint_count; i++) {
        Constraint72 *a = &vm->constraints[i];
        if (!a->active || a->strength == 0)
            continue;
        for (uint64_t j = i + 1; j < vm->constraint_count; j++) {
            Constraint72 *b = &vm->constraints[j];
            if (!b->active || b->strength == 0)
                continue;
            if (reciprocal_phase(a->phase) == b->phase) {
                uint8_t m = a->strength < b->strength ? a->strength : b->strength;
                a->strength = (uint8_t)(a->strength - m);
                b->strength = (uint8_t)(b->strength - m);
                if (a->strength == 0) a->active = 0;
                if (b->strength == 0) b->active = 0;
            }
        }
    }
}

// ============================================================
// PHASE TRANSPORT / DIGITAL DNA
// ============================================================

static void propagate_phase_transport(VM81 *vm, uint8_t origin, uint8_t energy, uint8_t cg) {
    origin = (uint8_t)(origin % 72u);
    uint8_t origin_phase = fold_word72(vm->cells[origin]);
    vm->cells[origin] = wrap72_i64((int64_t)origin_phase + energy + cg +
                                   constraint_bias_at(vm, origin));
    uint8_t r0 = reciprocal_phase(origin);
    vm->cells[r0] = reciprocal_phase(fold_word72(vm->cells[origin]));

    for (int radius = 1; radius < 6; radius++) {
        uint8_t l = wrap72_i64((int64_t)origin - radius);
        uint8_t r = wrap72_i64((int64_t)origin + radius);
        vm->cells[l] = wrap72_i64((int64_t)fold_word72(vm->cells[l]) + energy + cg + radius +
                                  constraint_bias_at(vm, l));
        vm->cells[r] = wrap72_i64((int64_t)fold_word72(vm->cells[r]) + energy + cg + radius + 1 +
                                  constraint_bias_at(vm, r));
        vm->cells[reciprocal_phase(l)] = reciprocal_phase(fold_word72(vm->cells[l]));
        vm->cells[reciprocal_phase(r)] = reciprocal_phase(fold_word72(vm->cells[r]));
    }

    for (int i = 0; i < 72; i++) {
        uint8_t delta = wrap72_i64((int64_t)i - origin);
        uint8_t h = (uint8_t)((energy + cg + delta) % 9u);
        vm->cells[i] = wrap72_i64((int64_t)fold_word72(vm->cells[i]) + h);
    }
    for (int i = 72; i < GRID_SIZE; i++) {
        uint8_t t = (uint8_t)((energy + cg + i + origin) % 72u);
        vm->cells[i] = wrap72_i64((int64_t)fold_word72(vm->cells[i]) + (t % 5u));
    }
}

static void apply_xyzw_state(VM81 *vm, uint8_t a, uint8_t b, int xy_order) {
    if (xy_order) {
        vm->xyzw[0] = wrap72_i64((int64_t)vm->xyzw[0] + a);
        vm->xyzw[1] = wrap72_i64((int64_t)vm->xyzw[1] + b);
    } else {
        vm->xyzw[1] = wrap72_i64((int64_t)vm->xyzw[1] + a);
        vm->xyzw[0] = wrap72_i64((int64_t)vm->xyzw[0] + b);
    }

    // The operation mutates only the ordered x/y pair.  z/w remain independent
    // native basis-state coordinates; no unstated algebraic relation is invented.
    refresh_phase8(vm);
}

// ============================================================
// SWEEP81 / CLOSE81
// ============================================================

static void sweep81(VM81 *vm) {
    uint64_t next[GRID_SIZE];
    for (int r = 0; r < 9; r++) {
        for (int c = 0; c < 9; c++) {
            int i = r * 9 + c;
            uint64_t acc = fold_word72(vm->cells[i]);
            acc += fold_word72(vm->cells[((r + 8) % 9) * 9 + c]);
            acc += fold_word72(vm->cells[((r + 1) % 9) * 9 + c]);
            acc += fold_word72(vm->cells[r * 9 + ((c + 8) % 9)]);
            acc += fold_word72(vm->cells[r * 9 + ((c + 1) % 9)]);
            next[i] = wrap72_u64(acc * 29ULL);
        }
    }
    memcpy(vm->cells, next, sizeof(next));
}

static void close81(VM81 *vm) {
    for (int k = 0; k < 9; k++) {
        int idx = 72 + k;
        vm->cells[idx] = wrap72_i64((int64_t)fold_word72(vm->cells[idx]) + LOSHU[k]);
    }
    for (int k = 0; k < 9; k++) {
        int idx = 63 + k;
        vm->cells[idx] = wrap72_i64((int64_t)fold_word72(vm->cells[idx]) + LOSHU[k]);
    }
}

// ============================================================
// HASH72 POSITIONAL PROJECTION
// ============================================================

static int hash72_to_vector(const char in[HASH_LEN + 1], Hash72Vector *out) {
    if (!in || !out || strlen(in) != HASH_LEN)
        return 0;
    for (int i = 0; i < HASH_LEN; i++) {
        int idx = hash72_index_checked(in[i]);
        if (idx < 0 || idx >= HASH_LEN)
            return 0;
        out->digit[i] = (uint8_t)idx;
    }
    return 1;
}

static void hash72_from_vector(const Hash72Vector *in, char out[HASH_LEN + 1]) {
    for (int i = 0; i < HASH_LEN; i++)
        out[i] = HASH72[in->digit[i] % 72u];
    out[HASH_LEN] = '\0';
}

static void project_hash72(VM81 *vm, char out[HASH_LEN + 1]) {
    uint8_t hidden_for_slot[HASH_LEN];
    memset(hidden_for_slot, 0xFF, sizeof(hidden_for_slot));
    for (int k = 0; k < 9; k++)
        hidden_for_slot[LOSHU_SLOTS[k]] = (uint8_t)(72 + k);

    Hash72Vector genesis;
    if (!hash72_to_vector(vm->genesis_hash, &genesis))
        memset(&genesis, 0, sizeof(genesis));

    Hash72Vector state;
    memset(&state, 0, sizeof(state));
    for (uint8_t i = 0; i < HASH_LEN; i++) {
        uint8_t h_contrib = 0;
        if (hidden_for_slot[i] != 0xFFu) {
            uint8_t hc = hidden_for_slot[i];
            h_contrib = wrap72_i64((int64_t)fold_word72(vm->cells[hc]) +
                                    ((int64_t)hc - 72) * 7);
        }

        // Preserve the historical Hash72 projection law.  The VM carrier is
        // now 64-bit/cell, so phase projection folds the carrier word to Z72.
        uint8_t v = wrap72_i64((int64_t)fold_word72(vm->cells[i]) +
                               genesis.digit[i] + h_contrib +
                               (int64_t)(i * 3u));

        // Encode the token occurrence as one exact coordinate of the 72x72
        // positional plane, then decode it back.  This makes the 5,184
        // position/symbol topology explicit without changing the symbol law.
        uint16_t coord = hash72_coord(i, v);
        uint8_t pos2 = 0, sym2 = 0;
        hash72_coord_decode(coord, &pos2, &sym2);
        state.digit[pos2] = sym2;
    }
    hash72_from_vector(&state, out);
}

static void compose_receipt_hash(const char *prev, uint8_t cg, uint32_t witness,
                                 const char *state, char out[HASH_LEN + 1]) {
    for (int i = 0; i < HASH_LEN; i++) {
        int pi = hash72_index_checked(prev[i]);
        int si = hash72_index_checked(state[i]);
        uint8_t p = (uint8_t)(pi < 0 ? 0 : pi);
        uint8_t s = (uint8_t)(si < 0 ? 0 : si);
        uint8_t w = (uint8_t)((witness ^ (witness >> 8) ^
                               (witness >> 16) ^ (witness >> 24) ^
                               (uint32_t)i) & 0xFFu);
        uint8_t r = wrap72_i64((int64_t)p + s + cg + w + (i * 7));
        uint16_t coord = hash72_coord((uint8_t)i, r);
        out[i] = HASH72[coord % 72u];
    }
    out[HASH_LEN] = '\0';
}

static int hash72_validate_word(const char *hash) {
    Hash72Vector v;
    return hash72_to_vector(hash, &v);
}

// ============================================================
// ORBIT / CLOSURE
// ============================================================

static uint64_t detect_orbit(VM81 *vm, const char *hash, uint64_t cur) {
    for (uint64_t i = 0; i < vm->seen_count; i++) {
        if (strcmp(vm->seen[i].hash, hash) == 0)
            return cur - vm->seen[i].step;
    }
    if (vm->seen_count < MAX_SEEN) {
        strcpy(vm->seen[vm->seen_count].hash, hash);
        vm->seen[vm->seen_count].step = cur;
        vm->seen_count++;
    }
    return 0;
}

static int close_orientation(VM81 *vm) {
    refresh_phase8(vm);
    return vm->phase8[HHS_PHASE_YX] == reciprocal_phase(vm->phase8[HHS_PHASE_XY]) &&
           vm->phase8[HHS_PHASE_WZ] == reciprocal_phase(vm->phase8[HHS_PHASE_ZW]);
}

static int close_constraint(VM81 *vm) {
    for (uint64_t i = 0; i < vm->constraint_count; i++) {
        Constraint72 *k = &vm->constraints[i];
        if (k->active && k->strength > CONSTRAINT_CLOSURE_THRESHOLD)
            return 0;
    }
    return 1;
}

// ============================================================
// GATES
// ============================================================

static int check_gate_apb(VM81 *vm, uint8_t a, uint8_t p, uint8_t b) {
    return vm->cells[a % GRID_SIZE] == vm->cells[p % GRID_SIZE] &&
           vm->cells[p % GRID_SIZE] == vm->cells[b % GRID_SIZE];
}

static int check_gate_closure(VM81 *vm, uint8_t Pc, uint8_t pc, uint8_t qc,
                              uint8_t nc, uint8_t xc, uint8_t yc) {
    uint8_t P = fold_word72(vm->cells[Pc % GRID_SIZE]);
    uint8_t p = fold_word72(vm->cells[pc % GRID_SIZE]);
    uint8_t q = fold_word72(vm->cells[qc % GRID_SIZE]);
    uint8_t n = fold_word72(vm->cells[nc % GRID_SIZE]);
    uint8_t x = fold_word72(vm->cells[xc % GRID_SIZE]);
    uint8_t y = fold_word72(vm->cells[yc % GRID_SIZE]);
    uint8_t P2 = wrap72_i64((int64_t)P * P);
    uint8_t pq = wrap72_i64((int64_t)p * q);
    uint8_t lhs = wrap72_i64((int64_t)P2 - pq);
    uint8_t n2 = wrap72_i64((int64_t)n * n);
    uint8_t n4 = wrap72_i64((int64_t)n2 * n2);
    uint8_t xy = wrap72_i64((int64_t)x * y);
    return lhs == n4 && n4 == xy;
}

// The historical gate attempted to decide a symbolic/transcendental identity
// numerically.  Canonical authority now refuses approximation.  This exact
// gate proves only the reciprocal ordered-phase portion; if the complete
// symbolic identity is not represented in this kernel frame it returns the
// typed unresolved/degenerate verdict (-1) rather than approximating a proof.
static int check_gate_identity_exact(VM81 *vm, uint8_t xc, uint8_t yc, uint8_t uc,
                                     uint64_t *witness_out) {
    uint8_t x = fold_word72(vm->cells[xc % GRID_SIZE]);
    uint8_t y = fold_word72(vm->cells[yc % GRID_SIZE]);
    uint8_t u = fold_word72(vm->cells[uc % GRID_SIZE]);
    uint8_t xy = hhs_dynamic_pair_phase(HHS_PHASE_X, HHS_PHASE_Y, x, y);
    uint8_t yx = hhs_dynamic_pair_phase(HHS_PHASE_Y, HHS_PHASE_X, y, x);
    uint64_t witness = ((uint64_t)x << 24) | ((uint64_t)y << 16) |
                       ((uint64_t)u << 8) | ((uint64_t)xy << 1) |
                       (uint64_t)(yx == reciprocal_phase(xy));
    if (witness_out)
        *witness_out = witness;
    if (x == 0 || y == 0 || u == 0)
        return -1;
    if (yx != reciprocal_phase(xy))
        return 0;
    return -1;
}

static uint8_t qgu_delta(uint8_t q, uint8_t c, uint8_t d) {
    uint8_t q2 = wrap72_i64((int64_t)q * q);
    uint8_t q4 = wrap72_i64((int64_t)q2 * q2);
    return wrap72_i64((int64_t)c * q2 + (int64_t)d * q4);
}

// ============================================================
// EXACT LAYERED EXTENSIONS
// ============================================================

static HHSRational hhs_calc_m_reciprocal(uint8_t xy_energy) {
    // 8/5 + 11/7 + 13/8 + 3/2 + 5/3 + 7/4 = 8159/840.
    // Division by 2*(xy+1) => 8159 / (1680*(xy+1)).
    return rational_make(8159, 1680ULL * ((uint64_t)xy_energy + 1ULL));
}

static void hhs_apply_ouroboros_closure(VM81 *vm) {
    uint8_t x = vm->xyzw[0];
    uint8_t x2 = wrap72_i64((int64_t)x * x);
    uint8_t x4 = wrap72_i64((int64_t)x2 * x2);
    vm->xyzw[3] = wrap72_i64((int64_t)(x4 / 4u));
    refresh_phase8(vm);
    sweep81(vm);
}

static void tensor_push(VM81 *vm, int64_t real_num, int64_t imag_num,
                        uint64_t den, uint8_t phase) {
    if (vm->tensor_count >= MAX_TENSORS || den == 0)
        return;
    HHSTensor *t = &vm->tensors[vm->tensor_count++];
    uint64_t g = gcd_u64(gcd_u64(abs_i64_u64(real_num), abs_i64_u64(imag_num)), den);
    t->real_num = real_num / (int64_t)g;
    t->imag_num = imag_num / (int64_t)g;
    t->den = den / g;
    t->phase = (uint8_t)(phase % 72u);
    t->orientation = (uint8_t)(phase & 1u);
}

static int tensor_reciprocal(HHSTensor *t) {
    int64_t a = t->real_num;
    int64_t b = t->imag_num;
    uint64_t d = t->den;
    uint64_t aa = abs_i64_u64(a);
    uint64_t bb = abs_i64_u64(b);
    if (aa > 0xFFFFFFFFULL || bb > 0xFFFFFFFFULL || d > (uint64_t)INT64_MAX)
        return 0;
    uint64_t denom = aa * aa + bb * bb;
    if (denom == 0)
        return 0;
    if (aa != 0 && d > (uint64_t)INT64_MAX / aa)
        return 0;
    if (bb != 0 && d > (uint64_t)INT64_MAX / bb)
        return 0;
    int64_t nr = a * (int64_t)d;
    int64_t ni = -b * (int64_t)d;
    uint64_t g = gcd_u64(gcd_u64(abs_i64_u64(nr), abs_i64_u64(ni)), denom);
    t->real_num = nr / (int64_t)g;
    t->imag_num = ni / (int64_t)g;
    t->den = denom / g;
    t->phase = reciprocal_phase(t->phase);
    t->orientation ^= 1u;
    return 1;
}

static void tensor_phase_lock(HHSTensor *a, HHSTensor *b) {
    uint8_t delta = wrap72_i64((int64_t)b->phase - a->phase);
    uint8_t p = wrap72_i64((int64_t)a->phase + (delta / 2u));
    a->phase = p;
    b->phase = p;
}

static void hhs_tensor_seed_from_xyzw(VM81 *vm) {
    tensor_push(vm, vm->xyzw[0], vm->xyzw[1], 1, vm->phase8[HHS_PHASE_XY]);
    tensor_push(vm, vm->xyzw[2], vm->xyzw[3], 1, vm->phase8[HHS_PHASE_ZW]);
    if (vm->tensor_count >= 2)
        tensor_phase_lock(&vm->tensors[0], &vm->tensors[1]);
}

static void hhs_genomic_map(VM81 *vm) {
    for (uint8_t i = 0; i < 4; i++)
        vm->genomic[i] = wrap72_i64((int64_t)vm->genomic[i] + vm->xyzw[i]);
}

static void hhs_manifold_step(VM81 *vm, uint8_t driver) {
    for (int r = 0; r < MANIFOLD_DIM; r++) {
        for (int c = 0; c < MANIFOLD_DIM; c++) {
            uint8_t lo = LOSHU[(r * 3 + c) % 9];
            uint8_t phase = vm->phase8[(r + c) % PHASE_BASIS_COUNT];
            vm->manifold[r][c] = wrap72_i64((int64_t)vm->manifold[r][c] +
                                             driver + lo + phase + r + c);
        }
    }
}

// ============================================================
// VM INIT
// ============================================================

static void vm81_init(VM81 *vm, uint64_t seed, SeedMode mode) {
    memset(vm, 0, sizeof(*vm));
    uint64_t mixer = seed;
    if (mode == SEED_PALINDROME)
        mixer ^= PALINDROME_SEED;

    for (int i = 0; i < GRID_SIZE; i++) {
        uint64_t word = (uint64_t)i * 2654435761ULL
                      ^ mixer * 0x9E3779B97F4A7C15ULL
                      ^ (mixer >> 13);
        // Preserve a true 64-bit raw carrier.  Phase consumers fold to Z72.
        vm->cells[i] = word;
    }

    if (mode == SEED_LOSHU) {
        for (int k = 0; k < 9; k++) {
            vm->cells[72 + k] = (uint64_t)LOSHU[k] * 8ULL;
            vm->cells[63 + k] = (uint64_t)wrap72_i64((int64_t)LOSHU[k] * 8 +
                                                      (int64_t)(seed % 72ULL));
        }
    }

    for (int i = 0; i < HASH_LEN; i++) {
        uint64_t x = ((uint64_t)i * 11400714819323198485ULL)
                   ^ (mixer + (uint64_t)i * 0xC2B2AE3D27D4EB4FULL);
        if (mode == SEED_PALINDROME)
            x ^= PALINDROME_SEED * (uint64_t)(i + 1);
        vm->genesis_hash[i] = HASH72[x % 72ULL];
    }
    vm->genesis_hash[HASH_LEN] = '\0';

    vm->xyzw[0] = HHS_PHASE_ANCHOR[HHS_PHASE_X];
    vm->xyzw[1] = HHS_PHASE_ANCHOR[HHS_PHASE_Y];
    vm->xyzw[2] = HHS_PHASE_ANCHOR[HHS_PHASE_Z];
    vm->xyzw[3] = HHS_PHASE_ANCHOR[HHS_PHASE_W];
    refresh_phase8(vm);
    memcpy(vm->genomic, vm->xyzw, sizeof(vm->genomic));
}

// ============================================================
// EXECUTION
// ============================================================

static void apply_instruction(VM81 *vm, Instruction *ins, uint32_t *witness,
                              uint64_t *identity_exact_witness_out,
                              int *identity_has_data_out) {
    uint64_t *A = &vm->cells[ins->a % GRID_SIZE];
    uint64_t *B = &vm->cells[ins->b % GRID_SIZE];
    uint64_t *C = &vm->cells[ins->c % GRID_SIZE];
    uint8_t pa = fold_word72(*A);
    uint8_t pb = fold_word72(*B);
    uint8_t energy = 0;
    int branched = 0;
    uint64_t new_pc = vm->pc + 1;

    switch (ins->op) {
        case OP_NOP:
            energy = ins->cg_id;
            break;
        case OP_ADD:
            *C = *A + *B;
            energy = fold_word72(*C);
            break;
        case OP_SUB:
            *C = *A - *B;
            energy = fold_word72(*C);
            break;
        case OP_ROT:
            *C = (uint64_t)wrap72_i64((int64_t)pa + ins->phase);
            energy = fold_word72(*C);
            break;
        case OP_XOR:
            *C = *A ^ *B;
            energy = wrap72_i64((int64_t)fold_word72(*C) + ins->phase + ins->cg_id);
            break;
        case OP_AND:
            *C = *A & *B;
            energy = wrap72_i64((int64_t)fold_word72(*C) + ins->phase);
            break;
        case OP_OR:
            *C = *A | *B;
            energy = wrap72_i64((int64_t)fold_word72(*C) + ins->phase);
            break;
        case OP_LOAD:
            *C = (uint64_t)ins->a;
            energy = fold_word72(*C);
            break;
        case OP_STORE:
            *C = *A;
            energy = fold_word72(*C);
            break;
        case OP_MULXY: {
            HHSOrderedPhaseProduct p = hhs_phase_product_anchor(HHS_PHASE_X, HHS_PHASE_Y);
            *C = p.phase;
            apply_xyzw_state(vm, pa, pb, 1);
            propagate_phase_transport(vm, pa, p.phase, ins->cg_id);
            propagate_phase_transport(vm, pb, p.phase, ins->cg_id);
            *witness |= W_NONCOMMUTATIVE | W_PHASE_TABLE_LOCKED;
            energy = p.phase;
            goto finalize;
        }
        case OP_MULYX: {
            HHSOrderedPhaseProduct p = hhs_phase_product_anchor(HHS_PHASE_Y, HHS_PHASE_X);
            *C = p.phase;
            apply_xyzw_state(vm, pa, pb, 0);
            propagate_phase_transport(vm, pb, p.phase, ins->cg_id);
            propagate_phase_transport(vm, pa, p.phase, ins->cg_id);
            *witness |= W_NONCOMMUTATIVE | W_PHASE_TABLE_LOCKED;
            energy = p.phase;
            goto finalize;
        }
        case OP_QGU: {
            uint8_t d = fold_word72(vm->cells[ins->cg_id % GRID_SIZE]);
            uint8_t delta = qgu_delta(pa, pb, d);
            *C = wrap72_i64((int64_t)fold_word72(*C) + delta);
            energy = fold_word72(*C);
            *witness |= W_QGU_APPLIED;
            break;
        }
        case OP_GATE_APB: {
            int pass = check_gate_apb(vm, ins->a, ins->b, ins->c);
            *witness |= pass ? W_GATE_APB_PASS : W_GATE_APB_FAIL;
            energy = wrap72_i64((int64_t)ins->cg_id + (pass ? 0 : 36));
            break;
        }
        case OP_GATE_CLOSURE: {
            uint8_t nc = (uint8_t)(ins->cg_id & 0x0Fu);
            uint8_t xc = (uint8_t)((ins->cg_id >> 4) & 0x0Fu);
            uint8_t yc = (uint8_t)(ins->phase & 0x0Fu);
            int pass = check_gate_closure(vm, ins->a, ins->b, ins->c, nc, xc, yc);
            *witness |= pass ? W_GATE_CLOSURE_PASS : W_GATE_CLOSURE_FAIL;
            energy = wrap72_i64((int64_t)ins->cg_id + (pass ? 0 : 48));
            break;
        }
        case OP_GATE_IDENTITY: {
            uint64_t exact_witness = 0;
            int verdict = check_gate_identity_exact(vm, ins->a, ins->b, ins->c, &exact_witness);
            if (verdict == 1) {
                *witness |= W_GATE_IDENTITY_PASS;
                vm->ever_identity_pass = 1;
            } else if (verdict == 0) {
                *witness |= W_GATE_IDENTITY_FAIL;
            } else {
                *witness |= W_IDENTITY_DEGENERATE;
            }
            if (identity_exact_witness_out)
                *identity_exact_witness_out = exact_witness;
            if (identity_has_data_out)
                *identity_has_data_out = 1;
            energy = wrap72_i64((int64_t)ins->cg_id + (verdict == 1 ? 0 : 24));
            break;
        }
        case OP_QBRANCH: {
            uint8_t pol = polarity_of(pa);
            if (ins->next[pol].enabled && ins->next[pol].target < vm->program_len) {
                new_pc = ins->next[pol].target;
                branched = 1;
            } else {
                vm->halted = 1;
            }
            energy = wrap72_i64((int64_t)ins->cg_id + pol * 9);
            break;
        }
        case OP_CONSTRAIN:
            constraint_add(vm, ins->a, fold_word72(vm->cells[ins->b % GRID_SIZE]), ins->c);
            *witness |= W_CONSTRAINT_FIRED;
            energy = wrap72_i64((int64_t)ins->cg_id + ins->c);
            break;
        case OP_RELAX:
            constraint_relax(vm, ins->a);
            energy = wrap72_i64((int64_t)ins->cg_id + 1);
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
            } else vm->halted = 1;
            energy = ins->cg_id;
            break;
        case OP_BZ:
            if (*A == 0) {
                if (ins->b < vm->program_len) {
                    new_pc = ins->b;
                    branched = 1;
                } else vm->halted = 1;
            }
            energy = ins->cg_id;
            break;
        case OP_BNZ:
            if (*A != 0) {
                if (ins->b < vm->program_len) {
                    new_pc = ins->b;
                    branched = 1;
                } else vm->halted = 1;
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

    if (!vm->halted)
        propagate_phase_transport(vm, ins->phase, energy, ins->cg_id);

finalize:
    constraint_compete(vm);
    if (branched && new_pc <= vm->pc)
        vm->sweep++;
    vm->pc = new_pc;
}

// ============================================================
// STEP / RECEIPT
// ============================================================

static void vm81_step(VM81 *vm) {
    if (vm->halted)
        return;
    if (vm->pc >= vm->program_len) {
        vm->last_receipt.witness |= W_HALT | W_LEDGER_FROZEN;
        vm->last_receipt.ledger_advanced = 0;
        vm->last_receipt.step = vm->step;
        vm->halted = 1;
        return;
    }

    Instruction *ins = &vm->program[vm->pc];
    if (!op_advances_ledger(ins->op)) {
        uint32_t w = 0;
        uint64_t id_w = 0;
        int id_has = 0;
        apply_instruction(vm, ins, &w, &id_w, &id_has);
        vm->last_receipt.witness |= w | W_LEDGER_FROZEN;
        vm->last_receipt.ledger_advanced = 0;
        vm->last_receipt.step = vm->step;
        vm->last_receipt.orbit_period = 0;
        if (id_has) {
            vm->last_receipt.identity_exact_witness = id_w;
            vm->last_receipt.identity_has_data = 1;
        }
        vm->step++;
        return;
    }

    char prev[HASH_LEN + 1];
    char state[HASH_LEN + 1];
    char rec[HASH_LEN + 1];
    uint32_t witness = W_HASH72_POSITIONAL;
    uint64_t id_w = 0;
    int id_has = 0;

    project_hash72(vm, prev);
    apply_instruction(vm, ins, &witness, &id_w, &id_has);
    project_hash72(vm, state);

    uint64_t orbit = detect_orbit(vm, state, vm->step);
    if (orbit > 0) {
        witness |= W_ORBIT_DETECTED | W_CLOSE_TRANSPORT;
        vm->orbit_halted = 1;
        vm->ever_closed_transport = 1;
    }
    if (close_orientation(vm)) {
        witness |= W_CLOSE_ORIENTATION;
        vm->ever_closed_orientation = 1;
    }
    if (close_constraint(vm)) {
        witness |= W_CLOSE_CONSTRAINT;
        vm->ever_closed_constraint = 1;
    }
    uint32_t closure_mask = W_CLOSE_TRANSPORT | W_CLOSE_ORIENTATION | W_CLOSE_CONSTRAINT;
    if ((witness & closure_mask) == closure_mask) {
        witness |= W_CONVERGED;
        vm->converged = 1;
    }

    compose_receipt_hash(prev, ins->cg_id, witness, state, rec);
    strcpy(vm->last_receipt.prev_h72, prev);
    strcpy(vm->last_receipt.state_h72, state);
    strcpy(vm->last_receipt.receipt_h72, rec);
    vm->last_receipt.cg_id = ins->cg_id;
    vm->last_receipt.witness = witness;
    vm->last_receipt.step = vm->step;
    vm->last_receipt.orbit_period = orbit;
    vm->last_receipt.ledger_advanced = 1;
    vm->last_receipt.identity_exact_witness = id_w;
    vm->last_receipt.identity_has_data = id_has;
    vm->step++;
}

// ============================================================
// PRINT / VERIFY
// ============================================================

static void print_witness(uint32_t w) {
    printf("WITNESS:");
    if (!w) printf(" -");
    if (w & W_GATE_APB_PASS)       printf(" APB+");
    if (w & W_GATE_APB_FAIL)       printf(" APB-");
    if (w & W_GATE_CLOSURE_PASS)   printf(" CLOSURE+");
    if (w & W_GATE_CLOSURE_FAIL)   printf(" CLOSURE-");
    if (w & W_GATE_IDENTITY_PASS)  printf(" ID+");
    if (w & W_GATE_IDENTITY_FAIL)  printf(" ID-");
    if (w & W_IDENTITY_DEGENERATE) printf(" ID?");
    if (w & W_QGU_APPLIED)         printf(" QGU");
    if (w & W_NONCOMMUTATIVE)      printf(" NC");
    if (w & W_PHASE_TABLE_LOCKED)  printf(" U72");
    if (w & W_HASH72_POSITIONAL)   printf(" H72POS");
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
    printf("\nSTEP %llu SWEEP %llu PC %llu K=%llu LEDGER=%s\n",
           (unsigned long long)vm->last_receipt.step,
           (unsigned long long)vm->sweep,
           (unsigned long long)vm->pc,
           (unsigned long long)vm->constraint_count,
           vm->last_receipt.ledger_advanced ? "ADVANCED" : "FROZEN");
    printf("CG%u\n", vm->last_receipt.cg_id);
    printf("PREV:    %s\n", vm->last_receipt.prev_h72);
    printf("STATE:   %s\n", vm->last_receipt.state_h72);
    printf("RECEIPT: %s\n", vm->last_receipt.receipt_h72);
    print_witness(vm->last_receipt.witness);
    printf("XYZW: [%u %u %u %u] XY=%u YX=%u ZW=%u WZ=%u\n",
           vm->xyzw[0], vm->xyzw[1], vm->xyzw[2], vm->xyzw[3],
           vm->phase8[HHS_PHASE_XY], vm->phase8[HHS_PHASE_YX],
           vm->phase8[HHS_PHASE_ZW], vm->phase8[HHS_PHASE_WZ]);
    if (vm->last_receipt.identity_has_data)
        printf("IDENTITY exact witness: %llu\n",
               (unsigned long long)vm->last_receipt.identity_exact_witness);
    if (vm->last_receipt.orbit_period > 0)
        printf("ORBIT PERIOD: %llu\n", (unsigned long long)vm->last_receipt.orbit_period);
    if (vm->halted) printf("HALTED\n");
}

static void print_closure_summary(VM81 *vm) {
    printf("\n---- RUN CLOSURE SUMMARY ----\n");
    printf("Transport closure ever reached : %s\n", vm->ever_closed_transport ? "YES" : "no");
    printf("Orientation closure ever reached : %s\n", vm->ever_closed_orientation ? "YES" : "no");
    printf("Constraint closure ever reached : %s\n", vm->ever_closed_constraint ? "YES" : "no");
    printf("Identity gate ever passed : %s\n", vm->ever_identity_pass ? "YES" : "no");
    printf("Joint CONVERGED at some step : %s\n", vm->converged ? "YES" : "no");
    printf("Tensor layer count : %llu\n", (unsigned long long)vm->tensor_count);
    printf("Genomic layer : [%u %u %u %u]\n",
           vm->genomic[0], vm->genomic[1], vm->genomic[2], vm->genomic[3]);
    printf("Frame bits/bytes : %d/%d\n", VM81_FRAME_BITS, VM81_FRAME_BYTES);
    printf("Hash72 alphabet/positions/positional-plane : %d/%d/%d\n",
           HASH_LEN, HASH_LEN, HASH72_COORDS);
    printf("Hash72 formal word space : 72^%d\n", HASH72_STATE_EXPONENT);
    printf("-----------------------------\n");
}

static int verify_kernel_invariants(VM81 *vm) {
    if (!hhs_phase_table_selfcheck())
        return 0;
    if (!hash72_validate_word(vm->genesis_hash))
        return 0;
    char h[HASH_LEN + 1];
    project_hash72(vm, h);
    if (!hash72_validate_word(h))
        return 0;
    for (uint16_t coord = 0; coord < 5184; coord++) {
        uint8_t p, s;
        hash72_coord_decode(coord, &p, &s);
        if (hash72_coord(p, s) != coord)
            return 0;
    }
    for (uint16_t addr = 0; addr < 5184; addr++) {
        uint8_t c, l, r;
        vm5184_decode(addr, &c, &l, &r);
        if (vm5184_address(c, l, r) != addr)
            return 0;
    }
    uint8_t frame[VM81_FRAME_BYTES];
    VM81 copy = *vm;
    vm81_serialize_frame_le(vm, frame);
    memset(copy.cells, 0, sizeof(copy.cells));
    vm81_deserialize_frame_le(&copy, frame);
    if (memcmp(copy.cells, vm->cells, sizeof(vm->cells)) != 0)
        return 0;
    return 1;
}

// ============================================================
// DEMO
// ============================================================

static void load_demo(VM81 *vm) {
    vm->program_len = 0;
    vm->cells[10] = 36;
    vm->cells[11] = 54;
    vm->cells[12] = 40;
    vm->program[vm->program_len++] = instruction_make(OP_ADD,0,1,2,21,3);
    vm->program[vm->program_len++] = instruction_make(OP_MULXY,2,1,3,16,7);
    vm->program[vm->program_len++] = instruction_make(OP_QGU,3,1,4,2,11);
    vm->program[vm->program_len++] = instruction_make(OP_GATE_APB,0,0,0,17,0);
    vm->program[vm->program_len++] = instruction_make(OP_GATE_IDENTITY,10,11,12,25,0);
    vm->program[vm->program_len++] = instruction_make(OP_CONSTRAIN,1,4,40,19,0);
    vm->program[vm->program_len++] = instruction_make(OP_SWEEP81,0,0,0,22,0);
    vm->program[vm->program_len++] = instruction_make(OP_CLOSE81,0,0,0,23,0);
    vm->program[vm->program_len++] = instruction_make(OP_LOAD,50,0,10,5,0);
    vm->program[vm->program_len++] = instruction_make(OP_LOAD,20,0,11,5,0);
    vm->program[vm->program_len++] = instruction_make(OP_LOAD,60,0,12,5,0);
    vm->program[vm->program_len++] = instruction_make(OP_GATE_IDENTITY,10,11,12,26,0);
    vm->program[vm->program_len++] = instruction_make(OP_RELAX,40,0,0,18,0);
    vm->program[vm->program_len++] = instruction_make(OP_HALT,0,0,0,0,0);
}

typedef struct {
    int steps;
    uint64_t seed;
    SeedMode mode;
    int trace;
    int halt_on_orbit;
    int verify;
} Options;

static void run_vm(VM81 *vm, Options *opt) {
    for (int i = 0; i < opt->steps && i < MAX_STEPS; i++) {
        vm81_step(vm);
        if (opt->trace) print_vm(vm);
        if (vm->halted) break;
        if (opt->halt_on_orbit && vm->orbit_halted) break;
    }
}

// ============================================================
// PYTHON->VM IR BRIDGE (kept inside the same exact kernel source)
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

typedef struct {
    HHS_IR_Node *nodes;
    uint32_t node_count;
    uint32_t entry_phase;
    uint32_t parent_block;
} HHS_IR_Block;

typedef struct {
    char symbol[64];
    uint32_t reg;
    uint32_t ir_block;
    uint32_t transport_phase;
    uint32_t witness_mask;
} HHS_SymbolBinding;

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

typedef struct {
    HHS_IR_Block *blocks;
    uint32_t block_count;
    HHS_SymbolBinding symbols[256];
    uint32_t symbol_count;
} HHS_IR_Program;

static void hhs_frame_init(HHS_VM_Frame *f) {
    memset(f, 0, sizeof(*f));
}

static void hhs_ir_project_hash72(VM81 *vm, char out[HASH_LEN + 1]) {
    project_hash72(vm, out);
}

static void hhs_vm_native_add(VM81 *vm, uint64_t a, uint64_t b, uint64_t *out) {
    vm->cells[0] = a;
    vm->cells[1] = b;
    Instruction ins = instruction_make(OP_ADD,0,1,2,31,7);
    uint32_t witness = 0;
    uint64_t idw = 0;
    int idh = 0;
    apply_instruction(vm, &ins, &witness, &idw, &idh);
    *out = vm->cells[2];
}

static void hhs_vm_native_mul(VM81 *vm, uint64_t a, uint64_t b, uint64_t *out) {
    vm->cells[0] = a;
    vm->cells[1] = b;
    Instruction ins = instruction_make(OP_MULXY,0,1,2,32,9);
    uint32_t witness = 0;
    uint64_t idw = 0;
    int idh = 0;
    apply_instruction(vm, &ins, &witness, &idw, &idh);
    *out = vm->cells[2];
}

static int hhs_execute_ir_node(VM81 *vm, HHS_VM_Frame *frame, HHS_IR_Node *node) {
    if (node->dst >= 256u || node->srcA >= 256u || node->srcB >= 256u)
        return 0;
    uint64_t a = frame->registers[node->srcA];
    uint64_t b = frame->registers[node->srcB];
    switch (node->op) {
        case IR_NOP: break;
        case IR_CONST: frame->registers[node->dst] = node->imm; break;
        case IR_MOVE: frame->registers[node->dst] = a; break;
        case IR_ADD: hhs_vm_native_add(vm, a, b, &frame->registers[node->dst]); break;
        case IR_SUB: frame->registers[node->dst] = a - b; break;
        case IR_MUL: hhs_vm_native_mul(vm, a, b, &frame->registers[node->dst]); break;
        case IR_DIV: if (b == 0) return 0; frame->registers[node->dst] = a / b; break;
        case IR_MOD: if (b == 0) return 0; frame->registers[node->dst] = a % b; break;
        case IR_COMPARE_EQ: frame->last_compare = (a == b); break;
        case IR_COMPARE_NEQ: frame->last_compare = (a != b); break;
        case IR_COMPARE_LT: frame->last_compare = (a < b); break;
        case IR_COMPARE_GT: frame->last_compare = (a > b); break;
        case IR_BRANCH:
            if (frame->last_compare) { frame->current_block = (uint32_t)node->imm; frame->current_node = 0; }
            break;
        case IR_JUMP:
            frame->current_block = (uint32_t)node->imm; frame->current_node = 0; break;
        case IR_CALL:
            if (frame->sp > 1021u) return 0;
            frame->stack[frame->sp++] = frame->current_block;
            frame->stack[frame->sp++] = frame->current_node;
            frame->current_block = (uint32_t)node->imm;
            frame->current_node = 0;
            break;
        case IR_RETURN:
            if (frame->sp < 2u) { frame->halted = 1; break; }
            frame->current_node = (uint32_t)frame->stack[--frame->sp];
            frame->current_block = (uint32_t)frame->stack[--frame->sp];
            break;
        case IR_CONSTRAIN:
            constraint_add(vm, (uint8_t)a, (uint8_t)b, (uint8_t)(node->imm & 0xFFu));
            break;
        case IR_QGU:
            frame->registers[node->dst] = qgu_delta((uint8_t)(a % 72u),
                                                    (uint8_t)(b % 72u),
                                                    (uint8_t)(node->imm % 72u));
            break;
        case IR_HASH72_PROJECT: {
            char hash[HASH_LEN + 1];
            hhs_ir_project_hash72(vm, hash);
            printf("[IR HASH72] %s\n", hash);
            break;
        }
        case IR_VM_NATIVE: break;
        default: return 0;
    }
    return 1;
}

static int hhs_execute_ir_block(VM81 *vm, HHS_IR_Program *prog, HHS_VM_Frame *frame) {
    if (frame->current_block >= prog->block_count) return 0;
    HHS_IR_Block *blk = &prog->blocks[frame->current_block];
    while (frame->current_node < blk->node_count) {
        uint32_t before_block = frame->current_block;
        uint32_t before_node = frame->current_node;
        HHS_IR_Node *node = &blk->nodes[frame->current_node];
        if (!hhs_execute_ir_node(vm, frame, node)) return 0;
        if (frame->halted) return 1;
        if (frame->current_block == before_block && frame->current_node == before_node)
            frame->current_node++;
        else
            return 1;
    }
    return 1;
}

static int hhs_execute_ir(VM81 *vm, HHS_IR_Program *prog, HHS_VM_Frame *frame) {
    uint64_t guard = 0;
    while (!frame->halted && guard++ < MAX_STEPS) {
        uint32_t block_before = frame->current_block;
        if (!hhs_execute_ir_block(vm, prog, frame)) return 0;
        if (frame->halted) break;
        if (frame->current_block == block_before) {
            if (frame->current_block + 1u >= prog->block_count) frame->halted = 1;
            else { frame->current_block++; frame->current_node = 0; }
        }
    }
    return guard < MAX_STEPS;
}

static HHS_IR_Node DEMO_NODES[] = {
    { IR_CONST,0,0,0,5,0,0,0 },
    { IR_CONST,1,0,0,7,0,0,0 },
    { IR_ADD,2,0,1,0,0,0,0 },
    { IR_MUL,3,2,1,0,0,0,0 },
    { IR_QGU,4,3,1,9,0,0,0 },
    { IR_HASH72_PROJECT,0,0,0,0,0,0,0 }
};

static HHS_IR_Block DEMO_BLOCKS[] = {
    { DEMO_NODES, sizeof(DEMO_NODES)/sizeof(DEMO_NODES[0]), 0, 0 }
};

static HHS_IR_Program DEMO_PROGRAM = { .blocks = DEMO_BLOCKS, .block_count = 1 };

static void hhs_run_bridge_demo(VM81 *vm) {
    HHS_VM_Frame frame;
    hhs_frame_init(&frame);
    if (!hhs_execute_ir(vm, &DEMO_PROGRAM, &frame)) {
        printf("IR bridge execution failed\n");
        return;
    }
    printf("R0=%llu R1=%llu R2=%llu R3=%llu R4=%llu\n",
           (unsigned long long)frame.registers[0],
           (unsigned long long)frame.registers[1],
           (unsigned long long)frame.registers[2],
           (unsigned long long)frame.registers[3],
           (unsigned long long)frame.registers[4]);
}

// ============================================================
// MAIN
// ============================================================

int main(int argc, char **argv) {
    if (!init_hash72()) {
        fprintf(stderr, "kernel init failed: Hash72/phase table invariant\n");
        return 2;
    }

    Options opt = {128,0,SEED_LOSHU,1,0,0};
    int bridge_demo = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--steps") && i + 1 < argc) opt.steps = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--seed") && i + 1 < argc) opt.seed = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--palindrome")) opt.mode = SEED_PALINDROME;
        else if (!strcmp(argv[i], "--loshu")) opt.mode = SEED_LOSHU;
        else if (!strcmp(argv[i], "--halt-on-orbit")) opt.halt_on_orbit = 1;
        else if (!strcmp(argv[i], "--verify")) opt.verify = 1;
        else if (!strcmp(argv[i], "--no-trace")) opt.trace = 0;
        else if (!strcmp(argv[i], "--trace")) opt.trace = 1;
        else if (!strcmp(argv[i], "--bridge-demo")) bridge_demo = 1;
    }

    VM81 vm;
    vm81_init(&vm, opt.seed, opt.mode);
    load_demo(&vm);
    run_vm(&vm, &opt);

    hhs_tensor_seed_from_xyzw(&vm);
    hhs_genomic_map(&vm);
    hhs_manifold_step(&vm, vm.xyzw[0]);

    if (opt.verify) {
        HHSRational mrec = hhs_calc_m_reciprocal(vm.phase8[HHS_PHASE_XY]);
        printf("\nVERIFY m-reciprocal probe: %lld/%llu\n",
               (long long)mrec.num, (unsigned long long)mrec.den);
        hhs_apply_ouroboros_closure(&vm);
        if (vm.tensor_count > 0)
            (void)tensor_reciprocal(&vm.tensors[0]);
        if (!verify_kernel_invariants(&vm)) {
            fprintf(stderr, "VERIFY kernel invariant failure\n");
            return 3;
        }
        printf("VERIFY exact-kernel invariants: PASS\n");
    }

    if (bridge_demo)
        hhs_run_bridge_demo(&vm);

    print_closure_summary(&vm);
    printf("\nFINAL HASH72:\n%s\n", vm.last_receipt.state_h72);
    return 0;
}
