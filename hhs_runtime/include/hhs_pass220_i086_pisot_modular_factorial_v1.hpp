#ifndef HHS_PASS220_I086_PISOT_MODULAR_FACTORIAL_V1_HPP
#define HHS_PASS220_I086_PISOT_MODULAR_FACTORIAL_V1_HPP

#include <boost/multiprecision/cpp_int.hpp>
#include <cstdint>

namespace hhs::lane5::reciprocal_nesting {
using boost::multiprecision::cpp_int;

// Exact integer operands of the user-supplied expression. This module does not
// scalarize exponent gates, assert the Pisot value is exact, or mint receipts.
struct ModularFactorialScale final {
    cpp_int numerator_remainder;
    cpp_int denominator_remainder;
    cpp_int exponent_numerator;    // -0.2752680919, exact decimal
    cpp_int exponent_denominator;  // 10^10
};

inline cpp_int factorial72() {
    cpp_int value = 1;
    for (unsigned i = 2; i <= 72; ++i) value *= i;
    return value;
}
inline cpp_int pow72_72() {
    cpp_int value = 1;
    for (unsigned i = 0; i < 72; ++i) value *= 72;
    return value;
}
inline ModularFactorialScale derive_modular_factorial_scale() {
    const cpp_int factorial = factorial72();
    const cpp_int manifold = pow72_72();
    return {manifold % factorial, factorial % manifold,
            cpp_int(-2752680919LL), cpp_int(10000000000LL)};
}
inline bool scale_operands_valid(const ModularFactorialScale& value) {
    return value.numerator_remainder > 0 &&
           value.denominator_remainder > value.numerator_remainder &&
           value.exponent_denominator > 0 &&
           value.exponent_numerator < 0;
}
} // namespace hhs::lane5::reciprocal_nesting
#endif
