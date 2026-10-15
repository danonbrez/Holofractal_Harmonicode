#ifndef HHS_PASS220_I086_TENSOR_CELL_BINDING_V1_HPP
#define HHS_PASS220_I086_TENSOR_CELL_BINDING_V1_HPP

#include "hhs_pass220_i086_reciprocal_nesting_address_v1.hpp"
#include "hhs_pass220_i086_pisot_modular_factorial_v1.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <cstdint>

namespace hhs::lane5::reciprocal_nesting {

struct ExactRatio final {
    cpp_int numerator;
    cpp_int denominator;
};
inline cpp_int positive_gcd(cpp_int a, cpp_int b) {
    while (b != 0) { cpp_int rem = a % b; a = b; b = rem; }
    return a < 0 ? -a : a;
}
inline ExactRatio exact_add(const ExactRatio& a, const ExactRatio& b) {
    const cpp_int n = a.numerator * b.denominator + b.numerator * a.denominator;
    const cpp_int d = a.denominator * b.denominator;
    const cpp_int g = positive_gcd(n,d);
    return {n/g,d/g};
}
inline constexpr std::int32_t kReciprocalDenominators[4][4] = {
    {1,2,3,5},{2,4,6,10},{3,6,9,15},{4,7,11,18}
};
inline constexpr std::int32_t kMagicCellOrder[4][4] = {
    {16,3,2,13},{5,10,11,8},{9,6,7,12},{4,15,14,1}
};

// Coefficients are derived only in source operand order. No equality gate,
// Pisot exponent or typed tensor symbol is evaluated as a host scalar.
inline ExactRatio coefficient(std::uint32_t row, std::uint32_t col) {
    if (row >= 4 || col >= 4) return {0,0};
    ExactRatio sum{0,1};
    for (std::uint32_t k = 0; k < 4; ++k)
        sum = exact_add(sum,{kMagicCellOrder[k][col],
                             kReciprocalDenominators[row][k]});
    return sum;
}

struct CellBinding final {
    Address address{};
    std::uint32_t kernel_row{};
    std::uint32_t kernel_col{};
    ExactRatio weight{};
    // Scale is an exact inert operand descriptor; native cell-wall admission
    // owns exponent evaluation, operator ordering, closure and Hash216.
    ModularFactorialScale scale{};
    bool candidate_only{true};
};
inline bool bind_cell(std::uint32_t flat, CellBinding& out) {
    Address address{};
    if (!from_flat(flat,address)) return false;
    const std::uint32_t index = address.cell4x4;
    out = CellBinding{address,index/4,index%4,
                      coefficient(index/4,index%4),
                      derive_modular_factorial_scale(),true};
    return out.weight.denominator != 0 && scale_operands_valid(out.scale);
}
} // namespace hhs::lane5::reciprocal_nesting
#endif
