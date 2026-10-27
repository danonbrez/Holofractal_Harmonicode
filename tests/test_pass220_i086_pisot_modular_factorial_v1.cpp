#include "hhs_pass220_i086_pisot_modular_factorial_v1.hpp"
#include <cassert>
using namespace hhs::lane5::reciprocal_nesting;
int main() {
    const auto value = derive_modular_factorial_scale();
    assert(scale_operands_valid(value));
    assert(value.numerator_remainder == cpp_int("15272925592854713514250352339843222168795337611734716711939417599987158680867449865638882341642322313216"));
    assert(value.denominator_remainder == cpp_int("61234458376886086861524070385274672740778091784697328983823014963978384987221689274204160000000000000000"));
    assert(value.exponent_numerator == -2752680919LL);
    assert(value.exponent_denominator == 10000000000LL);
    assert(pow72_72() % factorial72() == value.numerator_remainder);
    assert(factorial72() % pow72_72() == value.denominator_remainder);
}
