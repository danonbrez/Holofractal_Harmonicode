#ifndef HHS_PASS220_MATHLIB_ALGEBRA_V1_HPP
#define HHS_PASS220_MATHLIB_ALGEBRA_V1_HPP

#include "hhs_pass220_mathlib_order_rat_v1.hpp"

#include <cstring>

namespace hhs::mathlib {

struct NativeAlgebraLawSetV1 {
    bool valid{false};
    bool add_assoc{false};
    bool add_identity{false};
    bool mul_assoc{false};
    bool mul_identity{false};
    bool left_distrib{false};
    bool right_distrib{false};
    bool add_inverse{false};
    bool exact{false};
    bool python1_executed{false};
    bool operand_order_preserved{false};
    bool host_float_used{false};
    bool host_primitive_arithmetic_used{false};

    bool semiring_pass() const noexcept {
        return valid
            && add_assoc
            && add_identity
            && mul_assoc
            && mul_identity
            && left_distrib
            && right_distrib
            && exact
            && python1_executed
            && operand_order_preserved
            && !host_float_used
            && !host_primitive_arithmetic_used;
    }

    bool ring_pass() const noexcept {
        return semiring_pass() && add_inverse;
    }
};

inline bool native_int_equal(
    const NativeInt& lhs,
    const NativeInt& rhs
) noexcept {
    return lhs.valid()
        && rhs.valid()
        && std::strcmp(lhs.decimal(), rhs.decimal()) == 0;
}

inline bool native_nat_equal(
    const NativeNat& lhs,
    const NativeNat& rhs
) noexcept {
    return lhs.valid()
        && rhs.valid()
        && std::strcmp(lhs.decimal(), rhs.decimal()) == 0;
}

class NativeAlgebraLaws final {
public:
    static NativeAlgebraLawSetV1 nat_semiring(
        const NativeNat& a,
        const NativeNat& b,
        const NativeNat& c
    ) noexcept {
        NativeAlgebraLawSetV1 out{};
        const NativeNat zero("0");
        const NativeNat one("1");

        const NativeNat add_ab = NativeNat::add(a, b);
        const NativeNat add_bc = NativeNat::add(b, c);
        const NativeNat add_assoc_l = NativeNat::add(add_ab, c);
        const NativeNat add_assoc_r = NativeNat::add(a, add_bc);

        const NativeNat mul_ab = NativeNat::mul(a, b);
        const NativeNat mul_bc = NativeNat::mul(b, c);
        const NativeNat mul_assoc_l = NativeNat::mul(mul_ab, c);
        const NativeNat mul_assoc_r = NativeNat::mul(a, mul_bc);

        const NativeNat left_dist_l = NativeNat::mul(a, add_bc);
        const NativeNat left_dist_r =
            NativeNat::add(NativeNat::mul(a, b), NativeNat::mul(a, c));

        const NativeNat right_dist_l = NativeNat::mul(add_ab, c);
        const NativeNat right_dist_r =
            NativeNat::add(NativeNat::mul(a, c), NativeNat::mul(b, c));

        out.valid =
            a.valid() && b.valid() && c.valid()
            && add_assoc_l.valid() && add_assoc_r.valid()
            && mul_assoc_l.valid() && mul_assoc_r.valid()
            && left_dist_l.valid() && left_dist_r.valid()
            && right_dist_l.valid() && right_dist_r.valid();

        out.add_assoc = native_nat_equal(add_assoc_l, add_assoc_r);
        out.add_identity =
            native_nat_equal(NativeNat::add(zero, a), a)
            && native_nat_equal(NativeNat::add(a, zero), a);
        out.mul_assoc = native_nat_equal(mul_assoc_l, mul_assoc_r);
        out.mul_identity =
            native_nat_equal(NativeNat::mul(one, a), a)
            && native_nat_equal(NativeNat::mul(a, one), a);
        out.left_distrib = native_nat_equal(left_dist_l, left_dist_r);
        out.right_distrib = native_nat_equal(right_dist_l, right_dist_r);
        out.exact = out.valid;
        out.python1_executed = out.valid;
        out.operand_order_preserved = true;
        return out;
    }

    static NativeAlgebraLawSetV1 int_ring(
        const NativeInt& a,
        const NativeInt& b,
        const NativeInt& c
    ) noexcept {
        NativeAlgebraLawSetV1 out{};
        const NativeInt zero("0");
        const NativeInt one("1");

        const NativeInt add_ab = NativeInt::add(a, b);
        const NativeInt add_bc = NativeInt::add(b, c);
        const NativeInt add_assoc_l = NativeInt::add(add_ab, c);
        const NativeInt add_assoc_r = NativeInt::add(a, add_bc);

        const NativeInt mul_ab = NativeInt::mul(a, b);
        const NativeInt mul_bc = NativeInt::mul(b, c);
        const NativeInt mul_assoc_l = NativeInt::mul(mul_ab, c);
        const NativeInt mul_assoc_r = NativeInt::mul(a, mul_bc);

        const NativeInt left_dist_l = NativeInt::mul(a, add_bc);
        const NativeInt left_dist_r =
            NativeInt::add(NativeInt::mul(a, b), NativeInt::mul(a, c));

        const NativeInt right_dist_l = NativeInt::mul(add_ab, c);
        const NativeInt right_dist_r =
            NativeInt::add(NativeInt::mul(a, c), NativeInt::mul(b, c));

        const NativeInt neg_a = NativeInt::sub(zero, a);
        const NativeInt inverse_sum = NativeInt::add(a, neg_a);

        out.valid =
            a.valid() && b.valid() && c.valid()
            && add_assoc_l.valid() && add_assoc_r.valid()
            && mul_assoc_l.valid() && mul_assoc_r.valid()
            && left_dist_l.valid() && left_dist_r.valid()
            && right_dist_l.valid() && right_dist_r.valid()
            && neg_a.valid() && inverse_sum.valid();

        out.add_assoc = native_int_equal(add_assoc_l, add_assoc_r);
        out.add_identity =
            native_int_equal(NativeInt::add(zero, a), a)
            && native_int_equal(NativeInt::add(a, zero), a);
        out.mul_assoc = native_int_equal(mul_assoc_l, mul_assoc_r);
        out.mul_identity =
            native_int_equal(NativeInt::mul(one, a), a)
            && native_int_equal(NativeInt::mul(a, one), a);
        out.left_distrib = native_int_equal(left_dist_l, left_dist_r);
        out.right_distrib = native_int_equal(right_dist_l, right_dist_r);
        out.add_inverse = native_int_equal(inverse_sum, zero);
        out.exact = out.valid;
        out.python1_executed = out.valid;
        out.operand_order_preserved = true;
        return out;
    }

    static NativeAlgebraLawSetV1 rat_ring(
        const NativeRat& a,
        const NativeRat& b,
        const NativeRat& c
    ) noexcept {
        NativeAlgebraLawSetV1 out{};
        const NativeRat zero("0", "1");
        const NativeRat one("1", "1");

        const NativeRat add_ab = NativeRat::add(a, b);
        const NativeRat add_bc = NativeRat::add(b, c);
        const NativeRat add_assoc_l = NativeRat::add(add_ab, c);
        const NativeRat add_assoc_r = NativeRat::add(a, add_bc);

        const NativeRat mul_ab = NativeRat::mul(a, b);
        const NativeRat mul_bc = NativeRat::mul(b, c);
        const NativeRat mul_assoc_l = NativeRat::mul(mul_ab, c);
        const NativeRat mul_assoc_r = NativeRat::mul(a, mul_bc);

        const NativeRat left_dist_l = NativeRat::mul(a, add_bc);
        const NativeRat left_dist_r =
            NativeRat::add(NativeRat::mul(a, b), NativeRat::mul(a, c));

        const NativeRat right_dist_l = NativeRat::mul(add_ab, c);
        const NativeRat right_dist_r =
            NativeRat::add(NativeRat::mul(a, c), NativeRat::mul(b, c));

        const NativeRat neg_a = NativeRat::sub(zero, a);
        const NativeRat inverse_sum = NativeRat::add(a, neg_a);

        out.valid =
            a.valid() && b.valid() && c.valid()
            && add_assoc_l.valid() && add_assoc_r.valid()
            && mul_assoc_l.valid() && mul_assoc_r.valid()
            && left_dist_l.valid() && left_dist_r.valid()
            && right_dist_l.valid() && right_dist_r.valid()
            && neg_a.valid() && inverse_sum.valid();

        out.add_assoc = NativeRat::equivalent(add_assoc_l, add_assoc_r);
        out.add_identity =
            NativeRat::equivalent(NativeRat::add(zero, a), a)
            && NativeRat::equivalent(NativeRat::add(a, zero), a);
        out.mul_assoc = NativeRat::equivalent(mul_assoc_l, mul_assoc_r);
        out.mul_identity =
            NativeRat::equivalent(NativeRat::mul(one, a), a)
            && NativeRat::equivalent(NativeRat::mul(a, one), a);
        out.left_distrib = NativeRat::equivalent(left_dist_l, left_dist_r);
        out.right_distrib = NativeRat::equivalent(right_dist_l, right_dist_r);
        out.add_inverse = NativeRat::equivalent(inverse_sum, zero);
        out.exact = out.valid;
        out.python1_executed = out.valid;
        out.operand_order_preserved = true;
        return out;
    }

    static constexpr bool implicit_commutation_authorized() noexcept {
        return false;
    }

    static constexpr bool universal_proof_closed() noexcept {
        return false;
    }
};

}  // namespace hhs::mathlib

#endif
