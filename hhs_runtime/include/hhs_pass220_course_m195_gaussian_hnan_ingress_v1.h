/* Module 195 bounded exact Gaussian denominator selector: candidate-only.
 * Composes the existing Course Module 9 C11 passthrough ABI without altering
 * its logic. This is neither Lane 5 producer ingress nor canonical VM81.
 */
#ifndef HHS_PASS220_COURSE_M195_GAUSSIAN_HNAN_INGRESS_V1_H
#define HHS_PASS220_COURSE_M195_GAUSSIAN_HNAN_INGRESS_V1_H
#include <stdint.h>
#include <stddef.h>
#include "hhs_pass220_course_passthrough_witness.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
    int64_t denominator_real;
    int64_t denominator_imag;
    uint32_t exact_guard_evaluated;
    uint32_t denominator_zero;
    uint32_t inherited_c_passthrough_invoked;
    uint32_t canonical_admission;
} HHS220M195GaussianDecision;
/* Only |a|,|b|<=100000 are accepted, proving int64 polynomial safety. */
int hhs220_m195_gaussian_denominator(int32_t a, int32_t b,
                                     HHS220M195GaussianDecision *out);
/* Executes the inherited C ABI only for exact D(a+bi)=0. */
int hhs220_m195_gaussian_hnan_candidate(
    int32_t a, int32_t b, const uint8_t *carrier, size_t carrier_len,
    const uint8_t *phase, size_t phase_len, uint8_t *carrier_out,
    uint8_t *phase_out, HHS220PassthroughWitness *receipt,
    HHS220M195GaussianDecision *decision);
#ifdef __cplusplus
}
#endif
#endif
