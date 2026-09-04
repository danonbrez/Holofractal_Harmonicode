#ifndef HHS_PASS168_COMPARATOR_1_0_H
#define HHS_PASS168_COMPARATOR_1_0_H

#include "hhs_pass168_parameter_circuit_1_0.h"

#ifdef __cplusplus
extern "C" {
#endif

HHS_EXACT_API HHSExactStatus hhs_pass168_compare_rational(
    HHSPass168Rational left_gain,
    HHSPass168Rational left_value,
    HHSPass168Rational right_gain,
    HHSPass168Rational right_value,
    HHSPass168Rational *out_shadow
);

HHS_EXACT_API HHSExactStatus hhs_pass168_compare_matrix(
    HHSPass168Rational left_gain,
    const HHSPass168Matrix3 *left_value,
    HHSPass168Rational right_gain,
    const HHSPass168Matrix3 *right_value,
    HHSPass168Matrix3 *out_shadow
);

HHS_EXACT_API HHSExactStatus hhs_pass168_comparator_conformance(
    uint32_t *out_verified_count
);

#ifdef __cplusplus
}
#endif

#endif
