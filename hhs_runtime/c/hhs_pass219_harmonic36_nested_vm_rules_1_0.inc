#include "../include/hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <limits.h>
#include <string.h>

#define H36_PC(n) ((uint16_t)(UINT16_C(1) << (n)))
#define H36_MAJOR_SCALE (H36_PC(0)|H36_PC(2)|H36_PC(4)|H36_PC(5)|H36_PC(7)|H36_PC(9)|H36_PC(11))
#define H36_MINOR_SCALE (H36_PC(0)|H36_PC(2)|H36_PC(3)|H36_PC(5)|H36_PC(7)|H36_PC(8)|H36_PC(10))
#define H36_CHROMATIC UINT16_C(0x0FFF)
#define H36_BASS_DEFAULT UINT8_C(255)

typedef struct H36RuleSeed {
    uint8_t era;
    uint8_t function_class;
    uint16_t core;
    uint16_t tension;
    uint16_t resolution;
    uint16_t scale;
    uint8_t bass;
    uint8_t flags;
} H36RuleSeed;

static const H36RuleSeed H36_RULES[HHS_EXACT_PASS219_H36_RULE_COUNT + 1U] = {
    {0,0,0,0,0,0,0,0},
    {1,1,H36_PC(0)|H36_PC(4)|H36_PC(7),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_MAJOR_SCALE,0,0},
    {1,2,H36_PC(0)|H36_PC(2)|H36_PC(5)|H36_PC(9),0,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_MAJOR_SCALE,2,0},
    {1,3,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_MAJOR_SCALE,7,0},
    {1,1,H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(9),0,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_MAJOR_SCALE,9,0},
    {1,3,H36_PC(2)|H36_PC(5)|H36_PC(8)|H36_PC(11),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_MAJOR_SCALE,11,0},
    {1,3,H36_PC(0)|H36_PC(2)|H36_PC(6)|H36_PC(9),0,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,2,1},
    {1,3,H36_PC(0)|H36_PC(3)|H36_PC(6)|H36_PC(9),0,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,6,1},
    {2,2,H36_PC(0)|H36_PC(5)|H36_PC(8),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_MINOR_SCALE,5,1},
    {2,2,H36_PC(0)|H36_PC(3)|H36_PC(8),0,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_MINOR_SCALE,8,1},
    {2,2,H36_PC(1)|H36_PC(5)|H36_PC(8),0,H36_PC(2)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,5,1},
    {2,2,H36_PC(0)|H36_PC(6)|H36_PC(8),0,H36_PC(2)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,8,1},
    {2,2,H36_PC(0)|H36_PC(2)|H36_PC(6)|H36_PC(8),0,H36_PC(2)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,8,1},
    {2,2,H36_PC(0)|H36_PC(3)|H36_PC(6)|H36_PC(8),0,H36_PC(2)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,8,1},
    {2,2,H36_PC(0)|H36_PC(3)|H36_PC(6)|H36_PC(8),0,H36_PC(2)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,8,3},
    {2,5,H36_PC(0)|H36_PC(3)|H36_PC(6)|H36_PC(9),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_CHROMATIC,H36_BASS_DEFAULT,1},
    {2,5,H36_PC(0)|H36_PC(3)|H36_PC(6)|H36_PC(8),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_CHROMATIC,H36_BASS_DEFAULT,1},
    {2,5,H36_PC(3)|H36_PC(7)|H36_PC(11),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_CHROMATIC,7,1},
    {2,7,H36_PC(3)|H36_PC(7)|H36_PC(10),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_CHROMATIC,3,1},
    {2,7,H36_PC(4)|H36_PC(8)|H36_PC(11),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_CHROMATIC,4,1},
    {2,7,H36_PC(0)|H36_PC(3)|H36_PC(8),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_CHROMATIC,8,1},
    {2,7,H36_PC(1)|H36_PC(4)|H36_PC(9),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_CHROMATIC,9,1},
    {2,6,H36_PC(0)|H36_PC(4)|H36_PC(8),0,H36_PC(0)|H36_PC(4)|H36_PC(8),H36_CHROMATIC,H36_BASS_DEFAULT,2},
    {2,6,H36_PC(0)|H36_PC(3)|H36_PC(6)|H36_PC(9),0,H36_PC(0)|H36_PC(3)|H36_PC(6)|H36_PC(9),H36_CHROMATIC,H36_BASS_DEFAULT,2},
    {2,7,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(3)|H36_PC(6)|H36_PC(8)|H36_PC(9)|H36_PC(10),H36_PC(0)|H36_PC(4)|H36_PC(7),H36_CHROMATIC,7,1},
    {3,2,H36_PC(0)|H36_PC(2)|H36_PC(5)|H36_PC(9),H36_PC(4)|H36_PC(7)|H36_PC(11),H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_MAJOR_SCALE,2,0},
    {3,3,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_PC(0)|H36_PC(4)|H36_PC(9),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_MAJOR_SCALE,7,0},
    {3,1,H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_PC(2)|H36_PC(6)|H36_PC(9),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_MAJOR_SCALE,0,0},
    {3,2,H36_PC(0)|H36_PC(2)|H36_PC(5)|H36_PC(8),H36_PC(10),H36_PC(1)|H36_PC(4)|H36_PC(7)|H36_PC(10),H36_MINOR_SCALE,2,1},
    {3,3,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_PC(8),H36_PC(0)|H36_PC(3)|H36_PC(7),H36_CHROMATIC,7,1},
    {3,1,H36_PC(0)|H36_PC(3)|H36_PC(7)|H36_PC(11),H36_PC(2)|H36_PC(5)|H36_PC(9),H36_PC(0)|H36_PC(3)|H36_PC(7)|H36_PC(11),H36_MINOR_SCALE,0,1},
    {3,3,H36_PC(1)|H36_PC(5)|H36_PC(8)|H36_PC(11),H36_PC(3)|H36_PC(6)|H36_PC(10),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,1,4},
    {3,3,H36_PC(2)|H36_PC(5)|H36_PC(8)|H36_PC(10),H36_PC(0)|H36_PC(3)|H36_PC(7),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,10,4},
    {4,3,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(3)|H36_PC(6)|H36_PC(8)|H36_PC(10),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(3)|H36_PC(4)|H36_PC(6)|H36_PC(7)|H36_PC(8)|H36_PC(10),7,4},
    {4,3,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(4)|H36_PC(6)|H36_PC(9),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(2)|H36_PC(4)|H36_PC(6)|H36_PC(7)|H36_PC(9)|H36_PC(11),7,4},
    {4,3,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(3)|H36_PC(6)|H36_PC(8),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(3)|H36_PC(4)|H36_PC(6)|H36_PC(7)|H36_PC(9)|H36_PC(10),7,4},
    {4,3,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(3)|H36_PC(9),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(3)|H36_PC(5)|H36_PC(7)|H36_PC(9)|H36_PC(11),7,4},
    {3,4,H36_PC(0)|H36_PC(3)|H36_PC(7)|H36_PC(10),H36_PC(2)|H36_PC(5)|H36_PC(9),H36_PC(0)|H36_PC(3)|H36_PC(7)|H36_PC(10),H36_PC(0)|H36_PC(2)|H36_PC(3)|H36_PC(5)|H36_PC(7)|H36_PC(9)|H36_PC(10),0,8},
    {4,4,H36_PC(0)|H36_PC(4)|H36_PC(6)|H36_PC(7)|H36_PC(11),H36_PC(2)|H36_PC(9),H36_PC(0)|H36_PC(4)|H36_PC(6)|H36_PC(7)|H36_PC(11),H36_PC(0)|H36_PC(2)|H36_PC(4)|H36_PC(6)|H36_PC(7)|H36_PC(9)|H36_PC(11),0,8},
    {4,4,H36_PC(0)|H36_PC(2)|H36_PC(4)|H36_PC(5)|H36_PC(7)|H36_PC(9)|H36_PC(10),0,H36_PC(0)|H36_PC(2)|H36_PC(4)|H36_PC(5)|H36_PC(7)|H36_PC(9)|H36_PC(10),H36_PC(0)|H36_PC(2)|H36_PC(4)|H36_PC(5)|H36_PC(7)|H36_PC(9)|H36_PC(10),0,8},
    {4,4,H36_PC(0)|H36_PC(5)|H36_PC(10),H36_PC(2)|H36_PC(7),H36_PC(0)|H36_PC(5)|H36_PC(10),H36_CHROMATIC,0,8},
    {4,3,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(6)|H36_PC(9),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,7,16},
    {4,3,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(10)|H36_PC(11),H36_PC(3)|H36_PC(6)|H36_PC(8),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,7,16},
    {4,3,H36_PC(0)|H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(10),H36_PC(9),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,7,8},
    {4,7,H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_PC(2)|H36_PC(6)|H36_PC(9),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,H36_BASS_DEFAULT,32},
    {4,6,H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(8)|H36_PC(11),H36_PC(2)|H36_PC(3)|H36_PC(6)|H36_PC(9)|H36_PC(10),H36_PC(0)|H36_PC(4)|H36_PC(8),H36_CHROMATIC,H36_BASS_DEFAULT,2},
    {3,1,H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(10),H36_PC(3)|H36_PC(5)|H36_PC(9),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(10),H36_CHROMATIC,0,8},
    {4,5,H36_PC(1)|H36_PC(4)|H36_PC(7)|H36_PC(10),0,H36_PC(0)|H36_PC(2)|H36_PC(5)|H36_PC(9),H36_CHROMATIC,1,2},
    {2,7,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_PC(2)|H36_PC(5)|H36_PC(9)|H36_PC(11),H36_PC(2)|H36_PC(5)|H36_PC(9),H36_CHROMATIC,H36_BASS_DEFAULT,32},
    {2,7,H36_PC(0)|H36_PC(3)|H36_PC(6)|H36_PC(9),0,H36_PC(1)|H36_PC(4)|H36_PC(7)|H36_PC(10),H36_CHROMATIC,H36_BASS_DEFAULT,34},
    {2,7,H36_PC(0)|H36_PC(3)|H36_PC(6)|H36_PC(8),0,H36_PC(1)|H36_PC(5)|H36_PC(8)|H36_PC(11),H36_CHROMATIC,H36_BASS_DEFAULT,34},
    {2,7,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_PC(1)|H36_PC(3)|H36_PC(6)|H36_PC(8)|H36_PC(10),H36_PC(1)|H36_PC(5)|H36_PC(8),H36_CHROMATIC,H36_BASS_DEFAULT,32},
    {2,7,H36_PC(0)|H36_PC(3)|H36_PC(5)|H36_PC(7)|H36_PC(8)|H36_PC(10),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_MINOR_SCALE,0,32},
    {2,5,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_PC(0)|H36_PC(4)|H36_PC(9),H36_PC(0)|H36_PC(4)|H36_PC(7),H36_CHROMATIC,7,8},
    {2,2,H36_PC(0)|H36_PC(5)|H36_PC(8),0,H36_PC(0)|H36_PC(4)|H36_PC(7),H36_MINOR_SCALE,5,1},
    {2,3,H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),0,H36_PC(0)|H36_PC(4)|H36_PC(9),H36_CHROMATIC,7,1},
    {3,3,H36_PC(0)|H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(3)|H36_PC(6)|H36_PC(8)|H36_PC(10),H36_PC(0)|H36_PC(4)|H36_PC(7),H36_CHROMATIC,7,4},
    {3,2,H36_PC(0)|H36_PC(2)|H36_PC(5)|H36_PC(9),H36_PC(3)|H36_PC(6)|H36_PC(10),H36_PC(1)|H36_PC(5)|H36_PC(8)|H36_PC(11),H36_CHROMATIC,2,4},
    {4,3,H36_PC(0)|H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(11),H36_PC(1)|H36_PC(8),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(11),H36_CHROMATIC,7,8},
    {3,1,H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(9),H36_PC(2)|H36_PC(6)|H36_PC(11),H36_PC(0)|H36_PC(4)|H36_PC(7)|H36_PC(9),H36_MAJOR_SCALE,0,8},
    {3,1,H36_PC(0)|H36_PC(3)|H36_PC(7)|H36_PC(9),H36_PC(2)|H36_PC(5)|H36_PC(10),H36_PC(0)|H36_PC(3)|H36_PC(7)|H36_PC(9),H36_MINOR_SCALE,0,8},
    {4,1,H36_PC(0)|H36_PC(2)|H36_PC(4)|H36_PC(7)|H36_PC(9),H36_PC(6)|H36_PC(11),H36_PC(0)|H36_PC(2)|H36_PC(4)|H36_PC(7)|H36_PC(9),H36_MAJOR_SCALE,0,8},
    {4,1,H36_PC(0)|H36_PC(2)|H36_PC(3)|H36_PC(7)|H36_PC(9),H36_PC(5)|H36_PC(10),H36_PC(0)|H36_PC(2)|H36_PC(3)|H36_PC(7)|H36_PC(9),H36_MINOR_SCALE,0,8},
    {4,7,H36_PC(0)|H36_PC(2)|H36_PC(5)|H36_PC(7)|H36_PC(9)|H36_PC(11),H36_PC(1)|H36_PC(3)|H36_PC(6)|H36_PC(8)|H36_PC(10),H36_PC(0)|H36_PC(4)|H36_PC(7),H36_CHROMATIC,7,16},
    {4,6,H36_PC(0)|H36_PC(3)|H36_PC(6)|H36_PC(9),H36_PC(1)|H36_PC(4)|H36_PC(7)|H36_PC(10),H36_PC(0)|H36_PC(3)|H36_PC(6)|H36_PC(9),H36_CHROMATIC,H36_BASS_DEFAULT,2}
};

static uint32_t h36_version_word(void) {
    return (HHS_EXACT_PASS219_H36_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_H36_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_H36_VERSION_PATCH;
}

static uint16_t h36_rotate12(uint16_t mask, uint8_t semitones) {
    uint8_t s = (uint8_t)(semitones % 12U);
    uint16_t m = (uint16_t)(mask & UINT16_C(0x0FFF));
    if (s == 0U) return m;
    return (uint16_t)(((uint32_t)m << s | (uint32_t)m >> (12U - s)) & UINT32_C(0x0FFF));
}

static uint32_t h36_popcount12(uint16_t mask) {
    uint32_t count = 0U;
    uint16_t m = (uint16_t)(mask & UINT16_C(0x0FFF));
    while (m != 0U) { count += (uint32_t)(m & 1U); m = (uint16_t)(m >> 1U); }
    return count;
}

static uint64_t h36_pack_harmonic(uint16_t core, uint16_t tension, uint16_t resolution) {
    return ((((uint64_t)core & UINT64_C(0x0FFF)) << 24U) |
            (((uint64_t)tension & UINT64_C(0x0FFF)) << 12U) |
            ((uint64_t)resolution & UINT64_C(0x0FFF))) & HHS_EXACT_PASS219_H36_WORD_MASK;
}

static int64_t h36_signed(uint64_t word) {
    uint64_t v = word & HHS_EXACT_PASS219_H36_WORD_MASK;
    if ((v & (UINT64_C(1) << 35U)) != 0U) return (int64_t)(v | ~HHS_EXACT_PASS219_H36_WORD_MASK);
    return (int64_t)v;
}

static uint64_t h36_wrap_i64(int64_t value) {
    return ((uint64_t)value) & HHS_EXACT_PASS219_H36_WORD_MASK;
}

static uint64_t h36_bool_fn(uint8_t fn, uint64_t a, uint64_t b) {
    a &= HHS_EXACT_PASS219_H36_WORD_MASK;
    b &= HHS_EXACT_PASS219_H36_WORD_MASK;
    switch (fn) {
        case 0U: return 0U; case 1U: return a & b;
        case 2U: return (~a) & b & HHS_EXACT_PASS219_H36_WORD_MASK; case 3U: return b;
        case 4U: return a & (~b) & HHS_EXACT_PASS219_H36_WORD_MASK; case 5U: return a;
        case 6U: return a ^ b; case 7U: return a | b;
        case 8U: return (~a) & (~b) & HHS_EXACT_PASS219_H36_WORD_MASK;
        case 9U: return (~(a ^ b)) & HHS_EXACT_PASS219_H36_WORD_MASK;
        case 10U: return (~a) & HHS_EXACT_PASS219_H36_WORD_MASK;
        case 11U: return ((~a) | b) & HHS_EXACT_PASS219_H36_WORD_MASK;
        case 12U: return (~b) & HHS_EXACT_PASS219_H36_WORD_MASK;
        case 13U: return (a | (~b)) & HHS_EXACT_PASS219_H36_WORD_MASK;
        case 14U: return (~(a & b)) & HHS_EXACT_PASS219_H36_WORD_MASK;
        case 15U: return HHS_EXACT_PASS219_H36_WORD_MASK;
        default: return 0U;
    }
}

static int h36_condition(uint8_t code, int64_t lhs, int64_t rhs) {
    switch (code & 7U) {
        case 0U: return 0; case 1U: return lhs < rhs; case 2U: return lhs == rhs;
        case 3U: return lhs <= rhs; case 4U: return 1; case 5U: return lhs >= rhs;
        case 6U: return lhs != rhs; case 7U: return lhs > rhs; default: return 0;
    }
}

static HHSExactStatus h36_effective_address(HHSExactPass219H36VMStateV1 *state, const HHSExactPass219H36InstructionV1 *ins, uint32_t *out_e) {
    uint32_t y = ins->address18; uint8_t i = ins->indirect1; uint8_t x = ins->index4; uint32_t depth = 0U;
    while (1) {
        uint32_t e = y;
        if (x != 0U) e = (e + (uint32_t)(state->accumulators[x] & HHS_EXACT_PASS219_H36_HALF_MASK)) & UINT32_C(0x3FFFF);
        if (i == 0U) { *out_e = e; return HHS_EXACT_STATUS_OK; }
        if (e >= HHS_EXACT_PASS219_H36_WORD_COUNT) { state->trap = HHS_EXACT_PASS219_H36_TRAP_RANGE; return HHS_EXACT_STATUS_RANGE_ERROR; }
        if (++depth > 32U) { state->trap = HHS_EXACT_PASS219_H36_TRAP_INDIRECT_LIMIT; return HHS_EXACT_STATUS_INVARIANT_FAILURE; }
        {
            HHSExactPass219H36InstructionV1 pointer;
            HHSExactStatus status = hhs_exact_pass219_h36_instruction_decode(state->memory[e], &pointer);
            if (status != HHS_EXACT_STATUS_OK) return status;
            y = pointer.address18; i = pointer.indirect1; x = pointer.index4;
        }
    }
}
