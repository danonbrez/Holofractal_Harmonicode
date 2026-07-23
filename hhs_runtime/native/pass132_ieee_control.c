/* Pass 132 reconstructed IEEE control backend.
 *
 * This is not the unavailable historical source committed by the original
 * Pass 132 release. It supplies an explicit, callable binary32/binary64 control
 * surface for the reconstructed lineage and is compiled with strict FP flags
 * in the dependency-scoped tests.
 */
#include <stdint.h>
#include <math.h>

float hhs_pass132_binary32_add(float a, float b) { return a + b; }
float hhs_pass132_binary32_sub(float a, float b) { return a - b; }
float hhs_pass132_binary32_mul(float a, float b) { return a * b; }
float hhs_pass132_binary32_div(float a, float b) { return a / b; }

double hhs_pass132_binary64_add(double a, double b) { return a + b; }
double hhs_pass132_binary64_sub(double a, double b) { return a - b; }
double hhs_pass132_binary64_mul(double a, double b) { return a * b; }
double hhs_pass132_binary64_div(double a, double b) { return a / b; }

int hhs_pass132_ieee_classify64(double value) {
    if (isnan(value)) return 1;
    if (isinf(value)) return 2;
    if (value == 0.0 && signbit(value)) return 3;
    if (value == 0.0) return 4;
    return 0;
}
