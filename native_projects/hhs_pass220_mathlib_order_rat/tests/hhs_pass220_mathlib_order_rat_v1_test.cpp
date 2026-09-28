#include "hhs_pass220_mathlib_order_rat_v1.hpp"

#include <cassert>
#include <string_view>

int main() {
    using hhs::mathlib::NativeRat;
    using hhs::mathlib::NativeRelationV1;

    const NativeRat half("1", "2");
    const NativeRat third("1", "3");
    assert(half.valid());
    assert(third.valid());

    const NativeRat sum = NativeRat::add(half, third);
    assert(sum.valid());
    assert(std::string_view(sum.numerator_decimal()) == "5");
    assert(std::string_view(sum.denominator_decimal()) == "6");

    const NativeRat two_thirds("2", "3");
    const NativeRat nine_fourths("9", "4");
    const NativeRat product = NativeRat::mul(two_thirds, nine_fourths);
    assert(product.valid());
    assert(std::string_view(product.numerator_decimal()) == "18");
    assert(std::string_view(product.denominator_decimal()) == "12");

    const NativeRat two_fourths("2", "4");
    assert(NativeRat::equivalent(half, two_fourths));
    assert(NativeRat::compare(half, two_fourths) == NativeRelationV1::equal);

    const NativeRat negative_half("-1", "2");
    const NativeRat zero("0", "1");
    assert(NativeRat::less(negative_half, zero));
    assert(NativeRat::less_equal(negative_half, zero));
    assert(NativeRat::compare(negative_half, zero) == NativeRelationV1::less);

    const NativeRat three_fourths("3", "4");
    assert(NativeRat::compare(three_fourths, two_thirds) ==
           NativeRelationV1::greater);

    const NativeRat invalid_zero_denominator("1", "0");
    const NativeRat invalid_negative_denominator("1", "-2");
    assert(!invalid_zero_denominator.valid());
    assert(!invalid_negative_denominator.valid());
    assert(NativeRat::compare(invalid_zero_denominator, half) ==
           NativeRelationV1::invalid);

    const NativeRat seventy_two("72", "1");
    const NativeRat square = NativeRat::mul(seventy_two, seventy_two);
    assert(square.valid());
    assert(std::string_view(square.numerator_decimal()) == "5184");
    assert(std::string_view(square.denominator_decimal()) == "1");

    assert(!NativeRat::gcd_reduction_required_for_identity());
    assert(!NativeRat::host_float_used());
    assert(!NativeRat::host_integer_comparison_used());

    return 0;
}
