#include "hhs_pass220_course_m195_gaussian_hnan_ingress_v1.h"
#include <string.h>

/* Algebraic calculation only; bounded |a|,|b| prevents int64 overflow.
 * D(x)=x^3+6*x^2+25*x, x=a+bi. Ingress is candidate-only.
 */
int hhs220_m195_gaussian_denominator(int32_t a, int32_t b,
                                     HHS220M195GaussianDecision *out) {
    if (!out) return 0;
    memset(out, 0, sizeof(*out));
    if (a < -100000 || a > 100000 || b < -100000 || b > 100000)
        return 0;
    int64_t ar = a, bi = b;
    int64_t qr = ar*ar - bi*bi;
    int64_t qi = 2*ar*bi;
    int64_t cr = ar*qr - bi*qi;
    int64_t ci = ar*qi + bi*qr;
    out->denominator_real = cr + 6*qr + 25*ar;
    out->denominator_imag = ci + 6*qi + 25*bi;
    out->exact_guard_evaluated = 1U;
    out->denominator_zero =
        (out->denominator_real == 0 && out->denominator_imag == 0) ? 1U : 0U;
    return 1;
}

int hhs220_m195_gaussian_hnan_candidate(
    int32_t a, int32_t b, const uint8_t *carrier, size_t carrier_len,
    const uint8_t *phase, size_t phase_len, uint8_t *carrier_out,
    uint8_t *phase_out, HHS220PassthroughWitness *receipt,
    HHS220M195GaussianDecision *decision) {
    if (!decision || !receipt) return 0;
    memset(receipt, 0, sizeof(*receipt));
    if (!hhs220_m195_gaussian_denominator(a, b, decision) ||
        !decision->denominator_zero) return 0;
    /* Inherited checker is sole passthrough executor; no new HNAN gate. */
    int ok = hhs220_course_passthrough_execute(
        carrier, carrier_len, phase, phase_len, 1U,
        carrier_out, phase_out, receipt);
    decision->inherited_c_passthrough_invoked = ok == 1 ? 1U : 0U;
    return ok;
}
