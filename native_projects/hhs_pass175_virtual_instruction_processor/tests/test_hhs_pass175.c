#include "hhs_pass175.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    uint32_t state, projected, recovered_state, recovered_control;
    uint16_t control16, recovered_control16;
    uint8_t trits[5], recovered_trits[5];
    HHS175Address address;
    HHS175Candidate candidates[2];
    uint8_t lr[81] = {0}, lw[81] = {0}, rr[81] = {0}, rw[81] = {0};
    uint32_t cell, operation, control;

    for (cell = 0; cell < 81; ++cell) {
        for (operation = 0; operation < 64; ++operation) {
            assert(hhs175_address_encode(cell, operation, &state) == 0);
            assert(hhs175_address_decode(state, &address) == 0);
            assert(address.cell == cell);
            assert(address.operation == operation);
        }
    }
    assert(hhs175_address_encode(80, 63, &state) == 0 && state == 5183);

    for (control = 0; control < 243; ++control) {
        assert(hhs175_control_decode(control, trits) == 0);
        assert(hhs175_control_encode(trits, &recovered_control16) == 0);
        assert(recovered_control16 == control);
    }

    for (state = 0; state < 5184; ++state) {
        for (control = 0; control < 243; ++control) {
            assert(hhs175_projected_encode(state, control, &projected) == 0);
            assert(hhs175_projected_decode(projected, &recovered_state, &recovered_control) == 0);
            assert(recovered_state == state && recovered_control == control);
        }
    }
    assert(projected == 1259711);

    memset(recovered_trits, 0, sizeof(recovered_trits));
    trits[0] = 2; trits[1] = 1; trits[2] = 0; trits[3] = 2; trits[4] = 1;
    assert(hhs175_control_encode(trits, &control16) == 0);
    assert(hhs175_control_decode(control16, recovered_trits) == 0);
    assert(memcmp(trits, recovered_trits, 5) == 0);

    lw[1] = 1; rr[1] = 1;
    assert(hhs175_candidate_conflict(lr, lw, rr, rw) == 1);
    rr[1] = 0; rw[2] = 1;
    assert(hhs175_candidate_conflict(lr, lw, rr, rw) == 0);

    assert(hhs175_candidate_build(1, 0, 0, 0, 0, 1, 1, &candidates[0]) == 0);
    assert(hhs175_candidate_build(1, 1, 1, 1, 1, 2, -1, &candidates[1]) == 0);
    assert(candidates[0].identity != candidates[1].identity);
    assert(hhs175_singular_commit_root(0, candidates, 2) == hhs175_singular_commit_root(0, candidates, 2));

    printf("HHS_PASS_175_NATIVE_ADDRESS_CONTROL_CANDIDATE_TEST_PASS\n");
    return 0;
}
