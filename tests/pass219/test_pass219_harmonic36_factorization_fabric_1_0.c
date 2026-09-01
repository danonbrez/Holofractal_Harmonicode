#include "hhs_pass219_harmonic36_factorization_fabric_1_0.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

static uint64_t next64(uint64_t *x) {
    *x ^= *x << 13U;
    *x ^= *x >> 7U;
    *x ^= *x << 17U;
    return *x;
}

int main(void) {
    uint32_t i;

    for (i = 0U; i < HHS_EXACT_PASS219_H36_FRAME_BITS; ++i) {
        HHSExactPass219H36FactorizationCircuitV1 c;
        assert(hhs_exact_pass219_h36_factorization_circuit(
            (uint16_t)i, &c) == HHS_EXACT_STATUS_OK);
        assert(hhs_exact_pass219_h36_factorization_circuit_validate(&c) ==
               HHS_EXACT_STATUS_OK);
        assert((uint32_t)c.vm81_cell81 * 64U + c.vm81_operation64 == i);
        assert((uint32_t)c.hash72_row72 * 72U + c.hash72_col72 == i);
        assert((uint32_t)c.h36_word144 * 36U + c.h36_bit36 == i);
        assert((uint32_t)c.phase_left8 * 8U + c.phase_right8 ==
               c.vm81_operation64);
        assert(c.harmonic_rule64 == (uint8_t)(c.vm81_operation64 + 1U));
        assert(c.genesis_equal == 1U);
        assert(c.factorization_identity_preserved == 1U);
    }

    {
        uint64_t seed = UINT64_C(0xD1B54A32D192ED03);
        uint32_t round;
        for (round = 0U; round < 32U; ++round) {
            HHSExactVM81Frame frame;
            HHSExactPass219H36HydrationWitnessV1 witness;
            uint32_t w;
            for (w = 0U; w < HHS_EXACT_VM81_CELLS; ++w)
                frame.words[w] = next64(&seed);

            assert(hhs_exact_pass219_h36_hydration_roundtrip(
                &frame, &witness) == HHS_EXACT_STATUS_OK);
            assert(hhs_exact_pass219_h36_hydration_witness_validate(
                &witness) == HHS_EXACT_STATUS_OK);
        }
    }

    puts("PASS219 Harmonic36 factorization fabric: PASS");
    return 0;
}
