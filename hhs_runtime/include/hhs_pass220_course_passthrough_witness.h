/* Pass 220 course passthrough: independent, candidate-only execution witness.
 * This does NOT replace the native HNAN phase-preservation gate. */
#ifndef HHS_PASS220_COURSE_PASSTHROUGH_WITNESS_H
#define HHS_PASS220_COURSE_PASSTHROUGH_WITNESS_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
    uint32_t decision;
    uint32_t bypass_applied;
    uint32_t gain_numerator;
    uint32_t gain_denominator;
    uint32_t phase_writes;
    uint32_t carrier_preserved;
    uint32_t phase_preserved;
    uint32_t canonical_admission;
} HHS220PassthroughWitness;
/* Input is an opaque, ordered, typed byte-state. Both payloads must be
 * nonempty. Denominator-zero bypass never attempts host division and cannot
 * mint canonical runtime state or Hash216 receipts. */
int hhs220_course_passthrough_execute(
    const uint8_t *carrier, size_t carrier_len,
    const uint8_t *phase, size_t phase_len,
    uint32_t divisor_zero,
    uint8_t *carrier_out, uint8_t *phase_out,
    HHS220PassthroughWitness *receipt);
#ifdef __cplusplus
}
#endif
#endif
