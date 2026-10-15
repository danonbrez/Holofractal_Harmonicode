#include "hhs_pass220_course_passthrough_witness.h"
#include <string.h>
int hhs220_course_passthrough_execute(
    const uint8_t *carrier, size_t carrier_len,
    const uint8_t *phase, size_t phase_len,
    uint32_t divisor_zero,
    uint8_t *carrier_out, uint8_t *phase_out,
    HHS220PassthroughWitness *receipt) {
    if (!carrier || !phase || !carrier_out || !phase_out || !receipt ||
        !carrier_len || !phase_len || divisor_zero != 1U) return 0;
    /* Only the exact zero-divisor passthrough branch is defined by this ABI. */
    memcpy(carrier_out, carrier, carrier_len);
    memcpy(phase_out, phase, phase_len);
    memset(receipt, 0, sizeof(*receipt));
    receipt->decision=1U;
    receipt->bypass_applied=1U;
    receipt->gain_numerator=1U;
    receipt->gain_denominator=1U;
    receipt->carrier_preserved=(memcmp(carrier,carrier_out,carrier_len)==0);
    receipt->phase_preserved=(memcmp(phase,phase_out,phase_len)==0);
    return receipt->carrier_preserved && receipt->phase_preserved;
}
