/* Pass 220 I085: original Pass186 C ABI vs 5184 rational x/u ADDRESSES.
   This tests the existing C mapping, not a simulated replacement runtime.
   It never evaluates a native (x/u)^r operator nor commits Hash72/VM81. */
#include "hhs_pass186_x64_vm81_q144_abi.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint32_t gcd32(uint32_t a, uint32_t b) {
    while (b != 0U) {
        uint32_t t = a % b;
        a = b;
        b = t;
    }
    return a;
}

int main(void) {
    uint8_t seen_vm5184[HHS186_VM5184_STATES] = {0};
    uint8_t seen_hash_grid[HHS186_VM5184_STATES] = {0};
    uint8_t seen_phase_exponents[HHS186_VM5184_STATES] = {0};
    uint32_t state;
    for (state = 0U; state < HHS186_VM5184_STATES; state++) {
        HHS186Quantization q;
        HHS186MappingResult native;
        uint32_t opcode_lane = state / HHS186_Q144;
        uint32_t q144 = state % HHS186_Q144;
        uint32_t hash72_row = state / HHS186_U72_RING;
        uint32_t hash72_col = state % HHS186_U72_RING;
        uint32_t divisor = gcd32(state, HHS186_U72_RING);
        uint32_t rational_num = state / divisor;
        uint32_t rational_den = HHS186_U72_RING / divisor;
        uint32_t reconstructed;

        memset(&q, 0, sizeof(q));
        q.struct_size = (uint32_t)sizeof(q);
        q.abi_version = HHS186_ABI_VERSION;
        q.opcode_lane36 = (uint8_t)opcode_lane;
        q.root_row12 = (uint8_t)(q144 / HHS186_Q12);
        q.root_col12 = (uint8_t)(q144 % HHS186_Q12);
        q.g243 = 0U;
        memset(&native, 0, sizeof(native));

        assert(hhs186_x64_vm81_q144_map(
            2, 3, 5, 7, &q, &native
        ) == HHS186_STATUS_OK);
        assert(native.instruction_state5184 == state);
        assert(native.vm81_cell == state / HHS186_VM81_OPERATIONS_PER_CELL);
        assert(native.vm81_operation64 == state % HHS186_VM81_OPERATIONS_PER_CELL);
        assert(native.ordered_basis == native.vm81_operation64 % 8U);
        assert(native.operation_class8 == native.vm81_operation64 / 8U);
        assert(native.opcode_lane36 == opcode_lane);
        assert(native.q144_index == q144);
        assert(native.u72_pair == q144 / HHS186_U72_RING);
        assert(native.u72_index == q144 % HHS186_U72_RING);
        assert(hash72_row < HHS186_U72_RING);
        assert(hash72_col < HHS186_U72_RING);
        assert(hash72_row * HHS186_U72_RING + hash72_col == state);
        assert(rational_den > 0U);
        assert(rational_num * HHS186_U72_RING == state * rational_den);
        reconstructed = (rational_num * HHS186_U72_RING) / rational_den;
        assert(reconstructed == state);
        assert(!seen_vm5184[native.instruction_state5184]);
        assert(!seen_hash_grid[hash72_row * HHS186_U72_RING + hash72_col]);
        assert(!seen_phase_exponents[reconstructed]);
        seen_vm5184[native.instruction_state5184] = 1U;
        seen_hash_grid[hash72_row * HHS186_U72_RING + hash72_col] = 1U;
        seen_phase_exponents[reconstructed] = 1U;
    }
    for (state = 0; state < HHS186_VM5184_STATES; state++) {
        assert(seen_vm5184[state]);
        assert(seen_hash_grid[state]);
        assert(seen_phase_exponents[state]);
    }
    /* Equality of ordered integer magnitudes is not a commutation proof. */
    {
        HHS186Quantization xy, yx;
        HHS186MappingResult a, b;
        memset(&xy, 0, sizeof(xy));
        xy.struct_size = (uint32_t)sizeof(xy);
        xy.abi_version = HHS186_ABI_VERSION;
        xy.root_col12 = 4U;
        yx = xy;
        yx.root_col12 = 5U;
        assert(hhs186_x64_vm81_q144_map(2, 3, 5, 7, &xy, &a) == HHS186_STATUS_OK);
        assert(hhs186_x64_vm81_q144_map(2, 3, 5, 7, &yx, &b) == HHS186_STATUS_OK);
        assert(a.ordered_product_witness == b.ordered_product_witness);
        assert(a.ordered_basis == HHS186_BASIS_XY);
        assert(b.ordered_basis == HHS186_BASIS_YX);
        assert(a.ordered_tag != b.ordered_tag);
    }
    puts("HHS_PASS220_I085_EXACT_PASS186_CROSSWALK_OK positions=5184");
    return 0;
}
