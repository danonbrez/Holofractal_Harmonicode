#ifndef HHS_PASS220_MATHLIB_ORDER_RAT_V1_HPP
#define HHS_PASS220_MATHLIB_ORDER_RAT_V1_HPP

#include "hhs_pass220_mathlib_native_v1.hpp"

#include <cstring>
#include <string_view>

namespace hhs::mathlib {

enum class NativeRelationV1 {
    invalid = -2,
    less = -1,
    equal = 0,
    greater = 1
};

class NativeRat final {
public:
    NativeRat(std::string_view numerator, std::string_view denominator) noexcept
        : numerator_(numerator),
          denominator_(denominator),
          admitted_(
              numerator_.valid()
              && denominator_.valid()
              && denominator_.decimal()[0] != '-'
              && std::strcmp(denominator_.decimal(), "0") != 0
          ) {}

    bool valid() const noexcept { return admitted_; }
    const char* numerator_decimal() const noexcept { return numerator_.decimal(); }
    const char* denominator_decimal() const noexcept { return denominator_.decimal(); }

    static NativeRat add(const NativeRat& lhs, const NativeRat& rhs) noexcept {
        if (!lhs.valid() || !rhs.valid()) return NativeRat(RawTag{});
        const NativeInt left =
            NativeInt::mul(lhs.numerator_, rhs.denominator_);
        const NativeInt right =
            NativeInt::mul(rhs.numerator_, lhs.denominator_);
        const NativeInt numerator = NativeInt::add(left, right);
        const NativeInt denominator =
            NativeInt::mul(lhs.denominator_, rhs.denominator_);
        return from_native(numerator, denominator);
    }

    static NativeRat sub(const NativeRat& lhs, const NativeRat& rhs) noexcept {
        if (!lhs.valid() || !rhs.valid()) return NativeRat(RawTag{});
        const NativeInt left =
            NativeInt::mul(lhs.numerator_, rhs.denominator_);
        const NativeInt right =
            NativeInt::mul(rhs.numerator_, lhs.denominator_);
        const NativeInt numerator = NativeInt::sub(left, right);
        const NativeInt denominator =
            NativeInt::mul(lhs.denominator_, rhs.denominator_);
        return from_native(numerator, denominator);
    }

    static NativeRat mul(const NativeRat& lhs, const NativeRat& rhs) noexcept {
        if (!lhs.valid() || !rhs.valid()) return NativeRat(RawTag{});
        const NativeInt numerator =
            NativeInt::mul(lhs.numerator_, rhs.numerator_);
        const NativeInt denominator =
            NativeInt::mul(lhs.denominator_, rhs.denominator_);
        return from_native(numerator, denominator);
    }

    static NativeRelationV1 compare(
        const NativeRat& lhs,
        const NativeRat& rhs
    ) noexcept {
        if (!lhs.valid() || !rhs.valid()) return NativeRelationV1::invalid;
        const NativeInt left =
            NativeInt::mul(lhs.numerator_, rhs.denominator_);
        const NativeInt right =
            NativeInt::mul(rhs.numerator_, lhs.denominator_);
        const NativeInt delta = NativeInt::sub(left, right);
        if (!delta.valid()) return NativeRelationV1::invalid;
        if (std::strcmp(delta.decimal(), "0") == 0)
            return NativeRelationV1::equal;
        if (delta.decimal()[0] == '-')
            return NativeRelationV1::less;
        return NativeRelationV1::greater;
    }

    static bool equivalent(const NativeRat& lhs, const NativeRat& rhs) noexcept {
        return compare(lhs, rhs) == NativeRelationV1::equal;
    }

    static bool less(const NativeRat& lhs, const NativeRat& rhs) noexcept {
        return compare(lhs, rhs) == NativeRelationV1::less;
    }

    static bool less_equal(const NativeRat& lhs, const NativeRat& rhs) noexcept {
        const NativeRelationV1 relation = compare(lhs, rhs);
        return relation == NativeRelationV1::less
            || relation == NativeRelationV1::equal;
    }

    static constexpr bool gcd_reduction_required_for_identity() noexcept {
        return false;
    }

    static constexpr bool host_float_used() noexcept {
        return false;
    }

    static constexpr bool host_integer_comparison_used() noexcept {
        return false;
    }

private:
    struct RawTag {};

    explicit NativeRat(RawTag) noexcept
        : numerator_("0"), denominator_("0"), admitted_(false) {}

    static NativeRat from_native(
        const NativeInt& numerator,
        const NativeInt& denominator
    ) noexcept {
        NativeRat out(RawTag{});
        out.numerator_ = numerator;
        out.denominator_ = denominator;
        out.admitted_ =
            out.numerator_.valid()
            && out.denominator_.valid()
            && out.denominator_.decimal()[0] != '-'
            && std::strcmp(out.denominator_.decimal(), "0") != 0;
        return out;
    }

    NativeInt numerator_;
    NativeInt denominator_;
    bool admitted_{false};
};

}  // namespace hhs::mathlib

#endif
