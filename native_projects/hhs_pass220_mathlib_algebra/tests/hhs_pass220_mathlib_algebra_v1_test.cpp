#include "hhs_pass220_mathlib_algebra_v1.hpp"

#include <cassert>

int main() {
    using hhs::mathlib::NativeAlgebraLaws;
    using hhs::mathlib::NativeInt;
    using hhs::mathlib::NativeNat;
    using hhs::mathlib::NativeRat;

    const auto nat = NativeAlgebraLaws::nat_semiring(
        NativeNat("72"),
        NativeNat("81"),
        NativeNat("64")
    );
    assert(nat.semiring_pass());
    assert(!nat.add_inverse);

    const auto integer = NativeAlgebraLaws::int_ring(
        NativeInt("-37"),
        NativeInt("72"),
        NativeInt("5184")
    );
    assert(integer.ring_pass());

    const auto rational = NativeAlgebraLaws::rat_ring(
        NativeRat("1", "2"),
        NativeRat("2", "3"),
        NativeRat("-3", "4")
    );
    assert(rational.ring_pass());

    const auto large = NativeAlgebraLaws::int_ring(
        NativeInt("999999999999999999999999"),
        NativeInt("-888888888888888888888888"),
        NativeInt("777777777777777777777777")
    );
    assert(large.ring_pass());

    assert(!NativeAlgebraLaws::implicit_commutation_authorized());
    assert(!NativeAlgebraLaws::universal_proof_closed());

    return 0;
}
